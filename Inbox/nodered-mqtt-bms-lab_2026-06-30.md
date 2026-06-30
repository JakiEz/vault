---
type: project-log
description: Hands-on lab building a simulated 8-cell BMS telemetry pipeline (Docker → Mosquitto MQTT → Node-RED → PostgreSQL → dashboard). First practical build of the BMS Cloud Telemetry Platform plan.
created: 2026-06-30
updated: 2026-06-30
---

# Node-RED + MQTT + Postgres BMS Lab — 2026-06-30

> Practical warm-up for [[portfolio-tracker-plan]] (BMS Cloud Telemetry Platform). Mirrors the real [[bms-project-context]] LTC6811 architecture in software. Goal beyond the lab: **prepare for paid work deploying on a customer's cloud.**

## TL;DR

Built a full **device → broker → processor → database → dashboard** pipeline locally with Docker, all running and verified:

- **Simulator** publishes 8 fake Li-ion cell voltages (random walk, every 2s) over MQTT.
- **Monitor** subscribes, runs UV/OV fault checks, drives a live dashboard, and publishes verdicts back.
- **PostgreSQL** logs every reading; queried it back for faults + per-cell stats (1,376+ rows).
- Learned the concepts behind each layer and how they map to a customer cloud.

Status: steps 1–5 done. Next = **cloud-readiness** (TLS/auth + point pipeline at a managed cloud DB).

## Stack (Docker Desktop on Windows, `D:\projects\lab`)

| Service | Image | Host port | Docker-network hostname |
|---|---|---|---|
| Mosquitto broker | `eclipse-mosquitto:2` | 1883 | `mosquitto` |
| Node-RED | `nodered/node-red:latest` | 1880 (UI at `/ui`) | `nodered` |
| PostgreSQL | `postgres:16` | 5432 | `postgres` |

- One `docker-compose.yml` defines all three; `docker compose up -d` runs the lot.
- DB creds (local lab only): user `bms` / pass `bmspass` / db `bms`.
- Node-RED dashboard palette: `node-red-dashboard` 3.6.6. Postgres node: `node-red-contrib-postgresql` (Alapetite).

## MQTT topic design

- `bms/pack1/cell/<1-8>/voltage` — float, retained
- `bms/pack1/cell/<1-8>/status` — `ok|uv|ov`, retained (published by monitor)
- `bms/pack1/pack/voltage` — sum of cells, retained
- Thresholds: **UV < 3.0 V, OV > 4.2 V**

## Flows built

- **Simulator**: `inject (2s) → function (random-walk 8 cells, returns array of msgs) → mqtt out`. Uses `context` to remember each cell between runs; soft rails 2.95/4.25 V so cells still cross thresholds.
- **Monitor**: `mqtt in (cell/+/voltage) → fault check function (2 outputs) → [out1 → chart + debug + SQL] [out2 → mqtt out status]`.
  - `fault check` parses cell # from topic, `parseFloat` payload, computes verdict.
  - SQL branch: `prep insert` function sets `msg.params=[cell,voltage]` → `postgresql` node runs `INSERT INTO cell_readings (cell,voltage) VALUES ($1,$2)`.

## SQL — table + queries

```sql
CREATE TABLE cell_readings (
    ts      timestamptz NOT NULL DEFAULT now(),
    cell    smallint    NOT NULL,
    voltage real        NOT NULL
);
```
- Design choice: **store raw voltages, derive faults at query time** (`WHERE voltage<3.0`, `CASE …`) instead of a status column → change a threshold, all history re-evaluates.
- Insight surfaced: cells 1, 5, 7 had lowest avg/min → the "weak cells" that limit pack capacity (real BMS analysis).
- Run queries via `docker exec -it postgres psql -U bms -d bms`, or laptop psql/pgAdmin → `localhost:5432`.

## Concepts learned

- **Docker** = plumbing only: fetches prebuilt **images**, runs each in an isolated **container**, on a private **network** (services find each other by name — why broker host is `mosquitto` not `localhost`), **ports** publish to Windows, **volumes** persist data to disk.
- **MQTT retain** = broker stores last value per topic → new subscribers get current state instantly (right for dashboards). Not a history buffer.
- **Parameterized queries** (`$1,$2`) — values travel separately from SQL text → no injection. Build the reflex now.
- **Client vs server** — data lives in the *server*; any *client* (psql/pgAdmin/Node-RED) connects from anywhere by changing host+creds. Same SQL local or cloud.
- **Where data is kept** — Postgres data directory `/var/lib/postgresql/data` bind-mounted to `D:\projects\lab\postgres\data`. Table `cell_readings` = file `base/16384/16389`. Only the server touches these files; `pg_wal/` (write-ahead log) gives crash safety. Back up with `pg_dump`, not raw copy.
- **Production topology** — move all hosting onto an always-on machine (cloud VM running the same compose, or managed services); laptop becomes a **pure client** (browser to edit Node-RED + view dashboards). Editing Node-RED ≠ hosting it — the editor is a web app; flows run on the server even with the laptop off. Must secure: editor behind login/HTTPS/VPN, broker on TLS+auth, DB not public.

## Gotchas hit (and fixes)

| Symptom | Cause | Fix |
|---|---|---|
| Compose ignored config | files saved as `.yml.txt` / `.conf.txt` (Notepad) | rename to real extensions |
| Imported flow "vanished" | Node-RED import needs **click canvas to drop** before Deploy | re-import and drop |
| No status on broker | mqtt out wired to **output 1** not output 2 | rewire to bottom port |
| `Cwd must be absolute path` on `docker exec -w /data` | Git-Bash path mangling | prefix `MSYS_NO_PATHCONV=1` |
| (future) port 5432 clash | laptop's own Postgres also uses 5432 | stop one before `up` |

## Next steps

1. **Cloud-readiness (priority):** repoint pipeline at a free managed Postgres (Neon/Supabase/TimescaleDB Cloud) — flip `SSL: on`, change host/creds, nothing else. Then add **TLS + username/password** to Mosquitto (port 8883, no `allow_anonymous`).
2. Finish dashboard fault story: pack voltage + red/green FAULT indicator (uses `flow` context to aggregate cells).
3. Bonus: `http request → JSON → dashboard` mini-pipeline (Node-RED as web/API integrator).
4. Stretch: prove persistence (restart container, rows survive); MQTT **LWT** (last will) when simulator stops; eventually swap simulator for real ESP32.

## Links

- [[portfolio-tracker-plan]] — the 8-week platform plan this kicks off
- [[bms-project-context]] — the real LTC6811 hardware this simulates
