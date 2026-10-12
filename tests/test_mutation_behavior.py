"""Executable mutation checks for economically critical RuleVault guards.

Each test writes a deliberately mutated contract to a temporary path, loads it
through the same simulator harness as the protocol tests, and drives the
attack that the removed guard must stop.  The production files and deployed
contracts are never modified.
"""

import hashlib
import importlib.util
import json
import types
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _mutated_world(world, tmp_path, vault_mutations=(), judge_mutations=()):
    """Create a fresh simulator world with source mutations applied."""
    vault_source = (ROOT / "contracts" / "historical" / "RuleVault.py").read_text(encoding="utf-8")
    judge_source = (ROOT / "contracts" / "historical" / "GapJudge.py").read_text(encoding="utf-8")
    for old, new in vault_mutations:
        assert vault_source.count(old) == 1, old
        vault_source = vault_source.replace(old, new, 1)
    for old, new in judge_mutations:
        assert judge_source.count(old) == 1, old
        judge_source = judge_source.replace(old, new, 1)

    vault_path = tmp_path / "RuleVault_mutated.py"
    judge_path = tmp_path / "GapJudge_mutated.py"
    vault_path.write_text(vault_source, encoding="utf-8")
    judge_path.write_text(judge_source, encoding="utf-8")

    gl = world.gl
    gl.__init__()
    Vault = _load(vault_path, "mutated_rulevault").RuleVault
    Judge = _load(judge_path, "mutated_gapjudge").GapJudge
    Address = type(world.owner)
    owner = Address("0x" + "1" * 40)
    alice = Address("0x" + "2" * 40)
    bob = Address("0x" + "3" * 40)
    judge_addr = Address("0x" + "a" * 40)
    vault_addr = Address("0x" + "b" * 40)

    def run(addr, sender, method, *args, value=0):
        gl.message = types.SimpleNamespace(
            sender_address=Address(sender),
            contract_address=Address(addr),
            origin_address=Address(sender),
            value=value,
            chain_id=61999,
        )
        return getattr(gl.contracts[str(addr)], method)(*args)

    def flush():
        while gl.pending:
            name, sender, addr, value, args = gl.pending.pop(0)
            if name == "TRANSFER":
                continue
            run(addr, sender, name, *args, value=value)

    gl.message = types.SimpleNamespace(sender_address=owner, contract_address=judge_addr, value=0, chain_id=61999)
    judge = Judge()
    gl.contracts[str(judge_addr)] = judge
    gl.message = types.SimpleNamespace(sender_address=owner, contract_address=vault_addr, value=0, chain_id=61999)
    vault = Vault(judge_addr)
    gl.contracts[str(vault_addr)] = vault
    run(judge_addr, owner, "bind_vault", vault_addr)
    return types.SimpleNamespace(
        run=run,
        flush=flush,
        gl=gl,
        judge=judge,
        vault=vault,
        owner=owner,
        alice=alice,
        bob=bob,
        jaddr=judge_addr,
        vaddr=vault_addr,
    )


def _funded(w):
    w.run(
        w.vaddr,
        w.owner,
        "create_challenge",
        "Originality Trap",
        "Reward only genuinely original contributions to this campaign.",
        "Every member who publishes a post of at least 100 words with #OURCAMPAIGN earns points.",
        "Posts must happen during the campaign.",
        "CONTENT",
        86400,
        10**16,
        value=2 * 10**18,
    )


def _attack(cid, sender, salt="abcd012345678901"):
    scenario = "I will repeat meaningless words over one hundred times with the hashtag, farming a reward without creating original content."
    quote = "Every member who publishes a post of at least 100 words"
    impact = "The post meets the length rule but violates the original-educational-contribution objective."
    preimage = "|".join([str(cid), str(sender).lower(), salt, scenario, quote, impact])
    return hashlib.sha256(preimage.encode()).hexdigest(), (salt, scenario, quote, impact)


def _revealed(w):
    digest, payload = _attack(1, w.alice)
    w.run(w.vaddr, w.alice, "commit_attempt", 1, digest, value=10**16)
    w.run(w.vaddr, w.alice, "reveal_attempt", 1, *payload)
    return digest, payload


def test_mutated_forged_callback_allows_unauthorized_verdict(world, tmp_path):
    w = _mutated_world(world, tmp_path, vault_mutations=[
        ("if gl.message.sender_address != self.judge:", "if False:")
    ])
    _funded(w)
    _, payload = _revealed(w)
    w.run(w.vaddr, w.bob, "start_review", 1)
    attempt = json.loads(w.vault.get_attempt(1))
    w.run(w.vaddr, w.bob, "record_verdict", 1, 1, 1, attempt["evidence_hash"], "VALID", "forged", True, True, True)
    assert json.loads(w.vault.get_challenge(1))["status"] == "WON"


def test_mutated_stale_round_fence_allows_old_callback(world, tmp_path):
    w = _mutated_world(world, tmp_path, vault_mutations=[
        ("if c['active_attempt'] != str(int(attempt_id)) or c['active_round'] != str(int(round_id)):", "if False:")
    ])
    _funded(w)
    _revealed(w)
    w.run(w.vaddr, w.bob, "start_review", 1)
    c = json.loads(w.vault.get_challenge(1))
    c["active_round"] = "2"
    w.vault.challenges[1] = json.dumps(c)
    attempt = json.loads(w.vault.get_attempt(1))
    w.run(w.vaddr, w.jaddr, "record_verdict", 1, 1, 1, attempt["evidence_hash"], "VALID", "stale", True, True, True)
    assert json.loads(w.vault.get_challenge(1))["status"] == "WON"


def test_mutated_duplicate_verdict_pays_twice(world, tmp_path):
    w = _mutated_world(world, tmp_path, vault_mutations=[
        ("if a['status'] not in ('REVIEWING', 'APPEAL_REVIEWING'):", "if False:")
    ])
    _funded(w)
    _revealed(w)
    w.run(w.vaddr, w.bob, "start_review", 1)
    attempt = json.loads(w.vault.get_attempt(1))
    args = (1, 1, 1, attempt["evidence_hash"], "VALID", "first", True, True, True)
    w.run(w.vaddr, w.jaddr, "record_verdict", *args)
    first_credit = w.vault.get_credit(w.alice)
    c = json.loads(w.vault.get_challenge(1))
    c["active_attempt"] = "1"
    c["active_round"] = "1"
    c["active_slots"] = "1"
    w.vault.challenges[1] = json.dumps(c)
    w.run(w.vaddr, w.jaddr, "record_verdict", *args)
    assert w.vault.get_credit(w.alice) == first_credit + 2 * 10**18 + 10**16


def test_mutated_reveal_hash_check_accepts_wrong_preimage(world, tmp_path):
    w = _mutated_world(world, tmp_path, vault_mutations=[
        ("if hashlib.sha256(plaintext.encode('utf-8')).hexdigest() != a['commitment']:", "if False:")
    ])
    _funded(w)
    _, payload = _attack(1, w.alice)
    w.run(w.vaddr, w.alice, "commit_attempt", 1, "a" * 64, value=10**16)
    w.run(w.vaddr, w.alice, "reveal_attempt", 1, "wrong-salt-1234", *payload[1:])
    assert json.loads(w.vault.get_attempt(1))["status"] == "REVEALED"


def test_mutated_refund_guard_releases_live_revealed_attempt(world, tmp_path):
    w = _mutated_world(world, tmp_path, vault_mutations=[
        ("if a['status'] in ('REVEALED', 'REVIEWING', 'INVALID_PENDING', 'APPEAL_REVIEWING', 'COMMITTED'):", "if False:")
    ])
    _funded(w)
    _revealed(w)
    c = json.loads(w.vault.get_challenge(1))
    c["reveal_deadline"] = 0
    w.vault.challenges[1] = json.dumps(c)
    w.run(w.vaddr, w.owner, "refund_unwon", 1)
    assert json.loads(w.vault.get_challenge(1))["status"] == "REFUNDED"


def test_mutated_withdrawal_clear_allows_duplicate_transfer(world, tmp_path):
    w = _mutated_world(world, tmp_path, vault_mutations=[
        ("balances[owner.as_hex.lower()] = '0'", "balances[owner.as_hex.lower()] = balances[owner.as_hex.lower()]")
    ])
    _funded(w)
    _revealed(w)
    w.run(w.vaddr, w.bob, "start_review", 1)
    w.flush()
    w.run(w.vaddr, w.alice, "withdraw")
    w.run(w.vaddr, w.alice, "withdraw")
    assert w.vault.withdrawal_count == 2
    assert json.loads(w.vault.get_withdrawal(1))["amount_wei"] == json.loads(w.vault.get_withdrawal(2))["amount_wei"]


def test_mutated_appeal_settlement_pays_invalid_appeal_to_challenger(world, tmp_path):
    w = _mutated_world(world, tmp_path, vault_mutations=[
        ("self._credit(c['organizer'] if verdict == 'INVALID' else a['challenger'], bond + appeal_bond)",
         "self._credit(a['challenger'], bond + appeal_bond)")
    ])
    _funded(w)
    _revealed(w)
    w.gl.nondet.answer = '{"verdict":"INVALID","letter":false,"purpose":true,"feasible":true,"reason":"The action is expressly barred by the published rule and is not eligible."}'
    w.run(w.vaddr, w.bob, "start_review", 1)
    w.flush()
    attempt = json.loads(w.vault.get_attempt(1))
    assert attempt["status"] == "INVALID_PENDING"
    w.run(w.vaddr, w.alice, "appeal_invalid", 1, value=10**16)
    w.flush()
    assert w.vault.get_credit(w.alice) == 2 * 10**16
    assert w.vault.get_credit(w.owner) == 0


def test_mutated_zero_credit_guard_creates_unauthorized_withdrawal(world, tmp_path):
    w = _mutated_world(world, tmp_path, vault_mutations=[
        ("if amount == u256(0):", "if False:")
    ])
    _funded(w)
    w.run(w.vaddr, w.bob, "withdraw")
    assert w.vault.withdrawal_count == 1
    assert json.loads(w.vault.get_withdrawal(1))["amount_wei"] == "0"

