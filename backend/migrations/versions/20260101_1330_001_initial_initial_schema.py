"""Initial schema with all existing tables

Revision ID: 001_initial
Revises:
Create Date: 2026-01-01 13:30:00.000000

This migration creates all tables for Constellation Hub:
- Core Orbits: constellations, satellites
- Routing: links, policies
- Ground Scheduler: ground_stations, passes, schedules, data_queues
- Auth: users
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ===========================================
    # AUTH: Users table
    # ===========================================
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False, server_default='viewer'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('api_key', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_api_key', 'users', ['api_key'], unique=True)

    # ===========================================
    # CORE ORBITS: Constellations and Satellites
    # ===========================================
    op.create_table(
        'constellations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('operator', sa.String(255), nullable=True),
        sa.Column('orbit_type', sa.String(50), nullable=True),
        sa.Column('num_planes', sa.Integer(), nullable=True),
        sa.Column('sats_per_plane', sa.Integer(), nullable=True),
        sa.Column('altitude_km', sa.Float(), nullable=True),
        sa.Column('inclination_deg', sa.Float(), nullable=True),
        sa.Column('metadata_', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_constellations_name', 'constellations', ['name'], unique=True)

    op.create_table(
        'satellites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('constellation_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('norad_id', sa.String(50), nullable=True),
        sa.Column('international_designator', sa.String(50), nullable=True),
        sa.Column('tle_line1', sa.String(70), nullable=True),
        sa.Column('tle_line2', sa.String(70), nullable=True),
        sa.Column('tle_epoch', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='operational'),
        sa.Column('metadata_', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['constellation_id'], ['constellations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_satellites_norad_id', 'satellites', ['norad_id'])
    op.create_index('ix_satellites_constellation_id', 'satellites', ['constellation_id'])

    # ===========================================
    # ROUTING: Links and Policies
    # ===========================================
    op.create_table(
        'links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('link_type', sa.String(50), nullable=False),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('target_type', sa.String(50), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('latency_ms', sa.Float(), nullable=True),
        sa.Column('bandwidth_mbps', sa.Float(), nullable=True),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('metadata_', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_links_source', 'links', ['source_type', 'source_id'])
    op.create_index('ix_links_target', 'links', ['target_type', 'target_id'])

    op.create_table(
        'policies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('latency_weight', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('cost_weight', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('hop_weight', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('max_latency_ms', sa.Float(), nullable=True),
        sa.Column('max_hops', sa.Integer(), nullable=True),
        sa.Column('max_cost', sa.Float(), nullable=True),
        sa.Column('preferred_ground_stations', postgresql.JSON(), nullable=True),
        sa.Column('avoided_ground_stations', postgresql.JSON(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_policies_name', 'policies', ['name'], unique=True)

    # ===========================================
    # GROUND SCHEDULER: Stations, Passes, Schedules
    # ===========================================
    op.create_table(
        'ground_stations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('elevation_m', sa.Float(), nullable=True, server_default='0'),
        sa.Column('min_elevation_deg', sa.Float(), nullable=False, server_default='10.0'),
        sa.Column('capabilities', postgresql.JSON(), nullable=True),
        sa.Column('health_status', sa.String(50), nullable=False, server_default='nominal'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('cost_per_minute', sa.Float(), nullable=True),
        sa.Column('metadata_', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ground_stations_name', 'ground_stations', ['name'], unique=True)

    op.create_table(
        'passes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('satellite_id', sa.Integer(), nullable=False),
        sa.Column('station_id', sa.Integer(), nullable=False),
        sa.Column('aos', sa.DateTime(timezone=True), nullable=False),
        sa.Column('los', sa.DateTime(timezone=True), nullable=False),
        sa.Column('max_elevation_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('max_elevation_deg', sa.Float(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=False),
        sa.Column('is_scheduled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('metadata_', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['station_id'], ['ground_stations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_passes_satellite_id', 'passes', ['satellite_id'])
    op.create_index('ix_passes_station_id', 'passes', ['station_id'])
    op.create_index('ix_passes_aos', 'passes', ['aos'])

    op.create_table(
        'schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_optimized', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('scheduled_passes', postgresql.JSON(), nullable=True),
        sa.Column('total_contact_minutes', sa.Float(), nullable=True),
        sa.Column('total_data_volume_mb', sa.Float(), nullable=True),
        sa.Column('metadata_', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'data_queues',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('satellite_id', sa.Integer(), nullable=False),
        sa.Column('critical_volume_mb', sa.Float(), nullable=False, server_default='0'),
        sa.Column('high_volume_mb', sa.Float(), nullable=False, server_default='0'),
        sa.Column('medium_volume_mb', sa.Float(), nullable=False, server_default='0'),
        sa.Column('low_volume_mb', sa.Float(), nullable=False, server_default='0'),
        sa.Column('total_volume_mb', sa.Float(), nullable=False, server_default='0'),
        sa.Column('customer_allocations', postgresql.JSON(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_data_queues_satellite_id', 'data_queues', ['satellite_id'], unique=True)

    # ===========================================
    # TLE RECORDS: For TLE feed ingestion
    # ===========================================
    op.create_table(
        'tle_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('norad_id', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('tle_line1', sa.String(70), nullable=False),
        sa.Column('tle_line2', sa.String(70), nullable=False),
        sa.Column('source', sa.String(50), nullable=False, server_default='celestrak'),
        sa.Column('epoch', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fetched_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tle_records_norad_id', 'tle_records', ['norad_id'])
    op.create_index('ix_tle_records_fetched_at', 'tle_records', ['fetched_at'])


def downgrade() -> None:
    # Drop in reverse order of creation
    op.drop_table('tle_records')
    op.drop_table('data_queues')
    op.drop_table('schedules')
    op.drop_table('passes')
    op.drop_table('ground_stations')
    op.drop_table('policies')
    op.drop_table('links')
    op.drop_table('satellites')
    op.drop_table('constellations')
    op.drop_table('users')
