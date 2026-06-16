# My Role — Desktop App Developer (Tauri)

#role #desktop #tauri #phase1 #phase2

## Overview

I am responsible for the **Tauri desktop app** — the piece of software students install on their PC.

- Phase 1: Account linking + game session detection (runs silently in tray)
- Phase 2: Screen recording + video upload to Cloudflare R2

My friend handles the frontend (school dashboard + student portal in Next.js).
The AI/ML engineer (another friend) owns the video analysis pipeline that processes recordings I send.

---

## The Stack

| Technology | Purpose |
|---|---|
| Tauri | Desktop app framework (Rust + React) |
| Rust | System-level code — process detection, screen capture |
| React + TypeScript | UI inside the app |
| Windows Graphics Capture API | Screen recording (Phase 2) |
| Cloudflare R2 | Video upload destination (Phase 2) |

### Why Tauri over Electron
- ~5MB install vs ~200MB for Electron
- Much easier to get past school IT approval
- Lower memory usage (uses OS webview, not bundled Chromium)

---

## Phase 1 — What I Build

### Goal
A small desktop app that:
1. Lets students log in with their school account
2. Links their Riot / Steam / FACEIT accounts
3. Detects when they open Valorant, LoL, or CS2
4. Notifies the backend when a game session ends → triggers API pull

Screen recording is NOT in Phase 1.

---

### Setup

```bash
# Install Rust
# https://rustup.rs

# Verify
rustc --version
cargo --version

# Install Tauri CLI
cargo install tauri-cli

# Scaffold the app
npm create tauri-app@latest edutainment-desktop
cd edutainment-desktop
# Choose: React + TypeScript

# Run dev
npm run tauri dev
```

### Project Structure

```
edutainment-desktop/
├── src/                   ← React UI
│   ├── App.tsx
│   └── main.tsx
├── src-tauri/             ← Rust backend
│   ├── src/
│   │   └── main.rs
│   ├── Cargo.toml
│   └── tauri.conf.json
└── package.json
```

---

### Screen 1 — Login

Student logs in with their school email.
Calls the backend API → returns JWT token → stored locally.

---

### Screen 2 — Link Accounts

```
[ Connect Riot Account ]    ← opens Riot OAuth in browser
[ Connect Steam Account ]   ← opens Steam login in browser
[ Connect FACEIT Account ]  ← optional
```

On success → store `riot_puuid` / `steam_id` via backend API call.

---

### Screen 3 — Home / Status

```
✅ Riot account linked   (RiotName#TAG)
✅ Steam account linked
⏳ Waiting for game session...
```

---

### Game Session Detection (Rust)

Poll every 60 seconds to check if a supported game is running:

```rust
use std::process::Command;

fn get_running_games() -> Vec<String> {
    let output = Command::new("tasklist").output().unwrap();
    let list = String::from_utf8_lossy(&output.stdout);

    let games = vec![
        ("VALORANT-Win64-Shipping.exe", "valorant"),
        ("League of Legends.exe", "lol"),
        ("cs2.exe", "cs2"),
    ];

    games.iter()
        .filter(|(process, _)| list.contains(process))
        .map(|(_, name)| name.to_string())
        .collect()
}
```

When a game process disappears → fire webhook to backend → backend pulls match history from Riot/Steam API for that student.

---

### System Tray

App runs silently in background. Students don't interact with it after setup.

```json
// tauri.conf.json
{
  "tauri": {
    "systemTray": {
      "iconPath": "icons/icon.png",
      "iconAsTemplate": true
    }
  }
}
```

---

### Phase 1 Checklist

- [ ] Tauri app scaffolded and runs
- [ ] Login screen → calls backend API
- [ ] Riot + Steam + FACEIT account linking UI
- [ ] Game process detection (Valorant, LoL, CS2)
- [ ] On game close → POST to backend webhook
- [ ] Runs silently in system tray
- [ ] Auto-start on Windows login (optional)

---

## Phase 2 — Screen Recording (Deep Behavior Mode)

> Not started until Phase 1 is validated and at least 1 pilot school is live.

### What gets added
- Screen recording using **Windows Graphics Capture API** via Rust
- Record the game window (not the whole screen — privacy)
- Upload as chunked `.mp4` to **Cloudflare R2** during/after session
- New UI: recording indicator, start/stop controls, privacy notice

### Who uses the recording
The **AI/ML engineer** (Person 4) owns the pipeline that processes the video:
- Frame sampling (30fps → 2fps)
- OpenCV gatekeeper (filters boring frames)
- LLaVA 7B local model (mid-tier analysis)
- Gemini 2.0 Flash (high-interest frames)
- Outputs behavior events → stored in `behavior_events` table

I just need to get clean `.mp4` files into R2. The AI pipeline handles the rest.

### Privacy rules
- Record only the game window, never the full desktop
- Show a visible recording indicator while active
- Raw video deleted from R2 after the AI pipeline processes it
- Student must give consent before recording starts (COPPA/FERPA)

---

## How My Work Connects to the Rest of the Platform

```
[Student PC]
    └── Tauri App (my work)
            ├── Account linking → Backend API stores riot_puuid / steam_id
            ├── Game detection  → Backend API pulls match history
            └── Screen recording (Phase 2) → Cloudflare R2
                                                └── AI Pipeline (friend's work)
                                                        └── behavior_events table
                                                                └── Profile Engine
                                                                        └── student_profiles
                                                                                └── School Dashboard (other friend's work)
```

---

## Interfaces I Share With Other People

### With Person 3 (Backend)
- `POST /api/session/game-detected` — I call this when a game starts
- `POST /api/session/game-ended` — I call this when a game closes
- `POST /api/accounts/link` — I call this when student links Riot/Steam
- `POST /api/upload/video-chunk` — Phase 2, chunked video upload

### With Person 4 (AI/ML)
- R2 bucket path format for uploaded videos
- Video naming convention: `{student_id}/{session_id}/{timestamp}.mp4`

---

## First 30 Days Plan

| Week | Goal |
|---|---|
| Week 1 | Tauri app running, basic React UI shell |
| Week 2 | Login screen + Riot OAuth flow working |
| Week 3 | Steam linking + game process detection |
| Week 4 | System tray, auto-start, connect to backend API |

---

## Resources

- Tauri docs: https://tauri.app/v1/guides/
- Tauri + React starter: `npm create tauri-app@latest`
- Windows Graphics Capture API (Phase 2): https://learn.microsoft.com/en-us/windows/uwp/audio-video-camera/screen-capture
- Riot OAuth docs: https://developer.riotgames.com
- Steam OpenID docs: https://steamcommunity.com/dev

---

## Related Docs

- [[architecture]] — full system overview
- [[tech-stack]] — why Tauri, full infrastructure
- [[video-pipeline]] — what happens to the recordings I upload
- [[team-structure]] — full team, who owns what
- [[database-schema]] — tables my app writes to (students, game_sessions)
