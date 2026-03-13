"""phase2_ordem_status_machine

Revision ID: 4f4f2bce8c1f
Revises: 08d07f84aa66
Create Date: 2026-03-12 21:30:00.000000-03:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4f4f2bce8c1f'
down_revision: Union[str, None] = '08d07f84aa66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('ordens_servico', sa.Column('motivo_cancelamento', sa.Text(), nullable=True))

    op.execute("UPDATE ordens_servico SET status = 'NOVO' WHERE status = 'ABERTA'")
    op.execute("UPDATE ordens_servico SET status = 'AGENDADO' WHERE status = 'AGENDADA'")
    op.execute("UPDATE ordens_servico SET status = 'RESOLVIDO' WHERE status = 'CONCLUIDA'")
    op.execute("UPDATE ordens_servico SET status = 'FECHADO' WHERE status = 'ENCERRADA'")

    op.execute("UPDATE historico_os SET status_anterior = 'NOVO' WHERE status_anterior = 'ABERTA'")
    op.execute("UPDATE historico_os SET status_anterior = 'AGENDADO' WHERE status_anterior = 'AGENDADA'")
    op.execute("UPDATE historico_os SET status_anterior = 'RESOLVIDO' WHERE status_anterior = 'CONCLUIDA'")
    op.execute("UPDATE historico_os SET status_anterior = 'FECHADO' WHERE status_anterior = 'ENCERRADA'")

    op.execute("UPDATE historico_os SET status_novo = 'NOVO' WHERE status_novo = 'ABERTA'")
    op.execute("UPDATE historico_os SET status_novo = 'AGENDADO' WHERE status_novo = 'AGENDADA'")
    op.execute("UPDATE historico_os SET status_novo = 'RESOLVIDO' WHERE status_novo = 'CONCLUIDA'")
    op.execute("UPDATE historico_os SET status_novo = 'FECHADO' WHERE status_novo = 'ENCERRADA'")


def downgrade() -> None:
    op.execute("UPDATE historico_os SET status_novo = 'ABERTA' WHERE status_novo = 'NOVO'")
    op.execute("UPDATE historico_os SET status_novo = 'AGENDADA' WHERE status_novo = 'AGENDADO'")
    op.execute("UPDATE historico_os SET status_novo = 'CONCLUIDA' WHERE status_novo = 'RESOLVIDO'")
    op.execute("UPDATE historico_os SET status_novo = 'ENCERRADA' WHERE status_novo = 'FECHADO'")

    op.execute("UPDATE historico_os SET status_anterior = 'ABERTA' WHERE status_anterior = 'NOVO'")
    op.execute("UPDATE historico_os SET status_anterior = 'AGENDADA' WHERE status_anterior = 'AGENDADO'")
    op.execute("UPDATE historico_os SET status_anterior = 'CONCLUIDA' WHERE status_anterior = 'RESOLVIDO'")
    op.execute("UPDATE historico_os SET status_anterior = 'ENCERRADA' WHERE status_anterior = 'FECHADO'")

    op.execute("UPDATE ordens_servico SET status = 'ABERTA' WHERE status = 'NOVO'")
    op.execute("UPDATE ordens_servico SET status = 'AGENDADA' WHERE status = 'AGENDADO'")
    op.execute("UPDATE ordens_servico SET status = 'CONCLUIDA' WHERE status = 'RESOLVIDO'")
    op.execute("UPDATE ordens_servico SET status = 'ENCERRADA' WHERE status = 'FECHADO'")

    op.drop_column('ordens_servico', 'motivo_cancelamento')
