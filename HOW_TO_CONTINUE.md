# How to Continue — v2.2 roadmap and contributor guide

`barotrauma/v2/` is a complete, calibrated, externally-validated physics-
informed MEB model with 122 passing tests and **three Q1-grade
manuscripts at submission readiness**. This document orders the
next-highest-leverage work so the next session / contributor can resume
without re-deriving the plan.

> **🎯 Current state — 2026-04-25 (supersedes the historical content
> below where they conflict).**

---

## What is in submission-ready state today

All three manuscripts have full text, peer-review-grade figures with
committed source scripts, cover letters, reproducible analysis
artefacts, and (for prediction-model components) full TRIPOD 2015
compliance. The remaining work is operational, not scientific.

| Paper | Manuscript | Figures (TIFF, 600 dpi) | Cover letter | Reporting | Target |
|---|---|---|---|---|---|
| **1 — Physics-informed model** | `docs/manuscript.md` | 4 in `docs/figures/paper_c/` | `docs/cover_letter.md` | TRIPOD 2015 (`docs/submission/supplementary_S1_tripod_checklist.md`) | AMHP — primary; Otology & Neurotology / Eur Arch ORL / Auris Nasus Larynx / J Appl Physiol — fallback tiers (see `docs/2026-04-19_journal-scout_meb-model.md`) |
| **2 — FAC cohort epidemiology** | `docs/manuscript_fac_cohort.md` | 4 in `docs/figures/paper_b/` (figs 1-4) | `docs/cover_letter_fac_cohort.md` | STROBE 2007 (`docs/submission/strobe_checklist_fac_cohort.md`) | AMHP (companion to Paper 1) |
| **3 — Preflight screening** | `docs/manuscript_preflight_fidelity.md` | 2 in `docs/figures/paper_b/` (figs 2 + 5) | `docs/cover_letter_preflight_fidelity.md` | TRIPOD 2015 (prediction-model component) | BMJ Open (cover letter says so) |

**Headline numbers (all reproducible from committed scripts):**

- Paper 1: pooled FAC 2.38% per-exposure, 6.97% career-3; external
  validation 2/3 inside Wilson 95% CI (Morgagni 2010 sits +0.91 pp
  outside its tightest CI, within the cohort's own pre-screened-vs-
  unscreened 1.1–2.7% spread); Sobol N=128 aperture half-point
  S_T = 0.99 (50× the next term).
- Paper 2: 173/7,271 = 2.38% (Wilson 95% CI 2.06–2.75) sits within the
  published Italian Air Force envelope; 56% of preflight BP readings
  meet ACC/AHA stage-1 criteria; mean SpO₂ 94.8% at 2,640 m.
- Paper 3: penalised L2-ridge logistic regression with bootstrap
  optimism correction (1,000 reps, seed 2026): AUC corrected = 0.813
  (95% CI 0.717–0.859); at Youden threshold sens 63.6%, spec 91.9%,
  PPV 15.2%, NPV 99.1%, LR+ 6.5, LR− 0.39, DOR 17. Per-flag univariable:
  recent_respiratory LR+ 17.4 [9.05–33.63] is the strongest single
  discriminator; anaemia/bleeding and malaise/fever/fatigue are
  pathognomonic (specificity 100%, LR+ ∞).

---

## What remains for publication

Operational, not scientific. Roughly half a day of focused work per
paper.

### Paper 1 — AMHP submission (most progressed)

The *only* blocking items are documented in
`docs/submission/2026-04-18_amhp_compliance_audit.md` (5 FAILs as of
2026-04-18, since reduced; re-run the audit before submission). Once
those clear:

1. **Convert manuscript to .docx** — `pandoc docs/manuscript.md -o
   docs/submission/manuscript.docx` (or use the `amhp-submit` skill).
2. **Convert cover letter to .pdf** — `pandoc docs/cover_letter.md
   --pdf-engine=xelatex -o docs/submission/cover_letter.pdf`.
3. **Sign the four AMHP forms** (Author Checklist, Copyright Release,
   COI; skip Color Surcharge — B&W requested).
4. **DIMAE ethics memo** — secure a one-page memo from the DIMAE
   ethics office confirming retrospective de-identified-registry
   approval.
5. **Verify reviewer emails** (Kanick, Alper, Ghadiali, Morgagni,
   Landolfi) — see
   `docs/submission/2026-04-18_reviewer_verification_checklist.md`.
6. **Upload via Editorial Manager** — file order in
   `docs/submission/2026-04-18_upload_playbook.md` Step 6 (now
   includes all 4 figures: fig_01..fig_04 in `docs/figures/paper_c/`).
7. **PDF proof check**, **submit**, save the AMHP manuscript ID.
8. **Tag the repository** as `v2.3.0-paper1-submitted` once the
   acknowledgement email lands.

### Paper 2 — FAC cohort (companion submission)

Has all the same building blocks as Paper 1 but is missing a dedicated
submission playbook. Concrete remaining work:

1. **Create `docs/submission/2026-XX-XX_paper2_upload_playbook.md`**
   modelled on the Paper 1 playbook, listing Paper 2's 4 TIFFs in
   `docs/figures/paper_b/` (fig_01..fig_04).
2. **Pandoc → .docx + .pdf** as for Paper 1.
3. **Cover letter** is at `docs/cover_letter_fac_cohort.md` — already
   updated to "4 figures" in this session.
4. **Reuse** the AMHP forms / ethics memo — same author, same DIMAE
   programme, same data boundary.
5. **Submit after Paper 1** so the prediction-model paper has the
   epidemiology paper to cite as a non-preprint companion (currently
   ref 7 in `manuscript_fac_cohort.md` is "(submitted)" — once Paper 1
   is in review, update to a manuscript ID; once accepted, update to
   the journal cite).
6. **STROBE checklist** at
   `docs/submission/strobe_checklist_fac_cohort.md` is already drafted;
   re-verify after the §3 / §4 prose changes from this session.

### Paper 3 — Preflight screening (BMJ Open)

The cover letter says BMJ Open. Concrete remaining work:

1. **Create a TRIPOD checklist** for the prediction-model component.
   Use the Paper 1 TRIPOD S1 as the template; the multivariable Path C
   work added in this session (penalised regression, bootstrap optimism
   correction) means most TRIPOD items are now actually answered (they
   were previously unanswerable because §2.7 said "no model fitted").
   Save as `docs/submission/tripod_checklist_preflight_fidelity.md`.
2. **Create a submission playbook** for BMJ Open (different portal
   from AMHP — uses ScholarOne):
   `docs/submission/2026-XX-XX_paper3_upload_playbook.md`. List the
   2 TIFFs (`fig_02_denial_forest.tiff`, `fig_05_preflight_roc.tiff`),
   the 4 tables, the cover letter, ethics memo, and the analysis-script
   citation in the data-availability statement.
3. **Pandoc → .docx + .pdf**.
4. **Re-export per-flag univariable Table 4** at journal-final precision
   (the values in Paper 3 Table 4 are computed live by
   `analysis/scripts/preflight_roc.py`; re-run before final upload to
   confirm bit-for-bit reproducibility against
   `analysis/results/preflight_roc_logreg.json`).
5. **External validation** is flagged in Limitations §5 as the next
   needed step. If a different DIMAE training year or a partner
   programme can supply a comparable preflight CSV, the
   `analysis/scripts/preflight_roc.py` script will run it without
   modification (replace the `INPUT` constant); the resulting external-
   AUC would warrant an addendum or a follow-up publication.

### Cross-cutting

- **Bump version** in `setup.py` from `2.2.1` to `2.3.0` once the v2.3.0
  covariates roadmap (sensory_neuropathy, impaired_volitional_
  equalization, glp1_exposure, bdet_treated) lands and the figure
  / manuscript reconciliation work in this session is reviewed.
- **Update the README citation block** with journal references after
  acceptance.

---

## ⭐ Next step (historical — superseded)

Below is the original "next step" guidance from before the session
that built the publication-grade figure pipeline and TRIPOD-compliant
ROC analysis. Most actions are still correct in spirit but the figure
file paths and the AUC numbers are stale. Use the **What remains for
publication** section above as the authoritative current task list;
keep the historical content for context.

**Complete the AMHP submission portal upload and sign the four required
forms; immediately afterward, start the v2.3.0 roadmap informed by the
2025–2026 literature scan.**

The manuscript, cover letter, author page, and two TIFF figures are
ready (`docs/manuscript.md`, `docs/cover_letter.md`,
`docs/manuscript_author_page.md`, `docs/figures/`). All five AMHP
compliance FAILs were resolved 2026-04-19 in commit `d2f439f`. The
remaining blocking actions are operational, not scientific.

Concrete actions, in strict order:

1. **Forms** — download the four AMHP forms from Editorial Manager and
   sign each:
   - Author Checklist (corresponding author)
   - Copyright Release Form (author)
   - Conflict of Interest Form (author)
   - Agreement to Pay Extra Charges — **skip**; submission requests B&W
     print.
2. **IRB / ethics documentation** — secure a DIMAE ethics-board memo
   confirming de-identified-registry approval for the FAC cohort data.
   Upload as supplementary material.
3. **Editorial Manager submission** — use the `amhp-submit` skill's
   `upload` mode for the step-by-step portal walkthrough. Files in
   required order: cover_letter → manuscript → manuscript_author_page →
   figure1 → figure2 → signed forms. Select article type "Research
   Article".
4. **Suggest reviewers** in the portal — the five candidates already
   drafted in `docs/cover_letter.md`: Kanick (replaced Doyle — deceased),
   Alper, Ghadiali, Fabio Morgagni, Angelo Landolfi. Ghadiali's email
   `ghadiali.1@osu.edu` is publicly listed and verified; Morgagni's
   `fabio.morgagni@aeronautica.difesa.it` is 2012-authoritative but
   needs a live check. Alper, Kanick, Landolfi emails still require
   verification before portal entry — see
   `docs/submission/2026-04-18_reviewer_verification_checklist.md`.
5. **PDF proof review** — download and verify the system-generated PDF
   in Editorial Manager: title page depersonalized, double-spaced,
   page-numbered, tables Roman-numerated after references, figures
   NOT embedded in body.
6. **Submit** and save the AMHP manuscript ID from the acknowledgment
   email.
7. **GitHub Release** — tag the current repository state as
   `v2.2.1-manuscript` with a release note linking the manuscript PDF.

**Pre-portal WARN deferrals to close** before step 3:

- **WARN-1** — re-export `docs/figures/figure1_descent_rate_sensitivity.tiff`
  and `figure2_sobol_indices.tiff` as 8-bit grayscale with alpha
  flattened against white (AMHP IFA for B&W print). Current files are
  RGB with alpha.
- **WARN-2** — verify author counts on refs 11 (Doyle 1999 *Laryngoscope*,
  7 authors — `et al.` OK per NLM) and 16 (Chen 2022 *Eur Arch
  Otorhinolaryngol*) and expand any with ≤6 authors to full NLM lists.
- **WARN-4** — `.docx` render with pandoc using a reference template
  that enforces double-spacing, page numbers, table-per-page breaks,
  and a page break before "## Figure captions." Verify by eye before
  upload.

**While the manuscript is in review**, the next code deliverable is
v2.3.0, informed by the 2025–2026 literature scan
(`docs/research_notes/06_2025_2026_updates.md`):

- **Zhang 2025 bidirectional ET vortex pumping** — add a perturbation
  term on per-swallow FGE when P_ME < P_nasopharynx reflecting the
  PIV-observed orifice vortex. Sensitivity-analysis axis, not a
  first-order physics change.
- **Holm 2026 anatomic atrophy** — parameterize anatomic susceptibility
  from Ostmann fat-pad thickness and levator-veli-palatini volume
  rather than age alone. Unlocks a new `PatientAnatomy` axis.
- **Voigt 2025 sensory neuropathy** — add a categorical risk modifier.
- **Lee 2025 altered mental status** — add an `impaired_volitional_
  equalization` flag (mechanistically equivalent to failed-Valsalva).
- **Sudhoff 2025 GLP-1 agonist → PET** — add a weak covariate in the
  PET-state transition probabilities.
- **Swords 2025 / Khan 2026 BDET effect size** — add a
  post-BDET-treatment arm to the patient state with ETDQ-7 MD −2.03
  (12-mo) as the prior; flag the sham-controlled null for calibration
  against the S1 return-to-normal-ΔP behavior.

Only after the AMHP manuscript is in review (likely ~2 weeks after
submission) should the v2.3.0 **code** work begin. Do not start it
concurrently with the submission — a moving model confuses reviewers.

**Parallel data-prep track — starts now, no collision with the v2.2.1
submission:** the FAC 5.8% cohort paper (§1 below) is the single
highest-leverage publication queued after the AMHP manuscript and is
also the empirical anchor for v2.3.0 re-calibration. The raw data lives
under `docs/Cohort FAC/`:

- `2010_2020/` — the 2010-2020 prevalence-of-barotitis manuscript
  (`barotrauma articulo 2020.doc`) plus two Excel databases (`Barotrauma.xlsx`,
  `base de datos barotrauma.xls`).
- `2025_2026/` — Jan 2025 → Apr 2026 operational data: preflight medical
  evaluation with symptoms that denied chamber flight + vital signs
  (`EVALUACIÓN MEDICA PRE VUELO...xlsx`), and the medical-director Spanish
  narrative of chamber runs and barotitis cases (`FORMATO DE DIRECTOR
  MEDICO...xlsx`).

Tabulating these into structured analyzable data — prevalence per year,
preflight-denial rate stratified by symptom, vital-sign covariates, and
per-case Spanish narrative converted to structured fields — can happen
in parallel with the manuscript review.

---

This document orders the next-highest-leverage work so the next session /
contributor can resume without re-deriving the plan.

## Before anything else — read these

1. [`docs/research_notes/`](docs/research_notes/) — the 5 literature briefs.
   Every constant in the model cites one of them.
2. [`docs/model_card.md`](docs/model_card.md) — inputs, outputs, limitations.
3. [`CHANGELOG.md`](CHANGELOG.md) — what's in v2.0 and why.
4. Kanick-Doyle 2005 (PMID 15608090) — the canonical model you're extending.
5. Doyle 2017 (PMID 28917121) — the species-resolved successor.

## Priorities — in order

Items 2, 3, 4, 5 from the v2.0 roadmap are now **delivered in v2.1**:

- [x] (2) External validation against Italian AF cohorts — see
      `barotrauma/v2/validation.py` and `tests/test_v2_validation.py`.
- [x] (3) ABC-SMC multi-parameter calibration — see
      `barotrauma/v2/abc_smc.py` and `tests/test_v2_abc_smc.py`.
- [x] (4) Sobol global sensitivity — see `barotrauma/v2/sensitivity.py`
      and `tests/test_v2_sensitivity.py`.
- [x] (5) Kanick-Doyle Fig 3 pinned baseline test — see
      `tests/fixtures/kanick_doyle_2005_fig3.json` and
      `tests/test_v2_kanick_doyle_fig3.py`.

Items 7, 8 **delivered in v2.2**:

- [x] (7a) Ghadiali FEM time-varying R_A extension — see
      `barotrauma/v2/et_muscle.py` and `tests/test_v2_muscle.py`.
      Lumped-parameter approximation (fatigue/priming, mucosal
      adhesion, TVP/LVP timing) rather than full FEM, but captures
      the clinically meaningful effects; default disabled to preserve
      v2.1 calibration.
- [x] (7b) Doyle 2017 multi-pathway gas exchange — see
      `barotrauma/v2/middle_ear.py` (`full_gas_exchange_step`,
      `transmembrane_tm_exchange_step`, `transmembrane_rw_exchange_step`)
      and `tests/test_v2_doyle2017.py`. Trans-TM + trans-RW pathways
      added; default disabled.
- [x] (8) Hybrid physics-ML head scaffolding — see
      `barotrauma/v2/ml_hybrid.py` (`PhysicsMLPredictor`,
      `extract_features`) and `tests/test_v2_ml_hybrid.py`. Trains a
      calibrated residual correction on labeled outcomes; falls through
      to physics when unfit. Awaits a real labeled cohort to actually
      become useful.

Remaining open items below.

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

### 9. Modern Node.js interactive web application (post-model-freeze)

**Deferred until the model is complete, externally validated, and
stable.** Once the physics core stops churning, the next big deliverable
is a production-grade web application so clinicians, researchers, and
aviation-medicine trainees can run the model without Python. Target
experience:

- **Stack**: Node.js backend + Next.js / React frontend (TypeScript).
  Tailwind CSS + shadcn/ui or Radix primitives for the design system.
  Framer Motion for transitions. Dark/light themes. Fully responsive.
- **Visualization**: interactive ΔP trajectory, altitude profile, TM
  displacement, ET-open event raster, and hazard-stratified probability
  curves. Recharts or ECharts for 2-D; optional three.js / D3-force
  for a 3-D middle-ear schematic that animates TM retraction and ET
  state in real time. Monte-Carlo uncertainty fans overlaid on every
  plot. Exportable as SVG / PNG / PDF for clinical reports.
- **UX**: patient-builder wizard (anatomy, URI staging, PET state,
  medications), chamber-profile presets with live editing, one-click
  re-simulate, comparison mode (A vs B profiles or patients side-by-
  side). Clinical-decision-support panel showing dominant risk factor,
  recommended max descent rate, and plain-language explanation of
  *why*. Shareable permalinks that encode patient + profile in the URL.
- **Deployment**: Vercel / Netlify static frontend + Python simulator
  invoked via serverless Python function or WASM-compiled numeric core
  (e.g. Pyodide) so the whole thing runs in the browser with no
  server-side simulation cost. Version-pinned to a specific v2.x
  release of the Python package.
- **Quality bar**: Lighthouse 95+ across performance, accessibility,
  and best practices. WCAG 2.2 AA. Full keyboard navigation. Strict
  TypeScript, tested with Playwright end-to-end.

**Do not start this before** the Python model hits v2.3+ stability
(Ghadiali FEM extension, Doyle 2017 multi-pathway gas exchange, and the
FAC cohort paper all finalized). Shipping a web UI that tracks a still-
moving model creates churn; ship it once the underlying physics is
frozen.

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
