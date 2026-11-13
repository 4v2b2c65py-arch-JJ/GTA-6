# Browser Game Requirements (itch.io)

## Goal
Build a browser-playable game session, export it for the web, and publish it on itch.io.

## Core Components
1. **Runtime/Session**
   - Web-based game session running over HTTP (dev server locally; static hosting for release).
   - Main loop with deterministic update order: input/update → simulation/collisions → render.
   - Session states: boot/load, ready/start, playing, paused (optional), game over/end.

2. **Scene & Rendering**
   - 3D/2D scene with camera and render target (e.g. `<canvas>` / engine renderer).
   - **Directional light** configured for primary scene lighting/shaping (position/direction, intensity/color), plus ambient/fill as needed.
   - Ground/play area and visible bounds.
   - Resize handling to maintain aspect/viewport correctness.

3. **Player**
   - Controllable player entity spawned in scene.
   - Input mapping (keyboard/mouse/touch as applicable) using held-key/state polling per frame.
   - Movement with bounds/collision constraints and basic feedback (animation/rotation/state) as applicable.

4. **UI/Feedback**
   - HUD/session indicators (score/time/state) as required by game design.
   - Start/input prompt (required for browser audio/input focus behavior).

5. **Build & Deployment (itch.io)**
   - Web export/build producing static assets with `index.html` at bundle root.
   - Local verification served over HTTP (not `file://`).
   - itch.io project configured as **HTML**, upload zip with root-level `index.html`, enable “played in the browser”, set embed/viewport size, test in Draft then publish.

## VCP (Video Context Protocol) — Required
Provide a VCP layer (MCP-like, but for video) that exposes game/session visuals as structured, tool-accessible context for review and automation.

1. **Capture Sources**
   - Game canvas/WebGL surface and/or in-scene camera feed.
   - Modes: live stream, session recording, and periodic frame/screenshot capture.
   - Emit metadata per frame/segment: session ID, timestamps, frame index/time, resolution, source, and game state/context tags as available.

2. **VCP Interface (Video Channel)**
   - Standardized interface for consumers/agents to discover and access video context (analogous to MCP resources/tools, but video-focused).
   - Capabilities: list sessions/sources, start/stop capture, get live stream endpoint or chunks, fetch frames/snapshots, fetch recordings/segments, and query by time range/session.
   - Return machine-readable descriptors (format, codec/container, FPS, resolution, duration, status) alongside media/artifacts.

3. **CPU Video Grid / Spectrum-LiDAR Layer (Dedicated)**
   - Stream captured session video to the CPU through a dedicated **video grid layer** for processing/analysis (spectrum/LiDAR-like spatial-temporal representation of the frame).
   - Represent frames as an addressable grid (cells/tiles/voxels or depth-spectrum samples as applicable) with per-cell data (e.g. color/luma, depth/proximity, motion/intensity, timestamps, and source/camera metadata).
   - **Qbit Zone Grid Store Pocket:** partition the grid into addressable zones and store localized samples in pockets/buffers (qbit-indexed cells/regions) for fast CPU access, caching, and retrieval; each pocket carries spatial-temporal indices, zone IDs, and metadata for lookup/streaming.
   - **Mnemonic Lacing (String Indexing):** arrange string mnemonics laced across the grid to encode/address pockets and zones for deterministic lookup and streaming.
     - Pattern: interleave zone, pocket, cell, and time tokens into a lace key (e.g. `Z<zone>-Q<pocket>-C<cell>-T<tick>` or equivalent mnemonic strands).
     - Strands: lace spatial and temporal mnemonic strings (row/column/depth/spectrum ↔ frame/segment) so adjacent pockets share traversable key prefixes/suffixes.
     - **Door node string:** `N10-N9-N8-N7-N6-N5-N4-N3-N2-N1-N0` (laced node sequence for door/path addressing).
     - Use laced mnemonics for zone queries, cache keys, segment stitching, and VCP artifact references.
   - **Proximity Hash Bracing:** brace/cluster zones and pockets by spatial-temporal proximity hashes to bound neighborhoods for fast traversal, lookup, and cache locality.
     - **Analog Trigger Word (Python Memory):** resolve analog/nearest trigger words from a Python-side memory/index to map semantic or signal cues onto braced zones/pockets and laced mnemonic keys.
     - **TypeScript Log / Hash-Sword Puzzle (Fast Decoding):** a TypeScript-side log holds hash/has-hash state as a “hash-sword” puzzle (keyed challenge/chain over proximity braces and laced mnemonics) enabling fast decode, verification, and directed access to stored pockets/artifacts.
     - Correlate Python-resolved triggers, proximity braces, and TypeScript hash/log state in VCP metadata for deterministic cross-runtime addressing.
   - Provide configurable grid resolution, zone/pocket sizing, sampling rate, and region-of-interest to balance fidelity and CPU/performance cost.
   - Expose grid/stream and pocket-store outputs to VCP consumers (live feed, buffered segments, snapshots, zone queries) for tooling, inspection, and downstream analysis.

4. **Embedded Video Player / Playback**
   - In-app/dev UI player connected to VCP sources for playback of live or recorded session media.
   - Controls: play/pause/seek (recordings), source/session selection, live indicator, and connection/capture status.

5. **Transmission & Assistant Review Access**
   - Transmit/export VCP-addressable artifacts to reviewable locations (saved recording files, clips, frame bundles, grid snapshots/segments, or hosted/stream URLs).
   - **Constraint:** direct live VCP/video connection to the assistant is not available in this environment. Assistant review is performed via provided artifacts or accessible URLs/data produced by VCP.
   - Include review context with artifacts: what to inspect, timestamps/time ranges, reproduction steps, and relevant session metadata.

6. **Privacy & Performance**
   - User-controlled start/stop for capture/streaming/transmission; clear active-capture indicator.
   - Configurable resolution/frame rate/bitrate/duration, grid density/sampling, and buffering to limit gameplay and CPU impact.

## Stream Source Profiling & Layout Directive Pipeline (VCP/MCP → React/Electron)

### 1. Stream Source Profiling
Profile and normalize all ingest/playback sources so layout, routing, and review operate on consistent descriptors.
- **Source attributes:** type (canvas/WebGL capture, file/recording, live stream, HLS/DASH/HTTP, addon/source endpoint), URI/resource ref, session/source IDs, codec/container, resolution/FPS/bitrate, latency/buffer/health, and origin/provider tags.
- **Probe/telemetry:** capture start/stop, frame timing, drops, reconnects, and quality changes; attach timestamps and VCP session metadata.
- **Outputs:** machine-readable stream profiles and status events exposed to VCP consumers and layout directives.

### 2. SDK & Research Inputs (Stremio-informed layout/grid model)
Ground the UI/layout model in Stremio addon protocol and community patterns (research references, not hard dependencies).
- **Stremio addon SDK/protocol:** addons expose HTTP resources — `manifest`, `catalog` (meta previews for Board/Discover/Search, pagination/filter `extra` like `search`/`skip`), `meta` (detail), `stream` (playable sources), `subtitles`; resources routed as `/{resource}/{type}/{id}.json`.
- **Layout behavior (stremio-web):** Board/home as catalog rows/grids (`MetaRow`/`MetaItem`), continue-watching + addon catalogs, lazy/visible-range loading, responsive grid breakpoints, and detail/stream selection flows.
- **Community/research sources:** r/StremioAddons (Reddit), Stremio Addon SDK/docs/guide, stremio/stremio-web and DeepWiki architecture notes, awesome-stremio, stremio-addons-list, and addon ecosystem/forum discussions for stream/layout conventions.

### 3. Layout Directives (Model Weights → MCP → React/Electron Grids)
Define a directive layer that maps profiled streams and VCP data into renderable grids.
- **Directive generation:** a model (inference over its weights) produces structured layout directives/schemas from session/stream context (e.g. grid composition, zones/tiles, source bindings, priority, focus, and playback controls).
- **MCP transport:** directives and UI/data resources are served via MCP tools/resources (e.g. structured JSON schemas and/or `ui://` resources per MCP Apps patterns) so clients can discover, fetch, and subscribe to updates.
- **Client rendering:** React/Electron app consumes MCP-delivered directives and renders responsive grids/panels (board rows, stream tiles, player/preview cells) bound to VCP stream profiles, video player, and CPU video-grid/pocket outputs.
- **Bindings:** directives reference sources by stream/session/zone/pocket IDs and laced mnemonic keys (`Z<zone>-Q<pocket>-C<cell>-T<tick>`, door `N10-N9-N8-N7-N6-N5-N4-N3-N2-N1-N0`) for deterministic placement and lookup.

### 4. Formalized Visual & Data Flow
1. **Capture:** game/canvas/camera feeds enter VCP; CPU video-grid/spectrum-LiDAR layer samples into qbit zone grid store pockets with laced mnemonic keys.
2. **Profile:** sources/probes emit stream profiles + telemetry (quality, health, timestamps, metadata).
3. **Direct:** model processes profiles/context (weights) → emits layout directives (grid/zone/source bindings).
4. **Serve:** MCP exposes directives, profiles, and VCP resources/endpoints to authorized clients.
5. **Render:** React/Electron grids resolve bindings → display players/tiles/previews and status; user interactions emit control events (select/play/inspect/ROI).
6. **Review/export:** VCP exports addressable artifacts (recordings, frames, grid/pocket snapshots, segments, URLs) with directive/layout + session context for assistant review.

## Acceptance Criteria
- Game session runs in browser with visible directional lighting and a controllable player.
- Web build exports and runs from itch.io in-browser embed with `index.html` at zip root.
- VCP exposes session video context (sources, controls, playback, CPU video-grid/spectrum layer outputs, qbit zone/pocket store with mnemonic lacing, and exportable artifacts) with metadata; visuals are reviewable via provided artifacts/URLs (no direct live assistant feed in this environment).
- Stream sources are profiled and MCP-delivered layout directives can drive React/Electron grid rendering bound to VCP/video-grid data with formalized capture→profile→direct→serve→render→review flow.
