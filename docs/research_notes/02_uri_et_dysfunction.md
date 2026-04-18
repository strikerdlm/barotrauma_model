# URI and Eustachian Tube Dysfunction: Quantitative Risk Modifier Evidence

**Target model:** Colombian Aerospace Force MEB risk model. Hypobaric chamber cohort: 5.8% MEB prevalence over 10 y; URI is dominant modifiable risk factor.
**Purpose:** Provide calibrated effect-size inputs for a URI pathophysiology module (multipliers on ET mechanical constants and on per-exposure MEB hazard).

---

## 1. Magnitude of ET dysfunction during acute URI (experimental rhinovirus challenge)

The Pittsburgh experimental-cold cohort (intranasal rhinovirus type 39 / Hanks, n=32–316 across studies) is the gold standard.

| Measure | Pre-infection | Post-infection | Source |
|---|---|---|---|
| 9-step (inflation-deflation) test abnormal, peak | ≈5% of ears | ~80% of ears (50% of ears had any tubal function on day 2 post-challenge) | McBride 1989, PMID 2548538 |
| Middle-ear pressure < −50 mmH2O (≈ −49 daPa) | <5% | 50% of subjects on day 2 | McBride 1989; Sperber 1992 PMID 1323974 |
| Middle-ear pressure < −100 mmH2O (≈ −98 daPa) | 5% (3/60) | **39%** (22/57) | Buchman 1994, PMID 7934605 |
| Any abnormal ME pressure in infected-ill | baseline | ~60% of subjects, ~40% of ears | Doyle 1999, PMID 10890787 |
| Any abnormal ME pressure in infected-asymptomatic | baseline | ~30% still develop abnormality | Doyle 1999, PMID 10890787 |
| ETDQ-7 in chronic-ETD analogues | 8–10 (normal) | 20.7 ± 8.4 (CRS+ETD), 29.5 ± 8.1 (primary ETD), 25.8 ± 8.0 (CRS with ETD) | Chen 2022 (PMID 34919345); Chang 2020 (PMID 32343633) |

URI → ETDQ-7 analogues: although no controlled cold-challenge study used ETDQ-7, the closest disease-state benchmarks (acute ETD and CRS-associated ETD) produce an 8–15-point rise over the 14.5 cutoff. Adopt a modeled URI-peak increment of +13 points (95% CI 9–18) for Days 2–5.

**Valsalva success rate:** No direct RCT during URI, but CRS+ETD cohorts with symptoms comparable to active URI show Valsalva positivity rising from ~35% to ~75% *after* anti-inflammatory treatment (Chen X 2021, PMID 34608896). This implies a ~35–40 percentage-point drop in Valsalva success during acute inflammation. Model modifier: **0.55× baseline success** during URI days 1–7.

---

## 2. Temporal recovery course

Peak ET dysfunction on **days 2–5** post-URI onset (McBride 1989; Doyle 1992 PMID 1316390). Tubal function normalizes in most subjects **by day 6–10**. Tympanometric abnormalities and mucosal inflammation may persist longer.

| Day post-onset | ET function status (human challenge data) |
|---|---|
| 0 | Pre-exposure baseline |
| 1–3 | Rapid-onset obstruction; 50% ears with no tubal function by day 2 |
| 4–7 | Peak dysfunction; 39% have ME pressure < −100 mmH2O; max symptoms day 4–5 |
| 8–14 | Progressive recovery; most ears restored by day 10 (McBride 1989) |
| 15–21 | Near-baseline in healthy adults; some mucosal edema persists |
| 22–28 | Residual: COVID-era data show OME and SARS-CoV-2 detectable in middle-ear fluid up to 28 days (Yu 2025 PMID 40319775, Zhang 2024 PMID 38356273) — justifies extending a 14-d grounding rule to ≥21 d in high-acuity viral URI |

**Recommended grounding window** (maps to RCAC flight-surgeon policy): MEB risk elevated ×3–4 at day 7, ×1.5–2 at day 14, and ×1.2 residual through day 21 (inferred from peak-to-baseline curves in the Doyle cohort).

---

## 3. Mechanism parameters (modeler-prior ranges)

Direct in-vivo human measurement of tissue pressure PET, luminal % diameter reduction, and active-resistance fold increase during URI does **not exist** in the literature. Parameters must be set as priors from primate and cadaver studies and calibrated to the observed MEB rates.

| Parameter | Healthy baseline | URI effect (proposed prior) | Source / basis |
|---|---|---|---|
| PET (peritubal tissue pressure) | ~0 mmHg | **+5 to +10 mmHg** (venous engorgement + submucosal edema) | Inferred from nasal mucosal pressure rise during experimental rhinovirus (Doyle 1992); no direct ET measurement |
| Luminal diameter | 100% | **60–75%** (25–40% reduction) | Extrapolated from primate cleft-palate and cadaveric ET edema models (Doyle 1980, PMID 6778347); consistent with obstruction physiology |
| Active resistance RA | ~10⁴ dPa·mL⁻¹·s (healthy adult) | **×2–4 fold increase** | Shupak 1996 (PMID 8583858): hypoxic/hypercarbic mixes ↓RA by ~30%, implying URI (inflammatory, edematous) ↑RA by at least the same order. Fit to 50% ETD failure rate on day 2 (McBride 1989) |
| Passive opening pressure PO′ | ~150–200 daPa | **+100 to +200 daPa shift upward** | Shupak 1996; Doyle 1980; primate edema studies. Reflects that forced opening requires higher transtubal gradient. |

**Transparent modeling rule:** these are calibration priors, not measured constants. Fit the multipliers such that simulated MEB incidence at 8,000 ft descent reproduces the observed Buchman 39% ME pressure <-100 mmH2O fraction.

---

## 4. Barotrauma risk effect sizes

| Exposure / state | Effect size for MEB or analog | Source |
|---|---|---|
| Active URI + flight (commercial pilots) | Lifetime barotitis prevalence: 55.5% vs. non-URI pilots (baseline ~37.4%); crude odds ratio ≈ **2.1** | Boel 2017 PMID 28061917; Rosenkvist 2008 PMID 18856186 |
| Flying with URI, self-report | 50.1% of pilots flew despite URI signs (2017) vs 42.8% (2008); correlates with the barotitis rise | Boel 2017 |
| Pre-chamber screening positive → chamber MEB | 2.4% with screening vs historical >5–8% without; NNT ≈ 20 | Landolfi 2009 PMID 20027855 |
| ENT comorbidity in divers (chronic rhinitis, CRS, prior ETD) | **OR 9.3** (P=0.006) for hospitalized barotrauma/DCS | Tournoy 2024 PMID 39675736 |
| Self-reported AR in civil aviation aircrew | AR prevalence 23.38%; ear barotrauma 10.37% overall; symptom aggravation in flight 9.95% | Bai 2021 PMID 33357269 |
| Chronic rhinosinusitis → ETD | Prevalence 25–68%; ETDQ-7 > 14.5 in 47%; pooled ETDQ-7 mean 20.7 ± 8.4 | Chen 2022 PMID 34919345; Wu 2020 PMID 32188265 |

No per-flight pooled OR for windowed URI (≤7 d / 8–14 d / 15–28 d) exists; stratify in the model using the recovery curve in §2.

---

## 5. Medication effects (quantitative)

| Agent | Dose/route | Effect on MEB or ET function | Source |
|---|---|---|---|
| Oral pseudoephedrine 60–120 mg pre-descent | PO | Adults: reduced otalgia during air travel (RCT-level evidence, 1 of 3 pooled RCTs); Children: **no benefit** | Mirza 2005 PMID 15949100 |
| Oral pseudoephedrine + atropine during rhinovirus cold | PO, 4× daily | **No significant improvement** in 9-step test or ME pressure; only nasal congestion fell | Doyle 1993 PMID 8392820 |
| Oxymetazoline 0.05% spray, 30 min pre-descent | Intranasal | **No statistically significant reduction** in adult barotrauma symptoms in RCT | Mirza 2005; DeCruz (in Mirza review) |
| Xylometazoline spray on healthy ears | Intranasal | No change in ET opening rate (tympanometry, sonotubometry); only duration of opening slightly longer | Joshi 2020 PMID 31964436 |
| Oxymetazoline in children with tympanostomy tubes | Intranasal | No change in 9-step or forced-response parameters | Lildholdt 1982 PMID 6889803 |
| Mometasone furoate nasal spray (chronic, 12 wk) | Intranasal corticosteroid | ETDQ-7 significantly lower vs control (pediatric SOM); adult CRS+ETD: post-medication ETDQ-7 drop ≈ 7.4 (95% CI −10.82 to −3.99) | Yu 2024 PMID 39671881; Adams 2024 PMID 37646427; Chen T 2022 PMID 34919345 |
| Postoperative antihistamine nasal spray | Intranasal | β = −8.70 (95% CI −14.20 to −3.20) ETDQ-7 improvement | Daum 2024 PMID 38037398 |
| Oral antihistamine (chlorpheniramine) during cold | PO | **No significant effect** on ET function or ME pressure vs placebo | Doyle 1988 PMID 3282216 |

**Modeling rule:** oral pseudoephedrine → pre-descent MEB RR ≈ 0.7 (adults only, weak evidence). Topical decongestants → RR ≈ 0.95 (null). Intranasal steroids and chronic-use antihistamine sprays → RR ≈ 0.6–0.7 for chronic AR/CRS baseline, not acute URI.

---

## 6. Allergic rhinitis comorbidity

AR prevalence in Chinese civil aircrew: **23.38%** (Bai 2021). Subjects with AR had rhinovirus-induced ET dysfunction of **earlier onset** but similar magnitude vs. non-atopic controls (Doyle 1992 PMID 1316390). AR + CRS + nasal polyposis drives the chronic ETDQ-7 elevation (+10–15 points) and elevated tympanometric abnormality rate (12.7% vs 4.4%, P<0.001; García-Callejo 2025 PMID 40122164). Model AR as a permanent +2 mmHg PET offset and a ×1.3 RA multiplier even at baseline; during URI, the AR-positive pilot compounds: ×1.3 × (acute URI multiplier).

---

## URI Effect Modifier Table (plug-in for pathophysiology module)

| State | RA multiplier | PO′ shift (daPa) | PET shift (mmHg) | Equalization rate × | Valsalva success × | Per-descent MEB RR |
|---|---|---|---|---|---|---|
| Healthy baseline | 1.0 | 0 | 0 | 1.0 | 1.0 | 1.0 (ref) |
| URI day 1–3 (early) | 2.0 | +80 | +4 | 0.6 | 0.7 | 2.5 |
| URI day 4–7 (peak) | 3.0–4.0 | +150 | +8 | 0.4 | 0.5 | 3.5–5.0 |
| URI day 8–14 (recovery) | 1.8 | +60 | +3 | 0.75 | 0.8 | 2.0 |
| URI day 15–21 (residual) | 1.3 | +20 | +1 | 0.9 | 0.9 | 1.3 |
| URI day 22–28 | 1.1 | +5 | 0 | 0.95 | 0.95 | 1.1 |
| Chronic AR (no URI) | 1.3 | +30 | +2 | 0.85 | 0.9 | 1.5 |
| AR + acute URI (peak) | 4.0–5.0 | +180 | +10 | 0.35 | 0.45 | 5.0–7.0 |
| CRS ± NP (chronic) | 1.5 | +50 | +3 | 0.8 | 0.85 | 2.0 |

**Notes on the table**
- RR column is a calibration target. Priors should be fitted to achieve the 5.8% observed MEB prevalence in the Colombian cohort when convolved with baseline URI exposure probability.
- PET and PO′ shifts are modeler priors based on extrapolation from Doyle/Bluestone primate-ET forced-response studies (no direct human ET tissue-pressure measurement in URI exists).
- RA fold-increase is bracketed to reproduce the McBride 1989 day-2 "50% ears with no tubal function" observation.
- All multipliers are independent of the Valsalva pressure magnitude itself; Kanick & Doyle (2005) PV equations should be used upstream with these multipliers applied to RA, PO′, PET.

---

## Key references (PMID)

- Buchman CA et al. 1994, Arch Otolaryngol. **PMID 7934605** (rhinovirus → ME effusion).
- McBride TP et al. 1989, JAMA. **PMID 2548538** (9-step test, ME pressure, post-cold).
- Doyle WJ et al. 1999. **PMID 10890787** (illness / asymptomatic URI ME pressure).
- Doyle WJ et al. 2000, Auris Nasus Larynx. **PMID 10996490** (influenza A, ME pressure).
- Doyle WJ et al. 1992, Ann Otol Rhinol Laryngol. **PMID 1316390** (allergic vs non-allergic rhinovirus).
- Doyle WJ et al. 1993. **PMID 8392820** (pseudoephedrine+atropine null).
- Doyle WJ et al. 1988. **PMID 3282216** (chlorpheniramine null).
- Sperber SJ et al. 1992. **PMID 1323974** (interferon, ME pressure abnormalities).
- Boel NM, Klokker M. 2017, Aerosp Med Hum Perform. **PMID 28061917** (pilot URI/barotrauma survey).
- Rosenkvist L et al. 2008. **PMID 18856186** (prior Danish pilot survey).
- Landolfi A et al. 2009. **PMID 20027855** (hypobaric chamber barotitis prevalence 2.4%).
- Bai Y et al. 2021, AMHP. **PMID 33357269** (AR in Chinese aircrew).
- Tournoy KG et al. 2024. **PMID 39675736** (divers; ENT comorbidity OR 9.3).
- Mirza S, Richardson H. 2005. **PMID 15949100** (otic barotrauma review / pseudoephedrine RCTs).
- Basu A. 2007, Clin Evid. **PMID 19450303** (systematic review, interventions pre-flight).
- Joshi KS et al. 2020, J Laryngol Otol. **PMID 31964436** (xylometazoline null on ET).
- Shupak A et al. 1996, Laryngoscope. **PMID 8583858** (forced response, ME gas composition).
- Chen T et al. 2022. **PMID 34919345** (CRS + ETD meta-analysis, ETDQ-7 pooled).
- Chang MT et al. 2020. **PMID 32343633** (ESS → ETDQ-7 improvement).
- Yu X et al. 2024. **PMID 39671881** (mometasone → ETDQ-7).
- Adams SM et al. 2024. **PMID 37646427** (CRS medical management → ETDQ-7).
- Daum R et al. 2024. **PMID 38037398** (antihistamine spray → ETDQ-7 β −8.70).
- García-Callejo FJ et al. 2025. **PMID 40122164** (CRSwNP → ETD, AOM 18.1%).
- Yu Q et al. 2025. **PMID 40319775** (COVID-19, OME, MEF persistence).
- Zhang Y et al. 2024. **PMID 38356273** (SARS-CoV-2 in MEE to day 28).

**Caveat for the modeler:** Question 3 parameters (PET mmHg, luminal diameter %, RA fold) are not directly measured during human URI. They are inferred from (a) primate forced-response studies and (b) the requirement that downstream outputs (ME pressure distribution, 9-step failure rate, Valsalva success) reproduce experimental-cold human data. Treat as calibration priors with the uncertainty ranges shown, not as literature-derived constants.
