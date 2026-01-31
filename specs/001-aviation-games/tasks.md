# Tasks: Aviation Games

**Feature**: Aviation Games  
**Branch**: `001-aviation-games`  
**Date**: 2026-01-31  
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [data-model.md](data-model.md), [contracts/](contracts/)

This document breaks down the implementation into testable, independently deliverable tasks organized by user story priority. Each phase can be implemented and tested autonomously.

---

## Task Format

```
- [ ] [TaskID] [P?] [Story?] Description with file path
```

- **[P]**: Parallelizable (different files, no blocking dependencies)
- **[Story]**: User story association (US1, US2, US3, US4)
- File paths follow web app structure: `backend/src/`, `frontend/src/`

---

## Phase 1: Setup

**Purpose**: Initialize project structure and tooling

- [ ] T001 Create backend directory structure (backend/src/{models,services,api,data,utils})
- [ ] T002 Create frontend directory structure (frontend/src/{components,pages,services,styles,types})
- [ ] T003 Create storage directories (storage/{photos,cache})
- [ ] T004 Initialize Python 3.11 backend project with FastAPI in backend/requirements.txt
- [ ] T005 Initialize React 18 + TypeScript frontend project with Vite in frontend/package.json
- [ ] T006 [P] Configure pytest for backend in backend/pytest.ini
- [ ] T007 [P] Configure Jest + React Testing Library for frontend in frontend/jest.config.js
- [ ] T008 [P] Configure Python linting (ruff) and formatting (black) in backend/pyproject.toml
- [ ] T009 [P] Configure TypeScript linting (eslint) and formatting (prettier) in frontend/.eslintrc.json
- [ ] T010 [P] Setup Tailwind CSS with WCAG AA color palette in frontend/tailwind.config.js
- [ ] T011 Create .gitignore for backend (venv/, __pycache__/, .pytest_cache/)
- [ ] T012 Create .gitignore for frontend (node_modules/, dist/, .env.local)
- [ ] T013 Initialize SQLite database schema with Alembic in backend/migrations/

---

## Phase 2: Foundational

**Purpose**: Core infrastructure that blocks all user story implementation

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T014 Implement database connection and session management in backend/src/database.py
- [ ] T015 Create base SQLAlchemy model class in backend/src/models/base.py
- [ ] T016 Setup FastAPI application with CORS and error handlers in backend/src/main.py
- [ ] T017 Implement health check endpoint in backend/src/api/system.py
- [ ] T018 [P] Create API client service in frontend/src/services/api.ts
- [ ] T019 [P] Implement error handling utilities in backend/src/utils/errors.py
- [ ] T020 [P] Implement logging configuration in backend/src/utils/logging.py
- [ ] T021 Setup environment configuration in backend/src/config.py
- [ ] T022 Create TypeScript types from OpenAPI spec in frontend/src/types/api.ts
- [ ] T023 [P] Implement Haversine distance calculation utility in backend/src/utils/distance.py
- [ ] T024 [P] Implement EXIF stripping utility with Pillow in backend/src/utils/exif.py
- [ ] T025 Create validation schemas with Pydantic in backend/src/utils/validation.py

**Checkpoint**: Foundation complete - user story implementation begins

---

## Phase 2.5: Security Infrastructure

**Purpose**: Account security, bot prevention, and database protection  
**CRITICAL**: Required before player account creation in User Story 1

### Account Security

- [ ] T111 [P] Create ProofOfWorkChallenge model in backend/src/models/pow_challenge.py
- [ ] T112 [P] Create RateLimitEntry model in backend/src/models/rate_limit.py
- [ ] T113 [P] Create AuditLogEntry model in backend/src/models/audit_log.py
- [ ] T114 Create Alembic migration for security entities in backend/migrations/versions/001a_security.py
- [ ] T115 Implement ProofOfWorkService with SHA-256 verification in backend/src/services/pow_service.py
- [ ] T116 Implement RateLimitService with IP hash tracking in backend/src/services/rate_limit_service.py
- [ ] T117 Implement AuditLogService for security event logging in backend/src/services/audit_service.py
- [ ] T118 Implement POST /players/challenge endpoint in backend/src/api/players.py
- [ ] T119 Implement POST /players/register with PoW validation in backend/src/api/players.py
- [ ] T120 Implement GET /players/{id}/export (GDPR) in backend/src/api/players.py
- [ ] T121 Implement DELETE /players/{id} (GDPR) in backend/src/api/players.py
- [ ] T122 Add rate limit middleware to FastAPI in backend/src/middleware/rate_limit.py
- [ ] T123 Add X-RateLimit-* headers to all responses in backend/src/middleware/headers.py

### Database Security

- [ ] T124 Configure SQLite AES-256 encryption with SQLCipher in backend/src/database.py
- [ ] T125 Implement parameterized queries audit in backend/tests/security/test_sql_injection.py
- [ ] T126 Configure TLS 1.3 for API connections in backend/src/config.py
- [ ] T127 Implement audit log retention policy (2 years) in backend/src/workers/cleanup_worker.py

### Frontend Security

- [ ] T128 [P] Create ProofOfWorkSolver utility in frontend/src/utils/proofOfWork.ts
- [ ] T129 [P] Create RateLimitHandler with retry logic in frontend/src/services/rateLimitHandler.ts
- [ ] T130 Create AccountRegistration component with PoW in frontend/src/components/AccountRegistration.tsx
- [ ] T131 Create AccountDeletion component (GDPR) in frontend/src/components/AccountDeletion.tsx
- [ ] T132 Create DataExport component (GDPR) in frontend/src/components/DataExport.tsx

### Security Tests

- [ ] T133 [P] Unit test for PoW verification in backend/tests/unit/test_pow_service.py
- [ ] T134 [P] Integration test for rate limiting in backend/tests/integration/test_rate_limit.py
- [ ] T135 [P] Penetration test for SQL injection in backend/tests/security/test_sql_injection.py
- [ ] T136 [P] E2E test for account registration flow in frontend/tests/e2e/registration.spec.ts

**Checkpoint**: Security infrastructure complete - account creation secured

---

## Phase 3: User Story 1 - Airport Guessing Game (Priority: P1)

**Goal**: Players can view aviation photos and guess airports using a 3-attempt progressive scoring system

**Independent Test**: Load pre-seeded photo, start game, submit guesses across 3 attempts, verify feedback (correct/distance/country hint) and scoring (10/5/3/0 points)

### Implementation for User Story 1

- [ ] T026 [P] [US1] Create Player model in backend/src/models/player.py
- [ ] T027 [P] [US1] Create Photo model in backend/src/models/photo.py
- [ ] T028 [P] [US1] Create Airport model in backend/src/models/airport.py
- [ ] T029 [P] [US1] Create GameRound model with state machine in backend/src/models/game_round.py
- [ ] T030 [P] [US1] Create Guess model in backend/src/models/guess.py
- [ ] T031 [US1] Create Alembic migration for User Story 1 entities in backend/migrations/versions/001_user_story_1.py
- [ ] T032 [US1] Implement PlayerService for user management in backend/src/services/player_service.py
- [ ] T033 [US1] Implement GameService for round state machine in backend/src/services/game_service.py
- [ ] T034 [US1] Implement ScoringService for 3-attempt logic in backend/src/services/scoring_service.py
- [ ] T035 [US1] Implement POST /game/start endpoint in backend/src/api/gameplay.py
- [ ] T036 [US1] Implement POST /game/guess endpoint with progressive feedback in backend/src/api/gameplay.py
- [ ] T037 [US1] Implement GET /airports search endpoint in backend/src/api/data.py
- [ ] T038 [US1] Implement GET /airports/{icao} detail endpoint in backend/src/api/data.py
- [ ] T039 [P] [US1] Create PhotoViewer component in frontend/src/components/PhotoViewer.tsx
- [ ] T040 [P] [US1] Create AirportSearch component with autocomplete in frontend/src/components/AirportSearch.tsx
- [ ] T041 [P] [US1] Create GuessResult component with attempt feedback in frontend/src/components/GuessResult.tsx
- [ ] T042 [P] [US1] Create ScoreDisplay component in frontend/src/components/ScoreDisplay.tsx
- [ ] T043 [US1] Create GamePage with 3-attempt flow in frontend/src/pages/GamePage.tsx
- [ ] T044 [US1] Implement game state management in frontend/src/services/gameState.ts
- [ ] T045 [US1] Add keyboard navigation support (Enter to submit) in frontend/src/components/AirportSearch.tsx
- [ ] T046 [US1] Add ARIA labels and screen reader support to game components

**Checkpoint**: User Story 1 complete - MVP functional

---

## Phase 4: User Story 2 - Photo Upload (Priority: P2)

**Goal**: Users can upload aviation photos with EXIF stripping and airport association

**Independent Test**: Upload image file with EXIF data, verify metadata stripped, associate with airport, confirm photo enters game pool

### Implementation for User Story 2

- [ ] T047 [P] [US2] Create PhotoAttribution model in backend/src/models/photo_attribution.py
- [ ] T048 [US2] Create Alembic migration for photo attribution in backend/migrations/versions/002_user_story_2.py
- [ ] T049 [US2] Implement PhotoUploadService with EXIF verification in backend/src/services/photo_upload_service.py
- [ ] T050 [US2] Implement validation for file format and dimensions in backend/src/utils/validation.py
- [ ] T051 [US2] Implement POST /photos/upload endpoint in backend/src/api/content.py
- [ ] T052 [P] [US2] Create PhotoUpload component with drag-and-drop in frontend/src/components/PhotoUpload.tsx
- [ ] T053 [P] [US2] Create AttributionForm component in frontend/src/components/AttributionForm.tsx
- [ ] T054 [US2] Create UploadPage with airport selection in frontend/src/pages/UploadPage.tsx
- [ ] T055 [US2] Implement upload progress tracking in frontend/src/services/uploadService.ts
- [ ] T056 [US2] Add file type validation and preview in frontend/src/components/PhotoUpload.tsx

**Checkpoint**: User Story 2 complete - user contributions enabled

---

## Phase 4.5: Content Moderation Pipeline

**Purpose**: Multi-layer content moderation for uploaded photos  
**CRITICAL**: Required before production to ensure aviation-only, appropriate content

### Moderation Infrastructure

- [ ] T137 [P] Create ModerationQueueEntry model in backend/src/models/moderation_queue.py
- [ ] T138 [P] Create PhotoFlag model in backend/src/models/photo_flag.py
- [ ] T139 Create Alembic migration for moderation entities in backend/migrations/versions/002a_moderation.py
- [ ] T140 Implement magic number validation (JPEG/PNG/WebP) in backend/src/utils/file_validation.py
- [ ] T141 Implement pHash duplicate detection (>95% similarity) in backend/src/services/phash_service.py
- [ ] T142 Integrate PhotoDNA API for CSAM detection in backend/src/services/photodna_service.py
- [ ] T143 Implement aviation histogram analysis in backend/src/services/aviation_classifier.py
- [ ] T144 Implement AI-generated image detection in backend/src/services/ai_detection_service.py
- [ ] T145 Implement OCR for text detection in backend/src/services/ocr_service.py
- [ ] T146 Create ModerationPipeline orchestrator in backend/src/services/moderation_pipeline.py

### Moderation Endpoints

- [ ] T147 Implement POST /photos/{id}/flag endpoint in backend/src/api/moderation.py
- [ ] T148 Implement internal GET /moderation/queue endpoint in backend/src/api/moderation.py
- [ ] T149 Implement internal POST /moderation/queue/{id}/decision endpoint in backend/src/api/moderation.py
- [ ] T150 Add moderation status to photo upload response in backend/src/api/content.py

### Moderation Frontend

- [ ] T151 [P] Create PhotoFlagButton component in frontend/src/components/PhotoFlagButton.tsx
- [ ] T152 [P] Create FlagReasonModal component in frontend/src/components/FlagReasonModal.tsx
- [ ] T153 Add flag functionality to GamePage in frontend/src/pages/GamePage.tsx

### Moderation Tests

- [ ] T154 [P] Unit test for magic number validation in backend/tests/unit/test_file_validation.py
- [ ] T155 [P] Unit test for pHash duplicate detection in backend/tests/unit/test_phash_service.py
- [ ] T156 [P] Integration test for moderation pipeline in backend/tests/integration/test_moderation_pipeline.py
- [ ] T157 [P] E2E test for photo flag flow in frontend/tests/e2e/photo-flag.spec.ts

**Checkpoint**: Content moderation pipeline complete - safe user uploads

---

## Phase 5: User Story 3 - Leaderboards (Priority: P3)

**Goal**: Players view global leaderboards showing top scores without social features

**Independent Test**: Pre-populate player scores, verify leaderboard displays correctly ordered rankings with usernames and scores only

### Implementation for User Story 3

- [ ] T057 [US3] Create LeaderboardEntry model in backend/src/models/leaderboard_entry.py
- [ ] T058 [US3] Create Alembic migration for leaderboard in backend/migrations/versions/003_user_story_3.py
- [ ] T059 [US3] Implement LeaderboardService with ranking calculation in backend/src/services/leaderboard_service.py
- [ ] T060 [US3] Implement GET /leaderboard endpoint in backend/src/api/leaderboard.py
- [ ] T061 [US3] Implement GET /player/{player_id} endpoint in backend/src/api/leaderboard.py
- [ ] T062 [P] [US3] Create LeaderboardTable component in frontend/src/components/LeaderboardTable.tsx
- [ ] T063 [P] [US3] Create PlayerStats component in frontend/src/components/PlayerStats.tsx
- [ ] T064 [US3] Create LeaderboardPage in frontend/src/pages/LeaderboardPage.tsx
- [ ] T065 [US3] Implement leaderboard caching in frontend/src/services/cacheService.ts

**Checkpoint**: User Story 3 complete - competitive element added

---

## Phase 6: User Story 4 - Difficulty Multiplier (Priority: P3)

**Goal**: Dynamic difficulty scoring based on community success rate (activates at 500+ photos, 100+ players)

**Independent Test**: Simulate 500+ photos and 100+ players with varying success rates, verify multipliers calculate correctly (1.0-3.0x), confirm retroactive score adjustment

### Implementation for User Story 4

- [ ] T066 [US4] Create PhotoDifficulty model in backend/src/models/photo_difficulty.py
- [ ] T067 [US4] Create Alembic migration for difficulty system in backend/migrations/versions/004_user_story_4.py
- [ ] T068 [US4] Implement DifficultyService with multiplier calculation in backend/src/services/difficulty_service.py
- [ ] T069 [US4] Implement background worker for hourly recalculation in backend/src/workers/difficulty_worker.py
- [ ] T070 [US4] Update ScoringService to apply multipliers in backend/src/services/scoring_service.py
- [ ] T071 [US4] Implement retroactive score adjustment in backend/src/services/leaderboard_service.py
- [ ] T072 [US4] Add difficulty indicator to photo metadata in frontend/src/components/PhotoViewer.tsx

**Checkpoint**: User Story 4 complete - dynamic difficulty live

---

## Phase 7: Data Seeding

**Purpose**: Populate databases with open aviation data and initial photos

- [ ] T073 Implement OurAirports data loader in backend/src/data/airports_loader.py
- [ ] T074 Implement OpenFlights airline data loader in backend/src/data/airlines_loader.py
- [ ] T075 Implement aircraft model data loader in backend/src/data/aircraft_loader.py
- [ ] T076 Create data seeding script in backend/scripts/seed_data.py
- [ ] T077 Document Flickr/Wikimedia photo curation process in docs/photo-curation.md
- [ ] T078 Seed initial 500+ airport photos in storage/photos/

**Checkpoint**: Database populated with production data

---

## Phase 8: Offline Support

**Purpose**: Enable offline gameplay with cached photos

- [ ] T079 Implement Service Worker for offline caching in frontend/public/service-worker.js
- [ ] T080 Setup IndexedDB for local photo storage in frontend/src/services/offlineStorage.ts
- [ ] T081 Implement offline game queue in frontend/src/services/offlineQueue.ts
- [ ] T082 Add online/offline status indicator in frontend/src/components/OfflineIndicator.tsx
- [ ] T083 Implement background sync for pending uploads in frontend/src/services/syncService.ts

**Checkpoint**: Offline gameplay functional

---

## Phase 9: Testing

**Purpose**: Comprehensive test coverage

### Contract Tests

- [ ] T084 [P] Contract test for POST /game/start in backend/tests/contract/test_game_start.py
- [ ] T085 [P] Contract test for POST /game/guess in backend/tests/contract/test_game_guess.py
- [ ] T086 [P] Contract test for POST /photos/upload in backend/tests/contract/test_photo_upload.py
- [ ] T087 [P] Contract test for GET /airports in backend/tests/contract/test_airports.py
- [ ] T088 [P] Contract test for GET /leaderboard in backend/tests/contract/test_leaderboard.py

### Integration Tests

- [ ] T089 [P] Integration test for 3-attempt game flow in backend/tests/integration/test_full_game.py
- [ ] T090 [P] Integration test for EXIF stripping pipeline in backend/tests/integration/test_photo_upload.py
- [ ] T091 [P] Integration test for difficulty multiplier activation in backend/tests/integration/test_difficulty.py

### Frontend Tests

- [ ] T092 [P] Unit test for GamePage state management in frontend/src/pages/GamePage.test.tsx
- [ ] T093 [P] Unit test for AirportSearch autocomplete in frontend/src/components/AirportSearch.test.tsx
- [ ] T094 [P] Accessibility test for game flow with jest-axe in frontend/src/tests/accessibility.test.tsx

### E2E Tests

- [ ] T095 E2E test for complete game round with Playwright in frontend/tests/e2e/game-flow.spec.ts
- [ ] T096 E2E test for photo upload flow with Playwright in frontend/tests/e2e/upload-flow.spec.ts

**Checkpoint**: Test coverage complete

---

## Phase 10: Documentation & Polish

**Purpose**: Production-ready documentation and final polish

- [ ] T097 Create README.md with project overview and setup instructions
- [ ] T098 Create CONTRIBUTING.md with development guidelines
- [ ] T099 Create docs/api-reference.md from OpenAPI specification
- [ ] T100 Create docs/privacy-policy.md documenting data handling
- [ ] T101 Create docs/accessibility.md with WCAG AA compliance details
- [ ] T102 Create docs/deployment.md with production deployment guide
- [ ] T103 Add inline code documentation (docstrings) to all backend services
- [ ] T104 Add JSDoc comments to all frontend components
- [ ] T105 Create docs/architecture.md with system design diagrams
- [ ] T106 Perform final WCAG AA accessibility audit
- [ ] T107 Perform final privacy audit against constitution principles
- [ ] T108 Optimize frontend bundle size (target: <100KB initial)
- [ ] T109 Add performance monitoring to critical endpoints
- [ ] T110 Setup error tracking and logging infrastructure

**Checkpoint**: Production-ready application

---

## Dependencies & Parallel Execution

### User Story Independence

```
Phase 1 (Setup) → Phase 2 (Foundation)
                       ↓
    ┌──────────────────┼──────────────────┐
    ↓                  ↓                  ↓
Phase 3 (US1)    Phase 4 (US2)    Phase 5 (US3)
    ↓                  ↓                  ↓
    └──────────────────┼──────────────────┘
                       ↓
                 Phase 6 (US4)
                       ↓
    ┌──────────────────┼──────────────────┐
    ↓                  ↓                  ↓
Phase 7 (Data)  Phase 8 (Offline)  Phase 9 (Tests)
    ↓                  ↓                  ↓
    └──────────────────┼──────────────────┘
                       ↓
                Phase 10 (Docs)
```

### Parallel Opportunities

**Within User Story 1** (after models complete):
- T039-T042: All frontend components can be built in parallel
- T035-T038: Backend endpoints can be implemented in parallel

**Within User Story 2**:
- T052-T053: Frontend components can be built in parallel with T049 (backend service)

**Phase 9 Testing**:
- T084-T088: All contract tests can run in parallel
- T089-T091: All integration tests can run in parallel
- T092-T094: All frontend tests can run in parallel

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Phase 1 + Phase 2 + Phase 3 (User Story 1)** = Playable game

This delivers the core gameplay loop:
1. Player starts game
2. Photo displayed (EXIF stripped)
3. Player searches for airport
4. Progressive 3-attempt scoring
5. Feedback and score calculation

**Estimated Tasks**: T001-T046 (46 tasks)  
**Estimated Timeline**: 2-3 weeks for solo developer

### Incremental Delivery

After MVP:
- **Week 4**: Add User Story 2 (Photo Upload) for user contributions
- **Week 5**: Add User Story 3 (Leaderboards) for competition
- **Week 6**: Add User Story 4 (Difficulty Multiplier) when 500+ photos available
- **Week 7**: Add Offline Support for mobile-like experience
- **Week 8**: Complete Testing and Documentation

---

## TDD Workflow

For each task:

1. **Write test** for the requirement (from spec.md)
2. **Run test** → Should FAIL (red)
3. **Implement** minimum code to pass
4. **Run test** → Should PASS (green)
5. **Refactor** for simplicity and clarity
6. **Commit** with spec reference: `feat(gameplay): implement 3-attempt scoring [spec:001-aviation-games:FR-005]`

---

## Constitution Compliance

All tasks maintain constitutional principles:

- **Privacy by Design**: T024 (EXIF stripping), T026 (minimal player data), T117 (IP hash logging), T124 (AES-256 encryption)
- **Accessibility**: T010 (WCAG AA colors), T045-T046 (keyboard/screen reader)
- **Simplicity**: SQLite first (T013), progressive enhancement
- **Openness**: T073-T075 (open data sources), T097-T102 (documentation)
- **Safety**: T111-T127 (security infrastructure), T137-T157 (content moderation)
- **Environmental Sustainability**: T108 (bundle optimization), T065 (caching)

---

**Total Tasks**: 157  
**Parallelizable Tasks**: 52 (marked with [P])  
**Security Tasks**: 26 (T111-T136)  
**Moderation Tasks**: 21 (T137-T157)  
**MVP Tasks**: 46 (T001-T046)  
**Status**: Ready for implementation
