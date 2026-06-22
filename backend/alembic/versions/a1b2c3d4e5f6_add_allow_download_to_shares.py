"""add_allow_download_to_shares

Revision ID: a1b2c3d4e5f6
Revises: 37d3ad3e8f10
Create Date: 2026-06-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '37d3ad3e8f10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('shares', sa.Column('allow_download', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='是否允许下载，默认允许'))


def downgrade() -> None:
    op.drop_column('shares', 'allow_download')
