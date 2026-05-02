# Bulletin of Mathematical Biology — Prioritized Fix List

**Manuscript:** Physics-Informed Middle Ear Barotrauma Risk for Hypobaric Chamber Training: A Computational Prediction Model Calibrated to the Colombian Aerospace Force Cohort and Externally Validated Against Italian Air Force Cohorts
**Date:** 2026-05-01
**Audit source:** `2026-05-01_bmb_compliance_audit.md`

---

## Critical — Blocks Submission (10 items)

| # | Item | Current State | Required State | Effort |
|---|------|---------------|----------------|--------|
| 1 | **File format** | Single `.md` file | LaTeX source (.tex) + compiled PDF using Springer Nature template | High |
| 2 | **Reference format — in-text** | Numbered superscripts (¹⁻³) | Name-year: `(Author Year)` or `Author (Year)` | High |
| 3 | **Reference format — list** | Numbered 1–24 | Alphabetized by first-author surname; include DOIs as full `https://doi.org/…` links | High |
| 4 | **Line numbering** | Absent | Continuous on every page | Low |
| 5 | **Page numbering** | Absent | Sequential | Low |
| 6 | **Table numbering** | Roman numerals (I, II, III, IV) | Arabic numerals (1, 2, 3, 4) | Low |
| 7 | **Declarations heading** | "Declarations" | "Statements and Declarations" | Low |
| 8 | **Corresponding author email** | Missing from title page | Active email required on title page | Low |
| 9 | **Affiliations detail** | Author initials only | Institution, department, city, country for each author | Low |
| 10 | **Figure count discrepancy** | Header claims 2 figures; captions list 4 | Resolve count and ensure all figures are cited consecutively in text | Medium |

---

## High — Likely Editorial Return (3 items)

| # | Item | Current State | Required State | Effort |
|---|------|---------------|----------------|--------|
| 11 | **DOIs in references** | 1 of 24 refs includes a DOI | All available DOIs included as full links | Medium |
| 12 | **LaTeX template** | Not used | Springer Nature LaTeX template | Medium |
| 13 | **Figure source files** | Not present in repo | EPS (vector) or TIFF (halftone) at required resolution; named `Fig1.eps`, `Fig2.tif`, etc. | High |

---

## Medium — Reviewer Friction (4 items)

| # | Item | Current State | Required State | Effort |
|---|------|---------------|----------------|--------|
| 14 | **Mathematical notation — variables** | HTML `<sub>` tags in plain text (e.g., `R<sub>A</sub>`) | LaTeX math mode: `$R_A$` (italic variables) | Medium |
| 15 | **Mathematical notation — functions/derivatives** | Plain text `d(ΔP)/dt` | Upright d for derivative: `$\mathrm{d}(\Delta P)/\mathrm{d}t$`; upright standard functions | Medium |
| 16 | **Figure captions** | `**Figure 1.** Description...` (period after number and at end) | `**Fig. 1** Description` (no punctuation after number or at end) | Low |
| 17 | **ORCID** | Not provided for any author | 16-digit ORCID for every author (strongly recommended) | Low |

---

## Low — Polish (3 items)

| # | Item | Current State | Required State | Effort |
|---|------|---------------|----------------|--------|
| 18 | **Color contrast / accessibility** | Unknown | Contrast ratio ≥ 4.5:1 for lettering; patterns + colors for colorblind users | Medium |
| 19 | **Reference abbreviations** | Inconsistent | Standard journal abbreviations (or full title if unsure) | Low |
| 20 | **Standard functions formatting** | Plain text `cos`, `exp`, `log`, etc. | Upright in math mode: `$\cos$`, `$\exp$`, `$\log$` | Low |

---

## Specific Math Notation Fixes

Apply these regex-style replacements when converting to LaTeX:

| Current | Fix |
|---------|-----|
| `R<sub>A</sub>` | `$R_A$` |
| `P<sub>O</sub>'` | `$P_O'$` |
| `ΔP` | `$\Delta P$` |
| `d(ΔP)/dt` | `$\mathrm{d}(\Delta P)/\mathrm{d}t$` |
| `V<sub>ME</sub>` | `$V_{\mathrm{ME}}$` |
| `h<sub>i</sub>(t)` | `$h_i(t)$` |
| `Θ<sub>i</sub>` | `$\Theta_i$` |
| `r<sub>i</sub>` | `$r_i$` |
| `p<sub>barotitis</sub>` | `$p_{\mathrm{barotitis}}$` |
| `ft·min⁻¹` | `$\mathrm{ft}\cdot\mathrm{min}^{-1}$` |
| `mmHg` | `$\mathrm{mmHg}$` |
| `daPa` | `$\mathrm{daPa}$` |

---

## Reference Conversion Required

All 24 references must be manually converted from numbered citations to name-year style. Example transformations:

- **In-text:** `Kanick and Doyle's 2005 pressure-regulation model.⁵` → `Kanick and Doyle's (2005) pressure-regulation model.`
- **List entry:** `5. Kanick SC, Doyle WJ...` → `Kanick SC, Doyle WJ (2005) Title. *Journal* vol:pages. https://doi.org/...`

Because reference data quality is unknown (some refs may lack DOIs or use non-standard formatting), plan for a manual pass with CrossRef/DOI lookup.

---

## Recommended Action Order

1. **Resolve figure count** (10 min) — confirm whether there are 2 or 4 figures; update header or add missing figures.
2. **Collect metadata** (15 min) — full author names, affiliations, corresponding author email, ORCID IDs.
3. **Convert to LaTeX** (2–4 h) — use Springer Nature template; apply math notation fixes; add line numbering (`\usepackage{lineno}`) and page numbering.
4. **Convert references** (2–3 h) — reformat all 24 refs to name-year + alphabetized + DOIs.
5. **Fix tables & declarations** (30 min) — Roman → Arabic table numbers; rename "Declarations" → "Statements and Declarations".
6. **Prepare figure files** (1–2 h) — export/render source files to EPS/TIFF at required resolution; rename per spec.
7. **Final PDF review** (30 min) — compile, verify formatting, check no placeholder text remains.

**Estimated total effort:** 6–10 hours

---

*Generated by bmb-submission skill v1.0.0*
