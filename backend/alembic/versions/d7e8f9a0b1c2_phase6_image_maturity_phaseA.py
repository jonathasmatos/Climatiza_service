"""phase6: image maturity phase A

Revision ID: d7e8f9a0b1c2
Revises: c6d7e8f9a0b1
Create Date: 2026-03-12 23:20:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "d7e8f9a0b1c2"
down_revision = "c6d7e8f9a0b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("os_fotos", sa.Column("url_thumb", sa.String(length=500), nullable=True))
    op.add_column("os_fotos", sa.Column("mime_type", sa.String(length=100), nullable=True))
    op.add_column("os_fotos", sa.Column("tamanho_bytes", sa.Integer(), nullable=True))
    op.add_column("os_fotos", sa.Column("largura_px", sa.Integer(), nullable=True))
    op.add_column("os_fotos", sa.Column("altura_px", sa.Integer(), nullable=True))
    op.add_column("os_fotos", sa.Column("hash_sha256", sa.String(length=64), nullable=True))
    op.add_column(
        "os_fotos",
        sa.Column("duplicada_de_foto_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "os_fotos",
        sa.Column("foto_principal", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "os_fotos",
        sa.Column("status_arquivo", sa.String(length=20), nullable=False, server_default="ATIVO"),
    )
    op.add_column("os_fotos", sa.Column("criado_por_usuario", sa.Integer(), nullable=True))

    op.create_foreign_key(
        "fk_os_fotos_duplicada_de_foto",
        "os_fotos",
        "os_fotos",
        ["duplicada_de_foto_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_os_fotos_criado_por_usuario",
        "os_fotos",
        "usuarios",
        ["criado_por_usuario"],
        ["id"],
    )

    op.create_index("idx_os_fotos_ordem", "os_fotos", ["ordem_servico_id"])
    op.create_index("idx_os_fotos_hash", "os_fotos", ["hash_sha256"])


def downgrade() -> None:
    op.drop_index("idx_os_fotos_hash", table_name="os_fotos")
    op.drop_index("idx_os_fotos_ordem", table_name="os_fotos")

    op.drop_constraint("fk_os_fotos_criado_por_usuario", "os_fotos", type_="foreignkey")
    op.drop_constraint("fk_os_fotos_duplicada_de_foto", "os_fotos", type_="foreignkey")

    op.drop_column("os_fotos", "criado_por_usuario")
    op.drop_column("os_fotos", "status_arquivo")
    op.drop_column("os_fotos", "foto_principal")
    op.drop_column("os_fotos", "duplicada_de_foto_id")
    op.drop_column("os_fotos", "hash_sha256")
    op.drop_column("os_fotos", "altura_px")
    op.drop_column("os_fotos", "largura_px")
    op.drop_column("os_fotos", "tamanho_bytes")
    op.drop_column("os_fotos", "mime_type")
    op.drop_column("os_fotos", "url_thumb")
