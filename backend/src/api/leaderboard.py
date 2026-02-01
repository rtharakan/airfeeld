"""
Leaderboard API Endpoints

Provides global player rankings and statistics.

Endpoints:
- GET /leaderboard - Get top players
- GET /leaderboard/{player_id}/rank - Get specific player's rank
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.player import Player

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


# Response Models

class LeaderboardEntry(BaseModel):
    """A single leaderboard entry."""
    
    rank: int = Field(description="Player rank (1-based)")
    player_id: uuid.UUID = Field(description="Player ID")
    username: str = Field(description="Player username")
    total_score: int = Field(description="Total score")
    games_played: int = Field(description="Games played")


class LeaderboardResponse(BaseModel):
    """Leaderboard response with rankings."""
    
    entries: list[LeaderboardEntry] = Field(description="Ranked players")
    total_players: int = Field(description="Total players in system")


class PlayerRankResponse(BaseModel):
    """Individual player rank response."""
    
    player_id: uuid.UUID = Field(description="Player ID")
    username: str = Field(description="Player username")
    rank: int = Field(description="Current rank")
    total_score: int = Field(description="Total score")
    games_played: int = Field(description="Games played")
    percentile: float = Field(description="Percentile rank (0-100)")


# Endpoints

@router.get(
    "",
    response_model=LeaderboardResponse,
    summary="Get global leaderboard",
    description="Returns top players ranked by total score.",
)
async def get_leaderboard(
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> LeaderboardResponse:
    """
    Get global leaderboard.
    
    Players are ranked by total_score (descending).
    Ties are broken by games_played (ascending) then username (ascending).
    """
    # Get top players
    query = (
        select(Player)
        .where(Player.games_played > 0)
        .order_by(
            desc(Player.total_score),
            Player.games_played,
            Player.username,
        )
        .offset(offset)
        .limit(limit)
    )
    
    result = await session.execute(query)
    players = list(result.scalars().all())
    
    # Get total player count
    count_query = select(func.count()).select_from(Player).where(Player.games_played > 0)
    total_result = await session.execute(count_query)
    total_players = total_result.scalar_one()
    
    # Build response with ranks
    entries = [
        LeaderboardEntry(
            rank=offset + idx + 1,
            player_id=player.id,
            username=player.username,
            total_score=player.total_score,
            games_played=player.games_played,
        )
        for idx, player in enumerate(players)
    ]
    
    return LeaderboardResponse(
        entries=entries,
        total_players=total_players,
    )


@router.get(
    "/{player_id}/rank",
    response_model=PlayerRankResponse,
    summary="Get player's rank",
    description="Returns a specific player's current leaderboard rank and percentile.",
)
async def get_player_rank(
    player_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PlayerRankResponse:
    """
    Get a player's current rank.
    
    Calculates rank and percentile based on total_score.
    """
    # Get player
    player = await session.get(Player, player_id)
    if not player:
        from src.utils.errors import NotFoundError
        raise NotFoundError("Player", str(player_id))
    
    # Count players with higher score
    higher_query = (
        select(func.count())
        .select_from(Player)
        .where(
            Player.games_played > 0,
            Player.total_score > player.total_score,
        )
    )
    higher_result = await session.execute(higher_query)
    players_ahead = higher_result.scalar_one()
    
    rank = players_ahead + 1
    
    # Get total active players
    total_query = select(func.count()).select_from(Player).where(Player.games_played > 0)
    total_result = await session.execute(total_query)
    total_players = total_result.scalar_one()
    
    # Calculate percentile
    percentile = 100.0 * (1 - (rank - 1) / max(total_players, 1))
    
    return PlayerRankResponse(
        player_id=player.id,
        username=player.username,
        rank=rank,
        total_score=player.total_score,
        games_played=player.games_played,
        percentile=round(percentile, 2),
    )
