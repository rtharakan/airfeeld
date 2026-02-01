# Implementation Plan: Release Preparation & Next Iteration Planning

**Branch**: `002-release-preparation` | **Date**: 2026-02-01 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/002-release-preparation/spec.md`

## Summary

This plan prepares Airfeeld for its initial public release by ensuring the core gameplay loop is functional, tested, and constitutional. Primary objectives: (1) Fix unit/integration tests to match current API signatures, (2) Complete frontend game UI components, (3) Implement content moderation pipeline, (4) Seed photo pool with 100+ images, (5) Validate privacy guarantees through testing, (6) Create structured roadmap for future iterations (P2/P3 features). Technical approach: systematic testing validation, component completion, data seeding automation, and privacy-preserving moderation using local models.

## Technical Context

**Language/Version**: Python 3.11+ (backend), Node.js 18+ (frontend), TypeScript (frontend)  
**Primary Dependencies**: FastAPI (backend), React 18+ (frontend), SQLAlchemy (ORM), Tailwind CSS (styling), Vite (build)  
**Storage**: SQLite database (backend/data/airfeeld.db), local filesystem (storage/photos/), IndexedDB (future offline support)  
**Testing**: pytest (backend unit/integration), Playwright (future E2E), Lighthouse (future accessibility)  
**Target Platform**: Web application (Linux/macOS/Windows servers, modern browsers)  
**Project Type**: Web application (separate backend + frontend)  
**Performance Goals**: API response < 500ms, page load < 3s on 3G, image size < 200KB, frontend bundle < 500KB gzipped  
**Constraints**: WCAG AA accessibility, no third-party tracking, EXIF stripping validated, PoW + rate limiting for DoS protection  
**Scale/Scope**: MVP with 100+ seed photos, support for 100+ concurrent players, leaderboard top 100, expandable to 1000+ photos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**✅ Privacy by Design**
- Data minimization: Only storing username, scores, game state (no emails, no profiles, no behavioral tracking)
- EXIF stripping: All location metadata removed from uploaded photos before storage
- No third-party analytics: No external tracking scripts or data sharing
- Ephemeral rate limiting: IP addresses used only for DoS protection, not logged long-term
- Session tokens: httpOnly, secure, SameSite=Strict cookies only
- **Status**: PASS - All requirements aligned with existing implementation

**✅ Public Interest First**
- Core gameplay accessible to all: No paywalls, no premium tiers, no advertising
- Community contributions: User-uploaded photos expand game pool voluntarily
- Educational value: Geography learning through gameplay
- No social manipulation: No engagement optimization, no dark patterns, no infinite scroll
- **Status**: PASS - Project serves users, not markets

**✅ Accessibility as Constraint**
- WCAG AA compliance: 4.5:1 contrast, keyboard navigation, screen reader support
- Progressive enhancement: Core gameplay works without JavaScript where possible
- Responsive design: Mobile and desktop support
- Clear UI: Minimalist design, semantic HTML, proper ARIA labels
- **Status**: REQUIRES VALIDATION - Accessibility audit needed (automated tools + manual testing)

**✅ Radical Simplicity**
- Minimal dependencies: FastAPI, React, SQLite (no microservices, no complex architectures)
- No premature optimization: Start with simple solutions, refactor only when needed
- YAGNI enforced: Difficulty multiplier system deferred until threshold met (500+ photos, 100+ players)
- Refactoring encouraged: Code clarity prioritized over cleverness
- **Status**: PASS - Architecture remains simple, no unnecessary complexity added

**✅ Openness in Practice**
- MIT License: Code is freely available and modifiable
- Public repository: Development process visible on GitHub
- Decision transparency: Specifications document "why" not just "what"
- Contribution welcome: Open to community input respecting constitutional principles
- **Status**: PASS - Project is open source and transparent

**✅ Specification-Driven Development**
- Feature spec complete: User scenarios, acceptance criteria, requirements documented
- Research phase planned: Open questions identified for resolution
- Design phase planned: Data models, contracts, quickstart to be generated
- Tests before implementation: Contract tests, integration tests, unit tests prioritized
- **Status**: PASS - Following SDD workflow as required

**✅ Environmental Sustainability** (added in Constitution v1.1.0)
- Minimal bundle size: Target < 500KB gzipped frontend
- Image optimization: WebP format, compression, lazy loading
- Efficient queries: Database indexes on frequently accessed fields
- Renewable hosting: Provider selection TBD (must meet sustainability criteria)
- **Status**: REQUIRES RESEARCH - Hosting provider options need evaluation

**❌ Gate Violations: NONE**

**✅ All Gates Pass**: Proceeding to Phase 0 research

**Re-evaluation Trigger**: After Phase 1 (design complete), re-check accessibility validation and hosting provider alignment.

## Project Structure

### Documentation (this feature)

```text
specs/002-release-preparation/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated - minimal changes expected)
├── quickstart.md        # Phase 1 output (to be generated - testing guide)
├── contracts/           # Phase 1 output (to be generated - test contracts)
└── tasks.md             # Phase 2 output (to be generated by /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/          # [EXISTING] SQLAlchemy models (player, game_round, photo, etc.)
│   ├── services/        # [EXISTING] Business logic (game_service, photo_service, etc.)
│   ├── api/             # [EXISTING] FastAPI endpoints (players, games, photos, leaderboard)
│   ├── middleware/      # [EXISTING] Rate limiting, headers, PoW validation
│   ├── utils/           # [EXISTING] Errors, logging
│   └── workers/         # [NEW] Background tasks for content moderation
├── tests/
│   ├── unit/            # [UPDATE] Fix existing unit tests to match API changes
│   ├── integration/     # [NEW] Add API workflow tests (registration, gameplay, leaderboard)
│   └── contract/        # [NEW] Add OpenAPI contract validation tests
├── scripts/             # [NEW] Data seeding scripts (photos, airports)
├── data/                # [EXISTING] SQLite database storage
└── requirements.txt     # [UPDATE] Add testing dependencies

frontend/
├── src/
│   ├── components/      # [UPDATE] Complete GameRound, RegisterForm, Leaderboard
│   ├── pages/           # [EXISTING] HomePage, PlayPage, LeaderboardPage, UploadPage
│   ├── api/             # [EXISTING] API client for backend communication
│   ├── contexts/        # [EXISTING] PlayerContext for session management
│   └── utils/           # [EXISTING] PoW utility
├── tests/               # [NEW] Component tests (future)
└── package.json         # [UPDATE] Add testing dependencies

storage/
├── photos/              # [EXISTING] Uploaded photo storage (EXIF-stripped)
└── cache/               # [EXISTING] Temporary cache for processing

docs/
├── api-reference.md     # [EXISTING] API documentation
└── deployment.md        # [UPDATE] Add release checklist and hosting guidance

specs/
├── 001-aviation-games/  # [EXISTING] Original feature specification
└── 002-release-preparation/ # [NEW] This specification
```

**Structure Decision**: Existing web application structure (backend + frontend) is appropriate and follows constitutional simplicity principles. No architectural changes needed. Focus on completing gaps within existing structure: backend tests, frontend components, data seeding scripts, and content moderation workers.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations detected.** All planned work aligns with constitutional principles:
- No new external dependencies added
- No architectural complexity introduced
- Simplicity maintained through completing existing patterns
- Privacy, accessibility, and openness requirements met
