"""20260512_client_secret_hash

Revision ID: 5b2c3d4e5f60
Revises: 4a1b2c3d4e5f
Create Date: 2026-05-12 16:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '5b2c3d4e5f60'
down_revision: Union[str, Sequence[str], None] = '4a1b2c3d4e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'payment_intents',
        sa.Column('client_secret_hash', sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('payment_intents', 'client_secret_hash')
