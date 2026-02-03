# Barotrauma Risk Assessment Dashboard

A modern, publication-ready TypeScript frontend for analyzing middle ear barotrauma risk during hypobaric chamber training and flight operations.

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

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
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
│   │   └── Dashboard.tsx     # Main dashboard component
│   ├── lib/
│   │   ├── simulation.ts     # Barotrauma simulation engine
│   │   ├── references.ts     # Scientific references database
│   │   └── chartTheme.ts     # ECharts theme configuration
│   ├── types/
│   │   └── simulation.ts     # TypeScript type definitions
│   └── App.tsx
├── tailwind.config.js        # Tailwind theme extensions
└── vite.config.ts            # Vite configuration
```

## Simulation Model

The TypeScript simulation engine implements a physics-informed, physiology-constrained model:

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
