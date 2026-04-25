"""
Paper B — Figure 2. Preflight denial-rate forest plot, ranked by discrimination.

Per-flag denial rate `denied / flag+ evaluated` with Wilson 95% CIs, ordered
descending by point estimate so the highest-discrimination flags are at the
top. Color-coded discrimination tiers; n_denied/n_flag+ annotations on the
right margin. Vertical dashed line marks overall denial rate (2.29%, Wilson
CI 1.53–3.41%).
"""
from __future__ import annotations

import csv
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
DENIAL_CSV = ANALYSIS / "phase2_denial_by_flag.csv"

flags = []
with DENIAL_CSV.open() as f:
    reader = csv.DictReader(f)
    for row in reader:
        n_pos = int(row["n_flag_positive_evaluated"])
        n_den = int(row["n_denied"])
        if n_pos == 0:
            continue
        flag_name = row["flag"].replace("_", " ")
        flags.append({
            "name": flag_name,
            "n_pos": n_pos,
            "n_den": n_den,
            "rate": float(row["denial_pct"]),
            "lo": float(row["wilson_lo_pct"]),
            "hi": float(row["wilson_hi_pct"]),
        })

# Sort descending by rate (highest discrimination at top)
flags.sort(key=lambda r: r["rate"], reverse=True)

# Overall denial rate from manuscript: 23/1004
OVERALL_PCT = 2.29
OVERALL_LO = 1.53
OVERALL_HI = 3.41

# ---------------------------------------------------------------------------
# Color tiers (greyscale-friendly through luminance and shape)
# ---------------------------------------------------------------------------
def tier_color(rate: float) -> str:
    if rate >= 25:
        return PALETTE["vermilion"]   # high discrimination
    if rate >= 10:
        return PALETTE["orange"]       # moderate
    if rate > 0:
        return PALETTE["green"]        # low
    return PALETTE["grey"]             # null (0 denials)


# ---------------------------------------------------------------------------
# Build option — horizontal bar/scatter with custom whiskers (yAxis = flags)
# ---------------------------------------------------------------------------
flag_labels = [f["name"] for f in flags]
points = [f["rate"] for f in flags]
los = [f["lo"] for f in flags]
his = [f["hi"] for f in flags]
colors = [tier_color(f["rate"]) for f in flags]
annot_labels = [f"{f['n_den']}/{f['n_pos']}" for f in flags]

# yAxis must be reversed (top = first item)
y_categories = list(reversed(flag_labels))
points_rev = list(reversed(points))
los_rev = list(reversed(los))
his_rev = list(reversed(his))
colors_rev = list(reversed(colors))
annots_rev = list(reversed(annot_labels))

# X-axis max — cap at 100% for readability
X_MAX = 105

# Build colored scatter data with per-point itemStyle
scatter_data = []
for i, (rate, color) in enumerate(zip(points_rev, colors_rev)):
    scatter_data.append({"value": [rate, i], "itemStyle": {"color": color, "borderColor": "#000", "borderWidth": 0.6}})

opt = {
    "backgroundColor": "#ffffff",
    "textStyle": {"fontFamily": FONT_FAMILY, "color": "#000000"},
    "animation": False,
    "title": {
        "text": "Preflight denial rate by screening flag (n = 1,004 evaluated)",
        "left": "center", "top": 8,
        "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_TITLE, "fontWeight": "normal"},
    },
    "graphic": [{
        "type": "text",
        "left": "center", "bottom": 12,
        "z": 100,
        "style": {
            "text": "Denial rate (%) with Wilson 95% CI",
            "font": f"{FONT_SIZE_AXIS_TITLE}px Arial,sans-serif",
            "fill": "#000",
            "textAlign": "center", "textVerticalAlign": "bottom",
        },
    }],
    "grid": {"left": 110, "right": 80, "top": 40, "bottom": 70, "containLabel": True},
    "xAxis": {
        "type": "value",
        "min": 0, "max": X_MAX,
        "name": "",
        "nameLocation": "middle", "nameGap": 30,
        "nameTextStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_TITLE, "color": "#000"},
        "axisLine": {"lineStyle": {"color": "#000", "width": 1}},
        "axisTick": {"lineStyle": {"color": "#000", "width": 1}, "length": 4},
        "axisLabel": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_LABEL, "color": "#000",
                      "formatter": "{value}%"},
        "splitLine": {"lineStyle": {"color": "#E5E5E5", "width": 0.5, "type": "dashed"}},
    },
    "yAxis": {
        "type": "category", "data": y_categories,
        "axisLine": {"lineStyle": {"color": "#000", "width": 1}},
        "axisTick": {"show": False},
        "axisLabel": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_LABEL, "color": "#000",
                      "interval": 0},
        "splitLine": {"show": False},
    },
    "series": [
        # Reference line at overall denial rate
        {"name": "Overall (2.29%)", "type": "line",
         "data": [[OVERALL_PCT, i] for i in range(len(y_categories))],
         "lineStyle": {"color": "#000", "width": 1.2, "type": "dashed"},
         "symbol": "none", "z": 5,
         "markArea": {
             "silent": True,
             "itemStyle": {"color": PALETTE["lightgrey"], "opacity": 0.5},
             "data": [[{"xAxis": OVERALL_LO}, {"xAxis": OVERALL_HI}]]
         }},
        # Wilson whiskers (custom)
        {"name": "CI", "type": "custom",
         "renderItem": "RENDERWHISKER",
         "data": [[i, los_rev[i], his_rev[i]] for i in range(len(y_categories))],
         "z": 8},
        # Per-flag scatter points
        {"name": "Denial rate", "type": "scatter",
         "data": scatter_data,
         "symbolSize": 11,
         "z": 10,
         "encode": {"x": 0, "y": 1}},
        # Right-margin n_denied/n_flag+ annotation (custom labels)
        {"name": "annot", "type": "custom",
         "renderItem": "RENDERANNOT",
         "data": [[X_MAX, i, annots_rev[i]] for i in range(len(y_categories))],
         "z": 12,
         "silent": True},
    ],
}

WHISKER_JS = """function(params, api){
  var y = api.coord([0, api.value(0)])[1];
  var xLo = api.coord([api.value(1), api.value(0)])[0];
  var xHi = api.coord([api.value(2), api.value(0)])[0];
  var capH = 5;
  return { type: 'group', children: [
    { type: 'line', shape: { x1: xLo, y1: y, x2: xHi, y2: y },
      style: { stroke: '#000', lineWidth: 1.0 } },
    { type: 'line', shape: { x1: xLo, y1: y - capH, x2: xLo, y2: y + capH },
      style: { stroke: '#000', lineWidth: 1.0 } },
    { type: 'line', shape: { x1: xHi, y1: y - capH, x2: xHi, y2: y + capH },
      style: { stroke: '#000', lineWidth: 1.0 } }
  ] };
}"""

ANNOT_JS = """function(params, api){
  var x = api.coord([api.value(0), api.value(1)])[0];
  var y = api.coord([api.value(0), api.value(1)])[1];
  return { type: 'text', style: {
    text: api.value(2),
    x: x + 8, y: y,
    fontSize: 10, fontFamily: 'Arial,sans-serif',
    fill: '#000', textAlign: 'left', textVerticalAlign: 'middle'
  }};
}"""

OUT_DIR = Path(__file__).resolve().parent
result = render(
    opt,
    out_dir=OUT_DIR,
    slug="fig_02_denial_forest",
    width_mm=120,
    height_mm=120,
    render_item_replacements={"RENDERWHISKER": WHISKER_JS, "RENDERANNOT": ANNOT_JS},
    emit_tiff=True,
)
print("Rendered:", result["png"])
for f in flags:
    print(f"  {f['name']}: {f['rate']}% [{f['lo']}-{f['hi']}] ({f['n_den']}/{f['n_pos']})")
