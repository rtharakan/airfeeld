# Research: Aviation Games

**Feature**: Aviation Games  
**Phase**: Phase 0 - Research  
**Date**: 2026-01-31  
**Purpose**: Resolve technical unknowns and establish best practices for implementation

## Research Tasks

This document addresses technical unknowns identified during specification and planning, particularly the deferred categories from clarification: aviation data sources and performance optimization.

---

## 1. Open Aviation Data Sources

### Decision: OurAirports + OpenFlights for airport data, with fallback strategies

### Research Context

The specification requires open, publicly available aviation databases for airports (IATA/ICAO codes), airlines, and aircraft models (FR-038 to FR-041). Need to identify sources that are:
- Legally open (public domain or permissive license)
- Comprehensive (500+ airports minimum)
- Maintained and accurate
- Downloadable for offline use
- Privacy-respecting (no user tracking to access data)

### Sources Evaluated

| Source | Type | Coverage | License | Update Frequency | Verdict |
|--------|------|----------|---------|------------------|---------|
| **OurAirports** | Airports | 70,000+ airports worldwide | Public Domain (CC0) | Monthly | ✅ **Primary** |
| **OpenFlights** | Airports, Airlines, Aircraft | 14,000+ airports, 6,000+ airlines | Open Database License | Irregular | ✅ **Secondary** |
| **ICAO Data** | Official codes | All registered airports | Proprietary (paid) | Quarterly | ❌ **Rejected** (not open) |
| **FlightRadar24 API** | Live flight data | Real-time | Commercial API | Real-time | ❌ **Rejected** (not open) |
| **OpenSky Network** | Flight tracking | Live ADS-B data | Creative Commons | Real-time | ✅ **For aircraft mode only** |
| **Plane Spotters** | Aircraft data | 450,000+ aircraft | Database available | Regular | ⚠️ **Evaluate license** |

### Selected Approach

**Airports (FR-002):**
- **Primary**: OurAirports (https://ourairports.com/data/)
  - CSV format: airports.csv, countries.csv, regions.csv
  - Fields: ident (ICAO), iata_code, name, latitude_deg, longitude_deg, continent, iso_country, iso_region, municipality, type
  - Public domain (CC0) - no attribution required but will provide credit
  - Download full dataset, import into SQLite on initial setup
  - Filter to: type IN ('large_airport', 'medium_airport') for initial 500+ airports
  
- **Fallback**: OpenFlights airports.dat
  - If OurAirports data quality issues found
  - Fields: Airport ID, Name, City, Country, IATA, ICAO, Lat, Lon, Altitude, Timezone, DST, Tz

**Airlines (FR-007):**
- **Primary**: OpenFlights airlines.dat
  - Fields: Airline ID, Name, Alias, IATA, ICAO, Callsign, Country, Active
  - Open Database License (ODbL) - requires attribution
  - Filter to active airlines only

**Aircraft Models (FR-008):**
- **Primary**: Manual curated list from public sources (Wikipedia, manufacturer data)
  - Focus on common commercial aircraft: Boeing 737/747/777/787, Airbus A320/A330/A350/A380, etc.
  - ~50 aircraft models sufficient for MVP
  - Structure: Manufacturer, Model, Type (narrow-body, wide-body, regional)
  
- **Alternative**: Plane Spotters database (if license compatible)
  - More comprehensive but need to verify ODbL compatibility

**Live Flight Data (FR-010, FR-033):**
- **Primary**: OpenSky Network API (https://opensky-network.org/)
  - REST API for ADS-B flight data
  - Creative Commons BY-SA 4.0
  - Free tier: 400 API calls/day (sufficient for aircraft identification mode)
  - Required for matching photo location to active flights
  - Rate limiting strategy: cache results for 5 minutes, limit aircraft mode attempts per user

### Rationale

OurAirports chosen for comprehensiveness (70k airports vs 14k) and true public domain status (CC0). OpenFlights provides complementary airline/aircraft data with ODbL license (requires attribution, which aligns with openness principle). OpenSky Network is the only viable open-source live flight tracker - alternatives like FlightRadar24 are commercial and violate constitution principle V (Openness).

### Data Update Strategy

- **Initial seeding**: Download and import all datasets on first deployment
- **Periodic refresh**: Monthly cron job to download updated OurAirports/OpenFlights data
- **Version tracking**: Store data version/date in database, display in UI for transparency
- **No automatic deletion**: Keep existing photos even if airport removed from dataset (archive, don't delete)

### Implementation Notes

```python
# Example data import structure
import csv
import sqlite3

def import_ourairports_data(csv_path, db_conn):
    """Import OurAirports CSV into SQLite database"""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['type'] in ['large_airport', 'medium_airport']:
                db_conn.execute("""
                    INSERT INTO airports (icao, iata, name, lat, lon, country, region)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['ident'],
                    row['iata_code'],
                    row['name'],
                    float(row['latitude_deg']),
                    float(row['longitude_deg']),
                    row['iso_country'],
                    row['iso_region']
                ))
    db_conn.commit()
```

---

## 2. EXIF Data Stripping Implementation

### Decision: Pillow (PIL) with complete metadata removal

### Research Context

FR-012 mandates stripping all EXIF location data from uploaded photos. Need library that:
- Removes GPS coordinates (latitude, longitude, altitude)
- Removes device identifiers (camera make/model, serial number)
- Removes timestamps (could reveal travel patterns)
- Preserves image quality
- Cross-platform (macOS, Linux for deployment)
- Python compatible (backend language)

### Libraries Evaluated

| Library | Language | Metadata Removal | Image Quality | Verdict |
|---------|----------|------------------|---------------|---------|
| **Pillow** | Python | Full control via Image.getexif() | Lossless | ✅ **Selected** |
| **ExifTool** | Perl (CLI) | Comprehensive | Lossless | ⚠️ External dependency |
| **piexif** | Python | EXIF only | Lossless | ⚠️ Limited to EXIF |
| **pyexiv2** | Python | Full metadata | Lossless | ❌ Heavy dependency |

### Selected Approach

**Pillow (PIL Fork)** - balances simplicity and control:

```python
from PIL import Image
import io

def strip_exif_data(image_bytes: bytes) -> bytes:
    """
    Remove ALL metadata from image, return clean bytes.
    Privacy-critical operation - MUST NOT fail silently.
    """
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_bytes))
        
        # Create new image without metadata
        # This discards EXIF, IPTC, XMP, and other metadata
        clean_image = Image.new(image.mode, image.size)
        clean_image.putdata(list(image.getdata()))
        
        # Save to bytes without metadata
        output = io.BytesIO()
        clean_image.save(output, format=image.format or 'JPEG', quality=95)
        
        # Verify no EXIF data remains
        verification = Image.open(io.BytesIO(output.getvalue()))
        if verification.getexif():
            raise ValueError("EXIF stripping failed - metadata still present")
        
        return output.getvalue()
        
    except Exception as e:
        # NEVER save photo if EXIF stripping fails
        raise RuntimeError(f"Critical: EXIF stripping failed - {e}")
```

### Verification Strategy

- **Pre-upload check**: Frontend warns if photo has GPS data (optional, not blocking)
- **Backend enforcement**: EXIF stripping happens immediately on upload, before any storage
- **Post-strip verification**: Re-read image and assert no EXIF data present
- **Test coverage**: Unit tests with known GPS-tagged photos verify complete removal
- **Audit logging**: Log when EXIF data is stripped (not the data itself, just the fact)

### Rationale

Pillow is already a FastAPI ecosystem standard, lightweight, and provides full control over metadata removal. Creating a new image from pixel data (rather than just removing EXIF tags) ensures no hidden metadata survives. The verification step is critical - we MUST fail loudly if stripping doesn't work, rather than silently storing location data.

---

## 3. Progressive 3-Attempt Scoring System

### Decision: State machine with distance calculation caching

### Research Context

Clarification defined a 3-attempt system (10/5/3 points) with distance feedback (exact km/miles) on attempt 2. Need to implement:
- State machine tracking current attempt (1/2/3)
- Distance calculation between airports (Haversine formula)
- Country lookup for hint (attempt 3)
- Score multiplier application (when difficulty system active)
- Client-server synchronization (prevent cheating)

### Distance Calculation Approach

**Haversine Formula** for great-circle distance:

```python
import math

def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great-circle distance between two coordinates.
    Returns distance in kilometers.
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def format_distance(distance_km: float, unit: str = 'metric') -> str:
    """Format distance for display"""
    if unit == 'imperial':
        distance_miles = distance_km * 0.621371
        return f"{distance_miles:.1f} miles"
    return f"{distance_km:.1f} km"
```

### State Machine Design

```python
from enum import Enum
from typing import Optional

class AttemptState(Enum):
    ATTEMPT_1 = 1
    ATTEMPT_2 = 2
    ATTEMPT_3 = 3
    COMPLETED = 4

class GameRound:
    photo_id: str
    player_id: str
    correct_airport_id: str
    state: AttemptState
    attempt_1_guess: Optional[str]
    attempt_2_guess: Optional[str]
    attempt_3_guess: Optional[str]
    final_score: int
    difficulty_multiplier: float
    
    def submit_guess(self, guessed_airport_id: str) -> dict:
        """Process guess and return feedback"""
        if self.state == AttemptState.ATTEMPT_1:
            if guessed_airport_id == self.correct_airport_id:
                self.final_score = 10
                self.state = AttemptState.COMPLETED
                return {"correct": True, "score": 10, "final": True}
            else:
                self.attempt_1_guess = guessed_airport_id
                self.state = AttemptState.ATTEMPT_2
                return {"correct": False, "attempt": 2}
        
        elif self.state == AttemptState.ATTEMPT_2:
            # Calculate distance from attempt 1
            distance = self._calculate_distance(self.attempt_1_guess, self.correct_airport_id)
            if guessed_airport_id == self.correct_airport_id:
                self.final_score = 5
                self.state = AttemptState.COMPLETED
                return {"correct": True, "score": 5, "final": True, "distance": distance}
            else:
                self.attempt_2_guess = guessed_airport_id
                self.state = AttemptState.ATTEMPT_3
                return {"correct": False, "attempt": 3, "distance": distance}
        
        elif self.state == AttemptState.ATTEMPT_3:
            country_hint = self._get_country(self.correct_airport_id)
            if guessed_airport_id == self.correct_airport_id:
                self.final_score = 3
                self.state = AttemptState.COMPLETED
                return {"correct": True, "score": 3, "final": True, "country_hint": country_hint}
            else:
                self.final_score = 0
                self.state = AttemptState.COMPLETED
                return {
                    "correct": False, 
                    "score": 0, 
                    "final": True, 
                    "revealed_airport": self.correct_airport_id,
                    "country_hint": country_hint
                }
```

### Anti-Cheat Strategy

- **Server-side state**: All attempt tracking happens in backend, client only displays results
- **Round tokens**: Each game round gets unique token, expired after completion or 30 minutes
- **No client-side answer**: Frontend never receives correct answer until round complete
- **Rate limiting**: Max 1 guess per 5 seconds to prevent brute force

### Performance Optimization

- **Distance caching**: Cache distance calculations per airport pair (max 500×500 = 250k entries)
- **Lazy loading**: Only calculate distance when needed (attempt 2)
- **Country pre-computation**: Store country in airport table, no lookup needed
- **In-memory state**: Use Redis for active game rounds (10-minute TTL)

### Rationale

Server-side state machine prevents client manipulation. Haversine formula is standard for aviation distances. Caching optimizations address deferred performance concerns from clarification without premature complexity.

---

## 4. Dynamic Difficulty Multiplier System

### Decision: Background worker with statistical aggregation

### Research Context

Clarification defined difficulty multiplier based on community success rate: `multiplier = 1 / success_rate`, capped at 3x. System activates when ≥500 photos AND ≥100 players. Each photo needs ≥20 attempts before individual activation. Must retroactively adjust scores when system goes live.

### Architecture Decision

**Background Worker + Periodic Batch Processing** (avoids real-time complexity):

```python
# Difficulty calculation runs every hour as cron job
def calculate_difficulty_multipliers():
    """
    Recalculate difficulty for all photos with sufficient attempts.
    Only runs if global thresholds met.
    """
    # Check global activation
    photo_count = db.execute("SELECT COUNT(*) FROM photos").fetchone()[0]
    player_count = db.execute("SELECT COUNT(DISTINCT player_id) FROM players").fetchone()[0]
    
    if photo_count < 500 or player_count < 100:
        return  # System not yet active
    
    # Calculate per-photo difficulty
    photos_with_attempts = db.execute("""
        SELECT 
            photo_id,
            COUNT(*) as total_attempts,
            SUM(CASE WHEN final_score > 0 THEN 1 ELSE 0 END) as successful_attempts
        FROM game_rounds
        WHERE state = 'COMPLETED'
        GROUP BY photo_id
        HAVING total_attempts >= 20
    """).fetchall()
    
    for photo in photos_with_attempts:
        success_rate = photo['successful_attempts'] / photo['total_attempts']
        
        # Apply formula with caps
        if success_rate == 0:
            multiplier = 3.0  # Max cap
        else:
            multiplier = min(3.0, max(1.0, 1.0 / success_rate))
        
        db.execute("""
            UPDATE photo_difficulty 
            SET multiplier = ?, last_calculated = ?
            WHERE photo_id = ?
        """, (multiplier, datetime.now(), photo['photo_id']))
    
    db.commit()

def retroactively_adjust_scores():
    """
    One-time migration when difficulty system first activates.
    Recalculates all historical scores with new multipliers.
    """
    # Triggered manually or automatically on first activation
    rounds = db.execute("""
        SELECT gr.id, gr.final_score, pd.multiplier
        FROM game_rounds gr
        JOIN photo_difficulty pd ON gr.photo_id = pd.photo_id
        WHERE gr.state = 'COMPLETED' AND gr.final_score > 0
    """).fetchall()
    
    for round in rounds:
        adjusted_score = round['final_score'] * round['multiplier']
        db.execute("""
            UPDATE game_rounds 
            SET adjusted_score = ?
            WHERE id = ?
        """, (adjusted_score, round['id']))
    
    # Recalculate all player totals
    db.execute("""
        UPDATE players
        SET total_score = (
            SELECT COALESCE(SUM(adjusted_score), 0)
            FROM game_rounds
            WHERE player_id = players.id
        )
    """)
    
    db.commit()
```

### Database Schema Considerations

```sql
CREATE TABLE photo_difficulty (
    photo_id TEXT PRIMARY KEY,
    total_attempts INTEGER DEFAULT 0,
    successful_attempts INTEGER DEFAULT 0,
    multiplier REAL DEFAULT 1.0,
    last_calculated TIMESTAMP,
    FOREIGN KEY (photo_id) REFERENCES photos(id)
);

CREATE INDEX idx_photo_difficulty_multiplier ON photo_difficulty(multiplier);

-- Game rounds track both base and adjusted scores
CREATE TABLE game_rounds (
    id TEXT PRIMARY KEY,
    photo_id TEXT NOT NULL,
    player_id TEXT NOT NULL,
    final_score INTEGER DEFAULT 0,  -- Base score (10/5/3/0)
    adjusted_score REAL DEFAULT 0,   -- final_score * multiplier
    -- ... other fields
);
```

### Performance Considerations (Deferred Category)

1. **Calculation frequency**: Hourly cron job balances accuracy and load
2. **Indexing**: Index on `photo_difficulty.multiplier` for leaderboard queries
3. **Caching**: Cache multipliers in application memory, refresh hourly
4. **Query optimization**: Use materialized view for leaderboard (top 100 players)
5. **Write batching**: Batch difficulty updates in single transaction

### Monitoring & Observability

- **Metrics**: Track difficulty distribution (histogram of multipliers)
- **Alerts**: Alert if >10% of photos hit 3x cap (suggests data quality issue)
- **Audit log**: Log activation event, retroactive adjustment completion
- **UI transparency**: Show photo difficulty on result screen ("This photo has 2.3x difficulty")

### Rationale

Background worker avoids real-time calculation overhead during gameplay. Hourly recalculation provides ~99% accuracy with minimal compute cost. Retroactive adjustment ensures early adopters benefit from established multipliers. Capped at 3x prevents outliers from distorting leaderboard (addresses deferred performance concern).

---

## 5. Photo Seeding & Attribution

### Decision: Semi-automated Flickr/Wikimedia scraper with manual curation

### Research Context

Clarification defined mixed sources: Creative Commons (CC BY 2.0/CC0) + public domain. Need attribution display after reveal, alt text for accessibility. Must seed 500+ airports at launch.

### Data Collection Strategy

**Phase 1: Automated Discovery**

```python
import flickrapi
import requests

def search_flickr_aviation_photos(airport_icao: str, airport_name: str) -> list:
    """
    Search Flickr for CC-licensed aviation photos of specific airport.
    Returns metadata for manual review.
    """
    flickr = flickrapi.FlickrAPI(API_KEY, API_SECRET, format='parsed-json')
    
    photos = flickr.photos.search(
        text=f"{airport_name} airport runway takeoff landing",
        tags=f"aviation,airport,{airport_icao}",
        license='4,5,9,10',  # CC BY 2.0, CC BY-SA 2.0, CC0, Public Domain
        sort='relevance',
        per_page=10,
        extras='license,owner_name,url_c,description'
    )
    
    results = []
    for photo in photos['photos']['photo']:
        results.append({
            'flickr_id': photo['id'],
            'url': photo['url_c'],
            'photographer': photo['ownername'],
            'license': photo['license'],
            'title': photo['title'],
            'description': photo['description']['_content']
        })
    
    return results
```

**Phase 2: Manual Curation**

- Review photos for quality (clear runway/terminal, no people visible)
- Verify photo actually shows correct airport
- Generate alt text: "Runway view at {airport name}, showing {observable features}"
- Download and strip EXIF locally before upload
- Flag for content moderation if needed

**Phase 3: Attribution Storage**

```sql
CREATE TABLE photo_attribution (
    photo_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,  -- 'flickr', 'wikimedia', 'public_domain', 'user_upload'
    photographer_name TEXT,
    photographer_url TEXT,
    license TEXT NOT NULL,  -- 'CC BY 2.0', 'CC0', 'Public Domain'
    original_url TEXT,
    alt_text TEXT NOT NULL,
    FOREIGN KEY (photo_id) REFERENCES photos(id)
);
```

**Phase 4: Attribution Display**

```typescript
// Display after game round complete
<div className="attribution" aria-label="Photo credit">
  {photo.source === 'flickr' || photo.source === 'wikimedia' ? (
    <>
      Photo by <a href={photo.photographer_url}>{photo.photographer_name}</a>
      {' '}(License: {photo.license})
    </>
  ) : photo.source === 'public_domain' ? (
    <>Public domain image, courtesy of {photo.photographer_name}</>
  ) : (
    <>Contributed by community member</>
  )}
</div>
```

### Accessibility: Alt Text Generation

```python
def generate_alt_text(airport_name: str, airport_type: str, features: list[str]) -> str:
    """
    Generate descriptive alt text that doesn't reveal answer.
    Features: runway, terminal, mountains, ocean, urban, etc.
    """
    feature_text = ", ".join(features) if features else "aviation infrastructure"
    return f"Aerial or ground view of airport runway and facilities showing {feature_text}"

# Examples:
# "Aerial view of airport runway and facilities showing mountainous terrain"
# "Ground view of airport runway and facilities showing terminal architecture"
# "View of airport runway and facilities showing coastal features"
```

### Seeding Target

- 500 airports minimum (SC-009)
- Priority: Major international hubs (100), regional airports (200), scenic/distinctive airports (200)
- Geographic distribution: All continents represented
- Difficulty variety: Mix obvious (JFK, LAX) and challenging (small regional)

### Legal Compliance

- **CC BY 2.0**: Requires attribution (name + link) ✅ Implemented
- **CC0/Public Domain**: No attribution required, but we provide it anyway (principle V: Openness)
- **User uploads**: Display "Contributed by community" (no username to preserve privacy)
- **License verification**: Manual check during curation, stored in database

### Rationale

Semi-automated approach balances speed and quality. Flickr API provides legal access to CC-licensed content. Manual curation ensures photo quality and correct airport association. Attribution after reveal maintains clean gameplay while respecting creators (and licenses). Alt text supports accessibility constraint without revealing answers.

---

## 6. Frontend Technology Stack

### Decision: React 18 + TypeScript + Vite for web

### Research Context

Need frontend that supports:
- WCAG AA accessibility (4.5:1 contrast)
- Offline capability (Service Worker + caching)
- Minimalist design (neutral colors)
- Fast load times (<3s startup)
- Progressive enhancement (works without JS for critical content)

### Stack Selection

| Technology | Purpose | Rationale |
|------------|---------|-----------|
| **React 18** | UI framework | Industry standard, accessibility support, concurrent rendering |
| **TypeScript** | Type safety | Prevents runtime errors, better IDE support, contracts from backend |
| **Vite** | Build tool | Faster than Webpack, optimized HMR, smaller bundles |
| **Tailwind CSS** | Styling | Utility-first, easy WCAG AA compliance, tree-shaking |
| **React Router** | Navigation | Standard routing, supports lazy loading |
| **TanStack Query** | Data fetching | Caching, offline support, optimistic updates |
| **Workbox** | Service Worker | Google's PWA toolkit, offline caching |
| **Playwright** | E2E testing | Cross-browser, accessibility testing built-in |

### Accessibility Strategy

```typescript
// Color palette (WCAG AA compliant - 4.5:1 contrast minimum)
const colors = {
  background: '#FFFFFF',      // White
  surface: '#F5F5F5',         // Light gray
  primary: '#1E3A8A',         // Deep blue (7.8:1 contrast on white)
  secondary: '#64748B',       // Slate gray (4.9:1 contrast on white)
  text: '#1F2937',            // Near black (14.6:1 contrast on white)
  textSecondary: '#4B5563',   // Dark gray (7.8:1 contrast on white)
  accent: '#0369A1',          // Sky blue (6.4:1 contrast on white)
  error: '#B91C1C',           // Red (5.9:1 contrast on white)
  success: '#047857',         // Green (4.7:1 contrast on white)
};

// Component example with accessibility
const PhotoViewer: React.FC<PhotoViewerProps> = ({ photo }) => {
  return (
    <figure role="img" aria-label={photo.altText}>
      <img 
        src={photo.url} 
        alt={photo.altText}
        loading="lazy"
      />
      <figcaption className="sr-only">
        {photo.altText}
      </figcaption>
    </figure>
  );
};
```

### Progressive Enhancement

```html
<!-- Server renders basic content, JavaScript enhances -->
<noscript>
  <div class="no-js-warning">
    This game works best with JavaScript enabled, but you can still view 
    leaderboards and documentation without it.
  </div>
</noscript>

<!-- Critical CSS inlined, rest lazy loaded -->
<style>/* Inline critical CSS */</style>
<link rel="stylesheet" href="/styles/main.css" media="print" onload="this.media='all'">
```

### Offline Capability

```typescript
// Service Worker strategy (Workbox)
import { precacheAndRoute } from 'workbox-precaching';
import { registerRoute } from 'workbox-routing';
import { CacheFirst, StaleWhileRevalidate } from 'workbox-strategies';

// Precache app shell
precacheAndRoute(self.__WB_MANIFEST);

// Cache photos (with size limit)
registerRoute(
  ({ url }) => url.pathname.startsWith('/api/photos/'),
  new CacheFirst({
    cacheName: 'photos-cache',
    plugins: [
      new ExpirationPlugin({
        maxEntries: 50,  // ~10 game rounds worth
        maxAgeSeconds: 7 * 24 * 60 * 60,  // 1 week
      }),
    ],
  })
);

// Cache API responses (recent data)
registerRoute(
  ({ url }) => url.pathname.startsWith('/api/'),
  new StaleWhileRevalidate({
    cacheName: 'api-cache',
    plugins: [
      new ExpirationPlugin({
        maxEntries: 100,
        maxAgeSeconds: 5 * 60,  // 5 minutes
      }),
    ],
  })
);
```

### Performance Budget

- **Initial bundle**: <150KB gzipped
- **Time to Interactive**: <3s on 3G
- **First Contentful Paint**: <1s
- **Largest Contentful Paint**: <2.5s
- **Cumulative Layout Shift**: <0.1

### Rationale

React 18 provides modern concurrent rendering for smooth UX. TypeScript enforces type safety between frontend and backend contracts. Vite dramatically reduces build times vs Webpack. Tailwind enables rapid WCAG-compliant styling. Workbox provides battle-tested offline capability. This stack balances simplicity (no Redux, no GraphQL) with capability (offline, accessible, fast).

---

## 7. Testing Strategy

### Decision: TDD with contract, integration, and E2E coverage

### Research Context

Constitution principle VI requires tests written before implementation. Need strategy covering:
- Contract testing (API matches OpenAPI spec)
- Integration testing (multi-service workflows)
- Unit testing (business logic)
- E2E testing (user journeys)
- Accessibility testing (WCAG AA compliance)

### Test Pyramid

```
         /\
        /E2\      Playwright (critical user journeys)
       /----\
      / Integ \   pytest (API endpoints, workflows)
     /--------\
    / Contract \ pytest + OpenAPI validator
   /----------\
  /    Unit    \ pytest (services, utilities) + Jest (components)
 /--------------\
```

### Backend Testing (pytest)

```python
# Contract test - validates API matches OpenAPI spec
def test_gameplay_endpoint_contract(client, openapi_spec):
    """POST /api/game/guess must match OpenAPI specification"""
    response = client.post('/api/game/guess', json={
        'round_id': 'test-round-123',
        'guessed_airport': 'KJFK'
    })
    
    # Validate response against OpenAPI schema
    validate_response(response.json(), openapi_spec, '/api/game/guess', 'post', '200')
    assert response.status_code == 200

# Integration test - multi-step workflow
def test_complete_game_round_workflow(client, db):
    """Test full game round: start -> guess -> score -> leaderboard"""
    # Start round
    start_response = client.post('/api/game/start')
    round_id = start_response.json()['round_id']
    
    # Make guess (attempt 1, incorrect)
    guess1 = client.post(f'/api/game/guess', json={
        'round_id': round_id,
        'guessed_airport': 'KJFK'
    })
    assert guess1.json()['correct'] == False
    assert guess1.json()['attempt'] == 2
    
    # Make guess (attempt 2, correct)
    guess2 = client.post(f'/api/game/guess', json={
        'round_id': round_id,
        'guessed_airport': 'KLAX'
    })
    assert guess2.json()['correct'] == True
    assert guess2.json()['score'] == 5
    
    # Verify leaderboard updated
    leaderboard = client.get('/api/leaderboard')
    assert any(p['total_score'] >= 5 for p in leaderboard.json()['players'])

# Unit test - EXIF stripping
def test_exif_stripping_removes_gps_data():
    """EXIF stripping must remove ALL location metadata"""
    # Load test image with GPS data
    with open('tests/fixtures/photo_with_gps.jpg', 'rb') as f:
        original_bytes = f.read()
    
    # Verify GPS data present in original
    original = Image.open(io.BytesIO(original_bytes))
    assert original.getexif().get(34853)  # GPS IFD tag
    
    # Strip EXIF
    clean_bytes = strip_exif_data(original_bytes)
    
    # Verify GPS data removed
    clean = Image.open(io.BytesIO(clean_bytes))
    assert not clean.getexif()
    assert clean.getexif().get(34853) is None
```

### Frontend Testing (Jest + Playwright)

```typescript
// Unit test - React component (Jest + React Testing Library)
describe('AirportSearch', () => {
  it('filters airports as user types', async () => {
    render(<AirportSearch onSelect={jest.fn()} />);
    
    const input = screen.getByRole('searchbox', { name: /search airports/i });
    await userEvent.type(input, 'JFK');
    
    // Should show matching results
    expect(await screen.findByText(/John F Kennedy/i)).toBeInTheDocument();
    expect(screen.queryByText(/Los Angeles/i)).not.toBeInTheDocument();
  });
  
  it('meets WCAG AA contrast requirements', () => {
    const { container } = render(<AirportSearch onSelect={jest.fn()} />);
    
    // Check contrast ratio (requires jest-axe)
    const results = axe(container);
    expect(results).toHaveNoViolations();
  });
});

// E2E test - complete user journey (Playwright)
test('complete airport guessing game', async ({ page }) => {
  await page.goto('http://localhost:3000');
  
  // Start game
  await page.click('button:has-text("Start Game")');
  
  // Verify photo loads
  await expect(page.locator('img[alt*="airport"]')).toBeVisible();
  
  // Make incorrect guess (attempt 1)
  await page.fill('input[type="search"]', 'JFK');
  await page.click('button:has-text("John F Kennedy")');
  await page.click('button:has-text("Submit Guess")');
  
  // Should show distance feedback
  await expect(page.locator('text=miles away')).toBeVisible();
  
  // Make correct guess (attempt 2)
  await page.fill('input[type="search"]', 'LAX');
  await page.click('button:has-text("Los Angeles")');
  await page.click('button:has-text("Submit Guess")');
  
  // Should show success and score
  await expect(page.locator('text=Correct!')).toBeVisible();
  await expect(page.locator('text=5 points')).toBeVisible();
  
  // Verify leaderboard updates
  await page.click('a:has-text("Leaderboard")');
  await expect(page.locator('table')).toContainText('5');
});

// Accessibility E2E test
test('keyboard navigation works throughout app', async ({ page }) => {
  await page.goto('http://localhost:3000');
  
  // Tab through interactive elements
  await page.keyboard.press('Tab');  // Focus on "Start Game"
  await expect(page.locator('button:has-text("Start Game")')).toBeFocused();
  
  await page.keyboard.press('Enter');  // Activate button
  await page.waitForSelector('img[alt*="airport"]');
  
  // Continue tabbing through game interface
  await page.keyboard.press('Tab');  // Focus on search input
  await expect(page.locator('input[type="search"]')).toBeFocused();
});
```

### Coverage Targets

- **Backend unit tests**: >80% coverage (services, utilities)
- **Backend integration tests**: All API endpoints covered
- **Backend contract tests**: 100% OpenAPI spec coverage
- **Frontend unit tests**: >70% coverage (components, services)
- **Frontend E2E tests**: All critical user journeys (4 stories from spec)
- **Accessibility tests**: WCAG AA automated checks + manual audit

### CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v3
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:unit
      - run: npm run test:e2e
```

### Rationale

TDD enforces specification-driven development (principle VI). Contract tests ensure frontend-backend compatibility. Integration tests catch multi-service issues. E2E tests validate user journeys match spec acceptance scenarios. Accessibility tests enforce constraint from constitution. High coverage targets (>70%) without perfectionism (not 100%) balance thoroughness and pragmatism.

---

## Research Summary

All technical unknowns resolved. Key decisions:

1. **Aviation Data**: OurAirports (CC0) + OpenFlights (ODbL) + OpenSky Network (CC BY-SA)
2. **EXIF Stripping**: Pillow with verification, fail-loud approach
3. **Scoring System**: Server-side state machine, Haversine distance, anti-cheat tokens
4. **Difficulty System**: Background worker, hourly recalculation, 3x cap
5. **Photo Seeding**: Semi-automated Flickr scraping + manual curation, proper attribution
6. **Frontend Stack**: React 18 + TypeScript + Vite + Tailwind, offline-capable
7. **Testing**: TDD with contract/integration/E2E coverage, WCAG AA validation

All decisions align with constitution principles. No NEEDS CLARIFICATION items remain. Ready for Phase 1: Design (data model, contracts, quickstart).
