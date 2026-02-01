# Research: Release Preparation

**Feature**: 002-release-preparation  
**Date**: 2026-02-01  
**Phase**: 0 (Research & Resolution)

## Purpose

This document resolves open questions and unknowns identified in the feature specification ([spec.md](./spec.md)). Each research task investigates technical approaches, best practices, and decision criteria to enable informed design choices in Phase 1.

---

## Research Task 1: Photo Seeding Sources

**Question**: Which specific Flickr/Wikimedia collections have suitable airport photos under CC BY 2.0 or CC0 licenses?

### Investigation

**Flickr API Approach**:
- Flickr API allows searching by license type (CC BY 2.0, CC0) and tags (e.g., "airport", "runway", "terminal")
- API endpoint: `flickr.photos.search` with parameters:
  - `license=1,2,9,10` (CC BY, CC BY-SA, CC0, Public Domain)
  - `tags=airport,runway,terminal,aviation`
  - `text=airport name` (e.g., "JFK airport")
- Attribution requirements: Display photographer name + Flickr photo URL
- Rate limit: 3600 requests/hour (sufficient for batch seeding)

**Wikimedia Commons Approach**:
- Wikimedia Commons API allows searching by category and license
- API endpoint: `MediaWiki API` with `list=categorymembers`
- Relevant categories: `Category:Airports`, `Category:Airport photographs`, `Category:Runways`
- License filtering: Can query for CC BY, CC BY-SA, CC0, Public Domain
- Attribution requirements: Display author name + Wikimedia Commons page URL
- No rate limit for reasonable batch requests

**OurAirports Integration**:
- OurAirports provides airport database (ICAO/IATA codes, names, locations) under CC0
- Can match airport names from photo metadata to OurAirports codes
- This provides canonical airport identifiers for game logic

**Seed Data Strategy**:
1. Use Wikimedia Commons as primary source (no API key required, high quality)
2. Use Flickr as secondary source (requires API key, broader variety)
3. Manual curation: Review first 100 photos for quality and variety
4. Automated script: Fetch photos, validate licenses, strip EXIF, store metadata

### Decision

**Adopt Wikimedia Commons as primary source**:
- **Rationale**: No API key required, high-quality photos, clear licensing, strong community curation
- **Attribution format**: `Photo by [Author] via Wikimedia Commons ([License])` with link to original page
- **Fallback**: Use Flickr API if Wikimedia results are insufficient (requires Flickr API key)

**Seed script workflow**:
1. Query Wikimedia Commons for airport photos (Category:Airport photographs)
2. Filter by license (CC BY, CC BY-SA, CC0, Public Domain)
3. Download images, resize/compress to < 200KB, convert to WebP
4. Strip all EXIF metadata using Pillow
5. Match airport names to OurAirports database (ICAO/IATA codes)
6. Store in database with attribution metadata
7. Target: 100-150 photos covering diverse airports (major hubs, regional, international)

**Alternatives considered**:
- Unsplash API: Rejected (most photos are generic, license unclear for attribution requirements)
- Getty Images: Rejected (not open license, requires payment)
- Government sources (FAA, Eurocontrol): Viable for public domain photos but lower variety

**Implementation note**: Create `backend/scripts/seed_photos.py` with CLI arguments for source selection, batch size, and manual review mode.

---

## Research Task 2: Content Moderation Approach

**Question**: Should we use an existing image classification API (e.g., Google Cloud Vision, AWS Rekognition) or a local model? How does this align with privacy principles?

### Investigation

**External API Options**:
- **Google Cloud Vision**: Provides NSFW detection, explicit content classification, label detection
  - Privacy concern: Sends images to Google servers, potential data retention
  - Cost: $1.50 per 1000 images (moderate cost for MVP)
  - Accuracy: High (trained on massive datasets)
- **AWS Rekognition**: Similar features, similar privacy concerns, similar pricing
  - Privacy concern: Sends images to AWS servers, potential metadata leakage
  - Cost: $1.00 per 1000 images
  - Accuracy: High

**Local Model Options**:
- **CLIP (OpenAI)**: Zero-shot image classification, can be run locally
  - Privacy: No external API calls, images processed locally
  - Cost: Free (model weights are open)
  - Accuracy: Moderate (requires prompt engineering for NSFW detection)
  - Performance: Requires GPU for reasonable speed (CPU inference is slow)
- **NSFW Detection Model (Yahoo/Tumblr open-sourced model)**: Specialized for NSFW content
  - Privacy: Fully local, no external calls
  - Cost: Free (open source)
  - Accuracy: High for NSFW content specifically
  - Performance: Lightweight, can run on CPU
  - Model: https://github.com/GantMan/nsfw_model (TensorFlow.js or Python versions available)
- **Profanity filtering (existing implementation)**: Already implemented for usernames
  - Extend to photo metadata (filename, EXIF comments if present before stripping)

**Constitutional Alignment**:
- Privacy by Design: External APIs violate principle (data sent to third parties)
- Openness in Practice: Local models align with transparency (model behavior is auditable)
- Environmental Sustainability: Local models avoid unnecessary network transfer, but GPU usage may increase energy consumption
- Radical Simplicity: External APIs are simpler to integrate, but local models avoid external dependencies

### Decision

**Adopt local NSFW detection model (Yahoo/Tumblr open-sourced model)**:
- **Rationale**: Aligns with constitutional privacy principles (no data sharing), open source (auditable), accurate for NSFW detection, lightweight enough for CPU inference
- **Implementation**: Use Python wrapper for NSFW model, run during photo upload processing
- **Fallback**: Manual review queue for flagged photos (admin interface to approve/reject)
- **Profanity filtering**: Extend existing implementation to check photo metadata before EXIF stripping

**Moderation pipeline**:
1. User uploads photo → API receives file
2. Validate file type and size (< 5MB, JPEG/PNG only)
3. Check filename for profanity (using existing profanity_filter.py)
4. Run NSFW detection model (score threshold: 0.8 = auto-reject, 0.6-0.8 = flag for review, < 0.6 = auto-approve)
5. Strip EXIF metadata
6. Store photo + metadata in database (with moderation status)
7. Only approved photos appear in game pool

**Alternatives considered**:
- External APIs: Rejected due to privacy violations (data sharing with third parties)
- Manual-only moderation: Rejected due to scaling concerns (100+ photos requires significant human time)
- No moderation: Rejected due to constitutional "Public Interest First" principle (must protect users from harmful content)

**Implementation note**: Add NSFW model as Python dependency (e.g., `nsfw-detector` package), create `backend/src/workers/moderation.py` service, add moderation status to `Photo` model.

---

## Research Task 3: Offline Support Requirements

**Question**: What is the minimum service worker functionality needed for a playable offline experience?

### Investigation

**Service Worker Capabilities**:
- Cache static assets (HTML, CSS, JS bundles)
- Cache API responses (game rounds, leaderboard data)
- Background sync (submit guesses when back online)
- Offline fallback pages

**MVP Offline Experience** (P2 priority, not release blocker):
- User can view previously loaded pages (Home, Play, Leaderboard)
- User can view cached photos and make guesses (stored locally until online)
- User cannot fetch new photos offline (acceptable limitation)
- User sees "offline mode" indicator

**IndexedDB Storage**:
- Store completed game rounds (photos, guesses, scores)
- Store leaderboard snapshot (refreshed when online)
- Store player session data (username, scores)

**Implementation Complexity**:
- Service worker: ~200 lines of code (cache strategies, offline fallback)
- IndexedDB wrapper: ~100 lines (store/retrieve game data)
- React offline detection: ~50 lines (useEffect hook for online/offline events)
- Testing: Service worker behavior is difficult to test (requires browser DevTools or E2E tests)

**Constitutional Alignment**:
- Accessibility as Constraint: Offline support improves accessibility for users with unreliable connections
- Environmental Sustainability: Reduces network requests (cached assets, local-first data)
- Radical Simplicity: Adds complexity (service worker lifecycle, cache invalidation), but provides significant user value

### Decision

**Defer offline support to P2 (post-MVP)**:
- **Rationale**: Offline support adds significant complexity, testing overhead, and is not required for initial release. MVP can function as online-only app. Implement in future iteration once core gameplay is stable.
- **Minimum viable offline support (when implemented)**:
  1. Cache static assets (HTML, CSS, JS, fonts)
  2. Cache API responses for leaderboard (stale-while-revalidate strategy)
  3. Show offline indicator in UI
  4. Defer background sync (not required for MVP offline experience)

**Alternatives considered**:
- Full offline support (P1): Rejected due to complexity and testing burden for MVP
- No offline support ever: Rejected due to accessibility and sustainability benefits
- Progressive Web App (PWA) with full offline capabilities: Deferred to P3 (mobile app iteration)

**Implementation note**: When P2 is prioritized, create `frontend/src/workers/service-worker.ts`, add Workbox library for cache strategies, implement offline detection hook in `frontend/src/utils/offline.ts`.

---

## Research Task 4: E2E Testing with Playwright

**Question**: What Playwright test scenarios are critical for release confidence?

### Investigation

**Playwright Capabilities**:
- Cross-browser testing (Chromium, Firefox, WebKit)
- Accessibility testing (axe-core integration)
- Screenshot comparison (visual regression testing)
- Network mocking (test offline scenarios, API failures)
- Parallel test execution

**Critical E2E Scenarios for MVP**:
1. **User registration flow**: Visit homepage → Enter username → Complete PoW → Register → Receive session token
2. **Gameplay flow**: Start game → View photo → Search for airport → Submit guess → See results → Score updates
3. **Leaderboard flow**: Navigate to leaderboard → See rankings → Find own score
4. **Error handling**: Test network failures, invalid inputs, expired sessions

**Test Coverage Priority** (P2, not release blocker):
- P0 (must have before P2 launch): Registration + gameplay + leaderboard happy paths
- P1 (nice to have): Error handling, accessibility checks, cross-browser validation
- P2 (future): Visual regression, offline scenarios, performance budgets

**Implementation Complexity**:
- Test setup: ~100 lines (Playwright config, fixtures, test utilities)
- Per scenario: ~50-100 lines (page object pattern, assertions)
- CI/CD integration: ~50 lines (GitHub Actions workflow for Playwright)
- Total: ~500 lines for comprehensive E2E suite

**Constitutional Alignment**:
- Specification-Driven Development: E2E tests validate user scenarios from specification
- Accessibility as Constraint: Playwright can run axe-core audits as part of E2E tests
- Radical Simplicity: E2E tests add maintenance overhead but provide high confidence for critical paths

### Decision

**Defer comprehensive E2E tests to P2, implement basic smoke tests for P1**:
- **Rationale**: E2E tests are valuable but not required for MVP release. Manual testing can cover critical paths for initial launch. Add Playwright tests in post-MVP iteration to prevent regressions.
- **Minimum viable E2E testing (P1)**:
  1. Playwright setup + configuration
  2. One smoke test: Full gameplay flow (registration → game → leaderboard)
  3. CI/CD integration: Run smoke test on pull requests
- **Comprehensive E2E suite (P2)**:
  4. All user scenarios from specification
  5. Accessibility audits (axe-core)
  6. Error handling and edge cases
  7. Cross-browser testing (Chromium + Firefox + WebKit)

**Alternatives considered**:
- No E2E testing: Rejected (manual testing alone is insufficient for regression prevention)
- Full E2E suite before MVP: Rejected (too time-consuming, delays release)
- Cypress instead of Playwright: Rejected (Playwright has better cross-browser support and accessibility testing)

**Implementation note**: Create `frontend/tests/e2e/` directory, add Playwright config, implement smoke test in `frontend/tests/e2e/gameplay.spec.ts`, add GitHub Actions workflow `.github/workflows/e2e.yml`.

---

## Research Task 5: Performance Optimization Opportunities

**Question**: What are the current page load times and bundle sizes, and where are optimization opportunities?

### Investigation

**Current Performance Metrics** (estimated, requires measurement):
- Frontend bundle size: Unknown (requires `npm run build` analysis)
- Page load time: Unknown (requires Lighthouse audit)
- API response time: < 100ms (observed in testing, fast for local development)
- Image sizes: Varies (uploaded photos not yet optimized)

**Measurement Tools**:
- **Lighthouse**: Audits performance, accessibility, SEO, best practices
- **Webpack Bundle Analyzer**: Visualizes bundle size and dependencies
- **Chrome DevTools Network tab**: Measures actual load times and resource sizes

**Optimization Strategies**:
1. **Code splitting**: Split React bundles by route (lazy load pages)
2. **Image optimization**: Convert to WebP, compress, lazy load below-the-fold images
3. **Tree shaking**: Remove unused code (Vite does this automatically)
4. **Minification**: Compress CSS/JS (Vite does this automatically in production builds)
5. **CDN caching**: Cache static assets (headers, fonts, images)
6. **Database indexing**: Add indexes on frequently queried fields (player.username, photo.airport_id)

**Performance Budget** (constitutional requirement):
- Frontend bundle < 500KB gzipped
- Page load < 3 seconds on 3G (1.6 Mbps, 300ms RTT)
- API response < 500ms for guess submission
- Image size < 200KB per photo

### Decision

**Measure first, optimize second** (P2 priority):
- **Rationale**: Premature optimization violates "Radical Simplicity" principle. Measure actual performance before optimizing. Focus on low-hanging fruit (image optimization) and defer advanced optimizations (code splitting) until metrics justify them.
- **Immediate actions (P1)**:
  1. Measure current bundle size: `npm run build` + analyze output
  2. Run Lighthouse audit: Establish baseline metrics
  3. Optimize images: Convert to WebP, compress during upload/seeding
  4. Add database indexes: player.username, photo.airport_id, game_round.player_id
- **Deferred optimizations (P2)**:
  5. Code splitting by route (if bundle > 500KB)
  6. Lazy loading images (if page load > 3s)
  7. Service worker caching (if offline support is implemented)
  8. CDN setup (if deploying to production with global users)

**Alternatives considered**:
- Optimize everything upfront: Rejected (premature optimization, violates simplicity)
- No performance optimization: Rejected (constitutional sustainability requirement)
- Use Next.js for automatic optimizations: Rejected (adds framework complexity, Vite is sufficient)

**Implementation note**: Create `docs/performance-baseline.md` with initial measurements, set performance budgets in `frontend/vite.config.ts` (budget plugin), add image optimization to photo upload/seeding pipelines.

---

## Research Task 6: Accessibility Audit Tools

**Question**: What automated tools should be integrated into CI/CD for ongoing compliance?

### Investigation

**Automated Accessibility Tools**:
1. **Lighthouse (Chrome DevTools)**: Audits accessibility, provides scores and recommendations
   - Pros: Free, comprehensive, well-documented
   - Cons: Requires browser environment, slower than CLI-only tools
2. **axe-core (Deque)**: Industry-standard accessibility testing library
   - Pros: Fast, integrates with Playwright/Jest, catches most WCAG violations
   - Cons: Doesn't catch all issues (e.g., color contrast edge cases)
3. **Pa11y**: CLI tool for accessibility testing
   - Pros: Simple, fast, CI/CD-friendly
   - Cons: Less comprehensive than axe-core
4. **WAVE (WebAIM)**: Browser extension for manual testing
   - Pros: Visual overlay shows issues directly on page
   - Cons: Manual only, not automatable

**WCAG AA Requirements**:
- Color contrast: 4.5:1 for normal text, 3:1 for large text
- Keyboard navigation: All interactive elements focusable and operable via keyboard
- Screen reader support: Semantic HTML, ARIA labels where needed
- Form labels: All inputs have associated labels
- Alt text: All images have descriptive alt text (without revealing airport identity for gameplay)

**CI/CD Integration Approach**:
- Run axe-core as part of E2E tests (Playwright integration)
- Run Lighthouse CI in GitHub Actions (automated audits on pull requests)
- Block PRs if accessibility score drops below threshold (e.g., < 90/100)

**Manual Testing** (required, automation is insufficient):
- Screen reader testing: VoiceOver (macOS), NVDA (Windows), JAWS (Windows)
- Keyboard-only navigation: Tab through all interactive elements
- Color blindness simulation: Chrome DevTools or Color Oracle

### Decision

**Integrate axe-core + Lighthouse CI for automated audits (P1)**:
- **Rationale**: Axe-core is fast and catches most issues, Lighthouse provides comprehensive reports. Both are free and CI/CD-friendly. Manual testing is still required but automation catches regressions.
- **Implementation**:
  1. Add axe-core to Playwright E2E tests (run accessibility checks on each page)
  2. Add Lighthouse CI to GitHub Actions (audit on every pull request)
  3. Set accessibility score threshold: 90/100 minimum (Lighthouse)
  4. Document manual testing checklist in `docs/accessibility-checklist.md`
- **Defer to P2**:
  5. Comprehensive manual testing (screen readers, keyboard-only navigation)
  6. Color blindness simulation and contrast validation
  7. Accessibility-focused user testing (recruit users with disabilities)

**Alternatives considered**:
- Manual testing only: Rejected (not scalable, misses regressions)
- Automated testing only: Rejected (insufficient, many issues require human judgment)
- Pa11y instead of axe-core: Rejected (axe-core is more comprehensive and better integrated with Playwright)

**Implementation note**: Add axe-core integration to `frontend/tests/e2e/accessibility.spec.ts`, add Lighthouse CI config `.lighthouserc.json`, add GitHub Actions workflow `.github/workflows/lighthouse.yml`.

---

## Research Task 7: Renewable Energy Hosting Providers

**Question**: Which renewable energy hosting providers support Python/Node.js apps and meet constitutional sustainability requirements?

### Investigation

**Renewable Energy Hosting Options**:
1. **Vercel**: 100% renewable energy (wind power), supports Node.js (frontend), serverless functions (backend alternative)
   - Pros: Easy deployment, automatic HTTPS, global CDN, free tier generous
   - Cons: Serverless functions have cold start latency, SQLite not supported (requires external DB)
2. **Netlify**: 100% carbon offset, supports Node.js, serverless functions
   - Pros: Similar to Vercel, good free tier
   - Cons: Same serverless limitations (no persistent SQLite)
3. **Fly.io**: Runs on renewable energy data centers (Google Cloud), supports full-stack apps (Python + Node.js)
   - Pros: Supports SQLite (persistent volumes), no serverless constraints, free tier includes small VMs
   - Cons: More complex deployment than Vercel/Netlify
4. **Railway**: Renewable energy commitment (AWS with carbon offset), supports Python + Node.js, PostgreSQL/SQLite
   - Pros: Simple deployment, supports full-stack apps, free tier
   - Cons: Less transparent about renewable energy specifics
5. **Digital Ocean**: Carbon neutral commitment (100% renewable energy by 2025), supports Python + Node.js
   - Pros: Full VM control, affordable, supports SQLite
   - Cons: Requires more DevOps setup (not PaaS)

**Constitutional Requirements**:
- Environmental Sustainability: "Hosting infrastructure SHOULD prefer renewable energy providers where economically feasible"
- Radical Simplicity: Prefer simple deployment (PaaS) over complex DevOps (IaaS)
- Privacy by Design: No hosting provider should log or analyze user data (HTTPS only, no analytics)

### Decision

**Adopt Fly.io for MVP deployment**:
- **Rationale**: Supports Python + Node.js, allows SQLite (persistent volumes), runs on renewable energy infrastructure, simple deployment (flyctl CLI), free tier sufficient for MVP
- **Deployment approach**:
  1. Backend: Deploy as Fly.io app (Python/FastAPI)
  2. Frontend: Build static site, deploy on Fly.io (serve via Caddy or backend static route)
  3. Database: SQLite on persistent volume (Fly.io supports this)
  4. Photos: Store on persistent volume (alternative: S3-compatible storage with Backblaze B2)
- **Fallback**: If Fly.io proves insufficient, migrate to Railway or Digital Ocean

**Alternatives considered**:
- Vercel/Netlify: Rejected (serverless constraints make SQLite difficult, requires external DB migration)
- Heroku: Rejected (expensive, less transparent about renewable energy)
- AWS/GCP/Azure: Rejected (too complex for MVP, prefer smaller providers with clearer sustainability commitments)
- Self-hosting: Rejected (DevOps overhead, no free tier, renewable energy depends on local grid)

**Implementation note**: Create `fly.toml` configuration, document deployment process in `docs/deployment.md`, add deployment script `scripts/deploy.sh`, test deployment on Fly.io free tier before committing to production.

---

## Research Task 8: Mobile PWA Considerations

**Question**: Should the initial release target mobile browsers, or is that a future iteration?

### Investigation

**Mobile PWA Capabilities**:
- Add to home screen (app-like experience)
- Offline support (service worker + IndexedDB)
- Push notifications (not needed for this game)
- Native-like UI (full-screen, no browser chrome)

**Mobile Browser Support** (without PWA):
- Game is already responsive (Tailwind CSS)
- Touch interactions work (tap to select airport, swipe to scroll)
- No mobile-specific features required (camera API, geolocation, etc.)

**MVP Mobile Experience**:
- User can play game in mobile browser (Safari iOS, Chrome Android)
- UI is touch-friendly and responsive
- No "add to home screen" prompt (not required for MVP)
- No offline support (deferred to P2)

**PWA Benefits**:
- Better user engagement (app-like experience)
- Offline support (play without internet)
- Push notifications (future feature: notify when new photos available)

**PWA Costs**:
- Service worker complexity (caching strategies, offline sync)
- Testing overhead (test on iOS Safari, Android Chrome, different screen sizes)
- App manifest configuration (icons, splash screens, theme colors)

**Constitutional Alignment**:
- Accessibility as Constraint: Mobile support improves accessibility for users without desktop computers
- Radical Simplicity: PWA adds complexity, but mobile browser support is simple (responsive design)
- Environmental Sustainability: Offline support reduces network requests (but deferred to P2)

### Decision

**Target mobile browsers for MVP, defer PWA to P3**:
- **Rationale**: Game is already responsive and works in mobile browsers. PWA features (offline support, add to home screen) provide incremental value but add complexity. MVP can launch as mobile-friendly web app. Upgrade to PWA in future iteration based on user demand.
- **MVP mobile support (P1)**:
  1. Test on iOS Safari and Android Chrome (manual testing)
  2. Ensure touch interactions work (tap, scroll, swipe)
  3. Fix any mobile-specific layout issues (viewport, font sizes, button sizes)
- **PWA features (P3)**:
  4. Add web app manifest (`manifest.json`)
  5. Add service worker for offline support
  6. Add "add to home screen" prompt
  7. Design app icons and splash screens
  8. Test PWA on multiple devices (iOS, Android, different screen sizes)

**Alternatives considered**:
- PWA for MVP: Rejected (adds complexity, delays release)
- Desktop-only for MVP: Rejected (excludes mobile users, violates accessibility principle)
- Native mobile apps: Rejected (P3 priority, requires separate codebases for iOS/Android)

**Implementation note**: Test game on mobile browsers (iOS Safari, Android Chrome), document mobile compatibility in `docs/browser-compatibility.md`, add mobile testing to E2E test suite (Playwright device emulation).

---

## Summary of Decisions

| Research Task | Decision | Priority | Rationale |
|---------------|----------|----------|-----------|
| **Photo seeding sources** | Wikimedia Commons (primary) + Flickr (secondary) | P1 | Open license, no API key required, high quality |
| **Content moderation** | Local NSFW model (Yahoo/Tumblr open-sourced) | P1 | Privacy-aligned, no external APIs, accurate |
| **Offline support** | Defer to P2 (post-MVP) | P2 | Adds complexity, not required for initial release |
| **E2E testing** | Playwright smoke tests (P1), full suite (P2) | P1/P2 | Smoke tests sufficient for MVP, full suite for regressions |
| **Performance optimization** | Measure first, optimize second | P1/P2 | Avoid premature optimization, focus on image optimization |
| **Accessibility audits** | axe-core + Lighthouse CI | P1 | Automated audits catch regressions, manual testing required |
| **Hosting provider** | Fly.io (renewable energy, SQLite support) | P1 | Sustainability-aligned, simple deployment, free tier |
| **Mobile PWA** | Mobile browser support (P1), PWA features (P3) | P1/P3 | Game works in mobile browsers, PWA adds complexity |

**Next Steps**: Proceed to Phase 1 (Design) to generate data model, contracts, and quickstart guide based on these research decisions.
