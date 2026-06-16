# Team Structure (6 People)

## Overview

A 6-person mixed team covering product, development, AI/ML, design, and business development.

## Roles

### Person 1 — Founder / Product Lead
Owns: Vision, product decisions, investor relations, pilot school relationships
- Prioritize sprint backlog each week
- Talk to schools weekly — primary sales person in Phase 1
- Write research-backed content for LinkedIn and blog
- Make final call on product direction

Do NOT write code. Time is better spent in school conversations than in PRs.

### Person 2a — Frontend Developer (Friend)
Owns: School dashboard, student portal (Next.js)
Stack: TypeScript, Next.js, React, Tailwind CSS

Phase 1 priorities:
- School dashboard: student list, radar chart, reports
- Student portal: profile page, linked accounts
- Auth: school SSO + student invite flow

### Person 2b — Desktop App Developer (Founder)
Owns: Tauri desktop app
Stack: Tauri, Rust, React, TypeScript, Windows Graphics Capture API

Phase 1 priorities:
- Tauri app setup and account linking UI (Riot + Steam OAuth)
- Game session detection (detect when student launches a supported game)

Phase 2 priorities:
- Screen recording via Windows Graphics Capture API
- Chunked .mp4 upload to Cloudflare R2
- Recording controls UI (start/stop/status)

### Person 3 — Backend + Data Engineer
Owns: API server, database, game API integrations, profile engine
Stack: Node.js/Fastify or Python FastAPI, PostgreSQL, Python, Redis

Phase 1 priorities:
- Database schema and migrations
- Riot API integration (LoL match history)
- Steam and FACEIT API integration
- Profile scoring engine (6 dimensions)
- Nightly batch job
- Multi-tenant auth middleware

This is the most critical hire. Everything depends on data flowing correctly.

### Person 4 — AI / ML Engineer
Owns: Video analysis pipeline, local inference models, cloud vision integration, behavior tagging
Stack: Python, OpenCV, YOLO v8, LLaVA 7B (Ollama), Gemini 2.0 Flash API, PyTorch (basic)

Phase 1 priorities (preparation work, pipeline ships in Phase 2):
- Prototype frame gatekeeper using OpenCV (frame diff + HP bar reader)
- Train/fine-tune YOLO v8 on game UI screenshots (Valorant first)
- Set up LLaVA 7B locally via Ollama for mid-tier frame analysis
- Define behavior event JSON schema with Person 3
- Test Gemini Flash prompt accuracy on sample gameplay footage

Phase 2 priorities (when screen recording launches):
- Ship full 6-step video pipeline (sample → gate → route → analyze → detect → tag)
- Integrate pipeline output into behavior_events table
- Tune three-tier routing thresholds (0.0–0.4 / 0.4–0.7 / 0.7–1.0)
- Validate that video-derived signals match API-derived signals for same sessions
- Expand pipeline from Valorant to LoL and CS2

Key responsibilities:
- Frame sampling (30fps → 2fps)
- Local gatekeeper model — OpenCV + YOLO v8 (free, runs on server)
- Mid-tier inference — LLaVA 7B on rented GPU (~$50/month)
- High-interest frames — Gemini 2.0 Flash API (~$86/month for 500 students)
- Event detection (frame-to-frame state transition logic)
- Behavior tagging (raw events → profile dimension signals)

### Person 5 — Designer + Frontend Developer
Owns: UI/UX design, component library, landing page, marketing site
Stack: Figma, React/Next.js, Tailwind CSS

Phase 1 priorities:
- Design the radar chart profile (core visual of the product)
- Design the school dashboard (professional and trustworthy, not gamey)
- Build the public website (landing page + full site)
- Brand identity: logo, color system, typography

Key constraint: school software must look professional enough for a principal to trust. Not cool, not flashy — credible.

### Person 6 — Business Development
Owns: School outreach, partnerships, pilot schools, competitive intel
No coding required.

Phase 1 priorities:
- Cold outreach to 20 schools per month — esports coaches, edtech coordinators
- Book 10 discovery calls (learning calls, not sales calls)
- Secure 1 pilot school before MVP is done
- Research Squid Academy's school relationships
- Build relationships with esports tournament organizers (student pipeline)
- Apply for SEA edtech grants

## Responsibility Matrix

| Area | P1 Founder | P2 Full-Stack | P3 Backend | P4 AI/ML | P5 Designer | P6 Biz Dev |
|---|---|---|---|---|---|---|
| Product decisions | Lead | Input | Input | Input | Input | Input |
| School dashboard | Review | Build | API | — | Design | Demo |
| Profile engine | Review | — | Build | Input | — | — |
| Game API integrations | — | — | Build | — | — | — |
| Video pipeline | Review | — | DB/API | Build | — | — |
| Frame gatekeeper | — | — | — | Build | — | — |
| Gemini/LLaVA inference | — | — | — | Build | — | — |
| Behavior tagging | Review | — | Schema | Build | — | — |
| Tauri desktop app | Review | Build | Hooks | — | UI | — |
| Public website | Approve | — | — | — | Build | Content |
| School outreach | Senior | — | — | — | Materials | Lead |
| Pilot schools | Close | Demo | Demo | Demo | — | Find |
| Investor deck | Lead | — | — | — | Design | Market data |

## Gaps With 6 People

No dedicated roles for:
- Mobile development (not needed Phase 1)
- QA/testing (everyone tests own work, P1 does final sign-off)
- DevOps (P3 owns infra, use managed services to minimize ops)
- Game developer (see game-development-strategy.md)
- Learning specialist — CRITICAL GAP. Need a part-time advisor (school counselor or university professor) to validate profile-to-pedagogy mapping before showing to schools.

## First 30 Days

```
Person 1: Talk to 10 schools. Define MVP scope. Apply for Riot API key.
Person 2: Set up monorepo. Build auth + basic dashboard shell.
Person 3: Database schema. Riot API integration. First profile scores.
Person 4: Prototype frame gatekeeper. Collect Valorant gameplay samples. Set up LLaVA locally.
Person 5: Brand identity. Landing page. Design the radar chart component.
Person 6: Identify 20 target schools. Send 10 outreach emails. Research Squid Academy partners.
```
