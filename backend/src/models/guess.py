"""
Guess Model

Records individual guesses made during a game round.
Each guess can include aircraft type and/or location.

Scoring Algorithm:
- Aircraft: Levenshtein distance + partial matching
- Location: Haversine distance from actual airport
"""

import uuid
from datetime import datetime, timezone
from typing import Self

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDMixin


class Guess(Base, UUIDMixin):
    """
    A single guess within a game round.
    
    Players can guess aircraft type and/or click on a map
    to guess the location where the photo was taken.
    """
    
    __tablename__ = "guesses"
    
    # Parent round
    round_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("game_rounds.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Guess number within round (1-5)
    guess_number: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Timestamp
    guessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    
    # Aircraft guess
    aircraft_guess: Mapped[str | None] = mapped_column(String(128), nullable=True)
    aircraft_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Location guess (click on map)
    location_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Total score for this guess
    total_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Relationship
    round = relationship("GameRound", back_populates="guesses")
    
    @classmethod
    def create(
        cls,
        round_id: uuid.UUID,
        guess_number: int,
        aircraft_guess: str | None = None,
        aircraft_score: int = 0,
        location_lat: float | None = None,
        location_lon: float | None = None,
        location_score: int = 0,
        distance_km: float | None = None,
    ) -> Self:
        """Create a new guess record."""
        return cls(
            round_id=round_id,
            guess_number=guess_number,
            aircraft_guess=aircraft_guess,
            aircraft_score=aircraft_score,
            location_lat=location_lat,
            location_lon=location_lon,
            location_score=location_score,
            distance_km=distance_km,
            total_score=aircraft_score + location_score,
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        result = {
            "id": str(self.id),
            "guess_number": self.guess_number,
            "guessed_at": self.guessed_at.isoformat(),
            "total_score": self.total_score,
        }
        
        if self.aircraft_guess:
            result["aircraft"] = {
                "guess": self.aircraft_guess,
                "score": self.aircraft_score,
            }
        
        if self.location_lat is not None:
            result["location"] = {
                "latitude": self.location_lat,
                "longitude": self.location_lon,
                "score": self.location_score,
                "distance_km": self.distance_km,
            }
        
        return result
