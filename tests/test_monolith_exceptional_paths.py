"""Adversarial economic lifecycle tests for the current single-contract Loophole.

These are simulator-state tests, not evidence of finalized Studionet writes.
The GenVM Direct Mode and on-chain evidence sets are reported separately.
"""
import json

import pytest

from test_monolith_protocol import monolith, _fund, _revealed, _attack

PRIZE = 2 * 10**18
BOND = 10**16

INVALID = {
    "letter": "DISPROVEN",
    "purpose": "PROVEN",
    "feasible": "PROVEN",
    "reason": "The attempt fails the exact minimum word count in the frozen rulebook.",
}
VALID = {
    "letter": "PROVEN",
    "purpose": "PROVEN",
    "feasible": "PROVEN",
    "reason": "The exact rule permits the sequence while the stated objective is defeated.",
}
INCONCLUSIVE = {
    "letter": "PROVEN",
    "purpose": "UNKNOWN",
    "feasible": "PROVEN",
    "reason": "The frozen evidence cannot establish the required harm to the rulebook goal.",
}


def _initial_invalid(w):
    _fund(w)
    _revealed(w)
    w.gl.nondet.answer = json.dumps(INVALID)
    w.run(w.vaddr, w.bob, "start_review", 1)
    w.run(w.vaddr, w.bob, "adjudicate_review", 1, 1, 1)
    a = json.loads(w.vault.get_attempt(1))
    assert a["status"] == "INVALID_PENDING"
    assert w.vault.total_locked == PRIZE + BOND
    assert w.vault.total_credit == 0
    return a


def _appeal(w):
    w.run(w.vaddr, w.alice, "appeal_invalid", 1, value=BOND)
    a = json.loads(w.vault.get_attempt(1))
    assert a["status"] == "APPEAL_REVIEWING"
    assert a["appeal_used"] is True
    assert json.loads(w.vault.get_challenge(1))["active_round"] == "2"
    assert w.vault.total_locked == PRIZE + 2 * BOND


def _resolve_appeal(w, result):
    w.gl.nondet.answer = json.dumps(result)
    w.run(w.vaddr, w.bob, "adjudicate_review", 1, 1, 2)


def test_bonded_appeal_overturn_credits_exact_challenger_liability(monolith):
    w = monolith
    _initial_invalid(w)
    _appeal(w)
    _resolve_appeal(w, VALID)
    a = json.loads(w.vault.get_attempt(1))
    c = json.loads(w.vault.get_challenge(1))
    assert a["status"] == "DECIDED" and a["verdict"] == "VALID"
    assert c["status"] == "WON" and c["winner"] == str(w.alice)
    assert w.vault.get_credit(w.alice) == PRIZE + 2 * BOND
    assert w.vault.get_credit(w.owner) == 0
    assert w.vault.total_locked == 0
    assert w.vault.total_credit == PRIZE + 2 * BOND
    w.run(w.vaddr, w.bob, "adjudicate_review", 1, 1, 2)
    assert w.vault.get_credit(w.alice) == PRIZE + 2 * BOND


def test_bonded_appeal_upheld_allocates_both_bonds_to_organizer(monolith):
    w = monolith
    _initial_invalid(w)
    _appeal(w)
    _resolve_appeal(w, INVALID)
    a = json.loads(w.vault.get_attempt(1))
    assert a["status"] == "DECIDED" and a["verdict"] == "INVALID"
    assert w.vault.get_credit(w.owner) == 2 * BOND
    assert w.vault.get_credit(w.alice) == 0
    assert w.vault.total_locked == PRIZE
    with pytest.raises(Exception, match="only the affected challenger"):
        w.run(w.vaddr, w.alice, "appeal_invalid", 1, value=BOND)


def test_bonded_appeal_inconclusive_returns_both_bonds_not_bounty(monolith):
    w = monolith
    _initial_invalid(w)
    _appeal(w)
    _resolve_appeal(w, INCONCLUSIVE)
    a = json.loads(w.vault.get_attempt(1))
    assert a["status"] == "DECIDED" and a["verdict"] == "INCONCLUSIVE"
    assert w.vault.get_credit(w.alice) == 2 * BOND
    assert w.vault.get_credit(w.owner) == 0
    assert w.vault.total_locked == PRIZE


def test_expired_invalid_frees_bond_once_and_allows_eventual_refund(monolith):
    w = monolith
    a = _initial_invalid(w)
    with pytest.raises(Exception, match="not ready"):
        w.run(w.vaddr, w.bob, "finalize_invalid", 1)
    future = max(a["appeal_deadline"], json.loads(w.vault.get_challenge(1))["reveal_deadline"]) + 1
    w.vault._now = lambda: future
    w.run(w.vaddr, w.bob, "finalize_invalid", 1)
    assert json.loads(w.vault.get_attempt(1))["status"] == "DECIDED"
    assert w.vault.get_credit(w.owner) == BOND
    with pytest.raises(Exception, match="not ready"):
        w.run(w.vaddr, w.bob, "finalize_invalid", 1)
    w.run(w.vaddr, w.owner, "refund_unwon", 1)
    assert json.loads(w.vault.get_challenge(1))["status"] == "REFUNDED"
    assert w.vault.get_credit(w.owner) == PRIZE + BOND
    assert w.vault.total_credit == PRIZE + BOND
    assert w.vault.total_locked == 0


def test_stalled_review_returns_bond_and_invalidates_old_round(monolith):
    w = monolith
    _fund(w)
    _revealed(w)
    w.run(w.vaddr, w.owner, "start_review", 1)
    c = json.loads(w.vault.get_challenge(1))
    with pytest.raises(Exception, match="not eligible"):
        w.run(w.vaddr, w.bob, "recover_stalled_review", 1)
    w.vault._now = lambda: c["review_started"] + 5 * 24 * 3600 + 1
    w.run(w.vaddr, w.bob, "recover_stalled_review", 1)
    assert json.loads(w.vault.get_attempt(1))["status"] == "DECIDED"
    assert json.loads(w.vault.get_attempt(1))["verdict"] == "INCONCLUSIVE"
    assert w.vault.get_credit(w.alice) == BOND
    assert w.vault.total_locked == PRIZE
    with pytest.raises(Exception, match="stale"):
        w.run(w.vaddr, w.bob, "adjudicate_review", 1, 1, 1)
    with pytest.raises(Exception, match="not eligible"):
        w.run(w.vaddr, w.bob, "recover_stalled_review", 1)


def test_unrevealed_commitment_expires_once_then_bounty_can_refund(monolith):
    w = monolith
    _fund(w)
    commitment, _ = _attack(1, w.alice)
    w.run(w.vaddr, w.alice, "commit_attempt", 1, commitment, value=BOND)
    with pytest.raises(Exception, match="not eligible"):
        w.run(w.vaddr, w.bob, "settle_remaining_bond", 1)
    deadline = json.loads(w.vault.get_challenge(1))["reveal_deadline"]
    w.vault._now = lambda: deadline + 1
    w.run(w.vaddr, w.bob, "settle_remaining_bond", 1)
    assert json.loads(w.vault.get_attempt(1))["status"] == "EXPIRED"
    assert w.vault.get_credit(w.owner) == BOND
    with pytest.raises(Exception, match="not eligible"):
        w.run(w.vaddr, w.bob, "settle_remaining_bond", 1)
    w.run(w.vaddr, w.owner, "refund_unwon", 1)
    assert json.loads(w.vault.get_challenge(1))["status"] == "REFUNDED"
    assert w.vault.get_credit(w.owner) == PRIZE + BOND
    assert w.vault.total_locked == 0


def test_appeal_is_one_time_challenger_only_and_exact_bond(monolith):
    w = monolith
    _initial_invalid(w)
    with pytest.raises(Exception, match="only the affected challenger"):
        w.run(w.vaddr, w.bob, "appeal_invalid", 1, value=BOND)
    with pytest.raises(Exception, match="equal neutral bond"):
        w.run(w.vaddr, w.alice, "appeal_invalid", 1, value=BOND - 1)
    assert json.loads(w.vault.get_attempt(1))["status"] == "INVALID_PENDING"
    _appeal(w)
    with pytest.raises(Exception, match="only the affected challenger"):
        w.run(w.vaddr, w.alice, "appeal_invalid", 1, value=BOND)
    assert w.vault.total_locked == PRIZE + 2 * BOND


def test_invalid_ruling_cannot_refund_organizer_while_appealable(monolith):
    w = monolith
    a = _initial_invalid(w)
    c = json.loads(w.vault.get_challenge(1))
    w.vault._now = lambda: c["reveal_deadline"] + 1
    with pytest.raises(Exception, match="pending challenger rights"):
        w.run(w.vaddr, w.owner, "refund_unwon", 1)
    assert json.loads(w.vault.get_challenge(1))["status"] == "OPEN"
    assert w.vault.get_credit(w.owner) == 0
    # Our simulated time advanced past the genuine appeal deadline as well;
    # a separate finalization is still required before a refund.
    assert a["appeal_deadline"] < c["reveal_deadline"] + 1
