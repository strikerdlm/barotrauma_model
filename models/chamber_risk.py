"""
Hypobaric chamber barotrauma risk model

This module implements a physiology-informed, physics-constrained simulator to
estimate the risk of middle-ear barotrauma during hypobaric chamber training.

Key concepts
- During descent, ambient pressure rises; if the Eustachian tube (ET) does not
  equalize adequately, middle-ear pressure lags (lower than ambient), the
  tympanic membrane (TM) is pulled inward, and barotrauma risk increases.
- Boyle's law (P·V ≈ constant) implies that without equalization the effective
  middle-ear gas volume is reduced as ambient pressure rises; TM compliance
  limits the apparent volume change but tension rises with |ΔP|.
- ET dysfunction severity reduces equalization speed and increases locking
  thresholds; rapid descent further impairs equalization effectiveness.

This model provides a deterministic approximation suitable for interactive use
in a clinical tool. It avoids stochastic swallow events to ensure reproducible
outputs while preserving physiological trends.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np


# ------------------------------ Configuration ----------------------------- #

ET_SEVERITY_TO_DYSFUNCTION: Dict[str, float] = {
    # Clinical categories mapped to 0-1 dysfunction (0 normal, 1 severe)
    "mild": 0.35,
    "moderate": 0.60,
    "severe": 0.85,
}

# Descent rate safety envelopes (ft/min) by severity
SAFE_DESCENT_RATES: Dict[str, float] = {
    "mild": 2500.0,
    "moderate": 1500.0,
    "severe": 1000.0,
}

CRITICAL_DESCENT_RATES: Dict[str, float] = {
    "mild": 8000.0,
    "moderate": 4000.0,
    "severe": 2500.0,
}

# Thresholds (mmHg)
PASSIVE_OPENING_THRESHOLD = 15.0  # baseline passive ET opening pressure
ET_LOCK_THRESHOLD = 90.0          # ET locking risk threshold
MEMBRANE_RUPTURE_THRESHOLD = 150.0

# Tympanic membrane compliance model
# Choose compliance such that ~100 mmHg yields ~0.3 mL displacement (upper bound)
TM_MAX_DISPLACEMENT_ML = 0.30
TM_COMPLIANCE_ML_PER_MMHG = TM_MAX_DISPLACEMENT_ML / 100.0


def altitude_to_pressure_mmHg(altitude_ft: float) -> float:
    """Standard atmosphere approximation to convert altitude to pressure."""
    P0 = 760.0
    scale_height_ft = 29921.0
    return P0 * np.exp(-altitude_ft / scale_height_ft)


@dataclass
class ChamberScenario:
    """Scenario configuration for hypobaric chamber descent."""
    start_altitude_ft: float = 25000.0
    descent_rate_ft_min: float = 3000.0  # 1000 - 10000 per requirements
    et_severity: str = "moderate"       # "mild" | "moderate" | "severe"
    enable_valsava: bool = True
    valsalva_interval_s: float = 120.0   # frequency to attempt valsalva

    # Anatomy (can be tuned per patient if desired)
    tympanum_volume_ml: float = 1.0
    mastoid_volume_ml: float = 7.75

    def validate(self) -> None:
        if self.et_severity not in ET_SEVERITY_TO_DYSFUNCTION:
            raise ValueError("et_severity must be one of: mild, moderate, severe")
        if not (1000.0 <= self.descent_rate_ft_min <= 10000.0):
            raise ValueError("descent_rate_ft_min must be between 1000 and 10000 ft/min")
        if self.start_altitude_ft <= 0:
            raise ValueError("start_altitude_ft must be positive")
        if self.valsalva_interval_s <= 0:
            raise ValueError("valsalva_interval_s must be positive")


@dataclass
class ChamberResult:
    time_s: np.ndarray
    altitude_ft: np.ndarray
    P_amb_mmHg: np.ndarray
    P_ME_mmHg: np.ndarray
    delta_P_mmHg: np.ndarray
    tm_displacement_ml: np.ndarray
    equalization_rate_mmHg_s: np.ndarray
    risk_score: float
    risk_category: str
    metrics: Dict[str, float]


class HypobaricChamberRiskModel:
    """
    Deterministic, physiology-informed simulator for chamber descent.

    - Uses a continuous equalization rate that depends on:
      - ET dysfunction severity (slower with worse dysfunction)
      - Descent rate (faster descent impairs equalization effectiveness)
      - Pressure differential |ΔP| (passive opening increases rate above threshold)
      - Optional Valsalva at fixed intervals to temporarily increase equalization rate
    - Applies a simple TM compliance model to estimate displacement (Boyle + compliance)
    - Produces risk metrics and category
    """

    def __init__(self, seed: int | None = None):
        self.rng = np.random.default_rng(seed) if seed is not None else None

    @staticmethod
    def _risk_factor_from_descent(severity: str, descent_rate: float) -> float:
        """Scaled 0-1 risk factor from descent rate vs severity-specific envelope."""
        safe = SAFE_DESCENT_RATES[severity]
        critical = CRITICAL_DESCENT_RATES[severity]
        if descent_rate <= safe:
            return 0.0
        # logarithmic growth up to 1.0 at critical
        ratio = np.clip(descent_rate / safe, 1.0, critical / safe)
        return float(np.log(ratio) / np.log(critical / safe))

    @staticmethod
    def _equalization_speed_mmHg_s(
        dysfunction: float,
        risk_factor: float,
        delta_p_mmHg: float,
        valsalva_boost: float,
    ) -> float:
        """
        Effective equalization speed (mmHg/s):
        - Base speed ~ 1.0 mmHg/s in healthy subjects
        - Scales down with dysfunction and risk_factor
        - Increases with |ΔP| above the passive opening threshold
        - Valsalva temporarily boosts speed
        """
        base_speed = 1.0  # mmHg/s baseline equalization capability
        dysfunction_scale = (
            1.0 - 0.6 * dysfunction
        )  # 1.0 -> 0.46 as dysfunction 0->1
        descent_penalty = (1.0 - 0.7 * risk_factor)   # down to 0.3 at high risk

        pressure_factor = 0.0
        if abs(delta_p_mmHg) > PASSIVE_OPENING_THRESHOLD:
            pressure_factor = 0.5 * (
                (abs(delta_p_mmHg) / PASSIVE_OPENING_THRESHOLD) - 1.0
            )

        speed = base_speed * dysfunction_scale * descent_penalty * (1.0 + pressure_factor)
        return max(0.0, speed * (1.0 + valsalva_boost))

    @staticmethod
    def _tm_displacement_ml(delta_p_mmHg: float) -> float:
        # Linear compliance capped at physiological maximum
        disp = np.clip(delta_p_mmHg * TM_COMPLIANCE_ML_PER_MMHG,
                       -TM_MAX_DISPLACEMENT_ML,
                       TM_MAX_DISPLACEMENT_ML)
        return float(disp)

    @staticmethod
    def _categorize_risk(score: float) -> str:
        if score < 0.3:
            return "Low"
        if score < 0.6:
            return "Moderate"
        return "High"

    def simulate_descent(self, scenario: ChamberScenario) -> ChamberResult:
        scenario.validate()

        dysfunction = ET_SEVERITY_TO_DYSFUNCTION[scenario.et_severity]
        risk_factor = self._risk_factor_from_descent(scenario.et_severity,
                                                     scenario.descent_rate_ft_min)

        # Time grid: simulate descent from start_altitude to sea level at constant rate
        descent_rate_ft_s = scenario.descent_rate_ft_min / 60.0
        total_seconds = int(
            np.ceil(scenario.start_altitude_ft / descent_rate_ft_s)
        )
        t = np.arange(0.0, total_seconds + 1.0, 1.0)

        altitude = np.clip(
            scenario.start_altitude_ft - descent_rate_ft_s * t, 0.0, None
        )
        P_amb = altitude_to_pressure_mmHg(altitude)

        # Initialize ME pressure equal to ambient at top (pre-descent equalized)
        P_ME = np.empty_like(P_amb)
        P_ME[0] = P_amb[0]

        eq_rate_series = np.zeros_like(P_amb)
        tm_disp = np.zeros_like(P_amb)

        last_valsava_time = -1e9
        valsalva_active_window_s = 5.0

        for i in range(1, len(t)):
            dt = t[i] - t[i - 1]
            delta_p = P_ME[i - 1] - P_amb[i]  # negative during descent without equalization

            # Valsalva scheduling
            valsalva_boost = 0.0
            if scenario.enable_valsava:
                if (t[i] - last_valsava_time) >= scenario.valsalva_interval_s:
                    last_valsava_time = t[i]
                if (t[i] - last_valsava_time) <= valsalva_active_window_s:
                    valsalva_boost = 3.0  # 4x speed during active Valsalva

            # Lock condition reduces equalization dramatically
            locked = abs(delta_p) > (ET_LOCK_THRESHOLD / (1.0 + risk_factor))
            lock_penalty = 0.15 if locked else 1.0

            # Equalization speed
            speed = self._equalization_speed_mmHg_s(
                dysfunction=dysfunction,
                risk_factor=risk_factor,
                delta_p_mmHg=delta_p,
                valsalva_boost=valsalva_boost,
            ) * lock_penalty

            # Move P_ME toward P_amb by at most `speed * dt`
            correction = np.clip(
                P_amb[i] - P_ME[i - 1], -speed * dt, speed * dt
            )
            P_ME[i] = P_ME[i - 1] + correction
            eq_rate_series[i] = speed
            tm_disp[i] = self._tm_displacement_ml(P_ME[i] - P_amb[i])

        delta_P = P_ME - P_amb

        # Metrics
        max_abs_dp = float(np.max(np.abs(delta_P)))
        time_above_lock = float(
            np.mean(np.abs(delta_P) > ET_LOCK_THRESHOLD)
        )  # fraction of time
        time_above_rupture = float(np.mean(np.abs(delta_P) > MEMBRANE_RUPTURE_THRESHOLD))
        mean_eq_speed = float(np.mean(eq_rate_series))

        # Risk score: combine normalized components
        # - Peak ΔP (soft cap at rupture threshold)
        peak_component = np.clip(max_abs_dp / MEMBRANE_RUPTURE_THRESHOLD, 0.0, 1.0)
        # - Time above lock
        lock_component = np.clip(time_above_lock * 2.0, 0.0, 1.0)
        # - Descent risk factor
        descent_component = risk_factor
        # - Equalization speed mitigates risk
        mitigation = np.clip(mean_eq_speed / 2.0, 0.0, 1.0)  # 0-1; higher is better

        raw_score = (
            0.45 * peak_component + 0.30 * lock_component + 0.25 * descent_component
        )
        risk_score = float(
            np.clip(raw_score * (1.0 - 0.5 * mitigation), 0.0, 1.0)
        )
        risk_category = self._categorize_risk(risk_score)

        metrics = {
            "max_abs_deltaP_mmHg": max_abs_dp,
            "fraction_time_above_lock": time_above_lock,
            "fraction_time_above_rupture": time_above_rupture,
            "mean_equalization_speed_mmHg_s": mean_eq_speed,
            "descent_risk_factor": descent_component,
        }

        return ChamberResult(
            time_s=t,
            altitude_ft=altitude,
            P_amb_mmHg=P_amb,
            P_ME_mmHg=P_ME,
            delta_P_mmHg=delta_P,
            tm_displacement_ml=tm_disp,
            equalization_rate_mmHg_s=eq_rate_series,
            risk_score=risk_score,
            risk_category=risk_category,
            metrics=metrics,
        )

    def risk_vs_descent_rate(
        self, scenario: ChamberScenario, rates_ft_min: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Convenience function to compute risk across multiple descent rates."""
        scores: List[float] = []
        for r in rates_ft_min:
            s = ChamberScenario(
                start_altitude_ft=scenario.start_altitude_ft,
                descent_rate_ft_min=float(r),
                et_severity=scenario.et_severity,
                enable_valsava=scenario.enable_valsava,
                valsalva_interval_s=scenario.valsalva_interval_s,
                tympanum_volume_ml=scenario.tympanum_volume_ml,
                mastoid_volume_ml=scenario.mastoid_volume_ml,
            )
            res = self.simulate_descent(s)
            scores.append(res.risk_score)
        return rates_ft_min, np.array(scores)


