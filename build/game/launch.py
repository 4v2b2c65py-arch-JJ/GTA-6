#!/usr/bin/env python3
"""
Spatial Avy game build launcher:
- shows Character Hub deck (pre-launch)
- verifies key runtime assets/manifests
- loads runtime/index references and emits launch state
"""

import json
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build/game/build.json"
CHAR_HUB = ROOT / "systems/character_hub/character_hub.json"
DECK = ROOT / "systems/character_hub/deck/deck.json"
HUB_UI = ROOT / "assets/ui/character_hub/index.html"
RUNTIME = ROOT / "systems/runtime/game_world_runtime.json"
WORLD = ROOT / "home_world/home_world_index.json"
IMAGES = ROOT / "assets/images/images_manifest.json"
ICONS = ROOT / "assets/images/icons_manifest.json"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(p):
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def check(p):
    return {"path": str(p.relative_to(ROOT)), "exists": p.exists()}


def main(open_ui=True):
    checks = [check(p) for p in [CHAR_HUB, DECK, HUB_UI, RUNTIME, WORLD, IMAGES, ICONS]]
    ready = all(c["exists"] for c in checks)
    deck = load_json(DECK) if DECK.exists() else {}
    state = {
        "id": "game_launch_state",
        "launched_at": now(),
        "status": "launched" if ready else "degraded",
        "character_hub": str(CHAR_HUB.relative_to(ROOT)),
        "deck": str(DECK.relative_to(ROOT)),
        "character": deck.get("character", {}),
        "cards": [c.get("card_id") for c in deck.get("cards", [])],
        "checks": checks,
        "runtime_ref": str(RUNTIME.relative_to(ROOT)),
        "world_ref": str(WORLD.relative_to(ROOT)),
        "ui": str(HUB_UI.relative_to(ROOT))
    }
    save_json(BUILD, state)
    print("=== Spatial Avy Build ===")
    print(f"Status: {state['status']}")
    print(f"Character Hub Deck: {state['deck']}")
    print(f"Cards: {', '.join(state['cards']) if state['cards'] else '-'}")
    for c in checks:
        print(f"[{'OK' if c['exists'] else 'MISS'}] {c['path']}")
    if open_ui and HUB_UI.exists():
        try:
            webbrowser.open(HUB_UI.resolve().as_uri())
            print(f"Opened UI: {HUB_UI}")
        except Exception as e:
            print(f"UI open skipped: {e}")
    print(f"Build state: {BUILD}")
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main(open_ui=True))
