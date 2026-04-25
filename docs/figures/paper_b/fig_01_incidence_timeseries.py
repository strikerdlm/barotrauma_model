"""
Paper B — Figure 1. FAC clinical ear-barotrauma incidence across 2010–2026.

Panel A (top):    per-year case counts of FAC-only clinical barotrauma (2010–2020 registry).
Panel B (bottom): per-quarter rate from 2025–2026 director log with Wilson 95% CIs against
                  the pooled 2010–2026 reference (2.38%, Wilson CI 2.06–2.75%).

Implementation: single ECharts canvas with two stacked grids, 89 mm × 130 mm at 600 dpi.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "figures" / "_shared"))

from amhp_theme import (
    PALETTE, FONT_FAMILY, FONT_SIZE_AXIS_LABEL, FONT_SIZE_AXIS_TITLE, FONT_SIZE_TITLE, wilson,
)
from render import render

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
ANALYSIS = ROOT / "Cohort FAC" / "analysis"
P1_TIDY = ANALYSIS / "phase1_2010_2020_tidy.csv"

year_counts = Counter()
with P1_TIDY.open() as f:
    reader = csv.DictReader(f)
    for row in reader:
        if (row.get("entity", "").upper() == "FAC"
                and row.get("lesion_category", "") == "barotrauma"):
            try:
                year_counts[int(row.get("flight_year", ""))] += 1
            except ValueError:
                continue

years = sorted(year_counts.keys())
counts = [year_counts[y] for y in years]
total_2010_2020 = sum(counts)

PHASE2_QUARTERS = [
    ("2025Q1", 0, 75),
    ("2025Q2", 2, 165),
    ("2025Q3", 1, 116),
    ("2025Q4", 6, 227),
    ("2026Q1", 3, 115),
]

q_keys, q_pct, q_lo, q_hi, q_label = [], [], [], [], []
for q, ev, exp in PHASE2_QUARTERS:
    p, lo, hi = wilson(ev, exp)
    q_keys.append(q)
    q_pct.append(round(100 * p, 2))
    q_lo.append(round(100 * lo, 2))
    q_hi.append(round(100 * hi, 2))
    q_label.append(f"{ev}/{exp}")

POOLED_PCT, POOLED_LO, POOLED_HI = 2.38, 2.06, 2.75

# ---------------------------------------------------------------------------
# Layout: 89 mm × 130 mm, two grids
#   Canvas height (logical px) = 130 × 300/25.4 = 1535
#   Grid A: top=44px, bottom=730px → height ≈ 760px
#   Grid B: top=830px, bottom=1490px → height ≈ 660px
# ---------------------------------------------------------------------------
def axis_x(name, data, grid_index):
    return {
        "type": "category", "data": data, "gridIndex": grid_index,
        "name": name, "nameLocation": "middle", "nameGap": 28,
        "nameTextStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_TITLE, "color": "#000"},
        "axisLine": {"lineStyle": {"color": "#000", "width": 1}},
        "axisTick": {"lineStyle": {"color": "#000", "width": 1}, "length": 4},
        "axisLabel": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_LABEL, "color": "#000"},
        "splitLine": {"show": False},
    }

def axis_y(name, grid_index, **kw):
    base = {
        "type": "value", "min": 0, "gridIndex": grid_index,
        "name": name, "nameLocation": "middle", "nameGap": 38, "nameRotate": 90,
        "nameTextStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_TITLE, "color": "#000"},
        "axisLine": {"show": True, "lineStyle": {"color": "#000", "width": 1}},
        "axisTick": {"show": True, "lineStyle": {"color": "#000", "width": 1}},
        "axisLabel": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_LABEL, "color": "#000"},
        "splitLine": {"lineStyle": {"color": "#E5E5E5", "width": 0.5, "type": "dashed"}},
    }
    base.update(kw)
    return base


opt = {
    "backgroundColor": "#ffffff",
    "textStyle": {"fontFamily": FONT_FAMILY, "color": "#000000"},
    "animation": False,
    "title": [
        # Panel A label + title
        {"text": "A", "left": 8, "top": 6,
         "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": 16, "fontWeight": "bold"}},
        {"text": f"FAC clinical barotrauma cases per year, 2010–2020 (total n = {total_2010_2020})",
         "left": "center", "top": 8,
         "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_TITLE, "fontWeight": "normal"}},
        # Panel B label + title
        {"text": "B", "left": 8, "top": 800,
         "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": 16, "fontWeight": "bold"}},
        {"text": "Per-quarter incidence 2025–2026 vs pooled 2010–2026 reference",
         "left": "center", "top": 802,
         "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_TITLE, "fontWeight": "normal"}},
    ],
    "grid": [
        # Panel A — top half
        {"left": 50, "right": 18, "top": 38, "height": 660, "containLabel": True},
        # Panel B — bottom half (leaves ~60px bottom for x-axis labels + title)
        {"left": 50, "right": 18, "top": 832, "height": 580, "containLabel": True},
    ],
    "xAxis": [
        axis_x("Year", [str(y) for y in years], 0),
        axis_x("Quarter", q_keys, 1),
    ],
    "yAxis": [
        axis_y("Cases (n)", 0),
        axis_y("Per-exposure incidence (%)", 1, max=9, interval=1.5,
               axisLabel={"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_LABEL, "color": "#000",
                          "formatter": "{value}%"}),
    ],
    "series": [
        # Panel A — yearly bars
        {"name": "Cases", "type": "bar",
         "xAxisIndex": 0, "yAxisIndex": 0,
         "data": counts,
         "itemStyle": {"color": PALETTE["blue"], "borderColor": "#000", "borderWidth": 0.5},
         "barWidth": "70%",
         "label": {"show": True, "position": "top",
                   "fontFamily": FONT_FAMILY, "fontSize": 10, "color": "#000"}},
        # Panel B — pooled CI band (stacked area trick)
        {"name": "lo", "type": "line",
         "xAxisIndex": 1, "yAxisIndex": 1,
         "data": [POOLED_LO] * len(q_keys),
         "lineStyle": {"opacity": 0}, "stack": "ci", "symbol": "none", "silent": True},
        {"name": "band", "type": "line",
         "xAxisIndex": 1, "yAxisIndex": 1,
         "data": [round(POOLED_HI - POOLED_LO, 3)] * len(q_keys),
         "lineStyle": {"opacity": 0},
         "areaStyle": {"color": PALETTE["lightgrey"], "opacity": 0.7},
         "stack": "ci", "symbol": "none", "silent": True},
        # Panel B — pooled mean reference (dashed)
        {"name": "Pooled mean (2.38%)", "type": "line",
         "xAxisIndex": 1, "yAxisIndex": 1,
         "data": [POOLED_PCT] * len(q_keys),
         "lineStyle": {"color": "#000", "width": 1.4, "type": "dashed"},
         "symbol": "none", "z": 5},
        # Panel B — per-quarter scatter
        {"name": "Quarterly rate", "type": "scatter",
         "xAxisIndex": 1, "yAxisIndex": 1,
         "data": q_pct,
         "symbolSize": 11,
         "itemStyle": {"color": PALETTE["vermilion"], "borderColor": "#000", "borderWidth": 0.6},
         "z": 10,
         "label": {"show": True, "position": "top",
                   "fontFamily": FONT_FAMILY, "fontSize": 9, "color": "#000",
                   "formatter": "RENDERLABELS",
                   "distance": 7}},
        # Panel B — Wilson whiskers
        {"name": "CI", "type": "custom",
         "xAxisIndex": 1, "yAxisIndex": 1,
         "renderItem": "RENDERWHISKER",
         "data": [[i, q_lo[i], q_hi[i]] for i in range(len(q_keys))],
         "z": 8},
    ],
}

WHISKER_JS = """function(params, api){
  var x = api.coord([api.value(0), 0])[0];
  var yLo = api.coord([api.value(0), api.value(1)])[1];
  var yHi = api.coord([api.value(0), api.value(2)])[1];
  var capW = 7;
  return { type: 'group', children: [
    { type: 'line', shape: { x1: x, y1: yLo, x2: x, y2: yHi },
      style: { stroke: '#000', lineWidth: 1.0 } },
    { type: 'line', shape: { x1: x - capW, y1: yLo, x2: x + capW, y2: yLo },
      style: { stroke: '#000', lineWidth: 1.0 } },
    { type: 'line', shape: { x1: x - capW, y1: yHi, x2: x + capW, y2: yHi },
      style: { stroke: '#000', lineWidth: 1.0 } }
  ] };
}"""

LABELS_JS = (
    "function(params){ var labels = "
    + repr(q_label).replace("'", '"')
    + "; return labels[params.dataIndex]; }"
)

OUT_DIR = Path(__file__).resolve().parent
result = render(
    opt,
    out_dir=OUT_DIR,
    slug="fig_01_incidence_timeseries",
    width_mm=89,
    height_mm=130,
    render_item_replacements={"RENDERWHISKER": WHISKER_JS, "RENDERLABELS": LABELS_JS},
)
print("Rendered:", result["png"])
print(f"Total cases 2010-2020: {total_2010_2020}; Per-year: {dict(zip(years, counts))}")
print(f"Quarters: {list(zip(q_keys, q_pct, q_label))}")
