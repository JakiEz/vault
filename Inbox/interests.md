---
type: note
title: Interests
description: Running list of tech topics / fields I want to explore.
tags: [interests, ideas]
created: 2026-06-19
updated: 2026-06-19
---

# Interests

Running list of technologies / fields I'm curious about. One line each; expand any into its own note later.

## Energy & hardware

### ATS — Advanced Thermovoltaic Systems ("ATS Energy") — waste heat → electricity
- **What:** a startup making a **solid-state generator (SSG)** that turns industrial **waste heat directly into electricity** — no turbines, no moving parts, no emissions/noise. "Thermovoltaic" modules on smartphone-sized plates; a hot-side temperature difference drives electron flow → DC power.
- **How:** thermoelectric effect using **proprietary Bismuth-Telluride (Bi₂Te₃) semiconductors** engineered at near-atomic level.
- **Numbers:** ~**14% thermal efficiency** (claimed ~5× prior art) on **moderate-temp waste heat (150–500 °C)** — the band that was previously uneconomic to recover.
- **Proof point:** 2024 deployment at **Holcim's Alpena cement plant (Michigan)** — **13.9% efficiency on a 240 °C** waste-heat stream, **independently validated by the US DOE**.
- **Recognition:** **2024 Earthshot Prize winner** ("Fix the Climate").
- **Target uses:** cement/lime/soda-ash kilns, refinery hot loops, turbine/engine exhaust, thermal oxidizers (VOC burn-off), waste-to-energy/pyrolysis, data centers, geothermal.
- **Why it interests me:** solid-state power conversion + semiconductors + energy harvesting — overlaps my power-electronics / embedded lane; complements (not competes with) PV/MPPT work. See [[bms-project-context]].
- Source: [ats.energy](https://ats.energy/our-technology/) · [Earthshot Prize 2024](https://earthshotprize.org/winners-finalists/advanced-thermovoltaic-systems/)

### CPO — Co-Packaged Optics — light transmission instead of copper
- **What:** integrate the **optical engine (silicon photonics) into the same package as the switch/compute ASIC**, so fiber connects right at the chip — replacing copper electrical traces *and* the separate pluggable optical transceivers.
- **Why it wins over copper:**
  - **Power:** shortening the electrical path lets you **drop DSPs/retimers/repeaters** → huge power-per-bit savings. NVIDIA claims **~5× better power efficiency** vs pluggables; Broadcom **~65% power savings** (an 800G pluggable ≈ 15 W vs CPO optical engine ≈ 5.4 W per 800G).
  - **Bandwidth & reach:** higher data rates, **~100× longer reach** than copper cabling, and immune to EMI.
  - **Scale:** NVIDIA estimates **~40 MW** saved across a large AI data center.
- **Players / products:** **NVIDIA** Spectrum-X / Quantum Photonics switches (optics on the ASIC, up to **409.6 Tb/s**, shipping ~H2 2026); **Broadcom** Bailly / Tomahawk-6 "Davisson" (Mach-Zehnder-modulator based, ~3.5× power efficiency, developing since 2021).
- **Driver:** AI/HPC clusters — GPU-to-GPU and node-to-switch "scale-up" fabrics where copper is hitting power/reach limits.
- **Market:** ~$46 M (2024) → projected **~$8.1 B by 2030** (~137% CAGR); first deployment-ready products in **2025**.
- **Why it interests me:** photonics + high-speed signal integrity + power efficiency — a frontier where my embedded/hardware interest meets the AI-infrastructure buildout.
- Sources: [NVIDIA Silicon Photonics](https://www.nvidia.com/en-us/networking/products/silicon-photonics/) · [Network World explainer](https://www.networkworld.com/article/4098942/what-is-co-packaged-optics-a-solution-for-surging-capacity-in-ai-data-center-networks.html) · [Yole CPO 2025 report](https://www.yolegroup.com/product/report/co-packaged-optics-2025/)

## Related notes
- [[bms-project-context]] — my embedded / power-electronics background.
- [[taiwan-internship]] — current solar/MPPT direction.
