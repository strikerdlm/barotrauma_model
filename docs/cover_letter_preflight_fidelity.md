# Cover Letter — AMHP Submission (Preflight-Fidelity)

**To:** David G. Newman, AM, MBBS, DAvMed, MBA, PhD — Editor-in-Chief
*Aerospace Medicine and Human Performance*
Aerospace Medical Association
AMHPJournal@asma.org

**From:** Diego L. Malpica, MD
Dirección de Medicina Aeroespacial (DIMAE), Fuerza Aeroespacial Colombiana
Bogotá, Colombia
Email: dlmalpica@yahoo.com · ORCID: [0000-0002-2257-4940](https://orcid.org/0000-0002-2257-4940)

**Date:** 2026-04-19

**Manuscript title:** Preflight medical-screening fidelity in hypobaric-chamber training: a Microsoft Forms-based surveillance study at 2,640 m baseline altitude
**Article type:** Research Article
**Running head:** FAC PREFLIGHT SCREENING FIDELITY

---

Dear Dr. Newman,

I am submitting the enclosed Research Article, "Preflight medical-screening fidelity in hypobaric-chamber training: a Microsoft Forms-based surveillance study at 2,640 m baseline altitude," for consideration at *Aerospace Medicine and Human Performance*.

### Principal novelty and relevance

Preflight medical-evaluation forms gate access to hypobaric-chamber training at every national aerospace-medicine program, but their internal discriminatory performance — per-flag prevalence, per-flag denial rate, area under the receiver-operating-characteristic curve, and cross-form event-capture concordance — is rarely reported. To our knowledge this is the first published operational audit of a preflight screening instrument for a military aircrew population trained at a high-altitude baseline (2,640 m / 8,530 ft), and the first to report ROC-AUC discrimination and structured free-text subcategorization alongside per-flag Wilson confidence intervals. The manuscript ends with five concrete v2 form-design recommendations (ETDQ-7 block, structured TEED/O'Neill field, de-identifiable trainee ID, etc.) that are directly actionable by peer programs.

### Relation to companion manuscripts

Two companion manuscripts are under concurrent review at AMHP: (a) a FAC 2010–2026 cohort incidence paper that reports the 2.38% pooled per-exposure barotrauma rate across the 16-year window, and (b) a physics-informed middle-ear-barotrauma model calibrated against that cohort. The present paper focuses on the preflight instrument's internal validity, a methodological angle that is out of scope for the cohort paper. Overlap is minimal and handled by mutual cross-reference; each paper stands alone editorially. I note the companion manuscripts for editorial awareness and any author-network handling.

### Originality and prior publication

This manuscript has not been submitted or published elsewhere, in whole or in part. The 2025–2026 preflight dataset is analyzed here for the first time. No part of the work has been posted to any preprint server.

### Author approval and authorship

I am the sole author and have read and approved the final manuscript. Per ICMJE authorship criteria: I designed the preflight Microsoft Forms instrument, curated the DIMAE dataset, de-identified and analyzed the data, and wrote the manuscript.

### Statistical expertise

All statistical computations — Wilson 95% confidence intervals, per-flag univariable sensitivity / specificity tabulation, multivariate logistic-regression fitness-decision modeling with ROC/AUC, Youden J statistic for the optimal operating point, and per-quarter time-course analysis — were implemented and executed by the author in Python 3.11 with NumPy 1.26, SciPy 1.11, and scikit-learn 1.3. The de-identified tidy CSV used for all analyses is publicly available at the companion repository.

### Generative AI disclosure

No generative AI writing tools were used for the scientific content or clinical interpretation. An AI-assisted software-engineering assistant (Claude) was used in de-identification of the raw Excel source, regex categorization of Spanish-language "Especifique" free-text entries (subject to manual review), and prose editing; all epidemiological analysis, clinical interpretation, and authorship decisions are the author's own.

### Figures

The submission includes 2 figures and 4 tables. Figure 1, a forest plot of per-flag preflight denial rates with Wilson 95% CIs and tier coloring; Figure 2, a receiver-operating-characteristic curve of the 14-flag battery fitted by penalised L2-ridge logistic regression and internally validated by 1,000-resample Harrell–Steyerberg bootstrap optimism correction, reporting both apparent and corrected discrimination. The optimism-corrected AUC is **0.813 (95% CI 0.717–0.859)** versus an apparent AUC of 0.858; at the Youden operating threshold (predicted probability 0.051) the optimism-corrected operating-point characteristics are **sensitivity 63.6%, specificity 91.9%, PPV 15.2%, NPV 99.1%, LR+ 6.5 (moderate-to-large), LR− 0.39 (small-to-moderate), DOR 17**. The 0.045-AUC and ~10-percentage-point sensitivity reductions from apparent to corrected quantify the residual optimism of the in-sample fit even after L2 shrinkage; this is the principled response to the cohort's low (1.6) events-per-variable ratio rather than refusing the multivariable analysis or reporting in-sample optimism as the headline. Per-flag univariable sensitivity, specificity, PPV, NPV, LR+ and LR− with Wilson and Katz log 95% CIs are tabulated in Table 4 and are not subject to the same optimism penalty (no fitted coefficients). The prediction-model component of the analysis is reported following the TRIPOD 2015 statement; methodological references for low-EPV penalised regression and bootstrap optimism correction are cited in the Methods (refs 23–26). Both figures use the colorblind-safe Wong palette and are greyscale-legible; **B&W print is requested** (no color charges). Figure files will be uploaded separately as TIFF at ≥ 600 dpi (combination halftone) per AMHP requirements.

### Ethics and data

The DIMAE de-identified-registry secondary analysis is covered by the institutional ethics-board memo that will be uploaded as supplementary material. Raw case-level data with Colombian national identifiers (Cédula), names, and institutional emails remain under DIMAE data-protection boundaries and are not shared; de-identified aggregate CSVs and analysis scripts are publicly available in the companion repository (https://github.com/strikerdlm/barotrauma_model, under `docs/Cohort FAC/analysis/`).

### Conflicts of interest

The author declares no conflicts of interest, financial or otherwise.

### Funding

No external funding supported this work. Analysis was performed on personally-owned computing equipment.

### Suggested reviewers

1. **Idit Nakdimon, MD** or **Oded Ben-Ari, MD**
   Israeli Air Force, Aeromedical Center
   Rationale: Author of Nakdimon 2022 (*Aerosp Med Hum Perform* 93(11):811; PMID 36309795), a methodology-matched chamber-training safety audit of the Israeli Air Force cohort. Direct methodological peer. No coauthorship with the author.

2. **Fabio Morgagni, MD**
   Italian Air Force, Experimental Flight Centre (Pratica di Mare), Pomezia, Italy
   Rationale: Author of the Morgagni 2010/2012 Italian AF chamber cohorts, who has reported on preflight-screening-associated incidence reductions (pre-screened vs. control subsets in Morgagni 2010). No coauthorship with the author.

3. **Olli H. Lindfors, MD, PhD**
   Department of Otorhinolaryngology, University of Helsinki and Helsinki University Hospital, Helsinki, Finland
   Rationale: First author of Lindfors 2021 (*Aerosp Med Hum Perform* 92:126–132; PMID 33468294), a commercial-pilot risk-factor survey methodologically analogous to our flag-discrimination analysis. No coauthorship with the author.

4. **Edward D. McCoul, MD, MPH** or **Cuneyt M. Alper, MD**
   Rationale: McCoul — author of the ETDQ-7 validation paper (Laryngoscope 2012;122:1137; PMID 22437662); Alper — chamber-barotrauma epidemiology program at Children's Hospital of Pittsburgh (PMID 32176133). Either would provide strong methodological review of the ETDQ-7 integration recommendation. No coauthorship with the author.

5. **Iván Nakdimon or equivalent USAFSAM preflight-screening expert** (to be confirmed by the editor) — institutional preflight instrument and chamber-training program at a comparable scale.

Current institutional emails for suggested reviewers will be provided through the Editorial Manager portal fields at submission.

### Opposed reviewers

None.

---

I look forward to the editorial office's consideration. The manuscript, figures, required forms, and author page are submitted through Editorial Manager as separate files per AMHP formatting requirements.

Sincerely,

**Diego L. Malpica, MD**
Dirección de Medicina Aeroespacial
Fuerza Aeroespacial Colombiana
Bogotá, Colombia
