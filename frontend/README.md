# Barotrauma Risk Assessment Dashboard

A modern, publication-ready TypeScript frontend for analyzing middle ear barotrauma risk during hypobaric chamber training and flight operations.

> **Requires the Python backend.** The default (v2) dashboard does **not** run
> the physics in the browser — it calls the FastAPI sidecar in [`../api/`](../api/),
> which wraps the authoritative `barotrauma.v2` engine. You must start **both**
> the backend (`uvicorn api.main:app --port 8000`) and this dev server. If you
> start only the frontend, the dashboard cannot load presets — the Vite proxy
> returns `API 500` (nothing on `:8000`), or `API 404` if another server is.
> Full step-by-step (two terminals) and troubleshooting are in the
> [repository README](../README.md#interactive-dashboard-react-frontend--fastapi-backend).

## Features

### Publication-Ready Visualizations

- **Risk Gauge** - Animated circular gauge showing real-time risk score with clinical thresholds
- **Pressure Dynamics** - Time series visualization of ambient and middle ear pressure evolution
- **3D Risk Surface** - Interactive WebGL surface showing risk as a function of ET dysfunction and descent rate
- **Risk Heatmap** - Color-coded matrix showing risk across severity levels and descent rates
- **Sensitivity Analysis** - Risk response curves with current position marker
- **Equalization Charts** - ET function capacity and TM displacement over time
- **Altitude Profile** - Descent trajectory with instantaneous risk overlay

### Scientific Accuracy

All visualizations include:
- Clinical threshold annotations (ET Lock: 90 mmHg, Rupture Risk: 150 mmHg)
- Verifiable scientific references panel with PubMed and DOI links
- Model parameters sourced from peer-reviewed literature

### Key References

- Kanick & Doyle (2005) - Barotrauma during air travel: mathematical model
- Ryan et al. (2018) - Prevention of otic barotrauma in aviation
- Bayoumy et al. (2021) - Management of tympanic membrane retractions
- NASA Bioastronautics Data Book - Altitude-pressure formulas

## Technology Stack

- **React 19** - UI framework
- **TypeScript** - Type-safe development
- **Vite** - Fast build tooling
- **ECharts + ECharts-GL** - Publication-quality visualizations with WebGL 3D support
- **Tailwind CSS v4** - Modern styling with CSS-based configuration
- **Framer Motion** - Smooth animations
- **Lucide React** - Beautiful icons

## Quick Start

**1. Start the backend first** (separate terminal, from the repo root):

```bash
cd ..
python3 -m venv .venv && source .venv/bin/activate
pip install -r api/requirements.txt
uvicorn api.main:app --reload --port 8000     # leave running
```

**2. Then start this frontend:**

```bash
# Install dependencies (first run only)
npm install

# Run development server → http://localhost:3000
# Vite proxies /api/* to the backend on :8000
npm run dev

# Build for production (set API origin if not same-origin)
VITE_API_BASE=https://your-api-host npm run build

# Preview production build
npm run preview
```

If the chamber-profile picker stays empty (`API 500` from the proxy when nothing
is on `:8000`, or `API 404` when a different server is), the backend is not the
process on `:8000`. Confirm with `curl localhost:8000/api/health` → it must
return `…"version":"2.2.1"`. See the
[repository README troubleshooting table](../README.md#troubleshooting-the-dashboard).

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── v2/               # API-backed v2 patient/profile/risk UI
│   │   │   ├── PatientBuilder.tsx
│   │   │   ├── ProfilePicker.tsx
│   │   │   ├── ProbabilityTrio.tsx
│   │   │   ├── TrajectoryChart.tsx
│   │   │   ├── TmDisplacementChart.tsx
│   │   │   └── ClinicalDecisionSupport.tsx
│   │   ├── charts/           # ECharts visualization components
│   │   │   ├── RiskGauge.tsx
│   │   │   ├── PressureDynamics.tsx
│   │   │   ├── RiskHeatmap.tsx
│   │   │   ├── RiskSurface3D.tsx
│   │   │   ├── SensitivityAnalysis.tsx
│   │   │   ├── EqualizationChart.tsx
│   │   │   └── AltitudeProfile.tsx
│   │   ├── ui/               # Reusable UI components
│   │   │   ├── MetricCard.tsx
│   │   │   ├── Slider.tsx
│   │   │   ├── TabGroup.tsx
│   │   │   └── ReferencesPanel.tsx
│   │   ├── V2Dashboard.tsx   # Default API-backed dashboard
│   │   └── Dashboard.tsx     # Frozen v1 legacy dashboard
│   ├── lib/
│   │   ├── v2api.ts          # FastAPI client for barotrauma.v2
│   │   ├── simulation.ts     # Legacy in-browser v1 engine
│   │   ├── references.ts     # Scientific references database
│   │   └── chartTheme.ts     # ECharts theme configuration
│   ├── types/
│   │   ├── v2.ts             # API-backed v2 request/response types
│   │   └── simulation.ts     # Legacy v1 type definitions
│   └── App.tsx
├── tailwind.config.js        # Tailwind theme extensions
└── vite.config.ts            # Vite configuration
```

## Simulation Model

**The default v2 dashboard does not compute physics in the browser.** It posts
patient + profile + options to `POST /api/simulate` and renders whatever the
Python `barotrauma.v2` engine returns (trace + three-outcome risk with CIs).
The API client lives in [`src/lib/v2api.ts`](src/lib/v2api.ts); request/response
shapes are documented in [`../api/README.md`](../api/README.md).

The in-browser TypeScript engine (`src/lib/simulation.ts`) below powers **only**
the frozen **v1 legacy** view (reachable via the "View v1 legacy" button), kept
for reproducibility against the pre-2026 single-risk model:

1. **Boyle's Law**: P₁V₁ = P₂V₂ for gas pressure-volume relationships
2. **ET Function**: Equalization rate = f(dysfunction, ΔP, descent_rate)
3. **TM Compliance**: Displacement = ΔP × Compliance (capped at physiological limits)
4. **Risk Score**: Integrated function of pressure differential, time above thresholds, and ET lock probability

### Key Thresholds

| Threshold | Value | Description |
|-----------|-------|-------------|
| Passive ET Opening | 15 mmHg | Pressure at which passive equalization begins |
| ET Lock | 90 mmHg | Active equalization severely impaired |
| Rupture Risk | 150 mmHg | TM perforation risk becomes significant |
| Max TM Displacement | 0.30 mL | Upper physiological bound |

## Development

```bash
# Type checking
npm run typecheck

# Linting
npm run lint

# Build with source maps
npm run build
```

## License

MIT

## Authors

Aerospace Medicine Research Team
