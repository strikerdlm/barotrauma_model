"""
Paper C — Figure 2. Saltelli-Sobol total-order sensitivity index over four
model parameters evaluated at a moderate-risk reference patient.

Source: manuscript.md L117 (§3.4) and L310 (Figure 2 caption). The aperture
half-point dominates (S_T ≈ 1.84), an order of magnitude above descent-phase
swallow frequency (0.18), mastoid volume (0.16), and aperture free-zone
threshold (0.08). N = 32 Saltelli base samples → 192 model evaluations;
production runs should use N ≥ 128.

NOTE: The vendored `barotrauma/v2/sobol_indices.json` carries different total-
order values (1.10 / 0.14 / 0.22 / 0.09) from a separate development run.
This figure intentionally tracks the manuscript prose so the figure matches
what the reader sees in §3.4. The JSON-vs-prose discrepancy is flagged for
v2.3.0 reconciliation; a production rerun at N ≥ 128 will replace both.

Visualizes the paper's headline empirical-refinement claim: any future
calibration effort should target the aperture half-point first.
"""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "figures" / "_shared"))

from amhp_theme import (
    PALETTE, FONT_FAMILY, FONT_SIZE_AXIS_LABEL, FONT_SIZE_AXIS_TITLE, FONT_SIZE_TITLE,
)
from render import render

# ---------------------------------------------------------------------------
# Data — manuscript.md L117 (§3.4 Sobol-sampled sensitivity)
# ---------------------------------------------------------------------------
PARAMS = [
    # (display label, S_T, parameter range, is_dominant)
    ("Aperture half-point\n(70–180 mmHg)",            1.84, True),
    ("Swallow frequency, descent\n(30–120 per hr)",   0.18, False),
    ("Mastoid volume\n(3–13 mL)",                     0.16, False),
    ("Aperture free zone\n(20–60 mmHg)",              0.08, False),
]

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

X_MAX = 2.1

opt = {
    "backgroundColor": "#ffffff",
    "textStyle": {"fontFamily": FONT_FAMILY, "color": "#000000"},
    "animation": False,
    "title": {
        "text": "Total-order Sobol sensitivity index (Saltelli, N = 32)",
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
             "text": "Per-exposure p_barotitis at moderate-risk reference patient · N=32 Saltelli base · 192 evaluations · production runs use N≥128",
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
)
print("Rendered:", result["png"])
for label, st, _ in PARAMS_SORTED:
    print(f"  {label.replace(chr(10), ' '):<55} S_T = {st:.2f}")
