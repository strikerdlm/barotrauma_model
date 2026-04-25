# Documentation index — `barotrauma_model/docs/`

This directory holds every prose artefact for the project: the three
manuscripts in submission preparation, the cover letters, the
literature briefs that anchor every constant in `barotrauma/v2/`, the
publication-grade figures, and the submission packages for the target
journals.

The entry point for the whole project is the [top-level
`README.md`](../README.md).

---

## Manuscripts

| File | Role | Reporting | Status |
|---|---|---|---|
| [`manuscript.md`](manuscript.md) | Paper 1 — physics-informed prediction model | TRIPOD 2015 | AMHP submission-ready |
| [`manuscript_fac_cohort.md`](manuscript_fac_cohort.md) | Paper 2 — 16-year FAC cohort epidemiology | STROBE 2007 | AMHP submission-ready (companion to Paper 1) |
| [`manuscript_preflight_fidelity.md`](manuscript_preflight_fidelity.md) | Paper 3 — DIMAE preflight screening instrument | TRIPOD 2015 (model component) | BMJ Open submission-ready |
| [`manuscript_author_page.md`](manuscript_author_page.md) | Depersonalised title page for Editorial Manager | — | Used for Paper 1 |

## Cover letters

| File | Paper | Target journal |
|---|---|---|
| [`cover_letter.md`](cover_letter.md) | Paper 1 | AMHP |
| [`cover_letter_fac_cohort.md`](cover_letter_fac_cohort.md) | Paper 2 | AMHP |
| [`cover_letter_preflight_fidelity.md`](cover_letter_preflight_fidelity.md) | Paper 3 | BMJ Open |

## Figures

All figures are built from committed source scripts using the shared
ECharts → SVG → cairosvg → 600 dpi LZW TIFF pipeline in
[`figures/_shared/`](figures/_shared/). Wong 2011 colorblind-safe
palette, Arial throughout, vector SVG masters preserved for editorial
markup.

| Path | Paper | Figures |
|---|---|---|
| [`figures/paper_b/`](figures/paper_b/) | Papers 2 & 3 | `fig_01..fig_05` (5 figures) |
| [`figures/paper_c/`](figures/paper_c/) | Paper 1 | `fig_01..fig_04` (4 figures) |

Each figure is committed in 4 forms: source script (`*.py`), vector
master (`*.svg`), preview (`*.png`), and AMHP-ready submission TIFF
(`*.tiff`, 600 dpi LZW).

## Research notes

Seven structured literature briefs in [`research_notes/`](research_notes/).
Every constant in `barotrauma/v2/constants.py` cites one of them.

| File | Topic |
|---|---|
| [`01_mathematical_models.md`](research_notes/01_mathematical_models.md) | Post-Kanick-Doyle physics models, Doyle 2017, Ghadiali FEM |
| [`02_uri_et_dysfunction.md`](research_notes/02_uri_et_dysfunction.md) | URI temporal modifier table with effect sizes |
| [`03_patulous_et.md`](research_notes/03_patulous_et.md) | PET 4-state model, JOS criteria, PHI-10 |
| [`04_chamber_epidemiology.md`](research_notes/04_chamber_epidemiology.md) | FAC anchor, Italian AF, Israeli AF, chamber incidence data |
| [`05_ml_bayesian_hazard.md`](research_notes/05_ml_bayesian_hazard.md) | ABC-SMC, Thalmann LEM, conformal prediction |
| [`06_2025_2026_updates.md`](research_notes/06_2025_2026_updates.md) | 2025-2026 literature scan — 10 actionable findings |
| [`07_v23_scope_rationale.md`](research_notes/07_v23_scope_rationale.md) | Rationale for deferring Zhang 2025 and Holm 2026 from v2.3.0 |

## Submission packages

In [`submission/`](submission/):

| File | Purpose |
|---|---|
| `supplementary_S1_tripod_checklist.md` | TRIPOD 2015 checklist for Paper 1 |
| `strobe_checklist_fac_cohort.md` | STROBE 2007 checklist for Paper 2 |
| `2026-04-18_amhp_compliance_audit.md` | AMHP IFA compliance audit (Paper 1 + Paper 2 figures) |
| `2026-04-18_upload_playbook.md` | Step-by-step Editorial Manager walkthrough for AMHP (currently scoped to Paper 1; Paper 2 needs its own) |
| `2026-04-18_reviewer_verification_checklist.md` | Reviewer-email verification log |
| `ref_verification_model_paper.md` | DOI-verification log for Paper 1 references |
| `ref_verification_fac_cohort.md` | DOI-verification log for Paper 2 references |

A **TRIPOD checklist for Paper 3** and **submission playbooks for
Papers 2 and 3** are still to be created — see
[`HOW_TO_CONTINUE.md`](../HOW_TO_CONTINUE.md) §"What remains for
publication" for the concrete task list.

## Other

- [`model_card.md`](model_card.md) — model inputs, outputs, assumptions,
  modeler-prior list, known limitations.
- [`2026-04-19_journal-scout_meb-model.md`](2026-04-19_journal-scout_meb-model.md)
  — fallback journal candidates if AMHP rejects Paper 1.
- [`Cohort FAC/`](Cohort%20FAC/) — raw data and tidy CSVs underlying
  the FAC anchor (Phase 1: 2010–2020 case registry; Phase 2: 2025–2026
  preflight + medical-director logs).
