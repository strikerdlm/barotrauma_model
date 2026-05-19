# Journal Scout — Middle-Ear Barotrauma Prediction Model (Paper 1)

**Date:** 2026-05-11  
**Manuscript:** *Beyond Binary Lock: A Continuous Aperture-Collapse Hazard Model of Middle-Ear Barotrauma in Hypobaric-Chamber Training* (BMB submission title) /  
*Physics-Informed Middle Ear Barotrauma Risk for Hypobaric Chamber Training: A Computational Prediction Model Calibrated to the Colombian Aerospace Force Cohort and Externally Validated Against Italian Air Force Cohorts* (primary title)  
**File reference:** `docs/manuscript.md` (pending creation)  
**Scout version:** 2.2.0 · AI-policy filter ON

---

## Phase 1 — Field Inference

| Dimension | Assessment |
|---|---|
| **Primary field** | Computational/aerospace medicine |
| **Subfield** | Middle-ear barotrauma (MEB) prediction; otologic risk; hypobaric chamber physiology; Eustachian tube dynamics |
| **Article type** | Original research — TRIPOD-compliant computational prediction model development + external validation |
| **Key methodology** | Physics-informed ODE (Kanick-Doyle 2005 core), Hill-function aperture-collapse factor, ABC-SMC posterior, Saltelli-Sobol global SA, three-threshold cumulative hazard model |
| **Word count** | ~3,400 body · 248-word abstract · 4 tables · 4 figures |
| **Reporting guideline** | TRIPOD 2015 (checklist S1 filed) |
| **Author context** | Colombia (DIMAE, FAC) = Research4Life Group B = 50% APC discount, not full waiver |
| **AI disclosure** | Filter **ON** — generative-AI assistance in manuscript preparation will be declared |
| **Prior rejections** | (1) AMHP (AI-policy denylist, 2026-05-08); (2) Bulletin of Mathematical Biology (BMB) — desk reject 2026-05-11; (3) International Journal of Applied and Computational Mathematics (IJACM) — desk reject 2026-05-19 |

### Critical signal from BMB rejection

BMB's rejection letter stated: *"The mathematical modelling contribution of the work is not sufficiently strong to be suitable for our readership."*

**Implication for resubmission framing:** This manuscript should NOT be positioned as a mathematical biology paper. The aperture-collapse Hill function and Sobol sensitivity analysis are methodological tools, not the theoretical contribution — which is the **clinical and operational prediction model for a real military cohort with external validation**. Reframing should emphasize:

- TRIPOD-grade prediction model calibrated to n = 7,271 real-world FAC exposures
- External validation against three published Italian AF cohorts (zero refitting)
- Operational utility for hypobaric chamber screening decisions
- Mechanistic underpinning (physics + pathophysiology) as the novelty framing, not the mathematics per se

**Target journal class accordingly:** Otology/ENT journals, military/aerospace medicine journals, applied physiology journals — where clinical and operational relevance drives scope, not mathematical novelty.

---

## Phase 3.5 — AI-Use Policy Filter

Filter status: **ON** (Diego discloses AI tool use per ICMJE/COPE/WAME).

| Journal | Publisher | AI policy tag | Evidence |
|---|---|---|---|
| Otology & Neurotology | Wolters Kluwer (LWW) | **Tolerant** | Publisher on tolerant list; COPE/ICMJE-aligned |
| European Archives ORL | Springer Nature | **Tolerant++** | Publisher on tolerant list; active AI Call for Papers on journal website |
| Auris Nasus Larynx | Elsevier | **Tolerant** | Publisher on tolerant list; ICMJE follows statement |
| Annals ORL | SAGE | **Tolerant** | Publisher on tolerant list |
| Journal of Applied Physiology | APS | **Unclear** | APS not verified; recommend pre-submission inquiry |
| Journal of Laryngology & Otology | Cambridge University Press | **Tolerant** | CUP prohibits AI authorship but requires clear declaration = COPE-standard |
| Military Medicine | OUP | **Tolerant** | Publisher on tolerant list |
| Laryngoscope Investigative ORL | Wiley | **Tolerant** | Publisher on tolerant list |
| **AMHP (ASMA)** | ASMA | **DENYLIST** | Verbatim desk-rejection 2026-05-08 on declared AI use — see `AI_POLICY_FILTER.md` §4 |
| **Bulletin of Mathematical Biology** | Springer Nature | Tolerant | Rejected on scope, not AI policy; re-eligible for other Springer titles |

---

## Phase 4 — Scoring

Rubric: Scope (30) + Quartile/SJR (25) + APC (25) + Acceptance proxy (10) + Speed (5) + Indexing bonus (up to +5). Maximum 105.

| # | Journal | Scope | Quartile | APC | Acceptance | Speed | Bonus | **Total** |
|---|---|---|---|---|---|---|---|---|
| **1** | **Otology & Neurotology** | 28 | 25 (Q1 Scimago ORL) | 22 ($0 subscription) | 5 (unknown) | 3 (unknown) | +4 | **87** |
| **2** | **European Archives ORL** | 26 | 25 (Q1 Scimago ORL) | 22 ($0 subscription) | 5 (unknown) | 3 (unknown) | +4 | **85** |
| **3** | **Auris Nasus Larynx** | 27 | 20 (Q2 Scimago/JCR) | 22 ($0 subscription) | 6 (est. 35–45%) | 3 (unknown) | +4 | **82** |
| 4 | Journal of Applied Physiology ⚠️ | 22 | 25 (Q1 Physiology) | 22 ($0 S2O) | 4 (est. 15–25%) | 3 (unknown) | +4 | 80 |
| 5 | Annals of Otology, Rhinology & Laryngology | 25 | 20 (Q2 Scimago ORL) | 22 ($0 subscription) | 5 (unknown) | 3 (unknown) | +4 | **79** |
| 6 | Journal of Laryngology & Otology | 22 | 14 (Q3 Scimago) | 22 ($0 subscription) | 6 (est. 40–50%) | 3 (unknown) | +4 | 71 |
| 7 | Military Medicine | 18 | 14 (Q3 Scimago) | 22 ($0 subscription) | 6 (est. 40–55%) | 3 (unknown) | +4 | 67 |
| 8 | Laryngoscope Investigative ORL | 24 | 20 (Q2 Scimago) | 10 (~$1,320 with 50% R4L waiver) | 6 (est. 40–50%) | 3 (11-wk median) | +4 | 67 |

⚠️ = AI policy unclear — pre-submission inquiry recommended before committing.

---

## Phase 5 — Top-3 Recommendations

### Top-3 Table

| Rank | Journal | Publisher | Quartile | APC | Scope match | Word cap | Indexing | Score |
|---|---|---|---|---|---|---|---|---|
| **#1** | **Otology & Neurotology** | Wolters Kluwer (LWW) | Q1 (Otorhinolaryngology, Scimago) | $0 subscription | Direct — otology, ET pathophysiology, clinical prediction | 3,000 words body [VERIFY] | Scopus, WoS SCIE, PubMed | **87** |
| **#2** | **European Archives of Oto-Rhino-Laryngology** | Springer Nature | Q1 (Otorhinolaryngology, Scimago) | $0 subscription | Strong — clinical and translational ORL; active AI Call for Papers | 3,500 body [VERIFY] | Scopus, WoS SCIE, PubMed | **85** |
| **#3** | **Auris Nasus Larynx** | Elsevier | Q2 (JCR IF 1.5–1.6; Scimago Q2) | $0 subscription | Strongest citation lineage — 3 cited papers from this journal in the manuscript | 3,500 body [VERIFY] | Scopus, WoS SCIE, PubMed | **82** |

---

### #1 — Otology & Neurotology (score 87)

**Fit rationale.** O&N is the flagship journal of the American Otological Society and American Neurotology Society. Its stated scope is "original articles relating to both clinical and basic science aspects of otology, neurotology, and cranial base surgery." Eustachian tube dysfunction, middle-ear pressure mechanics, and barotrauma in chamber/diving settings are central to its readership. The manuscript's physics-informed hazard model with FAC cohort calibration and Italian AF external validation is exactly the kind of clinical–basic science synthesis the journal targets.

**Tradeoff.** O&N is competitive (Q1, SJR 0.866, WoS rank 71.6th percentile among ORL journals). Rejection rate is not published but estimated high for Q1. Acceptance will depend on how compelling the FAC cohort data look to otology reviewers who may not have aerospace medicine context — the cover letter must do significant work bridging the military chamber context.

**Risk.** If reviewers are surgical otologists (cochlear implant, skull base), they may not relate to hypobaric chamber physiology. Consider framing the clinical utility (pre-chamber screening tool, recommended descent rates) prominently to anchor the "so what for otology practice" question.

**Indexing.** Scopus ✓, WoS SCIE ✓, PubMed/MEDLINE ✓. H-index 130. The most cited otology journal after Laryngoscope/Otolaryngology–HNS.

**APC.** $0 for non-OA submission (subscription model, LWW). Open access option via *Otology & Neurotology Open* at $1,850 APC — not required.

---

### #2 — European Archives of Oto-Rhino-Laryngology (score 85)

**Fit rationale.** European Archives covers "the broad variety of head and neck diseases with an inherent focus on clinical and translational research in all specialties of ORL and Head & Neck." Critically, the journal has an **active Call for Papers on AI and LLMs in Clinical Otolaryngology**, which signals a strongly AI-tolerant editorial stance — directly opposite to AMHP and BMB. This makes it the safest choice from an AI-disclosure standpoint. The journal also publishes methodologically rich papers more readily than American society journals, making the computational modeling framing a better fit here than at O&N.

**Tradeoff.** Q1 Scimago (SJR 0.787) but slightly lower than O&N in absolute SJR. IF 2.22 (WoS) which is actually higher than O&N (IF 1.77/2.0). High volume: 862 documents/year — editorial throughput is rapid and the acceptance rate is likely higher than O&N, making this the better risk-adjusted Q1 option.

**Risk.** Springer journal — the Transfer Desk email you received suggests they may route you here automatically. This is actually a positive signal: Springer Transfer Desk typically routes to in-scope Springer journals, and European Archives is the logical Springer ORL match. The pre-submission transfer path may be available.

**Indexing.** Scopus ✓, WoS SCIE ✓, PubMed/MEDLINE ✓. H-index 94.

**APC.** $0 for non-OA submission (hybrid Springer journal; subscription track = author pays nothing). OA option available but not required.

**Springer Transfer Desk note.** The Transfer Desk email following your BMB rejection means Springer will likely propose European Archives directly. Accept the transfer offer — it bypasses the cold-submission queue and may accelerate desk review.

---

### #3 — Auris Nasus Larynx (score 82)

**Fit rationale.** Auris Nasus Larynx (ANL) is the official English-language journal of the Japanese Society of ORL-Head & Neck Surgery. It publishes "fundamental and clinical aspects of otorhinolaryngology and related fields" with rapid peer review. The strongest evidence for scope fit is **internal**: the manuscript cites 3 papers published in ANL (the highest citation count for any single ORL journal in the reference list per README), which means the editorial board and readership have directly published on the precise topic. Reviewers are more likely to be experts in ET dysfunction and barotrauma biomechanics.

**Tradeoff.** Q2 (JCR IF 1.5–1.6; Scimago Q2), so prestige is one notch below the top two. However, the citation lineage means almost certain scope acceptance at desk review, and Q2 acceptance rates are typically higher, reducing time-to-publication. For a paper that has already received two desk rejections, a successful Q2 publication is preferable to a third Q1 rejection.

**Risk.** The journal is Elsevier hybrid — OA APC is $3,520, but the subscription (non-OA) route is $0. Confirm at submission that the non-OA route is selected. Some Japanese society journals have page charges for colour figures — verify in the Guide for Authors.

**Indexing.** Scopus ✓, WoS SCIE ✓, PubMed/MEDLINE ✓. H-index 76.

**APC.** $0 for non-OA hybrid submission (Elsevier subscription track).

---

### Best Q2/Q3 Alternative

**Annals of Otology, Rhinology & Laryngology** (SAGE, Q2 Scimago ORL, SJR 0.528, score 79)

AORN has a 130-year history publishing original clinical and research manuscripts in otolaryngology-HNS. The Miyazawa et al. 1996 paper on ET function and MEB in hypo/hyperbaric settings was published here — the oldest direct scope citation for the manuscript's topic. The journal is subscription-based (SAGE) with no APC, Q2 in Otorhinolaryngology, and a smaller volume (~171 docs/year) suggesting a more selective but field-specific readership. For authors who want a Q2 route with strong historical scope lineage and zero APC risk, AORN is the best single alternative to the top three. Submission is via ScholarOne Manuscripts. SAGE is on the tolerant publisher list; AI disclosure will not trigger desk rejection here.

---

## Excluded — AI-policy incompatible

| Journal | Publisher | Evidence | Date |
|---|---|---|---|
| **Aerospace Medicine and Human Performance (AMHP)** | ASMA | Verbatim desk-rejection: *"the declared use of AI in this manuscript means that we cannot send it for peer review"* | 2026-05-08 |

Note: AMHP (score would have been ~75 on scope/quartile grounds) remains excluded while this policy is in effect. Re-eligible only with `no-ai-disclosure` argument, which does not apply to this manuscript.

---

## JAP — Special Flag

**Journal of Applied Physiology** (APS, Q1 Physiology, SJR 1.078, $0 S2O model, score 80) scores fourth overall but carries an **unclear AI-use policy** because the American Physiological Society (APS) is not on the verified tolerant publisher list. JAP published the Kanick-Doyle 2005 mathematical model of MEB during flight — the strongest single scope validation in the literature. However, scope fit scores only 22/30 because JAP's editorial emphasis is on mechanistic physiology, not TRIPOD-grade clinical prediction models; the FAC cohort framing may feel like epidemiology to JAP reviewers. **Recommended action:** send a pre-submission inquiry to the JAP editorial office asking (a) whether the manuscript is in scope and (b) the journal's AI-disclosure policy before committing to submission.

---

## Submission Sequence Recommendation

Given **three** prior desk rejections (all from math/computational journals), the ORL pivot is now mandatory. Risk-adjusted sequence:

| Priority | Journal | Rationale |
|---|---|---|
| **1st** | **Otology & Neurotology** | Highest score (87); flagship otology Q1; direct scope match; accept Springer Transfer offer from IJACM only if it routes here (unlikely — IJACM is computational math, different editorial group) |
| **2nd** | **European Archives ORL** | Q1 Springer; active AI Call for Papers; AI-tolerant; check for IJACM Transfer Desk offer (Springer-to-Springer) |
| **3rd** | **Auris Nasus Larynx** | Strongest citation lineage (3 cited papers); Q2 with near-certain scope acceptance; submit if 1 and 2 reject |
| **Fallback** | **Annals ORL** (SAGE) | Q2, historical scope, $0 APC, SAGE tolerant |

**Updated 2026-05-19 after IJACM desk rejection.**

**Reframing checklist before any resubmission:**
- [ ] Title: emphasize prediction model + FAC cohort, not mathematical framework
- [ ] Abstract: lead with the clinical problem and cohort, not the aperture-collapse mathematics
- [ ] Cover letter: highlight TRIPOD compliance, external validation, operational context (military hypobaric training)
- [ ] Methods: present Sobol SA and Hill function as validation/characterization tools, not as the primary contribution
- [ ] Discussion: emphasize clinical screening utility and recommended safe descent rates as the "so what"

---

## Output Summary

```
✓ Journal Scout complete
  Papers scouted: 1 (MEB prediction model, Paper 1)
  Candidates evaluated: 8
  AI-policy filter: ON (AMHP excluded)
  Prior rejections excluded: AMHP (AI denylist), BMB (scope), IJACM (scope/desk)
  Top picks: Otology & Neurotology → European Archives ORL → Auris Nasus Larynx
  Best Q2 alternative: Annals of Otology, Rhinology & Laryngology
  Output: /root/repos/barotrauma_model/2026-05-11_journal-scout_meb-barotrauma.md
```
