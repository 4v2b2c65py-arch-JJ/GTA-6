#!/usr/bin/env python3
"""
Package entire codebase into an executable web-based game client & player:
- generates/refreshes identity assets (png/jpg/ico/favicon/insignia)
- syncs codebase snapshot into build/web/data for client+player consumption
- emits package manifest and distributable archive
"""

import json
import os
import shutil
import tarfile
import hashlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "build/web"
DATA = WEB / "data"
PKG_DIR = ROOT / "build/package"
LOG = ROOT / "logs/package/package.log"

EXCLUDE_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", "node_modules"}
# avoid recursive packaging of previous archives inside data snapshot
EXCLUDE_PATH_PREFIXES = [
    "build/package/",
    "build/web/data/",
]


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{now()}] {msg}\n"
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())


def save_json(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def should_skip(rel_posix: str, parts) -> bool:
    if any(p in EXCLUDE_DIRS for p in parts):
        return True
    for pref in EXCLUDE_PATH_PREFIXES:
        if rel_posix.startswith(pref):
            return True
    return False


def sync_codebase():
    if DATA.exists():
        shutil.rmtree(DATA)
    DATA.mkdir(parents=True, exist_ok=True)
    files_copied = 0
    bytes_copied = 0
    for src in ROOT.rglob("*"):
        if not src.is_file():
            continue
        rel = src.relative_to(ROOT)
        rel_posix = rel.as_posix()
        if should_skip(rel_posix, rel.parts):
            continue
        # don't copy the archive we'll create; also skip sockets/special
        dst = DATA / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(src, dst)
            files_copied += 1
            try:
                bytes_copied += src.stat().st_size
            except Exception:
                pass
        except Exception as e:
            log(f"skip {rel_posix}: {e}")
    return {"files": files_copied, "bytes": bytes_copied}


def make_archive():
    PKG_DIR.mkdir(parents=True, exist_ok=True)
    name = "spatial-avy-web-client-player.tar.gz"
    archive = PKG_DIR / name
    # package build/web (client+player+data snapshot) as runnable unit
    with tarfile.open(archive, "w:gz") as tf:
        tf.add(WEB, arcname="spatial-avy-web")
    # checksum
    h = hashlib.sha256()
    with archive.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return archive, h.hexdigest()


def main():
    # 1) generate identity assets
    import subprocess, sys
    gen = ROOT / "scripts/identity/generate_identity.py"
    r = subprocess.run([sys.executable, str(gen)], cwd=str(ROOT))
    if r.returncode != 0:
        log(f"identity generation failed rc={r.returncode}")
    else:
        log("identity generation complete")

    # 2) sync codebase snapshot into web data
    stats = sync_codebase()
    log(f"synced codebase to web data: files={stats['files']} bytes={stats['bytes']}")

    # 3) ensure key web identity files present
    for src, dst in [
        (ROOT / "assets/identity/icons/favicon.ico", WEB / "favicon.ico"),
        (ROOT / "assets/identity/icons/icon-16.png", WEB / "assets/icons/icon-16.png"),
        (ROOT / "assets/identity/icons/icon-32.png", WEB / "assets/icons/icon-32.png"),
        (ROOT / "assets/identity/icons/icon-64.png", WEB / "assets/icons/icon-64.png"),
        (ROOT / "assets/identity/icons/icon-192.png", WEB / "assets/icons/icon-192.png"),
        (ROOT / "assets/identity/icons/icon-512.png", WEB / "assets/icons/icon-512.png"),
        (ROOT / "assets/identity/icons/apple-touch-icon.png", WEB / "assets/icons/apple-touch-icon.png"),
        (ROOT / "assets/identity/insignia/og_image.png", WEB / "assets/insignia/og_image.png"),
        (ROOT / "assets/identity/identity_manifest.json", WEB / "assets/identity_manifest.json"),
    ]:
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    # 4) archive
    archive, sha = make_archive()
    log(f"archive={archive} sha256={sha}")

    manifest = {
        "id": "spatial_avy_web_package",
        "type": "web_client_player_package",
        "version": "1.0.0",
        "packaged_at": now(),
        "executable": "build/web/serve.py",
        "client_entry": "build/web/index.html",
        "codebase_snapshot": "build/web/data",
        "archive": str(archive.relative_to(ROOT)),
        "archive_sha256": sha,
        "snapshot_stats": stats,
        "identity": {
            "manifest": "assets/identity/identity_manifest.json",
            "favicon": "build/web/favicon.ico",
            "icons": "build/web/assets/icons",
            "insignia": "build/web/assets/insignia"
        },
        "story_novel_data": {
            "world": "spatial_avy_home",
            "motifs": ["Bodium terrain", "Mind aspect", "Soul aspect", "SATS/REA-REM border protocol"],
            "mnemonic_lace": "Z<zone>-Q<pocket>-C<cell>-T<tick>",
            "door_node_string": "N10-N9-N8-N7-N6-N5-N4-N3-N2-N1-N0"
        },
        "ai_integrated_data": {
            "local_ai": "ollama llama3.2:latest @ http://localhost:11434",
            "runtime": "systems/runtime/game_world_runtime.json",
            "voice_pipeline": "systems/audio/voice/voice_pipeline.json"
        }
    }
    save_json(WEB / "package_manifest.json", manifest)
    save_json(PKG_DIR / "package_manifest.json", manifest)
    print(json.dumps({"ok": True, "archive": manifest["archive"], "files": stats["files"]}, indent=2))


if __name__ == "__main__":
    main()
