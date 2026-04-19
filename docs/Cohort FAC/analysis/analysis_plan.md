# FAC Cohort Analysis Plan — 2010–2020 Paper Completion + 2025–2026 Extension

**Status:** 2026-04-19 — exploration complete; plan awaiting Diego's
decisions on publication target and data-sharing model.
**Repo constraint:** raw files under `docs/Cohort FAC/` are gitignored
(PII: Cédula, names, emails, phones). Only de-identified analysis
outputs may land under version control.

---

## 1. What we have — inventory

### 1.1 `2010_2020/` — unfinished DIMAE manuscript + two databases

| File | Shape | Content |
|---|---|---|
| `barotrauma articulo 2020.doc` | 896 lines of text | 2022 DIMAE internal manuscript by Correa Guarín (ENT) + Jaimes (Aerospace Med). **Draft — Results section is a placeholder, Conclusions = "xxxx".** |
| `Barotrauma.xlsx` | 1 sheet, 257 rows × 29 cols | Clean structured cases database. Columns: `Total, Por_año, Por_trimestre, Fecha_vuelo, Grado, Nombre, Cedula, Edad, Genero, Entidad, Unidad, Especialidad, SPN, IV_A, RD, Lesion, DCS, Parte, Alumno, Instructor, Perfil, Segmento, Altura, ANT_MED, ACCION_VUELO, TTO, INCAP, SECUELAS, ACCION_CA`. |
| `base de datos barotrauma.xls` | 5 sheets | Older wide-format raw roster with multi-row headers. `general` 315×41, `Enf por descompresio` 19×36 (DCS cases), `fechas Enf por descompresion` 19×16. Probably the source database the curated 257-row file was derived from. |

**Gotcha:** `Por_año` is a within-year case number (1, 2, 3 …), NOT a
year. The actual year lives in `Fecha_vuelo`. Any prevalence calculation
must parse `Fecha_vuelo` as a date and ignore `Por_año` as a year.

**Authoritative prevalence from the draft paper's Methods (line 698 of
the converted text):**

> "…la población de tripulantes de la Fuerza Aérea Colombiana, que
> asiste a la cámara de altura entre 2010 y 2020 en la Dirección de
> Medicina Aeroespacial, en total fueron **6565** de los cuales **257**
> presentaron síntomas de barotrauma, o bloqueo de oído durante el
> ejercicio en la cámara o síntomas tardíos…"

So the 2010–2020 denominator is **6,565 exposures** and the numerator
is **257 events (any grade + ear blocking + late-onset)**. Per-exposure
rate = 3.91%. Projected 3-career-exposure career rate =
1 − (1 − 0.0391)^3 = **11.3%**, which is almost **double the 5.8%
career anchor** the AMHP manuscript assumes. This discrepancy is
load-bearing for model calibration and must be reconciled before the
FAC paper is submitted.

Likely reconciliation axes: (a) the 257 includes sub-clinical "ear
blocking" + late-onset symptoms that wouldn't count as Teed-graded
barotitis; (b) the 5.8% anchor used a per-career (unique individuals
with any history) rather than per-exposure denominator; (c) the ratio
of instructors to students across exposures differs.

### 1.2 `2025_2026/` — operational data Jan 2025 → Apr 2026

| File | Shape | Content |
|---|---|---|
| `EVALUACIÓN MEDICA PRE VUELO DE LA CAMARA DE ALTURA.xlsx` | 1 sheet, 1,046 rows × 58 cols | Microsoft Forms preflight evaluation. Covers Feb 3 2025 → Apr 14 2026. Demographics (grade, specialty, unit, age, ID — PII), 17 yes/no medical screening questions (with free-text "Especifique" fields in Spanish), vital signs (PAS/PAD/FC/SpO2), physical-exam findings, diagnostic notes, fitness decision ("Apto para entrenamiento"), in-flight medical event free-text. |
| `FORMATO DE DIRECTOR MEDICO DE ENTRENAMIENTO FISIOLÓGICO CÁMARA HIPOBÁRICA.xlsx` | 1 sheet, 98 rows × 35 cols | Medical-director chamber-run log. Profile type, initial O₂ pressure, student count, event checklist (9 stages), emergency flags, Spanish free-text narrative of medical/technical/safety events. |

**Quick signal from the preflight data:**

- **Ear/URI history flag "SI":** 36/1046 (3.4%)
- **Recent respiratory symptoms "SI":** 34/1046 (3.3%)
- **Malaise/fever/fatigue "SI":** 4/1046 (0.4%)
- **Fitness decision "NO":** ~23/1046 (2.2%) — crude denial rate
- **"EVENTO MEDICO EN VUELO" populated:** 6/1046 (0.6%) — in-flight events explicitly noted (otalgia, plenitud aural, DCS-like arthralgias, etc.)

**Data-quality gotchas already surfaced:**

1. **Fitness decision column is messy:** 773 "SI", 200 "SI\nSI\nSI\nSI\nSI" (multi-student entries collapsed), 20+3 "NO" variants, edge cases "PENDIENTE" / "R" / "S" / "si". Must be normalized before a denial-rate analysis is meaningful.
2. **No clean join key** between the 1,046 preflight rows and the 98 director runs. Preflight's "ESCOJA EL ENTRENAMIENTO" is training **type** (INICIAL/RECURRENTE), not training **number**. Director's "NUMERO DE ENTRENAMIENTO" runs 1..98. Only link is `FECHA` (date) — join must be fuzzy-by-date plus student name, and the 200 multi-student preflight rows mean one form sometimes represents a whole class.
3. **Free-text Spanish "Especifique" columns** and director-narrative columns need structured extraction (regex for common ENT terms, or LLM categorization after de-identification).

---

## 2. Decisions Diego must make — plan diverges on these

### 2.1 Publication target

| Option | Meaning | Effort | Fit |
|---|---|---|---|
| **A. Complete the 2020 paper** | Finish Correa/Jaimes 2022 DIMAE draft with real Results + Conclusions; keep scope 2010–2020; target AMHP or *Aerosp Med Hum Perform* directly | Medium — fills a draft | Matches `HOW_TO_CONTINUE.md §1` FAC cohort anchor |
| **B. New 2010–2026 extended paper** | Absorb 2010–2020 + 2025–2026 into a single cohort paper with a ~16-year window and the operational URI/vital-signs data as value-add | Larger — two cohorts, two methodologies | Stronger novelty; unifies anchor + URI validation |
| **C. Two papers in sequence** | Paper 1 = close the 2020 draft for publication. Paper 2 = 2025–2026 operational-epidemiology companion focused on preflight symptoms → denial decision → in-flight event linkage | Largest — two submissions | Cleanest split; 2025–2026 narrative isn't constrained to match 2020 methodology |
| **D. Data-only release** | Package cleaned de-identified datasets + analysis notebooks as a supplementary release; no new paper | Smallest | Still useful for v2.3.0 calibration but doesn't produce the peer-reviewed anchor `HOW_TO_CONTINUE §1` asks for |

**Strong recommendation: A**, with the 2025–2026 data reserved as a
short follow-on paper (option C's Paper 2) and as the v2.3.0
calibration dataset. Reasons: the 2020 draft already exists and has the
clean structured numerator (257 cases) + explicit denominator (6,565);
completing it closes the `§1` peer-review gap immediately; the 2025–
2026 data then funds a separate narrower question about pre-flight
screening fidelity.

### 2.2 Data-sharing model

| Option | Meaning | Risk |
|---|---|---|
| **Private** | `docs/Cohort FAC/` stays gitignored; de-identified aggregates go to `docs/Cohort FAC/analysis/` and are tracked | No PII exposure; reproducibility limited to collaborators with the raw files |
| **De-identified public** | Publish cleaned CSVs (no Cédula, no name, no email, no phone, age bucketed, institutional unit generalized) alongside the paper | Good for citation + downstream use; requires a DIMAE IRB amendment covering publication |
| **Don't publish data** | Publish only the paper; share data on request | Standard for older cohort papers; weaker reproducibility signal |

**Strong recommendation: De-identified public** after the DIMAE IRB
memo that `HOW_TO_CONTINUE.md §1` already asks for covers both analysis
and publication. Bundle the ask.

### 2.3 Free-text handling

| Option | Meaning |
|---|---|
| **Regex + manual QC** | Pattern-match common Spanish ENT terms (otalgia, barotrauma, plenitud, rinitis, gripa, congestión, fiebre, tos, flema…) with a list curated from a 50-row manual labeling pass |
| **LLM categorization** | Send each "Especifique"/narrative row through an LLM that emits structured fields (symptom category, severity, anatomic side). **Requires de-identification upstream** — strip Cédula/name/email before any API call |
| **Defer** | v1 paper uses structured columns only; free-text reserved for v2 |

**Soft recommendation: Regex + manual QC for v1 paper** (the structured
columns alone carry enough signal for prevalence + denial-rate + event-
rate endpoints). LLM pass becomes the v2 refinement once the paper is
in review.

---

## 3. Fixed constraints

**C1. PII never leaves the gitignore boundary.** Any tidy/analysis
output written under `docs/Cohort FAC/analysis/` must already be
de-identified: drop `Cedula`, `Nombre`/`APELLIDOS Y NOMBRES`, `Email`,
`Celular`, `CORREO INSTITUCIONAL`. Age may be bucketed to 5-year bands
for public aggregates; exact age retained only in gitignored working
files.

**C2. IRB/ethics cover.** The DIMAE memo the AMHP submission needs
(`HOW_TO_CONTINUE.md §1` step 2) must also cover secondary analysis +
publication of these datasets. One request, two uses.

**C3. External API calls on raw rows are forbidden** until C1 and C2
are satisfied.

**C4. Any figure generated for the paper goes to
`docs/Cohort FAC/analysis/figures/` at ≥600 dpi TIFF (AMHP / aerospace-
medicine journal standard).**

---

## 4. Phased plan — acceptance criteria per phase

### Phase 0 — Safety + provenance (1 h, no dependencies)

- [ ] Confirm `.gitignore` entries (done 2026-04-19, commit pending).
- [ ] Write `docs/Cohort FAC/analysis/README.md` documenting file
      provenance, column dictionary, and the gitignore rules.
- [ ] Diego confirms decisions 2.1 / 2.2 / 2.3.

**Acceptance:** gitignore blocks all raw xlsx/xls/doc files; Diego has
committed to a publication target + data-sharing model + free-text
pathway.

### Phase 1 — 2010–2020 denominator + numerator reconciliation (1 day)

- [ ] Parse `Barotrauma.xlsx` 257 cases; convert `Fecha_vuelo` to ISO
      date; reconstruct per-year case counts 2010–2020.
- [ ] Read `base de datos barotrauma.xls` sheet `general` row-0
      descriptive headers; re-map the 315 rows into a tidy form;
      confirm whether these 315 overlap with the 257 clean cases or
      represent a different roster.
- [ ] Cross-reference against the draft paper's "6,565 exposures"
      denominator — find the chamber-run logbook that yields 6,565.
      (May require asking DIMAE for the operational logbook or
      accepting 6,565 as author-attested.)
- [ ] Compute per-exposure prevalence with Wilson 95% CI; stratify by
      year, grade, specialty, chamber profile (SPN/IV-A/RD), student
      vs. instructor.
- [ ] Compare to AMHP manuscript's 5.8% career anchor; produce a
      reconciliation note (per-exposure vs. per-career, TEED-grade
      definition, sub-clinical inclusion).

**Acceptance:** a single CSV `phase1_2010_2020_tidy.csv` (de-
identified), a summary table with Wilson 95% CI for per-year prevalence,
and a written reconciliation that lands the 2010–2020 paper's
incidence within ±0.2 pp of a defensible value.

### Phase 2 — 2025–2026 structured extraction (2 days)

- [ ] Parse preflight xlsx; normalize the fitness-decision column (SI,
      NO, variants, multi-student rows); split the multi-student
      "SI\nSI\nSI…" entries back into per-student records where
      possible.
- [ ] Compute denial rate overall + stratified by each medical-
      screening question (17 yes/no flags).
- [ ] Compute URI-symptom prevalence (cols 24/26/39 — ear/nasal,
      respiratory, malaise-fever) for the cohort; compare to AMHP
      paper's URI modifier table (`docs/research_notes/02_uri_et_
      dysfunction.md`).
- [ ] Summarize vital signs (PAS, PAD, FC, SpO2) distributions overall
      + for denied vs. cleared subgroups.
- [ ] Tally the 6 in-flight medical events (col `EVENTO MEDICO EN
      VUELO`) by symptom category.
- [ ] Parse director xlsx; map the 98 training runs to dates +
      attendees per the director-logged student count.
- [ ] Date-based fuzzy join preflight rows ↔ director runs to validate
      the 1,046 preflights map to ~98 × ~10 student slots.

**Acceptance:** `phase2_2025_2026_tidy.csv` + director-run summary +
event-rate table with Wilson CI; reconciliation of
preflight-roster ↔ director-run attendance within ±10%.

### Phase 3 — Free-text structuring (2 days, optional for v1 paper)

- [ ] Regex-extract ENT terms from preflight "Especifique" columns and
      director "Describa evento medico" narratives.
- [ ] Manual QC on a random 50-row sample from each.
- [ ] If regex precision < 80% for any key term (otalgia, barotrauma,
      plenitud, congestión, gripa), escalate to LLM categorization
      with a de-identified dataset.

**Acceptance:** a structured event-category column added to both tidy
CSVs; precision ≥ 80% against manual labels on the held-out sample.

### Phase 4 — Paper draft + figures (3–5 days)

- [ ] If option A: complete `barotrauma articulo 2020.doc` by filling
      Results + Conclusions from Phase 1 outputs; convert to
      `manuscript_fac_2010_2020.md` for source control; build figure
      set (prevalence-by-year time series, TEED-grade bar chart,
      specialty stratification, chamber-profile stratification).
- [ ] If option C: draft a separate `manuscript_fac_2025_2026.md`
      focused on preflight screening → denial → in-flight event chain.
- [ ] Target journal selection; use `amhp-submit` skill if AMHP
      remains the target; otherwise switch to the `frontend-design`
      or `npj-pdf-export` template as appropriate.

**Acceptance:** manuscript draft with filled Results + Conclusions,
figures at ≥600 dpi, and a reviewer-verification checklist (see the
AMHP submission pattern under `docs/submission/`).

---

## 5. Immediate next steps — recommend tackle in this order

1. **Commit the gitignore + this plan.** Stops accidental PII exposure.
   (Ready to push after this document lands.)
2. **Diego's decisions:** 2.1 (target), 2.2 (data-sharing), 2.3 (free-
   text pathway).
3. **Bundle the DIMAE IRB request** — one memo covers both AMHP
   submission + FAC cohort analysis/publication.
4. **Phase 1 execution** — I can start immediately after decision 2.1
   lands; no blockers otherwise.
5. **Parallel UI track** — TM-displacement subplot on the v2 dashboard
   remains ready to ship and is fully independent of this data work.
   Say the word.

---

## Appendix — column dictionary pointers (for future agents)

- 2010–2020 `Barotrauma.xlsx` 29 cols: see §1.1 list. `SPN`, `IV_A`,
  `RD` are chamber-profile type flags (from `base de datos` row 2
  header: "PERFIL REALIZADO").
- 2025–2026 preflight 58 cols: `Id/Start/Completion/Email/Name` are
  Microsoft Forms metadata; cols 6–21 are demographics + training
  context; cols 22–43 are 17 yes/no medical flags each followed by a
  free-text `Especifique*` column (exceptions: cols 34, 35, 38, 39,
  41–43 don't have an Especifique); cols 44–47 vital signs; 48–52
  exam + fitness; 53 referral reason; 54–57 in-flight event + follow-
  up.
- 2025–2026 director 35 cols: `Id/Start/Completion/Email/Name` are
  metadata; 6–10 run identification + student count; 11–12 inter-
  service notifications; 13–21 event-stage checklist; 22–30 emergency
  flags + free-text descriptions; 31–34 closing notes.
