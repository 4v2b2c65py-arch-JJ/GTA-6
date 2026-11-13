#!/usr/bin/env python3
"""Developer bot team runner: act on trace status and portal state until necessary resources are ready."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PORTALS = ROOT / "systems/network/portals/vercel_portals.json"
TRACE_STATUS = ROOT / "systems/autonomy/traces/trace_status.json"
TEAM = ROOT / "home_world/autonomy/developer_bot_team.json"
REPORT_JSON = ROOT / "systems/autonomy/reports/bot_cycle_report.json"
REPORT_MD = ROOT / "systems/autonomy/reports/bot_cycle_report.md"
TRACE_JSONL = ROOT / "systems/autonomy/traces/trace.jsonl"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path):
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def append_event(event):
    TRACE_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with TRACE_JSONL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, separators=(",", ":")) + "\n")


def main():
    ts = now()
    cycle_id = f"cycle-{uuid.uuid4().hex[:8]}"
    portals = load_json(PORTALS) or {"portals": []}
    trace = load_json(TRACE_STATUS) or {"portals": [], "summary": {}}
    team = load_json(TEAM) or {"bots": []}

    trace_by_id = {p.get("portal_id"): p for p in trace.get("portals", [])}
    actions = []

    for p in portals.get("portals", []):
        pid = p.get("portal_id")
        t = trace_by_id.get(pid, {})
        probe = t.get("probe", {})
        necessary = bool(t.get("ready") or probe.get("necessary"))

        if necessary:
            p.setdefault("access", {})["state"] = "ready"
            p.setdefault("download", {})["status"] = "ready_to_distribute"
            actions.append({
                "bot_id": "bot-portal-fixer",
                "action": "mark_ready_and_distribute",
                "portal_id": pid,
                "result": "ready",
                "detail": "Site returned necessary response; staged for distribution."
            })
        else:
            # Attempt fix steps (config/state-level fixes possible here; external auth required for Vercel SSO)
            p.setdefault("download", {})["status"] = "pending_auth_retry_scheduled"
            p.setdefault("access", {})["last_probe"] = {
                "ts": ts,
                "http_status": probe.get("http_status"),
                "reason": probe.get("reason"),
            }
            fix_detail = "Retry scheduled; awaiting necessary site response (Vercel SSO/auth or public artifact required)."
            actions.append({
                "bot_id": "bot-trace-sentinel",
                "action": "trace_and_diagnose",
                "portal_id": pid,
                "result": "pending",
                "detail": f"Probe status={probe.get('http_status')} reason={probe.get('reason')}"
            })
            actions.append({
                "bot_id": "bot-portal-fixer",
                "action": "attempt_fix_and_retry",
                "portal_id": pid,
                "result": "pending",
                "detail": fix_detail
            })
            actions.append({
                "bot_id": "bot-device-loader",
                "action": "hold_ported_downloads",
                "portal_id": pid,
                "result": "pending",
                "detail": "Webpointer/port mappings retained; distribution deferred until artifact ready."
            })

        append_event({
            "ts": ts,
            "trace_id": trace.get("trace_id"),
            "cycle_id": cycle_id,
            "event": "bot_cycle_portal",
            "portal_id": pid,
            "necessary": necessary,
            "http_status": probe.get("http_status"),
            "action_result": "ready" if necessary else "pending",
        })

    total = len(portals.get("portals", []))
    ready_count = sum(1 for p in portals.get("portals", []) if p.get("download", {}).get("status") == "ready_to_distribute")
    pending_count = total - ready_count
    all_ready = total > 0 and ready_count == total

    portals["summary"] = portals.get("summary", {})
    portals["summary"].update({
        "portals_installed": total,
        "downloads_staged": ready_count,
        "downloads_pending_auth": pending_count,
        "downloads_ready": ready_count,
        "target_devices": portals["summary"].get("target_devices", 4),
        "last_cycle_id": cycle_id,
        "last_cycle_at": ts,
        "autonomy_mode": "civilization_autonomy",
        "run_until": "all_targets_ready_and_necessary",
        "all_ready": all_ready,
    })
    save_json(PORTALS, portals)

    # update team state
    team["status"] = "active"
    team["autonomy"]["current_cycle"] = cycle_id
    team["autonomy"]["last_run_at"] = ts
    team["autonomy"]["all_targets_ready"] = all_ready
    team["autonomy"]["next_state"] = "distribute_and_monitor" if all_ready else "continue_fix_loop"
    save_json(TEAM, team)

    report = {
        "id": "bot_cycle_report",
        "cycle_id": cycle_id,
        "generated_at": ts,
        "trace_id": trace.get("trace_id"),
        "team_ref": str(TEAM.relative_to(ROOT)),
        "portal_registry": str(PORTALS.relative_to(ROOT)),
        "summary": {
            "total_portals": total,
            "ready": ready_count,
            "pending": pending_count,
            "all_ready": all_ready,
            "autonomy": "civilization_autonomy",
            "next_state": team["autonomy"]["next_state"],
        },
        "actions": actions,
        "bots_active": [b.get("bot_id") for b in team.get("bots", []) if b.get("state") == "active"],
    }
    save_json(REPORT_JSON, report)

    lines = [
        "# Developer Bot Cycle Report",
        "",
        f"- Cycle: `{cycle_id}`",
        f"- Trace: `{trace.get('trace_id')}`",
        f"- Generated: {ts}",
        f"- Autonomy: civilization_autonomy (active)",
        f"- Portals ready: {ready_count}/{total} | Pending: {pending_count} | All ready: {all_ready}",
        f"- Next state: **{team['autonomy']['next_state']}**",
        "",
        "## Active Bots",
    ]
    for b in team.get("bots", []):
        lines.append(f"- `{b.get('bot_id')}` ({b.get('role')}): {b.get('state')}")
    lines.append("")
    lines.append("## Actions")
    for a in actions:
        lines.append(f"- `{a['bot_id']}` [{a['portal_id']}] {a['action']} → **{a['result']}** — {a['detail']}")
    lines.append("")
    lines.append("## Loop Condition")
    lines.append("- Run until: all targets ready and sites return necessary resources.")
    lines.append("- Current: continue trace/fix/verify cycle while pending targets remain; distribute when ready.")
    with REPORT_MD.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    append_event({
        "ts": ts,
        "trace_id": trace.get("trace_id"),
        "cycle_id": cycle_id,
        "event": "bot_cycle_summary",
        "ready": ready_count,
        "pending": pending_count,
        "all_ready": all_ready,
        "next_state": team["autonomy"]["next_state"],
    })

    print(f"Wrote {REPORT_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Cycle {cycle_id}: ready={ready_count} pending={pending_count} all_ready={all_ready} next={team['autonomy']['next_state']}")


if __name__ == "__main__":
    main()
