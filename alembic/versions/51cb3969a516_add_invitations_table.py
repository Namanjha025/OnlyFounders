"""Add invitations table

Revision ID: 51cb3969a516
Revises: b68f17140c45
Create Date: 2026-03-15 19:18:05.937949

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '51cb3969a516'
down_revision: Union[str, None] = 'b68f17140c45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('invitations',
    sa.Column('startup_id', sa.UUID(), nullable=False),
    sa.Column('invited_by', sa.UUID(), nullable=False),
    sa.Column('invited_user_id', sa.UUID(), nullable=False),
    sa.Column('role', postgresql.ENUM('founder', 'cofounder', 'cto', 'cpo', 'cfo', 'advisor', 'employee', name='memberrole', create_type=False), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=True),
    sa.Column('responsibilities', sa.Text(), nullable=True),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('status', postgresql.ENUM('pending', 'accepted', 'declined', 'expired', name='invitationstatus', create_type=True), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['invited_by'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['invited_user_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['startup_id'], ['startups.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('invitations')
    op.execute("DROP TYPE IF EXISTS invitationstatus")
