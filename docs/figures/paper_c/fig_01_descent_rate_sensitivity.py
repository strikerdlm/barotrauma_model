"""
Paper C — Figure 1. Descent-rate sensitivity, healthy patient on 25,000-ft descent.

Two stacked panels (Table IV data):
  A — Peak |ΔP| (mmHg) vs descent rate, log-x axis
      Saturates near 400 mmHg above ~7,500 ft·min⁻¹.
      Threshold reference lines at Kanick-Doyle barotitis (18.4 mmHg),
      baromyringitis (95.6 mmHg), and rupture (150 mmHg).
  B — Per-exposure barotitis and rupture probability vs descent rate
      Barotitis grows monotonically across the full 500–10,000 ft·min⁻¹ range
      because the dose-time integral does not saturate as sharply as the peak.

Frames the key clinical message: chamber descent rates of 1,000–10,000 ft·min⁻¹
push max |ΔP| through three Kanick-Doyle clinical thresholds.

Canvas: 120 mm × 140 mm at 600 dpi → 1417 × 1654 logical px.
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
# Data — Table IV, manuscript.md L295–L302
# ---------------------------------------------------------------------------
DESCENT = [
    # rate (ft/min), max |dP| mmHg, p_barotitis %, p_rupture %
    (300,   10,  0.00, 0.00),
    (500,   16,  0.00, 0.00),
    (1000,  36,  0.04, 0.00),
    (2000,  59,  0.51, 0.00),
    (3000,  99,  1.51, 0.00),
    (5000,  274, 7.19, 0.17),
    (7500,  363, 9.71, 1.00),
    (10000, 405, 9.90, 1.57),
]
rates = [d[0] for d in DESCENT]
dp_max = [d[1] for d in DESCENT]
p_baro = [d[2] for d in DESCENT]
p_rupt = [d[3] for d in DESCENT]

# Clinical thresholds (Kanick-Doyle 2005, manuscript §2.5)
THR_BAROTITIS = 18.4
THR_MYRINGITIS = 95.6
THR_RUPTURE = 150.0

# Plot points as [x, y]
dp_points = [[r, y] for r, y in zip(rates, dp_max)]
baro_points = [[r, y] for r, y in zip(rates, p_baro)]
rupt_points = [[r, y] for r, y in zip(rates, p_rupt)]

# Per-point data labels — only show when meaningful (>0 or saturating)
def baro_label(v):
    return f"{v:.2f}%" if v > 0.0 else ""

def rupt_label(v):
    return f"{v:.2f}%" if v > 0.0 else ""

baro_label_data = [{"value": [r, y], "label": {"show": y > 0.0,
                    "position": "top",
                    "fontFamily": FONT_FAMILY, "fontSize": 9, "color": "#000",
                    "formatter": baro_label(y)}}
                   for r, y in zip(rates, p_baro)]
rupt_label_data = [{"value": [r, y], "label": {"show": y > 0.0,
                    "position": "bottom",
                    "fontFamily": FONT_FAMILY, "fontSize": 9, "color": "#000",
                    "formatter": rupt_label(y)}}
                   for r, y in zip(rates, p_rupt)]
dp_label_data = [{"value": [r, y], "label": {"show": True,
                    "position": "top",
                    "fontFamily": FONT_FAMILY, "fontSize": 9, "color": "#000",
                    "formatter": str(y)}}
                 for r, y in zip(rates, dp_max)]

opt = {
    "backgroundColor": "#ffffff",
    "textStyle": {"fontFamily": FONT_FAMILY, "color": "#000000"},
    "animation": False,
    "title": [
        {"text": "A", "left": 8, "top": 6,
         "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": 16, "fontWeight": "bold"}},
        {"text": "Peak |ΔP| vs descent rate (25,000-ft descent, healthy patient)",
         "left": "center", "top": 8,
         "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_TITLE, "fontWeight": "normal"}},
        {"text": "B", "left": 8, "top": 836,
         "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": 16, "fontWeight": "bold"}},
        {"text": "Per-exposure clinical-outcome probability vs descent rate",
         "left": "center", "top": 838,
         "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_TITLE, "fontWeight": "normal"}},
    ],
    "grid": [
        # Panel A — top
        {"left": 60, "right": 30, "top": 38, "height": 700, "containLabel": True},
        # Panel B — bottom
        {"left": 60, "right": 30, "top": 870, "height": 660, "containLabel": True},
    ],
    "legend": [
        # Panel A threshold legend (top-left of plot)
        {"data": ["Barotitis Θ=18.4", "Baromyringitis Θ=95.6", "Rupture Θ=150"],
         "left": 90, "top": 70,
         "orient": "vertical",
         "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": 9, "color": "#000"},
         "itemWidth": 22, "itemHeight": 2, "icon": "rect",
         "selectedMode": False,
         "padding": [4, 8, 4, 8],
         "backgroundColor": "rgba(255,255,255,0.85)",
         "borderColor": "#bbb", "borderWidth": 0.5},
        # Panel B outcome legend (top-right of plot)
        {"data": ["Barotitis", "Rupture"],
         "right": 50, "top": 880,
         "orient": "vertical",
         "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": 10, "color": "#000"},
         "itemWidth": 16, "itemHeight": 8,
         "padding": [4, 8, 4, 8],
         "backgroundColor": "rgba(255,255,255,0.85)",
         "borderColor": "#bbb", "borderWidth": 0.5},
    ],
    "xAxis": [
        # Panel A x — log scale
        {"type": "log", "min": 200, "max": 12000, "gridIndex": 0,
         "name": "Descent rate (ft/min)", "nameLocation": "middle", "nameGap": 30,
         "nameTextStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_TITLE, "color": "#000"},
         "axisLine": {"lineStyle": {"color": "#000", "width": 1}},
         "axisTick": {"lineStyle": {"color": "#000", "width": 1}, "length": 4},
         "axisLabel": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_LABEL, "color": "#000",
                       "formatter": "{value}"},
         "splitLine": {"lineStyle": {"color": "#E5E5E5", "width": 0.5, "type": "dashed"}}},
        # Panel B x — log scale
        {"type": "log", "min": 200, "max": 12000, "gridIndex": 1,
         "name": "Descent rate (ft/min)", "nameLocation": "middle", "nameGap": 30,
         "nameTextStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_TITLE, "color": "#000"},
         "axisLine": {"lineStyle": {"color": "#000", "width": 1}},
         "axisTick": {"lineStyle": {"color": "#000", "width": 1}, "length": 4},
         "axisLabel": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_LABEL, "color": "#000",
                       "formatter": "{value}"},
         "splitLine": {"lineStyle": {"color": "#E5E5E5", "width": 0.5, "type": "dashed"}}},
    ],
    "yAxis": [
        {"type": "value", "min": 0, "max": 450, "interval": 100, "gridIndex": 0,
         "name": "Peak |ΔP| (mmHg)", "nameLocation": "middle", "nameGap": 42, "nameRotate": 90,
         "nameTextStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_TITLE, "color": "#000"},
         "axisLine": {"show": True, "lineStyle": {"color": "#000", "width": 1}},
         "axisTick": {"show": True, "lineStyle": {"color": "#000", "width": 1}},
         "axisLabel": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_LABEL, "color": "#000"},
         "splitLine": {"lineStyle": {"color": "#E5E5E5", "width": 0.5, "type": "dashed"}}},
        {"type": "value", "min": 0, "max": 12, "interval": 2, "gridIndex": 1,
         "name": "Probability (%)", "nameLocation": "middle", "nameGap": 38, "nameRotate": 90,
         "nameTextStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_TITLE, "color": "#000"},
         "axisLine": {"show": True, "lineStyle": {"color": "#000", "width": 1}},
         "axisTick": {"show": True, "lineStyle": {"color": "#000", "width": 1}},
         "axisLabel": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_LABEL, "color": "#000",
                       "formatter": "{value}%"},
         "splitLine": {"lineStyle": {"color": "#E5E5E5", "width": 0.5, "type": "dashed"}}},
    ],
    "series": [
        # ---- Panel A: peak |dP| ----
        # Threshold reference lines (legend entries)
        {"name": "Barotitis Θ=18.4", "type": "line",
         "xAxisIndex": 0, "yAxisIndex": 0,
         "data": [[200, THR_BAROTITIS], [12000, THR_BAROTITIS]],
         "lineStyle": {"color": PALETTE["yellow"], "width": 1.4, "type": "dashed"},
         "symbol": "none", "z": 3, "silent": True},
        {"name": "Baromyringitis Θ=95.6", "type": "line",
         "xAxisIndex": 0, "yAxisIndex": 0,
         "data": [[200, THR_MYRINGITIS], [12000, THR_MYRINGITIS]],
         "lineStyle": {"color": PALETTE["orange"], "width": 1.4, "type": "dashed"},
         "symbol": "none", "z": 3, "silent": True},
        {"name": "Rupture Θ=150", "type": "line",
         "xAxisIndex": 0, "yAxisIndex": 0,
         "data": [[200, THR_RUPTURE], [12000, THR_RUPTURE]],
         "lineStyle": {"color": PALETTE["vermilion"], "width": 1.4, "type": "dashed"},
         "symbol": "none", "z": 3, "silent": True},
        # |dP| curve (with per-point label data)
        {"name": "Peak |ΔP|", "type": "line",
         "xAxisIndex": 0, "yAxisIndex": 0,
         "data": dp_label_data,
         "lineStyle": {"color": PALETTE["blue"], "width": 2.0},
         "symbol": "circle", "symbolSize": 10,
         "itemStyle": {"color": PALETTE["blue"], "borderColor": "#000", "borderWidth": 0.7},
         "z": 10},
        # ---- Panel B: probabilities ----
        {"name": "Barotitis", "type": "line",
         "xAxisIndex": 1, "yAxisIndex": 1,
         "data": baro_label_data,
         "lineStyle": {"color": PALETTE["vermilion"], "width": 2.0},
         "symbol": "circle", "symbolSize": 10,
         "itemStyle": {"color": PALETTE["vermilion"], "borderColor": "#000", "borderWidth": 0.7},
         "z": 10},
        {"name": "Rupture", "type": "line",
         "xAxisIndex": 1, "yAxisIndex": 1,
         "data": rupt_label_data,
         "lineStyle": {"color": PALETTE["orange"], "width": 1.6, "type": "dashed"},
         "symbol": "diamond", "symbolSize": 10,
         "itemStyle": {"color": PALETTE["orange"], "borderColor": "#000", "borderWidth": 0.7},
         "z": 9},
    ],
}

OUT_DIR = Path(__file__).resolve().parent
result = render(
    opt,
    out_dir=OUT_DIR,
    slug="fig_01_descent_rate_sensitivity",
    width_mm=120,
    height_mm=140,
    emit_tiff=True,
)
print("Rendered:", result["png"])
for r, dp, b, ru in DESCENT:
    print(f"  {r:>5} ft/min: dP={dp:>3} mmHg, p_baro={b:.2f}%, p_rupt={ru:.2f}%")
