# Mathematical Models of Middle Ear Barotrauma (post-Kanick-Doyle 2005)

**Target audience:** Physician-scientist building a physics-informed MEB risk model for hypobaric chamber training.
**Scope:** Peer-reviewed extensions, parameter updates, and validation data published after Kanick & Doyle (*J Appl Physiol* 98:1592-1602, 2005; PMID 15608090).
**Date of review:** 2026-04-18. Every numeric claim below is tagged with a PMID or DOI. Parameters not verifiable in retrieved sources are flagged as such.

---

## 1. Mathematical model extensions (2005-2026)

The Kanick-Doyle architecture (two-compartment lumped model, Hagen-Poiseuille trans-ET flow, passive+active ET opening governed by P_O'/P_C'/R_A, swallow-driven equilibration) has been **extended but not displaced**. Three parallel developments dominate the post-2005 literature:

- **Formal multi-species, multi-pathway gas-exchange framework (Doyle 2017, PMID 28917121, DOI 10.1016/j.heares.2017.08.005).** Doyle reformulated MEPR as a time-iterated, species-resolved balance combining (a) Fick diffusion across the tympanic membrane, round window, and mucosa; (b) Poiseuille bulk flow during ET openings. Core equation: P^ME_{g,i+1} = Σ_s [P^ME_{s,i} + (1/(β^ME_s·V^ME)) Σ_P K^P_s (P^C_s - P^ME_s)] where β is species capacitance and K^P_s pathway species-conductance (PMID 28917121). This is the most direct generalization of the Kanick-Doyle 2005 model. The paper validates the framework against "physiologic, pathologic and non-physiologic conditions" generally (abstract); it does not report an explicit cabin-descent simulation. Inclusion of the previously ignored TM and RW pathways is expected to alter the trajectory of V^ME during slow pressure changes, but this would need to be verified by direct simulation.

- **Finite-element / multi-scale models of ET opening mechanics (Ghadiali group).** A sequence of 2D and 3D FEM papers treats the ET as a collapsible compliant tube opened by TVP/LVP force vectors applied to histologically-reconstructed cartilage, mucosa, and Ostmann's fat (Ghadiali 2004, PMID 15047672; Ghadiali 2010, PMID 20413236, DOI 10.1016/j.anl.2010.02.008; Sheer 2012, PMID 21996354, DOI 10.1016/j.medengphy.2011.09.008; Malik 2016, PMID 26891171, DOI 10.1002/cnm.2776; Malik & Ghadiali 2019, PMID 29395489, DOI 10.1016/j.clinbiomech.2018.01.012). These supersede the constant-RA Hagen-Poiseuille assumption: the effective trans-ET resistance is a time-varying function of TVP/LVP timing, mucosal adhesion, cartilage stiffness, and viscoelastic wall properties (Ghadiali 2010, PMID 20413236).

- **Mastoid as a multi-compartment gas reserve.** Doyle's 2007 description (PMID 17174408) introduced the "MACS buffering efficiency" M, with the fitted value M ≈ 0.2 in adult humans implying the mastoid acts as a rate-limiter on ME pressure change. Alper et al. (PMID 21271597, DOI 10.1002/lary.21275) confirmed experimentally that N2O time-constants scale inversely with mastoid volume, supporting a multi-compartment extension to Kanick-Doyle (their original model used a single lumped V^ME = 8.75 mL). These data motivate splitting V^ME into a tympanum-proximal and a mastoid gas reserve.

- **Time-varying mucosal compliance / inflammation.** Yuksel 2005 (PMID 15882822) and Teixeira 2015-2017 (PMIDs 26152838, 26611245, 28103698) documented that inflammation (histamine, PGD2) raises and vasoconstrictors (pseudoephedrine, oxymetazoline) lower the trans-mucosal N2O rate-constant. These results justify making the mucosal conductance K^P_s a time-varying, cold-modulated parameter, which is absent from Kanick-Doyle 2005.

- **CFD has been embedded inside FEM** (Sheer 2012 used CFD to quantify lumen dilation and airflow; PMID 21996354), but no stand-alone CFD simulation of the 30-second descent profile has been published.

## 2. Dose-response / hazard functions for barotitis onset

No validated functional form (logistic, Weibull, time-above-threshold integral) for P(barotitis | ΔP, ΔP/Δt, ∫|ΔP|dt) has been published. The closest data are **categorical-incidence** not continuous hazard:

- Italian Air Force cohort of 314 aircrew exposed to 25,000 ft vs 35,000 ft chamber profiles: acute barotitis 2.3%, delayed ear pain 9.2% (Morgagni 2012, PMID 22764614). Altitude was a significant categorical predictor of delayed pain; history of ENT disease predicted delayed pain at 35,000 ft; abnormal ENT findings predicted acute barotitis.
- 1,241 Italian airmen over 2003-2009: barotitis 1.5% overall, 1.1% in pre-chamber-selection group vs 2.7% in control group (Morgagni 2010, PMID 20824995).
- 335 military pilots (tympanometry-screened): barotitis prevalence 2.4% (Landolfi 2009, PMID 20027855).

Dose information is limited to peak altitude; rate-of-change dependence is absent from human data. A dynamic rabbit model provides rate-dependent pathology grading (Wang 2019, PMID 31331419, DOI 10.3357/AMHP.5167.2019): 100 m·s⁻¹ pressure-change rate produced significantly more severe histopathology than 50-75 m·s⁻¹ (P<0.01), but altitude (6,562 vs 13,123 ft) did not (P>0.05). A hazard function will have to be fitted from these categorical/animal data or newly collected chamber data — this is a clear gap.

## 3. Hypobaric-chamber-specific models

No published physics-informed model is parameterized specifically for chamber profiles (1,000-10,000 ft·min⁻¹ descent). The rabbit model (Wang 2019, PMID 31331419) provides the only rate-resolved experimental anchor for chamber-like profiles. The Italian Air Force dataset (Morgagni 2012, PMID 22764614) provides human chamber-incidence data across two fixed profiles. These two sources constitute the currently available, chamber-specific validation set — both are outside Kanick-Doyle's original validation (Groth 1986 used slower pressure-chamber descents).

## 4. Key parameter updates (post-2005)

| Parameter | Kanick-Doyle 2005 | Post-2005 revision | Source |
|---|---|---|---|
| P_O' (passive ET opening) | 26 mmHg (~350 mmH2O) | 458 ± 160 daPa (≈ 34 mmHg) pre-BDET in adults with ETD + ventilation tubes (**diseased cohort, not a normative revision of Kanick-Doyle's healthy-ear value**); 308 ± 173 daPa post-BDET | Alper 2020, PMID 32176133 |
| P_C' (closing pressure) | 7 mmHg (~100 mmH2O) | 115 ± 83 daPa pre-BDET → 72 ± 81 daPa post-BDET (**ETD cohort, not normative**) | Alper 2020, PMID 32176133 |
| R_A (active resistance) | 2 mmHg·mL⁻¹·min⁻¹ (constant) | Time-varying, waveform-dependent; resistance drops sharply with TVP onset and rises with LVP timing (FEM fit) | Ghadiali 2010, PMID 20413236 |
| Transmucosal N2 rate | Perfusion-limited, lumped | Perfusion-limited confirmed; asymmetric ME→blood / blood→ME ratio ≈ 13 | Doyle 2007, PMID 17305281 |
| Transmucosal O2 rate-const | Not resolved | 0.011 ± 0.009 mmHg·min⁻¹·mmHg⁻¹ (t1/2 ≈ 61.6 min) | Doyle 2011, PMID 21330076 |
| Transmucosal CO2 rate-const | Not resolved | 0.062 ± 0.034 mmHg·min⁻¹·mmHg⁻¹ (t1/2 ≈ 11.1 min); CO2/O2 ratio 8.1 ± 4.0 | Doyle 2011, PMID 21330076 |
| V^ME (total volume) | 8.75 mL lumped | Volume should be split into tympanum + mastoid sub-compartments; MACS buffering efficiency M ≈ 0.2 in adults | Doyle 2007, PMID 17174408; Alper 2011, PMID 21271597 |
| TM gas conductance | Ignored | TM is permeable to CO2 and O2 at physiologic gradients; O2/CO2 conductance ratio inconsistent with a pure water/lipid barrier | Yuksel 2009, PMID 18728916 |
| Fractional gradient equilibrated (FGE) per swallow | Implicit in R_A | Adult no-disease controls FGE = 0.32 (CI 0.21-0.43); recurrent AOM history FGE = 0.16 (CI 0.08-0.24), both measured at -194 to -203 daPa pre-swallow pressure | Mandel 2016, PMID 26626132 |
| TM admittance during flight | Constant | Drops ~20% at cruise altitude vs airport (22.7% humidity); admittance-humidity slope ≈ 0.00315 mmho/%RH | Morse 2013, PMID 23887775 |
| VTMmax/VME ratio | 0.025 mL / 8.75 mL | No post-2005 revision found | — |
| Barotitis threshold | 250 mmH2O (18 mmHg) | No post-2005 revision found | — |
| Baromyringitis threshold | 1,300 mmH2O (96 mmHg) | No post-2005 revision found | — |
| Swallow frequency Sf | 5.2/hr cruise, 31/hr descent | No post-2005 revision of the Kanick-Doyle values found | — |

## 5. Validation datasets

- **Groth 1986** (Kanick-Doyle original) — passive chamber data.
- **Pittsburgh pressure-chamber protocol** (adults and children; Swarts 2011, PMID 21585150; Swarts 2014, PMID 24828350; Mandel 2016, PMID 26626132; Doyle 2014, PMID 24834936) — FGE at ±200 daPa, stratified by age and history of otitis media. This is the most extensive post-2005 dataset for calibrating ET opening efficiency.
- **Italian Air Force chamber cohort** (1,241 aircrew; Morgagni 2010, PMID 20824995; 314 aircrew Morgagni 2012, PMID 22764614; 335 pilots Landolfi 2009, PMID 20027855) — categorical barotitis incidence at real chamber-training altitudes.
- **Rabbit dynamic MEB model** (Wang 2019, PMID 31331419) — histopathology graded against pressure-change rate (50, 75, 100 m·s⁻¹) and altitude (6,562, 13,123 ft). Provides rate-dependent severity scoring.
- **Balloon-dilation pre/post-BDET cohort** (Alper 2020, PMID 32176133) — paired FRT + pressure-chamber data, useful for sensitivity analysis across a wide range of P_O' and P_C'.
- **N2O inhalation cohorts** (Alper 2011, PMID 21271597; Teixeira 2015, PMID 26152838) — time-constant data for calibrating multi-compartment gas exchange.
- **Morse 2013** (PMID 23887775) — in-flight TM admittance data across humidity gradients, useful if you want to model humidity-driven TM drying as a second-order effect.

## Recommendations for deep reading

1. **Doyle WJ (2017). *A formal description of middle ear pressure-regulation.* Hearing Research. PMID 28917121. DOI 10.1016/j.heares.2017.08.005.** The canonical post-Kanick-Doyle model. Start here — direct mathematical successor with explicit species-resolved equations ready for code translation.
2. **Malik JE & Ghadiali SN (2019). *Multi-scale modeling of an upper respiratory airway: Effect of mucosal adhesion on Eustachian tube function in young children.* Clinical Biomechanics. PMID 29395489. DOI 10.1016/j.clinbiomech.2018.01.012.** Most recent and methodologically complete FEM/multi-scale model; gives tissue parameters (cartilage stiffness, mucosa elasticity, adhesion force) needed to replace constant-R_A.
3. **Alper CM et al. (2011). *Role of the mastoid in middle ear pressure regulation.* Laryngoscope. PMID 21271597. DOI 10.1002/lary.21275.** Empirical validation for multi-compartment V^ME split and the mastoid-as-gas-reserve extension.
4. **Doyle WJ (2007). *The mastoid as a functional rate-limiter of middle ear pressure change.* International Journal of Pediatric Otorhinolaryngology. PMID 17174408.** Derives the M buffering-efficiency framework (M ≈ 0.2 fit to adult data); cleanly integrable with Kanick-Doyle's V^ME term.
5. **Morgagni F et al. (2012). *Predictors of ear barotrauma in aircrews exposed to simulated high altitude.* Aviation, Space, and Environmental Medicine. PMID 22764614.** Largest modern chamber-training cohort with per-profile barotitis incidence; essential anchor for fitting a chamber-specific hazard function.
6. **Alper CM et al. (2020). *Change in Eustachian Tube Function With Balloon Dilation in Adults With Ventilation Tubes.* Otology & Neurotology. PMID 32176133. DOI 10.1097/MAO.0000000000002559.** Paired pre/post-BDET values for P_O', P_C', and equilibration percentages; directly usable as stratified inputs in a patient-specific risk model (ETD cohort, not normative).

## Gaps the physician-scientist should flag

- No continuous hazard function P(MEB | ΔP, dP/dt) exists; it will have to be newly fitted, probably from the Italian AF and Wang rabbit datasets.
- VTMmax, barotitis thresholds (250, 1,300 mmH2O), and swallow frequencies (5.2/hr, 31/hr) remain at Kanick-Doyle 2005 values — no retrieved post-2005 paper revises them. Document this as an assumption if retained.
- No hypobaric-chamber-specific human physics-informed model has been published. The proposed project fills a literature gap.
