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
productstage = postgresql.ENUM('idea', 'prototype', 'mvp', 'beta', 'live', name='productstage', create_type=False)
fundingroundtype = postgresql.ENUM('pre_seed', 'seed', 'series_a', 'series_b', 'convertible_note', 'safe', 'grant', 'other', name='fundingroundtype', create_type=False)
documentcategory = postgresql.ENUM('pitch_deck', 'cap_table', 'financials', 'incorporation', 'business_plan', 'term_sheet', 'safe_agreement', 'patent', 'contract', 'other', name='documentcategory', create_type=False)
memberrole = postgresql.ENUM('founder', 'cofounder', 'cto', 'cpo', 'cfo', 'advisor', 'employee', name='memberrole', create_type=False)
accesslevel = postgresql.ENUM('admin', 'editor', 'viewer', name='accesslevel', create_type=False)
employmenttype = postgresql.ENUM('full_time', 'part_time', 'contract', 'intern', name='employmenttype', create_type=False)
memberdoccategory = postgresql.ENUM('offer_letter', 'contract', 'nda', 'policy_acknowledgement', 'review', 'tax_form', 'other', name='memberdoccategory', create_type=False)
taskstatus = postgresql.ENUM('pending', 'in_progress', 'blocked', 'review', 'completed', name='taskstatus', create_type=False)
taskpriority = postgresql.ENUM('low', 'medium', 'high', 'urgent', name='taskpriority', create_type=False)
calendareventtype = postgresql.ENUM('task_due', 'meeting', 'reminder', 'milestone', 'deadline', name='calendareventtype', create_type=False)
agenttype = postgresql.ENUM('platform', 'marketplace', name='agenttype', create_type=False)
messagerole = postgresql.ENUM('user', 'assistant', 'system', 'tool', name='messagerole', create_type=False)


def upgrade() -> None:
    # Create enum types
    userrole.create(op.get_bind(), checkfirst=True)
    startupstage.create(op.get_bind(), checkfirst=True)
    industry.create(op.get_bind(), checkfirst=True)
    productstage.create(op.get_bind(), checkfirst=True)
    fundingroundtype.create(op.get_bind(), checkfirst=True)
    documentcategory.create(op.get_bind(), checkfirst=True)
    memberrole.create(op.get_bind(), checkfirst=True)
    accesslevel.create(op.get_bind(), checkfirst=True)
    employmenttype.create(op.get_bind(), checkfirst=True)
    memberdoccategory.create(op.get_bind(), checkfirst=True)
    taskstatus.create(op.get_bind(), checkfirst=True)
    taskpriority.create(op.get_bind(), checkfirst=True)
    calendareventtype.create(op.get_bind(), checkfirst=True)
    agenttype.create(op.get_bind(), checkfirst=True)
    messagerole.create(op.get_bind(), checkfirst=True)

    # ── users ──
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

    # ── founder_profiles ──
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

    # ── agents ── (must come before startup_members which references it)
    op.create_table(
        'agents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(200), nullable=False, unique=True),
        sa.Column('description', sa.Text()),
        sa.Column('agent_type', agenttype, nullable=False, server_default='platform'),
        sa.Column('system_prompt', sa.Text()),
        sa.Column('skills', postgresql.JSONB()),
        sa.Column('tools_config', postgresql.JSONB()),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_agents_slug', 'agents', ['slug'], unique=True)

    # ── startups ── (simplified)
    op.create_table(
        'startups',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(200), nullable=False, unique=True),
        sa.Column('tagline', sa.String(80)),
        sa.Column('short_description', sa.String(500)),
        sa.Column('logo_url', sa.String(500)),
        sa.Column('website_url', sa.String(500)),
        sa.Column('stage', startupstage),
        sa.Column('industry', industry),
        sa.Column('founded_date', sa.Date()),
        sa.Column('hq_city', sa.String(100)),
        sa.Column('hq_country', sa.String(100)),
        sa.Column('is_remote', sa.Boolean()),
        sa.Column('team_size', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_startups_created_by', 'startups', ['created_by'])
    op.create_index('ix_startups_slug', 'startups', ['slug'], unique=True)
    op.create_index('ix_startups_stage', 'startups', ['stage'])
    op.create_index('ix_startups_industry', 'startups', ['industry'])

    # ── startup_members ── (humans + agents)
    op.create_table(
        'startup_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agents.id', ondelete='SET NULL')),
        sa.Column('name', sa.String(200)),
        sa.Column('email', sa.String(255)),
        sa.Column('role', memberrole, nullable=False),
        sa.Column('title', sa.String(100)),
        sa.Column('department', sa.String(100)),
        sa.Column('responsibilities', sa.Text()),
        sa.Column('access_level', accesslevel),
        sa.Column('employment_type', employmenttype),
        sa.Column('start_date', sa.Date()),
        sa.Column('salary', sa.BigInteger()),
        sa.Column('equity_percentage', sa.Numeric(5, 2)),
        sa.Column('is_full_time', sa.Boolean()),
        sa.Column('reporting_to', postgresql.UUID(as_uuid=True), sa.ForeignKey('startup_members.id', ondelete='SET NULL')),
        sa.Column('linkedin_url', sa.String(500)),
        sa.Column('bio', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('startup_id', 'user_id', name='uq_startup_member_user'),
        sa.UniqueConstraint('startup_id', 'agent_id', name='uq_startup_member_agent'),
    )

    # ── product_details ──
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

    # ── traction_metrics ──
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

    # ── financial_details ──
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

    # ── funding_rounds ──
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

    # ── equity_shareholders ──
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

    # ── documents ──
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

    # ── member_documents ──
    op.create_table(
        'member_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('member_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startup_members.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('category', memberdoccategory, nullable=False),
        sa.Column('file_name', sa.String(255)),
        sa.Column('file_size', sa.Integer()),
        sa.Column('mime_type', sa.String(100)),
        sa.Column('s3_key', sa.String(500)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_member_documents_startup_id', 'member_documents', ['startup_id'])
    op.create_index('ix_member_documents_member_id', 'member_documents', ['member_id'])

    # ── tasks ──
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('status', taskstatus, nullable=False, server_default='pending'),
        sa.Column('priority', taskpriority),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), sa.ForeignKey('startup_members.id', ondelete='SET NULL')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('startup_members.id', ondelete='SET NULL')),
        sa.Column('due_date', sa.Date()),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_tasks_startup_id', 'tasks', ['startup_id'])
    op.create_index('ix_tasks_assigned_to', 'tasks', ['assigned_to'])

    # ── calendar_events ──
    op.create_table(
        'calendar_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('event_type', calendareventtype, nullable=False),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('event_time', sa.Time()),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tasks.id', ondelete='CASCADE')),
        sa.Column('created_by_user', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('created_by_agent', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_calendar_events_startup_id', 'calendar_events', ['startup_id'])

    # ── messages ──
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('startups.id', ondelete='CASCADE'), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agents.id', ondelete='SET NULL')),
        sa.Column('role', messagerole, nullable=False),
        sa.Column('content', sa.Text()),
        sa.Column('metadata', postgresql.JSONB()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_messages_startup_id', 'messages', ['startup_id'])
    op.create_index('ix_messages_agent_id', 'messages', ['agent_id'])


def downgrade() -> None:
    op.drop_table('messages')
    op.drop_table('calendar_events')
    op.drop_table('tasks')
    op.drop_table('member_documents')
    op.drop_table('documents')
    op.drop_table('equity_shareholders')
    op.drop_table('funding_rounds')
    op.drop_table('financial_details')
    op.drop_table('traction_metrics')
    op.drop_table('product_details')
    op.drop_table('startup_members')
    op.drop_table('startups')
    op.drop_table('agents')
    op.drop_table('founder_profiles')
    op.drop_table('users')

    messagerole.drop(op.get_bind(), checkfirst=True)
    agenttype.drop(op.get_bind(), checkfirst=True)
    calendareventtype.drop(op.get_bind(), checkfirst=True)
    taskpriority.drop(op.get_bind(), checkfirst=True)
    taskstatus.drop(op.get_bind(), checkfirst=True)
    memberdoccategory.drop(op.get_bind(), checkfirst=True)
    employmenttype.drop(op.get_bind(), checkfirst=True)
    accesslevel.drop(op.get_bind(), checkfirst=True)
    documentcategory.drop(op.get_bind(), checkfirst=True)
    memberrole.drop(op.get_bind(), checkfirst=True)
    fundingroundtype.drop(op.get_bind(), checkfirst=True)
    productstage.drop(op.get_bind(), checkfirst=True)
    industry.drop(op.get_bind(), checkfirst=True)
    startupstage.drop(op.get_bind(), checkfirst=True)
    userrole.drop(op.get_bind(), checkfirst=True)
