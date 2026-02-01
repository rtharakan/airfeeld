"""
Audit Service

Records security-sensitive events for compliance and monitoring.
All entries use hashed identifiers for privacy.

Compliance:
- GDPR Article 30: Records of processing activities
- Retained for 2 years
- Archived to cold storage after 6 months
"""

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.audit_log import AuditAction, AuditActorType, AuditLogEntry
from src.utils.logging import get_logger

logger = get_logger(__name__)


class AuditService:
    """
    Service for recording and querying audit log entries.
    
    Important: Audit entries are APPEND-ONLY. They should never
    be modified or deleted except through scheduled archival.
    """
    
    async def log_event(
        self,
        session: AsyncSession,
        action: AuditAction,
        actor_type: AuditActorType = AuditActorType.SYSTEM,
        actor_id: str | uuid.UUID | None = None,
        target_type: str | None = None,
        target_id: str | uuid.UUID | None = None,
        client_ip: str | None = None,
        context_data: dict[str, Any] | None = None,
    ) -> AuditLogEntry:
        """
        Record a security-sensitive event.
        
        All IDs are automatically hashed before storage.
        Never pass raw personal data in context_data.
        
        Args:
            session: Database session
            action: Type of action being logged
            actor_type: Type of actor performing action
            actor_id: ID of actor (will be hashed)
            target_type: Type of target entity
            target_id: ID of target (will be hashed)
            client_ip: Client IP address (will be hashed)
            context_data: Additional context (must not contain PII)
        
        Returns:
            Created audit log entry
        """
        entry = AuditLogEntry.create(
            action=action,
            actor_type=actor_type,
            actor_id_hash=hash_id(actor_id) if actor_id else None,
            target_type=target_type,
            target_id_hash=hash_id(target_id) if target_id else None,
            ip_hash=hash_ip(client_ip) if client_ip else None,
            context_data=context_data,
        )
        
        session.add(entry)
        await session.flush()
        
        logger.debug(
            f"Audit: {action.value} by {actor_type.value} "
            f"on {target_type or 'N/A'}"
        )
        
        return entry
    
    async def log_player_created(
        self,
        session: AsyncSession,
        player_id: uuid.UUID,
        client_ip: str | None = None,
    ) -> AuditLogEntry:
        """Log player account creation."""
        return await self.log_event(
            session=session,
            action=AuditAction.PLAYER_CREATED,
            actor_type=AuditActorType.ANONYMOUS,
            target_type="player",
            target_id=player_id,
            client_ip=client_ip,
        )
    
    async def log_player_deleted(
        self,
        session: AsyncSession,
        player_id: uuid.UUID,
        client_ip: str | None = None,
    ) -> AuditLogEntry:
        """Log player account deletion (GDPR right to erasure)."""
        return await self.log_event(
            session=session,
            action=AuditAction.PLAYER_DELETED,
            actor_type=AuditActorType.PLAYER,
            actor_id=player_id,
            target_type="player",
            target_id=player_id,
            client_ip=client_ip,
        )
    
    async def log_data_export(
        self,
        session: AsyncSession,
        player_id: uuid.UUID,
        client_ip: str | None = None,
    ) -> AuditLogEntry:
        """Log data export request (GDPR data portability)."""
        return await self.log_event(
            session=session,
            action=AuditAction.DATA_EXPORT,
            actor_type=AuditActorType.PLAYER,
            actor_id=player_id,
            target_type="player",
            target_id=player_id,
            client_ip=client_ip,
        )
    
    async def log_photo_uploaded(
        self,
        session: AsyncSession,
        photo_id: uuid.UUID,
        uploader_id: uuid.UUID | None = None,
        client_ip: str | None = None,
    ) -> AuditLogEntry:
        """Log photo upload."""
        return await self.log_event(
            session=session,
            action=AuditAction.PHOTO_UPLOADED,
            actor_type=AuditActorType.PLAYER if uploader_id else AuditActorType.ANONYMOUS,
            actor_id=uploader_id,
            target_type="photo",
            target_id=photo_id,
            client_ip=client_ip,
        )
    
    async def log_photo_moderated(
        self,
        session: AsyncSession,
        photo_id: uuid.UUID,
        decision: str,
        moderator_id: uuid.UUID | None = None,
    ) -> AuditLogEntry:
        """Log photo moderation decision."""
        return await self.log_event(
            session=session,
            action=AuditAction.PHOTO_MODERATED,
            actor_type=AuditActorType.ADMIN if moderator_id else AuditActorType.SYSTEM,
            actor_id=moderator_id,
            target_type="photo",
            target_id=photo_id,
            context_data={"decision": decision},
        )
    
    async def get_recent_events(
        self,
        session: AsyncSession,
        action: AuditAction | None = None,
        hours: int = 24,
        limit: int = 100,
    ) -> list[AuditLogEntry]:
        """
        Get recent audit events for monitoring.
        
        Args:
            session: Database session
            action: Filter by action type (optional)
            hours: Time window in hours
            limit: Maximum entries to return
        
        Returns:
            List of audit entries (newest first)
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        query = select(AuditLogEntry).where(
            AuditLogEntry.timestamp >= cutoff
        )
        
        if action:
            query = query.where(AuditLogEntry.action == action.value)
        
        query = query.order_by(AuditLogEntry.timestamp.desc()).limit(limit)
        
        result = await session.execute(query)
        return list(result.scalars().all())
    
    async def archive_old_entries(
        self,
        session: AsyncSession,
        older_than_days: int = 180,
    ) -> int:
        """
        Archive entries older than specified days.
        
        In production, this should move entries to cold storage
        rather than deleting them (2-year retention requirement).
        
        Args:
            session: Database session
            older_than_days: Archive entries older than this
        
        Returns:
            Number of entries archived
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
        
        # In production: INSERT INTO audit_log_archive SELECT * FROM audit_log WHERE ...
        # For now, just count what would be archived
        query = select(AuditLogEntry).where(AuditLogEntry.timestamp < cutoff)
        result = await session.execute(query)
        entries = list(result.scalars().all())
        
        # TODO: Implement actual archival to cold storage
        logger.info(f"Would archive {len(entries)} audit entries older than {older_than_days} days")
        
        return len(entries)


def hash_id(value: str | uuid.UUID | None) -> str | None:
    """
    Hash an identifier using SHA-256.
    
    Args:
        value: ID to hash (string or UUID)
    
    Returns:
        64-character hex string, or None if input is None
    """
    if value is None:
        return None
    
    if isinstance(value, uuid.UUID):
        value = str(value)
    
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_ip(ip_address: str | None) -> str | None:
    """
    Hash an IP address using SHA-256.
    
    Args:
        ip_address: Raw IP address string
    
    Returns:
        64-character hex string, or None if input is None
    """
    if ip_address is None:
        return None
    
    return hashlib.sha256(ip_address.encode("utf-8")).hexdigest()
