# Study Protocol — FAC Chamber Barotrauma Cohort 2010–2026

**Version:** 1.0 | **Date:** 2026-04-25 | **Status:** retrospective, post-hoc

---

## 1. Research Question (PECO)

| Element | Specification |
|---|---|
| **P** Population | Military personnel (FAC) undergoing hypobaric chamber training at DIMAE, Bogotá, Colombia (2,640 m baseline altitude) |
| **E** Exposure | Simulated altitude chamber session (ascent to ≥10,000 ft simulated altitude) |
| **C** Comparator | International sea-level-baseline chamber-barotrauma cohorts (published 2005–2024) |
| **O** Outcome | Clinical ear barotrauma (TEED grade ≥1 or equivalent clinical event per DIMAE physician notation) at any point during or immediately after the chamber session |

---

## 2. Study Design

**Retrospective pooled cohort**, combining two data phases:

- **Phase 1 (2010–2020):** De-identified registry of all chamber-related clinical events, compiled from the Correa Guarín & Jaimes 2022 internal DIMAE draft. Unit of observation: chamber session per trainee. n = 6,565 exposures; n_cases = 161 FAC-only clinical barotrauma.

- **Phase 2 (Feb 2025 – Apr 2026):** Prospective preflight screening data (Microsoft Forms, DIMAE), director-logged chamber runs, and medical events. n = 706 Phase 2 exposures (director log); n_cases = 12 clinical barotrauma.

- **Pooled primary:** 7,271 exposures; 173 events; 2.38% per-exposure (Wilson 95% CI 2.06–2.75%).

---

## 3. Reporting Guideline

**STROBE** (Strengthening the Reporting of Observational Studies in Epidemiology), checklist version for cohort studies. Full item-by-item checklist in `docs/submission/strobe_checklist_fac_cohort.md`.

---

## 4. Primary Outcome

Per-exposure incidence of **FAC-only clinical ear barotrauma** (pooled 2010–2026). Primary estimate: Wilson score interval around a single binomial proportion.

---

## 5. Secondary Outcomes

1. Temporal stability of incidence over 15 years (visual Wilson CI overlap; no formal test — sample sizes not designed for equivalence)
2. Preflight screening flag prevalence (2025–2026 cohort, n = 1,046 submissions)
3. Per-flag denial rate and discrimination
4. Preflight vital signs distribution at 2,640 m baseline

---

## 6. Analytical Plan

All statistics computed in Python (pandas, numpy, scipy.stats). Scripts in `docs/Cohort FAC/analysis/`. Key methods:

- **Binomial proportions:** Wilson score interval (`scipy.stats.proportion_confint(method='wilson')`) throughout. No normal approximation.
- **Temporal stability:** Plot-and-CI overlay (Figure 1). No formal statistical test (year-level denominators not available for Phase 1 per-year rates; Phase 2 per-quarter denominators from director log).
- **No multivariable model in this paper** — prediction modeling is the companion paper (Paper C, Malpica 2026 in review).
- **No imputation** — missing values excluded from denominators with footnote counts.

---

## 7. Inclusion / Exclusion

### Included
- FAC-entity trainees (military or civilian personnel training under FAC administration)
- Sessions resulting in clinical event notation OR completed without event (denominator)
- Phase 1: all years 2010–2020 where case-year is recorded in source registry
- Phase 2: all preflight submissions 2025-02 through 2026-04 with completed forms

### Excluded
- Non-FAC trainees (foreign exchange, civilian agency) — excluded from numerator (primary analysis); included in sensitivity row (Table I)
- Sessions where entity affiliation unascertainable
- Phase 2 partial quarter 2026Q2 (0/8, single run as of April 2026 data cutoff) — excluded from temporal plots (footnoted)

---

## 8. Data Sources

| Source | Period | n | Custodian |
|---|---|---|---|
| Correa Guarín & Jaimes 2022 DIMAE internal draft | 2010–2020 | 6,565 exposures, 257 all-comers events | DIMAE/FAC |
| DIMAE Microsoft Forms preflight screening | Feb 2025 – Apr 2026 | 1,046 submissions | DIMAE/FAC |
| Chamber director log | Feb 2025 – Apr 2026 | 98 runs, 706 exposures | DIMAE/FAC |

Raw data de-identified; case-level data in `docs/Cohort FAC/analysis/phase1_2010_2020_tidy.csv`.

---

## 9. Ethics

Retrospective analysis of de-identified operational medical records held by DIMAE. No new interventions. Conducted under DIMAE institutional authority. Authors hold data custodianship within their institutional role.

---

## 10. Citation Style

Vancouver (numbered). All references DOI-verified via CrossRef/PubMed before final manuscript assembly.

---

## 11. Key References for Methods

- Wilson (1927) — score interval method [Ref 7]
- Agresti & Coull (1998) — approximation vs. exact [Ref 14]
- Brown, Cai & DasGupta (2001) — interval estimation [Ref 15]
- STROBE guidelines — von Elm et al. 2007 (Ann Intern Med 147:573–577; DOI pending verification)
