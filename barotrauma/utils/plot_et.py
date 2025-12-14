"""barotrauma.utils.plot_et

Quick diagnostic plot: ET dysfunction vs barotrauma risk.

This script uses the deterministic legacy simulator in `models/`.
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from models.barotrauma_simulation import BarotraumaSimulation
from models.flight_profile import FlightProfile

_MMHG_TO_MMH2O = 13.6


def main() -> None:
    flight_profile = {
        "cruise_altitude": 35000.0,
        "ascent_rate": 2000.0,
        "descent_rate": 2000.0,
        "cruise_duration": 10.0,
    }

    et_values = np.linspace(0.0, 1.0, 11)
    risk_scores: list[float] = []
    max_abs_dp_mmhg: list[float] = []

    for et in et_values:
        flight = FlightProfile(
            cruise_altitude=float(flight_profile["cruise_altitude"]),
            ascent_rate=float(flight_profile["ascent_rate"]),
            descent_rate=float(flight_profile["descent_rate"]),
            cruise_duration=float(flight_profile["cruise_duration"]),
            et_dysfunction=float(et),
        )
        sim = BarotraumaSimulation(flight)
        results = sim.run_simulation(dt=0.1)

        rf = np.asarray(results["risk_factor"], dtype=float)
        dp_mmh2o = np.asarray(results["dP"], dtype=float)

        risk_scores.append(float(np.max(rf)))
        max_abs_dp_mmhg.append(float(np.max(np.abs(dp_mmh2o)) / _MMHG_TO_MMH2O))

    plt.figure(figsize=(10, 6))
    plt.plot(et_values, risk_scores, "b-o", linewidth=2, label="Risk score (max risk_factor)")
    plt.plot(et_values, np.asarray(max_abs_dp_mmhg) / 100.0, "r--o", linewidth=2, label="Max |ΔP| (mmHg, /100)")

    plt.xlabel("ET dysfunction (0=normal, 1=severe)")
    plt.ylabel("Risk / normalized pressure")
    plt.title("ET dysfunction vs barotrauma risk")
    plt.grid(True)
    plt.legend()

    out = "et_risk_analysis.png"
    plt.savefig(out, dpi=150)
    plt.show()
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
