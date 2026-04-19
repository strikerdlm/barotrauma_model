# `api/` — FastAPI sidecar for the React/TS dashboard

Single source of truth: the Python `barotrauma.v2` engine is authoritative.
This FastAPI service exposes it over HTTP/JSON so the TypeScript frontend
never re-implements the physics.

## Run locally

```bash
pip install -r api/requirements.txt
uvicorn api.main:app --reload --port 8000
```

The Vite dev server (`frontend/`, port 3000) proxies `/api/*` to
`http://localhost:8000` via `frontend/vite.config.ts`. Start both:

```bash
# terminal 1
uvicorn api.main:app --reload --port 8000
# terminal 2
cd frontend && npm run dev
```

Then open http://localhost:3000 — all `/api/*` requests reach the Python
service.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Liveness + engine version |
| GET | `/api/scenarios` | List preset chamber profiles |
| GET | `/api/scenarios/{key}` | Single preset detail |
| POST | `/api/simulate` | Run a simulation, return trace + three-outcome risk |

OpenAPI schema at `/docs` (Swagger) and `/redoc` (ReDoc) when the server
is running.

### `POST /api/simulate` — request shape

```json
{
  "patient": {
    "uri": "day_4_7",
    "pet": "normal",
    "rhinitis": "allergic",
    "medication": "none",
    "anatomy": { "mastoid_volume_ml": 5.5 },
    "et": { "severity": "moderate" }
  },
  "profile": { "preset": "fac_bogota_default" },
  "options": { "dt_s": 0.1, "with_ci": true, "ci_n_samples": 200, "rng_seed": 42 }
}
```

Every `patient` field is optional; omitted fields default to the v2
dataclass defaults (healthy ear, no URI, no PET, etc.). `profile.preset`
accepts any key from `barotrauma.v2.scenarios.PRESETS`; for a custom
profile send `{ name, start_altitude_ft, segments: [{duration_s,
end_altitude_ft, label}] }` instead.

### `POST /api/simulate` — response shape

```ts
{
  trace: {
    t_s: number[], altitude_ft: number[], p_ambient_mmHg: number[],
    p_me_mmHg: number[], delta_p_mmHg: number[], tm_displacement_ml: number[],
    et_open: boolean[], swallow_events_s: number[], valsalva_events_s: number[]
  },
  risk: {
    p_barotitis, p_baromyringitis, p_rupture,
    ci95_barotitis: [lo, hi] | null,  // only when with_ci=true
    ci95_baromyringitis: [lo, hi] | null,
    ci95_rupture: [lo, hi] | null,
    max_abs_delta_p_mmHg, auc_mmHg_s_barotitis, auc_mmHg_s_baromyringitis,
    dominant_risk_factor: string,
    recommended_max_descent_ft_min: number,
    risk_category: "low" | "moderate" | "high" | "very_high"
  },
  notes: string[],
  profile_name: string,
  total_duration_s: number
}
```

## CORS

Allowed origins in dev: `http://localhost:{3000,5173}` (Vite default +
project override) and their `127.0.0.1` equivalents. Update
`api/main.py::add_middleware` for production.

## Versioning

The API's `version` header matches the `barotrauma` package version. When
v2.3.0 lands, no frontend changes are needed for physics — the extra
state (Zhang vortex pumping term, Holm anatomy covariates, Voigt/Lee/
Sudhoff modifiers) flows through the existing `PatientState` schema if
added as optional fields. New physics switches go in `options`.
