# BMS Cloud Telemetry Platform — Project Plan

> 8-week (2-month) build plan for idea #1 from [[bms-project-context]].
> Owner: Jackie (Jedsarid Sangsuwan). Created: 2026-06-11.

## Goal

Build an end-to-end IoT data pipeline that ingests CAN/MQTT data from the custom [[bms-project-context|FSAE BMS]], stores it in a time-series database, and serves it through a REST + WebSocket API to a React dashboard with historical charts and alerting.

**Portfolio thesis:** *"An IoT data pipeline I built end-to-end — sensor to screen."*

## Target stack

| Layer | Choice |
|---|---|
| Ingest | MQTT broker (Mosquitto) + Go/Fiber (or Node) ingest service |
| Storage | PostgreSQL + TimescaleDB hypertables |
| API | REST (historical queries) + WebSocket (live stream) |
| Frontend | React/Vite dashboard, charts (Recharts/uPlot) |
| Infra | Docker Compose, `.env` config, CI/CD (GitHub Actions) |
| Source data | BMS CAN frames: per-cell V, pack min/max/avg, temps, current (INA260) |

## Success criteria (definition of done)

- Live cell voltages + pack stats visible in the dashboard within ~1 s of the BMS publishing.
- Historical charts queryable over arbitrary time ranges.
- At least one working alert rule (e.g. cell undervoltage / overtemp).
- One-command spin-up (`docker compose up`) + a written README with architecture diagram.

---

## Weekly milestones

### Week 1 — Foundations & data contract
- Define the telemetry schema/protocol: reuse the existing schema-driven CAN protocol; document each field (cell index, voltage, temp, current, pack stats, timestamp).
- Stand up repo, `docker-compose.yml` skeleton, Mosquitto broker container.
- Write a **mock BMS publisher** that emits realistic frames to MQTT (so cloud dev isn't blocked on hardware).
- **Deliverable:** broker running locally; mock data flowing on a topic; schema doc committed.

### Week 2 — Storage layer
- Bring up PostgreSQL + TimescaleDB in Docker; design schema (hypertable for samples, dimension tables for cells/sensors).
- Decide downsampling/retention strategy (continuous aggregates for min/avg/max per minute).
- Write migrations.
- **Deliverable:** schema migrated; can hand-insert and query a time-range with `SELECT`.

### Week 3 — Ingest service
- Build the Go/Fiber (or Node) service that subscribes to MQTT, validates against the schema, and batch-inserts into TimescaleDB.
- Handle backpressure / reconnect / malformed frames.
- **Deliverable:** mock publisher → broker → ingest service → DB, persisting end-to-end.

### Week 4 — REST API
- Endpoints: list cells/devices, query samples by time range + aggregation, latest snapshot.
- Pagination, basic input validation, OpenAPI spec.
- **Deliverable:** documented REST API returning real historical data from the DB.

### Week 5 — WebSocket live stream
- WebSocket server that fan-outs new samples to subscribed clients as they're ingested.
- Topic/room model so a client can subscribe to a device or specific cells.
- **Deliverable:** a CLI/Postman client sees live updates pushed within ~1 s.

### Week 6 — Frontend dashboard
- React/Vite app: live pack overview (min/max/avg, temps, current), per-cell voltage grid, connection state.
- Wire WebSocket for live + REST for historical charts (time-range picker).
- **Deliverable:** dashboard shows live mock data and historical charts.

### Week 7 — Alerting & hardware-in-the-loop
- Alert rules engine (threshold-based: undervoltage, overtemp, cell imbalance) → dashboard banner + log.
- Swap the mock publisher for the **real BMS** (CAN → MQTT bridge); validate against live hardware.
- **Deliverable:** real BMS data on the dashboard; at least one alert firing correctly.

### Week 8 — Hardening, CI/CD & write-up
- GitHub Actions: build, test, lint, container publish.
- Polish README + architecture diagram; deploy a demo (Render/Netlify, mirroring the existing telemetry deployment).
- Record a short demo clip/GIF for the portfolio.
- **Deliverable:** deployed demo, green CI, recruiter-readable README. Ship it.

---

## Risks & notes

- **Hardware availability:** mock-first design (Week 1) keeps the cloud track unblocked if the BMS or car isn't available — real hardware only strictly needed by Week 7.
- **Scope creep:** multi-tenant/auth (JWT, org management) is explicitly *out of scope* here — that's the separate "Fleet BMS dashboard SaaS" idea (#4 in the backlog). Keep this single-tenant.
- **Reuse:** this is the portfolio-tracker architecture applied to your own hardware data — lean on that planned stack rather than reinventing.

## Related

- [[bms-project-context]] — hardware/firmware context and the source idea backlog.
- [[nodered-mqtt-bms-lab_2026-06-30]] — hands-on lab that prototypes Weeks 1–2 (Mosquitto broker + mock 8-cell publisher + PostgreSQL storage) in Node-RED; working end-to-end pipeline + concepts + cloud-readiness next steps. Personal portfolio work (not the LHU/Taiwan internship).
