"""
barotrauma.v2.atmosphere
========================

Altitude ↔ pressure utilities. Uses the isothermal standard-atmosphere fit
matching Kanick-Doyle 2005 (P = P0·exp(-z/H), H = 29921 ft).
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
from numpy.typing import NDArray

from .constants import P0_MMHG, SCALE_HEIGHT_FT
from .types import ChamberProfile


def altitude_to_pressure_mmHg(altitude_ft: float | NDArray[np.float64]) -> NDArray[np.float64] | float:
    """Standard atmosphere isothermal fit: P(z) = P0·exp(-z/H)."""
    return P0_MMHG * np.exp(-np.asarray(altitude_ft) / SCALE_HEIGHT_FT)


def pressure_to_altitude_ft(pressure_mmHg: float | NDArray[np.float64]) -> NDArray[np.float64] | float:
    """Inverse of altitude_to_pressure_mmHg."""
    return -SCALE_HEIGHT_FT * np.log(np.asarray(pressure_mmHg) / P0_MMHG)


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
