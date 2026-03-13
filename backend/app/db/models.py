"""
Climatiza Service — Modelos SQLAlchemy

Hierarquia: Cliente → Local → Ambiente → Equipamento
                                            ↓
                              OrdemServico (N:N Equipamentos)
                                    ↓
                        Checklist, Materiais, Fotos, Histórico

Contratos de Manutenção → N:N Locais
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Date, Integer, Numeric,
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def _uuid():
    return uuid.uuid4()


def _now():
    return datetime.now(timezone.utc)


# ── Autenticação ──────────────────────────────────────────────

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nome = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    senha_hash = Column(Text, nullable=False)
    perfil = Column(String(20), nullable=False)  # ADMIN | GESTOR | TECNICO
    telefone = Column(String(20), nullable=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=_now)
    atualizado_em = Column(DateTime, default=_now, onupdate=_now)

    __table_args__ = (
        Index("idx_usuarios_email", "email"),
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    token_hash = Column(Text, nullable=False)
    expira_em = Column(DateTime, nullable=False)
    revogado = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=_now)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"))
    token_hash = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=_now)


class AuthEvento(Base):
    __tablename__ = "auth_eventos"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    tipo_evento = Column(String(50))
    criado_em = Column(DateTime, default=_now)


# ── Domínio Climatiza ────────────────────────────────────────

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    nome = Column(String(200), nullable=False)
    cpf_cnpj = Column(String(20), unique=True, nullable=True)
    contato_principal = Column(String(200), nullable=True)
    telefone = Column(String(20), nullable=True)
    email = Column(String(200), nullable=True)
    ativo = Column(Boolean, default=True)
    plano_manutencao_ativo = Column(Boolean, default=False)
    observacoes = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=_now)
    atualizado_em = Column(DateTime, default=_now, onupdate=_now)

    locais = relationship("Local", back_populates="cliente", cascade="all, delete-orphan")
    ordens = relationship("OrdemServico", back_populates="cliente")
    contratos = relationship("ContratoManutencao", back_populates="cliente")


class Local(Base):
    __tablename__ = "locais"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    nome = Column(String(200), nullable=False)
    logradouro = Column(String(300), nullable=True)
    cidade = Column(String(100), nullable=True)
    estado = Column(String(2), nullable=True)
    cep = Column(String(10), nullable=True)
    criado_em = Column(DateTime, default=_now)
    atualizado_em = Column(DateTime, default=_now, onupdate=_now)

    cliente = relationship("Cliente", back_populates="locais")
    ambientes = relationship("Ambiente", back_populates="local", cascade="all, delete-orphan")
    ordens = relationship("OrdemServico", back_populates="local")


class Ambiente(Base):
    __tablename__ = "ambientes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    local_id = Column(UUID(as_uuid=True), ForeignKey("locais.id"), nullable=False)
    nome = Column(String(200), nullable=False)
    andar = Column(String(20), nullable=True)
    criado_em = Column(DateTime, default=_now)
    atualizado_em = Column(DateTime, default=_now, onupdate=_now)

    local = relationship("Local", back_populates="ambientes")
    equipamentos = relationship("Equipamento", back_populates="ambiente", cascade="all, delete-orphan")


class Equipamento(Base):
    __tablename__ = "equipamentos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    ambiente_id = Column(UUID(as_uuid=True), ForeignKey("ambientes.id"), nullable=False)
    marca = Column(String(100), nullable=False)
    linha = Column(String(50), nullable=True)           # Split, Piso Teto, Cassete
    modelo = Column(String(100), nullable=True)
    capacidade_btu = Column(Integer, nullable=True)     # 9000, 12000, ...
    voltagem = Column(String(10), nullable=True)        # 110V, 220V, Trifásico
    cor = Column(String(50), default="Branca")
    numero_serie = Column(String(100), nullable=True)
    data_instalacao = Column(Date, nullable=True)
    ultima_manutencao = Column(Date, nullable=True)
    status = Column(String(20), default="ATIVO")        # ATIVO | INATIVO | EM_GARANTIA
    criado_em = Column(DateTime, default=_now)
    atualizado_em = Column(DateTime, default=_now, onupdate=_now)

    ambiente = relationship("Ambiente", back_populates="equipamentos")
    os_equipamentos = relationship("OSEquipamento", back_populates="equipamento")


class Tecnico(Base):
    __tablename__ = "tecnicos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    nome = Column(String(200), nullable=False)
    telefone = Column(String(20), nullable=True)
    email = Column(String(200), nullable=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=_now)
    atualizado_em = Column(DateTime, default=_now, onupdate=_now)


class OrdemServico(Base):
    __tablename__ = "ordens_servico"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    numero_os = Column(Integer, autoincrement=True, unique=True)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    local_id = Column(UUID(as_uuid=True), ForeignKey("locais.id"), nullable=False)
    tipo_servico = Column(String(30), nullable=False)   # INSTALACAO | PREVENTIVA | CORRETIVA | DESINSTALACAO
    status = Column(String(30), default="NOVO")
    created_by = Column(String(20), default="ADMIN", nullable=False)
    criado_por_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    contrato_id = Column(UUID(as_uuid=True), ForeignKey("contratos_manutencao.id"), nullable=True)
    descricao_problema = Column(Text, nullable=True)
    diagnostico_tecnico = Column(Text, nullable=True)
    descricao_servico = Column(Text, nullable=True)
    motivo_cancelamento = Column(Text, nullable=True)
    fabricante_garantia = Column(String(50), nullable=True)  # Agratto | Gree | TCL | null
    valor_mao_obra = Column(Numeric(10, 2), default=0)
    valor_materiais = Column(Numeric(10, 2), default=0)
    valor_total = Column(Numeric(10, 2), default=0)
    km_percorrido = Column(Numeric(8, 2), nullable=True)
    data_primeira_visita = Column(Date, nullable=True)
    data_segunda_visita = Column(Date, nullable=True)
    data_agendamento = Column(DateTime, nullable=True)
    data_conclusao = Column(DateTime, nullable=True)
    data_encerramento = Column(DateTime, nullable=True)
    tecnico_responsavel_id = Column(UUID(as_uuid=True), ForeignKey("tecnicos.id"), nullable=True)
    assinatura_cliente = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=_now)
    atualizado_em = Column(DateTime, default=_now, onupdate=_now)

    cliente = relationship("Cliente", back_populates="ordens")
    local = relationship("Local", back_populates="ordens")
    tecnico = relationship("Tecnico")
    criado_por = relationship("Usuario")
    contrato = relationship("ContratoManutencao")
    os_equipamentos = relationship("OSEquipamento", back_populates="ordem_servico", cascade="all, delete-orphan")
    checklist = relationship("ChecklistTecnico", back_populates="ordem_servico", uselist=False, cascade="all, delete-orphan")
    materiais = relationship("OSMaterial", back_populates="ordem_servico", cascade="all, delete-orphan")
    fotos = relationship("OSFoto", back_populates="ordem_servico", cascade="all, delete-orphan")
    historico = relationship("HistoricoOS", back_populates="ordem_servico", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_os_status", "status"),
        Index("idx_os_cliente", "cliente_id"),
        Index("idx_os_tecnico", "tecnico_responsavel_id"),
        Index("idx_os_contrato", "contrato_id"),
    )


class OSEquipamento(Base):
    __tablename__ = "os_equipamentos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    ordem_servico_id = Column(UUID(as_uuid=True), ForeignKey("ordens_servico.id"), nullable=False)
    equipamento_id = Column(UUID(as_uuid=True), ForeignKey("equipamentos.id"), nullable=False)

    ordem_servico = relationship("OrdemServico", back_populates="os_equipamentos")
    equipamento = relationship("Equipamento", back_populates="os_equipamentos")

    __table_args__ = (
        UniqueConstraint("ordem_servico_id", "equipamento_id", name="uq_os_equipamento"),
    )


class ChecklistTecnico(Base):
    __tablename__ = "checklist_tecnico"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    ordem_servico_id = Column(UUID(as_uuid=True), ForeignKey("ordens_servico.id"), nullable=False, unique=True)
    tamanho_tubulacao = Column(String(50), nullable=True)
    pressao_fluido = Column(String(50), nullable=True)
    distancia_condensador_teto = Column(String(50), nullable=True)
    distancia_evaporador_teto = Column(String(50), nullable=True)
    erro_instalacao_previa = Column(Boolean, default=False)
    observacoes = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=_now)

    ordem_servico = relationship("OrdemServico", back_populates="checklist")


class OSMaterial(Base):
    __tablename__ = "os_materiais"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    ordem_servico_id = Column(UUID(as_uuid=True), ForeignKey("ordens_servico.id"), nullable=False)
    item = Column(String(200), nullable=False)
    quantidade = Column(Numeric(10, 2), default=1)
    unidade = Column(String(20), default="unidades")
    valor_unitario = Column(Numeric(10, 2), default=0)

    ordem_servico = relationship("OrdemServico", back_populates="materiais")


class OSFoto(Base):
    __tablename__ = "os_fotos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    ordem_servico_id = Column(UUID(as_uuid=True), ForeignKey("ordens_servico.id"), nullable=False)
    url_arquivo = Column(String(500), nullable=False)
    url_thumb = Column(String(500), nullable=True)
    categoria = Column(String(50), nullable=False)  # ESTADO_INICIAL | INFRAESTRUTURA | PARAMETROS | ENTORNO | ENTREGA_FINAL
    descricao = Column(Text, nullable=True)
    mime_type = Column(String(100), nullable=True)
    tamanho_bytes = Column(Integer, nullable=True)
    largura_px = Column(Integer, nullable=True)
    altura_px = Column(Integer, nullable=True)
    hash_sha256 = Column(String(64), nullable=True)
    duplicada_de_foto_id = Column(UUID(as_uuid=True), ForeignKey("os_fotos.id"), nullable=True)
    foto_principal = Column(Boolean, default=False, nullable=False)
    status_arquivo = Column(String(20), default="ATIVO", nullable=False)
    criado_por_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    criado_em = Column(DateTime, default=_now)

    ordem_servico = relationship("OrdemServico", back_populates="fotos")

    __table_args__ = (
        Index("idx_os_fotos_ordem", "ordem_servico_id"),
        Index("idx_os_fotos_hash", "hash_sha256"),
    )


class HistoricoOS(Base):
    __tablename__ = "historico_os"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    ordem_servico_id = Column(UUID(as_uuid=True), ForeignKey("ordens_servico.id"), nullable=False)
    status_anterior = Column(String(30), nullable=True)
    status_novo = Column(String(30), nullable=False)
    observacao = Column(Text, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    criado_em = Column(DateTime, default=_now)

    ordem_servico = relationship("OrdemServico", back_populates="historico")


class ContratoManutencao(Base):
    __tablename__ = "contratos_manutencao"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    descricao = Column(Text, nullable=True)
    periodicidade_dias = Column(Integer, nullable=True)  # 30, 90, etc.
    tipo_servico = Column(String(30), nullable=True)     # LIMPEZA_FILTROS | PREVENTIVA_COMPLETA
    ativo = Column(Boolean, default=True)
    data_inicio = Column(Date, nullable=True)
    data_fim = Column(Date, nullable=True)
    criado_em = Column(DateTime, default=_now)
    atualizado_em = Column(DateTime, default=_now, onupdate=_now)

    cliente = relationship("Cliente", back_populates="contratos")
    locais = relationship("ContratoLocal", back_populates="contrato", cascade="all, delete-orphan")


class ContratoLocal(Base):
    __tablename__ = "contrato_locais"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    contrato_id = Column(UUID(as_uuid=True), ForeignKey("contratos_manutencao.id"), nullable=False)
    local_id = Column(UUID(as_uuid=True), ForeignKey("locais.id"), nullable=False)

    contrato = relationship("ContratoManutencao", back_populates="locais")
    local = relationship("Local")

    __table_args__ = (
        UniqueConstraint("contrato_id", "local_id", name="uq_contrato_local"),
    )
