"""add endpoint_url and auth_token to agents

Revision ID: 4a57d6128483
Revises: e73781591922
Create Date: 2026-03-26 20:34:22.566540

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4a57d6128483'
down_revision: Union[str, None] = 'e73781591922'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('agents', sa.Column('endpoint_url', sa.String(length=500), nullable=True))
    op.add_column('agents', sa.Column('auth_token', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('agents', 'auth_token')
    op.drop_column('agents', 'endpoint_url')
