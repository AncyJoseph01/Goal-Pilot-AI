"""Add google_credentials to users

Revision ID: 333def97f030
Revises: 61889f7d92cf
Create Date: 2025-11-04 11:43:22.047224

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '333def97f030'
down_revision: Union[str, None] = '61889f7d92cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('google_credentials', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'google_credentials')

