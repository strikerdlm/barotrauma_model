"""
barotrauma.v2.sensitivity
=========================

Global sensitivity analysis of the v2.1 model using Saltelli-sampled
Sobol indices. Quantifies which physiology / pathophysiology / aperture
parameters drive the most variance in the per-exposure ``p_barotitis``
output, informing future data-collection priorities.

Method
------
- Saltelli sample: two QMC matrices A, B of shape (N, k) plus k mixed
  matrices A_B^(i) where column i of A is replaced by column i of B.
- Model evaluations: f_A, f_B, f_A_B^(i).
- First-order Sobol index S_i = V_i / V_total, where
    V_i ≈ (1/N) Σ f_B · (f_A_B^(i) - f_A)
- Total-order index S_T_i = (1/(2N)) Σ (f_A - f_A_B^(i))^2 / V_total.

Reference
---------
Saltelli 2010, Comput Phys Commun 181:259-270;
SALib package (not a dependency — this module is self-contained).

Runtime
-------
``(2 + k) × N`` model evaluations. With N=32 and k=4 default params the
full analysis runs in under a minute for a single-patient output.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from . import constants as C
from .anatomy import sample_population_anatomy
from .calibration import sample_cohort
from .engine import simulate
from .scenarios import FAC_BOGOTA_DEFAULT
from .types import ChamberProfile, PatientState


# ----------------------------------------------------- parameter spec -
@dataclass(frozen=True)
class ParameterSpec:
    name: str
    low: float
    high: float
    docstring: str = ""


DEFAULT_PARAMETERS: tuple[ParameterSpec, ...] = (
    ParameterSpec("APERTURE_HALF_MMHG", 70.0, 180.0,
                  "descent |ΔP| at half aperture"),
    ParameterSpec("APERTURE_FREE_ZONE_MMHG", 20.0, 60.0,
                  "below this, descent aperture is 1.0"),
    ParameterSpec("SF_DESCENT_PER_HR", 30.0, 120.0,
                  "descent-phase swallow frequency"),
    ParameterSpec("MASTOID_VOLUME_ML", 3.0, 13.0,
                  "individual mastoid volume"),
)


# ---------------------------------------- parameter injection ---------
def _set_parameter(patient: PatientState, name: str, value: float,
                   module: object) -> PatientState:
    """
    Inject parameter value into the relevant location. Most live on
    ``barotrauma.v2.constants`` and patch in place; mastoid volume lives
    on the patient anatomy and is set via dataclasses.replace.
    """
    if name in (
        "APERTURE_HALF_MMHG", "APERTURE_FREE_ZONE_MMHG",
        "APERTURE_HILL_N", "APERTURE_RATE_COEF", "APERTURE_RATE_CAP_MMHG_S",
    ):
        from . import et_dynamics
        setattr(et_dynamics, name, float(value))
        return patient
    if name == "SF_DESCENT_PER_HR":
        from dataclasses import replace
        et = replace(patient.et, swallow_freq_per_hr_descent=float(value))
        return replace(patient, et=et)
    if name == "MASTOID_VOLUME_ML":
        from dataclasses import replace
        anat = replace(patient.anatomy, mastoid_volume_ml=float(value))
        return replace(patient, anatomy=anat)
    if name == "FGE":
        from dataclasses import replace
        et = replace(patient.et, fge_controls=float(value))
        return replace(patient, et=et)
    raise ValueError(f"unknown parameter {name}")


def _default_patient() -> PatientState:
    """Moderate-risk typical aircrew: mild ETD, day_8_14 URI residual."""
    from .types import EtFunction
    return PatientState(
        et=EtFunction(severity="mild"),
        uri="day_8_14",
    )


def _evaluate(
    x: np.ndarray,
    parameters: tuple[ParameterSpec, ...],
    patient: PatientState,
    profile: ChamberProfile,
    dt_s: float,
) -> float:
    """Run one model evaluation at parameter point x (unit hypercube)."""
    from . import et_dynamics

    # Snapshot mutable module-level state
    saved: dict[str, float] = {}
    for ps, xi in zip(parameters, x):
        if ps.name.startswith("APERTURE_"):
            saved[ps.name] = getattr(et_dynamics, ps.name)

    try:
        p = patient
        for ps, xi in zip(parameters, x):
            value = ps.low + xi * (ps.high - ps.low)
            p = _set_parameter(p, ps.name, value, et_dynamics)
        r = simulate(p, profile, dt_s=dt_s)
        return float(r.risk.p_barotitis)
    finally:
        for k, v in saved.items():
            from . import et_dynamics as _ed
            setattr(_ed, k, v)


# ---------------------------------------------- Saltelli sampling ----
def _saltelli_sample(
    n: int,
    k: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Standard Saltelli 2010 sample:
    A of shape (n, k), B of shape (n, k),
    AB of shape (k, n, k) where AB[i] is A with column i replaced by B column i.

    Uses scipy.stats.qmc.Sobol for low-discrepancy sequence when available;
    falls back to uniform random.
    """
    try:
        from scipy.stats import qmc
        sampler = qmc.Sobol(d=2 * k, scramble=True, seed=int(rng.integers(0, 2**32 - 1)))
        # Sobol balance requires n to be a power of 2. Round up if needed.
        n_pow = 1 << int(np.ceil(np.log2(max(n, 2))))
        sample = sampler.random(n_pow)[:n]
        A = sample[:, :k]
        B = sample[:, k:]
    except Exception:
        A = rng.random((n, k))
        B = rng.random((n, k))

    AB = np.empty((k, n, k), dtype=np.float64)
    for i in range(k):
        AB[i] = A.copy()
        AB[i, :, i] = B[:, i]
    return A, B, AB


# ---------------------------------------------- Sobol estimators ----
@dataclass
class SobolResult:
    parameter_names: tuple[str, ...]
    first_order: np.ndarray          # S_i, length k
    total_order: np.ndarray          # S_T_i, length k
    variance_total: float
    n_samples: int
    n_evaluations: int


def run_sobol(
    *,
    parameters: tuple[ParameterSpec, ...] = DEFAULT_PARAMETERS,
    patient: PatientState | None = None,
    profile: ChamberProfile = FAC_BOGOTA_DEFAULT,
    dt_s: float = 0.5,
    n: int = 32,
    rng_seed: int = 2026,
) -> SobolResult:
    """Saltelli Sobol sensitivity on the per-exposure p_barotitis output."""
    rng = np.random.default_rng(rng_seed)
    k = len(parameters)
    patient = patient or _default_patient()

    A, B, AB = _saltelli_sample(n, k, rng)

    f_A = np.asarray([_evaluate(A[i], parameters, patient, profile, dt_s)
                      for i in range(n)])
    f_B = np.asarray([_evaluate(B[i], parameters, patient, profile, dt_s)
                      for i in range(n)])
    f_AB = np.zeros((k, n))
    for i in range(k):
        f_AB[i] = np.asarray(
            [_evaluate(AB[i, j], parameters, patient, profile, dt_s)
             for j in range(n)]
        )

    # Saltelli 2010 estimators
    var_total = float(np.var(np.concatenate([f_A, f_B]), ddof=1))
    var_total = max(var_total, 1e-12)

    first_order = np.zeros(k)
    total_order = np.zeros(k)
    for i in range(k):
        v_i = float(np.mean(f_B * (f_AB[i] - f_A)))
        v_t = float(0.5 * np.mean((f_A - f_AB[i]) ** 2))
        first_order[i] = v_i / var_total
        total_order[i] = v_t / var_total

    return SobolResult(
        parameter_names=tuple(p.name for p in parameters),
        first_order=first_order,
        total_order=total_order,
        variance_total=var_total,
        n_samples=n,
        n_evaluations=(2 + k) * n,
    )


# ------------------------------------------------------ CLI runner ---
def _main() -> int:
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Sobol global sensitivity")
    parser.add_argument("--n", type=int, default=32,
                        help="Saltelli base samples (total evals = (2+k)*n)")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--save", action="store_true",
                        help="Write indices to barotrauma/v2/sobol_indices.json")
    args = parser.parse_args()

    result = run_sobol(n=args.n, rng_seed=args.seed)

    print("Sobol sensitivity on p_barotitis (default at-risk patient)")
    print("=" * 66)
    print(f"  n = {result.n_samples}, evaluations = {result.n_evaluations}")
    print(f"  output variance = {result.variance_total:.3e}")
    print()
    print(f"  {'parameter':<28s} {'S_i':>8s} {'S_T_i':>8s}")
    order = np.argsort(-result.total_order)
    for j in order:
        name = result.parameter_names[j]
        s = result.first_order[j]
        t = result.total_order[j]
        print(f"  {name:<28s} {s:>8.3f} {t:>8.3f}")

    if args.save:
        path = Path(__file__).parent / "sobol_indices.json"
        payload = {
            "parameters": list(result.parameter_names),
            "first_order": result.first_order.tolist(),
            "total_order": result.total_order.tolist(),
            "variance_total": result.variance_total,
            "n_samples": result.n_samples,
            "n_evaluations": result.n_evaluations,
        }
        path.write_text(json.dumps(payload, indent=2))
        print(f"Saved → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
