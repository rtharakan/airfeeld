# API Reference

**Airfeeld API v1.0**  
Base URL: `http://localhost:8000` (development)

All timestamps are in UTC ISO 8601 format.
All IDs are UUIDs.

## Authentication

Currently, the API uses a simple header-based player identification:
- `X-Player-ID`: Player UUID (for authenticated operations)

Future: JWT tokens or session-based auth may be added.

## Rate Limiting

All endpoints are rate-limited. Response headers:
- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Window reset time (Unix timestamp)

## Endpoints

### Health

#### GET /health
Check API health and database status.

**Response 200:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```

---

### Players

#### POST /players/challenge
Request a proof-of-work challenge for registration (bot prevention).

**Request Body:**
```json
{
  "accessibility_mode": false
}
```

**Response 201:**
```json
{
  "challenge_id": "uuid",
  "challenge_nonce": "hex_string",
  "difficulty": 5,
  "expires_in": 300
}
```

#### POST /players/register
Register a new player account with PoW solution.

**Request Body:**
```json
{
  "username": "pilot123",
  "challenge_id": "uuid",
  "solution_nonce": "hex_string"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "username": "pilot123",
  "games_played": 0,
  "total_score": 0
}
```

**Errors:**
- `409`: Username already taken
- `400`: Invalid PoW solution
- `422`: Validation error

#### GET /players/{player_id}
Get player public profile.

**Response 200:**
```json
{
  "id": "uuid",
  "username": "pilot123",
  "games_played": 42,
  "total_score": 15750
}
```

#### GET /players/{player_id}/stats
Get detailed player statistics.

**Response 200:**
```json
{
  "id": "uuid",
  "username": "pilot123",
  "games_played": 42,
  "total_score": 15750,
  "average_score": 375.0,
  "rank": 127
}
```

#### GET /players/{player_id}/export
Export all player data (GDPR compliance).

**Headers:** `X-Player-ID: {player_id}`

**Response 200:**
```json
{
  "player_id": "uuid",
  "username": "pilot123",
  "exported_at": "2026-02-01T10:30:00Z",
  "data": {
    "profile": {...},
    "game_history": [...],
    "uploaded_photos": [...]
  }
}
```

#### DELETE /players/{player_id}
Delete player account and all data (GDPR compliance).

**Headers:** `X-Player-ID: {player_id}`

**Response 204:** No content

---

### Games

#### POST /games/rounds
Start a new game round.

**Request Body:**
```json
{
  "player_id": "uuid"
}
```

**Response 201:**
```json
{
  "round_id": "uuid",
  "photo_id": "uuid",
  "time_remaining": 300,
  "max_guesses": 5
}
```

#### GET /games/rounds/{round_id}
Get round status.

**Response 200:**
```json
{
  "round_id": "uuid",
  "status": "active",
  "guesses_made": 2,
  "max_guesses": 5,
  "time_remaining": 180,
  "current_score": 750
}
```

#### POST /games/rounds/{round_id}/guesses
Submit a guess.

**Request Body:**
```json
{
  "aircraft_guess": "Boeing 737-800",
  "location_lat": 40.6413,
  "location_lon": -73.7781
}
```

**Response 201:**
```json
{
  "guess_id": "uuid",
  "guess_number": 1,
  "aircraft_score": 950,
  "location_score": 800,
  "total_score": 1750,
  "distance_km": 12.5
}
```

#### POST /games/rounds/{round_id}/complete
Complete and finalize a round.

**Response 200:**
```json
{
  "round_id": "uuid",
  "photo_id": "uuid",
  "status": "completed",
  "final_score": 1750,
  "aircraft_score": 950,
  "location_score": 800,
  "guesses_made": 3,
  "correct_aircraft": "Boeing 737-800",
  "correct_location": {
    "airport": "JFK",
    "name": "John F. Kennedy International Airport",
    "lat": 40.6413,
    "lon": -73.7781
  }
}
```

---

### Photos

#### GET /photos/{photo_id}
Get photo metadata.

**Response 200:**
```json
{
  "id": "uuid",
  "filename": "uuid.jpg",
  "width": 1920,
  "height": 1080,
  "status": "approved",
  "times_used": 42
}
```

#### POST /photos/upload
Upload a new photo (EXIF stripped automatically).

**Request:** `multipart/form-data`
- `file`: Image file (JPEG/PNG/WebP, max 10MB)
- `aircraft_type`: string
- `airport_code`: string (optional)

**Response 201:**
```json
{
  "id": "uuid",
  "status": "pending",
  "message": "Photo uploaded and awaiting moderation"
}
```

---

### Leaderboard

#### GET /leaderboard
Get global leaderboard.

**Query Parameters:**
- `limit` (1-100, default 50): Number of entries
- `offset` (default 0): Pagination offset

**Response 200:**
```json
{
  "entries": [
    {
      "rank": 1,
      "player_id": "uuid",
      "username": "ace_pilot",
      "total_score": 42500,
      "games_played": 150
    }
  ],
  "total_players": 1250
}
```

#### GET /leaderboard/{player_id}/rank
Get specific player's rank.

**Response 200:**
```json
{
  "player_id": "uuid",
  "username": "pilot123",
  "rank": 127,
  "total_score": 15750,
  "games_played": 42,
  "percentile": 89.84
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Human-readable error message",
  "error_code": "ErrorClassName"
}
```

Common HTTP status codes:
- `400`: Bad request / validation failure
- `404`: Resource not found
- `409`: Conflict (e.g., duplicate username)
- `422`: Validation error (detailed field errors)
- `429`: Rate limit exceeded
- `500`: Internal server error

---

## Privacy Notes

- No cookies are set
- IP addresses are hashed (SHA-256) before storage
- EXIF metadata is automatically stripped from all photos
- No behavioral tracking or analytics
- All data exports available via GDPR endpoints
