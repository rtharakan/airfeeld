# Data Model: Release Preparation

**Feature**: 002-release-preparation  
**Phase**: Phase 1 - Design  
**Date**: 2026-02-01  
**Purpose**: Define data model changes and additions needed for release readiness

---

## Overview

This data model extends the existing [001-aviation-games data model](../001-aviation-games/data-model.md) with minimal additions required for content moderation, testing, and release preparation. No major schema changes are required - the existing model is sound and aligns with constitutional principles.

---

## Schema Changes

### 1. Photo Model - Content Moderation Fields

**Additions to existing Photo entity:**

```python
class Photo(Base):
    # ... existing fields from 001-aviation-games/data-model.md ...
    
    # NEW: Content moderation fields
    moderation_status = Column(Enum('pending', 'approved', 'rejected', 'flagged'), default='pending')
    moderation_score = Column(Float, nullable=True)  # NSFW score 0.0-1.0
    moderation_checked_at = Column(DateTime, nullable=True)
    rejection_reason = Column(String, nullable=True)  # Human-readable reason if rejected
    
    # NEW: Attribution metadata (for Creative Commons photos)
    attribution_author = Column(String, nullable=True)  # Photographer name
    attribution_source = Column(String, nullable=True)  # "Wikimedia Commons", "Flickr"
    attribution_url = Column(String, nullable=True)  # Link to original photo page
    attribution_license = Column(String, nullable=True)  # "CC BY 2.0", "CC0", "Public Domain"
```

**Validation Rules:**
- `moderation_status` must transition: pending → (approved | rejected | flagged)
- `moderation_score` range: 0.0 (safe) to 1.0 (explicit)
- Thresholds:
  - < 0.6: auto-approve
  - 0.6-0.8: flagged (manual review required)
  - > 0.8: auto-reject
- `rejection_reason` required if status = 'rejected'
- Attribution fields required if `upload_source` = 'seeded' and license is not Public Domain

**Privacy Constraints:**
- No personally identifying information in rejection reasons
- Moderation scores not displayed to users (internal only)

---

### 2. Testing Database Seeding

**Seed data required for tests:**

```yaml
# backend/tests/fixtures/seed_data.yaml
players:
  - id: "test-player-1-uuid"
    username: "test_player_1"
    total_score: 100
    games_played: 10
    
  - id: "test-player-2-uuid"
    username: "test_player_2"
    total_score: 50
    games_played: 5

airports:
  - icao: "KJFK"
    iata: "JFK"
    name: "John F Kennedy International Airport"
    country_code: "US"
    country_name: "United States"
    latitude: 40.639751
    longitude: -73.778925
    
  - icao: "EGLL"
    iata: "LHR"
    name: "London Heathrow Airport"
    country_code: "GB"
    country_name: "United Kingdom"
    latitude: 51.4700
    longitude: -0.4543

photos:
  - id: "test-photo-1-uuid"
    airport_id: "KJFK"
    file_path: "test/jfk_runway.jpg"
    verification_status: "approved"
    moderation_status: "approved"
    upload_source: "seeded"
    
  - id: "test-photo-2-uuid"
    airport_id: "EGLL"
    file_path: "test/lhr_terminal.jpg"
    verification_status: "approved"
    moderation_status: "approved"
    upload_source: "seeded"

game_rounds:
  - id: "test-round-1-uuid"
    player_id: "test-player-1-uuid"
    photo_id: "test-photo-1-uuid"
    correct_airport_id: "KJFK"
    state: "completed"
    final_score: 10
    adjusted_score: 10.0
```

**Purpose**: Tests require predictable data for assertions. Seed data provides known entities for unit and integration tests.

---

### 3. Index Additions for Performance

**Database indexes to add:**

```python
# In backend/src/models/player.py
__table_args__ = (
    Index('idx_player_username', 'username'),  # Fast username lookup for registration
    Index('idx_player_total_score', 'total_score', postgresql_using='btree'),  # Leaderboard queries
)

# In backend/src/models/photo.py
__table_args__ = (
    Index('idx_photo_airport_id', 'airport_id'),  # Photo selection by airport
    Index('idx_photo_moderation_status', 'moderation_status'),  # Filter approved photos
    Index('idx_photo_verification_status', 'verification_status'),  # Filter verified photos
)

# In backend/src/models/game_round.py
__table_args__ = (
    Index('idx_gameround_player_id', 'player_id'),  # Player game history
    Index('idx_gameround_photo_id', 'photo_id'),  # Photo usage tracking
    Index('idx_gameround_state', 'state'),  # Filter completed rounds
)
```

**Rationale**: Indexes improve query performance for:
- Leaderboard queries (sort by total_score)
- Photo selection (filter by moderation_status = 'approved')
- Player game history (filter by player_id)

**Performance Impact**: 
- Query time reduction: O(n) → O(log n) for indexed fields
- Storage overhead: Minimal (< 10% of table size)
- Write overhead: Minimal (indexes updated on insert/update)

---

## Validation State Machines

### Photo Moderation Workflow

```
┌─────────┐
│ PENDING │ (initial state on upload)
└────┬────┘
     │
     ├──── NSFW score < 0.6 ──────────┐
     │                                 │
     ├──── 0.6 ≤ NSFW score < 0.8 ────┤
     │                                 │
     └──── NSFW score ≥ 0.8 ───────────┤
                                       │
                                       ▼
            ┌──────────────────────────────────┐
            │                                  │
            │   ┌──────────┐   ┌──────────┐   │
            ├──>│ APPROVED │   │ FLAGGED  │   │
            │   └──────────┘   └────┬─────┘   │
            │                       │          │
            │                  Manual Review   │
            │                       │          │
            │                       ▼          │
            │                 ┌──────────┐     │
            └────────────────>│ REJECTED │<────┘
                              └──────────┘
```

**State Rules:**
1. All photos start in `PENDING` state
2. NSFW model runs automatically on upload
3. Auto-transitions:
   - Score < 0.6 → `APPROVED` (safe)
   - Score ≥ 0.8 → `REJECTED` (explicit)
4. Manual review required for `FLAGGED` (0.6-0.8 range)
5. Admin can override: `FLAGGED` → `APPROVED` or `REJECTED`
6. Once `APPROVED` or `REJECTED`, status is final (no transitions)

---

## Privacy-Preserving Data Flows

### Photo Upload Flow (with moderation)

```
User Upload
     │
     ▼
┌─────────────────┐
│ Validate File   │ ◄─── File type, size, dimensions
│ (No storage yet)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Profanity Check │ ◄─── Check filename for profanity
│ (Metadata only) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ NSFW Detection  │ ◄─── Local model (Yahoo/Tumblr)
│ (In memory)     │      Score: 0.0 - 1.0
└────────┬────────┘
         │
         ├── Score < 0.6 ──────────┐
         ├── 0.6 ≤ Score < 0.8 ─────┤
         └── Score ≥ 0.8 ────────────┤
                                     │
                                     ▼
                            ┌─────────────────┐
                            │ Strip EXIF Data │ ◄─── Remove GPS, timestamp, device ID
                            └────────┬────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │ Save to Storage │ ◄─── UUID filename, no metadata
                            └────────┬────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │ Save to DB      │ ◄─── With moderation_status
                            └─────────────────┘
```

**Privacy Guarantees:**
1. EXIF stripping happens BEFORE storage (no location data persisted)
2. NSFW detection runs in-memory (no external API calls)
3. Original filename discarded (UUID assigned)
4. No upload IP logging (ephemeral rate limiting only)

---

## Test Data Requirements

### Contract Tests (API validation)

**Required fixtures:**
- Valid player registration payload (with PoW solution)
- Valid photo upload payload (JPEG file, < 5MB)
- Valid guess submission payload (airport ICAO code)
- Invalid payloads for error testing (missing fields, invalid types)

### Integration Tests (Workflow validation)

**Required fixtures:**
- Pre-seeded player accounts (test_player_1, test_player_2)
- Pre-seeded photos (KJFK, EGLL, etc.)
- Pre-seeded airports (from OurAirports sample data)
- Mock PoW challenges (with known solutions)

### Unit Tests (Service validation)

**Required fixtures:**
- Mock NSFW model responses (scores: 0.2, 0.7, 0.9)
- Mock profanity filter lists
- Mock rate limit storage (in-memory Redis alternative)

---

## Migration Script

**Alembic migration for moderation fields:**

```python
# backend/migrations/versions/003_add_moderation_fields.py

"""Add content moderation fields to photos table

Revision ID: 003
Revises: 002
Create Date: 2026-02-01
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add moderation fields
    op.add_column('photos', sa.Column('moderation_status', 
        sa.Enum('pending', 'approved', 'rejected', 'flagged', name='moderation_status_enum'),
        nullable=False, server_default='pending'))
    op.add_column('photos', sa.Column('moderation_score', sa.Float, nullable=True))
    op.add_column('photos', sa.Column('moderation_checked_at', sa.DateTime, nullable=True))
    op.add_column('photos', sa.Column('rejection_reason', sa.String, nullable=True))
    
    # Add attribution fields
    op.add_column('photos', sa.Column('attribution_author', sa.String, nullable=True))
    op.add_column('photos', sa.Column('attribution_source', sa.String, nullable=True))
    op.add_column('photos', sa.Column('attribution_url', sa.String, nullable=True))
    op.add_column('photos', sa.Column('attribution_license', sa.String, nullable=True))
    
    # Add indexes
    op.create_index('idx_photo_moderation_status', 'photos', ['moderation_status'])
    op.create_index('idx_player_total_score', 'players', ['total_score'])
    op.create_index('idx_gameround_player_id', 'game_rounds', ['player_id'])

def downgrade():
    # Remove indexes
    op.drop_index('idx_gameround_player_id', 'game_rounds')
    op.drop_index('idx_player_total_score', 'players')
    op.drop_index('idx_photo_moderation_status', 'photos')
    
    # Remove columns
    op.drop_column('photos', 'attribution_license')
    op.drop_column('photos', 'attribution_url')
    op.drop_column('photos', 'attribution_source')
    op.drop_column('photos', 'attribution_author')
    op.drop_column('photos', 'rejection_reason')
    op.drop_column('photos', 'moderation_checked_at')
    op.drop_column('photos', 'moderation_score')
    op.drop_column('photos', 'moderation_status')
```

---

## Queries for Common Operations

### Leaderboard Query (Top 100)

```sql
SELECT username, total_score, games_played
FROM players
WHERE total_score > 0
ORDER BY total_score DESC, games_played ASC
LIMIT 100;
```

**Optimization**: Uses `idx_player_total_score` index for fast sorting.

### Photo Selection for Gameplay

```sql
SELECT p.id, p.file_path, p.airport_id
FROM photos p
WHERE p.moderation_status = 'approved'
  AND p.verification_status = 'approved'
  AND p.id NOT IN (
    SELECT photo_id FROM game_rounds WHERE player_id = :player_id
  )
ORDER BY RANDOM()
LIMIT 1;
```

**Optimization**: 
- Uses `idx_photo_moderation_status` index
- Subquery filters out seen photos (privacy: no duplicate photos per player)
- RANDOM() for variety (acceptable for MVP scale)

### Player Game History

```sql
SELECT gr.id, gr.final_score, gr.adjusted_score, p.file_path, a.name as airport_name
FROM game_rounds gr
JOIN photos p ON gr.photo_id = p.id
JOIN airports a ON gr.correct_airport_id = a.icao
WHERE gr.player_id = :player_id
  AND gr.state = 'completed'
ORDER BY gr.completed_at DESC
LIMIT 20;
```

**Optimization**: Uses `idx_gameround_player_id` index for fast player filtering.

---

## Summary

**No major schema changes required.** The existing data model from 001-aviation-games is sound. This document adds:

1. **Content moderation fields**: `moderation_status`, `moderation_score`, `rejection_reason`
2. **Attribution metadata**: `attribution_author`, `attribution_source`, `attribution_url`, `attribution_license`
3. **Database indexes**: For leaderboard, photo selection, game history queries
4. **Test fixtures**: Seed data for unit, integration, and contract tests
5. **Migration script**: Alembic migration to add new fields and indexes

**Constitutional alignment**: All changes respect Privacy by Design (no new tracking), Radical Simplicity (minimal additions), and Specification-Driven Development (documented before implementation).
