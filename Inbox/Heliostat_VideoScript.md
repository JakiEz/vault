---
type: resource
description: Ready-to-use prompt + full narration script for an AI to generate a learning video on "finding the sun" (solar geometry) for the heliostat problem. Plain words, full detail.
created: 2026-06-21
related: [[Heliostat_StudyLog]], [[Heliostat_Field_Notes]]
---

# Video Script — "Where Is the Sun?" (Solar Geometry for the Heliostat Field)

> Hand the whole file to a video-generating / explainer AI. **Part A** tells it how to make the video. **Part B** is the segment-by-segment script (narration + on-screen visuals + formulas + worked numbers). Everything is grounded in the real problem site (98.5°E, 39.4°N, 3000 m) and uses validated example numbers.

---

## PART A — Prompt / context for the video AI

**Your task:** Produce a single animated explainer video (~9–11 minutes) that teaches a university engineering student how to compute the Sun's position and strength from nothing but a date and a clock time, for a solar "heliostat field" power-plant design problem.

**Audience:** A 2nd–3rd year computer/electrical engineering student. Comfortable with basic trig and coding, but NOT with astronomy or solar-geometry jargon. Assume zero prior knowledge of declination, hour angle, azimuth, or DNI.

**Tone & style:**
- Friendly, plain-spoken, encouraging. Short sentences. Define every term the first time it appears.
- Use concrete analogies before formulas (e.g. a tilted spinning top, a flashlight at an angle).
- "Easy words, but get into the details" — always show the real formula AND walk one real number through it.
- Build strictly in order; each idea reuses the previous one. Never forward-reference.

**Visual direction:**
- Animated 3D Earth with a clearly tilted axis; the Sun orbiting; seasons changing.
- A small "field" scene: a flat circle of ground with a tower, an arrow pointing at the Sun, and the horizon line — for altitude and the sun-vector parts.
- Every formula appears on screen, with each symbol color-coded and labeled in words next to it.
- Show worked numbers ticking through the formula (substitute → simplify → result).
- Keep a persistent "pipeline" bar at the bottom that fills in as we go: date → δ → … → DNI → vector.

**Hard requirements:**
- Use the site values: latitude φ = 39.4° N, altitude H = 3 km, solar constant G₀ = 1.366 kW/m².
- All angles in formulas are in RADIANS when computed in code — call this out explicitly (it's a classic bug).
- Include the worked example "December 21" throughout so the viewer sees one case end-to-end.
- End with a 30-second recap of the full pipeline and the 4 common coding traps.

**Length per segment:** roughly as marked below. Narration text is provided; you may lightly rephrase for flow but keep all formulas and numbers exact.

---

## PART B — The script

### Segment 0 — Cold open (20 sec)
**[VISUAL]** Drone shot over a real tower-CSP plant: thousands of mirrors on the desert floor, all glinting toward one glowing point atop a tall tower.
**Narration:** "This is a heliostat field. Thousands of flat mirrors, each one tilting through the day to bounce sunlight onto a single point on a tower. That point gets blazing hot, boils a fluid, and makes electricity. Our job: figure out how much energy these mirrors collect. And that starts with one question that sounds simple but isn't — *where, exactly, is the Sun?*"

### Segment 1 — Why the Sun's position matters (50 sec)
**[VISUAL]** A single mirror tilting to track the Sun across the sky; the reflected beam stays locked on the tower.
**Narration:** "Every mirror has to aim so its reflection hits the tower. As the Sun moves across the sky, each mirror constantly re-aims. And here's the catch: how much light a mirror catches depends on the angle between the Sun and the mirror. So the Sun's position changes the power *every minute*. To model a whole year, we need the Sun's position again and again."
**[ON-SCREEN]** "We can't check every second of the year — so we sample."

### Segment 2 — The 60 snapshots (60 sec)
**[VISUAL]** A 12×5 grid lighting up cell by cell. Rows = months, columns = times.
**Narration:** "Instead of every second, the problem picks 60 representative moments: the 21st of each month — that's 12 dates — and 5 times each day: 9:00, 10:30, 12:00, 1:30, and 3:00. Twelve times five is sixty snapshots. Think of it as two separate dials. One dial is the **date** — that sets the *season*. The other is the **clock** — that sets the *time of day*. These two dials are independent, and each one controls a different part of where the Sun is."
**[ON-SCREEN]** "12 months × 5 times = 60 sun positions. Date → season. Clock → time of day."

### Segment 3 — Declination: the season dial (110 sec)
**[VISUAL]** Earth with its axis tilted 23.45°, orbiting the Sun. The axis keeps pointing the same way. Highlight north pole leaning toward Sun (summer) then away (winter).
**Narration:** "Start with the season. Earth spins on an axis that's tilted about 23 and a half degrees. Crucially, that tilt always points the same direction in space — Earth doesn't wobble as it orbits. So as we go around the Sun, sometimes the northern half leans *toward* the Sun — that's summer, the Sun rides high. Six months later it leans *away* — winter, the Sun stays low."
**Narration:** "We capture this with one number called **declination**, written delta (δ). Picture the spot on Earth where the Sun is *exactly overhead* at noon. In June that spot is far north; in December it's far south. Declination is just the latitude of that spot. It swings from plus 23.45 degrees in June, to zero at the spring and autumn equinoxes, to minus 23.45 in December."
**[ON-SCREEN FORMULA]** `sin δ = sin(2π·D / 365) · sin(23.45°)`  — "D = days since the spring equinox (March 21 = day 0)."
**Narration:** "The formula looks fancy but it's two simple pieces. The `sin(23.45°)` part is the *amplitude* — the biggest the tilt can ever push the Sun, a fixed fact about our planet. The `sin(2π·D/365)` part is the *timing* — a smooth wave that's zero at the equinox, peaks a quarter-year later in summer, and dips in winter. Multiply timing by amplitude and you get today's declination."
**[VISUAL]** Plug in December 21: D = 275.
**[ON-SCREEN]** `sin δ = sin(2π·275/365)·sin(23.45°) = (−0.999)(0.398) = −0.398  →  δ ≈ −23.4°`
**Narration:** "December 21 gives minus 23.4 degrees — deep winter, exactly as expected. One input, the date, and the season falls right out."

### Segment 4 — Hour angle: the clock dial (80 sec)
**[VISUAL]** Top-down view of the sky dome; Sun arcing from east, through due-south at noon, to west. A wedge angle opens from the noon line.
**Narration:** "Now the second dial: time of day. The Earth turns a full 360 degrees in 24 hours — that's 15 degrees every hour. We measure the Sun's daily progress with the **hour angle**, omega (ω): how far the Sun is from its highest, noon position."
**[ON-SCREEN FORMULA]** `ω = (π/12)(ST − 12)`  — "ST = local solar time, in hours."
**Narration:** "At noon, ST is 12, so omega is zero — the Sun is due south and highest. Before noon it's negative — the Sun is in the east. After noon, positive — in the west. So 9:00 is minus 45 degrees, 3:00 is plus 45 degrees. Same five values every single day of the year, because the clock doesn't care about the season."
**[ON-SCREEN]** "9:00 → −45° | 10:30 → −22.5° | 12:00 → 0° | 1:30 → +22.5° | 3:00 → +45°"
**Narration:** "Important: the hour angle by itself is NOT how high the Sun is. It's just the time dial. To get the real Sun height, we have to combine both dials."

### Segment 5 — Altitude: combining the dials (110 sec)
**[VISUAL]** The field scene: horizon line, an arrow to the Sun, the angle between arrow and ground highlighted as "altitude."
**Narration:** "Here's the payoff. **Altitude**, alpha (α), is the angle of the Sun above the horizon — how high it is right now. Zero means sitting on the horizon at sunrise; 90 means straight overhead. This is the number we actually want, and it comes from combining the season, the time, and *where you're standing* — your latitude, phi (φ), which for our site is 39.4 degrees north."
**[ON-SCREEN FORMULA]** `sin(altitude) = cos δ · cos φ · cos ω + sin δ · sin φ`
**Narration:** "Notice all three ingredients in there: declination from the date, hour angle from the time, and latitude from the location. Feed them in and you get the sine of the altitude."
**[VISUAL]** December 21, noon: δ = −23.4°, ω = 0, φ = 39.4°.
**[ON-SCREEN]** `sin α = cos(−23.4°)·cos(39.4°)·1 + sin(−23.4°)·sin(39.4°) = 0.457  →  α ≈ 27°`
**Narration:** "December noon: the Sun reaches just 27 degrees above the horizon — low winter Sun. Run the same math for June noon and you get about 74 degrees — high summer Sun. That huge swing, from 27 to 74 degrees, is the seasons showing up in your numbers."
**[ON-SCREEN WARNING BOX]** "⚠️ In code: convert degrees to RADIANS first. cos(39.4°) = 0.77, but cos(39.4 radians) = −0.13 — a completely different, wrong answer."
**Narration:** "And a coding warning that bites everyone: calculators and code expect radians, not degrees. Convert your latitude once, up front, or the whole formula flips and breaks."

### Segment 6 — DNI: how strong is the sunlight? (100 sec)
**[VISUAL]** Two flashlights hitting a table: one straight down (small bright circle), one at a low angle (big dim smear). Then sunlight passing through a thick slab of atmosphere at a low angle vs a thin slab straight down.
**Narration:** "Knowing where the Sun is, we now ask: how *strong* is the light arriving? This is called **DNI** — Direct Normal Irradiance — the power in the sunlight, in kilowatts per square meter. Its strength depends on how much air the light has to punch through, and that depends on the angle. A high Sun shoots almost straight down through a thin layer of air — strong light. A low Sun comes in at a slant through much more air, getting scattered and absorbed — weaker light."
**[ON-SCREEN FORMULA]** `DNI = G₀ · [ a + b · exp(−c / sin α) ]`  — "G₀ = 1.366 kW/m²; a, b, c set by altitude H = 3 km."
**Narration:** "The key piece is `exp(minus c over sin alpha)` — read it as *the fraction of light that survives the atmosphere*. When the Sun is high, `sin alpha` is big, the exponent is near zero, and that term is near one — almost all the light gets through. When the Sun is low, the term shrinks — more light is lost. That minus sign is the whole point; flip it by accident and your model says low Sun is stronger, which is nonsense."
**[VISUAL]** December numbers tick out.
**[ON-SCREEN]** "Dec 9:00 → DNI 0.74 | Dec noon → DNI 0.91 kW/m²  (noon strongest)"
**Narration:** "December noon gives about 0.91 kilowatts per square meter; early morning only 0.74. Noon is always the strongest, because that's when the Sun is highest and the air is thinnest."

### Segment 7 — The Sun as a vector (110 sec)
**[VISUAL]** The field scene with axes drawn: +x to the East, +y to the North, +z Up. The arrow to the Sun gets broken into its three shadow-components along x, y, z.
**Narration:** "One more move sets us up for everything that follows. So far we've described the Sun with two angles — altitude (how high) and azimuth (which compass direction). That's fine, but the next stage of the model needs to compare the Sun's direction with the direction each mirror aims. Comparing directions is *much* easier if we write the Sun as a 3D arrow instead of two angles."
**Narration:** "So we build a **unit vector** — an arrow of length one — pointing at the Sun, in field coordinates: x points east, y points north, z points up."
**[ON-SCREEN FORMULA]**
```
s_x = −cos δ · sin ω                          (East)
s_y =  sin δ · cos φ − cos δ · sin φ · cos ω   (North)
s_z =  sin α                                   (Up)
```
**Narration:** "Look at the pieces. The up-component, `s_z`, is just `sin alpha` — the altitude we already computed. The east-component flips with the time of day: positive in the morning when the Sun's in the east, negative in the afternoon. And we build all this straight from declination and hour angle — which neatly sidesteps a famous trap in the azimuth formula, where morning and afternoon can come out identical by mistake."
**[VISUAL]** December noon vector drawn in the scene.
**[ON-SCREEN]** "Dec noon: ŝ = (0, −0.89, 0.46)  → due south, moderately high.  Check: 0² + 0.89² + 0.46² ≈ 1 ✓"
**Narration:** "December noon gives an arrow of zero east-west, strongly south, and partway up — exactly a low southern winter Sun. And a built-in sanity check: a unit vector's three parts, squared and added, must equal one. If they don't, you've got a typo."

### Segment 8 — Recap & the traps (70 sec)
**[VISUAL]** The pipeline bar fills fully, then replays quickly.
**Narration:** "Let's zoom out. From just a date and a time, we got the whole Sun. The date gave us declination — the season. The time gave us the hour angle. Combine those with our latitude and we got the altitude — how high the Sun sits. From altitude we got DNI — how strong the light is. And we repackaged the direction as a clean 3D arrow for the next stage."
**[ON-SCREEN PIPELINE]** "date → δ  |  time → ω  |  +φ → altitude → DNI  |  → sun vector"
**[VISUAL]** Four red "trap" cards flip over.
**Narration:** "Four traps to remember when you code this. One: always work in radians, not degrees. Two: declination's formula gives you the *sine* of the angle — don't confuse `sin δ` with `δ` itself. Three: keep the minus sign in the DNI exponent. And four: don't take the sine of a number that's *already* a sine — a sneaky one-percent error. Watch those, and your Sun model will be rock solid."
**[VISUAL]** Mirrors glinting again, camera pulls back.
**Narration:** "Now that we know where the Sun is and how strong it shines, we're ready for the real prize: following that light into the mirrors and measuring exactly how much reaches the tower. That's next."

---

## Optional: shorter "prompt-only" version
If the tool just wants a one-paragraph brief: "Make a 10-minute friendly animated explainer for an engineering student on computing the Sun's position from a date and time, for a solar tower (heliostat) problem at latitude 39.4°N, altitude 3 km. Cover, in order and building on each other: (1) why sun position matters for mirror efficiency; (2) sampling 60 moments = 12 months × 5 times; (3) declination δ from the date — Earth's 23.45° tilt + the sine-wave formula `sin δ = sin(2πD/365)·sin(23.45°)`; (4) hour angle ω from the time, `ω=(π/12)(ST−12)`; (5) altitude α by combining δ, ω, latitude φ via `sin α = cosδ cosφ cosω + sinδ sinφ`; (6) DNI sunlight strength `G₀[a+b·exp(−c/sinα)]` and why angle controls strength; (7) repackaging the sun as a 3D unit vector (x=East, y=North, z=Up). Use plain words, define every term, show each formula on screen, and walk the December-21 example through end-to-end (noon altitude ≈27°, DNI ≈0.91 kW/m², vector ≈(0,−0.89,0.46)). End with the 4 coding traps: radians vs degrees; sinδ is not δ; keep the minus in DNI; don't sin() an already-sined value."
