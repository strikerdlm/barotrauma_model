"""
barotrauma.v2.atmosphere
========================

Altitude ↔ pressure utilities. Uses the 1976 U.S. Standard Atmosphere
pressure-altitude relationship for the troposphere and lower stratosphere.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
from numpy.typing import NDArray

from .constants import ACCEL_G_M_S2, P0_MMHG
from .types import ChamberProfile

FT_TO_M: float = 0.3048
ISA_SEA_LEVEL_TEMP_K: float = 288.15
ISA_TROPOSPHERIC_LAPSE_K_PER_M: float = 0.0065
ISA_TROPOPAUSE_ALT_M: float = 11_000.0
ISA_DRY_AIR_MOLAR_MASS_KG_PER_MOL: float = 0.0289644
ISA_GAS_CONSTANT_J_PER_MOL_K: float = 8.3144598

ISA_TROPOSPHERE_EXPONENT: float = (
    ACCEL_G_M_S2
    * ISA_DRY_AIR_MOLAR_MASS_KG_PER_MOL
    / (ISA_GAS_CONSTANT_J_PER_MOL_K * ISA_TROPOSPHERIC_LAPSE_K_PER_M)
)
ISA_TROPOPAUSE_TEMP_K: float = (
    ISA_SEA_LEVEL_TEMP_K
    - ISA_TROPOSPHERIC_LAPSE_K_PER_M * ISA_TROPOPAUSE_ALT_M
)
ISA_TROPOPAUSE_PRESSURE_MMHG: float = P0_MMHG * (
    ISA_TROPOPAUSE_TEMP_K / ISA_SEA_LEVEL_TEMP_K
) ** ISA_TROPOSPHERE_EXPONENT


def altitude_to_pressure_mmHg(altitude_ft: float | NDArray[np.float64]) -> NDArray[np.float64] | float:
    """
    Convert pressure altitude in feet to ambient pressure in mmHg.

    Implements the U.S. Standard Atmosphere lapse-rate relation through the
    troposphere and the isothermal lower-stratosphere relation above 11 km.
    This covers the model's chamber profiles up to at least 50,000 ft.
    """
    altitude_arr = np.asarray(altitude_ft, dtype=np.float64)
    altitude_m = altitude_arr * FT_TO_M
    pressure = np.empty_like(altitude_m, dtype=np.float64)

    in_troposphere = altitude_m <= ISA_TROPOPAUSE_ALT_M
    pressure[in_troposphere] = P0_MMHG * (
        1.0
        - ISA_TROPOSPHERIC_LAPSE_K_PER_M
        * altitude_m[in_troposphere]
        / ISA_SEA_LEVEL_TEMP_K
    ) ** ISA_TROPOSPHERE_EXPONENT

    pressure[~in_troposphere] = ISA_TROPOPAUSE_PRESSURE_MMHG * np.exp(
        -ACCEL_G_M_S2
        * ISA_DRY_AIR_MOLAR_MASS_KG_PER_MOL
        * (altitude_m[~in_troposphere] - ISA_TROPOPAUSE_ALT_M)
        / (ISA_GAS_CONSTANT_J_PER_MOL_K * ISA_TROPOPAUSE_TEMP_K)
    )
    return float(pressure) if pressure.ndim == 0 else pressure


def pressure_to_altitude_ft(pressure_mmHg: float | NDArray[np.float64]) -> NDArray[np.float64] | float:
    """Inverse of altitude_to_pressure_mmHg."""
    pressure_arr = np.asarray(pressure_mmHg, dtype=np.float64)
    if np.any(pressure_arr <= 0.0):
        raise ValueError("pressure_mmHg must be positive")

    altitude_m = np.empty_like(pressure_arr, dtype=np.float64)
    in_troposphere = pressure_arr >= ISA_TROPOPAUSE_PRESSURE_MMHG
    altitude_m[in_troposphere] = (
        ISA_SEA_LEVEL_TEMP_K
        / ISA_TROPOSPHERIC_LAPSE_K_PER_M
        * (
            1.0
            - (pressure_arr[in_troposphere] / P0_MMHG)
            ** (1.0 / ISA_TROPOSPHERE_EXPONENT)
        )
    )

    altitude_m[~in_troposphere] = ISA_TROPOPAUSE_ALT_M - (
        ISA_GAS_CONSTANT_J_PER_MOL_K
        * ISA_TROPOPAUSE_TEMP_K
        / (ACCEL_G_M_S2 * ISA_DRY_AIR_MOLAR_MASS_KG_PER_MOL)
    ) * np.log(pressure_arr[~in_troposphere] / ISA_TROPOPAUSE_PRESSURE_MMHG)

    altitude_ft = altitude_m / FT_TO_M
    return float(altitude_ft) if altitude_ft.ndim == 0 else altitude_ft


def discretize_profile(
    profile: ChamberProfile,
    dt_s: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """
    Expand a piecewise-linear ChamberProfile to per-step arrays.

    Returns (t_s, altitude_ft, p_ambient_mmHg).
    """
    profile.validate()
    if dt_s <= 0:
        raise ValueError("dt_s must be positive")

    t_list: list[float] = [0.0]
    alt_list: list[float] = [profile.start_altitude_ft]
    current_t = 0.0
    current_alt = profile.start_altitude_ft

    for seg in profile.segments:
        seg_t_end = current_t + seg.duration_s
        n_steps = max(1, int(np.ceil(seg.duration_s / dt_s)))
        for i in range(1, n_steps + 1):
            tau = i / n_steps
            t = current_t + tau * seg.duration_s
            alt = current_alt + tau * (seg.end_altitude_ft - current_alt)
            t_list.append(float(t))
            alt_list.append(float(alt))
        current_t = seg_t_end
        current_alt = seg.end_altitude_ft

    t_arr = np.asarray(t_list, dtype=np.float64)
    alt_arr = np.asarray(alt_list, dtype=np.float64)
    p_amb = altitude_to_pressure_mmHg(alt_arr)
    return t_arr, alt_arr, np.asarray(p_amb, dtype=np.float64)


def descent_rate_ft_min(t_s: NDArray[np.float64], altitude_ft: NDArray[np.float64]) -> NDArray[np.float64]:
    """Instantaneous descent rate in ft/min (negative = descending)."""
    if len(t_s) < 2:
        return np.zeros_like(t_s)
    dalt = np.gradient(altitude_ft, t_s)          # ft/s
    return -dalt * 60.0                            # ft/min positive on descent
