"""
Paper B — Figure 4. Vital signs at 2,640 m baseline (Bogotá preflight cohort).

Two panels:
  A — Blood-pressure category distribution (ACC/AHA 2017): horizontal stacked
      bar showing 56% of preflight readings ≥130/80
  B — SpO₂ distribution histogram with Bogotá-specific reference bands
      (93–96% expected, ≥97% high-normal, 90–92% borderline, <90% hypoxic)

Visualizes the unique high-altitude reference distribution that no other
published chamber-cohort paper reports.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "figures" / "_shared"))

from amhp_theme import (
    PALETTE, FONT_FAMILY, FONT_SIZE_AXIS_LABEL, FONT_SIZE_AXIS_TITLE, FONT_SIZE_TITLE,
)
from render import render

ANALYSIS = ROOT / "Cohort FAC" / "analysis"
PRE = ANALYSIS / "phase2_preflight_tidy.csv"

# ---------------------------------------------------------------------------
# Load BP and SpO2
# ---------------------------------------------------------------------------
pas_vals, pad_vals, spo2_vals = [], [], []
with PRE.open() as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            pas = float(row["PAS_mmHg"])
            pad = float(row["PAD_mmHg"])
            if 70 <= pas <= 220 and 40 <= pad <= 140:
                pas_vals.append(pas)
                pad_vals.append(pad)
        except (ValueError, KeyError):
            pass
        try:
            spo2 = float(row["SpO2_pct"])
            if 70 <= spo2 <= 100:
                spo2_vals.append(spo2)
        except (ValueError, KeyError):
            pass

# ACC/AHA 2017 categorisation
def bp_category(pas: float, pad: float) -> str:
    if pas < 90 or pad < 60:
        return "Hypotension (<90/60)"
    if pas >= 180 or pad >= 120:
        return "Hypertensive crisis (≥180/120)"
    if pas >= 140 or pad >= 90:
        return "Stage-2 HTN (≥140/90)"
    if pas >= 130 or pad >= 80:
        return "Stage-1 HTN (130–139/80–89)"
    if pas >= 120 and pad < 80:
        return "Elevated (120–129/<80)"
    return "Normal (<120/<80)"

bp_counts = Counter(bp_category(p, d) for p, d in zip(pas_vals, pad_vals))
total_bp = sum(bp_counts.values())

bp_order = [
    "Normal (<120/<80)",
    "Elevated (120–129/<80)",
    "Stage-1 HTN (130–139/80–89)",
    "Stage-2 HTN (≥140/90)",
    "Hypertensive crisis (≥180/120)",
    "Hypotension (<90/60)",
]
bp_colors = [
    PALETTE["green"],         # normal
    PALETTE["yellow"],        # elevated
    PALETTE["orange"],        # stage-1
    PALETTE["vermilion"],     # stage-2
    "#7f1d1d",                # crisis (deep red)
    PALETTE["skyblue"],       # hypotension
]
bp_pct = [round(100 * bp_counts.get(c, 0) / total_bp, 1) for c in bp_order]
bp_n = [bp_counts.get(c, 0) for c in bp_order]

# ---------------------------------------------------------------------------
# SpO2 histogram bins
# ---------------------------------------------------------------------------
spo2_bins_edges = list(range(85, 102))  # 85, 86, ..., 101 → 16 bins
spo2_hist = Counter()
for v in spo2_vals:
    b = int(v) if v < 101 else 100
    if b >= 85:
        spo2_hist[b] += 1
spo2_hist_data = [spo2_hist.get(b, 0) for b in range(85, 101)]
spo2_x_labels = [str(b) for b in range(85, 101)]

# ---------------------------------------------------------------------------
# Build option — two stacked panels
# ---------------------------------------------------------------------------
opt = {
    "backgroundColor": "#ffffff",
    "textStyle": {"fontFamily": FONT_FAMILY, "color": "#000000"},
    "animation": False,
    "title": [
        {"text": "A", "left": 8, "top": 6,
         "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": 16, "fontWeight": "bold"}},
        {"text": "Blood-pressure category distribution at 2,640 m preflight (ACC/AHA 2017)",
         "left": "center", "top": 8,
         "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_TITLE, "fontWeight": "normal"}},
        {"text": "B", "left": 8, "top": 350,
         "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": 16, "fontWeight": "bold"}},
        {"text": "SpO₂ distribution at 2,640 m preflight (n = " + f"{len(spo2_vals):,})",
         "left": "center", "top": 352,
         "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_TITLE, "fontWeight": "normal"}},
    ],
    "grid": [
        # Panel A — top: stacked BP bar
        {"left": 60, "right": 30, "top": 40, "height": 200, "containLabel": True},
        # Panel B — bottom: SpO2 histogram
        {"left": 60, "right": 30, "top": 390, "height": 380, "containLabel": True},
    ],
    "xAxis": [
        {"type": "value", "min": 0, "max": 100, "gridIndex": 0,
         "name": "Percent of cohort (%)", "nameLocation": "middle", "nameGap": 28,
         "nameTextStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_TITLE, "color": "#000"},
         "axisLine": {"lineStyle": {"color": "#000", "width": 1}},
         "axisTick": {"lineStyle": {"color": "#000", "width": 1}},
         "axisLabel": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_LABEL, "color": "#000",
                       "formatter": "{value}%"},
         "splitLine": {"lineStyle": {"color": "#E5E5E5", "width": 0.5, "type": "dashed"}}},
        {"type": "category", "data": spo2_x_labels, "gridIndex": 1,
         "name": "SpO₂ (%)", "nameLocation": "middle", "nameGap": 28,
         "nameTextStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_TITLE, "color": "#000"},
         "axisLine": {"lineStyle": {"color": "#000", "width": 1}},
         "axisTick": {"lineStyle": {"color": "#000", "width": 1}},
         "axisLabel": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_LABEL, "color": "#000"}},
    ],
    "yAxis": [
        {"type": "category", "data": ["BP categories"], "gridIndex": 0,
         "axisLine": {"show": False}, "axisTick": {"show": False},
         "axisLabel": {"show": False}},
        {"type": "value", "min": 0, "gridIndex": 1,
         "name": "Number of subjects", "nameLocation": "middle", "nameGap": 38, "nameRotate": 90,
         "nameTextStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_TITLE, "color": "#000"},
         "axisLine": {"show": True, "lineStyle": {"color": "#000", "width": 1}},
         "axisTick": {"show": True, "lineStyle": {"color": "#000", "width": 1}},
         "axisLabel": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_LABEL, "color": "#000"},
         "splitLine": {"lineStyle": {"color": "#E5E5E5", "width": 0.5, "type": "dashed"}}},
    ],
    "series": [
        # Panel A — stacked horizontal bar (one segment per BP category)
        *[
            {"name": cat, "type": "bar", "stack": "bp", "xAxisIndex": 0, "yAxisIndex": 0,
             "data": [bp_pct[i]],
             "itemStyle": {"color": bp_colors[i], "borderColor": "#fff", "borderWidth": 1.5},
             "barWidth": 80,
             "label": {
                 "show": bp_pct[i] >= 4,
                 "position": "inside",
                 "fontFamily": FONT_FAMILY, "fontSize": 11, "color": "#000",
                 "fontWeight": "bold",
                 "formatter": f"{bp_pct[i]}%",
             }}
            for i, cat in enumerate(bp_order)
        ],
        # Panel B — SpO2 histogram bars
        {"name": "SpO₂ count", "type": "bar",
         "xAxisIndex": 1, "yAxisIndex": 1,
         "data": spo2_hist_data,
         "itemStyle": {"color": PALETTE["blue"], "borderColor": "#000", "borderWidth": 0.4},
         "barWidth": "85%",
         "markArea": {
             "silent": True,
             "data": [
                 # < 90 hypoxic: red
                 [{"xAxis": "85", "itemStyle": {"color": PALETTE["vermilion"], "opacity": 0.10}},
                  {"xAxis": "89"}],
                 # 90-92 borderline: yellow
                 [{"xAxis": "90", "itemStyle": {"color": PALETTE["yellow"], "opacity": 0.20}},
                  {"xAxis": "92"}],
                 # 93-96 expected for Bogotá: green
                 [{"xAxis": "93", "itemStyle": {"color": PALETTE["green"], "opacity": 0.10}},
                  {"xAxis": "96"}],
                 # ≥97 high-normal: blue tint
                 [{"xAxis": "97", "itemStyle": {"color": PALETTE["skyblue"], "opacity": 0.15}},
                  {"xAxis": "100"}],
             ],
         }},
    ],
    "legend": {
        "show": True,
        "data": bp_order,
        "left": "center", "top": 280,
        "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": 10, "color": "#000"},
        "itemWidth": 14, "itemHeight": 10,
        "icon": "rect",
        "orient": "horizontal",
    },
}

OUT_DIR = Path(__file__).resolve().parent
result = render(
    opt,
    out_dir=OUT_DIR,
    slug="fig_04_vitals_distribution",
    width_mm=160,
    height_mm=70,
)
print("Rendered:", result["png"])
print(f"BP n: {total_bp}; SpO2 n: {len(spo2_vals)}")
for c, n, p in zip(bp_order, bp_n, bp_pct):
    print(f"  {c}: {n} ({p}%)")
