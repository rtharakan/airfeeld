# Feature Specification: Aviation Games

**Feature Branch**: `001-aviation-games`  
**Created**: 2026-01-31  
**Status**: Draft  
**Input**: User description: "Privacy-preserving aviation game and discovery app with Airport Guessing Game and Aircraft & Airline Identification Game"

## Clarifications

### Session 2026-01-31

- Q: What visual design language and color accessibility standards should the UI follow? → A: Minimalist design with neutral colors (grays, blues, earth tones) following WCAG AA standards (4.5:1 contrast)
- Q: How should the scoring system work given airports are unique and specific? → A: Progressive 3-attempt system: Attempt 1 = 10 points if correct; Attempt 2 = show exact distance feedback (km/miles), 5 points if correct; Attempt 3 = reveal country hint, 3 points if correct, otherwise 0 points and reveal answer
- Q: How should the initial photo database be seeded before user contributions exist, and how should photographer attribution be handled? → A: Mixed sources: Creative Commons (CC BY 2.0/CC0) from Flickr/Wikimedia + Public domain (CC0/government sources). CC photos display photographer name + source link after reveal. Public domain shows source + license statement. Include alt text without revealing airport identity. Encourage early adopter contributions.
- Q: How should photos be selected for gameplay and should difficulty affect scoring? → A: Never show same photo twice to a player (different photos of same airport allowed). Dynamic difficulty multiplier based on community success rate: Multiplier = 1 / success_rate, capped at 3x max, 1x min. Requires 20 attempts per photo before activating. System activates globally when ≥500 photos AND ≥100 unique players. Multiplier applies to final awarded points only. Retroactively adjust all historical scores when system activates.
- Q: What distance feedback format should be shown in Attempt 2? → A: Exact distance in kilometers or miles from the guessed airport to the correct airport

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Play Airport Guessing Game (Priority: P1)

A player views an aviation photo and guesses which airport it was taken at, based purely on visual clues like runway layout, terminal architecture, terrain, weather, and signage. After submitting their guess, they receive immediate feedback showing the correct answer and their score.

**Why this priority**: This is the core gameplay loop that delivers immediate value and can function completely standalone. It demonstrates the app's privacy-first approach while providing entertainment and education about airports worldwide.

**Independent Test**: Can be fully tested by loading a pre-seeded photo with known airport metadata, allowing a player to make a guess, and verifying that correct/incorrect feedback is displayed without exposing any location metadata to the player.

**Acceptance Scenarios**:

1. **Given** the app has airport photos in its game pool, **When** a player starts a new game, **Then** they see a photo with no embedded location data visible
2. **Given** a player is viewing an airport photo, **When** they search for and select an airport from the database, **Then** their guess is recorded
3. **Given** a player has submitted their guess, **When** the result is revealed, **Then** they see the correct airport name, code, and their accuracy score
4. **Given** a player guessed correctly, **When** the result is revealed, **Then** their score increases and they see brief factual context about the airport
5. **Given** a player guessed incorrectly, **When** the result is revealed, **Then** they see how close their guess was (exact match, same region, same country, or no match)

---

### User Story 2 - Upload Airport Photo (Priority: P2)

A traveler who has taken a photo during take-off or landing can contribute it to the game pool by uploading the photo and selecting the correct airport from an authoritative database. The photo becomes available for other players to guess.

**Why this priority**: User-generated content expands the game's variety and longevity. This creates community value while maintaining privacy—uploaders share photos voluntarily without exposing personal flight details.

**Independent Test**: Can be fully tested by allowing a user to upload an image file, select an airport from the database, and verifying the photo appears in the game pool with correct airport association and no EXIF location data exposed.

**Acceptance Scenarios**:

1. **Given** a user has a photo from take-off or landing, **When** they initiate photo upload, **Then** they can select the image from their device
2. **Given** a photo is selected for upload, **When** the user searches for airports, **Then** they see a searchable list of official airport names and codes
3. **Given** a user has selected the correct airport, **When** they submit the photo, **Then** all EXIF location data is stripped before storage
4. **Given** a photo has been uploaded, **When** other players start a game, **Then** the new photo may appear in their game rotation
5. **Given** a photo is processed for upload, **When** EXIF data is stripped, **Then** no geographical coordinates, timestamps, or device identifiers remain accessible

---

### User Story 3 - Play Aircraft Identification Game (Priority: P3)

A player views a photo of an aircraft and guesses both the airline and aircraft model. After guessing, they see the correct answers and, if the aircraft is currently airborne, contextual flight information such as departure and arrival airports.

**Why this priority**: This adds educational value and variety, but requires more complex data correlation (matching photo to live flight data). It can be delivered after the core airport game is stable.

**Independent Test**: Can be fully tested by showing a player an aircraft photo, accepting their airline and model guesses, and verifying that correct answers are displayed along with optional contextual flight data when available.

**Acceptance Scenarios**:

1. **Given** the app has aircraft photos available, **When** a player starts aircraft identification mode, **Then** they see a photo of an aircraft
2. **Given** a player is viewing an aircraft photo, **When** they select an airline from the database, **Then** their airline guess is recorded
3. **Given** a player has guessed the airline, **When** they select an aircraft model, **Then** both guesses are recorded
4. **Given** a player has submitted both guesses, **When** the result is revealed, **Then** they see the correct airline and aircraft model
5. **Given** the aircraft in the photo is currently airborne, **When** the result is revealed, **Then** the player sees departure and arrival airport information
6. **Given** the aircraft in the photo is not currently airborne, **When** the result is revealed, **Then** the player sees the correct answers without flight route information

---

### User Story 4 - View Leaderboards (Priority: P3)

A player can view global leaderboards showing top-scoring players. Leaderboards display only usernames and scores, with no social graph, friend lists, or personal information.

**Why this priority**: Leaderboards add competitive motivation but are not essential for core gameplay. They can be added once scoring mechanics are stable.

**Independent Test**: Can be fully tested by pre-populating score data for multiple players and verifying that leaderboards display correctly ordered scores with usernames only, and no personal or social data.

**Acceptance Scenarios**:

1. **Given** multiple players have played games, **When** a player views the global leaderboard, **Then** they see a ranked list of usernames and scores
2. **Given** leaderboards exist, **When** a player views their ranking, **Then** they see their position without any social connections or friend suggestions
3. **Given** optional seasonal leaderboards are enabled, **When** a player views them, **Then** they see rankings scoped to the current time period

---

### Edge Cases

- What happens when a photo contains no identifiable airport features?
- What happens when a player submits an invalid or corrupt image file?
- How does the system handle photos from private or military airports not in public databases?
- What happens when photo location is required (aircraft mode) but the photo has no location metadata?
- How does the system handle aircraft that are not in active flight when a player attempts aircraft identification?
- What happens when a player searches for an airport that doesn't exist or uses an incorrect code?
- How does the system handle duplicate photo uploads?
- What happens when the open aviation database is unavailable or outdated?
- How does the system handle slow network connections or offline usage?

## Requirements *(mandatory)*

### Functional Requirements

**Gameplay**

- **FR-001**: System MUST display aviation photos to players with all EXIF location data removed
- **FR-002**: System MUST provide a searchable database of airport names and IATA/ICAO codes from open data sources
- **FR-003**: System MUST accept player guesses for airport identification and calculate accuracy scores
- **FR-004**: System MUST reveal correct airport information after final attempt or correct guess
- **FR-005**: System MUST implement progressive 3-attempt scoring: Attempt 1 awards 10 points for correct guess; Attempt 2 shows exact distance (km/miles) from Attempt 1 guess to correct airport and awards 5 points if correct; Attempt 3 reveals country hint and awards 3 points if correct, otherwise 0 points and reveals answer
- **FR-006**: System MUST display brief factual context about airports after correct guesses
- **FR-007**: System MUST provide a searchable database of airline names and identifiers from open data sources
- **FR-008**: System MUST provide a searchable database of aircraft manufacturers and models from open data sources
- **FR-009**: System MUST accept player guesses for both airline and aircraft model in aircraft identification mode
- **FR-010**: System MUST optionally display contextual flight information (departure/arrival airports) when aircraft is currently airborne

**Content Management**

- **FR-011**: System MUST allow users to upload photos taken during take-off or landing
- **FR-012**: System MUST strip all EXIF location data from uploaded photos before storage
- **FR-013**: System MUST require uploaders to select the correct airport from the official database
- **FR-014**: System MUST validate uploaded photos are in acceptable image formats
- **FR-015**: System MUST prevent duplicate photos from being added to the game pool
- **FR-016**: Uploaded photos MUST enter the public game pool and become available to all players
- **FR-017**: System MUST seed initial photo database using Creative Commons licensed photos (CC BY 2.0 or CC0) from sources like Flickr/Wikimedia and public domain photos (CC0/government sources)
- **FR-018**: System MUST display non-intrusive photographer attribution after game reveal: photographer name + source link for CC licensed photos, source + license statement for public domain photos
- **FR-019**: System MUST include descriptive alt text for all photos that does not reveal the airport identity
- **FR-020**: System MUST never show the same photo twice to the same player, though different photos of the same airport are allowed
- **FR-021**: System MUST implement dynamic difficulty multiplier based on community success rate: multiplier = 1 / success_rate, capped at 3x maximum and 1x minimum, requiring minimum 20 player attempts per photo before activation
- **FR-022**: Difficulty multiplier system MUST activate globally only when database contains ≥500 photos AND ≥100 unique players have completed rounds
- **FR-023**: System MUST apply difficulty multiplier only to final awarded points (not individual attempt values)
- **FR-024**: System MUST retroactively recalculate all historical player scores using established difficulty multipliers when the difficulty system activates

**Privacy & Data Handling**

- **FR-025**: System MUST NOT collect continuous or background location data
- **FR-026**: System MUST NOT track user movement history or location across sessions
- **FR-027**: System MUST NOT create behavioral profiles or analytics based on user activity
- **FR-028**: For aircraft identification mode only, system MUST request photo location data with explicit user consent
- **FR-029**: Photo location data in aircraft identification mode MUST be used only for one-time flight correlation
- **FR-030**: Photo location data MUST NOT be stored beyond what is necessary for gameplay
- **FR-031**: System MUST NOT link photo location data to persistent user identity or location history
- **FR-032**: System MUST separate gameplay data (scores, guesses) from personal data (device identifiers, location history)
- **FR-033**: Player profiles MUST contain only username and score data

**Leaderboards**

- **FR-034**: System MUST maintain a global leaderboard displaying usernames and scores
- **FR-035**: System MUST optionally support time-based or seasonal leaderboards
- **FR-036**: Leaderboards MUST NOT display social connections, friend lists, or follower graphs
- **FR-037**: Leaderboards MUST NOT expose personal information beyond username and score

**Data Sources**

- **FR-038**: System MUST use only open and publicly available aviation databases for airport, airline, and aircraft data
- **FR-039**: System MUST NOT use proprietary or scraped personal data
- **FR-040**: System MUST use authoritative airport codes (IATA/ICAO) from public sources
- **FR-041**: System MUST use publicly available flight metadata where needed for aircraft identification

**Platform Requirements**

- **FR-042**: System MUST run on desktop platforms (macOS initially, extensible to Windows/Linux)
- **FR-043**: System MUST run on Apple iOS (iPhone initially, iPad compatible)
- **FR-044**: Application MUST be lightweight with fast startup (<3s) and low battery usage (<5% per hour active play)
- **FR-045**: Application MUST support offline gameplay where possible (viewing cached photos)
- **FR-046**: Application UI MUST focus on images and guessing, without feeds or advertisements
- **FR-047**: Application UI MUST follow minimalist design language with neutral color palette (grays, blues, earth tones) and WCAG AA accessibility standards (minimum 4.5:1 contrast ratio for text)

**Player Account Security**

- **FR-048**: System MUST implement passwordless account creation using username-only registration combined with proof-of-work verification
- **FR-049**: System MUST require client-side proof-of-work challenge (SHA-256 hash with difficulty target of 4 leading zeros, ~50ms on modern device, 10-second timeout) before account creation to prevent bot registration
- **FR-050**: Proof-of-work MUST provide accessible fallback for low-power devices (reduced difficulty target of 2 leading zeros with extended 30-second timeout)
- **FR-051**: System MUST rate-limit account creation to maximum 3 accounts per IP address per 24-hour period (IP used transiently, not stored beyond rate limit window)
- **FR-052**: System MUST enforce username uniqueness without device fingerprinting or persistent identifiers
- **FR-053**: System MUST filter profanity from usernames using open-source word list (List of Dirty, Naughty, Obscene Words) with locale-aware matching
- **FR-054**: System MUST prevent leaderboard manipulation by limiting score submission rate to 1 game completion per 30 seconds per player
- **FR-055**: System MUST support account deletion with complete data erasure within 72 hours of request (GDPR Article 17 compliance)
- **FR-056**: System MUST support data export in JSON format within 30 days of request (GDPR Article 20 compliance)

**Database Security**

- **FR-057**: Database MUST use AES-256 encryption at rest for all stored data
- **FR-058**: All database queries MUST use parameterized statements to prevent SQL injection (no string concatenation in queries)
- **FR-059**: Database connections MUST use TLS 1.3 encryption in transit
- **FR-060**: Database access MUST follow principle of least privilege with role-based access control (read-only for gameplay, write for uploads)
- **FR-061**: Server logs MUST retain IP addresses for maximum 7 days, used only for rate limiting and security, then permanently deleted
- **FR-062**: System MUST implement audit logging for security events only (login attempts, account creation, data deletion) without behavioral tracking
- **FR-063**: Backup systems MUST use encrypted storage with 90-day retention limit and geographic restriction to same jurisdiction

**Photo Content Moderation**

- **FR-064**: System MUST validate file format using magic number verification (not file extension) accepting only JPEG (FFD8FF), PNG (89504E47), and WebP (52494646)
- **FR-065**: System MUST enforce maximum image dimensions of 8192x8192 pixels to prevent resource exhaustion attacks
- **FR-066**: System MUST compute perceptual hash (pHash) for each upload and reject duplicates with >95% similarity to existing photos
- **FR-067**: System MUST reject photos that fail EXIF stripping verification (fail-loud: reject upload, log security event, do NOT store)
- **FR-068**: System MUST scan uploads against known inappropriate content hash database (Microsoft PhotoDNA API or equivalent open-source: photodna-api) and reject matches
- **FR-069**: System MUST perform basic aviation content validation: reject images where <10% of pixels contain aviation-relevant colors (runway gray #808080±30, sky blue #87CEEB±50, grass green #228B22±40) using histogram analysis
- **FR-070**: System MUST detect and reject AI-generated images using statistical analysis (JPEG compression artifact consistency, noise pattern analysis) with 90% confidence threshold
- **FR-071**: System MUST perform OCR scan and reject images containing offensive text (same word list as FR-053)
- **FR-072**: Photos failing ≥3 automated checks but confirmed genuine by uploader MUST enter manual review queue
- **FR-073**: Manual review queue MUST be processed within 48 hours; photos not reviewed within window are auto-rejected with notification to uploader
- **FR-074**: Manual reviewers MUST NOT have access to uploader identity beyond username; review MUST be blind
- **FR-075**: System MUST provide specific rejection reasons to uploaders (e.g., "No aviation content detected", "Duplicate of existing photo", "Inappropriate content detected")
- **FR-076**: Rejected uploads MUST allow one appeal with additional context; appeal decision is final
- **FR-077**: Approved photos MUST be removable post-approval if flagged by ≥3 unique players; flagged photos enter manual review
- **FR-078**: System MUST rate-limit flagging to 5 reports per player per 24 hours to prevent abuse
- **FR-079**: Photo storage MUST use isolated directories with no-execute permissions and path traversal protection (reject filenames containing .. or /)

### Non-Functional Requirements

**Environmental Sustainability (Hugging Face Responsible AI Alignment)**

- **NFR-001**: Backend API MUST maintain average CPU utilization below 30% during normal operation to minimize energy consumption
- **NFR-002**: Frontend bundle size MUST NOT exceed 100KB gzipped for initial load to reduce network energy transfer
- **NFR-003**: Images MUST be served in WebP format with 80% quality compression (fallback to JPEG 85% for unsupported browsers) to minimize bandwidth
- **NFR-004**: API responses MUST be cached for 5 minutes (airports, airlines, leaderboard) with ETags for conditional requests to reduce redundant computation
- **NFR-005**: Database queries MUST be optimized with indexes; no query may exceed 100ms execution time under normal load
- **NFR-006**: System MUST implement request coalescing for concurrent identical requests to prevent redundant processing
- **NFR-007**: Hosting infrastructure SHOULD prefer providers with documented renewable energy usage (>50% renewable) or carbon offset programs
- **NFR-008**: Photo storage MUST implement lifecycle management: photos with zero plays in 365 days moved to cold storage; deleted after 730 days of inactivity
- **NFR-009**: Offline-first design MUST reduce continuous network polling; sync only on user action or 15-minute intervals when app is active

**Performance**

- **NFR-010**: Application startup time MUST be under 3 seconds on target devices (iPhone 12 or equivalent, 4G connection)
- **NFR-011**: Photo load time MUST be under 1 second for cached photos, under 3 seconds for network fetch
- **NFR-012**: Airport search response MUST complete within 500ms for queries up to 1000 results
- **NFR-013**: Memory usage MUST NOT exceed 100MB during active gameplay
- **NFR-014**: Application MUST support 100 concurrent players without degradation (response time <2x baseline)

**Security**

- **NFR-015**: All API endpoints MUST be protected against common OWASP Top 10 vulnerabilities
- **NFR-016**: System MUST implement rate limiting: 60 requests/minute per IP for gameplay, 10 requests/minute for uploads
- **NFR-017**: All external dependencies MUST be pinned to specific versions and audited for known vulnerabilities monthly
- **NFR-018**: System MUST support graceful degradation under DoS conditions (serve cached content, queue requests)

**Accessibility**

- **NFR-019**: All interactive elements MUST be keyboard navigable with visible focus indicators
- **NFR-020**: All images MUST have descriptive alt text that does not reveal gameplay answers
- **NFR-021**: Color MUST NOT be the sole means of conveying information (patterns, labels required)
- **NFR-022**: Text MUST be resizable to 200% without loss of functionality
- **NFR-023**: System MUST support reduced motion preferences (prefers-reduced-motion media query)

**Compliance**

- **NFR-024**: System MUST comply with GDPR (EU), CCPA (California), and PIPEDA (Canada) data protection requirements
- **NFR-025**: System MUST comply with COPPA: no collection of data from users under 13 (age-neutral design, no age verification required)
- **NFR-026**: System MUST comply with ADA and Section 508 accessibility requirements
- **NFR-027**: All data handling practices MUST be documented and auditable by external reviewers within 30 days of request

### Key Entities *(include if feature involves data)*

- **Photo**: Represents an aviation image used in gameplay. Attributes include image data, associated airport or aircraft identifier, upload timestamp, and verification status. Must never contain EXIF location data accessible to players.

- **Airport**: Represents an airport in the official database. Attributes include airport name, IATA code, ICAO code, country, region, and brief factual description. Sourced from open aviation databases.

- **Airline**: Represents an airline in the official database. Attributes include airline name, identifier code, and country of operation. Sourced from open aviation databases.

- **Aircraft**: Represents an aircraft model in the official database. Attributes include manufacturer, model name, and type category. Sourced from open aviation databases.

- **Player**: Represents a user account with minimal identifying information. Attributes include username and cumulative score. No personal information, location history, or behavioral data.

- **Guess**: Represents a single player's guess in a game round. Attributes include photo identifier, player identifier, guessed airport/airline/aircraft, correctness score, and timestamp. Used only for gameplay scoring, not tracking.

- **Game Round**: Represents a single instance of gameplay. Attributes include photo shown, player identifier, guess submitted, correct answer, and score awarded. Ephemeral—not retained for behavioral analysis.

- **Leaderboard Entry**: Represents a player's position and score on a leaderboard. Attributes include username, total score, and rank. No personal or social connection data.

- **Proof of Work Challenge**: Represents a computational challenge issued during account creation. Attributes include challenge nonce, difficulty target, timestamp issued, and expiration (10 seconds). Used to prevent bot registration without storing user data.

- **Moderation Queue Entry**: Represents a photo pending manual review. Attributes include photo reference, failed automated checks list, uploader username (no other identity), submission timestamp, review deadline (48 hours), and resolution status. Used for content moderation without behavioral tracking.

- **Photo Flag**: Represents a community report on an approved photo. Attributes include photo reference, reporter username, reason category, timestamp. Aggregated to trigger re-review at threshold (≥3 unique flags).

- **Photo Difficulty**: Represents dynamically calculated difficulty metadata for each photo. Attributes include photo identifier, total attempts, successful attempts, success rate, calculated difficulty multiplier (1x-3x), and last updated timestamp. Only activated when global thresholds met (≥500 photos AND ≥100 players).

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Gameplay Experience**

- **SC-001**: Players can complete a full game round (view photo, make guess, see result) in under 60 seconds
- **SC-002**: 90% of players successfully submit a valid airport guess on their first attempt
- **SC-003**: Players can search and find any airport in the database within 10 seconds using name or code
- **SC-004**: Application startup time is under 3 seconds on target devices
- **SC-005**: Application uses less than 100MB of device memory during active gameplay
- **SC-006**: Players can play at least 10 game rounds while offline using cached photos

**Content Quality**

- **SC-007**: 95% of uploaded photos pass validation and enter the game pool within 5 seconds
- **SC-008**: Zero EXIF location data is accessible to players in any uploaded photo
- **SC-009**: Airport database contains at least 500 major international airports at launch
- **SC-010**: Airline and aircraft databases contain sufficient entries to support aircraft identification for major commercial flights

**Privacy Compliance**

- **SC-011**: Zero continuous or background location tracking events occur during normal usage
- **SC-012**: Zero behavioral profiling or analytics data is collected or stored
- **SC-013**: Photo location data in aircraft mode is accessed exactly once per identification attempt
- **SC-014**: Player profiles contain no personal information beyond username and score
- **SC-015**: All data handling practices are documented and auditable by external reviewers

**User Satisfaction**

- **SC-016**: 80% of players report feeling confident that their privacy is protected
- **SC-017**: 75% of players successfully complete at least 5 game rounds in their first session
- **SC-018**: Less than 5% of player feedback reports privacy concerns or unexpected data collection

**Security**

- **SC-019**: Zero successful bot registrations occur (proof-of-work prevents automated account creation)
- **SC-020**: Zero SQL injection or XSS vulnerabilities in security audits
- **SC-021**: Account creation rate limiting blocks >99% of brute-force registration attempts
- **SC-022**: All uploaded photos pass EXIF verification before storage (zero unverified photos stored)
- **SC-023**: Manual review queue maintains <48 hour processing time for 95% of submissions

**Content Moderation**

- **SC-024**: >99% of inappropriate content blocked by automated checks before reaching game pool
- **SC-025**: Zero photos containing offensive text reach the public game pool
- **SC-026**: Duplicate photo detection catches >95% of resubmissions
- **SC-027**: AI-generated image detection blocks >90% of synthetic content

**Environmental Sustainability**

- **SC-028**: Average backend CPU utilization remains below 30% during normal operation
- **SC-029**: Frontend initial bundle size under 100KB gzipped
- **SC-030**: API cache hit rate exceeds 80% for read-heavy endpoints (airports, leaderboard)
- **SC-031**: No database query exceeds 100ms under normal load

## Assumptions *(mandatory)*

1. **Open aviation databases are available**: We assume publicly available databases for airports (IATA/ICAO codes), airlines, aircraft models, and basic flight metadata exist and can be accessed legally and ethically.

2. **User-generated content moderation**: We assume that a basic content moderation system will be needed to prevent inappropriate photos from entering the game pool, though the technical approach is not specified here.

3. **Photo quality standards**: We assume that most user-uploaded photos will be of sufficient quality to be used in gameplay, though some validation may be needed.

4. **Network connectivity**: We assume that players have intermittent network connectivity for downloading new photos and uploading content, but offline gameplay with cached photos should be supported.

5. **Flight data correlation**: For aircraft identification mode, we assume that matching a photo's location to active flights is technically feasible using open flight tracking data, though the implementation approach is not defined here.

6. **Scoring algorithm**: We assume that a scoring algorithm based on geographical proximity (exact, region, country) is sufficient for determining guess accuracy, though the specific calculation method is not defined here.

7. **Platform capabilities**: We assume that target platforms (macOS desktop and iOS) provide standard APIs for image selection, display, and basic data storage without requiring invasive permissions.

8. **User consent mechanisms**: We assume that platform-standard mechanisms for requesting photo location access (iOS permissions, for example) are sufficient for the limited use case in aircraft identification mode.

9. **Leaderboard scale**: We assume that global leaderboards can be maintained without requiring complex distributed systems at launch, though scalability considerations may be needed later.

10. **No real-time multiplayer**: We assume that gameplay is asynchronous—players compete against scores but do not need real-time interaction with other players.

## Out of Scope *(mandatory)*

The following are explicitly excluded from this specification:

1. **Social networking features**: No friend lists, follower graphs, direct messaging, or social connections between players.

2. **Monetization**: No advertising, no in-app purchases, no premium tiers, no data harvesting for commercial purposes.

3. **Behavioral analytics**: No user profiling, no engagement optimization, no A/B testing based on user behavior.

4. **Continuous location tracking**: No background location monitoring, no movement history, no location-based notifications.

5. **Flight booking or commercial services**: This is not a travel app. No integration with booking platforms, airlines, or commercial services.

6. **Real-time multiplayer gameplay**: No simultaneous gameplay with other players, no live competitions, no chat features.

7. **User-generated ratings or reviews**: No voting, liking, or rating systems for photos or other players.

8. **Personalized recommendations**: No algorithmic content curation based on user behavior or preferences.

9. **Push notifications for engagement**: No notifications designed to increase app usage or re-engagement.

10. **Third-party integrations**: No connections to social media platforms, external analytics services, or advertising networks.

11. **Photo editing tools**: No in-app photo filters, cropping, or editing capabilities beyond basic upload.

12. **Advanced aircraft tracking**: This is not a comprehensive flight tracker. Only minimal contextual flight information is shown after guessing in aircraft identification mode.

13. **Private or military airports**: Only publicly documented airports from open databases are included. No classified or restricted locations.

14. **User-to-user interactions**: No mechanisms for players to contact, challenge, or interact with each other directly.

15. **Gamification beyond scoring**: No achievements, badges, streaks, or other engagement mechanics beyond simple scoring and leaderboards.

## Data Handling Invariants *(mandatory)*

The following rules MUST always hold true, regardless of implementation choices:

1. **Location data isolation**: Photo location metadata MUST NEVER be accessible to players viewing or guessing photos.

2. **One-time location use**: In aircraft identification mode, photo location data MUST be used exactly once for flight correlation and MUST NOT persist in any user history or profile.

3. **No behavioral tracking**: User actions (guesses, views, timing, patterns) MUST NOT be aggregated or analyzed for profiling purposes.

4. **Minimal player identity**: Player profiles MUST contain only username and score. No email, phone number, device identifier, or location history may be associated with player identity.

5. **EXIF stripping is non-negotiable**: All uploaded photos MUST have EXIF location data removed before any storage or processing. This operation MUST be verified and cannot be skipped.

6. **Public pool visibility**: All uploaded photos that pass validation MUST be visible to all players. No private collections or user-specific photo sets.

7. **Open data sources only**: Aviation databases MUST be sourced from publicly available, open datasets. No proprietary, scraped, or closed-source data may be used.

8. **No cross-session location correlation**: Location data MUST NOT be compared across multiple sessions or photos to infer user movement patterns.

9. **Score immutability**: Once a guess is scored, the result MUST NOT be changed or manipulated to affect leaderboards retroactively.

10. **Explicit consent for location**: When photo location is required (aircraft identification mode only), user consent MUST be obtained before accessing location metadata. Gameplay MUST be possible without granting this permission.

## Privacy Design Constraints *(mandatory)*

The following constraints shape all design and implementation decisions:

1. **Privacy by default**: The application MUST operate with maximal privacy protections enabled by default. Users MUST NOT need to configure settings to achieve privacy.

2. **Data minimization**: Only data strictly necessary for gameplay MUST be collected. If functionality can work without data, it MUST work without data.

3. **Purpose limitation**: Any data collected MUST be used only for its stated gameplay purpose and MUST NOT be repurposed for analytics, profiling, or monetization.

4. **Transparency**: All data handling practices MUST be documented in clear, human-readable language accessible to users.

5. **User control**: Users MUST be able to play the game without providing personal information beyond a username.

6. **No surveillance infrastructure**: The application MUST NOT create, enable, or support any form of continuous monitoring, tracking, or surveillance.

7. **Local-first when possible**: Gameplay data MUST be processed locally on the device when feasible, minimizing server-side data collection.

8. **No persistent identifiers**: Device identifiers, IP addresses, or other persistent tracking mechanisms MUST NOT be stored or used for user identification beyond what is required for basic account management.

9. **Auditability**: All data flows and storage decisions MUST be auditable by external privacy reviewers or contributors.

10. **No dark patterns**: UI design MUST NOT manipulate users into granting unnecessary permissions or sharing more data than required.
