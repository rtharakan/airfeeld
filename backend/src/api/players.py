"""
Players API Endpoints

Handles player account registration, data export, and deletion.

Endpoints:
- POST /players/challenge - Request PoW challenge for registration
- POST /players/register - Register new player with PoW solution
- GET /players/{player_id} - Get player public profile
- GET /players/{player_id}/stats - Get player statistics
- GET /players/{player_id}/export - Export all player data (GDPR)
- DELETE /players/{player_id} - Delete player account (GDPR)
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.middleware.rate_limit import get_client_ip
from src.services.player_service import PlayerService
from src.services.pow_service import ProofOfWorkService
from src.utils.errors import NotFoundError

router = APIRouter(prefix="/players", tags=["players"])


# Request/Response Models

class ChallengeRequest(BaseModel):
    """Request for a proof-of-work challenge."""
    
    accessibility_mode: bool = Field(
        default=False,
        description="Request reduced difficulty for accessibility",
    )


class ChallengeResponse(BaseModel):
    """Proof-of-work challenge for registration."""
    
    challenge_id: uuid.UUID = Field(description="Challenge identifier")
    challenge_nonce: str = Field(description="Challenge nonce to hash")
    difficulty: int = Field(description="Required leading zeros")
    expires_in: int = Field(description="Seconds until expiration")


class RegisterRequest(BaseModel):
    """Player registration request with PoW solution."""
    
    username: str = Field(
        min_length=3,
        max_length=24,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Desired username (3-24 chars, alphanumeric + underscore)",
    )
    challenge_id: uuid.UUID = Field(description="Challenge ID from /challenge")
    solution_nonce: str = Field(
        min_length=1,
        max_length=64,
        description="Nonce that solves the challenge",
    )


class PlayerResponse(BaseModel):
    """Player public profile."""
    
    id: uuid.UUID = Field(description="Player ID")
    username: str = Field(description="Display name")
    games_played: int = Field(description="Total games played")
    total_score: int = Field(description="Cumulative score")


class PlayerStatsResponse(BaseModel):
    """Detailed player statistics."""
    
    id: uuid.UUID = Field(description="Player ID")
    username: str = Field(description="Display name")
    games_played: int = Field(description="Total games played")
    total_score: int = Field(description="Cumulative score")
    average_score: float = Field(description="Average score per game")
    rank: int | None = Field(description="Leaderboard rank (if available)")


class DataExportResponse(BaseModel):
    """GDPR data export response."""
    
    player_id: str = Field(description="Player ID")
    username: str = Field(description="Username")
    exported_at: str = Field(description="Export timestamp (ISO 8601)")
    data: dict = Field(description="All player data")


# Dependencies

def get_player_service() -> PlayerService:
    """Dependency for PlayerService."""
    return PlayerService()


def get_pow_service() -> ProofOfWorkService:
    """Dependency for ProofOfWorkService."""
    return ProofOfWorkService()


# Endpoints

@router.post(
    "/challenge",
    response_model=ChallengeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Request registration challenge",
    description=(
        "Request a proof-of-work challenge required for account registration. "
        "This prevents automated bot registrations."
    ),
)
async def create_challenge(
    request: Request,
    body: ChallengeRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    pow_service: Annotated[ProofOfWorkService, Depends(get_pow_service)],
) -> ChallengeResponse:
    """
    Create a new proof-of-work challenge.
    
    The client must solve the challenge by finding a nonce such that
    SHA256(challenge_nonce + solution_nonce) starts with `difficulty`
    leading zeros (in hex).
    """
    client_ip = get_client_ip(request)
    
    challenge = await pow_service.create_challenge(
        session,
        client_ip,
        reduced_difficulty=body.accessibility_mode,
    )
    
    await session.commit()
    
    return ChallengeResponse(
        challenge_id=challenge.id,
        challenge_nonce=challenge.challenge_nonce,
        difficulty=challenge.difficulty,
        expires_in=300,  # 5 minutes
    )


@router.post(
    "/register",
    response_model=PlayerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new player",
    description=(
        "Register a new player account. Requires a valid proof-of-work solution "
        "obtained from /players/challenge."
    ),
)
async def register_player(
    request: Request,
    body: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    player_service: Annotated[PlayerService, Depends(get_player_service)],
) -> PlayerResponse:
    """
    Register a new player with PoW solution.
    
    Validates the proof-of-work solution and creates the account
    if the username is valid and available.
    """
    client_ip = get_client_ip(request)
    
    player = await player_service.create_player(
        session,
        username=body.username,
        challenge_id=body.challenge_id,
        solution_nonce=body.solution_nonce,
        client_ip=client_ip,
    )
    
    await session.commit()
    
    return PlayerResponse(
        id=player.id,
        username=player.username,
        games_played=player.games_played,
        total_score=player.total_score,
    )


@router.get(
    "/{player_id}",
    response_model=PlayerResponse,
    summary="Get player profile",
    description="Get a player's public profile information.",
)
async def get_player(
    player_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    player_service: Annotated[PlayerService, Depends(get_player_service)],
) -> PlayerResponse:
    """Get player public profile by ID."""
    player = await player_service.get_by_id(session, player_id)
    if not player:
        raise NotFoundError("Player", str(player_id))
    
    return PlayerResponse(
        id=player.id,
        username=player.username,
        games_played=player.games_played,
        total_score=player.total_score,
    )


@router.get(
    "/{player_id}/stats",
    response_model=PlayerStatsResponse,
    summary="Get player statistics",
    description="Get detailed statistics for a player.",
)
async def get_player_stats(
    player_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    player_service: Annotated[PlayerService, Depends(get_player_service)],
) -> PlayerStatsResponse:
    """Get detailed player statistics."""
    stats = await player_service.get_stats(session, player_id)
    if not stats:
        raise NotFoundError("Player", str(player_id))
    
    return PlayerStatsResponse(**stats)


@router.get(
    "/{player_id}/export",
    response_model=DataExportResponse,
    summary="Export player data",
    description=(
        "Export all data associated with a player account. "
        "GDPR Article 20: Right to data portability."
    ),
)
async def export_player_data(
    request: Request,
    player_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    player_service: Annotated[PlayerService, Depends(get_player_service)],
    x_player_id: Annotated[str | None, Header()] = None,
) -> DataExportResponse:
    """
    Export all player data for GDPR compliance.
    
    Only the player themselves can export their data.
    """
    # Verify requester is the player
    # TODO: Implement proper authentication
    if x_player_id != str(player_id):
        raise NotFoundError("Player", str(player_id))
    
    client_ip = get_client_ip(request)
    
    export_data = await player_service.export_player_data(
        session, player_id, client_ip
    )
    
    return DataExportResponse(**export_data)


@router.delete(
    "/{player_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete player account",
    description=(
        "Delete a player account and all associated data. "
        "GDPR Article 17: Right to erasure. This action is irreversible."
    ),
)
async def delete_player(
    request: Request,
    player_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    player_service: Annotated[PlayerService, Depends(get_player_service)],
    x_player_id: Annotated[str | None, Header()] = None,
) -> None:
    """
    Delete player account and all data.
    
    Only the player themselves can delete their account.
    Must complete within 72 hours per GDPR.
    """
    # Verify requester is the player
    # TODO: Implement proper authentication
    if x_player_id != str(player_id):
        raise NotFoundError("Player", str(player_id))
    
    client_ip = get_client_ip(request)
    
    deleted = await player_service.delete_player(
        session, player_id, client_ip
    )
    
    if not deleted:
        raise NotFoundError("Player", str(player_id))
    
    await session.commit()
