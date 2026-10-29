#!/usr/bin/env python3
"""Offline integrity checks for the not-yet-deployed LOOPHOLE V2 source."""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'contracts' / 'LoopholeV2.py'
REQUIRED_METHODS = (
    'propose_repair', 'start_repair_review', 'adjudicate_repair',
    'recover_stalled_repair', 'create_rechallenge', 'get_policy_version',
    'get_policy_history', 'get_repair_proposal', 'get_repair_adjudication',
    'get_audit_history',
)


def main() -> int:
    errors: list[str] = []
    if not SOURCE.exists():
        errors.append('missing contracts/LoopholeV2.py')
    else:
        source = SOURCE.read_text(encoding='utf-8')
        try:
            tree = ast.parse(source, filename=str(SOURCE))
        except SyntaxError as exc:
            errors.append(f'V2 is not valid Python: {exc}')
            tree = None
        if not source.startswith('# { "Depends": "py-genlayer:'):
            errors.append('V2 Depends header is not the first line')
        if 'class LoopholeV2(gl.Contract)' not in source:
            errors.append('V2 class declaration is missing')
        for method in REQUIRED_METHODS:
            if f'def {method}(' not in source:
                errors.append(f'missing V2 method: {method}')
        for marker in (
            'FINDING_PROVEN', 'FINDING_DISPROVEN', 'FINDING_UNKNOWN',
            'run_nondet_unsafe(assess, independently_verify)',
            "fields = ('verdict', 'closure', 'goal', 'coherence', 'evidence_state')",
            'MAX_POLICY_VERSIONS', 'REPAIR_TIMEOUT', 'content_commitment',
            'active_repair_proposal', 'authoritative_version',
        ):
            if marker not in source:
                errors.append(f'missing V2 safety marker: {marker}')
        if 'get_contract_at' in source or "emit(on='finalized')" in source:
            errors.append('V2 must not introduce an unverified callback dependency')
        if tree is not None:
            classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'LoopholeV2']
            if len(classes) != 1:
                errors.append('expected exactly one LoopholeV2 class')
        print(f'V2 source SHA-256: {hashlib.sha256(SOURCE.read_bytes()).hexdigest()}')
    if errors:
        print('V2 SOURCE INTEGRITY: FAIL')
        for error in errors:
            print(f'  ERROR: {error}')
        return 1
    print('V2 SOURCE INTEGRITY: PASS (deployment intentionally not asserted)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
