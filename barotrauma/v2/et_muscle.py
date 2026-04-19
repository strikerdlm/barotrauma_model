"""
barotrauma.v2.et_muscle
=======================

Ghadiali-FEM-inspired time-varying Eustachian-tube muscle mechanics, added
in v2.2 as an optional extension to the v2.1 constant-R_A baseline.

What it adds
------------
The Kanick-Doyle 2005 active opening model uses a single effective active
resistance R_A (mmHg·mL⁻¹·min⁻¹) that is constant across the ~250 ms
swallow window. Ghadiali-group FEM and multi-scale work (Ghadiali 2010
PMID 20413236; Sheer 2012 PMID 21996354; Malik & Ghadiali 2019
PMID 29395489) demonstrated that R_A is highly time-varying during
tensor-veli-palatini (TVP) and levator-veli-palatini (LVP) contraction,
and is further modulated by two slower effects:

1. **Mucosal adhesion buildup** when the ET has not opened in a while
   (intraluminal surface tension brings opposing mucosal surfaces
   together, raising the force required for next opening).
2. **Cartilage viscoelasticity** — rapid reopening after a recent swallow
   is easier than the same opening from a long-resting state.

This module implements a lumped-parameter approximation that captures the
*effect* of these FEM findings on the per-swallow Fractional Gradient
Equalized (FGE), without running a full FEM at each simulation step.

Approach
--------
The per-swallow FGE is modulated by three time-dependent factors:

- **fatigue factor** f_fat(t_since_last): the more recent the last swallow,
  the more "primed" the ET is, so FGE is higher. Model as exponential
  saturation to a plateau at τ ≈ 8 s.
- **adhesion factor** f_adh(t_since_last, |ΔP|): prolonged closure at
  high |ΔP| increases surface tension; f_adh decays with time-closed.
- **muscle timing factor** f_tim: TVP-LVP synchrony. Healthy subjects
  randomize within a narrow range (0.9–1.1 multiplier); dysfunctional
  coordination (pediatric, AR, post-URI) broadens it downward.

Default values reproduce v2.1's constant-R_A behavior when all factors
are at baseline, i.e. the extension is backward-compatible when disabled
on ``MuscleMechanics(enabled=False)``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# ---------------------------------------- mechanics parameters --------
@dataclass(frozen=True)
class MuscleMechanics:
    """
    Tunable Ghadiali-inspired muscle-mechanics config. Holding ``enabled``
    False makes ``fge_modulation`` return 1.0 (no effect), preserving
    v2.1 behavior exactly.
    """

    enabled: bool = False

    # Fatigue / priming — rate at which FGE rises toward plateau after a
    # previous swallow
    fatigue_tau_s: float = 8.0
    fatigue_peak_boost: float = 0.15      # fraction above baseline FGE

    # Adhesion buildup — rate at which FGE decays when ET has not opened
    adhesion_tau_s: float = 30.0          # time constant for surface-tension buildup
    adhesion_max_penalty: float = 0.35    # max fractional penalty on FGE
    adhesion_dp_scale_mmHg: float = 60.0  # |ΔP| at which adhesion penalty saturates

    # TVP-LVP timing variability — default 1.0 (healthy), lowered by dysfunction
    timing_mean: float = 1.0
    timing_cv: float = 0.05               # 5% coefficient of variation baseline


def default_healthy_mechanics() -> MuscleMechanics:
    return MuscleMechanics(enabled=True)


def default_dysfunctional_mechanics() -> MuscleMechanics:
    """Poor TVP-LVP synchrony (pediatric, AR, post-URI)."""
    return MuscleMechanics(
        enabled=True,
        fatigue_peak_boost=0.08,          # less priming benefit
        adhesion_max_penalty=0.50,        # more adhesion buildup
        timing_mean=0.85,
        timing_cv=0.15,
    )


# ------------------------------------------- state tracker ------------
@dataclass
class MuscleState:
    """Per-patient transient state used by the engine loop."""

    t_last_swallow_s: float = -1e9
    cumulative_adhesion: float = 0.0       # 0 = no adhesion, 1 = full


def update_state(
    state: MuscleState,
    t_now_s: float,
    delta_p_mmHg: float,
    mechanics: MuscleMechanics,
) -> MuscleState:
    """
    Step the adhesion state forward in time. Called each integrator step.
    Doesn't allocate a new dataclass — mutates in place for hot-loop
    performance.
    """
    if not mechanics.enabled:
        return state

    dt = t_now_s - state.t_last_swallow_s
    if dt < 0:
        return state

    # Adhesion rises toward a |ΔP|-scaled ceiling with time constant
    target = 1.0 - 1.0 / (1.0 + abs(delta_p_mmHg) / mechanics.adhesion_dp_scale_mmHg)
    rate = 1.0 - np.exp(-dt / mechanics.adhesion_tau_s)
    state.cumulative_adhesion = state.cumulative_adhesion + rate * (
        target - state.cumulative_adhesion
    )
    state.cumulative_adhesion = float(max(0.0, min(1.0, state.cumulative_adhesion)))
    return state


def record_swallow(state: MuscleState, t_now_s: float) -> MuscleState:
    """Reset adhesion on successful swallow; update last-swallow timestamp."""
    state.t_last_swallow_s = t_now_s
    state.cumulative_adhesion *= 0.2        # successful opening clears most adhesion
    return state


# ------------------------------------------- FGE modulation -----------
def fge_modulation(
    state: MuscleState,
    t_now_s: float,
    mechanics: MuscleMechanics,
    rng: np.random.Generator | None = None,
) -> float:
    """
    Return a multiplicative factor applied to the baseline FGE at the
    moment of a swallow event. When mechanics.enabled is False, returns
    1.0 (no effect on legacy behavior).

    fge_effective = fge_baseline × factor

    where
        factor = fatigue_boost × (1 - adhesion_penalty) × timing_factor
    """
    if not mechanics.enabled:
        return 1.0

    dt = t_now_s - state.t_last_swallow_s
    # Fatigue / priming: recent swallow boosts FGE up to +peak_boost at plateau
    fatigue_factor = 1.0 + mechanics.fatigue_peak_boost * (
        1.0 - np.exp(-max(0.0, dt) / mechanics.fatigue_tau_s)
    )

    # Adhesion penalty: accumulated during the time-closed interval
    adhesion_penalty = mechanics.adhesion_max_penalty * state.cumulative_adhesion
    adhesion_factor = 1.0 - adhesion_penalty

    # Timing variability (stochastic unless rng=None)
    if rng is None:
        timing_factor = mechanics.timing_mean
    else:
        timing_factor = float(rng.normal(
            loc=mechanics.timing_mean,
            scale=mechanics.timing_mean * mechanics.timing_cv,
        ))
        timing_factor = max(0.3, timing_factor)         # clamp

    return float(max(0.0, min(2.0, fatigue_factor * adhesion_factor * timing_factor)))
