## Cover Letter — Bulletin of Mathematical Biology

**Manuscript:** Beyond Binary Lock: A Continuous Aperture-Collapse Hazard Model of Middle-Ear Barotrauma in Hypobaric-Chamber Training

**Date:** 2026-05-01

---

Diego L. Malpica, MD
Subdirectorate of Aerospace Sciences
Direction of Aerospace Medicine (DIMAE)
Colombian Aerospace Force (Fuerza Aeroespacial Colombiana)
Bogotá, Colombia
diego.malpica@fac.mil.co — ORCID 0000-0002-2257-4940

Editorial Office
*Bulletin of Mathematical Biology*
Springer Nature

---

Dear Editor,

We submit for your consideration as an **Original Research Article** the manuscript **"Beyond Binary Lock: A Continuous Aperture-Collapse Hazard Model of Middle-Ear Barotrauma in Hypobaric-Chamber Training."**

**Scope match.** The work sits squarely at the *Bulletin*'s interface of mathematics and biology. We develop a physics-informed ordinary-differential-equation model of middle-ear pressure regulation in which the binary "open / locked" Eustachian-tube treatment of Kanick & Doyle (2005) is replaced with a continuous Hill-function aperture coupled to a discrete pathophysiology state machine (six-state upper-respiratory-infection temporal modifier; four-state Patulous Eustachian-tube model). Three hazard-rate constants are inferred via Approximate Bayesian Computation Sequential Monte Carlo (ABC-SMC), the model is externally validated on three independent previously published cohorts without parameter refitting, and global Saltelli–Sobol sensitivity analysis identifies the aperture half-pressure as the dominant variance driver. We believe this matches the journal's stated aim to publish "new biological insights gained with tools from the mathematical sciences, [and] new mathematical tools with demonstrated applicability to biological investigations."

**Key contributions.**

1. A continuous, rate-dependent Eustachian-tube aperture-collapse function that resolves a known regime gap of Kanick–Doyle's binary lock model when descent rates exceed cabin physiology by 5–30×.
2. An ABC-SMC calibration pipeline anchored to a 7,271-exposure operational registry (Colombian Aerospace Force, 2010–2026) that transfers across three independent published military-aviation cohorts within the observed Wilson 95% CI for two of three benchmarks, with no refitting.
3. A global Saltelli–Sobol decomposition that ranks the aperture half-pressure ($S_T \approx 0.99$) as the single highest-leverage empirical refinement target — a directly actionable conclusion for screening and chamber-training policy.

**Originality and prior dissemination.** This work has not been previously published and is not under consideration elsewhere. An open-source MIT-licensed implementation is available at <https://github.com/strikerdlm/barotrauma_model>; the tagged release `v2.2.1-manuscript` corresponds to the state described in this submission, and a permanent DOI-assigned snapshot will be deposited on Zenodo prior to publication.

**Compliance.** The manuscript complies with the journal's guidelines on data availability, code availability, ICMJE authorship, and the CRediT taxonomy, all of which are documented in the "Statements and Declarations" section. Reporting follows TRIPOD 2015; the completed 28-item checklist is provided as Supplementary File S1. Publication of this work was authorized by the Colombian Aerospace Force.

**Suggested reviewers.** The candidates listed below are proposed for their expertise in ODE-based physiology, Eustachian-tube mechanics, Bayesian computation, and aerospace medicine. None are at the authors' institution and no conflicts of interest are known to the authors.

1. **Samir N. Ghadiali, PhD** — Department of Biomedical Engineering, The Ohio State University, Columbus, OH, USA. Expertise: computational mechanics of the Eustachian tube and lung; finite-element pressure-regulation modelling.

2. **Cuneyt M. Alper, MD** — Department of Otolaryngology, University of Pittsburgh School of Medicine, Pittsburgh, PA, USA. Expertise: middle-ear pressure regulation, tympanometry, mastoid-volume physiology.

3. **Tina Toni, PhD** — Imperial College London, London, UK. Expertise: Approximate Bayesian Computation Sequential Monte Carlo for deterministic biological models; original author of the ABC-SMC algorithm used here.

4. **Andrea Saltelli, PhD** — European Centre for Governance in Complexity / Universitat Oberta de Catalunya. Expertise: Sobol global sensitivity analysis for mathematical models in the life sciences.

5. *(Optional, aerospace-medicine reviewer)* **Sarah J. Lindfors, MD, PhD** — Karolinska Institutet, Stockholm, Sweden. Expertise: epidemiology of middle-ear barotrauma in aircrew; URI as risk factor.

We have no opposed reviewers.

We thank you for considering this submission and look forward to the editorial decision.

Sincerely,

Diego L. Malpica, MD
On behalf of both authors
diego.malpica@fac.mil.co
ORCID 0000-0002-2257-4940
