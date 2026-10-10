"""REAL GenVM Direct Mode coverage; this is separate from tests/test_protocol.py simulator tests."""
import hashlib
import json


def _payload(vm, address):
    salt = 'direct-salt-1234'
    scenario = 'I will publish a qualifying example that satisfies the exact written word-count rule.'
    quote = 'Every member who publishes a post of at least 100 words'
    impact = 'The qualifying post defeats the objective by rewarding mechanically repeated engagement.'
    raw = '|'.join(['1', str(address).lower(), salt, scenario, quote, impact])
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


def test_rulevault_direct_rejects_wrong_chain_and_forged_reveal(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    direct_vm._chain_id = 61998
    with direct_vm.expect_revert('Studionet 61999'):
        direct_deploy('contracts/RuleVault.py', '0x' + 'a' * 40)
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
