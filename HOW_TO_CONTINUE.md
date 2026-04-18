# How to Continue — v2.1 roadmap and contributor guide

`barotrauma/v2/` is a complete physics-informed model. This document orders
the next-highest-leverage work so the next session / contributor can resume
without re-deriving the plan.

## Before anything else — read these

1. [`docs/research_notes/`](docs/research_notes/) — the 5 literature briefs.
   Every constant in the model cites one of them.
2. [`docs/model_card.md`](docs/model_card.md) — inputs, outputs, limitations.
3. [`CHANGELOG.md`](CHANGELOG.md) — what's in v2.0 and why.
4. Kanick-Doyle 2005 (PMID 15608090) — the canonical model you're extending.
5. Doyle 2017 (PMID 28917121) — the species-resolved successor.

## Priorities — in order

### 1. Publish the FAC 5.8% cohort

The most load-bearing anchor in the model is currently unpublished. Until
the FAC DIMAE 10-year cohort is peer-reviewed, external users will and
should treat 5.8% as an internal prior.

- Draft a methods-and-results paper using the existing registry.
- Stratify the 5.8% by per-exposure vs per-career denominator (research
  brief 04 flags this gap).
- Once published, add the citation to `constants.py::FAC_*` and
  `docs/model_card.md`.

### 2. Re-calibrate against per-grade outcomes

The current hazard rates fit a single target: per-exposure `p_barotitis`.
Baromyringitis and rupture rates are rescaled from the barotitis constant
using an assumed Teed-III+/Teed-I+ ratio (~15%, Landolfi 2009). When the
FAC cohort is stratified by TEED grade, re-fit independent `r_i` per
stratum:

```bash
# After the FAC TEED distribution is extracted:
python -m barotrauma.v2.calibration \
    --target-barotitis 0.020 \
    --target-baromyringitis 0.003 \
    --target-rupture 0.0005 \
    --n 1000 --save
```

This requires extending `calibrate_hazard_constants` to bisect all three
rate constants jointly (currently it bisects only `r_baro` and rescales).

### 3. ABC-SMC proper calibration

The current bisection calibration is a first-order approximation. For
publication-grade uncertainty on hazard rates, implement proper
Approximate Bayesian Computation Sequential Monte-Carlo (template:
Torres-Florez 2025 PMID 40853999, see research brief 05):

- Priors on physiological parameters (Vmas, P_O', R_A, FGE, URI prevalence).
- Multi-statistic summary: (cohort prevalence, URI-subgroup gradient,
  severity-subgroup gradient, TEED distribution once available).
- Adaptive tolerance schedule, 1000 particles/generation.
- Output: posterior distributions, not point estimates.

### 4. Chamber-run video or tympanometry integration

The v1 Valsalva video analysis module (`barotrauma/legacy/models/
valsalva_video_analysis.py`) extracted TM-movement features from
endoscopic recordings. v2 does not currently consume those features.
Wiring it in would:

- Condition `EtFunction` parameters on per-patient measured values
  instead of the population-prior defaults.
- Allow the Alper 2020 paired-BDET parameter distribution (research brief
  01) to be used directly, shrinking the uncertainty envelope.

Sketch:

```python
# New module: barotrauma/v2/measurements.py
def et_from_forced_response_test(
    opening_mmHg: float,
    closing_mmHg: float,
    active_resistance_mmHg_ml_min: float,
) -> EtFunction:
    ...
```

### 5. TypeScript / Streamlit dashboard rewrite

The existing `app/streamlit_app.py` and `frontend/` TypeScript dashboard
target v1. They need updating to:

- Import from `barotrauma.v2`.
- Expose the new URI/PET/rhinitis widgets.
- Render the three-outcome probability trio with credible intervals.
- Render the `dominant_risk_factor` and `recommended_max_descent_ft_min`
  in a clinical-decision-support format.

### 6. Multi-exposure / career modeling

Chamber trainees undergo 2–5 exposures across their career. v2 currently
simulates single exposures. A full career model would:

- Accept a list of `ChamberProfile` and `PatientState` snapshots (state
  can evolve between exposures if URI status changes, etc.).
- Return a per-career probability that accounts for inter-exposure
  correlations in mastoid volume and ET function.
- Be the natural unit for the FAC 5.8% anchor (which is career, not per-
  exposure).

### 7. Extended physics (Ghadiali FEM, Doyle 2017 multi-compartment)

Research brief 01 flags:

- Ghadiali-group time-varying R_A (PMID 20413236, PMID 29395489) as the
  state of the art for ET resistance. v2 uses a constant R_A with Valsalva
  multiplier; a time-varying R_A would let the model distinguish TVP/LVP
  timing effects.
- Doyle 2017 full species-resolved trans-mucosal + TM + round-window gas
  exchange. v2 implements trans-mucosal only. For long holds / multi-
  hour cabin flights, the TM and round-window pathways matter.
- Mastoid multi-compartment (Doyle 2007, Alper 2011). v2 lumps tympanum +
  mastoid as a single gas volume; splitting would reproduce the buffering-
  efficiency M ≈ 0.2 observation.

Each of these is a self-contained upgrade with clear acceptance criteria.

### 8. Machine-learning head (hybrid physics-ML)

When a labeled cohort exists (FAC, institutional, or pooled multi-cohort):

- Train a residual-correction ML layer on top of v2's deterministic
  output.
- Use Gaussian-process or NGBoost for calibrated uncertainty.
- Report Brier, ECE, AUROC, 90% coverage per research brief 05.

The scaffolding exists in `barotrauma/legacy/models/ml_risk_model.py` —
port it to `barotrauma/v2/ml.py` and connect to the v2 engine outputs.

## Contributor workflow

1. Read the briefs. Do NOT add constants without a citation.
2. Write a test FIRST for any new behavior (physics regression, modifier
   behavior, or calibration stability).
3. Run the full test suite: `pytest tests/test_v2_*.py`.
4. If you change a constant, re-run calibration:
   `python -m barotrauma.v2.calibration --save`.
5. Update `CHANGELOG.md` with a dated entry under `[Unreleased]`.
6. Cross-link every change in `docs/model_card.md` under "Assumptions" or
   "Limitations."

## Don't do

- Don't extend `barotrauma/legacy/` — it is frozen for reproducibility.
  Start new work in `barotrauma/v2/`.
- Don't hand-edit `barotrauma/v2/calibrated.json` — it's regenerated by
  the calibration CLI.
- Don't add machine-learning models without a labeled training set —
  untrained scaffolding is negative-value (the v1 `ml_risk_model.py`
  lesson).
- Don't collapse the URI temporal states into a single boolean — the
  day-window granularity is the whole point of the URI modifier table.

## Contact

Dr. Diego L. Malpica (maintainer):
- ORCID: [0000-0002-2257-4940](https://orcid.org/0000-0002-2257-4940)
- GitHub: [@strikerdlm](https://github.com/strikerdlm)
