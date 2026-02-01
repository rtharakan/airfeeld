"""
Games API Endpoints

Handles game rounds, guesses, and scoring.

Endpoints:
- POST /games/rounds - Start a new game round
- GET /games/rounds/{round_id} - Get round status
- POST /games/rounds/{round_id}/guesses - Submit a guess
- POST /games/rounds/{round_id}/complete - Complete a round
- GET /games/rounds/{round_id}/result - Get round result
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.middleware.rate_limit import get_client_ip
from src.models.game_round import RoundStatus
from src.services.game_service import GameService
from src.utils.errors import NotFoundError

router = APIRouter(prefix="/games", tags=["games"])


# Request/Response Models

class StartRoundResponse(BaseModel):
    """Response when starting a new game round."""
    
    round_id: uuid.UUID = Field(description="Round identifier")
    photo_id: uuid.UUID = Field(description="Photo to guess")
    time_remaining: int = Field(description="Seconds remaining")
    max_guesses: int = Field(description="Maximum guesses allowed")


class GuessRequest(BaseModel):
    """Submit a guess for aircraft type and/or location."""
    
    aircraft_guess: str | None = Field(
        default=None,
        max_length=128,
        description="Aircraft type guess",
    )
    location_lat: float | None = Field(
        default=None,
        ge=-90,
        le=90,
        description="Latitude of location guess",
    )
    location_lon: float | None = Field(
        default=None,
        ge=-180,
        le=180,
        description="Longitude of location guess",
    )


class GuessResponse(BaseModel):
    """Response after submitting a guess."""
    
    guess_id: uuid.UUID = Field(description="Guess identifier")
    guess_number: int = Field(description="Guess number (1-5)")
    aircraft_score: int = Field(description="Points for aircraft guess")
    location_score: int = Field(description="Points for location guess")
    total_score: int = Field(description="Total points this guess")
    distance_km: float | None = Field(description="Distance from actual location")


class RoundStatusResponse(BaseModel):
    """Current status of a game round."""
    
    round_id: uuid.UUID = Field(description="Round identifier")
    status: str = Field(description="Round status")
    guesses_made: int = Field(description="Guesses used")
    max_guesses: int = Field(description="Maximum guesses")
    time_remaining: int = Field(description="Seconds remaining")
    current_score: int = Field(description="Current best score")


class RoundResultResponse(BaseModel):
    """Final result of a completed round."""
    
    round_id: uuid.UUID = Field(description="Round identifier")
    photo_id: uuid.UUID = Field(description="Photo that was shown")
    status: str = Field(description="Final status")
    final_score: int = Field(description="Total points earned")
    aircraft_score: int = Field(description="Best aircraft guess score")
    location_score: int = Field(description="Best location guess score")
    guesses_made: int = Field(description="Total guesses made")
    
    # Correct answers (revealed after completion)
    correct_aircraft: str | None = Field(description="Actual aircraft type")
    correct_location: dict | None = Field(description="Actual airport location")


# Dependencies

def get_game_service() -> GameService:
    """Dependency for GameService."""
    return GameService()


# Endpoints

@router.post(
    "/rounds",
    response_model=StartRoundResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new game round",
    description="Start a new guessing round with a random aircraft photo.",
)
async def start_round(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    game_service: Annotated[GameService, Depends(get_game_service)],
    x_player_id: Annotated[str, Header()],
) -> StartRoundResponse:
    """
    Start a new game round.
    
    Selects a random approved photo and creates a timed round.
    """
    try:
        player_id = uuid.UUID(x_player_id)
    except ValueError:
        raise NotFoundError("Player", x_player_id)
    
    round = await game_service.start_round(session, player_id)
    await session.commit()
    
    return StartRoundResponse(
        round_id=round.id,
        photo_id=round.photo_id,
        time_remaining=round.time_remaining,
        max_guesses=round.max_guesses,
    )


@router.get(
    "/rounds/{round_id}",
    response_model=RoundStatusResponse,
    summary="Get round status",
    description="Get the current status of a game round.",
)
async def get_round_status(
    round_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    game_service: Annotated[GameService, Depends(get_game_service)],
    x_player_id: Annotated[str, Header()],
) -> RoundStatusResponse:
    """Get current status of a game round."""
    try:
        player_id = uuid.UUID(x_player_id)
    except ValueError:
        raise NotFoundError("Player", x_player_id)
    
    round = await game_service.get_round(session, round_id, player_id)
    if not round:
        raise NotFoundError("GameRound", str(round_id))
    
    return RoundStatusResponse(
        round_id=round.id,
        status=round.status.value,
        guesses_made=round.guesses_made,
        max_guesses=round.max_guesses,
        time_remaining=round.time_remaining,
        current_score=round.final_score,
    )


@router.post(
    "/rounds/{round_id}/guesses",
    response_model=GuessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a guess",
    description="Submit a guess for the aircraft type and/or location.",
)
async def submit_guess(
    round_id: uuid.UUID,
    body: GuessRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    game_service: Annotated[GameService, Depends(get_game_service)],
    x_player_id: Annotated[str, Header()],
) -> GuessResponse:
    """
    Submit a guess for the round.
    
    Can include aircraft type guess, location guess, or both.
    """
    try:
        player_id = uuid.UUID(x_player_id)
    except ValueError:
        raise NotFoundError("Player", x_player_id)
    
    guess = await game_service.submit_guess(
        session,
        round_id=round_id,
        player_id=player_id,
        aircraft_guess=body.aircraft_guess,
        location_lat=body.location_lat,
        location_lon=body.location_lon,
    )
    
    await session.commit()
    
    return GuessResponse(
        guess_id=guess.id,
        guess_number=guess.guess_number,
        aircraft_score=guess.aircraft_score,
        location_score=guess.location_score,
        total_score=guess.total_score,
        distance_km=guess.distance_km,
    )


@router.post(
    "/rounds/{round_id}/complete",
    response_model=RoundResultResponse,
    summary="Complete a round",
    description="Manually complete a round (give up) and see the answer.",
)
async def complete_round(
    round_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    game_service: Annotated[GameService, Depends(get_game_service)],
    x_player_id: Annotated[str, Header()],
) -> RoundResultResponse:
    """
    Complete a round and reveal the answer.
    
    Use this to give up early or after using all guesses.
    """
    try:
        player_id = uuid.UUID(x_player_id)
    except ValueError:
        raise NotFoundError("Player", x_player_id)
    
    round = await game_service.complete_round(session, round_id, player_id)
    await session.commit()
    
    # Get photo for correct answers
    from src.models.photo import Photo
    photo = await session.get(Photo, round.photo_id)
    
    return RoundResultResponse(
        round_id=round.id,
        photo_id=round.photo_id,
        status=round.status.value,
        final_score=round.final_score,
        aircraft_score=round.aircraft_score,
        location_score=round.location_score,
        guesses_made=round.guesses_made,
        correct_aircraft=photo.aircraft_type if photo else None,
        correct_location={
            "airport_code": photo.airport_code,
        } if photo and photo.airport_code else None,
    )


@router.get(
    "/rounds/{round_id}/result",
    response_model=RoundResultResponse,
    summary="Get round result",
    description="Get the final result of a completed round.",
)
async def get_round_result(
    round_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    game_service: Annotated[GameService, Depends(get_game_service)],
    x_player_id: Annotated[str, Header()],
) -> RoundResultResponse:
    """Get final result of a completed round."""
    try:
        player_id = uuid.UUID(x_player_id)
    except ValueError:
        raise NotFoundError("Player", x_player_id)
    
    round = await game_service.get_round(session, round_id, player_id)
    if not round:
        raise NotFoundError("GameRound", str(round_id))
    
    # Get photo for correct answers
    from src.models.photo import Photo
    photo = await session.get(Photo, round.photo_id)
    
    # Only reveal answers if round is completed
    if round.status == RoundStatus.ACTIVE:
        return RoundResultResponse(
            round_id=round.id,
            photo_id=round.photo_id,
            status=round.status.value,
            final_score=round.final_score,
            aircraft_score=round.aircraft_score,
            location_score=round.location_score,
            guesses_made=round.guesses_made,
            correct_aircraft=None,  # Hidden until complete
            correct_location=None,
        )
    
    return RoundResultResponse(
        round_id=round.id,
        photo_id=round.photo_id,
        status=round.status.value,
        final_score=round.final_score,
        aircraft_score=round.aircraft_score,
        location_score=round.location_score,
        guesses_made=round.guesses_made,
        correct_aircraft=photo.aircraft_type if photo else None,
        correct_location={
            "airport_code": photo.airport_code,
        } if photo and photo.airport_code else None,
    )
