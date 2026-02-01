# Airfeeld Release Status

**Version**: 0.1.0 (MVP)  
**Date**: 2026-02-01  
**Status**: ✅ Ready for Alpha Testing

---

## ✅ Completed Features

### Backend Infrastructure
- [X] FastAPI server with async SQLAlchemy ORM
- [X] SQLite database with Alembic migrations
- [X] Three migration files applied:
  - 001: Security tables (players, audit logs, PoW challenges, rate limits)
  - 002: Game tables (photos, game rounds, guesses)
  - 003: Moderation and attribution fields
- [X] RESTful API endpoints for:
  - Health check
  - Player registration with PoW
  - Game rounds management
  - Photo uploads and retrieval
  - Leaderboards
- [X] Content moderation system (local NSFW detection)
- [X] Privacy-preserving features:
  - EXIF stripping from uploaded photos (validated with unit tests)
  - IP hashing for rate limiting
  - Minimal player data collection
- [X] Security features:
  - Proof-of-work bot prevention
  - Rate limiting middleware
  - Profanity filtering
  - Input validation

### Testing
- [X] 58 unit tests passing (100% pass rate):
  - 7 tests for EXIF stripping (privacy validation)
  - 15 tests for content moderation service
  - 12 tests for PoW service
  - 14 tests for profanity filter
  - 10 tests for rate limit service
- [X] Test coverage for critical services
- [X] Privacy-critical functionality validated (EXIF stripping)

### Frontend
- [X] React 18 + TypeScript + Vite
- [X] Tailwind CSS styling
- [X] Production build successful (305KB JS, 20KB CSS gzipped)
- [X] Components implemented:
  - GameRound: Photo display, guessing, results
  - RegisterForm: Username input, PoW solving, registration
  - Leaderboard: Player rankings
  - Layout: Navigation and structure

### Infrastructure
- [X] Enhanced .gitignore for Python and Node.js
- [X] Dependencies updated (piexif added for test fixtures)
- [X] Development workflow documented
- [X] Player context for authentication
- [X] API client with type safety

### Data
- [X] 5 test photos seeded (KJFK, EGLL, KSFO, EDDF, RJAA)
- [X] Airport data prepared (40+ major airports ready for seeding)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup
```bash
cd backend

# Install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
PYTHONPATH=$PWD alembic upgrade head

# Start server
PYTHONPATH=$PWD python run.py
# Server runs on http://127.0.0.1:8000
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
# Server runs on http://localhost:5173
```

### Access the App
1. Backend API: http://127.0.0.1:8000
2. API Docs: http://127.0.0.1:8000/docs
3. Frontend: http://localhost:5173

---

## 🧪 Testing

### Run Unit Tests
```bash
cd backend
PYTHONPATH=$PWD pytest tests/unit/ -v
```

### Run All Tests
```bash
cd backend
PYTHONPATH=$PWD pytest tests/ -v --cov=src
```

---

## 📊 Current Status

### Servers Running
- ✅ Backend: http://127.0.0.1:8000 (FastAPI + Uvicorn)
- ✅ Frontend: http://localhost:5175 (Vite dev server)

### Database
- ✅ SQLite: `backend/data/airfeeld.db`
- ✅ All migrations applied (001, 002, 003)
- ✅ 5 test photos in database

### Known Limitations (MVP)
- ⚠️ Test photos only (5 airports) - real photo seeding needed for production
- ⚠️ No Airport model yet (airport data prepared but not stored in DB)
- ⚠️ No integration tests yet (covered by manual testing)
- ⚠️ No E2E tests yet (covered by manual testing)
- ⚠️ Local development only (deployment configuration needed)

---

## 🎯 Next Steps

### P1 (High Priority - Before Production)
1. **Integration Tests**: Create backend integration tests for key workflows
2. **E2E Tests**: Add Playwright tests for frontend workflows
3. **Airport Model**: Create Airport entity and migrate airport data
4. **Photo Seeding**: Implement Wikimedia Commons photo seeding script
5. **Deployment**: Configure for Fly.io or similar hosting

### P2 (Medium Priority - Post-MVP)
1. **Performance Testing**: Lighthouse CI and load testing
2. **Accessibility Audit**: axe-core validation
3. **Offline Support**: Service worker for offline play
4. **Mobile PWA**: Progressive Web App features
5. **Full Photo Attribution**: Display photographer credits

### P3 (Future Enhancements)
1. **Additional Game Modes**: Aircraft identification
2. **Social Features**: Friend leaderboards
3. **Photo Collections**: Curated themed challenges
4. **Internationalization**: Multi-language support

---

## 📝 API Documentation

### Key Endpoints

**Health Check**
```
GET /api/v1/health
```

**Player Registration**
```
POST /api/v1/players/register
Body: { username, pow_challenge_id, pow_solution, pow_nonce }
```

**Start Game Round**
```
POST /api/v1/games/rounds
Body: { player_id }
```

**Submit Guess**
```
POST /api/v1/games/rounds/{round_id}/guess
Body: { player_id, guess }
```

**Get Leaderboard**
```
GET /api/v1/players/leaderboard?limit=100
```

**Upload Photo**
```
POST /api/v1/photos
Body: multipart/form-data with file and metadata
```

Full API documentation: http://127.0.0.1:8000/docs

---

## 🛡️ Privacy & Security

### Privacy Features
- ✅ All uploaded photos have EXIF data stripped
- ✅ IP addresses are hashed for rate limiting (not stored)
- ✅ Minimal player data (username and scores only)
- ✅ No tracking scripts or analytics
- ✅ No third-party services for moderation (runs locally)

### Security Features
- ✅ Proof-of-work challenges prevent bot registration
- ✅ Rate limiting on all endpoints
- ✅ Username profanity filtering
- ✅ Content moderation for uploaded photos
- ✅ Input validation on all endpoints
- ✅ SQL injection protection (parameterized queries via SQLAlchemy)

---

## 📄 License & Attribution

### Project License
This project is licensed under [LICENSE_TBD]

### Data Sources
- **Test Photos**: Generated test images (no attribution required)
- **Airport Data**: OurAirports (CC0 Public Domain)
- **Future Photos**: Wikimedia Commons (CC BY 2.0, CC BY-SA 2.0, CC0)

### Dependencies
See `backend/requirements.txt` and `frontend/package.json` for full dependency lists.

---

## 🤝 Contributing

This is an MVP release. For contribution guidelines, see CONTRIBUTING.md.

### Current Development Focus
- Integration and E2E tests
- Production-ready photo seeding
- Deployment configuration
- Performance optimization

---

## 📞 Support

For issues or questions:
1. Check the [API documentation](http://127.0.0.1:8000/docs)
2. Review the [quickstart guide](specs/002-release-preparation/quickstart.md)
3. Check existing issues in the repository

---

**Last Updated**: 2026-02-01  
**Maintainer**: Development Team
