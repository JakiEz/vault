---
type: note
title: "LHU EE — Advisor Candidates (Active Balancing)"
description: Quick capture of LHU power-electronics / embedded professors as advisor candidates for the active-balancing BMS internship, with fit notes.
tags: [taiwan, lhu, internship, exchange, advisor, bms, active-balancing]
created: 2026-06-15
updated: 2026-06-15
status: shortlist
---

# LHU EE — Advisor Candidates (Active Balancing)

Quick shortlist of LHU professors whose lanes fit my **active-balancing BMS** project (see [[active-balancing-scope]] idea + [[bms-project-context]]). Department to confirm (likely Electrical/Electronic Eng). Add to [[taiwan-internship]] hub.

> ⚠️ **Superseded direction (16 Jun 2026):** the project pivoted from active balancing → **MPPT solar PV monitoring** under **Prof. Cheng-Chuan Chen (陳政傳)**. See [[LHU_Project_Notes_2026-06-16]] for the current plan. This note is kept for the advisor shortlist + power-electronics fit info.

> Romanization + Chinese name as given; verify exact dept, office, email on the LHU faculty page before outreach.

## Candidates

| Person                                | Title                                         | Specialties                                                        | Fit for active balancing                                                                                                                                                                    |
| ------------------------------------- | --------------------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Jui-Yuan Chai (翟瑞元)**               | Asst Prof (deputy chair); PhD Tsinghua / NTHU | Motor drive systems, electrical-machine control, power electronics | **Power-stage / converter side** — serious power-electronics person; the active-balance converter (flyback/LTC3300) is in his wheelhouse                                                    |
| **Heng-Kung Wang (王漢堃)**              | Asst Prof                                     | Power electronics + single-chip/MCU system applications            | **Best all-round** — exact power-electronics + microcontroller combo the project needs                                                                                                      |
| **Wei-Hong Lin ("William Lin," 林威宏)** | Asst Prof                                     | PIC MCU firmware, UART, I²C, SPI, CAN bus, Bluetooth               | **Embedded-comms / integration** — my exact stack (LTC6811 over SPI, isolated CAN). Natural match or co-advisor for ESP32/isoSPI side; English name → likely used to international students |

## Read

- **Wang** = strongest single-advisor fit (power electronics *and* MCU under one roof).
- **Chai** = best for the converter/power-stage depth (and is a deputy chair — useful for approvals).
- **Lin** = ideal **co-advisor** for the firmware/comms integration; possible English-language bridge.
- Ideal combo: **Wang or Chai (power stage) + Lin (embedded integration)**.

## Likely starter exercises (advisor's toolchain)

What an advisor here might assign as a bounded warm-up — the equivalent of "do X in Vivado." Match the tool to the professor's world:

- **MATLAB / Simulink** (the dominant tool in this world): a bounded exercise — model a power system or a battery, run a power-flow or fault simulation, or build a fault-diagnosis routine on signal data. Closest one-to-one match to a "do X in Vivado" task.
- **Python (or MATLAB) on a real dataset**: given a battery/energy dataset, build a monitoring + diagnosis pipeline — detect cell imbalance, classify faults, or estimate **SOH**. Plays to my software strengths *and* a diagnosis-oriented advisor's specialty.
- **Power-system tool (ETAP / PSCAD / PowerWorld)**: if the advisor leans grid / power-system analysis — "model this network and analyze the fault behavior." Heavier, more traditional, less aligned with my embedded/software strengths.

> Read: MATLAB/Simulink + a battery dataset (cell-imbalance detection / SOH) is the sweet spot — bounded, fits a 2-month window, and bridges my BMS background to a fault-diagnosis ask.

## Next

- [ ] Confirm each professor's department, office, email, ext on the LHU faculty page
- [ ] Pull their actual paper lists (LHU `Research_Display` / 學術成果 link) to verify active-balancing / converter relevance
- [ ] Decide lead advisor vs co-advisor split; mirror [[prof-ting-chung-yu]] note format for the chosen lead
- [ ] Fold into outreach ([[Mail note]])

## Related

- [[taiwan-internship]] — internship hub
- [[bms-project-context]] — my BMS background (V2: ESP32-C3 + LTC6811, passive balancing)
- [[prof-ting-chung-yu]] — existing advisor lead (solar/MPPT)
