#!/usr/bin/env node

const RPC = process.env.LOOPHOLE_RPC ?? 'https://studio.genlayer.com/api';
const VAULT = '0xa77A29C96c30B2A5dB865a2CE35c8F396d504F26'.toLowerCase();
const CHAIN_ID = '0xf22f';
const DELIVERY_STATES = Object.freeze({
  CLAIMABLE: 'CLAIMABLE',
  TRANSFER_SUBMITTED: 'TRANSFER SUBMITTED',
  PARENT_FINALIZED: 'PARENT FINALIZED',
  DELIVERY_VERIFIED: 'DELIVERY VERIFIED',
  FAILED: 'FAILED',
  UNRESOLVED: 'UNRESOLVED',
});

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

function executionSucceeded(tx) {
  const leader = tx?.consensus_data?.leader_receipt?.[0] ?? tx?.leader_receipt?.[0];
  return leader?.execution_result === 'SUCCESS' &&
    (leader?.result === 'AAA=' || leader?.result?.status === 'return');
}

function final(tx) { return String(tx?.status ?? '').toUpperCase() === 'FINALIZED'; }
function terminalFailure(tx) {
  const status = String(tx?.status ?? '').toUpperCase();
  return ['CANCELED', 'CANCELLED', 'FAILED', 'REVERTED'].includes(status) ||
    (final(tx) && tx?.consensus_data && executionSucceeded(tx) === false);
}
function childIsExactMatch(child, beneficiary, amountWei) {
  return child?.from_address?.toLowerCase() === VAULT &&
    child?.to_address?.toLowerCase() === beneficiary.toLowerCase() &&
    String(child?.value ?? '') === amountWei;
}

const result = {
  chain_id: null,
  parent_hash: parentHash,
  beneficiary: beneficiary.toLowerCase(),
  amount_wei: amountWei,
  status: DELIVERY_STATES.UNRESOLVED,
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
  } else if (final(parent) && executionSucceeded(parent) === false && parent.consensus_data) {
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
    record.exact_origin_recipient_value = childIsExactMatch(child, beneficiary, amountWei);
    record.execution_succeeded = child ? executionSucceeded(child) : false;
    record.finalized = child ? final(child) : false;
    record.authoritative_credit = child?.value_credited === true;
    record.failed = child ? terminalFailure(child) : false;
    record.matches = record.exact_origin_recipient_value && record.finalized &&
      record.execution_succeeded && record.authoritative_credit;
    result.children.push(record);
  }

  if (!parent) {
    result.status = DELIVERY_STATES.UNRESOLVED;
    result.reasons.push('parent transaction is unavailable');
  } else if (terminalFailure(parent)) {
    result.status = DELIVERY_STATES.FAILED;
    result.reasons.push('parent transaction failed or finalized without successful execution');
  } else if (!final(parent)) {
    result.status = DELIVERY_STATES.TRANSFER_SUBMITTED;
    result.reasons.push(`parent status is ${parent.status ?? 'unknown'}`);
  } else if (result.children.some((child) => child.matches)) {
    result.status = DELIVERY_STATES.DELIVERY_VERIFIED;
  } else if (result.children.some((child) => child.exact_origin_recipient_value && child.failed)) {
    result.status = DELIVERY_STATES.FAILED;
    result.reasons.push('matching child transfer failed or finalized without successful execution');
  } else if (result.children.some((child) => child.exact_origin_recipient_value && !child.finalized)) {
    result.status = DELIVERY_STATES.TRANSFER_SUBMITTED;
    result.reasons.push('matching child transfer is not finalized');
  } else if (!result.children.length) {
    result.status = DELIVERY_STATES.PARENT_FINALIZED;
    result.reasons.push('parent finalized, but no external child transfer is visible yet');
  } else {
    result.status = DELIVERY_STATES.UNRESOLVED;
    result.reasons.push('child transactions exist, but none matched the vault, beneficiary, amount, finality, and authoritative credit evidence');
  }
  console.log(JSON.stringify(result, null, 2));
  process.exit(result.status === DELIVERY_STATES.DELIVERY_VERIFIED ? 0 : 1);
} catch (error) {
  result.reasons.push(error instanceof Error ? error.message : String(error));
  console.log(JSON.stringify(result, null, 2));
  process.exit(1);
}
