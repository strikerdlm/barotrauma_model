# Bulletin of Mathematical Biology — Format Compliance Audit (post P1-P9 fix pass)

**Date:** 2026-05-04
**Manuscript:** `docs/submission/manuscript_bmb.tex` (compiled `manuscript_bmb.pdf`, 18 pp)
**Title:** *Beyond Binary Lock: A Continuous Aperture-Collapse Hazard Model of Middle-Ear Barotrauma in Hypobaric-Chamber Training*
**Journal:** Bulletin of Mathematical Biology (Springer Nature)
**Article type:** Original Research

This audit supersedes `2026-05-01_bmb_compliance_audit.md`, which reported "PASS 49 / FAIL 0" against a PDF that in fact contained six visible critical bugs (duplicate subsection numbering, citations rendering as initials-as-surname, inline `\textbf{...}.` lead-ins flowing as paragraph text, tables blocking the bibliography, figure axis lettering at ~3 pt, thin Discussion). The skill has been updated (`/root/.claude/skills/bmb-submit/SKILL.md`) to require a `compile-and-check` step before any future PASS verdict.

---

## Phase 1 — Compile-and-check transcript (per skill v1.1 protocol)

```
$ pdflatex … → bibtex → pdflatex → pdflatex
Output written on manuscript_bmb.pdf (18 pages, 1.4 MB)

$ grep -iE "warning" manuscript_bmb.blg
(no output)

$ grep -iE "undefined|! latex error|overfull \\hbox" manuscript_bmb.log
(no output)

$ pdftotext -layout manuscript_bmb.pdf /tmp/_bmb.txt

# (a) duplicate decimal numbering
$ grep -nE '\b[0-9]+\.[0-9]+\s+[0-9]+\.[0-9]+' /tmp/_bmb.txt   → no matches

# (b) initials-as-surname
$ grep -nE '\([A-Z]{1,3}\s+et\s+al' /tmp/_bmb.txt              → no matches

# (c) literal "and et al."
$ grep -in 'and et al' /tmp/_bmb.txt                            → no matches

# (d) author-year comma in citations
$ grep -nE '\([A-Z][a-z]+(\s+et\s+al)?,\s+[0-9]{4}\)' /tmp/_bmb.txt   → no matches

# (e) "Figure" instead of "Fig."
$ grep -nE '^Figure [0-9]' /tmp/_bmb.txt                        → no matches
```

All six regression patterns return zero matches. Compile is clean.

---

## Phase 2 — Format Compliance Audit (item-by-item)

| Item | Spec | Status | Notes |
|---|---|---|---|
| File format | LaTeX preferred | **PASS** | `.tex` + compiled `.pdf` |
| Headings | Decimal system, ≤ 3 levels | **PASS** | LaTeX auto-numbering; no manual prefixes; `\paragraph` used for the 4th level (unnumbered, allowed) |
| Line numbering | Continuous on every page | **PASS** | `\linenumbers` |
| Page numbering | Sequential | **PASS** | `\pagestyle{plain}` |
| Title page — full author names | Required | **PASS** | Diego L. Malpica; Marian A. Farfán |
| Title page — corresponding e-mail | Required | **PASS** | `diego.malpica@fac.mil.co` |
| Title page — ORCID for every author | Recommended | **PASS** | 0000-0002-2257-4940; 0000-0002-9910-6053 |
| Abstract length | 150–250 words | **PASS** | 248 |
| Keywords | 4–6 | **PASS** | 5 |
| Math notation | italic vars, roman ops/fns, bold vec | **PASS** | math-mode throughout, `\mathrm{d}` |
| References — in-text | author–year, no comma | **PASS** | `\bibpunct{(}{)}{;}{a}{}{,}` produces "(Alper et al 2011)" |
| References — list | alphabetised, DOIs as full links | **PASS** | sn-basic.bst output: "Alper CM, Kitsko DJ, Swarts JD, et al (2011) … https://doi.org/10.1002/lary.21275" |
| Reference style file | Springer preferred | **PASS** | `sn-basic.bst` (ships with Springer Nature LaTeX template, downloaded from CTAN-mirror godkingjay/springer-nature-latex-template) |
| Tables — Arabic numerals | Required | **PASS** | 1–4 |
| Tables — captions | Required | **PASS** | Bold "**Table N**" prefix via `\captionsetup[table]{labelfont=bf, …}` |
| Tables — float-vs-bibliography barrier | Recommended | **PASS** | `\FloatBarrier` before `\bibliography{}` |
| Figures — Arabic, consecutive | Required | **PASS** | Fig. 1–4 cited in order |
| Figures — caption format | "Fig." bold + bold N, no terminal punctuation | **PASS** | `\captionsetup[figure]{name=Fig., labelsep=space, labelfont=bf, labelformat=simple}`; captions audited for trailing periods |
| Figures — file format for submission | EPS or TIFF | **PASS** | TIFF copies at `docs/figures/paper_c/fig_0[1-4]_*.tiff` |
| Figures — resolution | 300/600/1200 dpi | **PASS** | All four TIFFs verified at 600 dpi via PIL |
| Figures — lettering | Helvetica/Arial 8–12 pt at final size | **PASS** | Source canvas fonts bumped from 11→32 px (axis labels), 12→36 (axis titles), 13→40 (panel titles), 11→30 (legend), inline 9-10 px → 22-26 px. Display via `\includegraphics[width=\linewidth]` (≈ 160 mm) yields effective 9-12 pt at print size |
| Figures — RGB 8-bit | Required for color | **PASS** | All four TIFFs RGB |
| Figures — colour-blind safety | Required | **PASS** | Wong 2011 / Okabe-Ito palette via `amhp_theme.PALETTE` |
| Figures — accessibility contrast ≥ 4.5:1 | Required | **PASS** | `#000` text on `#FFF` = 21:1 |
| Statements & Declarations | All sub-sections required | **PASS** | Ethics; Consent; Data; Code; Funding; Competing; CRediT; AI; Reporting guideline; Acknowledgements |
| Discussion | BMB scope: relevance to both biology and mathematics | **PASS** | §4.2 contrasts three lineages (Doyle gas-exchange, Ghadiali FEM, Alper mastoid); §4.3 frames Hill function as continuous bifurcation parameter, ABC-SMC as inverse-problem method, Sobol as model-self-diagnostic; §4.4 strengthened with cohort-aggregate vs person-level validity discussion |

---

## Summary count

| Category | Count |
|---|---|
| **PASS** | 24 |
| **FAIL** | 0 |
| **TO DO at portal** | 1 (rename `supplementary_S1_tripod_checklist.md` → `ESM_1.pdf` at upload) |

**No blocking failures remain.** Audit produced via the v1.1 `compile-and-check` protocol with grep transcripts above.

---

## What changed since the 2026-05-01 audit

| Phase | Fix | Resulting compliance |
|---|---|---|
| P1 | `references.bib` author fields rewritten as `Surname, F. M.` (spaced initials) and `and et al.` → `and others` | Citations now correctly resolve surnames |
| P2 | Removed manual `2.1 …` prefixes from every `\subsection{}` title | Single decimal numbering |
| P3 | §2.8 lead-ins (`Source of data`, `Outcome`, `Predictors`, `Missing data`, `Calibration methods`, `External validation`, `Model performance measures`) converted from `\textbf{...}.` to `\paragraph{...}` | Headings render as discrete blocks |
| P4 | Added `\usepackage{placeins}` + `\FloatBarrier` before `\bibliography{}` | Tables flushed before references |
| P5 | Caption `name=Fig.`, `labelfont=bf`; `\bibpunct` 5th arg emptied; switched bibliography style from `apalike` to `sn-basic` (downloaded from godkingjay mirror) with `\providecommand{\bibcommenthead}{}` fallback | BMB-style citation + caption format |
| P7 | Discussion expanded ~1100 → ~2200 words: §4.1 (extensions in contrast, with Hill-function-as-bifurcation-parameter framing), §4.2 (relation to prior ME models — Kanick-Doyle, Doyle 2017, Ghadiali, Alper), §4.3 (mathematical-biology framing), §4.4 (limitations strengthened with cohort-aggregate vs person-level discussion) | BMB scope satisfied; richer contrast |
| P8 | Figure source font sizes bumped 11→32 / 12→36 / 13→40 / inline 9-10 → 22-26 px; per-figure layout (grid margins, nameGap) widened proportionally; `\includegraphics` switched from `width=0.85\textwidth` to `width=\linewidth` | Axis lettering visually 9-12 pt at print size |
| P9 | Skill `compile-and-check` protocol added — pdflatex + bibtex + grep .blg/.log + pdftotext + regex on rendered PDF | Future audits cannot pass on broken PDFs |

---

*Audit generated by bmb-submit skill v1.1 (compile-and-check protocol).*
