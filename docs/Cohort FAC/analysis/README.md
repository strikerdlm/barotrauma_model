# `docs/Cohort FAC/analysis/` — de-identified outputs only

**Sister folder to `docs/Cohort FAC/2010_2020/` and
`docs/Cohort FAC/2025_2026/`, which are gitignored.** Only outputs
written here may be tracked in git. Keep this folder PII-free by
construction.

## Contents

- [`analysis_plan.md`](analysis_plan.md) — staged plan for completing
  the 2010–2020 incidence paper and analyzing the 2025–2026 preflight
  + director data.

## Raw data lives in the sibling gitignored folders

Raw files under `docs/Cohort FAC/2010_2020/` and
`docs/Cohort FAC/2025_2026/` contain Colombian national IDs (`Cédula`),
names, institutional emails, and mobile numbers. `.gitignore` blocks
`*.xlsx`, `*.xls`, `*.doc`, `*.docx`, `*.pdf`, `*.csv` in those paths.

Before writing any tidy/aggregate output here, strip:

- `Cedula` / ID columns
- `Nombre` / `APELLIDOS Y NOMBRES` / full-name columns
- `Email` / `CORREO INSTITUCIONAL`
- `Celular` / phone
- Any Microsoft-Forms `Id`/`Start time`/`Completion time` metadata
  that can fingerprint a submitter

Age should be bucketed to 5-year bands for any aggregate intended for
publication; exact age retained only in working files that stay in
gitignored paths.

## External API policy

Do **not** pass raw rows containing PII to external LLM/NLP services.
Any LLM-based free-text structuring pipeline must read from a
de-identified working CSV that has already been written under
`2010_2020/` or `2025_2026/` (and therefore is gitignored — fine for
local processing, off-limits for git), never from the Excel source.

## IRB

The DIMAE ethics-board memo that the AMHP manuscript submission
requires (`HOW_TO_CONTINUE.md §1` step 2) must also authorize
secondary analysis and publication of these cohort datasets. Bundle
the request — one memo, two uses.
