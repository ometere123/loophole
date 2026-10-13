"""Simulator coverage for the single-contract release candidate.

These tests exercise the state machine and accounting without claiming that the
simulator proves hosted validator execution. Real GenVM coverage is separate.
"""

import hashlib
import importlib.util
import json
import types
from pathlib import Path

import pytest



class Address(str):
    def __new__(cls, value):
        value = str(value).lower()
        if not value.startswith('0x') or len(value) != 42:
            raise ValueError('bad address')
        return str.__new__(cls, value)


ROOT = Path(__file__).parents[1]


def _load_monolith():
    spec = importlib.util.spec_from_file_location('fake_loophole', ROOT / 'contracts' / 'Loophole.py')
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.Loophole


@pytest.fixture
def monolith(world):
    Contract = _load_monolith()
    w = world
    w.gl.contracts = {}
    w.gl.pending = []
    w.vaddr = Address('0x' + 'b' * 40)
    w.gl.message = types.SimpleNamespace(
        sender_address=w.owner, contract_address=w.vaddr, value=0, chain_id=61999
    )
    w.vault = Contract()
    w.gl.contracts[str(w.vaddr)] = w.vault
    w.judge = None
    w.jaddr = None
    return w


def _attack(challenge_id, sender, salt='abcd012345678901'):
    scenario = 'I repeat meaningless words over one hundred times with the hashtag, farming a reward without original content.'
    quote = 'Every member who publishes a post of at least 100 words'
    impact = 'The post meets the length rule but violates the original educational contribution objective.'
    fields = [str(challenge_id), str(sender).lower(), salt, scenario, quote, impact]
    preimage = ''.join(f'{len(field.encode("utf-8"))}:{field}' for field in fields)
    return hashlib.sha256(preimage.encode()).hexdigest(), (salt, scenario, quote, impact)


def _fund(w):
    w.run(w.vaddr, w.owner, 'create_challenge', 'Originality Trap',
          'Reward only genuinely original contributions to this campaign.',
          'Every member who publishes a post of at least 100 words with #OURCAMPAIGN earns points.',
          'Posts must happen during the campaign.', 'CONTENT', 86400, 10**16,
          value=2 * 10**18)


def _revealed(w):
    digest, payload = _attack(1, w.alice)
    w.run(w.vaddr, w.alice, 'commit_attempt', 1, digest, value=10**16)
    w.run(w.vaddr, w.alice, 'reveal_attempt', 1, *payload)


def test_direct_review_settles_once_with_tristate_findings(monolith):
    w = monolith
    _fund(w)
    _revealed(w)
    w.gl.nondet.answer = json.dumps({
        'letter': 'DISPROVEN', 'purpose': 'PROVEN', 'feasible': 'PROVEN',
        'reason': 'The written conditions are not all satisfied by the described attack.',
    })
    w.run(w.vaddr, w.bob, 'start_review', 1)
    w.run(w.vaddr, w.bob, 'adjudicate_review', 1, 1, 1)
    challenge = json.loads(w.vault.get_challenge(1))
    attempt = json.loads(w.vault.get_attempt(1))
    case = json.loads(w.vault.get_adjudication('1:1:1'))
    assert challenge['status'] == 'OPEN'
    assert attempt['status'] == 'INVALID_PENDING'
    assert attempt['verdict'] == 'INVALID'
    assert case['letter'] == 'DISPROVEN'
    assert w.vault.total_locked == 2 * 10**18 + 10**16


def test_invalid_consensus_rejects_non_decisive_support_variation(monolith):
    w = monolith
    _fund(w)
    _revealed(w)
    leader = json.dumps({
        'letter': 'DISPROVEN', 'purpose': 'UNKNOWN', 'feasible': 'PROVEN',
        'reason': 'The explicit word-count condition is not satisfied by the attack.',
    })
    validator = json.dumps({
        'letter': 'DISPROVEN', 'purpose': 'DISPROVEN', 'feasible': 'PROVEN',
        'reason': 'The rule failure is decisive even though the purpose is also affected.',
    })
    w.gl.nondet.answers = [leader, validator]
    w.run(w.vaddr, w.owner, 'start_review', 1)
    with pytest.raises(Exception, match='disagreed'):
        w.run(w.vaddr, w.owner, 'adjudicate_review', 1, 1, 1)
    assert json.loads(w.vault.get_attempt(1))['status'] == 'REVIEWING'


def test_invalid_consensus_rejects_different_decisive_findings(monolith):
    w = monolith
    _fund(w)
    _revealed(w)
    leader = json.dumps({
        'letter': 'DISPROVEN', 'purpose': 'UNKNOWN', 'feasible': 'PROVEN',
        'reason': 'The exact written word-count condition is not met.',
    })
    validator = json.dumps({
        'letter': 'PROVEN', 'purpose': 'DISPROVEN', 'feasible': 'PROVEN',
        'reason': 'The stated goal is defeated even though the literal rule is met.',
    })
    w.gl.nondet.answers = [leader, validator]
    w.run(w.vaddr, w.owner, 'start_review', 1)
    with pytest.raises(Exception, match='disagreed'):
        w.run(w.vaddr, w.owner, 'adjudicate_review', 1, 1, 1)
    assert json.loads(w.vault.get_attempt(1))['status'] == 'REVIEWING'


def test_tristate_unknown_is_inconclusive_and_returns_bond(monolith):
    w = monolith
    _fund(w)
    _revealed(w)
    w.gl.nondet.answer = json.dumps({
        'letter': 'PROVEN', 'purpose': 'UNKNOWN', 'feasible': 'PROVEN',
        'reason': 'The frozen material does not establish the claimed purpose conflict.',
    })
    w.run(w.vaddr, w.owner, 'start_review', 1)
    w.run(w.vaddr, w.owner, 'adjudicate_review', 1, 1, 1)
    assert json.loads(w.vault.get_attempt(1))['verdict'] == 'INCONCLUSIVE'
    assert w.vault.get_credit(w.alice) == 10**16
    assert w.vault.total_locked == 2 * 10**18


def test_valid_entitlement_and_duplicate_adjudication_are_one_shot(monolith):
    w = monolith
    _fund(w)
    _revealed(w)
    w.gl.nondet.answer = json.dumps({
        'letter': 'PROVEN', 'purpose': 'PROVEN', 'feasible': 'PROVEN',
        'reason': 'The described sequence satisfies the rule, defeats the goal and is internally feasible.',
    })
    w.run(w.vaddr, w.owner, 'start_review', 1)
    w.run(w.vaddr, w.owner, 'adjudicate_review', 1, 1, 1)
    first = w.vault.get_credit(w.alice)
    w.run(w.vaddr, w.owner, 'adjudicate_review', 1, 1, 1)
    assert json.loads(w.vault.get_challenge(1))['status'] == 'WON'
    assert first == 2 * 10**18 + 10**16
    assert w.vault.get_credit(w.alice) == first


def test_withdrawal_clears_credit_and_emits_exact_recipient_transfer(monolith):
    w = monolith
    _fund(w)
    _revealed(w)
    w.gl.nondet.answer = json.dumps({
        'letter': 'PROVEN', 'purpose': 'PROVEN', 'feasible': 'PROVEN',
        'reason': 'The described sequence satisfies the rule, defeats the goal and is internally feasible.',
    })
    w.run(w.vaddr, w.owner, 'start_review', 1)
    w.run(w.vaddr, w.owner, 'adjudicate_review', 1, 1, 1)
    expected = 2 * 10**18 + 10**16
    w.run(w.vaddr, w.alice, 'withdraw')
    assert w.vault.get_credit(w.alice) == 0
    assert json.loads(w.vault.get_withdrawal(1))['amount_wei'] == str(expected)
    transfer = w.gl.pending[-1]
    assert transfer[:4] == ('TRANSFER', w.vaddr, str(w.alice), expected)


def test_direct_review_rejects_stale_round_and_forged_state(monolith):
    w = monolith
    _fund(w)
    _revealed(w)
    w.run(w.vaddr, w.owner, 'start_review', 1)
    with pytest.raises(Exception, match='stale'):
        w.run(w.vaddr, w.owner, 'adjudicate_review', 1, 1, 2)
    attempt = json.loads(w.vault.get_attempt(1))
    assert attempt['status'] == 'REVIEWING'


def test_commitment_encoding_is_length_prefixed_and_delimiter_safe(monolith):
    w = monolith
    _fund(w)
    salt = 'salt|é|🔒'
    scenario = 'I use a pipe | and Unicode 🔎 inside the described sequence without changing its meaning.'
    quote = 'Every member who publishes a post of at least 100 words'
    impact = 'The result | defeats the stated educational purpose.'
    fields = ['1', str(w.alice).lower(), salt, scenario, quote, impact]
    preimage = ''.join(f'{len(field.encode("utf-8"))}:{field}' for field in fields)
    digest = hashlib.sha256(preimage.encode('utf-8')).hexdigest()
    w.run(w.vaddr, w.alice, 'commit_attempt', 1, digest, value=10**16)
    w.run(w.vaddr, w.alice, 'reveal_attempt', 1, salt, scenario, quote, impact)
    assert json.loads(w.vault.get_attempt(1))['status'] == 'REVEALED'

    aliased = ['1', str(w.alice).lower(), 'salt', 'with', 'delimiters', scenario]
    alias_preimage = ''.join(f'{len(field.encode("utf-8"))}:{field}' for field in aliased)
    assert digest != hashlib.sha256(alias_preimage.encode('utf-8')).hexdigest()


def _source_case(w):
    goal = 'Reward only genuinely original contributions to this campaign.'
    rule = 'Every member who publishes a post of at least 100 words with #OURCAMPAIGN earns points.'
    limitations = 'Posts must happen during the campaign.'
    rule_url = 'https://raw.githubusercontent.com/example/rules/' + 'a' * 40 + '/rulebook.txt'
    evidence_url = 'https://raw.githubusercontent.com/example/evidence/' + 'b' * 40 + '/attempt.txt'
    rule_body = ('RULEBOOK-V1\n' + goal + '\n' + rule + '\n' + limitations + '\n').encode('utf-8')
    evidence_body = b'EVIDENCE-V1\nThe archived post is the claimant evidence snapshot.\n'
    w.gl.nondet.web.responses[rule_url] = (200, rule_body)
    w.gl.nondet.web.responses[evidence_url] = (200, evidence_body)
    w.run(w.vaddr, w.owner, 'create_source_challenge', 'Pinned policy', goal, rule,
          limitations, 'CONTENT', 86400, 10**16, rule_url,
          hashlib.sha256(rule_body).hexdigest(), 'RULEBOOK-V1', value=2 * 10**18)
    digest, payload = _attack(1, w.alice)
    w.run(w.vaddr, w.alice, 'commit_source_attempt', 1, digest, evidence_url,
          hashlib.sha256(evidence_body).hexdigest(), 'EVIDENCE-V1', value=10**16)
    w.run(w.vaddr, w.alice, 'reveal_source_attempt', 1, *payload)
    w.run(w.vaddr, w.owner, 'start_review', 1)
    return rule_url, evidence_url, rule_body, evidence_body


def test_pinned_source_is_authenticated_and_changes_assessment_context(monolith):
    w = monolith
    _source_case(w)
    w.gl.nondet.answer = json.dumps({
        'letter': 'PROVEN', 'purpose': 'UNKNOWN', 'feasible': 'PROVEN',
        'reason': 'The authenticated evidence does not establish the claimed purpose conflict.',
    })
    w.run(w.vaddr, w.owner, 'adjudicate_review', 1, 1, 1)
    attempt = json.loads(w.vault.get_attempt(1))
    adjudication = json.loads(w.vault.get_adjudication('1:1:1'))
    assert attempt['status'] == 'DECIDED'
    assert attempt['verdict'] == 'INCONCLUSIVE'
    assert attempt['evidence_state'] == 'VERIFIED'
    assert adjudication['evidence_state'] == 'VERIFIED'
    assert any('RULEBOOK-V1' in prompt and 'EVIDENCE-V1' in prompt
               for prompt in w.gl.nondet.prompts)


def test_pinned_source_hash_failure_is_inconclusive_without_payout(monolith):
    w = monolith
    _, evidence_url, _, _ = _source_case(w)
    w.gl.nondet.web.responses[evidence_url] = (200, b'EVIDENCE-V1\nsubstituted bytes')
    w.run(w.vaddr, w.owner, 'adjudicate_review', 1, 1, 1)
    attempt = json.loads(w.vault.get_attempt(1))
    assert attempt['status'] == 'DECIDED'
    assert attempt['verdict'] == 'INCONCLUSIVE'
    assert attempt['evidence_state'] == 'UNVERIFIED'
    assert w.vault.get_credit(w.alice) == 10**16
