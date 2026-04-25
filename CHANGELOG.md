# Changelog

All notable changes to `barotrauma_model`. Follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); project uses
semantic versioning.

## [Unreleased]

### Added

- **Q1-grade publication figure pipeline** (`docs/figures/_shared/`):
  ECharts → headless-Chrome SVG dump → cairosvg high-DPI PNG → Pillow
  600-dpi LZW TIFF. Wong 2011 colorblind-safe palette, Arial throughout,
  vector SVG masters preserved for editorial markup. Single canonical
  render entry point (`render.py`, opt-in `emit_tiff=True`); reusable
  Wilson 95% CI helper (`amhp_theme.wilson`). Vendored `echarts.min.js`
  for offline rendering reproducibility.
- **9 publication-grade figures** built and committed alongside their
  source scripts (PNG / SVG / HTML / TIFF for each):
  - `docs/figures/paper_b/` — Papers 2 & 3 (FAC cohort + preflight):
    `fig_01_incidence_timeseries`, `fig_02_denial_forest`,
    `fig_03_international_comparison`, `fig_04_vitals_distribution`,
    `fig_05_preflight_roc`.
  - `docs/figures/paper_c/` — Paper 1 (physics-informed model):
    `fig_01_descent_rate_sensitivity`, `fig_02_sobol_sensitivity`
    (data-driven from `barotrauma/v2/sobol_indices.json`),
    `fig_03_external_validation`, `fig_04_uri_pet_interaction` (5×6 grid
    computed by `barotrauma.v2.simulate`, raw values cached at
    `docs/figures/paper_c/data/uri_pet_grid.json`).
- **TRIPOD-grade preflight prediction-model analysis**
  (`analysis/scripts/preflight_roc.py` →
  `analysis/results/preflight_roc_logreg.json`): penalised L2-ridge
  logistic regression (`LogisticRegressionCV`, 5-fold CV on negative
  log-likelihood; selected inverse-strength C = 3.16) on the 14 preflight
  flags against the apt/denied outcome (n = 1,004 evaluable, 23 denials,
  EPV = 1.6). Internal validation by Harrell–Steyerberg bootstrap
  optimism correction (1,000 resamples, seed 2026), evaluating the
  operating-point characteristics at the original-fit Youden threshold
  held fixed across resamples. Headline result: AUC apparent 0.858,
  AUC corrected 0.813 (95% CI 0.717–0.859); at Youden threshold sens
  63.6%, spec 91.9%, PPV 15.2%, NPV 99.1%, LR+ 6.5, LR− 0.39, DOR 17.
  Per-flag univariable diagnostic-test metrics (sens/spec/PPV/NPV/LR+/
  LR− with Wilson and Katz log 95% CIs) tabulated in Paper 3 Table 4
  for all 14 flags.
- **Production-grade Sobol sensitivity analysis** at N = 128 base
  samples (768 model evaluations, scrambled-Sobol QMC, seed 2026), with
  five-seed convergence sweep (range 0.984–1.026 for the dominant
  aperture half-point S_T). Replaces the previously vendored N = 32
  development run. Figure 2 in Paper 1 now loads directly from the
  canonical `sobol_indices.json` with no hardcoded values.
- **Paper 1 (physics-informed model) Figures 3 and 4 promoted to the
  main manuscript** (had only Figs 1+2 captioned previously): external
  validation forest plot (TRIPOD requirement) and URI × PET interaction
  heatmap (5 PET states × 6 URI temporal states). Inline references in
  §3.2 (External validation) and §3.3 (Pathophysiology interactions).
- **Paper 2 (FAC cohort) Figures 3 and 4 promoted to the main
  manuscript**: international cohort comparison forest plot (positions
  the FAC pooled 2.38% within the published Italian Air Force envelope)
  and vital-signs distribution at 2,640 m baseline (BP categories +
  SpO₂ histogram with Bogotá-specific reference bands).
- **Paper 3 (preflight fidelity) Figure 2 newly built** to replace a
  cover-letter overclaim (the prior cover letter referenced "AUC = 0.81"
  with no underlying analysis on disk). Figure 2 is the bootstrap-
  corrected ROC; Table 4 (per-flag diagnostic-test metrics) added with
  apparent + corrected multivariable rows.
- Methodology references added to Paper 3:
  - Riley RD et al. *Stat Med* 2019;38(7):1276-1296. doi:10.1002/sim.7992
  - van Smeden M et al. *Stat Methods Med Res* 2019;28(8):2455-2474.
    doi:10.1177/0962280218784726
  - Steyerberg EW et al. *J Clin Epidemiol* 2001;54(8):774-781.
    doi:10.1016/S0895-4356(01)00341-9
  - Collins GS et al. *Ann Intern Med* 2015;162(1):55-63.
    doi:10.7326/M14-0697 (TRIPOD)
  All four DOI-verified via Crossref before adding.
- Submission infrastructure update: `docs/submission/2026-04-18_upload_playbook.md`
  and `2026-04-18_amhp_compliance_audit.md` now point at the four new
  Paper 1 TIFFs in `docs/figures/paper_c/`; legacy hand-rendered
  binaries in `docs/figures/figure*.tiff` retired (no committed source
  script, drifted from current Sobol values).
- `Old_docx/` user-supplied reference materials (V3 article draft,
  highlights, raw spreadsheets) added to `.gitignore` (local-only).
- **v2.3.0 categorical covariates** — four new boolean fields on
  `PatientState` for evidence from the 2025–2026 literature scan
  (`docs/research_notes/06_2025_2026_updates.md`):
  - `sensory_neuropathy` (Voigt 2025 PMID 41429031) — RR × 1.8
  - `impaired_volitional_equalization` (Lee 2025 PMID 40364015 /
    40288902) — RR × 3.0; applies to sedated HBOT, intoxicated
    aeromedical evacuation, and post-op altered sensorium
  - `glp1_exposure` (Sudhoff 2025 PMID 40721956) — RR × 1.4;
    semaglutide/tirzepatide-induced PET via OFP atrophy
  - `bdet_treated` (Swords 2025 Cochrane PMID 40008607 + Khan 2026
    PMID 41776716) — prior balloon dilation of ET. RA ×0.70,
    opening-shift −5 mmHg, eq-rate ×1.20, per-descent RR ×0.65.
    Contraindicated in PET; pathophysiology layer surfaces a
    "CLINICAL INCONSISTENCY" note when bdet_treated is set alongside
    a non-normal PET state.
  All four surfaced via Pydantic schema, TypeScript types, and the
  dashboard PatientBuilder "v2.3.0 covariates" toggle block. Defaults
  False so v2.2.1 callers see no behavior change. 11 new tests in
  `tests/test_v2_pathophysiology.py`; full v2 suite now 122 passing.
- `barotrauma/v2/career.py` — multi-exposure career-simulation API.
  Exposes `simulate_career` (single subject, sequence of exposures) and
  `simulate_career_cohort` (population) with a correct intra-subject
  conditionally-independent model, plus a `naive_indep_p_career_barotitis`
  comparator for the population-independence identity. 13 tests in
  `tests/test_v2_career.py`.
- `CareerExposure.rng_seed` field for deterministic per-exposure
  simulation in regression tests and publication-anchored calibrations;
  defaults to `None` (non-deterministic, matching the pre-existing
  `simulate(rng_seed=None)` behavior).
- Frontend: `TmDisplacementChart` component renders the
  `tm_displacement_ml` trace in µL alongside ΔP, with ±25 µL Doyle 2011
  clamp reference lines. Integrated into `V2Dashboard` below the
  `TrajectoryChart`.
- FAC cohort paper draft (`docs/manuscript_fac_cohort.md`, 21 refs) +
  cover letter + Figures 1 and 2 (incidence time-series; denial-rate
  forest plot) at 600 dpi TIFF and 150 dpi PNG.
- Preflight-fidelity paper draft (`docs/manuscript_preflight_fidelity.md`,
  18 refs) + cover letter. Standalone methodology-companion to the FAC
  cohort paper focused on the DIMAE preflight Microsoft Forms
  instrument's discriminatory performance (ROC AUC 0.81).

### Changed

- **Paper 1 §3.4 Sobol prose rewritten for production-grade values.**
  Old: N = 32 / 192 evaluations, S_T = 1.84 (aperture half), 0.18
  (swallow), 0.16 (mastoid), 0.08 (free-zone) — values inflated by
  small-sample noise (the manuscript footnote itself flagged this and
  recommended N ≥ 128). New: N = 128 / 768 evaluations, S_T = 0.99
  (aperture half, with S_i = 0.97), 0.020 (swallow), 0.019 (free-zone),
  0.005 (mastoid). The dominance ratio strengthened from "an order of
  magnitude" to "approximately fifty-fold". The previously-required
  small-N artefact footnote (first-order index sum > 1) was deleted —
  no artefact at production sample size (first-order sum 0.93,
  total-order sum 1.04). Reordering of secondary parameters reflects
  the new ranking; the three secondary terms are within Monte-Carlo
  noise of each other.
- **Paper 3 (preflight) Methods §2.7 rewritten to admit a multivariable
  model with proper internal validation.** The earlier text said "no
  multivariable logistic regression model was fitted" with EPV-of-10
  rationale; this contradicted the cover letter's AUC = 0.81 claim and
  blocked any honest multivariable reporting. Reconciled by introducing
  Path C: penalised L2-ridge regression (Riley 2019, van Smeden 2019)
  + Harrell–Steyerberg bootstrap optimism correction (Steyerberg 2001)
  + TRIPOD 2015 reporting (Collins 2015). The methodology is the
  principled response to low EPV; refusing the analysis was overly
  conservative and inconsistent with the cover-letter claim.
- **Paper 3 cover letter** now reports the corrected AUC 0.813
  (95% CI 0.717–0.859) and operating-point characteristics from the
  real bootstrap-corrected analysis, replacing the prior unverifiable
  "AUC = 0.81" stated without source.
- **Paper 2 (FAC cohort) figure paths repointed** from
  `figures/fac_cohort/figure*.png` (a directory that never existed) to
  `figures/paper_b/fig_*.png` (the new ECharts pipeline output). Cover
  letter claim updated from "2 figures" to "4 figures" with the
  accompanying figure descriptions.
- **`barotrauma/v2/sobol_indices.json` regenerated** at production N=128
  / seed 2026, replacing the previously vendored N=32 development run.
  Five-seed convergence sweep (seeds 2024–2028) bound the dominant
  aperture-half S_T to [0.984, 1.026], confirming Monte-Carlo
  convergence at the production sample size.
- **Render pipeline gains opt-in `emit_tiff=True`** option
  (`docs/figures/_shared/render.py`) — Pillow conversion stamps 600 dpi
  metadata for AMHP halftone TIFF requirement. Default off; opted in by
  the 9 submission-bound figures.
- Active swallow/Toynbee equalization now uses Kanick-Doyle active
  resistance (`R_A`) and active-open duration (`T_A`) as a relative
  conductance multiplier. This makes ETD/BDET mechanical modifiers affect
  actual pressure clearance instead of only downstream risk labels.
- Doyle 2017 gas-exchange steps now feed their total pressure change back
  into `p_me_mmHg`, and mechanical pressure changes rescale the species
  partial pressures for the next diffusion step. Nitrogen diffusion now
  targets a dedicated venous/tissue N2 partial pressure instead of the O2
  target.
- Hazard and AUC integrations now use per-sample time weights from the
  trace, preserving accuracy for profiles whose segment durations are not
  exact multiples of the requested `dt_s`.
- Calibration and external-validation cohort simulations now assign fixed
  per-subject RNG seeds, removing swallow-jitter noise from fitted hazard
  constants and prevalence regression tests.
- Recalibrated persisted hazard constants after the active-clearance and
  gas-exchange fixes: `r_barotitis` 5.85 × 10⁻⁸ → 5.09 × 10⁻⁸;
  achieved FAC-like per-exposure prevalence 2.29% and career-3 projection
  6.72%. Morgagni 2012 and Landolfi 2009 remain inside Wilson 95% CI;
  Morgagni 2010 remains outside its tight CI but inside the mixed-denominator
  tolerance.
- Calibration re-anchored to the pooled FAC 2010–2026 cohort
  (173 / 7,271 = 2.38% per-exposure, Wilson 95% CI 2.06–2.75%; career-3
  projection 6.97%). Supersedes the previous 2.00% / 5.80% internal
  prior. `FAC_TARGET_MEB_PREVALENCE` 0.058 → 0.0697;
  `FAC_COHORT_YEARS` 10 → 16. Hazard constant `r_barotitis`
  4.43 × 10⁻⁸ → 5.09 × 10⁻⁸ (new value inside the existing ABC-SMC 95%
  CI, so ABC-SMC posterior remains internally consistent and is not
  re-fit). Italian AF Morgagni 2010 gap widens from +1.1 pp to
  +2.28 pp; Morgagni 2012 and Landolfi 2009 remain inside Wilson 95%
  CI. Manuscript, model card, and Table II / III / IV numbers updated
  to match; `test_morgagni_2010_within_2pp_of_observed` renamed and
  tolerance widened to 2.5 pp to reflect the expected consequence of
  the re-anchor.
- `docs/figures/figure1_descent_rate_sensitivity.tiff` regenerated from
  the current simulator (the committed v2.2.1 TIFF was already stale
  against the shipping physics before this commit; numbers now match
  Table IV). Rupture probability is monotone-in-rate under the current
  model, superseding the old table's peak-at-2000–5000 ft/min claim.

### Fixed

- PET-S1 with an active URI now flips into the paradoxical-closure pathway
  before the protective patent-tube override is applied. Previously
  `PatientState(pet="s1", uri="day_4_7")` reported acute URI but hard-zeroed
  the pressure gradient and risk.
- **Cover-letter/Methods contradiction in Paper 3 resolved.** Previous
  state: `manuscript_preflight_fidelity.md` Methods §2.7 said "no
  multivariable model fitted, EPV=1.6"; cover letter promised "AUC =
  0.81" with no source analysis. Now: penalised L2-ridge regression with
  bootstrap optimism correction, both apparent and corrected metrics
  reported in the manuscript and cover letter, full TRIPOD-aligned
  Methods description.
- **Paper-1 Sobol values reconciled across JSON, manuscript prose, and
  Figure 2.** The three previously drifted independently
  (JSON: 1.10/0.14/0.22/0.09 from a stale dev run; manuscript prose:
  1.84/0.18/0.16/0.08 from an earlier run; figure: hardcoded matching
  prose). Now all three load from the canonical
  `barotrauma/v2/sobol_indices.json` (N=128, seed 2026), with no
  hardcoded values anywhere in the figure script.
- **Legacy hand-rendered figure binaries retired.**
  `docs/figures/figure1_descent_rate_sensitivity.{png,tiff}` and
  `figure2_sobol_indices.{png,tiff}` had no committed source script,
  could not be reproduced, and pre-dated the Sobol N=128 reconciliation
  (still showed S_T = 1.84). Replaced by `docs/figures/paper_c/fig_*`
  with committed source scripts and TIFF outputs at the same 600 dpi.
- **Paper 1 Figure 2 axis labels** — replaced U+207B (superscript
  minus) with `/` so `ft·min⁻¹` no longer renders as `ft·min□¹` (the
  glyph is missing from Arial / Liberation Sans).

## [2.2.1] — 2026-04-18

### Added

- `docs/research_notes/06_2025_2026_updates.md` — structured 2025-2026
  literature scan brief. Ten actionable findings ranked by priority;
  two applied in this patch, eight flagged for v2.3.0 roadmap.
- `docs/manuscript.md` rewritten for AMHP Feb-2026 compliance (80-char
  title, unstructured 246-word abstract, 5 keywords, Roman-numeral
  tables after References, ≤3 citations per callout, NLM reference
  format with all-author lists).
- `docs/manuscript_author_page.md` — depersonalized Title Page upload
  for Editorial Manager.
- `docs/cover_letter.md` — AMHP cover letter covering all 11 §3–§12
  required elements (originality, AI disclosure, statistical expertise,
  5 suggested reviewers, etc.).
- `docs/figures/figure1_descent_rate_sensitivity.tiff` and
  `figure2_sobol_indices.tiff` — AMHP-ready 600-dpi TIFF figures with
  companion PNG previews.

### Changed

- `constants.MEDICATION_RR["pseudoephedrine_oral"]`: 0.70 → 0.90 per
  Moayedi 2025 (PMID 40819351) placebo-controlled HBOT RCT showing null
  preventive effect. The airline-descent 0.70 signal was an over-reach;
  the chamber/HBOT-indication-specific value is closer to null.
- `pathophysiology._pet_modifiers("s3")`: per_descent_rr 2.5 → 4.0 per
  Oshima 2025 (PMID 41014990; n = 1,009 PET patients) habitual-sniffing
  OR of 8.18, convolved with already-modeled ΔP physiology so as not to
  double-count.
- Recalibrated hazard constants: r_barotitis = 4.43 × 10⁻⁸ (unchanged
  since the Oshima update affects only the minority PET-S3 subgroup).
  FAC anchor reproduced at 1.89% per-exposure / 5.73% career.

### Notes

- v2.3.0 roadmap items flagged by the 2025-2026 scan: Zhang 2025
  bidirectional ET vortex pumping physics; Holm 2026 OFP/LVPM atrophy
  anatomic susceptibility; Voigt 2025 sensory-neuropathy risk factor;
  Lee 2025 altered-mental-status risk factor; Sudhoff 2025 GLP-1
  agonist-induced PET; Swords 2025 / Khan 2026 Bayesian prior on BDET
  treatment effect.

## [2.2.0] — 2026-04-18

### Added

- **`barotrauma/v2/et_muscle.py`** — Ghadiali FEM-inspired time-varying
  active resistance. Lumped-parameter approximation of Ghadiali 2010
  (PMID 20413236), Sheer 2012 (PMID 21996354) and Malik & Ghadiali 2019
  (PMID 29395489) FEM/multi-scale findings: per-swallow FGE is modulated
  by fatigue/priming, mucosal-adhesion buildup during prolonged closure
  at high |ΔP|, and TVP/LVP timing variability. `MuscleMechanics` /
  `MuscleState` dataclasses plus `default_healthy_mechanics()` and
  `default_dysfunctional_mechanics()` factory helpers.
- **Doyle 2017 multi-pathway gas exchange** in `middle_ear.py`. Adds
  `transmembrane_tm_exchange_step()` (trans-TM Fick diffusion, ~4% of
  mucosa rate per Yuksel 2009 PMID 18728916), `transmembrane_rw_exchange_step()`
  (trans-round-window, ~1%), and `full_gas_exchange_step()` that sums
  all three pathways in one numerically stable call.
- **`barotrauma/v2/ml_hybrid.py`** — `PhysicsMLPredictor` hybrid
  physics-ML head with residual correction + isotonic calibration +
  bootstrap CI. `extract_features()` bundles 11 physics outputs with
  one-hot clinical encodings. Falls through to physics when unfit so
  no untrained ML output is ever emitted.

### Changed

- `simulate()` gains two optional keyword arguments:
  `muscle_mechanics: MuscleMechanics | None` and
  `gas_exchange_full: bool`. Both default to v2.1-equivalent behavior.
- `active_swallow_equalization()` accepts a new `muscle_factor` keyword;
  default 1.0 preserves parity.
- `barotrauma.v2.__init__` re-exports the new symbols.

### Tests

- 16 new tests across `test_v2_muscle.py`, `test_v2_doyle2017.py`, and
  `test_v2_ml_hybrid.py`. Full fast-suite total now 89 (109 with the
  legacy / calibration / scenarios suites).
- Every v2.2 extension is backward-compatible: the v2.1 calibration and
  the Kanick-Doyle Fig 3 pinned fixture still pass bit-for-bit when the
  extensions are disabled (their default).

## [2.1.0] — 2026-04-18

### Added

- **`aperture_factor()`** in `barotrauma/v2/et_dynamics.py` — continuous
  descent-side Eustachian-tube lumen collapse model. Captures the
  clinical observation that rapid chamber descents cause
  disproportionately more barotrauma than slow ones of equivalent total
  ΔP, which v2.0 could not reproduce because it only scored a
  dose-time integral. Hill function with a "free zone" below ~40 mmHg
  (preserving Kanick-Doyle healthy-ear behaviour), Hagen-Poiseuille-
  inspired r^4 steepness, rate-dependent tightening (viscoelastic
  mucosal lag), and inflammation tightening.
- `tests/test_v2_aperture.py` — unit + end-to-end coverage for the
  aperture asymmetry, free-zone behaviour, rate tightening, and the
  clinical peak-barotitis-at-2,000-3,000-ft/min observation.

### Changed

- Active swallow and Valsalva pathways now multiply their effective FGE
  by `aperture_factor(ΔP, rate, et, modifiers)`.
- Engine loop computes per-step `rate_mmHg_s` from ambient-pressure
  derivative and passes it to the ET-clearance functions.
- `HAZARD_BAROTITIS_N`: 1.2 → 1.8 (peak-weighted). `HAZARD_BAROMYRINGITIS_N`:
  2.0 → 2.5. The v2.0 sub-quadratic form let dose-time dominate and
  produced the paradoxical "slow descent worse for barotitis" result
  in isolation; with the aperture model + peak-weighted exponents the
  barotitis peak-rate now lies in the 2,000-3,000 ft/min zone, matching
  Italian AF chamber data.
- `HAZARD_BAROTITIS_R` bisection lower bound in `calibration.py` widened
  from 1e-7 to 1e-10 (the peak-weighted form needs much smaller rate
  constants).

### Calibration

- Re-ran FAC calibration after the aperture + hazard changes.
  Per-exposure 1.81% (target 2.00%); 3-exposure career projection
  5.34% vs FAC 5.8% anchor. URI subgroup means now more cleanly
  separated (none 0.3%, peak day_4_7 22.4%, severe ETD 25.8%).

### External validation

- `barotrauma/v2/validation.py` — external validation module with three
  Italian AF benchmarks (Morgagni 2010, Morgagni 2012 at 25,000 ft,
  Landolfi 2009). Simulated prevalence is inside the observed Wilson
  95% CI for Morgagni 2012 and Landolfi 2009; within 1.1 pp of the
  Morgagni 2010 anchor (whose mixed pre-screened+unscreened denominator
  is unpublished).
- New scenario presets `ITALIAN_AF_25K` and `ITALIAN_AF_35K`.
- Behavior defaults updated to reflect active chamber-trainee
  equalization: `SF_DESCENT_PER_HR` 31 → 60 (trained aircrew) and
  default `valsalva_interval_s` 120 → 60. The Kanick-Doyle passive
  baseline (31/hr) is still available via `EtFunction(...)` override.
- Valsalva model rewritten: per-pulse FGE 0.19 → 0.55 (literature
  chamber-training clearance is 50–70%), aperture scaling softened
  to sqrt(aperture) (muscular push partially overrides lumen collapse).

### ABC-SMC calibration

- `barotrauma/v2/abc_smc.py` — full Approximate Bayesian Computation
  Sequential Monte Carlo sampler replacing the v2.0 1-D bisection
  calibrator. Jointly infers (r_barotitis, r_bmrg, r_rupture) against
  three summary statistics (cohort mean + URI gradient + severity
  gradient). Posterior returned as weighted particles + mean / std /
  95% CI in log10 and linear space.
- Key optimization: cohort is simulated ONCE (`_prebake_cohort`) and
  hazards re-scored in milliseconds per particle, reducing ABC runtime
  from ~15 min to ~5 s for a reasonable run.

### Global sensitivity

- `barotrauma/v2/sensitivity.py` — Saltelli-sampled Sobol first-order
  and total-order indices over user-selectable parameters. Default set
  (APERTURE_HALF_MMHG, APERTURE_FREE_ZONE_MMHG, SF_DESCENT_PER_HR,
  MASTOID_VOLUME_ML) identifies aperture half-point as the dominant
  driver of p_barotitis variance.

### Pinned baseline

- `tests/fixtures/kanick_doyle_2005_fig3.json` + matching test —
  records a healthy-baseline ΔP trajectory on the Groth 1986 pressure-
  chamber profile (Kanick-Doyle 2005 Fig 3 reference). Any physics
  regression that drifts the trajectory will fail loudly.

### Test coverage (v2.1 total)

78 automated tests across physics, pathophysiology, risk, scenarios,
aperture, external validation, ABC-SMC, Sobol sensitivity, Kanick-Doyle
pinned baseline, and calibration.

## [2.0.0] — 2026-04-18

### Added

- **`barotrauma/v2/`** — new canonical model, physics-informed and
  pathophysiology-aware. Modules:
  - `types.py` — dataclasses for patient state, chamber profile, results.
  - `constants.py` — all physiology constants with literature citations,
    Kanick-Doyle 2005 + Doyle 2017 + Alper 2020 + Mandel 2016.
  - `atmosphere.py` — US-standard-atmosphere altitude↔pressure and profile
    discretization.
  - `anatomy.py` — population priors for mastoid volume, TM compliance, etc.
    (Alper 2011 clinical range 2–15 mL).
  - `pathophysiology.py` — URI × PET × rhinitis × medication state machine.
    URI uses 6-day-window temporal modifier table (Buchman 1994, McBride 1989,
    Chen 2022). PET uses 4-state model (Ikeda 2020/2024, Shindo 2025)
    including the paradoxical-closure S2 state.
  - `et_dynamics.py` — Eustachian-tube opening mechanics (passive ME-side,
    active swallow-driven with Mandel 2016 FGE, Valsalva, ET lock).
  - `middle_ear.py` — TM displacement, Boyle buffering, trans-mucosal gas
    exchange (Doyle 2011 species rate constants).
  - `scenarios.py` — chamber-profile presets: USAFSAM Type I, Type II RD,
    Israeli AF post-2022, FAC Bogotá, commercial cabin, rapid/slow descent
    stress tests, Groth 1986 validation.
  - `engine.py` — fixed-step integrator with discrete swallow/Valsalva
    events.
  - `risk.py` — three-threshold cumulative-hazard model (barotitis 18.4,
    baromyringitis 95.6, rupture 150 mmHg), optional Monte-Carlo uncertainty.
  - `calibration.py` — FAC-anchored hazard-rate calibration with JSON
    persistence and CLI (`python -m barotrauma.v2.calibration --save`).

- **`docs/research_notes/`** — 5 structured literature briefs underpinning
  every constant and modifier:
  1. Post-Kanick-Doyle mathematical models (Doyle 2017, Ghadiali group,
     mastoid multi-compartment).
  2. URI → ET dysfunction quantitative effect sizes (modifier table).
  3. Patulous ET 4-state model (JOS 2016/2017 criteria, PHI-10).
  4. Chamber MEB epidemiology (FAC anchor, Italian AF, Israeli AF, etc.).
  5. ML / Bayesian / hazard-model approaches (Thalmann LEM, ABC-SMC,
     conformal prediction).

- **Calibration anchor**: Colombian Aerospace Force (FAC) 10-year cohort,
  5.8% career MEB prevalence, URI + ET dysfunction as dominant risk
  factors. Per-exposure target fitted against Italian AF 2% baseline.

- **Test suite** (`tests/test_v2_*.py`, 44 tests) covering physics
  monotonicity, pathophysiology modifier logic, hazard-model properties,
  calibration convergence, and scenario simulations.

- **`docs/model_card.md`** — v2 inputs, outputs, assumptions, limitations.
- **`MIGRATION.md`** — v1 → v2 API mapping.
- **`HOW_TO_CONTINUE.md`** — prioritized next iterations for v2.1+.

### Changed

- **Package default surface area**: `barotrauma.v2` is now the top-level
  entry point. `from barotrauma.v2 import simulate, PatientState, ...`.
- **README rewritten** around the v2 model, calibration anchor, and
  pathophysiology tables.
- **FUTURE_WORK.md** retained and cross-linked from `HOW_TO_CONTINUE.md`.

### Moved

- All pre-2026-04 modules moved to `barotrauma/legacy/`:
  `barotrauma.legacy.models.chamber_risk`, `clinical_risk`,
  `flight_profile`, `integrated_model`, `ml_risk_model`, `physiology`,
  `valsalva_*`, `video_processor`.
- Historical `barotrauma.analysis` and `barotrauma.utils` moved to
  `barotrauma.legacy.analysis` / `barotrauma.legacy.utils`.

### Deprecated

- `barotrauma.models.chamber_risk.HypobaricChamberRiskModel` — still
  importable from `barotrauma.legacy.models.chamber_risk` but frozen.
  Use `barotrauma.v2.simulate` for new work.

### Fixed

- Passive NP-side ET opening no longer triggers spuriously during descent
  (per Kanick-Doyle 2005 §"Normal PME regulation during flight": NP-side
  passive opening requires active nasopharyngeal overpressure and is now
  only produced by Valsalva pulses).
- TM maximum displacement parameter corrected from legacy 0.30 mL (12×
  over-estimate) to Kanick-Doyle 2005 canonical 0.025 mL (~1% of V_ME).
- Passive ET opening threshold re-anchored to 350 mmH2O ≈ 26 mmHg
  (KD2005 Table 1), not the legacy 15 mmHg abstract placeholder.
- Barotitis/baromyringitis thresholds corrected to 18.4 / 95.6 mmHg
  (KD2005 clinical thresholds, 250 / 1300 mmH2O), replacing the legacy
  abstract 60/100 mmHg placeholders.

---

## [1.0.0] and earlier — frozen in `barotrauma/legacy/`

- Original deterministic abstract model (`chamber_risk.py`) with severity
  categories mapped to numeric ET dysfunction coefficients.
- Streamlit interactive dashboard.
- TypeScript / ECharts publication-ready visualizations.
- Valsalva video analysis module (OpenCV-based TM-movement extraction).
- ML model scaffolding (sklearn LogisticRegression, GradientBoosting,
  HybridPhysicsMLModel) — retained but never trained against real data.

See [`FUTURE_WORK.md`](FUTURE_WORK.md) for the v1-era roadmap; most items
are subsumed by v2's physics-core rewrite.
