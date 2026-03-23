"""Add workspaces notifications and feed tables

Revision ID: 20b083a2b653
Revises: c3a1f8b2d4e6
Create Date: 2026-03-23 00:43:31.380404

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '20b083a2b653'
down_revision: Union[str, None] = 'c3a1f8b2d4e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -- workspaces --
    op.create_table('workspaces',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('workspace_type', postgresql.ENUM('ongoing', 'goal', name='workspacetype', create_type=True), server_default='ongoing', nullable=False),
        sa.Column('goal', sa.Text(), nullable=True),
        sa.Column('brief', sa.Text(), nullable=True),
        sa.Column('status_text', sa.String(length=500), nullable=True),
        sa.Column('progress', sa.Integer(), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workspaces_user_id', 'workspaces', ['user_id'])

    # -- workspace_agents --
    op.create_table('workspace_agents',
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('agent_id', sa.UUID(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workspace_agents_workspace_id', 'workspace_agents', ['workspace_id'])
    op.create_index('ix_workspace_agents_agent_id', 'workspace_agents', ['agent_id'])

    # -- workspace_messages --
    op.create_table('workspace_messages',
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('agent_id', sa.UUID(), nullable=True),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('role', postgresql.ENUM('user', 'assistant', 'activity', name='workspacemessagerole', create_type=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('action_buttons', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workspace_messages_workspace_id', 'workspace_messages', ['workspace_id'])

    # -- workspace_tasks --
    op.create_table('workspace_tasks',
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('agent_id', sa.UUID(), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('assignee_name', sa.String(length=200), nullable=True),
        sa.Column('is_done', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workspace_tasks_workspace_id', 'workspace_tasks', ['workspace_id'])

    # -- notifications --
    op.create_table('notifications',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=True),
        sa.Column('agent_id', sa.UUID(), nullable=True),
        sa.Column('notification_type', postgresql.ENUM('approval', 'report', name='notificationtype', create_type=True), nullable=False),
        sa.Column('priority', postgresql.ENUM('high', 'medium', 'low', name='notificationpriority', create_type=True), server_default='low', nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('detail', sa.Text(), nullable=True),
        sa.Column('is_read', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('action_buttons', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_workspace_id', 'notifications', ['workspace_id'])

    # -- feed_events --
    op.create_table('feed_events',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('agent_id', sa.UUID(), nullable=True),
        sa.Column('event_type', postgresql.ENUM('task_complete', 'task_started', 'file_created', 'status_update', 'approval_request', name='feedeventtype', create_type=True), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_feed_events_user_id', 'feed_events', ['user_id'])
    op.create_index('ix_feed_events_workspace_id', 'feed_events', ['workspace_id'])

    # -- agent profile columns --
    op.add_column('agents', sa.Column('category', sa.String(length=100), nullable=True))
    op.add_column('agents', sa.Column('icon', sa.String(length=50), nullable=True))
    op.add_column('agents', sa.Column('color', sa.String(length=20), nullable=True))
    op.add_column('agents', sa.Column('capabilities', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('agents', sa.Column('instructions', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('agents', sa.Column('connections', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column('agents', 'connections')
    op.drop_column('agents', 'instructions')
    op.drop_column('agents', 'capabilities')
    op.drop_column('agents', 'color')
    op.drop_column('agents', 'icon')
    op.drop_column('agents', 'category')

    op.drop_index('ix_feed_events_workspace_id', table_name='feed_events')
    op.drop_index('ix_feed_events_user_id', table_name='feed_events')
    op.drop_table('feed_events')
    op.execute("DROP TYPE IF EXISTS feedeventtype")

    op.drop_index('ix_notifications_workspace_id', table_name='notifications')
    op.drop_index('ix_notifications_user_id', table_name='notifications')
    op.drop_table('notifications')
    op.execute("DROP TYPE IF EXISTS notificationtype")
    op.execute("DROP TYPE IF EXISTS notificationpriority")

    op.drop_index('ix_workspace_tasks_workspace_id', table_name='workspace_tasks')
    op.drop_table('workspace_tasks')

    op.drop_index('ix_workspace_messages_workspace_id', table_name='workspace_messages')
    op.drop_table('workspace_messages')
    op.execute("DROP TYPE IF EXISTS workspacemessagerole")

    op.drop_index('ix_workspace_agents_agent_id', table_name='workspace_agents')
    op.drop_index('ix_workspace_agents_workspace_id', table_name='workspace_agents')
    op.drop_table('workspace_agents')

    op.drop_index('ix_workspaces_user_id', table_name='workspaces')
    op.drop_table('workspaces')
    op.execute("DROP TYPE IF EXISTS workspacetype")
