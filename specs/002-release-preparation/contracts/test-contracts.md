# Test Contracts: Release Preparation

**Feature**: 002-release-preparation  
**Date**: 2026-02-01  
**Purpose**: Define test contracts for validating release readiness

---

## Overview

Test contracts ensure that implementations match specifications and that privacy/security guarantees are validated. This document defines test scenarios organized by priority (P0 = blocker, P1 = high, P2 = medium).

---

## P0 Tests (Release Blockers)

### TC-001: Backend Server Health Check

**Requirement**: Backend must start without errors and respond to health check

**Test**:
```bash
# Start backend server
cd backend && python -m uvicorn src.main:app --host 0.0.0.0 --port 8000

# Verify health endpoint
curl -s http://localhost:8000/api/v1/health | jq

# Expected response:
{
  "status": "ok",
  "timestamp": "2026-02-01T12:00:00Z"
}
```

**Acceptance**: 
- Server starts without errors
- Health endpoint returns 200 OK
- Response includes "status": "ok"

---

### TC-002: Frontend Server Start

**Requirement**: Frontend must start and serve accessible UI

**Test**:
```bash
# Start frontend dev server
cd frontend && npm run dev

# Verify homepage loads
curl -s http://localhost:5173 | grep "<title>"

# Expected output:
<title>Airfeeld - Aviation Guessing Game</title>
```

**Acceptance**:
- Dev server starts without errors
- Homepage loads with correct title
- No console errors in browser

---

### TC-003: Player Registration Workflow

**Requirement**: User must be able to register with username + PoW validation

**Test** (Integration):
```python
# backend/tests/integration/test_registration.py

import pytest
from fastapi.testclient import TestClient

def test_player_registration_full_workflow(client: TestClient):
    # Step 1: Get PoW challenge
    challenge_response = client.get("/api/v1/players/challenge")
    assert challenge_response.status_code == 200
    challenge = challenge_response.json()["challenge"]
    difficulty = challenge_response.json()["difficulty"]
    
    # Step 2: Solve PoW (mock solution for testing)
    solution = solve_pow_challenge(challenge, difficulty)
    
    # Step 3: Register player
    register_response = client.post("/api/v1/players/register", json={
        "username": "test_player_123",
        "challenge": challenge,
        "solution": solution
    })
    assert register_response.status_code == 200
    
    # Step 4: Verify response
    data = register_response.json()
    assert "player_id" in data
    assert "session_token" in data
    assert data["username"] == "test_player_123"
    
    # Step 5: Verify player in database
    player = db.query(Player).filter_by(username="test_player_123").first()
    assert player is not None
    assert player.total_score == 0
    assert player.games_played == 0
```

**Acceptance**:
- Challenge endpoint returns valid PoW challenge
- Registration succeeds with correct PoW solution
- Session token is returned
- Player is created in database with correct defaults

---

### TC-004: Gameplay Full Round

**Requirement**: User must be able to view photo, submit guess, receive feedback

**Test** (Integration):
```python
# backend/tests/integration/test_gameplay.py

def test_complete_game_round(client: TestClient, authenticated_player):
    # Step 1: Start game (get photo)
    game_response = client.post("/api/v1/games/start", 
        headers={"Authorization": f"Bearer {authenticated_player.session_token}"})
    assert game_response.status_code == 200
    
    game_data = game_response.json()
    round_id = game_data["round_id"]
    photo_url = game_data["photo_url"]
    round_token = game_data["round_token"]
    
    # Step 2: Submit guess (attempt 1)
    guess_response = client.post(f"/api/v1/games/{round_id}/guess", 
        headers={"Authorization": f"Bearer {authenticated_player.session_token}"},
        json={
            "guess": "KJFK",  # Assume correct answer for test
            "round_token": round_token,
            "attempt": 1
        })
    assert guess_response.status_code == 200
    
    # Step 3: Verify feedback
    feedback = guess_response.json()
    assert "correct" in feedback
    assert "score" in feedback
    assert "correct_airport" in feedback
    
    if feedback["correct"]:
        assert feedback["score"] == 10  # Correct on attempt 1
    
    # Step 4: Verify game round completed
    round = db.query(GameRound).filter_by(id=round_id).first()
    assert round.state == "completed"
    assert round.final_score in [0, 3, 5, 10]
    
    # Step 5: Verify player score updated
    player = db.query(Player).filter_by(id=authenticated_player.player_id).first()
    assert player.total_score >= 0
    assert player.games_played >= 1
```

**Acceptance**:
- Game start returns photo and round metadata
- Guess submission updates game round state
- Feedback includes correct/incorrect, score, and airport details
- Player score is updated correctly

---

### TC-005: Leaderboard Display

**Requirement**: Leaderboard must display player rankings

**Test** (Integration):
```python
# backend/tests/integration/test_leaderboard.py

def test_leaderboard_returns_top_players(client: TestClient, seed_players):
    # Seed database with test players (scores: 100, 75, 50, 25, 10)
    seed_players(5)
    
    # Query leaderboard
    leaderboard_response = client.get("/api/v1/players/leaderboard")
    assert leaderboard_response.status_code == 200
    
    leaderboard = leaderboard_response.json()
    assert "players" in leaderboard
    assert len(leaderboard["players"]) <= 100  # Max 100 players
    
    # Verify sorting (descending by score)
    scores = [p["total_score"] for p in leaderboard["players"]]
    assert scores == sorted(scores, reverse=True)
    
    # Verify no personal data exposed
    for player in leaderboard["players"]:
        assert "username" in player
        assert "total_score" in player
        assert "games_played" in player
        assert "email" not in player  # Privacy check
        assert "session_token" not in player  # Security check
```

**Acceptance**:
- Leaderboard returns ranked list of players
- Sorting is correct (descending by score)
- No personal or sensitive data exposed

---

### TC-006: EXIF Stripping Validation

**Requirement**: Uploaded photos must have all EXIF data stripped

**Test** (Unit):
```python
# backend/tests/unit/test_exif_stripping.py

from PIL import Image
from src.services.photo_service import strip_exif

def test_exif_data_removed_from_photo():
    # Load test photo with EXIF data
    test_photo_path = "tests/fixtures/test_photo_with_exif.jpg"
    original_image = Image.open(test_photo_path)
    original_exif = original_image.getexif()
    
    # Verify original has EXIF data
    assert len(original_exif) > 0, "Test photo must have EXIF data"
    
    # Strip EXIF
    stripped_photo_path = strip_exif(test_photo_path)
    stripped_image = Image.open(stripped_photo_path)
    stripped_exif = stripped_image.getexif()
    
    # Verify EXIF removed
    assert len(stripped_exif) == 0, "EXIF data not fully stripped"
    
    # Verify no GPS data
    gps_info = stripped_image._getexif()
    assert gps_info is None or 34853 not in gps_info, "GPS data still present"
```

**Acceptance**:
- Original photo has EXIF data (test validity)
- Stripped photo has zero EXIF entries
- GPS data specifically verified as removed

---

## P1 Tests (High Priority)

### TC-007: Content Moderation - Profanity Filter

**Requirement**: Usernames and photo metadata must be checked for profanity

**Test** (Unit):
```python
# backend/tests/unit/test_profanity_filter.py

from src.services.profanity_filter import contains_profanity

def test_profanity_detection():
    # Test profane words
    assert contains_profanity("badword123") == True
    assert contains_profanity("another_badword") == True
    
    # Test clean words
    assert contains_profanity("test_player") == False
    assert contains_profanity("aviation_fan") == False
    
    # Test edge cases
    assert contains_profanity("bad_word_with_spaces") == True
    assert contains_profanity("BADWORD") == True  # Case insensitive
    assert contains_profanity("b4dw0rd") == True  # Leetspeak
```

**Acceptance**:
- Profane words are detected correctly
- Clean words pass filter
- Case insensitivity and leetspeak variants handled

---

### TC-008: Content Moderation - NSFW Detection

**Requirement**: Photos must be scanned for NSFW content before approval

**Test** (Unit with mock):
```python
# backend/tests/unit/test_nsfw_detection.py

from src.workers.moderation import check_nsfw
from unittest.mock import patch

def test_nsfw_detection_auto_approve():
    # Mock NSFW model returning safe score
    with patch('src.workers.moderation.nsfw_model.predict') as mock_predict:
        mock_predict.return_value = 0.1  # Safe photo
        
        result = check_nsfw("tests/fixtures/test_airport_photo.jpg")
        
        assert result["score"] == 0.1
        assert result["status"] == "approved"
        assert result["reason"] is None

def test_nsfw_detection_auto_reject():
    # Mock NSFW model returning explicit score
    with patch('src.workers.moderation.nsfw_model.predict') as mock_predict:
        mock_predict.return_value = 0.9  # Explicit photo
        
        result = check_nsfw("tests/fixtures/test_explicit_photo.jpg")
        
        assert result["score"] == 0.9
        assert result["status"] == "rejected"
        assert "explicit content" in result["reason"].lower()

def test_nsfw_detection_flagged_for_review():
    # Mock NSFW model returning borderline score
    with patch('src.workers.moderation.nsfw_model.predict') as mock_predict:
        mock_predict.return_value = 0.7  # Borderline
        
        result = check_nsfw("tests/fixtures/test_borderline_photo.jpg")
        
        assert result["score"] == 0.7
        assert result["status"] == "flagged"
        assert "manual review" in result["reason"].lower()
```

**Acceptance**:
- Safe photos (score < 0.6) are auto-approved
- Explicit photos (score ≥ 0.8) are auto-rejected
- Borderline photos (0.6-0.8) are flagged for manual review

---

### TC-009: Rate Limiting Validation

**Requirement**: API must enforce rate limits (10 req/min registration, 100 req/min gameplay)

**Test** (Unit):
```python
# backend/tests/unit/test_rate_limit.py

from src.middleware.rate_limit import RateLimiter
import time

def test_rate_limit_registration_endpoint():
    rate_limiter = RateLimiter(max_requests=10, window_seconds=60)
    client_ip = "192.168.1.1"
    
    # Make 10 requests (should all pass)
    for i in range(10):
        assert rate_limiter.check(client_ip, "registration") == True
    
    # 11th request should be blocked
    assert rate_limiter.check(client_ip, "registration") == False
    
    # Wait for window to reset (mock time)
    time.sleep(61)
    
    # Should be allowed again
    assert rate_limiter.check(client_ip, "registration") == True
```

**Acceptance**:
- Rate limiter correctly counts requests per IP
- Blocks requests exceeding limit
- Resets after time window expires

---

### TC-010: Frontend Component - Game Round

**Requirement**: GameRound component must display photo and accept guess

**Test** (Component test - manual for MVP, automated in P2):
```typescript
// frontend/tests/unit/GameRound.test.tsx (future)

import { render, screen, fireEvent } from '@testing-library/react';
import GameRound from '@/components/GameRound';

test('renders photo and airport search', () => {
  const mockRound = {
    round_id: 'test-round-1',
    photo_url: '/storage/photos/test.jpg',
    round_token: 'test-token'
  };
  
  render(<GameRound round={mockRound} />);
  
  // Verify photo displayed
  const photoImg = screen.getByAlt('Airport photo');
  expect(photoImg).toBeInTheDocument();
  
  // Verify search input
  const searchInput = screen.getByPlaceholderText('Search for airport...');
  expect(searchInput).toBeInTheDocument();
  
  // Simulate typing
  fireEvent.change(searchInput, { target: { value: 'JFK' } });
  
  // Verify autocomplete suggestions appear
  const suggestion = screen.getByText(/John F Kennedy/i);
  expect(suggestion).toBeInTheDocument();
});
```

**Acceptance** (Manual testing for MVP):
- Photo renders correctly
- Airport search shows autocomplete suggestions
- Guess submission triggers API call
- Loading state shown during submission
- Results displayed after submission

---

### TC-011: Photo Pool Seeding

**Requirement**: Seed script must populate database with 100+ photos

**Test** (Integration):
```python
# backend/tests/integration/test_photo_seeding.py

from scripts.seed_photos import seed_photos_from_wikimedia

def test_photo_seeding_creates_minimum_photos():
    # Clear photos table
    db.query(Photo).delete()
    db.commit()
    
    # Run seed script
    count = seed_photos_from_wikimedia(target_count=100, dry_run=False)
    
    # Verify photos created
    assert count >= 100, f"Expected 100+ photos, got {count}"
    
    # Verify photos have required fields
    photos = db.query(Photo).all()
    for photo in photos:
        assert photo.airport_id is not None
        assert photo.file_path is not None
        assert photo.moderation_status == "approved"  # Seeded photos pre-approved
        assert photo.verification_status == "approved"
        
        # Verify attribution for CC photos
        if photo.attribution_license != "Public Domain":
            assert photo.attribution_author is not None
            assert photo.attribution_source is not None
            assert photo.attribution_url is not None
```

**Acceptance**:
- At least 100 photos seeded
- All photos have valid airport associations
- Attribution metadata present for CC-licensed photos
- Photos are approved and ready for gameplay

---

## P2 Tests (Medium Priority - Post-MVP)

### TC-012: E2E Smoke Test - Full Gameplay Flow

**Requirement**: End-to-end test validating entire user journey

**Test** (Playwright):
```typescript
// frontend/tests/e2e/gameplay.spec.ts

import { test, expect } from '@playwright/test';

test('complete game round from registration to leaderboard', async ({ page }) => {
  // Navigate to homepage
  await page.goto('http://localhost:5173');
  
  // Register player
  await page.fill('input[name="username"]', 'e2e_test_player');
  await page.click('button:has-text("Register")');
  
  // Wait for PoW challenge to complete (may take a few seconds)
  await expect(page.locator('text=Registration successful')).toBeVisible({ timeout: 10000 });
  
  // Start game
  await page.click('a:has-text("Play")');
  
  // Verify photo loads
  await expect(page.locator('img[alt*="Airport"]')).toBeVisible();
  
  // Search for airport
  await page.fill('input[placeholder*="Search"]', 'JFK');
  await page.click('text=/John F Kennedy/i');
  
  // Submit guess
  await page.click('button:has-text("Submit Guess")');
  
  // Verify results shown
  await expect(page.locator('text=/Correct|Incorrect/i')).toBeVisible();
  await expect(page.locator('text=/Score:/i')).toBeVisible();
  
  // Navigate to leaderboard
  await page.click('a:has-text("Leaderboard")');
  
  // Verify player appears in leaderboard
  await expect(page.locator('text=e2e_test_player')).toBeVisible();
});
```

**Acceptance**:
- Full user journey completes without errors
- All UI elements render correctly
- API calls succeed
- Data persists correctly

---

### TC-013: Accessibility Audit - WCAG AA Compliance

**Requirement**: All pages must pass WCAG AA accessibility checks

**Test** (Automated with axe-core):
```typescript
// frontend/tests/e2e/accessibility.spec.ts

import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

test('homepage passes accessibility audit', async ({ page }) => {
  await page.goto('http://localhost:5173');
  await injectAxe(page);
  
  const violations = await checkA11y(page, null, {
    detailedReport: true,
    detailedReportOptions: { html: true }
  });
  
  expect(violations).toEqual([]);  // No violations allowed
});

test('play page passes accessibility audit', async ({ page }) => {
  // Assume authenticated session
  await page.goto('http://localhost:5173/play');
  await injectAxe(page);
  
  const violations = await checkA11y(page);
  expect(violations).toEqual([]);
});
```

**Acceptance**:
- No critical or serious accessibility violations
- Color contrast meets WCAG AA (4.5:1)
- All images have alt text
- All interactive elements are keyboard accessible

---

### TC-014: Performance Budget - Bundle Size

**Requirement**: Frontend bundle must be < 500KB gzipped

**Test** (Build-time check):
```bash
# Run production build
npm run build

# Check bundle size
cd dist && du -sh assets/*.js | awk '{sum+=$1} END {print sum}'

# Expected output: < 500KB
```

**Acceptance**:
- Total bundle size (all JS files gzipped) < 500KB
- Individual chunks < 200KB each
- No duplicate dependencies

---

### TC-015: Performance Budget - Page Load Time

**Requirement**: Page load time < 3 seconds on 3G

**Test** (Lighthouse audit):
```bash
# Run Lighthouse with 3G throttling
npx lighthouse http://localhost:5173 \
  --throttling-method=devtools \
  --throttling.cpuSlowdownMultiplier=4 \
  --throttling.downloadThroughputKbps=1600 \
  --throttling.uploadThroughputKbps=750 \
  --throttling.rttMs=300 \
  --output=json \
  --output-path=lighthouse-report.json

# Check performance score
cat lighthouse-report.json | jq '.categories.performance.score'

# Expected score: >= 0.9 (90/100)
```

**Acceptance**:
- Performance score ≥ 90/100
- First Contentful Paint < 2s
- Time to Interactive < 3s

---

## Contract Test Summary

| Priority | Test ID | Area | Type | Automated | Status |
|----------|---------|------|------|-----------|--------|
| P0 | TC-001 | Backend | Manual | No | To Do |
| P0 | TC-002 | Frontend | Manual | No | To Do |
| P0 | TC-003 | API | Integration | Yes | To Do |
| P0 | TC-004 | API | Integration | Yes | To Do |
| P0 | TC-005 | API | Integration | Yes | To Do |
| P0 | TC-006 | Privacy | Unit | Yes | To Do |
| P1 | TC-007 | Moderation | Unit | Yes | To Do |
| P1 | TC-008 | Moderation | Unit | Yes | To Do |
| P1 | TC-009 | Security | Unit | Yes | To Do |
| P1 | TC-010 | Frontend | Component | Manual (P2: Automated) | To Do |
| P1 | TC-011 | Data | Integration | Yes | To Do |
| P2 | TC-012 | E2E | Playwright | Yes | Deferred |
| P2 | TC-013 | Accessibility | Playwright + axe | Yes | Deferred |
| P2 | TC-014 | Performance | Build-time | Yes | Deferred |
| P2 | TC-015 | Performance | Lighthouse | Yes | Deferred |

**Total Tests**: 15 (6 P0, 5 P1, 4 P2)  
**Automated**: 11/15 (73%)  
**Manual**: 4/15 (27% - to be automated in P2)
