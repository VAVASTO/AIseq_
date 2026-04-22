from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.metrics import balanced_accuracy_score, cohen_kappa_score, precision_recall_fscore_support

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results" / "normalized_results.csv"
OUT = ROOT / "results" / "summary.csv"

if not INPUT.exists():
    raise SystemExit("Run scripts/normalize_results.py first.")

df = pd.read_csv(INPUT)
rows = []

for (framework, task), part in df.groupby(["framework", "task"]):
    y_true = part["gold_label"].astype(int)
    y_pred = part["pred_label"].astype(int)

    p, r, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0
    )
    bacc = balanced_accuracy_score(y_true, y_pred)
    kappa = cohen_kappa_score(y_true, y_pred)

    rows.append(
        {
            "framework": framework,
            "task": task,
            "precision": round(float(p), 4),
            "recall": round(float(r), 4),
            "f1": round(float(f1), 4),
            "balanced_accuracy": round(float(bacc), 4),
            "kappa": round(float(kappa), 4),
            "n": len(part),
        }
    )

summary = pd.DataFrame(rows).sort_values(["task", "f1"], ascending=[True, False])
summary.to_csv(OUT, index=False)
print(summary)
print(f"saved -> {OUT}")
