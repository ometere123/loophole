"""Real GenVM Direct Mode coverage for the single-contract release candidate."""

import hashlib
import json


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
