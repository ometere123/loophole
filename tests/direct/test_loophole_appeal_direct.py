"""Genuine GenVM Direct Mode exercise of the active monolith's bonded appeal.

The LLM is mocked; these are not live Studionet receipts.
"""
import hashlib
import json


def test_bonded_invalid_appeal_upheld_without_duplicate_credit(
        direct_vm, direct_deploy, direct_owner, direct_alice):
    direct_vm._chain_id = 61999
    direct_vm.mock_llm(
        r'.*Return only this JSON shape.*',
        json.dumps({
            'letter': 'DISPROVEN', 'purpose': 'PROVEN', 'feasible': 'PROVEN',
            'reason': 'The attempt fails a material frozen written eligibility condition.',
        }),
    )
    contract = direct_deploy('contracts/Loophole.py')
    direct_vm.sender = direct_owner
    direct_vm.value = 2 * 10**18
    rule = 'A member earns 10 points when they publish a post containing #OurCampaign and at least 100 words.'
    contract.create_challenge(
        'Direct appeal challenge',
        'Reward genuinely original educational contributions to the campaign.',
        rule,
        'Posts must be newly written by the member.', 'CONTENT', 86400, 10**16,
    )
    direct_vm.sender = direct_alice
    direct_vm.value = 10**16
    salt = 'direct-appeal-salt'
    scenario = 'I publish a qualifying post that satisfies the literal condition but does not create original educational value.'
    impact = 'Mechanical repetition can meet a measurable eligibility condition while defeating the educational goal.'
    address = ('0x' + direct_alice.hex()).lower() if isinstance(direct_alice, bytes) else str(direct_alice).lower()
    fields = ['1', address, salt, scenario, rule, impact]
    commitment = hashlib.sha256(''.join(f'{len(f.encode("utf-8"))}:{f}' for f in fields).encode()).hexdigest()
    contract.commit_attempt(1, commitment)
    direct_vm.value = 0
    contract.reveal_attempt(1, salt, scenario, rule, impact)
    contract.start_review(1)
    contract.adjudicate_review(1, 1, 1)
    assert json.loads(contract.get_attempt(1))['status'] == 'INVALID_PENDING'
    direct_vm.value = 10**16
    contract.appeal_invalid(1)
    assert json.loads(contract.get_attempt(1))['status'] == 'APPEAL_REVIEWING'
    direct_vm.value = 0
    contract.adjudicate_review(1, 1, 2)
    verdict = json.loads(contract.get_attempt(1))
    state = json.loads(contract.get_config())
    assert verdict['status'] == 'DECIDED' and verdict['verdict'] == 'INVALID'
    assert verdict['appeal_used'] is True
    assert contract.get_credit(direct_owner) == 2 * 10**16
    assert contract.get_credit(direct_alice) == 0
    assert state['total_credit_wei'] == str(2 * 10**16)
    assert state['total_locked_wei'] == str(2 * 10**18)
    contract.adjudicate_review(1, 1, 2)
    assert contract.get_credit(direct_owner) == 2 * 10**16
