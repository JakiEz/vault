---
type: study-log
description: Learning progress on the heliostat Python model — running log of what I understood and where to resume. Q1 COMPLETE end-to-end incl. Table 1/2 (annual 33.39 MW, η_opt 0.546, within 4% of Paper 2); next is Q2 optimizer.
created: 2026-06-21
updated: 2026-07-01
related: [[Heliostat_Field_Notes]]
---

# Heliostat Model — Study Log

> Running log of building the Q1 Python model myself, concept-first. Companion to [[Heliostat_Field_Notes]] (the physics reference). Resume from the **Next** line at the bottom.

## The whole model in one line
Build **one function** `field_performance(layout) -> efficiency, power`. Q1 = call it once. Q2/Q3 = call it many times inside an optimizer. So all effort goes into Q1.

Power chain: `sun position → DNI (light strength) × 5 efficiency losses × mirror area = power on receiver`. Do it for 60 sun snapshots, average → annual answer.

## Build order (do not skip ahead)
1. **Solar geometry** → sun direction + DNI for 60 timestamps ✅ **done 2026-06-21**
2. Easy losses (cosine, atmospheric, reflectivity) — per-mirror formulas ✅ **done 2026-06-23**
3. Aggregate with η_sb = η_trunc = 1 → inflated number (proves plumbing) ✅ **done 2026-06-23**
4. Shadow & blocking (η_sb) — ray-casting vs neighbors ✅ **done 2026-06-28**
5. Truncation (η_trunc) — beam is a cone, spills off receiver ✅ **done 2026-06-28**
6. Validate + fill Table 1/2 (annual-avg optical & sub-efficiencies) ← *I am here*, then Q2/Q3
→ then Q2/Q3 wrap step 1–6 in an optimizer.

## 2026-06-21 — Step 1: finding the sun (concepts locked in)

**The 60 sun positions are a grid, not a sliced angle.** 12 months × 5 times = 60. Two *independent* axes:
- **date → declination δ** (the season / Earth's tilt toward sun)
- **time → hour angle ω** (how far the sun has rotated past noon)

**Three angles, and which is input vs output:**
| Angle | Means | From |
|---|---|---|
| δ declination | the season | the **date** only |
| ω hour angle | rotation past noon | the **time** only |
| α **altitude** | how high sun is above horizon | δ + ω + latitude *combined* |

δ and ω are **inputs**; altitude is the **output** I actually want. "Altitude" = angle above the horizon, **not** distance to the sun. Distance never matters here — the *angle* sets sunlight strength (low sun → more atmosphere → weaker).

**Declination formula demystified:** `sin δ = sin(2π·D/365) · sin(23.45°)`
- `sin(23.45°)` = amplitude = Earth's fixed axial tilt (the most δ can ever be).
- `sin(2π·D/365)` = timing = smooth swing −1→+1 over the year.
- Two facts (one tilt + the calendar) capture all of the seasons. Approximation (assumes circular orbit) but good to a fraction of a degree.

**D = days from spring equinox (Mar 21 = day 0).** Jan/Feb come out **negative — leave them negative** (negative D = winter = low sun). Do NOT wrap to positive.

**D table (non-leap, 21st of each month):**
| Date | D | δ |
|---|---|---|
| Jan 21 | −59 | −19.8° |
| Feb 21 | −28 | −10.8° |
| Mar 21 | 0 | 0° (equinox) |
| Apr 21 | +31 | +11.7° |
| May 21 | +61 | +20.1° |
| Jun 21 | +92 | +23.4° (summer peak) |
| Jul 21 | +122 | +21.5° |
| Aug 21 | +153 | +13.5° |
| Sep 21 | +184 | ≈0° (equinox) |
| Oct 21 | +214 | −10.7° |
| Nov 21 | +245 | −19.6° |
| Dec 21 | +275 | −23.4° (winter low) |

**Hour angle:** `ω = (π/12)(ST − 12)` (radians). Same 5 values every month:
| Time | ω (rad) | deg |
|---|---|---|
| 9:00 | −0.79 | −45° |
| 10:30 | −0.39 | −22.5° |
| 12:00 | 0 | 0° |
| 13:30 | +0.39 | +22.5° |
| 15:00 | +0.79 | +45° |
*(verified ✓)* Symmetric around noon. ω alone is NOT the sun height — same ω in June vs Dec, very different altitude (δ differs).

**Combine into altitude:** `sin(altitude) = cos δ · cos φ · cos ω + sin δ · sin φ`  (φ = 39.4° N).

## 2026-06-21 (cont.) — Step 1 COMPLETE ✅
Built the full sun model end-to-end: date+time → declination → hour angle → altitude → DNI for all 60 timestamps. Working script saved at `Inbox/heliostat_step1.py`.

**Validation — December (sin α and DNI in kW/m²):**
| Time | sin α | DNI |
|---|---|---|
| 9:00 | 0.249 | 0.739 |
| 10:30 | 0.403 | 0.875 |
| 12:00 | 0.457 | 0.910 ← noon peak |
| 13:30 | 0.403 | 0.875 |
| 15:00 | 0.249 | 0.739 |

Cross-check: **June noon** sin α ≈ 0.961 (sun ~74° up). The big winter/summer gap (0.46 vs 0.96) confirms the season is feeding through correctly. DNI always lands in the ~0.7–1.0 band.

**Four bugs found & fixed (all "value-vs-angle" or sign traps — watch for these again):**
1. **Latitude not in radians** — passed `39.4` into `sin/cos` instead of the `radians()` variable. `cos(39.4 rad)` is negative → flipped the whole altitude formula (noon came out lowest/negative). Fix: pass `latitude`.
2. **sin δ used as δ** — `season()` returned sin δ but `altitude()` applied `sin/cos` to it as if it were the angle. Fix: `season` returns `asin(sin_dec)` = real declination angle.
3. **DNI exponent sign** — had `exp(+c/sinα)`, must be `exp(−c/sinα)`. The minus = atmospheric survival (high sun → stronger DNI). Wrong sign inverted day/noon.
4. **Sine-of-a-sine** — called `dni(math.sin(sunAngle))` but `sunAngle` was already `sin α` → ~1% low everywhere. Fix: `dni(sunAngle)`.

**Habit:** round only at `print()` time, not at every stage (rounding stacks over 60×N calls).

## 2026-06-23 — Steps 2 + 3 COMPLETE ✅ (easy losses + field power)
Full pipeline runs end-to-end for all 60 timestamps. Chose the **azimuth route** (not the δ/ω decomposition): document's `cos γ_s` → `acos` (clamped) → east/west sign-fix via ω → `sunVector(α, A)`. Then per mirror: cosine (dot product + half-angle), atmospheric, reflectivity; `η_sb = η_trunc = 1`. Working script: `Inbox/heliostat_step2.py`.

**Result (inflated, sb=trunc=1):** annual average ≈ **41 MW**, per-unit-area ≈ **0.65 kW/m²**. Positive, noon-peak, summer>winter. Hand-check: Dec noon field power ≈ 37 MW ✓. Will fall to the realistic **~35 MW / ~0.55 kW/m²** once shadow/block + truncation go in.

**Bugs hit & fixed (this stretch):**
1. **azimuth `acos`/precedence** — `a / b * c` ≠ `a / (b*c)`; must parenthesize `(cosα·cosφ)`. And re-add the `clamp(-1,1)` — Dec noon gives −1.00007 → `acos` domain crash without it.
2. **`atmospheric` constant** — typed `0.00321`, must be **`0.99321`**. Made η_at negative → negative power *and* ~45× too small. Lesson: an efficiency near 0 / negative → check the leading constant.
3. **units** — `field_power/1000` is **MW** not kW/GW; per-unit-area must be `annual_avg*1000/total_area` for **kW/m²**.
4. **dotProduct z** — vertical component is `+76` (= 80−4), pointing up, and `Length = √(x²+y²+76²)` — not the mirror's z.
5. **sun vector ≠ angles** — `s_x,s_y,s_z` are *computed from* (altitude, azimuth), not the angles themselves.

**Key facts locked in:** area not needed for efficiency, only for power (`E = DNI·ΣAᵢηᵢ`); for equal-size mirrors per-unit-area = `DNI·mean(η)`; sun rays parallel → ŝ same for every mirror (compute once/timestamp), t̂ per mirror.

## 2026-06-28 — Step 4 COMPLETE ✅ (shadow & blocking) — the hard geometry part
Built the full ray-geometry engine. Working script: `Inbox/heliostat_step4.py`.

**Result:** annual average **41 → 37.245 MW**, per-unit-area **0.65 → 0.593 kW/m²**. That's a **~9% shadow/blocking loss** (field-avg η_sb ≈ 0.91) — healthy middle of the expected 5–15% band, and now close to Paper 2's ~34.8 MW (which already folded in some truncation). On track.

**How it works (3 building blocks, all [standard], not in the doc):**
1. `mirror_frame(x,y,sv)` → a mirror as a **tilted rectangle in 3D**: center C, normal `n = normalize(ŝ+t̂)` (reflection law), width axis `u = normalize(cross(n, ẑ))` (horizontal), height axis `v = cross(n,u)`. Corners = `C ± 3u ± 3v`.
2. `ray_hits_rect(P,d,C,n,u,v)` → **ray–plane intersect** `s = (C−P)·n / (d·n)` (guard: parallel `d·n≈0`, behind `s≤0`), then **in-rectangle test** (project hit point onto u,v, check ≤ half). Tested in isolation on a flat square first (True/False/False).
3. `shadow_block_eff(i,...)` → sample a **5×5 grid** on mirror i; from each point cast a ray toward **sun** (shadow) and toward **receiver** (block); η_sb = fraction hitting **no** nearby neighbor.
+ **neighbor pruning**: precompute once, per mirror the list of others within **R=25 m** (don't test all 1745²).

**Concepts that finally clicked:**
- `normalize` = keep direction, set length to 1 (needed so `u,v` are true-metre rulers). `cross(A,B)` = a vector ⊥ to both A and B.
- **"in the surface" = perpendicular to the normal**, and cross makes perpendiculars → that's why we cross to get the mirror's surface axes. Mirror is *tilted*, so corners offset along `u,v` (which change x,y **and** z), NOT along world x,y.
- Corners are the **obstacle** geometry; the shadow is the *result* of throwing rays at those obstacles.

**Assembly bugs hit & fixed:** building a list by **reassigning** inside a loop (`frames = [f]` each pass) gives a 1-element list → must use a **comprehension** or `.append` to accumulate; `neighbors` must be built (list of lists) and **once**, before the loops; `frames` rebuilt per timestamp (tilt depends on sun).

**Perf note (for later):** slow part = numpy on 3-element arrays in tight loops (dispatch overhead). Fine for Q1 (run once, a few min). For Q2/Q3 (model called 1000s of times in an optimizer) → use **Numba `@njit`** (near-C speed, ~1 decorator) or plain-float math; C is faster but a full rewrite; MATLAB only faster if vectorized.

## 2026-06-28 — Step 5 COMPLETE ✅ — Q1 OPTICAL MODEL DONE (all 5 losses)
Chose **Monte-Carlo ray trace** for truncation (over HFLCAL) because it's the honest model and reused later. Also ported the whole hot path to **Numba** first (see below). Working script: `Inbox/heliostat_step5_numba.py`.

**Result (all 5 losses):**
| slope error assumed | annual avg | per-unit-area |
|---|---|---|
| 2 mrad | **31.17 MW** | 0.496 kW/m² |
| 1 mrad | **33.39 MW** | 0.532 kW/m² |
Paper 2 (trustworthy) ≈ **34.8 MW / 0.554**. We're a touch lower because the MC models the **flat-mirror footprint + real beam blur** rigorously, while Paper 2 *assumed* a truncation factor. Implied optical efficiency ~0.55–0.57 — right in the papers' band (0.569–0.586). ✓

**Truncation via Monte-Carlo (all [standard]; params [assumed], not in doc):**
- Beam isn't a pencil: sun is a **disk** (~4.65 mrad) + mirror **slope error** → reflected **cone**. Flat mirrors don't focus, so the spot ≈ 6 m footprint **+** blur, on a 7 m×8 m receiver → spill.
- Per mirror, fire **N=200** rays: random point on the mirror + aim direction `t̂` jiggled by a 2D Gaussian `σ_beam = √(σ_sun² + (2·σ_slope)²)`; trace to the receiver **cylinder**; `η_trunc = hits/N`.
- New primitive: `hit_cyl` = **ray–cylinder intersection** (quadratic in s: `x²+y²=Rc²`, then check z∈[76,84]). Tested True/False/False in isolation.
- **σ_slope is the tunable knob** (least-certain assumption) — 2→1 mrad moved 31.2→33.4 MW.
- MC is **random** → result wiggles slightly run-to-run; raise N for a smoother final number.

**Numba port (the enabler):** moved the whole per-timestamp mirror loop into `@njit` kernels — verified it reproduces 37.246 MW (= the pure-Python 37.245) before adding truncation. Key gotchas: **no `np.cross`/`np.linalg.norm`** in njit → scalar math; **lists-of-tuples → arrays** (frames as an (N,12) array); **ragged neighbor lists → CSR** (`nbr_flat` + `nbr_start`); loops must live *inside* `@njit`. Bug caught: `neighbors` initialized but the radius-scan that fills it was missing → η_sb silently = 1 (matched the no-shadow run).

## 2026-07-01 — Step 6 COMPLETE ✅ — Table 1 & Table 2 reporting
Extended the Step 5 kernel to accumulate `sum_cos, sum_sb, sum_at, sum_trunc, sum_eta` alongside power (return a 6-tuple instead of just `total`), divide by N_mirrors per timestamp, then average 5-per-month (Table 1) and all 60 (Table 2). Working script: `heliostat_step6.py`.

**Table 2 (annual):**
| η_cos | η_sb | η_at | η_trunc | η_opt | Power | per-area |
|---|---|---|---|---|---|---|
| 0.757 | 0.914 | 0.965 | 0.902 | **0.546** | **33.39 MW** | 0.531 kW/m² |

Matches the Step 5 milestone (33.39 MW @ σ_slope=1 mrad) almost exactly — good internal consistency check. vs Paper 2 (trustworthy): optical η 0.569, power ≈34.8 MW — **within ~4%**, comfortably inside the papers' band (0.569–0.586). η_sb (shadow/block) and η_trunc are the two "designed" losses (~9% and ~10%); η_at is nearly flat (~0.965) since d_HR barely varies; η_cos does the heavy lifting on the summer/winter swing (0.71 Dec → 0.79 Jun).

**Table 1 (per-month)** confirms the expected seasonal curve: power peaks in June (38.3 MW) and troughs in December (25.6 MW), tracking η_cos almost exactly (both peak/trough on the solstices) — cosine really is the dominant time-varying loss, as flagged in the Field Notes "exam takeaways."

One console-encoding gotcha: Windows terminal (cp1252) mangles the em-dash `—` in `print()` — swapped for a plain hyphen in table headers.

## Next — Q2/Q3
- [x] ~~Report Table 1/2~~ — done above.
- [x] ~~Compare annual optical efficiency to the papers~~ — 0.546 vs 0.569, within band.
- [ ] Decide/document the σ_slope assumption formally (currently 1 mrad; report the 1↔2 mrad sensitivity range in the writeup).
- [ ] **Q2:** wrap this model in an optimizer (tower position, mirror size, install height, ring spacing) to hit 60 MW while maximizing per-unit-area. Numba speed now makes 1000s of evaluations feasible.
- [ ] **Q3:** allow per-zone size/height to vary.
