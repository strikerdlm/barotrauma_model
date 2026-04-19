"""
barotrauma.v2.constants
=======================

All physiological and physical constants used by the v2 model, with citations.
Every value must have a source, a unit, and a one-line rationale.

References (primary):
- Kanick & Doyle 2005, J Appl Physiol 98:1592-1602 (KD2005). PMID 15608090.
- Doyle 2017, Hearing Research 354:73-85. PMID 28917121.
- Doyle 2011, transmucosal rate constants. PMID 21330076.
- Doyle 2007, mastoid buffering. PMID 17174408.
- Alper 2011, mastoid and MEPR. PMID 21271597.
- Alper 2020, ET opening/closing distributions post-BDET. PMID 32176133.
- Mandel 2016, FGE per swallow. PMID 26626132.
- Wang 2019, rate-dependent rabbit MEB. PMID 31331419.
- Morgagni 2010 / 2012, Italian AF chamber. PMID 20824995 / 22764614.

Unit convention: mmHg for pressure (not daPa, not mmH2O). Conversions::
    1 mmHg = 13.595 mmH2O = 1.3595 cmH2O
    1 daPa = 0.07501 mmHg  (1 mmHg = 13.332 daPa)
    1 mmHg = 133.322 Pa
"""

from __future__ import annotations

# ------------------------------------------------------- unit constants --
MMHG_PER_MMH2O: float = 1.0 / 13.595
MMHG_PER_DAPA: float = 1.0 / 13.332
PA_PER_MMHG: float = 133.322

# ------------------------------------------------------ atmosphere -----
P0_MMHG: float = 760.0                    # Sea-level pressure
SCALE_HEIGHT_FT: float = 29921.0          # US Std Atmosphere isothermal fit
ACCEL_G_M_S2: float = 9.80665             # Standard gravity

# -------------------------------------------------------- ME volumes ---
TYMPANUM_VOLUME_ML: float = 1.0           # KD2005
MASTOID_VOLUME_ML_ADULT_MEAN: float = 7.75    # KD2005 (Doyle 2007 notes range 2-15 mL)
ME_VOLUME_ML_ADULT: float = 8.75          # KD2005 tabulated V_ME
MASTOID_VOLUME_ML_RANGE: tuple[float, float] = (2.0, 15.0)  # Alper 2011

# ------------------------------------------------------ TM mechanics --
TM_AREA_CM2: float = 0.6                  # KD2005
TM_STIFFNESS_MMHG_PER_ML: float = 179.0   # KD2005 (= 1 / compliance)
TM_MAX_DISPLACEMENT_ML: float = 0.025     # KD2005 (~1% of V_ME)
TM_COMPLIANCE_ML_PER_MMHG: float = 1.0 / TM_STIFFNESS_MMHG_PER_ML

# ---------------------------------------- Eustachian tube (normal) ----
# Pressure-referenced-to-ambient opening/closing values from KD2005 Table 1.
ET_PASSIVE_OPENING_ME_MMHG: float = 350.0 * MMHG_PER_MMH2O      # ≈25.7
ET_PASSIVE_OPENING_NP_MMHG: float = 600.0 * MMHG_PER_MMH2O      # ≈44.1
ET_CLOSING_MMHG: float = 100.0 * MMHG_PER_MMH2O                 # ≈7.35
ET_ACTIVE_RESISTANCE_MMHG_ML_MIN: float = 2.0                   # KD2005 R_A
ET_ACTIVE_OPEN_DURATION_S: float = 0.25                         # KD2005 T_A

# FGE — fractional pressure gradient equalized per swallow (Mandel 2016)
FGE_ADULT_CONTROLS: float = 0.32
FGE_ADULT_CONTROLS_CI: tuple[float, float] = (0.21, 0.43)
FGE_ADULT_RECURRENT_AOM: float = 0.16
FGE_ADULT_RECURRENT_AOM_CI: tuple[float, float] = (0.08, 0.24)

# Swallow frequencies. Kanick-Doyle 2005 Table ref 53 (Tideholm et al.)
# measured 31/hr during descent in passive subjects; trained chamber aircrew
# routinely hit ~60/hr (every ~60 s) because they are instructed to clear
# pro-actively (chew gum, swallow, Toynbee, Valsalva) whenever symptoms
# hint at a pressure gradient. The default here is the trained-aircrew
# value; set ``EtFunction(swallow_freq_per_hr_descent=31.0)`` to use the
# Kanick-Doyle passive baseline.
SF_CRUISE_PER_HR: float = 5.2
SF_DESCENT_PER_HR: float = 60.0

# ---------------------------------------- Obstructive ET severity ----
# Multipliers applied to the normal ET parameters by severity class.
# Mild / moderate / severe calibrated to retain published-prevalence ranges.
ET_SEVERITY_PASSIVE_OPENING_MULT = {
    "normal":   1.00,
    "mild":     1.40,                       # ~35 mmHg (Alper 2020 pre-BDET mean)
    "moderate": 2.40,                       # ~60 mmHg
    "severe":   7.00,                       # ~180 mmHg (approaches "locked")
}
ET_SEVERITY_RA_MULT = {
    "normal":   1.00,
    "mild":     2.00,
    "moderate": 5.00,
    "severe":  20.00,
}
ET_SEVERITY_FGE_MULT = {
    "normal":   1.00,
    "mild":     0.75,
    "moderate": 0.50,
    "severe":   0.25,
}

# ------------------------------------------------- Patulous ET (PET) -
# Four-state model (Ikeda 2020, Shindo 2025; see docs/research_notes/03).
# All pressures referenced to ambient.
PET_S1_OPENING_MMHG: float = 200.0 * MMHG_PER_DAPA      # ≈1.5 mmHg — "patent"
PET_S1_CLOSING_MMHG: float = 0.1 * MMHG_PER_DAPA        # effectively never closes
PET_S3_RESTING_ME_MMHG_OFFSET: float = -200.0 * MMHG_PER_DAPA   # ≈ −15 mmHg
PET_S3_SNIFF_ME_MMHG: tuple[float, float] = (
    -100.0 * MMHG_PER_DAPA, -400.0 * MMHG_PER_DAPA,
)                                                        # Shindo 2025 range
PET_S4_OPENING_MMHG: float = 1200.0 * MMHG_PER_DAPA     # ≈90 mmHg ("stenotic")

# Prevalence (Ikeda 2024)
PET_PREV_MIN: float = 0.003
PET_PREV_MAX: float = 0.070

# --------------------------------------------- URI timecourse modifiers -
# Multipliers applied to ET function during acute URI.
# Source: docs/research_notes/02_uri_et_dysfunction.md Table (brief 02).
URI_MODIFIERS: dict[str, dict[str, float]] = {
    "none": dict(
        ra_mult=1.0, po_shift_mmHg=0.0, pet_offset_mmHg=0.0,
        eq_rate_mult=1.0, valsalva_mult=1.0, meb_rr=1.0,
    ),
    "day_1_3": dict(
        ra_mult=2.0, po_shift_mmHg=80.0 * MMHG_PER_DAPA, pet_offset_mmHg=4.0,
        eq_rate_mult=0.60, valsalva_mult=0.70, meb_rr=2.5,
    ),
    "day_4_7": dict(
        ra_mult=3.5, po_shift_mmHg=150.0 * MMHG_PER_DAPA, pet_offset_mmHg=8.0,
        eq_rate_mult=0.40, valsalva_mult=0.50, meb_rr=4.25,
    ),
    "day_8_14": dict(
        ra_mult=1.8, po_shift_mmHg=60.0 * MMHG_PER_DAPA, pet_offset_mmHg=3.0,
        eq_rate_mult=0.75, valsalva_mult=0.80, meb_rr=2.0,
    ),
    "day_15_21": dict(
        ra_mult=1.3, po_shift_mmHg=20.0 * MMHG_PER_DAPA, pet_offset_mmHg=1.0,
        eq_rate_mult=0.90, valsalva_mult=0.90, meb_rr=1.3,
    ),
    "day_22_28": dict(
        ra_mult=1.1, po_shift_mmHg=5.0 * MMHG_PER_DAPA, pet_offset_mmHg=0.0,
        eq_rate_mult=0.95, valsalva_mult=0.95, meb_rr=1.1,
    ),
}

# Chronic comorbidity modifiers
CHRONIC_RHINITIS_MODIFIERS: dict[str, dict[str, float]] = {
    "none":                  dict(ra_mult=1.0, po_shift_mmHg=0.0, pet_offset_mmHg=0.0, meb_rr=1.0),
    "allergic":              dict(ra_mult=1.3, po_shift_mmHg=30.0*MMHG_PER_DAPA, pet_offset_mmHg=2.0, meb_rr=1.5),
    "chronic_rhinosinusitis": dict(ra_mult=1.5, po_shift_mmHg=50.0*MMHG_PER_DAPA, pet_offset_mmHg=3.0, meb_rr=2.0),
}

# Medication effects (RR modifier on per-descent MEB probability).
#
# v2.2.1 update — Moayedi 2025 (PMID 40819351) RCT of pseudoephedrine
# prophylaxis in HBOT found no significant effect on ear pain, TM injury,
# or rescue medication vs placebo. Previous baseline value of 0.70 was
# extrapolated from AlGhamdi 2026 (airline descent) and Mirza 2005; the
# Moayedi null applies directly to controlled-descent chamber physiology.
# We soften the value toward 0.90, splitting the difference between the
# airline-descent signal and the HBOT null — with the caveat in the model
# card that the true effect size is indication-specific.
MEDICATION_RR: dict[str, float] = {
    "none":                   1.00,
    "pseudoephedrine_oral":   0.90,   # v2.2.1: softened per Moayedi 2025 PMID 40819351
    "oxymetazoline_topical":  0.95,   # Null per Mirza 2005 / Joshi 2020
    "intranasal_steroid":     0.65,   # For chronic AR/CRS baseline, not acute URI
    "antihistamine_spray":    0.70,   # Daum 2024 β=-8.70 on ETDQ-7
}

# Pathological rule: decongestants are contraindicated in PET (paradoxical worsening)
# Applied as a penalty in pathophysiology.apply_medication().

# ------------------------------------- v2.3.0 covariate RRs (additive) -
# New patient-state categorical covariates introduced in v2.3.0 from the
# 2025-2026 literature scan (docs/research_notes/06_2025_2026_updates.md).
# Each multiplies the composite per-descent RR. Applied only when the
# patient flag is True; default False → RR 1.0, no change.
#
# Voigt 2025 (PMID 41429031) — HBOT otologic adverse-event meta-analysis,
# n = 18,284, 54 studies. Sensory neuropathy flagged as a risk factor for
# MEB without a pooled OR. We pick RR 1.8 as a moderate modifier
# (consistent with the typical "moderate risk factor" range in the same
# meta-analysis for age and female sex); model-card modeler-prior.
SENSORY_NEUROPATHY_RR: float = 1.8

# Lee 2025 (PMID 40364015, PMID 40288902) — two monoplace-HBOT cohorts
# (n ≈ 300 each). Altered mental status OR 2.50 (1.13-5.51) and
# 3.16 (1.05-9.52) independently across both. Applies whenever volitional
# equalization is impaired (sedated HBOT, intoxicated or unconscious
# aeromedical evacuation, post-op altered sensorium).
IMPAIRED_VOLITIONAL_EQUALIZATION_RR: float = 3.0

# Sudhoff 2025 (PMID 40721956) — case series (n = 7) of
# semaglutide/tirzepatide-induced PET via Ostmann fat-pad atrophy during
# 8.2-18.7% weight loss. Low-confidence parameter; applied as a
# precautionary modifier with a narrow RR 1.4. Mechanistically coherent
# with Holm 2026 OFP atrophy finding (roadmap item 6).
GLP1_EXPOSURE_RR: float = 1.4

# ----------------------------------- v2.3.0 BDET post-treatment arm ---
# Swords 2025 Cochrane (PMID 40008607) — 9 RCTs, n = 684, ≤3 mo ETDQ-7
# MD -1.66 (95% CI -2.16 to -1.16); tympanometry-normalization RR 2.51
# (1.82-3.48). Sham-controlled ETDQ-7 MD at ≤3 mo -0.54 (-2.55, 1.47)
# — NS. Khan 2026 (PMID 41776716) — 23 studies, pooled n = 309,
# 1-year ETDQ-7 MD -2.03 (-2.59 to -1.47).
#
# We translate "ETDQ-7 improves by ~2 points out of a symptomatic
# baseline ~25" + "tympanometry ~2.5x more likely to normalize" into
# direct ET-function modifiers applied whenever patient.bdet_treated
# is True.
BDET_RA_MULT: float = 0.70          # 30% reduction in active resistance
BDET_OPENING_SHIFT_MMHG: float = -5.0  # mildly lowered passive opening threshold
BDET_EQ_RATE_MULT: float = 1.20     # 20% improvement in equalization efficiency
BDET_PER_DESCENT_RR: float = 0.65   # 35% reduction in per-descent MEB RR
# Clinical safety rule: BDET is contraindicated in PET. When
# patient.bdet_treated is True AND patient.pet is not 'normal', the
# composite modifier logs a warning note; the numerical effect is still
# applied (the model does not assume the clinician will ignore
# evidence-based contraindications).

# ----------------------------------------------- Hazard model thresholds -
# Hybrid Kanick-Doyle + Thalmann LEM hazard (see research brief 05).
BAROTITIS_THRESHOLD_MMHG: float = 250.0 * MMHG_PER_MMH2O      # ≈18.4  (Teed I)
BAROMYRINGITIS_THRESHOLD_MMHG: float = 1300.0 * MMHG_PER_MMH2O # ≈95.6 (Teed III-IV)
RUPTURE_THRESHOLD_MMHG: float = 150.0                          # Teed V (conservative)

# Hazard rate coefficients (fitted to hit FAC 5.8% career prevalence via
# Italian AF 2% per-exposure anchor, see calibration.py). These DEFAULTS
# are overwritten on import if ``calibrated.json`` is present in this
# package directory.
HAZARD_BAROTITIS_R: float = 5.0e-5         # 1/(mmHg^n · s)
HAZARD_BAROTITIS_N: float = 1.8            # peak-leaning (v2.1) — was 1.2
HAZARD_BAROMYRINGITIS_R: float = 1.5e-6
HAZARD_BAROMYRINGITIS_N: float = 2.5
HAZARD_RUPTURE_R: float = 5.0e-8
HAZARD_RUPTURE_N: float = 3.0


def _autoload_calibration() -> None:
    """Overwrite hazard rate constants from ``calibrated.json`` if present."""
    import json
    from pathlib import Path

    global HAZARD_BAROTITIS_R, HAZARD_BAROMYRINGITIS_R, HAZARD_RUPTURE_R
    p = Path(__file__).parent / "calibrated.json"
    if not p.exists():
        return
    try:
        data = json.loads(p.read_text())
        h = data.get("hazard", {})
        HAZARD_BAROTITIS_R = float(h.get("barotitis_r", HAZARD_BAROTITIS_R))
        HAZARD_BAROMYRINGITIS_R = float(h.get("baromyringitis_r", HAZARD_BAROMYRINGITIS_R))
        HAZARD_RUPTURE_R = float(h.get("rupture_r", HAZARD_RUPTURE_R))
    except (json.JSONDecodeError, OSError, ValueError):
        pass


_autoload_calibration()

# ------------------------------------------ Transmucosal gas constants --
# Doyle 2011 (PMID 21330076) species-specific first-order transmucosal
# exchange rate constants: dP_s/dt = -k_s (P_me_s - P_vb_s)
# Units: 1/min (exchange time constant t_1/2 = ln(2)/k_s).
TRANSMEM_K_O2_PER_MIN: float = 0.0113           # t_1/2 ≈ 61.6 min
TRANSMEM_K_CO2_PER_MIN: float = 0.0625          # t_1/2 ≈ 11.1 min
TRANSMEM_K_N2_PER_MIN: float = 0.0008           # KD2005 (t_1/2 many hours)
TRANSMEM_K_H2O_PER_MIN: float = 0.32            # H2O saturates quickly
TRANSMEM_CO2_O2_RATIO: float = 8.1              # Doyle 2011

# Venous blood partial pressures (steady-state, mmHg)
P_VB_O2_MMHG: float = 45.0
P_VB_CO2_MMHG: float = 46.0
P_VB_H2O_MMHG: float = 47.0

# Cabin/NP partial-pressure fractions (assumed constant)
F_N2: float = 0.79
F_O2: float = 0.21

# ----------------------------------------- FAC cohort (calibration target) -
# Colombian Aerospace Force (DIMAE) hypobaric chamber training pooled cohort
# 2010-2020 + 2025-2026. Pooled n = 173 clinical barotrauma events in 7,271
# chamber exposures; per-exposure rate 2.38% (Wilson 95% CI 2.06-2.75%);
# projected 3-exposure career rate 6.97%.
# Source: Malpica et al. (FAC internal, de-identified; see
# `docs/Cohort FAC/analysis/phase2_summary.md §5`).
# Used as the primary calibration anchor. URI and ET dysfunction dominate RFs.
FAC_TARGET_MEB_PREVALENCE: float = 0.0697     # 6.97% (career-3 projection)
FAC_COHORT_YEARS: int = 16
FAC_URI_TOP_RISK_FACTOR: bool = True
FAC_ETD_TOP_RISK_FACTOR: bool = True

# Population priors (FAC aircrew trainee demographics)
FAC_AGE_YEARS_RANGE: tuple[int, int] = (19, 45)
FAC_MALE_FRACTION: float = 0.90               # reasonable for FAC cadet intake
FAC_URI_ACTIVE_PREVALENCE: float = 0.08       # at time of profile ~8%
FAC_URI_RECENT_PREVALENCE: float = 0.15       # 8–14d
FAC_AR_PREVALENCE: float = 0.15
FAC_CRS_PREVALENCE: float = 0.03
FAC_PET_PREVALENCE: float = 0.01
FAC_ETD_MILD_PREVALENCE: float = 0.10
FAC_ETD_MODERATE_PREVALENCE: float = 0.03
FAC_ETD_SEVERE_PREVALENCE: float = 0.005

# ------------------------------------------------ Simulation defaults ---
DEFAULT_DT_S: float = 0.1                     # integrator step
MIN_DT_S: float = 0.01
MAX_DT_S: float = 1.0

VALSALVA_ACTIVE_WINDOW_S: float = 2.0          # seconds of elevated flow
VALSALVA_RESISTANCE_MULT: float = 0.25         # Valsalva reduces effective RA
VALSALVA_OPENING_SHIFT_MMHG: float = -5.0      # lowers NP-ET opening threshold
