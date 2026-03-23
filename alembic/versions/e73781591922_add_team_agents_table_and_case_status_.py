"""add team_agents table and case_status to workspaces

Revision ID: e73781591922
Revises: 20b083a2b653
Create Date: 2026-03-23 01:23:51.414751

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'e73781591922'
down_revision: Union[str, None] = '20b083a2b653'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('team_agents',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('agent_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.String(length=200), nullable=True),
        sa.Column('job_description', sa.Text(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'agent_id', name='uq_team_user_agent')
    )
    op.create_index(op.f('ix_team_agents_agent_id'), 'team_agents', ['agent_id'], unique=False)
    op.create_index(op.f('ix_team_agents_user_id'), 'team_agents', ['user_id'], unique=False)

    casestatus = postgresql.ENUM('open', 'in_progress', 'resolved', name='casestatus', create_type=False)
    casestatus.create(op.get_bind(), checkfirst=True)
    op.add_column('workspaces', sa.Column('case_status', casestatus, server_default='open', nullable=False))


def downgrade() -> None:
    op.drop_column('workspaces', 'case_status')
    op.drop_index(op.f('ix_team_agents_user_id'), table_name='team_agents')
    op.drop_index(op.f('ix_team_agents_agent_id'), table_name='team_agents')
    op.drop_table('team_agents')
    sa.Enum(name='casestatus').drop(op.get_bind(), checkfirst=True)
