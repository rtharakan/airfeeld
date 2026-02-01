"""
API Routes Package

FastAPI router definitions for all endpoints.

Routers:
- health: Health check endpoints
- players: Player account management
- games: Game rounds and guessing
- photos: Photo upload and retrieval
- leaderboard: Global rankings
"""

from src.api.games import router as games_router
from src.api.health import router as health_router
from src.api.leaderboard import router as leaderboard_router
from src.api.photos import router as photos_router
from src.api.players import router as players_router

__all__ = [
    "games_router",
    "health_router",
    "leaderboard_router",
    "photos_router",
    "players_router",
]
