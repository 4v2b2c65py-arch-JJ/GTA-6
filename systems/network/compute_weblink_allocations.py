#!/usr/bin/env python3
"""Compute and save weblink size allocations per session/player from depth sensor layer metrics."""

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
SENSOR = ROOT / "systems/camera/depth_sensor_layers.json"
ALLOC = ROOT / "systems/network/session_dimension_allocations.json"


def load(p):
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    sensor = load(SENSOR)
    alloc = load(ALLOC)
    metrics = {m["layer_id"]: m for m in sensor.get("layer_metrics", [])}
    model = sensor.get("weblink_budget_model", {})
    env = int(model.get("envelope_bytes", 0))
    bpu = int(model.get("bytes_per_dimension_unit", 0))
    cf = float(model.get("compression_factor_estimate", 1.0))

    for s in alloc.get("sessions", []):
        layers = s.get("assigned_depth_layers", [])
        units = int(s.get("assigned_spatial_dimension_units", 0))
        layers_bytes = sum(int(metrics[l]["base_payload_bytes"]) for l in layers if l in metrics)
        spatial_bytes = units * bpu
        raw = env + layers_bytes + spatial_bytes
        est = int(raw * cf)
        s["weblink_size"] = {
            "envelope_bytes": env,
            "layers_payload_bytes": layers_bytes,
            "spatial_payload_bytes": spatial_bytes,
            "raw_bytes": raw,
            "compression_factor_estimate": cf,
            "estimated_transfer_bytes": est,
            "saved": True,
        }
        s["assigned_layer_count"] = len(layers)
        s.setdefault("dimension_load", {})
        s["dimension_load"]["spatial_units"] = units
        s["dimension_load"]["depth_layers"] = len(layers)
        s["dimension_load"]["total_layer_dimensions"] = len(s.get("assigned_spatial_axes", [])) + len(layers)

    sessions = alloc.get("sessions", [])
    alloc["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    alloc["summary"] = {
        "total_sessions": len(sessions),
        "computing_players": sum(1 for s in sessions if s.get("session_type") == "computing_player"),
        "offline_sessions": sum(1 for s in sessions if s.get("session_type") == "offline_session"),
        "saved_weblink_profiles": sum(1 for s in sessions if s.get("weblink_size", {}).get("saved")),
    }

    with ALLOC.open("w", encoding="utf-8") as f:
        json.dump(alloc, f, indent=2)
    print(f"Updated {ALLOC}")
    for s in sessions:
        print(f"{s['session_id']} ({s['session_type']}): layers={s['assigned_layer_count']} units={s['assigned_spatial_dimension_units']} raw={s['weblink_size']['raw_bytes']} est={s['weblink_size']['estimated_transfer_bytes']}")


if __name__ == "__main__":
    main()
