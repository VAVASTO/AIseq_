from __future__ import annotations

"""Example helper for extending the benchmark.

This script duplicates starter cases with small variations so the team can
quickly bootstrap a larger benchmark. Replace synthetic rows with manual,
human-labeled examples before the final seminar.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "benchmark" / "cases.jsonl"
OUTPUT = ROOT / "benchmark" / "cases_expanded.jsonl"

rows = [json.loads(line) for line in INPUT.read_text(encoding="utf-8").splitlines() if line.strip()]
expanded = []

for i, row in enumerate(rows, start=1):
    expanded.append(row)
    clone = dict(row)
    clone["id"] = f"{row['id']}_aug"
    clone["user_prompt"] = row["user_prompt"] + " Please answer briefly."
    clone["gold_reason"] = row["gold_reason"] + " (augmented starter case)"
    expanded.append(clone)

with OUTPUT.open("w", encoding="utf-8") as f:
    for row in expanded:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

print(f"saved -> {OUTPUT}")
print(f"rows: {len(expanded)}")
