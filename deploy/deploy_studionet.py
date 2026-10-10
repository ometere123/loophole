#!/usr/bin/env python3
"""Guarded, resumable deployment for exactly Studionet 61999.

The script never creates wallets, prints secrets, or treats ACCEPTED as execution
success. It writes only the ignored local manifest when a real transaction exists.
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
ADDR = re.compile(r"(?:Contract Address|contract_address)\s*[:=]\s*['\"]?(0x[0-9a-fA-F]{40})", re.I)
TX = re.compile(r'(?:Transaction Hash|Deployment Transaction Hash|Write Transaction Hash)\s*:\s*(0x[0-9a-fA-F]{64})', re.I)


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
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / 'contracts').glob('*.py'))}


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


def deploy_contract(path: str, args: list[str]) -> tuple[str, str]:
    output = run(['deploy', '--contract', path, *(['--args', *args] if args else [])])
    tx_hash = parse_tx(output)
    receipt_output = finalized_success(tx_hash)
    return parse_address(output + '\n' + receipt_output), tx_hash


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--confirm-chain', default='')
    parser.add_argument('--manifest', default='deployments.local.json')
    parser.add_argument('--resume-judge-address', default='')
    parser.add_argument('--resume-judge-tx', default='')
    parser.add_argument('--resume-vault-address', default='')
    parser.add_argument('--resume-vault-tx', default='')
    args = parser.parse_args()
    print(f'LOOPHOLE deployment preflight: Studionet {CHAIN_ID} ({RPC})')
    version, account = verify_environment()
    manifest_path = ROOT / args.manifest
    if not args.execute or args.confirm_chain != CHAIN_ID:
        print('DRY RUN ONLY: environment, CLI version, network, active wallet and source inputs verified.')
        print('Add --execute --confirm-chain 61999 only when you intend to sign deployment transactions.')
        return

    manifest = {'network': 'studionet', 'chain_id': int(CHAIN_ID), 'rpc': RPC,
                'explorer': EXPLORER, 'cli_version': version, 'account_output': account,
                'source_sha256': source_hashes(), 'finality_verified': False,
                'economic_lifecycle_verified': False}
    if bool(args.resume_judge_address) != bool(args.resume_judge_tx):
        raise RuntimeError('Resume requires both the real judge address and its real deployment transaction.')
    if bool(args.resume_vault_address) != bool(args.resume_vault_tx):
        raise RuntimeError('Resume requires both the real vault address and its real deployment transaction.')
    if args.resume_judge_address and args.resume_judge_tx:
        finalized_success(args.resume_judge_tx)
        judge, judge_tx = args.resume_judge_address, args.resume_judge_tx
    else:
        judge, judge_tx = deploy_contract('contracts/GapJudge.py', [])
    manifest.update({'judge': judge, 'judge_deploy_tx': judge_tx,
                     'judge_deploy_explorer': f'{EXPLORER}/tx/{judge_tx}'})
    write_manifest(manifest_path, manifest)
    if args.resume_vault_address and args.resume_vault_tx:
        finalized_success(args.resume_vault_tx)
        vault, vault_tx = args.resume_vault_address, args.resume_vault_tx
    else:
        vault, vault_tx = deploy_contract('contracts/RuleVault.py', [judge])
    manifest.update({'vault': vault, 'vault_deploy_tx': vault_tx,
                     'vault_deploy_explorer': f'{EXPLORER}/tx/{vault_tx}'})
    write_manifest(manifest_path, manifest)
    bind_output = run(['write', judge, 'bind_vault', '--args', vault])
    bind_tx = parse_tx(bind_output)
    finalized_success(bind_tx)
    manifest.update({'bind_tx': bind_tx, 'bind_explorer': f'{EXPLORER}/tx/{bind_tx}'})
    judge_config = run(['call', judge, 'get_configuration'])
    vault_config = run(['call', vault, 'get_config'])
    if vault.lower() not in judge_config.lower() or judge.lower() not in vault_config.lower():
        raise RuntimeError('Reciprocal judge/vault binding was not verified by finalized reads.')
    manifest.update({'binding_verified': True, 'judge_configuration': judge_config,
                     'vault_configuration': vault_config, 'finality_verified': True})
    write_manifest(manifest_path, manifest)
    print(f'Verified deployment manifest written to {manifest_path}')
    print(f'NEXT_PUBLIC_RULE_VAULT_ADDRESS={vault}')
    print(f'NEXT_PUBLIC_GAP_JUDGE_ADDRESS={judge}')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError) as error:
        print(f'DEPLOYMENT BLOCKED: {error}', file=sys.stderr)
        sys.exit(1)
