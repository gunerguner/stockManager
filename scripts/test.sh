#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

usage() {
  echo "usage: ./scripts/test.sh [--if-dirty]" >&2
  exit 2
}

IF_DIRTY=0
if [[ $# -gt 1 ]]; then
  usage
fi
case "${1:-}" in
  "") ;;
  --if-dirty) IF_DIRTY=1 ;;
  *) usage ;;
esac

code_dirty() {
  local line path status
  status="$(git status --porcelain)"
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    path="${line:3}"
    if [[ "$path" == *" -> "* ]]; then
      path="${path##* -> }"
    fi
    case "$path" in
      stockManager/backend/*|stockManager/front/src/*|stockManager/front/tests/*|stockManager/tests/*)
        return 0
        ;;
    esac
  done <<< "$status"
  return 1
}

if [[ "$IF_DIRTY" -eq 1 ]]; then
  if [[ -e "${ROOT}/.agents/skip-test-loop" ]]; then
    echo "skip-test-loop present; not running tests"
    exit 0
  fi
  if ! code_dirty; then
    echo "no backend/front/test changes; not running tests"
    exit 0
  fi
fi

PYTHON="${ROOT}/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="python3"
fi

echo "==> backend pytest"
"$PYTHON" -m pytest

echo "==> frontend jest"
(cd "${ROOT}/stockManager/front" && ut run test)
