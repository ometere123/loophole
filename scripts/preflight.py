#!/usr/bin/env python3
"""Offline source and packaging verification. No wallet, RPC or silent mutations."""
from pathlib import Path
import os
import re,json,hashlib,sys
root=Path(__file__).resolve().parents[1]
errors=[]
contracts=list((root/'contracts').glob('*.py'))
if len(contracts)!=2: errors.append(f'Expected exactly two contracts; found {len(contracts)}')
for p in contracts:
    source=p.read_text(encoding='utf-8')
    if not source.startswith('# { "Depends": "py-genlayer:'): errors.append(f'{p.name}: missing GenVM pin')
    if 'from genlayer import *' not in source: errors.append(f'{p.name}: missing SDK')
    print(f'  {p.name}: {hashlib.sha256(p.read_bytes()).hexdigest()}')
if not (root/'contracts/GapJudge.py').exists() or not (root/'contracts/RuleVault.py').exists(): errors.append('Missing critical contract')
s=(root/'contracts/RuleVault.py').read_text()
j=(root/'contracts/GapJudge.py').read_text()
for method in ('create_challenge','commit_attempt','reveal_attempt','start_review','record_verdict','refund_unwon','recover_stalled_review','settle_remaining_bond','withdraw'):
    if f'def {method}(' not in s:errors.append(f'Missing vault method: {method}')
for method in ('adjudicate','bind_vault'):
    if f'def {method}(' not in j:errors.append(f'Missing judge method: {method}')
if 'run_nondet_unsafe(assess, independently_verify)' not in j:errors.append('Missing independent substantive validator')
if "emit(on='finalized')" not in s or "emit(on='finalized')" not in j:errors.append('Missing finalized IC message')
if 'genlayer-js' not in (root/'frontend/package.json').read_text(): errors.append('Missing GenLayerJS')
if json.loads((root/'package.json').read_text())['devDependencies']['genlayer']!='0.39.1':errors.append('Incorrect CLI pin')
if 'window.ethereum' not in (root/'frontend/src/lib/genlayer.ts').read_text():errors.append('Missing injected wallet')
for path in ('frontend/src/app/page.tsx','frontend/src/app/create/page.tsx','frontend/src/app/profile/page.tsx','frontend/src/app/challenge/[id]/page.tsx','frontend/src/app/globals.css'):
    if not (root/path).exists():errors.append(f'Missing frontend {path}')
for directory in (root/'frontend',):
    for current, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ('node_modules', '.next')]
        for name in files:
            path = Path(current) / name
            if path.suffix in ('.ts', '.tsx'):
                text=path.read_text(encoding='utf-8')
                if 'WalletConnect' in text or 'MetaMask Snap' in text:errors.append(f'Forbidden wallet approach: {path}')
print('PREFLIGHT:', 'PASS' if not errors else 'FAIL')
for error in errors: print('  ERROR:',error)
if errors:sys.exit(1)
