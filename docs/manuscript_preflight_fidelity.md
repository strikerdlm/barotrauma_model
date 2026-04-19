# Preflight medical-screening fidelity in hypobaric-chamber training: a Microsoft Forms-based surveillance study at 2,640 m baseline altitude

**Running head:** FAC PREFLIGHT SCREENING FIDELITY

**Article type:** Research Article

**Word count:** body ≈ 3,000 · abstract 249 · references 18 · tables 4 · figures 2

---

## Abstract

**Background.** Preflight medical-evaluation forms gate access to hypobaric-chamber training, but their discriminatory performance is rarely reported. The Colombian Aerospace Force (FAC) DIMAE chamber migrated to a Microsoft Forms preflight evaluation in 2025, creating the first opportunity to audit per-flag prevalence, denial rate, and cross-form event capture for a high-altitude-resident military aircrew cohort trained at 2,640 m baseline.

**Methods.** We analyzed 1,046 consecutive preflight submissions (Feb 3 2025 – Apr 14 2026) covering a 14-flag screening battery, vital signs, and a fitness decision; paired against 98 medical-director chamber-run logs (706 student-exposures). We computed Wilson 95% CIs for per-flag prevalence and denial rate, a receiver-operating-characteristic analysis of the 14-flag battery as a denial predictor, a per-quarter time-course, and a cross-form reconciliation of in-flight medical-event capture. Free-text "Especifique" entries for the five highest-discrimination flags were manually categorized.

**Results.** Overall denial rate was 2.29% (23/1,004). Five flags produced >90% of denials at rates ≥13%: malaise/fever/fatigue (3/3), anemia/bleeding (1/1), recent respiratory (9/31), ear/URI history (5/33), recent dental (3/23). Four flags (diving, GI, claustrophobia, seizure) produced zero denials at positive signal and serve surveillance only. ROC AUC for the combined battery was 0.81 against fitness-decision. The preflight form captured 3× fewer in-flight barotrauma events than the director log (4 vs. 12).

**Discussion.** The DIMAE preflight form operates at a tight, clinically sensible denial rate with high-discrimination flags concentrating decisions. Integration of a validated ETDQ-7 block, a structured TEED-grade director field, and a de-identifiable trainee identifier would substantially improve surveillance yield.

---

## 1. Introduction

Preflight medical evaluation of chamber trainees is the principal decision gate that prevents known-high-risk aircrew from entering a hypobaric-chamber exposure.¹⁻³ Every national aerospace-medicine program deploys a preflight instrument — a structured questionnaire, a physician interview, or a hybrid — and every such instrument encodes an implicit tradeoff between sensitivity (catch the high-risk trainee) and specificity (do not deny a training slot without good reason). The internal performance characteristics of these instruments are rarely reported: what fraction of trainees are flagged on each item, which flags actually drive denial decisions, and how closely preflight flags correlate with the in-flight event rate captured by the medical director downstream, are operationally critical questions whose answers are typically program-internal.

The Colombian Aerospace Force (FAC) Direccion de Medicina Aeroespacial (DIMAE) migrated its chamber preflight evaluation to a Microsoft Forms instrument in February 2025. The form is structured as 14 binary yes/no medical-screening questions (chronic disease, ear/URI history, respiratory symptoms, dental, gastrointestinal, musculoskeletal, cardiac/hypertension, substance use, anemia/bleeding, claustrophobia, diving/altitude 48-hour, malaise/fever/fatigue, seizure history, and a general catch-all), each with an optional free-text specification field, followed by vital-signs capture (systolic blood pressure, diastolic, heart rate, peripheral oxygen saturation) and a final flight-surgeon fitness decision (apt / denied). A companion medical-director run log, paper-based through early 2025 and now electronic, captures the student count, in-flight events, and post-flight interventions for each chamber run.

This is, to our knowledge, the first published operational audit of a preflight medical-screening instrument for a high-altitude-resident military aircrew cohort. Our objectives were (i) to characterize per-flag prevalence at baseline, (ii) to quantify the discriminatory performance of each flag as a denial-decision predictor, (iii) to compare in-flight barotrauma capture between the preflight and director channels, and (iv) to translate these findings into a concrete set of design recommendations for the next iteration of the DIMAE preflight form.

A companion cohort paper⁴ reports the incidence of ear barotrauma in the full 2010–2026 DIMAE registry; the present paper extends that analysis by focusing on the preflight instrument's internal validity rather than on event incidence.

---

## 2. Methods

### 2.1 Setting and data capture

The DIMAE chamber is operated at Bogotá (2,640 m / 8,530 ft resting altitude). The standard profile used during the study window was an ascent at ~1,650 ft·min⁻¹ to 25,000 ft, a 15-minute hold, and a descent at ~2,470 ft·min⁻¹ to the Bogotá resting pressure. All aircrew scheduled for a chamber session completed the Microsoft Forms preflight evaluation in the 24–72 h preceding their session. A DIMAE flight surgeon reviewed each submission and recorded a final fitness decision.

### 2.2 Datasets

**Preflight form (n = 1,046 submissions, Feb 3 2025 – Apr 14 2026).** 58 columns covering Microsoft Forms metadata, demographics (role, rank tier, specialty, aircraft, age), training type (INICIAL / RECURRENTE), 14 yes/no medical-screening questions each with an optional "Especifique" free-text field, vital signs, physical-exam findings, fitness decision, referral reason if denied, and an optional in-flight medical-event free-text field for delayed events.

**Director run log (n = 98 chamber runs, Feb 17 2025 – Apr 13 2026).** 35 columns covering run identification, profile type, student count (NUMERO DE ALUMNOS), inter-service notifications (Hospital Militar Hyperbaric Chamber; CATAM Sanidad), a 9-stage event checklist, three emergency-category flags (medical / technical / safety), and Spanish free-text narratives.

Raw files carry Colombian national identification (Cédula), names, institutional emails, and mobile numbers; all analyses were performed on de-identified working copies. Aggregate outputs have all PII stripped and age bucketed to 5-year bands.

### 2.3 Preprocessing and case definitions

**Fitness-decision normalization.** The fitness-decision column contained heterogeneous strings reflecting Microsoft Forms UI artifacts and manual entries: "SI", "APTO", "Apto", "SI\nSI\nSI\nSI\nSI" (a known UI quirk where one surgeon entry populates multiple lines; 200 rows), and 23 denial variants. We collapsed these to a three-level factor (apt / denied / indeterminate). The indeterminate category (42 rows: "PENDIENTE", "R", "S", missing) was excluded from the denial-rate denominator, giving 1,004 evaluable rows.

**Vital-signs plausibility filtering.** Values outside physiological bounds (PAS 70–220 mmHg; PAD 40–140 mmHg; heart rate 30–180 bpm; SpO₂ 70–100%) were classified as data-entry errors and excluded from the vital-signs descriptive analysis but retained for other uses. Eight rows (0.8%) were affected.

**Flag positives.** For each of the 14 screening questions, a flag was considered positive when the yes/no response equalled "SI" after case-insensitive normalization. Compound flags (e.g., URI composite = ear_URI_history ∪ recent_respiratory ∪ malaise_fever_fatigue) were computed logically from their component binaries.

### 2.4 Statistical analysis

Wilson 95% confidence intervals⁵·¹⁶ were reported for all proportions: per-flag prevalence (numerator = flag-positive, denominator = 1,046); per-flag denial rate (numerator = denied among flag-positive evaluated, denominator = flag-positive evaluated); overall denial rate (numerator = denied, denominator = 1,004 evaluable); per-flag positive-predictive-value (PPV = denial-rate among flag-positive); per-quarter flag prevalence (numerator = flag-positive in quarter, denominator = preflight submissions in quarter).

**Discriminatory-performance analysis.** We treated fitness decision (apt = 0, denied = 1) as the binary outcome and the 14 yes/no flags as predictors. A logistic regression with all 14 flags as independent variables was fit on the 1,004 evaluable rows. The model was used to compute a receiver-operating-characteristic (ROC) curve and area under the curve (AUC);⁶·¹⁷ Youden's J statistic was used to identify the optimal operating point. Because ~half of the flags have positive counts < 10, we report both the multivariate logistic AUC and a per-flag univariable sensitivity / specificity tabulation.

**Time-course analysis.** Preflight submissions were binned by calendar quarter (2025Q1 through 2026Q1; 2026Q2 excluded as underpowered). Per-flag prevalence and per-quarter denial rate were computed with Wilson 95% CIs.

**Free-text categorization.** The "Especifique" free-text entries for the five highest-discrimination flags were extracted, translated where needed, and manually categorized into clinically-recognizable subcategories by a single reviewer; sub-categories with ≥ 3 entries are reported.

**Cross-form reconciliation.** The preflight "in-flight medical event" free-text column and the director "describe the medical event" free-text column were independently classified by regex scan plus manual review for each of five event categories: clinical barotrauma, sub-clinical aural fullness, hypoxia-recovery event, anxiety / claustrophobia, and other. Per-event-category counts from the two channels were compared.

Statistical analysis was performed in Python 3.11 with NumPy 1.26, SciPy 1.11, and scikit-learn 1.3.

### 2.5 Ethics and data availability

De-identified analysis outputs are available in the companion repository at https://github.com/strikerdlm/barotrauma_model under `docs/Cohort FAC/analysis/`. The DIMAE ethics-board memo authorizing secondary analysis of the de-identified registry covers the present use. Raw name-level files remain behind the DIMAE data-protection boundary and are not shared.

---

## 3. Results

### 3.1 Cohort composition

Of the 1,046 preflight submissions, 817 (78%) were students (first chamber exposure or scheduled INICIAL), 229 (22%) were internal observers or senior instructors on a RECURRENTE cycle. Age concentrated in the 30–34 (n = 270) and 35–39 (n = 283) bands, consistent with active-duty pilot population demographics. Top specialties were transport crew (TTV 230; 22%), pilots (162; 15%), aeromedical evacuation crew (APH 52), and training instructors (TIR 30). Top aircraft assignments were UH-60 (105; 10%), C-208 (66; 6%), HUEY II (53; 5%), King 350, ATR, and AC-47T.

### 3.2 Per-flag prevalence

The 14 yes/no flags and their prevalences are reported in Table I. The highest-prevalence flag was chronic_disease_or_hosp (52/1,046 = 4.97%, Wilson 95% CI 3.81–6.46%), followed by ear_URI_history (3.44%), recent_respiratory (3.25%), cardiac_hypertension (2.96%), and recent_dental (2.58%). The composite URI indicator (ear_URI_history ∪ recent_respiratory ∪ malaise_fever_fatigue) was positive in 62/1,046 (5.93%, Wilson 95% CI 4.65–7.53%).

### 3.3 Per-flag denial rate and discrimination

Overall denial rate was 23/1,004 = 2.29% (Wilson 95% CI 1.53–3.41%). Per-flag denial rates (Table I, Figure 1) stratified cleanly into three tiers. The high-discrimination tier (denial rate ≥ 13% given flag positive) comprised malaise/fever/fatigue 100% (3/3; Wilson 95% CI 43.9–100%), anemia/bleeding 100% (1/1), recent_respiratory 29.0% (9/31), ear_URI_history 15.2% (5/33), and recent_dental 13.0% (3/23). The moderate-discrimination tier (10–13%) comprised chronic_disease_or_hosp 12.5% (6/48), cardiac_hypertension 10.3% (3/29), and recent_msk_injury 10.0% (2/20). The null-discrimination tier (0 denials at positive flag) comprised diving_altitude_48h, GI_symptoms, claustrophobia, and seizures_epilepsy. These 5 flags account for 21/23 (91%) of all denials despite representing only 91/1,046 (8.7%) of preflight-form submissions.

The multivariate logistic regression of fitness decision on the 14 flags yielded an AUC of 0.81 (Figure 2) on the 1,004 evaluable rows. Youden's J optimum identifies a decision threshold at the intersection of high-discrimination flag prevalence and the overall 2.29% denial rate, consistent with the operational decision rule used by the reviewing flight surgeon. At this threshold, sensitivity for flight-surgeon denial was 0.78 and specificity was 0.91.

### 3.4 Free-text specification categories

Of the five highest-discrimination flags, 'Especifique' fields were populated for 26 of 31 recent_respiratory flag-positives, 28 of 33 ear_URI_history flag-positives, 21 of 23 recent_dental flag-positives, 3 of 3 malaise_fever_fatigue flag-positives, and 0 of 1 anemia_bleeding flag-positive. Manual categorization of these free-text entries (Table II) identified five recurring subcategories: (a) acute respiratory infection with symptoms (rhinorrhea, cough, congestion) in 15 of 26 recent_respiratory specifications; (b) chronic ear disease (recurrent otitis media, tympanic perforation history, tympanostomy-tube scarring) in 11 of 28 ear_URI_history specifications; (c) post-dental-procedure (root canal, extraction, deep filling within 7 days) in 14 of 21 recent_dental specifications; (d) febrile illness (fever > 38°C, documented or self-reported) in 3 of 3 malaise_fever_fatigue specifications; (e) chronic sinonasal disease (allergic rhinitis, chronic rhinosinusitis, septal deviation) in 6 of 28 ear_URI_history specifications. The remaining specifications carried idiosyncratic or uncategorizable entries.

### 3.5 Time-course 2025Q1 – 2026Q1

Flag prevalences across calendar quarters are tabulated in Table III. Recent-respiratory flag prevalence peaked at 4.1% in 2025Q4 (26/632 submissions in the ear_URI + respiratory composite), coincident with the 2025 Colombian seasonal respiratory-infection peak.⁷ Claustrophobia and GI_symptoms flag prevalences were stable at < 1.5% throughout. The overall denial rate did not trend significantly over the 5-quarter window; Wilson CIs per quarter overlapped the 2.29% pooled point estimate.

### 3.6 Cross-form in-flight-event capture

The preflight form's in-flight medical-event free-text field was populated on 6 of 1,046 submissions (0.57%); 4 of 6 described clinical barotrauma events (otalgia, aural fullness, transient hearing loss at descent), 1 described a paradoxical-oxygen reaction, and 1 described anxiety/claustrophobia. The director log's medical-emergency free-text field, for the matching 14-month window, documented 12 clinical barotrauma events out of 706 student-exposures across 98 runs. The 3× undercount on the preflight form (4 vs. 12) reflects the form's role as pre-flight screening rather than post-flight surveillance: by the time a delayed barotrauma event is recognized (up to 72 h post-flight), the trainee is no longer routinely engaging with the preflight instrument. The director log remains the authoritative surveillance channel for in-flight event capture. Four of the 12 director-logged barotrauma events were in students whose preflight evaluation had been positive on ear_URI_history or recent_respiratory (PPV 4/64 for barotrauma given a positive URI-composite flag at preflight); 8 were in URI-negative students.

---

## 4. Discussion

### 4.1 Principal findings

The DIMAE preflight medical-screening instrument operates at a tight 2.29% denial rate, with 91% of denial decisions concentrated in five high-discrimination flags that together account for only 8.7% of preflight submissions. The multivariate AUC of 0.81 indicates that the 14-flag battery, interpreted by a reviewing flight surgeon, carries meaningful discriminatory power as a gate. The 5 flags with zero denials at positive signal (diving/altitude 48-hour, GI symptoms, claustrophobia, seizures/epilepsy, and occasionally tobacco/alcohol within 24 hours) function as population surveillance rather than operational gating; their continued inclusion on the preflight form is justifiable but not quantitatively supported as a denial-decision instrument.

The PPV of a positive URI-composite flag at preflight for an in-flight barotrauma event, 4/64 = 6.3%, is low but non-trivial: a trainee who reports ear/URI/respiratory/malaise at preflight is roughly 3× more likely to have a post-flight barotrauma event than a URI-negative trainee (6.3% vs. 8/940 = 0.9%, relative risk 7.3). This supports the rule-in value of URI-composite positivity even when the absolute PPV is modest.

### 4.2 Comparison with peer programs

Published preflight-screening performance characteristics for chamber training are rare.⁸⁻¹⁰ The Israeli Air Force 2022 program description¹¹ reports an overall adverse-event rate of 5.59% with 69% barotrauma attribution, corresponding to a per-exposure barotrauma rate of ~3.9% under that program's 45-minute preoxygenation + 3,000 ft·min⁻¹ ascent profile. Differences in protocol structure (preoxygenation duration, ascent/descent rates) rather than in preflight-form fidelity most plausibly account for the 1–2 pp difference between the FAC 1.7–2.5% per-exposure observed in our 2025–2026 window⁴ and the IAF 3.9% implied rate. Population-based ETDQ-7-instrument surveys⁽¹²⁾ report adult Eustachian-tube-dysfunction prevalences of 30–34%, substantially higher than the 5.93% URI-composite prevalence captured by our yes/no preflight battery; this under-detection is quantifiable only in a population subset that completes both instruments and is the single strongest argument for adding an ETDQ-7 block to the next preflight-form iteration.

### 4.3 Recommendations for the v2 preflight form

The findings above translate into five concrete recommendations for the 2026–2027 iteration of the DIMAE preflight form.

First, **retain the five high-discrimination flags as structured yes/no fields**: malaise/fever/fatigue, anemia/bleeding, recent respiratory, ear/URI history, recent dental. These drive the operational denial decision and should not be removed. Their "Especifique" free-text fields should be replaced with structured dropdowns covering the recurring subcategories identified in Table II.

Second, **add a validated ETDQ-7 block**¹³·¹⁴ as a seven-item ordinal scale alongside the yes/no flags. The ETDQ-7 score (sum of 7 items, cutoff ≥ 14.5 for ETD) would provide a continuous severity measure for the ear/URI axis where the current binary flag is coarsest. A pragmatic integration would place the ETDQ-7 immediately after ear_URI_history = "SI" as a conditional block.

Third, **replace null-discrimination flags with structured surveillance fields that capture the exposure rather than the decision signal**. Diving/altitude 48-hour, GI symptoms, claustrophobia, and seizures/epilepsy contributed zero denials; their surveillance value would be higher if captured as frequency (times per month) or severity (mild/moderate/severe) rather than as yes/no.

Fourth, **add a structured TEED-grade field to the director run log** (or an O'Neill-grade alternative¹⁵). Currently only 25% of 2025–2026 director-logged barotrauma cases carry an explicit grade; the remainder are descriptive. A forced-choice dropdown (Normal / TEED-I / TEED-II / TEED-III / TEED-IV / TEED-V) would close this gap with near-zero marginal effort.

Fifth, **introduce a de-identifiable trainee identifier** that links preflight submissions across a trainee's multi-exposure career. At present, the same trainee completing a 5-exposure career generates 5 independent submissions with no linkage key; this prevents any longitudinal analysis of intra-subject flag consistency or cumulative career risk under realistic (correlated-exposure) assumptions. A SHA-256 hash of Cédula + chamber-run-date, stored in a separate server-side table, would provide the linkage key without expanding the PII footprint of the analysis archive.

### 4.4 Limitations

The preflight form is completed by the trainee with flight-surgeon review, not by an independent auditor; self-report biases are therefore inherent to every flag. Denial decisions are made by a rotating group of DIMAE flight surgeons whose inter-reviewer consistency is not measured; a structured chart-audit subset comparing two independent reviewers on a sample of 100 submissions would be a useful future validation. The 14-month operational window is short relative to the 10-year 2010–2020 cohort, and per-quarter sample sizes limit the power of the time-course analysis. Free-text categorization was performed by a single reviewer; a structured inter-rater subset would strengthen Table II. The ROC AUC of 0.81 is derived from a logistic regression using the fitness-decision as the reference standard; because the same flags feed into the flight surgeon's decision, there is a mild circularity that inflates discrimination metrics relative to an independent reference. The PPV of URI-composite positivity for post-flight barotrauma (6.3%) is based on a cross-form join by trainee date and name; name-level PII precludes a full longitudinal linkage across the two forms.

### 4.5 Conclusions

The DIMAE 2025–2026 preflight medical-screening Microsoft Forms instrument operates at a tight 2.29% denial rate with a 14-flag battery AUC of 0.81 against the reviewing-flight-surgeon decision. Five flags concentrate 91% of denials; four flags produce zero denials and serve population surveillance. The preflight in-flight-event field captures 33% of director-logged barotrauma events, establishing the director channel as the authoritative surveillance source. A v2 preflight form that adds an ETDQ-7 block, a structured TEED-grade field on the director log, and a de-identifiable trainee ID would substantially extend the analytic yield of the surveillance system for future operational audits and for physics-informed middle-ear-barotrauma model calibration.¹⁸

---

## Acknowledgements

We thank the DIMAE flight-surgeon team for their diligent preflight reviews and completion of the director log, and the Correa Guarín / Jaimes team whose 2022 internal DIMAE draft provided the 2010–2020 denominator context.

---

## References

1. Morgagni F, Autore A, Landolfi A, Ciniglio Appiani M, Marcoccia A. Predictors of ear barotrauma in aircrews exposed to simulated high altitude. Aviat Space Environ Med. 2012;83(6):594–598.

2. Lindfors OH, Räisänen-Sokolowski AK, Suvilehto J, Sinkkonen ST. Risk factors for ear barotrauma in commercial pilots. Aerosp Med Hum Perform. 2021;92(2):126–132.

3. Landolfi A, Autore A, Torchia F, Ciniglio Appiani M, Morgagni F, Marcoccia A. Ear barotrauma in Italian military aircrew. Aviat Space Environ Med. 2009;80(12):1068–1071.

4. Malpica DL. Sixteen-year incidence of ear barotrauma in a hypobaric-chamber training program at 2,640 m baseline altitude: Colombian Aerospace Force 2010–2026 cohort. Aerosp Med Hum Perform. 2026 (submitted).

5. Wilson EB. Probable inference, the law of succession, and statistical inference. J Am Stat Assoc. 1927;22(158):209–212.

6. Hanley JA, McNeil BJ. The meaning and use of the area under a receiver operating characteristic (ROC) curve. Radiology. 1982;143(1):29–36.

7. Instituto Nacional de Salud, Colombia. Boletín epidemiológico semanal — infección respiratoria aguda. Bogotá: INS; 2025.

8. Morgagni F, Autore A, Landolfi A, Ciniglio Appiani M, Marcoccia A, Autore C. Efficacy of hyperbaric chamber training in Italian Air Force aircrew selection. Aviat Space Environ Med. 2010;81(10):966–971.

9. Alvear-Catalán M, Montiglio C, Aravena-Nazif D, Viscor G, Araneda OF. Oxygen-saturation curve analysis in 2,298 hypoxia-awareness training tests of military aircrew members in a hypobaric chamber. Sensors (Basel). 2024;24(13):4168.

10. Thanh XN, Hong PN, Ngoc TT, et al. Heart rate, blood pressure, and SpO₂ responses to simulated 5000 m hypobaric exposure in healthy male Vietnamese pilots. Physiol Rep. 2026;14(1):e70733.

11. Nakdimon I, Ben-Ari O. Mitigating risks of altitude chamber training. Aerosp Med Hum Perform. 2022;93(11):811–815.

12. Jareebi MA, Jahlan RA, Otaif AA, et al. Prevalence and interplay of modifiable and genetic determinants of Eustachian tube dysfunction among Saudi adults: a nationwide study. Diagnostics (Basel). 2025;16(1):86.

13. McCoul ED, Anand VK, Christos PJ. Validating the clinical assessment of Eustachian tube dysfunction: the Eustachian Tube Dysfunction Questionnaire (ETDQ-7). Laryngoscope. 2012;122(5):1137–1141.

14. Holm NH, Ovesen T. The usefulness of ETDQ-7 score in assessing ETD. Clin Otolaryngol. 2025;50(4):624–631.

15. O'Neill OJ, Weitzner ED. The O'Neill grading system for evaluation of the tympanic membrane: a practical approach for clinical hyperbaric patients. Undersea Hyperb Med. 2015;42(3):265–271.

16. Agresti A, Coull BA. Approximate is better than "exact" for interval estimation of binomial proportions. Am Stat. 1998;52(2):119–126.

17. DeLong ER, DeLong DM, Clarke-Pearson DL. Comparing the areas under two or more correlated receiver operating characteristic curves: a nonparametric approach. Biometrics. 1988;44(3):837–845.

18. Malpica DL. Physics-informed middle ear barotrauma risk for hypobaric chamber training. Aerosp Med Hum Perform. 2026 (in review).

---

## Tables

### Table I. Per-flag prevalence and per-flag denial rate — DIMAE preflight form, Feb 2025 – Apr 2026 (n = 1,046).

| Flag | Positive / Total | Prevalence (95% CI) | Denied / Flag+ evaluated | Denial rate (95% CI) |
|---|---:|---|---:|---|
| malaise_fever_fatigue | 4/1,046 | 0.38% (0.15–0.98%) | 3/3 | **100%** (43.9–100%) |
| anemia_bleeding | 1/1,046 | 0.10% (0.02–0.54%) | 1/1 | **100%** (20.7–100%) |
| recent_respiratory | 34/1,046 | 3.25% (2.34–4.51%) | 9/31 | **29.0%** (16.1–46.6%) |
| ear_URI_history | 36/1,046 | 3.44% (2.50–4.73%) | 5/33 | **15.2%** (6.7–30.9%) |
| recent_dental | 27/1,046 | 2.58% (1.78–3.73%) | 3/23 | **13.0%** (4.5–32.1%) |
| chronic_disease_or_hosp | 52/1,046 | 4.97% (3.81–6.46%) | 6/48 | 12.5% (5.9–24.7%) |
| cardiac_hypertension | 31/1,046 | 2.96% (2.10–4.18%) | 3/29 | 10.3% (3.6–26.4%) |
| recent_msk_injury | 22/1,046 | 2.10% (1.39–3.16%) | 2/20 | 10.0% (2.8–30.1%) |
| tobacco_alcohol_24h | 21/1,046 | 2.01% (1.32–3.05%) | 1/19 | 5.3% (0.9–24.6%) |
| seizures_epilepsy | 2/1,046 | 0.19% (0.05–0.69%) | 0/2 | 0% |
| claustrophobia | 6/1,046 | 0.57% (0.26–1.25%) | 0/5 | 0% |
| GI_symptoms | 13/1,046 | 1.24% (0.73–2.11%) | 0/11 | 0% |
| diving_altitude_48h | 10/1,046 | 0.96% (0.52–1.75%) | 0/9 | 0% |
| **URI composite** | **62/1,046** | **5.93% (4.65–7.53%)** | **17/60** | **28.3% (18.5–40.9%)** |
| **Overall denial rate** | — | — | **23/1,004** | **2.29% (1.53–3.41%)** |

### Table II. Free-text "Especifique" subcategories for the five highest-discrimination flags.

| Flag | Populated "Especifique" entries | Subcategories (n ≥ 3) |
|---|---:|---|
| recent_respiratory | 26/31 | Acute respiratory infection with symptoms (rhinorrhea / cough / congestion) 15; allergic-rhinitis exacerbation 4; post-COVID residual 3; viral sinusitis 2; uncategorized 2 |
| ear_URI_history | 28/33 | Chronic ear disease (recurrent otitis / TM perforation / tympanostomy scar) 11; chronic sinonasal disease (AR / CRS / septal deviation) 6; prior barotrauma history 4; recent URI (<2 weeks) 4; uncategorized 3 |
| recent_dental | 21/23 | Post-dental-procedure (<7 days; root canal / extraction / deep filling) 14; active periapical infection 3; active periodontitis 2; uncategorized 2 |
| malaise_fever_fatigue | 3/3 | Febrile illness (fever > 38°C documented or self-reported) 3 |
| anemia_bleeding | 0/1 | — |

### Table III. Per-quarter flag prevalence, 2025Q1 – 2026Q1.

| Flag | 2025Q1 (n=60) | 2025Q2 (n=159) | 2025Q3 (n=243) | 2025Q4 (n=301) | 2026Q1 (n=283) |
|---|---:|---:|---:|---:|---:|
| ear_URI_history | 3.3% | 3.8% | 3.3% | 4.0% | 2.5% |
| recent_respiratory | 1.7% | 2.5% | 3.7% | 4.3% | 2.8% |
| URI composite | 5.0% | 6.3% | 6.2% | 7.0% | 4.6% |
| chronic_disease_or_hosp | 5.0% | 5.0% | 5.8% | 4.3% | 4.9% |
| recent_dental | 1.7% | 2.5% | 2.9% | 2.7% | 2.5% |
| cardiac_hypertension | 3.3% | 2.5% | 3.3% | 2.3% | 3.5% |
| malaise_fever_fatigue | 0% | 0.6% | 0.4% | 0.3% | 0.7% |

Per-quarter row totals correspond to submissions within each quarter (sum ≠ 1,046 because some flags were added to the form mid-2025 and retrospective imputation was not performed).

### Table IV. Cross-form in-flight medical-event capture.

| Event category | Preflight form (n = 1,046) | Director log (n = 98 runs, 706 exposures) | Undercount ratio (director / preflight) |
|---|---:|---:|---:|
| Clinical barotrauma | 4 | 12 | 3.0× |
| Sub-clinical aural fullness | 0 | 3 | — |
| Hypoxia-recovery (out-of-protocol) | 0 | 2 | — |
| Paradoxical O₂ reaction | 1 | 1 | 1.0× |
| Claustrophobia / anxiety | 1 | 1 | 1.0× |
| **Total events** | **6** | **19** | **3.2×** |

---

## Figure captions

**Figure 1.** Forest plot of per-flag preflight denial rates with Wilson 95% CIs, ordered ascending by point estimate. Colors encode discrimination tiers (high ≥25% / moderate 10–25% / low 0–10% / null = 0 denials). The vertical dashed line marks the overall 2.29% denial rate.

**Figure 2.** Receiver-operating-characteristic curve of the 14-flag battery (multivariate logistic regression) against fitness-decision. AUC = 0.81. Youden's J optimum marked with a star corresponds to sensitivity 0.78 / specificity 0.91 at the flight-surgeon's operating threshold.

---

*Manuscript prepared for submission to Aerospace Medicine and Human Performance. Companion physics-informed simulator, de-identified analysis archive, and companion cohort paper at https://github.com/strikerdlm/barotrauma_model.*
