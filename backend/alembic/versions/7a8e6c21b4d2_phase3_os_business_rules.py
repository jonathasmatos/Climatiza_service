"""phase3_os_business_rules

Revision ID: 7a8e6c21b4d2
Revises: 4f4f2bce8c1f
Create Date: 2026-03-12 21:45:00.000000-03:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '7a8e6c21b4d2'
down_revision: Union[str, None] = '4f4f2bce8c1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('ordens_servico', sa.Column('created_by', sa.String(length=20), nullable=False, server_default='ADMIN'))
    op.add_column('ordens_servico', sa.Column('criado_por_usuario', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_ordens_servico_criado_por_usuario_usuarios',
        'ordens_servico', 'usuarios', ['criado_por_usuario'], ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_ordens_servico_criado_por_usuario_usuarios', 'ordens_servico', type_='foreignkey')
    op.drop_column('ordens_servico', 'criado_por_usuario')
    op.drop_column('ordens_servico', 'created_by')
