"""REAL GenVM Direct Mode coverage; this is separate from tests/test_protocol.py simulator tests."""
import hashlib
import json


def _payload(vm, address):
    from genlayer.py.types import Address
    salt = 'direct-salt-1234'
    scenario = 'I will publish a qualifying example that satisfies the exact written word-count rule.'
    quote = 'Every member who publishes a post of at least 100 words'
    impact = 'The qualifying post defeats the objective by rewarding mechanically repeated engagement.'
    raw = '|'.join(['1', Address(address).as_hex.lower(), salt, scenario, quote, impact])
    return hashlib.sha256(raw.encode()).hexdigest(), (salt, scenario, quote, impact)


def test_rulevault_direct_create_commit_reveal(direct_vm, direct_deploy, direct_owner, direct_alice):
    direct_vm._chain_id = 61999
    vault = direct_deploy('contracts/RuleVault.py', '0x' + 'a' * 40)
    direct_vm.sender = direct_owner
    direct_vm.value = 2 * 10**18
    vault.create_challenge(
        'Direct challenge',
        'Reward genuinely original contributions to the campaign.',
        'Every member who publishes a post of at least 100 words',
        'Posts must be made during the campaign.', 'CONTENT', 86400, 10**16,
    )
    direct_vm.sender = direct_alice
    direct_vm.value = 10**16
    commitment, payload = _payload(direct_vm, direct_alice)
    vault.commit_attempt(1, commitment)
    vault.reveal_attempt(1, *payload)
    attempt = json.loads(vault.get_attempt(1))
    assert attempt['status'] == 'REVEALED'
    assert len(attempt['evidence_hash']) == 64


def test_rulevault_direct_rejects_wrong_chain(direct_vm, direct_deploy):
    direct_vm._chain_id = 61998
    with direct_vm.expect_revert('Studionet 61999'):
        direct_deploy('contracts/RuleVault.py', '0x' + 'a' * 40)


def test_rulevault_direct_rejects_forged_reveal(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    direct_vm._chain_id = 61999
    vault = direct_deploy('contracts/RuleVault.py', '0x' + 'a' * 40)
    direct_vm.sender = direct_owner
    direct_vm.value = 10**16
    vault.create_challenge('Direct challenge', 'A sufficiently specific objective for testing.',
                           'Every member who publishes a post of at least 100 words',
                           '', 'CONTENT', 86400, 10**14)
    direct_vm.sender = direct_alice
    direct_vm.value = 10**14
    commitment, payload = _payload(direct_vm, direct_alice)
    vault.commit_attempt(1, commitment)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert('original challenger'):
        vault.reveal_attempt(1, *payload)


def test_gapjudge_direct_validates_frozen_evidence_hash(direct_vm, direct_deploy, direct_owner, direct_alice):
    direct_vm._chain_id = 61999
    judge = direct_deploy('contracts/GapJudge.py')
    direct_vm.sender = direct_owner
    judge.bind_vault('0x' + 'b' * 40)
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert('only bound vault'):
        judge.adjudicate(1, 1, 1, '0' * 64, 'A rule text that is long enough for validation.',
                         'An explicit goal that is long enough for validation.', '',
                         'A scenario that contains enough concrete attack steps to validate.',
                         'A rule', 'A specific impact statement for validation.')


def test_gapjudge_direct_substantive_verdict(direct_vm, direct_deploy, direct_owner, direct_alice):
    """Exercise the real GapJudge assessment and validator agreement path."""
    direct_vm._chain_id = 61999
    direct_vm.mock_llm(
        r'.*Return ONLY a compact JSON object.*',
        json.dumps({
            'verdict': 'INVALID',
            'letter': True,
            'purpose': False,
            'feasible': True,
            'reason': 'The literal condition is met while the stated educational purpose is defeated.',
        }),
    )
    judge = direct_deploy('contracts/GapJudge.py')
    vault_address = '0x' + direct_alice.hex()
    direct_vm.sender = direct_owner
    judge.bind_vault(vault_address)
    direct_vm.sender = direct_alice

    rule = 'A member earns 10 points when they publish a post containing #OurCampaign and at least 100 words.'
    goal = 'Reward members who publish an original educational post that explains a topic clearly and helps readers learn.'
    limitations = 'Posts must be newly written by the member.'
    scenario = (
        'I publish a 100-word post made by repeating the same harmless sentence and include #OurCampaign. '
        'It meets the literal hashtag and word-count conditions, but it does not explain a topic or provide educational value.'
    )
    rule_quote = 'A member earns 10 points when they publish a post containing #OurCampaign and at least 100 words.'
    impact = 'The literal rule awards points for meaningless repetition, so an ineligible post can satisfy the measurable conditions while violating the stated educational purpose.'
    frozen = {
        'goal': goal,
        'published_rule': rule,
        'limitations': limitations,
        'claimed_rule_quote': rule_quote,
        'attack_sequence': scenario,
        'claimed_harm': impact,
    }
    evidence_hash = hashlib.sha256(
        json.dumps(frozen, sort_keys=True, separators=(',', ':')).encode('utf-8')
    ).hexdigest()

    judge.adjudicate(1, 1, 1, evidence_hash, rule, goal, limitations, scenario, rule_quote, impact)

    case = json.loads(judge.get_case('1:1:1'))
    assert case['verdict'] == 'INVALID'
    assert case['letter'] is True
    assert case['purpose'] is False
    assert case['feasible'] is True
    assert case['evidence_hash'] == evidence_hash
