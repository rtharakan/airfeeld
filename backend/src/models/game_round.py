"""
Game Round Model

Represents a single guessing round where players guess aircraft details.
Each round uses one photo and allows multiple guesses with distance scoring.

Scoring:
- Aircraft type guess: 0-1000 points based on similarity
- Distance from airport: 0-1000 points (decreasing with distance)
- Total possible: 2000 points per round
"""

import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Self

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class RoundStatus(str, Enum):
    """Game round status."""
    
    ACTIVE = "active"         # Currently playable
    COMPLETED = "completed"   # Time expired or all guesses made
    ABANDONED = "abandoned"   # Player left without completing


class GameRound(Base, UUIDMixin, TimestampMixin):
    """
    A single game round for a player.
    
    Each round presents one photo and allows the player
    to make guesses about aircraft type and location.
    """
    
    __tablename__ = "game_rounds"
    
    # Player (required)
    player_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("player.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Photo being guessed
    photo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("photos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Round status
    status: Mapped[RoundStatus] = mapped_column(
        SAEnum(RoundStatus),
        nullable=False,
        default=RoundStatus.ACTIVE,
        index=True,
    )
    
    # Time limits
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Guesses made
    guesses_made: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_guesses: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    
    # Final score
    final_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    aircraft_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    location_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Best guesses (for display)
    best_aircraft_guess: Mapped[str | None] = mapped_column(String(128), nullable=True)
    best_location_lat: Mapped[float | None] = mapped_column(nullable=True)
    best_location_lon: Mapped[float | None] = mapped_column(nullable=True)
    
    # Relationships
    player = relationship("Player", back_populates="game_rounds")
    photo = relationship("Photo")
    guesses = relationship("Guess", back_populates="round", cascade="all, delete-orphan")
    
    @classmethod
    def create(
        cls,
        player_id: uuid.UUID,
        photo_id: uuid.UUID,
        round_duration_seconds: int = 120,
        max_guesses: int = 5,
    ) -> Self:
        """
        Create a new game round.
        
        Args:
            player_id: Player starting the round
            photo_id: Photo to guess
            round_duration_seconds: Time limit (default 2 minutes)
            max_guesses: Maximum guesses allowed
        """
        now = datetime.now(timezone.utc)
        return cls(
            player_id=player_id,
            photo_id=photo_id,
            status=RoundStatus.ACTIVE,
            started_at=now,
            expires_at=now + timedelta(seconds=round_duration_seconds),
            max_guesses=max_guesses,
        )
    
    @property
    def is_active(self) -> bool:
        """Check if round is still playable."""
        if self.status != RoundStatus.ACTIVE:
            return False
        if datetime.now(timezone.utc) > self.expires_at:
            return False
        if self.guesses_made >= self.max_guesses:
            return False
        return True
    
    @property
    def time_remaining(self) -> int:
        """Seconds remaining in this round."""
        if not self.is_active:
            return 0
        delta = self.expires_at - datetime.now(timezone.utc)
        return max(0, int(delta.total_seconds()))
    
    def record_guess(
        self,
        aircraft_score: int,
        location_score: int,
        aircraft_guess: str | None = None,
        location_lat: float | None = None,
        location_lon: float | None = None,
    ) -> None:
        """
        Record a guess and update scores if better.
        
        Args:
            aircraft_score: Points for aircraft type guess
            location_score: Points for location guess
            aircraft_guess: The aircraft type guessed
            location_lat: Latitude of location guess
            location_lon: Longitude of location guess
        """
        self.guesses_made += 1
        
        # Update best aircraft score
        if aircraft_score > self.aircraft_score:
            self.aircraft_score = aircraft_score
            if aircraft_guess:
                self.best_aircraft_guess = aircraft_guess
        
        # Update best location score
        if location_score > self.location_score:
            self.location_score = location_score
            if location_lat is not None:
                self.best_location_lat = location_lat
            if location_lon is not None:
                self.best_location_lon = location_lon
        
        # Update final score
        self.final_score = self.aircraft_score + self.location_score
    
    def complete(self) -> None:
        """Mark round as completed."""
        self.status = RoundStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
    
    def abandon(self) -> None:
        """Mark round as abandoned."""
        self.status = RoundStatus.ABANDONED
        self.completed_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "photo_id": str(self.photo_id),
            "status": self.status.value,
            "guesses_made": self.guesses_made,
            "max_guesses": self.max_guesses,
            "time_remaining": self.time_remaining,
            "final_score": self.final_score,
            "started_at": self.started_at.isoformat(),
        }
    
    def to_result_dict(self) -> dict:
        """Convert to dictionary with full results (after completion)."""
        return {
            **self.to_dict(),
            "aircraft_score": self.aircraft_score,
            "location_score": self.location_score,
            "best_aircraft_guess": self.best_aircraft_guess,
            "best_location": {
                "latitude": self.best_location_lat,
                "longitude": self.best_location_lon,
            } if self.best_location_lat else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
