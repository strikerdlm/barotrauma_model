# Phase 2 Summary — FAC 2025–2026 operational data analysis

**Date:** 2026-04-19
**Datasets analyzed:**
- `2025_2026/EVALUACIÓN MEDICA PRE VUELO DE LA CAMARA DE ALTURA.xlsx` — 1,046 preflight evaluation rows, Feb 3 2025 – Apr 14 2026.
- `2025_2026/FORMATO DE DIRECTOR MEDICO DE ENTRENAMIENTO FISIOLÓGICO CÁMARA HIPOBÁRICA.xlsx` — 98 chamber-run director logs, Feb 17 2025 – Apr 13 2026.

Both datasets PII-stripped to de-identified tidy CSVs under
`docs/Cohort FAC/analysis/` (no Cédula, no names, no emails, no
phones; age bucketed to 5-year bands; vital signs plausibility-filtered).

---

## 1. Headline findings

**Per-exposure clinical barotrauma rate, director-logged 2025–2026:**
**12 / 706 = 1.70%** (Wilson 95% CI 0.97 – 2.95%). Wilson CI overlaps
the 2010–2020 FAC-only clinical barotrauma rate (2.45%, 95% CI 2.11 –
2.86%) — i.e. **incidence is statistically unchanged over the 15-year
span**.

**Per-run medical emergency rate (any category), director-logged:**
**20 / 98 runs = 20.4%** (Wilson 95% CI 13.6 – 29.4%). ~1 in 5 chamber
runs triggers a medical-emergency log entry; 60% of those (12/20) are
clinical barotrauma, the rest are loss-of-consciousness recoveries
during hypoxia practice, abdominal barotrauma (aerocolia), anxiety
events, and one paradoxical-oxygen reaction.

**Preflight denial rate:** **23 / 1,004 = 2.29%** (Wilson 95% CI 1.53 –
3.41%) of evaluated submissions. The denied subset concentrates in
flags with clear clinical indication: recent_respiratory 29.0% denial
(9/31), ear_URI_history 15.2% (5/33), recent_dental 13.0% (3/23),
chronic_disease 12.5% (6/48). Lowest-yield flags (tobacco_alcohol_24h
5.3%, MSK injury 10.0%, GI 0%) are kept for population surveillance
rather than denial-decision utility.

**URI composite prevalence at preflight:** **62 / 1,046 = 5.93%**
(Wilson 95% CI 4.65 – 7.53%), pooling ear/URI history, recent
respiratory symptoms, and malaise/fever/fatigue. This is the baseline
against which the AMHP v2.2.1 manuscript's URI-state modifier table
(`docs/research_notes/02_uri_et_dysfunction.md`) should be validated.

---

## 2. Preflight evaluation — descriptive

### 2.1 Cohort (`phase2_preflight_tidy.csv`, n = 1,046)

- Role: **817 students** (78%), **229 internal observers** (22%). No
  explicit "instructor" category — likely mapped to the observer role.
- Rank tier: 643 SUBOFICIAL (non-commissioned, 61%), 403 OFICIAL
  (commissioned, 39%).
- Training type: 659 INICIAL (initial, 63%), 387 RECURRENTE (refresh,
  37%).
- Age distribution (5-yr bands): 25-29 (166), 30-34 (270), 35-39 (283),
  40-44 (153). Majority of cohort is 30-44 years old.
- Top specialties: TTV (230, transport crew), PILOTO (162, after
  case-fold normalization), TVR (65), APH (52 aeromedical evac), TIR
  (30), COPILOTO (33).
- Top aircraft: UH-60 (105), C-208 (66), HUEY II (53), King 350 (31),
  ATR (24), AC-47T (24).

### 2.2 Screening flag prevalence (`phase2_flag_prevalence.csv`)

| Flag | Positive/Total | Prevalence | Wilson 95% CI |
|---|---:|---:|---|
| chronic_disease_or_hosp | 52/1046 | 4.97% | 3.81 – 6.46% |
| ear_URI_history | 36/1046 | 3.44% | 2.50 – 4.73% |
| recent_respiratory | 34/1046 | 3.25% | 2.34 – 4.51% |
| cardiac_hypertension | 31/1046 | 2.96% | 2.10 – 4.18% |
| recent_dental | 27/1046 | 2.58% | 1.78 – 3.73% |
| recent_msk_injury | 22/1046 | 2.10% | 1.39 – 3.16% |
| tobacco_alcohol_24h | 21/1046 | 2.01% | 1.32 – 3.05% |
| GI_symptoms | 13/1046 | 1.24% | 0.73 – 2.11% |
| diving_altitude_48h | 10/1046 | 0.96% | 0.52 – 1.75% |
| claustrophobia | 6/1046 | 0.57% | 0.26 – 1.25% |
| malaise_fever_fatigue | 4/1046 | 0.38% | 0.15 – 0.98% |
| seizures_epilepsy | 2/1046 | 0.19% | 0.05 – 0.69% |
| anemia_bleeding | 1/1046 | 0.10% | 0.02 – 0.54% |

### 2.3 Denial rate by flag (`phase2_denial_by_flag.csv`)

Ranked by discriminatory power (denial % given a positive flag):

| Flag | Denied / Flag+ evaluated | Denial % | Wilson 95% CI |
|---|---:|---:|---|
| malaise_fever_fatigue | 3/3 | 100% | 43.9 – 100% |
| anemia_bleeding | 1/1 | 100% | 20.7 – 100% |
| recent_respiratory | 9/31 | 29.0% | 16.1 – 46.6% |
| ear_URI_history | 5/33 | 15.2% | 6.7 – 30.9% |
| recent_dental | 3/23 | 13.0% | 4.5 – 32.1% |
| chronic_disease_or_hosp | 6/48 | 12.5% | 5.9 – 24.7% |
| cardiac_hypertension | 3/29 | 10.3% | 3.6 – 26.4% |
| recent_msk_injury | 2/20 | 10.0% | 2.8 – 30.1% |
| tobacco_alcohol_24h | 1/19 | 5.3% | 0.9 – 24.6% |
| seizures_epilepsy | 0/2 | 0% | — |
| claustrophobia | 0/5 | 0% | — |
| GI_symptoms | 0/11 | 0% | — |
| diving_altitude_48h | 0/9 | 0% | — |

**Operational interpretation:** ear/URI/respiratory/malaise flags are
the high-yield screening criteria (20–100% denial given positive);
musculoskeletal / dental / GI / substance flags are low-yield and
appear to exist for population surveillance rather than operational
gating.

### 2.4 Vital signs at Bogotá preflight (`phase2_vitals_summary.csv`)

Baseline measurements at 2,640 m / 8,660 ft resting altitude. After
plausibility filtering (PAS 70–220, PAD 40–140, FC 30–180, SpO₂ 70–100;
drops 8 outlier rows likely from data-entry error such as PAS = 1240,
PAD = 890):

| Vital | n | Mean | SD | Median | IQR |
|---|---:|---:|---:|---:|---|
| PAS (mmHg) | 1,004 | 126.7 | 13.6 | 125 | 117–135 |
| PAD (mmHg) | 1,005 | 79.9 | 8.3 | 80 | 74–85 |
| FC (bpm) | 1,007 | 75.1 | 12.6 | 74 | 66.5–84 |
| SpO₂ (%) | 1,004 | 94.8 | 2.3 | 95 | 94–96 |

**Blood-pressure categorization** (ACC/AHA 2017 thresholds applied to
pre-flight single reading):
- normal (<120/<80): 260 (25%)
- elevated (120–129/<80): 144 (14%)
- stage-1 HTN (130–139/80–89): **379 (36%)**
- stage-2 HTN (≥140/≥90): 207 (20%)
- hypertensive crisis (≥180/≥110): 4 (0.4%)
- hypotension (<90/<60): 8 (0.8%)

**Over half (56%) of preflight readings are ≥130/80.** This could
represent white-coat effect, undermanaged hypertension in a military
cohort, or both. Publishable finding for a preflight-screening paper;
needs paired-measurement (office vs. ambulatory) validation before any
clinical conclusion.

**SpO₂ at 2,640 m** distribution:
- expected-for-Bogotá (93–96%): 711 (68%)
- high-normal (≥97%): 177 (17%) — possible supplemental oxygen or
  measurement artifact
- borderline (90–92%): 111 (11%)
- clinical hypoxia (<90%): 5 (0.5%)

The 94.8% mean is consistent with Beall-era reference values for
acclimatized Bogotá residents.

**Denied vs. apt comparison:** vitals distributions are essentially
superimposed — denial appears to be driven by the 14 yes/no flags and
free-text findings, not by vital-sign thresholds. Mean FC is slightly
higher in the denied group (80.5 vs. 74.9 bpm), consistent with
symptomatic respiratory/cardiac subgroups.

---

## 3. Director-logged chamber runs (`phase2_director_tidy.csv`, n = 98)

### 3.1 Run characteristics

- Time span: Feb 17 2025 – Apr 13 2026 (14 months).
- Profile type: 64 INICIAL (65%), 34 RECURRENTE (35%).
- Students per run: mean 7.2 (range 1–24). Total student-exposures
  across all runs: **706**.
- O₂ system pressures: initial mean 1,742 psi, final mean 1,613 psi
  (−129 psi average usage per run).
- Inter-service coordination checklist: Hyperbaric Chamber notified
  (Hospital Militar) + CATAM Sanidad notified populated for each run.

### 3.2 Emergency flags across 98 runs

- **Medical emergency "SI": 20 (20.4%)**, Wilson 95% CI 13.6 – 29.4%.
- Technical emergency "SI": 3 (3.1%).
- Safety operational event "SI": 16 (16.3%).

### 3.3 Medical event categorization (narrative regex + manual review)

Classified from free-text "Describa evento medico en el entrenamiento"
narratives. 19 narratives carried enough detail for classification;
one "NO" response is excluded.

| Category | n runs |
|---|---:|
| Barotrauma (clinical) | 12 |
| Other (headache, paradoxical O₂, sinus) | 5 |
| Hypoxia recovery not within training bounds | 2 |
| Claustrophobia / anxiety | 1 |

**12 clinical barotrauma events / 706 student-exposures = 1.70%
per-exposure (Wilson 95% CI 0.97 – 2.95%).** This is the most
defensible 2025–2026 per-exposure rate.

Narrative detail on the 12 barotrauma events (representative):
- **Descent onset dominates:** 9 of 12 describe onset at altitudes
  8,500 – 18,000 ft during descent, with Valsalva unsuccessful.
- **Altitude distribution at onset:** 8,500–8,600 ft (3), 10,900 ft
  (1), 11,000 ft (1), 12,265 ft (1), 13,000–13,400 ft (3), 18,000 ft
  (1), 25,000 ft (1).
- **Teed grades explicitly noted:** Teed 0 (1), Teed I "Grado I" (1),
  T2 (1). Most narratives describe otalgia + plenitud aural without
  explicit Teed grading — same limitation as the 2010–2020 cohort.
- **Interventions:** bounce + slow descent (≥5), supplemental O₂,
  antihistamine + pseudoephedrine per the FAC protocol (see 2020
  draft paper Table 3).
- **Antecedents flagged in narrative:** rinitis alérgica no
  controlada (uncontrolled allergic rhinitis, 1), plenitud ótica
  prevue (1), previous barotrauma (unspecified, several).

---

## 4. Denominator reconciliation — preflight submissions vs. director attendance

| Count | Value |
|---|---:|
| Preflight submissions total | 1,046 |
| Preflight evaluated (apt + denied) | 1,004 |
| Preflight apt (cleared to fly) | 981 |
| Director-logged runs | 98 |
| Director-reported student-exposures | 706 |

**Gap:** 981 cleared preflights vs. 706 director-reported student
attendances = **275 excess preflight submissions** (28% of cleared).
Likely drivers (cannot distinguish without raw name-level join):

- Observers filing preflight forms but not counted in
  "NUMERO DE ALUMNOS" on the director form.
- Students who submitted a preflight but did not fly (cancellation,
  last-minute schedule change).
- Multiple submissions per student across a training cycle.

**Unique-date overlap:** preflight dates 98, director dates 67, both
63. Preflight captured submissions on dates when no director run was
logged — possibly next-day rescheduled flights. **A director-run-level
join would require name-level matching** (blocked by C1 — PII).

**Implication for the cohort paper:** when reporting 2025–2026
per-exposure rates, use the director's "NUMERO DE ALUMNOS" total (706)
as the exposure denominator. This is consistent with the 2010–2020
paper's methodology of denominator = "tripulantes que asistieron a la
cámara."

---

## 5. Comparison with 2010–2020 cohort + AMHP manuscript anchor

| Source | n (barotrauma) | N (exposures) | Rate per exposure | Wilson 95% CI |
|---|---:|---:|---:|---|
| **2010–2020 FAC-only clinical barotrauma** | 161 | 6,565 | **2.45%** | 2.11 – 2.86% |
| **2025–2026 director-logged barotrauma** | 12 | 706 | **1.70%** | 0.97 – 2.95% |
| AMHP v2.2.1 manuscript target | — | — | 2.00% | (assumed) |

**Conclusion:** the 2025–2026 rate sits between the AMHP manuscript's
assumed 2.00% and the 2010–2020 observed 2.45%, with overlapping Wilson
CIs to both. **Incidence is statistically unchanged across the 15-year
span**; the short 14-month window and smaller 706 denominator widens
the CI but does not produce a trend finding.

**Pooled 2010–2026 estimate** (combining both numerators + denominators):
- Numerator: 161 + 12 = 173
- Denominator: 6,565 + 706 = 7,271
- Pooled per-exposure: 173 / 7,271 = **2.38%** (Wilson 95% CI 2.06 – 2.75%)
- Projected 3-exposure career: **6.97%**

The pooled estimate is the strongest calibration anchor for the FAC
cohort paper and for any update to the AMHP §2.7 target — it integrates
16 years of operational data under consistent institutional
methodology.

**Revised Option 4.2 for AMHP §2.7** (superseding the phase-1
suggestion with the pooled number):

> "The calibration target uses the FAC DIMAE cohort 2010–2026
> (n = 173 clinical barotrauma events in 7,271 chamber exposures;
> per-exposure rate 2.38%, Wilson 95% CI 2.06–2.75%; projected
> 3-exposure career rate 6.97%). Hazard constants were re-bisected
> against this target…"

---

## 6. Data-quality findings for the FAC cohort paper Methods section

### 6.1 Preflight form (1,046 rows)

- **Fitness-decision column contains multi-student copy-paste
  artifacts.** 200 of 1,046 rows carry the literal string
  `"SI\nSI\nSI\nSI\nSI"` — normalized to "apt" under the assumption
  that each row still represents one student and the multiple SIs
  reflect a Forms UI quirk. An alternative interpretation (each such
  row actually represents 5 students) was rejected because the
  remaining fields on those rows do not duplicate.
- **Vital-sign data entry error rate: 8 / 1,046 (0.8%)** — implausible
  values (PAS = 1,240 etc.) filtered out. No systematic bias, but
  suggests the preflight data entry would benefit from in-form range
  validation.
- **In-flight event capture is 3× less complete on the preflight form
  than on the director form** (4 events vs. 12 for the same time
  window). The preflight form should be retired as a primary event-
  capture channel; director narratives are the reliable source.
- **"EDAD" column contains 9 text-valued entries** (e.g. "MIGUEL ÁNGEL")
  — name overflow from adjacent columns. Filtered out by numeric
  coercion.

### 6.2 Director form (98 rows)

- **Teed grading is again sparse** — only 3 of 12 barotrauma
  narratives carry an explicit Teed grade (0, I, II). The other 9 are
  symptom-descriptive only. Same limitation as the 2010–2020 cohort;
  a structured Teed-grade field on the director form would close the
  gap.
- **Free-text narrative regex classification required manual review.**
  Three narratives had to be reassigned from the initial category
  (e.g. "Perdida del estado de consciencia" during hypoxia practice
  — a training outcome, not a medical emergency — but flagged "SI" on
  the emergency column). A structured event-type picklist (barotitis
  media / DCS / hypoxia / anxiety / other) would remove this
  ambiguity.

---

## 7. Implications and next steps

### 7.1 For the FAC cohort paper (Option A, per `analysis_plan.md §2.1`)

The 2010–2020 + 2025–2026 pooled cohort is publishable as-is for
Results. The Methods section should cite both data sources, the
denominator methodology from the 2020 draft, and the director-form
definition for 2025–2026. Limitations section covers the three
data-quality findings in §6 above.

Candidate title: *Sixteen-year incidence of ear barotrauma in a
hypobaric-chamber training program at 2,640 m baseline altitude:
FAC 2010–2026 cohort.*

### 7.2 For the AMHP v2.2.1 manuscript (portal upload still pending)

Strongest defensible calibration target: **pooled 2010–2026 FAC
clinical barotrauma per-exposure 2.38%** (Wilson 95% CI 2.06–2.75%;
career-3 projection 6.97%). See §5 for the §2.7 replacement text.

This requires: re-run `barotrauma.v2.calibration --target-barotitis
0.0238 --save`; update Table II (target/achieved); verify abstract
remains ≤ 250 words; update model_card.md calibration target. ~30 min
of focused work, one commit, before Editorial Manager upload.

### 7.3 For v2.3.0 URI modifier validation

The 2025–2026 operational URI-composite prevalence of 5.93% among
preflight submissions matches published controlled-rhinovirus-
challenge incidence studies within an order of magnitude, supporting
the AMHP URI-state modifier table qualitatively. A formal URI-day →
denial-rate validation (URI-day-windowed subgroup analysis) would
require case-level URI onset dates, which this preflight form does
not collect. Adding a free-text field for URI symptom onset date on
the preflight form would make this validation possible prospectively.

---

## Appendix — outputs written

- `phase2_preflight_tidy.csv` — 1,046 rows × 32 cols, de-identified,
  normalized fitness decision, plausibility-filtered vitals, screening
  flags as booleans, in-flight event category.
- `phase2_director_tidy.csv` — 98 rows × 14 cols, de-identified,
  medical-event category from narrative classification.
- `phase2_flag_prevalence.csv` — 14 screening flags × Wilson 95% CI.
- `phase2_denial_by_flag.csv` — per-flag denial-rate discrimination.
- `phase2_vitals_summary.csv` — descriptive stats for PAS/PAD/FC/SpO₂.
- `phase2_event_rates.csv` — director vs. preflight vs. any-emergency
  event rates with Wilson CIs.
- `phase2_date_reconciliation.csv` — per-date preflight vs. director
  student-count cross-reference (102 unique dates).
