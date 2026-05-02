# Bulletin of Mathematical Biology — Format Compliance Audit
**Date:** 2026-05-01
**Manuscript:** `docs/manuscript.md`
**Journal:** Bulletin of Mathematical Biology (Springer Nature)
**Article type:** Original Research (or Methods, if reframed)

---

## Phase 1 — Manuscript Intake Summary

| Field | Value | Status |
|---|---|---|
| Title | Physics-Informed Middle Ear Barotrauma Risk for Hypobaric Chamber Training… | Present |
| Authors | D.L.M., M.A.F. | Present |
| Corresponding author | Not explicitly indicated on title page | **FAIL** |
| Abstract | 249 words | **PASS** (within 150–250) |
| Keywords | 5 terms | **PASS** (within 4–6) |
| Body word count | ~3,250 | **PASS** |
| Tables | 4 | Present |
| Figures (header claim) | 2 | **DISCREPANCY** — captions list 4 figures |
| Declarations section | Present under "Declarations" heading | **PASS** |
| Reference format | Numbered (1–24), superscript in-text | **FAIL** |
| File format | Markdown (.md) | **FAIL** (LaTeX strongly preferred) |

---

## Phase 2 — Format Compliance Audit

### Text & Structure

| Item | Spec | Status | Notes |
|---|---|---|---|
| File format | LaTeX strongly preferred; Word accepted | **FAIL** | Manuscript is `.md`; must convert to LaTeX using Springer Nature template |
| LaTeX template | Springer Nature template | **FAIL** | Not used |
| Source files included | All editable source files | **N/A** | Single `.md` file; LaTeX source set TBD |
| Headings | Decimal system (1, 1.1, 1.1.1); max 3 levels | **PASS** | Uses 1, 2.1, 2.2… format |
| Line numbering | Continuous on all pages | **FAIL** | Not present in `.md` |
| Page numbering | Sequential | **FAIL** | Not present in `.md` |
| Title page — authors | Names listed | **PASS** |
| Title page — affiliations | Institution, department, city, country | **PARTIAL** | Only author initials given; full affiliations missing |
| Title page — corresponding author email | Active email required | **FAIL** | No email on title page |
| Title page — ORCID | 16-digit for all authors (recommended) | **FAIL** | Not provided |
| Abstract length | 150–250 words | **PASS** | 249 words |
| Abstract — undefined abbreviations | Must NOT contain | **PASS** | All abbreviations defined in body |
| Abstract — unspecified references | Must NOT contain | **PASS** | No references in abstract |
| Keywords | 4–6 | **PASS** | 5 keywords |
| LLM / AI Disclosure | Documented in Methods if applicable | **PASS** | Present in Declarations |

### Mathematical Notation

| Item | Spec | Status | Notes |
|---|---|---|---|
| Variables/constants in italic | *Italic* | **FAIL** | Uses HTML `<sub>` tags in plain text; e.g., `R<sub>A</sub>` instead of `$R_A$` |
| Numerals/operators upright | Roman/upright | **PARTIAL** | Plain text numerals are upright, but math operators not in math mode |
| Standard functions upright | cos, det, exp, lim, log, max, min, sin, tan, d | **FAIL** | Not in LaTeX math mode; `d(ΔP)/dt` uses plain text |
| Vectors/matrices bold | **Bold** | **N/A** | No vectors/matrices in manuscript |
| Subscripts/superscripts | Use `_` and `^` in LaTeX | **FAIL** | Uses HTML `<sub>` and `<sup>`; e.g., `P<sub>O</sub>'`, `h<sub>i</sub>(t)` |
| HTML tags in math | None allowed | **FAIL** | `<sub>` and `<sup>` used throughout |

**Specific notation fixes needed:**
- `R<sub>A</sub>` → `$R_A$` (italic R, subscript A)
- `P<sub>O</sub>'` → `$P_O'$` (italic P, subscript O, prime)
- `ΔP` → `\Delta P` (upright Delta, italic P)
- `d(ΔP)/dt` → `\mathrm{d}(\Delta P)/\mathrm{d}t` (upright d for derivative)
- `V<sub>ME</sub>` → `$V_{\mathrm{ME}}$`
- `h<sub>i</sub>(t)` → `$h_i(t)$`
- `Θ<sub>i</sub>` → `$\Theta_i$`
- `r<sub>i</sub>` → `$r_i$`
- `p<sub>barotitis</sub>` → `$p_{\mathrm{barotitis}}$`
- `ft·min⁻¹` → `ft\cdot min^{-1}`
- `mmHg` → `\mathrm{mmHg}`
- `daPa` → `\mathrm{daPa}`

### References

| Item | Spec | Status | Notes |
|---|---|---|---|
| In-text citations — name-year | `(Author Year)` or `Author (Year)` | **FAIL** | Uses numbered superscripts (¹⁻³, etc.) |
| Reference list — alphabetized | By first author last name | **FAIL** | Numbered list 1–24 |
| DOIs as full links | `https://doi.org/…` | **FAIL** | Only 1 of 24 refs includes DOI (ref 16) |
| Standard journal abbreviations | Or full title if unsure | **PARTIAL** | Mostly full titles; inconsistent abbreviations |
| No bibliographic details in footnotes | Footnotes for refs prohibited | **PASS** | No footnotes used |

**Reference conversion required:** All 24 references must be reformatted from numbered to name-year style, alphabetized, and DOIs added where available. This is the single largest formatting task.

### Figures

| Item | Spec | Status | Notes |
|---|---|---|---|
| Numbered Arabic numerals | 1, 2, 3… | **PASS** | Captions use 1, 2, 3, 4 |
| Cited consecutively | In text order | **PARTIAL** | Figure 3 and 4 referenced in text; 1 and 2 also cited |
| Format | EPS (vector) or TIFF (halftone) | **UNKNOWN** | Figure source files not present in repo |
| Resolution | 1200/300/600 dpi | **UNKNOWN** | Cannot verify without source files |
| RGB color (8 bits/channel) | If color used | **UNKNOWN** | |
| Helvetica/Arial lettering; 8–12 pt | Sans-serif | **UNKNOWN** | |
| Contrast ratio ≥ 4.5:1 | For lettering | **UNKNOWN** | |
| No titles/captions inside illustrations | Separate text file | **UNKNOWN** | |
| Captions in text file | Bold `Fig. 1`; no end punctuation | **FAIL** | Current format uses `**Figure 1.**` not `**Fig. 1**` and ends with period |
| Size: 84/174 mm wide; max 234 mm high | Journal spec | **UNKNOWN** | |
| Descriptive captions for accessibility | Screen-reader friendly | **PARTIAL** | Captions are descriptive but need reformatting |
| Patterns + colors for colorblind | Accessibility | **UNKNOWN** | |
| **Figure count discrepancy** | Header says 2; captions list 4 | **FAIL** | Must resolve: are there 2 or 4 figures? |

**Figure caption reformatting examples:**
- Current: `**Figure 1.** Descent-rate sensitivity...`
- Required: **`Fig. 1` Descent-rate sensitivity** (no period after number or at end)

### Tables

| Item | Spec | Status | Notes |
|---|---|---|---|
| Numbered Arabic numerals | 1, 2, 3… | **FAIL** | Uses Roman numerals (Table I, II, III, IV) |
| Cited consecutively | In text order | **PASS** | Referenced in order |
| Caption explaining components | Required | **PASS** | Each table has descriptive title |
| Footnotes: superscript lowercase | a, b, c… | **N/A** | No table footnotes used |
| Previously published material cited | At end of caption | **N/A** | Tables appear original |
| **Table numbering** | Arabic required | **FAIL** | Must convert I→1, II→2, III→3, IV→4 |

### Mandatory Declarations

| Declaration | Present? | Notes |
|---|---|---|
| Competing Interests | **PASS** | "The authors declare no financial or non-financial competing interests." |
| Funding | **PASS** | "No external funding supported this work." |
| Data Availability | **PASS** | Detailed statement present |
| Code/Software Availability | **PASS** | GitHub link + MIT license stated |
| Author Contributions (CRediT) | **PASS** | Full CRediT taxonomy for both authors |
| Ethics Statement | **PASS** | Colombian Resolution 8430/1993 cited; Declaration of Helsinki |
| Informed Consent | **PASS** | "Not applicable" with rationale |
| AI/LLM Disclosure | **PASS** | Detailed disclosure present |
| ORCID | **FAIL** | Not provided for any author |
| **Heading format** | Must be "Statements and Declarations" | **FAIL** | Current heading is "Declarations" |

### Supplementary Materials

| Item | Spec | Status | Notes |
|---|---|---|---|
| TRIPOD checklist as supplementary | File S1 mentioned | **PASS** | Referenced in Declarations |
| Model card | Mentioned in Data Availability | **PASS** | Referenced |

---

## Summary Count

| Category | Count |
|---|---|
| PASS | 20 |
| PARTIAL | 5 |
| FAIL | 15 |
| N/A | 4 |
| UNKNOWN | 6 |

**Critical failures (blocks submission):** reference format, file format, figure count discrepancy, line numbering, page numbering, table numbering, declarations heading, ORCID, corresponding author email, affiliations detail.

---

*Audit generated by bmb-submission skill v1.0.0*
