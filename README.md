# Spatial Avy — Home World

Structured workspace aligned to the home-world model: terrain, mind, soul, border systems, and narrative.

## Live Deployment

- **Production (aliased):** https://gta-6-spatial-avy.vercel.app
- **GTA 6 Pageout:** https://gta-6-spatial-avy.vercel.app/gta6/
- **Deployment (requested):** https://gta-6-spatial-ax0p85zpk-jjonthelaptop-5497s-projects.vercel.app
- **Vercel Portal:** https://vercel.com/jjonthelaptop-5497s-projects/gta-6-spatial-avy
- **GitHub:** https://github.com/4v2b2c65py-arch-JJ/GTA-6

## Structure

- `home_world/` — core world domains
  - `bodium_terrain/` — Bodium terrain constructs, materials, and spatial maps
  - `mind_core/` — mind-aspect logic, indexes, and cognitive overlays
  - `soul_sanctum/` — soul-aspect values, vows, and continuity anchors
  - `border_protocols/` — SATS/REA-REM and boundary/host-port protocols
  - `gates_nodes/` — door/node paths and mnemonic gate strings
- `systems/` — technical/runtime systems
  - `vcp/` — Video Context Protocol interfaces and artifacts
  - `grid_store/` — CPU video grid, qbit zone/pocket storage, proximity/hash bracing, timeline pockets
  - `stream_pipeline/` — stream profiling, MCP/layout directives, React/Electron grid bindings
  - `devices/` — device libraries, spec graph accounting, model-to-spec transfer, compute webpointers
  - `fpv/` — in-game FPV insertions and runtime activation configs
  - `camera/` — camera/viewpoint configs and depth-based render partitioning
  - `runtime/` — in-world runtime (VS Code UI port, Kilo Code, Python, physics/algorithms, world timeline model rule)
  - `local_ai/` — local model runtime and ported model weights
  - `world_items/` — usable in-game items (computers, intelligent devices, laptops, phones, tablets, wearables)
  - `network/` — satcom, webpointers, portals, dimension/weblink allocations
  - `autonomy/` — tracer, developer bot team cycles/reports
  - `gta_portal/` — portal referencer, fetcher, gap bot/reports
  - `launchers/` — Rockstar launcher (login/signup/library/install/start), map loader/region expansion, Steam/Epic/related installments, hub/UI/state
- `narrative/` — story development
  - `manuscript/chapters/` — chapter drafts
  - `outline/` — plot structure and beat maps
  - `drafts/` — scene/entry drafts
  - `characters/` — character profiles and arcs
  - `worldbuilding/` — setting and lore
  - `research/` — references and notes
  - `notes/` — scratch ideas
- `assets/` — media
  - `avatars/` — character avatars and portraits
- `docs/` — specifications and requirements
- `exports/` — compiled/exported outputs
- `.venv/` — Python virtual environment (local)

## Key Documents
- `docs/GAME_REQUIREMENTS.md` — VCP, grid/store, stream pipeline, and build requirements
- `docs/LOCAL_AI.md` — local model runtime connection (Ollama) and usage
- `docs/launchers/ROCKSTAR_LAUNCHER_ENVIRONMENT.md` — host environment status and Rockstar launcher integration notes
- `systems/launchers/rockstar/map_loader/map_loader.json` — map loader with region expansion and real-world location modeling pipeline
- `systems/launchers/rockstar/map_loader/region_expansion.json` — broader mapping scope region sets (Leonida/US/global seeds)
- `systems/launchers/rockstar/map_loader/sources/camera_sources.json` — external camera/API source registry (Flock authorized, traffic, street imagery, CCTV, mapping APIs) with compliance/redaction controls
- `systems/launchers/rockstar/map_loader/barcode_hashes/regional_barcode_hashes.json` — regional barcode hashes (sha256) downloaded/passed around satcom network
- `systems/launchers/rockstar/map_loader/barcode_hashes/network_pass_log.json` — network distribution/pass log for barcode hashes
- `systems/launchers/rockstar/map_loader/data_flow/data_flow_state.json` — installed map data flow state per region
- `systems/launchers/rockstar/map_loader/data_flow/information_gap_report.json` — accounted information gaps and fill strategies
- `assets/game_assets/map_loader/barcode_hashes/` — hash-identical copies of regional barcode hashes and network pass log (game resources)
- `assets/game_assets/map_loader/data_flow/` — hash-identical copies of data flow state and gap report (game resources)
- `assets/game_assets/map_loader/entries/file_entries.json` — game resource file entries with sha256 verification and per-region hash index
- `docs/research/GTA6_REQUIREMENTS_AND_DETAILS.md` — GTA 6 researched release/platform/pricing/preload/storage details (PC specs not officially published)
- `systems/local_ai/connection.json` — local AI endpoint/model config
- `systems/local_ai/model_weights_port.json` — ported model weights/runtime binding for in-game use
- `systems/runtime/game_world_runtime.json` — unified in-world runtime (model, VS Code UI, Kilo Code, Python, physics/algorithms)
- `systems/runtime/vscode_world_interface.json` — VS Code UI interface port config
- `assets/ui/vscode/index.html` — in-world VS Code UI surface
- `systems/runtime/kilo_code.json` — full Kilo Code integration and automation config
- `systems/runtime/python_access.json` — Python runtime access for in-world execution
- `systems/runtime/physics_algorithms.json` — automated physics and algorithms runtime
- `systems/runtime/world_timeline_model_rule.json` — model rule for timeline routing, data/file label pockets, and base-tag rebrand/edit policy
- `systems/grid_store/timeline_pockets.json` — past/present/future timeline pockets with data/file labels and base-tag lineage
- `systems/world_items/compute_devices.json` — usable in-game compute items (computer, laptop, intelligent device, tablet, phone, wearable)
- `systems/devices/compute/compute_device_webpointers.json` — URIs/ports for in-world compute devices
- `home_world/home_world_index.json` — master index of world/system maps and mnemonic refs
- `systems/devices/device_library.json` — device library including inactive inventory
- `systems/devices/spec_graph.json` — spec graph transferred/accounted to device models
- `systems/fpv/game_fpv_devices.json` — inactive devices inserted and turned on in game FPVs
- `systems/network/sat_coms_forum_manager.json` — Sat Coms Forum Manager, device loaders/webpointers, and portal download ports
- `systems/devices/device_webpointers.json` — per-device loader webpointers (URI/port) and portal download mappings
- `systems/network/portals/vercel_portals.json` — installed Vercel portal registry and download staging status
- `systems/autonomy/tracer.py` — portal trace probes and `traces/trace.jsonl` + `trace_status.json`
- `systems/autonomy/bots/bot_runner.py` — developer bot team cycle runner (trace/fix/verify/distribute loop)
- `home_world/autonomy/developer_bot_team.json` — in-world dedicated developer bot team (civilization autonomy)
- `systems/autonomy/reports/bot_cycle_report.{json,md}` — latest autonomy cycle report
- `systems/camera/camera_viewpoints.json` — camera and terrain viewpoint definitions
- `home_world/bodium_terrain/render/map_partitions_by_depth.json` — map partitions rendered by pixel depth per camera
- `narrative/drafts/cinematic-entry-bodium.md` — beat-preserving cinematic entry (Bodium/mind/soul load-in)
- `narrative/outline/entry-beat-map.md` — beat integrity map and overlays
