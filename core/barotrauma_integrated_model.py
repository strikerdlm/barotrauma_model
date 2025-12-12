"""core.barotrauma_integrated_model

Integrated model combining a deterministic physics-inspired simulator with
machine learning calibration.

Important:
- This module intentionally uses the **legacy** deterministic simulation stack
  in `models/` because it is covered by the repository's validation tests.
- Simulation outputs are treated as *features* and a *physical prior*; ML models
  learn a calibrated correction on top.

Units
-----
- The underlying `models` simulator returns pressures as **mmH2O**.
- This module converts pressure-derived features to **mmHg** where appropriate
  using 13.6 mmH2O/mmHg.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import joblib
import numpy as np
from numpy.typing import NDArray
from scipy.integrate import trapezoid
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import cross_validate
from sklearn.preprocessing import StandardScaler

from models.barotrauma_simulation import BarotraumaSimulation
from models.flight_profile import FlightProfile
from models.physiology import PhysiologyParameters


FloatArray = NDArray[np.floating[Any]]

_MMHG_TO_MMH2O = 13.6


@dataclass(slots=True)
class SimulationResult:
    """Container for simulation results.

    Attributes:
        time_s: Simulation time in seconds.
        delta_p_mmhg: Middle-ear pressure differential in mmHg.
        risk_factor: Normalized risk proxy in [0, 1].
        risk_score: Scalar score in [0, 1].
        risk_category: Human-readable category derived from `risk_score`.
        gas_exchange_rates_min_inv: Gas exchange rates (min^-1) used by the
            legacy physiology model.
    """

    time_s: FloatArray
    delta_p_mmhg: FloatArray
    risk_factor: FloatArray
    risk_score: float
    risk_category: str
    gas_exchange_rates_min_inv: Mapping[str, float]

    def validate(self) -> None:
        """Validate basic numeric and physiological plausibility.

        Raises:
            ValueError: If arrays are inconsistent or contain non-finite values.
        """
        if self.time_s.ndim != 1 or self.delta_p_mmhg.ndim != 1 or self.risk_factor.ndim != 1:
            raise ValueError("time_s, delta_p_mmhg, and risk_factor must be 1D arrays")
        if not (len(self.time_s) == len(self.delta_p_mmhg) == len(self.risk_factor)):
            raise ValueError("time_s, delta_p_mmhg, and risk_factor must have equal length")

        if len(self.time_s) < 2:
            raise ValueError("simulation must contain at least 2 timepoints")

        if not np.all(np.isfinite(self.time_s)):
            raise ValueError("time_s contains non-finite values")
        if not np.all(np.isfinite(self.delta_p_mmhg)):
            raise ValueError("delta_p_mmhg contains non-finite values")
        if not np.all(np.isfinite(self.risk_factor)):
            raise ValueError("risk_factor contains non-finite values")

        if float(np.min(self.risk_factor)) < 0.0 or float(np.max(self.risk_factor)) > 1.0:
            raise ValueError("risk_factor must be within [0, 1]")
        if not (0.0 <= float(self.risk_score) <= 1.0):
            raise ValueError("risk_score must be within [0, 1]")


class _LRUCache:
    """Small bounded LRU cache for simulation results."""

    def __init__(self, maxsize: int) -> None:
        if maxsize <= 0:
            raise ValueError("maxsize must be positive")
        self._maxsize = int(maxsize)
        self._data: "OrderedDict[str, SimulationResult]" = OrderedDict()

    def get(self, key: str) -> Optional[SimulationResult]:
        if key in self._data:
            self._data.move_to_end(key)
            return self._data[key]
        return None

    def put(self, key: str, value: SimulationResult) -> None:
        self._data[key] = value
        self._data.move_to_end(key)
        if len(self._data) > self._maxsize:
            self._data.popitem(last=False)


def _scenario_cache_key(scenario: Mapping[str, Any]) -> str:
    """Create a stable cache key without recursion."""
    items: List[str] = []
    for k in sorted(scenario.keys()):
        v = scenario.get(k)
        if isinstance(v, (str, int, float, bool)) or v is None:
            items.append(f"{k}={v!r}")
        elif isinstance(v, dict):
            # One-level deep normalization only.
            inner_parts: List[str] = []
            for ik in sorted(v.keys()):
                iv = v.get(ik)
                if isinstance(iv, (str, int, float, bool)) or iv is None:
                    inner_parts.append(f"{ik}={iv!r}")
                else:
                    inner_parts.append(f"{ik}={repr(iv)}")
            inner = ",".join(inner_parts)
            items.append(f"{k}={{ {inner} }}")
        elif isinstance(v, (list, tuple)):
            # One-level deep normalization only.
            parts: List[str] = []
            for iv in v:
                if isinstance(iv, (str, int, float, bool)) or iv is None:
                    parts.append(repr(iv))
                else:
                    parts.append(repr(iv))
            items.append(f"{k}=[{','.join(parts)}]")
        else:
            items.append(f"{k}={repr(v)}")
    return "|".join(items)


class IntegratedBarotraumaModel:
    """Integrated model: deterministic simulation + ML calibration.

    This class is designed to be robust in interactive settings:
    - bounded simulation caching
    - explicit validation
    - deterministic ML via fixed random_state
    """

    def __init__(self, physical_weight: float = 0.6, simulation_cache_maxsize: int = 256) -> None:
        if not (0.0 <= float(physical_weight) <= 1.0):
            raise ValueError("physical_weight must be within [0, 1]")
        self.physical_weight = float(physical_weight)
        self.ml_weight = 1.0 - float(physical_weight)

        self.rf_classifier = RandomForestClassifier(
            n_estimators=200,
            max_depth=8,
            min_samples_split=10,
            random_state=42,
        )
        self.gb_classifier = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42,
        )
        self.scaler = StandardScaler()

        self.calibrated_rf: Optional[CalibratedClassifierCV] = None
        self.calibrated_gb: Optional[CalibratedClassifierCV] = None

        self._cache = _LRUCache(maxsize=int(simulation_cache_maxsize))
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _categorize_risk(score: float) -> str:
        if score < 0.3:
            return "Low"
        if score < 0.6:
            return "Moderate"
        return "High"

    @staticmethod
    def _get_float(scenario: Mapping[str, Any], keys: Sequence[str], default: float) -> float:
        for k in keys:
            if k in scenario and scenario[k] is not None:
                return float(scenario[k])
        return float(default)

    def validate_scenario(self, scenario: Mapping[str, Any]) -> Dict[str, Any]:
        """Validate a scenario.

        Returns:
            dict with keys: valid (bool), messages (list[str]).
        """
        messages: List[str] = []
        valid = True

        et = scenario.get("et_dysfunction", None)
        try:
            et_val = float(et) if et is not None else 0.0
        except (TypeError, ValueError) as e:
            valid = False
            messages.append(f"et_dysfunction is not a number: {e}")
            et_val = 0.0

        if not (0.0 <= et_val <= 1.0):
            valid = False
            messages.append("ET dysfunction must be between 0 and 1")

        climb = self._get_float(scenario, ["climb_rate_ft_min", "ascent_rate_ft_min", "ascent_rate"], 2000.0)
        descent = self._get_float(scenario, ["descent_rate_ft_min", "descent_rate"], 1500.0)
        cruise = self._get_float(scenario, ["cruise_duration_min", "cruise_duration"], 120.0)
        alt = self._get_float(scenario, ["final_altitude_ft", "cruise_altitude_ft", "cruise_altitude"], 35000.0)

        if climb <= 0.0:
            valid = False
            messages.append("climb_rate_ft_min/ascent_rate must be positive")
        if descent <= 0.0:
            valid = False
            messages.append("descent_rate_ft_min must be positive")
        if cruise < 0.0:
            valid = False
            messages.append("cruise_duration_min must be non-negative")
        if alt <= 0.0:
            valid = False
            messages.append("cruise_altitude_ft/final_altitude_ft must be positive")

        dt_min = self._get_float(scenario, ["dt_min"], 0.1)
        if dt_min <= 0.0:
            valid = False
            messages.append("dt_min must be positive")
        if dt_min > 5.0:
            valid = False
            messages.append("dt_min is too large for meaningful simulation (>5 minutes)")

        return {"valid": valid, "messages": messages}

    def _simulate_scenario(self, scenario: Mapping[str, Any]) -> Optional[SimulationResult]:
        """Run deterministic simulation and post-process outputs."""
        v = self.validate_scenario(scenario)
        if not bool(v["valid"]):
            self.logger.warning("Scenario validation failed: %s", v["messages"])
            return None

        cache_key = _scenario_cache_key(scenario)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            et = float(scenario.get("et_dysfunction", 0.0))
            cruise_alt = self._get_float(
                scenario,
                ["final_altitude_ft", "cruise_altitude_ft", "cruise_altitude"],
                35000.0,
            )
            ascent = self._get_float(scenario, ["climb_rate_ft_min", "ascent_rate_ft_min", "ascent_rate"], 2000.0)
            descent = self._get_float(scenario, ["descent_rate_ft_min", "descent_rate"], 1500.0)
            cruise_dur = self._get_float(scenario, ["cruise_duration_min", "cruise_duration"], 120.0)
            dt_min = self._get_float(scenario, ["dt_min"], 0.1)

            flight = FlightProfile(
                cruise_altitude=float(cruise_alt),
                ascent_rate=float(ascent),
                descent_rate=float(descent),
                cruise_duration=float(cruise_dur),
                et_dysfunction=float(et),
            )

            physiology = PhysiologyParameters()
            sim = BarotraumaSimulation(flight=flight, physiology=physiology)
            results = sim.run_simulation(dt=float(dt_min))

            time_s = np.asarray(results["time"], dtype=np.float64)
            dp_mmh2o = np.asarray(results["dP"], dtype=np.float64)
            risk_factor = np.asarray(results["risk_factor"], dtype=np.float64)

            dp_mmhg = dp_mmh2o / _MMHG_TO_MMH2O
            risk_score = float(np.clip(float(np.max(risk_factor)), 0.0, 1.0))
            risk_category = self._categorize_risk(risk_score)

            sim_result = SimulationResult(
                time_s=time_s,
                delta_p_mmhg=dp_mmhg,
                risk_factor=risk_factor,
                risk_score=risk_score,
                risk_category=risk_category,
                gas_exchange_rates_min_inv={
                    "O2": float(physiology.k_O2),
                    "CO2": float(physiology.k_CO2),
                    "N2": float(physiology.k_N2),
                    "H2O": float(physiology.k_H2O),
                },
            )
            sim_result.validate()
            self._cache.put(cache_key, sim_result)
            return sim_result
        except (KeyError, TypeError, ValueError) as e:
            self.logger.error("Simulation error: %s", e)
            return None

    def _extract_features(self, scenario: Mapping[str, Any]) -> Optional[FloatArray]:
        """Extract ML features from a scenario and its simulation."""
        sim_result = self._simulate_scenario(scenario)
        if sim_result is None:
            return None

        dp = sim_result.delta_p_mmhg
        t_s = sim_result.time_s
        if len(t_s) < 2:
            return None

        # Derivatives are computed w.r.t. seconds.
        dp_rate = np.gradient(dp, t_s)

        features: List[float] = [
            float(scenario.get("et_dysfunction", 0.0)),
            float(np.max(np.abs(dp))),
            float(np.mean(dp)),
            float(np.std(dp)),
            float(np.max(np.abs(dp_rate))),
            float(np.mean(sim_result.risk_factor)),
            float(np.max(sim_result.risk_factor)),
            float(sim_result.gas_exchange_rates_min_inv.get("O2", 0.0)),
            float(sim_result.gas_exchange_rates_min_inv.get("CO2", 0.0)),
            float(sim_result.gas_exchange_rates_min_inv.get("N2", 0.0)),
            float(sim_result.gas_exchange_rates_min_inv.get("H2O", 0.0)),
        ]
        return np.asarray(features, dtype=np.float64)

    def fit(
        self,
        scenarios: Sequence[Mapping[str, Any]],
        labels: NDArray[np.integer[Any]] | NDArray[np.bool_],
        validation_data: Optional[Tuple[Sequence[Mapping[str, Any]], NDArray[np.integer[Any]] | NDArray[np.bool_]]] = None,
    ) -> Dict[str, Any]:
        """Train the integrated model.

        Args:
            scenarios: Iterable of scenario dicts.
            labels: Binary labels aligned to `scenarios`.
            validation_data: Optional tuple (val_scenarios, val_labels).

        Returns:
            Training summary dict.
        """
        features: List[FloatArray] = []
        valid_indices: List[int] = []

        for i, scn in enumerate(scenarios):
            fv = self._extract_features(scn)
            if fv is not None:
                features.append(fv)
                valid_indices.append(i)

        if not features:
            raise ValueError("No valid features extracted")

        X = np.vstack(features)
        y = np.asarray(labels)[valid_indices]

        Xs = self.scaler.fit_transform(X)

        self.calibrated_rf = CalibratedClassifierCV(self.rf_classifier, cv=5, method="sigmoid")
        self.calibrated_rf.fit(Xs, y)

        self.calibrated_gb = CalibratedClassifierCV(self.gb_classifier, cv=5, method="sigmoid")
        self.calibrated_gb.fit(Xs, y)

        cv_results = cross_validate(
            self.rf_classifier,
            Xs,
            y,
            cv=5,
            scoring=["roc_auc", "accuracy", "precision", "recall"],
        )

        validation_metrics: Dict[str, float] = {}
        if validation_data is not None:
            val_scenarios, val_labels = validation_data
            val_features: List[FloatArray] = []
            val_valid: List[int] = []
            for i, scn in enumerate(val_scenarios):
                fv = self._extract_features(scn)
                if fv is not None:
                    val_features.append(fv)
                    val_valid.append(i)

            if val_features:
                Xv = np.vstack(val_features)
                Xv = self.scaler.transform(Xv)
                yv = np.asarray(val_labels)[val_valid]

                rf_val = self.calibrated_rf.predict_proba(Xv)[:, 1]
                gb_val = self.calibrated_gb.predict_proba(Xv)[:, 1]
                validation_metrics = {
                    "rf_val_auc": float(roc_auc_score(yv, rf_val)),
                    "gb_val_auc": float(roc_auc_score(yv, gb_val)),
                }

        return {"cv_results": cv_results, "validation_metrics": validation_metrics, "n_samples": int(len(X))}

    def predict(
        self, scenarios: Sequence[Mapping[str, Any]], return_uncertainty: bool = False
    ) -> Tuple[FloatArray, Optional[FloatArray]]:
        """Predict risk scores.

        Returns arrays aligned to the input ordering. Scenarios that fail validation
        or simulation return NaN.
        """
        if self.calibrated_rf is None or self.calibrated_gb is None:
            raise ValueError("Model not trained")

        n = len(scenarios)
        preds = np.full((n,), np.nan, dtype=np.float64)
        unc = np.full((n,), np.nan, dtype=np.float64) if return_uncertainty else None

        feature_rows: List[FloatArray] = []
        physical_scores: List[float] = []
        valid_positions: List[int] = []

        for i in range(n):
            scn = scenarios[i]
            sim_res = self._simulate_scenario(scn)
            fv = self._extract_features(scn)
            if sim_res is None or fv is None:
                continue
            feature_rows.append(fv)
            physical_scores.append(float(sim_res.risk_score))
            valid_positions.append(i)

        if not feature_rows:
            return preds, unc

        X = np.vstack(feature_rows)
        X = self.scaler.transform(X)

        rf_pred = self.calibrated_rf.predict_proba(X)[:, 1]
        gb_pred = self.calibrated_gb.predict_proba(X)[:, 1]
        ml_pred = 0.5 * (rf_pred + gb_pred)

        physical = np.asarray(physical_scores, dtype=np.float64)
        final = (self.physical_weight * physical) + (self.ml_weight * ml_pred)

        for j, pos in enumerate(valid_positions):
            preds[pos] = float(np.clip(final[j], 0.0, 1.0))

        if return_uncertainty and unc is not None:
            model_disagreement = np.abs(rf_pred - gb_pred)
            physical_ml_disagreement = np.abs(physical - ml_pred)
            u = np.sqrt(0.5 * model_disagreement**2 + 0.5 * physical_ml_disagreement**2)
            for j, pos in enumerate(valid_positions):
                unc[pos] = float(np.clip(u[j], 0.0, 1.0))

        return preds, unc

    def save_model(self, path: Path) -> None:
        """Save the trained model."""
        if self.calibrated_rf is None or self.calibrated_gb is None:
            raise ValueError("Model not trained")
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "rf_model": self.calibrated_rf,
                "gb_model": self.calibrated_gb,
                "scaler": self.scaler,
                "physical_weight": self.physical_weight,
            },
            path,
        )

    def load_model(self, path: Path) -> None:
        """Load a previously saved model."""
        model_data = joblib.load(path)
        self.calibrated_rf = model_data["rf_model"]
        self.calibrated_gb = model_data["gb_model"]
        self.scaler = model_data["scaler"]
        self.physical_weight = float(model_data["physical_weight"])
        self.ml_weight = 1.0 - self.physical_weight

    def analyze_feature_importance(self) -> Dict[str, float]:
        """Estimate feature importance from the fitted base estimators.

        Notes:
            With `CalibratedClassifierCV`, the fitted estimators live inside
            `calibrated_classifiers_`. We compute the mean importance across folds.
        """
        if self.calibrated_rf is None or self.calibrated_gb is None:
            raise ValueError("Model must be trained before analyzing feature importance")

        feature_names = [
            "et_dysfunction",
            "dp_abs_max_mmhg",
            "dp_mean_mmhg",
            "dp_std_mmhg",
            "dp_rate_abs_max_mmhg_s",
            "risk_factor_mean",
            "risk_factor_max",
            "k_O2_min_inv",
            "k_CO2_min_inv",
            "k_N2_min_inv",
            "k_H2O_min_inv",
        ]

        rf_imps: List[np.ndarray] = []
        for cc in getattr(self.calibrated_rf, "calibrated_classifiers_", []):
            est = getattr(cc, "estimator", None)
            imp = getattr(est, "feature_importances_", None)
            if imp is not None:
                rf_imps.append(np.asarray(imp, dtype=np.float64))

        gb_imps: List[np.ndarray] = []
        for cc in getattr(self.calibrated_gb, "calibrated_classifiers_", []):
            est = getattr(cc, "estimator", None)
            imp = getattr(est, "feature_importances_", None)
            if imp is not None:
                gb_imps.append(np.asarray(imp, dtype=np.float64))

        if not rf_imps or not gb_imps:
            raise ValueError("Feature importances are unavailable for the fitted estimators")

        rf_mean = np.mean(np.vstack(rf_imps), axis=0)
        gb_mean = np.mean(np.vstack(gb_imps), axis=0)

        combined = 0.6 * rf_mean + 0.4 * gb_mean
        s = float(np.sum(combined))
        if s <= 0.0:
            raise ValueError("Non-positive total feature importance")

        normalized = combined / s
        return dict(zip(feature_names, normalized.tolist()))

    def analyze_prediction_confidence(self, scenario: Mapping[str, Any]) -> Dict[str, Any]:
        """Analyze confidence in a single scenario prediction."""
        sim_result = self._simulate_scenario(scenario)
        if sim_result is None:
            return {"confidence": 0.0, "reason": "Simulation failed"}

        if self.calibrated_rf is None or self.calibrated_gb is None:
            return {"confidence": 0.0, "reason": "Model not trained"}

        fv = self._extract_features(scenario)
        if fv is None:
            return {"confidence": 0.0, "reason": "Feature extraction failed"}

        X = self.scaler.transform(fv.reshape(1, -1))
        rf_pred = float(self.calibrated_rf.predict_proba(X)[0, 1])
        gb_pred = float(self.calibrated_gb.predict_proba(X)[0, 1])

        pred_diff = abs(rf_pred - gb_pred)
        ml_confidence = float(np.clip(1.0 - pred_diff, 0.0, 1.0))
        phys_confidence = float(np.clip(1.0 - abs(0.5 - sim_result.risk_score), 0.0, 1.0))

        combined = (self.physical_weight * phys_confidence) + (self.ml_weight * ml_confidence)

        return {
            "confidence": float(np.clip(combined, 0.0, 1.0)),
            "physical_confidence": phys_confidence,
            "ml_confidence": ml_confidence,
            "model_agreement": float(np.clip(1.0 - pred_diff, 0.0, 1.0)),
            "risk_score": float(sim_result.risk_score),
            "risk_category": str(sim_result.risk_category),
        }

    def get_feature_ranges(self) -> Dict[str, Tuple[float, float]]:
        """Return conservative feature ranges (for UI validation)."""
        return {
            "et_dysfunction": (0.0, 1.0),
            "dp_abs_max_mmhg": (0.0, 300.0),
            "dp_mean_mmhg": (-100.0, 100.0),
            "dp_std_mmhg": (0.0, 100.0),
            "dp_rate_abs_max_mmhg_s": (0.0, 200.0),
            "risk_factor_mean": (0.0, 1.0),
            "risk_factor_max": (0.0, 1.0),
            "k_O2_min_inv": (0.0, 1.0),
            "k_CO2_min_inv": (0.0, 5.0),
            "k_N2_min_inv": (0.0, 0.1),
            "k_H2O_min_inv": (0.0, 10.0),
        }

    @staticmethod
    def calculate_cumulative_exposure(time_s: FloatArray, pressure_mmhg: FloatArray) -> float:
        """Compute cumulative exposure \(\int |\Delta P(t)| dt\)."""
        if len(time_s) != len(pressure_mmhg):
            raise ValueError("time_s and pressure_mmhg must have the same length")
        if len(time_s) < 2:
            return 0.0
        return float(trapezoid(np.abs(pressure_mmhg), time_s))
