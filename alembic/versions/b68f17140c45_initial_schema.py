"""initial_schema

Revision ID: b68f17140c45
Revises:
Create Date: 2026-03-09 01:00:25.816814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b68f17140c45'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Enum types
userrole = postgresql.ENUM('founder', 'advisor', 'investor', 'admin', name='userrole', create_type=False)
startupstage = postgresql.ENUM('idea', 'pre_seed', 'seed', 'series_a', 'series_b', 'growth', name='startupstage', create_type=False)
industry = postgresql.ENUM('saas', 'fintech', 'healthtech', 'edtech', 'ecommerce', 'ai_ml', 'biotech', 'cleantech', 'hardware', 'marketplace', 'media', 'gaming', 'enterprise', 'consumer', 'other', name='industry', create_type=False)
businessmodel = postgresql.ENUM('saas', 'marketplace', 'ecommerce', 'subscription', 'transactional', 'freemium', 'ad_supported', 'hardware', 'licensing', 'other', name='businessmodel', create_type=False)
targetmarket = postgresql.ENUM('b2b', 'b2c', 'b2b2c', 'b2g', 'd2c', name='targetmarket', create_type=False)
productstage = postgresql.ENUM('idea', 'prototype', 'mvp', 'beta', 'live', name='productstage', create_type=False)
fundingroundtype = postgresql.ENUM('pre_seed', 'seed', 'series_a', 'series_b', 'convertible_note', 'safe', 'grant', 'other', name='fundingroundtype', create_type=False)
documentcategory = postgresql.ENUM('pitch_deck', 'cap_table', 'financials', 'incorporation', 'business_plan', 'term_sheet', 'safe_agreement', 'patent', 'contract', 'other', name='documentcategory', create_type=False)
memberrole = postgresql.ENUM('founder', 'cofounder', 'cto', 'cpo', 'cfo', 'advisor', 'employee', name='memberrole', create_type=False)
incorporationtype = postgresql.ENUM('c_corp', 's_corp', 'llc', 'llp', 'pbc', 'ltd', 'other', name='incorporationtype', create_type=False)


def upgrade() -> None:
    # Create enum types
    userrole.create(op.get_bind(), checkfirst=True)
    startupstage.create(op.get_bind(), checkfirst=True)
    industry.create(op.get_bind(), checkfirst=True)
    businessmodel.create(op.get_bind(), checkfirst=True)
    targetmarket.create(op.get_bind(), checkfirst=True)
    productstage.create(op.get_bind(), checkfirst=True)
    fundingroundtype.create(op.get_bind(), checkfirst=True)
    documentcategory.create(op.get_bind(), checkfirst=True)
    memberrole.create(op.get_bind(), checkfirst=True)
    incorporationtype.create(op.get_bind(), checkfirst=True)

    # users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('role', userrole, server_default='founder'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # founder_profiles
    op.create_table(
        'founder_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('phone', sa.String(20)),
        sa.Column('bio', sa.Text()),
        sa.Column('linkedin_url', sa.String(500)),
        sa.Column('twitter_url', sa.String(500)),
        sa.Column('github_url', sa.String(500)),
        sa.Column('website_url', sa.String(500)),
        sa.Column('profile_photo_url', sa.String(500)),
        sa.Column('city', sa.String(100)),
        sa.Column('country', sa.String(100)),
        sa.Column('is_technical', sa.Boolean()),
        sa.Column('is_full_time', sa.Boolean()),
        sa.Column('education', sa.String(255)),
        sa.Column('degree_field', sa.String(255)),
        sa.Column('years_of_experience', sa.Integer()),
        sa.Column('previous_startups', sa.Text()),
        sa.Column('notable_achievement', sa.Text()),
        sa.Column('skills', postgresql.JSONB()),
        sa.Column('domain_expertise', postgresql.JSONB()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # startups
    op.create_table(
        'startups',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(200), nullable=False, unique=True),
        sa.Column('tagline', sa.String(80)),
        sa.Column('short_description', sa.String(500)),
        sa.Column('long_description', sa.Text()),
        sa.Column('logo_url', sa.String(500)),
        sa.Column('website_url', sa.String(500)),
        sa.Column('demo_url', sa.String(500)),
        sa.Column('stage', startupstage),
        sa.Column('industry', industry),
        sa.Column('industries', postgresql.JSONB()),
        sa.Column('business_model', businessmodel),
        sa.Column('target_market', targetmarket),
        sa.Column('founded_date', sa.Date()),
        sa.Column('is_incorporated', sa.Boolean()),
        sa.Column('entity_type', incorporationtype),
        sa.Column('incorporation_country', sa.String(100)),
        sa.Column('incorporation_state', sa.String(100)),
        sa.Column('legal_entity_name', sa.String(255)),
        sa.Column('hq_city', sa.String(100)),
        sa.Column('hq_country', sa.String(100)),
        sa.Column('is_remote', sa.Boolean()),
        sa.Column('company_linkedin', sa.String(500)),
        sa.Column('company_twitter', sa.String(500)),
        sa.Column('team_size', sa.Integer()),
        sa.Column('profile_completeness', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_startups_created_by', 'startups', ['created_by'])
    op.create_index('ix_startups_slug', 'startups', ['slug'], unique=True)
    op.create_index('ix_startups_stage', 'startups', ['stage'])
    op.create_index('ix_startups_industry', 'startups', ['industry'])

    # startup_members
    op.create_table(
        'startup_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('name', sa.String(200)),
        sa.Column('email', sa.String(255)),
        sa.Column('role', memberrole, nullable=False),
        sa.Column('title', sa.String(100)),
        sa.Column('equity_percentage', sa.Numeric(5, 2)),
        sa.Column('is_full_time', sa.Boolean()),
        sa.Column('linkedin_url', sa.String(500)),
        sa.Column('bio', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('startup_id', 'user_id', name='uq_startup_member_user'),
    )

    # product_details
    op.create_table(
        'product_details',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('problem', sa.Text()),
        sa.Column('solution', sa.Text()),
        sa.Column('product_stage', productstage),
        sa.Column('why_now', sa.Text()),
        sa.Column('unique_insight', sa.Text()),
        sa.Column('target_audience', sa.Text()),
        sa.Column('tam', sa.BigInteger()),
        sa.Column('sam', sa.BigInteger()),
        sa.Column('som', sa.BigInteger()),
        sa.Column('competitors', postgresql.JSONB()),
        sa.Column('competitive_advantage', sa.Text()),
        sa.Column('revenue_model', sa.Text()),
        sa.Column('tech_stack', postgresql.JSONB()),
        sa.Column('go_to_market', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # traction_metrics
    op.create_table(
        'traction_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('has_users', sa.Boolean()),
        sa.Column('active_users', sa.Integer()),
        sa.Column('total_registered_users', sa.Integer()),
        sa.Column('paying_customers', sa.Integer()),
        sa.Column('user_growth_rate_pct', sa.Numeric(5, 2)),
        sa.Column('churn_rate_pct', sa.Numeric(5, 2)),
        sa.Column('has_revenue', sa.Boolean()),
        sa.Column('mrr', sa.BigInteger()),
        sa.Column('arr', sa.BigInteger()),
        sa.Column('revenue_growth_rate_pct', sa.Numeric(5, 2)),
        sa.Column('north_star_metric_name', sa.String(100)),
        sa.Column('north_star_metric_value', sa.String(100)),
        sa.Column('ltv_cents', sa.BigInteger()),
        sa.Column('cac_cents', sa.BigInteger()),
        sa.Column('key_milestones', sa.Text()),
        sa.Column('next_milestones', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # financial_details
    op.create_table(
        'financial_details',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('monthly_burn_rate', sa.BigInteger()),
        sa.Column('cash_in_bank', sa.BigInteger()),
        sa.Column('runway_months', sa.Integer()),
        sa.Column('monthly_revenue', sa.BigInteger()),
        sa.Column('monthly_expenses', sa.BigInteger()),
        sa.Column('gross_margin_pct', sa.Numeric(5, 2)),
        sa.Column('is_fundraising', sa.Boolean()),
        sa.Column('fundraise_target', sa.BigInteger()),
        sa.Column('fundraise_round_type', fundingroundtype),
        sa.Column('total_raised', sa.BigInteger()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # funding_rounds
    op.create_table(
        'funding_rounds',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('round_type', fundingroundtype, nullable=False),
        sa.Column('amount_raised', sa.BigInteger()),
        sa.Column('pre_money_valuation', sa.BigInteger()),
        sa.Column('post_money_valuation', sa.BigInteger()),
        sa.Column('round_date', sa.Date()),
        sa.Column('lead_investor', sa.String(200)),
        sa.Column('investors', postgresql.JSONB()),
        sa.Column('instrument_type', sa.String(50)),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_funding_rounds_startup_id', 'funding_rounds', ['startup_id'])

    # equity_shareholders
    op.create_table(
        'equity_shareholders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('relationship_type', sa.String(50)),
        sa.Column('equity_percentage', sa.Numeric(5, 2)),
        sa.Column('share_class', sa.String(50)),
        sa.Column('shares_owned', sa.Integer()),
        sa.Column('vesting_schedule', sa.String(200)),
        sa.Column('investment_amount', sa.BigInteger()),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_equity_shareholders_startup_id', 'equity_shareholders', ['startup_id'])

    # documents
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('category', documentcategory, nullable=False),
        sa.Column('file_name', sa.String(255)),
        sa.Column('file_size', sa.Integer()),
        sa.Column('mime_type', sa.String(100)),
        sa.Column('s3_key', sa.String(500)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_documents_startup_id', 'documents', ['startup_id'])
    op.create_index('ix_documents_category', 'documents', ['category'])


def downgrade() -> None:
    op.drop_table('documents')
    op.drop_table('equity_shareholders')
    op.drop_table('funding_rounds')
    op.drop_table('financial_details')
    op.drop_table('traction_metrics')
    op.drop_table('product_details')
    op.drop_table('startup_members')
    op.drop_table('startups')
    op.drop_table('founder_profiles')
    op.drop_table('users')

    documentcategory.drop(op.get_bind(), checkfirst=True)
    memberrole.drop(op.get_bind(), checkfirst=True)
    fundingroundtype.drop(op.get_bind(), checkfirst=True)
    productstage.drop(op.get_bind(), checkfirst=True)
    targetmarket.drop(op.get_bind(), checkfirst=True)
    businessmodel.drop(op.get_bind(), checkfirst=True)
    industry.drop(op.get_bind(), checkfirst=True)
    startupstage.drop(op.get_bind(), checkfirst=True)
    incorporationtype.drop(op.get_bind(), checkfirst=True)
    userrole.drop(op.get_bind(), checkfirst=True)
