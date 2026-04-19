# Changelog

All notable changes to `barotrauma_model`. Follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); project uses
semantic versioning.

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
