"""
Audit Log Entry Model

Immutable audit trail for security-sensitive operations.
Required for compliance (GDPR, CCPA) and security monitoring.

Privacy Design:
- NO raw IPs, user IDs, or personal data stored
- Only SHA-256 hashes for correlation (one-way)
- Cannot reconstruct user identity from logs
- Retained for 2 years (compliance), archived after 6 months
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from sqlalchemy import JSON, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class AuditAction(str, Enum):
    """Types of auditable security events."""
    
    PLAYER_CREATED = "player_created"
    PLAYER_DELETED = "player_deleted"
    PHOTO_UPLOADED = "photo_uploaded"
    PHOTO_MODERATED = "photo_moderated"
    DATA_EXPORT = "data_export"
    RATE_LIMIT_TRIGGERED = "rate_limit_triggered"
    POW_FAILED = "pow_failed"
    ADMIN_ACTION = "admin_action"


class AuditActorType(str, Enum):
    """Types of actors performing auditable actions."""
    
    SYSTEM = "system"
    PLAYER = "player"
    ADMIN = "admin"
    ANONYMOUS = "anonymous"


class AuditLogEntry(Base):
    """
    Immutable audit trail entry.
    
    Important: Entries are APPEND-ONLY. Never update or delete
    audit log entries except through scheduled archival.
    """
    
    __tablename__ = "audit_log_entry"
    
    # Primary key (UUID)
    id: Mapped[uuid.UUID] = mapped_column(
        String(36),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Timestamp (set by database, immutable)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    
    # Type of action performed
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    
    # Type of actor performing the action
    actor_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    
    # SHA-256 hash of actor ID (never raw ID)
    actor_id_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    
    # Type of target entity (e.g., "photo", "player")
    target_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    
    # SHA-256 hash of target ID (never raw ID)
    target_id_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    
    # Additional context (must NOT contain PII)
    metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    
    # SHA-256 hash of client IP (never raw IP)
    ip_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    
    __table_args__ = (
        Index("ix_audit_timestamp", "timestamp"),
        Index("ix_audit_action_timestamp", "action", "timestamp"),
    )
    
    @classmethod
    def create(
        cls,
        action: AuditAction,
        actor_type: AuditActorType,
        actor_id_hash: str | None = None,
        target_type: str | None = None,
        target_id_hash: str | None = None,
        metadata: dict[str, Any] | None = None,
        ip_hash: str | None = None,
    ) -> "AuditLogEntry":
        """
        Create a new audit log entry.
        
        Important: All IDs should be pre-hashed using SHA-256.
        Never pass raw IDs or personal data.
        
        Args:
            action: Type of action being logged
            actor_type: Type of actor performing action
            actor_id_hash: SHA-256 hash of actor ID (optional)
            target_type: Type of target entity (optional)
            target_id_hash: SHA-256 hash of target ID (optional)
            metadata: Additional context (must not contain PII)
            ip_hash: SHA-256 hash of client IP (optional)
        
        Returns:
            New AuditLogEntry instance (not yet persisted)
        """
        return cls(
            id=uuid.uuid4(),
            timestamp=datetime.now(timezone.utc),
            action=action.value,
            actor_type=actor_type.value,
            actor_id_hash=actor_id_hash,
            target_type=target_type,
            target_id_hash=target_id_hash,
            metadata=metadata,
            ip_hash=ip_hash,
        )


def create_audit_entry(
    action: AuditAction,
    actor_type: AuditActorType = AuditActorType.SYSTEM,
    **kwargs: Any,
) -> AuditLogEntry:
    """
    Convenience function to create audit entries.
    
    Example:
        entry = create_audit_entry(
            AuditAction.PLAYER_CREATED,
            AuditActorType.ANONYMOUS,
            target_type="player",
            target_id_hash=hash_id(player_id),
            ip_hash=hash_ip(client_ip),
        )
    """
    return AuditLogEntry.create(action, actor_type, **kwargs)
