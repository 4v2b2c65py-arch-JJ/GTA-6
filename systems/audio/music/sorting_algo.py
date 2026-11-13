"""
Installed in-game sorting algorithm for Spatial Avy music system.

"my_sorting_algo" is the authoritative sorter installed into the game runtime:
- sorts tracks/playlists using peer affinity, zone/beat/mood alignment, energy,
  popularity, and stable title tie-breakers.
- can be imported and used by loaders, runtime, and web/player data pipelines.

Customize weights or logic here to change in-game music ordering behavior.
"""

from __future__ import annotations

ALGO_ID = "spatial_peer_sort_v1"
ALGO_NAME = "Spatial Peer Sort (installed)"

DEFAULT_WEIGHTS = {
    "peer_affinity": 3.0,
    "zone_match": 2.5,
    "beat_match": 2.5,
    "mood_match": 1.5,
    "energy": 1.0,
    "popularity": 0.5,
}

ZONE_ORDER = {"Z0": 0, "Z1": 1, "Z2": 2, "Z3": 3, "Z4": 4, "Z5": 5, "M0": 6, "S0": 7}
BEAT_ORDER = {f"BEAT_{i}": i for i in range(6)}


def _peer_affinity(track, context):
    peers = set(track.get("peers") or [])
    preferred = set((context or {}).get("preferred_peers") or [])
    seed = (context or {}).get("seed_track_id")
    score = len(peers & preferred)
    if seed and seed in peers:
        score += 2
    # boost if track is itself preferred
    if track.get("track_id") in preferred or track.get("id") in preferred:
        score += 2
    return score


def _match_score(track_val, ctx_vals):
    if not ctx_vals:
        return 0
    if isinstance(track_val, list):
        return len(set(track_val) & set(ctx_vals))
    return 1 if track_val in set(ctx_vals) else 0


def score_track(track, context=None, weights=None):
    ctx = context or {}
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    zone = track.get("zone")
    beat = track.get("beat")
    moods = track.get("mood") or track.get("moods") or []
    energy = float(track.get("energy", 0.5) or 0.5)
    popularity = float(track.get("popularity", 50) or 50) / 100.0
    s = 0.0
    s += w["peer_affinity"] * _peer_affinity(track, ctx)
    s += w["zone_match"] * _match_score(zone, ctx.get("zones") or [])
    s += w["beat_match"] * _match_score(beat, ctx.get("beats") or [])
    s += w["mood_match"] * _match_score(moods, ctx.get("moods") or [])
    s += w["energy"] * energy
    s += w["popularity"] * popularity
    # small timeline ordering bias (earlier zones/beats first unless context overrides)
    z_bias = ZONE_ORDER.get(zone, 99)
    b_bias = BEAT_ORDER.get(beat, 99)
    s += max(0.0, (20 - z_bias - b_bias) * 0.01)
    return round(s, 6)


def sort_tracks(tracks, context=None, weights=None, reverse=True):
    """Return tracks sorted by installed algo. Higher score first by default."""
    ctx = context or {}
    indexed = []
    for i, t in enumerate(tracks or []):
        t2 = dict(t)
        t2["_sort_score"] = score_track(t2, ctx, weights)
        t2["_sort_index"] = i
        indexed.append(t2)
    indexed.sort(
        key=lambda x: (
            x.get("_sort_score", 0),
            -ZONE_ORDER.get(x.get("zone"), 99),
            -BEAT_ORDER.get(x.get("beat"), 99),
            str(x.get("title") or x.get("name") or "").lower(),
            x.get("_sort_index", 0),
        ),
        reverse=reverse,
    )
    # expose rank
    for rank, t in enumerate(indexed, start=1):
        t["sort_rank"] = rank
        t["sort_algo"] = ALGO_ID
    return indexed


def install_info():
    return {
        "algo_id": ALGO_ID,
        "name": ALGO_NAME,
        "installed": True,
        "weights": DEFAULT_WEIGHTS,
        "entrypoint": "systems/audio/music/sorting_algo.py:sort_tracks",
        "description": "In-game installed sorting algo: peer-affinity + zone/beat/mood alignment + energy/popularity + stable ordering."
    }
