"""
Base SQLAlchemy Model

Provides common functionality for all database models:
- UUID primary keys for privacy (no sequential IDs to enumerate)
- Timestamp tracking (created_at, updated_at)
- Consistent table naming conventions
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, MetaData
from sqlalchemy.dialects.sqlite import CHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

# Naming convention for database constraints
# This ensures consistent, predictable constraint names across migrations
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    
    Provides:
    - Automatic table naming from class name (snake_case)
    - UUID primary key (non-sequential for privacy)
    - Created/updated timestamp tracking
    - Consistent metadata with naming conventions
    """
    
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    
    # Type annotations for common columns
    type_annotation_map = {
        uuid.UUID: CHAR(36),
    }
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Generate table name from class name.
        
        Converts CamelCase to snake_case:
        - Player -> player
        - GameRound -> game_round
        - PhotoAttribution -> photo_attribution
        """
        name = cls.__name__
        # Insert underscore before uppercase letters and lowercase
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append("_")
            result.append(char.lower())
        return "".join(result)
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert model to dictionary.
        
        Useful for serialization. Handles UUIDs and datetimes.
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, uuid.UUID):
                value = str(value)
            elif isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result


class TimestampMixin:
    """
    Mixin for automatic timestamp tracking.
    
    Adds created_at and updated_at columns that are automatically
    managed by the database.
    """
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UUIDMixin:
    """
    Mixin for UUID primary key.
    
    Uses UUIDs instead of sequential integers for privacy:
    - Cannot enumerate records by ID
    - Cannot determine creation order from ID
    - Cannot estimate total record count from ID
    """
    
    id: Mapped[uuid.UUID] = mapped_column(
        CHAR(36),
        primary_key=True,
        default=uuid.uuid4,
    )


def generate_uuid() -> uuid.UUID:
    """Generate a new UUID v4."""
    return uuid.uuid4()
