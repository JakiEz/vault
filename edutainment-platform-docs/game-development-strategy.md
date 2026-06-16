# Game Development Strategy

## The Problem

None of the 5 core team roles owns game development. Building an educational game properly requires game design, game development (Unity/Godot), art assets, and behavior event logging. This is essentially a mini-team inside the team.

## Decision: Phase-Gated Approach

Game development is NOT a Phase 1 requirement. The platform's core differentiator is behavioral profiling intelligence — not original games. Prove that first.

```
Phase 1 (months 1–3):  No original game. API data only. Prove the profile model.
Phase 2 (months 4–6):  Outsource 1 simple edu game. Budget ~$10,000 USD.
Phase 3 (months 7+):   Hire full-time game developer if games drive retention.
```

## Phase 2 Game Spec: What to Outsource

The edu game is NOT an entertainment product. It is a behavior capture instrument disguised as a game. Entertainment quality is secondary to behavioral signal quality.

### Required Behavioral Decision Points

The game must force choices that reveal all 6 profile dimensions:

```
Dimension         → Game mechanic
─────────────────────────────────────────────────────
Risk Appetite     → Risky vs safe path choices under time pressure
Collaboration     → Solo vs team tasks, resource sharing
Strategic Depth   → Resource management, planning before acting
Persistence       → Retry mechanics, difficulty escalation
Precision         → Timed accuracy challenges, aim-based tasks
Role Identity     → Role selection at game start, specialization paths
```

### Event Log Schema (Required in Game Build)

Every decision must fire an event to the backend:

```json
{
  "student_id": "uuid",
  "game_id": "edu_game_001",
  "session_id": "uuid",
  "timestamp": "ISO8601",
  "event_type": "decision|retry|hint_used|level_complete|quit|time_bonus",
  "event_data": {
    "decision_id": "branch_3a",
    "time_taken_ms": 4200,
    "chose_risky_option": false,
    "near_teammate": true,
    "score_delta": 150
  }
}
```

### Game Format Options

| Format | Cost | Time | Best for |
|---|---|---|---|
| Browser-based 2D (Godot → HTML5) | $5–8k | 6 weeks | Zero install, runs in school browser |
| Mobile (Godot → Android/iOS) | $8–12k | 8 weeks | Students play at home |
| Simple web puzzle game | $3–5k | 4 weeks | Fastest to ship, lowest barrier |

**Recommended for Phase 2:** Browser-based 2D puzzle/decision game in Godot, exported to HTML5. No install required — runs in any school browser, no IT approval needed.

## Phase 3: Hiring a Game Developer

If games become a retention driver (students return weekly), hire:

**Role: Game Developer**
- Stack: Godot (preferred) or Unity, GDScript or C#
- Owns: Build and maintain edu games, implement behavior event logging, work with designer on art/UI, work with backend engineer on event API
- Option A: Restructure Person 2 into frontend-only + hire dedicated game dev
- Option B: Add as 6th team member after first revenue milestone

## Why Not Build In-House in Phase 1

Person 2 (Full-Stack) could learn Godot and build a simple 2D game in 3 months. But this means:
- Dashboard and Tauri app are delayed 3 months
- The game is built before the profile model is validated
- Risk: spend 3 months on a game that captures the wrong signals

Build the profile engine first. Validate it with commercial game API data. Then build games that are designed to fill the gaps the APIs can't cover.

## Competitive Note vs Squid Academy

Squid Academy's games are structured esports training programs. Their addressable market is students interested in esports careers.

Our games serve a different purpose: passive behavioral signal capture for all students, regardless of esports interest. A student playing a math puzzle game is still generating Risk Appetite and Persistence signals. This expands our total addressable market beyond esports.

The game design principle: **every edu game should feel fun to a student who has never touched Valorant.**
