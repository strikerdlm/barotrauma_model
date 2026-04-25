# AMHP Editorial Manager — Upload Playbook

**Manuscript:** Physics-Informed Middle Ear Barotrauma Risk for Hypobaric Chamber Training
**Corresponding author:** Diego L. Malpica, MD · diego.malpica@fac.mil.co · ORCID 0000-0002-2257-4940
**Co-author:** Marian A. Farfán, MD (Subdirectorate of Aerospace Sciences, DIMAE, Colombian Aerospace Force)
**Portal:** https://www.editorialmanager.com/AMHP/
**Journal email:** AMHPJournal@asma.org

Pre-requisite: the three FAIL items in `2026-04-18_amhp_compliance_audit.md` are resolved, figures re-rendered as grayscale, and the four forms signed.

---

## Step 0 — Pre-flight files checklist

Work from `docs/submission/` so every file has a canonical name and nothing gets uploaded wrong:

| # | File | Source | Portal label |
|---|---|---|---|
| 1 | `cover_letter.pdf` | from `docs/cover_letter.md` via pandoc → PDF | Cover Letter |
| 2 | `manuscript.docx` | from `docs/manuscript.md` via pandoc → Word | Manuscript |
| 3 | `author_title_page.docx` | from `docs/manuscript_author_page.md` via pandoc → Word | Title Page |
| 4 | `fig_01_descent_rate_sensitivity.tiff` | `docs/figures/paper_c/` (ECharts → SVG → 600 dpi LZW TIFF, Wong colorblind palette is greyscale-legible) | Figure |
| 5 | `fig_02_sobol_sensitivity.tiff` | `docs/figures/paper_c/` (ECharts → SVG → 600 dpi LZW TIFF, Wong colorblind palette is greyscale-legible) | Figure |
| 6 | `fig_03_external_validation.tiff` | `docs/figures/paper_c/` (TRIPOD external-validation forest plot — observed vs simulated for FAC anchor + 3 Italian AF cohorts) | Figure |
| 7 | `fig_04_uri_pet_interaction.tiff` | `docs/figures/paper_c/` (5 PET × 6 URI heatmap; visualises the headline pathophysiology innovation) | Figure |
| 8 | `forms/author_checklist_signed.pdf` | Editorial Manager form, wet signature | Author Checklist |
| 9 | `forms/copyright_release_signed.pdf` | Editorial Manager form, wet signature | Copyright Release Form |
| 10 | `forms/coi_signed.pdf` | Editorial Manager form, wet signature (one author = one section) | Conflict of Interest |
| 11 | `dimae_ethics_memo.pdf` | DIMAE IRB/ethics office | Supplementary Material |

**Skip:** Color Surcharge form (B&W print requested).

Pandoc recipes (run from repo root):

```bash
# Manuscript (depersonalized body + tables + figure captions)
pandoc docs/manuscript.md \
  -o docs/submission/manuscript.docx \
  --standalone \
  --reference-doc=docs/amhp_reference.docx  # if you have a template; else omit

# Author/title page
pandoc docs/manuscript_author_page.md \
  -o docs/submission/author_title_page.docx \
  --standalone

# Cover letter
pandoc docs/cover_letter.md \
  -o docs/submission/cover_letter.pdf \
  --pdf-engine=xelatex
```

If no AMHP reference template exists, use the default pandoc Word output and manually verify:
- Line spacing set to 2.0 (Home → Paragraph → Line spacing → Double).
- Page numbers in header, upper-right (Insert → Page Number → Top Right).
- Insert page break before each table heading (Table I, II, III, IV).
- Insert page break before "Figure captions" heading.
- Text alignment = Left (ragged right), not Justify.

---

## Step 1 — Log in

Open https://www.editorialmanager.com/AMHP/

- If you have an ORCID login, click "Login via ORCID" and use 0000-0002-2257-4940.
- If first time: register. Use your institutional/medical email and the same ORCID. Save the username/password somewhere durable (1Password, KeePass).

---

## Step 2 — Start a new submission

Landing page → "Submit New Manuscript" → Article Type: **Research Article**.

Confirm the Article Type limits on the next page:
- Abstract ≤ 250 words
- Body ≤ 6,000 words (Introduction → Conclusions only)
- Tables ≤ 4, Figures ≤ 4, References ~25

---

## Step 3 — Enter title, running head, abstract

Paste the DEPERSONALIZED title (no author names): `Physics-Informed Middle Ear Barotrauma Risk for Hypobaric Chamber Training`

Running head: `PHYSICS-INFORMED MEB MODEL`

Paste the abstract text verbatim from `manuscript.md` (after the FAIL-1 trim). Confirm the portal's word counter reads ≤ 250.

---

## Step 4 — Keywords

Enter the 5 keywords one per field, after the FAIL-3 replacement:

1. Eustachian tube dysfunction
2. altitude training
3. upper respiratory infection
4. physics-informed modeling
5. external validation

Confirm none appears verbatim in the title.

---

## Step 5 — Authors

**Author 1 (Corresponding, PI):**

- **Full name:** Diego L. Malpica, MD
- **Affiliation:** Subdirectorate of Aerospace Sciences, Direction of Aerospace Medicine (DIMAE), Colombian Aerospace Force (Fuerza Aeroespacial Colombiana, FAC), Bogotá, Colombia
- **Email:** diego.malpica@fac.mil.co
- **ORCID:** 0000-0002-2257-4940
- **Corresponding author:** ✓
- **CRediT contribution:** "Conceptualization; Methodology; Software; Validation; Formal analysis; Investigation; Data curation; Writing – Original Draft; Writing – Review & Editing; Visualization; Supervision; Project administration."

**Author 2:**

- **Full name:** Marian A. Farfán, MD
- **Affiliation:** Subdirectorate of Aerospace Sciences, Direction of Aerospace Medicine (DIMAE), Colombian Aerospace Force, Bogotá, Colombia
- **Email:** [TO BE COMPLETED — institutional @fac.mil.co]
- **ORCID:** [TO BE COMPLETED]
- **Corresponding author:** ✗
- **CRediT contribution:** "Conceptualization; Methodology; Validation; Writing – Review & Editing."

---

## Step 6 — File uploads (in this order)

1. **Cover Letter** → `cover_letter.pdf`
2. **Manuscript** → `manuscript.docx` (depersonalized; includes abstract, body, references, tables, figure captions)
3. **Title Page** → `author_title_page.docx` (full author info)
4. **Figure** → `fig_01_descent_rate_sensitivity.tiff`
5. **Figure** → `fig_02_sobol_sensitivity.tiff`
6. **Figure** → `fig_03_external_validation.tiff`
7. **Figure** → `fig_04_uri_pet_interaction.tiff`
8. **Author Checklist** → `forms/author_checklist_signed.pdf`
9. **Copyright Release Form** → `forms/copyright_release_signed.pdf`
10. **Conflict of Interest** → `forms/coi_signed.pdf`
11. **Supplementary Material** → `dimae_ethics_memo.pdf`

Do NOT upload the Agreement-to-Pay-Extra-Charges form (B&W print).

---

## Step 7 — Suggested reviewers

Enter each of the five reviewers in separate rows:

| # | Full name | Institution | City, Country | Email |
|---|---|---|---|---|
| 1 | William J. Doyle, PhD | University of Pittsburgh School of Medicine, Dept. of Otolaryngology | Pittsburgh, PA, USA | (verify — see reviewer-verification checklist) |
| 2 | Cuneyt M. Alper, MD | Children's Hospital of Pittsburgh, Dept. of Otolaryngology | Pittsburgh, PA, USA | (verify) |
| 3 | Samir N. Ghadiali, PhD | Ohio State University, Dept. of Biomedical Engineering | Columbus, OH, USA | (verify) |
| 4 | Francesco Morgagni, MD | Italian Air Force, Experimental Flight Centre (Pratica di Mare) | Pomezia, Italy | (verify) |
| 5 | Andrea Landolfi, MD | Italian Air Force | Rome, Italy | (verify) |

For each, fill the 1–2 sentence rationale field with the text already drafted in `cover_letter.md` §"Suggested reviewers."

---

## Step 8 — PDF proof review (CRITICAL — do not skip)

The portal builds a compiled PDF from your uploads. Inspect it end-to-end before clicking Submit:

- [ ] Title page shows the title but NO author names (depersonalized).
- [ ] Running head appears in every page header, upper right.
- [ ] Page numbers appear every page, upper right.
- [ ] Double-spaced throughout.
- [ ] Ragged right margin (not justified).
- [ ] Superscript citations, ≤ 3 per callout.
- [ ] References in NLM format; all 24 cited in body; citation-order.
- [ ] Table I, II, III, IV after References; each on its own page.
- [ ] Figure captions section at the end of the manuscript file; figures NOT embedded in body.
- [ ] Figures 1 and 2 appear as separately-uploaded files (not in body).

If any of these fail, cancel/withdraw, go back to the upload step, and re-upload the corrected file. The portal allows replacement uploads before final submission.

---

## Step 9 — Submit

Click **Submit**.

Save the confirmation email (contains the AMHP manuscript ID, e.g., `AMHP-2026-####`) and paste the ID into `docs/submission/manuscript_id.txt`.

Expected first response from editorial office: 1–3 business days.

---

## Post-submission

- **GitHub Release:** tag the current `main` as `v2.2.1-manuscript` with release notes pointing to the submitted manuscript PDF. Do NOT push source changes to the manuscript after this tag until the revision decision.
- **Update `HOW_TO_CONTINUE.md`:** swap the "Next step" from "Complete AMHP submission" to "v2.3.0 roadmap work" (already queued there).
- **During review (~2 weeks):** start the v2.3.0 roadmap and the frontend-port Option 2 work. Do NOT amend the manuscript unless the editor requests it — a moving model confuses reviewers.

---

## Emergency rollback

If you accidentally submit with an error (e.g., un-depersonalized title page):

1. Immediately email the editorial office at **AMHPJournal@asma.org** with subject `WITHDRAW & RESUBMIT — AMHP-YYYY-####` and explain.
2. In the portal, the submission may still be in "Editorial Office Processing" — ask them to return it to your Author Main Menu.
3. Fix, re-upload, re-submit.

Editorial offices are generally accommodating for day-of-submission errors. Do not ignore and wait.
