"""
Player Service

Manages player account creation, lookup, and GDPR compliance.
Implements proof-of-work verification for bot prevention.

Security Features:
- Proof-of-work required for account creation
- Rate limiting per IP address
- Profanity filtering for usernames
- GDPR data export and deletion
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.models.audit_log import AuditAction, AuditActorType
from src.models.player import Player
from src.services.audit_service import AuditService
from src.services.pow_service import ProofOfWorkService
from src.services.profanity_filter import contains_profanity
from src.services.rate_limit_service import RateLimitService
from src.utils.errors import (
    NotFoundError,
    ProfanityError,
    UsernameConflictError,
    UsernameValidationError,
)
from src.utils.logging import get_logger

logger = get_logger(__name__)


class PlayerService:
    """
    Service for player account management.
    
    Handles:
    - Account creation with PoW verification
    - Username validation and profanity filtering
    - GDPR compliance (export, deletion)
    - Player lookup and statistics
    """
    
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.pow_service = ProofOfWorkService(settings)
        self.rate_limit_service = RateLimitService(settings)
        self.audit_service = AuditService()
    
    async def create_player(
        self,
        session: AsyncSession,
        username: str,
        challenge_id: uuid.UUID,
        solution_nonce: str,
        client_ip: str,
    ) -> Player:
        """
        Create a new player account.
        
        Requires valid proof-of-work solution for bot prevention.
        
        Args:
            session: Database session
            username: Desired username
            challenge_id: PoW challenge ID
            solution_nonce: PoW solution
            client_ip: Client IP for rate limiting and logging
        
        Returns:
            Created Player instance
        
        Raises:
            RateLimitError: If too many accounts from this IP
            ProofOfWorkError: If PoW verification fails
            UsernameValidationError: If username format invalid
            ProfanityError: If username contains inappropriate content
            UsernameConflictError: If username already taken
        """
        # Check rate limit first
        await self.rate_limit_service.check_rate_limit(
            session, client_ip, "/players/register"
        )
        
        # Verify proof-of-work
        await self.pow_service.verify_solution(
            session, challenge_id, solution_nonce, client_ip
        )
        
        # Validate username format
        if not Player.validate_username(username):
            raise UsernameValidationError()
        
        # Check for profanity
        if contains_profanity(username):
            raise ProfanityError()
        
        # Check username uniqueness (case-insensitive)
        existing = await self.get_by_username(session, username)
        if existing:
            raise UsernameConflictError()
        
        # Create player
        player = Player.create(username=username)
        session.add(player)
        await session.flush()
        
        # Audit log
        await self.audit_service.log_player_created(
            session, player.id, client_ip
        )
        
        logger.info(f"Created player: id={player.id}, username={username}")
        
        return player
    
    async def get_by_id(
        self,
        session: AsyncSession,
        player_id: uuid.UUID,
    ) -> Player | None:
        """
        Get player by ID.
        
        Args:
            session: Database session
            player_id: Player UUID
        
        Returns:
            Player if found, None otherwise
        """
        query = select(Player).where(Player.id == player_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_username(
        self,
        session: AsyncSession,
        username: str,
    ) -> Player | None:
        """
        Get player by username (case-insensitive).
        
        Args:
            session: Database session
            username: Username to search
        
        Returns:
            Player if found, None otherwise
        """
        # SQLite LIKE is case-insensitive by default for ASCII
        query = select(Player).where(
            func.lower(Player.username) == func.lower(username)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def delete_player(
        self,
        session: AsyncSession,
        player_id: uuid.UUID,
        client_ip: str | None = None,
    ) -> bool:
        """
        Delete player account and all associated data.
        
        GDPR Article 17: Right to erasure.
        Must complete within 72 hours of request.
        
        Args:
            session: Database session
            player_id: Player UUID to delete
            client_ip: Client IP for audit logging
        
        Returns:
            True if deleted, False if not found
        """
        player = await self.get_by_id(session, player_id)
        if not player:
            return False
        
        # Delete associated data
        # TODO: Delete game rounds, guesses, uploaded photos
        
        # Audit log before deletion
        await self.audit_service.log_player_deleted(
            session, player_id, client_ip
        )
        
        # Delete player
        await session.delete(player)
        await session.flush()
        
        logger.info(f"Deleted player: id={player_id}")
        
        return True
    
    async def export_player_data(
        self,
        session: AsyncSession,
        player_id: uuid.UUID,
        client_ip: str | None = None,
    ) -> dict:
        """
        Export all player data for GDPR compliance.
        
        GDPR Article 20: Right to data portability.
        Must provide within 30 days of request.
        
        Args:
            session: Database session
            player_id: Player UUID
            client_ip: Client IP for audit logging
        
        Returns:
            Dictionary containing all player data
        
        Raises:
            NotFoundError: If player not found
        """
        player = await self.get_by_id(session, player_id)
        if not player:
            raise NotFoundError("Player", str(player_id))
        
        # Audit log
        await self.audit_service.log_data_export(
            session, player_id, client_ip
        )
        
        # Build export data
        export = {
            "player_id": str(player.id),
            "username": player.username,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "data": {
                "profile": player.to_export_dict(),
                "game_history": [],  # TODO: Include game rounds
                "uploaded_photos": [],  # TODO: Include photo metadata
            },
        }
        
        logger.info(f"Exported data for player: id={player_id}")
        
        return export
    
    async def update_last_active(
        self,
        session: AsyncSession,
        player_id: uuid.UUID,
    ) -> None:
        """
        Update player's last active timestamp.
        
        Called after each game round completion.
        """
        player = await self.get_by_id(session, player_id)
        if player:
            player.last_active = datetime.now(timezone.utc)
            await session.flush()
    
    async def add_score(
        self,
        session: AsyncSession,
        player_id: uuid.UUID,
        points: int,
    ) -> None:
        """
        Add points to player's total score.
        
        Args:
            session: Database session
            player_id: Player UUID
            points: Points to add
        """
        player = await self.get_by_id(session, player_id)
        if player:
            player.add_score(points)
            await session.flush()
    
    async def get_stats(
        self,
        session: AsyncSession,
        player_id: uuid.UUID,
    ) -> dict | None:
        """
        Get player statistics.
        
        Args:
            session: Database session
            player_id: Player UUID
        
        Returns:
            Statistics dictionary or None if not found
        """
        player = await self.get_by_id(session, player_id)
        if not player:
            return None
        
        stats = player.to_public_dict()
        
        # Calculate average score
        if player.games_played > 0:
            stats["average_score"] = round(
                player.total_score / player.games_played, 2
            )
        else:
            stats["average_score"] = 0.0
        
        # TODO: Add rank from leaderboard
        stats["rank"] = None
        
        return stats
