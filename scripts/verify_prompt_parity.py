#!/usr/bin/env python3
"""Verify that the diagnostic workload uses the exact production prompt bytes."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT = re.compile(r"exec_prompt\('''(?P<prompt>.*?)''' \+ evidence", re.DOTALL)


def extract(path: Path) -> str:
    match = PROMPT.search(path.read_text(encoding="utf-8"))
    if not match:
        raise SystemExit(f"missing assessment prompt: {path}")
    return match.group("prompt")


def main() -> int:
    production = extract(ROOT / "contracts" / "Loophole.py")
    diagnostic = extract(ROOT / "diagnostics" / "DirectGapJudgeWorkloadProbe.py")
    if production != diagnostic:
        print("PROMPT PARITY: FAIL")
        for index, (left, right) in enumerate(zip(production, diagnostic)):
            if left != right:
                print(f"first difference at byte {index}: production={left!r} diagnostic={right!r}")
                break
        else:
            print(f"length differs: production={len(production)} diagnostic={len(diagnostic)}")
        return 1
    print(f"PROMPT PARITY: PASS ({len(production.encode('utf-8'))} UTF-8 bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
