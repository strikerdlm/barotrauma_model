# v2.3.0 Scope Rationale — what was included, what was deferred, and why

**Date**: 2026-04-19.
**Author**: Dr. Diego L. Malpica.
**Scope**: Documents the scientific decision to include four items and defer two others from the `06_2025_2026_updates.md` literature brief in the v2.3.0 release candidate. Establishes unlock criteria for the deferred items and the hardening plan that closes v2.3.0-rc1.
**Baseline**: v2.2.1 (commit `886e529`) with 118 passing tests, pooled FAC 2010–2026 calibration anchor, three papers portal-ready (v2.2.1 physics model; FAC cohort 2010–2026; preflight-fidelity methodology).

---

## 1. Why a scope-rationale document

The model has grown rapidly across v2.2.1 → v2.3.0-rc1. Adding modeler-derived parameters is technically easy; it is scientifically defensible only if each addition is justified against a consistent epistemic framework. Without such a framework the model accrues "modeler freedom" — the aggregate latitude to fit the model to any observation by post-hoc parameter choice. A reviewer can challenge any individual parameter, but the aggregate indictment — "the model has more free parameters than the data constrains" — is the one that destroys external validity.

This document therefore (a) states the framework, (b) classifies the eight 2025–2026 literature-scan items against it, and (c) records the hardening commits that close the release candidate. It is the decision of record for v2.3.0 scope.

---

## 2. Epistemic framework

Four disciplines applied uniformly:

### 2.1 Evidence tiering

Every candidate parameter is tagged with a confidence tier:

- **HIGH** — meta-analysis of RCTs, single large RCT (n ≥ 500), or convergent observational cohorts totalling ≥ 1,000 subjects. Can change DEFAULT behavior (re-calibration required).
- **MEDIUM** — single well-powered observational cohort (n ≈ 200–1,000), smaller RCT, or multiple convergent smaller observational studies. Becomes a SENSITIVITY AXIS (parameter exposed, default preserves v2.2.1).
- **LOW** — case series (n < 30), in-vitro / mechanistic study without clinical endpoint, expert opinion, or any single study that has not been independently replicated. Becomes a FLAG (declared at the API surface and in the UI, but off by default and unused in calibration).

The tier constrains the form of implementation. A HIGH-confidence finding can alter calibration; a LOW-confidence finding cannot, no matter how clinically intuitive.

### 2.2 Translation honesty

When a paper reports ETDQ-7 mean difference, odds ratio, or tympanometry normalization rate, the translation to an engine parameter (multiplier on active resistance, shift in passive-opening threshold, etc.) is the modeler's choice, not the paper's result. Every such translation is explicitly recorded in `model_card.md` §6.1 "Explicit modeler priors" so a reviewer can challenge the translation without challenging the data.

A practical corollary: the sign and magnitude of an engine-parameter change may not be deducible from the reported effect size when the reported endpoint is symptomatic (ETDQ-7) and the engine operates on mechanical quantities (RA, FGE). In such cases, the translation interval is wider than the reported confidence interval, and the honest representation is a sensitivity axis, not a point estimate.

### 2.3 Calibration preservation

The defining test: "all v2.3.0 flags at default values must reproduce v2.2.1 byte-identical behavior." Any default change triggers a re-calibration (`python -m barotrauma.v2.calibration --save`) and a re-verification of the three external-validation benchmarks (Morgagni 2010/2012, Landolfi 2009). The tests `test_v2_validation.py::test_simulated_prevalence_within_observed_ci[...]` and the Morgagni 2010 ±2.5 pp guard enforce this at the regression level.

This discipline keeps the FAC anchor meaningful. A calibration that drifts with every added parameter is a moving target; reviewers rightly refuse to accept such a model as an external-validation benchmark.

### 2.4 Non-circular validation

Validation of an added parameter must be performed against a cohort *other than* the one that generated the parameter. Zhang 2025 data cannot validate a Zhang-derived parameter; Holm 2026 data cannot validate a Holm-derived parameter. In both cases the correct validation cohort is the *future* data generated under the v2 preflight-form recommendations (ETDQ-7 block, structured TEED grade, de-identifiable trainee ID). Until that validation lands, the parameter carries a "pending cohort confirmation" tag in the model card.

---

## 3. Evidence-tier classification of the eight 2025–2026 items

Items are from `docs/research_notes/06_2025_2026_updates.md`.

| # | Item | Study design / n | Tier | Decision | Status |
|---|---|---|---|---|---|
| 1 | Moayedi — pseudoephedrine null in HBOT | Placebo-controlled RCT | HIGH | Update default (RR 0.70 → 0.90) | ✅ v2.2.1 |
| 2 | Swords / Khan — BDET treatment effect | MA of 9 RCTs (n=684) + MA of 23 studies (n=309) | HIGH | Add as `bdet_treated: bool` flag with RA/RR/FGE modifiers | ✅ v2.3.0-rc1 |
| 3 | **Zhang — ET bidirectional pumping / vortex** | **In-vitro PIV on PET-derived anatomy; no clinical endpoint** | **MEDIUM→LOW** | **DEFER** | ❌ §4.1 |
| 4 | Voigt — HBOT otologic AE meta-analysis | Systematic review n=18,284 (54 studies) | HIGH | Add as `sensory_neuropathy: bool` flag | ✅ v2.3.0-rc1 |
| 5 | Lee — altered mental status predictor | Two convergent cohorts n ≈ 300 each | MEDIUM | Add as `impaired_volitional_equalization: bool` flag | ✅ v2.3.0-rc1 |
| 6 | **Holm — OFP / LVPM atrophy in ETD** | **3T MRI + CBCT, n=28 ETD vs 10 controls, retrospective, no reference ranges** | **LOW** | **DEFER** | ❌ §4.2 |
| 7 | Oshima — habitual sniffer OR 8.18 | Large adult PET cohort n=1,009 | HIGH | Update PET-S3 `per_descent_rr` 2.5 → 4.0 | ✅ v2.2.1 |
| 8 | Sudhoff — GLP-1-induced PET | Case series n=7 | LOW | Add as `glp1_exposure: bool` precautionary flag | ✅ v2.3.0-rc1 (explicitly tagged LOW) |

Items 1, 2, 4, 5, 7 operate at HIGH / MEDIUM tier and support either a default update (1, 7) or a flag with a specific multiplier derived from the reported effect size (2, 4, 5). Item 8 is LOW tier; it ships as a flag but is explicitly labeled so in the UI description ("Low-confidence precautionary RR"), and its applied multiplier is narrow (1.4) to avoid over-weighting the case-series signal.

Items 3 and 6 are deferred. The rationale is in §4.

---

## 4. Deferred items and their unlock criteria

### 4.1 Zhang 2025 — bidirectional ET pumping / tympanic-orifice vortex (PMID 41092566)

**Why the brief initially suggested it**: the paper provides the first fluid-dynamic visualization of ET behavior under negative intraluminal pressure and appears to contradict the Kanick-Doyle / Doyle 2017 assumption of unidirectional opening-driven clearance.

**Why it is not ready for implementation**:

1. **In-vitro, not in-vivo.** PIV (particle-image velocimetry) on CT-derived tube models shows velocity fields; it does not observe clearance volumes, tympanometry change, ETDQ-7 change, or any clinical endpoint. There is no published in-vivo confirmation that the vortex affects per-swallow clearance efficiency.

2. **PET-anatomy specificity.** The tube models used for the PIV experiment are derived from PET patients. PET anatomy is the explicit clinical indication for altered lumen compliance; healthy-tube geometry may not exhibit the same vortex signature. Any engine parameter that applies the finding to non-PET patients is an extrapolation without evidence.

3. **Direction and magnitude are not recoverable from the reported data.** The paper shows that a vortex forms; it does not quantify whether the vortex increases or decreases per-swallow fractional-gradient-equalization (FGE), by how much, or under what pressure regimes. Any `zhang_vortex_modulation: float = 1.0` parameter with a declared range (e.g., [0.7, 1.3]) would pick the range from modeling-convenience rather than data.

4. **Adding it as a Sobol axis pollutes the variance decomposition.** The current Sobol analysis (`sobol_indices.json`) identifies the aperture half-point as the dominant variance driver. Adding a free-parameter axis with a modeler-chosen range adds variance from a parameter that has no empirical constraint — it manufactures sensitivity rather than measures it.

**Unlock criteria**:

- A paired PIV + clinical-endpoint study (tympanometry change or ETDQ-7 change) in healthy tube anatomy that quantifies the functional translation of the vortex. OR
- A computational-fluid-dynamics (CFD) study that couples the PIV-observed velocity field to a volumetric clearance calculation for the ET geometry, producing a quantitative FGE(ΔP) relationship. OR
- A DIMAE-internal paired forced-response-test (FRT) study pre- and post-simulated descent with tympanometric readouts across a ΔP range.

Until any of these lands, Zhang 2025 is cited in the v2.2.1 manuscript (submitted) and in this document as a qualitative mechanistic observation motivating future work. The model card §6 "Limitations / considered but not implemented" block states the deferral explicitly.

### 4.2 Holm 2026 — OFP / LVPM atrophy in ETD (PMID 41466069)

**Why the brief initially suggested it**: the paper is the first multimodal quantitative ET-anatomy study and offers a structural susceptibility axis that could replace or augment the age-based susceptibility implicit in the discrete `EtSeverity` enum.

**Why it is not ready for implementation**:

1. **Sample size is grossly inadequate for a continuous dose-response.** n = 28 ETD vs. n = 10 controls total. A 2-point linear extrapolation (ETD mean → control mean) is not a defensible mapping from OFP thickness to severity. A reviewer will ask for the confidence interval on the slope; the CI from n = 38 is wide enough to include zero effect.

2. **Reference ranges for OFP and LVPM in healthy populations are not published at a standardized measurement protocol.** The same anatomic measurement can differ by 20–30% across measurement methods (sagittal vs. parasagittal plane, landmark choice, 3T vs. 1.5T MRI). Without a protocol-matched reference range, a user's OFP thickness measurement cannot be mapped to a severity score without importing a measurement-protocol assumption.

3. **Causal direction is undetermined.** The Holm cohort does not establish whether OFP/LVPM atrophy precedes and causes ETD or whether chronic ETD → disuse atrophy is the relationship. The second case implies that OFP thickness is an *effect* of severity, not a *covariate*, and including it as a predictive parameter introduces reverse causation.

4. **Almost no user would benefit.** OFP/LVPM measurements require a 3T MRI or CBCT with a specialized protocol. DIMAE does not routinely acquire these. A `PatientAnatomy.ostmann_fat_pad_thickness_mm` field would be NULL on ≥ 99% of real inputs. The resulting API and UI surface area adds complexity that pays no dividend for operational users.

5. **Misuse risk.** A user who enters an OFP thickness from a non-standardized imaging protocol, without understanding the tight confidence interval on the 2-point extrapolation, would produce a severity score with unwarranted precision. The model would display a number that its underlying data do not support.

**Unlock criteria**:

- An independent cohort n ≥ 100 with a standardized imaging protocol confirming Holm's OFP/LVPM ↔ ETD relationship. OR
- A healthy-population reference-range paper (ideally ≥ 200 subjects, multi-site) publishing OFP thickness and LVPM volume percentiles under a specified measurement protocol.

Until either lands, Holm 2026 is cited as the best current structural evidence on ET anatomy in ETD but is not encoded as a model parameter. The `EtSeverity` discrete enum remains the primary susceptibility axis; anatomic covariates are a v2.4 candidate.

### 4.3 General rule for future deferrals

A finding is deferred when at least one of the following conditions holds: (a) the study design is below MEDIUM tier; (b) the reported endpoint does not translate uniquely to an engine parameter; (c) the cohort that generated the finding is also the only cohort available to validate it (circular validation); (d) implementation requires extrapolation outside the studied population.

---

## 5. Hardening plan for v2.3.0-rc1

Four commits that close the release candidate without adding parameters.

### 5.1 Sobol re-run with the four v2.3.0 covariates

**What**: run `python -m barotrauma.v2.sensitivity` with the four new covariate flags cycled through {False, True} combinations. Record first-order and total-order Sobol indices for the union of the pre-existing four parameters (aperture half-point, free-zone threshold, swallow frequency, mastoid volume) plus the four covariates.

**Why**: the current Sobol output identifies the aperture half-point as the dominant variance driver. Adding four covariates without re-checking Sobol would leave that claim untested. The re-run either (a) confirms the ranking, in which case the manuscript claim holds, or (b) exposes a new dominant driver, in which case the manuscript discussion needs updating. Either outcome is honest.

**Acceptance**: `barotrauma/v2/sobol_indices.json` regenerated; if aperture half-point remains dominant, the v2.2.1 manuscript claim is re-verified. If a covariate dominates, the model card and manuscript discussion need a matching update.

### 5.2 External-validation regression check

**What**: run `python -m barotrauma.v2.validation` and confirm the three Italian AF benchmarks produce the same simulated rates as the `dd5a056` baseline (pooled FAC 2010–2026 anchor). Morgagni 2010: 3.27% expected; Morgagni 2012: 3.31% expected; Landolfi 2009: 3.37% expected. Verify the Morgagni 2010 ±2.5 pp guard still passes.

**Why**: the four new covariates default to False. A validation result that differs from `dd5a056` would indicate a silent leak in the modifier composition (for example, a covariate flag not correctly short-circuiting at default). This is a cheap byte-identity check that enforces the calibration-preservation discipline of §2.3.

**Acceptance**: three simulated rates match `dd5a056` to floating-point tolerance; Morgagni 2010 within the ±2.5 pp guard.

### 5.3 Model card §6.1 — new modeler-prior rows

**What**: extend the "Explicit modeler priors" table in `docs/model_card.md` §6.1 with four new rows covering `sensory_neuropathy`, `impaired_volitional_equalization`, `glp1_exposure`, and `bdet_treated`. Each row names the paper, the confidence tier, the applied engine multiplier, the translation assumption, and the unlock condition for a future default update.

**Why**: §6.1 is the contract between the modeler and the reviewer. A parameter not listed in §6.1 is a hidden prior. By listing all four new covariates with their translation assumptions explicit, we allow a reviewer to challenge any individual choice without challenging the underlying data, per §2.2.

**Acceptance**: `model_card.md` §6.1 has four new rows; each cites its paper and tier.

### 5.4 Model card §6 — "Considered but not implemented"

**What**: add a new sub-section to `docs/model_card.md` §6 Limitations titled "Considered but not implemented" that lists Zhang 2025 and Holm 2026 with (a) the original finding, (b) the reason for deferral (pointing into this document §4.1 and §4.2), and (c) the unlock criteria.

**Why**: an external reviewer of the v2.2.1 manuscript is likely to be familiar with Zhang 2025 and Holm 2026 — both appeared in the 2025–2026 update window. They may ask "why doesn't your model include these?" An explicit "Considered but not implemented" block answers this question before it is raised, preserves the decision reasoning, and signals to reviewers that the exclusion is deliberate, not oversight.

**Acceptance**: `model_card.md` §6 has the new sub-section with both items.

---

## 6. When to revisit v2.3.0 engine work

Three trigger conditions:

1. One of the three portal-ready manuscripts (v2.2.1 physics model; FAC cohort 2010–2026; preflight-fidelity methodology) returns from review with actionable feedback that affects parameter choices. Revise the affected parameters in v2.3.1 rather than accumulating v2.3.0 scope.

2. A Zhang-unlock or Holm-unlock publication lands (§4.1 / §4.2). At that point the deferred item is re-evaluated against §2 and either promoted to implementation or kept deferred with updated rationale.

3. The FAC 2026-Q3+ preflight form adds the three v2.3.0-recommended fields (ETDQ-7 block, structured TEED grade, de-identifiable trainee ID). Once the data arrive, the existing engine surface (career.py, the four covariates) can be re-calibrated against the new longitudinal cohort; that motivates a v2.4.0 rather than extending v2.3.0.

Before any of these, v2.3.0 engine work is frozen. The HOW_TO_CONTINUE.md roadmap and this document are the references of record for what was considered, what was included, what was deferred, and why.

---

## 7. Summary

v2.3.0-rc1 encodes four 2025–2026 literature findings as optional, defaults-False patient-state flags. All four are byte-compatible with v2.2.1 at defaults. The two items not implemented (Zhang 2025 vortex; Holm 2026 anatomic atrophy) are deferred with explicit unlock criteria captured here and in the model card. The four hardening commits listed in §5 close the release candidate. The rationale is preserved in this document so that v2.4.0 or later maintainers can audit what was decided, why, and what would change the decision.
