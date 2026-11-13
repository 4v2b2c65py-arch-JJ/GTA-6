# Rockstar Launcher — Environment Status & Integration

## Host Environment (detected)
- **OS:** macOS (darwin)
- **Workspace:** `/Users/jjmarte/Desktop/spatial avy`
- **Steam:** `/Applications/Steam.app` detected
- **CrossOver/Wine:** not detected (`crossover` not in PATH; no CrossOver/Bottles/Whisky apps found in `/Applications` scan)
- **Rockstar Games Launcher (native macOS):** not installed (Windows-only application)

## Rockstar Games Launcher (official facts)
- **Supported OS:** Windows (official). **No native macOS or Linux client.**
- **Minimum (launcher, per Rockstar Support):** Windows 10 64-bit; Intel Core 2 Quad Q6600 / AMD Phenom 9850; 4 CPUs @ 2.4–2.5GHz; 2 GB RAM; DX11 supported GPU; 1 GB HDD space; internet required for sign-in/signup/activation.
- **Installed components (typical):** RGL, Rockstar Games Framework, Windows Universal CRT, Rockstar Games Authentication Software, CEF, MSVC 2015–2019 Redistributable (x86/x64), Steam Client API.
- **Account:** Rockstar Games (Social Club) account required (sign-in or sign-up), email verification, 2-step verification recommended.
- **Features:** library, install/download, updates, game start/launch, cloud saves (supported titles/digital), scan PC for installs, redeem code, store, settings/verify integrity, account linking (Steam/Epic/Xbox/PlayStation), overlay/chat (recent updates), offline launch args for supported titles (e.g. `-scofflineonly` for GTAV story, after activation).
- **Constraints:** one active signed-in session per account across PCs (per support docs); entitlements tied to purchase account.

## Steam / Epic / Related Installments
- **Steam:** Purchases/installs managed by Steam; RGL required for activation/sign-in/launch for most Rockstar titles (`Play on Steam` handoff). Steam detected locally (`Steam.app`).
- **Epic Games Store:** Similar handoff (`Play on Epic`), link Epic ↔ Rockstar account; EGS not detected locally.
- **Xbox app (PC):** Can install/launch via Xbox app with RGL link (Windows context). Not present on macOS.
- **Rockstar Store/RGL direct:** Purchase/redeem/install directly in launcher.

## macOS Integration Path
1. **Native:** Not supported for RGL binary.
2. **Compatibility layer (optional, user-installed):** CrossOver/Wine/Whisky/Parallels VM can run Windows apps on macOS (community-reported for RGL/Steam games); **CrossOver not currently installed** in this environment. If installed later, configure bottle + Steam/RGL per vendor/community guidance.
3. **In-workspace/game-world integration (implemented here):** Launcher/auth/library/install/game-start flows, Steam/Epic installment configs, environment state, and UI components are modeled under `systems/launchers/` and wired to runtime/devices for in-world use.

## Working State (this environment)
- **Modeled launcher:** `systems/launchers/rockstar/` (config, auth/login-signup, session, library/install/start, UI).
- **Integrations:** `systems/launchers/steam/`, `systems/launchers/epic/`, `systems/launchers/related/`, hub `systems/launchers/launcher_hub.json`.
- **Auth:** local/session auth model with login/signup flows and account state (workspace/game-world); external Rockstar account linking recorded as integration targets.
- **Game start:** launch pipeline and state machine (installed/ready → launching → running) with provider handoff awareness (RGL/Steam/Epic).
- **GTA 6:** cataloged as announced (console) / PC pending per research doc.