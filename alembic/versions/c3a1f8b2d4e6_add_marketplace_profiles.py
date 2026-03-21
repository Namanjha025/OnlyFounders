"""Add marketplace profiles

Revision ID: c3a1f8b2d4e6
Revises: 51cb3969a516
Create Date: 2026-03-21 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c3a1f8b2d4e6'
down_revision: Union[str, None] = '51cb3969a516'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Create enum types ──────────────────────────────────────────
    marketplacerole = postgresql.ENUM(
        'founder', 'professional', 'advisor',
        name='marketplacerole', create_type=False,
    )
    marketplacerole.create(op.get_bind(), checkfirst=True)

    profiletype = postgresql.ENUM(
        'founder', 'professional', 'advisor',
        name='profiletype', create_type=False,
    )
    profiletype.create(op.get_bind(), checkfirst=True)

    availabilitystatus = postgresql.ENUM(
        'available', 'busy', 'not_available', 'open_to_offers',
        name='availabilitystatus', create_type=False,
    )
    availabilitystatus.create(op.get_bind(), checkfirst=True)

    marketplacedocumenttype = postgresql.ENUM(
        'resume', 'portfolio', 'case_study', 'certification', 'pitch_deck', 'other',
        name='marketplacedocumenttype', create_type=False,
    )
    marketplacedocumenttype.create(op.get_bind(), checkfirst=True)

    commitmentlevel = postgresql.ENUM(
        'full_time', 'part_time', 'flexible', 'advisory',
        name='commitmentlevel', create_type=False,
    )
    commitmentlevel.create(op.get_bind(), checkfirst=True)

    feestructure = postgresql.ENUM(
        'hourly', 'fixed', 'equity', 'retainer', 'success_fee', 'pro_bono',
        name='feestructure', create_type=False,
    )
    feestructure.create(op.get_bind(), checkfirst=True)

    # ── Add marketplace_role to users ──────────────────────────────
    op.add_column('users', sa.Column('marketplace_role', marketplacerole, nullable=True))

    # ── Enable pg_trgm extension ───────────────────────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # ── Create marketplace_profiles ────────────────────────────────
    op.create_table(
        'marketplace_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('profile_type', sa.String(20), nullable=False),
        sa.Column('headline', sa.String(500)),
        sa.Column('bio', sa.Text()),
        sa.Column('avatar_url', sa.Text()),
        sa.Column('location', sa.String(255)),
        sa.Column('skills', postgresql.JSONB(), server_default='[]'),
        sa.Column('skills_text', sa.Text()),
        sa.Column('linkedin_url', sa.Text()),
        sa.Column('website_url', sa.Text()),
        sa.Column('profile_score', sa.Integer(), server_default='0', nullable=False),
        sa.Column('is_public', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('visibility_settings', postgresql.JSONB(), server_default='{}'),
        sa.Column('extra_data', postgresql.JSONB(), server_default='{}'),
        sa.Column('twin_id', postgresql.UUID(as_uuid=True), nullable=True),  # FK to twins deferred until twins table exists
        sa.Column('profile_views', sa.Integer(), server_default='0', nullable=False),
        sa.Column('search_vector', postgresql.TSVECTOR()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("profile_type IN ('founder', 'professional', 'advisor')", name='ck_mp_profile_type'),
    )

    # ── Create professional_profiles ───────────────────────────────
    op.create_table(
        'professional_profiles',
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('marketplace_profiles.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('primary_role', sa.String(100)),
        sa.Column('years_experience', sa.Integer()),
        sa.Column('hourly_rate', sa.Numeric(10, 2)),
        sa.Column('availability_status', availabilitystatus),
        sa.Column('employment_type_preference', postgresql.JSONB(), server_default='[]'),
        sa.Column('portfolio_url', sa.Text()),
        sa.Column('certifications', postgresql.JSONB(), server_default='[]'),
        sa.Column('service_offerings', postgresql.JSONB(), server_default='[]'),
        sa.Column('cal_booking_link', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── Create advisor_profiles ────────────────────────────────────
    op.create_table(
        'advisor_profiles',
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('marketplace_profiles.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('domain_expertise', postgresql.JSONB(), server_default='[]'),
        sa.Column('investment_thesis', sa.Text()),
        sa.Column('portfolio_companies', postgresql.JSONB(), server_default='[]'),
        sa.Column('investment_stages', postgresql.JSONB(), server_default='[]'),
        sa.Column('check_size_min', sa.Numeric(12, 2)),
        sa.Column('check_size_max', sa.Numeric(12, 2)),
        sa.Column('fee_structure', feestructure),
        sa.Column('availability', sa.String(50)),
        sa.Column('cal_booking_link', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── Create founder_marketplace_profiles ────────────────────────
    op.create_table(
        'founder_marketplace_profiles',
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('marketplace_profiles.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='SET NULL'), nullable=True),
        sa.Column('looking_for_roles', postgresql.JSONB(), server_default='[]'),
        sa.Column('equity_offered', sa.String(50)),
        sa.Column('startup_stage', postgresql.ENUM('idea', 'pre_seed', 'seed', 'series_a', 'series_b', 'growth', name='startupstage', create_type=False)),
        sa.Column('industry', postgresql.ENUM('saas', 'fintech', 'healthtech', 'edtech', 'ecommerce', 'ai_ml', 'biotech', 'cleantech', 'hardware', 'marketplace', 'media', 'gaming', 'enterprise', 'consumer', 'other', name='industry', create_type=False)),
        sa.Column('cofounder_brief', sa.Text()),
        sa.Column('commitment_level', commitmentlevel),
        sa.Column('remote_ok', sa.Boolean(), server_default='true'),
        sa.Column('funding_stage', sa.String(50)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── Create profile_documents ───────────────────────────────────
    op.create_table(
        'profile_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('marketplace_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('document_type', marketplacedocumenttype),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('s3_key', sa.Text(), nullable=False),
        sa.Column('s3_url', sa.Text(), nullable=False),
        sa.Column('file_size', sa.Integer()),
        sa.Column('mime_type', sa.String(100)),
        sa.Column('is_public', sa.Boolean(), server_default='true'),
        sa.Column('sort_order', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── Indexes ────────────────────────────────────────────────────
    op.create_index('ix_mp_search_vector', 'marketplace_profiles', ['search_vector'], postgresql_using='gin')
    op.create_index('ix_mp_skills', 'marketplace_profiles', ['skills'], postgresql_using='gin')
    op.create_index(
        'ix_mp_headline_trgm', 'marketplace_profiles', ['headline'],
        postgresql_using='gin',
        postgresql_ops={'headline': 'gin_trgm_ops'},
    )
    op.create_index('ix_mp_public_type', 'marketplace_profiles', ['is_public', 'profile_type'])
    op.create_index('ix_mp_profile_type', 'marketplace_profiles', ['profile_type'])
    op.create_index('ix_pd_profile_id', 'profile_documents', ['profile_id'])

    # ── tsvector trigger ───────────────────────────────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION marketplace_profile_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('english', coalesce(NEW.headline, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(NEW.bio, '')), 'B') ||
                setweight(to_tsvector('english', coalesce(NEW.skills_text, '')), 'C');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER marketplace_profiles_search_vector_trigger
        BEFORE INSERT OR UPDATE ON marketplace_profiles
        FOR EACH ROW EXECUTE FUNCTION marketplace_profile_search_vector_update();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS marketplace_profiles_search_vector_trigger ON marketplace_profiles")
    op.execute("DROP FUNCTION IF EXISTS marketplace_profile_search_vector_update()")

    op.drop_index('ix_pd_profile_id', table_name='profile_documents')
    op.drop_index('ix_mp_profile_type', table_name='marketplace_profiles')
    op.drop_index('ix_mp_public_type', table_name='marketplace_profiles')
    op.drop_index('ix_mp_headline_trgm', table_name='marketplace_profiles')
    op.drop_index('ix_mp_skills', table_name='marketplace_profiles')
    op.drop_index('ix_mp_search_vector', table_name='marketplace_profiles')

    op.drop_table('profile_documents')
    op.drop_table('founder_marketplace_profiles')
    op.drop_table('advisor_profiles')
    op.drop_table('professional_profiles')
    op.drop_table('marketplace_profiles')

    op.drop_column('users', 'marketplace_role')

    op.execute("DROP TYPE IF EXISTS feestructure")
    op.execute("DROP TYPE IF EXISTS commitmentlevel")
    op.execute("DROP TYPE IF EXISTS marketplacedocumenttype")
    op.execute("DROP TYPE IF EXISTS availabilitystatus")
    op.execute("DROP TYPE IF EXISTS profiletype")
    op.execute("DROP TYPE IF EXISTS marketplacerole")
