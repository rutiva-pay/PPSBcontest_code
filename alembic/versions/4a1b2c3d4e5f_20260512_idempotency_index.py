"""20260512_idempotency_index

Revision ID: 4a1b2c3d4e5f
Revises: 3ca9bba912db
Create Date: 2026-05-12 16:45:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = '4a1b2c3d4e5f'
down_revision: Union[str, Sequence[str], None] = '3ca9bba912db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_payment_intents_merchant_idem "
        "ON payment_intents (merchant_id, idempotency_key) "
        "WHERE idempotency_key IS NOT NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_payment_intents_merchant_idem")
