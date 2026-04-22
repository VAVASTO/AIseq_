from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
OUT: list[dict[str, Any]] = []


def add_row(case_id: str, framework: str, pred_label: int, task: str, gold_label: int) -> None:
    OUT.append(
        {
            "id": case_id,
            "framework": framework,
            "task": task,
            "gold_label": int(gold_label),
            "pred_label": int(pred_label),
        }
    )


# Promptfoo JSON outputs
for name in ["llm_rubric", "geval", "closedqa"]:
    pf_path = ROOT / "outputs" / "promptfoo" / f"{name}.json"
    if not pf_path.exists():
        continue

    data = json.loads(pf_path.read_text(encoding="utf-8"))
    for row in data.get("results", []):
        vars_ = row.get("vars", {})
        grading = row.get("gradingResult", {})
        case_id = vars_.get("id")
        task = vars_.get("task")
        gold = int(vars_.get("gold_label", 0))

        # Convention for this project:
        # pred_label = 1 means judge says failure/unsafe/broken.
        if "pass" in grading:
            pred = 0 if bool(grading["pass"]) else 1
        elif "score" in grading:
            pred = 0 if float(grading["score"]) >= 1 else 1
        else:
            continue

        add_row(case_id, f"promptfoo_{name}", pred, task, gold)


# garak baseline CSV
for garak_name in ["results.csv"]:
    garak_path = ROOT / "outputs" / "garak" / garak_name
    if garak_path.exists():
        df = pd.read_csv(garak_path)
        OUT.extend(df[["id", "framework", "task", "gold_label", "pred_label"]].to_dict(orient="records"))


# HiveTrace CSV normalization placeholder
hive_path = ROOT / "outputs" / "hivetrace" / "results.csv"
if hive_path.exists():
    hive = pd.read_csv(hive_path)
    required = {"id", "task", "gold_label", "pred_label"}
    if required.issubset(set(hive.columns)):
        hive = hive.copy()
        hive["framework"] = "hivetrace_red"
        OUT.extend(hive[["id", "framework", "task", "gold_label", "pred_label"]].to_dict(orient="records"))


# LLAMATOR CSV normalization placeholder
ll_path = ROOT / "outputs" / "llamator" / "results.csv"
if ll_path.exists():
    ll = pd.read_csv(ll_path)
    required = {"id", "task", "gold_label", "pred_label"}
    if required.issubset(set(ll.columns)):
        ll = ll.copy()
        ll["framework"] = "llamator"
        OUT.extend(ll[["id", "framework", "task", "gold_label", "pred_label"]].to_dict(orient="records"))


normalized = pd.DataFrame(OUT)
if normalized.empty:
    raise SystemExit("No results found. Run at least one framework first.")

normalized.to_csv(RESULTS_DIR / "normalized_results.csv", index=False)
print(f"saved -> {RESULTS_DIR / 'normalized_results.csv'}")
