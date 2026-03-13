"""phase4: preventiva automation — contrato_id em ordens_servico

Revision ID: b5c6d7e8f9a0
Revises: 7a8e6c21b4d2
Create Date: 2026-03-12 22:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'b5c6d7e8f9a0'
down_revision = '7a8e6c21b4d2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adiciona coluna contrato_id (nullable) em ordens_servico
    op.add_column(
        'ordens_servico',
        sa.Column('contrato_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    # FK para contratos_manutencao
    op.create_foreign_key(
        'fk_os_contrato_manutencao',
        'ordens_servico',
        'contratos_manutencao',
        ['contrato_id'],
        ['id'],
        ondelete='SET NULL',
    )
    # Índice para queries de anti-duplicidade do scheduler
    op.create_index('idx_os_contrato', 'ordens_servico', ['contrato_id'])


def downgrade() -> None:
    op.drop_index('idx_os_contrato', table_name='ordens_servico')
    op.drop_constraint('fk_os_contrato_manutencao', 'ordens_servico', type_='foreignkey')
    op.drop_column('ordens_servico', 'contrato_id')
