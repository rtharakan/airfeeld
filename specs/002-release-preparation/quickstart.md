# Quickstart Guide: Release Preparation

**Feature**: 002-release-preparation  
**Date**: 2026-02-01  
**Audience**: Developers preparing Airfeeld for release

---

## Purpose

This guide provides step-by-step instructions for preparing Airfeeld for its initial public release, validating all tests pass, and starting the game for playability verification.

---

## Prerequisites

**System Requirements:**
- macOS, Linux, or Windows (WSL recommended for Windows)
- Python 3.11+ installed
- Node.js 18+ installed
- Git installed
- 2GB free disk space

**Development Tools:**
- Code editor (VS Code recommended)
- Terminal/shell access
- Modern web browser (Chrome, Firefox, or Safari)

---

## Setup Instructions

### Step 1: Clone Repository & Switch Branch

```bash
cd /Users/rthar/Downloads/OpenCode/Projects/airfeeld

# Verify current branch
git branch

# Should show: * 002-release-preparation

# If not, switch to release prep branch
git checkout 002-release-preparation
```

---

### Step 2: Backend Setup

```bash
cd backend

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print(f'FastAPI {fastapi.__version__} installed')"
```

**Expected output**: `FastAPI 0.x.x installed`

---

### Step 3: Database Setup

```bash
# Still in backend/ directory

# Create data directory if not exists
mkdir -p data

# Run database migrations
alembic upgrade head

# Verify database created
ls -lh data/airfeeld.db
```

**Expected output**: `airfeeld.db` file exists (size ~50KB)

---

### Step 4: Photo Pool Seeding

```bash
# Still in backend/ directory

# Run photo seeding script (this will take 5-10 minutes)
python scripts/seed_photos.py --source wikimedia --count 100

# Verify photos seeded
sqlite3 data/airfeeld.db "SELECT COUNT(*) FROM photos WHERE moderation_status='approved';"
```

**Expected output**: `100` (or more)

**Note**: If seeding fails due to network issues, retry with `--count 50` for a smaller seed pool.

---

### Step 5: Frontend Setup

```bash
# Open new terminal window
cd /Users/rthar/Downloads/OpenCode/Projects/airfeeld/frontend

# Install dependencies
npm install

# Verify installation
npm list react react-dom vite
```

**Expected output**: Shows installed versions of React, React DOM, and Vite

---

## Running the Application

### Step 6: Start Backend Server

```bash
# Terminal 1: backend directory
cd /Users/rthar/Downloads/OpenCode/Projects/airfeeld/backend
source venv/bin/activate

# Start server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Wait for startup message:
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify backend health:**
```bash
# In new terminal window
curl http://localhost:8000/api/v1/health

# Expected output:
# {"status":"ok","timestamp":"2026-02-01T..."}
```

---

### Step 7: Start Frontend Server

```bash
# Terminal 2: frontend directory
cd /Users/rthar/Downloads/OpenCode/Projects/airfeeld/frontend

# Start dev server
npm run dev

# Wait for startup message:
# VITE ready in Xms
# ➜  Local:   http://localhost:5173/
```

**Verify frontend loads:**
- Open browser: http://localhost:5173
- Should see Airfeeld homepage with "Play" and "Leaderboard" links

---

## Testing the Application

### Step 8: Manual Smoke Test (P0 Validation)

**Test 1: Player Registration**
1. Navigate to http://localhost:5173
2. Enter username: `test_player_001`
3. Click "Register"
4. Wait for PoW challenge to complete (5-10 seconds)
5. ✅ Success: See "Registration successful" message

**Test 2: Play Game Round**
1. Click "Play" link in navigation
2. ✅ Success: Airport photo loads (no EXIF data visible in browser DevTools)
3. Use airport search: Type "JFK"
4. ✅ Success: Autocomplete shows "John F Kennedy International Airport (KJFK)"
5. Select airport from dropdown
6. Click "Submit Guess"
7. ✅ Success: Results show correct/incorrect, score, and airport details

**Test 3: View Leaderboard**
1. Click "Leaderboard" link in navigation
2. ✅ Success: See ranked list of players including your username
3. ✅ Success: No email addresses or personal data visible

---

### Step 9: Run Backend Unit Tests

```bash
# Terminal 3: backend directory
cd /Users/rthar/Downloads/OpenCode/Projects/airfeeld/backend
source venv/bin/activate

# Run all unit tests
pytest tests/unit/ -v

# Expected output: All tests pass (green)
# ===== X passed in Y.Ys =====
```

**If tests fail:**
- Check that virtual environment is activated
- Verify all dependencies installed: `pip list`
- Check test output for specific errors

---

### Step 10: Run Backend Integration Tests

```bash
# Still in backend/ directory

# Run integration tests (requires backend NOT running in another terminal)
# Stop backend server (Ctrl+C in Terminal 1) before running this

pytest tests/integration/ -v

# Expected output: All tests pass
```

**If integration tests fail:**
- Ensure backend server is NOT running (port 8000 must be free)
- Check database is initialized: `ls data/airfeeld.db`
- Verify test fixtures exist: `ls tests/fixtures/`

---

### Step 11: Run Contract Tests (API Validation)

```bash
# Still in backend/ directory

# Run contract tests against OpenAPI spec
pytest tests/contract/ -v

# Expected output: All API endpoints match specification
```

---

## Validation Checklist

Use this checklist to verify release readiness:

**Backend:**
- [ ] Backend server starts without errors
- [ ] Health endpoint returns 200 OK
- [ ] All unit tests pass (PoW, rate limiting, profanity filter)
- [ ] All integration tests pass (registration, gameplay, leaderboard)
- [ ] All contract tests pass (API matches OpenAPI spec)
- [ ] Database migrations applied successfully
- [ ] Photo pool seeded with 100+ photos

**Frontend:**
- [ ] Frontend dev server starts without errors
- [ ] Homepage loads without console errors
- [ ] Player registration completes successfully
- [ ] Game round completes successfully (photo → guess → result)
- [ ] Leaderboard displays correctly
- [ ] No EXIF data visible in browser DevTools (check Network tab → photo request)

**Privacy Validation:**
- [ ] EXIF stripping test passes (TC-006)
- [ ] No location data in photo metadata (manual check with `exiftool`)
- [ ] No personal data on leaderboard (only username + score)
- [ ] No third-party tracking scripts in frontend (check Network tab)

**Constitutional Compliance:**
- [ ] No monetization elements (no ads, no premium tiers)
- [ ] No user profiling (no analytics, no tracking)
- [ ] WCAG AA contrast ratios met (use browser DevTools → Lighthouse)
- [ ] Keyboard navigation works (Tab through all interactive elements)

---

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`  
**Fix**: Activate virtual environment and reinstall dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Error**: `Address already in use (port 8000)`  
**Fix**: Kill existing process on port 8000:
```bash
lsof -ti:8000 | xargs kill -9
```

---

### Frontend won't start

**Error**: `EADDRINUSE: address already in use :::5173`  
**Fix**: Kill existing process on port 5173:
```bash
lsof -ti:5173 | xargs kill -9
```

**Error**: `Module not found: Cannot resolve '@/components/...'`  
**Fix**: Reinstall dependencies:
```bash
rm -rf node_modules package-lock.json
npm install
```

---

### Tests fail

**Error**: `sqlite3.OperationalError: no such table: players`  
**Fix**: Run database migrations:
```bash
cd backend
alembic upgrade head
```

**Error**: `pytest: command not found`  
**Fix**: Install pytest in virtual environment:
```bash
source venv/bin/activate
pip install pytest pytest-asyncio
```

---

### Photo seeding fails

**Error**: `ConnectionError: Failed to connect to Wikimedia Commons API`  
**Fix**: Check internet connection and retry. If persistent, use smaller seed pool:
```bash
python scripts/seed_photos.py --source wikimedia --count 50
```

**Error**: `ValueError: No airport found for photo`  
**Fix**: This is expected for some photos. Script will skip them and continue. Verify final count is still ≥ 50.

---

## Next Steps

After completing this quickstart:

1. **Review test results**: Check `tests/contract/test-contracts.md` for detailed test scenarios
2. **Run accessibility audit**: Use Lighthouse in Chrome DevTools
3. **Performance testing**: Measure bundle size and page load times
4. **Code review**: Review implementation against specification
5. **Update documentation**: Document any changes or learnings

---

## Additional Resources

- [Feature Specification](../spec.md) - User scenarios and requirements
- [Data Model](../data-model.md) - Database schema and relationships
- [Test Contracts](../contracts/test-contracts.md) - Detailed test scenarios
- [Research Document](../research.md) - Technical decisions and rationale
- [Constitution](../../../.specify/memory/constitution.md) - Project principles and governance

---

## Getting Help

If you encounter issues not covered in this guide:

1. Check existing issues on GitHub
2. Review error logs in terminal output
3. Consult the constitution for decision-making guidance
4. Ask for help in project communication channels

---

**Last Updated**: 2026-02-01  
**Maintainer**: Airfeeld Development Team  
**Status**: Active
