"""
Paper B — Figure 3. International cohort comparison.

Forest plot of per-exposure clinical barotrauma incidence across published
hypobaric-chamber cohorts:
- FAC pooled 2010–2026 (this study) — highlighted reference
- Morgagni 2010 — overall + pre-screened + unscreened subset
- Morgagni 2012 — n = 314, 25,000 ft
- Landolfi 2009 — n = 335
- Nakdimon 2022 (Israeli AF) — implied barotrauma rate
- Lindfors 2021 (Finnish commercial aircrew) — career prevalence
  (shown for context with a separate axis label, since it's a different metric)

Visualizes the paper's headline claim: high-altitude-baseline FAC sits within
the sea-level Italian Air Force envelope.
"""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "figures" / "_shared"))

from amhp_theme import (
    PALETTE, FONT_FAMILY, FONT_SIZE_AXIS_LABEL, FONT_SIZE_AXIS_TITLE, FONT_SIZE_TITLE, wilson,
)
from render import render

# ---------------------------------------------------------------------------
# Cohort data (per-exposure barotrauma, except Lindfors)
# ---------------------------------------------------------------------------
cohorts = [
    # label, events, n, color, is_reference
    ("FAC 2010–2026 pooled (this study)", 173, 7271, PALETTE["vermilion"], True),
    ("Morgagni 2010 — overall (Italian AF)", 19, 1254, PALETTE["blue"], False),
    ("Morgagni 2010 — pre-screened subset",  10, 927,  PALETTE["skyblue"], False),
    ("Morgagni 2010 — unscreened controls",   9, 327,  PALETTE["skyblue"], False),
    ("Morgagni 2012 — 25,000 ft (Italian AF)", 7,  314, PALETTE["blue"], False),
    ("Landolfi 2009 (Italian AF, TEED-graded)", 8,  335, PALETTE["blue"], False),
    ("Nakdimon 2022 (Israeli AF, MEB+sinus)", 63, 1627, PALETTE["green"], False),
]
# (Nakdimon 2022 reports 5.59% overall adverse-event rate, of which 69% were
#  middle-ear or sinus barotrauma → implied barotrauma cases ≈ 91 × 0.69 ≈ 63.)

rows = []
for label, ev, n, color, is_ref in cohorts:
    p, lo, hi = wilson(ev, n)
    rows.append({
        "label": label,
        "n": n, "ev": ev,
        "pct": round(100 * p, 2),
        "lo": round(100 * lo, 2),
        "hi": round(100 * hi, 2),
        "color": color,
        "is_ref": is_ref,
        "annot": f"{ev}/{n:,}",
    })

# Reverse for ECharts (top of plot = first cohort)
rows_rev = list(reversed(rows))
y_categories = [r["label"] for r in rows_rev]
points = [r["pct"] for r in rows_rev]
los = [r["lo"] for r in rows_rev]
his = [r["hi"] for r in rows_rev]
annots = [r["annot"] for r in rows_rev]

# Per-cohort point styles
scatter_data = []
for i, r in enumerate(rows_rev):
    style = {"color": r["color"], "borderColor": "#000", "borderWidth": 0.7}
    sym_size = 14 if r["is_ref"] else 11
    scatter_data.append({
        "value": [r["pct"], i],
        "itemStyle": style,
        "symbolSize": sym_size,
    })

# FAC reference (the headline finding)
FAC_PCT, FAC_LO, FAC_HI = 2.38, 2.06, 2.75

X_MAX = 8

opt = {
    "backgroundColor": "#ffffff",
    "textStyle": {"fontFamily": FONT_FAMILY, "color": "#000000"},
    "animation": False,
    "title": {
        "text": "Per-exposure clinical barotrauma incidence — international cohort comparison",
        "left": "center", "top": 8,
        "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_TITLE, "fontWeight": "normal"},
    },
    "graphic": [{
        "type": "text",
        "left": "center", "bottom": 16,
        "z": 100,
        "style": {
            "text": "Per-exposure incidence (%) with Wilson 95% CI · n_events / N_exposures shown right",
            "font": f"{FONT_SIZE_AXIS_TITLE}px Arial,sans-serif",
            "fill": "#000",
            "textAlign": "center",
        },
    }],
    "grid": {"left": 200, "right": 95, "top": 36, "bottom": 70, "containLabel": True},
    "xAxis": {
        "type": "value",
        "min": 0, "max": X_MAX,
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
        # FAC reference band (highlight)
        {"name": "FAC reference", "type": "line",
         "data": [[FAC_PCT, i] for i in range(len(y_categories))],
         "lineStyle": {"color": PALETTE["vermilion"], "width": 1.4, "type": "dashed"},
         "symbol": "none", "z": 5,
         "markArea": {
             "silent": True,
             "itemStyle": {"color": PALETTE["vermilion"], "opacity": 0.10},
             "data": [[{"xAxis": FAC_LO}, {"xAxis": FAC_HI}]]
         }},
        # Wilson whiskers
        {"name": "CI", "type": "custom",
         "renderItem": "RENDERWHISKER",
         "data": [[i, los[i], his[i]] for i in range(len(y_categories))],
         "z": 8},
        # Cohort scatter points
        {"name": "Per-exposure rate", "type": "scatter",
         "data": scatter_data,
         "z": 10,
         "encode": {"x": 0, "y": 1}},
        # Right-margin n/N annotations
        {"name": "annot", "type": "custom",
         "renderItem": "RENDERANNOT",
         "data": [[X_MAX, i, annots[i]] for i in range(len(y_categories))],
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

ANNOT_JS = """function(params, api){
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
    slug="fig_03_international_comparison",
    width_mm=160,
    height_mm=95,
    render_item_replacements={"RENDERWHISKER": WHISKER_JS, "RENDERANNOT": ANNOT_JS},
)
print("Rendered:", result["png"])
for r in rows:
    print(f"  {r['label']}: {r['pct']}% [{r['lo']}-{r['hi']}] ({r['annot']})")
