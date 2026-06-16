---
type: moc
title: "Taiwan Internship / Exchange — Hub"
description: Hub for my LHU exchange research internship — connections, contacts, project search, and outreach status.
tags: [taiwan, lhu, internship, exchange, research]
created: 2026-06-13
updated: 2026-06-16
status: active
---

# Taiwan Internship / Exchange — Hub

Map of Content for my exchange research internship at **Lunghwa University of Science and Technology (LHU)**. Tracks people to connect with, their research lanes, and where I am in reaching out.

## TL;DR

- Goal: land a **research project during the exchange** that plays to my embedded / BMS / software strengths.
- **Chosen project (16 Jun):** ESP32-based **solar PV MPPT monitoring + dashboard** — full scoping in [[LHU_Project_Notes_2026-06-16]]. Deadline **31 Jul 2026**.
- **Chosen advisor:** **Prof. Cheng-Chuan Chen (陳政傳)** — solar PV + power electronics + MCU. (Active balancing was dropped as too hard for the window; Prof. Yu said BMS isn't his area.)
- Strategy: lead with the project in the advisor's lane; front-load the MATLAB/Simulink model so parts procurement can't block me.

## Connections

| Person | Role / Dept | Lane I'd pitch | Status | Note |
|---|---|---|---|---|
| Prof. Chen Zhengchuan / Cheng-Chuan Chen (陳政傳) | Assoc. Prof, EE, LHU (F511) | **MPPT solar PV monitoring** (power electronics + MCU + solar) | ✅ **Chosen advisor** | [[LHU_Project_Notes_2026-06-16]] · [ResearchGate](https://www.researchgate.net/profile/Cheng-Chuan-Chen-2) (⚠️ confirm = LHU) |
| Prof. Ting-Chung Yu (余定中) | Asst. Prof, EE, LHU (F415) | Applied solar / MPPT | ↩︎ Solar/MPPT fit, but said BMS not his area | [[prof-ting-chung-yu]] |
| Prof. Li Binghui (李炳輝) | Asst. Prof, Electronic Eng, LHU | Active balancing — power supply + MCU + control | 🔎 Shortlisted | Best battery-mgmt fit |
| Prof. Heng-Kung Wang (王漢堃) | Asst. Prof, EE, LHU | Active balancing — power electronics + MCU | 🔎 Shortlisted | [[lhu-ee-advisor-candidates]] |
| Prof. Jui-Yuan Chai (翟瑞元) | Asst. Prof (deputy chair), EE, LHU | Active-balance power stage / converter | 🔎 Shortlisted | [[lhu-ee-advisor-candidates]] |
| Prof. Wei-Hong Lin (林威宏) | Asst. Prof, EE, LHU | Embedded-comms integration (SPI/CAN) — co-advisor | 🔎 Shortlisted | [[lhu-ee-advisor-candidates]] |

> Add a row per new contact. Link each to a dedicated research note (mirror the [[prof-ting-chung-yu]] format).
> ⚠️ **Direction changed (16 Jun):** project is now **MPPT solar PV monitoring** under **Prof. Chen** — see [[LHU_Project_Notes_2026-06-16]]. The remaining shortlist rows + [[lhu-ee-advisor-candidates]] are kept as a historical record from the active-balancing era.

## Outreach status

- [ ] **Contact Prof. Chen (陳政傳)** with the MPPT project pitch — adapt drafts in [[Mail note]]; lead with his solar/MPPT work.
- [ ] Order parts (12 V-class PV panel, PWM-controllable boost converter, INA260, DS18B20) — front-load so procurement can't block the build.
- [ ] Confirm lab access: oscilloscope + MATLAB/Simulink (Simscape) license.
- [ ] Backup: Prof. Yu drafts in [[Mail note]] remain as a secondary contact.

## Project angles (my skills × their lanes)

Pulled from [[prof-ting-chung-yu]] — reuse / refine per advisor:

- **MPPT under partial shading** — metaheuristic / RL beats P&O at local maxima. Most self-contained, embedded + algorithms.
- **Solar generation forecasting** — ML from irradiance/weather → storage dispatch.
- **PV monitoring & fault detection** — telemetry → pipeline → dashboard (same shape as my FSAE telemetry work).
- **BMS for solar-coupled storage** — bridges solar + my [[bms-project-context]] background (LTC6811, CAN, balancing, logging).

## Related notes

- [[LHU_Project_Notes_2026-06-16]] — **chosen MPPT project** full scoping (concepts, boost sizing, Simulink, parts, advisor landscape, timeline).
- [[prof-ting-chung-yu]] — pre-meeting research on the advisor.
- [[lhu-ee-advisor-candidates]] — historical power-electronics/embedded shortlist (active-balancing era).
- [[Mail note]] — outreach email drafts.
- [[bms-project-context]] — BMS background I'm leveraging in pitches.
