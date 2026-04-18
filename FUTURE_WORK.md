# Future Work and Roadmap (v1 — historical)

> **Status: Historical document.** This roadmap predates the v2 rewrite
> (2026-04). Most of the near-term items here are now delivered in
> `barotrauma/v2/`. Prioritized next-steps for v2 live in
> [`HOW_TO_CONTINUE.md`](HOW_TO_CONTINUE.md). The text below is kept for
> continuity with pre-v2 discussions.

Author: Dr. Diego Malpica ([ORCID: 0000-0002-2257-4940](https://orcid.org/0000-0002-2257-4940))

## Vision
Advance a clinically trustworthy, physics-informed, and operationally useful platform for assessing middle ear barotrauma risk in aviation and hypobaric chamber contexts. The roadmap below outlines concrete enhancements across modeling, validation, ML integration, UI/UX, performance, packaging, and compliance.

---

## Phased Roadmap

### 0–1 releases (near-term)
- Robustify the core hypobaric descent model in `barotrauma.models.chamber_risk` and `barotrauma.models.flight_profile`.
- Add unit and property-based tests in `tests/` to cover edge descent profiles and ET dysfunction extremes.
- Expand Streamlit dashboard (`app/streamlit_app.py`) to include scenario presets and exportable PDF reports.
- Introduce first-class sensitivity analysis utilities (`barotrauma.utils.sensitivity_analyzer`).
- Establish a physics regression test suite with pinned baselines in `results/`.

### 2–4 releases (mid-term)
- Personalization via Bayesian calibration to subject data; introduce `barotrauma.analysis.calibration`.
- Add Valsalva and alternate equalization maneuvers with parameterized compliance.
- Integrate multi-segment ET opening dynamics with fatigue and hysteresis.
- ML-enhanced hybrid predictions in `barotrauma.models.integrated_model` with uncertainty estimates.
- Deploy as a packaged CLI and optional container; publish internal PyPI package.

### 6–12 months (longer-term)
- Prospective clinical validation study pipelines and dashboards in `docs/` and `analysis/`.
- FHIR/HL7 adapters for EHR integration with de-identification safeguards.
- Offline-first and edge-device support for field use and simulators.
- Regulatory-grade traceability: audit logs, versioned models, and locked baselines.

---

## 1) Modeling and Physiology Enhancements
- ET Dynamics
  - Passive/active opening thresholds modeled as stochastic processes (e.g., hazard-based opening with refractory periods).
  - Time-varying mucosal compliance and inflammation states; introduce state machine with transitions driven by ΔP and hydration.
- Tympanic Membrane and Middle Ear Mechanics
  - Nonlinear compliance curves; piecewise stiffness and rupture risk modeled via damage accumulation.
  - Coupling to mastoid air cell volume variability and thermal effects.
- Environmental and Operational Profiles
  - Realistic cabin pressurization profiles including holds, step descents, go-arounds, and rapid decompression events.
  - Humidity/temperature effects on gas behavior; supplemental oxygen scenarios.
- Risk Metrics
  - Extend risk from binary thresholds to continuous injury probability using dose–response models and time-above-threshold metrics (AUCΔP).
  - Composite risk indices (barotitis, ET lock, rupture) with tunable weights and clinical priors.

Deliverables:
- `barotrauma/models/chamber_risk.py`: parameterized TM compliance; stochastic ET opening; rupture probability function.
- `barotrauma/models/physiology.py`: curated, literature-traceable constants with citations.

Acceptance criteria:
- Physics regression parity within ±5% for legacy scenarios.
- New risk metrics validated against at least two published datasets.

---

## 2) Validation, Data, and Uncertainty Quantification
- Validation Datasets
  - Curate open and institutional datasets for hypobaric chamber outcomes; standardize schemas in `barotrauma/data/`.
  - Implement cross-study harmonization and metadata capture (age, ET status, prior barotrauma history, maneuvers used).
- Statistical Validation
  - Coverage metrics for ΔP prediction; calibration plots; sensitivity/specificity for risk categories.
  - Hierarchical models for inter-subject variability; mixed-effects regression to quantify variance components.
- Uncertainty Quantification (UQ)
  - Monte Carlo and Latin Hypercube sampling over physiology priors; Sobol indices for global sensitivity.
  - Propagate uncertainty to risk outputs and surface credible intervals in UI.

Deliverables:
- `analysis/statistics.py`: calibration curves, ROC/PR, Bland–Altman, bootstrap CIs.
- `analysis/visualization.py`: UQ-aware plots and cohort overlays.
- `tests/test_model_validation.py`: dataset-backed validation tests with pinned fixtures.

Acceptance criteria:
- Reported risk categories achieve ≥0.80 agreement with adjudicated labels on held-out data.
- Well-calibrated risk probabilities (Brier score and ECE targets defined per release).

---

## 3) ML-Enhanced and Hybrid Modeling
- Feature Engineering
  - Derived features from flight profiles (jerk, time-at-altitude, pressurization rate oscillations) and user-level physiology.
- Hybrid Predictors
  - Residual learning over physics outputs to correct systematic bias by severity class.
  - Gaussian Processes or NGBoost for calibrated uncertainty estimates.
- Personalization
  - Bayesian updating from prior clinic visits; learn patient-specific ET thresholds over time.

Deliverables:
- `barotrauma/models/integrated_model.py`: pluggable hybrid estimators with API parity to deterministic model.
- `tests/test_integrated_model.py`: unit tests for calibration and monotonicity constraints.

Acceptance criteria:
- Hybrid model improves MAE of ΔP by ≥15% vs. baseline while preserving monotonic risk behavior across descent rates.
- Uncertainty estimates pass coverage tests (e.g., 95% CI coverage within 92–98%).

---

## 4) Interactive App and Clinical UX
- Scenario Management
  - Save/load scenarios; versioned presets for training (e.g., chamber profiles, common flight ops).
  - PDF/CSV report export with embedded plots and parameter provenance.
- Accessibility and Guidance
  - Guided workflows with clinical guardrails; explainability panels for risk drivers.
  - Keyboard shortcuts, WCAG-compliant contrast, and internationalization hooks.
- Real-Time Integrations
  - Live serial/Bluetooth intake from cabin pressure sensors (optional module).

Deliverables:
- `app/streamlit_app.py`: scenario manager, export service, and UQ visualizations.
- `barotrauma/utils/plot_risk.py`: reusable plotting functions with clinical overlays.

Acceptance criteria:
- Median time-to-result under 2 seconds for typical scenarios on a midrange laptop.
- Usability study (n≥6) shows task success rate ≥90% and SUS ≥80.

---

## 5) Software Engineering, Performance, and Quality
- Performance
  - Vectorize core loops; optional JIT (Numba) for heavy kernels; batch evaluation for sweeps.
  - Profiling budget with targets documented per release.
- Testing
  - Unit, property-based, and stochastic tests (seeds, tolerances documented).
  - Golden-file tests for plots and physics baselines in `results/`.
- CI/CD
  - Lint, type-check (mypy), tests with coverage gates; release automation with semantic versioning.

Deliverables:
- GitHub Actions workflows; coverage reports; profiling notebooks in `analysis/`.

Acceptance criteria:
- ≥90% statement coverage on core models; no critical lints; type errors = 0.
- 2–5× speedup on 1k-scenario sweeps vs. v1 baseline.

---

## 6) Packaging, Deployment, and Distribution
- Packaging
  - Refine `setup.py` metadata; add `pyproject.toml`; split extras: `dev`, `docs`, `gpu` (if needed).
- Distribution
  - Internal PyPI; Docker images with pinned dependencies; optional `barotrauma-app` console entry point.
- Documentation Site
  - `docs/` with Sphinx + MyST; API docs, tutorials, and validation reports.

Deliverables:
- `pyproject.toml`; `Dockerfile`; `docs/README.md` expanded with build instructions.

Acceptance criteria:
- Reproducible builds on Linux/macOS/Windows; image size ≤1.2 GB; deterministic dependency lock.

---

## 7) Clinical and Regulatory Readiness
- Data Governance
  - De-identification, consent tracking, and secure storage interfaces; audit logs for scenario runs.
- Traceability
  - Model cards; versioned parameter sets; signed model artifacts for clinical audits.
- Standards
  - FHIR/HL7 mappings; ICD/SNOMED tagging for outcomes; preliminary IEC 62304-aligned processes.

Deliverables:
- `docs/model_card.md`; `docs/validation_report.md`; audit logging utility.

Acceptance criteria:
- End-to-end run produces a trace bundle: inputs, model version, parameters, outputs, plots, and environment hash.

---

## 8) Documentation and Education
- Tutorials
  - End-to-end notebooks: from scenario configuration to cohort analysis and UQ.
- Living References
  - Physiological parameter catalog with citations and justifications.
- Contribution Guides
  - Clear code of conduct, contribution standards, and style guide.

Deliverables:
- `docs/README.md` expanded; example notebooks in `analysis/`.

Acceptance criteria:
- New contributor can reproduce key figures and run validation in <30 minutes following docs only.

---

## 9) Community, Governance, and Sustainability
- Governance
  - Lightweight RFC process for model changes and new risk metrics.
- Issue Templates
  - Structured templates for bug reports, feature requests, and validation contributions.
- Citation and Attribution
  - CITATION.cff for scholarly use; explicit attribution guidance for derivatives.

Deliverables:
- `CITATION.cff`; `.github/ISSUE_TEMPLATE/*`; `docs/CONTRIBUTING.md`.

Acceptance criteria:
- First external contribution merged with full validation in CI.

---

## 10) Research Directions and Open Questions
- Multi-Compartment Ear Models
  - Coupling with cochlear/ossicular models to study secondary effects.
- Intervention Modeling
  - Impact of decongestants, nasal steroids, and prophylactic protocols on ET behavior.
- Population Health
  - Risk stratification across demographics and flying frequency; simulator training optimization.

---

## Milestones and Traces (Suggestive)
- M1: Physics regression suite; Streamlit scenario presets; baseline UQ plots.
- M2: Stochastic ET dynamics; Bayesian calibration; report export.
- M3: Hybrid model with calibrated uncertainty; cohort validation; Docker image.
- M4: FHIR pilot; audit logging; model card and validation report; governance templates.

---

## Dependencies and Risks
- Data access and IRB requirements may delay validation timelines.
- Stochastic models require careful test design to keep CI deterministic.
- ML components must preserve clinically expected monotonicities and guardrails.

---

## How To Contribute Next
- Pick an item tagged “Good first issue” under the corresponding milestone.
- Add or expand tests in `tests/` for any new feature.
- Include benchmarks and plots in PRs when changing model physics or risk metrics.

---

Maintained by: Dr. Diego Malpica ([ORCID: 0000-0002-2257-4940](https://orcid.org/0000-0002-2257-4940))