"""Add moderation and attribution fields

Revision ID: 003_add_moderation_fields
Revises: 002_game_tables
Create Date: 2026-02-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_add_moderation_fields'
down_revision = '002_game_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add moderation fields to photos table
    with op.batch_alter_table('photos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('moderation_status', sa.String(16), nullable=True))
        batch_op.add_column(sa.Column('moderation_score', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('moderation_checked_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('rejection_reason', sa.String(512), nullable=True))
        
        # Add attribution fields
        batch_op.add_column(sa.Column('attribution_author', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('attribution_source', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('attribution_url', sa.String(512), nullable=True))
        batch_op.add_column(sa.Column('attribution_license', sa.String(100), nullable=True))
        
        # Add EXIF stripped flag
        batch_op.add_column(sa.Column('exif_stripped', sa.Boolean(), nullable=True, default=True))
        
        # Add verification status if not exists
        batch_op.add_column(sa.Column('verification_status', sa.String(16), nullable=True))
        
        # Add file path if not exists
        batch_op.add_column(sa.Column('file_path', sa.String(512), nullable=True))
        
        # Add uploaded_at if not exists  
        batch_op.add_column(sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=True))
        
        # Add airport_id foreign key reference
        batch_op.add_column(sa.Column('airport_id', sa.Integer(), nullable=True))
        
        # Create indexes for performance
        batch_op.create_index('idx_photo_moderation_status', ['moderation_status'])
        batch_op.create_index('idx_photo_verification_status', ['verification_status'])
    
    # Set default values for existing records
    op.execute("UPDATE photos SET moderation_status = 'approved' WHERE moderation_status IS NULL")
    op.execute("UPDATE photos SET verification_status = 'approved' WHERE verification_status IS NULL")
    op.execute("UPDATE photos SET exif_stripped = 1 WHERE exif_stripped IS NULL")
    
    # Add indexes to players table for leaderboard performance
    with op.batch_alter_table('players', schema=None) as batch_op:
        batch_op.create_index('idx_player_total_score', ['total_score'])
        batch_op.create_index('idx_player_username', ['username'])
    
    # Add indexes to game_rounds table
    with op.batch_alter_table('game_rounds', schema=None) as batch_op:
        batch_op.create_index('idx_gameround_player_id', ['player_id'])
        batch_op.create_index('idx_gameround_status', ['status'])


def downgrade() -> None:
    # Remove indexes from game_rounds
    with op.batch_alter_table('game_rounds', schema=None) as batch_op:
        batch_op.drop_index('idx_gameround_status')
        batch_op.drop_index('idx_gameround_player_id')
    
    # Remove indexes from players
    with op.batch_alter_table('players', schema=None) as batch_op:
        batch_op.drop_index('idx_player_username')
        batch_op.drop_index('idx_player_total_score')
    
    # Remove indexes and columns from photos
    with op.batch_alter_table('photos', schema=None) as batch_op:
        batch_op.drop_index('idx_photo_verification_status')
        batch_op.drop_index('idx_photo_moderation_status')
        
        batch_op.drop_column('airport_id')
        batch_op.drop_column('uploaded_at')
        batch_op.drop_column('file_path')
        batch_op.drop_column('verification_status')
        batch_op.drop_column('exif_stripped')
        batch_op.drop_column('attribution_license')
        batch_op.drop_column('attribution_url')
        batch_op.drop_column('attribution_source')
        batch_op.drop_column('attribution_author')
        batch_op.drop_column('rejection_reason')
        batch_op.drop_column('moderation_checked_at')
        batch_op.drop_column('moderation_score')
        batch_op.drop_column('moderation_status')
