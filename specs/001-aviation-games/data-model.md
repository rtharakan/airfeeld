# Data Model: Aviation Games

**Feature**: Aviation Games  
**Phase**: Phase 1 - Design  
**Date**: 2026-01-31  
**Purpose**: Define entity relationships, validation rules, and state transitions

---

## Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Player    │────────<│  GameRound   │>────────│    Photo    │
└─────────────┘         └──────────────┘         └─────────────┘
      │                        │                        │
      │                        │                        ├──────────┐
      │                        │                        │          │
      ▼                        ▼                        ▼          ▼
┌─────────────┐         ┌──────────────┐         ┌─────────────┐ ┌──────────────┐
│ Leaderboard │         │    Guess     │         │   Airport   │ │ Attribution  │
│    Entry    │         └──────────────┘         └─────────────┘ └──────────────┘
└─────────────┘                                         │
                                                        ├─── Airline
                                                        └─── Aircraft
```

---

## Core Entities

### 1. Player

Represents a user account with minimal identifying information (Privacy by Design).

**Attributes:**
- `id` (UUID, primary key)
- `username` (string, unique, 3-20 chars)
- `total_score` (integer, default 0) - Sum of all adjusted scores
- `games_played` (integer, default 0)
- `created_at` (timestamp)
- `last_active` (timestamp)

**Validation Rules:**
- Username must be alphanumeric + underscore, no profanity
- Username cannot be changed after creation (prevents leaderboard manipulation)
- No email, password, or personal data stored (anonymous play)

**Privacy Constraints:**
- NO device identifiers
- NO IP address storage
- NO location history
- NO session tracking beyond active game

**Relationships:**
- One player → Many game rounds
- One player → One leaderboard entry

---

### 2. Photo

Represents an aviation image used in gameplay (EXIF stripped).

**Attributes:**
- `id` (UUID, primary key)
- `airport_id` (string, foreign key → Airport.icao)
- `file_path` (string) - Relative path in storage/photos/
- `file_size_bytes` (integer)
- `width_px` (integer)
- `height_px` (integer)
- `upload_source` (enum: 'seeded', 'user_upload')
- `uploader_id` (UUID, nullable, foreign key → Player.id)
- `verification_status` (enum: 'pending', 'approved', 'rejected')
- `uploaded_at` (timestamp)

**Validation Rules:**
- File formats: JPEG, PNG, WebP only
- Max file size: 10MB
- Min dimensions: 800x600px (ensures visibility)
- EXIF data MUST be stripped (verified post-upload)
- Airport association MUST exist in Airport table

**Privacy Constraints:**
- NO EXIF location data accessible (stripped before storage)
- NO original filename stored (use UUID)
- NO upload timestamp correlation to reveal patterns
- Uploader ID present but not displayed publicly (privacy)

**Relationships:**
- One photo → One airport
- One photo → One attribution record
- One photo → Many game rounds
- One photo → One difficulty record

---

### 3. Airport

Represents an airport in the official database (from OurAirports).

**Attributes:**
- `icao` (string, primary key, 4 chars)
- `iata` (string, nullable, 3 chars)
- `name` (string)
- `latitude` (decimal, 6 places)
- `longitude` (decimal, 6 places)
- `country_code` (string, ISO 3166-1 alpha-2)
- `country_name` (string)
- `region` (string) - e.g., "North America", "Europe"
- `municipality` (string) - City name
- `type` (enum: 'large_airport', 'medium_airport')
- `last_updated` (timestamp) - Data refresh tracking

**Validation Rules:**
- ICAO must be 4 uppercase letters
- IATA (if present) must be 3 uppercase letters
- Latitude: -90 to 90
- Longitude: -180 to 180
- Country code must be valid ISO 3166-1

**Relationships:**
- One airport → Many photos

---

### 4. Airline

Represents an airline in the official database (from OpenFlights).

**Attributes:**
- `id` (integer, primary key)
- `name` (string)
- `iata_code` (string, nullable, 2 chars)
- `icao_code` (string, nullable, 3 chars)
- `callsign` (string, nullable)
- `country` (string)
- `active` (boolean)
- `last_updated` (timestamp)

**Validation Rules:**
- IATA code (if present) must be 2 uppercase letters
- ICAO code (if present) must be 3 uppercase letters
- Only active airlines used in gameplay

**Relationships:**
- (Future: One airline → Many aircraft identification rounds)

---

### 5. Aircraft

Represents an aircraft model (curated list).

**Attributes:**
- `id` (integer, primary key)
- `manufacturer` (string) - e.g., "Boeing", "Airbus"
- `model` (string) - e.g., "737-800", "A320neo"
- `type` (enum: 'narrow_body', 'wide_body', 'regional', 'cargo')
- `common_name` (string) - e.g., "Boeing 737"

**Validation Rules:**
- Manufacturer + model must be unique
- Type must be one of defined enums

**Relationships:**
- (Future: One aircraft → Many aircraft identification rounds)

---

### 6. GameRound

Represents a single instance of gameplay (ephemeral, privacy-respecting).

**Attributes:**
- `id` (UUID, primary key)
- `player_id` (UUID, foreign key → Player.id)
- `photo_id` (UUID, foreign key → Photo.id)
- `correct_airport_id` (string, foreign key → Airport.icao)
- `state` (enum: 'attempt_1', 'attempt_2', 'attempt_3', 'completed')
- `attempt_1_guess` (string, nullable, foreign key → Airport.icao)
- `attempt_2_guess` (string, nullable, foreign key → Airport.icao)
- `attempt_3_guess` (string, nullable, foreign key → Airport.icao)
- `final_score` (integer) - Base score (10/5/3/0)
- `difficulty_multiplier` (decimal, default 1.0)
- `adjusted_score` (decimal) - final_score * difficulty_multiplier
- `round_token` (string, unique) - Anti-cheat token
- `expires_at` (timestamp) - Round expires after 30 minutes
- `started_at` (timestamp)
- `completed_at` (timestamp, nullable)

**Validation Rules:**
- Round token must be unique, random (UUID v4)
- Attempts must be sequential (can't skip from 1 to 3)
- Once completed, state cannot change
- Final score must be 0, 3, 5, or 10
- Difficulty multiplier must be 1.0 to 3.0

**State Transitions:**
```
attempt_1 → attempt_2 → attempt_3 → completed
    ↓           ↓           ↓
completed   completed   completed
```

**Privacy Constraints:**
- NO IP address or device fingerprint
- NO timing analysis data (beyond basic timestamps)
- Ephemeral - old rounds may be archived/deleted after leaderboard calculation
- NOT used for behavioral profiling

**Relationships:**
- One game round → One player
- One game round → One photo
- One game round → Multiple guesses (attempts)

---

### 7. Guess

Represents a single player's guess within a game round (for detailed analysis).

**Attributes:**
- `id` (UUID, primary key)
- `round_id` (UUID, foreign key → GameRound.id)
- `attempt_number` (integer, 1-3)
- `guessed_airport_id` (string, foreign key → Airport.icao)
- `correct` (boolean)
- `distance_km` (decimal, nullable) - Distance from guess to correct answer
- `submitted_at` (timestamp)

**Validation Rules:**
- Attempt number must be 1, 2, or 3
- Cannot have multiple guesses with same attempt number for same round
- Distance only calculated for incorrect guesses

**Privacy Constraints:**
- Used only for gameplay scoring, NOT behavioral tracking

**Relationships:**
- One guess → One game round
- One guess → One airport (guessed)

---

### 8. PhotoDifficulty

Represents dynamically calculated difficulty metadata (performance optimization).

**Attributes:**
- `photo_id` (UUID, primary key, foreign key → Photo.id)
- `total_attempts` (integer, default 0)
- `successful_attempts` (integer, default 0)
- `success_rate` (decimal, computed) - successful_attempts / total_attempts
- `multiplier` (decimal, default 1.0) - 1 / success_rate, capped [1.0, 3.0]
- `active` (boolean, default false) - True if ≥20 attempts
- `last_calculated` (timestamp)

**Validation Rules:**
- Success rate must be 0.0 to 1.0
- Multiplier must be 1.0 to 3.0
- Total attempts ≥ successful attempts
- Active only if total_attempts ≥ 20

**Calculation Logic:**
```python
if total_attempts < 20:
    active = False
    multiplier = 1.0
else:
    success_rate = successful_attempts / total_attempts
    if success_rate == 0:
        multiplier = 3.0
    else:
        multiplier = min(3.0, max(1.0, 1.0 / success_rate))
    active = True
```

**Global Activation:**
- System-wide difficulty only active when:
  - Total photos ≥ 500 AND
  - Unique players ≥ 100

**Relationships:**
- One photo difficulty → One photo

---

### 9. PhotoAttribution

Represents photographer credit and licensing (openness, legal compliance).

**Attributes:**
- `photo_id` (UUID, primary key, foreign key → Photo.id)
- `source` (enum: 'flickr', 'wikimedia', 'public_domain', 'user_upload')
- `photographer_name` (string)
- `photographer_url` (string, nullable)
- `license` (enum: 'CC BY 2.0', 'CC BY-SA 2.0', 'CC0', 'Public Domain')
- `original_url` (string, nullable)
- `alt_text` (string) - Accessibility description (doesn't reveal answer)

**Validation Rules:**
- License must match source (e.g., Flickr → CC BY 2.0)
- Alt text required for accessibility (100-200 chars)
- Alt text must NOT reveal airport name or location

**Privacy Constraints:**
- User uploads: Display "Contributed by community", NO username

**Relationships:**
- One attribution → One photo

---

### 10. LeaderboardEntry

Represents a player's position on the leaderboard (denormalized for performance).

**Attributes:**
- `player_id` (UUID, primary key, foreign key → Player.id)
- `username` (string) - Denormalized from Player
- `total_score` (decimal) - Sum of all adjusted_scores
- `games_played` (integer)
- `rank` (integer) - Calculated position
- `last_updated` (timestamp)

**Validation Rules:**
- Rank must be unique and sequential (1, 2, 3, ...)
- Total score must match sum of player's game rounds

**Update Strategy:**
- Recalculated hourly via background job
- Materialized view for performance
- Top 100 cached in Redis for instant access

**Privacy Constraints:**
- NO personal information beyond username and score
- NO social connections, friend lists, or follower graphs

**Relationships:**
- One leaderboard entry → One player

---

## Indexes for Performance

```sql
-- Leaderboard queries
CREATE INDEX idx_leaderboard_rank ON leaderboard_entry(rank);
CREATE INDEX idx_leaderboard_score DESC ON leaderboard_entry(total_score DESC);

-- Photo selection (random with difficulty)
CREATE INDEX idx_photo_difficulty_active ON photo_difficulty(active);
CREATE INDEX idx_photo_airport ON photo(airport_id);

-- Game round lookup
CREATE INDEX idx_gameround_token ON game_round(round_token);
CREATE INDEX idx_gameround_player ON game_round(player_id);

-- Airport search
CREATE INDEX idx_airport_name ON airport(name);
CREATE INDEX idx_airport_iata ON airport(iata);

-- Difficulty calculation
CREATE INDEX idx_gameround_photo ON game_round(photo_id);
CREATE INDEX idx_gameround_completed ON game_round(state) WHERE state = 'completed';
```

---

## State Transitions

### Game Round Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                     Game Round State Machine                 │
└─────────────────────────────────────────────────────────────┘

[CREATED]
    │
    ├── Player submits guess 1
    │
    ├─ If CORRECT ──────> [COMPLETED] (score: 10)
    │
    └─ If INCORRECT ───> [ATTEMPT_2]
                              │
                              ├── Player submits guess 2
                              │
                              ├─ If CORRECT ──> [COMPLETED] (score: 5)
                              │
                              └─ If INCORRECT ─> [ATTEMPT_3]
                                                     │
                                                     ├── Player submits guess 3
                                                     │
                                                     ├─ If CORRECT ─> [COMPLETED] (score: 3)
                                                     │
                                                     └─ If INCORRECT> [COMPLETED] (score: 0)

[EXPIRED]
    │
    └── Round not completed within 30 minutes
        (No score awarded, doesn't count toward stats)
```

### Photo Lifecycle

```
[UPLOADED]
    │
    ├── EXIF stripping ──> PASS ──> [PENDING_REVIEW]
    │                       │
    │                       FAIL ──> [REJECTED] (never stored)
    │
[PENDING_REVIEW]
    │
    ├── Manual moderation ──> APPROVE ──> [ACTIVE] (enters game pool)
    │                         │
    │                         REJECT ──> [REJECTED] (archived, not shown)
    │
[ACTIVE]
    │
    └── Used in gameplay, difficulty tracked
```

### Difficulty System Lifecycle

```
[SYSTEM INACTIVE]
    │
    ├── Conditions: photo_count < 500 OR player_count < 100
    │   All photos: multiplier = 1.0
    │
    └── Trigger: photo_count ≥ 500 AND player_count ≥ 100
            │
            ├── One-time: RETROACTIVE SCORE ADJUSTMENT
            │
            └───> [SYSTEM ACTIVE]
                      │
                      └── Hourly: Recalculate photo difficulties
                            │
                            └── For each photo with ≥20 attempts:
                                multiplier = 1 / success_rate (capped 1.0-3.0)
```

---

## Data Constraints & Invariants

### Privacy Invariants (MUST ALWAYS HOLD)

1. **No Location Tracking**: Player table MUST NOT contain location fields
2. **No Device Fingerprinting**: No device identifiers in any table
3. **EXIF Stripped**: All photos MUST pass EXIF verification before storage
4. **Anonymous Gameplay**: Game rounds MUST NOT store IP, user agent, or session data
5. **Minimal Identity**: Player profiles MUST contain ONLY username and score

### Data Integrity Invariants

1. **Score Consistency**: Player.total_score = SUM(GameRound.adjusted_score WHERE player_id = Player.id)
2. **Attempt Sequence**: GameRound attempts must be sequential (1→2→3, no gaps)
3. **Difficulty Bounds**: PhotoDifficulty.multiplier ∈ [1.0, 3.0]
4. **Airport References**: Every Photo.airport_id MUST exist in Airport table
5. **Token Uniqueness**: GameRound.round_token MUST be globally unique

### Performance Invariants

1. **Leaderboard Freshness**: Updated at least hourly
2. **Expired Rounds**: Cleaned up after 7 days (no gameplay impact)
3. **Photo Duplicates**: Prevented via hash comparison before upload
4. **Index Coverage**: All frequent queries MUST use indexes

---

## Data Retention & Cleanup

### Retention Periods

| Entity | Retention | Rationale |
|--------|-----------|-----------|
| Player | Indefinite | Core user data |
| Photo | Indefinite | Game content |
| GameRound (active) | 30 minutes | Gameplay session |
| GameRound (completed) | 90 days | Leaderboard calculation, then archive |
| Guess | 90 days | Difficulty calculation, then archive |
| PhotoDifficulty | Indefinite | Recalculated, not deleted |
| LeaderboardEntry | Indefinite | Rankings history |

### Cleanup Strategy

```python
# Daily cleanup job
def cleanup_expired_rounds():
    """Remove expired game rounds (not completed within 30 min)"""
    db.execute("""
        DELETE FROM game_round
        WHERE state != 'completed'
          AND expires_at < NOW()
    """)

def archive_old_rounds():
    """Archive completed rounds older than 90 days"""
    db.execute("""
        INSERT INTO game_round_archive
        SELECT * FROM game_round
        WHERE state = 'completed'
          AND completed_at < NOW() - INTERVAL '90 days'
    """)
    
    db.execute("""
        DELETE FROM game_round
        WHERE state = 'completed'
          AND completed_at < NOW() - INTERVAL '90 days'
    """)
```

---

## Migration Strategy

### Initial Schema Creation

```sql
-- Phase 1: Core tables (no dependencies)
CREATE TABLE player (...);
CREATE TABLE airport (...);
CREATE TABLE airline (...);
CREATE TABLE aircraft (...);

-- Phase 2: Content tables (depend on Phase 1)
CREATE TABLE photo (...);
CREATE TABLE photo_attribution (...);
CREATE TABLE photo_difficulty (...);

-- Phase 3: Gameplay tables (depend on Phase 1 & 2)
CREATE TABLE game_round (...);
CREATE TABLE guess (...);

-- Phase 4: Aggregation tables (depend on Phase 3)
CREATE TABLE leaderboard_entry (...);

-- Phase 5: Indexes (all tables created)
CREATE INDEX ...;
```

### Data Seeding Order

1. Import airports (OurAirports CSV)
2. Import airlines (OpenFlights DAT)
3. Import aircraft (manual curated list)
4. Seed photos with attributions (Flickr/Wikimedia)
5. Initialize photo_difficulty (multiplier = 1.0)
6. Create initial leaderboard (empty)

---

## Data Model Summary

**Total Entities**: 10  
**Core Gameplay**: Player, Photo, Airport, GameRound, Guess  
**Supporting**: Airline, Aircraft, PhotoDifficulty, PhotoAttribution, LeaderboardEntry  
**Privacy Compliance**: ✅ No tracking, minimal identity, EXIF stripped  
**Constitution Alignment**: ✅ All privacy and simplicity constraints satisfied

Ready for contract generation and quickstart documentation.
