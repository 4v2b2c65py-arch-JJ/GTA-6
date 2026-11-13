#!/usr/bin/env python3
"""Portal trace: probe target sites and record trace events/status for autonomy bots."""

import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parents[2]
PORTALS = ROOT / "systems/network/portals/vercel_portals.json"
TRACE_JSONL = ROOT / "systems/autonomy/traces/trace.jsonl"
STATUS_JSON = ROOT / "systems/autonomy/traces/trace_status.json"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def append_event(event):
    TRACE_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with TRACE_JSONL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, separators=(",", ":")) + "\n")


def probe_url(url, timeout=10):
    req = Request(url, headers={"User-Agent": "spatial-avy-tracer/1.0"})
    start = time.time()
    try:
        with urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", 200)
            body = resp.read(512)
            elapsed_ms = int((time.time() - start) * 1000)
            text = body.decode("utf-8", errors="ignore").lower()
            necessary = status == 200 and ("vercel" not in text or "login" not in text) and "log in" not in text
            return {
                "reachable": True,
                "http_status": status,
                "elapsed_ms": elapsed_ms,
                "necessary": necessary,
                "reason": "ok" if necessary else "response_not_ready_or_protected",
            }
    except HTTPError as e:
        elapsed_ms = int((time.time() - start) * 1000)
        # 401/403 often means SSO/auth gate
        return {
            "reachable": True,
            "http_status": e.code,
            "elapsed_ms": elapsed_ms,
            "necessary": False,
            "reason": f"http_error_{e.code}",
        }
    except (URLError, TimeoutError, OSError, ValueError) as e:
        elapsed_ms = int((time.time() - start) * 1000)
        return {
            "reachable": False,
            "http_status": None,
            "elapsed_ms": elapsed_ms,
            "necessary": False,
            "reason": f"unreachable:{e.__class__.__name__}",
        }


def main():
    portals_doc = load_json(PORTALS)
    trace_id = f"trace-{uuid.uuid4().hex[:8]}"
    ts = now()
    portal_results = []
    all_ready = True

    for p in portals_doc.get("portals", []):
        probe = probe_url(p["url"])
        ready = bool(probe.get("necessary"))
        all_ready = all_ready and ready
        result = {
            "portal_id": p.get("portal_id"),
            "name": p.get("name"),
            "url": p.get("url"),
            "access_state": p.get("access", {}).get("state"),
            "download_status": p.get("download", {}).get("status"),
            "probe": probe,
            "ready": ready,
        }
        portal_results.append(result)
        append_event({
            "ts": ts,
            "trace_id": trace_id,
            "event": "portal_probe",
            "portal_id": result["portal_id"],
            "url": result["url"],
            "http_status": probe.get("http_status"),
            "reachable": probe.get("reachable"),
            "necessary": probe.get("necessary"),
            "reason": probe.get("reason"),
            "elapsed_ms": probe.get("elapsed_ms"),
        })

    status = {
        "id": "portal_trace_status",
        "trace_id": trace_id,
        "generated_at": ts,
        "source": str(PORTALS.relative_to(ROOT)),
        "portals": portal_results,
        "summary": {
            "total": len(portal_results),
            "ready": sum(1 for r in portal_results if r["ready"]),
            "pending": sum(1 for r in portal_results if not r["ready"]),
            "all_ready": all_ready,
            "next_action": "distribute_downloads" if all_ready else "retry_and_fix_until_ready",
        },
    }
    STATUS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with STATUS_JSON.open("w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)

    append_event({
        "ts": ts,
        "trace_id": trace_id,
        "event": "trace_summary",
        "total": status["summary"]["total"],
        "ready": status["summary"]["ready"],
        "pending": status["summary"]["pending"],
        "all_ready": all_ready,
    })

    print(f"Wrote {STATUS_JSON}")
    print(f"Appended trace events to {TRACE_JSONL} (trace_id={trace_id})")
    for r in portal_results:
        print(f" - {r['portal_id']}: status={r['probe'].get('http_status')} necessary={r['probe'].get('necessary')} reason={r['probe'].get('reason')}")


if __name__ == "__main__":
    main()
