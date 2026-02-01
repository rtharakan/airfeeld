"""Create security tables

Revision ID: 001_security_tables
Revises: 
Create Date: 2024-01-01 00:00:00.000000

Initial migration creating core security infrastructure tables:
- proof_of_work_challenges: Bot prevention challenges
- rate_limit_entries: Rate limiting tracking
- audit_log_entries: Security event logging
- players: User accounts
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001_security_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create security infrastructure tables."""
    
    # Proof of Work Challenges
    op.create_table(
        "proof_of_work_challenges",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("challenge_nonce", sa.String(64), nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=False),
        sa.Column("ip_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("solved", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("solved_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_pow_challenges_ip_hash",
        "proof_of_work_challenges",
        ["ip_hash"],
    )
    op.create_index(
        "ix_pow_challenges_expires_at",
        "proof_of_work_challenges",
        ["expires_at"],
    )
    
    # Rate Limit Entries
    op.create_table(
        "rate_limit_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip_hash", sa.String(64), nullable=False),
        sa.Column("endpoint", sa.String(128), nullable=False),
        sa.Column("request_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ip_hash", "endpoint", name="uq_rate_limit_ip_endpoint"),
    )
    op.create_index(
        "ix_rate_limit_window_end",
        "rate_limit_entries",
        ["window_end"],
    )
    
    # Audit Log Entries
    op.create_table(
        "audit_log_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("actor_type", sa.String(32), nullable=False),
        sa.Column("actor_id_hash", sa.String(64), nullable=True),
        sa.Column("ip_hash", sa.String(64), nullable=True),
        sa.Column("resource_type", sa.String(64), nullable=True),
        sa.Column("resource_id_hash", sa.String(64), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_audit_log_action",
        "audit_log_entries",
        ["action"],
    )
    op.create_index(
        "ix_audit_log_created_at",
        "audit_log_entries",
        ["created_at"],
    )
    op.create_index(
        "ix_audit_log_actor_id_hash",
        "audit_log_entries",
        ["actor_id_hash"],
    )
    
    # Players
    op.create_table(
        "players",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("username", sa.String(24), nullable=False),
        sa.Column("games_played", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_active", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_players_username",
        "players",
        ["username"],
        unique=True,
    )


def downgrade() -> None:
    """Drop security infrastructure tables."""
    op.drop_table("players")
    op.drop_table("audit_log_entries")
    op.drop_table("rate_limit_entries")
    op.drop_table("proof_of_work_challenges")
