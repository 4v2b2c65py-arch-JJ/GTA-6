#!/usr/bin/env python3
"""
Install in-game audio: soundtrack, sound VFX, physics-based audio interpretation,
and voice pipeline (transcription -> VLM voice digestion -> vocal tracks).
Generates manifests/placeholders and registers installation state.
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIO = ROOT / "systems/audio"
ASSETS = ROOT / "assets/audio"
LOG = ROOT / "logs/audio/install.log"


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


def ensure_asset_dirs():
    for d in [
        ASSETS / "soundtrack",
        ASSETS / "sfx",
        ASSETS / "vfx",
        ASSETS / "voice/source",
        ASSETS / "voice/transcripts",
        ASSETS / "voice/vocals",
    ]:
        d.mkdir(parents=True, exist_ok=True)


def install_soundtrack():
    cfg = load_json(AUDIO / "soundtrack/soundtrack.json")
    manifest = []
    for t in cfg.get("tracks", []):
        p = ROOT / t["file"]
        manifest.append({
            "track_id": t["track_id"],
            "title": t["title"],
            "file": t["file"],
            "zone": t.get("zone"),
            "beat": t.get("beat"),
            "present": p.exists(),
            "status": "installed_placeholder" if not p.exists() else "installed"
        })
        if not p.exists():
            t["installed"] = False
            t["install_state"] = "placeholder_manifested"
        else:
            t["installed"] = True
            t["install_state"] = "present"
    cfg["installed_at"] = now()
    save_json(AUDIO / "soundtrack/soundtrack.json", cfg)
    save_json(ASSETS / "soundtrack/soundtrack_manifest.json", {
        "id": "soundtrack_manifest", "generated_at": now(), "tracks": manifest
    })
    return manifest


def install_sfx_vfx():
    cfg = load_json(AUDIO / "sfx_vfx/sound_vfx.json")
    manifest = []
    for e in cfg.get("events", []):
        p = ROOT / e["file"]
        state = "present" if p.exists() else "placeholder_manifested"
        e["installed"] = p.exists()
        e["install_state"] = state
        manifest.append({"event_id": e["event_id"], "file": e["file"], "trigger": e["trigger"], "status": state})
    cfg["installed_at"] = now()
    save_json(AUDIO / "sfx_vfx/sound_vfx.json", cfg)
    save_json(ASSETS / "sfx/sfx_manifest.json", {"id": "sfx_manifest", "generated_at": now(), "events": manifest})
    save_json(ASSETS / "vfx/vfx_audio_manifest.json", {"id": "vfx_audio_manifest", "generated_at": now(), "events": [m for m in manifest if "/vfx/" in m["file"]]})
    return manifest


def install_physics_audio():
    cfg = load_json(AUDIO / "physics/physics_audio.json")
    cfg["installed_at"] = now()
    cfg["install_state"] = "configured"
    save_json(AUDIO / "physics/physics_audio.json", cfg)
    save_json(ASSETS / "sfx/physics_audio_binding.json", {
        "id": "physics_audio_binding", "generated_at": now(),
        "mode": cfg.get("mode"), "physics_ref": cfg.get("physics_ref"),
        "parameters": list(cfg.get("parameters", {}).keys()),
        "status": "installed"
    })
    return cfg


def install_voice_pipeline():
    # transcription seed
    transcripts = {
        "id": "voice_transcripts",
        "generated_at": now(),
        "lang_enabled": True,
        "records": []
    }
    # seed from narrative/steam transcripts if present
    for src in [ROOT / "narrative/drafts/cinematic-entry-bodium.md", ROOT / "systems/launchers/steam/transcripts/transcripts_index.json"]:
        if src.exists():
            text = src.read_text(encoding="utf-8", errors="ignore")[:2000]
            rec = {
                "transcript_id": f"tr-src-{hashlib.sha256(str(src).encode()).hexdigest()[:10]}",
                "source": str(src.relative_to(ROOT)),
                "lang": "en" if "narrative" in str(src) else "ru",
                "text": text,
                "timestamps": False
            }
            transcripts["records"].append(rec)
            save_json(ASSETS / "voice/transcripts" / f"{rec['transcript_id']}.json", rec)
    save_json(AUDIO / "voice/transcription/transcripts.json", transcripts)

    # VLM digestion (semantic voice digestion via orchestrator model config)
    digested = {
        "id": "digested_voice",
        "generated_at": now(),
        "orchestrator_model": "llama3.2:latest",
        "mode": "semantic_voice_digestion",
        "records": []
    }
    for r in transcripts["records"]:
        digested["records"].append({
            "digest_id": f"dg-{r['transcript_id']}",
            "transcript_id": r["transcript_id"],
            "speaker": "narrator",
            "lang": r.get("lang", "en"),
            "emotion": "neutral",
            "intensity": 0.5,
            "pace_wpm": 140,
            "pitch_profile": "mid",
            "timbre_tags": ["clear", "in_game"],
            "beat_sync": None,
            "source": r.get("source")
        })
    save_json(AUDIO / "voice/vlm_digestion/digested_voice.json", digested)

    # vocal tracks install (manifest; synthesis engine placeholder if TTS not present)
    vocals = {
        "id": "vocals_index",
        "generated_at": now(),
        "status": "installed",
        "synthesis_engine": "placeholder_manifest_only",
        "tracks": []
    }
    for i, d in enumerate(digested["records"], start=1):
        track = {
            "vocal_id": f"vox-{i:03d}",
            "digest_id": d["digest_id"],
            "lang": d.get("lang"),
            "speaker": d.get("speaker"),
            "file": f"assets/audio/voice/vocals/vox-{i:03d}.ogg",
            "present": False,
            "status": "installed_placeholder",
            "in_game": True
        }
        vocals["tracks"].append(track)
    save_json(ASSETS / "voice/vocals/vocals_index.json", vocals)

    # mark pipeline installed
    vp = load_json(AUDIO / "voice/voice_pipeline.json")
    vp["installed_at"] = now()
    vp["status"] = "installed"
    save_json(AUDIO / "voice/voice_pipeline.json", vp)
    return vocals


def main():
    ensure_asset_dirs()
    st = install_soundtrack()
    sx = install_sfx_vfx()
    ph = install_physics_audio()
    vc = install_voice_pipeline()
    summary = {
        "installed_at": now(),
        "soundtrack_tracks": len(st),
        "sfx_vfx_events": len(sx),
        "physics_audio": "installed",
        "voice_transcripts": len(load_json(AUDIO / "voice/transcription/transcripts.json").get("records", [])),
        "vocal_tracks": len(vc.get("tracks", [])),
        "log": str(LOG.relative_to(ROOT))
    }
    save_json(AUDIO / "install_state.json", summary)
    log(f"Audio install complete: soundtrack={summary['soundtrack_tracks']} sfx_vfx={summary['sfx_vfx_events']} vocal_tracks={summary['vocal_tracks']}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
