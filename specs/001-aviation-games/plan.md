# Implementation Plan: Aviation Games

**Branch**: `001-aviation-games` | **Date**: 2026-01-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-aviation-games/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a privacy-preserving aviation guessing game with two core modes: Airport Guessing (identify take-off/landing locations from photos) and Aircraft Identification (identify airline and aircraft model). The application prioritizes desktop/web deployment first, followed by iOS. Key technical challenges include EXIF stripping, photo management, dynamic difficulty scoring, open aviation data integration, and offline-capable gameplay. Privacy by design requires no tracking, minimal player identity, and transparent data handling.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript/React (web frontend), Swift 5.9 (iOS - Phase 2)  
**Primary Dependencies**: FastAPI (backend API), React 18 (web UI), SQLite (initial storage), Pillow (EXIF stripping), pytest (backend testing), Jest/React Testing Library (frontend testing)  
**Storage**: SQLite for initial deployment (photos as files, metadata in DB), extensible to PostgreSQL if scaling needed  
**Testing**: pytest (backend), Jest + React Testing Library (frontend), Playwright (E2E web), XCTest (iOS - Phase 2)  
**Target Platform**: Web browsers (Chrome, Firefox, Safari) + macOS desktop (Electron wrapper optional), iOS 15+ (Phase 2)  
**Project Type**: Web application (backend + frontend) initially, then mobile (iOS API client)  
**Performance Goals**: <3s app startup, <1s photo load, <500ms search response, <5s photo upload with EXIF stripping  
**Constraints**: <100MB memory during gameplay, offline-capable (10+ cached photos), no continuous tracking, WCAG AA compliant UI  
**Scale/Scope**: 500+ airports at launch, support 100+ concurrent players initially, ~50 API endpoints, ~30 UI screens/components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Privacy by Design ✅

- ✅ No third-party analytics or tracking scripts (FastAPI backend controls all data)
- ✅ EXIF stripping mandatory (Pillow library chosen specifically for this)
- ✅ Minimal player identity (username + score only in data model)
- ✅ No behavioral profiling infrastructure in design
- ✅ Transparent data handling (all endpoints documented in OpenAPI)

### II. Public Interest First ✅

- ✅ Non-commercial deployment (no monetization endpoints)
- ✅ Open data sources (OurAirports, OpenFlights selected for research)
- ✅ Accessible to all (web-first approach, no paywalls)
- ✅ Solves real problem (aviation education + entertainment)

### III. Accessibility as Constraint ✅

- ✅ WCAG AA compliance (4.5:1 contrast ratios in UI design)
- ✅ Works without JavaScript for core content (progressive enhancement)
- ✅ Offline-capable (Service Worker + IndexedDB caching)
- ✅ Screen reader compatible (semantic HTML + ARIA labels)
- ✅ Low bandwidth friendly (<100KB initial bundle, lazy loading)

### IV. Radical Simplicity ✅

- ✅ Minimal dependencies (FastAPI, React, SQLite - all justified)
- ✅ No unnecessary frameworks (no Redux unless complexity demands it)
- ✅ Start simple: SQLite before PostgreSQL, files before object storage
- ✅ YAGNI enforced (no premature optimization, no unused features)

### V. Openness in Practice ✅

- ✅ Open source license (MIT or Apache 2.0)
- ✅ Open aviation data sources (documented in research.md)
- ✅ OpenAPI specification for all endpoints
- ✅ Documented decision-making (this plan + research artifacts)

### VI. Specification-Driven Development ✅

- ✅ Specification complete before this plan
- ✅ Tests written before implementation (TDD in tasks)
- ✅ Data model designed before code (data-model.md in Phase 1)
- ✅ Contracts defined before implementation (contracts/ in Phase 1)

### VII. Environmental Sustainability ✅

- ✅ Minimal resource consumption (<100KB initial bundle, lazy loading, Service Worker caching)
- ✅ Dependencies evaluated for efficiency (Pillow selected for performance, no bloated libraries)
- ✅ Caching and compression prioritized (5-min API cache, WebP 80% quality target)
- ✅ Data lifecycle includes archival/deletion policies (90-day game round retention, 7-day expired cleanup)
- ✅ Performance targets minimize server load (<500ms API response, <3s startup)

**Constitution Status**: ✅ PASSED — All seven principles satisfied, no violations requiring justification

## Project Structure

### Documentation (this feature)

```text
specs/001-aviation-games/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── openapi.yaml     # Backend API specification
│   └── types.ts         # Frontend TypeScript types
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/          # SQLAlchemy models (Player, Photo, Airport, etc.)
│   ├── services/        # Business logic (photo processing, scoring, difficulty)
│   ├── api/             # FastAPI routers (gameplay, upload, leaderboard)
│   ├── data/            # Aviation database loaders (airports, airlines, aircraft)
│   └── utils/           # EXIF stripping, distance calculation, validation
├── tests/
│   ├── unit/            # Unit tests for services and utilities
│   ├── integration/     # API endpoint tests
│   └── contract/        # OpenAPI contract validation tests
├── migrations/          # Alembic database migrations
└── requirements.txt

frontend/
├── src/
│   ├── components/      # React components (PhotoViewer, AirportSearch, ScoreDisplay)
│   ├── pages/           # Page-level components (GamePage, UploadPage, LeaderboardPage)
│   ├── services/        # API client, caching layer, offline sync
│   ├── styles/          # CSS modules (WCAG AA compliant colors)
│   └── types/           # TypeScript interfaces (from contracts/)
├── public/              # Static assets, service worker
├── tests/
│   ├── unit/            # Component unit tests (Jest + RTL)
│   └── e2e/             # End-to-end tests (Playwright)
└── package.json

storage/
├── photos/              # Uploaded aviation photos (EXIF stripped)
└── cache/               # Temporary processing directory

docs/
├── api/                 # API documentation (generated from OpenAPI)
├── architecture/        # Architecture decision records
└── deployment/          # Deployment guides
```

**Structure Decision**: Web application (Option 2) selected. Backend and frontend are separate concerns with clear boundaries. Backend handles privacy-critical operations (EXIF stripping, scoring), frontend focuses on accessibility and offline capability. This separation supports the phased deployment: web first (both backend + frontend), then iOS (iOS app + existing backend). SQLite database and file storage keep initial deployment simple, extensible to PostgreSQL and object storage if needed.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations requiring justification. All design choices align with constitutional principles.

---

## Phases

### Phase 0: Research ✅ COMPLETE

**Objective**: Resolve all [NEEDS CLARIFICATION] markers and establish technical foundations

**Deliverable**: [research.md](research.md)

**Key Decisions Made**:
1. **Aviation Data Sources**: OurAirports (CC0, primary) + OpenFlights (ODbL, airlines) + OpenSky Network (CC BY-SA, aircraft)
2. **EXIF Stripping**: Pillow library with fail-loud verification (never store unverified photos)
3. **Scoring System**: Server-side state machine, progressive 3-attempt scoring (10/5/3/0 points), anti-cheat tokens
4. **Difficulty Multiplier**: Background worker with hourly recalculation, 1/success_rate formula, capped at 3x, activates at ≥500 photos AND ≥100 players
5. **Photo Seeding**: Semi-automated Flickr/Wikimedia scraping with manual curation, CC-licensed photos only
6. **Frontend Stack**: React 18 + TypeScript + Vite, offline PWA with Service Worker + IndexedDB, Tailwind CSS for WCAG AA
7. **Testing Strategy**: TDD with contract tests (OpenAPI), integration tests (pytest), E2E tests (Playwright), accessibility audits (jest-axe)

**Constitution Re-Check**: ✅ All decisions maintain privacy-by-design, simplicity, and openness principles

---

### Phase 1: Design & Contracts ✅ COMPLETE

**Objective**: Define data model, API contracts, and developer onboarding before writing code

**Deliverables**:
- [data-model.md](data-model.md) — Entity relationships, validation rules, state machines
- [contracts/openapi.yaml](contracts/openapi.yaml) — Backend API specification (OpenAPI 3.1)
- [contracts/types.ts](contracts/types.ts) — TypeScript type definitions for frontend
- [quickstart.md](quickstart.md) — Developer guide for implementation

**Data Model Summary**:
- 10 entities: Player, Photo, Airport, Airline, Aircraft, GameRound, Guess, PhotoDifficulty, PhotoAttribution, LeaderboardEntry
- Privacy constraints: No location tracking, EXIF stripped, minimal player identity (username + score only)
- State machine: GameRound lifecycle (attempt_1 → attempt_2 → attempt_3 → completed)
- 10 indexes for performance: leaderboard queries, photo selection, airport search

**API Contract Summary**:
- 8 endpoints: POST /game/start, POST /game/guess, POST /photos/upload, GET /airports, GET /airports/{icao}, GET /leaderboard, GET /player/{player_id}, GET /health
- Progressive feedback: Attempt 1 (correct/incorrect), Attempt 2 (+ distance in km/mi), Attempt 3 (+ country hint + revealed airport)
- Anti-cheat: Unique round tokens (UUID v4), 30-minute expiration, rate limiting

**Constitution Re-Check**: ✅ Data model and API contracts maintain all constitutional principles. EXIF stripping enforced, no tracking infrastructure, minimal complexity.

---

### Phase 2: Tasks Breakdown ⏳ PENDING

**Objective**: Break down specification into testable, implementable tasks organized by user story priority

**Trigger**: Run `/speckit.tasks` command

**Deliverable**: [tasks.md](tasks.md) — Task breakdown with priority, estimates, dependencies

**Scope**:
- User Story 1 (Airport Guessing Game) — P1 MVP
- User Story 2 (Aircraft Identification) — P2
- User Story 3 (Photo Upload + Attribution) — P2
- User Story 4 (Leaderboard + Difficulty) — P3
- Non-functional requirements (accessibility, offline, performance) — Cross-cutting

**Exit Criteria**:
- All functional requirements mapped to tasks
- Each task testable (success criteria from spec)
- Dependencies identified (e.g., EXIF stripping before photo upload)
- Priority aligns with user story priority (P1 → P2 → P3)

---

## Implementation Workflow

**After Phase 2 complete**, follow TDD for each task:

```
1. Write test for user story requirement (from spec.md)
   ↓
2. Run test suite → ❌ RED (test fails)
   ↓
3. Implement minimum code to pass → ✅ GREEN
   ↓
4. Refactor for simplicity/clarity → 🔄 REFACTOR
   ↓
5. Commit with spec reference: "feat(gameplay): implement 3-attempt scoring [spec:001-aviation-games:FR-002]"
   ↓
6. Next task →
```

**Checkpoints**:
- After each user story: Run full test suite + accessibility audit
- Before merge: Constitution re-check (no tracking added, privacy maintained)
- After merge: Update quickstart.md if API or architecture changes

---

## Next Steps

1. ✅ Constitution created and ratified (v1.0.0)
2. ✅ Feature specification complete ([spec.md](spec.md))
3. ✅ Implementation plan complete (this file)
4. ✅ Phase 0 Research complete ([research.md](research.md))
5. ✅ Phase 1 Design complete ([data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md))
6. ⏳ **Next**: Run `/speckit.tasks` to generate tasks breakdown
7. ⏳ **Then**: Begin implementation following TDD workflow

---

**Plan Status**: ✅ COMPLETE — Ready for task generation (`/speckit.tasks` command)
