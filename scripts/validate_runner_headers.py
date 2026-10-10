"""Fail fast when a contract's GenVM Depends header is not the first comment."""

from __future__ import annotations

import re
import sys
from pathlib import Path


HEADER = re.compile(r'^# \{ "Depends": "[^:]+:[^"]+" \}$')


def main() -> int:
    paths = [Path(arg) for arg in sys.argv[1:]]
    if not paths:
        paths = sorted(Path("contracts").glob("*.py")) + [Path("diagnostics/AdjudicationProbe.py")]
    errors: list[str] = []
    for path in paths:
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines or not HEADER.fullmatch(lines[0]):
            errors.append(f"{path}: first line must be the GenVM Depends header")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"RUNNER HEADERS: PASS ({len(paths)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
