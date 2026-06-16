# Game API Signal Mapping

## League of Legends — Riot Match V5 API

Access: Free, requires developer key from developer.riotgames.com
Data: Full per-match participant data, post-match

| API Field | Behavior Signal | Profile Dimension |
|---|---|---|
| kills / deaths / assists | Kill-heavy = aggressive, assist-heavy = support | Risk Appetite, Collaboration |
| visionScore | Ward placement = strategic planner | Strategic Depth |
| firstBloodKill | Initiates early = risk-taker | Risk Appetite |
| totalTimeCCDealt | Crowd control usage = team disruptor | Collaboration |
| damageDealtToObjectives | Focuses objectives over kills = goal-oriented | Strategic Depth |
| longestTimeSpentLiving | Stays alive = patient, defensive | Persistence, Precision |
| totalHealsOnTeammates | Support behavior = empathetic, team-first | Collaboration |
| championName (across matches) | Role pattern: mage/tank/ADC/support | Role Identity |
| timePlayed | Session engagement depth | Persistence |
| win/loss streak pattern | Comeback vs tilt behavior | Persistence |
| bountyLevel | High bounty = high-impact risky play | Risk Appetite |
| detectorWardsPlaced | Control ward usage = strategic awareness | Strategic Depth |
| firstTowerKill | Proactive objective play | Strategic Depth |

## Valorant — Riot Valorant Match API

Access: Requires production key from Riot (apply at developer.riotgames.com, 2–4 week approval)
Data: Per-match participant stats

| API Field | Behavior Signal | Profile Dimension |
|---|---|---|
| headshots / bodyshots / legshots | High headshot % = precision, patience | Precision |
| agent (across matches) | Duelist = aggressive, Sentinel = defensive | Risk Appetite, Role Identity |
| assists vs kills ratio | Team-enabler vs solo fragger | Collaboration |
| plants / defuses | Objective-focused behavior | Strategic Depth |
| score vs combat score | Round impact beyond kills | Strategic Depth |
| grenadeCasts / ultimateCasts | Ability economy management | Strategic Depth |

## CS2 — Steam Web API

Access: Free with Steam API key
Limitation: Lifetime aggregate stats only, no per-match breakdown
Per-match data available via FACEIT API (free, most competitive players use FACEIT)

| API Field | Behavior Signal | Profile Dimension |
|---|---|---|
| total_kills / total_deaths | Overall KD tendency | Risk Appetite |
| total_headshots | Precision preference | Precision |
| total_weapons_donated | Giving teammates guns = generous, team-first | Collaboration |
| total_mvps | Clutch performance = confidence under pressure | Persistence |
| favorite_map / favorite_weapon | Consistency vs variety | Role Identity |
| total_wins | Long-term persistence | Persistence |

## FACEIT API (CS2 per-match)

Access: Free FACEIT developer account
Data: Full match history for FACEIT players, including round-level data

| Signal | Behavior Signal | Profile Dimension |
|---|---|---|
| k/d per map | Performance variance | Persistence |
| opening duel rate | Aggression, entry fragging | Risk Appetite |
| clutch win rate | Performance under pressure | Persistence |
| utility damage | Strategic grenade usage | Strategic Depth |
| flash assists | Team-enabling play | Collaboration |

## In-House Educational Games — Event Log Schema

Games built internally log events directly to our backend. No API needed — we own the data.

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
    "chose_safe_option": false,
    "score_delta": 150
  }
}
```

Events captured per edu game:
- Decision branches taken (risky vs safe path)
- Retry count per challenge
- Hint usage rate
- Time spent before acting
- Quit timing (did they give up early?)
- Collaboration events (multiplayer games)

## Signal Aggregation

All signals are normalized per-student before scoring:

1. Collect raw stats from all game sources (LoL + Valorant + CS2 + edu games)
2. Weight by recency (last 30 days weighted 2x)
3. Normalize against student's own baseline (not population average)
4. Score each dimension 1–10 using weighted formula per dimension
5. Minimum 10 matches/sessions required before generating a profile
