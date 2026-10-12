"""Reproducible GenVM Direct Mode asset resolver.

genlayer-test 0.29.2 still requests the pre-0.3 asset name
``genvm-universal.tar.xz``. GenVM v0.3.0-rc7 publishes the same runner bundle
as ``genvm-runners-all.tar.xz``. This adapter validates the release metadata and
SHA-256 digest before handing the real bundle to the installed loader.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import urllib.request
from pathlib import Path

import gltest.direct.sdk_loader as sdk_loader
import gltest.direct.loader as direct_loader


VERSION = os.environ.get("GENVM_DIRECT_VERSION", "v0.3.0-rc7")
ASSET = "genvm-runners-all.tar.xz" if VERSION.startswith("v0.3.") else "genvm-universal.tar.xz"
CACHE = Path.home() / ".cache" / "gltest-direct"
METADATA = CACHE / f"genvm-{VERSION}.json"
PINNED_ARTIFACT = {
    "version": "v0.3.0-rc7",
    "asset": "genvm-runners-all.tar.xz",
    "sha256": "e218a1854214681560351051f76fe2b878545cf3409455ef372d57014a88ca67",
    "size": 134842512,
}


def _github_headers(accept: str = "application/vnd.github+json") -> dict[str, str]:
    headers = {"Accept": accept, "User-Agent": "loophole-direct-mode"}
    token = os.environ.get("GENVM_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _release_asset() -> dict:
    url = f"https://api.github.com/repos/genlayerlabs/genvm/releases/tags/{VERSION}"
    request = urllib.request.Request(url, headers=_github_headers())
    with urllib.request.urlopen(request, timeout=30) as response:
        release = json.loads(response.read().decode("utf-8"))
    for asset in release.get("assets", []):
        if asset.get("name") == ASSET:
            return asset
    raise RuntimeError(f"GenVM release {VERSION} has no verified {ASSET} asset")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download_artifacts(version: str) -> Path:
    if version != VERSION:
        raise RuntimeError(f"Direct Mode is pinned to {VERSION}; received {version}")
    CACHE.mkdir(parents=True, exist_ok=True)
    destination = CACHE / f"genvm-universal-{VERSION}.tar.xz"
    metadata = None
    if METADATA.exists():
        try:
            metadata = json.loads(METADATA.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            metadata = None
    cache_matches = False
    if destination.exists() and isinstance(metadata, dict):
        cache_matches = (
            metadata.get("version") == VERSION
            and metadata.get("asset") == ASSET
            and isinstance(metadata.get("sha256"), str)
            and len(metadata["sha256"]) == 64
            and isinstance(metadata.get("size"), int)
            and destination.stat().st_size == metadata["size"]
            and _sha256(destination) == metadata["sha256"]
        )
        if VERSION == PINNED_ARTIFACT["version"]:
            cache_matches = cache_matches and metadata == PINNED_ARTIFACT
    if cache_matches:
        return destination

    asset = _release_asset()
    expected = str(asset.get("digest", "")).removeprefix("sha256:")
    size = asset.get("size")
    if len(expected) != 64 or any(c not in "0123456789abcdefABCDEF" for c in expected):
        raise RuntimeError(f"GenVM release {VERSION} did not publish a SHA-256 digest for {ASSET}")
    if VERSION == PINNED_ARTIFACT["version"] and {
        "version": VERSION, "asset": ASSET, "sha256": expected, "size": size
    } != PINNED_ARTIFACT:
        raise RuntimeError(f"GenVM release metadata changed for pinned {VERSION} {ASSET}")
    if not cache_matches:
        destination.unlink(missing_ok=True)
        METADATA.unlink(missing_ok=True)
        request = urllib.request.Request(asset["url"], headers=_github_headers("application/octet-stream"))
        temporary = destination.with_suffix(destination.suffix + ".download")
        temporary.unlink(missing_ok=True)
        with urllib.request.urlopen(request, timeout=600) as response, temporary.open("wb") as stream:
            shutil.copyfileobj(response, stream, length=1024 * 1024)
        if (size is not None and temporary.stat().st_size != int(size)) or _sha256(temporary) != expected:
            temporary.unlink(missing_ok=True)
            raise RuntimeError(f"SHA-256 mismatch for GenVM {VERSION} {ASSET}")
        temporary.replace(destination)
    METADATA.write_text(json.dumps({"version": VERSION, "asset": ASSET, "sha256": expected, "size": size}, indent=2) + "\n", encoding="utf-8")
    return destination


sdk_loader.download_artifacts = _download_artifacts


def _inject_message_to_fd0_windows(vm) -> None:
    """Keep the temporary stdin file until fd 0 is replaced on Windows."""
    import os
    import tempfile
    from genlayer.py import calldata
    from genlayer.py.types import Address

    previous = getattr(vm, "_direct_stdin_path", None)
    values = {
        "contract_address": Address(vm._contract_address) if isinstance(vm._contract_address, bytes) else vm._contract_address,
        "sender_address": Address(vm.sender) if isinstance(vm.sender, bytes) else vm.sender,
        "origin_address": Address(vm.origin) if isinstance(vm.origin, bytes) else vm.origin,
        "stack": [], "value": vm._value, "datetime": vm._datetime,
        "is_init": False, "chain_id": vm._chain_id, "entry_kind": 0,
        "entry_data": b"", "entry_stage_data": None,
    }
    encoded = calldata.encode(values)
    fd, path = tempfile.mkstemp()
    os.write(fd, encoded)
    os.lseek(fd, 0, os.SEEK_SET)
    vm._original_stdin_fd = os.dup(0)
    os.dup2(fd, 0)
    os.close(fd)
    vm._direct_stdin_path = path
    if previous:
        try:
            Path(previous).unlink(missing_ok=True)
        except PermissionError:
            pass


if os.name == "nt":
    direct_loader._inject_message_to_fd0 = _inject_message_to_fd0_windows


_load_module = direct_loader._load_module


def _load_module_per_contract(path):
    """Reset genlayer-py's module-global single-contract guard between tests."""
    try:
        import genlayer.gl.genvm_contracts as contracts_runtime
        contracts_runtime.__known_contract__ = None
    except (ImportError, AttributeError):
        pass
    return _load_module(path)


direct_loader._load_module = _load_module_per_contract
