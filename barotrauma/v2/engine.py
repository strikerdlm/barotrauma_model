"""
barotrauma.v2.engine
====================

Main simulation engine. Integrates middle-ear pressure dynamics across a
chamber exposure and returns a time-domain trace plus the hazard-model risk.

Design notes
------------
* Fixed-step integrator (default dt = 0.1 s) — chamber exposures are short
  (minutes) and the dynamics have multi-second event spacing (swallows), so
  no stiffness issues warrant solve_ivp.
* Discrete events (swallow, Valsalva) are evaluated at step boundaries. Each
  event mutates ΔP instantaneously.
* Trans-mucosal gas exchange (Doyle 2011) is small over minute timescales and
  applied as a slow drift on P_ME composition. Its effect on total P_ME is
  negligible compared to ET flow for chamber-length exposures; retained for
  long holds and multi-exposure days.
* The physics does NOT auto-clip ΔP at the rupture threshold — the engine
  reports the unclipped trajectory so ``risk.py`` can evaluate the hazard
  integral. Risk scoring treats the post-rupture regime as an absorbing
  state (probability saturates).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np
from numpy.typing import NDArray

from . import constants as C
from .anatomy import apply_severity_to_et
from .atmosphere import discretize_profile, descent_rate_ft_min
from .et_dynamics import (
    EtStepState,
    active_swallow_equalization,
    apply_patulous_state,
    attempt_unlock,
    check_et_lock,
    passive_equilibration_mmHg,
    passive_open_direction,
    swallow_interval_s,
    valsalva_pressurization_mmHg,
)
from .et_muscle import (
    MuscleMechanics,
    MuscleState,
    fge_modulation,
    record_swallow,
    update_state as update_muscle_state,
)
from .middle_ear import (
    GasComposition,
    MeState,
    boyle_update_me_pressure_mmHg,
    effective_me_volume_ml,
    full_gas_exchange_step,
    initial_me_gas,
    rescale_gas_to_total,
    tm_displacement_ml,
    transmucosal_exchange_step,
)
from .pathophysiology import (
    Modifiers,
    apply_modifiers_to_et,
    modifiers_for_patient,
)
from .types import (
    ChamberProfile,
    EtFunction,
    PatientState,
    SimulationResult,
    SimulationTrace,
)


# ------------------------------------------------------ public API -----
def simulate(
    patient: PatientState,
    profile: ChamberProfile,
    *,
    dt_s: float = C.DEFAULT_DT_S,
    rng_seed: int | None = None,
    muscle_mechanics: MuscleMechanics | None = None,
    gas_exchange_full: bool = False,
) -> SimulationResult:
    """
    Run a single-exposure chamber simulation.

    Parameters
    ----------
    patient : PatientState
        Full patient snapshot (anatomy + ET function + acute/chronic state).
    profile : ChamberProfile
        Chamber pressure profile to expose the patient to.
    dt_s : float, optional
        Integrator step (seconds). Default 0.1.
    rng_seed : int, optional
        Seed for stochastic swallow-interval jitter. None = deterministic.
    muscle_mechanics : MuscleMechanics, optional
        If provided and ``enabled=True``, applies Ghadiali-FEM-inspired
        time-varying active-resistance modulation on each swallow (v2.2).
        Default None → v2.1-equivalent constant-R_A behavior.
    gas_exchange_full : bool, optional
        If True, use the Doyle 2017 multi-pathway gas exchange
        (trans-mucosal + trans-TM + trans-RW). Default False → v2.1
        trans-mucosal only. Enabling matters for multi-hour exposures.

    Returns
    -------
    SimulationResult
        Time-domain trace, risk result, and metadata.
    """
    patient.validate()
    profile.validate()
    if not (C.MIN_DT_S <= dt_s <= C.MAX_DT_S):
        raise ValueError(f"dt_s out of range [{C.MIN_DT_S}, {C.MAX_DT_S}]")

    rng = np.random.default_rng(rng_seed)

    # --- pre-compute profile -------------------------------------------
    t_s, altitude_ft, p_ambient = discretize_profile(profile, dt_s)
    descent_rate = descent_rate_ft_min(t_s, altitude_ft)   # ft/min, positive on descent

    # --- resolve modifiers and effective ET function -------------------
    modifiers = modifiers_for_patient(patient)
    et_sev = apply_severity_to_et(patient.et, patient.et.severity)
    et_eff = apply_modifiers_to_et(et_sev, modifiers)

    # --- trace allocation ----------------------------------------------
    n = len(t_s)
    p_me = np.zeros(n, dtype=np.float64)
    delta_p = np.zeros(n, dtype=np.float64)
    tm_disp = np.zeros(n, dtype=np.float64)
    et_open = np.zeros(n, dtype=np.bool_)
    swallow_events: list[float] = []
    valsalva_events: list[float] = []

    # --- initial state ---------------------------------------------------
    # At t=0, ME is equilibrated with ambient (subject fully rested).
    me = MeState(
        p_me_mmHg=float(p_ambient[0]),
        gas=initial_me_gas(float(p_ambient[0])),
        v_me_effective_ml=patient.anatomy.me_volume_ml,
    )
    p_me[0] = me.p_me_mmHg
    delta_p[0] = 0.0
    tm_disp[0] = 0.0

    step = EtStepState()
    # randomize first swallow phase to avoid grid artifacts
    step.last_swallow_time_s = -rng.uniform(0.0, swallow_interval_s(et_eff, False))

    # Ghadiali FEM muscle-mechanics state (only used when mechanics.enabled)
    mechanics = muscle_mechanics or MuscleMechanics(enabled=False)
    muscle = MuscleState()

    # --- integration loop -------------------------------------------------
    for i in range(1, n):
        t = float(t_s[i])
        dt = float(t_s[i] - t_s[i - 1])
        p_amb_i = float(p_ambient[i])
        descending = bool(descent_rate[i] > 100.0)   # ≥100 ft/min

        # Ambient-pressure rate of change (mmHg/s). Positive on descent —
        # used by the descent-aperture model to tighten the lumen when
        # pressure is rising fast (viscoelastic mucosal response).
        rate_mmHg_s = float(p_ambient[i] - p_ambient[i - 1]) / max(dt, 1e-9)

        # --- 1) trans-mucosal + optional trans-TM / trans-RW drift -------
        if gas_exchange_full:
            me.gas = full_gas_exchange_step(me.gas, dt,
                                             include_tm=True, include_rw=True)
        else:
            me.gas = transmucosal_exchange_step(me.gas, dt)
        me.p_me_mmHg = me.gas.total_mmHg()

        # --- 2) Patulous S1 hard-zero override ----------------------------
        if modifiers.is_patulous_patent and not modifiers.patulous_unstable:
            me.p_me_mmHg = p_amb_i
            me.gas = rescale_gas_to_total(me.gas, me.p_me_mmHg)
            me.v_me_effective_ml = effective_me_volume_ml(0.0, patient.anatomy)
            delta_p[i] = 0.0
            p_me[i] = me.p_me_mmHg
            tm_disp[i] = 0.0
            continue

        # --- 3) TM displacement buffer (Boyle update) ---------------------
        # When P_ambient changes by Δ in one step, the ME pressure lags but
        # the TM displaces inward/outward, expanding/compressing V_ME.
        # Instead of a full implicit update, we pre-compute the effective
        # volume from the prior-step ΔP and apply Boyle.
        dp_pre = me.p_me_mmHg - p_amb_i            # provisional ΔP
        v_me_after = effective_me_volume_ml(dp_pre, patient.anatomy)
        p_me_buffered = boyle_update_me_pressure_mmHg(
            me.p_me_mmHg, me.v_me_effective_ml, v_me_after,
        )
        me.p_me_mmHg = p_me_buffered
        me.v_me_effective_ml = v_me_after
        dp = me.p_me_mmHg - p_amb_i

        # --- 4) ET state machine ------------------------------------------
        if step.is_locked and not attempt_unlock(dp, et_eff, modifiers):
            # Locked: no venting. ΔP continues to grow.
            pass
        else:
            if step.is_locked:
                step.is_locked = False

            # Passive opening
            direction = passive_open_direction(dp, et_eff)
            if direction != 0:
                dp = passive_equilibration_mmHg(dp, et_eff)
                et_open[i] = True

            # Update muscle-mechanics adhesion state every step
            update_muscle_state(muscle, t, dp, mechanics)

            # Swallow (active opening) — scheduled by frequency
            sint = swallow_interval_s(et_eff, descending)
            if (t - step.last_swallow_time_s) >= sint:
                jitter = rng.uniform(-0.2, 0.2) * sint
                step.last_swallow_time_s = t + jitter
                muscle_fac = fge_modulation(muscle, t, mechanics, rng=rng)
                dp = active_swallow_equalization(
                    dp, et_eff, modifiers, dt, descending,
                    rate_mmHg_s=rate_mmHg_s,
                    muscle_factor=muscle_fac,
                )
                record_swallow(muscle, t)
                et_open[i] = True
                swallow_events.append(t)

            # Valsalva
            if (
                patient.enable_valsalva
                and (t - step.last_valsalva_time_s) >= patient.valsalva_interval_s
                and descending
            ):
                step.last_valsalva_time_s = t
                dp = valsalva_pressurization_mmHg(
                    dp, et_eff, modifiers, rate_mmHg_s=rate_mmHg_s,
                )
                et_open[i] = True
                valsalva_events.append(t)

            # Recheck lock after opening attempts
            if check_et_lock(dp, et_eff, modifiers):
                step.is_locked = True
                step.lock_time_s = t

        # --- 5) Patulous S2/S3 corrections (after venting/lock logic) -----
        dp = apply_patulous_state(dp, modifiers)

        # --- 6) commit state ---------------------------------------------
        me.p_me_mmHg = p_amb_i + dp
        me.gas = rescale_gas_to_total(me.gas, me.p_me_mmHg)
        me.v_me_effective_ml = effective_me_volume_ml(dp, patient.anatomy)
        delta_p[i] = dp
        p_me[i] = me.p_me_mmHg
        tm_disp[i] = tm_displacement_ml(dp, patient.anatomy)

    # --- assemble trace ------------------------------------------------
    trace = SimulationTrace(
        t_s=t_s,
        altitude_ft=altitude_ft,
        p_ambient_mmHg=p_ambient,
        p_me_mmHg=p_me,
        delta_p_mmHg=delta_p,
        tm_displacement_ml=tm_disp,
        et_open=et_open,
        swallow_events_s=np.asarray(swallow_events, dtype=np.float64),
        valsalva_events_s=np.asarray(valsalva_events, dtype=np.float64),
    )

    # --- score risk (hazard model) -------------------------------------
    from .risk import score_trace
    risk = score_trace(trace, patient, modifiers)

    notes = list(modifiers.notes)
    return SimulationResult(
        trace=trace,
        risk=risk,
        patient=patient,
        profile=profile,
        notes=tuple(notes),
    )
