"""create payments table

Revision ID: f1e36bca0808
Revises:
Create Date: 2026-06-23 19:35:09.524800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f1e36bca0808'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'payments',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('currency', sa.Enum('RUB', 'USD', 'EUR', name='currency_enum'), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'succeeded', 'failed', name='payment_status_enum'), server_default=sa.text("'pending'"), nullable=False),
        sa.Column('idempotency_key', sa.String(), nullable=False),
        sa.Column('webhook_url', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_payments_idempotency_key'), 'payments', ['idempotency_key'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_payments_idempotency_key'), table_name='payments')
    op.drop_table('payments')
