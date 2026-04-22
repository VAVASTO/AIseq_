#!/usr/bin/env bash
# Run all three Promptfoo judge stacks. Requires:
#   - Node.js + npx
#   - mock target on :8000 (make run-mock or uvicorn)
#   - .env with XAI_API_KEY (and optional XAI_BASE_URL / XAI_MODEL)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

mkdir -p outputs/promptfoo

if ! command -v promptfoo >/dev/null 2>&1 && ! command -v npx >/dev/null 2>&1; then
  echo "promptfoo/npx not found — running Python xAI judge compat (see scripts/run_xai_judge_promptfoo_compat.py)."
  "${ROOT}/.venv/bin/python" "${ROOT}/scripts/run_xai_judge_promptfoo_compat.py"
  exit 0
fi

run_one() {
  local name="$1"
  local cfg="$2"
  echo "=== promptfoo: ${name} ==="
  if command -v promptfoo >/dev/null 2>&1; then
    promptfoo eval -c "$cfg" --output "outputs/promptfoo/${name}.json"
  else
    npx --yes promptfoo@latest eval -c "$cfg" --output "outputs/promptfoo/${name}.json"
  fi
}

run_one llm_rubric configs/promptfoo_llm_rubric.yaml
run_one geval configs/promptfoo_geval.yaml
run_one closedqa configs/promptfoo_closedqa.yaml

echo "Done. Outputs under outputs/promptfoo/"
