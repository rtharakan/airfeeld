"""
Player Model

Represents a user account with minimal identifying information.
Privacy-first design: only username and score data stored.

Privacy Constraints (from constitution):
- NO email, password, or personal data
- NO device identifiers
- NO IP address storage
- NO location history
- NO session tracking beyond active game
"""

import re
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


# Username validation pattern: alphanumeric + underscore, 3-20 chars
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,20}$")


class Player(Base):
    """
    Represents a user account with minimal identifying information.
    
    Attributes stored:
    - id: UUID primary key (non-sequential for privacy)
    - username: Display name (unique, alphanumeric + underscore)
    - total_score: Cumulative score from all games
    - games_played: Number of completed game rounds
    - created_at: Account creation timestamp
    - last_active: Last gameplay activity timestamp
    
    Attributes NOT stored (by design):
    - Email, phone, or personal identifiers
    - Device fingerprints or hardware IDs
    - IP addresses or location data
    - Behavioral patterns or analytics
    """
    
    __tablename__ = "player"
    
    # UUID primary key (non-sequential for privacy)
    id: Mapped[uuid.UUID] = mapped_column(
        String(36),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Display name (unique, alphanumeric + underscore, 3-20 chars)
    username: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    
    # Cumulative score (sum of all adjusted game scores)
    total_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    
    # Number of completed game rounds
    games_played: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    
    # Account creation timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    
    # Last gameplay activity
    last_active: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    
    # Relationships
    photos = relationship("Photo", back_populates="uploader")
    game_rounds = relationship("GameRound", back_populates="player", cascade="all, delete-orphan")
    
    @classmethod
    def create(cls, username: str) -> "Player":
        """
        Create a new player with validated username.
        
        Args:
            username: Display name (must match validation rules)
        
        Returns:
            New Player instance (not yet persisted)
        
        Raises:
            ValueError: If username is invalid
        """
        if not cls.validate_username(username):
            raise ValueError(
                f"Invalid username: must be 3-20 characters, "
                f"alphanumeric and underscore only"
            )
        
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid.uuid4(),
            username=username,
            total_score=0,
            games_played=0,
            created_at=now,
            last_active=now,
        )
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Validate username format.
        
        Rules:
        - 3-20 characters long
        - Alphanumeric and underscore only
        - Case-insensitive (stored as-is, compared lowercase)
        
        Args:
            username: Username to validate
        
        Returns:
            True if valid, False otherwise
        """
        if not username or not USERNAME_PATTERN.match(username):
            return False
        return True
    
    def add_score(self, points: int) -> None:
        """
        Add points to player's total score.
        
        Args:
            points: Points to add (can be 0)
        """
        self.total_score += points
        self.games_played += 1
        self.last_active = datetime.now(timezone.utc)
    
    def to_public_dict(self) -> dict:
        """
        Return player data safe for public display.
        
        Only includes: id, username, total_score, games_played
        Excludes: created_at, last_active (timing analysis prevention)
        """
        return {
            "player_id": str(self.id),
            "username": self.username,
            "total_score": self.total_score,
            "games_played": self.games_played,
        }
    
    def to_export_dict(self) -> dict:
        """
        Return all player data for GDPR export.
        
        Includes all stored data for data portability compliance.
        """
        return {
            "player_id": str(self.id),
            "username": self.username,
            "total_score": self.total_score,
            "games_played": self.games_played,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
        }
