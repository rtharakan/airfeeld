# Feature Specification: Release Preparation & Next Iteration Planning

**Feature Branch**: `002-release-preparation`  
**Created**: 2026-02-01  
**Status**: Active  
**Input**: User request: "Prepare this game for release. I want to play the game. Plan for this project's Next Steps (Future Iterations)."

## Purpose

This specification outlines the work required to prepare Airfeeld for its initial public release, ensuring the game is playable, stable, tested, and aligned with the project's constitutional principles. This includes fixing critical issues, completing essential features, and planning future iterations with clear prioritization.

## Clarifications

### Session 2026-02-01

- Q: What constitutes "ready for release" for this privacy-first game? → A: Core gameplay loop functional (airport guessing), basic photo pool seeded, API stable, frontend complete, privacy guarantees testable, and user can play without technical issues
- Q: Should all priority items be implemented before release? → A: High priority items are release blockers. Medium priority items are post-MVP enhancements. Low priority items are future roadmap only.
- Q: What does "start the game" mean? → A: Start both backend server and frontend dev server, ensure they can communicate, and allow user to play at least one round of the airport guessing game successfully

## User Scenarios & Testing *(mandatory)*

### User Story 1 - First Playable Release (Priority: P0 - Blocker)

A user can visit the game, register anonymously, view an airport photo, make a guess, receive feedback, and see their score—all without any technical errors or privacy violations.

**Why this priority**: This is the minimum viable product. If this doesn't work, there is no game to release.

**Independent Test**: Can be fully tested by starting both backend and frontend servers, navigating to the game in a browser, completing one full round of the airport guessing game, and verifying all functionality works without console errors.

**Acceptance Scenarios**:

1. **Given** both servers are running, **When** a user visits the frontend URL, **Then** they see the landing page without errors
2. **Given** a user is on the landing page, **When** they register with a username, **Then** they receive a session token and can access the game
3. **Given** a registered user starts a game, **When** they view a photo, **Then** the photo loads without EXIF data and displays properly
4. **Given** a user is viewing a photo, **When** they search for and select an airport, **Then** their guess is submitted successfully
5. **Given** a user submitted a guess, **When** results are revealed, **Then** they see correct feedback and their score updates
6. **Given** a user completed a round, **When** they check the leaderboard, **Then** they see rankings including their own score

---

### User Story 2 - Comprehensive Test Coverage (Priority: P0 - Blocker)

The codebase has sufficient test coverage to catch regressions and validate privacy guarantees, including unit tests for core services, integration tests for API workflows, and contract tests for API compliance.

**Why this priority**: Without tests, we cannot confidently claim the app works or respects privacy. Tests are a constitutional requirement for specification-driven development.

**Independent Test**: Can be fully tested by running the test suite and verifying all critical paths are covered, privacy functions are validated, and API contracts match specifications.

**Acceptance Scenarios**:

1. **Given** the backend test suite, **When** tests are executed, **Then** all unit tests for PoW, rate limiting, and profanity filtering pass
2. **Given** API integration tests exist, **When** tests are executed, **Then** player registration, game rounds, and guess submission workflows are validated
3. **Given** contract tests exist, **When** tests are executed, **Then** API responses match the OpenAPI specification
4. **Given** privacy-critical code exists, **When** tests are executed, **Then** EXIF stripping, data minimization, and no-tracking guarantees are validated

---

### User Story 3 - Content Moderation Pipeline (Priority: P1 - High)

Uploaded photos are filtered for profanity, inappropriate content, and malicious data before being added to the game pool, ensuring a safe and respectful experience.

**Why this priority**: User-generated content without moderation risks violating the constitution's "Public Interest First" and safety principles. This is a release blocker for photo uploads but not for gameplay.

**Independent Test**: Can be fully tested by simulating photo uploads with various content (profane usernames, inappropriate images, malicious files) and verifying they are rejected or flagged appropriately.

**Acceptance Scenarios**:

1. **Given** a user uploads a photo with profanity in metadata, **When** the photo is processed, **Then** it is rejected before storage
2. **Given** a user uploads a photo with inappropriate content, **When** the photo is analyzed, **Then** it is flagged for manual review
3. **Given** a user uploads a malicious file disguised as an image, **When** the file is validated, **Then** it is rejected with an error message
4. **Given** a clean photo is uploaded, **When** moderation passes, **Then** the photo is added to the game pool successfully

---

### User Story 4 - Frontend Game UI Completion (Priority: P1 - High)

The frontend includes all necessary components for the core gameplay loop: photo display, airport search/selection, guess submission, result feedback, scoring display, and leaderboard view.

**Why this priority**: The backend API is functional, but without a complete frontend, users cannot interact with the game. This is a release blocker.

**Independent Test**: Can be fully tested by manually interacting with each UI component and verifying visual correctness, accessibility, and functional behavior.

**Acceptance Scenarios**:

1. **Given** a user is playing the game, **When** they view a photo, **Then** the image displays responsively and accessibly
2. **Given** a user needs to make a guess, **When** they use the airport search, **Then** autocomplete suggests matching airports
3. **Given** a user selected an airport, **When** they submit their guess, **Then** loading state is shown and results appear
4. **Given** results are displayed, **When** the user views feedback, **Then** correct/incorrect status, score, and airport details are clear
5. **Given** a user checks the leaderboard, **When** data loads, **Then** rankings are displayed in a readable, accessible table

---

### User Story 5 - Photo Pool Seeding (Priority: P1 - High)

The game launches with a seed set of 100+ airport photos from Creative Commons and public domain sources, properly attributed and tagged with correct airport metadata.

**Why this priority**: Without photos, there is no game. A seed pool ensures the game is immediately playable without waiting for user contributions.

**Independent Test**: Can be fully tested by verifying the photo database contains at least 100 photos, each with valid airport associations, no EXIF data, and proper attribution metadata.

**Acceptance Scenarios**:

1. **Given** the seed script runs, **When** photos are imported, **Then** at least 100 photos are added to the database
2. **Given** seed photos are imported, **When** metadata is checked, **Then** each photo has a valid airport ICAO/IATA code
3. **Given** seed photos are imported, **When** EXIF data is checked, **Then** no location coordinates are present
4. **Given** seed photos are Creative Commons licensed, **When** displayed in-game, **Then** photographer name and source link are shown
5. **Given** seed photos are public domain, **When** displayed in-game, **Then** license statement and source are shown

---

### User Story 6 - Future Iteration Planning (Priority: P2 - Medium)

The project has a clear roadmap for medium and low priority features, documented in a structured format that aligns with specification-driven development principles.

**Why this priority**: Planning future work ensures the project maintains direction and avoids scope creep. This is not a release blocker but is valuable for project sustainability.

**Independent Test**: Can be fully tested by reviewing the generated roadmap document and verifying it contains prioritized features with clear acceptance criteria and constitutional alignment.

**Acceptance Scenarios**:

1. **Given** the roadmap document exists, **When** reviewed, **Then** features are organized by priority (P2 medium, P3 low)
2. **Given** each feature in the roadmap, **When** reviewed, **Then** it includes clear user scenarios and acceptance criteria
3. **Given** the roadmap is reviewed, **When** features are evaluated, **Then** each aligns with constitutional principles
4. **Given** the roadmap is reviewed, **When** dependencies are checked, **Then** implementation order is logical and testable

---

### Edge Cases

- What happens when the backend server fails during gameplay?
- What happens when the frontend cannot connect to the backend API?
- What happens when a user tries to guess an airport that doesn't exist in the database?
- What happens when the photo pool is empty or all photos have been seen by a player?
- What happens when test execution fails in CI/CD pipelines?
- What happens when seed data import encounters corrupt or invalid photos?
- How does the system handle browser compatibility issues (older browsers, mobile devices)?
- What happens when a user tries to upload a photo before completing PoW challenge?

## Requirements

### Functional Requirements *(must be testable)*

**Must Have (P0-P1 - Release Blockers)**:

1. Backend server must start without errors and expose health check endpoint
2. Frontend dev server must start and serve accessible UI
3. User registration must work with username + PoW validation
4. Photo display must render without EXIF location data
5. Airport search/selection UI must allow guess submission
6. Guess submission must return immediate feedback (correct/incorrect, score, details)
7. Leaderboard must display player rankings
8. Unit tests must validate PoW, rate limiting, profanity filtering
9. Integration tests must validate player registration, game rounds, guess workflows
10. Contract tests must validate API responses match OpenAPI spec
11. Content moderation must filter profane usernames and inappropriate content
12. Frontend must include complete GameRound, RegisterForm, and Leaderboard components
13. Photo pool must be seeded with 100+ properly attributed images
14. EXIF stripping must be validated by tests

**Should Have (P2 - Post-MVP Enhancements)**:

15. Offline support with Service Worker and IndexedDB
16. Data seeding scripts for airports, airlines, aircraft
17. Performance optimization (lazy loading, caching, compression)
18. Accessibility audit with automated tools (Lighthouse, axe-core)
19. E2E tests with Playwright
20. Detailed analytics dashboard (privacy-preserving)

**Could Have (P3 - Future Roadmap)**:

21. Difficulty multiplier system (requires 500+ photos, 100+ players)
22. Aircraft identification game mode
23. Advanced analytics with differential privacy
24. Mobile app (iOS/Android native or PWA)
25. Internationalization (i18n) support

### Non-Functional Requirements

**Performance**:
- Page load time < 3 seconds on 3G networks
- Image optimization: WebP format, max 800px width, < 200KB per photo
- API response time < 500ms for guess submission
- Leaderboard query < 1 second for top 100 players

**Accessibility**:
- WCAG AA compliance (4.5:1 contrast, keyboard navigation, screen reader support)
- No JavaScript-only critical functionality
- Semantic HTML with proper ARIA labels

**Security**:
- HTTPS only in production
- PoW challenge difficulty: 20 (4 leading zero bits)
- Rate limiting: 10 requests/minute per IP for registration, 100 requests/minute for gameplay
- EXIF stripping: all GPS, timestamp, and device metadata removed
- No cookies except session tokens (httpOnly, secure, SameSite=Strict)

**Privacy** (Constitutional Requirements):
- No third-party analytics or tracking scripts
- No user profiling or behavioral analysis
- Data minimization: only username and scores stored
- No IP address logging beyond rate limiting (ephemeral, no long-term storage)
- No fingerprinting techniques

**Sustainability** (Constitutional Requirements):
- Minimal bundle size: < 500KB gzipped for frontend
- Efficient database queries: indexes on frequently queried fields
- Image lazy loading and compression
- CDN usage for static assets (if using renewable energy provider)

**Compatibility**:
- Modern browsers: Chrome/Edge 90+, Firefox 88+, Safari 14+
- Mobile responsive: iOS Safari, Android Chrome
- Graceful degradation for older browsers

### System Requirements

**Backend**:
- Python 3.11+
- FastAPI framework
- SQLite database (SQLAlchemy ORM)
- Pillow for image processing
- Virtual environment (venv)

**Frontend**:
- Node.js 18+
- React 18+
- TypeScript
- Vite build tool
- Tailwind CSS

**Infrastructure**:
- Development: local servers (backend:8000, frontend:5173)
- Production: TBD (must support renewable energy hosting per constitution)

**Testing**:
- pytest for backend tests
- Playwright for E2E tests (future)
- Lighthouse for accessibility audits (future)

## Open Questions *(to be resolved in research phase)*

1. **Photo seeding sources**: Which specific Flickr/Wikimedia collections have suitable airport photos under CC BY 2.0 or CC0 licenses?
2. **Content moderation**: Should we use an existing image classification API (e.g., Google Cloud Vision, AWS Rekognition) or a local model? How does this align with privacy principles?
3. **Offline support**: What is the minimum service worker functionality needed for a playable offline experience?
4. **E2E testing**: What Playwright test scenarios are critical for release confidence?
5. **Performance baseline**: What are the current page load times and bundle sizes, and where are optimization opportunities?
6. **Accessibility audit**: What automated tools should be integrated into CI/CD for ongoing compliance?
7. **Mobile PWA**: Should the initial release target mobile browsers, or is that a future iteration?
8. **Hosting provider**: Which renewable energy hosting providers support Python/Node.js apps and meet constitutional sustainability requirements?

## Success Metrics

**Release Readiness**:
- ✅ Backend starts without errors
- ✅ Frontend starts without errors
- ✅ User can complete one full game round
- ✅ All high-priority tests pass
- ✅ Photo pool contains 100+ seed images
- ✅ EXIF stripping validated
- ✅ Content moderation functional

**Post-Release** (not part of this spec):
- User feedback collected
- Bug reports triaged
- Performance monitoring established
- Roadmap updated based on learnings

## Out of Scope

This specification explicitly excludes:

- Social features (friend lists, sharing, comments)
- User accounts with email/password (anonymous only)
- Paid features or monetization
- Third-party integrations (ads, analytics, social login)
- Advanced difficulty multiplier system (requires population threshold)
- Aircraft identification game mode (P3 priority)
- Mobile native apps (P3 priority)
- Internationalization (P3 priority)

## Dependencies

**Data Sources**:
- Airport database: OurAirports (CC0 license)
- Photo sources: Flickr API (CC BY 2.0), Wikimedia Commons (CC BY/CC0)
- Airline/aircraft data (future): OpenFlights, FlightAware

**External Services** (future consideration, must align with privacy principles):
- Image classification for moderation (local model preferred)
- Hosting provider with renewable energy commitment

**Technical**:
- All backend Python dependencies in requirements.txt
- All frontend Node dependencies in package.json
- SQLite database file (backend/data/airfeeld.db)

## Risks & Mitigations

**Risk**: Insufficient test coverage leads to undetected bugs  
**Mitigation**: Prioritize tests for privacy-critical code and core gameplay workflows. Use contract tests to validate API behavior.

**Risk**: Photo seeding is time-consuming and manual  
**Mitigation**: Create automated scripts to fetch, validate, and import photos from public sources. Start with smaller seed pool (50 photos) if necessary.

**Risk**: Content moderation requires external API, violating privacy principles  
**Mitigation**: Research local image classification models (e.g., NSFW detection with CLIP or ResNet). If external API needed, ensure no data retention and minimal metadata sharing.

**Risk**: Frontend performance suffers from large bundle size  
**Mitigation**: Code splitting, lazy loading, tree shaking. Measure with Lighthouse and set budget limits.

**Risk**: Game is not fun or engaging  
**Mitigation**: Playtest with early users. Gather feedback. Iterate based on user scenarios, not feature requests.

**Risk**: Hosting provider does not meet sustainability requirements  
**Mitigation**: Research renewable energy providers upfront. Document trade-offs if perfect option doesn't exist.

## Appendix

### Priority Definitions

- **P0 (Blocker)**: Must be completed for initial release. Game is unplayable without this.
- **P1 (High)**: Critical for release quality. Should be completed before public launch.
- **P2 (Medium)**: Enhances user experience but not required for MVP. Post-launch improvements.
- **P3 (Low)**: Future roadmap items. Nice-to-have features for later iterations.

### Related Documents

- [Constitution](../../.specify/memory/constitution.md) - Governance and principles
- [001-aviation-games/spec.md](../001-aviation-games/spec.md) - Original feature specification
- [plan.md](./plan.md) - Implementation plan (this document's companion)
- [tasks.md](./tasks.md) - Granular implementation tasks (to be generated)
