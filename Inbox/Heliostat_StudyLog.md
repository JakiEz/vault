---
type: study-log
description: Learning progress on the heliostat Python model — running log of what I understood and where to resume. Steps 1–3 DONE (solar geometry → easy losses → field power, ≈41 MW inflated); now on Step 4 (shadow & blocking).
created: 2026-06-21
updated: 2026-06-23
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
4. Shadow & blocking (η_sb) — ray-casting vs neighbors ← *I am here*
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

## Next — Step 4: shadow & blocking (η_sb), the first hard loss
- [ ] Concept: **shadow** = a neighbor blocks the *incoming* sun ray; **block** = a neighbor blocks the *outgoing* reflected beam to the tower. Plus tower shadow.
- [ ] Method: sample points across each mirror; cast a ray toward ŝ (shadow) and toward t̂ (block); test intersection with *nearby* neighbor rectangles (use a spatial index / radius — don't test all 1745²). η_sb = fraction of sample points that are clear.
- [ ] Core primitive to write & unit-test alone first: **ray → does it hit neighbor rectangle j?** (ray–plane intersect + in-rectangle test).
- [ ] Expect η_sb to drop the field ~10–20% → toward ~35 MW with truncation still = 1.
