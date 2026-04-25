"""
Q1 / AMHP-grade ECharts theme shared across all figures in both papers.

Design principles enforced:
- Sans-serif Arial throughout (AMHP Instructions for Authors)
- Print-grade colors that read in B&W (high luminance contrast + line-style/marker fallbacks)
- 600 dpi raster output via 4x device scaling
- Vector SVG export for editable masters
- Wilson 95% CIs on every proportion
- ColorBrewer-derived palette, color-blind safe (Wong 2011 / Okabe-Ito)
"""
from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Colour palette — Wong 2011 (color-blind safe, prints clearly in greyscale)
# ---------------------------------------------------------------------------
PALETTE = {
    "black":   "#000000",
    "orange":  "#E69F00",
    "skyblue": "#56B4E9",
    "green":   "#009E73",
    "yellow":  "#F0E442",
    "blue":    "#0072B2",
    "vermilion": "#D55E00",
    "purple":  "#CC79A7",
    "grey":    "#808080",
    "lightgrey": "#D9D9D9",
}

# ---------------------------------------------------------------------------
# Typography — AMHP requires Arial; sans-serif fallback chain
# ---------------------------------------------------------------------------
FONT_FAMILY = "Arial, Helvetica, 'Liberation Sans', sans-serif"
FONT_SIZE_AXIS_LABEL = 11      # axis tick labels
FONT_SIZE_AXIS_TITLE = 12      # axis names
FONT_SIZE_TITLE = 13           # subtitle / panel title
FONT_SIZE_LEGEND = 11

# ---------------------------------------------------------------------------
# Default dimensions (mm × scale = px). AMHP: column widths
#   single column   = 89 mm
#   1.5 column      = 120 mm
#   double column   = 183 mm
# Render at 4× pixel density for 600 dpi raster.
# ---------------------------------------------------------------------------
PX_PER_MM_AT_600DPI = 600 / 25.4   # ≈ 23.62
def mm_to_px(mm: float) -> int:
    return int(round(mm * PX_PER_MM_AT_600DPI))

CANVAS_SINGLE = (mm_to_px(89), mm_to_px(75))
CANVAS_ONEHALF = (mm_to_px(120), mm_to_px(95))
CANVAS_DOUBLE = (mm_to_px(183), mm_to_px(110))

# ---------------------------------------------------------------------------
# Wilson 95% CI — reused across cohort figures
# ---------------------------------------------------------------------------
def wilson(numerator: int, denominator: int, z: float = 1.959964) -> tuple[float, float, float]:
    """Wilson score interval for a binomial proportion. Returns (p, lo, hi)."""
    if denominator == 0:
        return float("nan"), float("nan"), float("nan")
    p = numerator / denominator
    n = denominator
    z2 = z * z
    centre = (p + z2 / (2 * n)) / (1 + z2 / n)
    half = (z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))) / (1 + z2 / n)
    return p, max(0.0, centre - half), min(1.0, centre + half)

# ---------------------------------------------------------------------------
# Base option scaffold — every figure builds on this
# ---------------------------------------------------------------------------
def base_option(title: str | None = None, subtitle: str | None = None) -> dict[str, Any]:
    return {
        "backgroundColor": "#ffffff",
        "textStyle": {"fontFamily": FONT_FAMILY, "color": "#000000"},
        "title": {
            "text": title or "",
            "subtext": subtitle or "",
            "left": "center",
            "top": 6,
            "textStyle": {
                "fontFamily": FONT_FAMILY,
                "fontSize": FONT_SIZE_TITLE,
                "fontWeight": "bold",
                "color": "#000000",
            },
            "subtextStyle": {
                "fontFamily": FONT_FAMILY,
                "fontSize": FONT_SIZE_AXIS_LABEL,
                "color": "#404040",
            },
        },
        "animation": False,
        "grid": {"left": 70, "right": 30, "top": 60, "bottom": 60, "containLabel": True},
        "tooltip": {"show": False},  # publication, not interactive
        "legend": {
            "show": False,            # default off; re-enable per figure
            "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_LEGEND, "color": "#000000"},
            "borderColor": "#000000",
            "borderWidth": 0,
            "icon": "rect",
        },
    }

# ---------------------------------------------------------------------------
# Common axis style
# ---------------------------------------------------------------------------
def axis(name: str = "", **overrides) -> dict[str, Any]:
    base = {
        "name": name,
        "nameLocation": "middle",
        "nameGap": 35,
        "nameTextStyle": {
            "fontFamily": FONT_FAMILY,
            "fontSize": FONT_SIZE_AXIS_TITLE,
            "fontWeight": "normal",
            "color": "#000000",
        },
        "axisLine": {"show": True, "lineStyle": {"color": "#000000", "width": 1}},
        "axisTick": {"show": True, "lineStyle": {"color": "#000000", "width": 1}, "length": 4},
        "axisLabel": {
            "fontFamily": FONT_FAMILY,
            "fontSize": FONT_SIZE_AXIS_LABEL,
            "color": "#000000",
        },
        "splitLine": {"show": True, "lineStyle": {"color": "#E5E5E5", "width": 0.5, "type": "dashed"}},
    }
    base.update(overrides)
    return base

# ---------------------------------------------------------------------------
# HTML template — embeds the option JSON, loads ECharts, allows screenshot
# ---------------------------------------------------------------------------
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>{title}</title>
<style>
  html, body {{ margin: 0; padding: 0; background: #ffffff; }}
  #c {{ width: {width}px; height: {height}px; }}
</style>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
</head>
<body>
<div id="c"></div>
<script>
  const opt = {option_json};
  const chart = echarts.init(document.getElementById('c'), null, {{ renderer: 'svg' }});
  chart.setOption(opt);
  // expose svg for puppeteer
  window.__svg = chart.renderToSVGString();
  document.title = "READY";
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Render helpers — write HTML and convert via Chromium headless
# ---------------------------------------------------------------------------
def write_html(option: dict[str, Any], html_path: Path, width_px: int, height_px: int, title: str = "fig") -> None:
    """Persist an editable HTML master with the ECharts option inline."""
    html = HTML_TEMPLATE.format(
        title=title,
        width=width_px,
        height=height_px,
        option_json=json.dumps(option, ensure_ascii=False),
    )
    html_path.write_text(html, encoding="utf-8")


def render_via_chromium(html_path: Path, png_path: Path, width_px: int, height_px: int, scale: float = 4.0) -> None:
    """Use system Chromium to screenshot the ECharts canvas at high DPI."""
    cmd = [
        "google-chrome",
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        f"--window-size={int(width_px * scale)},{int(height_px * scale)}",
        f"--force-device-scale-factor={scale}",
        f"--screenshot={png_path}",
        "--virtual-time-budget=4000",
        "--hide-scrollbars",
        f"file://{html_path.resolve()}",
    ]
    subprocess.run(cmd, check=True, capture_output=True, timeout=60)


def extract_svg(html_path: Path, svg_path: Path) -> None:
    """Use Chromium to evaluate window.__svg and dump to file."""
    eval_html = html_path.with_suffix(".eval.html")
    body = html_path.read_text(encoding="utf-8")
    body = body.replace(
        "document.title = \"READY\";",
        "document.title = \"READY\"; setTimeout(() => { const pre = document.createElement('pre'); pre.id='svgtxt'; pre.textContent = window.__svg; document.body.appendChild(pre); }, 800);",
    )
    eval_html.write_text(body, encoding="utf-8")

    out_html = svg_path.with_suffix(".dump.html")
    cmd = [
        "google-chrome",
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--window-size=2000,1500",
        "--virtual-time-budget=4000",
        "--dump-dom",
        f"file://{eval_html.resolve()}",
    ]
    proc = subprocess.run(cmd, check=True, capture_output=True, timeout=60)
    dom = proc.stdout.decode("utf-8", errors="replace")
    # Extract the <pre id="svgtxt">…</pre> block (which contains escaped SVG)
    import re
    match = re.search(r'<pre id="svgtxt">(.*?)</pre>', dom, re.DOTALL)
    if match:
        svg_str = match.group(1)
        # un-escape HTML entities
        svg_str = svg_str.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&quot;", '"')
        svg_path.write_text(svg_str, encoding="utf-8")
    eval_html.unlink(missing_ok=True)
    out_html.unlink(missing_ok=True)


def export_figure(
    option: dict[str, Any],
    *,
    out_dir: Path,
    slug: str,
    width_px: int,
    height_px: int,
    scale: float = 4.0,
) -> dict[str, Path]:
    """Export an ECharts option as the standard AMHP bundle."""
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / f"{slug}.html"
    png_path = out_dir / f"{slug}.png"
    svg_path = out_dir / f"{slug}.svg"

    write_html(option, html_path, width_px, height_px, title=slug)
    render_via_chromium(html_path, png_path, width_px, height_px, scale=scale)
    extract_svg(html_path, svg_path)
    return {"html": html_path, "png": png_path, "svg": svg_path}
