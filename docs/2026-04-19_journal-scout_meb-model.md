# Journal Scout Report — MEB Prediction Model Manuscript
**Generated:** 2026-04-19  
**Manuscript:** `docs/manuscript.md`  
**Title:** Physics-Informed Middle Ear Barotrauma Risk for Hypobaric Chamber Training…  
**Article type:** Original Research — computational prediction model development + external validation  
**Reporting guideline:** TRIPOD 2015  
**Word count:** ~3,400 body | 248-word abstract | 24 refs | 4 tables | 2 figures  
**Author context:** Colombian AF (LMIC, Research4Life Group B = 50% APC discount, not full waiver)  
**Methodology:** Physics-informed extension of Kanick-Doyle 2005; ABC-SMC calibration; Sobol SA; no ML  

---

## Strategic Context

**AMHP is the active submission target** (compliance audit 2026-04-18 lists 5 FAIL items pending before portal upload; `amhp-submit` skill tracks this). This report validates AMHP and surfaces credible Plan B / Plan C alternatives in order of pure score, so the decision tree is ready if AMHP does not accept.

**Key scope-validation signal:** The manuscript directly cites papers from two candidate journals:
- *Auris Nasus Larynx* (3 papers: Ikeda 2024, Shindo 2025, Oshima 2025)
- *Undersea and Hyperbaric Medicine* (1 paper: Moayedi 2025)
- The original Kanick-Doyle 2005 model was published in *Journal of Applied Physiology*

**APC posture:** Primary goal is $0 (subscription/hybrid non-OA path). All top candidates offer this.

---

## Phase 4 — Scoring Table (all candidates)

Rubric: Scope /30 · Quartile /25 · APC /25 · Acceptance-rate proxy /10 · Review speed /5 · Indexing bonus /+5  
Quartile: Scimago category most relevant to this paper's primary field. "AR" = acceptance rate.

| # | Journal | Publisher | Scope /30 | Quartile /25 | APC /25 | AR /10 | Speed /5 | Bonus | **Total** |
|---|---------|-----------|-----------|-------------|---------|--------|----------|-------|-----------|
| 1 | **Otology & Neurotology** | LWW | 24 | **25** (Q1 ENT) | **22** ($0 non-OA) | 5 | 3 | +5 | **84** |
| 2 | **Eur. Archives ORL** | Springer | 23 | **25** (Q1 ENT) | **22** ($0 non-OA) | 5 | 3 | +5 | **83** |
| 3 | **Auris Nasus Larynx** | Elsevier | **28** | 18 (Q2) | **22** ($0 non-OA) | 5 | 3 | +5 | **81** |
| 4 | **J. Applied Physiology** | APS | 20 | **25** (Q1) | **22** ($0 via S2O) | 5 | 3 | +5 | **80** |
| 5 | **AMHP** | ASMA | **29** | 8 (Q3) | **22** ($0 non-OA) | 5 | 1 | +5 | **70** |
| 6 | Annals ORL | SAGE | 22 | 8 (Q3) | 22 ($0 non-OA) | 5 | 3 | +5 | 65 |
| 7 | Military Medicine | OUP | 18 | 8 (Q3) | 22 ($0 non-OA) | 5 | 3 | +5 | 61 |

**Sort:** descending by Total. Bold = top 3.  
**AR all unknown** → scored 5 (neutral; no data available).  
**Speed:** AMHP = 1 pt (verified >120 days average, confirmed by ASMA 2019 stats: avg 5 months submission→acceptance). All others = 3 (unknown, neutral).

---

## Phase 5 — Top-3 Finalists + Tradeoff Analysis

### Q1 Tradeoff vs. Acceptance Rate

**Explicit statement:** Q1 journals (O&N, Eur Archives ORL, JAP) have higher acceptance barriers. AMHP (Q3) is the field-dominant journal in aerospace medicine with a smaller, specialized editorial pool that is more likely to recognize the paper's direct clinical and operational value. Prioritizing Q1 scores you higher on bibliometric prestige but increases rejection risk; prioritizing field dominance (AMHP) reduces rejection risk but scores lower on Scimago quartile.

---

### Rank 1: Otology & Neurotology (LWW) — Score 84

| | |
|---|---|
| **Publisher** | Wolters Kluwer / LWW |
| **Quartile** | Q1 (Otorhinolaryngology, Scimago) |
| **IF** | ~2.0 (JCR; unverified exact 2025 value) |
| **APC** | $0 (non-OA submission, subscription journal) |
| **Word limit** | 3,500 words body (clinical studies + basic science) — TRIPOD manuscript at ~3,400 ✓ |
| **Indexing** | Scopus, WoS (SCIE), PubMed/MEDLINE |
| **Submission** | Editorial Manager |

**Fit:** O&N is the leading ENT surgical science journal. Middle-ear barotrauma, Eustachian-tube dysfunction, and tympanic-membrane mechanics are all core O&N territory. The four-state PET model and three-threshold hazard system would be natural fits alongside clinical papers on ET balloon dilation and PET surgery.

**Tradeoff:** O&N's editorial culture is strongly clinical-surgical. Physics-informed computational models are unusual in its pages. Reviewers may push for more empirical data or a clinical companion dataset rather than cohort-level aggregate calibration. The 3,500-word body limit is tight; at ~3,400 the manuscript is within range but has no headroom for revision additions. [VERIFY word limit at journal website before submitting.]

**Risk:** The paper explicitly states it cannot provide discrimination metrics (c-statistic, calibration slope) "because cohort-level aggregate prediction makes them inapplicable." An O&N reviewer steeped in individual-risk prediction may find this limitation substantial. The military-aviation context (Colombian AF registry) may also be unfamiliar territory.

**Indexing:** Scopus + WoS SCIE + PubMed. Full triple indexing.

---

### Rank 2: European Archives of Oto-Rhino-Laryngology (Springer) — Score 83

| | |
|---|---|
| **Publisher** | Springer Nature |
| **Quartile** | Q1 (Otorhinolaryngology, Scimago); Q2 (Medicine misc.) |
| **IF** | 2.2 (JCR 2025); CiteScore 4.5 |
| **SJR** | 0.787 |
| **H-index** | 94 |
| **APC** | $0 (non-OA submission via Springer hybrid — standard article submission free) |
| **OA option** | ~€2,800–4,400 (Springer standard; unverified exact 2026 rate) |
| **Indexing** | Scopus, WoS (SCIE), PubMed/MEDLINE, Embase |

**Fit:** Eur Arch ORL publishes "original clinical reports and clinically relevant" research across all head-and-neck specialties, with strong Eustachian tube and middle ear content. The paper's multi-state pathophysiology (URI temporal dynamics, PET states, descent-rate mechanics) fits the journal's translational physiology niche well. The EUFOS scope is explicitly international and European-validation papers (Italian AF) would resonate with the readership.

**Tradeoff:** Eur Arch ORL is primarily clinical and translational. The physics/computational modeling depth may face the same editorial concern as O&N. However, the journal has published computational simulation and modeling studies in head-and-neck surgery, so the precedent exists. The subscription non-OA path is free but Springer's embargo policy [VERIFY AT JOURNAL WEBSITE].

**Risk:** Springer requires color figures often without an additional fee, but extra table and figure charges should be confirmed. Word limit [VERIFY AT JOURNAL WEBSITE] — not retrieved in this search; typical Springer original article = 4,000-6,000 words. At 3,400 the manuscript would likely be well within limits.

**Indexing:** Full quad indexing (Scopus + WoS SCIE + PubMed + Embase). Strongest indexing of all candidates.

---

### Rank 3: Auris Nasus Larynx (Elsevier Ireland) — Score 81

| | |
|---|---|
| **Publisher** | Elsevier Ireland Ltd |
| **Quartile** | Q2 (Otorhinolaryngology, Surgery, Medicine misc.) |
| **IF** | 1.5 (JCR 2025) |
| **SJR** | 0.588 |
| **APC** | $3,520 (Gold OA); $0 (non-OA via Elsevier hybrid) |
| **Indexing** | Scopus, WoS (SCIE), PubMed/MEDLINE |

**Fit:** This is the strongest scope match for the paper's content. The manuscript directly cites three ANL papers published within the last two years:
- Ikeda et al. 2024 — PET diagnostic criteria (ANL)
- Shindo et al. 2025 — middle-ear pressure in habitual sniffers (ANL)
- Oshima et al. 2025 — PET large-scale study, OR 8.18 for sniffing (ANL)

By citing these papers the authors have established a direct literature lineage into ANL. The journal publishes the Japan Otological Society and covers Eustachian tube, middle ear, and barotrauma as primary content areas. The PET four-state model in this paper directly extends findings published in ANL.

**Tradeoff:** Q2 rather than Q1 reduces bibliometric prestige slightly. If the primary goal is dissemination within the otology community most familiar with PET and ET dysfunction, ANL may actually achieve better readership penetration than the higher-impact O&N. Elsevier's hybrid non-OA path means the paper sits behind a paywall for 12 months (standard Elsevier embargo) unless OA fees (~$3,520) are paid. Research4Life Group B membership gives ~50% APC discount if OA is needed, bringing OA to ~$1,760.

**Risk:** Editorial bandwidth around the PET-barotrauma interface is highest here. However, the paper may be seen as primarily an aerospace-medicine modeling paper by ENT reviewers who expect more clinical validation data.

**Indexing:** Scopus + WoS SCIE + PubMed. Full triple indexing.

---

## AMHP Analysis — Primary Track

**AMHP ranks 5th by pure scoring rubric** (Q3 category penalizes it heavily). However, AMHP is the strategic primary target for this paper and the ranking understates its real-world appropriateness:

| Factor | Score-rubric view | Real-world view |
|--------|------------------|-----------------|
| Quartile | Q3 in "Public Health, Environmental and Occupational Health" — broad Scimago bucket | Field-dominant journal in aerospace medicine globally; only peer-reviewed monthly in its niche |
| Scope | 29/30 — near-perfect | The paper is explicitly an aerospace-medicine clinical decision-support tool. No other journal in this list serves that exact community |
| APC | $0 confirmed (ASMA website, Aug 2025 policy) | Verified zero cost for non-OA; OA option $1,500 |
| Word limit | [VERIFY at journal website] — found 3,000-word limit in one PDF but context was a specific article format | Typical AMHP Original Research ≈ 3,500 words body; manuscript at ~3,400 is at risk if limit is 3,000 |
| Review time | ~5 months submission→acceptance (ASMA 2019 stats) | Long but expected for monthly specialist journal |
| Indexing | Scopus + WoS | H-index 85; long-standing aviation medicine index |

**Current submission status:** 5 FAIL items from the 2026-04-18 compliance audit must be resolved before portal upload. These are tracked in `docs/submission/2026-04-18_amhp_compliance_audit.md`. The word limit for Original Research at AMHP must be verified as a PRIORITY — the manuscript body at ~3,400 words is within typical limits but if the hard cap is 3,000, revision is required before submission regardless of other FAIL items.

**Recommendation on AMHP:** Fix the 5 FAIL items and submit. If rejected, the decision tree below applies.

---

## Rejection Decision Tree

```
AMHP → reject or >6 months no decision
    ↓
Tier A (scope + Q1):
    → Otology & Neurotology   (best quartile, ENT audience, tight word limit)
    → Eur Archives ORL         (Q1, strongest indexing, translational fit)
    ↓
Tier B (best scope validation, Q2):
    → Auris Nasus Larynx       (3 cited papers, PET lineage, Elsevier hybrid free)
    ↓
Tier C (Kanick-Doyle lineage, Q1 physiology):
    → Journal of Applied Physiology (S2O = $0 APC, original KD venue)
    ↓
Tier D (military audience, lower bar):
    → Military Medicine         (Q3, OUP hybrid free, military context strong)
```

**JAP note on S2O:** APS (American Physiological Society) runs a Subscribe-to-Open program for JAP where no APC is charged to authors and content is immediately OA. This is contingent on institutional subscription levels being maintained. As of April 2026 this program is active; verify status at submission time.

---

## Additional Candidates — Below Cutoff

**Laryngoscope Investigative Otolaryngology (Wiley OA):** Gold OA, Q2, good ENT scope. APC ~$2,150 (Wiley standard). Research4Life discount applies (50% → ~$1,075). Reasonable Plan B if open access is required, but below Q1 targets and APC creates friction.

**Undersea & Hyperbaric Medicine (UHMS):** The paper cites Moayedi 2025 from this journal. However, WoS status shows "Discontinued" in WoS Core citation indexes as of this search (unverified — [VERIFY current indexing status]). If WoS indexing has lapsed, this journal does not meet minimum inclusion criteria. Scope is strong (chamber physiology, pressure-related injury), but indexing uncertainty disqualifies it from the ranked table.

**Annals ORL (SAGE):** Q3, non-OA free. Broad ENT scope but lower prestige than top options. Keep as backup after Tier D.

**Military Medicine (OUP):** Q3, OUP hybrid ($0 non-OA). Military aviation relevance is high. Editorial focus is broad federal medicine — the physics model depth may be unusual. Good backup for the military audience specifically. OUP Colombia is not in the EIFL APC-waiver countries list (Colombia is not listed), but hybrid non-OA submission remains free.

---

## Data Quality Flags

| Item | Status |
|---|---|
| AMHP Original Research word limit | [VERIFY AT JOURNAL WEBSITE] — 3,000 found for a specific article format; standard OR limit unconfirmed |
| Eur Archives ORL word limit | [VERIFY AT JOURNAL WEBSITE] — not retrieved in search |
| JAP S2O program active status | Confirmed active April 2026; re-verify at submission |
| Undersea & Hyperbaric Medicine WoS status | [VERIFY] — search returned "Discontinued" flag |
| AMHP MEDLINE indexing | Assumed yes (successor to Aviat Space Environ Med, which was MEDLINE-indexed); [VERIFY] |
| Quartile source | All from Scimago 2024 data (1-year lag); 2025 data not yet published |
| APC figures | Confirmed for AMHP ($0 non-OA, $1,500 OA from ASMA Aug 2025 form) and ANL ($3,520 from Elsevier); others inferred from hybrid-journal policies |
| Colombia Research4Life status | Group B = 50% APC discount (not full waiver). Do NOT claim full waiver. |

---

## Summary

```
✓ Journal Scout complete
  Paper scouted: docs/manuscript.md
  Candidates evaluated: 7
  Primary track: AMHP (active, 5 FAIL items to clear)
  Top picks by score: Otology & Neurotology (84) · Eur Archives ORL (83) · Auris Nasus Larynx (81)
  Best scope validation: Auris Nasus Larynx (3 cited papers, PET lineage)
  Best quartile: Otology & Neurotology / Eur Archives ORL / JAP (all Q1)
  Zero-APC path: All top candidates via non-OA hybrid submission
  Output: /root/code/barotrauma_model/docs/2026-04-19_journal-scout_meb-model.md
```
