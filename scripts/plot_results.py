from __future__ import annotations

"""Строит графики по ``results/summary.csv`` (после ``score_metrics.py``)."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results" / "summary.csv"
PLOTS = ROOT / "results" / "plots"
PLOTS.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(
    {
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "figure.facecolor": "white",
        "axes.facecolor": "#fafafa",
        "axes.grid": True,
        "grid.alpha": 0.35,
    }
)


def _short_fw(name: str) -> str:
    return (
        name.replace("promptfoo_", "pf_")
        .replace("garak_baseline", "garak")
        .replace("hivetrace_red", "hivetrace")
    )


if not INPUT.exists():
    raise SystemExit("Сначала запусти: python scripts/score_metrics.py")

df = pd.read_csv(INPUT)
df["framework_short"] = df["framework"].map(_short_fw)
tasks = list(df["task"].unique())
frameworks = list(df["framework_short"].unique())
x = np.arange(len(tasks))
width = min(0.22, 0.8 / max(len(frameworks), 1))


def grouped_bar(metric: str, title: str, filename: str) -> None:
    pivot = df.pivot(index="framework_short", columns="task", values=metric).reindex(
        columns=tasks
    )
    pivot = pivot.fillna(0)

    fig, ax = plt.subplots(figsize=(9, 5))
    for i, fw in enumerate(pivot.index):
        offset = width * (i - (len(pivot.index) - 1) / 2)
        vals = [pivot.loc[fw, t] if t in pivot.columns else 0 for t in tasks]
        ax.bar(x + offset, vals, width, label=fw)

    ax.set_xticks(x)
    ax.set_xticklabels(tasks, rotation=0)
    ax.set_ylabel(metric.replace("_", " "))
    ax.set_title(title)
    if metric == "kappa":
        ax.set_ylim(-1.05, 1.05)
    else:
        ax.set_ylim(0, 1.05)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.28), ncol=3, fontsize=8)
    plt.tight_layout()
    out_path = PLOTS / filename
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"saved -> {out_path}")


for metric, title in [
    ("f1", "F1 (binary, positive class = failure/unsafe)"),
    ("precision", "Precision"),
    ("recall", "Recall"),
    ("balanced_accuracy", "Balanced accuracy"),
    ("kappa", "Cohen's kappa vs gold"),
]:
    grouped_bar(metric, title, f"{metric}_by_task.png")

# Сводная сетка: F1 по всем task одним файлом
p_f1 = df.pivot(index="framework_short", columns="task", values="f1").fillna(0)
fig, ax = plt.subplots(figsize=(7.5, max(3.5, 0.45 * len(p_f1.index))))
im = ax.imshow(p_f1.values, aspect="auto", cmap="YlGn", vmin=0, vmax=1)
ax.set_xticks(range(len(p_f1.columns)))
ax.set_xticklabels(p_f1.columns, rotation=25, ha="right")
ax.set_yticks(range(len(p_f1.index)))
ax.set_yticklabels(p_f1.index)
ax.set_title("F1 heatmap (framework × task)")
for yi in range(len(p_f1.index)):
    for xi in range(len(p_f1.columns)):
        v = p_f1.values[yi, xi]
        ax.text(xi, yi, f"{v:.2f}", ha="center", va="center", color="black", fontsize=8)
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="F1")
plt.tight_layout()
heat_path = PLOTS / "f1_heatmap.png"
plt.savefig(heat_path, dpi=200, bbox_inches="tight")
plt.close()
print(f"saved -> {heat_path}")
