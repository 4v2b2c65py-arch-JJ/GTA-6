#!/usr/bin/env python3
"""Render map partition assignments by camera and pixel depth layers."""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CAM_CFG = ROOT / "systems/camera/camera_viewpoints.json"
TERRAIN = ROOT / "home_world/bodium_terrain/bodium_terrain_map.json"
SCENERY = ROOT / "home_world/bodium_terrain/scenery_compute.json"
OUT = ROOT / "home_world/bodium_terrain/render/map_partitions_by_depth.json"


def load(p):
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def dist(a, b):
    return math.sqrt((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2 + (a["z"] - b["z"]) ** 2)


def region_world_point(region, idx, total):
    # distribute regions along terrain depth (z) and center x; use elevation as y
    span = 80.0
    z = -span / 2 + (idx + 0.5) * (span / total)
    x = 0.0
    y = float(region.get("elevation", 0))
    return {"x": x, "y": y, "z": z}


def norm_depth(d, near, far):
    d = max(near, min(far, d))
    return (d - near) / (far - near) if far > near else 0.0


def pick_layer(nd, layers):
    for layer in layers:
        if layer["depth_min"] <= nd < layer["depth_max"] or (nd == 1.0 and layer["depth_max"] == 1.0):
            return layer
    return layers[-1]


def main():
    cam_cfg = load(CAM_CFG)
    terrain = load(TERRAIN)
    scenery = load(SCENERY)
    regions = terrain.get("regions", [])
    scen_by = {r["region_id"]: r for r in scenery.get("regions", [])}
    layers = cam_cfg["depth_partition"]["layers"]
    near = cam_cfg["depth_partition"]["near_plane"]
    far = cam_cfg["depth_partition"]["far_plane"]

    region_points = {}
    for i, r in enumerate(regions):
        region_points[r["id"]] = region_world_point(r, i, len(regions))

    cameras_out = []
    global_layer_regions = {l["layer_id"]: set() for l in layers}

    for cam in cam_cfg.get("cameras", []):
        if not cam.get("active", True):
            continue
        cpos = cam["position"]
        assignments = []
        per_layer = {l["layer_id"]: [] for l in layers}
        for r in regions:
            rid = r["id"]
            p = region_points[rid]
            d = dist(cpos, p)
            nd = norm_depth(d, near, far)
            layer = pick_layer(nd, layers)
            sidx = scen_by.get(rid, {}).get("computed_scenery", {}).get("indices", {})
            item = {
                "region_id": rid,
                "region_name": r.get("name"),
                "narrative_anchor": r.get("narrative_anchor"),
                "depth_m": round(d, 3),
                "depth_normalized": round(nd, 4),
                "partition_layer": layer["layer_id"],
                "layer_name": layer["name"],
                "priority": layer["priority"],
                "scenery_indices": sidx,
            }
            assignments.append(item)
            per_layer[layer["layer_id"]].append(rid)
            global_layer_regions[layer["layer_id"]].add(rid)

        assignments.sort(key=lambda x: (x["depth_normalized"], -x["priority"]))
        cameras_out.append({
            "camera_id": cam["camera_id"],
            "name": cam.get("name"),
            "category": cam.get("category", "visible"),
            "visibility": cam.get("visibility", cam.get("category", "visible")),
            "spawnable": cam.get("spawnable", False),
            "type": cam.get("type"),
            "mode": cam.get("mode"),
            "device_binding": cam.get("device_binding"),
            "focus_zone": cam.get("focus_zone"),
            "viewport": cam.get("viewport"),
            "clearance_profile": cam.get("clearance_profile"),
            "fidelity_tier": cam.get("fidelity_tier"),
            "region_count": len(assignments),
            "layers": [
                {"layer_id": lid, "region_ids": rids} for lid, rids in per_layer.items() if rids
            ],
            "assignments": assignments,
        })

    out = {
        "id": "map_partitions_by_depth",
        "type": "render_partition_map",
        "method": cam_cfg["depth_partition"]["method"],
        "space": cam_cfg["depth_partition"]["space"],
        "near_plane": near,
        "far_plane": far,
        "layers": layers,
        "summary": {
            "camera_count": len(cameras_out),
            "region_count": len(regions),
            "visible_cameras": sum(1 for c in cameras_out if c.get("category") == "visible"),
            "invisible_cameras": sum(1 for c in cameras_out if c.get("category") == "invisible"),
            "layer_region_index": {lid: sorted(list(rids)) for lid, rids in global_layer_regions.items()},
        },
        "ai_core": cam_cfg.get("ai_core", {}),
        "camera_categories": cam_cfg.get("camera_categories", {}),
        "cameras": cameras_out,
        "refs": cam_cfg.get("refs", {}),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {OUT}")
    for c in cameras_out:
        counts = {l["layer_id"]: len(l["region_ids"]) for l in c["layers"]}
        print(f"{c['camera_id']}: {counts}")


if __name__ == "__main__":
    main()
