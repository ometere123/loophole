#!/usr/bin/env node

const rpcUrl = process.env.GENLAYER_RPC ?? 'https://studio.genlayer.com/api';
const hashes = process.argv.slice(2);
if (hashes.length === 0) {
  console.error('usage: node scripts/inspect_adjudication.mjs <tx-hash> [<tx-hash> ...]');
  process.exit(2);
}

async function rpc(method, params) {
  const response = await fetch(rpcUrl, {
    method: 'POST',
    headers: {'content-type': 'application/json'},
    body: JSON.stringify({jsonrpc: '2.0', id: 1, method, params}),
  });
  const body = await response.json();
  if (body.error) throw new Error(`${method}: ${body.error.code} ${body.error.message}`);
  return body.result;
}

const chainId = await rpc('eth_chainId', []);
const rows = [];
for (const hash of hashes) {
  const receipt = await rpc('eth_getTransactionByHash', [hash]);
  if (!receipt) throw new Error(`transaction not found: ${hash}`);
  let trace;
  try {
    trace = await rpc('gen_dbg_traceTransaction', [hash]);
  } catch (error) {
    trace = {unavailable: String(error)};
  }
  rows.push({
    hash,
    chain_id: chainId,
    from: receipt.from_address,
    to: receipt.to_address,
    status: receipt.status,
    result_name: receipt.result_name,
    value: receipt.value,
    gaslimit: receipt.gaslimit,
    gas_used: receipt.consensus_data?.leader_receipt?.[0]?.gas_used ?? null,
    leader_execution: receipt.consensus_data?.leader_receipt?.[0]?.execution_result ?? null,
    votes: receipt.consensus_data?.votes ?? {},
    validator_count: receipt.consensus_data?.validators?.length ?? 0,
    triggered_by: receipt.triggered_by ?? null,
    triggered_transactions: receipt.triggered_transactions ?? [],
    value_credited: receipt.value_credited ?? false,
    consensus_error: receipt.consensus_data?.error ?? null,
    trace,
  });
}
console.log(JSON.stringify({rpc: rpcUrl, rows}, null, 2));
