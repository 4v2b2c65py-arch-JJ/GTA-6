#!/usr/bin/env python3
"""
Install/build DLC packs from catalog: generate per-pack game-data manifests,
install state, and asset indexes for in-game/world loading.
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CATALOG = ROOT / "systems/launchers/rockstar/dlc/dlc_catalog.json"
PACKS_DIR = ROOT / "systems/launchers/rockstar/dlc/packs"
ASSETS_OUT = ROOT / "assets/game_assets/dlc"
LOG = ROOT / "logs/launchers/dlc/install.log"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(p):
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{now()}] {msg}\n"
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())


def main():
    cat = load_json(CATALOG)
    ts = now()
    installed = []
    for entry in cat.get("packs", []):
        pref = ROOT / entry["pack_ref"]
        pack = load_json(pref) if pref.exists() else {"pack_id": entry["pack_id"], "features": []}
        features = pack.get("features", [])
        feature_ids = [f.get("id") for f in features] if features and isinstance(features[0], dict) else features
        data = {
            "pack_id": entry["pack_id"],
            "title": entry.get("title"),
            "base_game": entry.get("base_game"),
            "kind": entry.get("kind"),
            "status": "installed",
            "installed_at": ts,
            "features": features,
            "feature_ids": feature_ids,
            "build_hooks": pack.get("build_hooks", {}),
            "hash": hashlib.sha256((entry["pack_id"] + ts).encode()).hexdigest()[:16]
        }
        out = ASSETS_OUT / f"{entry['pack_id']}_data.json"
        save_json(out, data)
        installed.append({
            "pack_id": entry["pack_id"],
            "title": entry.get("title"),
            "base_game": entry.get("base_game"),
            "kind": entry.get("kind"),
            "status": "installed",
            "data_ref": str(out.relative_to(ROOT)),
            "feature_count": len(feature_ids)
        })
        log(f"installed {entry['pack_id']} features={len(feature_ids)}")

    manifest = {
        "id": "dlc_install_manifest",
        "generated_at": ts,
        "catalog_ref": str(CATALOG.relative_to(ROOT)),
        "packs": installed,
        "summary": {
            "total": len(installed),
            "by_game": {},
            "by_kind": {}
        }
    }
    for p in installed:
        manifest["summary"]["by_game"][p["base_game"]] = manifest["summary"]["by_game"].get(p["base_game"], 0) + 1
        manifest["summary"]["by_kind"][p["kind"]] = manifest["summary"]["by_kind"].get(p["kind"], 0) + 1
    save_json(ASSETS_OUT / "dlc_install_manifest.json", manifest)

    state = {
        "id": "dlc_install_state",
        "status": "installed",
        "installed_at": ts,
        "total_packs": len(installed),
        "manifest_ref": "assets/game_assets/dlc/dlc_install_manifest.json"
    }
    save_json(ROOT / "systems/launchers/rockstar/dlc/install_state.json", state)
    log(f"DLC install complete: {len(installed)} packs")
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
