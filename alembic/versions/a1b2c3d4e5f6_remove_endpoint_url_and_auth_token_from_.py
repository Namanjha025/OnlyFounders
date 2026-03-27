"""remove endpoint_url and auth_token from agents

Revision ID: a1b2c3d4e5f6
Revises: 4a57d6128483
Create Date: 2026-03-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '4a57d6128483'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('agents', 'endpoint_url')
    op.drop_column('agents', 'auth_token')


def downgrade() -> None:
    op.add_column('agents', sa.Column('endpoint_url', sa.String(length=500), nullable=True))
    op.add_column('agents', sa.Column('auth_token', sa.String(length=500), nullable=True))
