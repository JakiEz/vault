---
title: "Prof. Ting-Chung Yu (余定中) — Research Notes"
tags: [lhu, research, advisor, power-systems, solar, mppt, exchange]
created: 2026-06-13
status: pre-meeting research
---

# Prof. Ting-Chung Yu (余定中) — Research Notes

Notes compiled before reaching out for a research-direction meeting at LHU.

## Profile (confirmed)

- **Name:** 余定中 / Ting-Chung Yu
- **Title:** Assistant Professor, Dept. of Electrical Engineering (電機工程系), Lunghwa University of Science and Technology (LHU)
- **Office:** F415
- **Email:** tingyu@mail.lhu.edu.tw
- **Tel:** (02) 82093211 ext. 5531
- **PhD:** Electrical Engineering, University of British Columbia (UBC), Canada
- **Listed specialties:** Solar power technology · Solar maximum power point tracking (MPPT) algorithms · Power-system electromagnetic transient (EMT) analysis · Power network analysis

## What his research actually is

There is a clear split between his **frontier research** and his **listed teaching specialties** — important for picking a realistic project.

### Frontier research = numerical power-system modeling (theoretical, math-heavy)

- **Confirmed:** He was a member of the **UBC Power Group**, working specifically on **cable modeling**. (Independently confirmed via another UBC dissertation that thanks him for "discussions on cables.")
- This group is the lineage of **José Martí** and **Hermann Dommel** — the originators of the standard transmission-line / cable models used in EMTP-type simulators worldwide. Strong pedigree in the most established corner of transient modeling.
- **Core work (high confidence; verify authorship in one click):**
  *"A Frequency-Dependent Multiconductor Transmission Line Model with Collocated Voltage and Current Propagation"*
  - UBC dissertation → journal paper in **IEEE Transactions on Power Delivery, vol. 33, no. 1, pp. 71–81** (DOI: 10.1109/TPWRD.2017.2691343)
  - **Idea in plain terms:** classical multiconductor transmission-line equations need complex frequency-dependent transformation matrices. He adds a physical constraint — voltage and current waves must travel together (collocated) with the same propagation function — producing "Revised" equations that diagonalize with a **single real constant matrix** instead. Simpler, still accurate.
  - Benchmarked against the two most accepted frequency-dependent line models in EMTP: **J. Martí's fdLine** and the **Universal Line Model (ULM)**.
- **Earlier work (~2008):** frequency-dependent shunt admittances in underground cable systems (same research vein).

> This side is serious applied-math / numerical-methods territory. Far from an embedded/firmware/full-stack skill set — not realistic to contribute to in one exchange semester.

### Listed teaching specialties = applied solar / MPPT (where a student project fits)

- Solar power + MPPT are the **applied** items on his profile.
- At a university of science and technology like LHU, these are very likely what he **supervises student projects on**.
- This is where my embedded + software skills plug in: MPPT-under-partial-shading algorithms, solar–storage coordination, PV monitoring/telemetry + dashboard.

## Strategic read for the meeting

**Acknowledge his depth, propose in his applied lane.**

- Reference his EMT / transmission-line modeling background to show genuine homework (professors notice immediately).
- Steer toward the solar / MPPT / storage applied side — a project I can actually execute and that plays to my strengths.

**Sample framing line:**
> "I saw your doctoral work was on frequency-dependent transmission-line modeling for electromagnetic transient simulation in the UBC power group. I'm coming from the embedded and software side — interested in the more applied solar / MPPT direction. Is that something you supervise?"

## Candidate project angles (my skills × his lane)

- **MPPT under partial shading** — classic P&O / IncCond get stuck on local maxima; metaheuristic or ML/RL methods find the global peak. Pure algorithms + embedded (microcontroller + DC-DC converter). Most self-contained / prototype-able.
- **Solar generation forecasting** — ML from weather/irradiance data → storage dispatch. Maps onto my IoT / Random Forest coursework + backend pipeline skills.
- **PV monitoring & fault detection** — telemetry → pipeline → dashboard (same shape as FSAE telemetry + IoT power-monitoring projects).
- **BMS for solar-coupled storage** — bridges his solar specialty with my BMS/embedded background (LTC6811, CAN, balancing, logging).

## To verify / next steps

- [ ] Confirm authorship of the FDLM thesis/paper on IEEE Xplore + UBC cIRcle
- [ ] Check his **Google Scholar** profile (disambiguate: "Ting-Chung Yu" + photovoltaic / electromagnetic transient — common name)
- [ ] Search **Airiti Library** / Taiwan research databases for LHU-era publications
- [ ] Draft + send the meeting-request email (15–20 min, directions not a full pitch)
- [ ] Backup: drop by office F415 during office hours with a 1-page CV if no email reply in 2–3 working days

## Sources

- LHU EE faculty page: https://eee.lhu.edu.tw/p/412-1015-194.php?Lang=zh-tw
- IEEE TPWRD paper (FDLM): https://ieeexplore.ieee.org/document/7892918/
- UBC cIRcle thesis record: https://open.library.ubc.ca/soa/cIRcle/collections/ubctheses/24/items/1.0343065
