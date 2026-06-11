# Custom FSAE Battery Management System (BMS) — Project Context

> Context document for AI chats / Obsidian vault. Owner: Jackie (Jedsarid Sangsuwan), CPE @ KMUTT, ex-BlackPearl FSAE EV team (3 years).
> Last updated: 2026-06-11

## TL;DR

Custom 10-cell BMS for a Formula Student electric vehicle (BlackPearl FSAE team). ESP32-C3 master MCU talking to an LTC6811 battery monitor over SPI, broadcasting pack data over isolated CAN bus, with passive cell balancing, temperature sensing, and SD card logging. Replaced a previous Arduino Nano-based design that suffered data corruption from EMI/ground-loop issues when installed in the car.

## Why this project exists

- **V1 (previous year):** Arduino Nano + LTC6811, powered from external 12V supply, CAN comms working on the bench but **data became unreliable once installed in the car** (suspected causes: power supply noise, EMI from motor/inverter, ground loops, CAN termination/isolation issues).
- **V2 (this project):** ESP32-C3, powered **from the battery pack itself**, isolated CAN, better noise immunity. Goal was "surely working" reliability with ~1 month build time before competition.

## Hardware

| Block | Part / Detail |
|---|---|
| MCU | ESP32-C3 (ESP32-C3FH4), 3.3 V, ~160 mA active w/ WiFi |
| Cell monitor | LTC6811 (12-cell capable, used for 10 cells), ±1.2 mV typ. accuracy |
| MCU ↔ monitor link | SPI (raw commands initially, later official LTC6811 library) |
| CAN transceiver | SN65HVD230, isolated via ADUM1201 digital isolator |
| Current sensing | INA260 |
| Temperature | DS18B20 sensors (+ thermistor inputs on LTC6811 GPIOs) |
| Balancing hardware | Per-cell discharge: 4.7 kΩ ∥ 100 Ω resistors + MOSFET driven by LTC6811 DCC pins + indicator LEDs (~17–18 mA discharge current) |
| Logging | SD card |
| Power | Pack tap → buck converter (12 V → 5 V) → 3.3 V rails for ESP32 / LTC6811 / transceiver |
| Reference design | DC2259A (Analog Devices LTC6811 eval board) used as schematic reference |

## Architecture

```
Battery cells (10S)
   ↓ sense lines
LTC6811  ──SPI──>  ESP32-C3  ──ADUM1201──>  SN65HVD230  ──> CAN bus (vehicle)
   │                  │
 DCC pins          SD logging
   ↓
 MOSFET + resistor passive balancing
```

Vehicle CAN network context: BMS is one of four CAN nodes (Front, Rear, BAMO/Bamocar D3 motor controller, AMS) feeding a React/Vite + Node.js WebSocket telemetry dashboard (deployed Netlify/Render, schema-driven protocol).

## Firmware — key implementation details

- **Cell voltage read:** LTC6811 ADC conversion commands over SPI; configuration register (CFGA) readback used to verify the chip accepted commands.
- **Discharge / balancing control:** discharge bits live in CFGA[4] (cells 1–8) and CFGA[5] lower nibble (cells 9–12). DCTO (Discharge Time Out) timer is the **upper nibble of CFGA[5]**, 1 increment = 30 s, so timer value must be shifted left 4 bits. A premature-stop bug was traced to the hardware timer; fix was explicit timer clearing + readback verification.
- **Auto-balancing:** balances cells toward the minimum cell voltage with configurable timeouts.
- **CAN frames:** individual cell voltages + pack statistics (min/max/avg, temperatures, current).
- **Debugging features:** extensive serial diagnostics, SPI transaction management fixes (a CAN data-transmission bug was caused by improper SPI transaction handling).

## Hard-won lessons (the valuable part)

1. **Software being "correct" doesn't mean hardware works** — discharge commands were verified via register readback while the discharge circuit itself was dead. Always separate "chip received command" from "physical effect happened."
2. **Bench ≠ car.** EMI, ground loops, and supply noise destroyed V1's data integrity. Isolation (ADUM1201) and pack-powered design were the fixes.
3. **SPI transaction discipline matters** — sloppy transaction management broke an unrelated subsystem (CAN TX).
4. **Register-level datasheet reading is unavoidable** for chips like the LTC6811 (CFGA bit packing, DCTO nibble encoding).
5. **Use the official library** once you understand the raw protocol — best of both.

## Related projects (same ecosystem)

- **FSAE telemetry system:** React/Vite dashboard + Node.js WebSocket server, 4 CAN nodes, schema-driven protocol.
- **Bamocar D3 CAN logger** (motor controller data).
- **DIY smart power monitor:** ESP32 + PZEM-004T + SSR → MQTT → Node-RED → InfluxDB, Docker Compose, Express API (IoT course final).

## Skills demonstrated

Embedded C/C++ (ESP32/Arduino framework), SPI & CAN protocols, register-level driver work, PCB design, power architecture & isolation, EMI debugging, battery safety concepts (FSAE EV rules: AMS, IMD, contactor control), full-stack telemetry (React, Node.js, WebSocket).

---

# Project idea backlog (building on the BMS)

## Software-leaning (fits backend/full-stack career path)

1. **BMS Cloud Telemetry Platform** — Go/Fiber or Node backend ingesting CAN/MQTT data from the BMS, PostgreSQL/TimescaleDB storage, REST + WebSocket API, React dashboard with historical charts and alerting. Essentially the portfolio-tracker stack applied to your own hardware data. Strong portfolio piece: "IoT data pipeline I built end-to-end, sensor to screen."
2. **CAN bus decoder web tool** — upload a CAN log (or DBC file), get decoded signals + charts. Niche, useful, demonstrates parsing + visualization.
3. **Battery digital twin / SoC estimator** — implement Coulomb counting + OCV lookup (later: Kalman filter) on logged cell data; compare estimation methods in a Jupyter/Go service. Bridges embedded + data skills.
4. **Fleet BMS dashboard SaaS mock** — multi-tenant version of #1 with JWT auth, org/device management, Docker, CI/CD, OpenAPI — directly reuses your planned portfolio-tracker architecture.

## Hardware/embedded-leaning

5. **BMS v3:** daisy-chained LTC6811s for a full accumulator segment (isoSPI), active balancing exploration, or migrate to ESP32-S3/STM32 with FreeRTOS task structure.
6. **Battery cycler / capacity tester** — controlled charge/discharge rig with INA260 logging; produces real datasets for #3.
7. **Second-life battery monitor** — repurpose the BMS for a DIY powerwall/UPS from used 18650s; popular project genre, practical at home.

## Quick wins

8. Write the BMS up as a **technical blog post / GitHub README with schematics** — recruiters can't read your PCB, but they can read a good post-mortem (lesson #1 above is a great hook).
9. Publish the LTC6811 + ESP32-C3 driver code as a clean library — small, finished, citable.
