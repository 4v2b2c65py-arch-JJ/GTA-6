#!/usr/bin/env python3
"""Gap Bot: identify missing game assets by comparing inventory against normalized community spottings."""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INVENTORY = ROOT / "systems/gta_portal/inventory_snapshot.json"
SPOTTINGS = ROOT / "systems/gta_portal/fetcher/normalized_spottings.json"
OUT_JSON = ROOT / "systems/gta_portal/reports/gap_report.json"
OUT_MD = ROOT / "systems/gta_portal/reports/gap_report.md"

CATEGORIES = ["image", "video", "polygons", "items", "characters"]


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def norm_name(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def tokens(s: str):
    stop = {"a", "an", "the", "of", "for", "and", "with", "in", "on", "set", "kit", "map", "mesh", "prop"}
    return {t for t in norm_name(s).split() if t not in stop and len(t) > 2}


def is_present(spot, inv_items):
    sname = norm_name(spot["name"])
    stoks = tokens(spot["name"])
    for it in inv_items:
        iname = norm_name(it.get("name", ""))
        if not iname:
            continue
        if sname == iname or sname in iname or iname in sname:
            return True, it.get("id"), "name_match"
        itoks = tokens(it.get("name", ""))
        if stoks and itoks:
            overlap = stoks & itoks
            if len(overlap) >= 2 and len(overlap) / max(1, len(stoks)) >= 0.6:
                return True, it.get("id"), "token_overlap"
    return False, None, None


def main():
    inv = load_json(INVENTORY)
    spots_doc = load_json(SPOTTINGS)
    spottings = spots_doc.get("spottings", [])

    report_cat = {}
    missing_all = []
    present_all = []

    for cat in CATEGORIES:
        inv_items = inv.get(cat, []) or []
        cat_spots = [s for s in spottings if s.get("category") == cat]
        missing = []
        present = []
        for s in cat_spots:
            ok, matched_id, reason = is_present(s, inv_items)
            entry = {
                "spot_id": s["spot_id"],
                "name": s["name"],
                "category": cat,
                "confidence": s.get("confidence"),
                "refs": s.get("refs", []),
                "origin_source": s.get("origin_source"),
                "notes": s.get("notes", ""),
            }
            if "poly_budget" in s:
                entry["poly_budget"] = s["poly_budget"]
            if ok:
                entry["matched_inventory_id"] = matched_id
                entry["match_reason"] = reason
                present.append(entry)
                present_all.append(entry)
            else:
                entry["status"] = "missing"
                missing.append(entry)
                missing_all.append(entry)
        report_cat[cat] = {
            "inventory_count": len(inv_items),
            "spotted_count": len(cat_spots),
            "missing_count": len(missing),
            "present_count": len(present),
            "missing": missing,
            "present": present,
        }

    summary = {
        "total_spotted": len(spottings),
        "total_missing": len(missing_all),
        "total_matched": len(present_all),
        "by_category": {c: {"inventory": report_cat[c]["inventory_count"], "spotted": report_cat[c]["spotted_count"], "missing": report_cat[c]["missing_count"], "matched": report_cat[c]["present_count"]} for c in CATEGORIES},
    }

    report = {
        "id": "gta_portal_gap_report",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "referencer": "systems/gta_portal/referencer.json",
        "inputs": {
            "inventory": str(INVENTORY.relative_to(ROOT)),
            "normalized_spottings": str(SPOTTINGS.relative_to(ROOT)),
        },
        "source_summary": spots_doc.get("sources", []),
        "summary": summary,
        "categories": report_cat,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # markdown report
    lines = []
    lines.append("# GTA Portal Gap Report")
    lines.append("")
    lines.append(f"- Generated: {report['generated_at']}")
    lines.append(f"- Spottings: {summary['total_spotted']} | Missing: **{summary['total_missing']}** | Matched: {summary['total_matched']}")
    lines.append("")
    lines.append("## Summary by Category")
    lines.append("| Category | Inventory | Spotted | Missing | Matched |")
    lines.append("|---|---:|---:|---:|---:|")
    for c in CATEGORIES:
        b = summary["by_category"][c]
        lines.append(f"| {c} | {b['inventory']} | {b['spotted']} | {b['missing']} | {b['matched']} |")
    lines.append("")
    for c in CATEGORIES:
        cat = report_cat[c]
        lines.append(f"## Missing — {c} ({cat['missing_count']})")
        if not cat["missing"]:
            lines.append("_None_")
        else:
            for m in cat["missing"]:
                extra = f" (poly_budget: {m['poly_budget']})" if "poly_budget" in m else ""
                conf = f", conf {m['confidence']}" if m.get("confidence") is not None else ""
                lines.append(f"- `{m['spot_id']}` **{m['name']}**{extra}{conf} — {m.get('notes','')}")
        lines.append("")
    with OUT_MD.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Missing total: {summary['total_missing']} / Spotted: {summary['total_spotted']}")
    for c in CATEGORIES:
        b = summary["by_category"][c]
        print(f" - {c}: missing {b['missing']} (spotted {b['spotted']}, inv {b['inventory']})")


if __name__ == "__main__":
    main()
