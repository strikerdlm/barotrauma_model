# Supplemental Digital Content 3

**Calibration summary — full bisection and ABC-SMC results including all rate constants and credible intervals.**

This table provides the complete calibration parameters referenced in Sections 2.8 and 3.1 of the main manuscript. Calibration anchors the per-outcome hazard constants to the pooled Colombian Aerospace Force (FAC) DIMAE 2010–2026 registry (n = 7,271 chamber exposures, n = 173 clinical middle-ear barotrauma events).

| Metric | Value |
|---|---|
| Target per-exposure p<sub>barotitis</sub> (FAC pooled 2010–2026) | 2.38% |
| Wilson 95% confidence interval on target | [2.06%, 2.75%] |
| Achieved per-exposure p<sub>barotitis</sub> (bisection calibrator) | 2.47% |
| Calibration residual (achieved − target) | +0.09 percentage points |
| Career projection (3 exposures, simulated) | 7.23% |
| Pooled FAC 2010–2026 career anchor | 6.97% |
| Career-3 residual (simulated − anchor) | +0.26 percentage points |
| r<sub>barotitis</sub> (bisection point estimate; per-second hazard rate constant) | 5.85 × 10⁻⁸ |
| r<sub>baromyringitis</sub> (bisection point estimate) | 1.75 × 10⁻⁹ |
| r<sub>rupture</sub> (bisection point estimate) | 5.85 × 10⁻¹¹ |
| Bisection iterations to convergence | 6 |
| ABC-SMC posterior mean r<sub>barotitis</sub> (fit against 2.00% target) | 5.07 × 10⁻⁸ |
| ABC-SMC 95% credible interval on r<sub>barotitis</sub> | [3.59 × 10⁻⁸, 8.00 × 10⁻⁸] |
| Bisection re-anchored estimate (5.85 × 10⁻⁸) inside ABC-SMC 95% CrI | Yes |

ABC-SMC = Approximate Bayesian Computation Sequential Monte Carlo (reference 19 in main manuscript). Run configuration: 100 particles, 4 generations, 150 synthetic-cohort subjects per particle, tolerance schedule 13.9 → 5.0 against three summary statistics (cohort prevalence; URI day 4–7 / none gradient; severe / normal severity gradient).
