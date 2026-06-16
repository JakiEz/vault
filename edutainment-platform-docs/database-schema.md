# Database Schema

## Core Entities

### schools
```sql
id              UUID PRIMARY KEY
name            TEXT NOT NULL
domain          TEXT UNIQUE        -- used for SSO matching
subscription_tier TEXT             -- starter | growth | enterprise
student_count   INTEGER
created_at      TIMESTAMPTZ
```

### students
```sql
id              UUID PRIMARY KEY
school_id       UUID REFERENCES schools(id)
display_name    TEXT
age             INTEGER
grade           TEXT
consent_given   BOOLEAN DEFAULT FALSE   -- COPPA/FERPA consent
consent_date    TIMESTAMPTZ
riot_puuid      TEXT UNIQUE NULL        -- Riot account link
steam_id        TEXT UNIQUE NULL        -- Steam account link
faceit_id       TEXT UNIQUE NULL
created_at      TIMESTAMPTZ
```

### game_sessions
```sql
id              UUID PRIMARY KEY
student_id      UUID REFERENCES students(id)
game_source     TEXT    -- lol | valorant | cs2 | faceit | edu_game | recording
game_id         TEXT    -- match ID from API, or internal edu game ID
played_at       TIMESTAMPTZ
duration_seconds INTEGER
raw_data        JSONB   -- full API response stored for reprocessing
processed       BOOLEAN DEFAULT FALSE
created_at      TIMESTAMPTZ
```

### behavior_events
```sql
id              UUID PRIMARY KEY
session_id      UUID REFERENCES game_sessions(id)
student_id      UUID REFERENCES students(id)
event_type      TEXT    -- kill | death | low_hp_aggression | assist | objective | passive_phase | hint_used | retry | ...
event_data      JSONB   -- flexible payload per event type
timestamp_offset INTEGER -- seconds from session start
source          TEXT    -- api | video_ai | edu_game_log
confidence      FLOAT   -- 1.0 for API-derived, 0.6-0.95 for AI-inferred
created_at      TIMESTAMPTZ
```

### student_profiles
```sql
id              UUID PRIMARY KEY
student_id      UUID REFERENCES students(id) UNIQUE
risk_appetite       FLOAT   -- 1.0–10.0
collaboration       FLOAT
strategic_depth     FLOAT
persistence         FLOAT
precision           FLOAT
role_identity       FLOAT
sessions_analyzed   INTEGER
last_updated        TIMESTAMPTZ
profile_label       TEXT    -- human-readable archetype, e.g. "Independent Deep Learner"
confidence_score    FLOAT   -- how reliable is this profile (based on data volume)
created_at          TIMESTAMPTZ
```

### learning_recommendations
```sql
id              UUID PRIMARY KEY
student_id      UUID REFERENCES students(id)
content_type    TEXT    -- video | article | project | game | challenge
content_title   TEXT
content_url     TEXT
dimension       TEXT    -- which profile dimension this targets
rationale       TEXT    -- why this was recommended
shown_at        TIMESTAMPTZ
clicked         BOOLEAN DEFAULT FALSE
completed       BOOLEAN DEFAULT FALSE
```

### edu_game_events (for in-house games)
```sql
id              UUID PRIMARY KEY
student_id      UUID REFERENCES students(id)
game_id         TEXT
session_id      UUID
event_type      TEXT    -- decision | retry | hint_used | level_complete | quit | time_bonus
event_data      JSONB
timestamp       TIMESTAMPTZ
```

## Key Relationships

```
schools (1) ──── (many) students
students (1) ──── (many) game_sessions
game_sessions (1) ──── (many) behavior_events
students (1) ──── (1) student_profiles
students (1) ──── (many) learning_recommendations
students (1) ──── (many) edu_game_events
```

## Profile Scoring Query (example)

Nightly job aggregates last 90 days of behavior_events per student:

```sql
SELECT
  student_id,
  COUNT(*) FILTER (WHERE event_type = 'low_hp_aggression') AS risky_plays,
  COUNT(*) FILTER (WHERE event_type = 'kill') AS kills,
  COUNT(*) FILTER (WHERE event_type = 'death') AS deaths,
  COUNT(*) FILTER (WHERE event_type = 'assist') AS assists,
  COUNT(*) FILTER (WHERE event_type = 'objective') AS objective_plays,
  AVG((event_data->>'vision_score')::float) FILTER (WHERE event_data ? 'vision_score') AS avg_vision
FROM behavior_events
WHERE created_at > NOW() - INTERVAL '90 days'
GROUP BY student_id
```

Results feed into the profile engine Python service which scores each dimension and upserts student_profiles.

## Minimum Data Threshold

A profile is only generated and shown when:
- sessions_analyzed >= 10
- Total behavior_events >= 50
- At least 2 different game sources represented (reduces single-game bias)
