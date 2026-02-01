# Implementation Tasks: Release Preparation

**Feature**: 002-release-preparation  
**Branch**: `002-release-preparation`  
**Date**: 2026-02-01  
**Status**: Ready for implementation

---

## Task Organization

Tasks are organized by priority and dependency order. Complete P0 tasks before P1, and P1 before P2.

**Legend:**
- 🔴 P0 (Blocker) - Must complete for release
- 🟠 P1 (High) - Should complete before release
- 🟡 P2 (Medium) - Post-MVP enhancements
- 🟢 P3 (Low) - Future roadmap

---

## Phase: Backend Testing & Validation

### Task 1.1: Fix Unit Tests (Current API Signatures)

**Priority**: 🔴 P0  
**Estimate**: 2-3 hours  
**Dependencies**: None  
**Owner**: Backend team

**Description**: Update existing unit tests in `backend/tests/unit/` to match current API signatures and service implementations.

**Acceptance Criteria:**
- [X] All tests in `tests/unit/test_pow_service.py` pass
- [X] All tests in `tests/unit/test_profanity_filter.py` pass
- [X] All tests in `tests/unit/test_rate_limit_service.py` pass
- [X] No test warnings or deprecation messages
- [X] Test coverage >= 80% for critical services

**Steps:**
1. Run existing unit tests: `pytest tests/unit/ -v`
2. Identify failing tests and error messages
3. Update test signatures to match current service APIs
4. Fix mock return values to match actual implementations
5. Add missing test cases for new features (if any)
6. Verify all tests pass: `pytest tests/unit/ -v --cov=src/services`

**Files to modify:**
- `backend/tests/unit/test_pow_service.py`
- `backend/tests/unit/test_profanity_filter.py`
- `backend/tests/unit/test_rate_limit_service.py`

---

### Task 1.2: Add Integration Tests for API Workflows

**Priority**: 🔴 P0  
**Estimate**: 4-5 hours  
**Dependencies**: Task 1.1  
**Owner**: Backend team

**Description**: Create integration tests for critical user workflows: registration, gameplay, leaderboard.

**Acceptance Criteria:**
- [X] Test: Player registration workflow (challenge → register → session token)
- [X] Test: Full game round (start → guess → feedback → score update)
- [X] Test: Leaderboard query (returns sorted players)
- [X] Test: Photo selection (returns unseen photo for player)
- [X] All integration tests pass independently
- [X] Tests use isolated database (not production data)

**Steps:**
1. Create `backend/tests/integration/test_registration.py`
2. Implement TC-003 from test contracts (registration workflow)
3. Create `backend/tests/integration/test_gameplay.py`
4. Implement TC-004 from test contracts (gameplay workflow)
5. Create `backend/tests/integration/test_leaderboard.py`
6. Implement TC-005 from test contracts (leaderboard query)
7. Run all integration tests: `pytest tests/integration/ -v`

**Files to create:**
- `backend/tests/integration/test_registration.py`
- `backend/tests/integration/test_gameplay.py`
- `backend/tests/integration/test_leaderboard.py`

**Example test structure:**
```python
# test_registration.py
def test_player_registration_full_workflow(client, db):
    # Step 1: Get challenge
    # Step 2: Solve PoW
    # Step 3: Register player
    # Step 4: Verify response
    # Step 5: Verify database
```

---

### Task 1.3: Add Contract Tests (OpenAPI Validation)

**Priority**: 🔴 P0  
**Estimate**: 3-4 hours  
**Dependencies**: Task 1.2  
**Owner**: Backend team

**Description**: Create contract tests that validate API responses match OpenAPI specification.

**Acceptance Criteria:**
- [ ] All API endpoints have contract tests
- [ ] Response schemas validated against OpenAPI spec
- [ ] Required fields validated
- [ ] Data types validated
- [ ] HTTP status codes validated

**Steps:**
1. Create `backend/tests/contract/test_api_contracts.py`
2. Load OpenAPI spec from `specs/001-aviation-games/contracts/openapi.yaml`
3. For each endpoint: POST /players/register, POST /games/start, POST /games/{id}/guess, GET /players/leaderboard
4. Validate response schema matches OpenAPI definition
5. Test success cases (200, 201) and error cases (400, 404, 422)
6. Run contract tests: `pytest tests/contract/ -v`

**Files to create:**
- `backend/tests/contract/test_api_contracts.py`

**Libraries needed:**
```bash
pip install openapi-core jsonschema
```

---

### Task 1.4: Add EXIF Stripping Validation Test

**Priority**: 🔴 P0  
**Estimate**: 1-2 hours  
**Dependencies**: None  
**Owner**: Backend team

**Description**: Create test that validates EXIF data is fully stripped from uploaded photos.

**Acceptance Criteria:**
- [X] Test loads photo with EXIF data
- [X] Test verifies EXIF present before stripping
- [X] Test verifies EXIF absent after stripping
- [X] Test specifically checks GPS data removed
- [X] Test passes with 100% success rate

**Steps:**
1. Create test fixture: `backend/tests/fixtures/test_photo_with_exif.jpg` (include GPS data)
2. Create `backend/tests/unit/test_exif_stripping.py`
3. Implement TC-006 from test contracts
4. Use Pillow to verify EXIF removal
5. Run test: `pytest tests/unit/test_exif_stripping.py -v`

**Files to create:**
- `backend/tests/fixtures/test_photo_with_exif.jpg` (test fixture) 
- `backend/tests/unit/test_exif_stripping.py`

**Status**: ✅ COMPLETE - All 7 EXIF stripping tests passing. Uses piexif to create test images with GPS data.

---

## Phase: Content Moderation

### Task 2.1: Database Migration for Moderation Fields

**Priority**: 🟠 P1  
**Estimate**: 1 hour  
**Dependencies**: None  
**Owner**: Backend team

**Description**: Create Alembic migration to add content moderation and attribution fields to Photo model.

**Acceptance Criteria:**
- [ ] Migration file created: `003_add_moderation_fields.py`
- [ ] Migration adds all fields from data-model.md
- [ ] Migration includes indexes for performance
- [ ] Migration runs successfully: `alembic upgrade head`
- [ ] Downgrade works: `alembic downgrade -1`

**Steps:**
1. Create migration: `alembic revision -m "Add moderation fields"`
2. Add columns: `moderation_status`, `moderation_score`, `moderation_checked_at`, `rejection_reason`
3. Add attribution columns: `attribution_author`, `attribution_source`, `attribution_url`, `attribution_license`
4. Add indexes: `idx_photo_moderation_status`, `idx_player_total_score`, `idx_gameround_player_id`
5. Test migration: `alembic upgrade head`
6. Test rollback: `alembic downgrade -1 && alembic upgrade head`

**Files to create:**
- `backend/migrations/versions/003_add_moderation_fields.py`

---

### Task 2.2: Update Photo Model with Moderation Fields

**Priority**: 🟠 P1  
**Estimate**: 1 hour  
**Dependencies**: Task 2.1  
**Owner**: Backend team

**Description**: Update SQLAlchemy Photo model to include new moderation and attribution fields.

**Acceptance Criteria:**
- [ ] Photo model has all new fields from data-model.md
- [ ] Default values set correctly (moderation_status='pending')
- [ ] Validation rules implemented (score range 0-1, status enum)
- [ ] Model matches database schema

**Steps:**
1. Edit `backend/src/models/photo.py`
2. Add moderation fields with proper types and defaults
3. Add attribution fields
4. Add validation for moderation_status enum
5. Add validation for moderation_score range (0.0-1.0)
6. Test model: create instance and save to database

**Files to modify:**
- `backend/src/models/photo.py`

---

### Task 2.3: Implement NSFW Detection Service

**Priority**: 🟠 P1  
**Estimate**: 3-4 hours  
**Dependencies**: Task 2.2  
**Owner**: Backend team

**Description**: Implement local NSFW detection using Yahoo/Tumblr open-sourced model for content moderation.

**Acceptance Criteria:**
- [ ] NSFW model loaded and functional
- [ ] Service accepts image path, returns score (0.0-1.0)
- [ ] Auto-approve: score < 0.6
- [ ] Auto-reject: score >= 0.8
- [ ] Flag for review: 0.6 <= score < 0.8
- [ ] Service performance < 2 seconds per image (CPU)

**Steps:**
1. Install NSFW detection library: `pip install nsfw-detector` or equivalent
2. Create `backend/src/workers/moderation.py`
3. Implement `check_nsfw(image_path: str) -> dict` function
4. Load model in memory (lazy loading for performance)
5. Return structured result: `{"score": float, "status": str, "reason": str | None}`
6. Add unit tests (TC-008 from test contracts)
7. Test with sample images (safe, explicit, borderline)

**Files to create:**
- `backend/src/workers/moderation.py`
- `backend/tests/unit/test_nsfw_detection.py`

**Dependencies to add to requirements.txt:**
```
nsfw-detector==1.0.0  # Or equivalent NSFW detection library
tensorflow==2.x.x  # Required by NSFW model
```

---

### Task 2.4: Integrate Moderation into Photo Upload Workflow

**Priority**: 🟠 P1  
**Estimate**: 2-3 hours  
**Dependencies**: Task 2.3  
**Owner**: Backend team

**Description**: Update photo upload API to run moderation checks before saving photo.

**Acceptance Criteria:**
- [ ] Photo upload calls moderation service
- [ ] EXIF stripping happens BEFORE moderation
- [ ] Moderation status saved to database
- [ ] Rejected photos not added to game pool
- [ ] Flagged photos marked for manual review
- [ ] API returns appropriate error for rejected photos

**Steps:**
1. Edit `backend/src/api/photos.py` (photo upload endpoint)
2. Add moderation pipeline:
   - Validate file type/size
   - Check filename for profanity
   - Run NSFW detection
   - Strip EXIF data
   - Save to storage
   - Save metadata to database with moderation_status
3. Return 400 error if rejected: "Photo rejected due to explicit content"
4. Return 202 if flagged: "Photo submitted for review"
5. Test upload with various image types

**Files to modify:**
- `backend/src/api/photos.py`
- `backend/src/services/photo_service.py` (if upload logic is in service layer)

---

## Phase: Frontend Completion

### Task 3.1: Complete GameRound Component

**Priority**: 🔴 P0  
**Estimate**: 4-5 hours  
**Dependencies**: None  
**Owner**: Frontend team

**Description**: Finish GameRound component to display photo, accept guess, show results.

**Acceptance Criteria:**
- [ ] Photo displays responsively (mobile + desktop)
- [ ] Airport search with autocomplete works
- [ ] Guess submission triggers API call
- [ ] Loading state shown during submission
- [ ] Results display correct/incorrect, score, airport details
- [ ] No EXIF data visible in browser DevTools
- [ ] Keyboard navigation works (Tab, Enter)

**Steps:**
1. Edit `frontend/src/components/GameRound.tsx`
2. Implement photo display with responsive sizing
3. Implement airport search with autocomplete (use existing API)
4. Implement guess submission form
5. Add loading spinner during API call
6. Display results: correct/incorrect, score, airport name/country, distance (if attempt 2)
7. Style with Tailwind CSS (minimalist, accessible)
8. Test on mobile and desktop browsers

**Files to modify:**
- `frontend/src/components/GameRound.tsx`

**UI Structure:**
```tsx
<div className="game-round">
  <img src={photoUrl} alt="Airport photo" className="responsive-photo" />
  <AirportSearch onSelect={handleAirportSelect} />
  <button onClick={submitGuess} disabled={loading}>
    {loading ? 'Submitting...' : 'Submit Guess'}
  </button>
  {results && <ResultsDisplay results={results} />}
</div>
```

---

### Task 3.2: Complete RegisterForm Component

**Priority**: 🔴 P0  
**Estimate**: 2-3 hours  
**Dependencies**: None  
**Owner**: Frontend team

**Description**: Finish RegisterForm component to handle username input, PoW challenge, and registration.

**Acceptance Criteria:**
- [ ] Username input with validation (3-20 chars, alphanumeric + underscore)
- [ ] PoW challenge runs automatically on submit
- [ ] Progress indicator shows PoW status
- [ ] Registration completes and stores session token
- [ ] Error handling for invalid usernames, failed PoW, taken usernames
- [ ] Accessible form (labels, error messages, keyboard navigation)

**Steps:**
1. Edit `frontend/src/components/RegisterForm.tsx`
2. Implement username input with client-side validation
3. Integrate PoW utility from `frontend/src/utils/pow.ts`
4. Show progress indicator during PoW solving (0-100%)
5. Call registration API with challenge + solution
6. Store session token in PlayerContext
7. Redirect to /play on success
8. Show error messages for failures
9. Test with valid and invalid inputs

**Files to modify:**
- `frontend/src/components/RegisterForm.tsx`

---

### Task 3.3: Complete Leaderboard Component

**Priority**: 🔴 P0  
**Estimate**: 2-3 hours  
**Dependencies**: None  
**Owner**: Frontend team

**Description**: Finish Leaderboard component to display player rankings.

**Acceptance Criteria:**
- [ ] Leaderboard fetches data from API
- [ ] Displays top 100 players (or fewer if < 100 exist)
- [ ] Shows rank, username, total score, games played
- [ ] Highlights current player's rank (if authenticated)
- [ ] Loading state while fetching data
- [ ] Error handling for API failures
- [ ] Responsive table (mobile-friendly)
- [ ] Accessible (semantic HTML, ARIA labels)

**Steps:**
1. Edit `frontend/src/components/Leaderboard.tsx` or create if missing
2. Fetch leaderboard data from `/api/v1/players/leaderboard`
3. Display table with columns: Rank, Username, Score, Games Played
4. Add loading spinner while fetching
5. Highlight current player's row (different background color)
6. Handle empty leaderboard (no players yet)
7. Handle API errors gracefully
8. Style with Tailwind CSS (responsive table)

**Files to modify:**
- `frontend/src/components/Leaderboard.tsx` (or create)
- `frontend/src/pages/LeaderboardPage.tsx` (integrate component)

---

### Task 3.4: Add Photo Attribution Display

**Priority**: 🟠 P1  
**Estimate**: 1-2 hours  
**Dependencies**: Task 3.1  
**Owner**: Frontend team

**Description**: Display photo attribution (photographer, source, license) after guess is revealed.

**Acceptance Criteria:**
- [ ] Attribution shown AFTER guess is submitted (not before)
- [ ] Displays photographer name + source link
- [ ] Displays license type (CC BY 2.0, CC0, Public Domain)
- [ ] Link opens in new tab (`target="_blank" rel="noopener noreferrer"`)
- [ ] Hidden until results are revealed (prevent cheating)
- [ ] Accessible (proper link text, visible focus states)

**Steps:**
1. Modify `frontend/src/components/GameRound.tsx`
2. Add attribution section to results display
3. Show: "Photo by [Author] via [Source] ([License])"
4. Link to `attribution_url` from Photo metadata
5. Only display if `attribution_author` is present (some photos may be Public Domain with no specific author)
6. Style subtly (smaller text, below results)

**Files to modify:**
- `frontend/src/components/GameRound.tsx`

---

## Phase: Data Seeding

### Task 4.1: Create Airport Data Seeding Script

**Priority**: 🟠 P1  
**Estimate**: 2-3 hours  
**Dependencies**: None  
**Owner**: Backend team

**Description**: Create script to seed airport data from OurAirports database (CC0 license).

**Acceptance Criteria:**
- [ ] Script downloads OurAirports data (CSV format)
- [ ] Script parses and validates airport records
- [ ] Script filters: only large_airport and medium_airport types
- [ ] Script inserts airports into database (deduplicates by ICAO)
- [ ] Script completes in < 5 minutes for ~7000 airports
- [ ] CLI arguments: `--source`, `--limit`, `--dry-run`

**Steps:**
1. Create `backend/scripts/seed_airports.py`
2. Download OurAirports CSV: https://davidmegginson.github.io/ourairports-data/airports.csv
3. Parse CSV with pandas or csv module
4. Filter by `type IN ('large_airport', 'medium_airport')`
5. Insert into `airports` table (use bulk insert for performance)
6. Handle duplicates (ICAO is primary key)
7. Add CLI arguments with argparse
8. Test: `python scripts/seed_airports.py --dry-run`

**Files to create:**
- `backend/scripts/seed_airports.py`

**Example usage:**
```bash
python scripts/seed_airports.py --limit 100  # Seed 100 airports
python scripts/seed_airports.py --dry-run    # Preview without inserting
```

---

### Task 4.2: Create Photo Seeding Script (Wikimedia Commons)

**Priority**: 🟠 P1  
**Estimate**: 4-5 hours  
**Dependencies**: Task 4.1  
**Owner**: Backend team

**Description**: Create script to seed photos from Wikimedia Commons with proper attribution.

**Acceptance Criteria:**
- [ ] Script queries Wikimedia Commons API for airport photos
- [ ] Script downloads images (limit 100-150 photos)
- [ ] Script resizes and compresses images (< 200KB each)
- [ ] Script converts to WebP format
- [ ] Script strips EXIF data before saving
- [ ] Script matches photos to airports (by name/ICAO)
- [ ] Script stores attribution metadata (author, source, license, URL)
- [ ] Script marks photos as approved (pre-moderated)
- [ ] CLI arguments: `--source`, `--count`, `--dry-run`

**Steps:**
1. Create `backend/scripts/seed_photos.py`
2. Query Wikimedia Commons API:
   - Endpoint: `https://commons.wikimedia.org/w/api.php`
   - Action: `query`, list: `categorymembers`
   - Category: `Category:Airport photographs`
   - License filter: CC BY, CC BY-SA, CC0, Public Domain
3. Download images (use requests library)
4. Process images:
   - Resize to max 800px width (maintain aspect ratio)
   - Compress with Pillow (quality=85)
   - Convert to WebP
   - Strip EXIF data
5. Match to airports:
   - Parse photo title/description for airport names/codes
   - Query airports table for match
   - Skip if no match found
6. Save to `storage/photos/` with UUID filenames
7. Insert metadata to database (with attribution fields)
8. Set `moderation_status='approved'` and `verification_status='approved'`
9. Test: `python scripts/seed_photos.py --count 10 --dry-run`

**Files to create:**
- `backend/scripts/seed_photos.py`

**Dependencies to add:**
```bash
pip install requests Pillow
```

**Example usage:**
```bash
python scripts/seed_photos.py --source wikimedia --count 100
```

---

### Task 4.3: Create Test Fixtures for Integration Tests

**Priority**: 🔴 P0  
**Estimate**: 2 hours  
**Dependencies**: Task 4.1  
**Owner**: Backend team

**Description**: Create reusable test fixtures for integration tests (players, airports, photos, game rounds).

**Acceptance Criteria:**
- [ ] Fixtures in `backend/tests/fixtures/seed_data.yaml`
- [ ] Fixtures include: 2 players, 5 airports, 3 photos, 2 game rounds
- [ ] Fixture loader function: `load_test_fixtures(db)`
- [ ] Fixtures reset database to known state
- [ ] Fixtures used by all integration tests

**Steps:**
1. Create `backend/tests/fixtures/seed_data.yaml`
2. Define test players (test_player_1, test_player_2)
3. Define test airports (KJFK, EGLL, KSFO, EDDF, RJTT)
4. Define test photos (linked to airports)
5. Define test game rounds (completed rounds with scores)
6. Create `backend/tests/conftest.py` fixture loader:
   ```python
   @pytest.fixture
   def seed_test_data(db):
       # Load YAML
       # Clear existing data
       # Insert test fixtures
       # Return fixture IDs
   ```
7. Use in integration tests: `def test_something(client, seed_test_data):`

**Files to create:**
- `backend/tests/fixtures/seed_data.yaml`
- `backend/tests/conftest.py` (or modify existing)

---

## Phase: Performance & Polish

### Task 5.1: Add Database Indexes

**Priority**: 🟡 P2  
**Estimate**: 1 hour  
**Dependencies**: Task 2.1 (if not already in migration)  
**Owner**: Backend team

**Description**: Add database indexes for frequently queried fields.

**Acceptance Criteria:**
- [ ] Index on `players.total_score` (leaderboard sorting)
- [ ] Index on `photos.moderation_status` (photo selection)
- [ ] Index on `game_rounds.player_id` (player history)
- [ ] Indexes improve query performance (measure with EXPLAIN QUERY PLAN)

**Steps:**
1. If not in migration 003, create new migration: `alembic revision -m "Add performance indexes"`
2. Add indexes:
   - `CREATE INDEX idx_player_total_score ON players(total_score)`
   - `CREATE INDEX idx_photo_moderation_status ON photos(moderation_status)`
   - `CREATE INDEX idx_gameround_player_id ON game_rounds(player_id)`
3. Run migration: `alembic upgrade head`
4. Test query performance:
   ```sql
   EXPLAIN QUERY PLAN SELECT * FROM players ORDER BY total_score DESC LIMIT 100;
   ```
5. Verify index is used (output should mention index)

**Files to create (if needed):**
- `backend/migrations/versions/004_add_performance_indexes.py`

---

### Task 5.2: Optimize Frontend Bundle Size

**Priority**: 🟡 P2  
**Estimate**: 2-3 hours  
**Dependencies**: Task 3.1, 3.2, 3.3  
**Owner**: Frontend team

**Description**: Optimize frontend bundle to meet < 500KB gzipped target.

**Acceptance Criteria:**
- [ ] Production build bundle < 500KB gzipped
- [ ] No duplicate dependencies
- [ ] Code splitting by route (lazy load pages)
- [ ] Tree shaking removes unused code
- [ ] Bundle analysis shows no large unexpected dependencies

**Steps:**
1. Build production bundle: `npm run build`
2. Analyze bundle size:
   ```bash
   npm install --save-dev rollup-plugin-visualizer
   npm run build -- --mode=analyze
   ```
3. Identify large dependencies
4. Implement code splitting:
   ```tsx
   const PlayPage = lazy(() => import('./pages/PlayPage'));
   const LeaderboardPage = lazy(() => import('./pages/LeaderboardPage'));
   ```
5. Add Suspense boundaries for lazy-loaded components
6. Remove unused dependencies from package.json
7. Re-build and verify size: `du -sh dist/assets/*.js`

**Files to modify:**
- `frontend/src/main.tsx` (add lazy loading)
- `frontend/vite.config.ts` (configure code splitting)
- `frontend/package.json` (remove unused deps)

---

### Task 5.3: Optimize Images (WebP, Compression)

**Priority**: 🟡 P2  
**Estimate**: 1-2 hours  
**Dependencies**: Task 4.2  
**Owner**: Backend team

**Description**: Ensure all seeded photos are optimized (WebP format, < 200KB each).

**Acceptance Criteria:**
- [ ] All photos in `storage/photos/` are WebP format
- [ ] All photos < 200KB file size
- [ ] Image quality acceptable (no visible artifacts)
- [ ] Optimization does not remove alt text or accessibility

**Steps:**
1. Audit existing photos: `ls -lh storage/photos/` (check sizes)
2. Modify `seed_photos.py` to include optimization:
   ```python
   from PIL import Image
   img = Image.open(photo_path)
   img = img.resize((800, int(800 * img.height / img.width)))  # Max 800px width
   img.save(output_path, 'WEBP', quality=85, optimize=True)
   ```
3. Re-run seeding script on existing photos (batch conversion)
4. Verify sizes: all should be < 200KB
5. Test image display in browser (check quality)

**Files to modify:**
- `backend/scripts/seed_photos.py` (add optimization)

---

### Task 5.4: Run Lighthouse Accessibility Audit

**Priority**: 🟡 P2  
**Estimate**: 2-3 hours  
**Dependencies**: Task 3.1, 3.2, 3.3  
**Owner**: Frontend team

**Description**: Run Lighthouse audit and fix accessibility issues.

**Acceptance Criteria:**
- [ ] Lighthouse accessibility score >= 90/100
- [ ] No critical or serious accessibility violations
- [ ] Color contrast meets WCAG AA (4.5:1)
- [ ] All images have alt text
- [ ] All interactive elements keyboard accessible
- [ ] Form inputs have labels

**Steps:**
1. Start frontend dev server: `npm run dev`
2. Open Chrome DevTools → Lighthouse
3. Run audit on: Homepage, Play page, Leaderboard page
4. Review violations:
   - Color contrast issues
   - Missing alt text
   - Missing form labels
   - Focus indicators
5. Fix issues in components
6. Re-run audit until score >= 90
7. Document remaining issues in `docs/accessibility-report.md`

**Files to modify:**
- Various component files (based on audit results)
- Create `docs/accessibility-report.md` (audit summary)

---

## Phase: Documentation & Release

### Task 6.1: Update API Documentation

**Priority**: 🟠 P1  
**Estimate**: 1-2 hours  
**Dependencies**: All backend tasks  
**Owner**: Backend team

**Description**: Update `docs/api-reference.md` with any changes to API endpoints.

**Acceptance Criteria:**
- [ ] All endpoints documented (routes, methods, parameters, responses)
- [ ] Example requests and responses included
- [ ] Error codes documented
- [ ] Authentication requirements noted
- [ ] Rate limits documented

**Steps:**
1. Review `backend/src/api/` for all endpoints
2. Update `docs/api-reference.md` with current signatures
3. Add examples for new endpoints (if any)
4. Document moderation status codes (202 for flagged photos)
5. Verify documentation matches OpenAPI spec

**Files to modify:**
- `docs/api-reference.md`

---

### Task 6.2: Create Release Checklist

**Priority**: 🟠 P1  
**Estimate**: 1 hour  
**Dependencies**: All tasks  
**Owner**: Project lead

**Description**: Create release checklist in `docs/deployment.md` for pre-launch validation.

**Acceptance Criteria:**
- [ ] Checklist includes all P0/P1 tasks
- [ ] Checklist includes test validation steps
- [ ] Checklist includes deployment steps (Fly.io)
- [ ] Checklist includes rollback procedure
- [ ] Checklist includes post-launch monitoring

**Steps:**
1. Edit `docs/deployment.md`
2. Add "Pre-Release Checklist" section
3. Include:
   - All tests passing
   - Photo pool seeded (100+ photos)
   - EXIF stripping validated
   - Accessibility audit passed
   - Performance budgets met
   - Constitution compliance verified
4. Add "Deployment Steps" section (Fly.io specific)
5. Add "Rollback Procedure" section
6. Add "Post-Launch Monitoring" section

**Files to modify:**
- `docs/deployment.md`

---

### Task 6.3: Create Future Roadmap Document

**Priority**: 🟡 P2  
**Estimate**: 2-3 hours  
**Dependencies**: None  
**Owner**: Project lead

**Description**: Create structured roadmap for P2/P3 features with clear priorities.

**Acceptance Criteria:**
- [ ] Roadmap document created: `docs/roadmap.md`
- [ ] Features organized by priority (P2, P3)
- [ ] Each feature has: description, user scenarios, acceptance criteria
- [ ] Dependencies and effort estimates included
- [ ] Constitutional alignment verified for each feature

**Steps:**
1. Create `docs/roadmap.md`
2. Organize features from spec.md by priority:
   - **P2 (Medium Priority)**:
     - Offline support (Service Worker + IndexedDB)
     - Data seeding scripts (airlines, aircraft)
     - Performance optimization
     - Accessibility audit (comprehensive)
     - E2E tests with Playwright
   - **P3 (Low Priority)**:
     - Difficulty multiplier system
     - Aircraft identification game mode
     - Advanced analytics (privacy-preserving)
     - Mobile app (iOS/Android)
     - Internationalization (i18n)
3. For each feature, include:
   - Description (1-2 paragraphs)
   - User scenarios (from spec.md or new)
   - Acceptance criteria (testable)
   - Effort estimate (T-shirt sizes: S/M/L/XL)
   - Dependencies (which features must come first)
4. Add constitutional check for each feature
5. Add "When to prioritize" section (triggers for moving P2→P1, P3→P2)

**Files to create:**
- `docs/roadmap.md`

---

## Task Summary

**Total Tasks**: 23  
**P0 (Blocker)**: 7 tasks  
**P1 (High)**: 10 tasks  
**P2 (Medium)**: 6 tasks

**Estimated Timeline:**
- **Week 1**: Backend testing (Tasks 1.1-1.4, 2.1-2.2) - ~15 hours
- **Week 2**: Content moderation + Frontend (Tasks 2.3-2.4, 3.1-3.4) - ~18 hours
- **Week 3**: Data seeding + Polish (Tasks 4.1-4.3, 5.1-5.3, 6.1-6.2) - ~16 hours
- **Week 4**: Optimization + Documentation (Tasks 5.4, 6.3) - ~5 hours

**Total Effort**: ~54 hours (7-8 working days for one developer, 2-3 weeks with multiple contributors)

---

## Next Steps

1. **Task assignment**: Assign tasks to team members based on expertise
2. **Sprint planning**: Break into 1-week sprints with daily standups
3. **Progress tracking**: Update task status in project management tool
4. **Code reviews**: All code must be reviewed before merging
5. **Testing**: Run full test suite after each task completion
6. **Documentation**: Update docs as code is written, not after

---

## Success Criteria

**Release is ready when:**
- ✅ All P0 tasks completed
- ✅ All P1 tasks completed (or explicitly deferred with justification)
- ✅ All tests pass (unit, integration, contract)
- ✅ Manual smoke test passes (TC-001 to TC-006)
- ✅ Accessibility audit passes (score >= 90)
- ✅ Performance budgets met (bundle < 500KB, load < 3s)
- ✅ Constitution compliance verified
- ✅ Release checklist complete

**Post-release:**
- Monitor for bugs and issues
- Triage user feedback
- Prioritize P2 tasks based on learnings
- Update roadmap based on real-world usage

---

**Last Updated**: 2026-02-01  
**Status**: Ready for implementation  
**Branch**: `002-release-preparation`
