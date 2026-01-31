# Airfeeld

A privacy-preserving aviation guessing game for desktop, web, and iOS.

## About

Airfeeld is an aviation discovery game where players identify airports and aircraft from photographs. Inspired by geographic guessing games, Airfeeld focuses on aviation education while maintaining strict privacy protections.

**Core Principles:**
- Privacy by design (no tracking, minimal data collection)
- Non-commercial and open source
- Accessible to all (WCAG AA compliant)
- Built with open aviation data

## Game Modes

### Airport Guessing

View a photograph taken during take-off or landing and identify the airport. Progressive scoring system:

- **Attempt 1**: 10 points for correct guess
- **Attempt 2**: Distance feedback provided, 5 points for correct guess
- **Attempt 3**: Country hint provided, 3 points for correct guess

### Aircraft Identification

Identify the airline and aircraft model from photographs. When available, see contextual flight information after guessing.

## Features

- **Progressive Scoring**: Three-attempt system with increasing hints
- **Dynamic Difficulty**: Community-driven difficulty multipliers (activates at 500+ photos)
- **Photo Contributions**: Upload your own aviation photos with proper attribution
- **Global Leaderboards**: Compete for top scores without social tracking
- **Offline Gameplay**: Play with cached photos when offline
- **Privacy First**: No location tracking, no behavioral analytics, no dark patterns

## Privacy Commitment

Airfeeld is built with privacy as a core constraint, not an afterthought:

- No continuous location tracking
- No user behavior profiling
- No third-party analytics or advertising
- EXIF metadata stripped from all photos
- Minimal player identity (username and score only)
- Open data sources only

See [docs/privacy-policy.md](docs/privacy-policy.md) for complete details.

## Technology Stack

**Backend:**
- Python 3.11
- FastAPI
- SQLite (extensible to PostgreSQL)
- Pillow (EXIF stripping)

**Frontend:**
- React 18
- TypeScript
- Vite
- Tailwind CSS

**iOS** (Phase 2):
- Swift 5.9
- SwiftUI

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/airfeeld.git
cd airfeeld

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head

# Frontend setup
cd ../frontend
npm install

# Seed aviation data
cd ../backend
python scripts/seed_data.py
```

### Development

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn src.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

Visit http://localhost:5173 to play.

## Data Sources

Airfeeld uses open aviation databases:

- **Airports**: [OurAirports](https://ourairports.com/) (CC0)
- **Airlines**: [OpenFlights](https://openflights.org/) (ODbL)
- **Aircraft**: [OpenSky Network](https://opensky-network.org/) (CC BY-SA 4.0)
- **Photos**: Creative Commons licensed photos from Flickr/Wikimedia + user contributions

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Photo Contributions

We need aviation photos for gameplay. Requirements:

- Taken during take-off or landing
- Shows identifiable airport features (runways, terminals, terrain)
- Acceptable formats: JPEG, PNG, WebP
- Minimum resolution: 800x600px
- Maximum file size: 10MB

Upload through the web interface or see [docs/photo-curation.md](docs/photo-curation.md) for bulk contributions.

## Documentation

- [Implementation Plan](specs/001-aviation-games/plan.md) - Technical architecture
- [Feature Specification](specs/001-aviation-games/spec.md) - Requirements and user stories
- [Data Model](specs/001-aviation-games/data-model.md) - Database schema
- [API Reference](docs/api-reference.md) - REST API documentation
- [Accessibility](docs/accessibility.md) - WCAG AA compliance details
- [Deployment Guide](docs/deployment.md) - Production deployment

## Roadmap

**Phase 1: Web Application** (Current)
- Airport guessing game
- Photo upload and attribution
- Global leaderboards
- Offline support

**Phase 2: iOS Application**
- Native iOS app
- Aircraft identification mode
- Enhanced offline capabilities

See [tasks.md](specs/001-aviation-games/tasks.md) for detailed implementation plan.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [OurAirports](https://ourairports.com/) for comprehensive airport data
- [OpenFlights](https://openflights.org/) for airline and route information
- [OpenSky Network](https://opensky-network.org/) for aircraft tracking data
- All photographers who contribute Creative Commons licensed aviation photos

## Contact

For questions or feedback, open an issue on GitHub.

---

**Built for fun, learning, and public interest. Not for profit, not for surveillance.**
