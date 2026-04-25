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


def test_patulous_s1_with_uri_flips_to_paradoxical_instability():
    """A patent PET with active URI should not keep the protective S1 override."""
    m = modifiers_for_patient(PatientState(pet="s1", uri="day_4_7"))
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
    s1_uri = simulate(PatientState(pet="s1", uri="day_4_7"), FAC_BOGOTA_DEFAULT)

    # Kanick-Doyle protective prediction for S1
    assert s1.risk.p_barotitis < 0.02
    assert s1.risk.max_abs_delta_p_mmHg == 0.0

    # Paradoxical flip in S2 — high risk despite the PET label
    assert s2.risk.p_barotitis > 0.20
    assert s2.risk.max_abs_delta_p_mmHg > 50.0
    assert s1_uri.risk.p_barotitis > 0.20
    assert s1_uri.risk.max_abs_delta_p_mmHg > 50.0
    # Dominant risk factor reflects the real driver (URI or PET-S2)
    assert ("URI" in s2.risk.dominant_risk_factor
            or "Patulous" in s2.risk.dominant_risk_factor)


# ------------------------------------- v2.3.0 categorical covariates ---
def test_sensory_neuropathy_raises_per_descent_rr():
    """Voigt 2025 sensory-neuropathy flag multiplies per-descent RR by the
    configured SENSORY_NEUROPATHY_RR constant (1.8) and leaves other
    modifier fields untouched."""
    base_rr = modifiers_for_patient(PatientState()).per_descent_rr
    m = modifiers_for_patient(PatientState(sensory_neuropathy=True))
    assert m.per_descent_rr == pytest.approx(base_rr * 1.8)
    # Note text should surface the covariate
    assert any("Sensory neuropathy" in n for n in m.notes)


def test_impaired_volitional_equalization_raises_per_descent_rr():
    """Lee 2025 altered-mental-status flag multiplies per-descent RR by
    IMPAIRED_VOLITIONAL_EQUALIZATION_RR (3.0)."""
    base_rr = modifiers_for_patient(PatientState()).per_descent_rr
    m = modifiers_for_patient(
        PatientState(impaired_volitional_equalization=True)
    )
    assert m.per_descent_rr == pytest.approx(base_rr * 3.0)
    assert any("Impaired volitional" in n for n in m.notes)


def test_glp1_exposure_raises_per_descent_rr():
    """Sudhoff 2025 GLP-1 flag multiplies per-descent RR by
    GLP1_EXPOSURE_RR (1.4)."""
    base_rr = modifiers_for_patient(PatientState()).per_descent_rr
    m = modifiers_for_patient(PatientState(glp1_exposure=True))
    assert m.per_descent_rr == pytest.approx(base_rr * 1.4)
    assert any("GLP-1" in n for n in m.notes)


def test_v23_covariates_compose_multiplicatively():
    """All three v2.3.0 covariates active together multiply per-descent RR
    by 1.8 × 3.0 × 1.4 = 7.56."""
    m = modifiers_for_patient(
        PatientState(
            sensory_neuropathy=True,
            impaired_volitional_equalization=True,
            glp1_exposure=True,
        )
    )
    base_rr = modifiers_for_patient(PatientState()).per_descent_rr
    assert m.per_descent_rr == pytest.approx(base_rr * 1.8 * 3.0 * 1.4)
    # All three notes should be present
    notes_joined = " ".join(m.notes)
    assert "Sensory neuropathy" in notes_joined
    assert "Impaired volitional" in notes_joined
    assert "GLP-1" in notes_joined


def test_v23_covariates_default_false_is_noop():
    """Defaults (all False) match the v2.2.1 baseline modifiers exactly —
    no silent behavior change for existing callers."""
    m_default = modifiers_for_patient(PatientState())
    m_explicit_false = modifiers_for_patient(
        PatientState(
            sensory_neuropathy=False,
            impaired_volitional_equalization=False,
            glp1_exposure=False,
        )
    )
    assert m_default.per_descent_rr == pytest.approx(m_explicit_false.per_descent_rr)
    assert m_default.notes == m_explicit_false.notes


def test_v23_covariates_raise_simulated_risk():
    """End-to-end: at least one active v2.3.0 covariate raises
    p_barotitis relative to an otherwise-identical baseline on the FAC
    profile."""
    baseline = simulate(
        PatientState(uri="day_4_7"), FAC_BOGOTA_DEFAULT, rng_seed=42
    )
    with_flags = simulate(
        PatientState(uri="day_4_7", impaired_volitional_equalization=True),
        FAC_BOGOTA_DEFAULT,
        rng_seed=42,
    )
    assert with_flags.risk.p_barotitis > baseline.risk.p_barotitis


# ----------------------------------- BDET post-treatment arm (v2.3.0) -
def test_bdet_treated_applies_ra_and_rr_reduction():
    """bdet_treated=True multiplies ra_mult by BDET_RA_MULT and
    per-descent RR by BDET_PER_DESCENT_RR."""
    base = modifiers_for_patient(PatientState())
    treated = modifiers_for_patient(PatientState(bdet_treated=True))
    # ra_mult compounds multiplicatively (URI/rhinitis/PET/BDET)
    assert treated.ra_mult == pytest.approx(base.ra_mult * 0.70)
    assert treated.per_descent_rr == pytest.approx(base.per_descent_rr * 0.65)
    assert any("BDET-treated" in n for n in treated.notes)


def test_bdet_default_is_noop_against_v221_baseline():
    """Default (False) matches the v2.2.1 baseline modifier set exactly."""
    m_default = modifiers_for_patient(PatientState())
    m_explicit_false = modifiers_for_patient(PatientState(bdet_treated=False))
    assert m_default.ra_mult == pytest.approx(m_explicit_false.ra_mult)
    assert m_default.per_descent_rr == pytest.approx(m_explicit_false.per_descent_rr)
    assert m_default.notes == m_explicit_false.notes


def test_bdet_in_pet_flags_clinical_inconsistency():
    """bdet_treated=True alongside a non-normal PET state surfaces a
    "CLINICAL INCONSISTENCY" note for the CDS panel."""
    m = modifiers_for_patient(PatientState(bdet_treated=True, pet="s3"))
    notes_joined = " ".join(m.notes)
    assert "CLINICAL INCONSISTENCY" in notes_joined
    assert "s3" in notes_joined or "PET" in notes_joined


def test_bdet_in_pet_still_applies_numerical_modifier():
    """The contraindication flag is advisory only: BDET modifiers still
    apply numerically so a reviewer can quantify the discrepancy."""
    no_bdet = modifiers_for_patient(PatientState(pet="s3"))
    with_bdet = modifiers_for_patient(PatientState(bdet_treated=True, pet="s3"))
    # Not asserting direction — PET-S3 baseline can be dominated by the
    # Oshima multiplier; we only verify that the BDET modifiers were
    # actually composed in (not silently dropped).
    assert with_bdet.per_descent_rr != pytest.approx(no_bdet.per_descent_rr)


def test_bdet_reduces_simulated_risk_under_uri():
    """End-to-end: BDET lowers p_barotitis for a URI day 4–7 patient on
    the FAC Bogotá profile vs. an otherwise-identical untreated
    control."""
    untreated = simulate(
        PatientState(uri="day_4_7"), FAC_BOGOTA_DEFAULT, rng_seed=42
    )
    treated = simulate(
        PatientState(uri="day_4_7", bdet_treated=True),
        FAC_BOGOTA_DEFAULT,
        rng_seed=42,
    )
    assert treated.risk.p_barotitis < untreated.risk.p_barotitis
