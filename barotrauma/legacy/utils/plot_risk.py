"""barotrauma.utils.plot_risk

Visualization of ET dysfunction vs barotrauma risk relationship.

This script uses the deterministic legacy simulator in `models/`.
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from models.barotrauma_simulation import BarotraumaSimulation
from models.flight_profile import FlightProfile

_MMHG_TO_MMH2O = 13.6


def _simulate(et_dysfunction: float) -> dict[str, np.ndarray]:
    flight = FlightProfile(
        cruise_altitude=35000.0,
        ascent_rate=2000.0,
        descent_rate=2000.0,
        cruise_duration=10.0,
        et_dysfunction=float(et_dysfunction),
    )
    sim = BarotraumaSimulation(flight)
    results = sim.run_simulation(dt=0.1)

    dp_mmh2o = np.asarray(results["dP"], dtype=float)
    return {
        "time_s": np.asarray(results["time"], dtype=float),
        "dp_mmhg": dp_mmh2o / _MMHG_TO_MMH2O,
        "risk_score": float(np.max(np.asarray(results["risk_factor"], dtype=float))),
    }


def main() -> None:
    et_values = np.linspace(0.0, 1.0, 21)
    results = [_simulate(float(et)) for et in et_values]

    risk_scores = [float(r["risk_score"]) for r in results]
    max_abs_dp_mmhg = [float(np.max(np.abs(r["dp_mmhg"]))) for r in results]

    plt.figure(figsize=(15, 10))

    plt.subplot(2, 2, 1)
    plt.plot(et_values, risk_scores, "b-", linewidth=2)
    plt.fill_between(et_values, risk_scores, alpha=0.2)
    plt.xlabel("ET dysfunction")
    plt.ylabel("Risk score")
    plt.title("Risk score vs ET dysfunction")
    plt.grid(True)

    plt.subplot(2, 2, 2)
    plt.plot(et_values, max_abs_dp_mmhg, "r-", linewidth=2)
    plt.axhline(y=100.0, color="r", linestyle="--", alpha=0.5, label="100 mmHg")
    plt.xlabel("ET dysfunction")
    plt.ylabel("Max |ΔP| (mmHg)")
    plt.title("Max pressure differential vs ET dysfunction")
    plt.grid(True)
    plt.legend()

    plt.subplot(2, 2, 3)
    plt.plot(et_values, np.asarray(max_abs_dp_mmhg) / 100.0, "g-", linewidth=2)
    plt.xlabel("ET dysfunction")
    plt.ylabel("Max |ΔP| / 100")
    plt.title("Normalized max |ΔP| vs ET dysfunction")
    plt.grid(True)

    plt.subplot(2, 2, 4)
    selected_levels = [0.0, 0.5, 1.0]
    for et in selected_levels:
        idx = int(round(et * (len(et_values) - 1)))
        r = results[idx]
        plt.plot(r["time_s"] / 60.0, r["dp_mmhg"], label=f"ET={et:.1f}", linewidth=2)
    plt.xlabel("Time (min)")
    plt.ylabel("ΔP (mmHg)")
    plt.title("ΔP over time")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    out = "et_dysfunction_analysis.png"
    plt.savefig(out, dpi=150)
    plt.show()
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
