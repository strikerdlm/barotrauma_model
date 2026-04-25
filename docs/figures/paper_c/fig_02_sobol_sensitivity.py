"""
Paper C — Figure 2. Saltelli-Sobol total-order sensitivity index over four
model parameters evaluated at a moderate-risk reference patient.

Source: barotrauma/v2/sobol_indices.json (canonical), produced by
``python -m barotrauma.v2.sensitivity --n 128 --seed 2026 --save`` —
N = 128 Saltelli base samples × (2 + k=4) = 768 model evaluations,
scrambled-Sobol QMC sequence. The aperture half-point dominates
(S_T = 0.99), approximately fifty-fold above the next-largest indices
(swallow frequency 0.020, aperture free-zone 0.019, mastoid volume 0.005).
The three secondary parameters are within Monte-Carlo noise of each other
across a five-seed sweep at N = 128 (range 0.016–0.033 for swallow and
free-zone). First-order index sum ≈ 0.93; total-order sum ≈ 1.04
(no small-N artifact at the production sample size).

Visualizes the paper's headline empirical-refinement claim: any future
calibration effort should target the aperture half-point first.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "figures" / "_shared"))

from amhp_theme import (
    PALETTE, FONT_FAMILY, FONT_SIZE_AXIS_LABEL, FONT_SIZE_AXIS_TITLE, FONT_SIZE_TITLE,
)
from render import render

# ---------------------------------------------------------------------------
# Data — load from canonical sobol_indices.json (N = 128, seed 2026)
# ---------------------------------------------------------------------------
SOBOL_JSON = ROOT.parent / "barotrauma" / "v2" / "sobol_indices.json"
_sj = json.loads(SOBOL_JSON.read_text())
_st_by_name = dict(zip(_sj["parameters"], _sj["total_order"]))
N_SAMPLES = _sj["n_samples"]
N_EVALS = _sj["n_evaluations"]

# (display label, source-name, parameter range, is_dominant)
_PARAM_META = [
    ("APERTURE_HALF_MMHG",      "Aperture half-point\n(70–180 mmHg)",         "(70–180 mmHg)", True),
    ("SF_DESCENT_PER_HR",       "Swallow frequency, descent\n(30–120 per hr)", "(30–120 per hr)", False),
    ("APERTURE_FREE_ZONE_MMHG", "Aperture free zone\n(20–60 mmHg)",           "(20–60 mmHg)", False),
    ("MASTOID_VOLUME_ML",       "Mastoid volume\n(3–13 mL)",                  "(3–13 mL)", False),
]
PARAMS = [(label, round(_st_by_name[src], 3), is_dom)
          for src, label, _r, is_dom in _PARAM_META]

# Sort descending and reverse for ECharts (top of chart = first item)
PARAMS_SORTED = sorted(PARAMS, key=lambda r: r[1], reverse=True)
PARAMS_REV = list(reversed(PARAMS_SORTED))

labels = [r[0] for r in PARAMS_REV]
values = [r[1] for r in PARAMS_REV]
colors = [PALETTE["vermilion"] if r[2] else PALETTE["blue"] for r in PARAMS_REV]
annot = [f"{r[1]:.2f}" for r in PARAMS_REV]

# Build per-bar data with item style and value labels
bar_data = []
for i, r in enumerate(PARAMS_REV):
    bar_data.append({
        "value": r[1],
        "itemStyle": {"color": colors[i], "borderColor": "#000", "borderWidth": 0.6},
        "label": {"show": True, "position": "right",
                  "fontFamily": FONT_FAMILY, "fontSize": 11, "color": "#000",
                  "fontWeight": "bold",
                  "formatter": annot[i],
                  "distance": 6},
    })

# X-axis to 1.1 leaves room for the right-side value labels above the dominant bar (~1.0)
X_MAX = 1.15

opt = {
    "backgroundColor": "#ffffff",
    "textStyle": {"fontFamily": FONT_FAMILY, "color": "#000000"},
    "animation": False,
    "title": {
        "text": f"Total-order Sobol sensitivity index (Saltelli, N = {N_SAMPLES})",
        "left": "center", "top": 10,
        "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_TITLE, "fontWeight": "normal"},
    },
    "graphic": [
        # X-axis title (bottom-center)
        {"type": "text", "left": "center", "bottom": 38, "z": 100,
         "style": {
             "text": "Total-order Sobol index  S_T",
             "font": f"{FONT_SIZE_AXIS_TITLE}px Arial,sans-serif",
             "fill": "#000",
             "textAlign": "center",
         }},
        # Footnote on the small-N artifact
        {"type": "text", "left": "center", "bottom": 12, "z": 100,
         "style": {
             "text": f"Per-exposure p_barotitis at moderate-risk reference patient · N={N_SAMPLES} Saltelli base · {N_EVALS} evaluations · scrambled-Sobol QMC, seed 2026",
             "font": f"9px Arial,sans-serif",
             "fill": "#444",
             "textAlign": "center",
         }},
    ],
    "grid": {"left": 30, "right": 90, "top": 50, "bottom": 80, "containLabel": True},
    "xAxis": {
        "type": "value", "min": 0, "max": X_MAX,
        "axisLine": {"lineStyle": {"color": "#000", "width": 1}},
        "axisTick": {"lineStyle": {"color": "#000", "width": 1}, "length": 4},
        "axisLabel": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_LABEL, "color": "#000",
                      "formatter": "{value}"},
        "splitLine": {"lineStyle": {"color": "#E5E5E5", "width": 0.5, "type": "dashed"}},
    },
    "yAxis": {
        "type": "category", "data": labels,
        "axisLine": {"lineStyle": {"color": "#000", "width": 1}},
        "axisTick": {"show": False},
        "axisLabel": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_LABEL, "color": "#000",
                      "interval": 0, "lineHeight": 12},
        "splitLine": {"show": False},
    },
    "series": [
        {"name": "S_T", "type": "bar", "data": bar_data,
         "barWidth": "55%",
         "barCategoryGap": "20%"},
    ],
}

OUT_DIR = Path(__file__).resolve().parent
result = render(
    opt,
    out_dir=OUT_DIR,
    slug="fig_02_sobol_sensitivity",
    width_mm=120,
    height_mm=80,
    emit_tiff=True,
)
print("Rendered:", result["png"])
for label, st, _ in PARAMS_SORTED:
    print(f"  {label.replace(chr(10), ' '):<55} S_T = {st:.2f}")
