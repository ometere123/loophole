#!/usr/bin/env python3
"""Verify that the checked-in release metadata names one canonical deployment.

This is deliberately offline.  RPC source parity is established separately by
``verify_contract_deployment.mjs`` and its checked-in evidence record; this
check prevents a later edit from silently pointing the release metadata or
frontend at a different contract.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_ADDRESS = "0xB87353201CeC791cc16c25e8eE1077076D90548E"
ACTIVE_DEPLOYMENT_TX = (
    "0x2f458028f666690146b5b79e674d7170cf54d326d361f8240cac40c3ddb0b960"
)
ACTIVE_SOURCE_SHA256 = "423b42cb64edb3de95f27dcedeb12aeca42f8d82b709e3a92ec47c69f87d1222"
ACTIVE_SOURCE_BYTES = 38_780
ACTIVE_CHAIN_ID = 61_999
ACTIVE_CHAIN_HEX = "0xf22f"
ACTIVE_RPC = "https://studio.genlayer.com/api"
ACTIVE_EXPLORER = "https://explorer-studio.genlayer.com"
ACTIVE_SOURCE_PATH = "contracts/Loophole.py"
EVIDENCE_PATH = "docs/evidence/loophole-release-verification-2026-10-13.json"


def canonical_bytes(path: Path, relative: str | None = None) -> bytes:
    """Match bytes committed by Git for ordinary text files on Windows.

    The deployed contract is explicitly ``-text`` in .gitattributes because
    its exact CRLF bytes are part of the GenVM source fingerprint.  Other
    tracked text files use Git's normal LF normalization.
    """
    data = path.read_bytes()
    if relative == ACTIVE_SOURCE_PATH:
        return data
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256(path: Path, relative: str | None = None) -> str:
    return hashlib.sha256(canonical_bytes(path, relative)).hexdigest()


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def require_text(errors: list[str], relative: str, *needles: str) -> None:
    path = ROOT / relative
    if not path.exists():
        fail(errors, f"missing release file: {relative}")
        return
    content = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in content:
            fail(errors, f"{relative} does not contain required text: {needle}")


def verify_manifest(errors: list[str]) -> None:
    path = ROOT / "deployments.loophole.studionet.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - exercised by CI on corruption
        fail(errors, f"cannot read deployment manifest: {exc}")
        return

    if manifest.get("address", "").lower() != ACTIVE_ADDRESS.lower():
        fail(errors, "deployment manifest address is not the active release address")
    if manifest.get("deploy_tx", "").lower() != ACTIVE_DEPLOYMENT_TX.lower():
        fail(errors, "deployment manifest deploy_tx is not the verified release transaction")
    for key, expected in (
        ("network", "studionet"),
        ("chain_id", ACTIVE_CHAIN_ID),
        ("rpc", ACTIVE_RPC),
        ("explorer", ACTIVE_EXPLORER),
        ("cli_version", "0.39.1"),
        ("contract", "Loophole"),
    ):
        if manifest.get(key) != expected:
            fail(errors, f"deployment manifest {key!r} is {manifest.get(key)!r}; expected {expected!r}")

    source = manifest.get("source", {})
    if source.get("path") != ACTIVE_SOURCE_PATH:
        fail(errors, "deployment manifest source path is not contracts/Loophole.py")
    if source.get("sha256") != ACTIVE_SOURCE_SHA256:
        fail(errors, "deployment manifest source SHA-256 is stale or incorrect")
    if source.get("bytes") != ACTIVE_SOURCE_BYTES:
        fail(errors, "deployment manifest source byte count is stale or incorrect")
    if source.get("exact_byte_match") is not True:
        fail(errors, "deployment manifest does not assert exact source parity")

    history = manifest.get("historical_deployments", {})
    for name, address in (
        ("gapjudge", "0xb14B08cd35Fa64FE795e14931DdA09999627785d"),
        ("rulevault", "0xa77A29C96c30B2A5dB865a2CE35c8F396d504F26"),
    ):
        value = history.get(name)
        if isinstance(value, dict):
            value = value.get("address")
        if str(value).lower() != address.lower():
            fail(errors, f"historical {name} address is missing or changed")


def verify_deployment_evidence(errors: list[str]) -> None:
    path = ROOT / EVIDENCE_PATH
    try:
        evidence = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(errors, f"cannot read deployment parity evidence: {exc}")
        return
    if evidence.get("verification", {}).get("passed") is not True:
        fail(errors, "deployment parity evidence is not marked passed")
    if evidence.get("address", "").lower() != ACTIVE_ADDRESS.lower():
        fail(errors, "deployment parity evidence names a different address")
    if evidence.get("deployment_tx", "").lower() != ACTIVE_DEPLOYMENT_TX.lower():
        fail(errors, "deployment parity evidence names a different deployment transaction")
    source = evidence.get("source", {})
    if source.get("local_sha256") != ACTIVE_SOURCE_SHA256:
        fail(errors, "deployment parity evidence has the wrong local source hash")
    if source.get("gen_getContractCode_sha256") != ACTIVE_SOURCE_SHA256:
        fail(errors, "deployment parity evidence has the wrong RPC source hash")
    if source.get("deployed_exact_match") is not True or source.get("submitted_exact_match") is not True:
        fail(errors, "deployment parity evidence does not prove exact source matches")


def verify_frontend(errors: list[str]) -> None:
    env = ROOT / "frontend/.env.example"
    values = {}
    for line in env.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    if values.get("NEXT_PUBLIC_LOOPHOLE_ADDRESS", "").lower() != ACTIVE_ADDRESS.lower():
        fail(errors, "frontend/.env.example points at a different contract")
    if values.get("NEXT_PUBLIC_STUDIONET_RPC") != ACTIVE_RPC:
        fail(errors, "frontend/.env.example has the wrong Studionet RPC")
    if values.get("NEXT_PUBLIC_STUDIONET_EXPLORER") != ACTIVE_EXPLORER:
        fail(errors, "frontend/.env.example has the wrong explorer")

    helpers = (ROOT / "frontend/src/lib/helpers.ts").read_text(encoding="utf-8")
    if "export const VAULT_ADDRESS = LOOPHOLE_ADDRESS" not in helpers:
        fail(errors, "frontend helper does not bind VAULT_ADDRESS to the configured active address")


def verify_checksums(errors: list[str]) -> None:
    path = ROOT / "SOURCE_CHECKSUMS.sha256"
    entries: dict[str, str] = {}
    pattern = re.compile(r"^([0-9a-f]{64})\s+(.+)$")
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        match = pattern.match(line)
        if not match:
            fail(errors, f"invalid checksum line {number}")
            continue
        digest, relative = match.groups()
        if relative in entries:
            fail(errors, f"duplicate checksum entry: {relative}")
        entries[relative] = digest
        target = ROOT / Path(relative)
        if not target.exists():
            fail(errors, f"checksum entry points to missing file: {relative}")
        elif sha256(target, relative) != digest:
            fail(errors, f"checksum mismatch: {relative}")

    for relative in (
        ACTIVE_SOURCE_PATH,
        "deployments.loophole.studionet.json",
        "frontend/.env.example",
        "README.md",
        "docs/FINAL_STEWARD_CLOSEOUT.md",
        "docs/LOOPHOLE_RELEASE_DEPLOYMENT_2026-10-13.md",
        "docs/FRONTEND_DEPLOYMENT_2026-10-13.md",
        EVIDENCE_PATH,
        "docs/evidence/dependency-audit-2026-10-13.json",
        "scripts/verify_release_integrity.py",
    ):
        if relative not in entries:
            fail(errors, f"required release file is absent from SOURCE_CHECKSUMS.sha256: {relative}")
    if entries.get(ACTIVE_SOURCE_PATH) != ACTIVE_SOURCE_SHA256:
        fail(errors, "SOURCE_CHECKSUMS.sha256 does not contain the active contract hash")


def main() -> int:
    errors: list[str] = []
    source = ROOT / ACTIVE_SOURCE_PATH
    if not source.exists():
        fail(errors, f"missing active source: {ACTIVE_SOURCE_PATH}")
    else:
        if sha256(source, ACTIVE_SOURCE_PATH) != ACTIVE_SOURCE_SHA256:
            fail(errors, "local active source does not match the verified release hash")
        if source.stat().st_size != ACTIVE_SOURCE_BYTES:
            fail(errors, "local active source does not match the verified release byte count")

    verify_manifest(errors)
    verify_deployment_evidence(errors)
    verify_frontend(errors)
    verify_checksums(errors)

    require_text(
        errors,
        "README.md",
        ACTIVE_ADDRESS,
        ACTIVE_SOURCE_SHA256,
        "contracts/Loophole.py` is the sole active Intelligent Contract",
    )
    require_text(
        errors,
        "docs/LOOPHOLE_RELEASE_DEPLOYMENT_2026-10-13.md",
        ACTIVE_ADDRESS,
        ACTIVE_DEPLOYMENT_TX,
        ACTIVE_SOURCE_SHA256,
    )
    require_text(
        errors,
        "docs/FINAL_STEWARD_CLOSEOUT.md",
        ACTIVE_ADDRESS,
        ACTIVE_SOURCE_SHA256,
        "evidence/loophole-release-verification-2026-10-13.json",
    )
    require_text(
        errors,
        "docs/FRONTEND_DEPLOYMENT_2026-10-13.md",
        ACTIVE_ADDRESS,
        "https://loophole-one.vercel.app/",
    )

    if errors:
        print("RELEASE INTEGRITY: FAIL")
        for error in errors:
            print(f"  ERROR: {error}")
        return 1
    print(
        "RELEASE INTEGRITY: PASS "
        f"{ACTIVE_ADDRESS} {ACTIVE_SOURCE_SHA256} chain={ACTIVE_CHAIN_ID}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
