---
type: reference
description: Function-by-function map of the Q1 heliostat Python model — what each function does, its source, and how they chain together. Companion to the study log and heliostat_step4.py.
created: 2026-06-28
updated: 2026-06-28
related: [[Heliostat_StudyLog]], [[Heliostat_Field_Notes]]
---

# Heliostat Q1 — Code Map

> Every function in the model grouped by its job, plus the data-flow chain. Source tags: **[Problem doc]** = from `ProblemHeliostat.pdf` Appendix; **[standard]** = general math/geometry, not in the doc. Current script: `heliostat_step4.py` (Steps 1–4; η_trunc still = 1).

## The 4 groups

```
A. WHERE IS THE SUN?            (once per timestamp)  → sun vector ŝ + DNI
B. HOW WELL DOES 1 MIRROR AIM?  (per mirror)          → η_cos, η_at
C. DO NEIGHBORS BLOCK IT?       (per mirror)          → η_sb
D. PUT IT TOGETHER              (main loop)           → field power
```

## Group A — Where is the sun? (solar geometry)
Run **once per timestamp**; ŝ is the same for every mirror (sun rays are parallel).

| Function | In → Out | What it does | Source |
|---|---|---|---|
| `hourAngleF(time)` | clock time → **ω** | how far the sun rotated past noon | [Problem doc] |
| `declination(monthDist)` | days-from-equinox → **δ** | the season (sun's daily height) | [Problem doc] |
| `altitudeAngle(ω, δ, φ)` | → **sin α** | how high the sun is | [Problem doc] |
| `asimuth(sin α, ω, δ, φ)` | → **A** | which compass direction (radians) | [Problem doc] + [standard] acos/clamp/sign-fix |
| `dni(sin α)` | → **DNI** | sunlight strength (kW/m²) | [Problem doc] |
| `sunVector(sin α, A)` | 2 angles → **ŝ = (s_x,s_y,s_z)** | packs altitude+azimuth into a 3D unit vector | [standard] |

## Group B — How well does one mirror aim? (easy losses)
Per mirror.

| Function | In → Out | What it does | Source |
|---|---|---|---|
| `dotProduct(ŝ, x, y, z)` | → **ŝ·t̂** | builds t̂ (mirror→receiver, normalized) and dots it with ŝ | [standard] |
| `cosineEfficiency(dot)` | → **η_cos** | `√((1+dot)/2)` — tilt loss (half-angle) | [standard] |
| `atmospheric(d_HR)` | distance → **η_at** | air absorption over the trip to the tower | [Problem doc] |
| *(constant `rho = 0.92`)* | → **η_ref** | mirror reflectivity | [Problem doc] |

## Group C — Do neighbors block it? (shadow & blocking)
The geometry engine. Per mirror.

| Function | In → Out | What it does | Source |
|---|---|---|---|
| `mirror_frame(x, y, ŝ)` | → **(C, n, u, v)** | the mirror as a **tilted rectangle** (center, normal, 2 surface rulers) | [standard] |
| `ray_hits_rect(P, d, C,n,u,v)` | → **True/False** | does a ray from P along d pass through that rectangle? (plane-intersect + in-bounds) | [standard] |
| `shadow_block_eff(i, ŝ, frames, neighbors)` | → **η_sb** | 5×5 points on mirror i; cast rays toward sun (shadow) + receiver (block); fraction that hit **no** neighbor | [standard] |
| *(precomputed `neighbors`)* | → list of lists | mirrors within R=25 m of each mirror (avoid all-pairs) | [standard] |

## Group D — Put it together (main loop)

```
PRECOMPUTE ONCE:
   neighbors  ← which mirrors are near each mirror (geometry, no sun)

FOR each of 60 timestamps:
   ŝ   = sunVector(...)            # Group A
   DNI = dni(...)                  # Group A
   frames = [mirror_frame(...) for every mirror]   # Group C setup

   field_power = 0
   FOR each mirror i:
       η_cos = cosineEfficiency(dotProduct(ŝ, x,y,height))   # B
       η_at  = atmospheric(d_HR)                             # B
       η_sb  = shadow_block_eff(i, ŝ, frames, neighbors)     # C
       η_trunc = 1.0                                         # (Step 5, todo)
       η = η_cos · η_at · rho · η_sb · η_trunc               # 5 losses multiplied
       field_power += DNI · area · η                         # [Problem doc §3]

   store field_power

annual_avg = mean of the 60          # the answer
per_area   = annual_avg / total_area
```

## Data-flow chain (how outputs feed inputs)

```
 date ─► declination ─► δ ┐
                           ├─► altitudeAngle ─► sin α ─► dni ────────► DNI
 time ─► hourAngleF ──► ω ─┘                   │
                                               └─► asimuth ─► A ─► sunVector ─► ŝ

 per mirror (x, y):
    ŝ, x, y ─► dotProduct ─► cosineEfficiency ─► η_cos ──┐
    x, y ─► d_HR ─► atmospheric ─► η_at ─────────────────┤
    ŝ, frames, neighbors ─► shadow_block_eff ─► η_sb ────┤
                                        rho ─► η_ref ────┤
                                              η_trunc=1 ─┤
                                                         ▼
                          η = η_cos·η_at·η_ref·η_sb·η_trunc ─► field_power += DNI·area·η
```

## One-sentence summary
**Group A** finds the sun (→ ŝ, DNI) once per timestamp; **Group B** computes each mirror's aiming losses (cosine, atmospheric, reflectivity); **Group C** casts rays to find neighbor shadow/blocking (η_sb); **Group D** multiplies the five losses per mirror, weights by `DNI × area`, sums over mirrors, and averages the 60 timestamps.

## Key constants (Q1)
- `latitude φ = 39.4° N`, altitude `H = 3 km`, `G0 = 1.366 kW/m²` [Problem doc]
- receiver center `(0, 0, 80)`; mirror install height `4 m` → vertical gap `height = 76 m` [Problem doc]
- mirror `6×6 m` → `area = 36 m²`, half-side `3 m`; `rho = 0.92` [Problem doc]
- sampling `GRID = 5` (5×5 points), neighbor radius `R = 25 m` [standard, tunable]
