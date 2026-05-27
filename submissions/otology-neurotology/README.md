# Otology & Neurotology Submission Package — Paper 1

**Manuscript:** *Middle Ear Barotrauma During Hypobaric Chamber Training: A Physics-informed, Externally Validated Risk Model*

**Target journal:** Otology & Neurotology (Wolters Kluwer / LWW, Q1 ORL)
**Portal:** http://on.editorialmanager.com
**Build date:** 2026-05-11
**Skill used:** [`otology-submit`](https://github.com/strikerdlm/SKILLS.md/tree/main/otology-submit) v1.0.0

---

## Folder structure

```
otology-neurotology/
├── README.md                        # this file
├── source/                          # untouched source (audit trail)
│   ├── manuscript.md                # original Paper 1 manuscript (5,869 words total)
│   └── manuscript_author_page.md    # original title page (BMB-titled — superseded)
├── build/                           # O&N-compliant submission files
│   ├── title_page.md                # → DOCX export needed
│   ├── manuscript_body.md           # → DOCX export needed (NO author info)
│   ├── cover_letter.md              # → DOCX export needed
│   └── SUBMISSION_CHECKLIST.md      # pre-submission audit + portal sequence
├── figures/                         # TIFFs to be rendered (Figure1–4.tif)
└── supplementary/                   # SDC items
    ├── SDC1_TRIPOD_checklist.pdf    # TO BUILD (28-item TRIPOD 2015)
    ├── SDC2_URI_modifiers.md        # ready (PDF export needed)
    └── SDC3_calibration.md          # ready (PDF export needed)
```

---

## Changes from source to O&N-compliant build

The `build/` files diverge from `source/` in the ways the `/otology-submit` skill required:

| # | Change | Reason |
|---|---|---|
| 1 | **Article type label** changed from "Original Research" → "Original Article" | O&N article-type taxonomy |
| 2 | **Abstract restructured** to O&N headings: Objective / Study Design / Setting / Patients / Interventions / Main Outcome Measures / Results / Conclusions | O&N requires these 8 exact headings (not Background / Objective / Methods / Results / Conclusion) |
| 3 | **Title page title updated** from "Beyond Binary Lock…" (BMB framing) → primary clinical-prediction title | Avoid math-biology framing that drove the BMB desk rejection; align with clinical readership of O&N |
| 4 | **Running head updated** to "PHYSICS-INFORMED MEB MODEL" (26 chars) | Match the clinical-prediction-model framing |
| 5 | **COI heading** changed to exactly "Conflicts of Interest and Source of Funding" | O&N-mandated wording |
| 6 | **Tables I and II moved to SDC** | Combined figures+tables count: 8 (4 figures + 4 tables) → 6 (4 figures + 2 tables, within O&N limit). Tables I (URI modifiers, methods reference data) and II (calibration summary, technical data) became SDC 2 and SDC 3 respectively. Headline results tables (external validation, descent-rate sensitivity) remain in the main text as Tables 1 and 2. |
| 7 | **SDC call-outs added** at first mention of each item in the body | O&N requires consecutive SDC citation with description |
| 8 | **Word count line corrected** from "figures 2" → "figures 4 · tables 2 · supplemental digital content items 3" | Source had a typo; reconciled with actual figure/table counts |
| 9 | **Title page split** from `source/manuscript_author_page.md` → standalone `build/title_page.md` with all author info | O&N requires title page in a separate Word file, with NO author info anywhere in the manuscript body file |
| 10 | **Reference styling** harmonized to AMA (italic journal names, ≤6 authors then "et al.") | O&N uses AMA format |

The body manuscript text (Methods through Discussion) was preserved verbatim except for:
- AMA-style italicization of journal names in references
- Conversion of unicode superscript citation markers (¹²³) to `<sup>` HTML tags for pandoc compatibility
- Single redundant Discussion-section closing sentence added to surface clinical utility for an otology readership explicitly (per journal-scout reframing checklist)
- Section 2.7's R-A abbreviation expanded on first use

---

## Outstanding manual steps before portal submission

See `build/SUBMISSION_CHECKLIST.md` for the full pre-upload audit. Status of remaining items:

0. ~~Trim body to ≤3,500 words~~ ✅ **Done.** 3,601 → 3,442 words (under limit by 58 words).
1. ~~Render Figures 1–4 as TIFF~~ ✅ **Done.** All 4 TIFFs (600 dpi RGB) staged in `figures/Figure1-4.tif`.
2. ~~Build SDC 1: TRIPOD 2015 28-item checklist~~ ✅ **Done.** PDF + DOCX in `supplementary/`.
3. ~~Convert all `.md` build files to `.docx` via pandoc~~ ✅ **Done.** title_page.docx, manuscript_body.docx, cover_letter.docx ready.
4. ~~Convert SDC 2 and SDC 3 `.md` to PDF~~ ✅ **Done.** Both PDF and DOCX rendered.
5. **Add phone and fax** to corresponding-author block on title page — pending Diego
6. **Color vs. grayscale figure decision** — pending Diego (currently RGB; contact Marianna Hagan if color is needed)
7. ~~Confirm current Editor-in-Chief name~~ ✅ **Done.** Lustig, MD (Columbia) is current EIC through June 30, 2026; cover letter is addressed to him.
8. ~~Verify Ghadiali email~~ ✅ **Done.** All 3 reviewer emails verified: Alper (cuneyt.alper@chp.edu), Fokkens (w.j.fokkens@amsterdamumc.nl — domain updated), Ghadiali (ghadiali.1@osu.edu).

---

## Compliance audit summary (skill-driven)

Per `/otology-submit check`:

- ✅ Title page (separate file) — 11 of 12 items PASS; 1 item (phone/fax) pending manual entry
- ✅ Manuscript body — 9 of 9 items PASS; no author info ✓, abstract heading compliant ✓, **body word count = 3,442 words (within 3,500-word limit; 58-word margin)** after compression of §4.1 Limitations and §4.2 Incorporation of 2025–2026 evidence.
- ✅ References (AMA format) — 4 of 4 items PASS; double-spacing applied during DOCX export
- ✅ Statistics — 5 of 5 items PASS; all p-equivalents reported with CI/CrI
- ⚠️ Figures — 1 of 5 items PASS; 4 items pending file rendering (out of scope of this build, requires running the simulator export pipeline)
- ✅ Tables — 2 of 2 items PASS; combined figures+tables at 6 (limit 6)
- ✅ AI disclosure — 3 of 3 items PASS; stance is consistent with workspace policy and ICMJE/COPE
- ✅ Commercial product names — no commercial trade names requiring generic-name parentheses
- ✅ SDC — 2 of 2 items PASS; consecutive citation and final list both present
- ✅ Cover letter — 8 of 8 items PASS

**Overall:** content compliance is complete; remaining work is file-format conversion (DOCX/PDF/TIFF) and addition of corresponding-author phone/fax.
