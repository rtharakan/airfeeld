"""
Rate Limit Entry Model

Tracks API request rates per IP hash for abuse prevention.
No personal data is stored - only hashed IP addresses.

Privacy Design:
- Raw IP addresses are NEVER stored
- Only SHA-256 hashes used for rate limit tracking
- Entries deleted after window expiration + 1 hour
- Not correlated with player accounts
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class RateLimitEntry(Base):
    """
    Tracks request counts per IP hash for rate limiting.
    
    Each entry represents a specific IP + endpoint combination
    within a sliding time window. Entries are automatically
    cleaned up after the window expires.
    """
    
    __tablename__ = "rate_limit_entry"
    
    # SHA-256 hash of client IP (never raw IP)
    ip_hash: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )
    
    # API endpoint path being rate limited
    endpoint: Mapped[str] = mapped_column(
        String(128),
        primary_key=True,
    )
    
    # Number of requests in current window
    request_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    
    # Start of current rate limit window
    window_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    
    # Duration of rate limit window in seconds
    window_duration_seconds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    
    __table_args__ = (
        Index("ix_ratelimit_window", "window_start"),
    )
    
    @classmethod
    def create(
        cls,
        ip_hash: str,
        endpoint: str,
        window_duration_seconds: int,
    ) -> "RateLimitEntry":
        """
        Create a new rate limit entry.
        
        Args:
            ip_hash: SHA-256 hash of client IP
            endpoint: API endpoint path
            window_duration_seconds: Rate limit window duration
        
        Returns:
            New RateLimitEntry instance (not yet persisted)
        """
        return cls(
            ip_hash=ip_hash,
            endpoint=endpoint,
            request_count=1,
            window_start=datetime.now(timezone.utc),
            window_duration_seconds=window_duration_seconds,
        )
    
    @property
    def window_end(self) -> datetime:
        """Calculate when the current window expires."""
        return self.window_start + timedelta(seconds=self.window_duration_seconds)
    
    @property
    def is_window_expired(self) -> bool:
        """Check if the current rate limit window has expired."""
        return datetime.now(timezone.utc) > self.window_end
    
    def increment(self) -> int:
        """
        Increment request count and return new value.
        
        If window has expired, reset the window and count.
        
        Returns:
            New request count
        """
        if self.is_window_expired:
            self.window_start = datetime.now(timezone.utc)
            self.request_count = 1
        else:
            self.request_count += 1
        return self.request_count
    
    def reset_window(self) -> None:
        """Reset the rate limit window."""
        self.window_start = datetime.now(timezone.utc)
        self.request_count = 0


# Rate limit configurations by endpoint type
# Format: (max_requests, window_duration_seconds)
RATE_LIMITS = {
    # Account creation: 3 per IP per 24 hours
    "/players/register": (3, 86400),
    "/players/challenge": (10, 900),  # 10 challenges per 15 minutes
    
    # Photo upload: 5 per IP per hour
    "/photos/upload": (5, 3600),
    
    # Gameplay: 100 guesses per IP per hour
    "/game/guess": (100, 3600),
    
    # Search: 60 per IP per minute
    "/airports": (60, 60),
    "/airports/search": (60, 60),
    
    # Flagging: 5 per player per 24 hours
    "/photos/flag": (5, 86400),
}


def get_rate_limit(endpoint: str) -> tuple[int, int]:
    """
    Get rate limit configuration for an endpoint.
    
    Args:
        endpoint: API endpoint path
    
    Returns:
        Tuple of (max_requests, window_duration_seconds)
    """
    # Try exact match first
    if endpoint in RATE_LIMITS:
        return RATE_LIMITS[endpoint]
    
    # Try prefix match for parameterized routes
    for pattern, limits in RATE_LIMITS.items():
        if endpoint.startswith(pattern.rstrip("/")):
            return limits
    
    # Default: 100 requests per minute
    return (100, 60)
