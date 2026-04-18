"""
Tests for the URI / PET / rhinitis / medication pathophysiology layer.
"""

from __future__ import annotations

import pytest

from barotrauma.v2 import FAC_BOGOTA_DEFAULT, PatientState, simulate
from barotrauma.v2.pathophysiology import modifiers_for_patient
from barotrauma.v2.types import EtFunction


def test_uri_peak_multiplier_dominates_baseline():
    m_none = modifiers_for_patient(PatientState(uri="none"))
    m_peak = modifiers_for_patient(PatientState(uri="day_4_7"))
    assert m_peak.ra_mult > m_none.ra_mult
    assert m_peak.per_descent_rr > m_none.per_descent_rr


def test_uri_timecourse_peak_then_recovery():
    states = ["day_1_3", "day_4_7", "day_8_14", "day_15_21", "day_22_28"]
    rrs = [modifiers_for_patient(PatientState(uri=s)).per_descent_rr for s in states]
    # RR should peak at day_4_7 and decay after
    idx_peak = rrs.index(max(rrs))
    assert states[idx_peak] == "day_4_7"
    # Recovery monotonic
    assert rrs[2] > rrs[3] > rrs[4]


def test_allergic_rhinitis_plus_uri_is_compound():
    m_uri = modifiers_for_patient(PatientState(uri="day_4_7")).per_descent_rr
    m_both = modifiers_for_patient(
        PatientState(uri="day_4_7", rhinitis="allergic")
    ).per_descent_rr
    assert m_both > m_uri


def test_decongestant_is_paradoxical_in_patulous():
    """
    Oral pseudoephedrine normally RR 0.70 (Mirza 2005, protective). In PET
    the effect flips: the medication carries RR 1.4 (paradoxical worsening)
    rather than 0.7. Compare medication-vs-no-medication within the same
    PET state. See docs/research_notes/03 §7.
    """
    pet_no_med = modifiers_for_patient(
        PatientState(uri="none", pet="s1", medication="none")
    )
    pet_with_med = modifiers_for_patient(
        PatientState(uri="none", pet="s1", medication="pseudoephedrine_oral")
    )
    # In PET the medication should WORSEN (higher RR), not improve
    assert pet_with_med.per_descent_rr > pet_no_med.per_descent_rr
    # ratio should be ~1.4 (the paradoxical RR) not ~0.7 (the protective one)
    ratio = pet_with_med.per_descent_rr / pet_no_med.per_descent_rr
    assert ratio == pytest.approx(1.4, rel=0.01)

    # By contrast, in healthy subjects pseudoephedrine IS protective
    healthy_no_med = modifiers_for_patient(PatientState()).per_descent_rr
    healthy_med = modifiers_for_patient(
        PatientState(medication="pseudoephedrine_oral")
    ).per_descent_rr
    assert healthy_med < healthy_no_med


def test_patulous_s1_sets_patent_flag():
    m = modifiers_for_patient(PatientState(pet="s1"))
    assert m.is_patulous_patent is True
    assert m.patulous_unstable is False


def test_patulous_s2_flags_paradoxical_instability():
    m = modifiers_for_patient(PatientState(pet="s2"))
    assert m.patulous_unstable is True
    assert m.is_patulous_patent is False


def test_patulous_s4_sets_post_plug_flag():
    m = modifiers_for_patient(PatientState(pet="s4"))
    assert m.post_plug_stenotic is True


def test_severe_etd_worse_than_healthy():
    healthy = simulate(PatientState(), FAC_BOGOTA_DEFAULT)
    severe = simulate(
        PatientState(et=EtFunction(severity="severe")), FAC_BOGOTA_DEFAULT
    )
    assert severe.risk.max_abs_delta_p_mmHg > healthy.risk.max_abs_delta_p_mmHg
    assert severe.risk.p_barotitis > healthy.risk.p_barotitis


def test_previous_meb_modest_penalty():
    m0 = modifiers_for_patient(PatientState(previous_meb=False)).per_descent_rr
    m1 = modifiers_for_patient(PatientState(previous_meb=True)).per_descent_rr
    assert m1 > m0
    assert m1 / m0 == pytest.approx(1.5, rel=0.01)


def test_pet_s1_is_rupture_protective_but_s2_flips_to_high_risk():
    """
    Safety-critical physics-vs-pathophysiology interaction:

    - PET-S1 (baseline patent, dry mucosa) reproduces Kanick-Doyle's
      zero-ΔP protective prediction. p_barotitis should be ≈0.
    - PET-S2 (PET + acute URI / inflammation) is the paradoxical-closure
      state documented in Ikeda 2020/2024 and Shindo 2025. The tube loses
      its protective patency on an abnormal (inflamed, deficient cartilage)
      substrate, and MEB risk should be HIGH — not low.

    This regression guards against future refactors that might collapse
    PET into a single "protective" flag.
    """
    s1 = simulate(PatientState(pet="s1"), FAC_BOGOTA_DEFAULT)
    s2 = simulate(PatientState(pet="s2", uri="day_4_7"), FAC_BOGOTA_DEFAULT)

    # Kanick-Doyle protective prediction for S1
    assert s1.risk.p_barotitis < 0.02
    assert s1.risk.max_abs_delta_p_mmHg == 0.0

    # Paradoxical flip in S2 — high risk despite the PET label
    assert s2.risk.p_barotitis > 0.20
    assert s2.risk.max_abs_delta_p_mmHg > 50.0
    # Dominant risk factor reflects the real driver (URI or PET-S2)
    assert ("URI" in s2.risk.dominant_risk_factor
            or "Patulous" in s2.risk.dominant_risk_factor)
