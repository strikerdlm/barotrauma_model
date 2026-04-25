"""
Render one or more ECharts options to publication-grade PNG + SVG via Chrome headless.

Sizing model:
  - User passes physical size in mm (e.g. 89 × 75) at 600 dpi target
  - We render the canvas at LOGICAL pixels (mm × 300/25.4 ≈ 11.81 px/mm) with
    device-scale-factor 2 → final raster is 600 dpi
  - SVG is vector and dpi-agnostic
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

ECHARTS_JS = (Path(__file__).parent / "echarts.min.js").resolve()


def _mm_to_logical_px(mm: float) -> int:
    return int(round(mm * 300.0 / 25.4))


def _build_html(panels: list[dict], total_w_log: int, total_h_log: int,
                replacements: dict[str, str] | None = None,
                panel_titles: list[dict] | None = None) -> str:
    """Build an HTML page with one or more stacked ECharts canvases."""
    div_blocks, init_blocks = [], []
    svg_collect = []
    for i, panel in enumerate(panels):
        opt_str = json.dumps(panel["option"], ensure_ascii=False)
        if replacements:
            for k, v in replacements.items():
                opt_str = opt_str.replace(f'"{k}"', v)
        w = panel["w"]
        h = panel["h"]
        div_blocks.append(
            f'<div id="c{i}" style="width:{w}px;height:{h}px;display:block;"></div>'
        )
        init_blocks.append(
            f"const opt{i} = {opt_str};\n"
            f"const ch{i} = echarts.init(document.getElementById('c{i}'), null, {{ renderer: 'svg', width: {w}, height: {h} }});\n"
            f"ch{i}.setOption(opt{i});\n"
            f"ch{i}.resize({{width: {w}, height: {h}}});\n"
        )
        svg_collect.append(f"ch{i}.renderToSVGString()")

    panel_label_html = ""
    if panel_titles:
        for t in panel_titles:
            panel_label_html += (
                f'<span style="position:absolute;left:{t["left"]}px;top:{t["top"]}px;'
                f'font-family:Arial,sans-serif;font-size:{t.get("size",16)}px;font-weight:bold;color:#000;">{t["text"]}</span>'
            )

    html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><title>chart</title>
<style>
  html,body{{margin:0;padding:0;background:#fff}}
  #wrap{{width:{total_w_log}px;height:{total_h_log}px;position:relative;}}
</style>
<script src="file://{ECHARTS_JS}"></script>
</head><body>
<div id="wrap">
{''.join(div_blocks)}
{panel_label_html}
</div>
<script>
{''.join(init_blocks)}
window.__svg = [{', '.join(svg_collect)}].join('\\n');
document.title = "READY";
</script>
</body></html>
"""
    return html


def render(option: dict[str, Any], *, out_dir: Path, slug: str,
           width_mm: float, height_mm: float,
           render_item_replacements: dict[str, str] | None = None,
           panel_titles: list[dict] | None = None) -> dict[str, Any]:
    """Single-panel render."""
    return render_panels(
        [{"option": option, "w_mm": width_mm, "h_mm": height_mm}],
        out_dir=out_dir, slug=slug,
        total_w_mm=width_mm, total_h_mm=height_mm,
        render_item_replacements=render_item_replacements,
        panel_titles=panel_titles,
    )


def render_panels(panels_mm: list[dict], *, out_dir: Path, slug: str,
                  total_w_mm: float, total_h_mm: float,
                  render_item_replacements: dict[str, str] | None = None,
                  panel_titles: list[dict] | None = None) -> dict[str, Any]:
    """Render multiple stacked ECharts panels to a single PNG + SVG."""
    out_dir.mkdir(parents=True, exist_ok=True)
    total_w_log = _mm_to_logical_px(total_w_mm)
    total_h_log = _mm_to_logical_px(total_h_mm)

    panels_logical = []
    for p in panels_mm:
        panels_logical.append({
            "option": p["option"],
            "w": _mm_to_logical_px(p["w_mm"]),
            "h": _mm_to_logical_px(p["h_mm"]),
        })

    html = _build_html(panels_logical, total_w_log, total_h_log,
                       replacements=render_item_replacements,
                       panel_titles=panel_titles)

    html_path = out_dir / f"{slug}.html"
    png_path = out_dir / f"{slug}.png"
    svg_path = out_dir / f"{slug}.svg"
    html_path.write_text(html, encoding="utf-8")

    # Step 1: extract SVG via Chrome's dump-dom (gives us a clean vector master)
    eval_html = out_dir / f"{slug}.eval.html"
    body = html.replace(
        'document.title = "READY";',
        'document.title = "READY"; '
        'setTimeout(() => { const pre = document.createElement("pre"); pre.id="svgtxt"; pre.textContent = window.__svg; document.body.appendChild(pre); }, 800);'
    )
    eval_html.write_text(body, encoding="utf-8")
    proc = subprocess.run([
        "google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
        f"--window-size={total_w_log},{total_h_log}",
        "--virtual-time-budget=4000",
        "--dump-dom",
        f"file://{eval_html.resolve()}",
    ], check=True, capture_output=True, timeout=45)
    dom = proc.stdout.decode("utf-8", errors="replace")
    m = re.search(r'<pre id="svgtxt">(.*?)</pre>', dom, re.DOTALL)
    if m:
        svg = m.group(1).replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&quot;", '"')
        svg_path.write_text(svg, encoding="utf-8")
    eval_html.unlink(missing_ok=True)

    # Step 2: convert SVG to high-DPI PNG via cairosvg (bypasses Chrome's screenshot quirks)
    if svg_path.exists():
        import cairosvg
        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(png_path),
            output_width=total_w_log * 2,
            output_height=total_h_log * 2,
        )
    else:
        # Fallback to Chrome screenshot
        subprocess.run([
            "google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
            f"--window-size={total_w_log},{total_h_log}",
            "--force-device-scale-factor=2",
            f"--screenshot={png_path}",
            "--virtual-time-budget=4000",
            "--hide-scrollbars",
            f"file://{html_path.resolve()}",
        ], check=True, capture_output=True, timeout=45)

    return {"html": html_path, "png": png_path, "svg": svg_path,
            "size_px": (total_w_log * 2, total_h_log * 2),
            "size_mm": (total_w_mm, total_h_mm)}
