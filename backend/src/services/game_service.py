"""
Game Service

Manages game rounds, guessing logic, and scoring.
Core gameplay mechanics for the aviation guessing game.

Scoring:
- Aircraft type: Up to 1000 points (fuzzy matching)
- Location: Up to 1000 points (distance-based decay)
- Total per round: Up to 2000 points
"""

import math
import random
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.models.game_round import GameRound, RoundStatus
from src.models.guess import Guess
from src.models.photo import Photo, PhotoStatus
from src.models.player import Player
from src.utils.errors import (
    GameRoundNotFoundError,
    NotFoundError,
    RoundExpiredError,
    RoundNotActiveError,
)
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Scoring constants
MAX_AIRCRAFT_SCORE = 1000
MAX_LOCATION_SCORE = 1000

# Distance scoring (km thresholds)
PERFECT_DISTANCE_KM = 50      # Full points
ZERO_SCORE_DISTANCE_KM = 5000  # No points beyond this


class GameService:
    """
    Service for game round management.
    
    Handles:
    - Starting new rounds
    - Processing guesses
    - Calculating scores
    - Completing rounds
    """
    
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
    
    async def start_round(
        self,
        session: AsyncSession,
        player_id: uuid.UUID,
    ) -> GameRound:
        """
        Start a new game round for a player.
        
        Selects a random approved photo and creates a new round.
        
        Args:
            session: Database session
            player_id: Player starting the round
        
        Returns:
            New GameRound instance
        
        Raises:
            NotFoundError: If player not found
            GameError: If no photos available
        """
        # Verify player exists
        player = await session.get(Player, player_id)
        if not player:
            raise NotFoundError("Player", str(player_id))
        
        # Select random photo
        photo = await self._select_random_photo(session, player_id)
        if not photo:
            raise NotFoundError("Photo", "No approved photos available")
        
        # Create round
        round = GameRound.create(
            player_id=player_id,
            photo_id=photo.id,
            round_duration_seconds=self.settings.round_duration_seconds,
            max_guesses=self.settings.max_guesses_per_round,
        )
        
        session.add(round)
        await session.flush()
        
        logger.info(f"Started round {round.id} for player {player_id}")
        
        return round
    
    async def submit_guess(
        self,
        session: AsyncSession,
        round_id: uuid.UUID,
        player_id: uuid.UUID,
        aircraft_guess: str | None = None,
        location_lat: float | None = None,
        location_lon: float | None = None,
    ) -> Guess:
        """
        Submit a guess for a game round.
        
        Args:
            session: Database session
            round_id: Round to guess on
            player_id: Player making the guess
            aircraft_guess: Aircraft type guess
            location_lat: Latitude of location guess
            location_lon: Longitude of location guess
        
        Returns:
            Created Guess with scores
        
        Raises:
            GameRoundNotFoundError: If round not found
            RoundNotActiveError: If round is not active
            RoundExpiredError: If round has expired
        """
        # Get round with photo
        round = await session.get(GameRound, round_id)
        if not round:
            raise GameRoundNotFoundError(str(round_id))
        
        if round.player_id != player_id:
            raise GameRoundNotFoundError(str(round_id))
        
        # Check round status
        if round.status != RoundStatus.ACTIVE:
            raise RoundNotActiveError()
        
        if datetime.now(timezone.utc) > round.expires_at:
            round.status = RoundStatus.COMPLETED
            round.completed_at = datetime.now(timezone.utc)
            await session.flush()
            raise RoundExpiredError()
        
        if round.guesses_made >= round.max_guesses:
            round.complete()
            await session.flush()
            raise RoundNotActiveError()
        
        # Get photo for scoring
        photo = await session.get(Photo, round.photo_id)
        
        # Calculate scores
        aircraft_score = 0
        location_score = 0
        distance_km = None
        
        if aircraft_guess and photo:
            aircraft_score = self._score_aircraft_guess(
                aircraft_guess, photo.aircraft_type
            )
        
        if location_lat is not None and location_lon is not None and photo:
            location_score, distance_km = await self._score_location_guess(
                session, location_lat, location_lon, photo.airport_code
            )
        
        # Create guess record
        guess = Guess.create(
            round_id=round_id,
            guess_number=round.guesses_made + 1,
            aircraft_guess=aircraft_guess,
            aircraft_score=aircraft_score,
            location_lat=location_lat,
            location_lon=location_lon,
            location_score=location_score,
            distance_km=distance_km,
        )
        
        session.add(guess)
        
        # Update round
        round.record_guess(
            aircraft_score=aircraft_score,
            location_score=location_score,
            aircraft_guess=aircraft_guess,
            location_lat=location_lat,
            location_lon=location_lon,
        )
        
        # Check if round should complete
        if round.guesses_made >= round.max_guesses:
            round.complete()
        
        await session.flush()
        
        logger.info(
            f"Guess {guess.guess_number} on round {round_id}: "
            f"aircraft={aircraft_score}, location={location_score}"
        )
        
        return guess
    
    async def complete_round(
        self,
        session: AsyncSession,
        round_id: uuid.UUID,
        player_id: uuid.UUID,
    ) -> GameRound:
        """
        Manually complete a round (give up).
        
        Args:
            session: Database session
            round_id: Round to complete
            player_id: Player who owns the round
        
        Returns:
            Completed GameRound
        """
        round = await session.get(GameRound, round_id)
        if not round or round.player_id != player_id:
            raise GameRoundNotFoundError(str(round_id))
        
        if round.status == RoundStatus.ACTIVE:
            round.complete()
            
            # Update player stats
            player = await session.get(Player, player_id)
            if player:
                player.add_score(round.final_score)
            
            # Update photo stats
            photo = await session.get(Photo, round.photo_id)
            if photo:
                photo.record_usage(round.final_score)
            
            await session.flush()
        
        return round
    
    async def get_round(
        self,
        session: AsyncSession,
        round_id: uuid.UUID,
        player_id: uuid.UUID,
    ) -> GameRound | None:
        """Get a round by ID, verifying ownership."""
        round = await session.get(GameRound, round_id)
        if round and round.player_id == player_id:
            return round
        return None
    
    async def get_player_rounds(
        self,
        session: AsyncSession,
        player_id: uuid.UUID,
        limit: int = 10,
    ) -> list[GameRound]:
        """Get recent rounds for a player."""
        query = (
            select(GameRound)
            .where(GameRound.player_id == player_id)
            .order_by(GameRound.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(query)
        return list(result.scalars().all())
    
    async def _select_random_photo(
        self,
        session: AsyncSession,
        player_id: uuid.UUID,
    ) -> Photo | None:
        """
        Select a random approved photo.
        
        Tries to avoid photos the player has seen recently.
        """
        # Get IDs of photos player has seen recently
        recent_query = (
            select(GameRound.photo_id)
            .where(GameRound.player_id == player_id)
            .order_by(GameRound.created_at.desc())
            .limit(20)
        )
        recent_result = await session.execute(recent_query)
        recent_photo_ids = [r[0] for r in recent_result.all()]
        
        # Select random approved photo not recently seen
        query = (
            select(Photo)
            .where(Photo.status == PhotoStatus.APPROVED)
        )
        
        if recent_photo_ids:
            query = query.where(Photo.id.not_in(recent_photo_ids))
        
        result = await session.execute(query)
        photos = list(result.scalars().all())
        
        if not photos:
            # Fall back to any approved photo
            query = select(Photo).where(Photo.status == PhotoStatus.APPROVED)
            result = await session.execute(query)
            photos = list(result.scalars().all())
        
        if photos:
            return random.choice(photos)
        
        return None
    
    def _score_aircraft_guess(
        self,
        guess: str,
        actual: str,
    ) -> int:
        """
        Score an aircraft type guess using fuzzy matching.
        
        Uses a combination of:
        - Exact match (full points)
        - Contains match (partial points)
        - Levenshtein similarity (partial points)
        """
        guess_lower = guess.lower().strip()
        actual_lower = actual.lower().strip()
        
        # Exact match
        if guess_lower == actual_lower:
            return MAX_AIRCRAFT_SCORE
        
        # Contains match (either direction)
        if guess_lower in actual_lower or actual_lower in guess_lower:
            # Partial credit based on length ratio
            shorter = min(len(guess_lower), len(actual_lower))
            longer = max(len(guess_lower), len(actual_lower))
            ratio = shorter / longer
            return int(MAX_AIRCRAFT_SCORE * ratio * 0.8)
        
        # Levenshtein-based similarity
        distance = self._levenshtein_distance(guess_lower, actual_lower)
        max_len = max(len(guess_lower), len(actual_lower))
        
        if max_len == 0:
            return 0
        
        similarity = 1 - (distance / max_len)
        
        # Require at least 50% similarity for any points
        if similarity < 0.5:
            return 0
        
        # Scale remaining similarity to points
        return int(MAX_AIRCRAFT_SCORE * (similarity - 0.5) * 2 * 0.6)
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein edit distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    async def _score_location_guess(
        self,
        session: AsyncSession,
        guess_lat: float,
        guess_lon: float,
        airport_code: str | None,
    ) -> tuple[int, float | None]:
        """
        Score a location guess based on distance from airport.
        
        Returns (score, distance_km).
        """
        if not airport_code:
            return 0, None
        
        # Get airport coordinates
        airport_coords = await self._get_airport_coordinates(session, airport_code)
        if not airport_coords:
            return 0, None
        
        airport_lat, airport_lon = airport_coords
        
        # Calculate distance
        distance_km = self._haversine_distance(
            guess_lat, guess_lon, airport_lat, airport_lon
        )
        
        # Calculate score based on distance
        if distance_km <= PERFECT_DISTANCE_KM:
            score = MAX_LOCATION_SCORE
        elif distance_km >= ZERO_SCORE_DISTANCE_KM:
            score = 0
        else:
            # Linear decay between thresholds
            range_km = ZERO_SCORE_DISTANCE_KM - PERFECT_DISTANCE_KM
            excess_km = distance_km - PERFECT_DISTANCE_KM
            ratio = 1 - (excess_km / range_km)
            score = int(MAX_LOCATION_SCORE * ratio)
        
        return score, distance_km
    
    async def _get_airport_coordinates(
        self,
        session: AsyncSession,
        airport_code: str,
    ) -> tuple[float, float] | None:
        """
        Get airport coordinates from database or static data.
        
        TODO: Implement airport database lookup.
        For now, returns None (no location scoring).
        """
        # Placeholder - implement airport database
        return None
    
    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """
        Calculate great-circle distance between two points.
        
        Returns distance in kilometers.
        """
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) *
            math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
