# Cover Letter — Q1 Submission

**From:** Diego L. Malpica, MD (Corresponding Author, Principal Investigator)
Subdirectorate of Aerospace Sciences, Direction of Aerospace Medicine (DIMAE)
Colombian Aerospace Force (Fuerza Aeroespacial Colombiana)
Bogotá, Colombia
Email: diego.malpica@fac.mil.co · ORCID: [0000-0002-2257-4940](https://orcid.org/0000-0002-2257-4940)

**Co-author:** Marian A. Farfán, MD — Subdirectorate of Aerospace Sciences, Direction of Aerospace Medicine, Colombian Aerospace Force, Bogotá, Colombia.

**Date:** [TO BE COMPLETED on submission]

**Manuscript title:** Physics-Informed Middle Ear Barotrauma Risk for Hypobaric Chamber Training: A Computational Prediction Model Calibrated to the Colombian Aerospace Force Cohort and Externally Validated Against Italian Air Force Cohorts

**Article type:** Original Research (computational prediction-model development and external validation)

**Reporting guideline:** TRIPOD 2015

**Running head:** PHYSICS-INFORMED MEB MODEL

---

Dear Editor,

We are pleased to submit the enclosed Original Research article, "Physics-Informed Middle Ear Barotrauma Risk for Hypobaric Chamber Training," for consideration by the journal.

The manuscript reports the development and independent external validation of a physics-informed, pathophysiology-aware computational prediction model for per-exposure middle-ear barotrauma (MEB) risk during hypobaric-chamber training. The model extends the canonical Kanick-Doyle 2005 mathematical framework with four additions not present in any prior physics-informed MEB model: (i) a continuous descent-side aperture-collapse function that resolves the Hagen-Poiseuille r⁴ lumen-compression physics Kanick-Doyle treats only as a binary lock; (ii) a six-state temporal upper-respiratory-infection (URI) modifier table encoding controlled rhinovirus-challenge data into per-descent relative-risk multipliers; (iii) a four-state Patulous Eustachian-tube model that flips Kanick-Doyle's rupture-protective prediction to high-risk under mucosal inflammation; and (iv) a three-threshold cumulative-hazard score calibrated to the pooled Colombian Aerospace Force 2010–2026 hypobaric-chamber registry (n = 173 events in 7,271 exposures) and externally validated without refitting against three independent Italian Air Force cohorts (Morgagni 2010, Morgagni 2012, Landolfi 2009).

The study reports in accordance with the TRIPOD 2015 guideline for prediction-model development and external validation. The completed 28-item TRIPOD checklist is provided as Supplementary File S1. No machine-learning component is used in the deployed prediction pipeline.

### Originality and prior publication

This manuscript has not been submitted or published elsewhere, in whole or in part. It is not derived from a thesis or dissertation. No part of the work has been posted to any preprint server. The open-source simulator repository at <https://github.com/strikerdlm/barotrauma_model> accompanies the manuscript as a software artifact; the scientific content of the manuscript has not been previously published.

### Authorship and approval

Both authors meet all four ICMJE authorship criteria. Each author has read and approved the final version of the manuscript and agrees to be accountable for all aspects of the work. Contributions per CRediT:

- **D.L.M.** — Conceptualization; Methodology; Software; Validation; Formal analysis; Investigation; Data curation; Writing – Original Draft; Writing – Review & Editing; Visualization; Supervision; Project administration.
- **M.A.F.** — Methodology; Writing – Review & Editing.

### Ethics

The study underwent secondary-analysis ethics review by the Institutional Ethics Committee of the Direction of Aerospace Medicine (DIMAE), Colombian Aerospace Force. A waiver of informed consent was granted for retrospective analysis of de-identified operational registry data (reference [TO BE COMPLETED]). The study was conducted in accordance with the Declaration of Helsinki (2013 revision) and with Resolution 8430 of 1993 of the Colombian Ministry of Health.

### Statistical expertise

All statistical computations — binomial Wilson 95% confidence intervals, Saltelli-Sobol sensitivity estimators, log-space bisection calibration, and the Approximate Bayesian Computation Sequential Monte Carlo (ABC-SMC) sampler — were implemented and executed in Python 3.11 with NumPy 1.26 and SciPy 1.11, following published formulations (Toni 2009 for ABC-SMC; Saltelli 2010 for Sobol estimators). The open-source codebase with 109 automated tests provides full analytical reproducibility.

### Generative-AI disclosure

No generative AI writing tools were used in the preparation, writing, or editorial revision of the manuscript. An AI-assisted software-engineering assistant (Anthropic Claude) supported the implementation of the Python model under explicit author-directed specifications; all scientific content, literature synthesis, clinical interpretation, analytical design, and manuscript prose are the authors' own. No AI tool is listed or claimed as an author.

### Figures and tables

The submission includes 2 figures (descent-rate sensitivity curves; Sobol total-order sensitivity bar chart) and 4 tables. Figures are prepared for B&W print (no color charges requested) as TIFF at ≥ 600 dpi (combination halftone).

### Competing interests

The authors declare no financial or non-financial competing interests.

### Funding

No external funding supported this work. Institutional resources of the Direction of Aerospace Medicine (DIMAE), Colombian Aerospace Force, supported curation of the operational registry. The funders had no role in study design; collection, analysis, or interpretation of data; writing of the report; or the decision to submit the article for publication.

### Data and code availability

Aggregate cohort statistics required to reproduce the calibration are reported in the manuscript and in the accompanying model card. Individual-level registry records are institutional operational data and are not publicly available due to military institutional and personal data-protection constraints; de-identified aggregate extracts may be made available from the corresponding author upon reasonable request. The complete simulator is released open-source (MIT license) at <https://github.com/strikerdlm/barotrauma_model>; the tagged release `v2.2.1-manuscript` corresponds to the state described in this manuscript. A DOI-assigned archival snapshot will be deposited on Zenodo prior to publication.

### Suggested reviewers

1. **Stephen Chad Kanick, PhD** — Thayer School of Engineering, Dartmouth College, Hanover, NH, USA. First author of the canonical Kanick-Doyle 2005 mathematical model (*J Appl Physiol* 98:1592–1602) that this manuscript extends. No coauthorship with either author.

2. **Cuneyt M. Alper, MD** — Children's Hospital of Pittsburgh, Department of Otolaryngology, Pittsburgh, PA, USA. Lead author of Alper 2020 (PMID 32176133) paired pre/post-BDET dataset and Alper 2011 (PMID 21271597) mastoid-volume data, both of which parameterise our priors. No coauthorship with either author.

3. **Samir N. Ghadiali, PhD** — The Ohio State University, Department of Biomedical Engineering, Columbus, OH, USA. Author of the 2010 and 2019 Eustachian-tube FEM papers whose mechanical framework motivates our muscle-mechanics extension. No coauthorship with either author.

4. **Fabio Morgagni, MD** — Italian Air Force, Experimental Flight Centre (Pratica di Mare), Pomezia, Italy. Author of the Morgagni 2010 and 2012 cohorts used for external validation. Independent of the Colombian Aerospace Force data and of the authors.

5. **Angelo Landolfi, MD** — Italian Air Force, Rome, Italy. Author of Landolfi 2009 (PMID 20027855), one of the three Italian Air Force external-validation cohorts. No coauthorship with either author.

Current institutional emails for suggested reviewers will be provided through the submission portal fields.

### Opposed reviewers

None.

---

We believe this work will be of interest to the journal's readership because it (i) closes a regime gap in a 20-year-old canonical physiological model, (ii) reproduces operational-level cohort prevalence across two independent air forces without refitting, (iii) is released as an open-source simulator under a permissive licence with a full test suite, and (iv) directly addresses a modifiable, under-parameterised risk factor (URI) in a population where aviator medical fitness has operational consequences.

We look forward to the editorial office's consideration.

Sincerely,

**Diego L. Malpica, MD** (Corresponding Author, PI)
Subdirectorate of Aerospace Sciences
Direction of Aerospace Medicine (DIMAE)
Colombian Aerospace Force
Bogotá, Colombia
diego.malpica@fac.mil.co

**Marian A. Farfán, MD** (Co-author)
Subdirectorate of Aerospace Sciences
Direction of Aerospace Medicine (DIMAE)
Colombian Aerospace Force
Bogotá, Colombia
