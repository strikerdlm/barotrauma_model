"""
barotrauma.v2.middle_ear
========================

Middle-ear compartment: tympanic-membrane displacement (Boyle's-law buffer),
multi-species trans-mucosal gas exchange (Doyle 2011), and aggregate ME-state
updates.

For a chamber exposure of minutes, trans-mucosal exchange is a small
perturbation on the total ME pressure (O2/CO2 half-lives 11–62 min; N2 many
hours). It is still modeled because (a) it matters for long holds, (b) the
gas-composition drift matters for analyses of multiple-exposure days, and
(c) it gives the model a physically coherent baseline for future cabin-flight
extensions.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import constants as C
from .types import PatientAnatomy


# -------------------------------------------- TM displacement (Hooke) -
def tm_displacement_ml(
    delta_p_mmHg: float,
    anatomy: PatientAnatomy,
) -> float:
    """
    Tympanic membrane volume displacement.

    ΔV_TM = P_ME-Pambient · A_TM · C_TM, clamped to ±V_TM,max.
    Positive ΔP (ME overpressure) displaces TM outward, increasing V_ME.
    """
    # KD2005 eq 20 uses trans-TM gradient × compliance × area.
    # We collapse A_TM·C_TM into TM_COMPLIANCE_ML_PER_MMHG for the v2 layer.
    raw = delta_p_mmHg * C.TM_COMPLIANCE_ML_PER_MMHG
    max_disp = anatomy.tm_max_displacement_ml
    return float(np.clip(raw, -max_disp, max_disp))


def effective_me_volume_ml(
    delta_p_mmHg: float,
    anatomy: PatientAnatomy,
) -> float:
    """V_ME + ΔV_TM — the effective volume used in Boyle updates."""
    return anatomy.me_volume_ml + tm_displacement_ml(delta_p_mmHg, anatomy)


# ----------------------------------------------- Boyle's-law dynamics -
def boyle_update_me_pressure_mmHg(
    p_me_mmHg: float,
    v_me_before_ml: float,
    v_me_after_ml: float,
) -> float:
    """
    Apply PV = const. between ME states where volume changes (e.g. TM
    displacement buffer). Returns the updated P_ME.
    """
    if v_me_after_ml <= 0:
        raise ValueError("effective ME volume must be positive")
    return p_me_mmHg * v_me_before_ml / v_me_after_ml


# --------------------------------- Trans-mucosal gas exchange (Doyle 2011) -
@dataclass
class GasComposition:
    """ME gas partial pressures (mmHg)."""

    p_o2: float = 0.21 * 760.0
    p_co2: float = 40.0
    p_n2: float = 0.79 * 760.0
    p_h2o: float = 47.0

    def total_mmHg(self) -> float:
        return self.p_o2 + self.p_co2 + self.p_n2 + self.p_h2o


def initial_me_gas(p_total_mmHg: float) -> GasComposition:
    """
    Steady-state ME gas composition assumed equal to venous-blood composition
    scaled to the requested total pressure (Kanick-Doyle 2005 initialization).
    """
    # Start with approximately 'venous-blood-equilibrated' partial pressures
    # then rescale to sum to p_total_mmHg.
    raw = GasComposition(
        p_o2=C.P_VB_O2_MMHG,
        p_co2=C.P_VB_CO2_MMHG,
        p_n2=p_total_mmHg - C.P_VB_O2_MMHG - C.P_VB_CO2_MMHG - C.P_VB_H2O_MMHG,
        p_h2o=C.P_VB_H2O_MMHG,
    )
    return raw


def transmucosal_exchange_step(
    gas: GasComposition,
    dt_s: float,
) -> GasComposition:
    """
    One integration step of Fick diffusion between ME gas and venous blood
    (Doyle 2011 rate constants). dt in seconds; k in per-minute units.
    """
    dt_min = dt_s / 60.0
    p_o2 = gas.p_o2 - C.TRANSMEM_K_O2_PER_MIN * (gas.p_o2 - C.P_VB_O2_MMHG) * dt_min
    p_co2 = gas.p_co2 - C.TRANSMEM_K_CO2_PER_MIN * (gas.p_co2 - C.P_VB_CO2_MMHG) * dt_min
    p_n2 = gas.p_n2 - C.TRANSMEM_K_N2_PER_MIN * (gas.p_n2 - C.P_VB_O2_MMHG) * dt_min  # small drift
    p_h2o = gas.p_h2o - C.TRANSMEM_K_H2O_PER_MIN * (gas.p_h2o - C.P_VB_H2O_MMHG) * dt_min
    return GasComposition(p_o2=p_o2, p_co2=p_co2, p_n2=p_n2, p_h2o=p_h2o)


# -------------------------------------- aggregate ME state helper -------
@dataclass
class MeState:
    """Minimal middle-ear state needed by the integrator."""

    p_me_mmHg: float                           # total ME gas pressure
    gas: GasComposition = field(default_factory=GasComposition)
    v_me_effective_ml: float = C.ME_VOLUME_ML_ADULT
