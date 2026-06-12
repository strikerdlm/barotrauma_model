# Barotrauma Model — Middle-Ear Barotrauma Risk for Hypobaric Chamber Training

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-2.2.1-informational.svg)

Physics-informed, pathophysiology-aware middle-ear barotrauma (MEB) risk simulator. Calibrated to the Colombian Aerospace Force (FAC) DIMAE hypobaric-chamber registry 2010–2026 — 173 MEB events in 7,271 exposures (2.38% per-exposure; projected 6.97% career-3 prevalence); URI and ET dysfunction are the dominant risk factors. Externally validated against three published Italian Air Force cohorts without refitting.

**Repository boundary:** this repo is for model code, tests, APIs, dashboards, reproducibility outputs, and project-level markdown. Manuscript submission packages, rejection tracking, cover letters, journal-specific files, and upload-ready artifacts belong in `/root/repos/manuscripts/barotrauma` and remote `https://github.com/strikerdlm/manuscripts`. See [`MANUSCRIPT_BOUNDARY.md`](MANUSCRIPT_BOUNDARY.md).

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
- **Aperture-collapse model**: continuous Hill-function aperture factor α(ΔP, dΔP/dt) ∈ [0,1] applied multiplicatively to active ET clearance; captures Hagen-Poiseuille r⁴ lumen compression under NP tissue pressure, rate-dependent viscoelastic lag, and inflammation tightening. Production-grade Saltelli-Sobol sensitivity analysis (N = 128 base samples, 768 model evaluations, scrambled-Sobol QMC, seed 2026) identifies the aperture half-point (ΔP½ = 110 mmHg) as the dominant variance driver in per-exposure p_barotitis (S_T = 0.99, S_i = 0.97) — approximately fifty-fold above the next-largest indices (descent-phase swallow frequency S_T = 0.020, aperture free-zone S_T = 0.019, mastoid volume S_T = 0.005).
- **Active ET clearance**: swallow/Toynbee equalization scales with Kanick-Doyle active resistance (R_A) and active-open duration (T_A), so ETD and BDET modifiers affect actual clearance mechanics rather than only labels or posterior RR.
- **URI pathophysiology**: 6-state temporal modifier table (days 1–3, 4–7, 8–14, 15–21, 22–28) derived from Buchman 1994, McBride 1989, Doyle 1999, Chen 2022 (ETDQ-7 meta-analysis).
- **Patulous ET**: 4-state model (S1 baseline patent → S2 inflammation-induced paradoxical closure → S3 habitual sniffer → S4 post-plug) per Ikeda 2020/2024, Shindo 2025, Oshima 2025.
- **Calibration method**: deterministic log-space bisection of hazard constants against the FAC DIMAE 2010–2026 registry target, with an optional ABC-SMC (Approximate Bayesian Computation Sequential Monte Carlo) posterior sampler for uncertainty analysis.
- **Hazard model**: three-threshold cumulative hazard anchored to the FAC 2.38% per-exposure pooled rate and checked against Italian AF per-exposure barotitis cohorts (Morgagni 2010/2012, Landolfi 2009).
- **Medication effects**: Moayedi 2025 ([PMID 40819351](https://pubmed.ncbi.nlm.nih.gov/40819351/)) placebo-controlled HBOT RCT revised the pseudoephedrine RR from 0.70 → 0.90 (null preventive effect in chamber/HBOT context). Paradoxical decongestant worsening in PET retained at RR 1.40.
- Every constant and modifier in `barotrauma/v2/constants.py` has a citation.

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
result = simulate(PatientState(), FAC_BOGOTA_DEFAULT, rng_seed=2026)
print(result.risk.p_barotitis)            # ~0.0038 (0.38%)
print(result.risk.risk_category())        # "low"
print(result.risk.dominant_risk_factor)   # "Descent profile pressure exposure"

# Pilot with peak-URI (day 4–7) and allergic rhinitis, USAFSAM Type I
risky = PatientState(uri="day_4_7", rhinitis="allergic")
r2 = simulate(risky, USAFSAM_TYPE_I, rng_seed=2026)
print(r2.risk.p_barotitis)                # ~1.0
print(r2.risk.risk_category())            # "very_high"
print(r2.risk.dominant_risk_factor)       # "Acute URI (day_4_7)"
print(r2.risk.recommended_max_descent_ft_min)  # 600
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

## Interactive dashboard (React frontend + FastAPI backend)

The web dashboard is a **two-process** application. The physics never runs in
the browser — the React/TypeScript UI (`frontend/`) calls a thin FastAPI
sidecar (`api/`) that wraps `barotrauma.v2`, so the Python engine stays the
single source of truth.

```
browser → http://localhost:3000  (Vite dev server, React UI)
                │  Vite proxies every /api/* request to ↓
                └────────────────────→ http://localhost:8000  (uvicorn → api.main:app → barotrauma.v2)
```

**Both processes must be running.** If you start only the frontend, every
`/api/*` call fails: the Vite proxy returns `API 500` (nothing on `:8000`), or
`API 404 …{"detail":"Not Found"}` if a *different* server happens to occupy
`:8000`. See [Troubleshooting](#troubleshooting-the-dashboard) below.

### Prerequisites

- **Python ≥ 3.8** in a virtual environment (do **not** use a bare system /
  Homebrew Python — those usually have no `fastapi`, which is the most common
  cause of a dead backend).
- **Node.js ≥ 18** and npm (verified on Node 22 / npm 10).

### Step by step

**Terminal 1 — start the backend (from the repository root):**

```bash
cd barotrauma_model
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r api/requirements.txt   # fastapi, uvicorn, pydantic, numpy
uvicorn api.main:app --reload --port 8000
```

Run `uvicorn` **from the repository root** so the `api.main:app` import string
resolves and `barotrauma.v2` is importable. Confirm it is up:

```bash
curl http://localhost:8000/api/health
# → {"status":"ok","version":"2.2.1"}
```

**Terminal 2 — start the frontend:**

```bash
cd barotrauma_model/frontend
npm install            # first run only
npm run dev
```

Then open **http://localhost:3000**. The chamber-profile picker populates from
`GET /api/scenarios`, and **Run simulation** posts to `POST /api/simulate`.
The Vite proxy (`frontend/vite.config.ts`) forwards `/api/*` to `:8000`, so no
CORS or base-URL configuration is needed in development.

### Verify the full path (optional)

With both servers up, exercise the same loop the UI uses — *through the proxy*:

```bash
curl http://localhost:3000/api/scenarios          # 10 presets
curl -X POST http://localhost:3000/api/simulate \
  -H 'Content-Type: application/json' \
  -d '{"patient":{},"profile":{"preset":"fac_bogota_default"},"options":{}}'
```
### Summary
Terminal 1 — backend, leave it running (do NOT Ctrl+C it):
cd E:\Github\barotrauma_model
python -m uvicorn api.main:app --port 8000
Then, in any window, confirm which server owns :8000:
curl.exe http://localhost:8000/api/health
- {"status":"ok","version":"2.2.1"} → correct backend is up. Good.
- A different body / Not Found → another program holds :8000 (see below). Your own uvicorn would have failed to bind with address already in use — check Terminal 1 for that.

### Troubleshooting the dashboard

| Symptom in the UI / console | Cause | Fix |
|---|---|---|
| `Failed to load presets: API 404 at /api/scenarios: {"detail":"Not Found"}` and/or `API 404 at /api/simulate` | A *different* FastAPI app is answering on `:8000` (e.g. another project that also defaults to port 8000). The exact `{"detail":"Not Found"}` body is Starlette's default 404 — it can only come from a live server that lacks these routes, so the wrong backend is up. | Stop the other server (or see "port in use" below) and start this one (Terminal 1). Confirm it is the right one: `curl localhost:8000/api/health` must return `…"version":"2.2.1"`. |
| `Failed to load presets: API 500 at /api/scenarios …` (and the **dev-server** terminal logs a proxy / `ECONNREFUSED` error) | **Nothing is listening on `:8000`.** The Vite proxy cannot reach the backend and returns HTTP 500. This is the symptom when you forgot to start the backend at all. | Start the backend in Terminal 1 and leave it running; reload the page. |
| `Network error calling /api/scenarios … Is the Python API running on :8000?` | `fetch` itself could not connect — i.e. there is **no dev proxy** in front of the request. Happens in a production build, or when `VITE_API_BASE` points at an unreachable host. | Ensure the API host in `VITE_API_BASE` is reachable; in dev, just use the proxy (leave `VITE_API_BASE` unset). |
| Backend won't start: `ModuleNotFoundError: No module named 'fastapi'` | `uvicorn` was launched in a Python without the API deps (system/Homebrew interpreter). | `source .venv/bin/activate`, then `pip install -r api/requirements.txt`, then re-run `uvicorn`. |
| Backend won't start: `ModuleNotFoundError: No module named 'numpy'` | Older `api/requirements.txt` omitted numpy (the engine needs it). | Pull latest, then `pip install -r api/requirements.txt` (numpy is now listed). |
| `uvicorn` errors with `[Errno 98] address already in use` | Port 8000 is taken (often another project's API — the same situation that produces the 404 row above). | Stop the other process, or run the backend on a free port — `uvicorn api.main:app --port 8010` — and point the frontend at it with `VITE_API_BASE=http://localhost:8010 npm run dev`. |

### Production build

```bash
cd frontend
npm run build        # static bundle in frontend/dist/
```

The built bundle has no dev proxy, so set the API origin at build/serve time:

```bash
VITE_API_BASE=https://your-api-host npm run build
```

`VITE_API_BASE` is read in `frontend/src/lib/v2api.ts`; when unset (dev), all
calls are same-origin and ride the Vite proxy. See [`api/README.md`](api/README.md)
for the full endpoint contract and request/response shapes.

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
| Morgagni 2012 (25k ft) | 2.3% [1.13–4.62%] | 3.79% | Inside Wilson 95% CI |
| Landolfi 2009 | 2.4% [1.22–4.66%] | 3.79% | Inside Wilson 95% CI |
| Morgagni 2010 (mixed) | 1.5% [0.96–2.34%] | 3.79% (+2.29 pp) | Outside Wilson CI; within mixed-denominator tolerance |

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

The full v2 suite covers 123 tests: physics monotonicity, pathophysiology modifier composition, hazard-model properties, active-resistance clearance, aperture asymmetry and rate tightening, external validation against Italian AF benchmarks, ABC-SMC convergence, Sobol sensitivity, Kanick-Doyle 2005 Fig 3 pinned baseline, calibration convergence, muscle mechanics, Doyle 2017 multi-pathway gas exchange, and career-simulation API.

---

## Change Tracking

| Date | Reference | Scope |
|---|---|---|
| 2026-06-11 | README cleanup | Removed external writing references from this repository README; this README now tracks codebase changes only. |
| 2026-06-11 | `abb78c5` | Persist post-event middle-ear effective volume after ET/PET/lock pressure corrections; regenerated the Kanick-Doyle/Groth fixture. |
| 2026-06-11 | `40716c6` | Replaced the high-altitude pressure approximation with ISA pressure altitude; recalibrated hazards and refreshed validation priors. |
| 2026-06-11 | `652a7f0` | Added the evidence-backed model upgrade roadmap and seeded quick-start outputs. |

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
├── api/                          # FastAPI sidecar (Python) — JSON prediction endpoint
├── frontend/                     # React/TS dashboard (Vite + Tailwind + ECharts)
├── models/
│   ├── Literature/               # Structured literature PDFs / note files
│   └── middle_ear_model-matlab/  # Original MATLAB reference implementation
├── analysis/
│   ├── quick_analysis.py         # Legacy exploratory analysis helper
│   ├── statistical_analysis.py   # Legacy summary statistics helper
│   └── results/                  # Quick-analysis outputs kept for reference
├── app/                          # Streamlit dashboard (legacy prototype)
├── MIGRATION.md                  # v1 → v2 API migration guide
└── README.md
```

---

## Model Upgrade Roadmap

This roadmap reflects a second-pass methods audit completed in June 2026. Evidence checks were run with Consensus and paper-search before committing these items. Any P0 or P1 change that shifts pressure trajectories should be followed by fixture regeneration, FAC cohort recalibration, Sobol-cache refresh, and external-validation reruns.

### P0 - physics correctness

- **Completed: replace the high-altitude pressure model with ISA/U.S. Standard Atmosphere pressure altitude.** The v2 Python converter and frontend helper now use the standard-atmosphere lapse-rate relation and pin 0 ft, Bogota 8,530 ft, 25,000 ft (~282 mmHg), and 35,000 ft (~179 mmHg). Pressure altitude is foundational for chamber profiles, and Kanick-Doyle explicitly models middle-ear response to cabin-pressure change.
- **Regenerate all downstream artifacts after the atmosphere fix.** `calibrated.json`, the Kanick-Doyle/Groth fixture, and Italian validation priors were refreshed with the ISA correction. Before the next methods release, also recompute `abc_posterior.json`, `sobol_indices.json`, analysis figures, and any exported validation tables. A pressure change of this size alters peak |delta P|, time over threshold, hazard scaling, and external-transfer behavior.
- **Completed: make middle-ear volume state PV-consistent after every ET event.** The integrator now recomputes effective volume after passive venting, swallow, Valsalva, PET override, and pressure-lock updates before persisting the next state; the Kanick-Doyle/Groth fixture was regenerated after this correction. Doyle's formal pressure-regulation model treats pressure, compartment volume, gas composition, and pathway flows as coupled state variables.
- **Wire patient-specific tympanic-membrane anatomy into compliance, or remove those public fields.** `PatientAnatomy.tm_area_cm2` and `tm_stiffness_mmHg_per_ml` are currently accepted but do not affect `tm_displacement_ml()`. Kanick-Doyle identifies the ratio of maximum tympanic-membrane displacement to middle-ear volume as a relevant buffer, so exposed anatomy should either influence the simulation or be excluded from the API.

### P1 - methods and clinical-state fidelity

- **Refactor the PET/rhinitis/URI interaction state machine.** PET-S1 should not simply hard-zero the pressure gradient when allergic rhinitis, chronic rhinosinusitis, acute URI, recumbency, or sniffing behavior can produce intermittent obstruction or paradoxical closure. Add transition tests for PET-S1 + rhinitis/URI and PET-S2/S3 states instead of relying on a single override.
- **Split BDET benefit from post-BDET PET complication risk.** Obstructive ETD improvement after balloon dilation and post-procedure patulous symptoms are clinically different states. Model them separately, with tests that severe preoperative inflammation and repeat procedures can increase PET-like risk while successful dilatory-ETD treatment lowers active resistance.
- **Decide and document stochastic reproducibility.** The public docstring says `rng_seed=None` is deterministic, but `np.random.default_rng(None)` is nondeterministic. Either change the default to a fixed seed for reproducible science outputs, or document nondeterminism and require explicit seeds in examples, calibration, validation, and generated reports.
- **Clarify the Doyle 2017 gas-exchange scope.** The README describes species-resolved gas exchange as part of the core, while `simulate(..., gas_exchange_full=False)` defaults to trans-mucosal-only behavior. Decide whether full multi-pathway gas exchange is the default scientific model or an optional long-exposure extension, then align README guidance and validation tests.

### P2 - robustness and maintainability

- **Correct optional ET muscle-mechanics timing before making it a default.** The `et_muscle.py` comments describe recent-swallow priming, but the current timing formula increases the boost with time since last swallow; its initial sentinel can also saturate adhesion when enabled. Add directionality tests before using it in production calibration.
- **Add validity-envelope checks for extreme altitude and gas composition.** Guard against negative nitrogen fractions and nonphysical default total pressure in `GasComposition`, and reject or explicitly document chamber profiles outside the validated altitude range.
- **Keep README links repo-local and current.** Remove stale links when files leave this repository; use the living roadmap, tests, and generated validation artifacts as the source of truth for this codebase.
- **Synchronize calibration claims and examples.** Keep the README, `calibration.py` defaults, `calibrated.json`, tests, and quick-start outputs on the same FAC target and seed. Add a CI check that executes the quick-start snippets and fails on drift.

### Evidence links used for this roadmap

- Kanick S. C. & Doyle W. J. (2005), *Barotrauma during air travel: predictions of a mathematical model*: [doi:10.1152/japplphysiol.00974.2004](https://doi.org/10.1152/japplphysiol.00974.2004), [PMID 15608090](https://pubmed.ncbi.nlm.nih.gov/15608090/).
- Doyle W. J. (2017), *A formal description of middle ear pressure-regulation*: [doi:10.1016/j.heares.2017.08.005](https://doi.org/10.1016/j.heares.2017.08.005), [PMID 28917121](https://pubmed.ncbi.nlm.nih.gov/28917121/).
- U.S. Standard Atmosphere reference table: [doi:10.21236/ada320208](https://doi.org/10.21236/ada320208).
- Mandel E. M. et al. (2016), age-6 ET function/FGE comparison: [doi:10.1177/0194599815620149](https://doi.org/10.1177/0194599815620149), [PMID 26626132](https://pubmed.ncbi.nlm.nih.gov/26626132/).
- Ward B. K., Ashry Y., & Poe D. S. (2017), PETD demographics and comorbidities: [doi:10.1097/MAO.0000000000001543](https://doi.org/10.1097/MAO.0000000000001543), [PMID 28796094](https://pubmed.ncbi.nlm.nih.gov/28796094/).
- Juszczak H. M. & Loftus P. A. (2020), allergy and ETD review: [doi:10.1007/s11882-020-00951-3](https://doi.org/10.1007/s11882-020-00951-3).
- Poe D. et al. (2018), balloon dilation randomized controlled trial: [doi:10.1002/lary.26827](https://doi.org/10.1002/lary.26827), [PMID 28940574](https://pubmed.ncbi.nlm.nih.gov/28940574/).
- Hubbell R. D. et al. (2023), PETD symptoms following balloon dilation: [doi:10.1002/lary.30659](https://doi.org/10.1002/lary.30659), [PMID 36929856](https://pubmed.ncbi.nlm.nih.gov/36929856/).
- Raymond K. M. et al. (2022), systematic review of ET procedures for baro-challenge ETD: [Consensus record](https://consensus.app/papers/a-systematic-review-of-eustachian-tube-procedures-for-raymond-shih/c975a43f8fa65e9487abebb1e75a3aff/?utm_source=chatgpt).

---

## Known limitations (v2.2.1)

- **FAC anchor is unpublished.** The DIMAE 2010–2026 pooled rate (2.38% per-exposure / 6.97% career-3) is an internal institutional prior pending peer review. Treat it as a calibration prior, not cited external validation.
- **TM rupture threshold (150 mmHg) is conservative.** Biomechanical studies report higher real rupture pressures (~600–750 mmHg). `p_rupture` should be read as "imminent rupture risk" / comparative profile ranking, not an absolute clinical probability.
- **`p_barotitis` is not monotonic in descent rate in isolation.** With the v2.1 aperture model and peak-weighted hazard exponent (n = 1.8), the barotitis peak lies in the 2,000–3,000 ft/min zone, matching Italian AF chamber data. The rupture probability and peak |ΔP| are monotonic. Compare the full triple (`p_barotitis`, `p_baromyringitis`, `p_rupture`), not `p_barotitis` alone.
- **No per-subject ML head.** `ml_hybrid.py` is an unfit scaffold. No clinical individual-level tympanometry or FRT data are integrated.
- **Valsalva is idealized** as a 2-s bolus with a multiplicative FGE boost (0.55 per pulse). Real efficacy varies with anatomy and technique.
- **Full time-varying R_A (Ghadiali FEM) is not implemented.** Static Kanick-Doyle R_A and active-open duration now scale per-swallow clearance, and `et_muscle.py` provides a lumped time-varying approximation; the full 2-D FEM is not run per integration step.
- **No inter-exposure carry-over.** `career.simulate_career` composes independent `simulate()` calls; ME gas-composition and mucosal-fatigue state reset between exposures.
- **Population priors are FAC-demographic.** Re-calibrate before applying to pediatric, geriatric, or diving populations.

---

## License

MIT. See [LICENSE](LICENSE).

---

## Citation

If you use this software, please cite:

> Malpica DL, Farfán MA (2026). *Physics-informed middle-ear barotrauma risk prediction for hypobaric-chamber training, anchored to the Colombian Aerospace Force cohort.* `barotrauma_model` v2.2.1. Subdirectorate of Aerospace Sciences, Direction of Aerospace Medicine (DIMAE), Colombian Aerospace Force. https://github.com/strikerdlm/barotrauma_model
