# Gameplay Behavior Profile Taxonomy

## Why Not MBTI

MBTI is trademarked and scientifically contested. Instead we define a custom Gameplay Behavior Taxonomy built from observable, measurable in-game signals. The dimensions map cleanly to pedagogy without licensing issues.

## The 6 Dimensions

### 1. Risk Appetite
**Spectrum:** Cautious ←————→ Aggressive

**Game signals:**
- First blood kills (Valorant, LoL)
- Low HP aggression events (attacking while health < 25%)
- KD variance across sessions (high variance = streaky risk-taker)
- Agent/champion selection (duelists vs sentinels/tanks)

**Learning implication:**
- Low risk: needs psychological safety before attempting hard problems
- High risk: thrives on challenge-based learning, tolerates failure well

---

### 2. Collaboration Style
**Spectrum:** Solo ←————→ Team-Oriented

**Game signals:**
- Assist rate vs kill rate
- Support role preference (healers, tanks, sentinels)
- Teammates healed (LoL support heal stat)
- Weapons donated to teammates (CS2)
- Vision score (LoL ward placement)

**Learning implication:**
- Solo: prefers independent study, self-paced modules
- Team: thrives in group projects, peer teaching, discussion

---

### 3. Strategic Depth
**Spectrum:** Reactive ←————→ Planner

**Game signals:**
- Vision score (LoL) — planning ahead
- Objective damage vs kill damage ratio
- Setup kills vs reaction kills
- Rotation timing (how early a player repositions)

**Learning implication:**
- Reactive: hands-on trial-and-error learner
- Planner: conceptual/visual learner, benefits from diagrams and frameworks

---

### 4. Persistence
**Spectrum:** Quits Early ←————→ Grinds Through

**Game signals:**
- Session length
- Comeback patterns (win rate after being behind)
- Rank progression rate
- Return rate after losing streaks

**Learning implication:**
- Low persistence: needs short feedback loops and micro-rewards
- High persistence: tolerates long projects, benefits from deep-dive content

---

### 5. Precision vs Speed
**Spectrum:** Fast/Loose ←————→ Deliberate/Precise

**Game signals:**
- Headshot percentage (Valorant, CS2)
- Death rate vs time alive
- Ability accuracy (Valorant agent abilities)
- Spell hit rate (LoL skillshots)

**Learning implication:**
- Speed-oriented: fast guesser, benefits from immediate feedback correction
- Precision-oriented: deliberate thinker, prefers to understand before acting

---

### 6. Role Identity
**Spectrum:** Flexible Generalist ←————→ Deep Specialist

**Game signals:**
- Agent/champion pool diversity (many vs few)
- Role switching across sessions
- Mastery depth on preferred role

**Learning implication:**
- Generalist: broad curiosity, benefits from interdisciplinary content
- Specialist: deep focus, benefits from mastery-based progression

---

## Profile Output Format

Each student gets a hexagon radar chart across all 6 dimensions, scored 1–10.

Example profile:
```
Risk Appetite:     8/10  (aggressive)
Collaboration:     3/10  (solo)
Strategic Depth:   7/10  (planner)
Persistence:       9/10  (grinds)
Precision:         6/10  (balanced)
Role Identity:     2/10  (generalist)
```

This profile maps to: **"Independent Deep Learner"** — works best alone on long challenging projects. Prefers mastery-based progression but explores broadly.

## Normalization

Raw signals are normalized against the student's own history (not absolute population benchmarks) to distinguish style from skill level. A player who dies 12 times with 18 kills is aggressive; a player who dies 12 times with 2 kills is still learning.

```
risk_score = (kills * 0.4 + low_hp_aggression_events * 0.6) / total_deaths
```
