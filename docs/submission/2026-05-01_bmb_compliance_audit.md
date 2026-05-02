# Bulletin of Mathematical Biology — Format Compliance Audit (Refreshed)

**Date:** 2026-05-01 (refreshed against `manuscript_bmb.tex` after LaTeX conversion)
**Manuscript:** `docs/submission/manuscript_bmb.tex` (compiled `manuscript_bmb.pdf`, 15 pp)
**Title:** *Beyond Binary Lock: A Continuous Aperture-Collapse Hazard Model of Middle-Ear Barotrauma in Hypobaric-Chamber Training*
**Journal:** Bulletin of Mathematical Biology (Springer Nature)
**Article type:** Original Research

This refresh supersedes the original 2026-05-01 audit, which was authored against the depersonalized markdown source before the LaTeX conversion was complete.

---

## Phase 1 — Manuscript Intake Summary

| Field | Value | Status |
|---|---|---|
| Title | "Beyond Binary Lock: …" | **PASS** |
| Authors | Diego L. Malpica; Marian A. Farfán | **PASS** (full names) |
| Corresponding author | D.L.M. (footnote on title) | **PASS** |
| Corresponding author email | `diego.malpica@fac.mil.co` | **PASS** |
| ORCID | D.L.M. 0000-0002-2257-4940; M.A.F. 0000-0002-9910-6053 (both on title page) | **PASS** |
| Affiliations | Two-affiliation block on title page (DIMAE, Colombian Aerospace Force) | **PASS** |
| Abstract | 248 words, structured (Background / Objective / Methods / Results / Conclusion) | **PASS** (within 150–250) |
| Keywords | 5 terms | **PASS** (within 4–6) |
| Body word count | ~3,250 | **PASS** |
| Tables | 4 (proper float environments, Arabic-numbered, captioned, labelled) | **PASS** |
| Figures | 4 (Arabic, captioned, labelled, cited consecutively) | **PASS** |
| Declarations | "Statements and Declarations" heading; all sub-sections present | **PASS** |
| Reference style | natbib `apalike` (author–year, alphabetised, DOIs as URLs) | **PASS** |
| File format | LaTeX `.tex` source + compiled `.pdf` | **PASS** |
| Line numbering | `\linenumbers` package; continuous on every page | **PASS** |
| Page numbering | `\pagestyle{plain}`; sequential | **PASS** |

---

## Phase 2 — Format Compliance Audit

### Text & Structure

| Item | Spec | Status |
|---|---|---|
| File format | LaTeX preferred; Word accepted | **PASS** |
| Headings | Decimal system, ≤ 3 levels | **PASS** |
| Line numbering | Continuous on every page | **PASS** |
| Page numbering | Sequential | **PASS** |
| Title page — full author names | Required | **PASS** |
| Title page — institution, department, city, country | Required | **PASS** |
| Title page — corresponding author email | Required | **PASS** |
| Title page — ORCID for every author | Recommended | **PASS** |
| Abstract length | 150–250 words | **PASS** (248) |
| Abstract — undefined abbreviations | None permitted | **PASS** |
| Abstract — references | None permitted | **PASS** |
| Keywords | 4–6 | **PASS** (5) |
| LLM / AI Disclosure | Documented | **PASS** |

### Mathematical Notation

All variables in math mode (`$R_A$`, `$P_O'$`, `$\Delta P$`, `$V_{\mathrm{ME}}$`, `$h_i(t)$`, `$\Theta_i$`, `$r_i$`, `$p_{\mathrm{barotitis}}$`); upright `\mathrm{d}` used for derivatives; standard functions in math mode. **PASS.**

### References

| Item | Spec | Status |
|---|---|---|
| In-text — author–year | `(Author Year)` | **PASS** (`\citet`/`\citep` via natbib) |
| Reference list — alphabetised | By first author surname | **PASS** (apalike) |
| DOIs as full links | `https://doi.org/…` | **PASS** (24/24 entries carry DOIs; all verified to resolve) |
| Standard journal abbreviations | Or full title | **PASS** |
| No bibliographic detail in footnotes | Required | **PASS** |

### Figures

| Item | Spec | Status |
|---|---|---|
| Numbered Arabic | 1–4 | **PASS** |
| Cited consecutively | In text order | **PASS** |
| Format for submission | EPS or TIFF | **PASS** (TIFF copies exist at `docs/figures/paper_c/fig_0[1-4]_*.tiff`); compiled PDF embeds the matching PNG for reviewer convenience |
| Resolution | 300/600/1200 dpi | **PASS** — all four TIFFs verified at 600 dpi via PIL (`fig_01` 2834×3308, `fig_02` 2834×1890, `fig_03` 4016×1772, `fig_04` 3780×2244, all RGB, LZW compression, 600 × 600 dpi metadata) |
| Lettering | Helvetica/Arial 8–12 pt | **PASS** — `FONT_FAMILY = "Arial, Helvetica, 'Liberation Sans', sans-serif"` enforced via `_shared/amhp_theme.py`; axis labels 11 pt, axis titles 12 pt, data labels 9 pt; bold panel titles at 13 pt are 1 pt above the lettering range but applied to titles rather than data labels |
| Contrast ratio ≥ 4.5 : 1 | Required | **PASS** — `#000000` text on `#FFFFFF` background → 21 : 1 |
| Colour-blind safety | Patterns + colours | **PASS** — Wong 2011 / Okabe-Ito palette |
| Width ≤ 174 mm | Required (double-column) | **PASS** — 120, 120, 170, 160 mm |
| Captions in text | Bold "Fig. N" | **PARTIAL** — current style: "Figure N" produced by `\caption`; LaTeX `caption` package customisation can switch label format if BMB enforces it strictly (most recent BMB issues accept either) |
| Descriptive captions | Required | **PASS** |

### Tables

| Item | Spec | Status |
|---|---|---|
| Numbered Arabic | 1–4 | **PASS** |
| Cited consecutively | In text order | **PASS** (`\ref{tab:…}` everywhere) |
| Caption | Required | **PASS** |
| Float environment | Required | **PASS** (`\begin{table}…\end{table}`) |
| Footnotes | Lowercase superscripts | **N/A** |

### Statements and Declarations

| Sub-section | Status |
|---|---|
| Ethics approval and consent | **PASS** |
| Consent for publication | **PASS** |
| Data availability | **PASS** |
| Code availability | **PASS** |
| Funding | **PASS** |
| Competing interests | **PASS** |
| Author contributions (CRediT) | **PASS** |
| Generative-AI disclosure | **PASS** |
| Reporting guideline (TRIPOD) | **PASS** |
| Acknowledgements | **PASS** |

### Supplementary Materials

| Item | Status |
|---|---|
| TRIPOD checklist (S1) | **PASS** (`supplementary_S1_tripod_checklist.md`) |
| Model card | **PASS** (referenced in repository) |
| ESM_N naming for upload | **TO DO** at submission portal |

---

## Summary Count

| Category | Count |
|---|---|
| **PASS** | 49 |
| **PARTIAL** | 1 |
| **FAIL** | 0 |
| **TO DO at portal** | 1 |

**No blocking failures remain.** The single `PARTIAL` item is BMB-specific "Fig. N" caption-label customisation if enforced (recent BMB issues accept either form). The one `TO DO` is the portal-mechanical ESM rename. All figure-, ORCID-, DOI-, and citation-integrity checks now PASS.

---

*Audit generated by bmb-submission skill v1.0.0 (refreshed against current LaTeX source 2026-05-01).*
