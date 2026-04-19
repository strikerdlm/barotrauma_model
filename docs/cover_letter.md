# Cover Letter — AMHP Submission

**To:** David G. Newman, AM, MBBS, DAvMed, MBA, PhD — Editor-in-Chief
*Aerospace Medicine and Human Performance*
Aerospace Medical Association
AMHPJournal@asma.org

**From:** Diego L. Malpica, MD
Dirección de Medicina Aeroespacial (DIMAE), Fuerza Aeroespacial Colombiana
Bogotá, Colombia
Email: dlmalpica@yahoo.com · ORCID: [0000-0002-2257-4940](https://orcid.org/0000-0002-2257-4940)

**Date:** 2026-04-18

**Manuscript title:** Physics-Informed Middle Ear Barotrauma Risk for Hypobaric Chamber Training
**Article type:** Research Article
**Running head:** PHYSICS-INFORMED MEB MODEL

---

Dear Dr. Newman,

I am submitting the enclosed Research Article, "Physics-Informed Middle Ear Barotrauma Risk for Hypobaric Chamber Training," for consideration at *Aerospace Medicine and Human Performance*.

The manuscript presents a physics-informed, pathophysiology-aware extension of the canonical Kanick-Doyle 2005 middle-ear-pressure-regulation model specifically for hypobaric-chamber training at 1,000–10,000 ft·min⁻¹ descent rates. The novelty lies in four additions not present in any prior physics-informed middle-ear-barotrauma model: (i) a continuous descent-side aperture-collapse function that resolves the Hagen-Poiseuille r⁴ lumen-compression physics Kanick-Doyle treats only as a binary lock; (ii) a six-state temporal URI modifier table that encodes controlled rhinovirus-challenge data into per-descent relative-risk multipliers; (iii) a four-state Patulous ET model that flips Kanick-Doyle's rupture-protective prediction to high-risk under inflammation; and (iv) three-threshold cumulative-hazard scoring calibrated to the Colombian Aerospace Force 10-year chamber training cohort and externally validated on three independent Italian Air Force cohorts (Morgagni 2010, Morgagni 2012, Landolfi 2009).

### Originality and prior publication

This manuscript has not been submitted or published elsewhere, in whole or in part. It is not derived from a thesis or dissertation. No part of the work has been posted to any preprint server.

### Author approval and authorship

I am the sole author and have read and approved the final manuscript. Per the International Committee of Medical Journal Editors (ICMJE) authorship criteria: I conceived the study, designed the extensions, implemented the software, performed the analyses, and wrote the manuscript.

### Statistical expertise

All statistical computations — binomial Wilson 95% credible intervals for external-validation benchmarks, Saltelli-Sobol sensitivity estimators, log-space bisection calibration, and the Approximate Bayesian Computation Sequential Monte Carlo sampler — were implemented and executed by the author in Python 3.11 with NumPy 1.26 and SciPy 1.11, following published formulations (Toni 2009 for ABC-SMC; Saltelli 2010 for Sobol estimators). The author holds an MD and has prior experience with quantitative physiological modeling; the open-source codebase with 109 automated tests provides full analytical reproducibility.

### Generative AI disclosure

No generative AI writing tools were used in the preparation of the manuscript. An AI-assisted software-engineering assistant (Claude) supported the implementation of the Python model, following author-directed specifications and research briefs; all scientific content, literature synthesis, clinical interpretation, and manuscript prose are the author's own.

### Figures

The submission includes 2 figures (descent-rate sensitivity curves; Sobol total-order sensitivity bar chart). Both figures are intended for **B&W print** (no color charges requested). Figure files will be uploaded separately as TIFF at ≥ 600 dpi (combination halftone) and ≥ 1,200 dpi (line art) per AMHP requirements.

### Conflicts of interest

The author declares no conflicts of interest, financial or otherwise.

### Funding

No external funding supported this work. All software and data analysis were performed on personally-owned computing equipment.

### Suggested reviewers

1. **Stephen Chad Kanick, PhD**
   Thayer School of Engineering, Dartmouth College
   Hanover, NH, USA
   Rationale: First author of the canonical Kanick-Doyle 2005 mathematical model (*J Appl Physiol* 98:1592–1602) that this manuscript extends. Quantitative biomedical engineering background (Google Scholar h-index 31+). No coauthorship with the author.

2. **Cuneyt M. Alper, MD**
   Children's Hospital of Pittsburgh; Department of Otolaryngology
   Pittsburgh, PA, USA
   Rationale: Lead author of Alper 2020 (PMID 32176133) paired pre/post-BDET dataset and Alper 2011 (PMID 21271597) mastoid-volume data, both of which parameterize our priors. No coauthorship with the author.

3. **Samir N. Ghadiali, PhD**
   The Ohio State University, Department of Biomedical Engineering
   Columbus, OH, USA
   Rationale: Author of the 2010 and 2019 Eustachian-tube FEM papers whose mechanical framework motivates our v2.2 muscle-mechanics extension. No coauthorship with the author.

4. **Fabio Morgagni, MD**
   Italian Air Force, Experimental Flight Centre (Pratica di Mare)
   Pomezia, Italy
   Rationale: Author of the Morgagni 2010 and 2012 cohorts used for external validation. Independent of the Colombian Aerospace Force data and of the author.

5. **Angelo Landolfi, MD**
   Italian Air Force
   Rome, Italy
   Rationale: Author of Landolfi 2009 (PMID 20027855), one of the three Italian Air Force external-validation cohorts. No coauthorship with the author.

Current institutional emails for suggested reviewers will be provided through the Editorial Manager portal fields at submission.

---

I look forward to the editorial office's consideration. The manuscript, figures, required forms, and author page are submitted through Editorial Manager as separate files per AMHP formatting requirements.

Sincerely,

**Diego L. Malpica, MD**
Dirección de Medicina Aeroespacial
Fuerza Aeroespacial Colombiana
Bogotá, Colombia
