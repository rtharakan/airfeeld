"""
Unit Tests for Proof-of-Work Service

Tests challenge creation, verification, and cleanup.
"""

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.pow_challenge import ProofOfWorkChallenge
from src.services.pow_service import ProofOfWorkService
from src.utils.errors import ProofOfWorkError, ChallengeExpiredError


@pytest.fixture
def pow_service() -> ProofOfWorkService:
    """Create a PoW service with test settings."""
    mock_settings = MagicMock()
    mock_settings.pow_difficulty = 4
    mock_settings.pow_low_power_difficulty = 2
    mock_settings.pow_timeout_seconds = 10
    mock_settings.pow_low_power_timeout_seconds = 30
    mock_settings.pow_max_attempts_per_ip = 10
    return ProofOfWorkService(mock_settings)


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock database session."""
    session = AsyncMock()
    session.add = MagicMock()
    session.delete = AsyncMock()
    session.flush = AsyncMock()
    return session


class TestCreateChallenge:
    """Tests for challenge creation."""
    
    @pytest.mark.asyncio
    async def test_creates_challenge_with_correct_difficulty(
        self, pow_service: ProofOfWorkService, mock_session: AsyncMock
    ) -> None:
        """Challenge should have configured difficulty."""
        # Mock the rate limit check
        with patch.object(
            pow_service, "_check_challenge_rate_limit", return_value=None
        ):
            mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
            
            challenge = await pow_service.create_challenge(
                mock_session, "192.168.1.1", low_power=False
            )
        
        assert challenge.difficulty == 4
        mock_session.add.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_creates_challenge_with_reduced_difficulty(
        self, pow_service: ProofOfWorkService, mock_session: AsyncMock
    ) -> None:
        """Accessibility mode should use reduced difficulty."""
        with patch.object(
            pow_service, "_check_challenge_rate_limit", return_value=None
        ):
            mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
            
            challenge = await pow_service.create_challenge(
                mock_session, "192.168.1.1", low_power=True
            )
        
        assert challenge.difficulty == 2
    
    @pytest.mark.asyncio
    async def test_challenge_has_valid_nonce(
        self, pow_service: ProofOfWorkService, mock_session: AsyncMock
    ) -> None:
        """Challenge nonce should be valid hex string."""
        with patch.object(
            pow_service, "_check_challenge_rate_limit", return_value=None
        ):
            mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
            
            challenge = await pow_service.create_challenge(
                mock_session, "192.168.1.1"
            )
        
        assert len(challenge.challenge_nonce) == 32
        # Should be valid hex
        int(challenge.challenge_nonce, 16)
    
    @pytest.mark.asyncio
    async def test_challenge_expires_in_future(
        self, pow_service: ProofOfWorkService, mock_session: AsyncMock
    ) -> None:
        """Challenge should have future expiration."""
        with patch.object(
            pow_service, "_check_challenge_rate_limit", return_value=None
        ):
            mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
            
            challenge = await pow_service.create_challenge(
                mock_session, "192.168.1.1"
            )
        
        assert challenge.expires_at > datetime.now(timezone.utc)
    
    @pytest.mark.asyncio
    async def test_ip_is_hashed(
        self, pow_service: ProofOfWorkService, mock_session: AsyncMock
    ) -> None:
        """IP address should be stored as hash, not plaintext."""
        with patch.object(
            pow_service, "_check_challenge_rate_limit", return_value=None
        ):
            mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
            
            challenge = await pow_service.create_challenge(
                mock_session, "192.168.1.1"
            )
        
        # IP should not be stored as plaintext
        assert challenge.client_ip_hash != "192.168.1.1"
        # Should be SHA-256 hash (64 hex chars)
        assert len(challenge.client_ip_hash) == 64


class TestVerifySolution:
    """Tests for solution verification."""
    
    @pytest.mark.asyncio
    async def test_rejects_unknown_challenge(
        self, pow_service: ProofOfWorkService, mock_session: AsyncMock
    ) -> None:
        """Should reject solution for non-existent challenge."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        with pytest.raises(ProofOfWorkError, match="Challenge not found"):
            await pow_service.verify_solution(
                mock_session,
                uuid.uuid4(),
                "test_nonce",
                "192.168.1.1",
            )
    
    @pytest.mark.asyncio
    async def test_rejects_expired_challenge(
        self, pow_service: ProofOfWorkService, mock_session: AsyncMock
    ) -> None:
        """Should reject solution for expired challenge."""
        challenge = ProofOfWorkChallenge.create(
            client_ip="192.168.1.1",
            difficulty=4,
            ttl_seconds=300,
        )
        # Manually expire it
        challenge.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=challenge)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        with pytest.raises(ChallengeExpiredError):
            await pow_service.verify_solution(
                mock_session,
                challenge.id,
                "test_nonce",
                "192.168.1.1",
            )
    
    @pytest.mark.asyncio
    async def test_rejects_already_solved_challenge(
        self, pow_service: ProofOfWorkService, mock_session: AsyncMock
    ) -> None:
        """Should reject solution for already-solved challenge."""
        challenge = ProofOfWorkChallenge.create(
            client_ip="192.168.1.1",
            difficulty=4,
            ttl_seconds=300,
        )
        challenge.mark_solved("test_nonce")
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=challenge)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        with pytest.raises(ProofOfWorkError, match="already been used"):
            await pow_service.verify_solution(
                mock_session,
                challenge.id,
                "test_nonce",
                "192.168.1.1",
            )
    
    @pytest.mark.asyncio
    async def test_rejects_wrong_ip(
        self, pow_service: ProofOfWorkService, mock_session: AsyncMock
    ) -> None:
        """Should reject solution from different IP than challenge creator."""
        challenge = ProofOfWorkChallenge.create(
            client_ip="192.168.1.1",
            difficulty=4,
            ttl_seconds=300,
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=challenge)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        with pytest.raises(ProofOfWorkError, match="IP mismatch"):
            await pow_service.verify_solution(
                mock_session,
                challenge.id,
                "test_nonce",
                "10.0.0.1",  # Different IP
            )
    
    @pytest.mark.asyncio
    async def test_rejects_invalid_solution(
        self, pow_service: ProofOfWorkService, mock_session: AsyncMock
    ) -> None:
        """Should reject solution that doesn't meet difficulty."""
        challenge = ProofOfWorkChallenge.create(
            client_ip="192.168.1.1",
            difficulty=4,
            ttl_seconds=300,
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=challenge)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        with pytest.raises(ProofOfWorkError, match="Invalid proof-of-work solution"):
            await pow_service.verify_solution(
                mock_session,
                challenge.id,
                "wrong_nonce",
                "192.168.1.1",
            )
    
    @pytest.mark.asyncio
    async def test_accepts_valid_solution(
        self, pow_service: ProofOfWorkService, mock_session: AsyncMock
    ) -> None:
        """Should accept valid solution and mark challenge as solved."""
        challenge = ProofOfWorkChallenge.create(
            client_ip="192.168.1.1",
            difficulty=1,  # Low difficulty for test
            ttl_seconds=300,
        )
        
        # Find a valid solution
        solution_nonce = _find_valid_solution(challenge.challenge_nonce, 1)
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=challenge)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        result = await pow_service.verify_solution(
            mock_session,
            challenge.id,
            solution_nonce,
            "192.168.1.1",
        )
        
        assert result is True
        assert challenge.is_solved is True
        assert challenge.solved_at is not None


class TestCleanupExpired:
    """Tests for expired challenge cleanup."""
    
    @pytest.mark.asyncio
    async def test_deletes_expired_challenges(
        self, pow_service: ProofOfWorkService, mock_session: AsyncMock
    ) -> None:
        """Should delete all expired challenges."""
        mock_result = MagicMock()
        mock_result.rowcount = 5
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        count = await pow_service.cleanup_expired(mock_session)
        
        assert count == 5
        mock_session.execute.assert_called_once()


def _find_valid_solution(challenge_nonce: str, difficulty: int) -> str:
    """
    Find a valid PoW solution for testing.
    
    Brute-force search for a nonce that produces a hash
    with the required number of leading zeros.
    """
    prefix = "0" * difficulty
    nonce = 0
    
    while True:
        solution = str(nonce)
        combined = challenge_nonce + solution
        hash_result = hashlib.sha256(combined.encode()).hexdigest()
        
        if hash_result.startswith(prefix):
            return solution
        
        nonce += 1
        
        if nonce > 1000000:  # Safety limit
            raise RuntimeError("Could not find solution in reasonable time")
