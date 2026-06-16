# Video Event → Profile Dimension Mapping

## Purpose

This document closes the gap between the Video Analysis Pipeline and the Profile Scoring Engine. The video pipeline writes raw events to the `behavior_events` table, but the Profile Engine needs explicit rules for which video events map to which of the 6 profile dimensions and at what weight.

Without this mapping, API-derived events and video-derived events would produce incompatible scores for the same student.

## The Translation Table

| Video Event Type | Profile Dimension | Weight | Rationale |
|---|---|---|---|
| `low_hp_aggression` | Risk Appetite | 0.6 | Attacking while nearly dead is the clearest risk signal |
| `kill` | Risk Appetite | 0.4 | Kills indicate offensive intent but not necessarily recklessness |
| `death_immediate_reengage` | Persistence | 0.5 | Rejoining fight within 5s of death = grinds through adversity |
| `death_passive_wait` | Persistence | -0.2 | Long lobby time = may be tilting or disengaging |
| `passive_phase` (60s+) | Strategic Depth | 0.7 | Extended non-combat phase = setting up, planning next move |
| `assist_near_teammate` | Collaboration | 0.8 | Dealing damage/healing near teammates = team-enabling play |
| `solo_kill_isolated` | Collaboration | -0.3 | Kills far from team = lone wolf behavior |
| `ability_use_near_teammate` | Collaboration | 0.6 | Using abilities to support others |
| `headshot_kill` (from kill feed) | Precision | 0.9 | Precise aim = deliberate, patient targeting |
| `bodyshot_spam_kill` | Precision | -0.4 | Spray-and-pray style = speed over accuracy |
| `objective_play` | Strategic Depth | 0.65 | Planting/defusing/capping objectives = goal-oriented |
| `rotation_early` | Strategic Depth | 0.75 | Moving before being forced to = reads the game ahead |
| `same_agent_repeated` | Role Identity | 0.8 | Playing same agent/role consistently = specialist |
| `agent_switched` | Role Identity | -0.3 | Switching role = generalist tendency |
| `session_length_long` (90min+) | Persistence | 0.6 | Long sessions = engaged, grinds through |
| `rage_quit` (quit mid-match) | Persistence | -0.7 | Quitting mid-game = low frustration tolerance |

## Weighting Formula Per Dimension

Each dimension score is computed from all events in the past 90 days:

```python
def score_dimension(events, dimension_rules):
    raw_score = 0.0
    event_count = 0

    for event in events:
        rule = dimension_rules.get(event['event_type'])
        if rule:
            raw_score += rule['weight'] * event.get('confidence', 1.0)
            event_count += 1

    if event_count < 10:
        return None  # insufficient data

    # Normalize to 1–10 scale
    # raw_score ranges roughly -5 to +10 depending on playstyle
    normalized = (raw_score / event_count + 1) * 5
    return max(1.0, min(10.0, normalized))
```

## API Events vs Video Events — Equivalence Map

The same dimension can be fed by both API data and video data. These pairs are equivalent and should be merged in the profile engine:

| API Signal | Video Event Equivalent | Dimension |
|---|---|---|
| `firstBloodKill = true` | `low_hp_aggression` (first 60s) | Risk Appetite |
| `assists / kills ratio` | `assist_near_teammate` count | Collaboration |
| `visionScore` | `passive_phase` + `rotation_early` | Strategic Depth |
| `longestTimeSpentLiving` | inverse of `death` frequency | Persistence |
| `headshot %` (Valorant/CS2) | `headshot_kill` from kill feed | Precision |
| `championName` consistency | `same_agent_repeated` | Role Identity |

When both API and video data exist for the same session, **API data takes precedence** (higher reliability, no inference required). Video events fill gaps where API data is unavailable or insufficient.

## Confidence Scoring for Video Events

Video-derived events carry a confidence score (set during AI analysis) that is used in the weighting formula:

- EXTRACTED (from kill feed OCR, death screen detection): confidence = 0.95
- INFERRED (from frame analysis by Gemini/LLaVA): confidence = 0.75
- AMBIGUOUS (low-certainty detection): confidence = 0.3 — still recorded, low weight

The Profile Engine multiplies event weight × confidence before summing, so a low-confidence video event has reduced impact compared to a clean API signal.

## Minimum Data Requirements

A video-only profile (no API data) requires:
- Minimum 5 recorded sessions
- Minimum 80 behavior events with confidence ≥ 0.75
- At least 3 different event types represented (prevents single-signal bias)

A mixed profile (API + video) can generate after:
- 10 API matches OR 3 video sessions (whichever comes first)
