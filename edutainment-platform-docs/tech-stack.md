# Tech Stack

## Frontend

### School Dashboard
- Framework: Next.js 14 (App Router)
- Language: TypeScript
- Charts: Recharts or Nivo (radar/hexagon charts for profiles)
- Auth: NextAuth.js with school SSO (Google Workspace, Microsoft Entra)
- Deployment: Vercel

### Student Portal
- Same Next.js app, separate route group
- Shows personal profile, game history, learning recommendations

### Desktop App (Phase 2)
- Framework: Tauri (Rust + React) — ~5MB vs Electron's ~200MB
- Screen capture: Windows Graphics Capture API via Rust native module
- Purpose: game launcher + optional screen recorder
- Chosen over Electron for smaller install size and easier school IT approval

## Backend

### API Server
- Runtime: Node.js with Fastify or Python FastAPI
- Language: TypeScript (Node) or Python
- Auth: JWT tokens, school-scoped multi-tenancy
- REST API for dashboard, WebSocket for real-time session events

### Database
- Primary: PostgreSQL (Supabase for managed hosting)
- Schema: students, schools, sessions, events, profiles, recommendations
- Minimum 10 sessions before generating a profile

### Object Storage
- Cloudflare R2 — video recordings, processed frames
- Cost: $0.015/GB/month
- Policy: delete raw video after event extraction (privacy compliance)

### Cache
- Redis — session state, rate limiting, API response cache

## AI / ML

### Local Inference (video gatekeeper)
- YOLO v8 — game UI element detection
- OpenCV — frame diff, HP bar color reading, template matching
- LLaVA 7B via Ollama — mid-tier frame analysis (local GPU)
- Hardware: 1× A10G or RTX 4090 instance (~$0.60–1.00/hr spot)

### Cloud Inference (deep frame analysis)
- Gemini 2.0 Flash — primary vision model ($0.10/1M tokens)
- GPT-4o — fallback for edge cases
- Anthropic Claude — profile narrative generation, learning recommendations

### Profile Engine
- Python service
- Aggregates events → 6 dimension scores
- Runs nightly batch job per student
- Minimum data threshold: 10 matches/sessions

## Game Data APIs

| API | Cost | Data |
|---|---|---|
| Riot Games API (LoL) | Free | Per-match, 100 req/2min |
| Riot Games API (Valorant) | Free (prod key required) | Per-match |
| Steam Web API (CS2) | Free | Lifetime stats |
| FACEIT API | Free | Per-match CS2 |

## Infrastructure

### Hosting
- Vercel — frontend (free tier for MVP)
- Supabase — PostgreSQL + auth (free tier for MVP)
- Fly.io or Railway — backend API server
- Cloudflare R2 — video/image storage
- Replicate or RunPod — GPU for local inference model

### DevOps
- GitHub Actions — CI/CD
- Docker — containerized backend and AI workers
- Sentry — error tracking

## Compliance Stack

- COPPA compliance — parental consent flow for under-13
- FERPA compliance (US schools) — student data handling
- GDPR (if EU schools) — data deletion, portability
- Video recordings: processed and purged, never stored long-term
- Role-based access: teachers see class data, parents see their child only

## Cost Summary (500 students, steady state)

| Component | Monthly Cost |
|---|---|
| Vercel (frontend) | $20 |
| Supabase (database) | $25 |
| Backend server | $30 |
| Cloudflare R2 (storage) | $27 |
| AI analysis (hybrid) | $86 |
| GPU instance (local model) | $50 |
| Riot/Steam APIs | $0 |
| **Total** | **~$238/month** |

At $10/student/month SaaS pricing:
- Revenue: $5,000/month
- Infrastructure: $238/month
- Gross margin: ~95% (excluding labor)
