"""
Paper C — Figure 3. External validation forest plot (TRIPOD requirement).

Visualizes observed vs simulated per-exposure barotitis incidence across the
calibration cohort (Colombian Aerospace Force, FAC) and three independent
external validation cohorts (Italian Air Force).

Each row shows:
- Observed proportion with Wilson 95% CI (point + whiskers)
- Simulated point estimate (diamond marker)
- Color encodes whether the simulated point falls inside the observed CI

Source: manuscript.md L21 (FAC anchor) + Table III (L281-L287).
- FAC pooled 2010-2026:    173/7,271, observed 2.38% [2.06%, 2.75%]; simulated 2.47%  (anchor)
- Morgagni 2010:           19/1,254, observed 1.5%  [0.96%, 2.34%]; simulated 3.27%  (+1.77 pp outside CI)
- Morgagni 2012 25,000 ft: 7/314,    observed 2.3%  [1.13%, 4.62%]; simulated 3.31%  (within CI)
- Landolfi 2009 TEED:      8/335,    observed 2.4%  [1.22%, 4.66%]; simulated 3.37%  (within CI)
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
# Data — manuscript.md L21 + Table III
# ---------------------------------------------------------------------------
COHORTS = [
    # label, n, events, obs_pct, lo, hi, sim_pct, role
    ("FAC pooled 2010–2026  (anchor)",
     7271, 173, 2.38, 2.06, 2.75, 2.47, "anchor"),
    ("Morgagni 2010  (Italian AF)",
     1254, 19, 1.51, 0.97, 2.36, 3.27, "external"),
    ("Morgagni 2012, 25,000 ft  (Italian AF)",
     314, 7, 2.23, 1.09, 4.51, 3.31, "external"),
    ("Landolfi 2009, TEED-graded  (Italian AF)",
     335, 8, 2.39, 1.22, 4.62, 3.37, "external"),
]

def within(lo, hi, sim):
    return lo <= sim <= hi

# Reverse for ECharts (top = first row)
ROWS = []
for label, n, ev, obs, lo, hi, sim, role in COHORTS:
    inside = within(lo, hi, sim)
    status = "within CI" if inside else f"+{sim-hi:.2f} pp outside"
    ROWS.append({
        "label": label,
        "n": n, "ev": ev,
        "obs": obs, "lo": lo, "hi": hi,
        "sim": sim,
        "role": role,
        "inside": inside,
        "annot_right": f"k={ev}/{n:,}  ·  sim {sim:.2f}%  ({status})",
    })

ROWS_REV = list(reversed(ROWS))
y_categories = [r["label"] for r in ROWS_REV]

# Observed scatter (color encodes anchor vs external)
obs_scatter = []
for i, r in enumerate(ROWS_REV):
    color = PALETTE["vermilion"] if r["role"] == "anchor" else PALETTE["blue"]
    obs_scatter.append({
        "value": [r["obs"], i],
        "itemStyle": {"color": color, "borderColor": "#000", "borderWidth": 0.7},
        "symbolSize": 14 if r["role"] == "anchor" else 12,
    })

# Simulated scatter (diamond, color encodes within-CI status)
sim_scatter = []
for i, r in enumerate(ROWS_REV):
    color = PALETTE["green"] if r["inside"] else PALETTE["orange"]
    sim_scatter.append({
        "value": [r["sim"], i],
        "itemStyle": {"color": color, "borderColor": "#000", "borderWidth": 0.7},
        "symbolSize": 13,
    })

X_MAX = 6.0

opt = {
    "backgroundColor": "#ffffff",
    "textStyle": {"fontFamily": FONT_FAMILY, "color": "#000000"},
    "animation": False,
    "title": {
        "text": "External validation: observed vs simulated per-exposure barotitis (%)",
        "left": "center", "top": 8,
        "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_TITLE, "fontWeight": "normal"},
    },
    "graphic": [{
        "type": "text", "left": "center", "bottom": 14, "z": 100,
        "style": {
            "text": "Observed (filled circles) with Wilson 95% CI · simulated point (diamonds: green = within CI, orange = outside)",
            "font": f"9px Arial,sans-serif",
            "fill": "#000",
            "textAlign": "center",
        },
    }],
    "legend": {
        "data": ["Observed (anchor)", "Observed (external)", "Simulated (within CI)", "Simulated (outside CI)"],
        "left": "center", "top": 32,
        "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": 10, "color": "#000"},
        "itemWidth": 14, "itemHeight": 10,
        "selectedMode": False,
    },
    "grid": {"left": 200, "right": 280, "top": 70, "bottom": 60, "containLabel": True},
    "xAxis": {
        "type": "value", "min": 0, "max": X_MAX,
        "name": "",
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
        # Wilson CI whiskers
        {"name": "CI", "type": "custom",
         "renderItem": "RENDERWHISKER",
         "data": [[i, ROWS_REV[i]["lo"], ROWS_REV[i]["hi"]] for i in range(len(ROWS_REV))],
         "z": 6, "silent": True},
        # Observed scatter — anchor (red) and external (blue)
        {"name": "Observed (anchor)", "type": "scatter",
         "data": [s if ROWS_REV[i]["role"] == "anchor" else None for i, s in enumerate(obs_scatter)],
         "symbol": "circle", "z": 10, "encode": {"x": 0, "y": 1},
         "itemStyle": {"color": PALETTE["vermilion"], "borderColor": "#000", "borderWidth": 0.7}},
        {"name": "Observed (external)", "type": "scatter",
         "data": [s if ROWS_REV[i]["role"] != "anchor" else None for i, s in enumerate(obs_scatter)],
         "symbol": "circle", "z": 10, "encode": {"x": 0, "y": 1},
         "itemStyle": {"color": PALETTE["blue"], "borderColor": "#000", "borderWidth": 0.7}},
        # Simulated scatter — within CI (green) vs outside (orange)
        {"name": "Simulated (within CI)", "type": "scatter",
         "data": [s if ROWS_REV[i]["inside"] else None for i, s in enumerate(sim_scatter)],
         "symbol": "diamond", "z": 11, "encode": {"x": 0, "y": 1},
         "itemStyle": {"color": PALETTE["green"], "borderColor": "#000", "borderWidth": 0.7}},
        {"name": "Simulated (outside CI)", "type": "scatter",
         "data": [s if not ROWS_REV[i]["inside"] else None for i, s in enumerate(sim_scatter)],
         "symbol": "diamond", "z": 11, "encode": {"x": 0, "y": 1},
         "itemStyle": {"color": PALETTE["orange"], "borderColor": "#000", "borderWidth": 0.7}},
        # Right-margin annotation: k/n and sim status
        {"name": "annot_right", "type": "custom",
         "renderItem": "RENDERANNOT",
         "data": [[X_MAX, i, ROWS_REV[i]["annot_right"]] for i in range(len(ROWS_REV))],
         "z": 12, "silent": True},
    ],
}

WHISKER_JS = """function(params, api){
  var y = api.coord([0, api.value(0)])[1];
  var xLo = api.coord([api.value(1), api.value(0)])[0];
  var xHi = api.coord([api.value(2), api.value(0)])[0];
  var capH = 6;
  return { type: 'group', children: [
    { type: 'line', shape: { x1: xLo, y1: y, x2: xHi, y2: y },
      style: { stroke: '#000', lineWidth: 1.0 } },
    { type: 'line', shape: { x1: xLo, y1: y - capH, x2: xLo, y2: y + capH },
      style: { stroke: '#000', lineWidth: 1.0 } },
    { type: 'line', shape: { x1: xHi, y1: y - capH, x2: xHi, y2: y + capH },
      style: { stroke: '#000', lineWidth: 1.0 } }
  ] };
}"""

ANNOT_RIGHT_JS = """function(params, api){
  var x = api.coord([api.value(0), api.value(1)])[0];
  var y = api.coord([api.value(0), api.value(1)])[1];
  return { type: 'text', style: {
    text: api.value(2),
    x: x + 10, y: y,
    fontSize: 10, fontFamily: 'Arial,sans-serif',
    fill: '#000', textAlign: 'left', textVerticalAlign: 'middle'
  }};
}"""

OUT_DIR = Path(__file__).resolve().parent
result = render(
    opt,
    out_dir=OUT_DIR,
    slug="fig_03_external_validation",
    width_mm=170,
    height_mm=75,
    render_item_replacements={
        "RENDERWHISKER": WHISKER_JS,
        "RENDERANNOT": ANNOT_RIGHT_JS,
    },
)
print("Rendered:", result["png"])
for r in ROWS:
    print(f"  {r['label']}: obs={r['obs']:.2f}% [{r['lo']:.2f}-{r['hi']:.2f}], "
          f"sim={r['sim']:.2f}%, inside={r['inside']}")
