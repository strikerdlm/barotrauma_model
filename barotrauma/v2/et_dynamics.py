"""
barotrauma.v2.et_dynamics
=========================

Eustachian-tube mechanics: passive opening, active (muscle-assisted) opening
driven by swallow events and Valsalva, and Patulous-ET state handling.

Physics follows Kanick & Doyle 2005 with post-2005 refinements:
- Alper 2020 (PMID 32176133) paired pre/post-BDET P_O' / P_C' distributions.
- Mandel 2016 (PMID 26626132) per-swallow Fractional Gradient Equalized.
- Ghadiali group time-varying R_A (applied as Valsalva bolus multiplier here;
  full FEM out of scope for v2.0 — see FUTURE_WORK.md).

The module exposes pure numeric functions rather than a class-with-state so the
integrator in ``engine.py`` can call them cheaply in tight loops.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import constants as C
from .pathophysiology import Modifiers
from .types import EtFunction


# ------------------------------------------------------ ET state -------
@dataclass
class EtStepState:
    """Per-step ET state tracked across the integration."""

    last_swallow_time_s: float = -1e9
    last_valsalva_time_s: float = -1e9
    is_locked: bool = False               # persistent ET lock flag
    lock_time_s: float = -1e9


# ---------------------------------------------- passive ET openings ----
def passive_open_direction(
    delta_p_mmHg: float,
    et: EtFunction,
) -> int:
    """
    Determine passive-opening direction for current ΔP = P_ME − P_ambient.

    Per Kanick-Doyle 2005 §"Normal PME regulation during flight": passive
    ET opening happens only on the ME side, when the ME exerts outward force
    greater than the closing force (i.e. during ascent). During descent the
    developing ME underpressure does NOT passively open the tube — opening
    must be active (swallow, Valsalva, or muscle-assisted).

    Returns:
        +1 if ME-side overpressure opens the tube (ascent side).
         0 otherwise — including during descent (use swallow/Valsalva instead).

    NP-side passive opening also exists but requires active nasopharyngeal
    overpressure (Valsalva / muscle). We model that separately in
    ``valsalva_pressurization_mmHg`` rather than here.
    """
    if delta_p_mmHg > et.passive_opening_mmHg_me:
        return +1
    return 0


def passive_equilibration_mmHg(
    delta_p_mmHg: float,
    et: EtFunction,
) -> float:
    """
    Passive ET venting (ME → NP) reduces |ΔP| down to the closing pressure.

    Only fires during ascent (positive ΔP); see ``passive_open_direction``.
    """
    direction = passive_open_direction(delta_p_mmHg, et)
    if direction == 0:
        return delta_p_mmHg
    # direction == +1 → vent ME → NP; residual is Pc' (positive)
    return et.closing_mmHg


# ---------------------------------------- active swallow-driven flow --
def active_swallow_equalization(
    delta_p_mmHg: float,
    et: EtFunction,
    modifiers: Modifiers,
    dt_s: float,
    is_descent: bool,
) -> float:
    """
    Gas transfer during a single swallow-induced active opening.

    Uses the Fractional Gradient Equalized approach (Mandel 2016) scaled by
    severity and URI modifiers. Returns the NEW ΔP (mmHg) after the event.
    """
    fge = et.fge_controls * modifiers.eq_rate_mult
    fge = max(0.0, min(1.0, fge))
    new_delta = delta_p_mmHg * (1.0 - fge)
    return new_delta


def swallow_interval_s(et: EtFunction, is_descent: bool) -> float:
    """Expected interval between swallows, given cruise vs descent rate."""
    sf_per_hr = (
        et.swallow_freq_per_hr_descent if is_descent else et.swallow_freq_per_hr_cruise
    )
    if sf_per_hr <= 0:
        return float("inf")
    return 3600.0 / sf_per_hr


# ----------------------------------------- Valsalva (active NP overpressure) -
def valsalva_pressurization_mmHg(
    delta_p_mmHg: float,
    et: EtFunction,
    modifiers: Modifiers,
) -> float:
    """
    Simulate a successful Valsalva pulse: if the Valsalva-generated NP pressure
    overcomes the NP-side ET opening threshold (adjusted for Valsalva shift),
    gas flows NP→ME and ΔP is brought toward zero.

    Valsalva efficacy is modulated by the URI / PET modifiers.
    """
    # Probability of success — Kanick-Doyle passive NP threshold + Valsalva bonus
    np_threshold = et.passive_opening_mmHg_np + C.VALSALVA_OPENING_SHIFT_MMHG

    # Valsalva-induced P_NP excess (a bolus ~50 mmHg in typical subjects).
    # We represent this as an effective NP-side "push" amplitude.
    valsalva_push_mmHg = 50.0 * modifiers.valsalva_mult

    if -delta_p_mmHg > np_threshold - valsalva_push_mmHg:
        # Sufficient NP overpressure to open the tube. Equalize FGE fraction.
        fge = min(1.0, 0.6 * et.fge_controls * modifiers.valsalva_mult)
        return delta_p_mmHg * (1.0 - fge)
    # Valsalva attempted but failed. No change.
    return delta_p_mmHg


# ------------------------------------------------- ET lock mechanics ---
def check_et_lock(
    delta_p_mmHg: float,
    et: EtFunction,
    modifiers: Modifiers,
) -> bool:
    """
    ET "lock" per Kanick-Doyle: once |ΔP| exceeds an individual-specific
    limit, PET is exerted over a larger collapsible section of the ET lumen,
    which can exceed the maximal force exerted by either the mTVP or active
    NP pressurization. Lock is bounded by muscle + Valsalva capability and
    is approximately constant across obstructive severity; mucosal
    inflammation (URI) tightens it because engorged submucosa collapses at
    lower external ΔP.

    Baseline lock threshold ≈ 90 mmHg (Kanick-Doyle clinical observation).
    """
    BASE_LOCK_MMHG = 90.0
    inflammation_factor = max(1.0, modifiers.ra_mult) ** 0.3
    lock_threshold = BASE_LOCK_MMHG / inflammation_factor
    return abs(delta_p_mmHg) > lock_threshold


def attempt_unlock(
    delta_p_mmHg: float,
    et: EtFunction,
    modifiers: Modifiers,
) -> bool:
    """
    Unlock requires a successful Valsalva with substantial NP overpressure,
    which is harder under inflammation. Probability is non-zero only if the
    current |ΔP| is still within reach of an active-opening attempt.
    """
    UNLOCK_CEILING_MMHG = 200.0
    return bool(
        modifiers.valsalva_mult > 0.7
        and abs(delta_p_mmHg) < UNLOCK_CEILING_MMHG
    )


# ----------------------------------- Patulous-ET specific dynamics ---
def apply_patulous_state(
    delta_p_mmHg: float,
    modifiers: Modifiers,
) -> float:
    """
    In baseline Patulous-ET (S1) the tube is continuously open. We hard-zero
    ΔP every step, reproducing Kanick-Doyle's prediction (protective state).

    S3 (habitual sniffer) biases the resting ME pressure downward by
    PET_S3_RESTING_ME_MMHG_OFFSET, representing the sustained negative pressure
    from repeated active closure.
    """
    if modifiers.is_patulous_patent and not modifiers.patulous_unstable:
        return 0.0

    if modifiers.habitual_sniffer_bias:
        # Shift the baseline ΔP toward the sniff-induced offset without
        # forcing it there (the descent / ascent still dominates dynamics).
        target = C.PET_S3_RESTING_ME_MMHG_OFFSET
        # Exponential relaxation toward the biased baseline; cheap 1-step version
        return 0.8 * delta_p_mmHg + 0.2 * target

    return delta_p_mmHg
