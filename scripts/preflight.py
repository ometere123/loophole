#!/usr/bin/env python3
"""Offline source and packaging verification. No wallet, RPC or silent mutations."""
from pathlib import Path
import os
import re,json,hashlib,sys
root=Path(__file__).resolve().parents[1]
errors=[]
contracts=list((root/'contracts').glob('*.py'))
contract_names={p.name for p in contracts}
if contract_names != {'Loophole.py','LoopholeV2.py'}:
    errors.append(f'Expected the preserved V1 contract and versioned V2 contract; found {sorted(contract_names)}')
if not (root/'contracts/Loophole.py').exists(): errors.append('Missing Loophole.py')
if not (root/'contracts/historical/RuleVault.py').exists() or not (root/'contracts/historical/GapJudge.py').exists():
    errors.append('Missing historical production sources')
for p in contracts:
    source=p.read_text(encoding='utf-8')
    if not source.startswith('# { "Depends": "py-genlayer:'): errors.append(f'{p.name}: missing GenVM pin')
    if 'from genlayer import *' not in source: errors.append(f'{p.name}: missing SDK')
    print(f'  {p.name}: {hashlib.sha256(p.read_bytes()).hexdigest()}')
source=(root/'contracts/Loophole.py').read_text()
for method in ('create_challenge','create_source_challenge','commit_attempt','commit_source_attempt','reveal_attempt','reveal_source_attempt','start_review','adjudicate_review','finalize_invalid','appeal_invalid','refund_unwon','recover_stalled_review','settle_remaining_bond','withdraw'):
    if f'def {method}(' not in source:errors.append(f'Missing monolith method: {method}')
if 'run_nondet_unsafe(assess, independently_verify)' not in source:errors.append('Missing independent substantive validator')
if 'gl.nondet.web.get' not in source or 'MAX_SOURCE_BYTES' not in source:errors.append('Missing independent pinned-source retrieval')
if "fields = ('verdict', 'letter', 'purpose', 'feasible', 'evidence_state')" not in source:errors.append('Missing exact tri-state validator agreement')
if "get_contract_at" in source or "emit(on='finalized')" in source or 'record_verdict' in source:
    errors.append('Loophole.py must not depend on cross-contract callbacks')
if 'FINDING_PROVEN' not in source or 'FINDING_DISPROVEN' not in source or 'FINDING_UNKNOWN' not in source:
    errors.append('Missing tri-state substantive assessment rubric')
v2_source=(root/'contracts/LoopholeV2.py').read_text()
for method in ('propose_repair','start_repair_review','adjudicate_repair','recover_stalled_repair','create_rechallenge','get_policy_history','get_audit_history'):
    if f'def {method}(' not in v2_source: errors.append(f'Missing V2 policy-repair method: {method}')
if 'class LoopholeV2(gl.Contract)' not in v2_source or 'V2_VERSION' not in v2_source:
    errors.append('V2 contract is not clearly versioned')
if 'run_nondet_unsafe(assess, independently_verify)' not in v2_source:
    errors.append('V2 missing independent repair consensus')
if "fields = ('verdict', 'closure', 'goal', 'coherence', 'evidence_state')" not in v2_source:
    errors.append('V2 missing exact material repair-finding agreement')
if 'MAX_POLICY_VERSIONS' not in v2_source or 'MAX_REPAIR_TEXT' not in v2_source:
    errors.append('V2 missing bounded policy revision inputs')
if 'genlayer-js' not in (root/'frontend/package.json').read_text(): errors.append('Missing GenLayerJS')
if json.loads((root/'package.json').read_text())['devDependencies']['genlayer']!='0.39.1':errors.append('Incorrect CLI pin')
if 'window.ethereum' not in (root/'frontend/src/lib/genlayer.ts').read_text():errors.append('Missing injected wallet')
wallet_source=(root/'frontend/src/lib/genlayer.ts').read_text()
if "client.connect('studionet')" in wallet_source:errors.append('Wallet writes must not use the SDK extension connection helper')
if 'wallet_getSnaps' in wallet_source or 'wallet_requestSnaps' in wallet_source:errors.append('Unsupported wallet extension API in frontend')
for path in ('frontend/src/app/page.tsx','frontend/src/app/create/page.tsx','frontend/src/app/profile/page.tsx','frontend/src/app/challenge/[id]/page.tsx','frontend/src/app/globals.css'):
    if not (root/path).exists():errors.append(f'Missing frontend {path}')
for directory in (root/'frontend',):
    for current, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ('node_modules', '.next')]
        for name in files:
            path = Path(current) / name
            if path.suffix in ('.ts', '.tsx'):
                text=path.read_text(encoding='utf-8')
                if 'WalletConnect' in text or 'walletconnect' in text:errors.append(f'Forbidden non-injected wallet approach: {path}')
print('PREFLIGHT:', 'PASS' if not errors else 'FAIL')
for error in errors: print('  ERROR:',error)
if errors:sys.exit(1)
