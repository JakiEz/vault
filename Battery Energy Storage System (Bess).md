# Battery Energy Storage System (BESS) Monitoring Platform

A production-grade, full-stack monitoring platform for a battery energy storage system: an embedded edge node reads battery telemetry and feeds a hardened backend with live dashboards, alerting, and analytics.

> **Why this project:** It sits at the intersection of embedded systems (your differentiator) and backend/full-stack development (your career target). Industry rarely needs _just_ firmware or _just_ a backend — it needs someone who can carry a signal from a sensor all the way to a decision on a screen. This is a scaled-down version of a real commercial storage-monitoring stack.

---

## 1. Goals

- Build something **demonstrably "energy storage"** for a CV, not a toy demo.
- Stay aligned with a **backend/full-stack career target** — most of the work is backend, with embedded as the standout differentiator.
- Reuse proven strengths: BMS/telemetry hardware experience and a production-grade backend stack (JWT, PostgreSQL, Docker, CI/CD, tests, OpenAPI).
- Require **no electrochemistry** — the battery is treated as a black box with a behavioral interface (voltage / current / temperature limits).

---

## 2. System architecture

```
[ LiFePO4 pack ]
       │  per-cell V, pack current, temperature
       ▼
[ ESP32 edge node ]
   - reads cell data (LTC6811-style)
   - local buffering when offline
   - publishes MQTT / HTTP
       │
       ▼  telemetry
[ Ingestion service ]
   - validation
   - writes to time-series store
       │
       ├──────────────► [ PostgreSQL + TimescaleDB ]
       │
       ▼
[ REST / WebSocket API ]   ── JWT auth, input validation, OpenAPI spec
   - serves live + historical data
   - alerting rules engine
       │
       ▼
[ React / React Native dashboard ]
   - live pack status, per-cell view
   - historical charts, alarm log
```

Everything is containerized (Docker), with CI/CD and a real test suite.

---

## 3. Components

### 3.1 Edge node — embedded differentiator

|Item|Detail|
|---|---|
|MCU|ESP32|
|Pack|Small **LiFePO4** pack (safest, most forgiving chemistry to learn on)|
|Sensing|Per-cell voltage, pack current, temperature|
|Transport|MQTT (with HTTP fallback)|
|Resilience|Local buffering + resync when connection drops|

> The offline-resilience detail is exactly what real field devices need and most student projects ignore — a cheap, high-credibility differentiator.

### 3.2 Backend — career core

- **Ingestion service** — receives MQTT/HTTP telemetry, validates, persists.
- **Time-series store** — PostgreSQL + TimescaleDB (industry-standard, CV-friendly choice over InfluxDB for this use case).
- **API** — REST + WebSocket, JWT auth, input validation, OpenAPI spec.
- **Alerting rules engine** — over-voltage, over-temperature, cell imbalance → notification.
- **Ops** — Dockerized, CI/CD pipeline, automated tests.

### 3.3 Frontend

- Live pack status and per-cell view.
- Historical charts.
- Alarm / event log.
- React (web) or React Native (mobile) — both already in your toolkit.

---

## 4. The battery interface (the only "chemistry" you need)

Treat the cell as a black box with rules, exactly like a motor controller register map. The interface contract:

- **Voltage limits** — over/under-voltage is dangerous; the BMS enforces it.
- **Current limits** — charge/discharge rates, temperature-dependent.
- **Temperature limits** — thermal runaway is the safety case; monitor + cut off.
- **Voltage-vs-state-of-charge curve** — used to estimate how full the pack is.
- **Aging behavior** — state of health; capacity fades over cycles.

No electrode-level or molecular knowledge required.

---

## 5. Industry-credible deep-dives (pick 1–2)

These separate the project from a generic CRUD app. Choose based on the roles you target.

### A. State-of-Charge / State-of-Health estimation

- Coulomb counting + a **Kalman filter**.
- The single most respected piece of the project.
- Runs directly on your Signals & Systems (state-space, LTI) and Bayesian statistics background.

### B. Tariff-aware charge/discharge optimization

- Decide when to charge/discharge based on **time-of-use electricity pricing**.
- This is how real home/grid batteries make money.
- Distinctive angle: your finance interest expressed in an engineering project.

### C. Predictive maintenance

- Flag degradation trends before failure.
- Active, hot topic in the storage field.

---

## 6. Build order (MVP → industry-credible → stretch)

### Phase 1 — MVP

1. Edge node reads pack data, publishes telemetry.
2. Ingestion service validates and writes to TimescaleDB.
3. Minimal API serving latest readings.
4. Basic dashboard: live pack status + one historical chart.

### Phase 2 — Production hardening

5. JWT auth, input validation, OpenAPI spec.
6. Alerting rules engine + notifications.
7. Dockerize everything; add CI/CD and tests.
8. Offline buffering + resync on the edge node.

### Phase 3 — Differentiating deep-dive

9. Implement one of the deep-dives from section 5 (SoC/SoH recommended).
10. Polish dashboard; write a strong README with architecture + screenshots.

---

## 7. Hardware note

If parts are a constraint, scope a version that runs partly on **simulated telemetry** (a generator publishing realistic MQTT data) so backend and frontend work is never blocked on hardware availability. Swap in the real ESP32 + LiFePO4 pack once available.

---

## 8. Tech stack summary

|Layer|Choice|
|---|---|
|Edge|ESP32, MQTT|
|Backend|Go (Fiber) or Node.js|
|Datastore|PostgreSQL + TimescaleDB|
|API|REST + WebSocket, JWT, OpenAPI|
|Frontend|React / React Native|
|Ops|Docker, CI/CD, automated tests|

---

## 9. Note-keeping (Obsidian)

Keep project notes, design decisions, and progress logs in **Obsidian**: [https://obsidian.md](https://obsidian.md/)

This file drops straight into a vault as-is. Suggested vault structure:

```
BESS-Project/
├── 00-overview.md          ← this document
├── 01-architecture.md
├── 02-edge-node.md
├── 03-backend.md
├── 04-soc-soh-estimation.md
└── logs/
    └── YYYY-MM-DD.md        ← daily build log
```

Use Obsidian `[[wikilinks]]` to cross-reference (e.g. link `00-overview` to `[[04-soc-soh-estimation]]`), and tags like `#phase1` `#blocked` `#decision` to track progress and surface open questions in search.