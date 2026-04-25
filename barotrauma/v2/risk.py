"""
barotrauma.v2.risk
==================

Dose-response hazard model for middle-ear barotrauma. Three outcome strata
map to ΔP thresholds derived from Kanick-Doyle 2005:

- Barotitis (Teed I+): Θ = 18.4 mmHg  (250 mmH2O)
- Baromyringitis (Teed III–IV):  Θ = 95.6 mmHg  (1300 mmH2O)
- Rupture (Teed V): Θ = 150 mmHg  (conservative TM rupture anchor)

For each stratum i the instantaneous hazard is:

    h_i(t) = r_i · max(0, |ΔP(t)| − Θ_i) ** n_i

and the probability of event i by end of exposure is:

    P_i = 1 − exp(−∫ h_i(t) dt)

Stratum probabilities are then multiplied by the patient's per-descent
relative-risk factor (from the URI × PET × medication pathophysiology
chain) to reflect factors not captured in the ΔP trajectory itself (e.g.
mucosal friability that raises transudate risk at a given ΔP, decongestant
effects on tissue stiffness). The hazard rate constants r_i are calibrated
(see ``calibration.py``) to reproduce the FAC cohort prevalence of 5.8%
per individual over a 10-year career (~3–5 exposures), equivalent to a
per-exposure baseline of ~1.5–2.5% in pre-screened aircrew (Italian AF
Morgagni 2010/2012 per-exposure, see docs/research_notes/04).
"""

from __future__ import annotations

from typing import Sequence

import numpy as np
from numpy.typing import NDArray

from . import constants as C
from .pathophysiology import Modifiers
from .types import PatientState, RiskResult, SimulationTrace


# ----------------------------------------------- dose integration -----
def cumulative_hazard(
    delta_p_mmHg: NDArray[np.float64],
    dt_s: float | NDArray[np.float64],
    threshold_mmHg: float,
    rate: float,
    power: float,
) -> float:
    """∫ r·max(0, |ΔP| − Θ)^n dt, returned in absolute hazard units."""
    excess = np.clip(np.abs(delta_p_mmHg) - threshold_mmHg, 0.0, None)
    weights = np.asarray(dt_s, dtype=np.float64)
    if weights.ndim == 0:
        return float(rate * np.sum(excess ** power) * float(weights))
    if weights.shape != excess.shape:
        raise ValueError("dt_s array must have the same shape as delta_p_mmHg")
    return float(rate * np.sum((excess ** power) * weights))


def probability_from_hazard(cum_hazard: float) -> float:
    """P = 1 − exp(−H). Assumes H ≥ 0."""
    return float(1.0 - np.exp(-max(cum_hazard, 0.0)))


# -------------------------------------- per-exposure risk scoring ----
def score_trace(
    trace: SimulationTrace,
    patient: PatientState,
    modifiers: Modifiers,
) -> RiskResult:
    """
    Score the three hazard strata plus clinical-factor multipliers.

    Returns the ``RiskResult`` with per-stratum probabilities, the max |ΔP|,
    AUC exposures, and a plain-language dominant risk factor.
    """
    dt_s = trace.step_durations_s()
    max_abs_dp = trace.max_abs_delta_p()

    # Baseline hazards from the physics-only ΔP trajectory
    h_baro = cumulative_hazard(
        trace.delta_p_mmHg, dt_s,
        C.BAROTITIS_THRESHOLD_MMHG,
        C.HAZARD_BAROTITIS_R,
        C.HAZARD_BAROTITIS_N,
    )
    h_bmrg = cumulative_hazard(
        trace.delta_p_mmHg, dt_s,
        C.BAROMYRINGITIS_THRESHOLD_MMHG,
        C.HAZARD_BAROMYRINGITIS_R,
        C.HAZARD_BAROMYRINGITIS_N,
    )
    h_rupt = cumulative_hazard(
        trace.delta_p_mmHg, dt_s,
        C.RUPTURE_THRESHOLD_MMHG,
        C.HAZARD_RUPTURE_R,
        C.HAZARD_RUPTURE_N,
    )

    # Pathophysiology relative-risk multiplier (URI, PET, rhinitis, meds).
    # These factors adjust the overall per-exposure probability rather than
    # the physics hazard itself (e.g. friable mucosa transudates more at
    # lower ΔP than healthy mucosa).
    rr = float(max(0.0, modifiers.per_descent_rr))

    # Convert hazards → probabilities, then apply RR (cap at 1.0).
    p_baro = min(1.0, probability_from_hazard(h_baro) * rr)
    p_bmrg = min(1.0, probability_from_hazard(h_bmrg) * rr)
    p_rupt = min(1.0, probability_from_hazard(h_rupt) * rr)

    auc_baro = trace.auc_abs_delta_p(C.BAROTITIS_THRESHOLD_MMHG)
    auc_bmrg = trace.auc_abs_delta_p(C.BAROMYRINGITIS_THRESHOLD_MMHG)

    # Dominant risk factor — pick the biggest contributor for the report.
    dominant = _identify_dominant_risk(patient, modifiers, max_abs_dp)

    # Recommended max descent rate: fit by bisection on the profile's
    # descent rate (not done here to keep score_trace pure; see
    # recommend_max_descent below).
    recommended = _recommend_descent(p_baro, patient.et.severity)

    return RiskResult(
        p_barotitis=p_baro,
        p_baromyringitis=p_bmrg,
        p_rupture=p_rupt,
        max_abs_delta_p_mmHg=max_abs_dp,
        auc_mmHg_s_barotitis=auc_baro,
        auc_mmHg_s_baromyringitis=auc_bmrg,
        dominant_risk_factor=dominant,
        recommended_max_descent_ft_min=recommended,
    )


# ----------------------------------------- dominant-factor helper ----
def _identify_dominant_risk(
    patient: PatientState,
    modifiers: Modifiers,
    max_abs_dp: float,
) -> str:
    """Return a single human-readable label for the biggest risk driver."""
    # Order matters: acute URI dominates, then PET-unstable, then obstruction,
    # then descent physics.
    if patient.uri in ("day_4_7", "day_1_3"):
        return f"Acute URI ({patient.uri})"
    if modifiers.patulous_unstable:
        return "Patulous ET + inflammation (S2)"
    if modifiers.post_plug_stenotic:
        return "Post-plug stenotic ET (S4)"
    if patient.et.severity in ("severe", "moderate"):
        return f"Obstructive ET dysfunction ({patient.et.severity})"
    if patient.uri in ("day_8_14", "day_15_21"):
        return f"Recent URI ({patient.uri})"
    if patient.rhinitis == "chronic_rhinosinusitis":
        return "Chronic rhinosinusitis"
    if patient.rhinitis == "allergic":
        return "Allergic rhinitis"
    if modifiers.habitual_sniffer_bias:
        return "Habitual sniffer (PET-S3)"
    if max_abs_dp > 50.0:
        return "Descent profile pressure exposure"
    return "Baseline"


def _recommend_descent(p_baro: float, severity: str) -> float:
    """
    Back-of-envelope safe descent cap (ft/min) based on p_baro and severity.

    Anchored so that:
      - healthy baseline + low risk → 10,000 ft/min allowed
      - moderate risk → 4,000 ft/min
      - high risk → 1,500 ft/min
      - severe risk → 600 ft/min
    """
    if p_baro < 0.05:
        base = 10000.0
    elif p_baro < 0.20:
        base = 4000.0
    elif p_baro < 0.50:
        base = 1500.0
    else:
        base = 600.0

    severity_penalty = {"normal": 1.0, "mild": 0.75, "moderate": 0.5, "severe": 0.3}
    return base * severity_penalty.get(severity, 1.0)


# ------------------------------------------ Monte-Carlo uncertainty ---
def score_with_uncertainty(
    trace: SimulationTrace,
    patient: PatientState,
    modifiers: Modifiers,
    *,
    n_mc: int = 400,
    rr_cv: float = 0.25,
    rng: np.random.Generator | None = None,
) -> RiskResult:
    """
    Score with Monte-Carlo uncertainty on the RR multiplier. Returns a
    RiskResult with filled 95% CI fields. Useful for clinical reports.
    """
    rng = rng or np.random.default_rng()
    base = score_trace(trace, patient, modifiers)

    # Log-normal jitter on the per-descent RR (cv ~25%).
    rr_samples = rng.lognormal(mean=np.log(max(modifiers.per_descent_rr, 1e-3)),
                                sigma=rr_cv, size=n_mc)

    baro_dist = np.clip(1.0 - (1.0 - base.p_barotitis / max(modifiers.per_descent_rr, 1e-3))
                       ** (rr_samples / max(modifiers.per_descent_rr, 1e-3)), 0.0, 1.0)
    # Simpler: scale the base probability linearly by rr ratio and clip.
    baro_dist = np.clip(base.p_barotitis * (rr_samples / max(modifiers.per_descent_rr, 1e-3)), 0.0, 1.0)
    bmrg_dist = np.clip(base.p_baromyringitis * (rr_samples / max(modifiers.per_descent_rr, 1e-3)), 0.0, 1.0)
    rupt_dist = np.clip(base.p_rupture * (rr_samples / max(modifiers.per_descent_rr, 1e-3)), 0.0, 1.0)

    def ci(x: NDArray[np.float64]) -> tuple[float, float]:
        return (float(np.quantile(x, 0.025)), float(np.quantile(x, 0.975)))

    return RiskResult(
        p_barotitis=float(np.mean(baro_dist)),
        p_baromyringitis=float(np.mean(bmrg_dist)),
        p_rupture=float(np.mean(rupt_dist)),
        max_abs_delta_p_mmHg=base.max_abs_delta_p_mmHg,
        auc_mmHg_s_barotitis=base.auc_mmHg_s_barotitis,
        auc_mmHg_s_baromyringitis=base.auc_mmHg_s_baromyringitis,
        dominant_risk_factor=base.dominant_risk_factor,
        recommended_max_descent_ft_min=base.recommended_max_descent_ft_min,
        ci95_barotitis=ci(baro_dist),
        ci95_baromyringitis=ci(bmrg_dist),
        ci95_rupture=ci(rupt_dist),
    )
