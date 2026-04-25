"""
Doyle 2017 multi-pathway gas-exchange tests.
"""

from __future__ import annotations

import numpy as np
import pytest

from barotrauma.v2 import FAC_BOGOTA_DEFAULT, PatientState, simulate
from barotrauma.v2 import constants as C
from barotrauma.v2.middle_ear import (
    GasComposition,
    full_gas_exchange_step,
    initial_me_gas,
    transmembrane_rw_exchange_step,
    transmembrane_tm_exchange_step,
    transmucosal_exchange_step,
)
from barotrauma.v2.types import ChamberProfile, ChamberSegment


def test_full_gas_exchange_backward_compat_with_both_disabled():
    """Passing include_tm=False AND include_rw=False should match trans-mucosal only."""
    gas0 = initial_me_gas(760.0)
    a = transmucosal_exchange_step(gas0, 60.0)
    b = full_gas_exchange_step(gas0, 60.0, include_tm=False, include_rw=False)
    assert a.p_o2 == pytest.approx(b.p_o2)
    assert a.p_co2 == pytest.approx(b.p_co2)
    assert a.p_n2 == pytest.approx(b.p_n2)
    assert a.p_h2o == pytest.approx(b.p_h2o)


def test_full_gas_exchange_faster_than_mucosa_alone():
    """With both TM and RW paths enabled, species approach VB faster."""
    gas0 = initial_me_gas(760.0)
    # Bias the O2 away from VB target to see the gap close
    gas_biased = GasComposition(
        p_o2=gas0.p_o2 + 50.0,
        p_co2=gas0.p_co2,
        p_n2=gas0.p_n2,
        p_h2o=gas0.p_h2o,
    )
    a = transmucosal_exchange_step(gas_biased, 30 * 60.0)   # 30 min
    b = full_gas_exchange_step(gas_biased, 30 * 60.0,
                               include_tm=True, include_rw=True)
    gap_a = abs(a.p_o2 - C.P_VB_O2_MMHG)
    gap_b = abs(b.p_o2 - C.P_VB_O2_MMHG)
    assert gap_b < gap_a


def test_tm_exchange_smaller_magnitude_than_mucosa():
    gas0 = GasComposition(p_o2=200.0, p_co2=40.0, p_n2=500.0, p_h2o=47.0)
    a = transmucosal_exchange_step(gas0, 60.0)
    b = transmembrane_tm_exchange_step(gas0, 60.0)
    mucosa_delta = abs(a.p_o2 - gas0.p_o2)
    tm_delta = abs(b.p_o2 - gas0.p_o2)
    # TM pathway should move O2 less than the mucosa pathway (~4% per constants.py)
    assert tm_delta < mucosa_delta


def test_rw_exchange_even_smaller():
    gas0 = GasComposition(p_o2=200.0, p_co2=40.0, p_n2=500.0, p_h2o=47.0)
    tm = transmembrane_tm_exchange_step(gas0, 60.0)
    rw = transmembrane_rw_exchange_step(gas0, 60.0)
    assert abs(rw.p_o2 - gas0.p_o2) < abs(tm.p_o2 - gas0.p_o2)


def test_simulate_with_gas_exchange_full_returns_finite():
    r = simulate(PatientState(), FAC_BOGOTA_DEFAULT, gas_exchange_full=True,
                  rng_seed=42)
    assert np.isfinite(r.risk.p_barotitis)
    assert 0.0 <= r.risk.p_barotitis <= 1.0


def test_full_gas_exchange_couples_back_to_pressure_trace():
    """The Doyle 2017 option should affect ME pressure, not only hidden gas state."""
    long_altitude_hold = ChamberProfile(
        name="long hypobaric hold",
        start_altitude_ft=25000.0,
        segments=(ChamberSegment(duration_s=3600.0, end_altitude_ft=25000.0),),
    )
    simple = simulate(
        PatientState(),
        long_altitude_hold,
        dt_s=1.0,
        rng_seed=42,
        gas_exchange_full=False,
    )
    full = simulate(
        PatientState(),
        long_altitude_hold,
        dt_s=1.0,
        rng_seed=42,
        gas_exchange_full=True,
    )
    assert np.max(np.abs(simple.trace.p_me_mmHg - full.trace.p_me_mmHg)) > 1e-4
