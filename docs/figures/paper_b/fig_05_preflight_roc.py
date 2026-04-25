"""
Paper B (preflight fidelity sub-paper) — Figure 2. Receiver-operating-
characteristic curve for the 14-flag preflight battery.

Source: analysis/results/preflight_roc_logreg.json — produced by
``python -m analysis.scripts.preflight_roc`` from
docs/Cohort FAC/analysis/phase2_preflight_tidy.csv.

Multivariable logistic regression on the 14 yes/no preflight medical-
screening flags (target: fitness_decision in {apt, denied}; n = 1,004
evaluable, 23 denied). Reports AUC with non-parametric bootstrap 95% CI
(1,000 reps, seed 2026), and marks Youden's J optimum operating point.

Figure 2 (in the preflight fidelity paper's numbering) — note that this
script is paper_b/fig_05_* because the FAC cohort paper uses
fig_01..fig_04 from the same paper_b/ directory.
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
# Load curve from canonical JSON
# ---------------------------------------------------------------------------
ROC = json.loads((ROOT.parent / "analysis" / "results" / "preflight_roc_logreg.json").read_text())
fpr = ROC["fpr"]
tpr = ROC["tpr"]
auc_apparent = ROC["auc_apparent"]
auc_corrected = ROC["auc_corrected"]
auc_lo = ROC["auc_ci_lo_95_corrected"]
auc_hi = ROC["auc_ci_hi_95_corrected"]
youden_fpr = ROC["youden_fpr_apparent"]
youden_tpr = ROC["youden_tpr_sensitivity_apparent"]
youden_thr = ROC["youden_threshold"]
n_eval = ROC["n_eval"]
n_denied = ROC["n_denied"]
m_corrected = ROC["multivariable_at_youden_corrected"]

# Build series points
roc_points = [[f, t] for f, t in zip(fpr, tpr)]

opt = {
    "backgroundColor": "#ffffff",
    "textStyle": {"fontFamily": FONT_FAMILY, "color": "#000000"},
    "animation": False,
    "title": {
        "text": "Preflight 14-flag battery — ROC curve (multivariable logistic regression)",
        "left": "center", "top": 8,
        "textStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_TITLE, "fontWeight": "normal"},
    },
    "graphic": [
        # AUC annotation (top-left of plot area)
        {"type": "text", "left": 95, "top": 60, "z": 50,
         "style": {
             "text": (
                 f"AUC apparent  = {auc_apparent:.3f}\n"
                 f"AUC corrected = {auc_corrected:.3f}\n"
                 f"   95% CI [{auc_lo:.3f}, {auc_hi:.3f}]\n"
                 f"   Harrell-Steyerberg bootstrap, n=1,000"
             ),
             "font": "11px Arial,sans-serif",
             "fill": "#000",
             "lineHeight": 14,
             "textAlign": "left",
         }},
        # Operating-point annotation (corrected)
        {"type": "text", "left": 95, "top": 150, "z": 50,
         "style": {
             "text": (
                 f"At Youden threshold {youden_thr:.3f} (corrected):\n"
                 f"   sens {m_corrected['sensitivity']*100:.1f}%, spec {m_corrected['specificity']*100:.1f}%\n"
                 f"   PPV  {m_corrected['ppv']*100:.1f}%, NPV  {m_corrected['npv']*100:.1f}%\n"
                 f"   LR+  {m_corrected['lr_pos']:.2f},  LR-  {m_corrected['lr_neg']:.2f}"
             ),
             "font": "11px Arial,sans-serif",
             "fill": "#000",
             "lineHeight": 14,
             "textAlign": "left",
         }},
        # Footer note
        {"type": "text", "left": "center", "bottom": 14, "z": 100,
         "style": {
             "text": (
                 f"n = {n_eval:,} evaluable preflight submissions · {n_denied} denials · "
                 f"penalised L2-ridge logistic regression with bootstrap optimism correction (TRIPOD 2015)"
             ),
             "font": "9px Arial,sans-serif",
             "fill": "#000",
             "textAlign": "center",
         }},
    ],
    "grid": {"left": 60, "right": 30, "top": 40, "bottom": 60, "containLabel": True},
    "xAxis": {
        "type": "value", "min": 0, "max": 1.0,
        "name": "False positive rate (1 − specificity)",
        "nameLocation": "middle", "nameGap": 30,
        "nameTextStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_TITLE, "color": "#000"},
        "axisLine": {"lineStyle": {"color": "#000", "width": 1}},
        "axisTick": {"lineStyle": {"color": "#000", "width": 1}, "length": 4},
        "axisLabel": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_LABEL, "color": "#000"},
        "splitLine": {"lineStyle": {"color": "#E5E5E5", "width": 0.5, "type": "dashed"}},
    },
    "yAxis": {
        "type": "value", "min": 0, "max": 1.0,
        "name": "True positive rate (sensitivity)",
        "nameLocation": "middle", "nameGap": 38, "nameRotate": 90,
        "nameTextStyle": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_TITLE, "color": "#000"},
        "axisLine": {"show": True, "lineStyle": {"color": "#000", "width": 1}},
        "axisTick": {"show": True, "lineStyle": {"color": "#000", "width": 1}},
        "axisLabel": {"fontFamily": FONT_FAMILY, "fontSize": FONT_SIZE_AXIS_LABEL, "color": "#000"},
        "splitLine": {"lineStyle": {"color": "#E5E5E5", "width": 0.5, "type": "dashed"}},
    },
    "series": [
        # Diagonal reference (random classifier)
        {"name": "Chance line",
         "type": "line",
         "data": [[0, 0], [1, 1]],
         "lineStyle": {"color": PALETTE["grey"], "width": 1, "type": "dashed"},
         "symbol": "none",
         "z": 3, "silent": True},
        # ROC curve
        {"name": "ROC", "type": "line",
         "data": roc_points,
         "lineStyle": {"color": PALETTE["blue"], "width": 2.0},
         "symbol": "none",
         "areaStyle": {"color": PALETTE["skyblue"], "opacity": 0.18},
         "z": 8},
        # Youden optimum point
        {"name": "Youden optimum",
         "type": "scatter",
         "data": [[youden_fpr, youden_tpr]],
         "symbol": "diamond",
         "symbolSize": 16,
         "itemStyle": {"color": PALETTE["vermilion"], "borderColor": "#000", "borderWidth": 0.7},
         "z": 12,
         "label": {"show": True, "position": "bottom",
                   "fontFamily": FONT_FAMILY, "fontSize": 10, "color": "#000",
                   "formatter": "Youden optimum",
                   "distance": 8}},
    ],
}

OUT_DIR = Path(__file__).resolve().parent
result = render(
    opt,
    out_dir=OUT_DIR,
    slug="fig_05_preflight_roc",
    width_mm=89,
    height_mm=89,
    emit_tiff=True,
)
print(f"Rendered: {result['png']}")
print(f"AUC apparent  = {auc_apparent:.4f}")
print(f"AUC corrected = {auc_corrected:.4f}  [{auc_lo:.4f}, {auc_hi:.4f}]")
print(f"Youden threshold = {youden_thr:.4f}")
print(f"Corrected sens={m_corrected['sensitivity']*100:.1f}% spec={m_corrected['specificity']*100:.1f}% "
      f"PPV={m_corrected['ppv']*100:.1f}% NPV={m_corrected['npv']*100:.1f}% "
      f"LR+={m_corrected['lr_pos']:.2f} LR-={m_corrected['lr_neg']:.2f}")
