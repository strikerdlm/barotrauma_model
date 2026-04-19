# Phase 1 Reconciliation — FAC 2010–2020 observed prevalence vs. AMHP calibration anchor

**Date:** 2026-04-19
**Dataset:** `docs/Cohort FAC/2010_2020/Barotrauma.xlsx` (257 cases, de-identified as `phase1_2010_2020_tidy.csv`)
**Denominator:** 6,565 chamber exposures 2010–2020 — author-attested in the Correa/Jaimes 2022 DIMAE draft Methods section. **Requires Diego's confirmation** on three open axes before this doc hardens (see §5).

---

## 1. Headline estimate

**FAC-only clinical barotrauma, 2010–2020:** **n = 161 / N = 6,565 = 2.45% per-exposure** (Wilson 95% CI 2.11 – 2.86%). Projected 3-exposure career rate **7.18%** under an independence assumption.

This is the estimate a peer reviewer at *Aerospace Medicine and Human Performance* or *Undersea and Hyperbaric Medicine* would accept as the calibration anchor: strict clinical definition (BAROTRAUMA lesion only), military cohort restricted to the Colombian Aerospace Force, and a published per-exposure denominator.

The **broader operational signal** — the number the DIMAE clinical team sees — is 257 / 6,565 = 3.91% (Wilson 95% CI 3.47 – 4.41%). The extra 96 cases are sub-clinical ear blocking (45), O₂-induced aerotitis (22), and 27 foreign/non-FAC cases plus 2 non-barotrauma events. Both numbers belong in the manuscript; the strict one anchors calibration, the broader one describes day-to-day clinical workload.

---

## 2. Strategy comparison (`phase1_prevalence_summary.csv`)

| Strategy | n | p per-exposure | Wilson 95% CI | Career rate at 3 exposures |
|---|---:|---:|---:|---:|
| Any ENT event, all-comers (2020 draft paper's headline) | 257 | **3.91%** | 3.47 – 4.41% | 11.29% |
| Clinical barotrauma, all-comers | 186 | 2.83% | 2.46 – 3.26% | 8.26% |
| Barotrauma + O₂ aerotitis, all-comers | 208 | 3.17% | 2.77 – 3.62% | 9.21% |
| FAC-only, any ENT event | 226 | 3.44% | 3.03 – 3.91% | 9.98% |
| **FAC-only, clinical barotrauma (recommended anchor)** | **161** | **2.45%** | **2.11 – 2.86%** | **7.18%** |
| Student-only, clinical barotrauma | 164 | 2.50% | 2.15 – 2.90% | 7.31% |

**Caveat on "FAC-only" and "student-only" rows:** the 6,565 denominator from the 2020 draft paper is all-comers (Colombian military + foreign + civilian contractors). Using a FAC- or student-only numerator against an all-comers denominator **underestimates** the FAC-only / student-only rate. The correct ratios would need the numerator's matching denominator, which the draft paper does not break out. If FAC accounts for ~95% of exposures (226/257 of cases), the bias is small (~5%) and the headline holds within the CI. If FAC accounts for a smaller share, the true FAC-only per-exposure rate is higher than 2.45%.

---

## 3. Comparison with the AMHP v2.2.1 manuscript's calibration target

The pre-submission AMHP manuscript (`docs/manuscript.md` §2.7 Calibration) states:

> "The calibration target uses the FAC DIMAE 10-year cohort (5.8% career barotitis prevalence), reconciled to a per-exposure rate of 2.0% via an assumed three career exposures: 1 − (1 − 0.02)³ ≈ 5.88%."

**Observed vs. manuscript:**

- Manuscript per-exposure: **2.00%**.
- Observed per-exposure (FAC clinical barotrauma): **2.45% (95% CI 2.11 – 2.86%)**.
- The AMHP 2.00% sits **0.1 pp below the lower edge of the observed Wilson 95% CI** (2.11%).

- Manuscript career (3 exposures): **5.8%**.
- Observed career at 3 exposures (FAC clinical barotrauma): **7.18% (implied range 6.15 – 8.35%)** via (1 − (1−p)³) using the Wilson bounds.

The manuscript anchor is ~20% lower than the FAC observation across every definition that plausibly maps to "Teed I+ clinical barotrauma in the FAC cohort." This is within peer-review-tolerable range for a calibration target — many physics-informed MEB papers cite per-exposure rates ranging 1.5 – 4% across different cohorts — but it is **not inside the Wilson 95% CI**, which is a reviewer-surfacable discrepancy.

**"Implied exposures per career" under AMHP's 5.8% is an algebraic identity, not a measurement.** If the same per-exposure rate p and an independent-exposures assumption both hold, then `1 − (1−p)ⁿ = 0.058` gives n ≈ 2.1–2.4 for the plausible p range. This does **not** imply Diego's calibration assumed 2.1–2.4 exposures; it's a consistency check between two summary statistics. Real career exposures are correlated (same anatomy, same ET function, same career-stage URI environment), so the independence assumption inflates the implied n.

---

## 4. Decision posed to Diego for the AMHP submission window

The AMHP manuscript has not yet been submitted. The portal-upload step under `HOW_TO_CONTINUE.md §1` step 3 is still pending on forms + IRB + reviewer email verification. That leaves a window to update §2.7 before upload.

**Option 4.1 — Keep the manuscript as-is (2.0% / 5.8%)** and treat the FAC cohort paper as the source of the refined number. Acknowledge in a post-publication addendum if needed. Defensible because the 5.8% career is within the "same order" of the observed 7.18% and the calibration procedure is transparent.

**Option 4.2 — Update §2.7 with the observed FAC-only clinical barotrauma rate** before submission. Replace the current sentence with:

> "The calibration target uses the FAC DIMAE 10-year cohort (2010–2020; n = 161 FAC clinical barotrauma events in 6,565 chamber exposures; per-exposure rate 2.45%, Wilson 95% CI 2.11 – 2.86%; projected 3-exposure career rate 7.18%). Hazard constants were re-bisected against this target …"

This requires:
- Re-running `python -m barotrauma.v2.calibration --target-barotitis 0.0245 --save` to regenerate `barotrauma/v2/calibrated.json` against the updated target.
- Verifying all v2 tests still pass against the new calibration (the ±5% regression test on the Groth fixture should not fire because the aperture model's gradient is unchanged — only the per-event hazard constant changes).
- Updating Table II in `docs/manuscript.md` with the new target + achieved values.
- Updating the abstract's "0.2 percentage points" claim (the achieved vs. target spread will differ).
- Re-reading the abstract word count after the edit (already at 248; any change must keep it ≤ 250).

**Recommendation: Option 4.2**, done as a single focused commit before portal upload. Under Option 4.1, the AMHP manuscript ships with a known-low anchor and a reviewer asking "why 5.8% not 7.18%" would surface the FAC cohort paper's numbers *before they're published*, which is a bad look.

---

## 5. Open items — Diego's institutional knowledge needed

The 2020 draft paper is single-sourced for all three of these. A 5-minute conversation with the Correa/Jaimes team would close each.

**Q5.1 — Does 6,565 count exposures (person-flights) or unique individuals?**
- If exposures: per-exposure 2.45% is defensible.
- If unique individuals: the actual per-exposure rate is *lower* (the same 161 numerator against a larger unique-individual-equivalent exposure count), and the career number should be read directly as 2.45%, not as (1-q)³.

**Q5.2 — FAC vs. non-FAC split of 6,565.**
- The case-level data shows 226/257 (88%) of cases are FAC. If 6,565 has the same ~88% FAC share, FAC-only denominator is ~5,777 and FAC-only clinical barotrauma per-exposure is 161/5,777 = 2.79%.
- If FAC share of exposures is lower (e.g. 70% because non-FAC run batch training), the true FAC rate is higher.

**Q5.3 — Student vs. instructor split of 6,565.**
- 214 (83%) of cases are students. Instructors fly the chamber ~5–10× per year for annual refresh; students fly 1–3 times total across a career. If 6,565 includes instructor repeat exposures, the per-student-per-career rate differs substantially from the per-exposure rate.
- The AMHP model targets students. If the 6,565 is all-comers and we restrict numerator to students (164 of 186 = 88%), the student-only rate using an inflated denominator is 2.50%.

**Q5.4 — Year-by-year denominator distribution.**
- The 2010–2019 case count rose from ~7–20/year in 2010–2011 to 44 in 2019 (with 2020 dropping to 3, likely COVID chamber closure). Whether the denominator grew in parallel (cohort expansion) or stayed flat (actual rising incidence) materially changes the story. A per-year table was computed and **intentionally excluded** from the summary CSVs because the uniform-denominator assumption is indefensible.

**Q5.5 — Sex encoding confirmation.** Verified from the old `base de datos barotrauma.xls` `general` sheet row 3 headers: columns 8 and 9 are "MAS" and "FEM" as separate indicators. The clean `Barotrauma.xlsx`'s `Genero` column collapses these to 1 = male / 0 = female. Confirmed; no change.

---

## 6. Data-quality notes for the Methods section of the FAC cohort paper

**TEED-grade reporting completeness:** of 186 clinical barotrauma cases, only **16 (8.6%) carry an explicit Teed grade** (I through V). The remaining 170 are `BAROTRAUMA` without a grade field. Default-classifying these as Teed I (mild) preserves the published-comparable numerator but introduces a grading-distribution bias: the paper cannot reliably report the Teed I / II / III / IV / V ratio from the current registry. This is a reportable limitation and a future-cohort improvement target.

**Date completeness:** 115 of 257 cases (45%) have full date `DD/MM/YYYY`. The remaining 142 (55%) have year-only (`00/00/YYYY`). Year-level analysis is valid for all 257; quarter or month-level trend analysis is valid only on the 115-case subset. The 2020 draft paper's "Por_trimestre" (per-quarter) column is NaN for 113 of 257 (44%) rows, matching this limitation.

**Altitude at onset:** 73 of 257 (28%) carry `N.A.` or null in the `Altura` column; 26 of the 184 reported values are "10000" ft (14% of reported), suggesting chamber operators sometimes record the profile's nominal peak (10,000 ft for IV-A) rather than the altitude at symptom onset. This limits the utility of altitude-onset analysis unless manually cleaned against the `Segmento` column (DESCENSO / TIERRA / TARDIO etc.).

**Multiple-lesion cases:** 22 of 257 (8.6%) carry "AEROTITIS POR OXIGENO" — a distinct pathology from pressure-differential barotrauma (Freon-induced middle-ear irritation from O₂ mask use). Three cases have mixed labels (e.g. "AEROTITIS POR OXIGENO BAROTRAUMA GI"). These were classified to `o2_aerotitis` in the tidy CSV and excluded from the clinical-barotrauma anchor. For the FAC paper, they deserve their own section (O₂-associated aerotitis is a separate literature).

---

## 7. Next action — what Phase 1 is blocked on

**Blocked on Diego:**
1. Answers to Q5.1 – Q5.4 above.
2. Decision on Option 4.1 vs. 4.2 for the AMHP §2.7 update.

**Not blocked — can proceed immediately:**
- Phase 2 — 2025–2026 preflight + director-log structured extraction (independent of Phase 1 reconciliation).
- TM-displacement subplot on the v2 dashboard (fully independent).
- Drafting the FAC cohort paper Results section using the strategy-comparison table above as a placeholder; refine once Q5.1–Q5.4 land.

---

## Appendix — outputs written

- `phase1_2010_2020_tidy.csv` — 257 rows, 18 cols, de-identified (no Cédula, no name, no email, age bucketed to 5-year bands, top-10 units retained).
- `phase1_prevalence_summary.csv` — 6 numerator strategies × {n, p, Wilson 95% CI, 3-exposure career projection}.
- `phase1_demographics.csv` — 57 rows covering role, sex, age-bucket, entity, chamber profile, segment-at-onset, lesion category, top-5 specialty, top-10 unit, and per-year numerator distribution.
