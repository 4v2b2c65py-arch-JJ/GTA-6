#!/usr/bin/env python3
"""
Install in-game images and component/executable icons:
- collect existing images in workspace and install copies into assets/images/in_game
- register downloaded icons for components/executables/launchers/games/dlc
- emit manifests and install log
"""

import json
import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGES = ROOT / "assets/images"
LOG = ROOT / "logs/build/images_install.log"
IMG_EXTS = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif", ".ico"}


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


def sha256_file(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_workspace_images():
    found = []
    skip_parts = {".git", ".venv", "build/game/assets_copy"}  # avoid loops
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in IMG_EXTS:
            continue
        rel = p.relative_to(ROOT)
        if any(part in skip_parts for part in rel.parts):
            continue
        found.append(rel.as_posix())
    return sorted(set(found))


def install_in_game_images(all_images):
    installed = []
    # map known images to in-game buckets; copy into in_game folders
    for rel in all_images:
        src = ROOT / rel
        name = src.name
        lower = rel.lower()
        if "rdr2" in lower or "red_dead" in lower:
            bucket = "rdr2"
        elif "gta" in lower or "grand_theft" in lower:
            bucket = "gta5"
        else:
            bucket = "common"
        dst = IMAGES / "in_game" / bucket / name
        # avoid copying onto itself
        if src.resolve() != dst.resolve():
            dst.parent.mkdir(parents=True, exist_ok=True)
            try:
                if not dst.exists() or sha256_file(src) != sha256_file(dst):
                    shutil.copy2(src, dst)
            except Exception as e:
                log(f"copy_skip {rel}: {e}")
        installed.append({
            "source": rel,
            "installed_to": dst.relative_to(ROOT).as_posix() if dst.exists() else None,
            "bucket": bucket
        })
    return installed


def build_icons_manifest():
    icons = []
    icon_root = IMAGES / "icons"
    for p in sorted(icon_root.rglob("*")):
        if p.is_file():
            rel = p.relative_to(ROOT).as_posix()
            category = p.relative_to(icon_root).parts[0] if p.relative_to(icon_root).parts else "misc"
            icons.append({
                "id": f"icon-{p.stem}",
                "name": p.stem,
                "category": category,
                "file": rel,
                "format": p.suffix.lstrip(".")
            })

    # component/executable mappings
    components = [
        {"id": "exe-game-launch", "name": "Game Launch", "type": "executable", "path": "build/game/launch.py", "icon": "assets/images/icons/executables/game_launch.svg", "fallback_icon": "assets/images/icons/components/python.svg"},
        {"id": "exe-audio-install", "name": "Audio Install", "type": "executable", "path": "systems/audio/install_audio.py", "icon": "assets/images/icons/executables/audio_install.svg", "fallback_icon": "assets/images/icons/components/python.svg"},
        {"id": "exe-dlc-install", "name": "DLC Install", "type": "executable", "path": "systems/launchers/rockstar/dlc/install_dlc.py", "icon": "assets/images/icons/executables/dlc_install.svg", "fallback_icon": "assets/images/icons/components/python.svg"},
        {"id": "exe-steam-ru-fix", "name": "Steam RU Fix Pipeline", "type": "executable", "path": "systems/launchers/steam/russian_fix_pipeline.py", "icon": "assets/images/icons/executables/steam_fix.svg", "fallback_icon": "assets/images/icons/launchers/steam.svg"},
        {"id": "exe-images-install", "name": "Images/Icons Install", "type": "executable", "path": "systems/build/install_images.py", "icon": "assets/images/icons/executables/images_install.svg", "fallback_icon": "assets/images/icons/components/python.svg"},
        {"id": "comp-python", "name": "Python Runtime", "type": "component", "path": ".venv/bin/python", "icon": "assets/images/icons/components/python.svg"},
        {"id": "comp-vscode", "name": "VS Code UI", "type": "component", "path": "systems/runtime/vscode_world_interface.json", "icon": "assets/images/icons/components/vscode.svg"},
        {"id": "comp-kilo", "name": "Kilo Code", "type": "component", "path": "systems/runtime/kilo_code.json", "icon": "assets/images/icons/components/kilo.svg"},
        {"id": "comp-ollama", "name": "Ollama Local AI", "type": "component", "path": "systems/local_ai/connection.json", "icon": "assets/images/icons/components/ollama.png"},
        {"id": "comp-rockstar", "name": "Rockstar Launcher", "type": "launcher", "path": "systems/launchers/rockstar/launcher.json", "icon": "assets/images/icons/launchers/rockstar_launcher.png"},
        {"id": "comp-steam", "name": "Steam", "type": "launcher", "path": "systems/launchers/steam/steam_integration.json", "icon": "assets/images/icons/launchers/steam.svg"},
        {"id": "comp-epic", "name": "Epic Games", "type": "launcher", "path": "systems/launchers/epic/epic_integration.json", "icon": "assets/images/icons/launchers/epic.svg"},
        {"id": "game-gta5", "name": "Grand Theft Auto V", "type": "game", "path": "systems/launchers/rockstar/library/library.json#gta5", "icon": "assets/images/icons/games/gta5_logo.svg"},
        {"id": "game-rdr2", "name": "Red Dead Redemption 2", "type": "game", "path": "systems/launchers/rockstar/library/library.json#rdr2", "icon": "assets/images/icons/games/rdr2_logo.png"},
        {"id": "game-gtao", "name": "GTA Online", "type": "game", "path": "systems/launchers/rockstar/library/library.json#gta5", "icon": "assets/images/icons/launchers/gta_online.png"}
    ]
    manifest = {
        "id": "icons_manifest",
        "generated_at": now(),
        "icons": icons,
        "component_mappings": components,
        "summary": {"total_icons": len(icons), "total_mappings": len(components)}
    }
    save_json(IMAGES / "icons_manifest.json", manifest)
    return manifest


def main():
    all_images = collect_workspace_images()
    installed = install_in_game_images(all_images)
    images_manifest = {
        "id": "images_manifest",
        "generated_at": now(),
        "workspace_images_found": len(all_images),
        "installed": installed,
        "in_game_buckets": {
            "gta5": "assets/images/in_game/gta5",
            "rdr2": "assets/images/in_game/rdr2",
            "common": "assets/images/in_game/common"
        }
    }
    save_json(IMAGES / "images_manifest.json", images_manifest)
    icons_manifest = build_icons_manifest()
    log(f"images_found={len(all_images)} installed={len(installed)} icons={icons_manifest['summary']['total_icons']} mappings={icons_manifest['summary']['total_mappings']}")
    print(json.dumps({
        "images_found": len(all_images),
        "installed": len(installed),
        "icons": icons_manifest["summary"]["total_icons"],
        "mappings": icons_manifest["summary"]["total_mappings"],
        "images_manifest": "assets/images/images_manifest.json",
        "icons_manifest": "assets/images/icons_manifest.json"
    }, indent=2))


if __name__ == "__main__":
    main()
