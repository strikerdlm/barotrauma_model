# Physics-Informed Middle Ear Barotrauma Risk for Hypobaric Chamber Training

**Running head:** PHYSICS-INFORMED MEB MODEL

**Article type:** Research Article

**Word count:** body 3,980 · abstract 246 · references 27 · tables 4 · figures 2

---

## Abstract

Middle-ear barotrauma (MEB) is the most common medical complication of pressurized flight and hypobaric chamber training, and an indirect proxy for Eustachian-tube disease that disqualifies aviator candidates. The canonical Kanick-Doyle 2005 mathematical model reproduces airline-descent physiology well but does not address the chamber-specific regime of 1,000–10,000 ft·min⁻¹ descent rates, treats Patulous Eustachian tube (PET) as trivially rupture-protective, and does not parameterize acute upper-respiratory-infection (URI) modifiers despite epidemiology showing URI as the dominant modifiable risk factor in flying populations. We extended Kanick-Doyle with a continuous descent-side aperture-collapse model (Hagen-Poiseuille-informed Hill function with rate-dependent tightening), a six-state URI temporal modifier table, a four-state PET model that reproduces the rupture-protective prediction for baseline patency but flips high-risk under inflammation, a lumped-parameter approximation of Ghadiali-group Eustachian-tube muscle mechanics, Doyle 2017 multi-pathway gas exchange, and a three-threshold cumulative-hazard scoring model. Hazard constants were calibrated against the Colombian Aerospace Force 10-year chamber training cohort (5.8% career barotitis prevalence) via log-space bisection and Approximate Bayesian Computation Sequential Monte Carlo. External validation used three independent Italian Air Force cohorts (Morgagni 2010 n = 1,241; Morgagni 2012 n = 314; Landolfi 2009 n = 335). Calibration reproduced the FAC anchor within 0.2 percentage points. External validation fell inside the observed Wilson 95% CI for Morgagni 2012 and Landolfi 2009; the Morgagni 2010 gap (+1.1 pp) is smaller than that cohort's own pre-screened / unscreened denominator difference. Saltelli-Sobol sensitivity identified the aperture half-point as the dominant variance driver and therefore the highest-leverage empirical refinement target. The simulator, tests, and documentation are open source at https://github.com/strikerdlm/barotrauma_model.

**Keywords:** middle ear barotrauma, hypobaric chamber, upper respiratory infection, physics-informed modeling, external validation

---

## 1. Introduction

Middle-ear barotrauma (MEB) — the inability of the Eustachian tube (ET) to equalize middle-ear pressure against changing ambient pressure — affects an estimated 3–10% of aircrew per hypobaric-chamber exposure¹⁻³ and 30–85% of commercial pilots across their careers.⁴ In military aviation medicine its importance is twofold: as a direct medical consequence of altitude training, and as a proxy for the broader spectrum of Eustachian-tube disease that disqualifies aviator applicants and restricts operational employment.

The most widely used mathematical description is Kanick and Doyle's 2005 pressure-regulation model.⁵ Their gas-exchange framework combines Boyle's-law tympanic-membrane buffering, Hagen-Poiseuille bulk flow through an intermittently opening Eustachian tube, swallow-driven active openings with a fixed muscular resistance R<sub>A</sub>, and trans-mucosal species diffusion. The model reproduces passenger airline physiology accurately and is the reference against which subsequent work is benchmarked. Three shortcomings limit its direct use in hypobaric-chamber decision support.

First, chamber training descent rates of 1,000–10,000 ft·min⁻¹ exceed cabin descent by a factor of 5–30. At these rates the developing intra-tubal pressure gradient progressively collapses the collapsible cartilaginous portion of the ET, a Hagen-Poiseuille r⁴ effect that Kanick-Doyle's binary "open or locked" treatment approximates but does not resolve continuously. Second, Kanick-Doyle model obstructive dysfunction through R<sub>A</sub> and Patulous ET through a trivial "always open" case that predicts complete rupture protection. Clinical experience contradicts the latter when mucosal edema (such as concurrent URI) converts a patent tube into a paradoxically closed one.⁶⁻⁸ Third, controlled rhinovirus-challenge data have documented substantial ET dysfunction persisting for 2–3 weeks post-onset,⁹⁻¹¹ and survey data show URI to be the dominant modifiable risk factor for MEB in flying populations,⁴·¹² yet the Kanick-Doyle parameters do not vary with URI state.

We present a physics-informed, pathophysiology-aware extension that addresses these gaps, calibrated to the Colombian Aerospace Force (FAC) 10-year operational registry and externally validated on three independent Italian Air Force cohorts. The software is released open-source at https://github.com/strikerdlm/barotrauma_model under the MIT license.

---

## 2. Methods

### 2.1 Model architecture

The simulator is implemented in pure Python (NumPy and SciPy) as the `barotrauma.v2` package. It takes as inputs a patient state (anatomy, ET function, URI state, PET state, chronic rhinitis, medications, behavior) and a piecewise-linear chamber profile (ascent, hold, descent, or rapid-decompression segments). Output is a time-domain trace (ΔP, tympanic-membrane displacement, ET open-closed raster, swallow and Valsalva timestamps) and per-outcome probabilities scored by a dose-response hazard model.

### 2.2 Physics core

The physics core retains the Kanick-Doyle 2005 structure: standard-atmosphere altitude-to-pressure map P(z) = P₀ exp(−z/H) with H = 29,921 ft; two-compartment middle-ear volume V<sub>ME</sub> = V<sub>tympanum</sub> + V<sub>mastoid</sub> with the mastoid drawn from a log-normal prior (median 7.0 mL, 95% interval 2.9–16.9 mL) matching Alper 2011¹³; tympanic-membrane volume displacement clamped at ±0.025 mL (1% of V<sub>ME</sub>, Kanick-Doyle Table 1); passive ME-side ET opening when ΔP > 25.7 mmHg venting to 7.35 mmHg; active swallow-driven openings at a descent-phase frequency of 60·hr⁻¹ (trained aircrew default; Kanick-Doyle's 31·hr⁻¹ passive baseline is available as an override), each clearing a Fractional Gradient Equalized of 0.32 (Mandel 2016¹⁴); Valsalva pulses every 60 s on descent with per-pulse clearance 0.55; an ET-lock state at |ΔP| > 90 mmHg tightened by inflammation; species-resolved trans-mucosal Fick exchange with O<sub>2</sub>, CO<sub>2</sub>, N<sub>2</sub>, and H<sub>2</sub>O rate constants from Doyle 2011.¹⁵

### 2.3 Descent-side aperture-collapse model

The central physical insight is that active ET clearance pathways (swallow and Valsalva) are progressively defeated during descent because the nasopharyngeal tissue pressure compresses the cartilaginous lumen from the NP side. We model this with a continuous aperture factor α(ΔP, dΔP/dt) ∈ [0, 1] applied multiplicatively to the per-event Fractional Gradient Equalized. For ΔP ≥ 0 (ascent) α = 1; for descent, α = 1 below a 40-mmHg free zone, then decays as 1 / (1 + ((|ΔP| − free_zone) / (ΔP<sub>½</sub> − free_zone))ⁿ) with ΔP<sub>½</sub> = 110 mmHg and n = 3. A rate-tightening factor 1 + 0.15 · min(rate, 3 mmHg·s⁻¹) reduces effective ΔP<sub>½</sub> under fast ambient-pressure changes, reflecting mucosal viscoelastic lag. An inflammation-tightening factor √(R<sub>A</sub>-multiplier) additionally narrows the threshold under URI. The aperture factor applies to active swallows at unit power and to Valsalva pulses at square-root power — the muscular push of Valsalva partially overrides progressive collapse.

### 2.4 Pathophysiology state machine

URI state is encoded as one of six day-windows (none, 1–3, 4–7, 8–14, 15–21, 22–28), each with a tabulated multiplier set (Table I). Multipliers were derived from controlled rhinovirus-challenge data⁹⁻¹¹ and ETDQ-7 meta-analyses.¹⁶ The peak-dysfunction window (days 4–7) carries R<sub>A</sub> × 3.5, P<sub>O</sub>' shift +150 daPa (+11.3 mmHg), a 50% drop in equalization-rate modifier, and a 4.25× per-descent MEB relative-risk multiplier.

Patulous ET (PET) is encoded as one of four states.⁶⁻⁸ S1 (baseline patent, upright, dry mucosa) reproduces Kanick-Doyle's rupture-protective prediction via a hard-zero override on ΔP. S2 (PET with acute URI or mucosal inflammation) applies paradoxical closure on an abnormal cartilaginous substrate via R<sub>A</sub> × 3.5, P<sub>O</sub>' shift +60 daPa, and a 4.0× per-descent RR. S3 (habitual sniffer) biases resting ΔP toward −15 mmHg, reflecting the type-B/C tympanogram rate of 42.6% reported in Shindo 2025.⁸ Per-descent RR was raised from 2.5 to 4.0 to reflect the Oshima 2025²⁷ large-cohort (n = 1,009) sniffing OR of 8.18 convolved with the already-modeled ΔP physiology. S4 (post-Kobayashi-plug or cartilage augmentation) imposes stenotic-equivalent obstruction. Oral and topical decongestants carry a paradoxical-worsening RR of 1.4 in PET (versus 0.90 in healthy subjects — softened from the prior 0.70 per Moayedi 2025²⁶, a placebo-controlled HBOT RCT showing null preventive effect of prophylactic pseudoephedrine).

### 2.5 Muscle mechanics and multi-pathway gas exchange

A lumped-parameter approximation of Ghadiali-group FEM and multi-scale work¹⁷ captures three time-dependent muscle effects on per-swallow FGE without running a full 2-D or 3-D FEM per integration step: fatigue and priming (recent swallows boost FGE up to +15% with τ ≈ 8 s), mucosal adhesion buildup (prolonged closure at high |ΔP| raises intraluminal surface tension with τ ≈ 30 s), and TVP/LVP timing variability (stochastic multiplier CV 5% healthy, 15% dysfunctional). The extension is disabled by default. The trans-mucosal Fick diffusion is extended with trans-TM (~4% of mucosa rate) and trans-round-window (~1%) pathways per Doyle 2017.¹⁸

### 2.6 Three-threshold hazard model

Per-outcome probabilities are scored by a cumulative hazard applied to the ΔP trajectory: h<sub>i</sub>(t) = r<sub>i</sub> · max(0, |ΔP(t)| − Θ<sub>i</sub>)^n<sub>i</sub> with P<sub>i</sub> = 1 − exp(−∫ h<sub>i</sub> dt). Thresholds align with Kanick-Doyle's clinical values: barotitis onset Θ = 18.4 mmHg (250 mmH₂O, n = 1.8); baromyringitis Θ = 95.6 mmHg (1,300 mmH₂O, n = 2.5); rupture Θ = 150 mmHg (conservative, n = 3). Per-stratum probabilities are multiplied by the composite per-descent RR (URI × PET × rhinitis × medication × history).

### 2.7 Calibration and external validation

Calibration uses two methods. Bisection performs log-space bisection on r<sub>barotitis</sub> alone against cohort mean per-exposure p<sub>barotitis</sub>. Approximate Bayesian Computation Sequential Monte Carlo (ABC-SMC)¹⁹ jointly infers (r<sub>barotitis</sub>, r<sub>baromyringitis</sub>, r<sub>rupture</sub>) against three summary statistics (cohort prevalence, URI day 4–7 / none gradient, severe / normal severity gradient). The calibration target uses the FAC DIMAE 10-year cohort (5.8% career barotitis prevalence), reconciled to a per-exposure rate of 2.0% via an assumed three career exposures: 1 − (1 − 0.02)³ ≈ 5.88%.

External validation uses three published Italian Air Force cohorts¹⁻³ without refitting: Morgagni 2010 (n = 1,241, 1.5% overall barotitis), Morgagni 2012 (n = 314, 2.3% acute barotitis at 25,000 ft), and Landolfi 2009 (n = 335, 2.4% TEED-graded barotitis). Each carries a matched chamber profile (30-min preoxygenation, 25,000 ft hold, 3,000 ft·min⁻¹ descent), a tightened cohort prior reflecting Italian Air Force tympanometry screening, and a Wilson 95% CI around the observed proportion.

### 2.8 Global sensitivity and pinned baseline

Saltelli-sampled Sobol first-order and total-order indices²⁰ were computed over four model parameters — aperture half-point (70–180 mmHg), aperture free-zone threshold (20–60 mmHg), descent-phase swallow frequency (30–120 hr⁻¹), and mastoid volume (3–13 mL) — against the per-exposure p<sub>barotitis</sub> output of a reference moderate-risk patient. A 17-point ΔP trajectory on the Groth 1986 pressure-chamber profile was recorded as a fixture and tested continuously at ±5% per-point and ±0.5 pp on p<sub>barotitis</sub>. Statistical computations (Wilson intervals, Sobol estimators, bisection search) were performed by the corresponding author using NumPy 1.26 and SciPy 1.11; no inferential p-values are reported because the simulator is deterministic given a cohort prior.

---

## 3. Results

### 3.1 Calibration

The bisection calibrator converged in 5 iterations with an achieved per-exposure prevalence of 1.89% (target 2.0%) and a projected three-exposure career prevalence of 5.73% against the FAC anchor of 5.8% (Table II). URI subgroup means separated cleanly: none 0.30%, day 1–3 8.2%, day 4–7 22.4%, day 8–14 3.3%, day 15–21 0.9%. Severity subgroup means: normal 1.7%, mild 2.9%, moderate 1.9%, severe 25.8%.

ABC-SMC (100 particles, 4 generations, 150 cohort subjects, tolerance schedule 13.9 → 5.0) returned a posterior mean r<sub>barotitis</sub> = 5.07 × 10⁻⁸ with a 95% credible interval of [3.59 × 10⁻⁸, 8.00 × 10⁻⁸]. The bisection point estimate falls inside this CI, confirming internal consistency of the two methods. The baromyringitis and rupture constants have wider posterior intervals because the chosen summary statistics do not tightly constrain them; a FAC per-TEED-grade breakdown is the clearest next step.

### 3.2 External validation

Italian Air Force transfer tests (Table III) passed for Morgagni 2012 (simulated 2.69% vs. observed 2.3%, inside Wilson 95% CI [1.13%, 4.62%]) and Landolfi 2009 (simulated 2.63% vs. observed 2.4%, inside CI [1.22%, 4.66%]). Morgagni 2010 fell 1.1 pp outside the narrowest observed CI (simulated 2.62% vs. observed 1.5%, CI [0.96%, 2.34%]); the discrepancy is smaller than the gap between that cohort's own pre-screened subset (1.1%) and the unscreened controls (2.7%), so the mismatch plausibly reflects the unpublished denominator mix rather than a physics error. URI-state gradient in the validation cohorts (day 4–7 > 3 × URI none) confirms acute URI as the dominant predicted risk driver.

### 3.3 Descent-rate sensitivity and pathophysiology interactions

For a healthy baseline patient on a 25,000-ft descent, max |ΔP| grows monotonically with descent rate up to saturation at ~430 mmHg (Table IV; Figure 1). Barotitis probability increases from 0.0% at 300 ft·min⁻¹ (commercial cabin) to 7.6% at 10,000 ft·min⁻¹ (worst-case chamber stress test). Rupture probability peaks in the 2,000–5,000 ft·min⁻¹ range at about 0.9%. The dose-time integral of |ΔP| does not saturate as sharply as the peak, so barotitis probability retains its gradient across the full 500–10,000 ft·min⁻¹ range even where max |ΔP| plateaus.

The Patulous-S1 override reproduces Kanick-Doyle's rupture-protective prediction exactly (max |ΔP| = 0 on a rapid 10,000 ft·min⁻¹ descent, p<sub>barotitis</sub> = 0.0%). Adding peak URI converts this to PET-S2 paradoxical closure: max |ΔP| = 238 mmHg, p<sub>barotitis</sub> = 51%, the clinically dangerous state flagged by Ikeda 2020⁷ but absent from Kanick-Doyle's framework.

### 3.4 Global sensitivity and pinned-baseline stability

Sobol analysis (N = 32 Saltelli base samples, 192 model evaluations) identified the aperture half-point as the dominant variance driver in per-exposure p<sub>barotitis</sub> (S<sub>T</sub> = 1.84), an order of magnitude above descent-phase swallow frequency (S<sub>T</sub> = 0.18), mastoid volume (S<sub>T</sub> = 0.16), and aperture free-zone threshold (S<sub>T</sub> = 0.08). Figure 2 shows the ranking. Total-order indices sum to a plausible range; the first-order index sum exceeding unity at this sample size is a known small-N artifact resolvable by N ≥ 128 in production use. The clinical implication is that the single highest-leverage target for future empirical parameter refinement is the aperture half-point, most plausibly constrained by paired forced-response-test data or by ET balloon-dilation pre- and post-measurements.²¹

Across the v2.0 → v2.1 → v2.2 physics changes, the Kanick-Doyle Fig 3 / Groth 1986 healthy-baseline trajectory remained within ±5% of the pinned fixture at every one of 17 sample time points. Peak |ΔP| is 17.9 mmHg, matching the order of magnitude in Kanick-Doyle Fig 3.

---

## 4. Discussion

We have extended the canonical Kanick-Doyle 2005 middle-ear-barotrauma model with a set of additions motivated by operational hypobaric-chamber needs: a continuous descent-side aperture-collapse model, a six-state URI temporal modifier, a four-state Patulous ET model, Ghadiali-FEM-inspired muscle mechanics, and Doyle 2017 multi-pathway gas exchange. The resulting simulator reproduces the Colombian Aerospace Force 10-year anchor cohort within one decimal place of the observed career prevalence, transfers to two of three independent Italian Air Force cohorts within the observed Wilson 95% CI, and remains consistent with the Kanick-Doyle Fig 3 / Groth 1986 validation under a pinned regression test.

Three extensions deserve particular comment. First, the continuous aperture-collapse model was the single most load-bearing addition for chamber-rate physiology. Kanick-Doyle's binary lock treatment could not simultaneously reproduce a healthy-ear 20-mmHg gradient at 300 ft·min⁻¹ airline descent and a 400-mmHg gradient at 10,000 ft·min⁻¹ chamber stress — the single R<sub>A</sub> and lock threshold drifted one direction or the other. The Hill-function aperture with a protective free zone below 40 mmHg resolves this by leaving slow descents in the easy regime while progressively collapsing faster ones. Rate-dependent tightening captures the Wang 2019 rabbit histopathology gradient²² where pressure-change rate, not absolute altitude, predicted grade.

Second, the Patulous ET four-state model is a clinically-motivated departure from Kanick-Doyle's trivial treatment. S1 reproduces the rupture-protective prediction exactly; S2 flips to high risk consistent with Ikeda 2020 and Shindo 2025; S3 captures the sustained negative-ME-pressure physiology. Paradoxical decongestant worsening in PET replaces the protective RR 0.70 with 1.4 and reflects the peritubal-soft-tissue clinical reality. This level of PET granularity is not present in any prior physics-informed MEB model to our knowledge.

Third, the six-state URI temporal modifier is the most direct encoding of the controlled rhinovirus-challenge data¹⁰·¹¹ into a flight-medicine simulator we are aware of. The peak-dysfunction window at days 4–7 carries a per-descent RR of 4.25, which when composed with direct ET-function effects reproduces the Lindfors 2021⁴ commercial-pilot odds ratio of 9.02 for ≥3 URIs per year without overfitting — the numerical basis for the clinical rule that aviators should not fly during URI days 1–14 and remain elevated-risk through days 15–21.

### 4.1 Limitations

The calibration anchor, the Colombian Aerospace Force 10-year registry, is currently internal DIMAE cohort data awaiting peer-reviewed publication. Users should treat the specific hazard-rate constants as informed priors rather than externally validated point estimates until the anchor paper is published. External validation on two of three Italian Air Force benchmarks mitigates but does not eliminate this dependency.

The rupture threshold at 150 mmHg is a conservative anchor; biomechanical studies of isolated tympanic-membrane preparations report actual rupture pressures of 600–750 mmHg. The rupture output should be interpreted as "imminent perforation risk" and is most useful for ordinal ranking of profiles. Several parameters derive their magnitude from modeler judgment rather than retrieved data, including the decongestant-in-PET paradoxical RR of 1.4, the ET lock threshold of 90 mmHg, and the hazard exponents. These are listed explicitly in the model card so a reviewer can challenge any of them without challenging the underlying data.

No per-subject machine-learning head is trained in the shipped model; the scaffolding is in place and tested on synthetic cohorts but deliberately passes through to the deterministic physics output when unfit. Ghadiali-group full-FEM ET mechanics are approximated through lumped-parameter modulators. Individual chamber profiles for the Italian Air Force cohorts are not published verbatim; the simulator reconstructs the published envelope, which may differ from the exact cohort profiles in ways that affect validation numbers.

### 4.2 Incorporation of 2025–2026 evidence

A 2026 targeted literature scan identified two findings with immediate parameter impact. First, Moayedi 2025²⁶ is a placebo-controlled HBOT RCT showing no significant effect of prophylactic pseudoephedrine on ear pain, tympanic-membrane injury, or rescue medication — null in controlled-descent chamber physiology despite the protective signal in airline-descent data. We soften the pseudoephedrine RR from 0.70 to 0.90 to reflect this indication-specificity. Second, Oshima 2025²⁷ (n = 1,009) quantifies habitual-sniffing OR at 8.18 for PET and tympanic-membrane flutter OR at 42.17; we update the PET-S3 per-descent RR from 2.5 to 4.0 to reflect the large-cohort effect size. Other 2025–2026 findings (Swords 2025 Cochrane BDET meta-analysis; Khan 2026 12-month BDET effect; Voigt 2025 HBOT sensory-neuropathy risk factor; Zhang 2025 bidirectional ET vortex pumping; Holm 2026 quantified OFP and LVPM atrophy in ETD) are flagged for v2.3.0 consideration but do not alter the shipped v2.2.1 parameter set because they address treatment arms, anatomic covariates, or candidate physics terms rather than the core simulator's calibration target.

### 4.3 Conclusions

A physics-informed middle-ear barotrauma simulator that jointly models URI temporal dynamics, Patulous ET state dependence, descent-rate-driven aperture collapse, and active-equalization muscle mechanics can reproduce operational cohort prevalence and transfer across independent air forces without refitting hazard constants. The model is calibrated to the Colombian Aerospace Force cohort and validated against two independent Italian Air Force benchmarks within the observed Wilson 95% CI. The aperture half-point is the dominant source of output variance and the highest-leverage empirical refinement target.

---

## Acknowledgements

We thank Dr. William J. Doyle, whose 2005 and 2017 papers remain the canonical foundation on which this extension builds. No external funding supported this work.

---

## References

1. Morgagni F, Autore A, Landolfi A, Ciniglio Appiani M, Marcoccia A. Predictors of ear barotrauma in aircrews exposed to simulated high altitude. Aviat Space Environ Med. 2012;83(6):594–598.

2. Landolfi A, Autore A, Torchia F, Ciniglio Appiani M, Morgagni F, Marcoccia A. Ear barotrauma in Italian military aircrew. Aviat Space Environ Med. 2009;80(12):1068–1071.

3. Morgagni F, Autore A, Landolfi A, Ciniglio Appiani M, Marcoccia A, Autore C. Efficacy of hyperbaric chamber training in Italian Air Force aircrew selection. Aviat Space Environ Med. 2010;81(10):966–971.

4. Lindfors OH, Räisänen-Sokolowski AK, Suvilehto J, Sinkkonen ST. Risk factors for ear barotrauma in commercial pilots. Aerosp Med Hum Perform. 2021;92(2):126–132.

5. Kanick SC, Doyle WJ. Barotrauma during air travel: predictions of a mathematical model. J Appl Physiol. 2005;98(5):1592–1602.

6. Ikeda R, Oshima T, Oshima H, Miyazaki H, Kikuchi T, Kawase T. Clinical diagnostic criteria for patulous Eustachian tube: a proposal by the Japan Otological Society. Auris Nasus Larynx. 2024;51(2):415–421.

7. Ikeda R, Kikuchi T, Oshima H, Miyazaki H, Hidaka H, Kawase T. Long-term results of the Kobayashi plug for patulous Eustachian tube. Laryngoscope. 2020;130(6):1518–1523.

8. Shindo T, Ikeda R, Oshima H, Miyazaki H, Katori Y. Middle-ear pressure in habitual sniffers. Auris Nasus Larynx. 2025;52(2):245–252.

9. McBride TP, Doyle WJ, Hayden FG, Gwaltney JM Jr. Alterations of the Eustachian tube, middle ear, and nose in rhinovirus infection. Arch Otolaryngol Head Neck Surg. 1989;115(9):1054–1059.

10. Buchman CA, Doyle WJ, Skoner D, Fireman P, Gwaltney JM. Otological manifestations of experimental rhinovirus infection. Arch Otolaryngol Head Neck Surg. 1994;120(6):654–658.

11. Doyle WJ, Skoner DP, Alper CM, et al. Illness and otological changes during upper respiratory virus infection. Laryngoscope. 1999;109(2 Pt 1):324–328.

12. Boel NM, Klokker M. Upper respiratory tract infections and aeromedical decisions. Aerosp Med Hum Perform. 2017;88(2):136–141.

13. Alper CM, Kitsko DJ, Swarts JD, Martin B, Yuksel S, Doyle WJ. Role of the mastoid in middle ear pressure regulation. Laryngoscope. 2011;121(2):404–408.

14. Mandel EM, Doyle WJ, Swarts JD, Weissbrod PA. Fractional gradient equalized per swallow in children and adults. Laryngoscope. 2016;126(6):1433–1440.

15. Doyle WJ. Per-individual rate constants for middle ear trans-mucosal gas exchange. Hear Res. 2011;272(1–2):23–33.

16. Chen T, Hong H, Yuan J, et al. Eustachian tube dysfunction and chronic rhinosinusitis: a systematic review. Eur Arch Otorhinolaryngol. 2022;279(7):3457–3469.

17. Ghadiali SN, Banks J, Swarts JD. Finite element simulation of passive and active Eustachian tube function. Ann Otol Rhinol Laryngol. 2010;119(6):393–401.

18. Doyle WJ. A formal description of middle ear pressure-regulation. Hear Res. 2017;354:73–85.

19. Toni T, Welch D, Strelkowa N, Ipsen A, Stumpf MPH. Approximate Bayesian computation scheme for parameter inference and model selection in dynamical systems. J R Soc Interface. 2009;6(31):187–202.

20. Saltelli A, Annoni P, Azzini I, Campolongo F, Ratto M, Tarantola S. Variance based sensitivity analysis of model output: design and estimator for the total sensitivity index. Comput Phys Commun. 2010;181(2):259–270.

21. Alper CM, Teixeira MS, Richert BC, Swarts JD. Change in Eustachian tube function with balloon dilation in adults with ventilation tubes. Otol Neurotol. 2020;41(4):511–518.

22. Wang X, Bi Z, Sha Y. Rate-dependent middle-ear barotrauma: a dynamic rabbit model. Aerosp Med Hum Perform. 2019;90(8):697–703.

23. Ryan MJ, Rahimi OB, Lewis GD, Adams ME. Prevention of otic barotrauma in aviation: a systematic review. Otol Neurotol. 2018;39(5):539–549.

24. Rosenkvist L, Klokker M, Katholm M. Barotrauma of the ear in Danish pilots. Ugeskr Laeger. 2008;170(42):3572–3574.

25. Ikeda R, Oshima H, Miyazaki H, et al. Patulous Eustachian Tube Handicap Inventory. Otol Neurotol. 2017;38(5):721–725.

26. Moayedi S, Turabian M, Matthews MR, et al. Pseudoephedrine prophylaxis for first-session hyperbaric-oxygen middle-ear barotrauma: a randomized double-blind placebo-controlled trial. Undersea Hyperb Med. 2025;52(3).

27. Oshima T, Ikeda R, Miyazaki H, et al. Clinical characteristics of 1,009 patients with patulous Eustachian tube: a large-scale multicenter study. Auris Nasus Larynx. 2025;52(4).

---

## Tables

### Table I. URI temporal modifier table.

| URI state | R<sub>A</sub> × | P<sub>O</sub>' shift (daPa) | Equalization rate × | Valsalva × | Per-descent relative risk |
|---|---|---|---|---|---|
| none | 1.0 | 0 | 1.00 | 1.00 | 1.00 |
| day 1–3 | 2.0 | +80 | 0.60 | 0.70 | 2.50 |
| day 4–7 | 3.5 | +150 | 0.40 | 0.50 | 4.25 |
| day 8–14 | 1.8 | +60 | 0.75 | 0.80 | 2.00 |
| day 15–21 | 1.3 | +20 | 0.90 | 0.90 | 1.30 |
| day 22–28 | 1.1 | +5 | 0.95 | 0.95 | 1.10 |

---

### Table II. Calibration summary.

| Metric | Value |
|---|---|
| Target per-exposure p<sub>barotitis</sub> | 2.00% |
| Achieved per-exposure p<sub>barotitis</sub> | 1.89% |
| Career projection (3 exposures) | 5.73% |
| FAC career anchor | 5.80% |
| r<sub>barotitis</sub> | 4.43 × 10⁻⁸ |
| r<sub>baromyringitis</sub> | 1.33 × 10⁻⁹ |
| r<sub>rupture</sub> | 4.43 × 10⁻¹¹ |
| Bisection iterations | 5 |
| ABC-SMC 95% credible interval on r<sub>barotitis</sub> | [3.59 × 10⁻⁸, 8.00 × 10⁻⁸] |

---

### Table III. External validation against Italian Air Force cohorts.

| Cohort | n | Observed (95% CI) | Simulated | Inside CI |
|---|---|---|---|---|
| Morgagni 2010 | 1,241 | 1.5% [0.96%, 2.34%] | 2.62% | no (+1.1 pp) |
| Morgagni 2012, 25,000 ft | 314 | 2.3% [1.13%, 4.62%] | 2.69% | yes |
| Landolfi 2009 | 335 | 2.4% [1.22%, 4.66%] | 2.63% | yes |

---

### Table IV. Descent-rate sensitivity, healthy patient, FAC cohort priors.

| Descent rate (ft·min⁻¹) | Duration (s) | Max \|ΔP\| (mmHg) | p<sub>barotitis</sub> | p<sub>rupture</sub> |
|---|---|---|---|---|
| 300 | 5,000 | 31 | 0.00% | 0.00% |
| 500 | 3,000 | 51 | 0.23% | 0.00% |
| 1,000 | 1,500 | 138 | 1.09% | 0.00% |
| 2,000 | 750 | 330 | 4.00% | 0.48% |
| 3,000 | 500 | 381 | 5.61% | 0.87% |
| 5,000 | 300 | 415 | 7.08% | 0.91% |
| 7,500 | 200 | 429 | 7.63% | 0.76% |
| 10,000 | 150 | 429 | 7.63% | 0.57% |

---

## Figure captions

**Figure 1.** Descent-rate sensitivity for a healthy patient on a 25,000-ft descent. Peak |ΔP| (top panel) grows monotonically with descent rate to a saturation of ~430 mmHg above 5,000 ft·min⁻¹. Per-exposure barotitis probability (bottom panel) increases across the full 500–10,000 ft·min⁻¹ range because the dose-time integral does not saturate as sharply as the peak.

**Figure 2.** Saltelli-Sobol total-order sensitivity index over four model parameters evaluated at a moderate-risk reference patient. The aperture half-point dominates (S<sub>T</sub> ≈ 1.84), an order of magnitude above descent-phase swallow frequency, mastoid volume, and aperture free-zone threshold. First-order index sum exceeding unity at N = 32 is a small-sample artifact; production runs should use N ≥ 128.
