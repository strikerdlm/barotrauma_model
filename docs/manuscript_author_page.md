# Author Page (Title Page)

(This file is the **Title Page**. It is kept separate from the depersonalized `manuscript.md` for journals that require blinded peer review.)

---

## Title

Beyond Binary Lock: A Continuous Aperture-Collapse Hazard Model of Middle-Ear Barotrauma in Hypobaric-Chamber Training

## Running head

APERTURE-COLLAPSE MEB HAZARD MODEL

## Authors

**Diego L. Malpica, MD**<sup>1,2,\*</sup> (Principal Investigator)
**Marian A. Farfán, MD**<sup>1</sup> (ORCID: [0000-0002-9910-6053](https://orcid.org/0000-0002-9910-6053))

<sup>1</sup> Subdirectorate of Aerospace Sciences, Direction of Aerospace Medicine (DIMAE), Colombian Aerospace Force (Fuerza Aeroespacial Colombiana, FAC), Bogotá, Colombia.
<sup>2</sup> Aerospace Medicine Research Program, DIMAE, Colombian Aerospace Force, Bogotá, Colombia.

<sup>\*</sup> Corresponding author.

ORCID (D.L.M.): [0000-0002-2257-4940](https://orcid.org/0000-0002-2257-4940)
ORCID (M.A.F.): [0000-0002-9910-6053](https://orcid.org/0000-0002-9910-6053)

## Corresponding author

Diego L. Malpica, MD
Subdirectorate of Aerospace Sciences, Direction of Aerospace Medicine (DIMAE)
Colombian Aerospace Force (Fuerza Aeroespacial Colombiana)
Bogotá, Colombia
Email: diego.malpica@fac.mil.co
ORCID: [0000-0002-2257-4940](https://orcid.org/0000-0002-2257-4940)

## Author contributions (CRediT taxonomy)

Authorship adheres to the International Committee of Medical Journal Editors (ICMJE) recommendations. Contributions are declared per the Contributor Roles Taxonomy (CRediT):

- **D.L.M.** — Conceptualization; Methodology; Software; Validation; Formal analysis; Investigation; Data curation; Writing – Original Draft; Writing – Review & Editing; Visualization; Supervision; Project administration.
- **M.A.F.** — Methodology; Writing – Review & Editing.

Both authors read, critically revised, and approved the final version of the manuscript and agree to be accountable for all aspects of the work (ICMJE criteria 1–4).

## Affiliations where the work was performed

Subdirectorate of Aerospace Sciences, Direction of Aerospace Medicine (DIMAE), Colombian Aerospace Force, Bogotá, Colombia.

## Acknowledgements

The authors acknowledge the foundational contributions of the late William J. Doyle, PhD (University of Pittsburgh School of Medicine, 1946–2016), whose 2005 and 2017 papers remain the canonical description of middle-ear pressure regulation on which this extension builds. The authors thank the medical and technical staff of the Aerospace Medicine Directorate (DIMAE) for institutional support during the curation of the hypobaric-chamber training registry.

## Funding

No external funding supported this work. Institutional resources of the Direction of Aerospace Medicine (DIMAE), Colombian Aerospace Force, supported data curation of the operational registry. The funders had no role in study design; collection, analysis, or interpretation of data; writing of the report; or the decision to submit the article for publication.

## Conflicts of interest / Competing interests

The authors declare no financial or non-financial conflicts of interest, including no commercial, consultancy, or intellectual-property interests related to the physics model, the chamber-training program, or any cited device manufacturer.

## Ethics approval and consent to participate

Under Colombian Resolution 8430 of 1993 of the Ministry of Health (*"Por la cual se establecen las normas científicas, técnicas y administrativas para la investigación en salud"*), Article 11(a), this retrospective secondary analysis of de-identified Colombian Aerospace Force operational chamber-training records (2010–2026) is classified as *investigación sin riesgo* (research without risk) and does not require institutional-ethics-committee submission or individual informed consent. The study was conducted in accordance with the Declaration of Helsinki (2013 revision). No identifiable individual-level patient data are reported. **Publication of this work was authorized by the Colombian Aerospace Force.**

## Consent for publication

Not applicable — no identifiable individual-level patient data or images are included.

## Generative-AI disclosure

No generative artificial-intelligence tools were used in the preparation, writing, or editorial revision of the manuscript text, figures, tables, or interpretive content. An AI-assisted software-engineering assistant (Anthropic Claude) supported author-directed implementation of the Python software under explicit specifications; all scientific content, literature synthesis, clinical interpretation, analytical design, and manuscript prose are the authors' own. No AI tool is listed or claimed as an author (per ICMJE / COPE position statements).

## Data availability statement

The calibration anchor is the Colombian Aerospace Force DIMAE hypobaric-chamber training registry (2010–2026; n = 7,271 exposures, n = 173 clinical barotrauma events). Aggregate cohort statistics (per-exposure prevalence, Wilson 95% CI, URI subgroup gradients) required to reproduce the calibration are reported in the manuscript and in the model card. Individual-level registry records are institutional operational data of the Colombian Aerospace Force; further data may be shared with qualified researchers upon written authorization from the Colombian Aerospace Force institutional authority. External-validation data are drawn from three previously published Italian Air Force cohorts (Morgagni 2010, Morgagni 2012, Landolfi 2009) and are available in those publications.

## Code availability statement

The complete simulator (`barotrauma.v2`), automated test suite (n = 109 tests; 44 v2-specific), calibration scripts, external-validation harnesses, and documentation are available under the MIT license at <https://github.com/strikerdlm/barotrauma_model>. Version tag `v2.2.1-manuscript` corresponds to the state described in this manuscript. A permanent DOI-assigned snapshot of the tagged release will be archived on Zenodo prior to publication and referenced in the final manuscript.

## Reporting guidelines

The study is reported in accordance with the TRIPOD 2015 guideline (Transparent Reporting of a multivariable prediction model for Individual Prognosis Or Diagnosis) for prediction-model development and external validation. The completed TRIPOD 2015 checklist is provided as Supplementary File S1. TRIPOD+AI (Collins 2024) does not apply because no machine-learning component is used in the deployed prediction pipeline; the sklearn scaffolding referenced in the repository is disabled and does not alter the deterministic physics output.

## Institutional release

This work was conducted under the auspices of the Subdirectorate of Aerospace Sciences, Direction of Aerospace Medicine (DIMAE), Colombian Aerospace Force. **Publication of this work was authorized by the Colombian Aerospace Force.**
