#!/usr/bin/env node

const RPC = process.env.LOOPHOLE_RPC ?? 'https://studio.genlayer.com/api';
const VAULT = (process.env.LOOPHOLE_ADDRESS ??
  process.env.RULE_VAULT_ADDRESS ??
  '0x7a5eC154FfA7c05DDe0Fbb1a34286d2eaDA3FBaf').toLowerCase();
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
class RpcError extends Error {
  constructor(message, {code = null, httpStatus = null} = {}) {
    super(message);
    this.name = 'RpcError';
    this.code = code;
    this.httpStatus = httpStatus;
  }
}

async function rpc(method, params) {
  let response;
  try {
    response = await fetch(RPC, {
      method: 'POST',
      headers: {'content-type': 'application/json'},
      body: JSON.stringify({jsonrpc: '2.0', id: nextId++, method, params}),
    });
  } catch (error) {
    throw new RpcError(`${method}: ${error instanceof Error ? error.message : String(error)}`);
  }
  if (!response.ok) throw new RpcError(`${method}: RPC HTTP ${response.status}`, {httpStatus: response.status});
  let body;
  try {
    body = await response.json();
  } catch (error) {
    throw new RpcError(`${method}: invalid JSON response`);
  }
  if (body.error) throw new RpcError(`${method}: ${body.error.message ?? 'RPC error'}`, {code: body.error.code ?? null});
  return body.result;
}

function rpcFailureCategory(error) {
  const code = error?.code;
  const httpStatus = error?.httpStatus;
  const message = String(error?.message ?? error);
  if (code === -32601 || /method not found/i.test(message)) return 'unsupported';
  if (httpStatus === 429 || code === -32029 || /rate.?limit|too many requests/i.test(message)) return 'rate_limited';
  if ([408, 502, 503, 504].includes(httpStatus) || /timeout|timed out|fetch failed|network|temporar/i.test(message)) return 'temporary_failure';
  return 'error';
}

async function probeRpc(method, params) {
  try {
    return {supported: true, result: await rpc(method, params)};
  } catch (error) {
    return {
      supported: false,
      category: rpcFailureCategory(error),
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

function executionSucceeded(tx) {
  const leader = tx?.consensus_data?.leader_receipt?.[0] ?? tx?.leader_receipt?.[0];
  return leader?.execution_result === 'SUCCESS' &&
    (leader?.result === 'AAA=' || leader?.result?.status === 'return');
}

function childTransferSucceeded(child, receiptProbe) {
  // Native GEN child transfers do not run GenVM consensus. Their execution
  // evidence is finalized transport success plus authoritative credit. A
  // consensus-bearing child still requires successful GenVM execution.
  if (child?.consensus_data || child?.leader_receipt) return executionSucceeded(child);
  const receiptOk = receiptSucceeded(receiptProbe);
  return receiptOk === true || (receiptOk === null && child?.value_credited === true);
}

function probeStatus(probe) {
  if (!probe?.supported) return null;
  if (typeof probe.result === 'string') return probe.result.toUpperCase();
  if (probe.result && typeof probe.result.status === 'string') return probe.result.status.toUpperCase();
  return null;
}

function txStatus(tx, statusProbe) {
  const status = probeStatus(statusProbe) ?? String(tx?.status_name ?? tx?.status ?? '').toUpperCase();
  return status || null;
}

function statusConflict(tx, statusProbe) {
  const rpcStatus = probeStatus(statusProbe);
  const txValue = String(tx?.status_name ?? tx?.status ?? '').toUpperCase();
  return Boolean(rpcStatus && txValue && rpcStatus !== txValue);
}

function receiptStatus(receiptProbe) {
  if (!receiptProbe?.supported || !receiptProbe.result || typeof receiptProbe.result !== 'object') return null;
  return receiptProbe.result.status == null ? null : String(receiptProbe.result.status).toLowerCase();
}

function receiptSucceeded(receiptProbe) {
  if (!receiptProbe?.supported || receiptProbe.result == null) return null;
  const status = receiptStatus(receiptProbe);
  return status === '0x1' || status === '1';
}

function receiptEvidenceOptional(receiptProbe) {
  return receiptProbe?.supported === false && receiptProbe.category === 'unsupported';
}

function receiptEvidenceAvailable(receiptProbe) {
  return receiptEvidenceOptional(receiptProbe) || (receiptProbe?.supported === true && receiptProbe.result != null);
}

function final(tx, statusProbe) { return txStatus(tx, statusProbe) === 'FINALIZED'; }
function terminalFailure(tx, statusProbe) {
  const status = txStatus(tx, statusProbe);
  return ['CANCELED', 'CANCELLED', 'FAILED', 'REVERTED'].includes(status) ||
    (final(tx, statusProbe) && tx?.consensus_data && executionSucceeded(tx) === false);
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
  parent_evidence: null,
  children: [],
};

try {
  result.chain_id = await rpc('eth_chainId', []);
  if (result.chain_id !== CHAIN_ID) {
    result.reasons.push(`wrong chain: expected ${CHAIN_ID}, got ${result.chain_id}`);
    console.log(JSON.stringify(result, null, 2));
    process.exit(1);
  }

  const parentStatusProbe = await probeRpc('gen_getTransactionStatus', [parentHash]);
  const parentReceiptProbe = await probeRpc('eth_getTransactionReceipt', [parentHash]);
  const parent = await rpc('eth_getTransactionByHash', [parentHash]);
  result.parent_evidence = {
    gen_status: parentStatusProbe,
    evm_receipt: parentReceiptProbe,
    lifecycle_status: txStatus(parent, parentStatusProbe),
    status_conflict: statusConflict(parent, parentStatusProbe),
    execution_succeeded: parent ? executionSucceeded(parent) : false,
    evm_receipt_succeeded: receiptSucceeded(parentReceiptProbe),
  };
  if (!parent) {
    result.reasons.push('parent transaction not found');
  } else if (parent.to_address?.toLowerCase() !== VAULT) {
    result.reasons.push('parent destination is not the canonical RuleVault');
  } else if (statusConflict(parent, parentStatusProbe)) {
    result.reasons.push('parent lifecycle status conflicts between transaction and gen_getTransactionStatus');
  } else if (parentReceiptProbe.supported && parentReceiptProbe.result == null) {
    result.reasons.push('parent EVM receipt is not available yet');
  } else if (!parentReceiptProbe.supported && !receiptEvidenceOptional(parentReceiptProbe)) {
    result.reasons.push(`parent EVM receipt could not be checked (${parentReceiptProbe.category})`);
  } else if (parentReceiptProbe.supported && receiptSucceeded(parentReceiptProbe) === false) {
    result.reasons.push('parent EVM receipt reports unsuccessful transport execution');
  } else if (!final(parent, parentStatusProbe)) {
    result.reasons.push(`parent status is ${txStatus(parent, parentStatusProbe) ?? 'unknown'}`);
  } else if (final(parent, parentStatusProbe) && executionSucceeded(parent) === false && parent.consensus_data) {
    result.reasons.push('parent finalized without successful leader return evidence');
  }

  const childIds = parent?.triggered_transactions ?? [];
  for (const childHash of childIds) {
    const [child, childReceiptProbe, childStatusProbe] = await Promise.all([
      rpc('eth_getTransactionByHash', [childHash]),
      probeRpc('eth_getTransactionReceipt', [childHash]),
      probeRpc('gen_getTransactionStatus', [childHash]),
    ]);
    const record = {
      hash: childHash,
      from: child?.from_address?.toLowerCase() ?? null,
      to: child?.to_address?.toLowerCase() ?? null,
      value_wei: String(child?.value ?? ''),
      status: txStatus(child, childStatusProbe),
      value_credited: child?.value_credited ?? null,
      gen_status: childStatusProbe,
      evm_receipt: childReceiptProbe,
      status_conflict: statusConflict(child, childStatusProbe),
      evm_receipt_succeeded: receiptSucceeded(childReceiptProbe),
      matches: false,
    };
    record.exact_origin_recipient_value = childIsExactMatch(child, beneficiary, amountWei);
    record.execution_succeeded = child ? childTransferSucceeded(child, childReceiptProbe) : false;
    record.genvm_execution_applicable = Boolean(child?.consensus_data || child?.leader_receipt);
    record.finalized = child ? final(child, childStatusProbe) : false;
    record.authoritative_credit = child?.value_credited === true;
    record.failed = child ? terminalFailure(child, childStatusProbe) : false;
    record.receipt_complete = childReceiptProbe.supported && childReceiptProbe.result != null;
    record.receipt_acceptable = receiptEvidenceAvailable(childReceiptProbe);
    record.receipt_failed = record.receipt_complete && record.evm_receipt_succeeded === false;
    record.matches = record.exact_origin_recipient_value && record.finalized &&
      record.execution_succeeded && record.authoritative_credit &&
      !record.status_conflict && !record.receipt_failed && record.receipt_acceptable;
    result.children.push(record);
  }

  if (!parent) {
    result.status = DELIVERY_STATES.UNRESOLVED;
    result.reasons.push('parent transaction is unavailable');
  } else if (parent.to_address?.toLowerCase() !== VAULT) {
    result.status = DELIVERY_STATES.UNRESOLVED;
  } else if (statusConflict(parent, parentStatusProbe)) {
    result.status = DELIVERY_STATES.UNRESOLVED;
  } else if (terminalFailure(parent, parentStatusProbe)) {
    result.status = DELIVERY_STATES.FAILED;
    result.reasons.push('parent transaction failed or finalized without successful execution');
  } else if (parentReceiptProbe.supported && parentReceiptProbe.result == null) {
    result.status = DELIVERY_STATES.UNRESOLVED;
  } else if (!parentReceiptProbe.supported && !receiptEvidenceOptional(parentReceiptProbe)) {
    result.status = DELIVERY_STATES.UNRESOLVED;
  } else if (parentReceiptProbe.supported && receiptSucceeded(parentReceiptProbe) === false) {
    result.status = DELIVERY_STATES.FAILED;
  } else if (!final(parent, parentStatusProbe)) {
    result.status = DELIVERY_STATES.TRANSFER_SUBMITTED;
    result.reasons.push(`parent status is ${txStatus(parent, parentStatusProbe) ?? 'unknown'}`);
  } else if (result.children.some((child) => child.matches)) {
    result.status = DELIVERY_STATES.DELIVERY_VERIFIED;
  } else if (result.children.some((child) => child.exact_origin_recipient_value && child.failed)) {
    result.status = DELIVERY_STATES.FAILED;
    result.reasons.push('matching child transfer failed or finalized without successful execution');
  } else if (result.children.some((child) => child.exact_origin_recipient_value && child.receipt_failed)) {
    result.status = DELIVERY_STATES.FAILED;
    result.reasons.push('matching child EVM receipt reports unsuccessful transport execution');
  } else if (result.children.some((child) => child.exact_origin_recipient_value && child.finalized && !child.receipt_acceptable)) {
    result.status = DELIVERY_STATES.UNRESOLVED;
    result.reasons.push('matching child is finalized, but its EVM receipt evidence is unavailable or temporarily inaccessible');
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
