#!/usr/bin/env python3
"""Fetcher: ingest GTA/community portal spottings from configured sources and normalize."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parents[3]
CONFIG = ROOT / "systems/gta_portal/fetcher/sources.json"
OUT = ROOT / "systems/gta_portal/fetcher/normalized_spottings.json"

CATEGORIES = {"image", "video", "polygons", "items", "characters"}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def fetch_http_json(url: str):
    req = Request(url, headers={"User-Agent": "spatial-avy-gta-fetcher/1.0"})
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_spottings(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("spottings", "items", "data", "results"):
            if key in payload and isinstance(payload[key], list):
                return payload[key]
    return []


def normalize_item(raw, source_id):
    if not isinstance(raw, dict):
        return None
    spot_id = raw.get("spot_id") or raw.get("id")
    category = (raw.get("category") or raw.get("type") or "").lower().strip()
    name = raw.get("name") or raw.get("title") or raw.get("label")
    if not spot_id or not name or category not in CATEGORIES:
        return None
    item = {
        "spot_id": str(spot_id),
        "category": category,
        "name": str(name),
        "refs": raw.get("refs") or raw.get("references") or [],
        "confidence": raw.get("confidence"),
        "reporter": raw.get("reporter") or raw.get("source") or source_id,
        "notes": raw.get("notes") or raw.get("description") or "",
        "origin_source": source_id,
    }
    for k in ("poly_budget", "lods", "url", "thumbnail", "tags"):
        if k in raw:
            item[k] = raw[k]
    return item


def main():
    cfg = load_json(CONFIG)
    results = []
    source_reports = []
    seen = set()

    for src in cfg.get("sources", []):
        sid = src.get("source_id", "unknown")
        if not src.get("enabled", False):
            source_reports.append({"source_id": sid, "status": "skipped", "reason": "disabled"})
            continue
        kind = src.get("kind")
        try:
            if kind == "local_json":
                path = (ROOT / src["path"]).resolve()
                payload = load_json(path)
                status = "ok"
            elif kind == "http_json":
                payload = fetch_http_json(src["url"])
                status = "ok"
            else:
                source_reports.append({"source_id": sid, "status": "skipped", "reason": f"unsupported kind {kind}"})
                continue

            raw_items = extract_spottings(payload)
            count = 0
            for raw in raw_items:
                norm = normalize_item(raw, sid)
                if not norm:
                    continue
                key = (norm["category"], norm["spot_id"])
                if key in seen:
                    continue
                seen.add(key)
                results.append(norm)
                count += 1
            source_reports.append({"source_id": sid, "status": status, "kind": kind, "ingested": count, "raw_seen": len(raw_items)})
        except (URLError, HTTPError, TimeoutError, OSError, ValueError, KeyError) as e:
            source_reports.append({"source_id": sid, "status": "error", "kind": kind, "error": str(e)})

    out = {
        "id": "normalized_spottings",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "categories": sorted(CATEGORIES),
        "totals": {
            "all": len(results),
            **{c: sum(1 for r in results if r["category"] == c) for c in sorted(CATEGORIES)},
        },
        "sources": source_reports,
        "spottings": results,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {OUT} (normalized: {len(results)})")
    for s in source_reports:
        print(f" - {s['source_id']}: {s['status']} ({s.get('ingested', s.get('reason', s.get('error','')) )})")


if __name__ == "__main__":
    main()
