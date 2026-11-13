#!/usr/bin/env python3
"""
Steam Russian fix pipeline (speed-up): ingest researched guide/source data, enable
language/transcript flow, transform via Python, emit game data, and register
websites/in-game fixes for world builds.
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONFIG = ROOT / "systems/launchers/steam/russian_fix.json"
GUIDES_OUT = ROOT / "systems/launchers/steam/guides/guides.json"
TRANSCRIPTS_OUT = ROOT / "systems/launchers/steam/transcripts/transcripts_index.json"
FIXES_OUT = ROOT / "systems/launchers/steam/fixes/fixes.json"
GAME_DATA_OUT = ROOT / "assets/game_assets/steam_fixes/steam_fix_game_data.json"
WORLD_LOADER = ROOT / "systems/world_builds/web_loader/web_loader.json"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(p):
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def hid(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


# Researched guide/fix records (from web research) with transcript-enabled text
RESEARCHED_GUIDES = [
    {
        "id": "guide-steam-fix-ru",
        "source_id": "steam_fix_ru_script",
        "title": "Steam Fix RU — remove l=russian from store CSS/JS resources",
        "url": "https://greasyfork.org/en/scripts/515187-steam-fix-ru",
        "lang": "ru",
        "tags": ["steam", "store", "russian", "css", "js", "fix"],
        "summary": "Userscript removes l=russian query param from store.steampowered.com stylesheet/script URLs to fix broken/mismatched localized resources.",
        "steps": [
            "Match store.steampowered.com resources (link[rel=stylesheet], script[src]).",
            "If URL has l=russian, remove the parameter and update resource URL.",
            "Run on load and observe DOM mutations for dynamically added resources."
        ],
        "transcript": {
            "enabled": True,
            "lang": "ru",
            "text": "Steam Fix RU: убирает параметр l=russian из URL для CSS и JS на store.steampowered.com. Скрипт проверяет link/script ресурсы, удаляет l=russian и обновляет URL; работает при загрузке и через MutationObserver."
        }
    },
    {
        "id": "guide-zoneofgames",
        "source_id": "zoneofgames",
        "title": "Zone of Games — русификаторы и фиксы (RU guides)",
        "url": "https://www.zoneofgames.ru",
        "lang": "ru",
        "tags": ["russian", "localization", "fix", "guides", "downloads"],
        "summary": "Russian localization/fix guide hub; source for game-specific RU fixes and installer guides.",
        "steps": [
            "Find game-specific localization/fix guide.",
            "Check game version compatibility and backup files.",
            "Install per guide (auto/copy/manual) and verify in-game language."
        ],
        "transcript": {
            "enabled": True,
            "lang": "ru",
            "text": "Zone of Games: каталог русификаторов и гайдов. Рекомендуется проверять совместимость с версией игры, делать резервные копии и устанавливать по инструкции (автоустановка/копирование файлов)."
        }
    },
    {
        "id": "guide-playground-ru",
        "source_id": "playground",
        "title": "PlayGround — русификаторы и переводы",
        "url": "https://www.playground.ru/file/rus",
        "lang": "ru",
        "tags": ["russian", "translation", "mods", "fix"],
        "summary": "Russian translations/localization files and fix guides for games.",
        "steps": [
            "Select game and matching localization version.",
            "Download and apply per instructions; verify integrity if issues."
        ],
        "transcript": {
            "enabled": True,
            "lang": "ru",
            "text": "PlayGround: русификаторы и переводы для игр. Выбор версии под игру, установка по инструкции, проверка после обновлений."
        }
    },
    {
        "id": "guide-steam-language",
        "source_id": "steam_support_localization",
        "title": "Steam language/localization flow (properties, files, in-game)",
        "url": "https://partner.steamgames.com/doc/store/localization?language=russian",
        "lang": "ru",
        "tags": ["steam", "language", "localization", "settings"],
        "summary": "Steam supports store and in-game localization; language can be set per-game (Properties > General/Language), may require file download, and in-game audio/subtitles/interface can differ.",
        "steps": [
            "Check supported languages (interface/subtitles/audio) on store page.",
            "Set game language in Steam Library > Properties (or in-game settings).",
            "Wait for language depots/downloads; restart game; verify files if needed.",
            "Use launch options or config only when documented (e.g. -language)."
        ],
        "transcript": {
            "enabled": True,
            "lang": "ru",
            "text": "Локализация Steam: язык игры задаётся в свойствах игры или в настройках самой игры; после смены могут загружаться языковые файлы. Интерфейс, субтитры и озвучка поддерживаются отдельно; проверяйте наличие перевода на странице магазина."
        }
    }
]

RESEARCHED_FIXES = [
    {
        "fix_id": "fix-steam-store-l-russian",
        "source_id": "steam_fix_ru_script",
        "title": "Remove l=russian from Steam store asset URLs",
        "type": "web_resource_fix",
        "target": "store.steampowered.com",
        "enabled": True,
        "lang": "ru",
        "action": {"op": "remove_query_param", "param": "l", "value": "russian", "selectors": ["link[rel=stylesheet]", "script[src]"]},
        "apply": "in_game_web_loader_or_overlay"
    },
    {
        "fix_id": "fix-steam-game-language-flow",
        "source_id": "steam_support_localization",
        "title": "Steam per-game language/transcript enable flow",
        "type": "config_flow",
        "target": "steam_client_game",
        "enabled": True,
        "lang": "ru",
        "action": {"op": "set_language", "path": "Properties>General>Language", "fallback": "in_game_settings", "post": ["wait_downloads", "restart", "verify_files"]},
        "apply": "launcher_integration"
    }
]


def main():
    cfg = load_json(CONFIG)
    ts = now()

    # guides
    guides = {
        "id": "steam_russian_fix_guides",
        "generated_at": ts,
        "lang_enabled": True,
        "transcript_enabled": True,
        "sources": [s["source_id"] for s in cfg.get("sources", [])],
        "guides": RESEARCHED_GUIDES,
        "summary": {"total": len(RESEARCHED_GUIDES)}
    }
    save_json(GUIDES_OUT, guides)

    # transcripts index (lang-enabled transcript records)
    t_records = []
    for g in RESEARCHED_GUIDES:
        tr = g.get("transcript", {})
        rec = {
            "transcript_id": f"tr-{g['id']}",
            "guide_id": g["id"],
            "source_id": g["source_id"],
            "url": g["url"],
            "lang": tr.get("lang", g.get("lang", "ru")),
            "enabled": bool(tr.get("enabled", False)),
            "hash": hid(tr.get("text", "")),
            "text": tr.get("text", ""),
            "ts": ts
        }
        t_records.append(rec)
        # per-transcript file for direct loading
        save_json(ROOT / f"systems/launchers/steam/transcripts/{rec['transcript_id']}.json", rec)

    transcripts = {
        "id": "steam_russian_fix_transcripts",
        "generated_at": ts,
        "lang_enabled": True,
        "records": t_records,
        "summary": {"total": len(t_records), "enabled": sum(1 for r in t_records if r["enabled"])}
    }
    save_json(TRANSCRIPTS_OUT, transcripts)

    # fixes
    fixes = {
        "id": "steam_russian_fix_fixes",
        "generated_at": ts,
        "fixes": RESEARCHED_FIXES,
        "summary": {"total": len(RESEARCHED_FIXES), "enabled": sum(1 for f in RESEARCHED_FIXES if f.get("enabled"))}
    }
    save_json(FIXES_OUT, fixes)

    # game data emit (Python -> game data)
    game_data = {
        "id": "steam_fix_game_data",
        "type": "game_data",
        "generated_at": ts,
        "pipeline": "systems/launchers/steam/russian_fix_pipeline.py",
        "lang": cfg.get("language", {}),
        "guides_ref": str(GUIDES_OUT.relative_to(ROOT)),
        "transcripts_ref": str(TRANSCRIPTS_OUT.relative_to(ROOT)),
        "fixes_ref": str(FIXES_OUT.relative_to(ROOT)),
        "entries": [
            {
                "entry_id": f"gd-{g['id']}",
                "kind": "guide",
                "source_id": g["source_id"],
                "title": g["title"],
                "url": g["url"],
                "lang": g.get("lang"),
                "tags": g.get("tags", []),
                "transcript_id": f"tr-{g['id']}",
                "transcript_enabled": True,
                "hash": hid(g["id"] + g["url"])
            } for g in RESEARCHED_GUIDES
        ] + [
            {
                "entry_id": f"gd-{f['fix_id']}",
                "kind": "fix",
                "source_id": f["source_id"],
                "title": f["title"],
                "target": f.get("target"),
                "lang": f.get("lang"),
                "hash": hid(f["fix_id"])
            } for f in RESEARCHED_FIXES
        ],
        "summary": {"total_entries": len(RESEARCHED_GUIDES) + len(RESEARCHED_FIXES)}
    }
    save_json(GAME_DATA_OUT, game_data)

    # world build web loader registration
    loader = {
        "id": "world_web_loader",
        "type": "web_loader",
        "version": "1.0.0",
        "status": "active",
        "generated_at": ts,
        "description": "Loads websites and in-game fixes directly for world builds; fed by Steam RU fix pipeline (lang/transcript enabled).",
        "pipeline_ref": "systems/launchers/steam/russian_fix.json",
        "game_data_ref": str(GAME_DATA_OUT.relative_to(ROOT)),
        "load_websites": True,
        "load_in_game_fixes": True,
        "websites": [
            {"id": g["source_id"], "title": g["title"], "url": g["url"], "lang": g.get("lang", "ru"), "transcript_enabled": True, "load": "direct"}
            for g in RESEARCHED_GUIDES
        ],
        "in_game_fixes": [
            {"fix_id": f["fix_id"], "title": f["title"], "type": f["type"], "target": f.get("target"), "enabled": f.get("enabled", True), "apply": f.get("apply")}
            for f in RESEARCHED_FIXES
        ],
        "summary": {"websites": len(RESEARCHED_GUIDES), "in_game_fixes": len(RESEARCHED_FIXES)}
    }
    save_json(WORLD_LOADER, loader)

    print(f"Wrote {GUIDES_OUT}")
    print(f"Wrote {TRANSCRIPTS_OUT} (+{len(t_records)} transcript files)")
    print(f"Wrote {FIXES_OUT}")
    print(f"Wrote {GAME_DATA_OUT}")
    print(f"Wrote {WORLD_LOADER}")


if __name__ == "__main__":
    main()
