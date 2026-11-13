#!/usr/bin/env python3
"""Generate multiple terrain code sets from Bodium terrain map (python nmap)."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TERRAIN_MAP = ROOT / "home_world" / "bodium_terrain" / "bodium_terrain_map.json"
OUT_JSON = ROOT / "home_world" / "bodium_terrain" / "terrain_code_sets.json"
DOOR_STRING = "N10-N9-N8-N7-N6-N5-N4-N3-N2-N1-N0"


def load_map():
    with TERRAIN_MAP.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_sets(data):
    regions = data.get("regions", [])
    base = []
    elev = []
    state = []
    narrative = []
    lace = []
    material = []

    for i, r in enumerate(regions):
        rid = r["id"]
        beat = r.get("narrative_anchor", "NA")
        st = r.get("state", "unknown")
        mat = r.get("material", "unknown")
        el = r.get("elevation", 0)
        el_code = int(round(float(el) * 10))
        idx = rid.split("-")[0] if "-" in rid else rid

        base.append({
            "code": f"TERR-{idx}",
            "region_id": rid,
            "name": r.get("name"),
            "set": "base"
        })
        elev.append({
            "code": f"ELEV-{idx}-{el_code:03d}",
            "region_id": rid,
            "elevation": el,
            "set": "elevation"
        })
        state.append({
            "code": f"STATE-{idx}-{st.upper()}",
            "region_id": rid,
            "state": st,
            "properties": r.get("properties", {}),
            "set": "state"
        })
        narrative.append({
            "code": f"BEAT-{idx}-{beat}",
            "region_id": rid,
            "narrative_anchor": beat,
            "set": "narrative"
        })
        material.append({
            "code": f"MAT-{idx}-{mat.upper()}",
            "region_id": rid,
            "material": mat,
            "set": "material"
        })
        # multiple lace/on-set variants per region
        for q in range(2):
            for c in range(2):
                lace.append({
                    "code": f"LACE-{idx}-Q{q}-C{c:03d}-T0",
                    "lace_key": f"Z{idx.replace('Z','')}-Q{q}-C{c:03d}-T0",
                    "region_id": rid,
                    "pocket": f"Q{q}",
                    "cell": f"C{c:03d}",
                    "tick": 0,
                    "set": "lace"
                })

    # composite/on-set codes combining dimensions
    composite = []
    for r in regions:
        rid = r["id"]
        idx = rid.split("-")[0] if "-" in rid else rid
        beat = r.get("narrative_anchor", "NA")
        st = r.get("state", "unknown")
        el_code = int(round(float(r.get("elevation", 0)) * 10))
        composite.append({
            "code": f"ONSET-{idx}|{beat}|{st.upper()}|E{el_code:03d}",
            "region_id": rid,
            "narrative_anchor": beat,
            "state": st,
            "elevation_code": el_code,
            "set": "composite_onset"
        })

    return {
        "meta": {
            "source": str(TERRAIN_MAP.relative_to(ROOT)),
            "generator": "home_world/bodium_terrain/terrain_nmap.py",
            "door_node_string": DOOR_STRING,
            "lace_pattern": "Z<zone>-Q<pocket>-C<cell>-T<tick>",
            "region_count": len(regions)
        },
        "sets": {
            "base": base,
            "elevation": elev,
            "state": state,
            "material": material,
            "narrative": narrative,
            "lace": lace,
            "composite_onset": composite
        },
        "counts": {
            "base": len(base),
            "elevation": len(elev),
            "state": len(state),
            "material": len(material),
            "narrative": len(narrative),
            "lace": len(lace),
            "composite_onset": len(composite),
            "total": len(base)+len(elev)+len(state)+len(material)+len(narrative)+len(lace)+len(composite)
        }
    }


def main():
    data = load_map()
    out = build_sets(data)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {OUT_JSON} (total codes: {out['counts']['total']})")


if __name__ == "__main__":
    main()
