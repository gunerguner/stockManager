#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON="${ROOT}/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="python3"
fi

echo "==> backend pytest"
"$PYTHON" -m pytest

echo "==> frontend jest"
(cd "${ROOT}/stockManager/front" && ut run test)
