# ML, Bayesian, and Hybrid Approaches to MEB Risk — Technical Brief

**Author:** research agent (Chiron) | **Date:** 2026-04-18 | **Target audience:** barotrauma_model modelers

This brief synthesizes published work on machine learning (ML), probabilistic hazard modeling, hybrid physics–ML, and Bayesian calibration, applied to the problem of individual middle ear barotrauma (MEB) risk prediction and population-level calibration of a physics-informed simulator.

---

## 1. Published ML models for MEB prediction

**Gap.** Targeted PubMed and Semantic Scholar searches returned **no peer-reviewed ML model built specifically to predict MEB or ear barotrauma** in aviation or diving. The MEB modeling canon remains deterministic physics (Kanick & Doyle 2005, doi:10.1152/japplphysiol.00974.2004) or descriptive epidemiology (Landolfi 2009 PMID 20027855; Ryan 2018 PMID 29994817).

**Closest analogs in the adjacent DCS/diving literature:**

- Marroni et al. 2026 (DAN DSL): multivariate logistic regression on 127,957 dives, 628 DCS cases. AUROC **0.910**, 12 predictors including DAN Surface Supersaturation Gradient, leading compartment, sex, BMI, repetitive dive count, surface interval, gas count, exercise, thermal comfort, workload. No external validation reported. doi:10.5603/imh.108038.
- Tournoy et al. 2024 (Belgian diver cohort): binary logistic regression, ENT comorbidity OR 9.3 and cardiac medication OR 5.6 as independent predictors of diving hospitalisation. doi:10.28920/dhm54.4.287-295.

**Implication.** There is an unfilled niche for an MEB-specific prediction model. Borrow the Marroni feature template (exposure-derived + host-susceptibility + environmental), but adapt exposure features to the hypobaric profile: peak |ΔP|, time-above-threshold, integrated ∫|ΔP|dt, descent rate, number of failed equalizations.

---

## 2. Hybrid physics–ML in biomedical simulation

Dominant patterns relevant to this project:

- **Residual correction.** Physics simulator produces a low-frequency trend; an ML head (XGBoost, small NN) learns a bounded residual against observed labels. Example framework: Zhu et al. 2026, doi:10.3390/buildings16071380 (PINN + XGBoost residual, non-biomedical but canonical pattern).
- **Bayesian History Matching + Gaussian Process (GP) emulator.** Jones & Oomen 2025 (PMID 39515269) couple a cardiac biophysics model with GP emulators, calibrate parameters via two-tiered history matching to match observed growth to a 95% CI, validated on an independent canine dataset. This is the pattern I recommend most strongly for MEB.
- **GP emulation for cardiovascular simulators.** Paun et al. 2025 (PMID 40078149) compare GP vs. polynomial chaos emulators for 1D haemodynamics; GPs slightly superior in forward emulation and parameter inference.
- **Hybrid Weibull + PINN.** Reliability-layer on top of PINN physics for anomaly detection (doi:10.1109/ICCMA67641.2025.11369643) — analogous to attaching a hazard layer on top of the MEB ΔP simulator.

**No PINN applications to ENT physiology were found.** The MEB simulator can be the first.

---

## 3. Dose-response hazard functions (aviation/diving analogues)

The diving DCS literature has mature probabilistic hazard mathematics that translates directly:

- **Weathersby, Homer & Flynn** pioneered maximum-likelihood survival-analysis fitting of DCS probability to inert-gas supersaturation dose. Extended to include **time-to-DCS** (Weathersby et al. 1992, PMID 1592748) — richer than binary outcome.
- **Thalmann Linear-Exponential (LEM)** with VVAL-18/VVAL-79 parameters (Thalmann, Parker, Survanshi, Weathersby 1997, PMID 9444058): three parallel compartments with exponential uptake; at least one compartment uses linear elimination when supersaturation is high. Risk is an integral of instantaneous supersaturation above a threshold.
- **O₂-modified LEM** (Parker et al. 1998, PMID 9480974) adds metabolic gas contribution.
- **Hill dose-response** for VGE/DCS (Eckenhoff et al. 1990, PMID 2246178): endpoint probability as sigmoid of exposure magnitude; useful when only cumulative exposure is known.
- **Modified tissue ratio with variable P2** (Conkin et al. 1996, PMID 8834946): hypobaric NASA/USAF model — 211 DCS cases in 1,075 exposures, log-logistic survival fit. **Most directly applicable to the barotrauma_model use case.**
- **Hypobaric chamber training prevalence data:** Landolfi 2009 — barotitis prevalence **2.4%** (8/335 Italian AF pilots); Files 2005 (PMID 15945394) — 71 barotrauma events in 1,055 military decompression incidents (6.7%); Rice 2003 (PMID 12546299) — DCS 0.25% overall in naval training. Note the target **5.8%** does not match these cohorts; see "Calibration Recipe" for reconciliation.

---

## 4. Bayesian calibration of physiological models to prevalence

**Best practices, with published templates:**

- **ABC-SMC (Approximate Bayesian Computation Sequential Monte Carlo).** Torres-Florez et al. 2025 (PMID 40853999) calibrate a compartmental COVID transmission model in Québec to surveillance data; canonical template: priors on latent parameters → simulate → compare summary statistics to observations → adaptive tolerance schedule. Ideal when likelihood is intractable (here: a physics simulator).
- **Bayesian History Matching + GP emulator.** Andrianakis et al. 2015 (PMID 25569850, HIV in Uganda): 22-input simulator, 18 outputs, 9 iterations of implausibility-based parameter space pruning shrinking the input space by 10¹¹. For cardiac, see Rodero et al. 2023 (PMID 36271218) and Longobardi et al. 2020 (PMID 32448071).
- **Restitution curve emulators / probabilistic model calibration.** Coveney et al. 2021 (PMID 34366883) — GP emulator-based Bayesian calibration to noisy measurements.

---

## 5. Uncertainty quantification — one recommended combination

**Aleatoric + parameter uncertainty:** Monte Carlo (10⁴ draws) over posterior distributions of physiological priors (ET opening threshold, mTVP efficiency, TM compliance, mastoid volume) → propagate through the deterministic simulator → obtain per-patient predictive distribution of MEB probability.

**Individual predictive guarantee:** **Split conformal prediction** on a held-out calibration set ensures distribution-free 1−α marginal coverage (target α = 0.10). Majlatow et al. 2025 (doi:10.3390/app15147925) demonstrate calibrated probability + CP in healthcare PPM; Penso et al. 2025 (arXiv 2501.12749) handle noisy labels. Combine with **Platt scaling** or **isotonic regression** for probability calibration (Fan et al. 2021, PMID 33413321 — DLBCL ensemble with shape-restricted polynomial calibration).

**Metrics to report:** Brier score, Expected Calibration Error (ECE) across 10 bins, empirical 90% coverage, AUROC, net benefit decision curve analysis (mandatory for any risk tool, see most 2025–26 clinical ML papers).

---

## 6. Individual risk vs. population prevalence — the bridge

Deterministic ΔP(t) → individual P(MEB) requires explicit modeling of **latent physiological variability**. Recommended bridge:

1. Treat per-subject physiological parameters θᵢ = (ET threshold, TVP efficiency, TM compliance, mastoid volume) as draws from population priors calibrated in §4.
2. Given a descent profile, simulate ΔP(t; θᵢ) deterministically.
3. Apply hazard model P(MEB | θᵢ) = 1 − exp(−∫ h(τ; θᵢ) dτ) (see Recommended Hazard Model below).
4. Marginalize: P(MEB | descent) = E_θ [P(MEB | θ)] via Monte Carlo.
5. For individualized prediction on a specific subject, condition θ on subject-specific measurements (tympanometry, ETF score, history) via Bayesian update.

This is formally a **mixture-of-experts over physiological phenotypes**.

---

## Recommended Hazard Model (ready to implement)

**Primary recommendation — Weibull/Thalmann-style multi-threshold cumulative hazard**, adapted from Thalmann LEM (PMID 9444058) and Weathersby time-to-event (PMID 1592748):

```
h(t; θ) = Σᵢ rᵢ · max(0, |ΔP(t; θ)| − Θᵢ)^nᵢ
P(MEB | descent, θ) = 1 − exp(−∫₀ᵀ h(τ; θ) dτ)
```

with three suggested thresholds aligned to the project's own README:

| Stratum | Θ (mmHg) | Interpretation | Initial n |
|---|---|---|---|
| Barotitis onset | **60** | mucosal transudate, Teed 1–2 | 1 |
| Sustained pain | **100** | barotitis media, Teed 3 | 2 |
| Rupture risk | **150** | TM perforation / baromyringitis | 3 |

**Fit** {rᵢ, Θᵢ, nᵢ} by maximum likelihood on labeled exposure records using survival-analysis likelihoods (Weathersby 1992 formulation: each subject contributes failure-time or right-censored time). Regularize Θ with priors centered on the clinical thresholds above; let rᵢ vary by phenotype.

**Alternative — Hill/sigmoid dose-response** when only cumulative dose D = ∫|ΔP|dt is available (Eckenhoff 1990, PMID 2246178):
```
P(MEB | D) = D^k / (D₅₀^k + D^k)
```
Use if descent time-series is summarized by AUC; less informative than the hazard form.

**Diving-inspired alternative — modified tissue ratio** (Conkin 1996, PMID 8834946) with log-logistic survival — useful if hypobaric + nitrogen dynamics must be jointly fit.

---

## Calibration Recipe — matching 5.8% population prevalence

**Cohort caveat.** The 5.8% target does not match retrieved cohorts (Landolfi 2009: 2.4% in Italian AF hypobaric chamber; Files 2005: ~7% in military decompression; Ryan 2018: ~20% in commercial adults). State the source cohort for 5.8% in the model card; calibration is valid only for that cohort.

**Primary method: ABC-SMC** (template: Torres-Florez 2025, PMID 40853999).

1. **Priors** on latent physiological parameters θ = (ET_threshold ~ Normal(90, 20²) mmHg, TVP_efficiency ~ Beta, TM_compliance ~ LogNormal, mastoid_volume ~ LogNormal, dysfunction_grade_mix ~ Dirichlet(α_mild, α_mod, α_severe)).
2. **Summary statistics.** Primary: cohort MEB prevalence (target 5.8%, with tolerance). Secondary: severity stratification (Teed grade distribution), rupture rate, ET-lock rate.
3. **Simulator.** Run `barotrauma.models.chamber_risk` on representative descent profiles for N=10⁴ virtual subjects drawn from θ.
4. **Sequential tolerances.** ε₀ = 0.05 (absolute prevalence difference), halve each generation: εₖ₊₁ = 0.5 εₖ. Stop at ε ≤ 0.005.
5. **Particle count.** N = 1,000 per generation, weighted resampling with perturbation kernel.
6. **Validation.** Posterior predictive check against held-out cohort; report Wasserstein distance on prevalence and Teed-grade distributions.

**Scalable alternative — Bayesian History Matching + GP emulator** (template: Andrianakis 2015 PMID 25569850, Jones & Oomen 2025 PMID 39515269) — use if the physics simulator is too slow for ABC. Fit one GP emulator per summary statistic, iteratively prune the "non-implausible" parameter space using implausibility I(θ) = |y_obs − E[f(θ)]| / √(Var + σ²_obs), threshold I < 3.

**Calibration quality targets:** ECE ≤ 0.05, Brier ≤ 0.06 (for 5.8% base rate), 90% prediction interval empirical coverage 88–92%, simulated prevalence within ±0.5% of target.

---

## Key references (DOIs / PMIDs)

- Kanick & Doyle 2005 — doi:10.1152/japplphysiol.00974.2004
- Ryan et al. 2018 — doi:10.1097/MAO.0000000000001779 (PMID 29494475)
- Landolfi et al. 2009 — PMID 20027855
- Files et al. 2005 — PMID 15945394
- Marroni et al. 2026 — doi:10.5603/imh.108038
- Tournoy et al. 2024 — doi:10.28920/dhm54.4.287-295
- Thalmann, Parker, Survanshi, Weathersby 1997 — PMID 9444058 (LEM)
- Parker, Survanshi, Massell, Weathersby 1998 — PMID 9480974
- Weathersby, Survanshi, Homer, Parker, Thalmann 1992 — PMID 1592748
- Eckenhoff, Olstad, Carrod 1990 — PMID 2246178
- Conkin, Kumar, Powell, Foster, Waligora 1996 — PMID 8834946
- Andrianakis et al. 2015 — PMID 25569850 (Bayesian history matching tutorial)
- Torres-Florez et al. 2025 — PMID 40853999 (ABC-SMC COVID calibration)
- Jones & Oomen 2025 — PMID 39515269 (hybrid biophysics + GP + BHM)
- Rodero et al. 2023 — PMID 36271218 (virtual patient cohort calibration)
- Coveney et al. 2021 — PMID 34366883 (restitution curve emulators)
- Paun, Colebank, Husmeier 2025 — PMID 40078149 (GP vs. PCE for haemodynamics)
- Fan et al. 2021 — PMID 33413321 (Platt / isotonic / polynomial ensemble calibration)
- Majlatow et al. 2025 — doi:10.3390/app15147925 (conformal + calibration in healthcare)
