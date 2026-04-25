# Publication checklist — three-paper roadmap

Single tracker for every action that stands between **today** and **all
three papers in submission** at their target journals. Updated
2026-04-25 after the Path C TRIPOD reconciliation session.

Each item is one of:
- ☑️ **DONE** — finished, traceable to a commit
- ⬜ **TODO** — concrete blocking action, one person, < 1 day
- 🟡 **PARALLEL** — can be done at any time, doesn't block other tracks

---

## Paper 1 — Physics-informed prediction model → AMHP (primary)

**File:** `docs/manuscript.md` · **Cover letter:** `docs/cover_letter.md`
· **Figures:** `docs/figures/paper_c/` (4 TIFFs, all 600 dpi LZW)

### Scientific content (☑️ all done)

- ☑️ Manuscript text complete, ~3,400 body words, 248-word abstract,
  24 refs, 4 tables, 4 figures
- ☑️ TRIPOD 2015 reporting checklist
  (`docs/submission/supplementary_S1_tripod_checklist.md`)
- ☑️ All four figures with Q1-grade ECharts pipeline + 600 dpi LZW TIFF
  - ☑️ `fig_01_descent_rate_sensitivity` — Table IV companion
  - ☑️ `fig_02_sobol_sensitivity` — N=128 production Sobol (loads from
    canonical `barotrauma/v2/sobol_indices.json`, no hardcoded values)
  - ☑️ `fig_03_external_validation` — TRIPOD requirement
  - ☑️ `fig_04_uri_pet_interaction` — pathophysiology innovation
- ☑️ Figure 3 + Figure 4 captions + inline references in §3.2 / §3.3
- ☑️ Reference list DOI-verified
  (`docs/submission/ref_verification_model_paper.md`)

### Operational (⬜ blocking)

- ⬜ Re-run `2026-04-18_amhp_compliance_audit.md` against the current
  manuscript state (the prior audit had 5 FAILs; some have since been
  fixed but a fresh run is needed to catch new ones from the §3.4 / Fig
  3-4 caption additions)
- ⬜ Convert `docs/manuscript.md` → `docs/submission/manuscript.docx`
  via pandoc, manually verify double spacing + page numbers + tables
  Roman-numerated after refs + page break before "## Figure captions"
- ⬜ Convert `docs/cover_letter.md` → `docs/submission/cover_letter.pdf`
  via pandoc + xelatex
- ⬜ Verify reviewer emails per
  `docs/submission/2026-04-18_reviewer_verification_checklist.md`
  (Kanick, Alper, Ghadiali, Morgagni, Landolfi)
- ⬜ Sign three AMHP forms (Author Checklist, Copyright Release, COI
  — skip Color Surcharge; B&W requested)
- ⬜ DIMAE ethics memo (one-page, retrospective de-identified-registry
  approval, on FAC letterhead)
- ⬜ Editorial Manager upload per
  `docs/submission/2026-04-18_upload_playbook.md` Step 6 file order
- ⬜ Editorial Manager PDF proof check before final submit
- ⬜ Tag repository `v2.3.0-paper1-submitted` once the AMHP
  acknowledgement email arrives

---

## Paper 2 — FAC cohort epidemiology → AMHP (companion)

**File:** `docs/manuscript_fac_cohort.md` · **Cover letter:**
`docs/cover_letter_fac_cohort.md` · **Figures:** `docs/figures/paper_b/`
(figs 1–4, 600 dpi TIFF)

### Scientific content (☑️ all done)

- ☑️ Manuscript text complete, 16-year pooled incidence narrative,
  22 refs, 4 tables, 4 figures
- ☑️ STROBE 2007 reporting checklist
  (`docs/submission/strobe_checklist_fac_cohort.md`)
- ☑️ All four figures Q1-grade with 600 dpi TIFF
  - ☑️ `fig_01_incidence_timeseries` — per-year + per-quarter + Wilson CIs
  - ☑️ `fig_02_denial_forest` — 13 screening flags by discrimination tier
  - ☑️ `fig_03_international_comparison` — FAC vs Italian/Israeli AF
  - ☑️ `fig_04_vitals_distribution` — BP categories + SpO₂ histogram
- ☑️ Figure 3 + Figure 4 captions + inline §3.4 / §4 references added
- ☑️ Cover letter updated to "4 figures"
- ☑️ Figure paths repointed from `figures/fac_cohort/` (never existed)
  to `figures/paper_b/`
- ☑️ Reference list DOI-verified
  (`docs/submission/ref_verification_fac_cohort.md`)

### Operational (⬜ blocking)

- ⬜ **Create `docs/submission/2026-XX-XX_paper2_upload_playbook.md`**
  — modelled on the Paper 1 playbook but for the four `paper_b/`
  figures. Include the pandoc recipes, AMHP form list (reusable from
  Paper 1), upload order, and the suggested-reviewer block (likely
  different from Paper 1: this is an epidemiology paper, not a
  prediction model)
- ⬜ Re-verify the STROBE checklist against the current manuscript
  (the Fig 3 + Fig 4 inline additions in §3.4 / §4 should not change
  STROBE compliance, but a sanity pass is owed)
- ⬜ Convert `docs/manuscript_fac_cohort.md` → `.docx` via pandoc
- ⬜ Convert `docs/cover_letter_fac_cohort.md` → `.pdf` via pandoc
- ⬜ Reuse the same AMHP forms + DIMAE ethics memo as Paper 1
  (same author, same data boundary)
- ⬜ Update the Paper 1 manuscript's `ref 7 — Malpica DL ...
  (submitted)` to a manuscript ID once Paper 2 is in review (and to
  the journal cite once accepted)
- ⬜ Submit via Editorial Manager **after** Paper 1 (so Paper 1 has a
  citable companion)
- ⬜ Tag `v2.3.0-paper2-submitted`

---

## Paper 3 — Preflight screening instrument → BMJ Open

**File:** `docs/manuscript_preflight_fidelity.md` · **Cover letter:**
`docs/cover_letter_preflight_fidelity.md` · **Figures:**
`docs/figures/paper_b/` (figs 2 + 5, 600 dpi TIFF)

### Scientific content (☑️ all done)

- ☑️ Manuscript text complete with TRIPOD-aligned multivariable
  prediction model + per-flag univariable analysis
- ☑️ Path C analysis: penalised L2-ridge logistic regression with
  Harrell–Steyerberg bootstrap optimism correction (1,000 reps, seed
  2026); committed reproducible script
  (`analysis/scripts/preflight_roc.py`) + JSON output
  (`analysis/results/preflight_roc_logreg.json`)
- ☑️ Headline corrected metrics (TRIPOD-grade): AUC = 0.813
  [0.717, 0.859]; at Youden threshold sens 63.6%, spec 91.9%, PPV
  15.2%, NPV 99.1%, LR+ 6.5, LR− 0.39, DOR 17
- ☑️ Per-flag univariable Table 4 (sens, spec, PPV, NPV, LR+, LR− with
  Wilson and Katz log 95% CIs)
- ☑️ Figure 1 (denial forest, shared with Paper 2 Fig 2) and
  Figure 2 (preflight ROC) — both with 600 dpi TIFF
- ☑️ Methods §2.7 rewritten to admit the multivariable model + cite
  Riley 2019, van Smeden 2019, Steyerberg 2001 (optimism correction),
  Collins 2015 (TRIPOD)
- ☑️ Cover letter updated with corrected AUC + LR values
- ☑️ Limitations §5: in-sample concern replaced with internal-only
  validation + external validation as next step
- ☑️ All 4 methodology references DOI-verified via Crossref

### Operational (⬜ blocking)

- ⬜ **Create `docs/submission/tripod_checklist_preflight_fidelity.md`**
  for the prediction-model component. Use Paper 1 TRIPOD S1 as the
  template; the Path C work means most TRIPOD items are now answered
  (which they couldn't be when Methods said "no model fitted")
- ⬜ **Create `docs/submission/2026-XX-XX_paper3_upload_playbook.md`**
  for **BMJ Open** (different portal — ScholarOne, not Editorial
  Manager; different forms; OA fee considerations). List the 2 TIFFs
  (`fig_02_denial_forest.tiff`, `fig_05_preflight_roc.tiff`), the 4
  tables, the cover letter, ethics memo, and the analysis-script
  citation in the data-availability statement
- ⬜ Re-run `python -m analysis.scripts.preflight_roc` and compare its
  printed output against Table 4 + Figure 2 + Methods §2.7 + Results
  §3.x for bit-for-bit reproducibility (the analysis is deterministic
  modulo seed=2026)
- ⬜ Convert `docs/manuscript_preflight_fidelity.md` → `.docx`
- ⬜ Convert `docs/cover_letter_preflight_fidelity.md` → `.pdf`
- ⬜ Reuse DIMAE ethics memo (same data boundary)
- ⬜ Submit via BMJ Open ScholarOne portal
- ⬜ Tag `v2.3.0-paper3-submitted`

### 🟡 Parallel: external validation

- 🟡 If a different DIMAE training year or a partner Latin-American /
  sea-level programme can supply a comparable preflight CSV (same 14
  flags + denial decision), `analysis/scripts/preflight_roc.py` will
  evaluate it without modification — replace the `INPUT` constant. The
  resulting external-AUC would warrant a journal addendum or a follow-up
  publication.

---

## Cross-cutting (🟡 parallel, not blocking any single paper)

- 🟡 **Bump `setup.py` version** from `2.2.1` → `2.3.0` once the v2.3.0
  covariates roadmap (sensory_neuropathy, impaired_volitional_
  equalization, glp1_exposure, bdet_treated) merges and the figure /
  manuscript reconciliation work in this session is reviewed
- 🟡 **Update README citation block** with journal references after
  acceptance of any of the three papers
- 🟡 **GitHub releases** — tag `v2.3.0-paper{1,2,3}-submitted` at each
  acknowledgement email, then `v2.3.0` proper after the last submission
- 🟡 **Companion-citation chain** — once Paper 1 is in review, Paper 2's
  ref to "Malpica DL ... (in review)" should update to the AMHP
  manuscript ID; same for Paper 2 / Paper 3 cross-citations as each
  enters peer review

---

## Sequencing

1. Paper 1 first (most progressed, has full submission infrastructure).
2. Paper 2 second (~1 hour to clone the Paper 1 playbook for the
   epidemiology cover letter + STROBE checklist verify).
3. Paper 3 third (needs new TRIPOD checklist + ScholarOne playbook,
   ~half a day of focused setup work).

Doing them in this order keeps the companion-citation chain intact —
Paper 1 cites Paper 2 (which cites Paper 3); each can update its
citing reference as the previous one enters review.
