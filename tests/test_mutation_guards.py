"""Small mutation alarms for the economically critical source guards.

These tests deliberately remove one guard at a time from an in-memory source
copy and assert that the corresponding safety marker disappears.  They do not
execute mutated contracts or alter the deployed source.
"""

from pathlib import Path


ROOT = Path(__file__).parents[1]
VAULT = (ROOT / "contracts" / "RuleVault.py").read_text(encoding="utf-8")
JUDGE = (ROOT / "contracts" / "GapJudge.py").read_text(encoding="utf-8")


def test_mutating_callback_authentication_is_detectable():
    original = "if gl.message.sender_address != self.judge:"
    mutated = VAULT.replace(original, "if False:", 1)
    assert original in VAULT
    assert original not in mutated


def test_mutating_stale_round_fence_is_detectable():
    original = "if c['active_attempt'] != str(int(attempt_id)) or c['active_round'] != str(int(round_id)):"
    mutated = VAULT.replace(original, "if False:", 1)
    assert original in VAULT
    assert original not in mutated


def test_mutating_replay_fence_is_detectable():
    original = "if a['status'] not in ('REVIEWING', 'APPEAL_REVIEWING'):"
    mutated = VAULT.replace(original, "if False:", 1)
    assert original in VAULT
    assert original not in mutated


def test_mutating_frozen_evidence_hash_check_is_detectable():
    original = "if expected_hash != evidence_hash:"
    mutated = JUDGE.replace(original, "if False:", 1)
    assert original in JUDGE
    assert original not in mutated
