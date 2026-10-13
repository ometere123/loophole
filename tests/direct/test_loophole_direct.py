"""Real GenVM Direct Mode coverage for the single-contract release candidate."""

import hashlib
import json
import re


def _source_payload(address):
    goal = 'Reward genuinely original educational contributions to the campaign.'
    rule = 'A member earns 10 points when they publish a post containing #OurCampaign and at least 100 words.'
    limitations = 'Posts must be newly written by the member.'
    rule_url = 'https://raw.githubusercontent.com/example/rules/' + 'a' * 40 + '/rulebook.txt'
    evidence_url = 'https://raw.githubusercontent.com/example/evidence/' + 'b' * 40 + '/attempt.txt'
    rule_body = 'RULEBOOK-V1\n' + goal + '\n' + rule + '\n' + limitations + '\n'
    evidence_body = 'EVIDENCE-V1\nThe archived post is the claimant evidence snapshot.\n'
    salt = 'direct-source-salt'
    scenario = 'I publish a qualifying post that satisfies the literal condition but does not create original educational value.'
    quote = rule
    impact = 'Mechanical repetition can satisfy the measurable condition while defeating the stated educational goal.'
    sender = ('0x' + address.hex()) if isinstance(address, bytes) else str(address).lower()
    fields = ['1', sender, salt, scenario, quote, impact]
    raw = ''.join(f'{len(field.encode("utf-8"))}:{field}' for field in fields)
    commitment = hashlib.sha256(raw.encode()).hexdigest()
    return {
        'goal': goal, 'rule': rule, 'limitations': limitations,
        'rule_url': rule_url, 'rule_body': rule_body,
        'rule_sha256': hashlib.sha256(rule_body.encode()).hexdigest(),
        'rule_version': 'RULEBOOK-V1', 'evidence_url': evidence_url,
        'evidence_body': evidence_body,
        'evidence_sha256': hashlib.sha256(evidence_body.encode()).hexdigest(),
        'evidence_version': 'EVIDENCE-V1',
        'commitment': commitment,
        'reveal': (salt, scenario, quote, impact),
    }


def _payload(address):
    from genlayer.py.types import Address
    salt = 'direct-salt-1234'
    scenario = 'I publish a qualifying post that satisfies the literal condition but does not create original educational value.'
    quote = 'A member earns 10 points when they publish a post containing #OurCampaign and at least 100 words.'
    impact = 'Mechanical repetition can satisfy the measurable condition while defeating the stated educational goal.'
    fields = ['1', Address(address).as_hex.lower(), salt, scenario, quote, impact]
    raw = ''.join(f'{len(field.encode("utf-8"))}:{field}' for field in fields)
    return hashlib.sha256(raw.encode()).hexdigest(), (salt, scenario, quote, impact)


def test_loophole_direct_freeze_and_atomic_inconclusive(direct_vm, direct_deploy, direct_owner, direct_alice):
    direct_vm._chain_id = 61999
    direct_vm.mock_llm(
        r'.*Return only this JSON shape.*',
        json.dumps({
            'letter': 'PROVEN', 'purpose': 'UNKNOWN', 'feasible': 'PROVEN',
            'reason': 'The frozen material does not establish the claimed purpose conflict.',
        }),
    )
    loophole = direct_deploy('contracts/Loophole.py')
    direct_vm.sender = direct_owner
    direct_vm.value = 2 * 10**18
    loophole.create_challenge(
        'Direct challenge',
        'Reward genuinely original educational contributions to the campaign.',
        'A member earns 10 points when they publish a post containing #OurCampaign and at least 100 words.',
        'Posts must be newly written by the member.', 'CONTENT', 86400, 10**16,
    )
    direct_vm.sender = direct_alice
    direct_vm.value = 10**16
    commitment, payload = _payload(direct_alice)
    loophole.commit_attempt(1, commitment)
    loophole.reveal_attempt(1, *payload)
    loophole.start_review(1)
    loophole.adjudicate_review(1, 1, 1)
    attempt = json.loads(loophole.get_attempt(1))
    challenge = json.loads(loophole.get_challenge(1))
    assert attempt['verdict'] == 'INCONCLUSIVE'
    assert attempt['status'] == 'DECIDED'
    assert challenge['active_attempt'] == '0'
    assert loophole.get_credit(direct_alice) == 10**16


def test_loophole_direct_withdraw_records_unverified_transfer(direct_vm, direct_deploy, direct_owner, direct_alice):
    direct_vm._chain_id = 61999
    direct_vm.mock_llm(
        r'.*Return only this JSON shape.*',
        json.dumps({
            'letter': 'PROVEN', 'purpose': 'UNKNOWN', 'feasible': 'PROVEN',
            'reason': 'The frozen material does not establish the claimed purpose conflict.',
        }),
    )
    loophole = direct_deploy('contracts/Loophole.py')
    direct_vm.sender = direct_owner
    direct_vm.value = 2 * 10**18
    loophole.create_challenge(
        'Direct withdrawal challenge',
        'Reward genuinely original educational contributions to the campaign.',
        'A member earns 10 points when they publish a post containing #OurCampaign and at least 100 words.',
        'Posts must be newly written by the member.', 'CONTENT', 86400, 10**16,
    )
    direct_vm.sender = direct_alice
    direct_vm.value = 10**16
    commitment, payload = _payload(direct_alice)
    loophole.commit_attempt(1, commitment)
    loophole.reveal_attempt(1, *payload)
    loophole.start_review(1)
    loophole.adjudicate_review(1, 1, 1)
    direct_vm.sender = direct_alice
    direct_vm.value = 0
    loophole.withdraw()
    withdrawal = json.loads(loophole.get_withdrawal(1))
    assert withdrawal['amount_wei'] == str(10**16)
    assert withdrawal['status'] == 'TRANSFER_EMITTED_UNVERIFIED'
    assert loophole.get_credit(direct_alice) == 0


def test_loophole_direct_wrong_chain_is_rejected(direct_vm, direct_deploy):
    direct_vm._chain_id = 61998
    with direct_vm.expect_revert('Studionet 61999'):
        direct_deploy('contracts/Loophole.py')


def test_loophole_direct_pinned_source_is_verified_by_each_execution(
        direct_vm, direct_deploy, direct_owner, direct_alice):
    direct_vm._chain_id = 61999
    case = _source_payload(direct_alice)
    direct_vm.mock_web(re.escape(case['rule_url']), {
        'status': 200, 'body': case['rule_body'],
    })
    direct_vm.mock_web(re.escape(case['evidence_url']), {
        'status': 200, 'body': case['evidence_body'],
    })
    direct_vm.mock_llm(
        r'.*Return only this JSON shape.*',
        json.dumps({
            'letter': 'PROVEN', 'purpose': 'UNKNOWN', 'feasible': 'PROVEN',
            'reason': 'The authenticated source does not establish the purpose conflict.',
        }),
    )
    loophole = direct_deploy('contracts/Loophole.py')
    direct_vm.sender = direct_owner
    direct_vm.value = 2 * 10**18
    loophole.create_source_challenge(
        'Pinned source challenge', case['goal'], case['rule'], case['limitations'],
        'CONTENT', 86400, 10**16, case['rule_url'], case['rule_sha256'],
        case['rule_version'],
    )
    direct_vm.sender = direct_alice
    direct_vm.value = 10**16
    loophole.commit_source_attempt(
        1, case['commitment'], case['evidence_url'], case['evidence_sha256'],
        case['evidence_version'],
    )
    loophole.reveal_source_attempt(1, *case['reveal'])
    direct_vm.value = 0
    loophole.start_review(1)
    loophole.adjudicate_review(1, 1, 1)
    attempt = json.loads(loophole.get_attempt(1))
    adjudication = json.loads(loophole.get_adjudication('1:1:1'))
    assert attempt['verdict'] == 'INCONCLUSIVE'
    assert attempt['evidence_state'] == 'VERIFIED'
    assert adjudication['evidence_state'] == 'VERIFIED'
    assert loophole.get_credit(direct_alice) == 10**16


def test_loophole_direct_pinned_source_hash_failure_pays_no_prize(
        direct_vm, direct_deploy, direct_owner, direct_alice):
    direct_vm._chain_id = 61999
    case = _source_payload(direct_alice)
    direct_vm.mock_web(re.escape(case['rule_url']), {
        'status': 200, 'body': case['rule_body'],
    })
    direct_vm.mock_web(re.escape(case['evidence_url']), {
        'status': 200, 'body': 'EVIDENCE-V1\nsubstituted bytes',
    })
    loophole = direct_deploy('contracts/Loophole.py')
    direct_vm.sender = direct_owner
    direct_vm.value = 2 * 10**18
    loophole.create_source_challenge(
        'Pinned source failure', case['goal'], case['rule'], case['limitations'],
        'CONTENT', 86400, 10**16, case['rule_url'], case['rule_sha256'],
        case['rule_version'],
    )
    direct_vm.sender = direct_alice
    direct_vm.value = 10**16
    loophole.commit_source_attempt(
        1, case['commitment'], case['evidence_url'], case['evidence_sha256'],
        case['evidence_version'],
    )
    loophole.reveal_source_attempt(1, *case['reveal'])
    direct_vm.value = 0
    loophole.start_review(1)
    loophole.adjudicate_review(1, 1, 1)
    attempt = json.loads(loophole.get_attempt(1))
    assert attempt['verdict'] == 'INCONCLUSIVE'
    assert attempt['evidence_state'] == 'UNVERIFIED'
    assert loophole.get_credit(direct_alice) == 10**16


def test_loophole_direct_pinned_source_valid_settles_bounty_and_bond(
        direct_vm, direct_deploy, direct_owner, direct_alice):
    """Actual GenVM execution covers a source-backed VALID economic branch."""
    direct_vm._chain_id = 61999
    case = {
        'goal': 'Reward a genuinely new educational contribution rather than repeated text.',
        'rule': 'Award 10 points to any public post with at least five words and one source link.',
        'limitations': 'The post must add a new explanation of the linked source; repeating an earlier post without a new explanation is not eligible.',
        'rule_url': 'https://raw.githubusercontent.com/example/rules/' + 'a' * 40 + '/rulebook.txt',
        'rule_body': (
            '# LOOPHOLE source-backed rulebook\n'
            'VERSION: loophole-source-backed-demo-v1\n'
            'Goal: Reward a genuinely new educational contribution rather than repeated text.\n'
            'Rule: Award 10 points to any public post with at least five words and one source link.\n'
            'Limitations: The post must add a new explanation of the linked source; repeating an earlier post without a new explanation is not eligible.\n'
        ),
        'evidence_url': 'https://raw.githubusercontent.com/example/evidence/' + 'b' * 40 + '/valid-attempt.txt',
        'evidence_body': (
            'VERSION: loophole-source-backed-valid-evidence-v1\n'
            'The public post contains six words and one source link. It adds a new '
            'explanation of the linked source, but the explanation deliberately '
            'reverses the source\'s conclusion while presenting the reversal as education.\n'
        ),
        'rule_version': 'loophole-source-backed-demo-v1',
        'evidence_version': 'loophole-source-backed-valid-evidence-v1',
    }
    case['rule_sha256'] = hashlib.sha256(case['rule_body'].encode()).hexdigest()
    case['evidence_sha256'] = hashlib.sha256(case['evidence_body'].encode()).hexdigest()
    direct_vm.mock_web(re.escape(case['rule_url']), {
        'status': 200, 'body': case['rule_body'],
    })
    direct_vm.mock_web(re.escape(case['evidence_url']), {
        'status': 200, 'body': case['evidence_body'],
    })
    direct_vm.mock_llm(
        r'.*Return only this JSON shape.*',
        json.dumps({
            'letter': 'PROVEN', 'purpose': 'PROVEN', 'feasible': 'PROVEN',
            'reason': 'The exact conditions are met, the deliberate reversal defeats the educational goal, and the sequence is possible.',
        }),
    )
    loophole = direct_deploy('contracts/Loophole.py')
    direct_vm.sender = direct_owner
    direct_vm.value = 2 * 10**16
    loophole.create_source_challenge(
        'Pinned valid source challenge', case['goal'], case['rule'],
        case['limitations'], 'CONTENT', 86400, 10**16,
        case['rule_url'], case['rule_sha256'], case['rule_version'],
    )
    direct_vm.sender = direct_alice
    direct_vm.value = 10**16
    salt = 'direct-valid-source-salt'
    scenario = (
        'Publish a public post with six words and one source link, then add a new '
        "explanation that deliberately reverses the linked source's conclusion "
        'while presenting the reversal as education; do not copy an earlier post.'
    )
    quote = case['rule']
    impact = (
        'The post meets the five-word and source-link conditions and adds a new '
        'explanation, but the intentionally reversed explanation defeats the goal '
        'of a genuine educational contribution.'
    )
    sender = ('0x' + direct_alice.hex()).lower()
    fields = ['1', sender, salt, scenario, quote, impact]
    preimage = ''.join(f'{len(field.encode("utf-8"))}:{field}' for field in fields)
    commitment = hashlib.sha256(preimage.encode()).hexdigest()
    loophole.commit_source_attempt(
        1, commitment, case['evidence_url'], case['evidence_sha256'],
        case['evidence_version'],
    )
    loophole.reveal_source_attempt(1, salt, scenario, quote, impact)
    direct_vm.value = 0
    loophole.start_review(1)
    loophole.adjudicate_review(1, 1, 1)
    attempt = json.loads(loophole.get_attempt(1))
    challenge = json.loads(loophole.get_challenge(1))
    assert attempt['verdict'] == 'VALID'
    assert attempt['status'] == 'DECIDED'
    assert attempt['evidence_state'] == 'VERIFIED'
    assert challenge['status'] == 'WON'
    assert challenge['winner'] == sender
    assert loophole.get_credit(direct_alice) == 3 * 10**16
