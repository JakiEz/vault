# Platform Architecture

## Overview

An edutainment SaaS platform that sells to schools. Students play games (educational games built in-house and commercial titles like Valorant, League of Legends, CS2). Their gameplay behavior is captured, analyzed by AI, and categorized into a personality/learning-style profile. Schools receive reports; students receive personalized learning paths.

## Core Loop

1. Student plays games (edu games or commercial titles)
2. Behavior data captured (API pull or screen recording)
3. AI pipeline processes data into behavior events
4. Profile engine scores 6 behavior dimensions
5. School dashboard shows per-student and class-level reports
6. Student receives personalized extracurricular learning recommendations

## System Layers

### Student Layer
- Desktop app (Tauri) — game launcher + optional screen recorder
- Lightweight agent that captures screen frames and metadata
- OAuth account linking (Riot Games, Steam) for API-based tracking

### Data Ingestion Layer
- Riot Games API (League of Legends, Valorant) — free, post-match data
- Steam Web API (CS2) — free, lifetime aggregate stats
- FACEIT API — per-match CS2 data for competitive players
- In-game event logger — embedded in edu games built in-house
- Screen recording pipeline — optional deep behavior mode

### AI Analysis Pipeline
- Async batch processing (not real-time)
- Hybrid local + cloud inference model
- Frame sampler → local gatekeeper model → cloud vision model
- Output: structured behavior event log per session

### Backend API
- Node.js or FastAPI
- School management, student profiles, session data, reports
- PostgreSQL (structured data) + Cloudflare R2 (video/image storage)

### School Dashboard
- Next.js frontend
- Class-level radar chart overview
- Individual student profile with 6-dimension hexagon chart
- Learning recommendations mapped to profile
- Parent report export

## Deployment Phases

### Phase 1 — MVP (months 1–4)
- 1–2 educational games with embedded event logging
- Riot API integration (LoL match history)
- Basic profile engine (6 dimensions)
- School dashboard with student reports
- Manual consent flow for minors

### Phase 2 — Commercial Game Integration (months 5–7)
- Tauri desktop app with screen recorder
- Hybrid AI pipeline for video analysis (Valorant first)
- FACEIT API for CS2
- Refined profile model trained on real data

### Phase 3 — Scale
- Add CS2, LoL deeper signals
- Curriculum recommendations tied to profile
- API for schools to integrate into their LMS
- Screen recording as premium "Deep Behavior Mode"
