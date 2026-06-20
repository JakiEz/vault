---
type: study-log
description: Learning progress on the heliostat Python model — running log of what I understood and where to resume. Currently on Step 1 (solar geometry).
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
1. **Solar geometry** → sun direction + DNI for 60 timestamps ← *I am here*
2. Easy losses (cosine, atmospheric, reflectivity) — per-mirror formulas
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

## Next
- [ ] Combine δ + ω + φ → altitude on one worked example (**Jun 21, 9:00**: δ=+23.4°, ω=−0.79) and confirm it's a sensible height.
- [ ] Turn altitude → **DNI** via `DNI = G₀[a + b·exp(−c/sin α)]`, G₀=1.366, H=3 km.
- [ ] Then build the robust sun **unit vector** (use the δ/ω decomposition to dodge the azimuth AM/PM sign trap — see [[Heliostat_Field_Notes]]).
