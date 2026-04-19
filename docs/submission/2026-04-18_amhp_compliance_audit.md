# AMHP Compliance Audit — 2026-04-18

**Manuscript:** `docs/manuscript.md` — "Physics-Informed Middle Ear Barotrauma Risk for Hypobaric Chamber Training"
**Cover letter:** `docs/cover_letter.md`
**Author page:** `docs/manuscript_author_page.md`
**Figures:** `docs/figures/figure1_descent_rate_sensitivity.tiff`, `docs/figures/figure2_sobol_indices.tiff`

**Article type:** Research Article (limits: 6,000 body words; 250 abstract words; ≤4 tables; ≤4 figures; ~25 refs)
**Journal:** *Aerospace Medicine and Human Performance* — Feb 2026 Instructions for Authors
**Portal:** https://www.editorialmanager.com/AMHP/

---

## Summary

**5 FAIL, 5 WARN, 20 PASS.** All FAILs fixable in <45 min; two of them were
discovered through web-verification of the cover letter's reviewer list and
are critical — **do not submit until all five FAILs are resolved.** See
companion `2026-04-18_reviewer_verification_checklist.md` for the reviewer
diff.

---

## Blocking issues (FAIL)

### FAIL-1 — Abstract exceeds 250 words

Measured 255 words (manuscript header claims 246). Must cut ≥5 words.

Fix: trim redundancy in the abstract's last three sentences. The sentence
"Saltelli-Sobol sensitivity identified the aperture half-point as the
dominant variance driver and therefore the highest-leverage empirical
refinement target." can be tightened to "Saltelli-Sobol sensitivity
identified the aperture half-point as the dominant variance driver."
(−10 words). After editing, update the word-count line in `manuscript.md:7`
and re-verify.

### FAIL-2 — Dangling references 23, 24, 25

Reference-list entries that are not cited anywhere in the body (AMHP
uses NLM citation-order — every listed reference must be cited):

- **Ref 23** — Ryan MJ et al. 2018, "Prevention of otic barotrauma in
  aviation: a systematic review," *Otol Neurotol* 39(5):539-549.
- **Ref 24** — Rosenkvist L et al. 2008, "Barotrauma of the ear in
  Danish pilots," *Ugeskr Laeger* 170(42):3572-3574.
- **Ref 25** — Ikeda R et al. 2017, "Patulous Eustachian Tube Handicap
  Inventory," *Otol Neurotol* 38(5):721-725.

Fix: either (a) cite each where topically relevant, or (b) remove from
the reference list and renumber references 26 → 23 (Moayedi), 27 → 24
(Oshima). Option (b) shortens the list to 24 refs and removes a WARN on
over-count. Suggested cite locations if keeping them:

- Ref 23 — Introduction, after "Ryan et al." mention (no such mention
  currently exists; cite at ref to existing prevention-systematic-review
  framing, e.g., line 25 after "Clinical experience contradicts the latter
  when mucosal edema (such as concurrent URI) converts a patent tube into
  a paradoxically closed one.⁶⁻⁸" → add `²³`).
- Ref 24 — Introduction, 30-85% pilot-career prevalence claim (line 21,
  currently only `⁴`) → extend to `⁴·²⁴`.
- Ref 25 — §2.4 PET pathophysiology (line 49) could cite the PHI
  instrument → add `²⁵` after Shindo 2025 citation.

**Recommendation:** Option (b) — remove all three. They add no claim the
manuscript doesn't already support from closer references, and removing
them takes the ref list from 27 → 24 (inside the ~25 AMHP guideline).

### FAIL-3 — Reviewer 1 (William J. Doyle) is deceased

Web verification against Pitt University Times obituary
(https://www.utimes.pitt.edu/archives/?p=40927) confirms: William J. "Doc"
Doyle died Oct. 21, 2016. The cover letter lists him as suggested reviewer
#1. **Replace.** Proposed replacement: Stephen Chad Kanick, PhD (Thayer
School, Dartmouth) — first author of Kanick-Doyle 2005 and thus the other
co-owner of the canonical model this manuscript extends. See
`2026-04-18_reviewer_verification_checklist.md` §"Edit 1" for the exact
cover-letter diff and alternate fallback (J. Douglas Swarts, PhD).

### FAIL-4 — Two reviewer first-names are incorrect

PubMed 2012 paper (PMID 22764614) lists the authors of the
external-validation cohort as **Fabio Morgagni** and **Angelo Landolfi**.
The cover letter writes them as "Francesco Morgagni" and "Andrea
Landolfi." Both first names are wrong. AMHP portal editors verify
reviewer identities against published-author records; a name mismatch will
trigger a desk-level clarification request and delay initial triage.

Fix: apply the diffs in `2026-04-18_reviewer_verification_checklist.md`
§"Edit 2" and §"Edit 3" to `docs/cover_letter.md`.

### FAIL-5 — Keywords overlap title

Of the 5 keywords declared, two appear verbatim (case-insensitive) in the title:

- "middle ear barotrauma" ↔ title has "Middle Ear Barotrauma"
- "hypobaric chamber" ↔ title has "Hypobaric Chamber"

AMHP IFA §keyword rule: "3–5; none should appear verbatim in the title."

Fix: replace the two overlapping keywords with non-overlapping terms that
still index the paper well. Suggested 5-keyword set:

1. Eustachian tube dysfunction
2. altitude training
3. upper respiratory infection
4. physics-informed modeling
5. external validation

(Drops "middle ear barotrauma" and "hypobaric chamber"; adds "Eustachian
tube dysfunction" and "altitude training." None appears verbatim in the
title. All five remain strong MeSH/indexing terms for the paper.)

---

## Operational confirmations required (WARN)

### WARN-1 — Figures are RGB/RGBA, cover letter says B&W print

Measured:
- figure1: 2318×2905 px, 600 dpi, RGB with alpha channel (4 samples,
  photometric=2).
- figure2: 2340×1711 px, 600 dpi, RGB with alpha channel.

AMHP Feb-2026 IFA: "Color mode: grayscale if B&W print intended."
Cover letter declares B&W print, so figures should be saved as grayscale
(photometric=1) or bi-level, with the alpha channel flattened against
white. The 600 dpi resolution is compliant for combination-halftone
rasterized plots.

Fix: re-save both TIFFs as grayscale (8-bit) with alpha flattened against
white. Pandoc/matplotlib does this with `plt.savefig(..., dpi=600,
facecolor='white')` followed by `Pillow` conversion
`im.convert('L').save('...tiff', dpi=(600,600), compression='tiff_lzw')`.
Validate afterward by re-running the TIFF-header probe in this audit.

### WARN-2 — References using "et al." (4 of 27 refs)

Refs 11 (Doyle 1999), 16 (Chen 2022), 26 (Moayedi 2025), 27 (Oshima 2025)
abbreviate with "et al." after 3 authors. Standard NLM/PubMed style allows
"et al." for >6 authors and requires all authors listed for ≤6. AMHP
Feb-2026 IFA does not state whether it permits "et al." at all or demands
all-author lists in every case.

Fix: verify each of the four references' full author list:

- Ref 11 Doyle 1999 *Laryngoscope* — PubMed lists: Doyle WJ, Skoner DP,
  Alper CM, Allen G, Moody SA, Seroky JT, Hayden FG — **7 authors**, "et
  al." OK per standard NLM.
- Ref 16 Chen 2022 *Eur Arch Otorhinolaryngol* — verify on PubMed; if ≤6
  authors, expand; if ≥7, "et al." OK.
- Ref 26 Moayedi 2025 *Undersea Hyperb Med* — verify; expand if ≤6.
- Ref 27 Oshima 2025 *Auris Nasus Larynx* — verify; expand if ≤6.

Recommendation: safer to list all authors for all 27 refs (the AMHP
quick-reference is silent on the "et al." cutoff, and the editorial office
sometimes demands full lists). Action: go through each ref; if it
currently abbreviates and the full author count is ≤6, expand.

### WARN-3 — Reference count 27 vs. ~25 guideline

27 references against AMHP's "~25" guideline for a Research Article. Not a
hard cap. If you act on FAIL-2 recommendation (b) — remove refs 23, 24,
25 — the count drops to 24, resolving this.

### WARN-4 — Double-spacing, page numbers, table-per-page, figure-captions-on-final-page

These are Word-export artifacts, not inherent to `manuscript.md`. Must be
verified on the generated `.docx` before upload:

- Double-spaced throughout (line spacing 2.0).
- Page numbers upper-right header, starting page 1.
- Each table on its own page (page break before/after).
- Figure captions on a separate FINAL page (after Table IV; currently in
  `manuscript.md` under `## Figure captions` at line 245 — the converter
  must insert a page break before this section).
- Ragged right margin (no full-justify).

Fix: use pandoc with a .docx reference template enforcing these rules.
Suggested pandoc command (from `npj-pdf-export` skill's sibling .docx
template, or AMHP custom reference.docx):

```bash
pandoc docs/manuscript.md \
  -o docs/submission/manuscript_amhp.docx \
  --reference-doc=docs/amhp_reference.docx \
  --standalone
```

Then open the `.docx` and verify the five checklist items above by eye.

### WARN-5 — Reviewer institutional emails not in cover letter

Cover letter §"Suggested reviewers" defers emails to portal entry: "Current
institutional emails for suggested reviewers will be provided through the
Editorial Manager portal fields at submission." This is fine operationally
— the portal collects them — but you must have all 5 emails verified and
ready before starting the portal session. See companion doc
`2026-04-18_reviewer_verification_checklist.md` for where to find each.

### WARN-6 — Ghadiali lab Sheer 2012 and Malik 2019 cited in §2.5 but not in reference list

Line 53 cites "Ghadiali-group FEM and multi-scale work¹⁷" which points to
ref 17 (Ghadiali 2010 *Ann Otol Rhinol Laryngol*). The CHANGELOG 2.2.0
entry additionally names "Sheer 2012 (PMID 21996354) and Malik & Ghadiali
2019 (PMID 29395489)" as motivating papers, but these are not in the
reference list and are not individually cited. If the sentence claims to
approximate work from all three, consider either (a) adding Sheer 2012
and Malik 2019 as formal references and citing them inline alongside ref
17, or (b) leaving the single ref 17 in place (the sentence wording allows
either). Recommendation: (b) — Ghadiali 2010 covers the conceptual
framework and is the canonical citation for FEM ET modeling.

---

## Rule-by-rule PASS list

All rules met except the FAILs and WARNs above:

### Manuscript
- PASS Title 74 chars ≤ 100; no trailing punctuation.
- PASS Running head 26 chars ≤ 30; ALL CAPS.
- PASS Abstract unstructured (single paragraph).
- PASS Keywords count = 5 (3–5 required).
- PASS Body word count ~2,600 words (Introduction → Conclusions, tables
  stripped). ≤ 6,000 Research Article limit.
- PASS In-text citations superscript, citation-order, ≤ 3 per callout
  (max run observed: `⁹⁻¹¹`, `⁶⁻⁸`, `¹⁻³`).
- PASS References in NLM/MEDLINE format; abbreviated journal names
  (verified: "Aviat Space Environ Med", "J Appl Physiol", "Aerosp Med Hum
  Perform", "Auris Nasus Larynx", "Laryngoscope", "Arch Otolaryngol Head
  Neck Surg", "Hear Res", "J R Soc Interface", "Comput Phys Commun",
  "Otol Neurotol", "Eur Arch Otorhinolaryngol", "Ugeskr Laeger", "Undersea
  Hyperb Med").
- PASS Tables numbered I–IV (Roman).
- PASS Tables placed AFTER References in source order.
- PASS Figure captions on separate section at end of manuscript file.
- PASS Figures NOT embedded in body (uploaded separately).
- PASS Title page depersonalized (lines 1–9 carry no author names).
- PASS Author page separate file with full names, degrees, affiliations,
  ORCID, corresponding-author contact, ICMJE contributions, COI, funding,
  data availability.
- PASS Statistics: exact values reported (1.89%, 5.73%, Wilson CIs,
  Sobol indices); p-values absent by justified design (simulator is
  deterministic given a cohort prior — stated line 67).
- PASS Units: SI-dominant with aviation exceptions (ft, ft·min⁻¹) clearly
  denoted and SI equivalents supplied where needed.

### Cover letter (all 11 §3–§12 elements)

- PASS Originality statement.
- PASS Thesis/dissertation disclosure (negative — not derived).
- PASS Preprint disclosure (negative — not posted).
- PASS Author approval statement.
- PASS ICMJE authorship contributions.
- PASS Generative-AI disclosure (explicit negation of AI in writing;
  scoped disclosure of AI-assisted software implementation).
- PASS Statistical expertise disclosure (author performed, with software
  stack and reproducibility reference).
- PASS Suggested reviewers ≥ 2 (five provided: Doyle, Alper, Ghadiali,
  Morgagni, Landolfi).
- PASS Figure color confirmation (B&W print, no color surcharge).
- PASS Conflicts of interest (negative — none).
- PASS Funding (negative — no external funding).

### Figures

- PASS Figure count 2 ≤ 4.
- PASS Figure format TIFF.
- PASS Combination-halftone resolution 600 dpi (meets AMHP minimum).
- (See WARN-1 for color-mode concern.)

### Author page

- PASS All required elements present: title, running head, author name/
  degrees, affiliations (numbered), ORCID, corresponding-author contact
  (email + postal), ICMJE contributions, affiliations-where-work-performed,
  acknowledgements, COI, funding, data/software availability.

---

## Action punch-list (before submission)

In strict order, durable-first:

1. [ ] **Edit `docs/manuscript.md`:**
   a. Trim abstract to ≤ 250 words (cut the "therefore the highest-leverage
      empirical refinement target" clause or equivalent).
   b. Update the word-count line at `manuscript.md:7` to match the new
      counts (`body N · abstract M · references ~24 · tables 4 · figures 2`).
   c. Remove refs 23, 24, 25 from the reference list. Renumber 26 → 23
      (Moayedi), 27 → 24 (Oshima). Update all `²⁶` and `²⁷` superscript
      callouts accordingly.
   d. Replace the overlapping keywords: drop "middle ear barotrauma" and
      "hypobaric chamber"; add "Eustachian tube dysfunction" and "altitude
      training."

1a. [ ] **Edit `docs/cover_letter.md`:**
   a. Replace reviewer 1 (Doyle — deceased) with Stephen Chad Kanick, PhD
      (Thayer School, Dartmouth). Exact diff in
      `2026-04-18_reviewer_verification_checklist.md` §"Edit 1".
   b. Fix reviewer 4 first name: "Francesco Morgagni" → "Fabio Morgagni".
   c. Fix reviewer 5 first name: "Andrea Landolfi" → "Angelo Landolfi".

2. [ ] **Verify and expand "et al." references** (refs 11, 16, 26/23,
   27/24 after renumbering) — PubMed-fetch full author lists; expand any
   with ≤ 6 authors.

3. [ ] **Re-render figures in grayscale:** open each TIFF, convert to
   8-bit grayscale, flatten alpha against white, save at 600 dpi TIFF with
   LZW compression. Re-run the TIFF-header probe to confirm
   `photometric=1` (BlackIsZero) and `samples=1`.

4. [ ] **Generate submission `.docx`:** pandoc-convert `docs/manuscript.md`
   to Word with double-spacing, page numbers, ragged right, table-per-page
   breaks, and a page break before "## Figure captions."

5. [ ] **IRB/ethics memo:** secure from DIMAE the institutional board
   memo confirming de-identified-registry approval of the FAC cohort; save
   as `docs/submission/dimae_ethics_memo.pdf`. Upload as supplementary.

6. [ ] **Sign the four forms:** Author Checklist, Copyright Release, COI
   (× N authors; here N = 1), Color-Surcharge form SKIPPED (B&W print).
   Save the three signed PDFs under `docs/submission/forms/`.

7. [ ] **Verify reviewer emails** (see companion checklist).

8. [ ] **Portal upload** — follow `2026-04-18_upload_playbook.md`.

9. [ ] **PDF proof review** inside Editorial Manager before hitting
   Submit.

10. [ ] **Submit.** Save the AMHP manuscript ID from the acknowledgment
    email in `docs/submission/manuscript_id.txt`.

11. [ ] **GitHub Release** tag `v2.2.1-manuscript`.
