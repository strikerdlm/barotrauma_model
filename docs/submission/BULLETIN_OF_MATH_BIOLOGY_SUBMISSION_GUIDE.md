# Bulletin of Mathematical Biology — Submission Guide

> **Scout run:** 2026-05-01
> **Journal:** Bulletin of Mathematical Biology (Springer Nature)
> **Official journal of:** Society for Mathematical Biology
> **Scope:** Research at the interface of the life and mathematical sciences
> **Publishing model:** Hybrid (subscription + open access)
> **Quartile:** Q2 (Biology), Q1 (Mathematical & Computational Biology)
> **SJR:** ~0.787 | **IF:** 2.2 (JCR 2025) | **CiteScore:** ~2.7
> **APC:** $0 (subscription route) | OA: $3,090 USD / EUR 2,490 / GBP 2,190
> **Source:** https://link.springer.com/journal/11538/submission-guidelines
> **Submission portal:** https://www.editorialmanager.com/bulm (Editorial Manager)

---

## Journal Identity

| Field | Value |
|---|---|
| Full name | Bulletin of Mathematical Biology |
| ISSN (print) | 0092-8240 |
| ISSN (online) | 1522-9602 |
| Publisher | Springer Nature |
| SJR Quartile | Q2 (Biology); Q1 (Mathematical & Computational Biology) |
| SJR Score | ~0.787 (Scimago 2024) |
| CiteScore | ~2.7 (Scopus 2024) |
| Impact Factor | 2.2 (JCR 2025) |
| Indexed in | Scopus, Web of Science (SCIE), PubMed/MEDLINE, MathSciNet |
| APC (subscription) | $0 |
| APC (OA) | $3,090 USD |
| Submission portal | Editorial Manager |
| Official society | Society for Mathematical Biology (SMB) |

---

## Aims & Scope

The Bulletin of Mathematical Biology disseminates original research findings at the interface of biology and the mathematical sciences. **Contributions must have relevance to both fields.** The journal accepts:

- **Original Research Articles** — new biological insights gained with tools from the mathematical sciences, or new mathematical tools with demonstrated applicability to biological investigations.
- **Reviews** — critique with new points of view, synthesizing existing literature.
- **Methods** — new mathematical, statistical, or computational methods relevant to biological problems.
- **Perspectives** — science policy, careers, research conduct, public engagement, opinion pieces.
- **Unsolved Problems** — poorly understood research topics needing attention; aimed at broad audiences.
- **Education** — ideas, methods, tools, tutorials to enhance research and education.

**Key scope requirement for this manuscript:** The physics-informed middle-ear barotrauma model must be framed as a contribution to **mathematical biology / computational physiology** — emphasizing the ODE framework, parameter calibration (ABC-SMC), and sensitivity analysis (Sobol) as methodological advances applicable beyond otology. The clinical aviation-medicine framing should be secondary to the mathematical structure.

---

## Accepted Article Types

| Type | Accepted | Notes |
|------|----------|-------|
| Original research | Yes | Core article type |
| Reviews | Yes | By invitation or submission; must offer critique, not mere summary |
| Methods | Yes | New mathematical/statistical/computational methods |
| Perspectives | Yes | Peer-reviewed at editorial discretion |
| Unsolved problems | Yes | Discuss poorly understood topics |
| Education | Yes | Tutorials, background on methods |
| Case report | No | Not accepted |
| Short communication | No | Not accepted |
| Narrative review | No | Reviews must be critical syntheses |

**This manuscript = Original Research.** It could also be reframed as **Methods** if the emphasis is placed on the ABC-SMC calibration framework and Sobol analysis pipeline as generalizable tools.

---

## Manuscript Format Requirements

### Text

| Requirement | Specification |
|---|---|
| **File format** | **LaTeX strongly preferred.** Word (.docx) also accepted. |
| **LaTeX template** | Springer Nature LaTeX template (recommended) |
| **Submission must include** | Original source + compiled PDF |
| **Source files** | All editable source files at every submission and revision |
| **Headings** | Decimal system (1, 1.1, 1.1.1); max 3 levels |
| **Line numbering** | **Required** — continuous line numbering on all pages |
| **Page numbering** | Sequential page numbering required |

**CRITICAL:** The journal explicitly states: *"Failing to submit a complete set of editable source files will result in your article not being considered for review."*

### Title Page

Must contain:

1. **Title** — concise and informative
2. **Author information:**
   - Name(s) of author(s)
   - Affiliation(s): institution, (department), city, (state), country
   - Clear indication and active email address of corresponding author
   - ORCID (16-digit) for all authors if available
   - For unaffiliated authors: city and country only (email only if requested)
3. **Abstract** — 150 to 250 words (see below)
4. **Keywords** — 4 to 6 keywords
5. **Statements and Declarations** (see Mandatory Declarations below)
6. **Acknowledgments** — people, grants, funds (funding orgs written in full)

**LLM / AI Disclosure:** Use of LLMs (e.g., ChatGPT) must be documented in the Methods section. "AI assisted copy editing" (grammar, style, readability improvements to human-generated text) does **not** need declaration. Human accountability for the final version is mandatory.

### Abstract

- **Length:** 150 to 250 words
- **Must NOT contain:** undefined abbreviations or unspecified references
- **For life-science journals:** Trial registration number (if applicable)

**Current manuscript abstract = 249 words.** This is at the upper limit but acceptable.

### Keywords

- **Number:** 4 to 6
- **Purpose:** indexing

### Mathematical Notation (Scientific Style)

The journal enforces strict typographic conventions:

| Element | Format |
|---|---|
| Mathematical constants, variables, unknown quantities | *Italic* |
| Numerals, operators, punctuation | Roman/upright |
| Commonly defined functions/abbreviations (cos, det, exp, lim, log, max, min, sin, tan, d for derivative) | Roman/upright |
| Vectors, tensors, matrices | **Bold** |

**Apply to manuscript:** The current manuscript uses `<sub>` and `<sup>` HTML tags for subscripts/superscripts. In LaTeX, these should use `_` and `^`. Variables like `R_A`, `P_O`, `ΔP` should be formatted consistently:
- `R_A` → `$R_A$` (italic R, subscript A)
- `ΔP` → `\Delta P` (upright Delta, italic P)
- `d(ΔP)/dt` → `\mathrm{d}(\Delta P)/\mathrm{d}t` (upright d for derivative)

### Abbreviations

Define at first mention; use consistently thereafter.

### Footnotes

- **Use footnotes, NOT endnotes.**
- Numbered consecutively throughout text.
- Table footnotes: superscript lowercase letters (or asterisks for significance values).
- **Never** include bibliographic details in footnotes.
- **Never** include figures or tables in footnotes.
- No footnotes to title or authors (use symbols instead).

---

## Reference Style

### In-text Citation

Cite by **name and year in parentheses**:

- Single author: `(Thompson 1990)`
- Two authors: `(Becker and Seligman 1996)`
- Multiple authors: `(Abbott 1991; Barakat et al. 1995a, b; Kelso and Smith 1998)`
- Within sentence: `This result was later contradicted by Becker and Seligman (1996).`

### Reference List

- **Alphabetize** by last name of first author, then:
  - One author: by name, then chronologically
  - Two authors: by first author, then coauthor, then chronologically
  - Three+ authors: by first author, then chronologically
- **Include DOIs** as full links: `https://doi.org/abc`
- Use standard journal abbreviations (ISSN List of Title Word Abbreviations).
- If unsure, use full journal title.

### Format Examples

**Journal article (all authors):**
```
Gamelin FX, Baquet G, Berthoin S, Thevenet D, Nourry C, Nottin S, Bosquet L (2009) Effect of high intensity intermittent training on heart rate variability in prepubescent children. Eur J Appl Physiol 105:731-738. https://doi.org/10.1007/s00421-008-0955-8
```

**Journal article (et al. accepted):**
```
Smith J, Jones M Jr, Houghton L et al (1999) Future of health insurance. N Engl J Med 965:325-329
```

**Article by DOI:**
```
Slifka MK, Whitton JL (2000) Clinical implications of dysregulated cytokine production. J Mol Med. https://doi.org/10.1007/s001090000086
```

**Book:**
```
South J, Blass B (2001) The future of modern genomics. Blackwell, London
```

**Book chapter:**
```
Brown B, Aaron M (2001) The politics of nature. In: Smith J (ed) The rise of modern genomics, 3rd edn. Wiley, New York, pp 230-257
```

**Dissertation:**
```
Trent JW (1975) Experimental acute renal failure. Dissertation, University of California
```

---

## Tables

| Requirement | Specification |
|---|---|
| Numbering | Arabic numerals (1, 2, 3...) |
| Citation | Consecutive numerical order in text |
| Caption | Required; explain components of the table |
| Previously published material | Give original source as reference at end of caption |
| Footnotes | Superscript lowercase letters (a, b, c...); asterisks for significance values |
| Placement | In body of text |

---

## Figures & Illustrations

### Electronic Submission

| Requirement | Specification |
|---|---|
| Format | EPS (vector); TIFF (halftone); MS Office files acceptable |
| Vector fonts | Must be embedded |
| File naming | `Fig1.eps`, `Fig2.tif`, etc. |
| Graphics program | Indicate what program was used |

### Resolution

| Art type | Minimum resolution |
|---|---|
| Line art (black/white, no shading) | 1200 dpi |
| Halftone (photos, drawings with shading) | 300 dpi |
| Combination (halftone + line art) | 600 dpi |
| Line width | Minimum 0.1 mm (0.3 pt) |

### Color Art

- **Free for online publication**
- If print = B/W, ensure information remains visible when converted
- Do not refer to color in captions if print is B/W
- Submit as **RGB (8 bits per channel)**

### Figure Lettering

| Element | Specification |
|---|---|
| Font | Helvetica or Arial (sans serif) |
| Size | ~2-3 mm (8-12 pt) at final size |
| Consistency | Minimal variance within figure |
| Effects | Avoid shading, outline letters, etc. |
| Titles/captions | Do NOT include within illustrations |

### Figure Numbering

- Arabic numerals (1, 2, 3...)
- Cite in consecutive numerical order
- Parts: lowercase letters (a, b, c)
- Appendix figures: continue main text numbering (NOT A1, A2)
- Supplementary figures: numbered separately

### Figure Captions

- Include in text file, NOT in figure file
- Begin with **Fig.** in bold, followed by number in bold
- **No punctuation** after number or at end of caption
- Example: **`Fig. 1` Description of the figure content**
- Identify all elements; use boxes/circles as coordinate points
- Cite previously published material at end

### Figure Size

| Journal size | Width | Max height |
|---|---|---|
| Large | 84 mm (double-column) or 174 mm (single-column) | 234 mm |
| Small | 119 mm | 195 mm |

### Accessibility

- Descriptive captions (for screen readers)
- Patterns + colors (for colorblind users)
- Contrast ratio ≥ 4.5:1 for lettering

---

## Supplementary Information (SI)

| Aspect | Specification |
|---|---|
| **File formats** | Standard formats |
| **Required in each file** | Article title, journal name, author names; affiliation + email of corresponding author |
| **Audio/Video** | Aspect ratio 16:9 or 4:3; max 2 GB; min 1 sec; formats: avi, wmv, mp4, mov, m2p, mp2, mpg, mpeg, flv, mxf, mts, m4v, 3gp |
| **Text/Presentations** | PDF only (NOT .doc or .ppt) |
| **Spreadsheets** | .csv or .xlsx |
| **Specialized formats** | .pdb, .wrl, .nb, .tex accepted |
| **Multiple files** | .zip or .gz |
| **Citation** | Refer as "Online Resource", e.g., "...as shown in (Online Resource 3)" |
| **Naming** | Consecutive: `ESM_3.mpg`, `ESM_4.pdf` |
| **Captions** | Descriptive caption required for each |
| **Processing** | Published as received; no conversion/editing |
| **Accessibility** | No flashing >3 times per second |

---

## Mandatory Declarations & Statements

All submissions must include under the heading **"Statements and Declarations."** Incomplete submissions will be returned.

### Required Declarations

- [ ] **Competing Interests** — financial or non-financial interests related to the work
- [ ] **Funding** — grant numbers + funder full names
- [ ] **Data Availability** — standard text or custom; repository required where possible
- [ ] **Code/Software Availability** — if applicable (relevant for this manuscript)
- [ ] **Author Contributions** — CRediT taxonomy (Conceptualization, Methodology, Software, etc.)
- [ ] **Ethics Statement** — IRB/Ethics Committee if applicable
- [ ] **Informed Consent** — confirm obtained or state waiver rationale
- [ ] **AI/LLM Disclosure** — document LLM use in Methods; copy editing only exempt
- [ ] **ORCID** — for all authors (strongly recommended)

### Additional Requirements for This Manuscript

- [ ] **Clinical Trial Registration** — N/A (not a clinical trial)
- [ ] **Systematic Review Registration** — N/A
- [ ] **Permissions** — for any previously published figures/tables/text

### Cover Letter

- Required? Not explicitly stated, but strongly recommended
- Suggest reviewers? Yes — institutional email required for each; mix of countries/institutions
- Oppose reviewers? Yes — can request exclusion of certain individuals
- **Suggested reviewer count:** Mix from different countries and institutions
- **Verify identity:** Provide institutional email or link to homepage/publication record/author ID

---

## Peer Review Process

| Aspect | Value |
|---|---|
| Review type | Not explicitly stated; likely double-blind |
| Suggest reviewers | Yes (strongly recommended) |
| Oppose reviewers | Yes |
| Reviewer identity verification | Institutional email or publication record link required |
| International mix | Strongly recommended when suggesting reviewers |

---

## Preprint Policy

| Aspect | Policy |
|---|---|
| Preprint allowed pre-submission | Likely yes (Springer standard) — verify at submission |
| Must disclose preprint | Likely yes — disclose at submission |
| Embargo after acceptance | Standard Springer embargo for subscription route |

---

## Language & Editing

| Aspect | Specification |
|---|---|
| Language | English |
| Language editing | Not required; Springer Nature Author Services available (paid) |
| Free Grammar Check | Available from Springer |

---

## Submission Portal — Step-by-Step

**Portal:** Editorial Manager (https://www.editorialmanager.com/bulm)

1. Create account or log in at Editorial Manager
2. Click "Submit New Manuscript"
3. Select article type: **Original Research** (or **Methods** if reframed)
4. Enter metadata:
   - Title
   - Abstract (paste; 150–250 words)
   - Keywords (4–6)
   - Author list (ORCID for all)
   - Affiliations (institution, department, city, country)
   - Corresponding author email
5. Upload files in order:
   - Main manuscript (LaTeX source + compiled PDF; or Word)
   - Figures (separate files, named Fig1.eps, Fig2.tif, etc.)
   - Tables (if separate from text)
   - Supplementary materials (if any)
   - Cover letter (recommended)
   - Any mandatory declaration forms
6. Enter "Statements and Declarations"
7. Suggest reviewers (names, institutions, emails, expertise)
8. Oppose reviewers if applicable
9. Answer journal-specific questions (competing interests, funding, etc.)
10. Review final submission PDF
11. Submit

**Estimated time:** 2–3 hours first time

---

## Checklist Summary

### Manuscript
- [ ] Title concise and informative
- [ ] Abstract: 150–250 words; no undefined abbreviations; no unspecified references
- [ ] Keywords: 4–6
- [ ] Main text: LaTeX (preferred) or Word; decimal headings (max 3 levels)
- [ ] Line numbering on all pages
- [ ] Page numbers sequential
- [ ] Mathematical notation: italic variables, upright numerals/operators/functions, bold vectors/matrices
- [ ] Source files included (LaTeX: all .tex, .sty, .cls, figures)

### References
- [ ] Name-year format: `(Author Year)` or `Author (Year)`
- [ ] Alphabetized by first author last name
- [ ] DOIs included as full links where available
- [ ] Standard journal abbreviations (or full title if unsure)

### Figures
- [ ] Numbered Arabic numerals; cited consecutively
- [ ] Parts denoted lowercase letters (a, b, c)
- [ ] EPS (vector) or TIFF (halftone); 1200 dpi line / 300 dpi halftone / 600 dpi combo
- [ ] RGB color (8 bits/channel) if color
- [ ] Helvetica or Arial lettering; 8–12 pt; contrast ≥ 4.5:1
- [ ] No titles/captions within illustrations
- [ ] Captions in text file: **`Fig. 1` Bold; no punctuation after number or at end**
- [ ] Size: 84 mm (double-col) or 174 mm (single-col) wide; max 234 mm high

### Tables
- [ ] Numbered Arabic numerals; cited consecutively
- [ ] Caption explaining components
- [ ] Footnotes: superscript lowercase letters
- [ ] Previously published material cited

### Declarations
- [ ] Competing interests
- [ ] Funding statement
- [ ] Data availability
- [ ] Code/software availability
- [ ] Author contributions (CRediT)
- [ ] Ethics statement (if applicable)
- [ ] Informed consent (if applicable)
- [ ] LLM/AI disclosure (if applicable)
- [ ] ORCID for all authors

### Submission
- [ ] All editable source files uploaded
- [ ] Cover letter written and customized
- [ ] Suggested reviewers identified (mix of countries/institutions; institutional emails)
- [ ] Final PDF reviewed before submit

---

## Notes & Caveats

> All requirements above were extracted from https://link.springer.com/journal/11538/submission-guidelines on 2026-05-01.
> Guidelines change without notice. Verify directly at the journal website before submitting.
> Any field marked [VERIFY AT JOURNAL WEBSITE] was not found in the scraped guidelines.
> Colombia is Research4Life Group B = 50% APC discount (not full waiver). IOP offers reduced APC ($675) for Group B, but Springer's standard discount policy should be verified at submission if OA route is chosen.

---

*Generated by journal-scout v2.0 | Diego Malpica / Chiron (OpenClaw)*
