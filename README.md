# Barotrauma Model — Middle-Ear Barotrauma Risk for Hypobaric Chamber Training

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.2.1-informational.svg)](CHANGELOG.md)
[![TRIPOD 2015](https://img.shields.io/badge/reporting-TRIPOD%202015-green.svg)](docs/submission/supplementary_S1_tripod_checklist.md)

Physics-informed, pathophysiology-aware middle-ear barotrauma (MEB) risk simulator. Calibrated to the Colombian Aerospace Force (FAC) DIMAE hypobaric-chamber registry 2010–2026 — 173 MEB events in 7,271 exposures (2.38% per-exposure; projected 6.97% career-3 prevalence); URI and ET dysfunction are the dominant risk factors. Externally validated against three published Italian Air Force cohorts without refitting.

**Authors:**
- **Dr. Diego L. Malpica, MD** — Aerospace Medicine, DIMAE, Colombian Aerospace Force ([ORCID 0000-0002-2257-4940](https://orcid.org/0000-0002-2257-4940))
- **Dr. Marian A. Farfán, MD** — Aerospace Medicine, DIMAE, Colombian Aerospace Force

---

## What this model does

Given a patient (anatomy + ET function + URI/PET/rhinitis state + medications) and a chamber profile (ascent, hold, descent, or rapid decompression), it simulates middle-ear pressure dynamics **asymmetrically**:

- **Ascent** (P_ambient falling, ME relatively overpressurized): Boyle-law TM expansion buffers the gradient; the ET opens passively on the ME side at ~26 mmHg and vents cheaply. Clearance is easy.
- **Descent** (P_ambient rising, ME underpressurized): Boyle compresses the ME gas; the cartilaginous ET lumen is collapsed from the NP side by tissue pressure. Passive opening is impossible — only active swallow or Valsalva can force the tube open, and each attempt fights a progressive Hagen-Poiseuille-style aperture collapse (see `aperture_factor` in `et_dynamics.py`). Clearance is hard, and harder with faster descent, mucosal inflammation, or Patulous-ET paradoxical closure.

It returns:

- **ΔP trajectory** (P_ME − P_ambient) through the exposure
- **Per-exposure probabilities** for three outcomes:
  - Barotitis media (Teed I+, ≥18.4 mmHg absolute ΔP)
  - Baromyringitis (Teed III–IV hemorrhage, ≥95.6 mmHg)
  - Tympanic-membrane rupture (Teed V, ≥150 mmHg)
- **Dominant risk factor** (URI / PET-S2 / severe obstruction / descent physics / etc.)
- **Recommended safe descent rate** for that patient
- Optional **95% credible intervals** via Monte-Carlo over physiology priors

---

## Scientific anchor

- **Physics core**: Kanick & Doyle 2005 ([PMID 15608090](https://pubmed.ncbi.nlm.nih.gov/15608090/)) + Doyle 2017 ([PMID 28917121](https://pubmed.ncbi.nlm.nih.gov/28917121/)) species-resolved gas exchange coupled back into ME pressure + Alper 2020 ([PMID 32176133](https://pubmed.ncbi.nlm.nih.gov/32176133/)) parameter distributions.
- **Aperture-collapse model**: continuous Hill-function aperture factor α(ΔP, dΔP/dt) ∈ [0,1] applied multiplicatively to active ET clearance; captures Hagen-Poiseuille r⁴ lumen compression under NP tissue pressure, rate-dependent viscoelastic lag, and inflammation tightening. Sobol sensitivity analysis identifies the aperture half-point (ΔP½ = 110 mmHg) as the dominant variance driver.
- **Active ET clearance**: swallow/Toynbee equalization scales with Kanick-Doyle active resistance (R_A) and active-open duration (T_A), so ETD and BDET modifiers affect actual clearance mechanics rather than only labels or posterior RR.
- **URI pathophysiology**: 6-state temporal modifier table (days 1–3, 4–7, 8–14, 15–21, 22–28) derived from Buchman 1994, McBride 1989, Doyle 1999, Chen 2022 (ETDQ-7 meta-analysis).
- **Patulous ET**: 4-state model (S1 baseline patent → S2 inflammation-induced paradoxical closure → S3 habitual sniffer → S4 post-plug) per Ikeda 2020/2024, Shindo 2025, Oshima 2025.
- **Calibration method**: deterministic log-space bisection of hazard constants against the FAC DIMAE 2010–2026 registry target, with an optional ABC-SMC (Approximate Bayesian Computation Sequential Monte Carlo) posterior sampler for uncertainty analysis.
- **Hazard model**: three-threshold cumulative hazard anchored to the FAC 2.38% per-exposure pooled rate and checked against Italian AF per-exposure barotitis cohorts (Morgagni 2010/2012, Landolfi 2009).
- **Medication effects**: Moayedi 2025 ([PMID 40819351](https://pubmed.ncbi.nlm.nih.gov/40819351/)) placebo-controlled HBOT RCT revised the pseudoephedrine RR from 0.70 → 0.90 (null preventive effect in chamber/HBOT context). Paradoxical decongestant worsening in PET retained at RR 1.40.
- Every constant and modifier in `barotrauma/v2/constants.py` has a citation.

Full literature briefs live in [`docs/research_notes/`](docs/research_notes/):

| File | Content |
|------|---------|
| [`01_mathematical_models.md`](docs/research_notes/01_mathematical_models.md) | Post-Kanick-Doyle physics models, Doyle 2017, Ghadiali FEM |
| [`02_uri_et_dysfunction.md`](docs/research_notes/02_uri_et_dysfunction.md) | URI temporal modifier table with effect sizes |
| [`03_patulous_et.md`](docs/research_notes/03_patulous_et.md) | PET 4-state model, JOS criteria, PHI-10 |
| [`04_chamber_epidemiology.md`](docs/research_notes/04_chamber_epidemiology.md) | FAC anchor, Italian AF, Israeli AF, chamber incidence data |
| [`05_ml_bayesian_hazard.md`](docs/research_notes/05_ml_bayesian_hazard.md) | ABC-SMC, Thalmann LEM, conformal prediction |
| [`06_2025_2026_updates.md`](docs/research_notes/06_2025_2026_updates.md) | 2025–2026 literature scan — 10 actionable findings |
| [`07_v23_scope_rationale.md`](docs/research_notes/07_v23_scope_rationale.md) | Rationale for deferring Zhang 2025 and Holm 2026 from v2.3.0 |

---

## Associated manuscripts

Three manuscripts are in active development from this codebase:

### Paper 1 — Prediction model (primary, under submission)

**Title:** *Physics-Informed Middle Ear Barotrauma Risk for Hypobaric Chamber Training: A Computational Prediction Model Calibrated to the Colombian Aerospace Force Cohort and Externally Validated Against Italian Air Force Cohorts*

- **File:** [`docs/manuscript.md`](docs/manuscript.md)
- **Article type:** Original Research — computational prediction model development + external validation
- **Reporting:** TRIPOD 2015 ([checklist S1](docs/submission/supplementary_S1_tripod_checklist.md))
- **Word count:** ~3,400 body · 248-word abstract · 24 refs · 4 tables · 2 figures
- **Submission target:** *Aerospace Medicine and Human Performance* (AMHP) — primary track
  - Status: 5 FAIL items pending from 2026-04-18 compliance audit ([`docs/submission/2026-04-18_amhp_compliance_audit.md`](docs/submission/2026-04-18_amhp_compliance_audit.md))
  - Portal: <https://www.editorialmanager.com/AMHP/>
- **Journal decision tree** if AMHP rejects (by score):
  - Tier A: Otology & Neurotology (Q1, score 84) · European Archives ORL (Q1, score 83)
  - Tier B: Auris Nasus Larynx (Q2, score 81 — 3 cited papers, strongest scope lineage)
  - Tier C: Journal of Applied Physiology (Q1, score 80, S2O = $0 APC)
  - Full analysis: [`docs/2026-04-19_journal-scout_meb-model.md`](docs/2026-04-19_journal-scout_meb-model.md)
- **Cover letters:** [`docs/cover_letter.md`](docs/cover_letter.md) (AMHP) · [`docs/cover_letter_fac_cohort.md`](docs/cover_letter_fac_cohort.md) · [`docs/cover_letter_preflight_fidelity.md`](docs/cover_letter_preflight_fidelity.md)

### Paper 2 — FAC cohort epidemiology

**Title:** *Ten-Year Epidemiology of Middle-Ear Barotrauma in Colombian Aerospace Force Hypobaric-Chamber Training (DIMAE Registry 2010–2026)*

- **File:** [`docs/manuscript_fac_cohort.md`](docs/manuscript_fac_cohort.md)
- Incidence time-series + denial-rate forest plot (Figures 1 and 2, 600 dpi TIFF)
- Reports the 7,271-exposure DIMAE registry underlying the model's calibration anchor
- Standalone epidemiological companion to Paper 1

### Paper 3 — Preflight screening instrument

**Title:** Preflight fidelity and discriminatory performance of the DIMAE Microsoft Forms screening instrument

- **File:** [`docs/manuscript_preflight_fidelity.md`](docs/manuscript_preflight_fidelity.md)
- ROC AUC 0.81 for the DIMAE preflight questionnaire in predicting MEB during training
- Methodological companion establishing the screening instrument's validity

---

## Install

```bash
git clone https://github.com/strikerdlm/barotrauma_model
cd barotrauma_model
pip install -e .
```

Requires Python ≥ 3.8, numpy, scipy. Full requirements in [`requirements.txt`](requirements.txt).

---

## Quick start

```python
from barotrauma.v2 import simulate, PatientState, EtFunction
from barotrauma.v2.scenarios import FAC_BOGOTA_DEFAULT, USAFSAM_TYPE_I

# Healthy pilot, FAC chamber profile
result = simulate(PatientState(), FAC_BOGOTA_DEFAULT)
print(result.risk.p_barotitis)            # ~0.024 (2.4%)
print(result.risk.risk_category())        # "low"
print(result.risk.dominant_risk_factor)   # "Baseline"

# Pilot with peak-URI (day 4–7) and allergic rhinitis, USAFSAM Type I
risky = PatientState(uri="day_4_7", rhinitis="allergic")
r2 = simulate(risky, USAFSAM_TYPE_I)
print(r2.risk.p_barotitis)               # ~0.08 → HIGH
print(r2.risk.dominant_risk_factor)       # "Acute URI (day_4_7)"
print(r2.risk.recommended_max_descent_ft_min)
```

Available chamber profiles:

| Key | Description |
|---|---|
| `USAFSAM_TYPE_I` | 25,000 ft, 2,000 ft/min ascent, 5,000 ft/min descent |
| `USAFSAM_TYPE_II_RD` | Rapid decompression 8,000 → 35,000 ft in 1 s |
| `ISRAELI_AF_POST_2022` | 45-min O₂ preoxygenation + 25,000 ft (Nakdimon PMID 36309795) |
| `FAC_BOGOTA_DEFAULT` | Bogotá-sited chamber (starts at 8,530 ft) |
| `COMMERCIAL_CABIN_DESCENT` | 600 ft/min cabin descent (Kanick-Doyle reference) |
| `RAPID_DESCENT_10K_FT_MIN` | Worst-case stress test |
| `SLOW_DESCENT_1K_FT_MIN` | Best-case slow descent |
| `GROTH_1986_VALIDATION` | Kanick-Doyle 2005 Fig 3 validation profile |
| `ITALIAN_AF_25K` | Italian AF 25,000 ft validation profile |
| `ITALIAN_AF_35K` | Italian AF 35,000 ft validation profile |

---

## Model states

### URI timecourse
| State | Mechanism | RA × | MEB RR |
|---|---|---|---|
| `none` | Baseline | 1.0 | 1.0 |
| `day_1_3` | Early onset | 2.0 | 2.5 |
| `day_4_7` | **Peak dysfunction** | 3.5 | 4.25 |
| `day_8_14` | Recovery | 1.8 | 2.0 |
| `day_15_21` | Residual | 1.3 | 1.3 |
| `day_22_28` | Near-baseline | 1.1 | 1.1 |

### Patulous Eustachian Tube (PET)
| State | Behavior | Barotrauma risk |
|---|---|---|
| `normal` | No PET | Baseline |
| `s1` | Baseline patent | Rupture-protective (Kanick-Doyle) |
| `s2` | PET + inflammation / recumbency | **HIGH** — paradoxical closure |
| `s3` | Habitual sniffer | Elevated (sustained −ME pressure; Oshima 2025 OR 8.18) |
| `s4` | Post-Kobayashi plug | Stenotic-equivalent |

### Chronic rhinitis
| State | RA × | MEB RR |
|---|---|---|
| `none` | 1.0 | 1.0 |
| `allergic` | 1.3 | 1.5 |
| `chronic_rhinosinusitis` | 1.5 | 2.0 |

### Medications
| Medication | RR (healthy) | RR in PET |
|---|---|---|
| `none` | 1.00 | 1.00 |
| `pseudoephedrine_oral` | 0.90 (Moayedi 2025) | **1.40** (paradoxical) |
| `oxymetazoline_topical` | 0.95 | **1.40** (paradoxical) |
| `intranasal_steroid` | 0.65 | 0.65 |
| `antihistamine_spray` | 0.70 | 0.70 |

### v2.3.0 covariates (unreleased)
| Field | RR | Evidence |
|---|---|---|
| `sensory_neuropathy` | 1.8 | Voigt 2025 PMID 41429031 |
| `impaired_volitional_equalization` | 3.0 | Lee 2025 PMID 40364015/40288902 |
| `glp1_exposure` | 1.4 | Sudhoff 2025 PMID 40721956 (semaglutide/tirzepatide-induced PET) |
| `bdet_treated` | RA ×0.70, RR ×0.65 | Swords 2025 Cochrane PMID 40008607 + Khan 2026 PMID 41776716 |

---

## Calibration

The hazard-rate constants in `constants.py` ship pre-calibrated to the FAC 2010–2026 pooled registry. The persisted `calibrated.json` values are generated by deterministic log-space bisection against the cohort mean; the ABC-SMC sampler (`barotrauma/v2/abc_smc.py`) remains available to jointly infer (r_barotitis, r_bmrg, r_rupture) against multiple summary statistics (cohort mean + URI gradient + severity gradient).

```bash
python -m barotrauma.v2.calibration --target 0.0238 --n 400 --save
```

Results are written to `barotrauma/v2/calibrated.json` and auto-loaded on next import.

**Development cohort anchor:** FAC DIMAE 2010–2026 registry — 173 MEB events / 7,271 exposures = 2.38% per-exposure (Wilson 95% CI 2.06–2.75%); projected 3-exposure career rate 6.97%.

**External validation (Italian AF, not used in fitting):**

| Cohort | Observed | Simulated | Status |
|--------|----------|-----------|--------|
| Morgagni 2012 (25k ft) | 2.3% [1.13–4.62%] | 3.78% | Inside Wilson 95% CI |
| Landolfi 2009 | 2.4% [1.22–4.66%] | 3.78% | Inside Wilson 95% CI |
| Morgagni 2010 (mixed) | 1.5% [0.96–2.34%] | 3.78% (+2.28 pp) | Outside Wilson CI; within mixed-denominator tolerance |

---

## Testing

```bash
pip install pytest
pytest tests/test_v2_physics.py tests/test_v2_pathophysiology.py \
       tests/test_v2_risk.py tests/test_v2_scenarios.py \
       tests/test_v2_aperture.py tests/test_v2_validation.py \
       tests/test_v2_abc_smc.py tests/test_v2_sensitivity.py
# Slow (runs calibration loops):
pytest tests/test_v2_calibration.py
```

The full v2 suite covers 122 tests: physics monotonicity, pathophysiology modifier composition, hazard-model properties, active-resistance clearance, aperture asymmetry and rate tightening, external validation against Italian AF benchmarks, ABC-SMC convergence, Sobol sensitivity, Kanick-Doyle 2005 Fig 3 pinned baseline, calibration convergence, muscle mechanics, Doyle 2017 multi-pathway gas exchange, and career-simulation API.

---

## Repository structure

```
barotrauma_model/
├── barotrauma/
│   ├── v2/                       # current model — build against this
│   │   ├── types.py              # PatientState, ChamberProfile, SimulationResult
│   │   ├── constants.py          # All physiology constants, with citations
│   │   ├── atmosphere.py         # altitude ↔ pressure, profile discretization
│   │   ├── anatomy.py            # population priors for mastoid volume, TM compliance
│   │   ├── pathophysiology.py    # URI/PET/rhinitis/medication state machine
│   │   ├── et_dynamics.py        # ET opening mechanics + aperture_factor()
│   │   ├── et_muscle.py          # Ghadiali FEM-inspired time-varying active resistance
│   │   ├── middle_ear.py         # TM displacement, Boyle buffering, gas exchange
│   │   ├── scenarios.py          # chamber-profile presets (10 included)
│   │   ├── engine.py             # main integrator → SimulationResult
│   │   ├── risk.py               # three-threshold cumulative hazard model
│   │   ├── calibration.py        # log-space bisection calibration CLI
│   │   ├── abc_smc.py            # ABC-SMC joint sampler
│   │   ├── sensitivity.py        # Saltelli-Sobol global sensitivity analysis
│   │   ├── validation.py         # Italian AF external validation benchmarks
│   │   ├── career.py             # multi-exposure career simulation API
│   │   ├── ml_hybrid.py          # physics-ML residual head (unfit scaffold)
│   │   ├── abc_posterior.json    # ABC-SMC posterior (weighted particles)
│   │   ├── calibrated.json       # persisted hazard constants (auto-loaded)
│   │   └── sobol_indices.json    # Sobol SA results cache
│   └── legacy/                   # frozen v1 stack, do not extend
├── tests/
│   ├── test_v2_physics.py
│   ├── test_v2_pathophysiology.py
│   ├── test_v2_risk.py
│   ├── test_v2_scenarios.py
│   ├── test_v2_aperture.py
│   ├── test_v2_validation.py
│   ├── test_v2_abc_smc.py
│   ├── test_v2_sensitivity.py
│   ├── test_v2_calibration.py
│   ├── test_v2_muscle.py
│   ├── test_v2_doyle2017.py
│   ├── test_v2_ml_hybrid.py
│   ├── test_v2_career.py
│   └── test_v2_kanick_doyle_fig3.py
├── docs/
│   ├── manuscript.md             # Paper 1 — prediction model (active AMHP submission)
│   ├── manuscript_fac_cohort.md  # Paper 2 — FAC cohort epidemiology
│   ├── manuscript_preflight_fidelity.md  # Paper 3 — preflight screening instrument
│   ├── manuscript_author_page.md # Depersonalized title page for Editorial Manager
│   ├── model_card.md             # Inputs / outputs / assumptions / limitations
│   ├── cover_letter.md           # AMHP cover letter
│   ├── 2026-04-19_journal-scout_meb-model.md  # Journal scout report (all candidates)
│   ├── figures/
│   │   ├── figure1_descent_rate_sensitivity.tiff  # 600 dpi AMHP-ready
│   │   └── figure2_sobol_indices.tiff             # 600 dpi AMHP-ready
│   ├── research_notes/           # 7 structured literature briefs
│   └── submission/               # AMHP compliance audit, upload playbook, TRIPOD S1
├── api/                          # FastAPI sidecar (Python) — JSON prediction endpoint
├── frontend/                     # React/TS dashboard (Vite + Tailwind + ECharts)
├── models/
│   ├── Literature/               # Structured literature PDFs / note files
│   └── middle_ear_model-matlab/  # Original MATLAB reference implementation
├── analysis/                     # Standalone analysis scripts and figures
├── app/                          # Streamlit dashboard (legacy prototype)
├── CHANGELOG.md                  # Full semantic-version history
├── HOW_TO_CONTINUE.md            # Prioritized next iterations
├── MIGRATION.md                  # v1 → v2 API migration guide
├── FUTURE_WORK.md                # v1-era roadmap (mostly superseded by v2)
└── README.md
```

---

## Known limitations (v2.2.1)

- **FAC anchor is unpublished.** The DIMAE 2010–2026 pooled rate (2.38% per-exposure / 6.97% career-3) is an internal institutional prior pending peer review. Papers 1 and 2 in preparation; treat as calibration prior, not cited external validation.
- **TM rupture threshold (150 mmHg) is conservative.** Biomechanical studies report higher real rupture pressures (~600–750 mmHg). `p_rupture` should be read as "imminent rupture risk" / comparative profile ranking, not an absolute clinical probability.
- **`p_barotitis` is not monotonic in descent rate in isolation.** With the v2.1 aperture model and peak-weighted hazard exponent (n = 1.8), the barotitis peak lies in the 2,000–3,000 ft/min zone, matching Italian AF chamber data. The rupture probability and peak |ΔP| are monotonic. Compare the full triple (`p_barotitis`, `p_baromyringitis`, `p_rupture`), not `p_barotitis` alone.
- **No per-subject ML head.** `ml_hybrid.py` is an unfit scaffold. No clinical individual-level tympanometry or FRT data are integrated.
- **Valsalva is idealized** as a 2-s bolus with a multiplicative FGE boost (0.55 per pulse). Real efficacy varies with anatomy and technique.
- **Full time-varying R_A (Ghadiali FEM) is not implemented.** Static Kanick-Doyle R_A and active-open duration now scale per-swallow clearance, and `et_muscle.py` provides a lumped time-varying approximation; the full 2-D FEM is not run per integration step.
- **No inter-exposure carry-over.** `career.simulate_career` composes independent `simulate()` calls; ME gas-composition and mucosal-fatigue state reset between exposures.
- **Population priors are FAC-demographic.** Re-calibrate before applying to pediatric, geriatric, or diving populations.

See [`docs/model_card.md`](docs/model_card.md) for the full assumption table, modeler-prior list, and v2.3.0 deferred-items analysis.

---

## License

MIT. See [LICENSE](LICENSE).

---

## Citation

If you use this software, please cite:

> Malpica DL, Farfán MA (2026). *Physics-informed middle-ear barotrauma risk prediction for hypobaric-chamber training, anchored to the Colombian Aerospace Force cohort.* `barotrauma_model` v2.2.1. Subdirectorate of Aerospace Sciences, Direction of Aerospace Medicine (DIMAE), Colombian Aerospace Force. https://github.com/strikerdlm/barotrauma_model

Once published, cite the journal paper (Paper 1) as the primary reference for the model methodology. The software repository is the reference for the open-source implementation.
