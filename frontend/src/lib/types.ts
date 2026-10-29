export type ChallengeStatus = 'OPEN' | 'WON' | 'REFUNDED';
export type AttemptStatus = 'COMMITTED' | 'REVEALED' | 'REVIEWING' | 'INVALID_PENDING' | 'APPEAL_REVIEWING' | 'DECIDED' | 'EXPIRED' | 'FORFEITED' | 'RELEASED';
export type Verdict = 'VALID' | 'INVALID' | 'INCONCLUSIVE' | '';
export type Category = 'COMMUNITY' | 'CONTENT' | 'REFERRAL' | 'GOVERNANCE' | 'OTHER';
export type EvidenceMode = 'HYPOTHETICAL' | 'PINNED_SOURCE';
export type Challenge = {
  id: string; organizer: string; title: string; goal: string; rule: string;
  limitations: string; category: Category; prize_wei: string; bond_wei: string;
  created_at: number; ends_at: number; reveal_deadline: number; status: ChallengeStatus; winner: string;
  winner_attempt: string; active_attempt: string; active_round: string;
  review_started: number; attempts: string[]; evidence_mode?: EvidenceMode;
  source_url?: string; source_ref?: string; source_sha256?: string;
  source_version?: string; authoritative_version?: string; policy_version_count?: string;
  repair_proposals?: string[]; active_repair_proposal?: string; active_repair_round?: string;
  origin_challenge_id?: string; origin_policy_version?: string; repair_lineage?: string;
};
export type Attempt = {
  id: string; challenge_id: string; challenger: string; commitment: string;
  status: AttemptStatus; bond_wei: string; committed_at: number; revealed_at: number;
  scenario: string; rule_quote: string; impact: string; verdict: Verdict; evidence_hash?: string;
  reason: string; letter: boolean; purpose: boolean; feasible: boolean;
  appeal_used: boolean; appeal_deadline: number; appeal_bond_wei: string;
  evidence_ref?: string; evidence_sha256?: string; evidence_version?: string;
  evidence_state?: string;
};
export type VaultConfig = {contract?: string;chain:string;challenge_count:string;attempt_count:string;adjudication_count?:string;withdrawal_count:string;total_credit_wei:string;total_locked_wei:string;commitment_encoding?:string;adjudication_mode?:string;validator_agreement?:string;source_modes?:string;source_type?:string;max_source_bytes?:string};
export type TxPhase = 'idle' | 'awaiting_wallet' | 'submitted' | 'accepted' | 'finalized' | 'execution_failed' | 'unknown' | 'rejected';
export type TxInfo = {phase: TxPhase; hash?: string; title?: string; error?: string};
export type PersistedTransaction = {hash: string; account: string; phase: Exclude<TxPhase, 'idle'|'awaiting_wallet'|'rejected'|'finalized'>; title?: string; error?: string; updatedAt: number};
export type CommitmentBackup = { challengeId: string; address: string; salt: string; scenario: string; ruleQuote: string; impact: string; commitment: string; savedAt: number; evidenceRef?: string; evidenceSha256?: string; evidenceVersion?: string };
export type DeliveryStatus = 'CLAIMABLE' | 'TRANSFER SUBMITTED' | 'PARENT FINALIZED' | 'DELIVERY VERIFIED' | 'FAILED' | 'UNRESOLVED';
export type DeliveryVerification = {
  status: DeliveryStatus;
  parentHash: string;
  childHash?: string;
  beneficiary: string;
  amountWei: string;
  parentLifecycleStatus?: string | null;
  childLifecycleStatus?: string | null;
  parentEvmReceiptStatus?: string | null;
  childEvmReceiptStatus?: string | null;
  reasons: string[];
  checkedAt: number;
};
export type WithdrawalProvenance = DeliveryVerification & { withdrawalId: string };

export type PolicyVersionStatus = 'ORIGINAL' | 'PROPOSED' | 'VERIFIED_FIX' | 'NOT_VERIFIED' | 'INCONCLUSIVE' | 'RECHALLENGE_BASELINE' | string;
export type RepairStatus = 'PROPOSED' | 'REVIEWING' | 'VERIFIED_FIX' | 'NOT_VERIFIED' | 'INCONCLUSIVE' | string;
export type RepairFinding = 'PROVEN' | 'DISPROVEN' | 'UNKNOWN' | string;
export type PolicyVersion = {
  id: string; challenge_id: string; organizer: string; version: string; parent_version: string;
  goal: string; rule: string; limitations: string; evidence_mode: EvidenceMode;
  source_ref?: string; source_sha256?: string; source_version?: string;
  content_commitment: string; status: PolicyVersionStatus; authoritative: boolean;
  proposal_id: string; created_at: number;
};
export type RepairProposal = {
  id: string; challenge_id: string; organizer: string; successful_attempt_id: string;
  original_evidence_hash: string; original_verdict: Verdict; parent_version: string;
  proposed_version: string; goal: string; revised_rule: string; revised_limitations: string;
  explanation: string; source_ref?: string; source_sha256?: string; source_version?: string;
  content_commitment: string; status: RepairStatus; review_round: string; review_started: number;
  snapshot_hash: string; closure: RepairFinding; goal_finding: RepairFinding;
  coherence: RepairFinding; verdict: string; reason: string; evidence_state: string;
  adjudication_key: string; created_at: number;
};
export type RepairAdjudication = {
  id: string; challenge_id: string; proposal_id: string; round_id: string; snapshot_hash: string;
  closure: RepairFinding; goal: RepairFinding; coherence: RepairFinding; verdict: string;
  reason: string; evidence_state: string; settlement: string; recorded_at: number;
};
export type V2AuditHistory = {
  version: string; challenge: Challenge; policy_versions: PolicyVersion[]; attempts: Attempt[];
  repair_proposals: RepairProposal[]; repair_adjudications: RepairAdjudication[];
};
