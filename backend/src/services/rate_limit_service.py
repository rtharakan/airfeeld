"""
Rate Limit Service

Implements rate limiting for API endpoints to prevent abuse.
Uses IP hashing for privacy (never stores raw IPs).

Privacy Design:
- Raw IP addresses never stored
- Only SHA-256 hashes used for tracking
- Entries auto-expire after window + 1 hour
- Not correlated with player accounts
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.models.audit_log import AuditAction, AuditActorType, AuditLogEntry
from src.models.pow_challenge import hash_ip
from src.models.rate_limit import RATE_LIMITS, RateLimitEntry, get_rate_limit
from src.utils.errors import RateLimitError
from src.utils.logging import get_logger, log_security_event

logger = get_logger(__name__)


class RateLimitService:
    """
    Service for managing API rate limits.
    
    Rate limits are tracked per IP hash + endpoint combination.
    This prevents abuse while maintaining user privacy.
    """
    
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
    
    async def check_rate_limit(
        self,
        session: AsyncSession,
        client_ip: str,
        endpoint: str,
    ) -> tuple[int, int, int]:
        """
        Check if request is within rate limits.
        
        Args:
            session: Database session
            client_ip: Client IP address (will be hashed)
            endpoint: API endpoint path
        
        Returns:
            Tuple of (limit, remaining, reset_timestamp)
        
        Raises:
            RateLimitError: If rate limit exceeded
        """
        if not self.settings.rate_limit_enabled:
            return (0, 0, 0)  # Rate limiting disabled
        
        ip_hash = hash_ip(client_ip)
        limit, window_seconds = get_rate_limit(endpoint)
        
        # Get or create rate limit entry
        query = select(RateLimitEntry).where(
            RateLimitEntry.ip_hash == ip_hash,
            RateLimitEntry.endpoint == endpoint,
        )
        result = await session.execute(query)
        entry = result.scalar_one_or_none()
        
        now = datetime.now(timezone.utc)
        
        if entry is None:
            # First request from this IP for this endpoint
            entry = RateLimitEntry.create(
                ip_hash=ip_hash,
                endpoint=endpoint,
                window_duration_seconds=window_seconds,
            )
            session.add(entry)
            remaining = limit - 1
        elif entry.is_window_expired:
            # Window expired, reset
            entry.window_start = now
            entry.request_count = 1
            remaining = limit - 1
        else:
            # Increment counter
            entry.request_count += 1
            remaining = limit - entry.request_count
        
        # Calculate reset timestamp
        reset_timestamp = int(entry.window_end.timestamp())
        
        # Check if over limit
        if entry.request_count > limit:
            retry_after = int((entry.window_end - now).total_seconds())
            retry_after = max(1, retry_after)  # At least 1 second
            
            log_security_event(
                "rate_limit",
                f"Rate limit exceeded for {endpoint}",
                ip_hash=ip_hash,
                count=entry.request_count,
                limit=limit,
            )
            
            # Log to audit trail
            audit_entry = AuditLogEntry.create(
                action=AuditAction.RATE_LIMIT_TRIGGERED,
                actor_type=AuditActorType.ANONYMOUS,
                ip_hash=ip_hash,
                context_data={
                    "endpoint": endpoint,
                    "count": entry.request_count,
                    "limit": limit,
                },
            )
            session.add(audit_entry)
            await session.flush()
            
            raise RateLimitError(
                retry_after_seconds=retry_after,
                limit=limit,
                window_seconds=window_seconds,
            )
        
        await session.flush()
        
        return (limit, max(0, remaining), reset_timestamp)
    
    async def get_remaining(
        self,
        session: AsyncSession,
        client_ip: str,
        endpoint: str,
    ) -> tuple[int, int, int]:
        """
        Get remaining requests without incrementing counter.
        
        Args:
            session: Database session
            client_ip: Client IP address
            endpoint: API endpoint path
        
        Returns:
            Tuple of (limit, remaining, reset_timestamp)
        """
        ip_hash = hash_ip(client_ip)
        limit, window_seconds = get_rate_limit(endpoint)
        
        query = select(RateLimitEntry).where(
            RateLimitEntry.ip_hash == ip_hash,
            RateLimitEntry.endpoint == endpoint,
        )
        result = await session.execute(query)
        entry = result.scalar_one_or_none()
        
        if entry is None or entry.is_window_expired:
            # No active rate limit
            return (limit, limit, 0)
        
        remaining = max(0, limit - entry.request_count)
        reset_timestamp = int(entry.window_end.timestamp())
        
        return (limit, remaining, reset_timestamp)
    
    async def cleanup_expired(self, session: AsyncSession) -> int:
        """
        Remove expired rate limit entries.
        
        Entries are deleted 1 hour after their window expires
        to allow for any in-flight requests.
        
        Args:
            session: Database session
        
        Returns:
            Number of entries deleted
        """
        # Find entries where window has been expired for over 1 hour
        # This requires checking each entry's window_start + duration
        cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
        
        # Get all entries and check expiration
        query = select(RateLimitEntry)
        result = await session.execute(query)
        entries = result.scalars().all()
        
        deleted = 0
        for entry in entries:
            if entry.window_end < cutoff:
                await session.delete(entry)
                deleted += 1
        
        if deleted > 0:
            await session.flush()
            logger.info(f"Cleaned up {deleted} expired rate limit entries")
        
        return deleted


def get_rate_limit_headers(
    limit: int,
    remaining: int,
    reset_timestamp: int,
) -> dict[str, str]:
    """
    Generate standard rate limit response headers.
    
    Args:
        limit: Maximum requests per window
        remaining: Remaining requests in current window (will be clamped to 0 if negative)
        reset_timestamp: Unix timestamp when window resets
    
    Returns:
        Dictionary of header name to value
    """
    return {
        "X-RateLimit-Limit": str(limit),
        "X-RateLimit-Remaining": str(max(0, remaining)),
        "X-RateLimit-Reset": str(reset_timestamp),
    }
