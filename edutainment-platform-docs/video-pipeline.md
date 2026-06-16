# Video Analysis Pipeline (Deep Behavior Mode)

## Overview

Screen recording + AI analysis is an optional premium feature ("Deep Behavior Mode") for cases where API data is insufficient. It captures moment-to-moment gameplay behavior beyond what post-match stats can reveal.

## Why Hybrid Inference

Not every frame needs a powerful cloud model. Most frames are idle — menus, walking, loading. Only 10–20% of frames contain meaningful behavioral events. A hybrid local + cloud architecture routes frames by complexity:

```
Frame → Local Model (free, fast) → interesting? → Cloud Model (paid, accurate)
                                  → boring?     → discard
```

This reduces cloud API costs by ~80%.

## Pipeline Steps

### Step 1 — Frame Sampling
Reduce 30fps video to 2fps for analysis.

```python
# 1 hour at 2fps = 7,200 frames (vs 108,000 at 30fps)
interval = int(source_fps / fps_target)  # sample every Nth frame
```

### Step 2 — Local Gatekeeper Model
Runs on-server, zero API cost. Makes binary interesting/boring decisions.

Techniques used:
- Frame diff score — skip if scene hasn't changed (idle frames)
- Brightness check — skip dark/loading screens
- HP bar reader — OpenCV region crop + HSV color mask to read health value
- Scene classifier — lightweight YOLO v8 or MobileNet trained on game UI patterns
- Death screen detector — template matching (fast, no ML needed)

```python
def is_interesting_frame(frame, prev_frame):
    diff = cv2.absdiff(frame, prev_frame)
    if diff.mean() < 5.0: return False      # scene unchanged
    if frame.mean() < 20: return False       # loading screen
    hp = read_hp_bar(frame)
    if hp < 25: return True                  # low HP = always interesting
    return local_classifier.predict(frame) > 0.6
```

### Step 3 — Three-Tier Routing
```
Score 0.0–0.4 → discard         (OpenCV rules: idle/menu)
Score 0.4–0.7 → LLaVA 7B local  (free GPU inference, medium accuracy)
Score 0.7–1.0 → Gemini Flash     (cloud API, high accuracy)
```

LLaVA 7B runs on a ~$0.10/hour GPU instance. Handles simple questions like "is the player in a fight?" well enough for mid-tier frames.

### Step 4 — Cloud Model Analysis
Only called for high-interest frames (~10–20% of total).

```python
prompt = """
Analyze this game screenshot. Return JSON only:
{
  "event": "kill|death|teamfight|objective|rotation|clutch|idle",
  "risk_level": 1-5,
  "is_solo_play": true/false,
  "tactical_notes": "brief description"
}
"""
# Uses Gemini 2.0 Flash: ~$0.10 per 1M tokens
# 1 frame ≈ 1,000 tokens → $0.0001 per frame
```

### Step 5 — Event Detection
Compare frame-by-frame JSON outputs to detect state transitions:

```
prev["is_dead"] = false AND curr["is_dead"] = true  → death event
curr["notable_event"] = "kill"                       → kill event
hp < 20 AND position = "aggressive"                  → low_hp_aggression
no combat for 60+ seconds                            → passive_phase
```

### Step 6 — Behavior Tagging
Aggregate raw events into behavioral signals:

```
10 low_hp_aggression events → HIGH risk appetite
3 deaths followed by immediate rejoin → HIGH impulsivity
consistent passive phase before engaging → HIGH strategic patience
kill feed team kills > solo kills → HIGH collaboration
```

## Cost Estimate (500 students, 3 sessions/week, 1hr each)

```
Without hybrid (all cloud):
  6,000 sessions × 720 frames × $0.0001 = $432/month

With hybrid (local filters 80% of frames):
  6,000 sessions × 144 cloud frames × $0.0001 = $86/month
  + GPU server for local model ≈ $50/month
  Total: ~$136/month

Savings: ~68% cost reduction
```

## Technical Challenges

### 1. Game UI Changes With Patches
Valorant and LoL update HUD layouts frequently. Local template matchers and region-based readers will break. Solution: version detection layer that loads game-specific config per patch version.

### 2. Multiple Games Look Different
Each game needs separate detector configs or prompts. For cloud VLM approach this is just a different prompt string. For custom CV it requires separate trained models per game.

### 3. Style vs Skill Disambiguation
A player dying 12 times may be aggressive (18 kills) or inexperienced (2 kills). Context normalization required:

```python
# Wrong: 12 deaths → reckless
# Right: normalized score considers kill context
risk_score = (kills * 0.4 + low_hp_aggression_events * 0.6) / total_deaths
```

## Recommended Rollout

- Phase 1–2: Skip screen recording. Use game APIs (free, sufficient signal).
- Phase 3: Launch Deep Behavior Mode as a premium add-on (~$3–5/student/month extra).
- Start Valorant only. Validate pipeline accuracy before adding LoL and CS2.

## Capture Technology

- Desktop app: Tauri (Rust + React) + Windows Graphics Capture API
- Alternative: OBS SDK (cross-platform, well-documented)
- Upload: chunked .mp4 upload to Cloudflare R2 during/after session
- Privacy: recordings processed and deleted after event extraction (do not store long-term)
