---
title: Heliostat Field — CUMCM 2023 Problem A
tags: [research, CSP, solar, optimization, MATLAB, mcm]
status: in-progress
deadline: 2026-07-31
---

# Heliostat Field — CUMCM 2023 Problem A

Tower concentrating solar power (CSP). Goal: design the heliostat (定日镜) field layout to maximize output per unit mirror area. Solvable as a simulation (MATLAB/Simulink or Python) with no hardware.

## Site & physical setup
- Location: **98.5° E, 39.4° N, altitude 3000 m** (so H = 3 km in the DNI formula).
- Circular field, **radius 350 m**; **100 m keep-out zone** around the tower (no mirrors).
- Tower height **80 m**; receiver = cylinder **8 m tall × 7 m diameter**, external surface.
- Mirrors = flat rectangles. Edge length **2–8 m**; install height **2–6 m**; **width ≥ height**.
- Adjacent base-center spacing **> mirror width + 5 m** (for cleaning vehicles).
- Coordinates: origin at field center, **+x East, +y North, +z up**.
- Sampling for all "annual average" values: **21st of each month**, at **9:00, 10:30, 12:00, 13:30, 15:00** local solar time → 12 × 5 = 60 sun positions.

## The three problems
1. **Q1 (given layout):** tower at center, 1745 mirrors, all 6×6 m, install height 4 m, positions given (附件.xlsx). Compute annual avg optical efficiency (+ 4 sub-efficiencies), annual avg output thermal power, and avg output per unit mirror area. → Tables 1 & 2.
2. **Q2 (uniform design):** rated power **60 MW** annual avg. All mirrors same size & height. Choose tower position, mirror size, height, count, positions → maximize per-unit-area power. → save `result2.xlsx`.
3. **Q3 (variable design):** same 60 MW, but **sizes and heights may vary** across the field. → save `result3.xlsx`.

> [!important] Objective is **per-unit-area** power, not total. Total is pinned at 60 MW (a constraint); efficiency-per-m² is what you optimize.

## Optical efficiency model
$$\eta = \eta_{sb}\cdot\eta_{cos}\cdot\eta_{at}\cdot\eta_{trunc}\cdot\eta_{ref}$$

| Factor | Physical loss | Time-varying? |
|---|---|---|
| η_sb (shadow & block) | **Shadow** = neighbor blocks *incoming* sun; **Block** = neighbor intercepts *outgoing* reflected beam. Plus tower shadow. | **Yes** (sun direction) |
| η_cos (cosine) | Tilted mirror presents smaller *projected area* to the beam. Loss = (1 − cos θ). | **Yes** |
| η_at (atmospheric) | Beam absorbed/scattered over slant distance d_HR. | No (fixed geometry) |
| η_trunc (truncation) | Reflected beam is a **cone**; spot spilling past receiver edges is lost. | **Yes** |
| η_ref (reflectivity) | Mirror coating imperfect; fixed **0.92**. | No (constant) |

**Varies during the day: η_cos, η_sb, η_trunc** (all ride on sun's instantaneous direction).
**Constant: η_at, η_ref.**

### Key physics insights (exam takeaways)
- **Cosine is the subtle one.** $\eta_{cos}=\cos\theta$ where **θ = ½ × (angle sun–mirror–receiver)**. The mirror is *forced* to bisect by the reflection law — you never need the mirror tilt, only the angular spread between sun-direction and receiver-direction. It responds **only** to those two directions, *not* to small vertical lifts.
- **Distance trade-off (the heart of the problem):**
  - *Far mirror:* receiver low on horizon ≈ in line with sun → small θ → **good cosine**; but long d_HR → **bad atmospheric**.
  - *Close mirror:* receiver steep overhead → wide angle → **bad cosine**; short d_HR → **good atmospheric**.
  - *Caveat:* cosine also depends on **azimuthal position** (which side of the tower), not just radius — "far = good cosine" holds mainly for mirrors on the **far side from the sun**. Two mirrors at equal radius but opposite azimuth can differ a lot in η_cos.
- **Truncation worsens at low sun** (9:00): large θ → reflected spot stretches/smears → more spillage. Same θ as cosine, so cosine and truncation degrade together.
- **Raising install height** improves η_sb (clears neighbors' sightlines) at **almost no optical cost** (cosine barely moves). The real limit is structural → why height is capped 2–6 m, and why Q3 (variable heights) beats Q2.
- Geometry: **d_HR = √(R² + h²)**, where R = horizontal dist to tower, h = vertical gap = 80 − install_height = **76 m exactly** (the 80 m is defined as the receiver-*center* height above ground). h = leg, R = leg, d_HR = hypotenuse.

## Formulas (from official Appendix)
- Solar altitude: `sin α_s = cos δ cos φ cos ω + sin δ sin φ`
- Solar azimuth: `cos γ_s = (sin δ − sin α_s sin φ)/(cos α_s cos φ)`  — ⚠️ ambiguous alone (same cosine AM/PM); resolve the sign from hour angle ω (or use `atan2`), else the afternoon sun vector is mirrored.
- Hour angle: `ω = (π/12)(ST − 12)`  (ST = local time)
- Declination: `sin δ = sin(2πD/365)·sin(2π·23.45/360)`  (D = days from spring equinox = day 0)
- **DNI** = `G₀[a + b·exp(−c/sin α_s)]`, G₀ = 1.366 kW/m², **H in km**
  - `a = 0.4237 − 0.00821(6−H)²`  ⚠️ official is **0.00821** (Paper 2 wrote 0.008216)
  - `b = 0.5055 + 0.00595(6.5−H)²`
  - `c = 0.2711 + 0.01858(2.5−H)²`
- Output: `E_field = DNI · Σ Aᵢηᵢ`
- Atmospheric: `η_at = 0.99321 − 0.0001176·d_HR + 1.97×10⁻⁸·d_HR²`  (valid d_HR ≤ 1000 m — **always satisfied here**; max d_HR ≈ √(350² + 76²) ≈ 358 m)
- Truncation: `η_trunc = (receiver energy)/(total reflected energy − shadow/block loss energy)`

## Reference papers (both CC BY 4.0; translated to English in project)
- **Paper 1 — Li et al., *Modeling and Simulation* 2025, 14(7):175-184** (DOI 10.12677/mos.2025.147526). Three "Models": Q1 analysis; Q2 uniform (6×7 m, 1700 mirrors); Q3 three concentric zones. Q1 result claimed: optical 0.5856, output **48.79 MW**.
- **Paper 2 — Jia & Li, *Advances in Applied Mathematics* 2024, 13(3):1018-1026** (DOI 10.12677/aam.2024.133096). Monte-Carlo ray-tracing shadow model + Campo concentric-ring layout. Q1 result: optical 0.5688, output **34.81 MW**.

> [!warning] Known errors in the papers (don't copy blindly)
> - **They disagree on the same Q1** (35 vs 49 MW). Paper 2's ~35 MW is the trustworthy one.
> - **Paper 1:** defines cosine *inverted* (η_cos = 1 − cos θ); mislabels per-unit column kW/m² when values are W/m²; stray 0.5878 in Table 14; "total area" cols are per-mirror typos; Part-3 height text (4 m) vs table (6 m).
> - **Paper 2:** **truncation never modeled** (just assumed 60–90%); keep-out written as a square box instead of the annulus 100<√(x²+y²)<350; η_at coeff 1.79e-8 (eq 2.4) vs 1.97e-8 (eq 2.2); "67178 MW" in Table 4 is really kW (≈67 MW → overshoots 60 MW rating).

## Files (project / outputs)
- `A题.pdf` → original problem (was actually a zip). English translation: **`ProblemA_EN.pdf`**.
- English translations: **`Paper1_Li_EN.docx`**, **`Paper2_Jia_EN.docx`**.
- Data: `附件.xlsx` (1745 mirror x,y positions). Templates: `result2.xlsx`, `result3.xlsx` (8 cols: tower x,y / mirror# / width / height / x,y,z).

## Next steps
- [ ] **Exam 2 — optimization side:** objective (per-unit-area), decision variables, constraint set (keep-out annulus, spacing rule, size/height bounds), search strategy for Q2 & Q3.
- [ ] Build Q1 simulation: solar geometry over 60 sun positions → DNI, cosine, shadow/block (ray test), atmospheric → field totals. Validate against ~35 MW.
- [ ] Q2: sweep ring spacing / mirror size; Campo concentric-ring layout.
- [ ] Q3: zone the field; vary size + height per zone (inner→outer height gradient).
- [ ] Research-grade extensions: global MPPT-style search, PSO / NN optimizers, partial-shading robustness.

## Related notes
- [[LHU_Project_Notes_2026-06-16]] — the chosen MPPT internship project; this heliostat problem is its **seed** (the "CSP is niche → go solar PV + MPPT" reasoning started here).
- [[taiwan-internship]] — internship hub (advisor + project tracking).
- [[prof-ting-chung-yu]] — Prof. Yu (solar / MPPT): the advisor lane closest to this CSP/optimization work.
- [[bms-project-context]] — my embedded + simulation background (the "do it in MATLAB/Python, no hardware" angle).
