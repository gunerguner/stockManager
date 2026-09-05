#!/usr/bin/env python3
"""Cursor stop hook: 工作树有业务/测试改动时跑全量测试。"""
from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PREFIXES = (
    "stockManager/backend/",
    "stockManager/front/src/",
    "stockManager/front/tests/",
    "stockManager/tests/",
)


def emit(payload: dict) -> None:
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")


def hook_input() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def dirty_code_paths() -> bool:
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
    for line in status.splitlines():
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if any(path.startswith(prefix) for prefix in PREFIXES):
            return True
    return False


def main() -> None:
    payload = hook_input()
    if payload.get("status") != "completed":
        emit({})
        return
    if os.path.exists(os.path.join(ROOT, ".cursor", "skip-test-loop")):
        emit({})
        return
    if not dirty_code_paths():
        emit({})
        return

    proc = subprocess.run(
        ["bash", os.path.join(ROOT, "scripts", "test.sh")],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode == 0:
        emit({})
        return

    log = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()[-4000:]
    emit(
        {
            "followup_message": (
                "Stop hook: ./scripts/test.sh failed after your code changes. "
                "Read the failures, fix the root cause, then stop. "
                "To skip this loop once, create `.cursor/skip-test-loop` (do not commit it).\n\n"
                "----- test output -----\n"
                f"{log}"
            )
        }
    )


if __name__ == "__main__":
    main()
