#!/usr/bin/env python3
"""
Inject vehicles, transportation, and geo data into game assets and the built
web executable (client+player) package data.
"""
import json
import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VEH = ROOT / "systems/world/transportation/vehicles.json"
TRANS = ROOT / "systems/world/transportation/transportation.json"
GEO = ROOT / "systems/world/geo/geo_injection.json"
ASSETS_T = ROOT / "assets/game_assets/transportation"
ASSETS_G = ROOT / "assets/game_assets/geo"
INJECT_OUT = ROOT / "build/web/data/injection"
SYS_STATE = ROOT / "systems/world/transportation/injection_state.json"
LOG = ROOT / "logs/build/inject_transport_geo.log"

def now(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def load(p):
    with open(p,"r",encoding="utf-8") as f: return json.load(f)
def save(p,d):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p,"w",encoding="utf-8") as f: json.dump(d,f,indent=2,ensure_ascii=False)
def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line=f"[{now()}] {msg}\n"
    with open(LOG,"a",encoding="utf-8") as f: f.write(line)
    print(line.strip())

def main():
    veh=load(VEH); trans=load(TRANS); geo=load(GEO)
    # asset copies
    save(ASSETS_T/"vehicles.json", veh)
    save(ASSETS_T/"transportation.json", trans)
    save(ASSETS_G/"geo_injection.json", geo)
    # merged game-data index
    vlist=veh.get("vehicles",[])
    regions=geo.get("regions",[])
    hubs=geo.get("transport_hubs",[])
    routes=geo.get("routes",[])
    game_data={
        "id":"transport_geo_game_data","type":"game_data","generated_at":now(),
        "vehicles":vlist,"transportation":trans,"geo":geo,
        "summary":{"vehicles":len(vlist),"modes":len(trans.get("modes",[])),
                   "regions":len(regions),"hubs":len(hubs),"routes":len(routes)}
    }
    save(ASSETS_T/"transport_geo_game_data.json", game_data)

    payload={
        "id":"transport_geo_injection","type":"injection_payload","status":"injected",
        "injected_at":now(),"target":"build/web (executable web client & player)",
        "refs":{"vehicles":str(VEH.relative_to(ROOT)),"transportation":str(TRANS.relative_to(ROOT)),
                "geo":str(GEO.relative_to(ROOT)),
                "game_data":"assets/game_assets/transportation/transport_geo_game_data.json"},
        "summary":game_data["summary"],
        "hash":hashlib.sha256(json.dumps(game_data["summary"],sort_keys=True).encode()).hexdigest()[:16]
    }
    save(INJECT_OUT/"transport_geo_injection.json", payload)
    # also place in web assets/data for client
    save(ROOT/"build/web/assets/transport_geo_injection.json", payload)
    state={"id":"transport_geo_injection_state","status":"injected","injected_at":now(),
           "assets":{"vehicles":"assets/game_assets/transportation/vehicles.json",
                     "transportation":"assets/game_assets/transportation/transportation.json",
                     "geo":"assets/game_assets/geo/geo_injection.json",
                     "game_data":"assets/game_assets/transportation/transport_geo_game_data.json"},
           "web_injection":"build/web/data/injection/transport_geo_injection.json",
           "summary":game_data["summary"]}
    save(SYS_STATE,state)
    log(f"injected vehicles={len(vlist)} modes={len(trans.get('modes',[]))} regions={len(regions)} hubs={len(hubs)} routes={len(routes)}")
    print(json.dumps(state,indent=2))

if __name__=="__main__": main()
