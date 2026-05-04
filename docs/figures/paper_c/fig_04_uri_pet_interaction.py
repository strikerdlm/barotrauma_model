"""
Paper C — Figure 4. URI × PET interaction heatmap on the FAC chamber profile.

Visualizes the pathophysiology innovation that distinguishes this simulator
from Kanick-Doyle 2005: the joint dependence of per-exposure barotitis
probability on (i) URI temporal state (6 levels, none → day_22_28) and
(ii) Patulous Eustachian tube state (5 levels, normal/no-PET → S4
post-Kobayashi plug).

Each cell shows the simulator output for a default healthy baseline patient
on the FAC Bogotá default profile (8,530 ft start, 25,000 ft hold, 2,470
ft·min⁻¹ descent), varying only the URI and PET states. Cell value is
p_barotitis (%).

Source data: docs/figures/paper_c/data/uri_pet_grid.json — produced by
running barotrauma.v2.simulate over the 5×6 grid against FAC_BOGOTA_DEFAULT.

Headline pattern:
- URI day 4–7 dominates each PET row (peak inflammation window)
- PET-S1 (patent + dry) is rupture-protective at URI=none (0%) but URI
  *converts* it to paradoxically closed → matches PET-S2 risk under URI
- PET-S4 (stenotic-equivalent post-plug) saturates at high probability
  across all URI states
- PET-S3 (habitual sniffer) is anomalously low here because the negative
  resting-pressure bias offsets the descent-side ΔP integral on this
  profile (a model-output observation worth a footnote)
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
# Load grid (computed by barotrauma.v2.simulate, see commit message)
# ---------------------------------------------------------------------------
DATA = json.loads((Path(__file__).parent / "data" / "uri_pet_grid.json").read_text())
URI_STATES = DATA["uri_states"]
PET_STATES = DATA["pet_states"]
GRID = DATA["grid_pct"]

# Display labels
URI_LABELS = {
    "none":      "None",
    "day_1_3":   "Days 1–3",
    "day_4_7":   "Days 4–7\n(peak)",
    "day_8_14":  "Days 8–14",
    "day_15_21": "Days 15–21",
    "day_22_28": "Days 22–28",
}
PET_LABELS = {
    "normal": "No PET",
    "s1":     "S1 — patent\n(dry mucosa)",
    "s2":     "S2 — PET +\ninflammation",
    "s3":     "S3 — habitual\nsniffer",
    "s4":     "S4 — post-plug\n(stenotic)",
}

x_categories = [URI_LABELS[u] for u in URI_STATES]
# y-axis bottom→top (ECharts convention) — list bottom-row first
y_order = list(reversed(PET_STATES))
y_categories = [PET_LABELS[p] for p in y_order]

# Heatmap data with per-cell label color (white on dark cells, black on light)
heat_data = []
for yi, pet in enumerate(y_order):
    for xi, uri in enumerate(URI_STATES):
        v = GRID[pet][uri]
        text_color = "#ffffff" if v >= 45 else "#000000"
        heat_data.append({
            "value": [xi, yi, v],
            "label": {
                "show": True,
                "fontFamily": FONT_FAMILY,
                "fontSize": 28,
                "fontWeight": "bold",
                "color": text_color,
                "formatter": f"{v:.1f}%",
            },
        })

V_MAX = 100.0

opt = {
    "backgroundColor": "#ffffff",
    "textStyle": {"fontFamily": FONT_FAMILY, "color": "#000000"},
    "animation": False,
    "title": {
        "text": "URI × PET interaction: per-exposure p_barotitis (%) on FAC profile, healthy baseline patient",
        "left": "center", "top": 16,
        "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_TITLE, "fontWeight": "normal"},
    },
    "graphic": [
        {"type": "text", "left": "center", "bottom": 32, "z": 100,
         "style": {
             "text": "FAC Bogotá default chamber profile · 8,530 ft start · 25,000 ft hold · 2,470 ft/min descent · default healthy patient",
             "font": "22px Arial,sans-serif",
             "fill": "#000",
             "textAlign": "center",
         }},
    ],
    "grid": {"left": 320, "right": 220, "top": 130, "bottom": 220, "containLabel": True},
    "xAxis": {
        "type": "category", "data": x_categories,
        "name": "URI temporal state",
        "nameLocation": "middle", "nameGap": 68,
        "nameTextStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_TITLE, "color": "#000"},
        "splitArea": {"show": True},
        "axisLine": {"lineStyle": {"color": "#000", "width": 1}},
        "axisTick": {"show": False},
        "axisLabel": {"fontFamily": FONT_FAMILY, "fontSize": 26, "color": "#000",
                      "interval": 0, "lineHeight": 32},
    },
    "yAxis": {
        "type": "category", "data": y_categories,
        "name": "Patulous Eustachian-tube state",
        "nameLocation": "middle", "nameGap": 240, "nameRotate": 90,
        "nameTextStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_TITLE, "color": "#000"},
        "splitArea": {"show": True},
        "axisLine": {"lineStyle": {"color": "#000", "width": 1}},
        "axisTick": {"show": False},
        "axisLabel": {"fontFamily": FONT_FAMILY, "fontSize": 26, "color": "#000",
                      "interval": 0, "lineHeight": 32},
    },
    "visualMap": {
        "min": 0, "max": V_MAX,
        "calculable": False,
        "orient": "vertical",
        "right": 44, "top": 120, "bottom": 160,
        "itemWidth": 16,
        "text": ["100%", "0%"],
        "textGap": 8,
        "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": 26, "color": "#000"},
        # Ordered low→high stops; perceptually-sequential ramp (light yellow → red)
        "inRange": {
            "color": [
                "#FFF7BC",  # near-zero (very light yellow)
                "#FEE391",
                "#FEC44F",
                "#FE9929",
                "#EC7014",
                "#CC4C02",
                "#993404",  # ~50%
                "#662506",  # ~75%
                "#3F0F02",  # ~100% (deepest)
            ]
        },
        "show": True,
    },
    "series": [{
        "name": "p_barotitis",
        "type": "heatmap",
        "data": heat_data,
        "itemStyle": {"borderColor": "#000", "borderWidth": 0.4},
        "emphasis": {"itemStyle": {"shadowBlur": 0}},
    }],
}

OUT_DIR = Path(__file__).resolve().parent
result = render(
    opt,
    out_dir=OUT_DIR,
    slug="fig_04_uri_pet_interaction",
    width_mm=170,
    height_mm=130,
    emit_tiff=True,
)
print("Rendered:", result["png"])
print(f"Grid (PET × URI):")
header = "  " + "       ".join(URI_STATES)
print(header)
for pet in PET_STATES:
    row = f"  {pet:>6}: " + "  ".join(f"{GRID[pet][u]:>6.2f}%" for u in URI_STATES)
    print(row)
