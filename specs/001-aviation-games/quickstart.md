# Quickstart Guide: Aviation Games

**Feature**: Aviation Games  
**Phase**: Phase 1 - Design  
**Date**: 2026-01-31  
**Audience**: Developers getting started with implementation

---

## Overview

This guide provides a high-level walkthrough of the aviation games system architecture, key flows, and implementation approach. Read this before diving into implementation tasks.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User's Browser                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  React Frontend                                               │  │
│  │  - Game UI (photo viewer, airport search, scoring)          │  │
│  │  - Offline support (Service Worker + IndexedDB)             │  │
│  │  - WCAG AA accessible (4.5:1 contrast, keyboard nav)        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                            │ REST API (JSON)                        │
└────────────────────────────┼────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │  Gameplay  │  │   Photo    │  │  Airport   │  │ Leaderboard│  │
│  │  Routes    │  │  Upload    │  │  Search    │  │  Routes    │  │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘  │
│         │               │               │               │           │
│         └───────────────┴───────────────┴───────────────┘           │
│                         │                                            │
│                         ▼                                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Services Layer                                               │  │
│  │  - Scoring logic (3-attempt system, distance calculation)    │  │
│  │  - EXIF stripping (Pillow, verification required)           │  │
│  │  - Difficulty calculation (background worker)                │  │
│  │  - Anti-cheat (token validation, rate limiting)             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                         │                                            │
│                         ▼                                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  SQLite Database                                             │  │
│  │  - Players (username, score)                                │  │
│  │  - Photos (EXIF stripped, file refs)                        │  │
│  │  - Airports (OurAirports data)                              │  │
│  │  - GameRounds (state machine)                               │  │
│  │  - PhotoDifficulty (dynamic multipliers)                    │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      File Storage                                    │
│  storage/photos/      (EXIF-stripped aviation photos)               │
│  storage/cache/       (Temporary processing)                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Key Implementation Flows

### Flow 1: Start Game Round

```
Frontend                Backend                 Database
   │                       │                       │
   │  POST /game/start     │                       │
   ├──────────────────────>│                       │
   │                       │  SELECT random photo  │
   │                       │  WHERE not shown to   │
   │                       │  player yet           │
   │                       ├──────────────────────>│
   │                       │<──────────────────────┤
   │                       │  photo + airport      │
   │                       │                       │
   │                       │  INSERT game_round    │
   │                       │  (state=attempt_1)    │
   │                       ├──────────────────────>│
   │                       │<──────────────────────┤
   │                       │                       │
   │<──────────────────────┤                       │
   │  200 OK:              │                       │
   │  - round_id, token    │                       │
   │  - photo URL (EXIF    │                       │
   │    stripped)          │                       │
   │  - alt_text           │                       │
   │                       │                       │
   ▼                       ▼                       ▼
```

**Critical Steps:**
1. Select photo player hasn't seen (query: `WHERE photo_id NOT IN (SELECT photo_id FROM game_round WHERE player_id = ?)`)
2. Create round with unique token (UUID v4)
3. Set expiration (30 minutes from now)
4. Return ONLY photo URL and metadata (NOT the correct answer)

---

### Flow 2: Submit Guess (Progressive 3-Attempt System)

#### Attempt 1: First Guess

```
Frontend                Backend                 Database
   │                       │                       │
   │  POST /game/guess     │                       │
   │  {round_token,        │                       │
   │   guessed_airport}    │                       │
   ├──────────────────────>│                       │
   │                       │  Validate token       │
   │                       │  Check not expired    │
   │                       ├──────────────────────>│
   │                       │<──────────────────────┤
   │                       │                       │
   │                       │  IF guess == correct: │
   │                       │    score = 10         │
   │                       │    state = completed  │
   │                       │  ELSE:                │
   │                       │    state = attempt_2  │
   │                       │    store guess        │
   │                       ├──────────────────────>│
   │                       │<──────────────────────┤
   │<──────────────────────┤                       │
   │  200 OK:              │                       │
   │  {correct: false,     │                       │
   │   attempt: 2,         │                       │
   │   final: false}       │                       │
   ▼                       ▼                       ▼
```

#### Attempt 2: Distance Feedback

```
Frontend                Backend                 Database
   │                       │                       │
   │  POST /game/guess     │                       │
   ├──────────────────────>│                       │
   │                       │  Retrieve attempt_1   │
   │                       │  guess from round     │
   │                       ├──────────────────────>│
   │                       │<──────────────────────┤
   │                       │                       │
   │                       │  Calculate distance   │
   │                       │  using Haversine:     │
   │                       │  dist = f(attempt_1,  │
   │                       │         correct)      │
   │                       │                       │
   │                       │  IF guess == correct: │
   │                       │    score = 5          │
   │                       │  ELSE:                │
   │                       │    state = attempt_3  │
   │                       ├──────────────────────>│
   │<──────────────────────┤                       │
   │  200 OK:              │                       │
   │  {correct: false,     │                       │
   │   attempt: 3,         │                       │
   │   final: false,       │                       │
   │   distance_km: 847.3, │                       │
   │   distance_mi: 526.5} │                       │
   ▼                       ▼                       ▼
```

#### Attempt 3: Country Hint + Final

```
Frontend                Backend                 Database
   │                       │                       │
   │  POST /game/guess     │                       │
   ├──────────────────────>│                       │
   │                       │  Retrieve correct     │
   │                       │  airport              │
   │                       ├──────────────────────>│
   │                       │<──────────────────────┤
   │                       │  country_hint =       │
   │                       │  airport.country_name │
   │                       │                       │
   │                       │  IF guess == correct: │
   │                       │    score = 3          │
   │                       │  ELSE:                │
   │                       │    score = 0          │
   │                       │                       │
   │                       │  state = completed    │
   │                       │  Apply multiplier     │
   │                       │  Update player score  │
   │                       ├──────────────────────>│
   │<──────────────────────┤                       │
   │  200 OK:              │                       │
   │  {correct: false,     │                       │
   │   final: true,        │                       │
   │   score: 0,           │                       │
   │   country_hint: "USA",│                       │
   │   revealed_airport: {│                       │
   │     name: "JFK", ...},│                       │
   │   attribution: {...}} │                       │
   ▼                       ▼                       ▼
```

**Critical Steps:**
1. **Token validation**: Prevent replay attacks
2. **State machine**: Enforce sequential attempts (can't jump from 1 to 3)
3. **Distance calculation**: Haversine formula for great-circle distance
4. **Country hint**: Only on attempt 3
5. **Difficulty multiplier**: Applied to final score only
6. **Attribution**: Displayed after round complete (photographer credit)

---

### Flow 3: Photo Upload with EXIF Stripping

```
Frontend                Backend                 Database/Storage
   │                       │                       │
   │  POST /photos/upload  │                       │
   │  (multipart/form-data)│                       │
   │  - file               │                       │
   │  - airport_id         │                       │
   ├──────────────────────>│                       │
   │                       │  Validate file:       │
   │                       │  - Format (JPEG/PNG)  │
   │                       │  - Size (<10MB)       │
   │                       │  - Dimensions (≥800px)│
   │                       │                       │
   │                       │  CRITICAL: Strip EXIF │
   │                       │  ┌────────────────┐   │
   │                       │  │ Pillow Library │   │
   │                       │  │ - Load image   │   │
   │                       │  │ - Create clean │   │
   │                       │  │ - Verify no    │   │
   │                       │  │   metadata     │   │
   │                       │  └────────────────┘   │
   │                       │  IF verification fails:│
   │                       │    ABORT (never save)  │
   │                       │                       │
   │                       │  Save to storage/photos/│
   │                       ├──────────────────────>│
   │                       │<──────────────────────┤
   │                       │                       │
   │                       │  INSERT photo record  │
   │                       │  INSERT attribution   │
   │                       ├──────────────────────>│
   │<──────────────────────┤                       │
   │  201 Created:         │                       │
   │  {photo_id,           │                       │
   │   status: "pending"}  │                       │
   ▼                       ▼                       ▼
```

**Critical Steps:**
1. **EXIF stripping is NON-NEGOTIABLE**: Must verify post-strip
2. **Fail loudly**: If stripping fails, reject upload (don't silently store)
3. **Attribution required**: Store photographer/license info for transparency
4. **Manual review**: Photos enter as "pending", require approval

---

### Flow 4: Difficulty Multiplier Calculation (Background Worker)

```
Hourly Cron Job
   │
   ▼
┌──────────────────────────────────────────────────────────────┐
│  1. Check global activation threshold:                       │
│     - photo_count ≥ 500?                                     │
│     - player_count ≥ 100?                                    │
│     IF NO: Exit (system inactive)                            │
└──────────────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────────────┐
│  2. Query photos with ≥20 attempts:                          │
│     SELECT photo_id, COUNT(*) as total,                      │
│            SUM(CASE WHEN score > 0 THEN 1 ELSE 0) as success │
│     FROM game_rounds                                          │
│     WHERE state = 'completed'                                 │
│     GROUP BY photo_id                                         │
│     HAVING total ≥ 20                                         │
└──────────────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────────────┐
│  3. For each photo:                                          │
│     success_rate = success / total                           │
│     IF success_rate == 0:                                    │
│       multiplier = 3.0 (max cap)                            │
│     ELSE:                                                    │
│       multiplier = min(3.0, max(1.0, 1.0 / success_rate))  │
│                                                              │
│     UPDATE photo_difficulty                                  │
│     SET multiplier = calculated_value,                       │
│         active = TRUE                                        │
│     WHERE photo_id = current                                 │
└──────────────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────────────┐
│  4. (One-time on first activation):                          │
│     Retroactive score adjustment:                            │
│     - Recalculate all historical scores                      │
│     - Update player totals                                   │
│     - Rebuild leaderboard                                    │
└──────────────────────────────────────────────────────────────┘
```

**Critical Steps:**
1. **Global threshold**: System must have 500+ photos AND 100+ players
2. **Per-photo threshold**: Each photo needs ≥20 attempts
3. **Conservative caps**: 3x maximum prevents leaderboard distortion
4. **Retroactive fairness**: Adjust all historical scores when activating

---

## Data Model Key Points

### Entity Relationships
- **Player** 1 ──< ∞ **GameRound** >── 1 **Photo** >── 1 **Airport**
- **Photo** 1 ── 1 **PhotoAttribution**
- **Photo** 1 ── 1 **PhotoDifficulty**
- **Player** 1 ── 1 **LeaderboardEntry**

### Critical Constraints
1. **Privacy**: Player table contains ONLY username + score (no email, no location, no device info)
2. **EXIF**: All photos MUST have stripped metadata verified before storage
3. **State machine**: GameRound state transitions are enforced (no skipping)
4. **Token uniqueness**: Round tokens must be globally unique (UUID v4)

### Performance Indexes
```sql
-- High-frequency queries
CREATE INDEX idx_gameround_token ON game_round(round_token);
CREATE INDEX idx_leaderboard_rank ON leaderboard_entry(rank);
CREATE INDEX idx_airport_search ON airport(name, iata, icao);
```

---

## API Contract Highlights

### Core Endpoints
- `POST /game/start` → Start new round, returns photo + token
- `POST /game/guess` → Submit guess, returns feedback (attempt-dependent)
- `GET /airports` → Search airports by name/code
- `POST /photos/upload` → Upload photo (EXIF stripped)
- `GET /leaderboard` → Top 100 players

### Request/Response Pattern
```typescript
// Start game
const response = await fetch('/game/start', {
  method: 'POST',
  body: JSON.stringify({ player_id: 'uuid' })
});
const { round_id, round_token, photo } = await response.json();

// Submit guess
const guessResponse = await fetch('/game/guess', {
  method: 'POST',
  body: JSON.stringify({
    round_id,
    round_token,
    guessed_airport: 'KJFK'
  })
});
const feedback = await guessResponse.json();
// feedback.correct, feedback.attempt, feedback.distance_km, etc.
```

---

## Frontend Key Points

### Technology Stack
- **React 18**: Concurrent rendering, modern hooks
- **TypeScript**: Type safety from API contracts
- **Vite**: Fast builds, optimized HMR
- **Tailwind CSS**: Utility-first, WCAG AA colors
- **Workbox**: Service Worker for offline support

### Accessibility Requirements (WCAG AA)
```typescript
// Color palette with 4.5:1 minimum contrast
const colors = {
  background: '#FFFFFF',
  text: '#1F2937',         // 14.6:1 contrast
  primary: '#1E3A8A',      // 7.8:1 contrast
  secondary: '#64748B',    // 4.9:1 contrast
};

// Keyboard navigation
<button
  onClick={handleClick}
  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
  aria-label="Submit guess"
>
```

### Offline Strategy
1. **Service Worker caches**:
   - App shell (HTML, CSS, JS)
   - Last 10 photos viewed
   - Airport search results (5-minute TTL)
2. **IndexedDB storage**:
   - Player session
   - Pending uploads (sync when online)

---

## Testing Strategy

### Test Pyramid
```
      E2E (Playwright)
      - Full user journeys
      - Accessibility audits
     ----------------
    Integration (pytest)
    - API endpoint tests
    - Multi-service flows
   --------------------
  Contract (pytest + OpenAPI)
  - Schema validation
  - Response format
 ------------------------
Unit (pytest + Jest)
- Business logic
- Components
- Utilities
```

### Critical Tests
1. **EXIF stripping**: Load photo with GPS, verify complete removal
2. **Progressive scoring**: Test all 3-attempt paths (10/5/3/0 points)
3. **Distance calculation**: Haversine formula accuracy
4. **State machine**: Cannot skip attempts, completed is terminal
5. **Accessibility**: WCAG AA automated checks (jest-axe)

---

## Deployment Considerations

### Phase 1: Web (MVP)
- **Backend**: FastAPI on Linux server
- **Frontend**: Static site on CDN
- **Database**: SQLite (sufficient for <10k users)
- **Storage**: Local filesystem (`storage/photos/`)
- **Monitoring**: Basic health checks, error logging

### Phase 2: iOS (Future)
- **iOS app**: Swift + SwiftUI
- **API**: Reuse existing FastAPI backend
- **Storage**: Shared backend, SQLite on device for offline

### Scaling Triggers
- **Database**: Migrate SQLite → PostgreSQL if >10k players
- **Storage**: Migrate files → object storage (S3/Backblaze) if >50GB photos
- **Difficulty calc**: Move to Redis if calculation latency >100ms

---

## Privacy & Security Checklist

✅ **Privacy by Design**
- [ ] No third-party analytics or tracking scripts
- [ ] EXIF stripping verified before storage
- [ ] Minimal player identity (username + score only)
- [ ] No device fingerprinting or IP logging

✅ **Data Handling**
- [ ] Photo location metadata never exposed to players
- [ ] One-time location use in aircraft mode (Phase 2)
- [ ] No behavioral profiling infrastructure
- [ ] All data flows documented and auditable

✅ **Accessibility**
- [ ] WCAG AA compliance (4.5:1 contrast ratios)
- [ ] Keyboard navigation fully functional
- [ ] Screen reader compatible (semantic HTML, ARIA)
- [ ] Alt text for all images (doesn't reveal answers)

✅ **Security**
- [ ] Anti-cheat tokens (UUID v4, unique per round)
- [ ] Rate limiting (max 1 guess per 5 seconds)
- [ ] Round expiration (30 minutes)
- [ ] Input validation (airport codes, file formats)

---

## Next Steps

1. **Read research.md** for technical decisions and alternatives evaluated
2. **Review data-model.md** for entity details and relationships
3. **Study contracts/openapi.yaml** for API specification
4. **Check contracts/types.ts** for frontend type definitions
5. **Wait for tasks.md** generation (Phase 2: `/speckit.tasks` command)

Once tasks.md is generated, implementation can begin following TDD:
1. Write tests for user story (from spec.md)
2. Run tests (should fail - red)
3. Implement minimum code to pass (green)
4. Refactor for simplicity (refactor)
5. Repeat

---

**Design Phase Complete** ✓  
All technical decisions documented. Ready for task breakdown in Phase 2.
