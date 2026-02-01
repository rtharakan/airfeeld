"""
Proof of Work Service

Manages cryptographic challenges for bot prevention during account creation.
Implements SHA-256 hash-based proof-of-work with configurable difficulty.

Security Design:
- Challenges are single-use and time-limited (5 minutes)
- IP addresses are hashed before storage (SHA-256)
- Failed attempts are logged for security monitoring
- Supports reduced difficulty for accessibility
"""

import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.models.audit_log import AuditAction, AuditActorType, AuditLogEntry
from src.models.pow_challenge import ProofOfWorkChallenge, hash_ip
from src.utils.errors import ChallengeExpiredError, ProofOfWorkError, RateLimitError
from src.utils.logging import get_logger, log_security_event

logger = get_logger(__name__)


class ProofOfWorkService:
    """
    Service for managing proof-of-work challenges.
    
    The proof-of-work system prevents automated bot registration by
    requiring clients to solve a computational challenge before
    creating an account. This is privacy-friendly as it doesn't
    require CAPTCHAs or third-party services.
    """
    
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
    
    async def create_challenge(
        self,
        session: AsyncSession,
        client_ip: str,
        low_power: bool = False,
    ) -> ProofOfWorkChallenge:
        """
        Create a new proof-of-work challenge.
        
        Args:
            session: Database session
            client_ip: Client IP address (will be hashed)
            low_power: If True, use reduced difficulty for accessibility
        
        Returns:
            New ProofOfWorkChallenge instance
        
        Raises:
            RateLimitError: If too many challenges requested from this IP
        """
        ip_hash = hash_ip(client_ip)
        
        # Check rate limit: max 10 challenges per IP per 15 minutes
        await self._check_challenge_rate_limit(session, ip_hash)
        
        # Determine difficulty based on device capability
        if low_power:
            difficulty = self.settings.pow_low_power_difficulty
            ttl = self.settings.pow_low_power_timeout_seconds
        else:
            difficulty = self.settings.pow_difficulty
            ttl = self.settings.pow_timeout_seconds
        
        # Create challenge
        challenge = ProofOfWorkChallenge.create(
            client_ip=client_ip,
            difficulty=difficulty,
            ttl_seconds=ttl,
        )
        
        session.add(challenge)
        await session.flush()
        
        logger.info(
            f"Created PoW challenge: id={challenge.id}, "
            f"difficulty={difficulty}, ttl={ttl}s"
        )
        
        return challenge
    
    async def verify_solution(
        self,
        session: AsyncSession,
        challenge_id: uuid.UUID,
        solution_nonce: str,
        client_ip: str,
    ) -> bool:
        """
        Verify a proof-of-work solution.
        
        Args:
            session: Database session
            challenge_id: UUID of the challenge to verify
            solution_nonce: Client-provided solution nonce
            client_ip: Client IP address for logging
        
        Returns:
            True if solution is valid
        
        Raises:
            ProofOfWorkError: If challenge not found
            ChallengeExpiredError: If challenge has expired
            ProofOfWorkError: If solution is incorrect
        """
        ip_hash = hash_ip(client_ip)
        
        # Fetch challenge
        query = select(ProofOfWorkChallenge).where(
            ProofOfWorkChallenge.id == challenge_id
        )
        result = await session.execute(query)
        challenge = result.scalar_one_or_none()
        
        if challenge is None:
            log_security_event(
                "pow_failure",
                "Challenge not found",
                ip_hash=ip_hash,
                challenge_id=str(challenge_id),
            )
            raise ProofOfWorkError("Challenge not found")
        
        # Check if already solved
        if challenge.is_solved:
            log_security_event(
                "pow_failure",
                "Challenge already used",
                ip_hash=ip_hash,
                challenge_id=str(challenge_id),
            )
            raise ProofOfWorkError("Challenge has already been used")
        
        # Check expiration
        if challenge.is_expired:
            log_security_event(
                "pow_failure",
                "Challenge expired",
                ip_hash=ip_hash,
                challenge_id=str(challenge_id),
            )
            raise ChallengeExpiredError()
        
        # Verify IP matches (prevent challenge stealing)
        if challenge.client_ip_hash != ip_hash:
            log_security_event(
                "pow_failure",
                "IP mismatch",
                ip_hash=ip_hash,
                challenge_id=str(challenge_id),
            )
            raise ProofOfWorkError("IP mismatch - challenge must be solved from the same IP")
        
        # Verify solution
        if not challenge.verify_solution(solution_nonce):
            log_security_event(
                "pow_failure",
                "Invalid solution",
                ip_hash=ip_hash,
                challenge_id=str(challenge_id),
            )
            
            # Log failed attempt for audit
            audit_entry = AuditLogEntry.create(
                action=AuditAction.POW_FAILED,
                actor_type=AuditActorType.ANONYMOUS,
                ip_hash=ip_hash,
                context_data={"challenge_id": str(challenge_id)},
            )
            session.add(audit_entry)
            
            raise ProofOfWorkError("Invalid proof-of-work solution")
        
        # Mark as solved
        challenge.mark_solved(solution_nonce)
        await session.flush()
        
        logger.info(f"PoW challenge verified: id={challenge_id}")
        return True
    
    async def get_challenge(
        self,
        session: AsyncSession,
        challenge_id: uuid.UUID,
    ) -> ProofOfWorkChallenge | None:
        """
        Get a challenge by ID.
        
        Args:
            session: Database session
            challenge_id: UUID of the challenge
        
        Returns:
            Challenge if found, None otherwise
        """
        query = select(ProofOfWorkChallenge).where(
            ProofOfWorkChallenge.id == challenge_id
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def cleanup_expired(self, session: AsyncSession) -> int:
        """
        Remove expired challenges older than 24 hours.
        
        Args:
            session: Database session
        
        Returns:
            Number of challenges deleted
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        
        query = delete(ProofOfWorkChallenge).where(
            ProofOfWorkChallenge.expires_at < cutoff
        )
        result = await session.execute(query)
        deleted = result.rowcount
        
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} expired PoW challenges")
        
        return deleted
    
    async def _check_challenge_rate_limit(
        self,
        session: AsyncSession,
        ip_hash: str,
    ) -> None:
        """
        Check if IP has exceeded challenge creation rate limit.
        
        Limit: 10 challenges per IP per 15 minutes
        """
        window_start = datetime.now(timezone.utc) - timedelta(minutes=15)
        
        query = select(func.count()).select_from(ProofOfWorkChallenge).where(
            ProofOfWorkChallenge.client_ip_hash == ip_hash,
            ProofOfWorkChallenge.created_at >= window_start,
        )
        result = await session.execute(query)
        count = result.scalar() or 0
        
        if count >= 10:
            log_security_event(
                "rate_limit",
                "Too many PoW challenge requests",
                ip_hash=ip_hash,
                count=count,
            )
            raise RateLimitError(
                retry_after_seconds=900,  # 15 minutes
                limit=10,
                window_seconds=900,
            )


def verify_pow_hash(
    challenge_nonce: str,
    solution_nonce: str,
    difficulty: int,
) -> bool:
    """
    Verify a proof-of-work hash solution.
    
    This is a standalone function for testing and validation.
    
    Args:
        challenge_nonce: Server-provided challenge nonce
        solution_nonce: Client-provided solution nonce
        difficulty: Required leading zeros
    
    Returns:
        True if valid, False otherwise
    """
    data = (challenge_nonce + solution_nonce).encode("utf-8")
    hash_result = hashlib.sha256(data).hexdigest()
    target = "0" * difficulty
    return hash_result.startswith(target)
