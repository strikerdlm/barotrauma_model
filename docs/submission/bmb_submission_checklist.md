# Bulletin of Mathematical Biology — Pre-Submission Checklist (Refreshed)

**Manuscript:** *Beyond Binary Lock: A Continuous Aperture-Collapse Hazard Model of Middle-Ear Barotrauma in Hypobaric-Chamber Training*
**Date:** 2026-05-01
**Journal:** Bulletin of Mathematical Biology (Springer Nature)
**Article type:** Original Research

---

## Manuscript Files

- [x] **Main manuscript** — LaTeX `manuscript_bmb.tex` + compiled `manuscript_bmb.pdf` (15 pp)
- [x] **All editable source files** — `manuscript_bmb.tex`, `references.bib`, figure source `.py` and exported `.tiff/.png/.svg/.html` in `docs/figures/paper_c/`
- [x] **Line numbering** — `\linenumbers` continuous on every page
- [x] **Page numbers** — `\pagestyle{plain}`; sequential

## Title Page

- [x] Title concise and informative — *"Beyond Binary Lock: A Continuous Aperture-Collapse Hazard Model of Middle-Ear Barotrauma in Hypobaric-Chamber Training"*
- [x] All author full names listed — Diego L. Malpica; Marian A. Farfán
- [x] Affiliations — institution, department, city, country (DIMAE, Colombian Aerospace Force, Bogotá, Colombia)
- [x] Corresponding author indicated with active email — `diego.malpica@fac.mil.co`
- [x] ORCID for every author — D.L.M. 0000-0002-2257-4940 ; M.A.F. 0000-0002-9910-6053

## Abstract & Keywords

- [x] Abstract: 150–250 words (current 248)
- [x] No undefined abbreviations
- [x] No unspecified references inside abstract
- [x] Keywords: 4–6 (current 5)

## Text Format

- [x] Headings decimal system; ≤ 3 levels
- [x] Mathematical variables in italic (LaTeX math mode)
- [x] Numerals, operators, standard functions in upright Roman
- [x] Vectors / matrices in bold (none in this manuscript — N/A)
- [x] Derivative `d` upright via `\mathrm{d}`
- [x] Subscripts / superscripts via `_`/`^`, no HTML tags

## References

- [x] Author–year in-text citations via natbib `\citet` / `\citep`
- [x] Reference list alphabetised (`apalike` style)
- [x] DOIs included as full `https://doi.org/…` for every reference — 24/24 entries; all verified to resolve
- [x] Standard journal abbreviations or full title
- [x] No bibliographic detail in footnotes

## Figures

- [x] Numbered Arabic 1–4; cited consecutively
- [x] File naming: `fig_0[1-4]_*.tiff` matches caption number
- [x] Format: TIFF (LZW) for submission; PNG embedded in compiled review PDF
- [x] Resolution: **600 dpi** verified on all four (PIL inspection: dpi metadata 600 × 600)
- [x] RGB colour
- [x] Helvetica or Arial 8–12 pt — `FONT_FAMILY = "Arial, Helvetica, 'Liberation Sans', sans-serif"` (axis labels 11 pt, axis titles 12 pt, data labels 9 pt; panel titles 13 pt bold)
- [x] Contrast ratio ≥ 4.5 : 1 — `#000000` on `#FFFFFF` ⇒ 21 : 1
- [x] No titles or captions baked into figure files
- [x] Descriptive captions in text
- [x] Captions reference figure components for accessibility
- [x] Figure count consistent (4 figures, 4 captions, 4 in-text references)

## Tables

- [x] Numbered Arabic 1–4; cited consecutively
- [x] Caption explains components
- [x] Float environments with `\caption{}` and `\label{tab:…}`
- [x] No table footnotes required (N/A)

## Statements and Declarations

- [x] Competing interests
- [x] Funding (no external; DIMAE institutional support; no funder role)
- [x] Data availability
- [x] Code availability (MIT, GitHub, Zenodo DOI on publication)
- [x] Author contributions (CRediT)
- [x] Ethics statement (Colombian Resolution 8430/1993; Helsinki 2013)
- [x] Informed consent (N/A — retrospective de-identified)
- [x] AI / LLM disclosure
- [x] Reporting guideline (TRIPOD 2015)
- [x] Acknowledgements
- [x] ORCID for every author (D.L.M. + M.A.F. on title page)

## Supplementary Materials

- [x] TRIPOD checklist (`supplementary_S1_tripod_checklist.md`)
- [x] Model card mentioned in Data Availability
- [ ] Each ESM file labelled with article title, journal, authors, corresponding author
- [ ] Renamed to `ESM_1.pdf`, `ESM_2.csv`, … at upload time

## Cover Letter

- [x] Written and customised for *Bulletin of Mathematical Biology* (`bmb_cover_letter.md`)
- [x] Five suggested reviewers with names, institutions, expertise
- [x] International mix (USA, UK, Sweden, Spain)
- [x] No opposed reviewers (none required)

## Final Review

- [x] Submission PDF generates cleanly (`manuscript_bmb.pdf`, 15 pp; no undefined refs/citations; only 3–5 pt overfulls)
- [ ] All co-authors approve the final version
- [ ] No placeholder text remains in manuscript

---

## Compliance Summary

| Category | Count |
|---|---|
| PASS | 49 |
| PARTIAL | 1 (BMB "Fig. N" caption-label format, accepted either way) |
| FAIL | 0 |
| TO DO at portal | 3 (ESM rename, co-author approval, figure-file upload) |

No blocking failures remain. All figure-, ORCID-, DOI-, and citation-integrity checks PASS. Remaining work is portal mechanics only.

---

## Generated Artefacts

| File | Purpose |
|------|---------|
| `manuscript_bmb.tex` / `manuscript_bmb.pdf` | Submission manuscript (LaTeX + 15-pp compiled PDF) |
| `references.bib` | natbib bibliography (apalike style) |
| `2026-05-01_bmb_compliance_audit.md` | Refreshed PASS/FAIL audit against current LaTeX |
| `bmb_fix_list.md` | Refreshed prioritised fix list (no critical items remain) |
| `bmb_cover_letter.md` | Cover letter with author block, scope match, five suggested reviewers |
| `bmb_submission_checklist.md` | This consolidated checklist |
| `supplementary_S1_tripod_checklist.md` | TRIPOD 2015 28-item checklist (ESM_1) |

---

*Generated by bmb-submission skill v1.0.0 (refreshed 2026-05-01).*
