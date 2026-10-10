#!/usr/bin/env node

const RPC = process.env.LOOPHOLE_RPC ?? 'https://studio.genlayer.com/api';
const VAULT = '0xa77A29C96c30B2A5dB865a2CE35c8F396d504F26'.toLowerCase();
const CHAIN_ID = '0xf22f';

function usage() {
  console.error('Usage: node scripts/verify_delivery.mjs <withdrawal-parent-hash> <beneficiary> <amount-wei>');
  process.exit(2);
}

const [, , parentHash, beneficiary, amountWei] = process.argv;
if (!parentHash || !/^0x[0-9a-fA-F]{64}$/.test(parentHash) ||
    !beneficiary || !/^0x[0-9a-fA-F]{40}$/.test(beneficiary) ||
    !amountWei || !/^\d+$/.test(amountWei)) usage();

let nextId = 1;
async function rpc(method, params) {
  const response = await fetch(RPC, {
    method: 'POST',
    headers: {'content-type': 'application/json'},
    body: JSON.stringify({jsonrpc: '2.0', id: nextId++, method, params}),
  });
  if (!response.ok) throw new Error(`RPC HTTP ${response.status}`);
  const body = await response.json();
  if (body.error) throw new Error(`${method}: ${body.error.message}`);
  return body.result;
}

function parentExecutionSucceeded(tx) {
  const leader = tx?.consensus_data?.leader_receipt?.[0] ?? tx?.leader_receipt?.[0];
  return leader?.execution_result === 'SUCCESS' &&
    (leader?.result === 'AAA=' || leader?.result?.status === 'return');
}

function final(tx) { return String(tx?.status ?? '').toUpperCase() === 'FINALIZED'; }

const result = {
  chain_id: null,
  parent_hash: parentHash,
  beneficiary: beneficiary.toLowerCase(),
  amount_wei: amountWei,
  status: 'UNRESOLVED',
  reasons: [],
  children: [],
};

try {
  result.chain_id = await rpc('eth_chainId', []);
  if (result.chain_id !== CHAIN_ID) {
    result.reasons.push(`wrong chain: expected ${CHAIN_ID}, got ${result.chain_id}`);
    console.log(JSON.stringify(result, null, 2));
    process.exit(1);
  }

  const parent = await rpc('eth_getTransactionByHash', [parentHash]);
  if (!parent) {
    result.reasons.push('parent transaction not found');
  } else if (parent.to_address?.toLowerCase() !== VAULT) {
    result.reasons.push('parent destination is not the canonical RuleVault');
  } else if (!final(parent)) {
    result.reasons.push(`parent status is ${parent.status ?? 'unknown'}`);
  } else if (parentExecutionSucceeded(parent) === false && parent.consensus_data) {
    result.reasons.push('parent finalized without successful leader return evidence');
  }

  const childIds = parent?.triggered_transactions ?? [];
  for (const childHash of childIds) {
    const child = await rpc('eth_getTransactionByHash', [childHash]);
    const record = {
      hash: childHash,
      from: child?.from_address?.toLowerCase() ?? null,
      to: child?.to_address?.toLowerCase() ?? null,
      value_wei: String(child?.value ?? ''),
      status: child?.status ?? null,
      value_credited: child?.value_credited ?? null,
      matches: false,
    };
    record.matches = record.from === VAULT &&
      record.to === beneficiary.toLowerCase() &&
      record.value_wei === amountWei &&
      final(child) && child.value_credited === true;
    result.children.push(record);
  }

  if (!parent || result.reasons.length || !result.children.some((child) => child.matches)) {
    if (!result.children.length) result.reasons.push('no triggered child transfer found');
    else if (!result.children.some((child) => child.matches)) result.reasons.push('no child matched vault, beneficiary, amount, finality, and value_credited');
  } else {
    result.status = 'DELIVERY VERIFIED';
  }
  console.log(JSON.stringify(result, null, 2));
  process.exit(result.status === 'DELIVERY VERIFIED' ? 0 : 1);
} catch (error) {
  result.reasons.push(error instanceof Error ? error.message : String(error));
  console.log(JSON.stringify(result, null, 2));
  process.exit(1);
}
