// Pure delivery-state classification shared by the read-only verifier and its
// deterministic failure/ambiguity tests.  RPC fetching and contract writes do
// not belong here.

export const DELIVERY_STATES = Object.freeze({
  CLAIMABLE: 'CLAIMABLE',
  TRANSFER_SUBMITTED: 'TRANSFER SUBMITTED',
  PARENT_FINALIZED: 'PARENT FINALIZED',
  DELIVERY_VERIFIED: 'DELIVERY VERIFIED',
  FAILED: 'FAILED',
  UNRESOLVED: 'UNRESOLVED',
});

export function classifyDelivery({parent, children}) {
  const reasons = [];
  if (!parent?.found) {
    return {status: DELIVERY_STATES.UNRESOLVED, reasons: ['parent transaction is unavailable']};
  }
  if (!parent.destination_matches) {
    return {status: DELIVERY_STATES.UNRESOLVED, reasons: ['parent destination is not the configured Loophole contract']};
  }
  if (parent.status_conflict) {
    return {status: DELIVERY_STATES.UNRESOLVED, reasons: ['parent lifecycle status conflicts between transaction and gen_getTransactionStatus']};
  }
  if (parent.failed) {
    return {status: DELIVERY_STATES.FAILED, reasons: ['parent transaction failed or finalized without successful execution']};
  }
  if (parent.receipt_pending) {
    return {status: DELIVERY_STATES.UNRESOLVED, reasons: ['parent EVM receipt is not available yet']};
  }
  if (parent.receipt_unavailable) {
    return {status: DELIVERY_STATES.UNRESOLVED, reasons: [`parent EVM receipt could not be checked (${parent.receipt_category})`]};
  }
  if (parent.receipt_failed) {
    return {status: DELIVERY_STATES.FAILED, reasons: ['parent EVM receipt reports unsuccessful transport execution']};
  }
  if (!parent.finalized) {
    return {status: DELIVERY_STATES.TRANSFER_SUBMITTED, reasons: [`parent status is ${parent.status ?? 'unknown'}`]};
  }
  if (parent.execution_failed) {
    return {status: DELIVERY_STATES.FAILED, reasons: ['parent finalized without successful leader return evidence']};
  }

  const exact = (children ?? []).filter((child) => child.exact_origin_recipient_value);
  const verified = exact.find((child) =>
    child.finalized &&
    child.execution_succeeded &&
    child.authoritative_credit &&
    !child.status_conflict &&
    !child.receipt_failed &&
    child.receipt_acceptable,
  );
  if (verified) {
    return {status: DELIVERY_STATES.DELIVERY_VERIFIED, reasons: [], child_hash: verified.hash};
  }
  if (exact.some((child) => child.failed)) {
    return {
      status: DELIVERY_STATES.FAILED,
      reasons: ['matching child transfer failed or finalized without successful execution'],
    };
  }
  if (exact.some((child) => child.receipt_failed)) {
    return {
      status: DELIVERY_STATES.FAILED,
      reasons: ['matching child EVM receipt reports unsuccessful transport execution'],
    };
  }
  if (exact.some((child) => child.finalized && !child.receipt_acceptable)) {
    return {
      status: DELIVERY_STATES.UNRESOLVED,
      reasons: ['matching child is finalized, but its EVM receipt evidence is unavailable or temporarily inaccessible'],
    };
  }
  if (exact.some((child) => child.status_conflict)) {
    return {
      status: DELIVERY_STATES.UNRESOLVED,
      reasons: ['matching child lifecycle status conflicts between transaction and gen_getTransactionStatus'],
    };
  }
  if (exact.some((child) => !child.finalized)) {
    return {
      status: DELIVERY_STATES.TRANSFER_SUBMITTED,
      reasons: ['matching child transfer is not finalized'],
    };
  }
  if (!children?.length) {
    return {
      status: DELIVERY_STATES.PARENT_FINALIZED,
      reasons: ['parent finalized, but no external child transfer is visible yet'],
    };
  }
  reasons.push('child transactions exist, but none matched the vault, beneficiary, amount, finality, and authoritative credit evidence');
  return {status: DELIVERY_STATES.UNRESOLVED, reasons};
}
