"""
Photo Model

Represents an aircraft photo submitted for guessing games.
Stores only essential metadata - no PII from EXIF data.

Privacy Features:
- Original EXIF data stripped before storage
- Perceptual hash for duplicate detection
- No GPS or location data retained
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Self

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class PhotoStatus(str, Enum):
    """Photo moderation status."""
    
    PENDING = "pending"       # Awaiting moderation
    APPROVED = "approved"     # Cleared for use in games
    REJECTED = "rejected"     # Failed moderation
    ARCHIVED = "archived"     # No longer in active rotation


class Photo(Base, UUIDMixin, TimestampMixin):
    """
    Aircraft photo for guessing games.
    
    Photos are submitted by players and undergo automated
    moderation before being available in game rounds.
    """
    
    __tablename__ = "photos"
    
    # Uploader reference (optional - can be anonymous)
    uploader_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("players.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # File storage
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Image metadata
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(32), nullable=False)
    
    # Perceptual hash for duplicate detection
    perceptual_hash: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )
    
    # Aircraft information (ground truth for game)
    aircraft_type: Mapped[str] = mapped_column(String(128), nullable=False)
    aircraft_registration: Mapped[str | None] = mapped_column(String(32), nullable=True)
    airline: Mapped[str | None] = mapped_column(String(128), nullable=True)
    
    # Location (airport only, no precise GPS)
    airport_code: Mapped[str | None] = mapped_column(String(4), nullable=True)
    
    # Moderation
    status: Mapped[PhotoStatus] = mapped_column(
        SAEnum(PhotoStatus),
        nullable=False,
        default=PhotoStatus.PENDING,
        index=True,
    )
    moderation_notes: Mapped[str | None] = mapped_column(String(512), nullable=True)
    moderated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    # Game usage stats
    times_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_score_awarded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Relationships
    uploader = relationship("Player", back_populates="photos")
    
    @classmethod
    def create(
        cls,
        filename: str,
        file_hash: str,
        file_size: int,
        width: int,
        height: int,
        mime_type: str,
        aircraft_type: str,
        uploader_id: uuid.UUID | None = None,
        perceptual_hash: str | None = None,
        aircraft_registration: str | None = None,
        airline: str | None = None,
        airport_code: str | None = None,
    ) -> Self:
        """
        Create a new photo record.
        
        Photo starts in PENDING status until moderated.
        """
        return cls(
            uploader_id=uploader_id,
            filename=filename,
            file_hash=file_hash,
            file_size=file_size,
            width=width,
            height=height,
            mime_type=mime_type,
            perceptual_hash=perceptual_hash,
            aircraft_type=aircraft_type,
            aircraft_registration=aircraft_registration,
            airline=airline,
            airport_code=airport_code,
            status=PhotoStatus.PENDING,
        )
    
    def approve(self, notes: str | None = None) -> None:
        """Mark photo as approved for game use."""
        self.status = PhotoStatus.APPROVED
        self.moderation_notes = notes
        self.moderated_at = datetime.now(timezone.utc)
    
    def reject(self, reason: str) -> None:
        """Reject photo with reason."""
        self.status = PhotoStatus.REJECTED
        self.moderation_notes = reason
        self.moderated_at = datetime.now(timezone.utc)
    
    def archive(self) -> None:
        """Remove from active rotation."""
        self.status = PhotoStatus.ARCHIVED
    
    def record_usage(self, score_awarded: int) -> None:
        """Record that this photo was used in a game."""
        self.times_used += 1
        self.total_score_awarded += score_awarded
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "aircraft_type": self.aircraft_type,
            "airline": self.airline,
            "airport_code": self.airport_code,
            "status": self.status.value,
            "times_used": self.times_used,
            "created_at": self.created_at.isoformat(),
        }
    
    def to_game_dict(self) -> dict:
        """
        Convert to dictionary for game display.
        
        Excludes answer information (aircraft_type, etc.).
        """
        return {
            "id": str(self.id),
            "width": self.width,
            "height": self.height,
        }
