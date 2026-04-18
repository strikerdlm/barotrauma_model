"""
barotrauma.v2.anatomy
=====================

Population priors and sampling for patient anatomy. The mastoid volume is the
single largest source of inter-subject variance in MEB risk (~10× clinical
range), so it gets explicit distributional treatment (Doyle 2007, Alper 2011).
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from . import constants as C
from .types import EtFunction, EtSeverity, PatientAnatomy


def apply_severity_to_et(et: EtFunction, severity: EtSeverity) -> EtFunction:
    """Scale the ET parameters by the severity class multipliers (constants.py)."""
    pass_open_mult = C.ET_SEVERITY_PASSIVE_OPENING_MULT[severity]
    ra_mult = C.ET_SEVERITY_RA_MULT[severity]
    fge_mult = C.ET_SEVERITY_FGE_MULT[severity]
    return EtFunction(
        severity=severity,
        passive_opening_mmHg_me=et.passive_opening_mmHg_me * pass_open_mult,
        passive_opening_mmHg_np=et.passive_opening_mmHg_np * pass_open_mult,
        closing_mmHg=et.closing_mmHg,
        active_resistance_mmHg_ml_min=et.active_resistance_mmHg_ml_min * ra_mult,
        active_open_duration_s=et.active_open_duration_s,
        swallow_freq_per_hr_cruise=et.swallow_freq_per_hr_cruise,
        swallow_freq_per_hr_descent=et.swallow_freq_per_hr_descent,
        fge_controls=et.fge_controls * fge_mult,
    )


# ------------------------------------------------------ sampling ------
def sample_mastoid_volume_ml(
    rng: np.random.Generator,
    n: int = 1,
) -> NDArray[np.float64]:
    """
    Mastoid volume prior. Log-normal fit to the 2–15 mL clinical range observed
    by Alper 2011, anchored on the adult mean 7.75 mL from KD2005.

    log-normal parameters: μ_ln = ln(7.0), σ_ln = 0.45 → median 7.0 mL,
    95% interval ≈ [2.9, 16.9] mL.
    """
    mu_ln = np.log(7.0)
    sigma_ln = 0.45
    samples = rng.lognormal(mean=mu_ln, sigma=sigma_ln, size=n)
    lo, hi = C.MASTOID_VOLUME_ML_RANGE
    return np.clip(samples, lo, hi)


def sample_tympanum_volume_ml(
    rng: np.random.Generator,
    n: int = 1,
) -> NDArray[np.float64]:
    """Tympanum volume has much lower variance (Alper 2011)."""
    return rng.normal(loc=C.TYMPANUM_VOLUME_ML, scale=0.1, size=n).clip(0.6, 1.5)


def sample_tm_max_displacement_ml(
    rng: np.random.Generator,
    n: int = 1,
) -> NDArray[np.float64]:
    """Hypercompliant TM (atelectasis) extends the upper tail (KD2005 Fig 7B)."""
    return rng.lognormal(mean=np.log(0.025), sigma=0.35, size=n).clip(0.01, 0.15)


def sample_population_anatomy(
    rng: np.random.Generator,
    n: int,
    age_range: tuple[int, int] = C.FAC_AGE_YEARS_RANGE,
    male_fraction: float = C.FAC_MALE_FRACTION,
) -> list[PatientAnatomy]:
    """Draw a cohort of PatientAnatomy from FAC-like priors."""
    ages = rng.integers(age_range[0], age_range[1] + 1, size=n)
    males = rng.random(size=n) < male_fraction
    mast = sample_mastoid_volume_ml(rng, n)
    tymp = sample_tympanum_volume_ml(rng, n)
    tmmd = sample_tm_max_displacement_ml(rng, n)
    out: list[PatientAnatomy] = []
    for i in range(n):
        out.append(
            PatientAnatomy(
                tympanum_volume_ml=float(tymp[i]),
                mastoid_volume_ml=float(mast[i]),
                tm_area_cm2=C.TM_AREA_CM2,
                tm_stiffness_mmHg_per_ml=C.TM_STIFFNESS_MMHG_PER_ML,
                tm_max_displacement_ml=float(tmmd[i]),
                age_years=int(ages[i]),
                sex="male" if males[i] else "female",
            )
        )
    return out
