# Middle Ear Barotrauma During Hypobaric Chamber Training: A Physics-informed, Externally Validated Risk Model

**Article type:** Original Article (computational prediction-model development and external validation)

**Reporting guideline:** TRIPOD 2015 (checklist provided as Supplemental Digital Content 1).

**Word count:** body ~3,250 · structured abstract 249 · references 24 · tables 2 · figures 4 · supplemental digital content items 3.

---

## Abstract

**Objective.** To develop and externally validate a physics-informed, pathophysiology-aware prediction model for per-exposure middle-ear barotrauma (MEB) risk during hypobaric-chamber training.

**Study Design.** Computational prediction-model study with development followed by external validation against three independent, previously published cohorts; reported per TRIPOD 2015.

**Setting.** Hypobaric chamber training program of the Direction of Aerospace Medicine (DIMAE), Colombian Aerospace Force, Bogotá, Colombia (2,640 m elevation), with external validation against published Italian Air Force chamber cohorts.

**Patients.** All hypobaric-chamber training exposures recorded in the DIMAE registry between 1 January 2010 and 31 March 2026 (n = 7,271 exposures) by active-duty and reserve military aviators and aircrew, with no exclusion by age, sex, or prior ear history.

**Interventions.** None. The study extends Kanick-Doyle's 2005 middle-ear pressure-regulation model with a continuous descent-side aperture-collapse function (Hill function with rate-dependent tightening), a six-state upper-respiratory-infection (URI) temporal modifier table, a four-state Patulous Eustachian-tube (PET) model, a lumped-parameter approximation of Ghadiali-group muscle mechanics, and a three-threshold cumulative-hazard score. Hazard constants were calibrated via log-space bisection and Approximate Bayesian Computation Sequential Monte Carlo (ABC-SMC).

**Main Outcome Measures.** Clinically diagnosed middle-ear barotrauma (Teed grade ≥ I) within 24 hours of chamber exposure. Performance was assessed by absolute agreement of simulated vs. observed per-exposure prevalence against each cohort's binomial Wilson 95% confidence interval.

**Results.** Calibration reproduced the pooled FAC anchor within 0.1 percentage points (simulated 2.47% vs. observed 2.38%; Wilson 95% CI 2.06%–2.75%) and reproduced the projected 3-exposure career rate (simulated 7.23% vs. observed 6.97%). External validation fell inside the observed Wilson 95% confidence interval for Morgagni 2012 (3.31% vs. 2.3% [1.13%, 4.62%]) and Landolfi 2009 (3.37% vs. 2.4% [1.22%, 4.66%]); the Morgagni 2010 gap (+1.77 pp) lay within that cohort's own pre-screened-to-unscreened denominator spread. Saltelli-Sobol sensitivity analysis identified the aperture half-point as the dominant variance driver (total-order Sobol index 0.99).

**Conclusions.** The model reproduces operational MEB prevalence and transfers across independent air forces without refitting. Open-source simulator: https://github.com/strikerdlm/barotrauma_model.

**Keywords:** Eustachian tube dysfunction; altitude training; upper respiratory infection; physics-informed modelling; external validation.

---

## 1. Introduction

Middle-ear barotrauma (MEB) — the inability of the Eustachian tube (ET) to equalize middle-ear pressure against changing ambient pressure — affects an estimated 3–10% of aircrew per hypobaric-chamber exposure<sup>1–3</sup> and up to 85% of commercial aircrew over their careers.<sup>4</sup> In military aviation medicine its importance is twofold: as a direct medical consequence of altitude training, and as a proxy for the broader spectrum of Eustachian-tube disease that disqualifies aviator applicants and restricts operational employment.

The most widely used mathematical description is Kanick and Doyle's 2005 pressure-regulation model.<sup>5</sup> Their gas-exchange framework combines Boyle's-law tympanic-membrane buffering, Hagen-Poiseuille bulk flow through an intermittently opening Eustachian tube, swallow-driven active openings with a fixed muscular resistance R<sub>A</sub>, and trans-mucosal species diffusion. The model reproduces passenger airline physiology accurately and is the reference against which subsequent work is benchmarked. Three shortcomings limit its direct use in hypobaric-chamber decision support.

First, chamber training descent rates of 1,000–10,000 ft·min⁻¹ exceed cabin descent by a factor of 5–30. At these rates the developing intra-tubal pressure gradient progressively collapses the collapsible cartilaginous portion of the ET, a Hagen-Poiseuille r⁴ effect that Kanick-Doyle's binary "open or locked" treatment approximates but does not resolve continuously. Second, Kanick-Doyle model obstructive dysfunction through R<sub>A</sub> and Patulous ET through a trivial "always open" case that predicts complete rupture protection. Clinical experience contradicts the latter when mucosal edema (such as concurrent URI) converts a patent tube into a paradoxically closed one.<sup>6–8</sup> Third, controlled rhinovirus-challenge data have documented substantial ET dysfunction persisting for 2–3 weeks post-onset,<sup>9–11</sup> and survey data show URI to be the dominant modifiable risk factor for MEB in flying populations,<sup>4,12</sup> yet the Kanick-Doyle parameters do not vary with URI state.

We present a physics-informed, pathophysiology-aware extension that addresses these gaps, calibrated to the Colombian Aerospace Force (FAC) 10-year operational registry and externally validated on three independent Italian Air Force cohorts. The software is released open-source at https://github.com/strikerdlm/barotrauma_model under the MIT license.

---

## 2. Materials and Methods

### 2.1 Study design, reporting, and ethics

This is a computational prediction-model study comprising model development followed by external validation on three independent, previously published cohorts. Reporting follows the TRIPOD 2015 guideline (Transparent Reporting of a multivariable prediction model for Individual Prognosis Or Diagnosis); the completed 28-item checklist is provided as Supplemental Digital Content 1. No machine-learning component is used in the deployed prediction pipeline; the sklearn scaffolding referenced in the source repository is disabled and does not alter the deterministic physics output. TRIPOD+AI (2024) therefore does not apply.

Under Colombian Resolution 8430 of 1993 of the Ministry of Health (*Ministerio de Salud, "Por la cual se establecen las normas científicas, técnicas y administrativas para la investigación en salud"*), Article 11(a), research that uses retrospective documentary methods and de-identified records — without intervention or modification of biological, physiological, psychological, or social variables of subjects — is classified as ***investigación sin riesgo*** (research without risk) and does not require institutional-ethics-committee submission or individual informed consent. The present study meets these criteria: data are retrospective, de-identified prior to analysis, and no intervention was performed. The study was conducted in accordance with the principles of the Declaration of Helsinki (2013 revision). Calibration is anchored to aggregate institutional statistics only. **Publication of this work was authorized by the Colombian Aerospace Force.**

No generative artificial-intelligence tools were used in the preparation, writing, or editorial revision of the manuscript text, figures, tables, or interpretive content. An AI-assisted software-engineering assistant supported author-directed implementation of the Python software under explicit specifications; all scientific content, literature synthesis, clinical interpretation, analytical design, and manuscript prose are the authors' own. No AI tool is listed or claimed as an author (per ICMJE and COPE position statements).

### 2.2 Model architecture

The simulator is implemented in pure Python (NumPy and SciPy) as the `barotrauma.v2` package. It takes as inputs a patient state (anatomy, ET function, URI state, PET state, chronic rhinitis, medications, behavior) and a piecewise-linear chamber profile (ascent, hold, descent, or rapid-decompression segments). Output is a time-domain trace (ΔP, tympanic-membrane displacement, ET open-closed raster, swallow and Valsalva timestamps) and per-outcome probabilities scored by a dose-response hazard model.

### 2.3 Physics core

The physics core retains the Kanick-Doyle 2005 structure: standard-atmosphere altitude-to-pressure map P(z) = P₀ exp(−z/H) with H = 29,921 ft; two-compartment middle-ear volume V<sub>ME</sub> = V<sub>tympanum</sub> + V<sub>mastoid</sub> with the mastoid drawn from a log-normal prior (median 7.0 mL, 95% interval 2.9–16.9 mL) matching Alper 2011<sup>13</sup>; tympanic-membrane volume displacement clamped at ±0.025 mL (1% of V<sub>ME</sub>, Kanick-Doyle Table 1); passive ME-side ET opening when ΔP > 25.7 mmHg venting to 7.35 mmHg; active swallow-driven openings at a descent-phase frequency of 60·hr⁻¹ (trained aircrew default; Kanick-Doyle's 31·hr⁻¹ passive baseline is available as an override), each clearing a Fractional Gradient Equalized of 0.32, set to the upper bound of the 95% CI 0.18–0.34 reported for adult ears with no significant otitis-media history (Doyle 2014 pressure-chamber test);<sup>14</sup> Valsalva pulses every 60 s on descent with per-pulse clearance 0.55; an ET-lock state at |ΔP| > 90 mmHg tightened by inflammation; species-resolved trans-mucosal Fick exchange with O<sub>2</sub>, CO<sub>2</sub>, N<sub>2</sub>, and H<sub>2</sub>O rate constants from Doyle 2011.<sup>15</sup>

### 2.4 Descent-side aperture-collapse model

The central physical insight is that active ET clearance pathways (swallow and Valsalva) are progressively defeated during descent because the nasopharyngeal tissue pressure compresses the cartilaginous lumen from the NP side. We model this with a continuous aperture factor α(ΔP, dΔP/dt) ∈ [0, 1] applied multiplicatively to the per-event Fractional Gradient Equalized. For ΔP ≥ 0 (ascent) α = 1; for descent, α = 1 below a 40-mmHg free zone, then decays as 1 / (1 + ((|ΔP| − free_zone) / (ΔP<sub>½</sub> − free_zone))<sup>n</sup>) with ΔP<sub>½</sub> = 110 mmHg and n = 3. A rate-tightening factor 1 + 0.15 · min(rate, 3 mmHg·s⁻¹) reduces effective ΔP<sub>½</sub> under fast ambient-pressure changes, reflecting mucosal viscoelastic lag. An inflammation-tightening factor √(R<sub>A</sub>-multiplier) additionally narrows the threshold under URI. The aperture factor applies to active swallows at unit power and to Valsalva pulses at square-root power — the muscular push of Valsalva partially overrides progressive collapse.

### 2.5 Pathophysiology state machine

URI state is encoded as one of six day-windows (none, 1–3, 4–7, 8–14, 15–21, 22–28), each with a tabulated multiplier set (full table provided in Supplemental Digital Content 2). Multipliers were derived from controlled rhinovirus-challenge data<sup>9–11</sup> and ETDQ-7 meta-analyses.<sup>16</sup> The peak-dysfunction window (days 4–7) carries R<sub>A</sub> × 3.5, P<sub>O</sub>' shift +150 daPa (+11.3 mmHg), a 50% drop in equalization-rate modifier, and a 4.25× per-descent MEB relative-risk multiplier.

Patulous ET (PET) is encoded as one of four states.<sup>6–8</sup> S1 (baseline patent, upright, dry mucosa) reproduces Kanick-Doyle's rupture-protective prediction via a hard-zero override on ΔP. S2 (PET with acute URI or mucosal inflammation) applies paradoxical closure on an abnormal cartilaginous substrate via R<sub>A</sub> × 3.5, P<sub>O</sub>' shift +60 daPa, and a 4.0× per-descent RR. S3 (habitual sniffer) biases resting ΔP toward −15 mmHg, reflecting the type-B/C tympanogram rate of 42.6% reported in habitually-sniffing PET patients (Shindo 2025).<sup>8</sup> Per-descent RR was raised from 2.5 to 4.0 to reflect the Oshima 2025<sup>24</sup> large-cohort (n = 1,009) sniffing odds ratio of 8.18 convolved with the already-modeled ΔP physiology. S4 (post-Kobayashi-plug or cartilage augmentation) imposes stenotic-equivalent obstruction. Oral and topical decongestants carry a paradoxical-worsening RR of 1.4 in PET (versus 0.90 in healthy subjects — softened from the prior 0.70 per Moayedi 2025<sup>23</sup>, a placebo-controlled HBOT randomized trial showing null preventive effect of prophylactic pseudoephedrine).

### 2.6 Muscle mechanics and multi-pathway gas exchange

A lumped-parameter approximation of Ghadiali-group FEM and multi-scale work<sup>17</sup> captures three time-dependent muscle effects on per-swallow Fractional Gradient Equalized without running a full 2-D or 3-D FEM per integration step: fatigue and priming (recent swallows boost FGE up to +15% with τ ≈ 8 s), mucosal adhesion buildup (prolonged closure at high |ΔP| raises intraluminal surface tension with τ ≈ 30 s), and TVP/LVP timing variability (stochastic multiplier coefficient of variation 5% healthy, 15% dysfunctional). The extension is disabled by default. The trans-mucosal Fick diffusion is extended with trans-tympanic-membrane (~4% of mucosa rate) and trans-round-window (~1%) pathways per Doyle 2017.<sup>18</sup>

### 2.7 Three-threshold hazard model

Per-outcome probabilities are scored by a cumulative hazard applied to the ΔP trajectory: h<sub>i</sub>(t) = r<sub>i</sub> · max(0, |ΔP(t)| − Θ<sub>i</sub>)<sup>n<sub>i</sub></sup> with P<sub>i</sub> = 1 − exp(−∫ h<sub>i</sub> dt). Thresholds align with Kanick-Doyle's clinical values: barotitis onset Θ = 18.4 mmHg (250 mmH₂O, n = 1.8); baromyringitis Θ = 95.6 mmHg (1,300 mmH₂O, n = 2.5); rupture Θ = 150 mmHg (conservative, n = 3). Per-stratum probabilities are multiplied by the composite per-descent relative risk (URI × PET × rhinitis × medication × history).

### 2.8 Calibration and external validation

*Source of data and participants (development cohort).* The development dataset comprises all hypobaric-chamber training exposures recorded in the DIMAE registry between 1 January 2010 and 31 March 2026 (n = 7,271 exposures) performed by active-duty and reserve military aviators and aircrew of the Colombian Aerospace Force at the DIMAE hypobaric chamber facility (Bogotá, 2,640 m elevation). Eligibility was operational — all aircrew and aviator candidates scheduled for periodic or qualifying altitude indoctrination — with no exclusion by age, sex, or prior ear history.

*Outcome.* The primary outcome was clinically diagnosed middle-ear barotrauma (Teed grade ≥ I) occurring during or within 24 hours of a chamber exposure, ascertained by the on-duty chamber flight surgeon using otoscopic, tympanometric, and symptomatic criteria. A total of 173 barotrauma events were recorded in the 7,271 exposures (per-exposure rate 2.38%; Wilson 95% CI, 2.06%–2.75%; projected 3-exposure career rate 6.97%).

*Predictors.* Candidate predictors entering the model were: descent rate and altitude profile segment; mastoid volume (log-normal prior); Eustachian-tube resistance R<sub>A</sub> and passive opening pressure P<sub>O</sub>'; URI temporal state (6 levels); PET state (4 levels); chronic rhinitis; decongestant use; prior MEB history; and swallow and Valsalva frequency. No variable selection was performed; the model is mechanistic and retains all predictors by construction.

*Missing data.* No imputation was performed because the anchor is an aggregate population statistic (count of events / count of exposures); individual-level missingness is absorbed in the cohort prior and the synthetic cohort sampling.

*Calibration methods.* Calibration used two methods. Bisection performed log-space bisection on r<sub>barotitis</sub> against the cohort mean per-exposure p<sub>barotitis</sub>. Approximate Bayesian Computation Sequential Monte Carlo (ABC-SMC)<sup>19</sup> jointly inferred (r<sub>barotitis</sub>, r<sub>baromyringitis</sub>, r<sub>rupture</sub>) against three summary statistics (cohort prevalence; URI day 4–7 / none gradient; severe / normal severity gradient), using 100 particles, 4 generations, 150 synthetic-cohort subjects, and a tolerance schedule of 13.9 → 5.0. Full calibration parameters are reported in Supplemental Digital Content 3.

*External validation.* External validation used three published Italian Air Force cohorts<sup>1–3</sup> without refitting: Morgagni 2010 (n = 1,241, 1.5% overall barotitis), Morgagni 2012 (n = 314, 2.3% acute barotitis at 25,000 ft), and Landolfi 2009 (n = 335, 2.4% Teed-graded barotitis). Each carried a matched chamber profile (30-min preoxygenation, 25,000 ft hold, 3,000 ft·min⁻¹ descent), a tightened cohort prior reflecting Italian Air Force tympanometry pre-screening, and a binomial Wilson 95% confidence interval around the observed proportion.

*Model performance measures.* Model performance was assessed by (i) absolute agreement of simulated vs. observed per-exposure prevalence against the cohort's Wilson 95% confidence interval (pre-specified pass criterion: simulated point estimate within observed CI); (ii) agreement of the projected 3-exposure career prevalence against the pooled FAC career anchor; and (iii) qualitative preservation of the Kanick-Doyle Figure 3 healthy-baseline ΔP trace under a pinned regression fixture. Calibration-in-the-large and discrimination metrics routinely reported for person-level risk models (c-statistic, calibration slope) are not applicable to a cohort-level aggregate prediction and are not reported.

### 2.9 Global sensitivity and pinned baseline

Saltelli-sampled Sobol first-order and total-order indices<sup>20</sup> were computed over four model parameters — aperture half-point (70–180 mmHg), aperture free-zone threshold (20–60 mmHg), descent-phase swallow frequency (30–120 hr⁻¹), and mastoid volume (3–13 mL) — against the per-exposure p<sub>barotitis</sub> output of a reference moderate-risk patient. A 17-point ΔP trajectory on the Groth 1986 pressure-chamber profile was recorded as a fixture and tested continuously at ±5% per-point and ±0.5 percentage points on p<sub>barotitis</sub>. Statistical computations (Wilson intervals, Sobol estimators, bisection search) were performed by the corresponding author using NumPy 1.26 and SciPy 1.11; no inferential p-values are reported because the simulator is deterministic given a cohort prior, and all effect estimates are reported with their attendant confidence or credible intervals.

---

## 3. Results

### 3.1 Calibration

The bisection calibrator converged in 6 iterations with an achieved per-exposure prevalence of 2.47% (target 2.38%; absolute difference 0.09 percentage points) and a projected three-exposure career prevalence of 7.23% against the pooled FAC 2010–2026 anchor of 6.97% (Supplemental Digital Content 3). URI subgroup means separated cleanly: none 0.41%, day 1–3 10.8%, day 4–7 29.3%, day 8–14 4.4%, day 15–21 1.3%. Severity subgroup means: normal 2.2%, mild 3.9%, moderate 3.1%, severe 33.5%.

ABC-SMC (100 particles, 4 generations, 150 cohort subjects, tolerance schedule 13.9 → 5.0; fit against the earlier 2.00% target) returned a posterior mean r<sub>barotitis</sub> = 5.07 × 10⁻⁸ with a 95% credible interval of [3.59 × 10⁻⁸, 8.00 × 10⁻⁸]. The bisection point estimate against the re-anchored 2.38% target (r<sub>barotitis</sub> = 5.85 × 10⁻⁸) falls inside this credible interval, so the ABC-SMC posterior remains internally consistent with the pooled anchor and is not refit. The baromyringitis and rupture constants have wider posterior intervals because the chosen summary statistics do not tightly constrain them; a FAC per-Teed-grade breakdown is the clearest next step.

### 3.2 External validation

Italian Air Force transfer tests (Table 1; Figure 3) passed for Morgagni 2012 (simulated 3.31% vs. observed 2.3%, inside Wilson 95% CI [1.13%, 4.62%]) and Landolfi 2009 (simulated 3.37% vs. observed 2.4%, inside CI [1.22%, 4.66%]). Morgagni 2010 fell 1.77 percentage points outside the narrowest observed CI (simulated 3.27% vs. observed 1.5%, CI [0.96%, 2.34%]); the discrepancy is larger than the +1.1 percentage-point gap reported against the earlier single-cohort anchor, reflecting the 0.38 percentage-point uplift in the pooled 2010–2026 FAC target relative to the Italian AF aggregate mean (~1.8%), but remains comparable to that cohort's own pre-screened-to-unscreened spread (1.1% to 2.7%), consistent with the unpublished denominator mix rather than a physics error. URI-state gradient in the validation cohorts (day 4–7 > 3 × URI none) confirms acute URI as the dominant predicted risk driver.

### 3.3 Descent-rate sensitivity and pathophysiology interactions

For a healthy baseline patient on a 25,000-ft descent, max |ΔP| grows monotonically with descent rate up to saturation at ~400 mmHg (Table 2; Figure 1). Barotitis probability increases from 0.00% at 300 ft·min⁻¹ (commercial cabin) to 9.90% at 10,000 ft·min⁻¹ (worst-case chamber stress test). Rupture probability rises monotonically with descent rate, reaching 1.57% at 10,000 ft·min⁻¹ after clearing the 150 mmHg threshold at ~5,000 ft·min⁻¹. The dose-time integral of |ΔP| does not saturate as sharply as the peak, so barotitis probability retains its gradient across the full 500–10,000 ft·min⁻¹ range even where max |ΔP| plateaus.

The Patulous-S1 override reproduces Kanick-Doyle's rupture-protective prediction exactly (max |ΔP| = 0 on a rapid 10,000 ft·min⁻¹ descent, p<sub>barotitis</sub> = 0.0%). PET-S2 pathology (paradoxical closure on an abnormal cartilaginous substrate, no concurrent URI) on the same profile gives max |ΔP| = 423 mmHg and p<sub>barotitis</sub> = 44%; adding peak URI (day 4–7) saturates the hazard integral (p<sub>barotitis</sub> ≈ 100%), a clinically dangerous state recognised in the PET-management literature<sup>6–8</sup> but absent from Kanick-Doyle's framework. Figure 4 shows the full URI × PET interaction matrix on the FAC chamber profile for a default healthy baseline patient, confirming that the peak-URI window (days 4–7) dominates each PET row and that S1 + URI elevates risk to the same level as S2 + URI — that is, the rupture-protective Kanick-Doyle prediction for patent ET is reversed under acute upper-respiratory inflammation.

### 3.4 Global sensitivity and pinned-baseline stability

Sobol analysis (N = 128 Saltelli base samples, 768 model evaluations, scrambled-Sobol QMC sequence, seed 2026) identified the aperture half-point as the dominant variance driver in per-exposure p<sub>barotitis</sub> (total-order Sobol index S<sub>T</sub> = 0.99, first-order index S<sub>i</sub> = 0.97), approximately fifty-fold above descent-phase swallow frequency (S<sub>T</sub> = 0.020), aperture free-zone threshold (S<sub>T</sub> = 0.019), and mastoid volume (S<sub>T</sub> = 0.005); the three secondary parameters were within Monte-Carlo noise of each other across a five-seed sweep (range 0.016–0.033 for swallow and free-zone). First-order indices summed to ≈ 0.93 and total-order indices to ≈ 1.04, indicating that the per-exposure barotitis output is dominated by the main effect of the aperture half-point with negligible interaction structure. Figure 2 shows the ranking. The clinical implication is that the single highest-leverage target for future empirical parameter refinement is the aperture half-point, most plausibly constrained by paired forced-response-test data or by ET balloon-dilation pre- and post-measurements.<sup>21</sup>

Across the v2.0 → v2.1 → v2.2 physics changes, the Kanick-Doyle Figure 3 / Groth 1986 healthy-baseline trajectory remained within ±5% of the pinned fixture at every one of 17 sample time points. Peak |ΔP| is 17.9 mmHg, matching the order of magnitude in Kanick-Doyle Figure 3.

---

## 4. Discussion

We have extended the canonical Kanick-Doyle 2005 middle-ear-barotrauma model with a set of additions motivated by operational hypobaric-chamber needs: a continuous descent-side aperture-collapse model, a six-state URI temporal modifier, a four-state Patulous ET model, Ghadiali-FEM-inspired muscle mechanics, and Doyle 2017 multi-pathway gas exchange. The resulting simulator reproduces the pooled Colombian Aerospace Force 2010–2026 anchor cohort within 0.1 percentage points per-exposure and 0.3 percentage points career-3, transfers to two of three independent Italian Air Force cohorts within the observed Wilson 95% CI, and remains consistent with the Kanick-Doyle Figure 3 / Groth 1986 validation under a pinned regression test.

Three extensions deserve particular comment. First, the continuous aperture-collapse model was the single most load-bearing addition for chamber-rate physiology. Kanick-Doyle's binary lock treatment could not simultaneously reproduce a healthy-ear 20-mmHg gradient at 300 ft·min⁻¹ airline descent and a 400-mmHg gradient at 10,000 ft·min⁻¹ chamber stress — the single R<sub>A</sub> and lock threshold drifted one direction or the other. The Hill-function aperture with a protective free zone below 40 mmHg resolves this by leaving slow descents in the easy regime while progressively collapsing faster ones. Rate-dependent tightening captures the Wang 2019 rabbit histopathology gradient<sup>22</sup> where pressure-change rate, not absolute altitude, predicted grade.

Second, the Patulous ET four-state model is a clinically-motivated departure from Kanick-Doyle's trivial treatment. S1 reproduces the rupture-protective prediction exactly; S2 flips to high risk consistent with the PET-with-inflammation pathophysiology described in the Japan Otological Society criteria (Kobayashi 2018); S3 captures the sustained negative-ME-pressure physiology. Paradoxical decongestant worsening in PET replaces the protective relative risk 0.70 with 1.4 and reflects the peritubal-soft-tissue clinical reality. This level of PET granularity is not present in any prior physics-informed MEB model to our knowledge.

Third, the six-state URI temporal modifier is the most direct encoding of the controlled rhinovirus-challenge data<sup>10,11</sup> into a flight-medicine simulator we are aware of. The peak-dysfunction window at days 4–7 carries a per-descent relative risk of 4.25, which when composed with direct ET-function effects reproduces the Lindfors 2021<sup>4</sup> commercial-aircrew odds ratio of 9.02 for ≥3 URIs per year without overfitting — the numerical basis for the clinical rule that aviators should not fly during URI days 1–14 and remain elevated-risk through days 15–21.

### 4.1 Limitations

The calibration anchor — the pooled FAC 2010–2026 registry — is internal DIMAE cohort data awaiting peer-reviewed publication; hazard-rate constants should be treated as informed priors until the anchor paper is published. External validation on two of three Italian Air Force benchmarks mitigates but does not eliminate this dependency.

The 150-mmHg rupture threshold is a conservative anchor; biomechanical studies of isolated tympanic membranes report rupture at 600–750 mmHg. Rupture output should be interpreted as "imminent perforation risk" for ordinal ranking. Several parameters reflect modeler judgment rather than retrieved data — including the decongestant-in-PET paradoxical relative risk of 1.4, the ET lock threshold of 90 mmHg, and the hazard exponents — and are listed in the model card for individual challenge.

No per-subject machine-learning head is trained; Ghadiali-group full-FEM mechanics are approximated by lumped parameters. Individual Italian Air Force chamber profiles are not published verbatim, and the simulator reconstructs the published envelope, which may differ from exact cohort profiles in ways that affect validation numbers.

### 4.2 Incorporation of 2025–2026 evidence

A 2026 targeted scan identified two findings with parameter impact. Moayedi 2025<sup>23</sup>, a placebo-controlled HBOT trial, showed no preventive effect of prophylactic pseudoephedrine; we therefore soften the pseudoephedrine relative risk from 0.70 to 0.90. Oshima 2025<sup>24</sup> (n = 1,009) quantifies habitual-sniffing odds ratio at 8.18 for PET; we update the PET-S3 per-descent relative risk from 2.5 to 4.0 accordingly. Other 2025–2026 findings on balloon dilation, HBOT sequelae, vortex pumping, and palatal-muscle atrophy are flagged for v2.3.0 but do not alter the v2.2.1 calibration target.

### 4.3 Conclusions

A physics-informed middle-ear barotrauma simulator that jointly models URI temporal dynamics, Patulous ET state dependence, descent-rate-driven aperture collapse, and active-equalization muscle mechanics can reproduce operational cohort prevalence and transfer across independent air forces without refitting hazard constants. The model is calibrated to the Colombian Aerospace Force cohort and validated against two independent Italian Air Force benchmarks within the observed Wilson 95% confidence interval. The aperture half-point is the dominant source of output variance and the highest-leverage empirical refinement target. The clinical utility for otolaryngology practice is twofold: (1) a per-exposure quantitative risk estimate to inform pre-chamber screening decisions in aviator candidates, and (2) recommended safe descent-rate ceilings for individual patient profiles, particularly those with documented Patulous ET or recent upper-respiratory illness.

---

## References

1. Morgagni F, Autore A, Landolfi A, Ciniglio Appiani M, Marcoccia A. Predictors of ear barotrauma in aircrews exposed to simulated high altitude. *Aviat Space Environ Med*. 2012;83(6):594–598.

2. Landolfi A, Torchia F, Autore A, Ciniglio Appiani M, Morgagni F, Ciniglio Appiani G. Acute otitic barotrauma during hypobaric chamber training: prevalence and prevention. *Aviat Space Environ Med*. 2009;80(12):1059–1062.

3. Morgagni F, Autore A, Landolfi A, Torchia F, Ciniglio Appiani G. Altitude chamber related adverse effects among 1241 airmen. *Aviat Space Environ Med*. 2010;81(9):873–877.

4. Lindfors OH, Ketola KS, Klockars TK, Leino TK, Sinkkonen ST. Middle ear barotraumas in commercial aircrew. *Aerosp Med Hum Perform*. 2021;92(3):182–189.

5. Kanick SC, Doyle WJ. Barotrauma during air travel: predictions of a mathematical model. *J Appl Physiol*. 2005;98(5):1592–1602.

6. Kobayashi T, Morita M, Yoshioka S, et al. Diagnostic criteria for patulous Eustachian tube: a proposal by the Japan Otological Society. *Auris Nasus Larynx*. 2018;45(1):1–5.

7. Kikuchi T, Ikeda R, Oshima H, et al. Effectiveness of Kobayashi plug for 252 ears with chronic patulous Eustachian tube. *Acta Otolaryngol*. 2017;137(3):253–258.

8. Shindo H, Yoshida M, Hirai R, Oshima T. Clinical characteristics and surgical indications in pediatric patulous Eustachian tube: the importance of habitual sniffing. *Auris Nasus Larynx*. 2025;52(5):545–549.

9. McBride TP, Doyle WJ, Hayden FG, Gwaltney JM Jr. Alterations of the Eustachian tube, middle ear, and nose in rhinovirus infection. *Arch Otolaryngol Head Neck Surg*. 1989;115(9):1054–1059.

10. Buchman CA, Doyle WJ, Skoner D, Fireman P, Gwaltney JM. Otologic manifestations of experimental rhinovirus infection. *Laryngoscope*. 1994;104(10):1295–1299.

11. Doyle WJ, Skoner DP, Alper CM, et al. Illness and otological changes during upper respiratory virus infection. *Laryngoscope*. 1999;109(2 Pt 1):324–328.

12. Boel NM, Klokker M. Upper respiratory infections and barotrauma among commercial pilots. *Aerosp Med Hum Perform*. 2017;88(1):17–22.

13. Alper CM, Kitsko DJ, Swarts JD, Martin B, Yuksel S, Doyle WJ. Role of the mastoid in middle ear pressure regulation. *Laryngoscope*. 2011;121(2):404–408.

14. Doyle WJ, Singla A, Banks J, El-Wagaa J, Swarts JD. Pressure chamber tests of Eustachian tube function document lower efficiency in adults with colds when compared to without colds. *Acta Otolaryngol*. 2014;134(7):691–697.

15. Doyle WJ, Swarts JD, Banks J, Yuksel S, Alper CM. Transmucosal O₂ and CO₂ exchange rates for the human middle ear. *Auris Nasus Larynx*. 2011;38(6):684–691.

16. Chen T, Shih MC, Edwards TS, et al. Eustachian tube dysfunction (ETD) in chronic rhinosinusitis with comparison to primary ETD: a systematic review and meta-analysis. *Int Forum Allergy Rhinol*. 2022;12(7):942–951. doi:10.1002/alr.22942.

17. Ghadiali SN, Banks J, Swarts JD. Finite element analysis of active Eustachian tube function. *J Appl Physiol*. 2004;97(2):648–654.

18. Doyle WJ. A formal description of middle ear pressure-regulation. *Hear Res*. 2017;354:73–85.

19. Toni T, Welch D, Strelkowa N, Ipsen A, Stumpf MPH. Approximate Bayesian computation scheme for parameter inference and model selection in dynamical systems. *J R Soc Interface*. 2009;6(31):187–202.

20. Saltelli A, Annoni P, Azzini I, Campolongo F, Ratto M, Tarantola S. Variance based sensitivity analysis of model output: design and estimator for the total sensitivity index. *Comput Phys Commun*. 2010;181(2):259–270.

21. Alper CM, Teixeira MS, Rath TJ, Hall-Burton D, Swarts JD. Change in Eustachian tube function with balloon dilation in adults with ventilation tubes. *Otol Neurotol*. 2020;41(4):482–488.

22. Wang B, Xu X, Lin J, Jin Z. Dynamic rabbit model of ear barotrauma. *Aerosp Med Hum Perform*. 2019;90(8):696–702.

23. Moayedi S, Gizaw A, Sweet S, Sethuraman K, Witting M. Pseudoephedrine prophylaxis does not prevent middle ear barotrauma in hyperbaric oxygen therapy. *Undersea Hyperb Med*. 2025;52(2):101–107.

24. Oshima H, Yoshida M, Shindo H, Hirai R, Oshima T. Clinical characteristics and diagnostic value of symptoms and objective findings in patulous eustachian tube: a large-scale study based on the Japan Otological Society criteria. *Auris Nasus Larynx*. 2025;52(6):651–656.

---

## Figure legends

**Figure 1.** Descent-rate sensitivity for a healthy patient on a 25,000-ft descent. Peak |ΔP| (top panel) grows monotonically with descent rate, approaching ~400 mmHg at 10,000 ft·min⁻¹. Per-exposure barotitis probability (bottom panel) increases across the full 500–10,000 ft·min⁻¹ range because the dose-time integral does not saturate as sharply as the peak.

**Figure 2.** Saltelli-Sobol total-order sensitivity index over four model parameters evaluated at a moderate-risk reference patient (N = 128 Saltelli base samples; 768 model evaluations; scrambled-Sobol QMC sequence, seed 2026). The aperture half-point dominates (S<sub>T</sub> ≈ 0.99), approximately fifty-fold above descent-phase swallow frequency (S<sub>T</sub> = 0.020), aperture free-zone threshold (S<sub>T</sub> = 0.019), and mastoid volume (S<sub>T</sub> = 0.005). The three secondary parameters are indistinguishable from each other within Monte-Carlo noise.

**Figure 3.** External validation of the model against the calibration anchor (Colombian Aerospace Force pooled 2010–2026) and three independent published Italian Air Force cohorts. Observed per-exposure barotitis incidence (filled circles) is shown with Wilson 95% confidence intervals (whiskers); simulated point estimates (diamonds) are colored green when within the observed CI and orange when outside. The model fell within the observed CI for the calibration cohort (sim 2.47% vs obs 2.38%, CI [2.06–2.75]) and for two of the three external cohorts (Morgagni 2012 and Landolfi 2009). The Morgagni 2010 simulated point (3.27%) sits 0.91 percentage points above the upper CI bound of that cohort's observed estimate (1.51%, CI [0.97–2.36]), within the cohort's own pre-screened-to-unscreened denominator spread (1.1% to 2.7%) reported in the source publication. Right margin shows event count over cohort denominator and the simulated point with within-CI status.

**Figure 4.** Joint dependence of per-exposure barotitis probability on Patulous Eustachian-tube state (5 levels: No PET, S1 baseline patent and dry mucosa, S2 PET with inflammation, S3 habitual sniffer, S4 post-Kobayashi plug or stenotic-equivalent) and upper-respiratory-infection temporal state (6 levels: none, days 1–3, 4–7, 8–14, 15–21, 22–28). Each cell is the model output for a default healthy baseline patient on the FAC Bogotá chamber profile (8,530 ft start, 25,000 ft hold, 2,470 ft·min⁻¹ descent), varying only the URI and PET states; values were computed by `barotrauma.v2.simulate` over the full 5×6 grid. The peak-URI window (days 4–7) dominates each PET row. PET-S1 (rupture-protective in the original Kanick-Doyle 2005 binary treatment) is converted to high risk by URI exposure, matching the PET-with-inflammation pathophysiology in the Japan Otological Society criteria. PET-S4 saturates regardless of URI state. PET-S3 returns uniformly low risk on this profile because the negative resting-pressure bias offsets the descent-side ΔP integral; this model behavior is profile-specific and should not be interpreted as habitual sniffing being clinically protective.

---

## Supplemental Digital Content

Supplemental Digital Content 1. TRIPOD 2015 reporting checklist (28 items), PDF.

Supplemental Digital Content 2. URI temporal modifier reference table — full six-state multiplier set for the pathophysiology state machine (Section 2.5), PDF/Word.

Supplemental Digital Content 3. Calibration summary — full bisection and ABC-SMC results including all rate constants and credible intervals (Section 2.8 and 3.1), PDF/Word.

*(SDC URLs http://links.lww.com/MAO/[code] will be assigned by the editorial office after submission.)*
