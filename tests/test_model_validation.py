"""
Validation tests for barotrauma simulation model.

Uses the HypobaricChamberRiskModel for model validation.
"""

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from barotrauma.models.chamber_risk import (
    HypobaricChamberRiskModel,
    ChamberScenario,
)


def map_dysfunction_to_severity(dysfunction: float) -> str:
    """Map numerical dysfunction level to severity category."""
    if dysfunction < 0.4:
        return "mild"
    elif dysfunction < 0.7:
        return "moderate"
    else:
        return "severe"


def validate_descent_rates() -> None:
    """Test model behavior at different descent rates for healthy and ET dysfunction cases."""

    # Test parameters - limited to valid range [1000, 10000]
    descent_rates = [1000, 3000, 5000, 8000, 10000]  # ft/min
    dysfunction_levels = [0.0, 0.5, 1.0]  # 0=healthy, 0.5=moderate, 1.0=severe

    # Flight profile parameters
    initial_altitude = 25000.0  # ft

    # Results storage
    max_pressure_diffs = np.zeros((len(dysfunction_levels), len(descent_rates)))
    risk_scores = np.zeros((len(dysfunction_levels), len(descent_rates)))

    model = HypobaricChamberRiskModel()

    for i, et_dysfunction in enumerate(dysfunction_levels):
        severity = map_dysfunction_to_severity(et_dysfunction)

        for j, descent_rate in enumerate(descent_rates):
            scenario = ChamberScenario(
                start_altitude_ft=initial_altitude,
                descent_rate_ft_min=float(descent_rate),
                et_severity=severity,
                enable_valsava=True,
                valsalva_interval_s=60.0,
            )

            result = model.simulate_descent(scenario)

            max_pressure = float(np.max(np.abs(result.delta_P_mmHg)))
            max_pressure_diffs[i, j] = max_pressure
            risk_scores[i, j] = result.risk_score

            # Print progress
            print(
                f"\nResults for ET severity {severity} at descent rate {descent_rate} ft/min:"
            )
            print(f"Risk score: {result.risk_score:.2f}")
            print(f"Risk category: {result.risk_category}")
            print(f"Max pressure diff: {max_pressure:.1f} mmHg")

    # Print summary results
    print("\n" + "=" * 70)
    print("Validation Results Summary:")
    print("=" * 70)

    print("\nRisk Scores:")
    print("Descent Rate (ft/min) |", end=" ")
    for rate in descent_rates:
        print(f"{rate:8d} |", end=" ")
    print("\n" + "-" * 70)

    for i, dysfunction in enumerate(dysfunction_levels):
        severity = map_dysfunction_to_severity(dysfunction)
        print(f"ET {severity:10s}         |", end=" ")
        for j in range(len(descent_rates)):
            print(f"{risk_scores[i, j]:8.2f} |", end=" ")
        print()

    print("\nMax Pressure Differences (mmHg):")
    print("Descent Rate (ft/min) |", end=" ")
    for rate in descent_rates:
        print(f"{rate:8d} |", end=" ")
    print("\n" + "-" * 70)

    for i, dysfunction in enumerate(dysfunction_levels):
        severity = map_dysfunction_to_severity(dysfunction)
        print(f"ET {severity:10s}         |", end=" ")
        for j in range(len(descent_rates)):
            print(f"{max_pressure_diffs[i, j]:8.1f} |", end=" ")
        print()


class TestModelValidation:
    """Pytest-compatible validation tests."""

    def test_risk_increases_with_severity(self) -> None:
        """Verify that risk increases with ET dysfunction severity."""
        model = HypobaricChamberRiskModel()
        severities = ["mild", "moderate", "severe"]
        risks = []

        for severity in severities:
            scenario = ChamberScenario(
                start_altitude_ft=25000.0,
                descent_rate_ft_min=5000.0,
                et_severity=severity,
                enable_valsava=True,
            )
            result = model.simulate_descent(scenario)
            risks.append(result.risk_score)

        # Risk should increase with severity
        for i in range(len(risks) - 1):
            assert risks[i] <= risks[i + 1], (
                f"Risk should increase: {severities[i]}={risks[i]} <= "
                f"{severities[i+1]}={risks[i+1]}"
            )

    def test_risk_increases_with_descent_rate(self) -> None:
        """Verify that risk increases with descent rate."""
        model = HypobaricChamberRiskModel()
        rates = [1000, 3000, 5000, 8000, 10000]
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

        # Risk should generally increase with descent rate
        assert risks[-1] >= risks[0], (
            f"Risk should increase with rate: {risks[0]} -> {risks[-1]}"
        )

    def test_pressure_differential_increases_with_severity(self) -> None:
        """Verify that max pressure differential increases with severity."""
        model = HypobaricChamberRiskModel()
        severities = ["mild", "moderate", "severe"]
        pressures = []

        for severity in severities:
            scenario = ChamberScenario(
                start_altitude_ft=25000.0,
                descent_rate_ft_min=5000.0,
                et_severity=severity,
                enable_valsava=False,  # No Valsalva to see raw effect
            )
            result = model.simulate_descent(scenario)
            max_p = float(np.max(np.abs(result.delta_P_mmHg)))
            pressures.append(max_p)

        # Pressure should increase with severity
        for i in range(len(pressures) - 1):
            assert pressures[i] <= pressures[i + 1], (
                f"Pressure should increase: {severities[i]}={pressures[i]:.1f} <= "
                f"{severities[i+1]}={pressures[i+1]:.1f}"
            )


if __name__ == "__main__":
    print("Starting validation test...")
    validate_descent_rates()
    print("\nValidation test complete.")
    print("\nRunning pytest validations...")
    pytest.main(["-v", __file__]) 