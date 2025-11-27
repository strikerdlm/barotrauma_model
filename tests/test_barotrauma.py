"""
Test script for barotrauma model validation.

Uses the HypobaricChamberRiskModel for testing barotrauma risk predictions.
"""

import numpy as np
import pytest
from typing import Dict

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from barotrauma.models.chamber_risk import (
    HypobaricChamberRiskModel,
    ChamberScenario,
    ET_SEVERITY_TO_DYSFUNCTION,
    ET_LOCK_THRESHOLD,
    MEMBRANE_RUPTURE_THRESHOLD,
)


class TestBasicCases:
    """Test basic cases with known outcomes."""

    def test_low_risk_mild_dysfunction(self) -> None:
        """Test that mild ET dysfunction with slow descent yields low risk."""
        model = HypobaricChamberRiskModel()
        scenario = ChamberScenario(
            start_altitude_ft=25000.0,
            descent_rate_ft_min=1500.0,  # Slow descent
            et_severity="mild",
            enable_valsava=True,
            valsalva_interval_s=60.0,
        )
        result = model.simulate_descent(scenario)

        assert result.risk_score < 0.4, (
            f"Risk too high for mild dysfunction with slow descent: {result.risk_score}"
        )
        assert result.risk_category in ("Low", "Moderate"), (
            f"Unexpected risk category: {result.risk_category}"
        )

    def test_high_risk_severe_dysfunction(self) -> None:
        """Test that severe ET dysfunction with fast descent yields high risk."""
        model = HypobaricChamberRiskModel()
        scenario = ChamberScenario(
            start_altitude_ft=30000.0,
            descent_rate_ft_min=8000.0,  # Fast descent
            et_severity="severe",
            enable_valsava=False,
        )
        result = model.simulate_descent(scenario)

        assert result.risk_score > 0.5, (
            f"Risk too low for severe dysfunction with fast descent: {result.risk_score}"
        )

    def test_risk_increases_with_et_severity(self) -> None:
        """Test that risk increases with ET severity."""
        model = HypobaricChamberRiskModel()
        risks: Dict[str, float] = {}

        for severity in ["mild", "moderate", "severe"]:
            scenario = ChamberScenario(
                start_altitude_ft=25000.0,
                descent_rate_ft_min=4000.0,
                et_severity=severity,
                enable_valsava=True,
            )
            result = model.simulate_descent(scenario)
            risks[severity] = result.risk_score

        assert risks["mild"] <= risks["moderate"], (
            f"Mild risk ({risks['mild']}) should be <= moderate risk ({risks['moderate']})"
        )
        assert risks["moderate"] <= risks["severe"], (
            f"Moderate risk ({risks['moderate']}) should be <= severe risk ({risks['severe']})"
        )


class TestPhysiologicalBounds:
    """Test if model respects physiological constraints."""

    def test_et_lock_threshold(self) -> None:
        """Test ET lock threshold is correctly defined."""
        assert ET_LOCK_THRESHOLD == 90.0, f"Incorrect ET lock threshold: {ET_LOCK_THRESHOLD}"

    def test_membrane_rupture_threshold(self) -> None:
        """Test membrane rupture threshold is correctly defined."""
        assert MEMBRANE_RUPTURE_THRESHOLD == 150.0, (
            f"Incorrect rupture threshold: {MEMBRANE_RUPTURE_THRESHOLD}"
        )

    def test_dysfunction_mapping(self) -> None:
        """Test ET severity to dysfunction mapping."""
        expected = {"mild": 0.35, "moderate": 0.60, "severe": 0.85}
        for severity, expected_value in expected.items():
            actual = ET_SEVERITY_TO_DYSFUNCTION[severity]
            assert actual == expected_value, (
                f"Incorrect dysfunction for {severity}: expected {expected_value}, got {actual}"
            )

    def test_pressure_within_bounds(self) -> None:
        """Test that pressure differentials stay within physiological bounds."""
        model = HypobaricChamberRiskModel()
        # Use typical chamber training altitude (25000 ft) with safe descent rate
        scenario = ChamberScenario(
            start_altitude_ft=25000.0,
            descent_rate_ft_min=2000.0,  # Safe descent rate for moderate dysfunction
            et_severity="moderate",
            enable_valsava=True,
            valsalva_interval_s=60.0,
        )
        result = model.simulate_descent(scenario)

        max_pressure = np.max(np.abs(result.delta_P_mmHg))
        # In controlled descent with Valsalva, pressure should stay manageable
        assert max_pressure < 200.0, f"Pressure differential too high: {max_pressure} mmHg"


class TestRiskCalculations:
    """Test risk calculation components."""

    def test_risk_score_bounds(self) -> None:
        """Test that risk scores are always between 0 and 1."""
        model = HypobaricChamberRiskModel()

        for severity in ["mild", "moderate", "severe"]:
            for descent_rate in [1000, 3000, 5000, 8000, 10000]:
                scenario = ChamberScenario(
                    start_altitude_ft=25000.0,
                    descent_rate_ft_min=float(descent_rate),
                    et_severity=severity,
                    enable_valsava=True,
                )
                result = model.simulate_descent(scenario)

                assert 0.0 <= result.risk_score <= 1.0, (
                    f"Risk score out of bounds: {result.risk_score}"
                )

    def test_metrics_consistency(self) -> None:
        """Test that metrics are consistent with results."""
        model = HypobaricChamberRiskModel()
        scenario = ChamberScenario(
            start_altitude_ft=25000.0,
            descent_rate_ft_min=5000.0,
            et_severity="moderate",
            enable_valsava=True,
        )
        result = model.simulate_descent(scenario)

        # Check metrics exist
        assert "max_abs_deltaP_mmHg" in result.metrics
        assert "fraction_time_above_lock" in result.metrics
        assert "fraction_time_above_rupture" in result.metrics

        # Validate metric values
        assert result.metrics["max_abs_deltaP_mmHg"] == np.max(np.abs(result.delta_P_mmHg))
        assert 0.0 <= result.metrics["fraction_time_above_lock"] <= 1.0
        assert 0.0 <= result.metrics["fraction_time_above_rupture"] <= 1.0


class TestDescentRateSensitivity:
    """Test sensitivity to descent rate changes."""

    def test_risk_increases_with_descent_rate(self) -> None:
        """Test that risk generally increases with descent rate."""
        model = HypobaricChamberRiskModel()
        rates = [1500, 3000, 5000, 7000, 9000]
        risks = []

        for rate in rates:
            scenario = ChamberScenario(
                start_altitude_ft=25000.0,
                descent_rate_ft_min=float(rate),
                et_severity="moderate",
                enable_valsava=True,
            )
            result = model.simulate_descent(scenario)
            risks.append(result.risk_score)

        # Risk should generally trend upward (allowing some tolerance)
        assert risks[-1] >= risks[0], (
            f"Risk should increase with descent rate: {risks[0]} -> {risks[-1]}"
        )

    def test_valsalva_reduces_risk(self) -> None:
        """Test that Valsalva maneuvers reduce risk."""
        model = HypobaricChamberRiskModel()

        scenario_with_valsalva = ChamberScenario(
            start_altitude_ft=25000.0,
            descent_rate_ft_min=5000.0,
            et_severity="moderate",
            enable_valsava=True,
            valsalva_interval_s=60.0,
        )
        scenario_without_valsalva = ChamberScenario(
            start_altitude_ft=25000.0,
            descent_rate_ft_min=5000.0,
            et_severity="moderate",
            enable_valsava=False,
        )

        result_with = model.simulate_descent(scenario_with_valsalva)
        result_without = model.simulate_descent(scenario_without_valsalva)

        assert result_with.risk_score <= result_without.risk_score, (
            f"Valsalva should reduce risk: with={result_with.risk_score}, "
            f"without={result_without.risk_score}"
        )


if __name__ == "__main__":
    pytest.main(["-v", __file__]) 