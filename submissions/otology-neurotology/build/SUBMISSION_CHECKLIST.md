# O&N Submission Checklist — MEB Hypobaric Chamber Risk Model

**Manuscript:** Middle Ear Barotrauma During Hypobaric Chamber Training: A Physics-informed, Externally Validated Risk Model
**Article type:** Original Article
**Portal:** http://on.editorialmanager.com
**Managing Editor:** Mackenzie Aronhalt (per 2026-05-21 editorial email; historical: Marianna Hagan, marianna.hagan@wolterskluwer.com · (215) 521-8350)
**Build date:** 2026-05-27 (Round 1 revision — editorial pre-processing fixes)

---

## File inventory

| # | File | Local path | O&N upload category | Status |
|---|---|---|---|---|
| 1 | Title page | `build/title_page.docx` | **Title Page** | ✅ Rebuilt 2026-05-27 |
| 2 | Manuscript body | `build/manuscript_body.docx` | **Manuscript** | ✅ Rebuilt 2026-05-27 (tables removed; 0 embedded tables) |
| 3 | Tables | `build/tables.docx` | **Tables** | ✅ Rebuilt 2026-05-27 (editable Word tables; Tables 1 + 2) |
| 4 | Figure 1 | `figures/Figure1.tif` (612K, 2834×3308 @ 600 dpi RGB) | **Figure** | ✅ Ready — **MUST upload as separate file** |
| 5 | Figure 2 | `figures/Figure2.tif` (456K, 3308×2598 @ 600 dpi RGB) | **Figure** | ✅ Ready — **MUST upload as separate file** |
| 6 | Figure 3 | `figures/Figure3.tif` (564K, 4016×2598 @ 600 dpi RGB) | **Figure** | ✅ Ready — **MUST upload as separate file** |
| 7 | Figure 4 | `figures/Figure4.tif` (1.2M, 4016×3070 @ 600 dpi RGB) | **Figure** | ✅ Ready — **MUST upload as separate file** |
| 8 | Cover letter | `build/cover_letter.docx` | **Cover Letter** | ✅ Rebuilt 2026-05-27 (addressed to Dr. Lustig) |
| 9 | SDC 1: TRIPOD 2015 checklist | `supplementary/SDC1_TRIPOD_checklist.pdf` (60K) + `.docx` (16K) | **Supplemental Digital Content** | ✅ Ready (28-item checklist; 26 PASS + 2 NA) |
| 10 | SDC 2: URI modifier table | `supplementary/SDC2_URI_modifiers.pdf` (16K) + `.docx` (12K) | **Supplemental Digital Content** | ✅ Ready |
| 11 | SDC 3: Calibration summary | `supplementary/SDC3_calibration.pdf` (32K) + `.docx` (12K) | **Supplemental Digital Content** | ✅ Ready |

**Color note:** Figures are currently RGB at 600 dpi. Diego: decide before upload whether to submit as color (color charges may apply — contact Mackenzie Aronhalt for current rate) or convert to grayscale (use ImageMagick: `convert Figure1.tif -colorspace Gray -compress LZW Figure1_gray.tif`).

**CRITICAL — previous submission failed because figure files were not attached.** All four TIFFs must be individually uploaded under the **Figure** category. The manuscript body cites them and contains their legends, but the files themselves must appear in the portal file inventory.

---

## Round 1 revision log (editorial pre-processing — 2026-05-27)

The following changes were made in response to the editorial pre-processing email (Mackenzie Aronhalt, received after 2026-05-19 submission):

| # | Issue flagged | Fix applied |
|---|---|---|
| 1 | Author name mismatch — "Diego L. Malpica, MD" does not match EM profile | Changed to **"Diego L Malpica Hincapie, MD"** (no period after L, dual surname, no accent on Hincapie) in title_page.md, cover_letter.md |
| 2 | Author name mismatch — "Marian A. Farfán, MD" does not match EM profile | Changed to **"Marian Farfan Fontalvo, MD"** (no middle initial, dual surname, no accent on Farfan) in title_page.md, cover_letter.md |
| 3 | Tables embedded in manuscript body file | Removed Tables 1 and 2 from manuscript_body.md. Tables provided as separate editable Word file (`tables.docx`) generated via `_build_tables_docx.py`. Manuscript body now contains 0 embedded tables — verified via python-docx. |
| 4 | Figure files not uploaded in file inventory | Four TIFF files (Figure1–4.tif) are staged in `figures/`. Checklist now prominently notes they MUST be uploaded as separate files under the Figure category. |

---

## Compliance check (skill-driven audit)

### Title page (separate Word file)

- [x] Title — no abbreviations
- [x] Running head ≤45 characters incl. spaces ("PHYSICS-INFORMED MEB MODEL" = 26 chars)
- [x] Full names (Colombian dual surnames) + highest academic degrees for all authors — **byte-match EM profile**
- [x] Institutional affiliations for all authors
- [x] Corresponding author: name, address, email, ORCID
- [ ] **Phone and fax** — to be added prior to portal submission (IFA requires it)
- [x] Source of Funding statement (no external funding)
- [x] COI heading: **"Conflicts of Interest and Source of Funding"** (exact O&N wording)
- [x] Word counts of abstract and body declared
- [x] Acknowledgements
- [x] Presentation at meeting: not applicable (declared)

### Manuscript body file

- [x] Title repeated at top
- [x] **NO author names, affiliations, or identifying headers in body file**
- [x] Structured abstract present, 249 words (within 250-word limit)
- [x] Abstract sections match O&N format: Objective / Study Design / Setting / Patients / Interventions / Main Outcome Measures / Results / Conclusions
- [x] Body word count: **3,442 words** (excluding section headings, refs, tables, legends, abstract) — within 3,500-word O&N limit (58-word margin)
- [x] Sections: Introduction, Materials and Methods, Results, Discussion
- [x] References at end (double-spaced in DOCX export)
- [x] Figure legends at very end of file (after references, per IFA)
- [x] SDC items called out in text and listed at end of file
- [x] **No embedded tables** — tables removed to separate file (verified: 0 tables in DOCX)
- [ ] **Continuous line numbering** — must be enabled in DOCX before upload (IFA requirement). In Word: Layout → Line Numbers → Continuous.
- [ ] **Page numbers** — must be present in header or footer (IFA requirement). In Word: Insert → Page Number.
- [ ] **Double spacing** — must be applied to full document in DOCX (IFA requirement). In Word: Select All → Paragraph → Line Spacing → Double.

### References (AMA format)

- [x] All 24 references numbered in order of first citation
- [x] >6 authors → first 3 + "et al." per O&N IFA (verified for refs 6, 7, 11, 16)
- [x] ≤6 authors → all listed (verified for refs 2, 13, 20 with 6 authors each)
- [x] Journal names in italics, abbreviated per NLM
- [x] Year, volume, issue, pages or DOI for every reference

### Statistics — mandatory effect sizes

- [x] Per-exposure prevalence reported with Wilson 95% CI throughout
- [x] ABC-SMC posterior reported with 95% credible interval
- [x] Sobol indices (S_T and S_i) reported with magnitudes
- [x] Validation comparisons report point estimates with attendant 95% CIs
- [x] No standalone p-values without paired effect estimate
- [x] Methods section explicitly notes deterministic simulator → no inferential p-values

### Figures (4 separate TIFF files)

- [x] Manuscript references each figure (Figs 1–4)
- [x] Figures rendered as TIFF at 600 dpi RGB (mixed photo+text ≥600 dpi threshold per IFA)
- [x] Each figure as separate file named `Figure1.tif` … `Figure4.tif`
- [x] No figure legends embedded inside figure files (legends are in manuscript body file, after references)
- [ ] **Confirm color vs. grayscale decision** — pending Diego (color charges may apply)
- [x] **Figures MUST be uploaded individually** under the Figure category — previous submission failed because they were missing

### Tables (separate editable Word file)

- [x] Table 1 (External validation) — in `tables.docx`
- [x] Table 2 (Descent-rate sensitivity) — in `tables.docx`
- [x] Combined figures + tables = 4 + 2 = **6** (within O&N limit of 6)
- [x] Tables NOT embedded in manuscript body (0 tables in manuscript_body.docx)
- [x] Tables created using Word table feature (python-docx native tables), NOT Excel
- [x] Editable cells — editorial office can modify directly

### AI disclosure (Materials and Methods)

- [x] Statement present: "No generative artificial-intelligence tools were used in the preparation, writing, or editorial revision of the manuscript text, figures, tables, or interpretive content."
- [x] Code-assistance scope documented: Python software implementation under explicit author specification
- [x] AI not listed as author (ICMJE/COPE compliant)

### Commercial product names

- [x] No commercial trade names appear in the manuscript body that require generic-name parentheses on first use
- [x] Software (NumPy, SciPy) noted as standard scientific Python — not promotional

### Supplemental Digital Content

- [x] SDC items cited consecutively in body (SDC 1 in Section 2.1; SDC 2 in Section 2.5; SDC 3 in Sections 2.8 and 3.1)
- [x] SDC list at end of manuscript body file (Section "Supplemental Digital Content")
- [ ] SDC URLs `http://links.lww.com/MAO/[code]` placeholder text noted for editorial assignment

### Cover letter

- [x] Addressed to Editor-in-Chief (Dr. Lustig)
- [x] Date updated to 2026-05-27
- [x] Article type stated explicitly ("Original Article")
- [x] What-it-adds paragraph — clinical prediction tool for individual otology decisions
- [x] Confirms not under consideration elsewhere
- [x] Confirms all authors approved submission
- [x] IRB/ethics statement (Resolution 8430, Article 11(a) waiver; FAC institutional release)
- [x] 3 suggested reviewers with degree, institution, expertise rationale
- [x] Author names match EM profile in signoff and co-author mention
- [x] No opposed reviewers section (none specified)

---

## Outstanding manual steps before portal resubmission

| # | Action | Owner | Notes |
|---|---|---|---|
| 1 | **Add phone and fax** to corresponding-author block on title page | DLM | Edit `title_page.docx` directly before upload. IFA requires fax and telephone. |
| 2 | **Color vs. grayscale figure decision** | DLM | Figures are RGB at 600 dpi. If color, contact Mackenzie Aronhalt re: charges. If grayscale: `convert FigureN.tif -colorspace Gray -compress LZW FigureN_gray.tif`. |
| 3 | **Enable continuous line numbering** in `manuscript_body.docx` | DLM | In Word: Layout → Line Numbers → Continuous. IFA mandates this; pandoc output does not include it. |
| 4 | **Enable page numbers** in `manuscript_body.docx` | DLM | In Word: Insert → Page Number → choose header or footer. IFA mandates this. |
| 5 | **Apply double spacing** in all DOCX files | DLM | In Word: Select All → Paragraph → Line Spacing → Double. IFA mandates this. |
| 6 | **Upload Figure1–4.tif as separate files** under the **Figure** category | DLM | Previous submission was rejected because figure files were missing from the file inventory. Each TIFF must be uploaded individually. |

---

## Portal upload sequence (Editorial Manager)

Navigate to **http://on.editorialmanager.com** → log in → select the existing submission → "Edit Submission" (or resubmit per editorial instructions).

1. **Article Type:** Original Article (already set)
2. **Title:** Middle Ear Barotrauma During Hypobaric Chamber Training: A Physics-informed, Externally Validated Risk Model
3. **Authors:** Diego L Malpica Hincapie, MD (corresponding) + Marian Farfan Fontalvo, MD — **verify names byte-match EM profiles**; verify ORCID and affiliations
4. **Abstract:** paste structured abstract from `manuscript_body.md` (8 O&N-required sections)
5. **Keywords (1–5, MeSH preferred):** Eustachian Tube Dysfunction; Aerospace Medicine; Pressure; Risk Assessment; Models, Statistical
6. **Upload files** (in this order, to these categories):
   - `cover_letter.docx` → **Cover Letter**
   - `title_page.docx` → **Title Page**
   - `manuscript_body.docx` → **Manuscript**
   - `tables.docx` → **Tables** (editable Word file, separate from manuscript)
   - `Figure1.tif` → **Figure** (label "Figure 1")
   - `Figure2.tif` → **Figure** (label "Figure 2")
   - `Figure3.tif` → **Figure** (label "Figure 3")
   - `Figure4.tif` → **Figure** (label "Figure 4")
   - `SDC1_TRIPOD_checklist.pdf` → **Supplemental Digital Content**
   - `SDC2_URI_modifiers.pdf` → **Supplemental Digital Content**
   - `SDC3_calibration.pdf` → **Supplemental Digital Content**
7. **Funding / COI portal fields:** copy verbatim from title page
8. **Ethics / IRB portal field:** "Retrospective de-identified registry analysis classified as *investigación sin riesgo* under Colombian Resolution 8430/1993 Article 11(a); no IRB submission required. Publication authorized by the Colombian Aerospace Force."
9. **AI-use portal field (if asked):** "No generative AI tools were used in the preparation, writing, or editorial revision of the manuscript. AI-assisted software-engineering support was used for author-directed implementation of the open-source Python simulator."
10. **Build PDF for approval** → review carefully:
    - Confirm title page contains all author info with EM-matching names
    - Confirm manuscript body contains NO author names or affiliations
    - Confirm manuscript body contains NO embedded tables
    - Confirm tables file contains Tables 1 and 2 as editable Word tables
    - Confirm **all 4 figures appear** in correct order with sufficient resolution
    - Confirm figure legends appear at end of body, not inside figure files
    - Confirm continuous line numbering is present
    - Confirm page numbers are present
    - Confirm references are double-spaced
11. **Approve and submit** → record manuscript number from confirmation email
