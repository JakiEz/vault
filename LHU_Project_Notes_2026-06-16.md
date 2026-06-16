---
type: project
title: "LHU Internship — MPPT Project Scoping Notes"
description: "Chosen internship project = ESP32-based solar PV MPPT monitoring + dashboard under Prof. Cheng-Chuan Chen (陳政傳); deadline 31 Jul 2026. Covers MPPT/P&O, boost sizing, Simulink, parts, advisor landscape, timeline."
tags: [taiwan, lhu, internship, exchange, mppt, solar, pv, esp32, project]
created: 2026-06-16
updated: 2026-06-16
status: active
---

# LHU Internship — Project Scoping Notes
*Conversation summary — 16 June 2026*

---

## 1. The decision journey (how we got to the project)

- Started from the 2023 heliostat-field modeling problem and a question about whether concentrated solar power (CSP) is practical → concluded CSP is real but niche (good only for utility-scale, high-sun sites needing dispatchable storage); plain solar PV wins almost everywhere else.
- Explored research directions: quant finance, battery SOH/ML, energy-system optimization. Chose the **engineering path over finance**.
- Battery/BMS active balancing was scoped in depth but judged **too hard for the ~2-month window** (custom magnetics, PCB, power-stage risk).
- Pivoted to picking an **available, well-matched advisor first**, then co-designing a project in their domain.
- Landed on **solar PV + MPPT** to fit **Assoc. Prof. Cheng-Chuan Chen (陳政傳)**, whose fields are sensing & microcontrollers, power electronics, analog IC, and solar PV.

---

## 2. The chosen project

**Title:** A microcontroller-based solar PV monitoring system with on-MCU MPPT control and a real-time dashboard.

**One-line description:** Pull the most power possible from a solar panel by continuously adjusting the converter's duty cycle (MPPT), and monitor it live.

**Core idea:** an ESP32 senses panel V/I/temperature/light, drives a DC–DC boost converter via PWM to run an MPPT loop, logs and streams everything to a dashboard, then quantifies energy gained vs a fixed operating point — primarily using Perturb & Observe (P&O), with Incremental Conductance as a time-permitting comparison.

**Key scoping rule:** *buy the power stage, own the control + measurement.* No custom magnetics/PCB; the contribution is sensing, control firmware, measurement, and analysis.

**Never-blocked fallback:** build the MATLAB/Simulink model from day one; if hardware is delayed, develop P&O in simulation first, then port to hardware.

---

## 3. MPPT — core concepts

- A PV panel's output depends on **where on its I–V curve** it operates; there is one **maximum power point (MPP)** where P = V×I is greatest.
- The MPP **moves** with irradiance and temperature, so it must be tracked continuously.
- **What you control:** the converter's duty cycle, which changes the effective resistance the converter presents → shifts the panel's operating point → changes extracted power.
- **You do NOT adjust the load** — the load just receives delivered power.

**P&O algorithm (the loop):**
1. Measure V and I → compute P.
2. Compare P to the previous step (up or down?).
3. If power rose → keep going same direction; if it fell → reverse.
4. Perturb the operating point one small step (change duty cycle).
5. Repeat.

It is hill-climbing; it always jitters slightly around the MPP. **Step size** sets the trade-off: bigger step = faster but more oscillation (wasted energy); smaller = accurate but slow.

**Partial shading** creates multiple peaks on the P–V curve, so simple P&O can lock onto a *local* (wrong) maximum — this is the hard case.

---

## 4. Boost converter & component sizing

**Inductor formula (boost):**

`L = (Vin × D) / (f × ΔI_L)`

- D (duty cycle) = 1 − Vin/Vout = fraction of each switching cycle the MOSFET is ON
- ΔI_L = peak-to-peak ripple current (pick ~30% of average inductor current)
- I_avg (inductor) = Pin / Vin
- Higher f or larger allowed ripple → smaller inductor

**Worked example (12 V → 24 V, 10 W, 50 kHz):**
- D = 1 − 12/24 = 0.5
- I_avg = 10/12 ≈ 0.9 A
- ΔI_L = 30% × 0.9 ≈ 0.27 A
- L = (12 × 0.5)/(50,000 × 0.27) ≈ 440 µH → **use 470 µH, ≥2 A**

**Why a Schottky diode:** it's the one-way valve that lets the inductor dump energy to the output and blocks reverse drain when the switch is on. Schottky specifically = low forward drop (~0.3 V vs ~0.7 V) and fast switching → higher efficiency at high PWM frequency.

**Recommended voltage:** design around a small **12 V-class panel**, boost to ~24 V, keep every node **under 36 V** (INA260 sensor limit + safety). A 6 V→12 V build is even safer.

---

## 5. Hardware parts list

| Category | Item | Spec / note |
|---|---|---|
| Brain | ESP32 dev board | runs MPPT loop, PWM, sensing |
| Source | PV panel | ~10 W, 12 V class |
| Switch | MOSFET | IRLZ44N (logic-level; driven directly by ESP32 PWM) |
| (opt) | Gate driver | TLP250 — if switching >~100 kHz or MOSFET runs hot |
| Power stage | Inductor | 470 µH, ≥2 A |
| Power stage | Schottky diode | SS34 |
| Power stage | Capacitors | ~100 µF input; ~100 µF/50 V + 1 µF ceramic output |
| Sensing | INA260 | V, I, power over I²C (36 V max) |
| Sensing | DS18B20 | panel temperature |
| Sensing (opt) | BH1750 | irradiance / light level |
| Load | Power resistor / e-load | for repeatable tests |
| Equipment | Oscilloscope | critical — view PWM & inductor current |
| Equipment | Multimeter, bench PSU | bring-up / checks |
| Equipment | Halogen lamp + card | controllable light & partial-shading tests |
| Software | MATLAB/Simulink | model / cross-check |

> A buck-boost **module** replaces the loose inductor + diode + MOSFET + caps — BUT only works for MPPT if its **switch is PWM-controllable**. Cheap pot-adjustable modules have a fixed controller you can't command → monitoring only. The realistic controllable build = IRLZ44N + inductor + SS34 + caps.

---

## 6. Simulink model

**Block flow:** Irradiance & temp → PV Array → Boost converter → Load, with a feedback loop: sensed V,I → MPPT (P&O, MATLAB Function) → duty cycle D → PWM generator → gate → converter switch.

**Build steps:**
1. New model + `powergui` block; solver `ode23tb`.
2. Add `PV Array` (Specialized Power Systems → Renewables); feed irradiance & temperature.
3. Build boost converter from Specialized Power Systems parts.
4. Add `Voltage Measurement` + `Current Measurement`.
5. `MATLAB Function` block for P&O (in V, I → out duty cycle D, clamped ~0.1–0.9).
6. PWM via `PWM Generator (DC-DC)` or compare D to a sawtooth; drive MOSFET gate.
7. Scopes on power, V, I, D.
8. Run; apply irradiance step (e.g. 1000 → 600 W/m²) and watch re-tracking.
9. Later: two series PV arrays at different irradiance → partial-shading multi-peak test.

**Connection fix:** the PV Array is a **Specialized Power Systems** block, so every circuit component must come from that same family. There's no standalone inductor — use **Series RLC Branch** set to *Branch type: L* (and another set to C for the cap, R for the load). A general Simscape Foundation inductor uses a different port type and won't connect. Keep one family throughout, and include a `powergui`.

> Fastest start: open a MathWorks "MPPT boost converter" example, run it, then swap in your panel + your own P&O function.

---

## 7. Making it harder / more meaningful

Climb one of three ladders — harder algorithm, harder conditions, harder validation:
1. **Global MPPT under partial shading** (solve the case P&O fails at).
2. **AI / metaheuristic tracker** — fuzzy logic, small neural net, or Particle Swarm Optimization (PSO) for global MPP.
3. **Rigorous validation** — tracking efficiency vs theoretical MPP, dynamic response, oscillation loss, hardware-vs-Simulink cross-check.
4. **Embedded-cost angle (your unique edge):** does a heavier method (PSO/NN) still fit the ESP32's compute budget?
5. **Meaningful framing:** "Does PSO-based global MPPT justify its complexity over simple periodic-scan P&O on a low-cost MCU under partial shading?"

**Recommended combo:** partial shading + PSO (or NN) + embedded-cost question, framed as #5. **Keep the staircase:** get simple P&O working as a guaranteed baseline first, then climb — don't let "harder" become "unfinished" in a 5-week window.

---

## 8. Lunghwa advisor landscape

**Departments are separate:** Electrical Engineering (電機工程系) vs Electronic Engineering (電子工程系).

| Professor | Dept | Fields | Fit |
|---|---|---|---|
| Cheng-Chuan Chen 陳政傳 | Electrical | sensing/MCU, power electronics, analog IC, solar PV | **Chosen** — matches the MPPT project |
| Ting-Chung Yu 余定中 | Electrical | solar PV, MPPT, EM transient, power networks | Solar/MPPT; said BMS not his area |
| Yu-Ming Jheng 鄭育明 | Electrical | power system analysis, smart energy monitoring, equipment diagnosis | Monitoring/diagnosis (battery via data) |
| Chen Fu-Xian 陳輔賢 | Electronic | power-equipment fault diagnosis, power systems | Diagnosis-focused alternative |
| Li Bing-Hui 李炳輝 | Electronic | AC-DC power supply, MCU, control | Works on micromouse robots |
| Qiu Huang-Sen 邱煌森 | Electronic | databases, embedded, software; indoor positioning | Applied embedded/IoT, not battery |
| Ji Wei-Min 紀偉民 | Electronic | sensors, biomedical, AI; some EV control | Biomedical + an EV-control angle |
| Que He-Li 闕河立 | Electronic | FPGA, digital comms | The FPGA/Vivado route |

**Verifying a professor's papers yourself:** search the **exact publishing name in quotes** on Google Scholar (e.g. names romanize inconsistently), check the LHU institutional repository (學術成果 link), or PubMed/IEEE Xplore by title. Judge fit by recency, authorship position (first/last = their work), and topic match to what they told you.

---

## 9. Communicating with Prof. Chen

- **Lead with the project, in his lane.** Reference his actual MPPT/solar work.
- **When asked "specific goal or just learning?"** → answer goal-oriented: finish one concrete, documented deliverable.
- **Be honest about scope:** analog work is board-level signal conditioning, not chip design.
- **Lab needs to confirm:** oscilloscope, a small PV panel, and a MATLAB/Simulink license (with Simscape). Frame as low-burden: "the rest I can source cheaply."
- **Ask for a tool-based exercise** (like the friend's Vivado task) — e.g. a MATLAB/Simulink MPPT exercise — as an easy entry point.

**Likely questions to prep:** explain P&O step-by-step; the step-size trade-off; why partial shading is hard; P&O vs IncCond; converter topology; how the MCU sets the operating point; why ESP32 (honest: your expertise + connectivity, not the optimal industrial choice); can you finish by 31 July; what's *your* contribution vs off-the-shelf; **how will you validate results** (cross-check vs Simulink and theoretical MPP).

---

## 10. Timeline (fixed end: 31 July 2026)

~5 working weeks after setup. Front-load simulation so procurement can't block you.

| Period | Activity |
|---|---|
| 16–20 Jun | Confirm advisor + meeting; order panel, converter parts, sensors; start Simulink model |
| Late Jun (parts shipping) | P&O in simulation; ESP32 sensing firmware + dashboard |
| Early–mid Jul | Hardware bring-up; P&O tracking on real panel; measurements |
| Mid–late Jul | Characterize P&O + partial-shading tests; stretch: IncCond / PSO |
| Final 4–5 days | Analysis + final report |

**Highest-value action now:** contact Chen and order parts — every day of delay compresses the build.

---

## 11. Open next steps (offered)

- One-page email version of the proposal for first contact.
- The actual P&O code for the MATLAB Function block.
- Spelling out the PSO-under-partial-shading upgrade within 5 weeks.
- Exact Series RLC Branch settings for each component.

---

## Related notes

- [[taiwan-internship]] — internship hub (connections table, outreach status). **This note is the chosen-project record it points to.**
- [[prof-ting-chung-yu]] — Prof. Yu (余定中): solar/MPPT lane, but told me **BMS isn't his area** (why I moved to Chen).
- [[lhu-ee-advisor-candidates]] — earlier power-electronics/embedded shortlist from the **active-balancing** direction (now superseded by this MPPT plan; kept for advisor fit info).
- [[bms-project-context]] — my BMS/embedded background (ESP32, sensing, telemetry, FSAE) that this project reuses.
- [[Mail note]] — outreach email drafts to adapt for Prof. Chen.
- Seed problem: **CUMCM 2023 A — heliostat field optimization** (CSP) at `D:\kmutt\internship\research\cumcm2023a\` (`A题.pdf` + `附件.xlsx`); led to the "CSP is niche → go solar PV + MPPT" conclusion in §1.
