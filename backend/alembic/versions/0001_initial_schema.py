"""Initial schema for rovers, telemetry, locations, and detections

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-11-03 17:35:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Rovers table
    op.create_table(
        'rovers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rover_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='idle'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rover_id')
    )
    op.create_index(op.f('ix_rovers_id'), 'rovers', ['id'], unique=False)
    op.create_index(op.f('ix_rovers_rover_id'), 'rovers', ['rover_id'], unique=True)

    # 2. Telemetry table
    op.create_table(
        'telemetry',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rover_id', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('battery', sa.Float(), nullable=False),
        sa.Column('speed', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('signal', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['rover_id'], ['rovers.rover_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_telemetry_id'), 'telemetry', ['id'], unique=False)
    op.create_index('ix_telemetry_rover_id_timestamp', 'telemetry', ['rover_id', 'timestamp'], unique=False)

    # 3. Locations table
    op.create_table(
        'locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rover_id', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['rover_id'], ['rovers.rover_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_locations_id'), 'locations', ['id'], unique=False)
    op.create_index('ix_locations_rover_id_timestamp', 'locations', ['rover_id', 'timestamp'], unique=False)

    # 4. Detections table
    op.create_table(
        'detections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rover_id', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('class_name', sa.String(length=100), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('bbox', sa.JSON(), nullable=False),
        sa.Column('image_ref', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['rover_id'], ['rovers.rover_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_detections_id'), 'detections', ['id'], unique=False)
    op.create_index(op.f('ix_detections_class_name'), 'detections', ['class_name'], unique=False)
    op.create_index('ix_detections_rover_id_timestamp', 'detections', ['rover_id', 'timestamp'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_detections_rover_id_timestamp', table_name='detections')
    op.drop_index(op.f('ix_detections_class_name'), table_name='detections')
    op.drop_index(op.f('ix_detections_id'), table_name='detections')
    op.drop_table('detections')

    op.drop_index('ix_locations_rover_id_timestamp', table_name='locations')
    op.drop_index(op.f('ix_locations_id'), table_name='locations')
    op.drop_table('locations')

    op.drop_index('ix_telemetry_rover_id_timestamp', table_name='telemetry')
    op.drop_index(op.f('ix_telemetry_id'), table_name='telemetry')
    op.drop_table('telemetry')

    op.drop_index(op.f('ix_rovers_rover_id'), table_name='rovers')
    op.drop_index(op.f('ix_rovers_id'), table_name='rovers')
    op.drop_table('rovers')
