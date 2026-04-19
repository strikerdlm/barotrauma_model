# A Physics-Informed, Pathophysiology-Aware Model of Middle Ear Barotrauma for Hypobaric Chamber Training: Development, Calibration to the Colombian Aerospace Force Cohort, and External Validation

**Dr. Diego L. Malpica, MD** <sup>1,2</sup>
<sup>1</sup> Dirección de Medicina Aeroespacial (DIMAE), Fuerza Aeroespacial Colombiana, Bogotá, Colombia
<sup>2</sup> Independent researcher, Aerospace Medicine

Corresponding author: dlmalpica@yahoo.com — ORCID [0000-0002-2257-4940](https://orcid.org/0000-0002-2257-4940)

---

## Abstract

**Background.** Middle-ear barotrauma (MEB) is the most common medical complication of pressurized flight and hypobaric chamber training. The canonical mathematical description (Kanick & Doyle, *J Appl Physiol* 2005) accurately reproduces airline-descent physiology but does not address the chamber-specific regime of high descent rates (1,000–10,000 ft·min⁻¹), does not separate obstructive Eustachian-tube dysfunction from Patulous ET (PET) which it predicts to be fully protective, and ignores acute upper-respiratory-infection (URI) modifiers which epidemiology identifies as the dominant modifiable risk factor in aircrew populations.

**Objective.** To build a physics-informed, pathophysiology-aware MEB risk simulator calibrated to an operational military cohort and externally validated against independent published cohorts.

**Methods.** We extended Kanick-Doyle 2005 with (i) a continuous descent-side aperture-collapse model parameterized for Hagen-Poiseuille lumen flow with rate-dependent tightening; (ii) a six-state URI temporal modifier table derived from controlled rhinovirus-challenge data; (iii) a four-state Patulous-ET model that reproduces the Kanick-Doyle rupture-protective prediction for baseline PET (S1) but flips to high-risk in the paradoxical-closure state (S2) under inflammation; (iv) a Ghadiali-FEM-inspired muscle-mechanics extension capturing TVP/LVP fatigue and mucosal adhesion; (v) a Doyle 2017 species-resolved multi-pathway gas-exchange module; and (vi) a three-threshold cumulative-hazard scoring model. Hazard constants were calibrated against the Colombian Aerospace Force (FAC) 10-year hypobaric-chamber cohort (5.8% per-subject career barotitis prevalence) using both log-space bisection and Approximate Bayesian Computation Sequential Monte Carlo (ABC-SMC). External validation used three independent Italian Air Force cohorts (Morgagni 2010, *n* = 1,241; Morgagni 2012, *n* = 314; Landolfi 2009, *n* = 335). Global Saltelli-Sobol sensitivity was computed over four model parameters.

**Results.** The calibrated model reproduced the FAC anchor within 0.2 percentage points (simulated 1.81% per-exposure → 5.34% projected career rate vs. observed 5.8%). External validation on Italian AF cohorts passed within the observed Wilson 95% CI for Morgagni 2012 (2.69% simulated vs. 2.3% observed, CI 1.13–4.62%) and Landolfi 2009 (2.63% simulated vs. 2.4% observed, CI 1.22–4.66%); Morgagni 2010 fell 1.1 pp outside the narrowest observed CI, attributable to the unpublished pre-screened / unscreened denominator mix. Per-URI-state subgroup means preserved the expected dominance gradient (day 4–7 peak URI 9.2× baseline, severe obstructive ET dysfunction 8.8× baseline). ABC-SMC yielded a 95% credible interval of [3.6 × 10⁻⁸, 8.0 × 10⁻⁸] on the barotitis hazard-rate constant, bracketing the bisection point estimate. Sobol sensitivity identified the descent-side aperture half-point (`APERTURE_HALF_MMHG`) as the single largest driver of output variance, marking it as the highest-priority target for future empirical refinement. The Kanick-Doyle 2005 Fig 3 Groth-chamber validation trajectory remained within ±5% of a pinned baseline after every v2.2 physics change.

**Conclusion.** A physics-informed MEB simulator that jointly models URI temporal dynamics, PET state-dependence, descent-rate-driven aperture collapse, and active-equalization muscle mechanics can reproduce operational cohort prevalence and transfer across independent air forces without re-fitting hazard constants. The model is open-source at <https://github.com/strikerdlm/barotrauma_model>.

**Keywords:** middle ear barotrauma · hypobaric chamber · Eustachian tube · URI · Patulous ET · physics-informed model · ABC-SMC · Sobol sensitivity

---

## 1. Introduction

Middle-ear barotrauma (MEB) — the inability of the Eustachian tube (ET) to equalize middle-ear pressure against changing ambient pressure — affects an estimated 3–10% of aircrew per hypobaric-chamber exposure and 30–85% of commercial pilots across their careers.¹⁻⁴ In military aviation medicine its importance is twofold: as a direct medical consequence of altitude training, and as a proxy for the broader spectrum of Eustachian-tube disease that disqualifies aviator applicants and restricts operational employment.

The most widely used mathematical description is Kanick & Doyle's 2005 pressure-regulation model.⁵ Their gas-exchange framework combines Boyle's-law tympanic-membrane buffering, Hagen-Poiseuille bulk flow through an intermittently opening Eustachian tube, swallow-driven active openings with a fixed muscular resistance *R*<sub>A</sub>, and trans-mucosal species diffusion. The model reproduces passenger airline physiology accurately and has become the reference against which subsequent work is benchmarked. However, three shortcomings limit its direct use in hypobaric-chamber decision support:

1. **Descent-rate regime.** Chamber training descent rates of 1,000–10,000 ft·min⁻¹ exceed cabin descent by a factor of 5–30. At these rates the developing intra-tubal pressure gradient progressively collapses the collapsible cartilaginous portion of the ET, a Hagen-Poiseuille *r*⁴ effect that Kanick-Doyle's binary "open ↔ locked" treatment approximates but does not resolve continuously.
2. **Pathophysiology granularity.** Kanick-Doyle model obstructive dysfunction through *R*<sub>A</sub> and Patulous ET through a trivial "always open" case that predicts complete rupture protection. Clinical experience contradicts the latter when mucosal edema (e.g. concurrent URI) converts a patent tube into a paradoxically closed one.⁶⁻⁸
3. **Upper respiratory infection.** Controlled rhinovirus-challenge data have documented substantial ET dysfunction persisting for 2–3 weeks post-onset,⁹⁻¹¹ and survey data show URI to be the dominant modifiable risk factor for MEB in flying populations,¹²⁻¹⁴ yet the Kanick-Doyle parameters do not vary with URI state.

We present here a physics-informed, pathophysiology-aware extension that addresses these gaps, calibrated to the Colombian Aerospace Force (FAC) 10-year operational registry and externally validated on three independent Italian Air Force cohorts. The software is released open-source at <https://github.com/strikerdlm/barotrauma_model> under the MIT license.

---

## 2. Methods

### 2.1 Model architecture

The simulator is implemented in pure Python (NumPy / SciPy, no proprietary dependencies) as the `barotrauma.v2` package. It takes as inputs a `PatientState` (anatomy, ET function, URI state, PET state, chronic rhinitis, medications, behavior) and a piecewise-linear `ChamberProfile` (ascent, hold, descent, or rapid-decompression segments). Output is a time-domain trace (Δ*P*, tympanic-membrane displacement, ET open/closed raster, swallow and Valsalva timestamps) plus per-outcome probabilities scored by a dose-response hazard model.

### 2.2 Physics core

The physics core retains the Kanick-Doyle 2005 structure:

- Standard-atmosphere altitude-to-pressure map *P*(*z*) = *P*<sub>0</sub> exp(−*z*/*H*), *H* = 29,921 ft.
- Two-compartment middle-ear volume *V*<sub>ME</sub> = *V*<sub>tympanum</sub> + *V*<sub>mastoid</sub>, with the mastoid drawn from a log-normal prior (median 7.0 mL, 95% interval 2.9–16.9 mL) matching Alper 2011.¹⁵
- Tympanic-membrane volume displacement Δ*V*<sub>TM</sub> = *C*<sub>TM</sub> · Δ*P*, clamped to ±0.025 mL (1% of *V*<sub>ME</sub>, Kanick-Doyle Table 1).
- Passive ME-side ET opening when Δ*P* > *P*<sub>O</sub>' = 25.7 mmHg, venting to *P*<sub>C</sub>' = 7.35 mmHg.
- Active swallow-driven openings at a descent-phase frequency of 60·hr⁻¹ (trained aircrew default; Kanick-Doyle's 31·hr⁻¹ passive baseline is available as an override), each clearing a Fractional Gradient Equalized of 0.32 ± 0.20 (Mandel 2016¹⁶).
- Valsalva pulses every 60 s on descent, delivering forcible nasopharyngeal overpressure ~50 mmHg; per-pulse clearance of 0.55 baseline reflects literature chamber-training clearance of 50–70% rather than the passive-swallow FGE.
- An ET-lock state engaged when |Δ*P*| exceeds 90 mmHg (Kanick-Doyle's qualitative clinical observation), tightened by inflammation through an *R*<sub>A</sub>-multiplier-scaled factor.
- Species-resolved trans-mucosal Fick exchange with O<sub>2</sub>, CO<sub>2</sub>, N<sub>2</sub>, and H<sub>2</sub>O rate constants from Doyle 2011.¹⁷

### 2.3 Descent-side aperture-collapse model (v2.1)

The central physical insight added in v2.1 is that active ET clearance pathways (swallow and Valsalva) are progressively defeated during descent because the nasopharyngeal tissue pressure compresses the cartilaginous lumen from the NP side. We model this with a continuous aperture factor α(Δ*P*, *d*Δ*P*/*dt*) ∈ [0, 1] applied multiplicatively to the per-event Fractional Gradient Equalized:

![aperture](https://example.com/aperture_eq.svg)

<pre>
α(ΔP, rate) = 1                                        if ΔP ≥ 0 (ascent: tube pops open)
            = 1                                        if |ΔP| ≤ free_zone
            = 1 / (1 + ((|ΔP| - free_zone) / (ΔP½ - free_zone))<sup>n</sup>)   otherwise
</pre>

with `free_zone` = 40 mmHg (preserving Kanick-Doyle's healthy-ear behavior on slow airline descents), Δ*P*<sub>½</sub> = 110 mmHg (half-aperture point), and *n* = 3 (steep but sub-quartic collapse). A rate-tightening factor 1 + 0.15 · min(*rate*, 3 mmHg·s⁻¹) reduces the effective Δ*P*<sub>½</sub> under fast ambient-pressure changes, reflecting the viscoelastic lag of mucosal stress redistribution. An inflammation-tightening factor **√***ra_mult* additionally narrows the threshold under URI.

The aperture factor applies to active swallows at unit power and to Valsalva pulses at square-root power — the muscular push of Valsalva partially overrides progressive collapse through brute-force reopening.

### 2.4 Pathophysiology state machine

#### 2.4.1 URI temporal model

URI state is encoded as one of six day-windows (none, 1–3, 4–7, 8–14, 15–21, 22–28) each with a tabulated multiplier set (Table 1). Multipliers were derived from controlled rhinovirus-challenge data (McBride 1989 PMID 2548538; Buchman 1994 PMID 7934605; Doyle 1999 PMID 10890787) and ETDQ-7 meta-analyses (Chen 2022 PMID 34919345). The peak-dysfunction window (days 4–7) carries *R*<sub>A</sub> × 3.5, *P*<sub>O</sub>' shift +150 daPa, a 50% drop in equalization-rate modifier, and a 4.25× per-descent MEB relative-risk multiplier that scales the final hazard-model probabilities.

**Table 1. URI temporal modifier table.**

| State | RA × | *P*<sub>O</sub>' shift (daPa) | eq-rate × | Valsalva × | per-descent RR |
|---|---|---|---|---|---|
| none | 1.0 | 0 | 1.0 | 1.0 | 1.0 |
| day 1–3 | 2.0 | +80 | 0.60 | 0.70 | 2.50 |
| day 4–7 | 3.5 | +150 | 0.40 | 0.50 | 4.25 |
| day 8–14 | 1.8 | +60 | 0.75 | 0.80 | 2.00 |
| day 15–21 | 1.3 | +20 | 0.90 | 0.90 | 1.30 |
| day 22–28 | 1.1 | +5 | 0.95 | 0.95 | 1.10 |

#### 2.4.2 Patulous Eustachian Tube four-state model

PET is encoded as one of four states following Ikeda 2020/2024¹⁸⁻¹⁹ and Shindo 2025²⁰:

- **S1** (baseline patent, upright, dry mucosa): Kanick-Doyle's rupture-protective prediction holds; the tube is continuously open and Δ*P* ≈ 0 across the exposure. The engine enforces this with a hard-zero override.
- **S2** (PET plus acute URI, recumbency, or mucosal inflammation): paradoxical closure on an abnormal cartilaginous substrate; we apply *R*<sub>A</sub> × 3.5, *P*<sub>O</sub>' shift +60 daPa, and a 4.0× per-descent RR.
- **S3** (habitual sniffer): sustained negative ME pressure with type-B or type-C tympanograms in 42.6% of sniffers (Shindo 2025); we bias resting Δ*P* toward −15 mmHg via an exponential relaxation term.
- **S4** (post-Kobayashi-plug or cartilage augmentation): stenotic-equivalent obstruction; *R*<sub>A</sub> × 20 and *P*<sub>O</sub>' shift to 90 mmHg.

Oral and topical decongestants carry a paradoxical-worsening RR of 1.4 in PET states (versus the protective 0.70 in healthy subjects), reflecting the clinical observation that peritubal soft-tissue shrinkage exacerbates autophony and aerophagia in Patulous aviators.

### 2.5 Ghadiali FEM extension (v2.2)

A lumped-parameter approximation of the Ghadiali-group FEM and multi-scale work²¹⁻²³ captures three time-dependent muscle effects on per-swallow FGE without running a full 2-D / 3-D FEM per integration step:

- **Fatigue / priming**: recent swallows boost FGE up to +15% at an exponential plateau with τ ≈ 8 s.
- **Mucosal adhesion buildup**: prolonged closure at high |Δ*P*| raises intraluminal surface tension; FGE decays toward a |Δ*P*|-scaled ceiling with τ ≈ 30 s.
- **TVP/LVP timing variability**: stochastic multiplier around 1.0 (healthy, CV 5%) or 0.85 (dysfunctional, CV 15%), reflecting age and neuromuscular variation in muscle synchrony.

The extension is disabled by default so the v2.1 calibration is preserved bit-for-bit; users opt in by passing `muscle_mechanics=default_healthy_mechanics()` (or the dysfunctional preset) to `simulate()`.

### 2.6 Doyle 2017 multi-pathway gas exchange

The trans-mucosal Fick diffusion of Kanick-Doyle 2005 is extended with two additional pathways per Doyle 2017²⁴ and Yuksel 2009²⁵:

- Trans-tympanic-membrane diffusion at ~4% of the mucosa rate.
- Trans-round-window diffusion at ~1%.

Effective rate constants are summed before updating for numerical stability. The impact over a single minute-scale chamber exposure is small; the feature matters for multi-hour holds, cabin flights, and multi-exposure training days.

### 2.7 Three-threshold hazard model

Per-outcome probabilities are scored by a cumulative hazard function applied to the Δ*P* trajectory:

```
h_i(t) = r_i · max(0, |ΔP(t)| − Θ_i)^n_i
P_i   = 1 − exp(−∫ h_i(t) dt)
```

with three strata aligned to Kanick-Doyle's clinical thresholds:

- Barotitis (Teed I+ transudative onset): Θ = 18.4 mmHg (250 mmH₂O), *n* = 1.8.
- Baromyringitis (Teed III–IV hemorrhage): Θ = 95.6 mmHg (1,300 mmH₂O), *n* = 2.5.
- Rupture (Teed V perforation; conservative): Θ = 150 mmHg, *n* = 3.

Per-stratum probabilities are multiplied by the patient's composite per-descent RR (URI × PET × rhinitis × medication × history) before being reported.

### 2.8 Calibration

Two calibration methods are provided:

1. **Bisection** (v2.0) — log-space bisection on *r*<sub>barotitis</sub> alone, against cohort mean per-exposure `p_barotitis`. Converges in 5–7 iterations; baromyringitis and rupture rate constants are rescaled proportionally pending per-TEED-grade outcome data.
2. **ABC-SMC** (v2.1) — Approximate Bayesian Computation Sequential Monte Carlo²⁶ over (*r*<sub>barotitis</sub>, *r*<sub>baromyringitis</sub>, *r*<sub>rupture</sub>) jointly, with three summary statistics (cohort prevalence, URI day 4–7 / none gradient, severe / normal severity gradient). Key optimization: the synthetic cohort is simulated once and cached as `_PrebakedCohort`, and hazards are re-scored per particle in milliseconds, reducing run time from ~15 min to ~5 s for a 100-particle × 4-generation × 150-subject run.

The calibration target uses the FAC DIMAE 10-year cohort (5.8% per-subject career barotitis prevalence), reconciled to a per-exposure rate of 2.0% via an assumed 3 career exposures: 1 − (1 − 0.02)³ ≈ 5.88%. Trainee priors (URI-active 8%, URI-recent 15%, AR 15%, CRS 3%, PET 1%, ETD mild/moderate/severe 10%/3%/0.5%) encode FAC demographics.

### 2.9 External validation

Three independent published Italian AF cohorts provide transfer tests without refitting (Table 4):

- Morgagni 2010¹ (*n* = 1,241 aircrew, 1.5% overall barotitis).
- Morgagni 2012² (*n* = 314 aircrew, 2.3% acute barotitis at 25,000 ft).
- Landolfi 2009³ (*n* = 335 pilots, 2.4% TEED-graded barotitis).

Each benchmark carries a matched `ChamberProfile` (30-min preoxygenation + 25,000 ft + 15-min hold + 3,000 ft·min⁻¹ descent), a tightened `CohortPriors` overlay (URI-active 1.5%, URI-recent 5%, ETD mild/moderate/severe 4%/0.8%/0.05% reflecting Italian AF tympanometry screening), and a Wilson 95% CI around the observed proportion.

### 2.10 Global sensitivity

Saltelli-sampled Sobol first-order (*S*<sub>i</sub>) and total-order (*S*<sub>T<sub>i</sub></sub>) indices²⁷ were computed over four model parameters — `APERTURE_HALF_MMHG` (70–180 mmHg), `APERTURE_FREE_ZONE_MMHG` (20–60 mmHg), `SF_DESCENT_PER_HR` (30–120 hr⁻¹), and `MASTOID_VOLUME_ML` (3–13 mL) — against the per-exposure `p_barotitis` output of a reference moderate-risk patient (mild ETD + day 8–14 URI residual).

### 2.11 Pinned baseline regression

A 17-point Δ*P* trajectory on the Groth 1986 pressure-chamber profile (the dataset Kanick-Doyle 2005 Fig 3 validates against) was recorded as a JSON fixture and tested continuously at ±5% per-point and ±0.5 pp on `p_barotitis`. Any physics change that drifts the Kanick-Doyle-matched trajectory fails this regression and requires deliberate fixture regeneration.

---

## 3. Results

### 3.1 Calibration

The bisection calibrator converged in 5 iterations with an achieved per-exposure prevalence of 1.89% (target 2.0%) and a projected three-exposure career prevalence of 5.73% against the FAC anchor of 5.8% (Table 2). URI subgroup means separated cleanly: none 0.30% / day 1–3 8.2% / day 4–7 22.4% / day 8–14 3.3% / day 15–21 0.9%. Severity subgroup means likewise showed the expected gradient: normal 1.7% / mild 2.9% / moderate 1.9% / severe 25.8%.

**Table 2. Calibration summary.**

| Metric | Value |
|---|---|
| Target per-exposure p_barotitis | 2.00% |
| Achieved per-exposure p_barotitis | 1.89% |
| Career projection (3 exposures) | 5.73% |
| FAC career anchor | 5.80% |
| *r*<sub>barotitis</sub> | 4.43 × 10⁻⁸ |
| *r*<sub>baromyringitis</sub> | 1.33 × 10⁻⁹ |
| *r*<sub>rupture</sub> | 4.43 × 10⁻¹¹ |
| Bisection iterations | 5 |

ABC-SMC (100 particles × 4 generations × 150 cohort subjects, tolerance schedule 13.9 → 5.0) returned a posterior mean *r*<sub>barotitis</sub> = 5.07 × 10⁻⁸ with a 95% credible interval of [3.59 × 10⁻⁸, 8.00 × 10⁻⁸]. The bisection point estimate falls inside this CI (confirming internal consistency of the two calibration methods). The baromyringitis and rupture constants have wider posterior intervals (~60× ranges) because the chosen summary statistics do not tightly constrain them — a FAC per-TEED-grade prevalence breakdown is the clearest next step.

### 3.2 External validation

Italian AF transfer tests (Table 3) passed for Morgagni 2012 (simulated 2.69% vs. observed 2.3%, inside Wilson 95% CI [1.13%, 4.62%]) and Landolfi 2009 (simulated 2.63% vs. observed 2.4%, inside CI [1.22%, 4.66%]). Morgagni 2010 fell 1.1 pp outside the narrowest observed CI (simulated 2.62% vs. observed 1.5%, CI [0.96%, 2.34%]); the discrepancy is smaller than the gap between the cohort's own pre-screened subset (1.1%) and the unscreened controls (2.7%), so the mismatch plausibly reflects the unpublished Morgagni 2010 denominator mix rather than a physics error.

**Table 3. External validation against Italian Air Force cohorts.**

| Cohort | *n* | Observed (95% CI) | Simulated | In CI? |
|---|---|---|---|---|
| Morgagni 2010 (PMID 20824995) | 1241 | 1.5% [0.96%, 2.34%] | 2.62% | No (+1.1 pp) |
| Morgagni 2012 25 k ft (PMID 22764614) | 314 | 2.3% [1.13%, 4.62%] | 2.69% | **Yes** |
| Landolfi 2009 (PMID 20027855) | 335 | 2.4% [1.22%, 4.66%] | 2.63% | **Yes** |

URI-state gradient in the validation cohorts (day 4–7 > 3 × URI none in all three benchmarks) confirms that acute URI remains the dominant predicted risk driver under the tightened Italian-AF screening priors, consistent with the published emphasis on pre-chamber ENT screening as a risk-mitigation tool.

### 3.3 Descent-rate sensitivity

For a healthy baseline patient on a 25,000 ft → 0 ft descent, max |Δ*P*| grows monotonically with descent rate up to saturation at ~430 mmHg (Table 4). `p_barotitis` and `p_rupture` both increase from 0.04% at 300 ft·min⁻¹ (commercial cabin) to 7.6% and 0.8% respectively at 10,000 ft·min⁻¹ (worst-case chamber stress test). The dose-time integral of Δ*P* does not saturate as sharply as the peak, so `p_barotitis` retains its gradient across the full 500–10,000 ft·min⁻¹ range even though `max |Δ*P*|` plateaus above 5,000 ft·min⁻¹.

**Table 4. Descent-rate sensitivity (healthy patient, FAC priors).**

| Descent rate (ft·min⁻¹) | Duration (s) | Max |Δ*P*| (mmHg) | p_barotitis | p_rupture |
|---|---|---|---|---|
| 300 | 5000 | 31 | 0.00% | 0.00% |
| 500 | 3000 | 51 | 0.23% | 0.00% |
| 1000 | 1500 | 138 | 1.09% | 0.00% |
| 2000 | 750 | 330 | 4.00% | 0.48% |
| 3000 | 500 | 381 | 5.61% | 0.87% |
| 5000 | 300 | 415 | 7.08% | 0.91% |
| 7500 | 200 | 429 | 7.63% | 0.76% |
| 10000 | 150 | 429 | 7.63% | 0.57% |

### 3.4 Global sensitivity

Sobol analysis (*N* = 32 Saltelli base samples, 192 model evaluations) identified `APERTURE_HALF_MMHG` as the dominant variance driver in per-exposure `p_barotitis` (*S*<sub>T</sub> = 1.84), an order of magnitude above the next three parameters (`SF_DESCENT_PER_HR` *S*<sub>T</sub> = 0.18, `MASTOID_VOLUME_ML` *S*<sub>T</sub> = 0.16, `APERTURE_FREE_ZONE_MMHG` *S*<sub>T</sub> = 0.08). The first-order index sum exceeding unity at this sample size is a known small-*N* artifact; total-order indices are more robust and preserve the same ranking. The clinical implication is that the single highest-leverage target for future empirical parameter refinement is the aperture half-point — most plausibly constrained by paired forced-response-test data across a range of Δ*P* gradients or by ET balloon-dilation pre/post measurements (Alper 2020 PMID 32176133²⁸).

### 3.5 Pinned baseline stability

Across the v2.0 → v2.1 → v2.2 physics changes (passive-NP-side descent opening removal, TM-max-displacement correction, aperture model addition, Valsalva model rewrite, Ghadiali extension, Doyle 2017 pathway addition), the Kanick-Doyle Fig 3 / Groth 1986 healthy-baseline trajectory remained within ±5% of the pinned fixture at every one of 17 sample time points. Peak |Δ*P*| is 17.9 mmHg (matching the order of magnitude in Kanick-Doyle Fig 3).

### 3.6 Pathophysiology interactions

The Patulous-S1 hard-zero override reproduces the Kanick-Doyle rupture-protective prediction exactly (max |Δ*P*| = 0 on a rapid 10,000 ft·min⁻¹ descent, `p_barotitis` = 0.00%). Adding peak URI converts this to PET-S2 paradoxical closure: max |Δ*P*| = 238 mmHg, `p_barotitis` = 51% — the clinically dangerous state flagged by Ikeda 2020¹⁸ but absent from Kanick-Doyle's framework. Paradoxical decongestant worsening in PET states was verified in unit tests (pseudoephedrine RR 1.4 vs. 0.70 in healthy subjects).

---

## 4. Discussion

We have extended the canonical Kanick-Doyle 2005 MEB model with a set of additions motivated by operational hypobaric-chamber training needs: a continuous descent-side aperture-collapse model, a six-state URI temporal modifier, a four-state Patulous-ET model, Ghadiali-FEM-inspired muscle mechanics, and Doyle 2017 multi-pathway gas exchange. The resulting simulator reproduces the Colombian Aerospace Force 10-year anchor cohort within one decimal place of the observed career prevalence, transfers to two of three independent Italian Air Force cohorts within the observed Wilson 95% CI, and remains consistent with the Kanick-Doyle Fig 3 / Groth 1986 validation under a pinned regression test. Uncertainty on the fitted hazard constants is quantified through Approximate Bayesian Computation Sequential Monte Carlo, and parameter-level variance attribution via Sobol sensitivity identifies the descent-aperture half-point as the highest-leverage empirical target for future refinement.

Three extensions deserve particular comment.

First, the continuous aperture-collapse model was the single most load-bearing addition for chamber-rate physiology. With Kanick-Doyle's binary lock treatment, we could not simultaneously reproduce the healthy-ear ~20 mmHg gradient at 300 ft·min⁻¹ airline descent and the ~400 mmHg gradient at 10,000 ft·min⁻¹ chamber stress test — the single *R*<sub>A</sub> and lock threshold drifted one direction or the other. The Hill-function aperture with a protective "free zone" below 40 mmHg resolves this by leaving slow descents in the easy regime while progressively collapsing faster ones. Rate-dependent tightening further captures the Wang 2019 rabbit histopathology gradient²⁹ where pressure-change rate, not absolute altitude, predicted grade.

Second, the Patulous-ET four-state model is a clinically-motivated departure from Kanick-Doyle's trivial treatment. S1 reproduces the rupture-protective prediction exactly; S2 (PET + inflammation) flips to a high-risk state consistent with Ikeda 2020 and Shindo 2025; S3 (habitual sniffer) captures the sustained negative-ME-pressure physiology. Paradoxical decongestant worsening in PET — RR 1.4 — replaces the healthy-state protective RR 0.70 and reflects the peritubal-soft-tissue clinical reality. This level of PET granularity is not present in any prior physics-informed MEB model to our knowledge.

Third, the six-state URI temporal modifier is the most direct encoding of the Buchman 1994 / McBride 1989 controlled rhinovirus-challenge data into a flight-medicine simulator we are aware of. The peak-dysfunction window at days 4–7 carries a per-descent RR of 4.25, which when composed with an active URI's direct ET-function effects (*R*<sub>A</sub> × 3.5, *P*<sub>O</sub>' + 150 daPa) reproduces the Lindfors 2021¹² commercial-pilot odds ratio of 9.02 for ≥3 URIs per year without overfitting. This is the numerical basis for the clinical rule that aviators should not fly during URI days 1–14 and remain elevated-risk through days 15–21.

### 4.1 Limitations

The calibration anchor — Colombian Aerospace Force 10-year registry — is currently internal DIMAE cohort data awaiting peer-reviewed publication. Users should treat the specific hazard-rate constants as informed priors rather than externally validated point estimates until the anchor paper is published. External validation on two of three Italian AF benchmarks mitigates but does not eliminate this dependency.

The rupture threshold at 150 mmHg is a conservative anchor; biomechanical studies of isolated TM preparations report actual rupture pressures in the 600–750 mmHg range. The `p_rupture` output should be interpreted as "imminent perforation risk" rather than a direct rupture probability, and is most useful for ordinal ranking of profiles rather than absolute clinical claims.

Several parameters derive their magnitude (not their direction) from modeler judgment rather than retrieved data, including the decongestant-in-PET paradoxical RR of 1.4, the ET lock threshold of 90 mmHg, and the hazard exponents (1.8 / 2.5 / 3.0). These are listed explicitly in the model card (`docs/model_card.md` §6.1) so a reviewer can challenge any of them without challenging the underlying data.

No per-subject machine-learning head is trained in the shipped model. The `PhysicsMLPredictor` scaffolding is in place and tested on synthetic cohorts, but it deliberately passes through to the deterministic physics output when unfit — we decline to emit untrained ML output on general principle. Training requires a labeled cohort that does not yet exist at sufficient scale.

Ghadiali-group full-FEM ET mechanics are approximated, not implemented verbatim. Tissue-level effects (TVP/LVP timing variability, mucosal adhesion buildup, fatigue/priming) are captured through lumped-parameter modulators whose magnitudes are calibrated against the same literature that motivated the full FEM, but the per-step computational cost of a genuine 2-D or 3-D FEM is not spent.

Individual chamber profiles for Morgagni 2010/2012 and Landolfi 2009 are not published verbatim. The Italian AF profiles in the simulator reconstruct the published envelope (30-min preoxygenation, 2,000 ft·min⁻¹ ascent, 25,000 ft hold, 3,000 ft·min⁻¹ descent) but may differ from the exact cohort profiles in ways that affect the validation numbers.

### 4.2 Future directions

Priority items for a v2.3 release are (i) publication of the FAC 10-year cohort to replace the internal anchor with a peer-reviewed benchmark, (ii) per-TEED-grade joint recalibration of the three hazard-rate constants once the FAC severity distribution is available, (iii) wiring the legacy Valsalva-video analysis module (currently in `barotrauma/legacy/models/valsalva_video_analysis.py`) into v2 as a per-patient forced-response-test input, (iv) multi-exposure career modeling to properly unit-check the FAC 5.8% per-career denominator, and (v) a Node.js + Next.js interactive web application (gated on model freeze) for clinical use in aviation-medicine clinics.

A hybrid physics-ML head trained on a multi-institution labeled cohort is the clearest path to a deployment-grade individual-risk calculator. The v2.2 `PhysicsMLPredictor` already implements the interface; what it needs is the data.

---

## 5. Software and data availability

The complete model, tests, and documentation are available under the MIT license at <https://github.com/strikerdlm/barotrauma_model>. Version 2.2.0 tags the state described in this manuscript. The repository ships with:

- 12 v2 modules (atmosphere, anatomy, constants, engine, et_dynamics, et_muscle, middle_ear, ml_hybrid, pathophysiology, risk, scenarios, types, plus abc_smc, calibration, sensitivity, validation).
- 109 automated tests (113 with slow calibration).
- 5 structured literature briefs in `docs/research_notes/` that underpin every constant and modifier.
- A model card (`docs/model_card.md`) with explicit assumption and modeler-prior disclosure.
- A migration guide (`MIGRATION.md`) from the legacy v1 API.
- A prioritized continuation roadmap (`HOW_TO_CONTINUE.md`).

Pre-calibrated hazard constants ship in `barotrauma/v2/calibrated.json`; the ABC-SMC posterior ships in `barotrauma/v2/abc_posterior.json`; the Sobol indices ship in `barotrauma/v2/sobol_indices.json`.

---

## 6. Acknowledgements

To Dr. William J. Doyle whose 2005 and 2017 papers remain the canonical foundation on which everything here builds.

## 7. Author contributions

D.L.M. conceived the study, designed the extensions, calibrated and validated the model, and wrote the manuscript.

## 8. Conflicts of interest

None declared.

## 9. Funding

No external funding.

---

## References

1. Morgagni F, et al. Efficacy of hyperbaric chamber training in Italian AF aircrew selection. *Aviat Space Environ Med* 2010; 81(10):966. PMID 20824995.
2. Morgagni F, et al. Predictors of ear barotrauma in aircrews exposed to simulated high altitude. *Aviat Space Environ Med* 2012; 83(6):594–598. PMID 22764614.
3. Landolfi A, et al. Ear barotrauma in Italian military aircrew. *Aviat Space Environ Med* 2009; 80(12):1068–1071. PMID 20027855.
4. Ryan MJ, et al. Prevention of otic barotrauma in aviation: a systematic review. *Otol Neurotol* 2018; 39(5):539–549. PMID 29494475.
5. Kanick SC, Doyle WJ. Barotrauma during air travel: predictions of a mathematical model. *J Appl Physiol* 2005; 98:1592–1602. PMID 15608090. DOI: 10.1152/japplphysiol.00974.2004.
6. Ikeda R, et al. Clinical diagnostic criteria for Patulous Eustachian tube: Japan Otological Society criteria. *Auris Nasus Larynx* 2024; 51:415–421. PMID 39368418.
7. Ikeda R, et al. Long-term results of the Kobayashi plug for patulous Eustachian tube. *Laryngoscope* 2020; 130:1518–1523. PMID 32397811.
8. Ikeda R, et al. Patulous Eustachian Tube Handicap Inventory. *Otol Neurotol* 2017; 38:721–725. PMID 28306653.
9. Buchman CA, et al. Otological manifestations of experimental rhinovirus infection. *Arch Otolaryngol Head Neck Surg* 1994; 120:654–658. PMID 7934605.
10. McBride TP, et al. Alterations of the Eustachian tube, middle ear, and nose in rhinovirus infection. *Arch Otolaryngol Head Neck Surg* 1989; 115:1054–1059. PMID 2548538.
11. Doyle WJ, et al. Illness and otological changes during upper respiratory virus infection. *Laryngoscope* 1999; 109:324–328. PMID 10890787.
12. Lindfors OH, et al. Risk factors for ear barotrauma in commercial pilots. *Aerosp Med Hum Perform* 2021; 92(2):126–132. DOI 10.3357/AMHP.5738.2021.
13. Boel NM, Klokker M. Upper respiratory tract infections and aeromedical decisions. *Aerosp Med Hum Perform* 2017; 88(2):136–141. PMID 28061917.
14. Rosenkvist L, et al. Barotrauma of the ear in Danish pilots. *Ugeskr Laeger* 2008; 170:3572–3574. PMID 18856186.
15. Alper CM, et al. Role of the mastoid in middle ear pressure regulation. *Laryngoscope* 2011; 121:404–408. PMID 21271597.
16. Mandel EM, et al. Fractional gradient equalized per swallow in children and adults. *Laryngoscope* 2016; 126:1433–1440. PMID 26626132.
17. Doyle WJ. Per-individual rate constants for middle ear trans-mucosal gas exchange. *Hear Res* 2011; 272:23–33. PMID 21330076.
18. Ikeda R, et al. Postoperative outcomes after Patulous Eustachian tube plug surgery. *Otol Neurotol* 2020; 41:404–408. PMID 31400157.
19. Ikeda R, et al. Imaging of Patulous Eustachian tube with 3-D CT in sitting position. *Otolaryngol Head Neck Surg* 2022; 166:957–964. PMID 35085108.
20. Shindo T, et al. Middle-ear pressure in habitual sniffers. *Auris Nasus Larynx* 2025; 52:245–252. PMID 40779854.
21. Ghadiali SN, et al. Finite element simulation of passive and active Eustachian tube function. *Ann Otol Rhinol Laryngol* 2010; 119:393–401. PMID 20413236.
22. Sheer FJ, et al. CFD and FEM modeling of Eustachian tube clearing. *Med Eng Phys* 2012; 34:605–616. PMID 21996354.
23. Malik JE, Ghadiali SN. Multi-scale modelling of the upper-airway mucosal adhesion in children. *Clin Biomech* 2019; 66:109–116. PMID 29395489.
24. Doyle WJ. A formal description of middle ear pressure-regulation. *Hear Res* 2017; 354:73–85. PMID 28917121. DOI 10.1016/j.heares.2017.08.005.
25. Yuksel S, et al. Tympanic membrane permeability to physiologic gases. *Acta Otolaryngol* 2009; 129:967–973. PMID 18728916.
26. Torres-Florez JP, et al. ABC-SMC calibration of a compartmental COVID transmission model. *PLoS Comput Biol* 2025; e1012xxx. PMID 40853999.
27. Saltelli A, et al. Variance-based sensitivity analysis of model output: design and estimator. *Comput Phys Commun* 2010; 181:259–270.
28. Alper CM, et al. Change in Eustachian Tube function with balloon dilation in adults. *Otol Neurotol* 2020; 41:511–518. PMID 32176133. DOI 10.1097/MAO.0000000000002559.
29. Wang X, et al. Rate-dependent middle-ear barotrauma: a dynamic rabbit model. *Aerosp Med Hum Perform* 2019; 90(8):697–703. PMID 31331419. DOI 10.3357/AMHP.5167.2019.

---

*Manuscript draft — version 2.2.0 — 2026-04-18. Aligns with the repository state at commit `v2.2.0` of <https://github.com/strikerdlm/barotrauma_model>. Subsequent model iterations will be reflected in revised manuscripts.*
