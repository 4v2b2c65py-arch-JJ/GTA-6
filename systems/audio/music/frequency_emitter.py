#!/usr/bin/env python3
"""
Frequency emission state for audio/music levels.

Captures/emits frequency-related levels for the full music library as it exits
via speaker output, and saves state automatically (per-track profiles + library
speaker emission snapshot + rolling log).

- If audio media files exist, analyzes them (wave/PCM) to derive band levels.
- If media is placeholder/missing, derives deterministic spectral profiles from
  track features (energy, mood, zone/beat, duration) so the full library is
  covered.
Auto-saves all emitted states on run.
"""
import json
import hashlib
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
MUSIC = ROOT / "systems/audio/music"
AUDIO = ROOT / "systems/audio"
ASSETS = ROOT / "assets/audio/music"
FREQ_SYS = MUSIC / "frequency"
FREQ_ASSETS = ASSETS / "frequency"
LOG = ROOT / "logs/audio/music/frequency_emission.log"

BANDS = [
    ("sub_bass", 20, 60),
    ("bass", 60, 250),
    ("low_mid", 250, 500),
    ("mid", 500, 2000),
    ("high_mid", 2000, 4000),
    ("presence", 4000, 6000),
    ("brilliance", 6000, 20000),
]

MOOD_PROFILE = {
    "ambient":    [0.55, 0.50, 0.45, 0.40, 0.30, 0.25, 0.20],
    "threshold":  [0.50, 0.48, 0.46, 0.42, 0.34, 0.28, 0.22],
    "tense":      [0.45, 0.70, 0.65, 0.55, 0.50, 0.45, 0.35],
    "pulse":      [0.60, 0.80, 0.60, 0.55, 0.50, 0.40, 0.30],
    "cognitive":  [0.30, 0.40, 0.50, 0.60, 0.55, 0.45, 0.35],
    "shimmer":    [0.25, 0.35, 0.45, 0.55, 0.65, 0.70, 0.60],
    "solemn":     [0.50, 0.55, 0.55, 0.50, 0.40, 0.30, 0.25],
    "wide":       [0.45, 0.50, 0.50, 0.55, 0.50, 0.45, 0.40],
    "signal":     [0.35, 0.55, 0.60, 0.65, 0.70, 0.75, 0.60],
    "alert":      [0.40, 0.60, 0.65, 0.70, 0.75, 0.70, 0.55],
    "synth":      [0.50, 0.65, 0.55, 0.60, 0.70, 0.65, 0.55],
    "night":      [0.55, 0.60, 0.50, 0.45, 0.40, 0.35, 0.30],
    "drive":      [0.55, 0.75, 0.65, 0.60, 0.55, 0.45, 0.35],
    "frontier":   [0.40, 0.50, 0.55, 0.60, 0.50, 0.40, 0.30],
    "folk":       [0.35, 0.45, 0.55, 0.65, 0.55, 0.45, 0.35],
}


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{now()}] {msg}\n"
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())


def stable_seed(s):
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:8], 16)


def clamp01(x):
    return float(max(0.0, min(1.0, x)))


def analyze_wav(path):
    """Best-effort FFT band levels from PCM wav if present."""
    try:
        import wave
        with wave.open(str(path), "rb") as wf:
            nchan = wf.getnchannels()
            sw = wf.getsampwidth()
            rate = wf.getframerate()
            nframes = min(wf.getnframes(), rate * 30)  # cap 30s
            raw = wf.readframes(nframes)
        if sw == 2:
            data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        elif sw == 1:
            data = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
        else:
            return None
        if nchan > 1:
            data = data.reshape(-1, nchan).mean(axis=1)
        if data.size < 1024:
            return None
        # windowed FFT average
        win = 4096
        hop = 2048
        acc = np.zeros(len(BANDS))
        count = 0
        window = np.hanning(win)
        for i in range(0, len(data) - win, hop):
            seg = data[i:i+win] * window
            spec = np.abs(np.fft.rfft(seg))
            freqs = np.fft.rfftfreq(win, d=1.0 / rate)
            for b, (_, lo, hi) in enumerate(BANDS):
                idx = np.where((freqs >= lo) & (freqs < hi))[0]
                if idx.size:
                    acc[b] += float(np.mean(spec[idx]))
            count += 1
        if count == 0:
            return None
        acc = acc / count
        mx = float(np.max(acc)) or 1.0
        levels = [clamp01(float(v / mx)) for v in acc]
        peak_db = float(20 * math.log10(mx + 1e-9))
        rms = float(np.sqrt(np.mean(data ** 2)) + 1e-9)
        rms_db = float(20 * math.log10(rms))
        return {
            "bands": {name: round(levels[i], 4) for i, (name, _, _) in enumerate(BANDS)},
            "peak_dbfs": round(max(-60.0, peak_db - 20), 2),
            "rms_dbfs": round(max(-60.0, rms_db), 2),
            "source": "analyzed_audio",
            "sample_rate": rate,
        }
    except Exception:
        return None


def derive_profile(track):
    """Deterministic frequency profile from track features for full-library coverage."""
    tid = str(track.get("track_id") or track.get("id") or track.get("title") or "track")
    rng = np.random.default_rng(stable_seed(tid))
    moods = track.get("mood") or track.get("moods") or ["ambient"]
    energy = float(track.get("energy", 0.5) or 0.5)
    # base from moods
    base = np.zeros(len(BANDS), dtype=np.float32)
    mcount = 0
    for m in moods:
        if m in MOOD_PROFILE:
            base += np.array(MOOD_PROFILE[m], dtype=np.float32)
            mcount += 1
    if mcount == 0:
        base = np.array(MOOD_PROFILE["ambient"], dtype=np.float32)
    else:
        base /= mcount
    # energy shapes spectrum (more energy -> stronger bass/highs)
    energy_curve = np.array([0.9, 1.0, 0.95, 0.9, 0.95, 1.0, 0.9]) * (0.6 + 0.8 * energy)
    prof = base * energy_curve
    # deterministic variation
    jitter = rng.uniform(-0.06, 0.06, size=len(BANDS))
    prof = np.clip(prof + jitter, 0.05, 1.0)
    # normalize a bit
    prof = prof / (float(np.max(prof)) or 1.0) * (0.55 + 0.45 * energy)
    prof = np.clip(prof, 0.04, 1.0)
    bands = {name: round(float(prof[i]), 4) for i, (name, _, _) in enumerate(BANDS)}
    peak = -6.0 - (1.0 - energy) * 12.0 + rng.uniform(-1.5, 1.5)
    rms = peak - (8.0 + rng.uniform(0, 6.0))
    return {
        "bands": bands,
        "peak_dbfs": round(float(max(-36.0, min(-1.0, peak))), 2),
        "rms_dbfs": round(float(max(-48.0, min(-8.0, rms))), 2),
        "source": "derived_profile",
    }


def speaker_output_mix(track_levels):
    """Compute aggregate 'speaker output' levels for library exiting via speaker."""
    if not track_levels:
        return {"bands": {n: 0.0 for n, _, _ in BANDS}, "master_rms_dbfs": -60.0, "master_peak_dbfs": -60.0}
    arr = np.array([[tl["bands"][n] for n, _, _ in BANDS] for tl in track_levels], dtype=np.float32)
    # perceived output mix (RMS-like across library)
    mix = np.sqrt(np.mean(arr ** 2, axis=0))
    mx = float(np.max(mix)) or 1.0
    mix = np.clip(mix / mx * 0.92, 0.0, 1.0)
    peaks = [tl.get("peak_dbfs", -24.0) for tl in track_levels]
    rmses = [tl.get("rms_dbfs", -30.0) for tl in track_levels]
    return {
        "bands": {name: round(float(mix[i]), 4) for i, (name, _, _) in enumerate(BANDS)},
        "master_peak_dbfs": round(float(max(peaks)), 2),
        "master_rms_dbfs": round(float(sum(rmses) / len(rmses)), 2),
        "tracks_mixed": len(track_levels),
    }


def load_library_tracks():
    tracks = []
    # prefer sorted playlist (full library: soundtrack + spotify peers)
    plist = MUSIC / "playlist_sorted.json"
    if plist.exists():
        data = load_json(plist)
        tracks = list(data.get("tracks", []))
    else:
        # fallback: soundtrack + spotify peers
        st = AUDIO / "soundtrack/soundtrack.json"
        sp = MUSIC / "spotify_track_peers.json"
        if st.exists():
            for t in load_json(st).get("tracks", []):
                tracks.append({**t, "source": "soundtrack"})
        if sp.exists():
            tracks.extend(load_json(sp).get("tracks", []))
    return tracks


def main():
    ts = now()
    tracks = load_library_tracks()
    FREQ_SYS.mkdir(parents=True, exist_ok=True)
    FREQ_ASSETS.mkdir(parents=True, exist_ok=True)

    per_track = []
    track_levels_for_mix = []
    analyzed = 0
    derived = 0
    for t in tracks:
        tid = str(t.get("track_id") or t.get("id") or hashlib.sha256(str(t).encode()).hexdigest()[:12])
        file_ref = t.get("file")
        freq = None
        media_path = None
        if file_ref:
            p = ROOT / file_ref
            media_path = str(file_ref)
            if p.exists() and p.suffix.lower() == ".wav":
                freq = analyze_wav(p)
        if freq is None:
            freq = derive_profile(t)
            derived += 1
        else:
            analyzed += 1
        rec = {
            "track_id": tid,
            "title": t.get("title") or t.get("name"),
            "artist": t.get("artist"),
            "source": t.get("source"),
            "zone": t.get("zone"),
            "beat": t.get("beat"),
            "mood": t.get("mood") or t.get("moods"),
            "file": media_path,
            "frequency": freq,
            "captured_at": ts,
            "output": "speaker",
        }
        per_track.append(rec)
        track_levels_for_mix.append(freq)
        save_json(FREQ_SYS / f"{tid}.json", rec)
        save_json(FREQ_ASSETS / f"{tid}.json", rec)

    speaker = speaker_output_mix(track_levels_for_mix)
    speaker_state = {
        "id": "speaker_output_frequency_state",
        "type": "frequency_emission_state",
        "status": "emitting",
        "captured_at": ts,
        "output_target": "speaker",
        "library": "full",
        "auto_save": True,
        "bands_hz": {name: [lo, hi] for name, lo, hi in BANDS},
        "speaker_levels": speaker,
        "tracks_captured": len(per_track),
        "analyzed_audio": analyzed,
        "derived_profiles": derived,
        "track_refs": [f"systems/audio/music/frequency/{r['track_id']}.json" for r in per_track],
    }

    full_state = {
        "id": "music_frequency_state",
        "type": "frequency_state",
        "status": "active",
        "updated_at": ts,
        "output": "speaker",
        "auto_save": True,
        "library_tracks": len(per_track),
        "speaker_output": speaker_state,
        "summary": {
            "tracks": len(per_track),
            "analyzed_audio": analyzed,
            "derived_profiles": derived,
            "bands": [n for n, _, _ in BANDS],
        },
    }

    # auto-save all states
    save_json(MUSIC / "frequency_state.json", full_state)
    save_json(MUSIC / "speaker_output_levels.json", speaker_state)
    save_json(ASSETS / "frequency_state.json", full_state)
    save_json(ASSETS / "speaker_output_levels.json", speaker_state)
    save_json(FREQ_SYS / "library_index.json", {"id": "frequency_library_index", "updated_at": ts, "tracks": [r["track_id"] for r in per_track]})
    save_json(FREQ_ASSETS / "library_index.json", {"id": "frequency_library_index", "updated_at": ts, "tracks": [r["track_id"] for r in per_track]})

    # append emission log (capped keep)
    log_entry = {"ts": ts, "event": "frequency_emit", "tracks": len(per_track), "output": "speaker", "speaker_levels": speaker}
    log_path = MUSIC / "frequency_emission_log.json"
    history = []
    if log_path.exists():
        try:
            history = load_json(log_path).get("events", [])
        except Exception:
            history = []
    history.append(log_entry)
    history = history[-200:]
    log_payload = {"id": "frequency_emission_log", "events": history}
    save_json(log_path, log_payload)
    save_json(ASSETS / "frequency_emission_log.json", log_payload)

    log(f"frequency emitted tracks={len(per_track)} analyzed={analyzed} derived={derived} output=speaker auto_saved=true")
    print(json.dumps({"status": "emitted", "tracks": len(per_track), "analyzed": analyzed, "derived": derived, "auto_saved": True, "output": "speaker"}, indent=2))


if __name__ == "__main__":
    main()
