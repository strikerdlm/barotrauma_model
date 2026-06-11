# Migration Guide: v1 → v2

The v1 API is frozen but still importable. This document maps the v1 public
API to its v2 equivalent.

## Top-level imports

| v1 | v2 |
|---|---|
| `from barotrauma import HypobaricChamberRiskModel, ChamberScenario` | `from barotrauma.v2 import simulate, PatientState, ChamberProfile` |
| `from barotrauma.models.chamber_risk import ChamberScenario` | `from barotrauma.v2.types import PatientState` |
| `from barotrauma.analysis.statistics import ...` | `from barotrauma.legacy.analysis.statistics import ...` |

## Minimal simulation

### v1

```python
from barotrauma import HypobaricChamberRiskModel, ChamberScenario

scenario = ChamberScenario(
    start_altitude_ft=25000,
    descent_rate_ft_min=3000,
    et_severity="moderate",
)
model = HypobaricChamberRiskModel()
result = model.simulate_descent(scenario)
print(result.risk_category, result.risk_score)
```

### v2

```python
from barotrauma.v2 import simulate, PatientState, EtFunction
from barotrauma.v2.scenarios import USAFSAM_TYPE_I

patient = PatientState(et=EtFunction(severity="moderate"))
result = simulate(patient, USAFSAM_TYPE_I)
print(result.risk.risk_category(), result.risk.p_barotitis)
```

Key differences:

- v2 separates patient state from the chamber profile. A chamber profile is
  now a piecewise-linear `ChamberProfile` (any number of ascent/hold/
  descent/RD segments), not a single descent rate.
- v2 returns per-outcome probabilities (`p_barotitis`, `p_baromyringitis`,
  `p_rupture`) from a dose-response hazard model, not an abstract 0–1
  score.
- v2 exposes the dominant risk factor, recommended safe descent rate, and
  optional Monte-Carlo credible intervals.

## State-variable mapping

### ET severity

| v1 `et_severity` | v2 |
|---|---|
| `"mild"` | `EtFunction(severity="mild")` |
| `"moderate"` | `EtFunction(severity="moderate")` |
| `"severe"` | `EtFunction(severity="severe")` |

v2 also has `"normal"` for healthy baseline and decouples severity from
URI state, Patulous state, and chronic rhinitis (which were not modeled in
v1).

### Valsalva

v1 had `enable_valsava: bool` (note the typo) and `valsalva_interval_s`.
v2 keeps both but on `PatientState` rather than the scenario, and uses
the correctly-spelled `enable_valsalva`:

```python
PatientState(enable_valsalva=True, valsalva_interval_s=120.0)
```

### Patient anatomy

v1 hardcoded `tympanum_volume_ml=1.0` and `mastoid_volume_ml=7.75` on the
scenario. v2 exposes a full `PatientAnatomy` dataclass and draws
population samples from a log-normal prior in the calibration module:

```python
from barotrauma.v2.types import PatientAnatomy
anat = PatientAnatomy(tympanum_volume_ml=1.1, mastoid_volume_ml=4.2)
patient = PatientState(anatomy=anat)
```

## Risk output mapping

| v1 | v2 |
|---|---|
| `result.risk_score` (0–1 abstract) | `result.risk.p_barotitis` (calibrated probability) |
| `result.risk_category` (`"Low"`/`"Moderate"`/`"High"`) | `result.risk.risk_category()` (`"low"`/`"moderate"`/`"high"`/`"very_high"`) |
| — | `result.risk.p_baromyringitis` (Teed III–IV) |
| — | `result.risk.p_rupture` (Teed V) |
| `result.metrics["max_abs_deltaP_mmHg"]` | `result.risk.max_abs_delta_p_mmHg` |
| — | `result.risk.dominant_risk_factor` |
| — | `result.risk.recommended_max_descent_ft_min` |

## Trace output mapping

| v1 (`ChamberResult`) | v2 (`SimulationTrace`) |
|---|---|
| `result.time_s` | `result.trace.t_s` |
| `result.altitude_ft` | `result.trace.altitude_ft` |
| `result.P_amb_mmHg` | `result.trace.p_ambient_mmHg` |
| `result.P_ME_mmHg` | `result.trace.p_me_mmHg` |
| `result.delta_P_mmHg` | `result.trace.delta_p_mmHg` |
| `result.tm_displacement_ml` | `result.trace.tm_displacement_ml` |

## Legacy API still available

If you cannot migrate, the v1 entry points are kept verbatim:

```python
from barotrauma.legacy.models.chamber_risk import (
    HypobaricChamberRiskModel, ChamberScenario,
)
```

They produce identical outputs to v1. They are frozen: bugs in v1 are not
fixed (re-implement against v2 instead).

## When NOT to migrate

- If you have v1-trained artifacts (e.g. saved `sklearn` pipelines from
  `ml_risk_model.py`) you want to re-use verbatim. v2 does not yet ship an
  ML head; training a v2 ML head requires a new labeled cohort.
- If you have archived v1 analyses or operational records whose outputs must
  remain reproducible bit-for-bit from the v1 code path.
