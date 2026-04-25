"""
Preflight 14-flag battery — TRIPOD-compliant prediction-model analysis for the
manuscript_preflight_fidelity paper.

Method (Path C — penalized regression + bootstrap optimism correction):

  - Per-flag univariable diagnostic-test characteristics (2x2 tables):
    sensitivity, specificity, PPV, NPV, LR+, LR-, DOR with Wilson 95% CIs for
    proportions and Katz log 95% CIs for likelihood ratios.

  - Multivariable model: penalized (L2 ridge) logistic regression on all 14
    flags. Penalisation provides shrinkage that stabilises coefficient
    estimates in the low-EPV regime (23 events, 14 predictors, EPV = 1.6).
    Regularisation strength selected by 5-fold cross-validated maximum
    log-likelihood (sklearn LogisticRegressionCV with L1 inverse-strength
    grid).
    - References: Riley et al., Stat Med 2019;38(7):1276-1296 (sample size /
      shrinkage rationale); van Smeden et al., Stat Methods Med Res
      2019;28(8):2455-2474 (EPV-of-10 superseded); Collins et al., Ann Intern
      Med 2015;162(1):55-63 (TRIPOD reporting).

  - Internal validation: Harrell-Steyerberg bootstrap optimism correction
    (Steyerberg et al., J Clin Epidemiol 2001;54(8):774-781). For each of B
    bootstrap resamples (with replacement, sample size = original n):
      1. Refit the same model spec on the bootstrap sample.
      2. Evaluate AUC on the bootstrap sample (apparent_b) and on the
         original sample (test_b).
      3. Optimism_b = apparent_b - test_b.
    Optimism-corrected AUC = original_apparent - mean(optimism). Same
    procedure applies to the operating-point metrics (sens, spec, PPV, NPV,
    LR+, LR-) evaluated at the original Youden threshold.

Outputs the full payload (apparent + corrected) to
analysis/results/preflight_roc_logreg.json. Drives both the figure
(docs/figures/paper_b/fig_05_preflight_roc.py) and the diagnostic-test table
in manuscript_preflight_fidelity.md.

Usage:
    python -m analysis.scripts.preflight_roc

Inputs:  docs/Cohort FAC/analysis/phase2_preflight_tidy.csv
Outputs: analysis/results/preflight_roc_logreg.json
"""
from __future__ import annotations

import csv
import json
import math
import warnings
from pathlib import Path

import numpy as np
# Silence sklearn 1.8+ deprecation noise for LogisticRegressionCV. The current
# API is still functional; we'll migrate to l1_ratios when scikit-learn 1.10
# lands and the new API stabilises.
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")
from sklearn.linear_model import LogisticRegressionCV  # noqa: E402
from sklearn.metrics import roc_auc_score, roc_curve  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "docs" / "Cohort FAC" / "analysis" / "phase2_preflight_tidy.csv"
OUTPUT = ROOT / "analysis" / "results" / "preflight_roc_logreg.json"

RNG_SEED = 2026
N_BOOTSTRAP = 1000
Z_95 = 1.959964
CV_FOLDS = 5
# Inverse regularisation strength grid (sklearn convention: smaller C => stronger penalty).
# Spans 1e-3 (heavy shrinkage toward zero) to 1e3 (effectively unpenalised).
C_GRID = np.logspace(-3, 3, 13).tolist()


def wilson(num: int, den: int, z: float = Z_95) -> tuple[float, float, float]:
    if den == 0:
        return float("nan"), float("nan"), float("nan")
    p = num / den
    z2 = z * z
    centre = (p + z2 / (2 * den)) / (1 + z2 / den)
    half = (z * math.sqrt(p * (1 - p) / den + z2 / (4 * den * den))) / (1 + z2 / den)
    return p, max(0.0, centre - half), min(1.0, centre + half)


def diag_metrics(tp: int, fp: int, fn: int, tn: int, z: float = Z_95) -> dict:
    """All diagnostic-test metrics from a 2x2 table.

    Proportions get Wilson 95% CIs; LR+ and LR- get Katz log 95% CIs.
    Returns NaN bounds when zero-cell precludes a finite Katz CI.
    """
    sens, sens_lo, sens_hi = wilson(tp, tp + fn)
    spec, spec_lo, spec_hi = wilson(tn, tn + fp)
    ppv, ppv_lo, ppv_hi = wilson(tp, tp + fp)
    npv, npv_lo, npv_hi = wilson(tn, tn + fn)

    if tp > 0 and fp > 0 and fn > 0 and tn > 0:
        lrp = (tp / (tp + fn)) / (fp / (fp + tn))
        se_log_lrp = math.sqrt(1 / tp - 1 / (tp + fn) + 1 / fp - 1 / (fp + tn))
        lrp_lo = math.exp(math.log(lrp) - z * se_log_lrp)
        lrp_hi = math.exp(math.log(lrp) + z * se_log_lrp)
        lrn = (fn / (tp + fn)) / (tn / (fp + tn))
        se_log_lrn = math.sqrt(1 / fn - 1 / (tp + fn) + 1 / tn - 1 / (fp + tn))
        lrn_lo = math.exp(math.log(lrn) - z * se_log_lrn)
        lrn_hi = math.exp(math.log(lrn) + z * se_log_lrn)
        dor = lrp / lrn
    else:
        lrp = (sens / (1 - spec)) if (spec < 1) else float("inf")
        lrn = ((1 - sens) / spec) if (spec > 0) else float("nan")
        lrp_lo = lrp_hi = lrn_lo = lrn_hi = float("nan")
        dor = (lrp / lrn) if (lrn and math.isfinite(lrn)) else float("inf")

    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "sensitivity": sens, "sensitivity_lo": sens_lo, "sensitivity_hi": sens_hi,
        "specificity": spec, "specificity_lo": spec_lo, "specificity_hi": spec_hi,
        "ppv": ppv, "ppv_lo": ppv_lo, "ppv_hi": ppv_hi,
        "npv": npv, "npv_lo": npv_lo, "npv_hi": npv_hi,
        "lr_pos": lrp, "lr_pos_lo": lrp_lo, "lr_pos_hi": lrp_hi,
        "lr_neg": lrn, "lr_neg_lo": lrn_lo, "lr_neg_hi": lrn_hi,
        "dor": dor,
    }


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

    # ---- Multivariable model: penalized (L2 ridge) logistic regression ----
    # Cross-validated regularisation strength on the original sample.
    def fit_model(X_fit: np.ndarray, y_fit: np.ndarray) -> LogisticRegressionCV:
        m = LogisticRegressionCV(
            Cs=C_GRID, cv=CV_FOLDS, penalty="l2", solver="lbfgs",
            max_iter=2000, scoring="neg_log_loss",
            class_weight=None, random_state=RNG_SEED,
        )
        m.fit(X_fit, y_fit)
        return m

    model = fit_model(X, y)
    y_score = model.predict_proba(X)[:, 1]
    selected_C = float(model.C_[0])

    apparent_auc = float(roc_auc_score(y, y_score))
    fpr, tpr, thr = roc_curve(y, y_score)
    youden = tpr - fpr
    opt_idx = int(np.argmax(youden))
    threshold = float(thr[opt_idx])
    y_pred = (y_score >= threshold).astype(int)

    tp = int(((y == 1) & (y_pred == 1)).sum())
    fp = int(((y == 0) & (y_pred == 1)).sum())
    fn = int(((y == 1) & (y_pred == 0)).sum())
    tn = int(((y == 0) & (y_pred == 0)).sum())
    multivar_apparent = diag_metrics(tp, fp, fn, tn)

    coefs = sorted(zip(flags, model.coef_[0].tolist()), key=lambda r: -abs(r[1]))

    # ---- Bootstrap optimism correction (Harrell-Steyerberg) ----
    # For each bootstrap rep:
    #   1. Resample with replacement (size n).
    #   2. Refit model on bootstrap sample.
    #   3. Compute apparent AUC on bootstrap sample.
    #   4. Compute test AUC on the ORIGINAL sample.
    #   5. Optimism = apparent_b - test_b.
    # Corrected = original_apparent - mean(optimism).
    # Same logic for sens/spec/PPV/NPV/LR+/LR- evaluated at the original
    # Youden threshold (held fixed across bootstrap reps to mirror deployed
    # use of a pre-set screening threshold).
    rng = np.random.default_rng(RNG_SEED)
    boot_test_aucs: list[float] = []
    optimism_auc: list[float] = []
    optimism_sens: list[float] = []
    optimism_spec: list[float] = []
    optimism_ppv: list[float] = []
    optimism_npv: list[float] = []
    optimism_lrp: list[float] = []
    optimism_lrn: list[float] = []

    def metrics_at_threshold(y_true: np.ndarray, scores: np.ndarray, thr_val: float) -> dict:
        pred = (scores >= thr_val).astype(int)
        tp_ = int(((y_true == 1) & (pred == 1)).sum())
        fp_ = int(((y_true == 0) & (pred == 1)).sum())
        fn_ = int(((y_true == 1) & (pred == 0)).sum())
        tn_ = int(((y_true == 0) & (pred == 0)).sum())
        return diag_metrics(tp_, fp_, fn_, tn_)

    for _ in range(N_BOOTSTRAP):
        idx = rng.integers(0, len(y), len(y))
        y_b = y[idx]
        if y_b.sum() == 0 or y_b.sum() == len(y_b):
            continue
        X_b = X[idx]
        m_b = fit_model(X_b, y_b)
        score_b_on_b = m_b.predict_proba(X_b)[:, 1]
        score_b_on_orig = m_b.predict_proba(X)[:, 1]

        try:
            apparent_b = float(roc_auc_score(y_b, score_b_on_b))
            test_b = float(roc_auc_score(y, score_b_on_orig))
        except ValueError:
            continue
        optimism_auc.append(apparent_b - test_b)
        boot_test_aucs.append(test_b)

        # Operating-point metrics: evaluate at the original Youden threshold
        # (the deployment scenario where the threshold is fixed before the
        # next sample is drawn).
        m_app_b = metrics_at_threshold(y_b, score_b_on_b, threshold)
        m_test_b = metrics_at_threshold(y, score_b_on_orig, threshold)
        for key, accumulator in [
            ("sensitivity", optimism_sens), ("specificity", optimism_spec),
            ("ppv", optimism_ppv), ("npv", optimism_npv),
            ("lr_pos", optimism_lrp), ("lr_neg", optimism_lrn),
        ]:
            a = m_app_b[key]
            t = m_test_b[key]
            if math.isfinite(a) and math.isfinite(t):
                accumulator.append(a - t)

    def corrected(apparent: float, optimism_list: list[float]) -> float:
        if not optimism_list:
            return float("nan")
        return apparent - float(np.mean(optimism_list))

    auc_corrected = corrected(apparent_auc, optimism_auc)
    # Use the bootstrap-test AUC distribution for an honest CI on
    # generalisation performance (not the apparent-on-bootstrap distribution).
    auc_lo, auc_hi = np.percentile(boot_test_aucs, [2.5, 97.5])

    multivar_corrected = {
        "sensitivity": corrected(multivar_apparent["sensitivity"], optimism_sens),
        "specificity": corrected(multivar_apparent["specificity"], optimism_spec),
        "ppv": corrected(multivar_apparent["ppv"], optimism_ppv),
        "npv": corrected(multivar_apparent["npv"], optimism_npv),
        "lr_pos": corrected(multivar_apparent["lr_pos"], optimism_lrp),
        "lr_neg": corrected(multivar_apparent["lr_neg"], optimism_lrn),
    }
    multivar_corrected["dor"] = (
        multivar_corrected["lr_pos"] / multivar_corrected["lr_neg"]
        if multivar_corrected["lr_neg"] not in (0, float("nan"))
        and math.isfinite(multivar_corrected["lr_pos"])
        and math.isfinite(multivar_corrected["lr_neg"])
        else float("nan")
    )

    # ---- Per-flag univariable diagnostic-test metrics ----
    per_flag = {}
    for j, fname in enumerate(flags):
        flag_pos = X[:, j] == 1
        tp_f = int(((y == 1) & flag_pos).sum())
        fp_f = int(((y == 0) & flag_pos).sum())
        fn_f = int(((y == 1) & ~flag_pos).sum())
        tn_f = int(((y == 0) & ~flag_pos).sum())
        per_flag[fname] = diag_metrics(tp_f, fp_f, fn_f, tn_f)

    payload = {
        "method": "penalized (L2 ridge) logistic regression with cross-validated regularisation",
        "modelling_software": "scikit-learn LogisticRegressionCV (lbfgs, L2, 5-fold CV on neg-log-loss)",
        "regularisation_strength_grid_C": C_GRID,
        "regularisation_strength_selected_C": selected_C,
        "internal_validation": "Harrell-Steyerberg bootstrap optimism correction",
        "n_bootstrap": N_BOOTSTRAP,
        "rng_seed": RNG_SEED,
        "n_eval": int(len(y)),
        "n_denied": int(y.sum()),
        "denial_rate_prevalence": float(y.mean()),
        "epv_unpenalised_equivalent": float(int(y.sum()) / len(flags)),
        # Discrimination
        "auc_apparent": apparent_auc,
        "auc_corrected": auc_corrected,
        "auc_ci_lo_95_corrected": float(auc_lo),
        "auc_ci_hi_95_corrected": float(auc_hi),
        "auc_ci_method": (
            "non-parametric percentile bootstrap of test-on-original AUC over "
            f"{len(boot_test_aucs)} reps; reflects expected out-of-sample "
            "discrimination uncertainty"
        ),
        # Operating point
        "youden_j_apparent": float(youden[opt_idx]),
        "youden_threshold": threshold,
        "youden_fpr_apparent": float(fpr[opt_idx]),
        "youden_tpr_sensitivity_apparent": float(tpr[opt_idx]),
        "multivariable_at_youden_apparent": multivar_apparent,
        "multivariable_at_youden_corrected": multivar_corrected,
        # Per-flag univariable (no fitting => no optimism correction)
        "diagnostic_test_metric_methods": {
            "proportions_ci": "Wilson 95% (z=1.959964)",
            "lr_ci": "Katz log 95% (NaN when any zero cell)",
            "dor": "LR+ / LR-",
            "multivariable_corrected": (
                "Harrell-Steyerberg bootstrap optimism correction "
                f"({N_BOOTSTRAP} reps, seed {RNG_SEED}); operating-point metrics "
                "evaluated at the original Youden threshold across all reps"
            ),
        },
        "per_flag_univariable": per_flag,
        # ROC curve (apparent fit)
        "fpr": fpr.tolist(),
        "tpr": tpr.tolist(),
        "thresholds": thr.tolist(),
        "flags": flags,
        "flag_coefs_log_odds_penalised": dict(coefs),
        "intercept_log_odds": float(model.intercept_[0]),
        "input_csv": str(INPUT.relative_to(ROOT)),
        "references": [
            "Riley RD et al. Stat Med 2019;38(7):1276-1296. doi:10.1002/sim.7992",
            "van Smeden M et al. Stat Methods Med Res 2019;28(8):2455-2474. doi:10.1177/0962280218784726",
            "Steyerberg EW et al. J Clin Epidemiol 2001;54(8):774-781. doi:10.1016/S0895-4356(01)00341-9",
            "Collins GS et al. Ann Intern Med 2015;162(1):55-63. doi:10.7326/M14-0697",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2))

    print(f"  n eval = {len(y)}, denied = {int(y.sum())}, EPV = {int(y.sum())/len(flags):.2f}")
    print(f"  Selected ridge inverse-strength C = {selected_C:.4f} (smaller = stronger shrinkage)")
    print(f"  AUC apparent  = {apparent_auc:.4f}")
    print(f"  AUC corrected = {auc_corrected:.4f}  (95% CI [{auc_lo:.4f}, {auc_hi:.4f}], bootstrap test-on-original)")
    print(f"  Youden J (apparent) = {youden[opt_idx]:.4f} at threshold {threshold:.4f}")
    a = multivar_apparent
    c = multivar_corrected
    print(f"  At Youden threshold:")
    print(f"    sens     apparent {a['sensitivity']*100:5.1f}%  corrected {c['sensitivity']*100:5.1f}%")
    print(f"    spec     apparent {a['specificity']*100:5.1f}%  corrected {c['specificity']*100:5.1f}%")
    print(f"    PPV      apparent {a['ppv']*100:5.1f}%  corrected {c['ppv']*100:5.1f}%")
    print(f"    NPV      apparent {a['npv']*100:5.1f}%  corrected {c['npv']*100:5.1f}%")
    print(f"    LR+      apparent {a['lr_pos']:5.2f}   corrected {c['lr_pos']:5.2f}")
    print(f"    LR-      apparent {a['lr_neg']:5.2f}   corrected {c['lr_neg']:5.2f}")
    print(f"    DOR      apparent {a['dor']:5.1f}    corrected {c['dor']:5.1f}")
    print(f"  Top 3 penalised log-odds coefficients:")
    for name, ci in coefs[:3]:
        print(f"    {name}: {ci:+.3f}")
    print(f"Saved → {OUTPUT}")


if __name__ == "__main__":
    main()
