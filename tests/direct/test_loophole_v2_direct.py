"""GenVM Direct Mode coverage for the V2 policy-repair state machine."""

import hashlib
import json
import re


def _commitment(address, salt, scenario, quote, impact):
    sender = ('0x' + address.hex()).lower() if isinstance(address, bytes) else str(address).lower()
    fields = ['1', sender, salt, scenario, quote, impact]
    raw = ''.join(f'{len(field.encode("utf-8"))}:{field}' for field in fields)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def _prepare_valid_challenge(direct_vm, direct_deploy, direct_owner, direct_alice):
    direct_vm._chain_id = 61999
    direct_vm.mock_llm(
        r'(?s).*Derive the verdict mechanically.*',
        json.dumps({
            'letter': 'PROVEN', 'purpose': 'PROVEN', 'feasible': 'PROVEN',
            'reason': 'The exact conditions are met and the documented sequence is feasible.',
        }),
    )
    contract = direct_deploy('contracts/LoopholeV2.py')
    goal = 'Reward genuinely new educational contributions rather than repeated text.'
    rule = 'Award points to any public post with at least five words and one source link.'
    limitations = 'The post must add a new explanation of the linked source.'
    scenario = 'Publish a qualifying post with six words and one source link, then add a new explanation.'
    impact = 'The qualifying post can defeat the educational purpose through a deliberate misleading explanation.'
    quote = rule
    salt = 'v2-direct-salt-1234'
    direct_vm.sender = direct_owner
    direct_vm.value = 2 * 10**16
    contract.create_challenge(
        'V2 policy repair', goal, rule, limitations, 'CONTENT', 86400, 10**16,
    )
    direct_vm.sender = direct_alice
    direct_vm.value = 10**16
    contract.commit_attempt(1, _commitment(direct_alice, salt, scenario, quote, impact))
    contract.reveal_attempt(1, salt, scenario, quote, impact)
    contract.start_review(1)
    contract.adjudicate_review(1, 1, 1)
    assert json.loads(contract.get_attempt(1))['verdict'] == 'VALID'
    return contract, goal, rule, limitations


def _propose(contract, direct_vm, direct_owner, goal, rule, limitations, revised_rule=None):
    direct_vm.sender = direct_owner
    direct_vm.value = 0
    contract.propose_repair(
        1, 1, 1,
        revised_rule or 'Award points only when a public post includes a source link and a new verifiable explanation.',
        limitations + ' The explanation must materially add context supported by the linked source.',
        'The correction closes the repeated-text loophole while preserving genuine education.',
        '', '', '',
    )


def test_v2_valid_repair_is_authoritative_and_rechallenge_is_separate(
        direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, goal, rule, limitations = _prepare_valid_challenge(
        direct_vm, direct_deploy, direct_owner, direct_alice)
    _propose(contract, direct_vm, direct_owner, goal, rule, limitations)
    proposal = json.loads(contract.get_repair_proposal(1))
    assert proposal['status'] == 'PROPOSED'
    assert proposal['parent_version'] == '1'
    assert json.loads(contract.get_policy_version(1, 1))['status'] == 'ORIGINAL'
    assert json.loads(contract.get_policy_version(1, 2))['status'] == 'PROPOSED'

    direct_vm.mock_llm(
        r'(?s).*CLOSURE.*Derive the economic result mechanically.*',
        json.dumps({
            'closure': 'PROVEN', 'goal': 'PROVEN', 'coherence': 'PROVEN',
            'reason': 'The revised condition blocks the exact attempt while retaining a workable educational path.',
        }),
    )
    contract.start_repair_review(1, 1)
    contract.adjudicate_repair(1, 1, 1)

    proposal = json.loads(contract.get_repair_proposal(1))
    version = json.loads(contract.get_policy_version(1, 2))
    challenge = json.loads(contract.get_challenge(1))
    assert proposal['status'] == 'VERIFIED_FIX'
    assert proposal['verdict'] == 'VERIFIED_FIX'
    assert version['status'] == 'VERIFIED_FIX'
    assert version['authoritative'] is True
    assert challenge['authoritative_version'] == '2'
    assert contract.get_credit(direct_alice) == 3 * 10**16

    direct_vm.sender = direct_owner
    direct_vm.value = 2 * 10**16
    contract.create_rechallenge(1, 2, 'V2 regression challenge', 86400, 10**16)
    rechallenge = json.loads(contract.get_challenge(2))
    rechallenge_version = json.loads(contract.get_policy_version(2, 1))
    assert rechallenge['origin_challenge_id'] == '1'
    assert rechallenge['origin_policy_version'] == '2'
    assert rechallenge['repair_lineage'] == '1:2'
    assert rechallenge_version['status'] == 'RECHALLENGE_BASELINE'
    assert rechallenge_version['authoritative'] is True
    assert json.loads(contract.get_challenge(1))['status'] == 'WON'
    assert contract.get_credit(direct_alice) == 3 * 10**16


def test_v2_disproved_repair_cannot_become_authoritative_or_rechallenged(
        direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, goal, rule, limitations = _prepare_valid_challenge(
        direct_vm, direct_deploy, direct_owner, direct_alice)
    _propose(contract, direct_vm, direct_owner, goal, rule, limitations,
             'Award points for any public post without changing the original rule.')
    direct_vm.mock_llm(
        r'(?s).*CLOSURE.*Derive the economic result mechanically.*',
        json.dumps({
            'closure': 'DISPROVEN', 'goal': 'PROVEN', 'coherence': 'PROVEN',
            'reason': 'The unchanged rule still permits the exact previously validated loophole.',
        }),
    )
    contract.start_repair_review(1, 1)
    contract.adjudicate_repair(1, 1, 1)
    assert json.loads(contract.get_repair_proposal(1))['status'] == 'NOT_VERIFIED'
    assert json.loads(contract.get_challenge(1))['authoritative_version'] == '1'
    with direct_vm.expect_revert('authoritative policy version'):
        direct_vm.sender = direct_owner
        direct_vm.value = 2 * 10**16
        contract.create_rechallenge(1, 2, 'Rejected repair challenge', 86400, 10**16)


def test_v2_hypothetical_repair_rejects_unexpected_source_metadata(
        direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, goal, rule, limitations = _prepare_valid_challenge(
        direct_vm, direct_deploy, direct_owner, direct_alice)
    # The hypothetical challenge deliberately rejects source metadata.
    with direct_vm.expect_revert('source metadata is not enabled'):
        direct_vm.sender = direct_owner
        direct_vm.value = 0
        contract.propose_repair(
            1, 1, 1,
            'Award points only when a public post includes a source link and a new explanation.',
            limitations + ' The explanation must add context.',
            'This correction is not allowed to attach source metadata here.',
            'https://raw.githubusercontent.com/example/rules/' + 'a' * 40 + '/rulebook.txt',
            'a' * 64, 'RULEBOOK-V2',
        )


def test_v2_wrong_organizer_stale_parent_and_duplicate_review_are_rejected(
        direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    contract, goal, rule, limitations = _prepare_valid_challenge(
        direct_vm, direct_deploy, direct_owner, direct_alice)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert('original organizer'):
        _propose(contract, direct_vm, direct_bob, goal, rule, limitations)

    direct_vm.sender = direct_owner
    with direct_vm.expect_revert('authoritative policy version'):
        direct_vm.value = 0
        contract.propose_repair(
            1, 1, 2, 'A different correction that is bounded and clear.',
            limitations, 'This is a deliberately stale parent version.', '', '', '',
        )
    _propose(contract, direct_vm, direct_owner, goal, rule, limitations)
    contract.start_repair_review(1, 1)
    with direct_vm.expect_revert('repair is not ready'):
        contract.start_repair_review(1, 1)
    with direct_vm.expect_revert('not awaiting adjudication'):
        contract.adjudicate_repair(1, 1, 2)


def test_v2_source_backed_repair_hash_mismatch_is_inconclusive(
        direct_vm, direct_deploy, direct_owner, direct_alice):
    direct_vm._chain_id = 61999
    direct_vm.mock_llm(
        r'(?s).*Derive the verdict mechanically.*',
        json.dumps({
            'letter': 'PROVEN', 'purpose': 'PROVEN', 'feasible': 'PROVEN',
            'reason': 'The source-backed original evidence establishes the winning loophole.',
        }),
    )
    contract = direct_deploy('contracts/LoopholeV2.py')
    goal = 'Reward genuinely new educational contributions rather than repeated text.'
    rule = 'Award points to any public post with at least five words and one source link.'
    limitations = 'The post must add a new explanation of the linked source.'
    original_url = 'https://raw.githubusercontent.com/example/rules/' + 'a' * 40 + '/rulebook.txt'
    evidence_url = 'https://raw.githubusercontent.com/example/evidence/' + 'b' * 40 + '/attempt.txt'
    revised_url = 'https://raw.githubusercontent.com/example/rules/' + 'c' * 40 + '/rulebook.txt'
    original_body = 'RULEBOOK-V1\n' + goal + '\n' + rule + '\n' + limitations + '\n'
    evidence_body = 'EVIDENCE-V1\nThe exact winning educational post is frozen.\n'
    revised_rule = 'Award points only when a public post includes a source link and a new explanation.'
    revised_limitations = limitations + ' The explanation must add context.'
    revised_body = 'RULEBOOK-V2\n' + goal + '\n' + revised_rule + '\n' + revised_limitations + '\n'
    direct_vm.mock_web(re.escape(original_url), {'status': 200, 'body': original_body})
    direct_vm.mock_web(re.escape(evidence_url), {'status': 200, 'body': evidence_body})
    direct_vm.mock_web(re.escape(revised_url), {'status': 200, 'body': 'RULEBOOK-V2\nsubstituted bytes'})
    direct_vm.sender = direct_owner
    direct_vm.value = 2 * 10**16
    contract.create_source_challenge(
        'V2 pinned repair', goal, rule, limitations, 'CONTENT', 86400, 10**16,
        original_url, hashlib.sha256(original_body.encode()).hexdigest(), 'RULEBOOK-V1',
    )
    scenario = 'Publish a qualifying post and add a misleading explanation that defeats the goal.'
    impact = 'The post satisfies the literal conditions while defeating the educational purpose.'
    salt = 'v2-source-salt-1234'
    direct_vm.sender = direct_alice
    direct_vm.value = 10**16
    contract.commit_source_attempt(
        1, _commitment(direct_alice, salt, scenario, rule, impact),
        evidence_url, hashlib.sha256(evidence_body.encode()).hexdigest(), 'EVIDENCE-V1',
    )
    contract.reveal_source_attempt(1, salt, scenario, rule, impact)
    direct_vm.sender = direct_alice
    direct_vm.value = 0
    contract.start_review(1)
    contract.adjudicate_review(1, 1, 1)
    direct_vm.sender = direct_owner
    contract.propose_repair(
        1, 1, 1, revised_rule, revised_limitations,
        'This correction is intended to close the original exploit.', revised_url,
        hashlib.sha256(revised_body.encode()).hexdigest(), 'RULEBOOK-V2',
    )
    contract.start_repair_review(1, 1)
    contract.adjudicate_repair(1, 1, 1)
    proposal = json.loads(contract.get_repair_proposal(1))
    version = json.loads(contract.get_policy_version(1, 2))
    assert proposal['status'] == 'INCONCLUSIVE'
    assert proposal['evidence_state'] == 'UNVERIFIED'
    assert version['status'] == 'INCONCLUSIVE'
    assert json.loads(contract.get_challenge(1))['authoritative_version'] == '1'


def test_v2_source_backed_repair_authenticates_all_frozen_bytes(
        direct_vm, direct_deploy, direct_owner, direct_alice):
    direct_vm._chain_id = 61999
    direct_vm.mock_llm(
        r'(?s).*Derive the verdict mechanically.*',
        json.dumps({
            'letter': 'PROVEN', 'purpose': 'PROVEN', 'feasible': 'PROVEN',
            'reason': 'The exact conditions are met and the documented sequence is feasible.',
        }),
    )
    contract = direct_deploy('contracts/LoopholeV2.py')
    goal = 'Reward genuinely new educational contributions rather than repeated text.'
    rule = 'Award points to any public post with at least five words and one source link.'
    limitations = 'The post must add a new explanation of the linked source.'
    original_url = 'https://raw.githubusercontent.com/example/rules/' + 'a' * 40 + '/rulebook.txt'
    evidence_url = 'https://raw.githubusercontent.com/example/evidence/' + 'b' * 40 + '/attempt.txt'
    revised_url = 'https://raw.githubusercontent.com/example/rules/' + 'c' * 40 + '/rulebook.txt'
    original_body = 'RULEBOOK-V1\n' + goal + '\n' + rule + '\n' + limitations + '\n'
    evidence_body = 'EVIDENCE-V1\nThe exact winning educational post is frozen.\n'
    revised_rule = 'Award points only when a public post includes a source link and a new explanation.'
    revised_limitations = limitations + ' The explanation must add context.'
    revised_body = 'RULEBOOK-V2\n' + goal + '\n' + revised_rule + '\n' + revised_limitations + '\n'
    direct_vm.mock_web(re.escape(original_url), {'status': 200, 'body': original_body})
    direct_vm.mock_web(re.escape(evidence_url), {'status': 200, 'body': evidence_body})
    direct_vm.mock_web(re.escape(revised_url), {'status': 200, 'body': revised_body})
    direct_vm.sender = direct_owner
    direct_vm.value = 2 * 10**16
    contract.create_source_challenge(
        'V2 pinned repair positive', goal, rule, limitations, 'CONTENT', 86400, 10**16,
        original_url, hashlib.sha256(original_body.encode()).hexdigest(), 'RULEBOOK-V1',
    )
    scenario = 'Publish a qualifying post and add a misleading explanation that defeats the goal.'
    impact = 'The post satisfies the literal conditions while defeating the educational purpose.'
    salt = 'v2-source-positive-salt'
    direct_vm.sender = direct_alice
    direct_vm.value = 10**16
    contract.commit_source_attempt(
        1, _commitment(direct_alice, salt, scenario, rule, impact),
        evidence_url, hashlib.sha256(evidence_body.encode()).hexdigest(), 'EVIDENCE-V1',
    )
    contract.reveal_source_attempt(1, salt, scenario, rule, impact)
    direct_vm.value = 0
    contract.start_review(1)
    contract.adjudicate_review(1, 1, 1)
    direct_vm.sender = direct_owner
    contract.propose_repair(
        1, 1, 1, revised_rule, revised_limitations,
        'This correction closes the original exploit while preserving education.', revised_url,
        hashlib.sha256(revised_body.encode()).hexdigest(), 'RULEBOOK-V2',
    )
    direct_vm.mock_llm(
        r'(?s).*CLOSURE.*Derive the economic result mechanically.*',
        json.dumps({
            'closure': 'PROVEN', 'goal': 'PROVEN', 'coherence': 'PROVEN',
            'reason': 'Authenticated original, winning and revised bytes support the repair.',
        }),
    )
    contract.start_repair_review(1, 1)
    contract.adjudicate_repair(1, 1, 1)
    proposal = json.loads(contract.get_repair_proposal(1))
    assert proposal['status'] == 'VERIFIED_FIX'
    assert proposal['evidence_state'] == 'VERIFIED'
    assert json.loads(contract.get_challenge(1))['authoritative_version'] == '2'


def test_v2_unknown_findings_are_inconclusive_and_do_not_change_authority(
        direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, goal, rule, limitations = _prepare_valid_challenge(
        direct_vm, direct_deploy, direct_owner, direct_alice)
    _propose(contract, direct_vm, direct_owner, goal, rule, limitations)
    direct_vm.mock_llm(
        r'(?s).*CLOSURE.*Derive the economic result mechanically.*',
        json.dumps({
            'closure': 'UNKNOWN', 'goal': 'UNKNOWN', 'coherence': 'UNKNOWN',
            'reason': 'The frozen material is insufficient to prove closure, purpose preservation, or feasibility.',
        }),
    )
    contract.start_repair_review(1, 1)
    contract.adjudicate_repair(1, 1, 1)
    proposal = json.loads(contract.get_repair_proposal(1))
    assert proposal['verdict'] == 'INCONCLUSIVE'
    assert json.loads(contract.get_challenge(1))['authoritative_version'] == '1'


def test_v2_goal_defeat_is_not_verified_even_when_closure_is_proven(
        direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, goal, rule, limitations = _prepare_valid_challenge(
        direct_vm, direct_deploy, direct_owner, direct_alice)
    _propose(contract, direct_vm, direct_owner, goal, rule, limitations,
             'Award points only to no public posts at all, so the original loophole cannot be used.')
    direct_vm.mock_llm(
        r'(?s).*CLOSURE.*Derive the economic result mechanically.*',
        json.dumps({
            'closure': 'PROVEN', 'goal': 'DISPROVEN', 'coherence': 'PROVEN',
            'reason': 'The revision blocks the exploit only by making the intended public activity impossible.',
        }),
    )
    contract.start_repair_review(1, 1)
    contract.adjudicate_repair(1, 1, 1)
    assert json.loads(contract.get_repair_proposal(1))['status'] == 'NOT_VERIFIED'
    assert json.loads(contract.get_policy_version(1, 2))['authoritative'] is False


def test_v2_malformed_assessment_is_fail_closed_and_replay_is_idempotent(
        direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, goal, rule, limitations = _prepare_valid_challenge(
        direct_vm, direct_deploy, direct_owner, direct_alice)
    _propose(contract, direct_vm, direct_owner, goal, rule, limitations)
    direct_vm.mock_llm(
        r'(?s).*CLOSURE.*Derive the economic result mechanically.*',
        json.dumps({'closure': 'PROVEN', 'goal': 'PROVEN', 'coherence': 'PROVEN', 'reason': 'too short'}),
    )
    contract.start_repair_review(1, 1)
    contract.adjudicate_repair(1, 1, 1)
    assert json.loads(contract.get_repair_proposal(1))['verdict'] == 'INCONCLUSIVE'
    assert json.loads(contract.get_challenge(1))['active_repair_proposal'] == '0'
    assert contract.repair_adjudication_count == 1
    # A repeated call for the same finalized round is a no-op, not a second settlement.
    contract.adjudicate_repair(1, 1, 1)
    assert contract.repair_adjudication_count == 1


def test_v2_stalled_repair_recovers_without_authorizing_the_revision(
        direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, goal, rule, limitations = _prepare_valid_challenge(
        direct_vm, direct_deploy, direct_owner, direct_alice)
    _propose(contract, direct_vm, direct_owner, goal, rule, limitations)
    contract.start_repair_review(1, 1)
    direct_vm.warp('2030-01-01T00:00:00Z')
    contract.recover_stalled_repair(1)
    proposal = json.loads(contract.get_repair_proposal(1))
    challenge = json.loads(contract.get_challenge(1))
    assert proposal['status'] == 'INCONCLUSIVE'
    assert proposal['evidence_state'] == 'UNRESOLVED_TIMEOUT'
    assert challenge['active_repair_proposal'] == '0'
    assert challenge['authoritative_version'] == '1'
