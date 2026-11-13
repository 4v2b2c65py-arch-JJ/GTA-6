#!/usr/bin/env python3
"""
Install music system: load Spotify track peers, merge with soundtrack, apply installed
sorting algo (systems/audio/music/sorting_algo.py), install EQ/soundboard, emit
frequency state for full library (speaker), and emit sorted playlist/manifests.
"""
import json, hashlib, importlib.util, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MUSIC = ROOT / "systems/audio/music"
AUDIO = ROOT / "systems/audio"
ASSETS = ROOT / "assets/audio/music"
LOG = ROOT / "logs/audio/music/install.log"

def now(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def load(p):
    with open(p,"r",encoding="utf-8") as f: return json.load(f)
def save(p,d):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p,"w",encoding="utf-8") as f: json.dump(d,f,indent=2,ensure_ascii=False)
def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line=f"[{now()}] {msg}\n"
    with open(LOG,"a",encoding="utf-8") as f: f.write(line)
    print(line.strip())

def load_sorter():
    path = MUSIC / "sorting_algo.py"
    spec = importlib.util.spec_from_file_location("sorting_algo", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def run_frequency_emitter():
    emitter = MUSIC / "frequency_emitter.py"
    if emitter.exists():
        r = subprocess.run([sys.executable, str(emitter)], cwd=str(ROOT), capture_output=True, text=True)
        if r.returncode == 0:
            log("frequency_emitter ok")
        else:
            log(f"frequency_emitter rc={r.returncode} err={(r.stderr or '').strip()[:200]}")
    else:
        log("frequency_emitter missing")

def main():
    sorter = load_sorter()
    peers_cfg = load(MUSIC / "spotify_track_peers.json")
    st_cfg = load(AUDIO / "soundtrack/soundtrack.json")
    loader = load(MUSIC / "music_loader.json")

    # normalize soundtrack tracks
    st_tracks = []
    for t in st_cfg.get("tracks", []):
        st_tracks.append({
            "track_id": t.get("track_id"),
            "spotify_id": None,
            "title": t.get("title"),
            "artist": "Spatial Avy OST",
            "album": "Spatial Avy Soundtrack",
            "duration_ms": None,
            "mood": t.get("mood", []),
            "zone": t.get("zone"),
            "beat": t.get("beat"),
            "energy": 0.5,
            "popularity": 50,
            "peers": [t.get("track_id")],
            "source": "soundtrack",
            "file": t.get("file"),
            "installed": t.get("installed", False),
            "install_state": t.get("install_state")
        })

    sp_tracks = peers_cfg.get("tracks", [])
    all_tracks = st_tracks + sp_tracks

    context = loader.get("sorting", {}).get("default_context", {})
    sorted_tracks = sorter.sort_tracks(all_tracks, context=context, reverse=True)
    algo_info = sorter.install_info()

    playlist = {
        "id": "music_playlist_sorted",
        "type": "playlist",
        "generated_at": now(),
        "algo": algo_info,
        "context": context,
        "tracks": sorted_tracks,
        "summary": {
            "total": len(sorted_tracks),
            "soundtrack_tracks": len(st_tracks),
            "spotify_peer_tracks": len(sp_tracks),
            "installed": True
        }
    }
    save(MUSIC / "playlist_sorted.json", playlist)
    save(ASSETS / "music_playlist_sorted.json", playlist)

    # install EQ and soundboard (copy/ensure asset manifests)
    eq = load(MUSIC / "eq_presets.json") if (MUSIC / "eq_presets.json").exists() else None
    sb = load(MUSIC / "soundboard.json") if (MUSIC / "soundboard.json").exists() else None
    if eq:
        eq["installed_at"] = now(); eq["status"] = "installed"
        save(MUSIC / "eq_presets.json", eq); save(ASSETS / "eq_presets.json", eq)
    if sb:
        sb["installed_at"] = now(); sb["status"] = "installed"
        save(MUSIC / "soundboard.json", sb); save(ASSETS / "soundboard.json", sb)

    # emit frequency state (full library, speaker, auto-save)
    run_frequency_emitter()
    freq_state = load(MUSIC / "frequency_state.json") if (MUSIC / "frequency_state.json").exists() else {}

    manifest = {
        "id": "music_manifest",
        "generated_at": now(),
        "algo": algo_info,
        "sources": {
            "soundtrack": "systems/audio/soundtrack/soundtrack.json",
            "spotify_track_peers": "systems/audio/music/spotify_track_peers.json"
        },
        "playlist": "systems/audio/music/playlist_sorted.json",
        "asset_playlist": "assets/audio/music/music_playlist_sorted.json",
        "eq_presets": "systems/audio/music/eq_presets.json",
        "soundboard": "systems/audio/music/soundboard.json",
        "frequency_state": "systems/audio/music/frequency_state.json",
        "speaker_levels": "systems/audio/music/speaker_output_levels.json",
        "peers_count": len(peers_cfg.get("peers", [])),
        "tracks_count": len(sorted_tracks)
    }
    save(ASSETS / "music_manifest.json", manifest)

    state = {
        "id": "music_state",
        "status": "installed",
        "installed_at": now(),
        "provider": "spotify_peers",
        "algo_id": algo_info.get("algo_id"),
        "algo_installed": True,
        "tracks_total": len(sorted_tracks),
        "soundtrack_tracks": len(st_tracks),
        "spotify_tracks": len(sp_tracks),
        "eq_installed": bool(eq),
        "eq_presets_ref": "systems/audio/music/eq_presets.json",
        "soundboard_installed": bool(sb),
        "soundboard_ref": "systems/audio/music/soundboard.json",
        "frequency_emission": {
            "enabled": True,
            "auto_save": True,
            "output": "speaker",
            "state_ref": "systems/audio/music/frequency_state.json",
            "speaker_levels_ref": "systems/audio/music/speaker_output_levels.json",
            "tracks_captured": freq_state.get("library_tracks", len(sorted_tracks))
        },
        "original_sound_quality": True,
        "playlist_ref": "systems/audio/music/playlist_sorted.json",
        "manifest_ref": "assets/audio/music/music_manifest.json"
    }
    save(MUSIC / "music_state.json", state)
    log(f"music installed tracks={len(sorted_tracks)} (ost={len(st_tracks)} spotify={len(sp_tracks)}) algo={algo_info.get('algo_id')} eq={bool(eq)} soundboard={bool(sb)} freq=1")
    print(json.dumps(state, indent=2))

if __name__ == "__main__":
    main()
