"""Patient-level detection metrics. Validation thresholds must be selected before final test use."""
import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, confusion_matrix, roc_auc_score


def detection_metrics(labels, probabilities, threshold: float = 0.5) -> dict:
    y = np.asarray(labels, dtype=int)
    p = np.asarray(probabilities, dtype=float)
    if len(y) != len(p) or len(y) == 0 or not np.isin(y, [0, 1]).all() or not np.isfinite(p).all():
        raise ValueError("Invalid labels or probabilities")
    if ((p < 0) | (p > 1)).any():
        raise ValueError("Probabilities must be in [0, 1]")
    tn, fp, fn, tp = confusion_matrix(y, p >= threshold, labels=[0, 1]).ravel()
    return {
        "n": int(len(y)), "events": int(y.sum()), "prevalence": float(y.mean()),
        "auroc": float(roc_auc_score(y, p)) if len(set(y)) == 2 else None,
        "pr_auc": float(average_precision_score(y, p)) if y.sum() else None,
        "brier": float(brier_score_loss(y, p)), "threshold": threshold,
        "sensitivity": float(tp / (tp + fn)) if tp + fn else None,
        "specificity": float(tn / (tn + fp)) if tn + fp else None,
        "ppv": float(tp / (tp + fp)) if tp + fp else None,
        "npv": float(tn / (tn + fn)) if tn + fn else None,
    }
