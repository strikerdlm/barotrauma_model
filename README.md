# Barotrauma Model — Middle-Ear Barotrauma Risk for Hypobaric Chamber Training

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.1.0-informational.svg)](CHANGELOG.md)

Physics-informed, pathophysiology-aware middle-ear barotrauma (MEB) risk
simulator. Calibrated to the Colombian Aerospace Force (FAC) 10-year
hypobaric-chamber cohort — 5.8% career MEB prevalence, URI and ET
dysfunction as the dominant risk factors.

**Maintainer:** Dr. Diego L. Malpica, MD — Aerospace Medicine, Colombia
([ORCID 0000-0002-2257-4940](https://orcid.org/0000-0002-2257-4940))

---

## What this model does

Given a patient (anatomy + ET function + URI/PET/rhinitis state + medications)
and a chamber profile (ascent, hold, descent, or rapid decompression), it
simulates middle-ear pressure dynamics **asymmetrically**:

- **Ascent** (P_ambient falling, ME relatively overpressurized): Boyle-law
  TM expansion buffers the gradient; the ET opens passively on the ME side
  at ~26 mmHg and vents cheaply. Clearance is easy.
- **Descent** (P_ambient rising, ME underpressurized): Boyle compresses the
  ME gas; the cartilaginous ET lumen is collapsed from the NP side by
  tissue pressure. Passive opening is impossible — only active swallow or
  Valsalva can force the tube open, and each attempt fights progressive
  Hagen-Poiseuille-style aperture collapse (see `aperture_factor` in
  `et_dynamics.py`). Clearance is hard, and harder with faster descent,
  mucosal inflammation, or Patulous-ET paradoxical closure.

It returns:

- **ΔP trajectory** (P_ME − P_ambient) through the exposure
- **Per-exposure probabilities** for three outcomes:
  - Barotitis media (Teed I+, ≥18 mmHg absolute ΔP)
  - Baromyringitis (Teed III–IV hemorrhage, ≥96 mmHg)
  - Tympanic-membrane rupture (Teed V, ≥150 mmHg)
- **Dominant risk factor** (URI / PET-S2 / severe obstruction / descent
  physics / etc.)
- **Recommended safe descent rate** for that patient
- Optional **95% credible intervals** via Monte-Carlo over physiology priors

---

## Scientific anchor

- **Physics core**: Kanick & Doyle 2005 ([PMID 15608090](https://pubmed.ncbi.nlm.nih.gov/15608090/))
  + Doyle 2017 ([PMID 28917121](https://pubmed.ncbi.nlm.nih.gov/28917121/))
  species-resolved gas exchange + Alper 2020 ([PMID 32176133](https://pubmed.ncbi.nlm.nih.gov/32176133/))
  parameter distributions.
- **URI pathophysiology**: 6-state temporal modifier table (days 1–3, 4–7,
  8–14, 15–21, 22–28) derived from Buchman 1994, McBride 1989, Doyle 1999,
  Chen 2022 (ETDQ-7 meta-analysis).
- **Patulous ET**: 4-state model (S1 baseline patent → S2 inflammation-
  induced closure → S3 habitual sniffer → S4 post-plug) per Ikeda
  2020/2024, Shindo 2025.
- **Hazard model**: three-threshold cumulative hazard, fitted against the
  Italian AF ([Morgagni 2010/2012](https://pubmed.ncbi.nlm.nih.gov/22764614/))
  per-exposure barotitis rate (1.5–2.5%) and projected to the FAC 5.8%
  career anchor.
- Every constant and modifier in `barotrauma/v2/constants.py` has a citation.

Full literature briefs live in [`docs/research_notes/`](docs/research_notes/):

- [`01_mathematical_models.md`](docs/research_notes/01_mathematical_models.md)
- [`02_uri_et_dysfunction.md`](docs/research_notes/02_uri_et_dysfunction.md)
- [`03_patulous_et.md`](docs/research_notes/03_patulous_et.md)
- [`04_chamber_epidemiology.md`](docs/research_notes/04_chamber_epidemiology.md)
- [`05_ml_bayesian_hazard.md`](docs/research_notes/05_ml_bayesian_hazard.md)

---

## Install

```bash
git clone https://github.com/strikerdlm/barotrauma_model
cd barotrauma_model
pip install -e .
```

Requires Python ≥ 3.8, numpy, scipy. Full requirements in
[`requirements.txt`](requirements.txt).

---

## Quick start

```python
from barotrauma.v2 import simulate, PatientState, EtFunction
from barotrauma.v2.scenarios import FAC_BOGOTA_DEFAULT, USAFSAM_TYPE_I

# Healthy pilot, FAC chamber profile
result = simulate(PatientState(), FAC_BOGOTA_DEFAULT)
print(result.risk.p_barotitis)            # ~0.012 (1.2%)
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

---

## Model states

### URI timecourse
| State | Mechanism | RA × | MEB RR |
|---|---|---|---|
| `none` | Baseline | 1.0 | 1.0 |
| `day_1_3` | Early onset | 2.0 | 2.5 |
| `day_4_7` | Peak dysfunction | 3.5 | 4.25 |
| `day_8_14` | Recovery | 1.8 | 2.0 |
| `day_15_21` | Residual | 1.3 | 1.3 |
| `day_22_28` | Near-baseline | 1.1 | 1.1 |

### Patulous Eustachian Tube (PET)
| State | Behavior | Barotrauma risk |
|---|---|---|
| `normal` | No PET | Baseline |
| `s1` | Baseline patent | Rupture-protective (Kanick-Doyle) |
| `s2` | PET + inflammation / recumbency | **HIGH** — paradoxical closure |
| `s3` | Habitual sniffer | Elevated (sustained −ME pressure) |
| `s4` | Post-Kobayashi plug | Stenotic-equivalent |

### Chronic rhinitis
| State | RA × | MEB RR |
|---|---|---|
| `none` | 1.0 | 1.0 |
| `allergic` | 1.3 | 1.5 |
| `chronic_rhinosinusitis` | 1.5 | 2.0 |

### Medications
| Medication | Baseline RR | RR in PET |
|---|---|---|
| `none` | 1.00 | 1.00 |
| `pseudoephedrine_oral` | 0.70 | **1.40** (paradoxical) |
| `oxymetazoline_topical` | 0.95 | **1.40** (paradoxical) |
| `intranasal_steroid` | 0.65 | 0.65 |
| `antihistamine_spray` | 0.70 | 0.70 |

---

## Calibration

The hazard-rate constants in `constants.py` ship pre-calibrated. To
re-calibrate against a different cohort or target prevalence:

```bash
python -m barotrauma.v2.calibration --target 0.02 --n 400 --save
```

This performs log-space bisection on `HAZARD_BAROTITIS_R` until the cohort
mean per-exposure `p_barotitis` matches the target. Results are written to
`barotrauma/v2/calibrated.json` and auto-loaded on next import.

Default FAC anchor: 2.0% per-exposure in pre-screened aircrew → 5.8% career
over ~3 exposures, matching the FAC 10-year cohort.

---

## Testing

```bash
pip install pytest
pytest tests/test_v2_physics.py tests/test_v2_pathophysiology.py \
       tests/test_v2_risk.py tests/test_v2_scenarios.py
# Slow (runs calibration loops):
pytest tests/test_v2_calibration.py
```

---

## Repository structure

```
barotrauma_model/
├── barotrauma/
│   ├── v2/                  # current model — build against this
│   │   ├── types.py          # PatientState, ChamberProfile, SimulationResult
│   │   ├── constants.py      # All physiology constants, with citations
│   │   ├── atmosphere.py     # altitude ↔ pressure, profile discretization
│   │   ├── anatomy.py        # population priors for mastoid volume, etc.
│   │   ├── pathophysiology.py # URI/PET/rhinitis modifier state machine
│   │   ├── et_dynamics.py    # Eustachian-tube opening mechanics
│   │   ├── middle_ear.py     # TM displacement, trans-mucosal gas exchange
│   │   ├── scenarios.py      # chamber-profile presets
│   │   ├── engine.py         # main integrator → SimulationResult
│   │   ├── risk.py           # three-threshold hazard model
│   │   ├── calibration.py    # ABC-style bisection calibration
│   │   └── calibrated.json   # persisted hazard constants (auto-loaded)
│   └── legacy/              # frozen v1 stack, do not extend
├── tests/
│   ├── test_v2_physics.py
│   ├── test_v2_pathophysiology.py
│   ├── test_v2_risk.py
│   ├── test_v2_scenarios.py
│   └── test_v2_calibration.py
├── docs/
│   ├── model_card.md         # inputs/outputs/limitations
│   ├── research_notes/       # 5 structured literature briefs
│   └── README.md
├── app/                     # Streamlit dashboard (legacy; see HOW_TO_CONTINUE)
├── CHANGELOG.md
├── HOW_TO_CONTINUE.md       # roadmap for next iterations
├── MIGRATION.md             # v1 → v2 API migration
└── README.md
```

---

## Known limitations (v2.0)

- The FAC 5.8% anchor is currently unpublished DIMAE cohort data. Treat as
  internal priors until formally published.
- TM rupture threshold (150 mmHg) is a conservative placeholder; real TM
  rupture pressures are higher (~600–750 mmHg in biomechanical studies).
  The v2 hazard at 150 mmHg should be interpreted as "imminent rupture risk."
- **`p_barotitis` is NOT monotonic in descent rate.** The barotitis hazard
  exponent is sub-quadratic, so dose-time integral dominates — a slow,
  long descent can out-score a fast, brief descent for Teed-I transudative
  risk. Peak |ΔP| and `p_rupture` remain monotonic. See
  [`docs/model_card.md`](docs/model_card.md) §6 for the physiological
  rationale. Rule of thumb: compare the full triple
  (`p_barotitis`, `p_baromyringitis`, `p_rupture`), not `p_barotitis` alone.
- No per-subject machine-learning head is implemented (see
  `HOW_TO_CONTINUE.md`). Training data are not yet available.
- Valsalva is modeled as an idealized bolus every 120 s. The published FEM
  (Ghadiali group) time-varying R_A is not used in v2.0.
- Multiple sequential chamber exposures within a day are not modeled (no
  inter-exposure ME gas-composition carry-over).

See [`docs/model_card.md`](docs/model_card.md) for the full assumption and
modeler-prior list.

---

## License

MIT. See [LICENSE](LICENSE).

## Citation

Preferred citation (manuscript in prep):

> Malpica, D.L. (2026). *barotrauma_model v2: Physics-informed middle-ear
> barotrauma risk prediction for hypobaric-chamber training, anchored to the
> Colombian Aerospace Force cohort.* Version 2.0.0.
> https://github.com/strikerdlm/barotrauma_model
