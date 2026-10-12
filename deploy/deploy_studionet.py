#!/usr/bin/env python3
"""Guarded deployment for the single Loophole contract on Studionet 61999.

This script never touches the historical RuleVault/GapJudge deployments. It
never creates wallets, prints secrets, or treats ACCEPTED as execution success.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
CLI = ROOT / 'node_modules' / '.bin' / ('genlayer.cmd' if os.name == 'nt' else 'genlayer')
RPC = 'https://studio.genlayer.com/api'
CHAIN_ID = '61999'
EXPLORER = 'https://explorer-studio.genlayer.com'
TX = re.compile(r'(?:Transaction Hash|Deployment Transaction Hash|Write Transaction Hash)\s*:\s*(0x[0-9a-fA-F]{64})', re.I)
ADDR = re.compile(r'(?:Contract Address|contract_address)\s*[:=]\s*[\'\"]?(0x[0-9a-fA-F]{40})', re.I)


def run(args: list[str]) -> str:
    completed = subprocess.run([str(CLI), *args], cwd=ROOT, capture_output=True,
                               text=True, encoding='utf-8', errors='replace')
    output = completed.stdout + '\n' + completed.stderr
    print(output)
    if completed.returncode:
        raise RuntimeError('CLI command failed: ' + ' '.join(args))
    return output


def parse_tx(output: str) -> str:
    match = TX.search(output)
    if not match:
        raise RuntimeError('No transaction hash was returned; inspect CLI output before retrying.')
    return match.group(1)


def parse_address(output: str) -> str:
    match = ADDR.search(output)
    if not match:
        raise RuntimeError('No contract address was returned; inspect the finalized receipt before retrying.')
    return match.group(1)


def finalized_success(tx_hash: str) -> str:
    output = run(['receipt', tx_hash, '--status', 'FINALIZED', '--retries', '120', '--interval', '5000'])
    success = 'FINISHED_WITH_RETURN' in output or "execution_result: 'SUCCESS'" in output
    if not success:
        if 'FINISHED_WITH_ERROR' in output or 'NOT_VOTED' in output or "execution_result: 'ERROR'" in output:
            raise RuntimeError(f'{tx_hash} finalized without successful contract execution.')
        raise RuntimeError(f'{tx_hash} did not expose a verified successful execution result.')
    return output


def source_hashes() -> dict[str, str]:
    paths = [ROOT / 'contracts' / 'Loophole.py',
             ROOT / 'contracts' / 'historical' / 'RuleVault.py',
             ROOT / 'contracts' / 'historical' / 'GapJudge.py']
    return {str(path.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths}


def verify_environment() -> tuple[str, str]:
    if not CLI.exists():
        raise RuntimeError('Repository-local CLI is missing. Run npm ci first; no global fallback is allowed.')
    version = run(['--version']).strip()
    if '0.39.1' not in version:
        raise RuntimeError('Refusing to deploy without repository-local GenLayer CLI 0.39.1.')
    info = run(['network', 'info'])
    if "chainId: '61999'" not in info or "rpc: 'https://studio.genlayer.com/api'" not in info:
        raise RuntimeError('Effective CLI network is not exactly Studionet 61999 at the required RPC.')
    account = run(['account', 'show'])
    if 'active: true' not in account or 'address:' not in account:
        raise RuntimeError('No active CLI wallet was confirmed.')
    return version, account


def write_manifest(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--confirm-chain', default='')
    parser.add_argument('--manifest', default='deployments.local.json')
    args = parser.parse_args()

    print(f'LOOPHOLE deployment preflight: Studionet {CHAIN_ID} ({RPC})')
    version, account = verify_environment()
    manifest_path = ROOT / args.manifest
    if not args.execute or args.confirm_chain != CHAIN_ID:
        print('DRY RUN ONLY: environment, CLI version, network, active wallet and source inputs verified.')
        print('Add --execute --confirm-chain 61999 only when you intend to sign one deployment transaction.')
        return

    output = run(['deploy', '--contract', 'contracts/Loophole.py'])
    deploy_tx = parse_tx(output)
    receipt = finalized_success(deploy_tx)
    address = parse_address(output + '\n' + receipt)
    config = run(['call', address, 'get_config'])
    if 'Loophole' not in config or 'DIRECT_ATOMIC' not in config or "'61999'" not in config:
        raise RuntimeError('Deployed Loophole configuration did not prove the expected chain or mode.')

    manifest = {
        'network': 'studionet', 'chain_id': int(CHAIN_ID), 'rpc': RPC,
        'explorer': EXPLORER, 'cli_version': version,
        'account_output': account, 'contract': 'Loophole', 'address': address,
        'deploy_tx': deploy_tx, 'deploy_explorer': f'{EXPLORER}/tx/{deploy_tx}',
        'source_sha256': source_hashes(), 'deployment_receipt': receipt,
        'configuration': config, 'finality_verified': True,
        'economic_lifecycle_verified': False,
        'historical_deployments': {
            'gapjudge': '0xb14B08cd35Fa64FE795e14931DdA09999627785d',
            'rulevault': '0xa77A29C96c30B2A5dB865a2CE35c8F396d504F26',
        },
    }
    write_manifest(manifest_path, manifest)
    print(f'Verified deployment manifest written to {manifest_path}')
    print(f'NEXT_PUBLIC_LOOPHOLE_ADDRESS={address}')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError) as error:
        print(f'DEPLOYMENT BLOCKED: {error}', file=sys.stderr)
        sys.exit(1)
