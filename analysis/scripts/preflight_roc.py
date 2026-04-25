"""
Preflight 14-flag battery — ROC analysis for the manuscript_preflight_fidelity
paper. Produces analysis/results/preflight_roc_logreg.json with AUC + bootstrap
95% CI + Youden J optimum + per-flag log-odds, then drives the figure script
docs/figures/paper_b/fig_05_preflight_roc.py.

Usage:
    python -m analysis.scripts.preflight_roc

Inputs:  docs/Cohort FAC/analysis/phase2_preflight_tidy.csv
Outputs: analysis/results/preflight_roc_logreg.json
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "docs" / "Cohort FAC" / "analysis" / "phase2_preflight_tidy.csv"
OUTPUT = ROOT / "analysis" / "results" / "preflight_roc_logreg.json"

RNG_SEED = 2026
N_BOOTSTRAP = 1000


def main() -> None:
    rows = []
    with INPUT.open() as f:
        for r in csv.DictReader(f):
            rows.append(r)

    # Evaluable rows = preflight submissions with a clean apt/denied decision
    evaluable = [r for r in rows if r["fitness_decision"] in ("apt", "denied")]
    flags = [k for k in evaluable[0] if k.startswith("flag_")]

    def to_int(v: str) -> int:
        return 1 if v in ("1", "True", "TRUE", "true") else 0

    X = np.array([[to_int(r[f]) for f in flags] for r in evaluable])
    y = np.array([1 if r["fitness_decision"] == "denied" else 0 for r in evaluable])

    # Multivariable logistic regression (no regularisation tweak; lbfgs default L2)
    model = LogisticRegression(max_iter=1000, solver="lbfgs")
    model.fit(X, y)
    y_score = model.predict_proba(X)[:, 1]

    auc = float(roc_auc_score(y, y_score))
    fpr, tpr, thr = roc_curve(y, y_score)
    youden = tpr - fpr
    opt_idx = int(np.argmax(youden))

    # Bootstrap 95% CI for AUC
    rng = np.random.default_rng(RNG_SEED)
    boot_aucs: list[float] = []
    for _ in range(N_BOOTSTRAP):
        idx = rng.integers(0, len(y), len(y))
        if y[idx].sum() == 0 or y[idx].sum() == len(y):
            continue
        boot_aucs.append(float(roc_auc_score(y[idx], y_score[idx])))
    auc_lo, auc_hi = np.percentile(boot_aucs, [2.5, 97.5])

    coefs = sorted(zip(flags, model.coef_[0].tolist()), key=lambda r: -abs(r[1]))

    payload = {
        "method": "multivariable logistic regression (sklearn lbfgs, default L2)",
        "n_eval": int(len(y)),
        "n_denied": int(y.sum()),
        "denial_rate": float(y.mean()),
        "auc": auc,
        "auc_ci_lo_95": float(auc_lo),
        "auc_ci_hi_95": float(auc_hi),
        "auc_ci_method": f"non-parametric percentile bootstrap, {N_BOOTSTRAP} reps, seed {RNG_SEED}",
        "youden_j": float(youden[opt_idx]),
        "youden_threshold": float(thr[opt_idx]),
        "youden_fpr": float(fpr[opt_idx]),
        "youden_tpr_sensitivity": float(tpr[opt_idx]),
        "fpr": fpr.tolist(),
        "tpr": tpr.tolist(),
        "thresholds": thr.tolist(),
        "flags": flags,
        "flag_coefs_log_odds": dict(coefs),
        "intercept_log_odds": float(model.intercept_[0]),
        "rng_seed": RNG_SEED,
        "input_csv": str(INPUT.relative_to(ROOT)),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2))

    print(f"AUC: {auc:.4f}  CI [{auc_lo:.4f}, {auc_hi:.4f}]  (n={len(y)}, denied={int(y.sum())})")
    print(f"Youden J: {youden[opt_idx]:.4f} at thr={thr[opt_idx]:.4f} "
          f"(FPR={fpr[opt_idx]:.4f}, TPR={tpr[opt_idx]:.4f})")
    print(f"Top 3 flag coefficients (log-odds):")
    for name, c in coefs[:3]:
        print(f"  {name}: {c:+.3f}")
    print(f"Saved → {OUTPUT}")


if __name__ == "__main__":
    main()
