'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { Download, ExternalLink, FileCheck2, GitBranch, RefreshCcw, ShieldCheck, Sparkles, Wrench } from 'lucide-react';
import { useWallet } from '@/components/Providers';
import { dateFormat, explorerAddress, explorerTx, fromWei, toWei } from '@/lib/helpers';
import { fetchV2Audit, fetchV2Config, resolveV2GithubSource, V2_ADDRESS, V2_READY } from '@/lib/v2';
import type { RepairProposal, V2AuditHistory } from '@/lib/types';

function stateClass(state: string) {
  return `v2-state v2-state-${state.toLowerCase().replaceAll('_', '-')}`;
}

function shortHash(value: string) {
  return value ? `${value.slice(0, 10)}…${value.slice(-8)}` : '—';
}

export default function V2Explorer() {
  const { account, chain, connect, switchChain, submit, busy } = useWallet();
  const [challengeId, setChallengeId] = useState('1');
  const [audit, setAudit] = useState<V2AuditHistory | null>(null);
  const [config, setConfig] = useState<Record<string, string> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [revisedRule, setRevisedRule] = useState('');
  const [revisedLimitations, setRevisedLimitations] = useState('');
  const [explanation, setExplanation] = useState('');
  const [sourceOwner, setSourceOwner] = useState('ometere123');
  const [sourceRepo, setSourceRepo] = useState('loophole');
  const [sourceCommit, setSourceCommit] = useState('');
  const [sourcePath, setSourcePath] = useState('');
  const [sourceMarker, setSourceMarker] = useState('');
  const [sourceDigest, setSourceDigest] = useState('');
  const [sourceRef, setSourceRef] = useState('');
  const [sourceBusy, setSourceBusy] = useState(false);
  const [sourceMessage, setSourceMessage] = useState('');
  const [rechallengeTitle, setRechallengeTitle] = useState('');
  const [rechallengeBounty, setRechallengeBounty] = useState('0.02');
  const [rechallengeBond, setRechallengeBond] = useState('0.01');
  const [rechallengeDuration, setRechallengeDuration] = useState('86400');
  const rehallengeTitle = rechallengeTitle;
  const rehallengeBounty = rechallengeBounty;
  const rehallengeBond = rechallengeBond;
  const rehallengeDuration = rechallengeDuration;

  const load = useCallback(async () => {
    if (!V2_READY) return;
    setLoading(true); setError('');
    try {
      const [nextAudit, nextConfig] = await Promise.all([fetchV2Audit(challengeId), fetchV2Config()]);
      setAudit(nextAudit); setConfig(nextConfig);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally { setLoading(false); }
  }, [challengeId]);

  useEffect(() => { if (V2_READY) void load(); }, [load]);

  const authoritative = useMemo(() => audit?.policy_versions.find(item => item.authoritative) || null, [audit]);
  const activeProposal = useMemo<RepairProposal | null>(() => {
    const id = audit?.challenge.active_repair_proposal;
    return id && id !== '0' ? audit.repair_proposals.find(item => item.id === id) || null : null;
  }, [audit]);

  const runWrite = async (method: string, args: unknown[], value = 0n) => {
    setError(''); setNotice('');
    try {
      await submit(method, args, value, V2_ADDRESS);
      setNotice(`${method.replaceAll('_', ' ')} finalized and execution-checked.`);
      await load();
    } catch (cause) { setError(cause instanceof Error ? cause.message : String(cause)); }
  };

  const propose = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!audit || !authoritative || audit.challenge.winner_attempt === '0') return;
    await runWrite('propose_repair', [
      BigInt(challengeId), BigInt(audit.challenge.winner_attempt), BigInt(authoritative.version),
      revisedRule, revisedLimitations, explanation, sourceRef, sourceDigest, sourceMarker,
    ]);
  };

  const resolveSource = async (event: React.FormEvent) => {
    event.preventDefault(); setSourceBusy(true); setSourceMessage(''); setError('');
    try {
      const result = await resolveV2GithubSource({ owner: sourceOwner, repo: sourceRepo, commit: sourceCommit, path: sourcePath, versionMarker: sourceMarker });
      setSourceRef(result.rawUrl); setSourceDigest(result.sha256);
      setSourceMessage(`Authenticated ${result.byteLength} exact UTF-8 bytes at ${result.rawUrl}. SHA-256: ${result.sha256}`);
    } catch (cause) { setSourceMessage(cause instanceof Error ? cause.message : String(cause)); }
    finally { setSourceBusy(false); }
  };

  const downloadAudit = () => {
    if (!audit || typeof window === 'undefined') return;
    const blob = new Blob([JSON.stringify(audit, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob); const anchor = document.createElement('a');
    anchor.href = url; anchor.download = `loophole-v2-audit-${challengeId}.json`; anchor.click(); URL.revokeObjectURL(url);
  };

  if (!V2_READY) return <section className="container v2-page"><div className="eyebrow"><Wrench size={15}/> POLICY REPAIR EXPLORER</div><h1>V2 is ready for a verified deployment.</h1><p className="lead">The V1 production address remains unchanged. This audit surface stays read-only and clearly unavailable until <code>NEXT_PUBLIC_LOOPHOLE_V2_ADDRESS</code> points to an explicitly approved, source-verified V2 deployment.</p><div className="notice warning"><ShieldCheck size={17}/> No V2 address is configured, so no V2 state or economic action is displayed.</div></section>;

  return <section className="container v2-page">
    <div className="v2-heading"><div><div className="eyebrow"><Sparkles size={15}/> POLICY REPAIR EXPLORER</div><h1>Find the flaw. Repair the rule.</h1><p className="lead">A versioned, consensus-backed audit trail for corrections that are proposed after a finalized loophole verdict.</p></div><button className="button button-light" onClick={downloadAudit} disabled={!audit}><Download size={17}/> Export JSON</button></div>
    <div className="v2-config"><span><b>V2 contract</b> <a href={explorerAddress(V2_ADDRESS)} target="_blank" rel="noreferrer">{shortHash(V2_ADDRESS)} <ExternalLink size={14}/></a></span><span><b>Protocol</b> {config?.protocol_version || 'loading…'}</span><span><b>Chain</b> {config?.chain || '61999'}</span></div>
    <div className="v2-lookup"><label>Challenge ID<input inputMode="numeric" value={challengeId} onChange={event => setChallengeId(event.target.value)} /></label><button className="button button-dark" onClick={() => void load()} disabled={loading}><RefreshCcw size={17}/> {loading ? 'Loading…' : 'Load audit history'}</button></div>
    {error && <div className="notice danger" role="alert">{error}</div>}
    {notice && <div className="notice success" role="status">{notice}</div>}
    {audit && <>
      <div className="v2-summary"><div><span className="eyebrow">CURRENT CHALLENGE</span><h2>{audit.challenge.title}</h2><p>{audit.challenge.goal}</p></div><span className={stateClass(audit.challenge.status)}>{audit.challenge.status}</span></div>
      <div className="v2-grid"><article className="v2-card"><div className="v2-card-title"><GitBranch size={18}/><h2>Policy lineage</h2></div>{audit.policy_versions.map(version => <div className="v2-timeline-item" key={version.version}><div className="v2-timeline-dot"/><div><div className="v2-row"><b>Version {version.version}</b><span className={stateClass(version.status)}>{version.status}</span></div><p>{version.rule}</p><small>Parent {version.parent_version} · commitment <code>{shortHash(version.content_commitment)}</code> · {version.authoritative ? 'authoritative' : 'historical'}</small></div></div>)}</article>
      <article className="v2-card"><div className="v2-card-title"><FileCheck2 size={18}/><h2>Repair reviews</h2></div>{audit.repair_proposals.length === 0 && <p className="muted">No correction has been proposed for this challenge.</p>}{audit.repair_proposals.map(proposal => <div className="v2-review" key={proposal.id}><div className="v2-row"><b>Proposal {proposal.id} → v{proposal.proposed_version}</b><span className={stateClass(proposal.status)}>{proposal.status}</span></div><p>{proposal.explanation}</p><div className="v2-findings"><span>Closure <b>{proposal.closure}</b></span><span>Goal <b>{proposal.goal_finding}</b></span><span>Coherence <b>{proposal.coherence}</b></span></div><small>Evidence: {proposal.evidence_state || 'not reviewed'} · round {proposal.review_round}</small>{proposal.reason && <p className="muted">{proposal.reason}</p>}</div>)}</article></div>
      <article className="v2-card v2-audit-card"><div className="v2-card-title"><ShieldCheck size={18}/><h2>Chronological audit</h2></div><ol className="v2-audit-list"><li>Original rulebook version 1 was frozen with the challenge.</li>{audit.attempts.filter(item => item.verdict).map(item => <li key={`attempt-${item.id}`}>Attempt {item.id} finalized <b>{item.verdict}</b> with evidence <code>{shortHash(item.evidence_hash || '')}</code>.</li>)}{audit.repair_adjudications.map(record => <li key={record.id}>Repair proposal {record.proposal_id}, round {record.round_id}, finalized <b>{record.verdict}</b>: closure {record.closure}, goal {record.goal}, coherence {record.coherence}.</li>)}{audit.policy_versions.filter(item => item.version !== '1').map(item => <li key={`version-${item.version}`}>Version {item.version} is {item.status}; {item.authoritative ? 'it is now authoritative.' : 'the prior authoritative version remains in force.'}</li>)}</ol></article>
      {audit.challenge.status === 'WON' && <article className="v2-card"><div className="v2-card-title"><Wrench size={18}/><h2>Propose a repair</h2></div><p className="muted">Only the original organizer can submit a bounded revision. The revision is not authoritative until independent repair consensus finalizes as <b>VERIFIED_FIX</b>.</p><form className="v2-form" onSubmit={propose}><label>Corrected rule<textarea required minLength={20} maxLength={3000} value={revisedRule} onChange={event => setRevisedRule(event.target.value)} placeholder="State the precise condition that closes the frozen exploit." /></label><label>Limitations<textarea maxLength={2000} value={revisedLimitations} onChange={event => setRevisedLimitations(event.target.value)} placeholder="Keep the original goal operational and bounded." /></label><label>Explanation<textarea required minLength={20} maxLength={1200} value={explanation} onChange={event => setExplanation(event.target.value)} placeholder="Explain why the change closes this exact exploit." /></label>{audit.challenge.evidence_mode === 'PINNED_SOURCE' && <><div className="v2-source-wizard"><div className="v2-card-title"><GitBranch size={17}/><h3>Authenticate pinned GitHub source</h3></div><div className="v2-form-grid"><label>Owner<input value={sourceOwner} onChange={event => setSourceOwner(event.target.value)} /></label><label>Repository<input value={sourceRepo} onChange={event => setSourceRepo(event.target.value)} /></label><label>Full commit SHA<input required pattern="[a-fA-F0-9]{40}" value={sourceCommit} onChange={event => setSourceCommit(event.target.value)} /></label><label>File path<input required value={sourcePath} onChange={event => setSourcePath(event.target.value)} /></label><label>Version marker<input required value={sourceMarker} onChange={event => setSourceMarker(event.target.value)} /></label></div><button className="button button-light" type="button" onClick={resolveSource} disabled={sourceBusy}>{sourceBusy ? 'Fetching exact bytes…' : 'Resolve and hash source'}</button>{sourceMessage && <p className="muted">{sourceMessage}</p>}<small>Client preflight is convenience only; validators independently fetch and authenticate the pinned bytes before settlement.</small></div><label>Resolved raw source URL<input required value={sourceRef} onChange={event => setSourceRef(event.target.value)} /></label><label>Source SHA-256<input required pattern="[0-9a-f]{64}" value={sourceDigest} onChange={event => setSourceDigest(event.target.value)} /></label></>}{<button className="button button-dark" disabled={busy || !account || chain !== 61999 || !!activeProposal} type="submit">{activeProposal ? 'A repair is already active' : 'Submit repair proposal'}</button>}</form></article>}
      {activeProposal?.status === 'PROPOSED' && <article className="v2-card v2-action-card"><h2>Start repair review</h2><p>This permissionless action freezes the complete original and proposed evidence for round {Number(activeProposal.review_round) + 1}.</p><button className="button button-dark" disabled={busy || chain !== 61999} onClick={() => void runWrite('start_repair_review', [BigInt(challengeId), BigInt(activeProposal.id)])}>Start review</button></article>}
      {activeProposal?.status === 'REVIEWING' && <article className="v2-card v2-action-card"><h2>Adjudicate repair</h2><p>Validators independently reassess closure, goal preservation and coherence. No UI input can choose the verdict.</p><button className="button button-dark" disabled={busy || chain !== 61999} onClick={() => void runWrite('adjudicate_repair', [BigInt(challengeId), BigInt(activeProposal.id), BigInt(activeProposal.review_round)])}>Trigger repair consensus</button></article>}
      {authoritative?.status === 'VERIFIED_FIX' && !activeProposal && <article className="v2-card"><div className="v2-card-title"><Sparkles size={18}/><h2>Launch a separately funded re-challenge</h2></div><p className="muted">A re-challenge uses the verified version but has independent bounty and bond liabilities. Original winners and history remain unchanged.</p><form className="v2-form" onSubmit={event => { event.preventDefault(); void runWrite('create_rechallenge', [BigInt(challengeId), BigInt(authoritative.version), rehallengeTitle, BigInt(rehallengeDuration), toWei(rechallengeBond)], toWei(rechallengeBounty)); }}><label>Title<input required value={rehallengeTitle} onChange={event => setRechallengeTitle(event.target.value)} /></label><div className="v2-form-grid"><label>Bounty (GEN)<input required value={rehallengeBounty} onChange={event => setRechallengeBounty(event.target.value)} /></label><label>Bond (GEN)<input required value={rehallengeBond} onChange={event => setRechallengeBond(event.target.value)} /></label><label>Duration (seconds)<input required inputMode="numeric" value={rehallengeDuration} onChange={event => setRechallengeDuration(event.target.value)} /></label></div><button className="button button-dark" disabled={busy || !account || chain !== 61999} type="submit">Fund re-challenge</button></form></article>}
    </>}
    {account && chain !== 61999 && <div className="notice warning">Switch the connected wallet to Studionet 61999 before any V2 write. <button className="text-link" onClick={() => void switchChain()}>Switch network</button></div>}
    {!account && <div className="notice warning">Connect the injected EIP-1193 wallet only when you are ready to authorize a V2 write. <button className="text-link" onClick={() => void connect()}>Connect wallet</button></div>}
  </section>;
}
