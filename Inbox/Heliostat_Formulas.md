---
type: reference
description: The complete Q1 heliostat method — every step with its formula and source tag ([Problem doc] vs [standard]), from date/time to field power. The one-page derivation companion to the code map and study log.
created: 2026-06-28
updated: 2026-06-28
related: [[Heliostat_CodeMap]], [[Heliostat_StudyLog]], [[Heliostat_Field_Notes]]
---

# Heliostat Q1 — All Steps & Formulas

> Every formula in the model, in order, with what each symbol means. Tags: **[Problem doc]** = from `ProblemHeliostat.pdf` Appendix; **[standard]** = general math/geometry, not in the doc. Angles are in **radians** in code.

## Constants (site & field) — [Problem doc]
| Symbol | Value | Meaning |
|---|---|---|
| φ | 39.4° N | latitude |
| H | 3 km | altitude (used in DNI a,b,c) |
| G₀ | 1.366 kW/m² | solar constant |
| — | receiver at (0, 0, 80) | tower at field center, receiver 80 m up |
| — | install height 4 m → gap **76 m** | mirror center to receiver center: 80 − 4 |
| — | mirror 6×6 m → A = 36 m², half = 3 m | Q1 all mirrors identical |
| ρ (η_ref) | 0.92 | mirror reflectivity |
| — | 21st of each month × {9:00, 10:30, 12:00, 13:30, 15:00} = **60** | sampling for annual averages |

---

## Step 1 — Solar geometry (once per timestamp → ŝ + DNI)

**Days from spring equinox** (Mar 21 = 0; Jan/Feb negative) — [Problem doc]
$$D = \text{day-of-year} - 80$$

**Declination δ** (the season) — [Problem doc]
$$\sin\delta = \sin\!\Big(\tfrac{2\pi D}{365}\Big)\cdot\sin\!\Big(\tfrac{2\pi\cdot 23.45}{360}\Big), \qquad \delta = \arcsin(\sin\delta)$$

**Hour angle ω** (time of day) — [Problem doc]
$$\omega = \tfrac{\pi}{12}\,(ST - 12)\quad(\text{ST = local solar time, hours})$$

**Altitude α** (how high the sun is) — [Problem doc]
$$\sin\alpha = \cos\delta\,\cos\varphi\,\cos\omega + \sin\delta\,\sin\varphi, \qquad \cos\alpha = \sqrt{1-\sin^2\alpha}\ \text{[standard]}$$

**Azimuth A** (compass direction) — [Problem doc] + [standard]
$$\cos\gamma = \frac{\sin\delta - \sin\alpha\,\sin\varphi}{\cos\alpha\,\cos\varphi}$$
$$A = \arccos\big(\text{clamp}(\cos\gamma,\,-1,\,1)\big);\quad \text{if } \omega > 0:\ A = 2\pi - A$$
(measured from north; the `clamp` avoids an acos domain crash at noon; the ω-sign fix picks east vs west.)

**Sun unit vector ŝ** (East, North, Up) — [standard]
$$s_x = \cos\alpha\,\sin A,\qquad s_y = \cos\alpha\,\cos A,\qquad s_z = \sin\alpha$$

**DNI** (sunlight strength, kW/m²) — [Problem doc]
$$\text{DNI} = G_0\big[a + b\,e^{-c/\sin\alpha}\big]$$
$$a = 0.4237 - 0.00821(6-H)^2,\quad b = 0.5055 + 0.00595(6.5-H)^2,\quad c = 0.2711 + 0.01858(2.5-H)^2$$

---

## Step 2 — Per-mirror easy efficiencies

**Mirror → receiver direction & distance** — [standard] + [Problem doc] geometry
$$\vec t = (0,0,80) - (x,y,4) = (-x,\,-y,\,76),\qquad d_{HR} = \sqrt{x^2+y^2+76^2},\qquad \hat t = \vec t / d_{HR}$$

**Cosine efficiency η_cos** (half-angle) — [standard]
$$\hat s\cdot\hat t = s_x\hat t_x + s_y\hat t_y + s_z\hat t_z, \qquad \eta_{cos} = \sqrt{\tfrac{1 + \hat s\cdot\hat t}{2}}$$

**Atmospheric transmittance η_at** — [Problem doc]
$$\eta_{at} = 0.99321 - 0.0001176\,d_{HR} + 1.97\times10^{-8}\,d_{HR}^2$$

**Reflectivity η_ref** — [Problem doc]
$$\eta_{ref} = 0.92$$

---

## Step 3 — Optical efficiency & field power — [Problem doc]
$$\eta_i = \eta_{cos}\cdot\eta_{sb}\cdot\eta_{at}\cdot\eta_{trunc}\cdot\eta_{ref}$$
$$E_{field} = \text{DNI}\cdot\sum_{i=1}^{N} A_i\,\eta_i \quad (\text{kW},\ A_i = 36\ \text{m}^2)$$

---

## Step 4 — Shadow & blocking η_sb — [standard] (all)

**Mirror as a tilted rectangle (frame)** — `ẑ = (0,0,1)`
$$\hat n = \frac{\hat s + \hat t}{|\hat s + \hat t|}\ (\text{normal, reflection law}),\quad \hat u = \frac{\hat n\times\hat z}{|\hat n\times\hat z|}\ (\text{width, horizontal}),\quad \hat v = \hat n\times\hat u\ (\text{height})$$
$$\text{corners} = C \pm 3\hat u \pm 3\hat v,\qquad C=(x,y,4)$$

**Ray → plane intersection** (ray from P along d hits the neighbor's plane)
$$s = \frac{(C - P)\cdot\hat n}{d\cdot\hat n}\qquad
\begin{cases}|d\cdot\hat n|\approx 0 & \Rightarrow \text{parallel, miss}\\ s\le 0 & \Rightarrow \text{behind, miss}\end{cases}\qquad X = P + s\,d$$

**In-rectangle test** (is the hit inside the neighbor's 6×6?)
$$\vec w = X - C,\quad a = \vec w\cdot\hat u,\quad b = \vec w\cdot\hat v,\qquad \text{inside} \iff |a|\le 3\ \text{and}\ |b|\le 3$$

**η_sb (sampling)**
- 5×5 grid of points P across mirror i's surface
- from each P cast a ray toward the **sun** (ŝ, shadow) and toward the **receiver** (t̂, block)
- if either ray hits **any nearby neighbor's** rectangle → that point is lost
$$\eta_{sb} = \frac{\text{clear points}}{\text{total points}}$$
- **neighbors** precomputed once: mirrors within **R = 25 m** (avoid all-pairs)

---

## Step 5 — Truncation η_trunc — [TODO, currently = 1]
Reflected beam is a **cone** (sun angular width ~9.3 mrad + mirror slope error) → the spot at the tower is bigger than the 7 m × 8 m receiver, so the edges spill off.
$$\eta_{trunc} = \frac{\text{energy on the receiver}}{\text{total reflected energy}}\quad\text{[Problem doc, definition only]}$$
Method to choose: **HFLCAL** (spot as a 2D Gaussian, integrate over aperture — fast) vs **Monte-Carlo ray trace** (accurate). Expect it to take 37.2 → **~35 MW**.

---

## Step 6 — Aggregation & tables — [Problem doc]
$$E_{field}\,[\text{MW}] = \frac{\text{field power [kW]}}{1000},\qquad \text{per-unit-area}\,[\text{kW/m}^2] = \frac{E_{field}[\text{kW}]}{N\cdot 36}$$
- **Table 1:** average the 5 daily times → per-month values
- **Table 2:** average all 60 → annual values
- Shortcut (equal-size mirrors): per-unit-area $= \text{DNI}\cdot\overline{\eta}$ — [standard]

---

## Current status
✅ Steps 1–4 (η_trunc = 1) → annual **37.245 MW**, **0.593 kW/m²**. 🔜 Step 5 truncation → ~35 MW.
Companion notes: [[Heliostat_CodeMap]] (functions), [[Heliostat_StudyLog]] (journey + bugs), [[Heliostat_Field_Notes]] (problem/physics).
