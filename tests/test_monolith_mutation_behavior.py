"""Executable mutation tests for the single-contract economic guards."""

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


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.Loophole


def _mutated(world, tmp_path, mutation):
    source = (ROOT / 'contracts' / 'Loophole.py').read_text(encoding='utf-8')
    old, new, *options = mutation
    assert old in source
    if options and options[0] == 'all':
        source = source.replace(old, new)
    elif options and options[0] == 'last':
        offset = source.rfind(old)
        source = source[:offset] + new + source[offset + len(old):]
    else:
        source = source.replace(old, new, 1)
    path = tmp_path / 'Loophole_mutated.py'
    path.write_text(source, encoding='utf-8')
    Contract = _load(path, 'mutated_loophole')
    w = world
    w.gl.contracts = {}
    w.gl.pending = []
    w.vaddr = Address('0x' + 'b' * 40)
    w.gl.message = types.SimpleNamespace(
        sender_address=w.owner, contract_address=w.vaddr, value=0, chain_id=61999
    )
    w.vault = Contract()
    w.gl.contracts[str(w.vaddr)] = w.vault
    return w


def _fund(w):
    w.run(w.vaddr, w.owner, 'create_challenge', 'Originality Trap',
          'Reward only genuinely original contributions to this campaign.',
          'Every member who publishes a post of at least 100 words with #OURCAMPAIGN earns points.',
          'Posts must happen during the campaign.', 'CONTENT', 86400, 10**16,
          value=2 * 10**18)


def _attack(w, salt='abcd012345678901'):
    scenario = 'I repeat meaningless words over one hundred times with the hashtag, farming a reward without original content.'
    quote = 'Every member who publishes a post of at least 100 words'
    impact = 'The post meets the length rule but violates the original educational contribution objective.'
    fields = ['1', str(w.alice).lower(), salt, scenario, quote, impact]
    preimage = ''.join(f'{len(field.encode("utf-8"))}:{field}' for field in fields)
    return hashlib.sha256(preimage.encode()).hexdigest(), (salt, scenario, quote, impact)


def _revealed(w):
    digest, payload = _attack(w)
    w.run(w.vaddr, w.alice, 'commit_attempt', 1, digest, value=10**16)
    w.run(w.vaddr, w.alice, 'reveal_attempt', 1, *payload)


def _valid(w):
    w.gl.nondet.answer = json.dumps({
        'letter': 'PROVEN', 'purpose': 'PROVEN', 'feasible': 'PROVEN',
        'reason': 'The described sequence satisfies the rule, defeats the goal and is internally feasible.',
    })


def test_mutated_stale_round_guard_would_settle_wrong_round(world, tmp_path):
    old = "        if c['active_attempt'] != str(int(attempt_id)) or c['active_round'] != str(int(round_id)):\n            raise gl.vm.UserError('review round is stale')"
    w = _mutated(world, tmp_path, (old, "        if False:\n            raise gl.vm.UserError('review round is stale')", 'all'))
    _fund(w); _revealed(w); _valid(w)
    w.run(w.vaddr, w.owner, 'start_review', 1)
    c = json.loads(w.vault.get_challenge(1)); c['active_round'] = '2'; w.vault.challenges[1] = json.dumps(c)
    w.run(w.vaddr, w.owner, 'adjudicate_review', 1, 1, 1)
    assert json.loads(w.vault.get_challenge(1))['status'] == 'WON'


def test_mutated_commitment_guard_accepts_wrong_reveal(world, tmp_path):
    old = "        if hashlib.sha256(plaintext.encode('utf-8')).hexdigest() != a['commitment']:\n            raise gl.vm.UserError('commitment does not match revealed attack')"
    w = _mutated(world, tmp_path, (old, "        if False:\n            raise gl.vm.UserError('commitment does not match revealed attack')"))
    _fund(w)
    digest, payload = _attack(w)
    w.run(w.vaddr, w.alice, 'commit_attempt', 1, digest, value=10**16)
    w.run(w.vaddr, w.alice, 'reveal_attempt', 1, 'wrong-salt-1234', *payload[1:])
    assert json.loads(w.vault.get_attempt(1))['status'] == 'REVEALED'


def test_mutated_refund_guard_releases_revealed_right(world, tmp_path):
    old = "            if a['status'] in ('REVEALED', 'REVIEWING', 'INVALID_PENDING', 'APPEAL_REVIEWING', 'COMMITTED'):"
    w = _mutated(world, tmp_path, (old, "            if False:"))
    _fund(w); _revealed(w)
    c = json.loads(w.vault.get_challenge(1)); c['reveal_deadline'] = 0; w.vault.challenges[1] = json.dumps(c)
    w.run(w.vaddr, w.owner, 'refund_unwon', 1)
    assert json.loads(w.vault.get_challenge(1))['status'] == 'REFUNDED'


def test_mutated_withdraw_guard_emits_zero_unauthorized_transfer(world, tmp_path):
    old = "        if amount == u256(0):\n            raise gl.vm.UserError('no claimable GEN')"
    w = _mutated(world, tmp_path, (old, "        if False:\n            raise gl.vm.UserError('no claimable GEN')"))
    _fund(w)
    w.run(w.vaddr, w.bob, 'withdraw')
    assert w.vault.withdrawal_count == 1
    assert json.loads(w.vault.get_withdrawal(1))['amount_wei'] == '0'


def test_mutated_appeal_recipient_pays_invalid_bond_to_challenger(world, tmp_path):
    old = "            recipient = c['organizer'] if result['verdict'] == 'INVALID' else a['challenger']"
    w = _mutated(world, tmp_path, (old, "            recipient = a['challenger']"))
    _fund(w); _revealed(w)
    w.gl.nondet.answer = json.dumps({
        'letter': 'DISPROVEN', 'purpose': 'PROVEN', 'feasible': 'PROVEN',
        'reason': 'The written conditions are not all satisfied by the described attack.',
    })
    w.run(w.vaddr, w.owner, 'start_review', 1)
    w.run(w.vaddr, w.owner, 'adjudicate_review', 1, 1, 1)
    w.run(w.vaddr, w.alice, 'appeal_invalid', 1, value=10**16)
    w.gl.nondet.answer = json.dumps({
        'letter': 'DISPROVEN', 'purpose': 'PROVEN', 'feasible': 'PROVEN',
        'reason': 'The appeal remains unsupported by the frozen policy.',
    })
    w.run(w.vaddr, w.owner, 'adjudicate_review', 1, 1, 2)
    assert w.vault.get_credit(w.alice) == 2 * 10**16


def test_monolith_has_no_forged_callback_surface():
    source = (ROOT / 'contracts' / 'Loophole.py').read_text(encoding='utf-8')
    assert 'def record_verdict' not in source
    assert 'def bind_vault' not in source
    assert 'get_contract_at' not in source
    assert "emit(on='finalized')" not in source
