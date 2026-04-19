# Model Card: `barotrauma.v2` — Middle-Ear Barotrauma Risk Model

Version 2.0.0. Created 2026-04-18.

## 1. Intended use

This model estimates the per-exposure probability of middle-ear barotrauma
(MEB) outcomes in a patient undergoing a defined hypobaric-chamber or
pressurized-cabin pressure profile. Intended users: aerospace-medicine
physicians and chamber-training medical officers, research teams studying
MEB physiology, and clinical-decision-support prototypes.

**Not intended for:** real-time in-chamber clinical monitoring (no sensor
integration), treatment planning beyond pre-exposure risk assessment, use
outside adult aviation / military populations without re-calibration.

## 2. Inputs

- **`PatientState`**: anatomy (mastoid + tympanum volumes, TM compliance,
  age, sex), ET function (severity class with underlying opening/closing
  pressures and active resistance), URI state (6-day-window temporal
  staging), Patulous ET state (4-state), chronic rhinitis, medications,
  behavior (Valsalva on/off, interval, habitual-sniffer flag), prior MEB.
- **`ChamberProfile`**: piecewise-linear altitude-vs-time profile (any
  number of ascent, hold, descent, rapid-decompression segments).

## 3. Outputs

Per-exposure:

- `p_barotitis` — probability of Teed I+ (mucosal transudate onset at
  ≥18.4 mmHg absolute ΔP).
- `p_baromyringitis` — probability of Teed III–IV (gross hemorrhage /
  severe pain, ≥95.6 mmHg).
- `p_rupture` — probability of Teed V (TM perforation, ≥150 mmHg — see
  Limitations for threshold caveat).
- `max_abs_delta_p_mmHg` — peak pressure gradient across exposure.
- `auc_mmHg_s_barotitis` / `auc_mmHg_s_baromyringitis` — cumulative dose
  above threshold (mmHg·s).
- `dominant_risk_factor` — human-readable label for the strongest risk
  driver.
- `recommended_max_descent_ft_min` — rate cap at which the model predicts
  acceptable risk (<5% `p_barotitis`) for this patient.
- `risk_category()` — low / moderate / high / very_high.
- Optional 95% credible intervals via Monte-Carlo over physiology priors.

Time-domain trace: per-step `t_s`, `altitude_ft`, `p_ambient_mmHg`,
`p_me_mmHg`, `delta_p_mmHg`, `tm_displacement_ml`, `et_open` indicator,
plus `swallow_events_s` and `valsalva_events_s` timestamp arrays.

## 4. Data and calibration

**Primary anchor:** Colombian Aerospace Force (FAC) pooled 2010–2026
hypobaric-chamber training registry. n = 173 clinical barotrauma events
in 7,271 chamber exposures; per-exposure rate 2.38% (Wilson 95% CI
2.06–2.75%); projected 3-exposure career rate 6.97%. URI and ET
dysfunction reported as dominant risk factors (DIMAE, unpublished —
**currently an internal prior**, awaiting peer-reviewed publication; see
`docs/Cohort FAC/analysis/phase2_summary.md §5`).

**Per-exposure target:** 2.38%, anchored to the pooled FAC 2010–2026
cohort. Bisection-achieved per-exposure 2.47% and career-3 projection
7.23% on an FAC_BOGOTA_DEFAULT synthetic cohort (n = 400). For
cross-reference, Italian Air Force per-exposure rates 1.5–2.5%
(Morgagni 2010 PMID 20824995; Morgagni 2012 PMID 22764614; Landolfi
2009 PMID 20027855) remain the external-validation benchmarks.

**Calibration method:** log-space bisection on `HAZARD_BAROTITIS_R`
against the cohort mean `p_barotitis` over 300–400 synthetic subjects
drawn from FAC-like priors (see `barotrauma/v2/calibration.py`,
`CohortPriors`). Baromyringitis and rupture rate constants are rescaled
proportionally until per-grade cohort data enable independent fitting.

**Calibration persistence:** `barotrauma/v2/calibrated.json` (auto-loaded
on import).

## 5. Assumptions

- **Physics**: Kanick-Doyle 2005 single-compartment ME gas-exchange
  framework (tympanum + mastoid collapsed). Trans-mucosal exchange is
  first-order with Doyle 2011 species rate constants. TM displacement
  obeys Hooke's law with saturation at V_TM,max ≈ 0.025 mL.
- **ET mechanics**: passive ME-side opening at P_O' + closure to P_C';
  active opening via discrete swallows at 31/hr during descent, 5.2/hr at
  cruise (Kanick-Doyle 2005 Table 1 / ref 53); Valsalva every 120 s
  during descent with Mandel 2016-style FGE.
- **URI dynamics**: 6-state temporal modifier table with multiplicative
  effect on RA, P_O', per-descent RR, and the equalization-rate proxy.
  Based on Buchman 1994 (PMID 7934605), McBride 1989 (PMID 2548538),
  Doyle 1999 (PMID 10890787), Chen 2022 (PMID 34919345).
- **Patulous ET**: 4-state (S1 patent / S2 paradoxical-closure / S3
  sniffer / S4 post-plug), Ikeda 2020 PMID 31400157, Shindo 2025.
- **Subject independence**: simulations are per-exposure, per-subject.
  Inter-subject and inter-exposure correlations (e.g. a URI persists
  across a multi-day chamber week) are not modeled.
- **Uniform swallowing**: the model does not condition swallow frequency
  on individual trainee behavior or instruction.

## 6. Limitations

- **FAC anchor is unpublished** — treat the pooled 2010–2026 rate
  (2.38% per-exposure / 6.97% career-3) as an internal prior until the
  FAC cohort paper is formally published. See `HOW_TO_CONTINUE.md` §1
  and `docs/Cohort FAC/analysis/phase2_summary.md`.
- **Rupture threshold at 150 mmHg is conservative.** Biomechanical
  studies report higher TM rupture pressures (~600–750 mmHg). The
  `p_rupture` output should be interpreted as "high risk of perforation"
  rather than a direct rupture probability; it is useful for ranking
  profiles, less so for absolute clinical claims.
- **Barotitis probability is NOT monotonic in descent rate.** The
  barotitis hazard exponent (`n = 1.2`) is sub-quadratic, so the dose-
  time integral dominates the peak pressure. A slow, long descent can
  accumulate more Teed-I transudative dose than a fast, brief descent
  despite a lower peak |ΔP|. This matches the clinical physiology of
  transudative leak (cumulative exposure drives mucosal capillary
  leak) and is consistent with the Italian AF observation that delayed
  ear pain is common even in controlled chamber descents. Rupture
  probability (`n = 3`, peak-dominated) and peak |ΔP| remain monotonic
  in descent rate; tests encode only these latter two monotonicities.
  Users comparing profile risk should look at the full triple
  (`p_barotitis`, `p_baromyringitis`, `p_rupture`), not `p_barotitis`
  alone.
- **No per-subject machine-learning head.** Individual risk conditioning
  on tympanometry / forced-response-test readings is not wired in. v1
  had sklearn scaffolding never trained against real data; we dropped
  it from the v2 surface to avoid implying trained ML capability.
- **Valsalva is idealized** as a 2-s bolus with a multiplicative FGE
  boost. Real Valsalva efficacy varies widely with technique and anatomy.
- **Time-varying R_A (Ghadiali FEM) is not implemented.** v2 uses a
  constant R_A per severity class with a Valsalva multiplier.
- **Chronological exposure carry-over is not modeled.** Two exposures the
  same day reset the ME gas composition to ambient each time. The
  v2.2.2 `career.simulate_career` / `simulate_career_cohort` API
  composes multiple `simulate()` calls but does not pass ME gas state
  or mucosal-fatigue state between exposures; each exposure is a fresh
  draw conditioned on the subject's fixed parameters.
- **Population priors are FAC-demographic.** Transfer to pediatric,
  geriatric, or diving populations requires re-calibration.
- **Calibration is against a self-consistent synthetic cohort**, not an
  external held-out dataset. The Italian AF 1.5–2.5% per-exposure anchor
  is stated in prose but not yet enforced by an automated external-
  validation test. This is the single biggest item for v2.1.

## 6.1 Explicit modeler priors (vs. retrieved data)

These values come from modeler judgment informed by the literature
direction of effect, not from published point estimates. A reviewer can
challenge any of them without challenging the underlying data:

| Quantity | Value | Direction from lit | Magnitude source |
|---|---|---|---|
| Decongestant-in-PET paradoxical RR | 1.4 | Ikeda 2017/2020 clinical reports of worsening autophony with decongestants in PET | Modeler pick; no RCT measures the effect size |
| ET lock threshold | 90 mmHg | Kanick-Doyle 2005 text: "individual-specific limit"; no population distribution published | Anchored to the midpoint of Kanick-Doyle's qualitative description |
| Hazard exponents (n = 1.2 / 2.0 / 3.0) | Sub-quadratic / quadratic / cubic | Survival-analysis pattern (Thalmann LEM, Weathersby 1992) | Chosen to preserve rupture monotonicity while letting dose-time matter for barotitis |
| PET-S1 `per_descent_rr` | 0.4 | Kanick-Doyle protective prediction (ΔP ≈ 0 in simulation) | Modeler pick to convert the physics prediction into a calibrated probability multiplier |
| PET-S2 `per_descent_rr` | 4.0 | Ikeda 2020/2024, Shindo 2025 describe paradoxical closure worse than obstructive baseline | Modeler pick; no cohort data stratifies MEB by PET |
| PET-S3 `per_descent_rr` | 2.5 | Shindo 2025: type-B/C tympanogram in 42.6% of sniffers | Modeler pick |
| URI-peak `meb_rr = 4.25` (day 4–7) | Yes | Buchman 1994: 39% vs 5% ME pressure abnormality ratio ≈ 8× (Lindfors 2021 career OR 9.02) | Halved toward 4.25 to avoid double-counting with the ET-function modifier chain |
| Post-MEB history RR 1.5 | Yes | Boel 2017, Rosenkvist 2008 commercial-pilot repeat-barotrauma trends | Modeler pick; no hypobaric-specific effect size retrieved |
| Swallow-interval jitter ±20% | — | Physiological variation assumption | Modeler pick; jitter prevents grid artifacts |
| Valsalva push amplitude 50 mmHg | — | Typical physiology | Modeler pick within plausible range |

Parameters sourced directly from retrieved literature (NOT modeler priors)
include: URI temporal modifier multipliers (research brief 02 Table),
PET state criteria (Ikeda 2020 JOS), hazard thresholds 18.4 / 95.6 mmHg
(Kanick-Doyle 2005 clinical thresholds 250 / 1300 mmH2O), species rate
constants (Doyle 2011), ET passive opening P_O' 26 mmHg (Kanick-Doyle
Table 1 / Alper 2020 distribution), swallow frequencies 5.2 / 31 per hr
(Kanick-Doyle Table 1 ref 53), FGE 0.32 / 0.16 (Mandel 2016).

## 7. Known risks of misuse

- **Do not** use this model as the sole basis for clearing or denying an
  aviator medical certification. It is a decision-support tool.
- **Do not** substitute this for direct tympanometry or FRT measurement
  in a patient with symptomatic ETD.
- **Do not** extrapolate the Patulous-S1 "protective" output to
  clinically green-light high-altitude operations for PET patients — the
  S2 state (inflammation-induced paradoxical closure) can flip the
  prediction dramatically.

## 8. Validation

Automated tests (`tests/test_v2_*.py`, 44 cases):

- Standard-atmosphere altitude↔pressure parity.
- Groth 1986 short-cycle validation (healthy ears tolerate; <2%
  `p_barotitis`).
- Monotonicity: peak |ΔP| and rupture hazard increase with descent rate.
- FAC baseline simulates to `low`/`moderate` risk category.
- Patulous-S1 reproduces Kanick-Doyle zero-ΔP prediction exactly.
- URI/PET/rhinitis modifier composition: peak URI > baseline, AR+URI >
  URI alone, paradoxical decongestant in PET > protective in healthy.
- Severe ETD simulates to higher risk than mild and normal.
- Calibration converges within ±0.5% of the target per-exposure
  prevalence and preserves URI dominance (day_4_7 > 2× none).

External validation anchors (not yet automated):

- Italian AF per-exposure barotitis rate 1.5–2.5% (Morgagni 2010/2012,
  Landolfi 2009).
- Pooled FAC 2010–2026 career rate 6.97% projected from 3 per-exposure
  samples against an achieved 2.47% per-exposure (~7.23%).
- Kanick-Doyle 2005 Fig 3 qualitative trace matching (pending visual
  regression test).

## 9. Version history

See [`CHANGELOG.md`](../CHANGELOG.md).

## 10. Citation

Malpica, D.L. (2026). *barotrauma_model v2: Physics-informed middle-ear
barotrauma risk prediction for hypobaric-chamber training, anchored to the
Colombian Aerospace Force cohort.* Version 2.0.0.
https://github.com/strikerdlm/barotrauma_model

## 11. Contact / maintainer

Dr. Diego L. Malpica, MD — Aerospace Medicine, Colombia
- ORCID: [0000-0002-2257-4940](https://orcid.org/0000-0002-2257-4940)
- GitHub: [@strikerdlm](https://github.com/strikerdlm)
