"""Create game tables

Revision ID: 002_game_tables
Revises: 001_security_tables
Create Date: 2024-01-01 00:00:00.000000

Adds game-related tables:
- photos: Aircraft photos for guessing
- game_rounds: Individual game rounds
- guesses: Player guesses within rounds
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002_game_tables"
down_revision: Union[str, None] = "001_security_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create game tables."""
    
    # Photos
    op.create_table(
        "photos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("uploader_id", sa.Uuid(), nullable=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_hash", sa.String(64), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(32), nullable=False),
        sa.Column("perceptual_hash", sa.String(64), nullable=True),
        sa.Column("aircraft_type", sa.String(128), nullable=False),
        sa.Column("aircraft_registration", sa.String(32), nullable=True),
        sa.Column("airline", sa.String(128), nullable=True),
        sa.Column("airport_code", sa.String(4), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("moderation_notes", sa.String(512), nullable=True),
        sa.Column("moderated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("times_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_score_awarded", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["uploader_id"], ["players.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_photos_file_hash", "photos", ["file_hash"], unique=True)
    op.create_index("ix_photos_perceptual_hash", "photos", ["perceptual_hash"])
    op.create_index("ix_photos_status", "photos", ["status"])
    op.create_index("ix_photos_uploader_id", "photos", ["uploader_id"])
    
    # Game Rounds
    op.create_table(
        "game_rounds",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("player_id", sa.Uuid(), nullable=False),
        sa.Column("photo_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("guesses_made", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_guesses", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("final_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("aircraft_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("location_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("best_aircraft_guess", sa.String(128), nullable=True),
        sa.Column("best_location_lat", sa.Float(), nullable=True),
        sa.Column("best_location_lon", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["photo_id"], ["photos.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_game_rounds_player_id", "game_rounds", ["player_id"])
    op.create_index("ix_game_rounds_photo_id", "game_rounds", ["photo_id"])
    op.create_index("ix_game_rounds_status", "game_rounds", ["status"])
    
    # Guesses
    op.create_table(
        "guesses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("round_id", sa.Uuid(), nullable=False),
        sa.Column("guess_number", sa.Integer(), nullable=False),
        sa.Column("guessed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("aircraft_guess", sa.String(128), nullable=True),
        sa.Column("aircraft_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("location_lat", sa.Float(), nullable=True),
        sa.Column("location_lon", sa.Float(), nullable=True),
        sa.Column("location_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("distance_km", sa.Float(), nullable=True),
        sa.Column("total_score", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["round_id"], ["game_rounds.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_guesses_round_id", "guesses", ["round_id"])


def downgrade() -> None:
    """Drop game tables."""
    op.drop_table("guesses")
    op.drop_table("game_rounds")
    op.drop_table("photos")
