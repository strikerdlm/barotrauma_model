"""
barotrauma.v2.et_dynamics
=========================

Eustachian-tube mechanics: passive opening, active (muscle-assisted) opening
driven by swallow events and Valsalva, Patulous-ET state handling, and the
ascent/descent asymmetric aperture model introduced in v2.1.

Asymmetry (physiology)
----------------------
- **Ascent** (positive ΔP, ME > ambient): Boyle's law buffers the ME as ambient
  drops; the TM pushes outward, expanding V_ME and relieving some overpressure.
  More importantly, the ME overpressure pushes OUT against the cartilaginous
  portion of the ET, opening it passively at P_O' ≈ 26 mmHg and dumping excess
  gas ME → NP. Net: trivial clearance, ΔP bounded near P_O'.
- **Descent** (negative ΔP, ambient > ME): the ME underpressure pulls the TM
  IN, shrinking V_ME; ambient rises faster than Boyle can offset. The
  nasopharyngeal tissue pressure now COLLAPSES the cartilaginous ET lumen from
  the NP side. Passive opening is NOT possible from this direction — only
  active nasopharyngeal overpressure (Valsalva, Toynbee, mTVP activation via
  swallowing) can force the tube open, and each such attempt fights progressive
  lumen collapse. Hagen-Poiseuille flow scales as r^4, so a modest radius drop
  translates into a dramatic flow reduction.

``aperture_factor()`` models this continuous NP-side collapse as a steep Hill
function of |ΔP|, further tightened by the instantaneous pressure-change rate
(mucosal viscoelastic response). All clearance paths (active swallow,
Valsalva) multiply their effective FGE by the aperture factor, reproducing the
clinical observation that rapid chamber descents produce disproportionately
more barotrauma than slow descents of equivalent total ΔP.

Physics also follows Kanick & Doyle 2005 with post-2005 refinements:
- Alper 2020 (PMID 32176133) paired pre/post-BDET P_O' / P_C' distributions.
- Mandel 2016 (PMID 26626132) per-swallow Fractional Gradient Equalized.
- Ghadiali group time-varying R_A (Ghadiali 2010 PMID 20413236; Malik &
  Ghadiali 2019 PMID 29395489) inspires the rate-dependent aperture term;
  full FEM is out of scope.

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
    prev_delta_p_mmHg: float = 0.0        # for rate estimation


# --------------------------------------- ascent/descent asymmetric aperture -
# Anchors chosen so that at moderate |ΔP| (below ~60 mmHg) the tube flows
# close to unimpeded — this preserves the Kanick-Doyle healthy-ear behavior
# (<15 mmHg ΔP at 300 ft/min airline descent) — while retaining steep
# collapse at the high-|ΔP| regime where swallow clearance starts failing.
APERTURE_FREE_ZONE_MMHG: float = 40.0      # below this, aperture = 1.0
APERTURE_HALF_MMHG: float = 110.0          # half-aperture point on descent
APERTURE_HILL_N: float = 3.0               # steepness beyond the free zone
APERTURE_RATE_COEF: float = 0.15           # tightening per mmHg/s rate
APERTURE_RATE_CAP_MMHG_S: float = 3.0      # clip rate contribution at ~7000 ft/min


def aperture_factor(
    delta_p_mmHg: float,
    rate_mmHg_s: float,
    et: EtFunction,
    modifiers: Modifiers,
) -> float:
    """
    Effective ET lumen patency on the NP side, returned as the multiplicative
    factor applied to all active clearance attempts (swallow FGE, Valsalva
    push, etc.). Range [0, 1]; 1.0 means the tube opens and flows freely,
    0.0 means the tube is fully collapsed.

    Mechanism
    ---------
    On **ascent** (ΔP > 0) the tube pops open passively from the ME side and
    vents cheaply; aperture is effectively 1.0 (clearance is limited by P_O'
    and P_C' in ``passive_equilibration_mmHg``, not by aperture).

    On **descent** (ΔP < 0) the NP tissue pressure compresses the
    cartilaginous lumen. Aperture follows a Hill function of |ΔP| centered
    on an individual half-aperture threshold. Inflammation (URI, CRS)
    tightens the threshold — mucosal edema collapses the tube at lower
    applied ΔP. Rapid pressure change (dP/dt) additionally tightens the
    threshold because the mucosa's viscoelastic response lags, concentrating
    stress on the collapsible segment.

    Patulous-S1 patients have the opposite behavior (aperture saturated at
    1.0 across all descent profiles); this is handled in engine.py with a
    hard-zero override and is not re-duplicated here.
    """
    # Ascent: cheap passive venting — full aperture for active pathways too.
    if delta_p_mmHg >= 0:
        return 1.0

    abs_dp = -delta_p_mmHg

    # Inflammation tightens: sqrt damping keeps the effect meaningful without
    # runaway collapse at very high ra_mult values.
    inflammation_tightening = max(1.0, modifiers.ra_mult) ** 0.5

    # Rate tightening: faster pressure growth -> lower effective ΔP_half.
    r = max(0.0, min(rate_mmHg_s, APERTURE_RATE_CAP_MMHG_S))
    rate_tightening = 1.0 + APERTURE_RATE_COEF * r

    free_zone = APERTURE_FREE_ZONE_MMHG / inflammation_tightening
    if abs_dp <= free_zone:
        return 1.0

    dp_half = APERTURE_HALF_MMHG / (inflammation_tightening * rate_tightening)
    excess = abs_dp - free_zone
    half_excess = max(dp_half - free_zone, 1.0)
    return 1.0 / (1.0 + (excess / half_excess) ** APERTURE_HILL_N)


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
    rate_mmHg_s: float = 0.0,
    muscle_factor: float = 1.0,
) -> float:
    """
    Gas transfer during a single swallow-induced active opening.

    Uses the Fractional Gradient Equalized approach (Mandel 2016) scaled by
    severity and URI modifiers, further modulated by the NP-side aperture
    factor (``aperture_factor``) so that descent-rate-dependent lumen
    collapse progressively defeats each swallow's ability to equalize, and
    — since v2.2 — by an optional muscle-mechanics factor reflecting
    TVP/LVP timing, fatigue, and mucosal adhesion (Ghadiali-group FEM).

    Parameters
    ----------
    muscle_factor : float
        Multiplier from ``et_muscle.fge_modulation``. 1.0 = baseline
        v2.1 behavior; <1.0 = adhesion-penalized; >1.0 = priming-boosted.
        Bypass with default 1.0 to preserve v2.1 parity.

    Returns
    -------
    float
        New ΔP (mmHg) after the swallow event.
    """
    fge = et.fge_controls
    fge = max(0.0, min(1.0, fge))
    # Convert the Kanick-Doyle active-resistance/open-duration parameters into
    # a relative conductance multiplier. Baseline EtFunction values preserve the
    # published FGE; higher R_A or shorter openings reduce the delivered bolus.
    baseline_conductance = C.ET_ACTIVE_OPEN_DURATION_S / C.ET_ACTIVE_RESISTANCE_MMHG_ML_MIN
    conductance = et.active_open_duration_s / et.active_resistance_mmHg_ml_min
    flow_factor = conductance / max(baseline_conductance, 1e-12)
    fge *= max(0.0, min(4.0, flow_factor))
    # Aperture-limited effective clearance (Hagen-Poiseuille-informed)
    fge *= aperture_factor(delta_p_mmHg, rate_mmHg_s, et, modifiers)
    # Ghadiali FEM muscle modulation (v2.2)
    fge *= max(0.0, min(2.0, muscle_factor))
    fge = min(1.0, fge)
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
    rate_mmHg_s: float = 0.0,
) -> float:
    """
    Simulate a successful Valsalva pulse: if the Valsalva-generated NP pressure
    overcomes the NP-side ET opening threshold (adjusted for Valsalva shift),
    gas flows NP→ME and ΔP is brought toward zero.

    Valsalva efficacy is modulated by URI/PET modifiers AND by the
    descent-aperture factor — a fast-growing |ΔP| collapses the lumen faster
    than the Valsalva pulse can reopen it, so each unsuccessful Valsalva
    contributes progressively less.
    """
    # Probability of success — Kanick-Doyle passive NP threshold + Valsalva bonus
    np_threshold = et.passive_opening_mmHg_np + C.VALSALVA_OPENING_SHIFT_MMHG

    # Valsalva-induced P_NP excess (a bolus ~50 mmHg in typical subjects).
    valsalva_push_mmHg = 50.0 * modifiers.valsalva_mult

    if -delta_p_mmHg > np_threshold - valsalva_push_mmHg:
        # Valsalva delivers forcible NP overpressure capable of clearing 50-70%
        # of the gradient per successful pulse (literature; not the 32% FGE
        # baseline that applies to passive swallows). Aperture scaling is
        # square-rooted because the muscular push can partially override
        # progressive lumen collapse — brute-force reopening — so Valsalva
        # degrades less sharply than a passive swallow as aperture narrows.
        valsalva_base = 0.55 * modifiers.valsalva_mult
        ap = aperture_factor(delta_p_mmHg, rate_mmHg_s, et, modifiers)
        fge = min(1.0, valsalva_base * (ap ** 0.5))
        return delta_p_mmHg * (1.0 - fge)
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
