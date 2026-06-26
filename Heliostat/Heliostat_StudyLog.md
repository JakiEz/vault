---
type: study-log
description: Learning progress on the heliostat Python model — running log of what I understood and where to resume. Step 1 (solar geometry) DONE; now on Step 2 (per-mirror efficiencies).
created: 2026-06-21
updated: 2026-06-21
related: [[Heliostat_Field_Notes]]
---

# Heliostat Model — Study Log

> Running log of building the Q1 Python model myself, concept-first. Companion to [[Heliostat_Field_Notes]] (the physics reference). Resume from the **Next** line at the bottom.

## The whole model in one line
Build **one function** `field_performance(layout) -> efficiency, power`. Q1 = call it once. Q2/Q3 = call it many times inside an optimizer. So all effort goes into Q1.

Power chain: `sun position → DNI (light strength) × 5 efficiency losses × mirror area = power on receiver`. Do it for 60 sun snapshots, average → annual answer.

## Build order (do not skip ahead)
1. **Solar geometry** → sun direction + DNI for 60 timestamps ✅ **done 2026-06-21**
2. Easy losses (cosine, atmospheric, reflectivity) — per-mirror formulas ← *I am here*
3. Aggregate with η_sb = η_trunc = 1 → inflated number (proves plumbing)
4. Shadow & blocking (η_sb) — ray-casting vs neighbors
5. Truncation (η_trunc) — beam is a cone, spills off receiver
6. Validate against **~35 MW** (Paper 2, the trustworthy one)
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
Built the full sun model end-to-end: date+time → declination → hour angle → altitude → DNI for all 60 timestamps. Working script saved at `Heliostat/heliostat_step1.py`.

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

## Next — Step 2: per-mirror efficiencies
- [ ] **New ingredient first:** build the sun **3D unit vector** — `s_x = −cosδ·sinω`, `s_y = sinδ·cosφ − cosδ·sinφ·cosω`, `s_z = sinα`. Needed for cosine; also dodges the azimuth AM/PM sign trap (see [[Heliostat_Field_Notes]]).
- [ ] Load the **1745 mirror positions** from `附件.xlsx` (x, y; z = install height = 4 m for Q1).
- [ ] **Cosine** `η_cos = sqrt((1 + s·t)/2)`, where `t = unit(receiver_center − mirror)`, receiver at (0,0,80).
- [ ] **Atmospheric** `η_at(d_HR)` and **reflectivity** 0.92 (constant).
- [ ] Aggregate with `η_sb = η_trunc = 1` → a deliberately-too-high power number → proves the plumbing before the hard losses.
