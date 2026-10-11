"""Direct Mode proof for the exact frozen workload from live challenge #2.

These tests keep the production GapJudge source and prompt intact.  They do
not model a live verdict: the LLM response is deliberately controlled so the
tests can exercise the real parser, conservative normalization, and captured
independent validator against the full policy/evidence dimensions.
"""

import hashlib
import json


RULE = (
    "A member earns 10 points when they publish a post containing "
    "#OurCampaign and at least 100 words."
)
GOAL = (
    "Reward members who publish an original educational post that explains "
    "a topic clearly and helps readers learn."
)
LIMITATIONS = "Posts must be newly written by the member."
SCENARIO = (
    "I publish a 100-word post made by repeating the same harmless sentence "
    "and include #OurCampaign. It meets the literal hashtag and word-count "
    "conditions, but it does not explain a topic or provide educational "
    "value. The wording permits the points even though the stated educational "
    "outcome is not achieved."
)
RULE_QUOTE = RULE
IMPACT = (
    "The literal rule awards points for meaningless repetition, so an "
    "ineligible post can satisfy the measurable conditions while violating "
    "the stated educational purpose."
)


def _challenge_two_args():
    frozen = {
        "goal": GOAL,
        "published_rule": RULE,
        "limitations": LIMITATIONS,
        "claimed_rule_quote": RULE_QUOTE,
        "attack_sequence": SCENARIO,
        "claimed_harm": IMPACT,
    }
    evidence_hash = hashlib.sha256(
        json.dumps(frozen, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return (2, 2, 1, evidence_hash, RULE, GOAL, LIMITATIONS, SCENARIO, RULE_QUOTE, IMPACT)


def _deploy_bound_judge(direct_vm, direct_deploy, direct_owner, direct_alice):
    judge = direct_deploy("contracts/GapJudge.py")
    vault_address = "0x" + direct_alice.hex()
    direct_vm.sender = direct_owner
    judge.bind_vault(vault_address)
    direct_vm.sender = direct_alice
    return judge


def test_gapjudge_direct_full_challenge_two_normalizes_contradictory_output(
    direct_vm, direct_deploy, direct_owner, direct_alice
):
    """A VALID proposal with letter=false is conservatively non-VALID."""
    direct_vm._chain_id = 61999
    direct_vm.clear_mocks()
    direct_vm.mock_llm(
        r".*Return ONLY a compact JSON object.*",
        json.dumps(
            {
                "verdict": "VALID",
                "letter": False,
                "purpose": False,
                "feasible": False,
                "reason": "The literal wording appears to permit the described repetition.",
            }
        ),
    )
    judge = _deploy_bound_judge(direct_vm, direct_deploy, direct_owner, direct_alice)

    judge.adjudicate(*_challenge_two_args())

    case = json.loads(judge.get_case("2:2:1"))
    assert case == {
        "challenge_id": "2",
        "attempt_id": "2",
        "round_id": "1",
        "evidence_hash": case["evidence_hash"],
        "verdict": "INCONCLUSIVE",
        "letter": False,
        "purpose": False,
        "feasible": False,
        "reason": "Validator could not establish a safely structured answer.",
    }
    assert direct_vm.run_validator() is True


def test_gapjudge_direct_full_challenge_two_validator_rechecks_material_findings(
    direct_vm, direct_deploy, direct_owner, direct_alice
):
    """A validator that changes a material finding rejects the leader result."""
    direct_vm._chain_id = 61999
    leader = {
        "verdict": "INVALID",
        "letter": True,
        "purpose": False,
        "feasible": True,
        "reason": "The measurable conditions are met, but the stated educational purpose is not.",
    }
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r".*Return ONLY a compact JSON object.*", json.dumps(leader))
    judge = _deploy_bound_judge(direct_vm, direct_deploy, direct_owner, direct_alice)

    judge.adjudicate(*_challenge_two_args())
    case = json.loads(judge.get_case("2:2:1"))
    assert case["verdict"] == "INVALID"
    assert (case["letter"], case["purpose"], case["feasible"]) == (True, False, True)

    direct_vm.clear_mocks()
    direct_vm.mock_llm(
        r".*Return ONLY a compact JSON object.*",
        json.dumps(
            {
                "verdict": "VALID",
                "letter": True,
                "purpose": True,
                "feasible": True,
                "reason": "A different validator cannot erase the purpose conflict.",
            }
        ),
    )
    assert direct_vm.run_validator() is False


def test_direct_workload_probe_fixture_uses_the_same_full_assessment(
    direct_vm, direct_deploy, direct_alice
):
    """The isolated direct probe executes the production-sized prompt path."""
    direct_vm._chain_id = 61999
    direct_vm.clear_mocks()
    direct_vm.mock_llm(
        r".*Return ONLY a compact JSON object.*",
        json.dumps(
            {
                "verdict": "INCONCLUSIVE",
                "letter": False,
                "purpose": False,
                "feasible": False,
                "reason": "The frozen text does not safely establish a payable loophole.",
            }
        ),
    )
    probe = direct_deploy("diagnostics/DirectGapJudgeWorkloadProbe.py", "0x" + "a" * 40)
    direct_vm.sender = direct_alice
    probe.adjudicate_fixture(*_challenge_two_args())
    record = json.loads(probe.get_case("2:2:1"))
    assert record["result"]["verdict"] == "INCONCLUSIVE"
    assert direct_vm.run_validator() is True
