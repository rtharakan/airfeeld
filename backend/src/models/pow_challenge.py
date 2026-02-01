"""
Proof of Work Challenge Model

Stores cryptographic challenges issued during account registration.
Used to prevent automated bot registration without storing user identity.

Security Design:
- Challenges expire after 5 minutes
- Client IP is stored as SHA-256 hash (never raw)
- Solved challenges are cleaned up after 24 hours
- No link to player identity after verification
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, UUIDMixin


class ProofOfWorkChallenge(Base, UUIDMixin):
    """
    Represents a proof-of-work challenge for account creation.
    
    The client must find a nonce such that:
    SHA256(challenge_nonce + solution_nonce) starts with `difficulty` zeros
    
    This prevents automated account creation while remaining accessible
    to legitimate users on various devices.
    """
    
    __tablename__ = "proof_of_work_challenge"
    
    # Server-generated random nonce (32 hex characters)
    challenge_nonce: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    
    # Required leading zeros in hash solution
    difficulty: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=4,
    )
    
    # Client-provided solution (set when solved)
    solved_nonce: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    
    # Timestamp when solved
    solved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Challenge expiration (5 minutes from creation)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    
    # Creation timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    
    # SHA-256 hash of client IP (never store raw IP)
    client_ip_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    
    __table_args__ = (
        Index("ix_pow_expires", "expires_at"),
        Index("ix_pow_ip_created", "client_ip_hash", "created_at"),
    )
    
    @classmethod
    def create(
        cls,
        client_ip: str,
        difficulty: int = 4,
        ttl_seconds: int = 300,  # 5 minutes
    ) -> "ProofOfWorkChallenge":
        """
        Create a new proof-of-work challenge.
        
        Args:
            client_ip: Client IP address (will be hashed)
            difficulty: Number of leading zeros required (default: 4)
            ttl_seconds: Challenge validity period (default: 5 minutes)
        
        Returns:
            New ProofOfWorkChallenge instance (not yet persisted)
        """
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid.uuid4(),
            challenge_nonce=secrets.token_hex(16),  # 32 hex chars
            difficulty=difficulty,
            expires_at=now + timedelta(seconds=ttl_seconds),
            created_at=now,
            client_ip_hash=hash_ip(client_ip),
        )
    
    @property
    def is_expired(self) -> bool:
        """Check if challenge has expired."""
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def is_solved(self) -> bool:
        """Check if challenge has been solved."""
        return self.solved_nonce is not None
    
    def verify_solution(self, solution_nonce: str) -> bool:
        """
        Verify a proposed solution to the challenge.
        
        Args:
            solution_nonce: Client-provided nonce to verify
        
        Returns:
            True if solution is valid, False otherwise
        """
        if self.is_expired:
            return False
        
        # Compute hash of challenge_nonce + solution_nonce
        data = (self.challenge_nonce + solution_nonce).encode("utf-8")
        hash_result = hashlib.sha256(data).hexdigest()
        
        # Check if hash starts with required zeros
        target = "0" * self.difficulty
        return hash_result.startswith(target)
    
    def mark_solved(self, solution_nonce: str) -> None:
        """Mark challenge as solved with the provided nonce."""
        self.solved_nonce = solution_nonce
        self.solved_at = datetime.now(timezone.utc)


def hash_ip(ip_address: str) -> str:
    """
    Hash an IP address using SHA-256.
    
    This provides one-way transformation for rate limiting
    without storing raw IP addresses (privacy requirement).
    
    Args:
        ip_address: Raw IP address string
    
    Returns:
        64-character hex string (SHA-256 hash)
    """
    return hashlib.sha256(ip_address.encode("utf-8")).hexdigest()
