"""Behavioral mutations for V2's organizer and material-consensus guards.

These tests load deliberately mutated V2 source copies into the deterministic
state-machine harness. The real GenVM Direct Mode tests remain in
tests/direct/test_loophole_v2_direct.py; neither suite treats a source-string
check as proof by itself.
"""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]


def _load_contract(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.LoopholeV2


def _build(world, path: Path, name: str):
    world.gl.contracts = {}
    world.gl.pending = []
    world.vaddr = world.vault_address = type(world.owner)('0x' + 'b' * 40)
    world.gl.nondet.answers = []
    world.gl.nondet.answer = json.dumps({
        'letter': 'PROVEN', 'purpose': 'PROVEN', 'feasible': 'PROVEN',
        'reason': 'The frozen attack satisfies the literal rule, defeats the goal and is feasible.',
    })
    contract = _load_contract(path, name)()
    world.gl.contracts[str(world.vaddr)] = contract
    return contract


def _commitment(address, salt, scenario, quote, impact):
    fields = ['1', str(address).lower(), salt, scenario, quote, impact]
    return hashlib.sha256(''.join(f'{len(field.encode()):d}:{field}' for field in fields).encode()).hexdigest()


def _prepare_won(world, contract):
    goal = 'Reward genuinely new educational contributions rather than repeated text.'
    rule = 'Award points to public posts with at least five words and one source link.'
    limitations = 'The post must add a new explanation of the linked source.'
    scenario = 'Publish six words and one source link, then add a new explanation.'
    impact = 'A misleading explanation can satisfy the literal conditions while defeating education.'
    salt = 'mutation-v2-salt'
    commitment = _commitment(world.alice, salt, scenario, rule, impact)
    world.run(world.vaddr, world.owner, 'create_challenge', 'V2 mutation', goal, rule,
              limitations, 'CONTENT', 86400, 10**16, value=2 * 10**16)
    world.run(world.vaddr, world.alice, 'commit_attempt', 1, commitment, value=10**16)
    world.run(world.vaddr, world.alice, 'reveal_attempt', 1, salt, scenario, rule, impact)
    world.run(world.vaddr, world.owner, 'start_review', 1)
    world.run(world.vaddr, world.owner, 'adjudicate_review', 1, 1, 1)
    assert json.loads(contract.get_challenge(1))['status'] == 'WON'
    return goal, rule, limitations


def _propose(world, contract, goal, limitations):
    world.run(
        world.vaddr, world.owner, 'propose_repair', 1, 1, 1,
        'Award points only when a post includes a source link and a new verifiable explanation.',
        limitations + ' The explanation must materially add context.',
        'This bounded correction closes the exact repeated-text loophole while preserving education.',
        '', '', '',
    )


def test_mutated_v2_organizer_guard_would_allow_unauthorized_repair(tmp_path, world):
    source = (ROOT / 'contracts' / 'LoopholeV2.py').read_text(encoding='utf-8')
    guard = "        if sender != c['organizer']:\n            raise gl.vm.UserError('only the original organizer may propose a repair')"
    mutated = source.replace(guard, "        if False:\n            raise gl.vm.UserError('only the original organizer may propose a repair')", 1)
    assert mutated != source
    mutated_path = tmp_path / 'LoopholeV2_mutated_organizer.py'
    mutated_path.write_text(mutated, encoding='utf-8')

    original = _build(world, ROOT / 'contracts' / 'LoopholeV2.py', 'v2_original_organizer')
    goal, rule, limitations = _prepare_won(world, original)
    with pytest.raises(Exception, match='original organizer'):
        world.run(world.vaddr, world.bob, 'propose_repair', 1, 1, 1,
                  'Award points only when a post includes a source link and a new verifiable explanation.',
                  limitations, 'This correction is sufficiently bounded for the original goal.', '', '', '')

    mutated_contract = _build(world, mutated_path, 'v2_mutated_organizer')
    goal, rule, limitations = _prepare_won(world, mutated_contract)
    world.run(world.vaddr, world.bob, 'propose_repair', 1, 1, 1,
              'Award points only when a post includes a source link and a new verifiable explanation.',
              limitations, 'This correction is sufficiently bounded for the original goal.', '', '', '')
    assert json.loads(mutated_contract.get_repair_proposal(1))['organizer'] == str(world.bob)


def test_mutated_v2_material_agreement_would_accept_incompatible_findings(tmp_path, world):
    source = (ROOT / 'contracts' / 'LoopholeV2.py').read_text(encoding='utf-8')
    guard = "        fields = ('verdict', 'closure', 'goal', 'coherence', 'evidence_state')"
    mutated = source.replace(guard, "        fields = ('verdict', 'evidence_state')", 1)
    assert mutated != source
    mutated_path = tmp_path / 'LoopholeV2_mutated_agreement.py'
    mutated_path.write_text(mutated, encoding='utf-8')

    for path, name, should_reject in (
        (ROOT / 'contracts' / 'LoopholeV2.py', 'v2_original_agreement', True),
        (mutated_path, 'v2_mutated_agreement', False),
    ):
        contract = _build(world, path, name)
        goal, rule, limitations = _prepare_won(world, contract)
        _propose(world, contract, goal, limitations)
        world.gl.nondet.answers = [
            json.dumps({'closure': 'UNKNOWN', 'goal': 'PROVEN', 'coherence': 'PROVEN',
                        'reason': 'Closure remains uncertain while the other findings are supported.'}),
            json.dumps({'closure': 'PROVEN', 'goal': 'UNKNOWN', 'coherence': 'PROVEN',
                        'reason': 'Goal preservation remains uncertain while the other findings are supported.'}),
        ]
        world.run(world.vaddr, world.owner, 'start_repair_review', 1, 1)
        if should_reject:
            with pytest.raises(Exception, match='validator disagreed'):
                world.run(world.vaddr, world.owner, 'adjudicate_repair', 1, 1, 1)
        else:
            world.run(world.vaddr, world.owner, 'adjudicate_repair', 1, 1, 1)
            assert json.loads(contract.get_repair_proposal(1))['verdict'] == 'INCONCLUSIVE'
