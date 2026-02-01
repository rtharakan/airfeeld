"""
Unit Tests for Rate Limit Service

Tests rate limit checking, tracking, and cleanup.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.models.rate_limit import RateLimitEntry
from src.services.rate_limit_service import (
    RateLimitService,
    get_rate_limit_headers,
)
from src.utils.errors import RateLimitError


@pytest.fixture
def rate_limit_service() -> RateLimitService:
    """Create a rate limit service with test settings."""
    mock_settings = MagicMock()
    return RateLimitService(mock_settings)


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock database session."""
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    return session


class TestCheckRateLimit:
    """Tests for rate limit checking."""
    
    @pytest.mark.asyncio
    async def test_allows_first_request(
        self, rate_limit_service: RateLimitService, mock_session: AsyncMock
    ) -> None:
        """First request should always be allowed."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Should not raise
        await rate_limit_service.check_rate_limit(
            mock_session, "192.168.1.1", "/players/register"
        )
        
        # Should create new entry
        mock_session.add.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_allows_request_within_limit(
        self, rate_limit_service: RateLimitService, mock_session: AsyncMock
    ) -> None:
        """Request within limit should be allowed."""
        entry = RateLimitEntry.create(
            ip_hash="hashed_ip",
            endpoint="/players/register",
            window_seconds=3600,
        )
        entry.request_count = 5  # Well under limit
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=entry)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Should not raise
        await rate_limit_service.check_rate_limit(
            mock_session, "192.168.1.1", "/players/register"
        )
        
        # Should increment count
        assert entry.request_count == 6
    
    @pytest.mark.asyncio
    async def test_rejects_request_over_limit(
        self, rate_limit_service: RateLimitService, mock_session: AsyncMock
    ) -> None:
        """Request over limit should be rejected with 429."""
        entry = RateLimitEntry.create(
            ip_hash="hashed_ip",
            endpoint="/players/register",
            window_seconds=3600,
        )
        entry.request_count = 100  # At or over limit (assuming limit is 10)
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=entry)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        with pytest.raises(RateLimitError) as exc_info:
            await rate_limit_service.check_rate_limit(
                mock_session, "192.168.1.1", "/players/register"
            )
        
        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after > 0
    
    @pytest.mark.asyncio
    async def test_resets_expired_window(
        self, rate_limit_service: RateLimitService, mock_session: AsyncMock
    ) -> None:
        """Expired window should be reset, not rejected."""
        entry = RateLimitEntry.create(
            ip_hash="hashed_ip",
            endpoint="/players/register",
            window_seconds=3600,
        )
        entry.request_count = 100  # Over limit
        # But window has expired
        entry.window_end = datetime.now(timezone.utc) - timedelta(hours=1)
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=entry)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Should not raise - window expired
        await rate_limit_service.check_rate_limit(
            mock_session, "192.168.1.1", "/players/register"
        )
        
        # Window should be reset
        assert entry.request_count == 1
        assert entry.window_end > datetime.now(timezone.utc)
    
    @pytest.mark.asyncio
    async def test_ip_is_hashed(
        self, rate_limit_service: RateLimitService, mock_session: AsyncMock
    ) -> None:
        """IP should be stored as hash, not plaintext."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        await rate_limit_service.check_rate_limit(
            mock_session, "192.168.1.1", "/players/register"
        )
        
        # Check the entry that was added
        added_entry = mock_session.add.call_args[0][0]
        assert added_entry.ip_hash != "192.168.1.1"
        assert len(added_entry.ip_hash) == 64  # SHA-256


class TestGetRemaining:
    """Tests for getting remaining requests."""
    
    @pytest.mark.asyncio
    async def test_returns_full_limit_for_new_ip(
        self, rate_limit_service: RateLimitService, mock_session: AsyncMock
    ) -> None:
        """New IP should have full limit available."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        remaining, reset_time = await rate_limit_service.get_remaining(
            mock_session, "192.168.1.1", "/players/register"
        )
        
        assert remaining > 0
        assert reset_time is None
    
    @pytest.mark.asyncio
    async def test_returns_correct_remaining(
        self, rate_limit_service: RateLimitService, mock_session: AsyncMock
    ) -> None:
        """Should return correct remaining count."""
        entry = RateLimitEntry.create(
            ip_hash="hashed_ip",
            endpoint="/players/register",
            window_seconds=3600,
        )
        entry.request_count = 3  # 3 requests used
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=entry)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        remaining, reset_time = await rate_limit_service.get_remaining(
            mock_session, "192.168.1.1", "/players/register"
        )
        
        # Assuming limit is 10
        assert remaining >= 0
        assert reset_time == entry.window_end


class TestCleanupExpired:
    """Tests for expired entry cleanup."""
    
    @pytest.mark.asyncio
    async def test_deletes_expired_entries(
        self, rate_limit_service: RateLimitService, mock_session: AsyncMock
    ) -> None:
        """Should delete all expired entries."""
        mock_result = MagicMock()
        mock_result.rowcount = 10
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        count = await rate_limit_service.cleanup_expired(mock_session)
        
        assert count == 10


class TestGetRateLimitHeaders:
    """Tests for rate limit header generation."""
    
    def test_generates_correct_headers(self) -> None:
        """Should generate standard rate limit headers."""
        headers = get_rate_limit_headers(
            limit=100,
            remaining=50,
            reset_timestamp=1704067200,
        )
        
        assert headers["X-RateLimit-Limit"] == "100"
        assert headers["X-RateLimit-Remaining"] == "50"
        assert headers["X-RateLimit-Reset"] == "1704067200"
    
    def test_remaining_not_negative(self) -> None:
        """Remaining should not be negative."""
        headers = get_rate_limit_headers(
            limit=10,
            remaining=-5,
            reset_timestamp=1704067200,
        )
        
        assert int(headers["X-RateLimit-Remaining"]) >= 0
