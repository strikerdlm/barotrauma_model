# Changelog

All notable changes to `barotrauma_model`. Follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); project uses
semantic versioning.

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
  Per-exposure 2.17% (target 2.00%); 3-exposure career projection
  6.38% vs FAC 5.8% anchor. URI subgroup means now more cleanly
  separated (none 1.4%, peak day_4_7 9.2%, severe ETD 8.8%).

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
