"""
Models Package

SQLAlchemy model definitions for all database entities.

Security Models:
- ProofOfWorkChallenge: Bot prevention challenges
- RateLimitEntry: Rate limiting tracking
- AuditLogEntry: Security audit trail

Domain Models:
- Player: User accounts with minimal identity
- Photo: Aircraft photos for guessing games
- GameRound: Individual guessing rounds
- Guess: Individual guesses within rounds
"""

from src.models.audit_log import AuditAction, AuditActorType, AuditLogEntry
from src.models.base import Base, TimestampMixin, UUIDMixin
from src.models.game_round import GameRound, RoundStatus
from src.models.guess import Guess
from src.models.photo import Photo, PhotoStatus
from src.models.player import Player
from src.models.pow_challenge import ProofOfWorkChallenge
from src.models.rate_limit import RATE_LIMITS, RateLimitEntry, get_rate_limit

__all__ = [
    # Base
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    # Security
    "ProofOfWorkChallenge",
    "RateLimitEntry",
    "RATE_LIMITS",
    "get_rate_limit",
    "AuditLogEntry",
    "AuditAction",
    "AuditActorType",
    # Domain
    "Player",
    "Photo",
    "PhotoStatus",
    "GameRound",
    "RoundStatus",
    "Guess",
]
