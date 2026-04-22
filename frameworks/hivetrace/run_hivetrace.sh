#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT_DIR"

echo "[INFO] Running HiveTrace Red with configs/hivetrace.yaml"
echo "[INFO] Make sure hivetracered CLI is installed and available in PATH"

hivetracered --config configs/hivetrace.yaml
