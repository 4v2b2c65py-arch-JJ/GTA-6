#!/usr/bin/env python3
"""Compute region scenery report with IDs for terrain, nodes, and FPV devices."""

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PATHS = {
    "terrain": ROOT / "home_world/bodium_terrain/bodium_terrain_map.json",
    "nodes": ROOT / "home_world/gates_nodes/door_node_map.json",
    "alien": ROOT / "home_world/gates_nodes/alien_node.json",
    "fpv": ROOT / "systems/fpv/game_fpv_devices.json",
}


def load(p):
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def scenery_profile(region):
    props = region.get("properties", {})
    elev = float(region.get("elevation", 0))
    fracture = float(props.get("fracture_risk", 0))
    instability = float(props.get("instability", 0))
    traction = float(props.get("traction", 1.0))
    visibility = 1.0 if props.get("visibility") == "full_catch" else 0.5
    resonance = props.get("resonance", "neutral")
    vein = props.get("vein_light", "neutral")

    complexity = round(0.3 + elev * 0.25 + fracture * 0.2 + instability * 0.25, 3)
    navigability = round(max(0.0, min(1.0, traction - fracture * 0.3 - instability * 0.4)), 3)
    hazard = round(max(0.0, min(1.0, fracture * 0.6 + instability * 0.5 + (0.2 if props.get("heave") else 0))), 3)
    luminance = {
        "dim_silver": 0.3, "brightening": 0.65, "edge_glow": 0.55,
        "stressed": 0.6, "focused": 0.85, "held_glow": 0.5
    }.get(vein, 0.4)
    atmosphere = {
        "dim_silver": "calm, low resonance mineral hush",
        "brightening": "charged fracture glare, rising tension",
        "edge_glow": "kinetic rim-light, forward momentum",
        "stressed": "strained shimmer, heaving pressure",
        "focused": "revelatory beam, high contrast crest",
        "held_glow": "settled aftertone, altered calm",
    }.get(vein, "neutral bodium ambience")

    return {
        "atmosphere": atmosphere,
        "vein_light": vein,
        "resonance": resonance,
        "indices": {
            "complexity": complexity,
            "navigability": navigability,
            "hazard": hazard,
            "visibility": visibility,
            "luminance": luminance,
        },
    }


def main():
    terrain = load(PATHS["terrain"])
    nodes = load(PATHS["nodes"])
    alien = load(PATHS["alien"])
    fpv = load(PATHS["fpv"])

    nodes_by_zone = defaultdict(list)
    for n in nodes.get("nodes", []):
        nodes_by_zone[n["zone_ref"]].append({
            "node_id": n["id"],
            "label": n.get("label"),
            "state": n.get("state"),
            "links": n.get("links", []),
            "protocol_ref": n.get("protocol_ref"),
        })
    if alien.get("zone_ref"):
        nodes_by_zone[alien["zone_ref"]].append({
            "node_id": alien.get("node_id"),
            "label": alien.get("label"),
            "state": alien.get("state"),
            "links": alien.get("links", []),
            "classification": alien.get("classification"),
            "webclient": alien.get("webclient", {}).get("id"),
        })

    devices_by_zone = defaultdict(list)
    for rig in fpv.get("fpvs", []):
        for d in rig.get("active_devices", []):
            # map by mount/stud-region context via known refs; fallback to zone inference not stored, so include with fpv context
            devices_by_zone["_unscoped"].append({
                "fpv_id": rig.get("fpv_id"),
                "fpv_name": rig.get("name"),
                "device_id": d.get("device_id"),
                "model": d.get("model"),
                "role": d.get("role"),
                "status": d.get("status"),
                "power": d.get("power"),
                "mount": d.get("mount", {}),
            })

    # attach devices by stud region naming heuristic to zones through node/terrain context not explicit; provide per-fpv+region listing
    # better: compute per region scenery and include all nodes in zone and fpv devices mounted to regions conceptually mapped
    region_to_studs = {
        "Z0-core-plate": ["head_center", "head_left"],  # N10,N9,N-ALIEN area
        "Z1-fault-belt": [],
        "Z2-traction-run": [],
        "Z3-cant-plates": [],
        "Z4-crest-reveal": [],
        "Z5-settled-path": [],
    }
    # also include back/chest mounted devices as global; we’ll list them under a fpv overlay and per-region availability
    all_devices = devices_by_zone["_unscoped"]

    regions_out = []
    for r in terrain.get("regions", []):
        z = r["id"]
        scene = scenery_profile(r)
        zone_nodes = nodes_by_zone.get(z, [])
        # devices relevant: those whose mount region name hints not direct, so include fpv presence summary per region
        regions_out.append({
            "region_id": z,
            "region_name": r.get("name"),
            "narrative_anchor": r.get("narrative_anchor"),
            "state": r.get("state"),
            "elevation": r.get("elevation"),
            "ids": {
                "node_ids": [n["node_id"] for n in zone_nodes],
                "nodes": zone_nodes,
            },
            "computed_scenery": scene,
        })

    report = {
        "id": "scenery_compute_report",
        "source": {
            "terrain": str(PATHS["terrain"].relative_to(ROOT)),
            "nodes": str(PATHS["nodes"].relative_to(ROOT)),
            "alien_node": str(PATHS["alien"].relative_to(ROOT)),
            "fpv": str(PATHS["fpv"].relative_to(ROOT)),
        },
        "lighting": terrain.get("lighting"),
        "regions": regions_out,
        "fpv_devices": {
            "summary": fpv.get("summary"),
            "devices": all_devices,
            "fpvs": [{"fpv_id": x.get("fpv_id"), "name": x.get("name"), "state": x.get("state"), "device_ids": [d.get("device_id") for d in x.get("active_devices", [])]} for x in fpv.get("fpvs", [])]
        },
        "totals": {
            "regions": len(regions_out),
            "nodes": len(nodes.get("nodes", [])) + 1,
            "fpv_devices": len(all_devices),
            "active_fpvs": len(fpv.get("fpvs", [])),
        },
    }

    out_path = ROOT / "home_world/bodium_terrain/scenery_compute.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Wrote {out_path}")
    # print compact summary
    for r in regions_out:
        print(f"{r['region_id']} | nodes={r['ids']['node_ids']} | hazard={r['computed_scenery']['indices']['hazard']} lum={r['computed_scenery']['indices']['luminance']} nav={r['computed_scenery']['indices']['navigability']} | {r['computed_scenery']['atmosphere']}")
    print("FPV_DEVICES:", [d["device_id"] for d in all_devices])


if __name__ == "__main__":
    main()
