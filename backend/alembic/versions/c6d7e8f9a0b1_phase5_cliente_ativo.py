"""phase5: campo ativo em clientes

Revision ID: c6d7e8f9a0b1
Revises: b5c6d7e8f9a0
Create Date: 2026-03-12 22:30:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = 'c6d7e8f9a0b1'
down_revision = 'b5c6d7e8f9a0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adiciona coluna ativo em clientes (default True — todos existentes ficam ativos)
    op.add_column(
        'clientes',
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default='true'),
    )
    op.create_index('idx_clientes_ativo', 'clientes', ['ativo'])


def downgrade() -> None:
    op.drop_index('idx_clientes_ativo', table_name='clientes')
    op.drop_column('clientes', 'ativo')
