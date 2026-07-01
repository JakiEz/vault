---
type: reference
description: Physics→code walkthrough of the Q1 heliostat model, step by step — how each formula becomes a line, the "how often does it run?" loop placement, and the classic traps. Learning companion to the CodeMap (what) and Formulas (derivation).
created: 2026-07-02
updated: 2026-07-02
related: [[Heliostat_CodeMap]], [[Heliostat_Formulas]], [[Heliostat_StudyLog]], [[Heliostat_Field_Notes]]
---

# Heliostat Q1 — Physics→Code Walkthrough

> How to *read the code as you'd write it*: for every step, physics first, then the line that expresses it. Companion to [[Heliostat_CodeMap]] (function map) and [[Heliostat_Formulas]] (derivations). Source tags: **[Problem doc]** = in `ProblemHeliostat.pdf`; **[standard]** = general math/optics, not in the doc; **[assumed]** = a parameter we chose.

## The method — 4 questions for turning physics into code
Ask these, in order, for every formula:
1. **Inputs → output?** A formula is just `output = f(inputs)`.
2. **How often does it run?** once (constant, top of file) · once per timestamp (the sun) · once per mirror (efficiencies). This decides *which loop the line lives in*. Hoist anything that doesn't depend on the loop variable *out* of the loop.
3. **Exact formula + unit/type of each symbol?** degrees vs radians; an angle vs the *sine* of an angle. ~90% of bugs live here.
4. **Translate operators:** `·` → multiply-add · `×` → cross-product expansion · `|v|` → `sqrt(x²+y²+z²)` · `normalize` → divide by length.

---

## Step 1 — Where is the sun? (`heliostat_step1.py`)
Goal: **date + time → DNI** (sunlight strength). A chain of small conversions:
`date → δ` and `time → ω`, then `(δ, ω, φ) → altitude α → DNI`.

| Link | Line | Note |
|---|---|---|
| constants `a,b,c`, `latitude` | top of file | depend only on `H`/site → compute **once**. `math.radians(39.4)` up front (**trap: radians not degrees**). |
| hour angle | `ω = (π/12)(ST−12)` | direct; 15°/hour past noon. |
| declination | `sin δ = sin(2πD/365)·sin(23.45°)`, then `asin` | formula gives **sin δ, not δ** → `asin` to recover the angle for the next `cos`. Name it `sin_dec` so you can't misuse it. |
| altitude | `sin α = cosδ cosφ cosω + sinδ sinφ` | output is **sin α, not α**. Three inputs each appear once (season, time, place). |
| DNI | `G₀[a + b·exp(−c/sin α)]` | input is **sin α** (don't `sin()` it again). **Minus sign** = atmospheric survival (high sun → stronger). |

**Traps (all "value-vs-angle"/sign):** radians not degrees · `sin δ` ≠ `δ` · keep the `−` in the DNI exponent · don't take `sin()` of an already-sined value.

---

## Step 2 — How well does each mirror aim? (`heliostat_step2.py`)
Adds a **second (per-mirror) loop** and turns the sun into a **3D vector**. Losses: cosine, atmospheric, reflectivity.

**Setup A — azimuth** (`cos γ = (sinδ − sinα sinφ)/(cosα cosφ)`):
- `cos α = cos(arcsin(sin α))` — recover cos α from sin α without recomputing α.
- **clamp before `acos`** (`max(-1,min(1,·))`) — float noise gives −1.00007 at noon → domain crash otherwise.
- **sign fix** `A = γ0 if ω≤0 else 2π−γ0` — `acos` loses AM/PM (cos is symmetric); recover it from the hour-angle sign, else the afternoon sun mirrors to the east.

**Setup B — sun vector** `ŝ = (cosα·sinA, cosα·cosA, sinα)` = (East, North, Up). Why: comparing *directions* is one dot product with vectors, painful with angles. `ŝ` is the **same for every mirror** (rays parallel) → compute **once per timestamp**, in the outer loop.

**Cosine efficiency (the clever one):**
- `t̂ = normalize(−x, −y, 76)` — mirror→receiver (the `76` is the *gap* 80−4, not the mirror's z).
- `ŝ·t̂ = cos(full angle sun↔receiver)` (both unit vectors).
- η_cos needs the **half**-angle → identity `cos(Ψ/2) = √((1+cosΨ)/2)` → `sqrt((1+dot)/2)`. No `acos`, no crash.

**Atmospheric** `η_at = 0.99321 − 0.0001176·d_HR + 1.97e-8·d_HR²` (leading const **0.99321** — a `0.00321` typo makes it negative). **Reflectivity** `rho = 0.92`, a top-of-file constant.

**Loop shape (now 2-deep):** sun `ŝ`, DNI → per timestamp (middle). Efficiencies → per mirror (inner). `field_power += DNI·area·η` (the `+=` *is* the `Σ` in `E = DNI·ΣAᵢηᵢ`). Stub `η_sb = η_trunc = 1.0` to prove the pipeline runs (inflated ~41 MW) before adding the hard parts.

### ⚠️ Where does η_cos come from? (source audit)
The problem doc Appendix §4 gives the **skeleton** `η = η_sb·η_cos·η_at·η_trunc·η_ref` but for η_cos only says **"η_cos = 1 − (cosine loss)"** — a *definition, not a formula*. Explicit formulas are given **only** for η_at and η_ref. So `√((1+ŝ·t̂)/2)` is **[standard]**, supplied by us via: (1) η_cos = cos(incidence angle) [optics]; (2) reflection law → normal bisects sun↔receiver, so incidence = ½·(angle between ŝ and t̂); (3) half-angle identity on `ŝ·t̂`.
- **Paper 1's error** (flagged in [[Heliostat_Field_Notes]]): misread the wording as η_cos = 1 − cos θ (**inverted**). Correct reading: cosine *loss* = 1 − cos θ, so η_cos = **cos θ**. Our code is right.

---

## Step 4 — Do neighbors block the light? (`heliostat_step4.py`)
Problem gives only **"η_sb = 1 − (shadow-blocking loss)"** — no formula. All **[standard]** geometry.
- **Shadow** = neighbor between mirror and *sun* (ŝ). **Blocking** = neighbor between mirror and *receiver* (t̂). Same test, two ray directions.
- **Strategy:** exact geometry is a nightmare → **sample the surface + cast rays**. 5×5 grid on the mirror; from each point shoot toward sun & receiver; η_sb = clear points / total.

**Primitive A — `mirror_frame` (mirror as a tilted rectangle):** `C`(center), `n`(normal), `u,v`(surface axes). Corners = `C ± 3u ± 3v`.
- `n = normalize(ŝ + t̂)` — reflection law. **`t̂` is used HERE, to build n, then set aside.**
- `u = normalize(n × ẑ)` — width axis. **Cross with the NORMAL to stay in the plane** (anything × n ⟂ n → lies in the mirror). Crossing with **ẑ (up)** specifically forces `u` **horizontal** → matches "top/bottom edges parallel to the ground."
- `v = n × u` — height axis (already unit; n⟂u).
- **Confusion resolved:** `[0,0,1]` is a *direction* (sets the roll → keep width horizontal); the `3` is a *length* (sizes the panel, used later in `C ± 3u`). Direction first, distance second. `t̂` is **not** in the plane, so you can't cross with it to get in-plane axes. Order: `n` (t̂ used here) → `u = n×ẑ` → `v = n×u`.

**Primitive B — `ray_hits_rect`:** ray→plane intersect `s = (C−P)·n / (d·n)` (guards: `|d·n|≈0` parallel-miss; `s≤0` behind-miss), then in-rectangle test by projecting `w = X−C` onto `u,v` and checking `≤ 3`. **Test in isolation first** (flat square → True/False/False).

**Primitive C — `shadow_block_eff`:** loop the 5×5 grid `P = C + du·u + dv·v`; for each, `or` of ray-toward-sun / ray-toward-receiver over `neighbors[i]`; `break` on first blocker; return `clear/total`.

**Optimization — `neighbors` precomputed ONCE:** only mirrors within **R=25 m** can block. Depends only on positions (not sun) → build before the loops. Compare **squared** distance (`≤ R*R`) to skip sqrt.

**Loop change:** `frames` rebuilt **every timestamp** (tilt depends on sun) but once per timestamp via a comprehension (bug: reassigning `frames=[f]` gives a 1-element list). `neighbors` built once, ever. Result: 41 → **37.2 MW** (~9% loss, η_sb≈0.91).

---

## Step 5 — Does the beam spill off the receiver? (`heliostat_step5_numba.py`)
Problem gives only the **definition** `η_trunc = (energy on receiver)/(total reflected − shadow loss)`. **[standard]** physics + **[assumed]** beam width.
- **Physics:** beam is a **cone** (sun is a disk ~4.65 mrad + mirror slope error), and flat mirrors **don't focus** → spot ≈ 6 m footprint + blur on a 7×8 m receiver → edges spill.
- **Strategy:** **Monte-Carlo** — fire `N=200` random rays/mirror; each starts at a random point on the mirror, aims at the receiver with a random wobble; trace to the receiver cylinder; **η_trunc = hits/N.** (Chosen over analytic HFLCAL: honest + reused later. Random → result **wiggles** run-to-run; raise N to smooth.)

**Beam width** `σ_beam = √(σ_sun² + (2·σ_slope)²)` — independent spreads **add in quadrature**; `2×` slope because a surface tilt θ deflects the ray by 2θ. `σ_sun≈2.51 mrad` [standard]; **`σ_slope`≈1–2 mrad [assumed] = the tunable knob** (2→1 mrad moves 31.2→33.4 MW; report as a range).

**Perpendicular basis** `e1 = t̂×ẑ`, `e2 = t̂×e1` — two directions ⟂ to the aim to nudge along (hand-expanded cross products; Numba has no `np.cross`).

**Per-ray:** random start `P = C + r1·u + r2·v`, `r1,r2 ~ U(−3,3)` (**uniform** over the flat face); wobble `r = t̂ + θ1·e1 + θ2·e2`, `θ ~ N(0, σ_beam)` (**Gaussian** — most rays near-on-target), then **renormalize** r. Distribution choice = the modeling judgment.

**New primitive — `hit_cyl` (ray→cylinder):** receiver at origin, `Rc=3.5`, `z∈[76,84]`. Side is `x²+y²=Rc²` → quadratic `A s²+Bs+C=0` (`A=rx²+ry²`, `B=2(Px rx+Py ry)`, `C=Px²+Py²−Rc²`). `disc<0` miss; take nearer root `s=(−B−√disc)/2A`; guard `s≤0`; then confirm `76 ≤ Pz+s·rz ≤ 84` (quadratic only hits the *infinite* cylinder). Test alone first (True/False/False).

Result: 37.2 → **33.4 MW** (~10% loss, σ_slope 1 mrad) ≈ Paper 2's 34.8. **Q1 complete.** MC noise is expected, not a bug (validate deterministic no-trunc number 37.246 vs 37.245 before trusting the random part).

---

## Meta-lessons (transferable)
- A physics model = a **chain of conversions**; place each line at the **right loop depth** and **track what each variable physically is** (angle? sine? radians?).
- **Convert angles → unit vectors** so "compare directions" = one dot product; use **trig identities** to dodge `acos`.
- **Cross with the normal** to get in-plane axes; **normalize** for true rulers.
- When exact geometry is too hard: **sample** (deterministic grid) or **Monte-Carlo** (random) and count successes; match each random distribution to the physics.
- **Test every geometry primitive in isolation** before wiring it into thousands of mirrors.
- The problem hands you the **skeleton + a few formulas**; the loss *models* (η_cos, η_sb, η_trunc) are yours to supply — tag every formula **[Problem doc] / [standard] / [assumed]** and never fabricate a citation.
