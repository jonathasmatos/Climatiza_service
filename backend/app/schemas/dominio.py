"""Climatiza Service — Schemas de domínio (Pydantic V2)"""

from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.core.states import FotoCategoria, OrdemOrigem, OrdemStatus


# ── Cliente ──────────────────────────────────────────
class ClienteBase(BaseModel):
    nome: str
    cpf_cnpj: str | None = None
    contato_principal: str | None = None
    telefone: str | None = None
    email: str | None = None
    ativo: bool = True
    plano_manutencao_ativo: bool = False
    observacoes: str | None = None


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nome: str | None = None
    cpf_cnpj: str | None = None
    contato_principal: str | None = None
    telefone: str | None = None
    email: str | None = None
    ativo: bool | None = None
    plano_manutencao_ativo: bool | None = None
    observacoes: str | None = None


class ClienteRead(ClienteBase):
    id: UUID
    criado_em: datetime | None = None
    atualizado_em: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


# ── Local ────────────────────────────────────────────
class LocalBase(BaseModel):
    nome: str
    logradouro: str | None = None
    cidade: str | None = None
    estado: str | None = None
    cep: str | None = None


class LocalCreate(LocalBase):
    cliente_id: UUID


class LocalUpdate(BaseModel):
    nome: str | None = None
    logradouro: str | None = None
    cidade: str | None = None
    estado: str | None = None
    cep: str | None = None


class LocalRead(LocalBase):
    id: UUID
    cliente_id: UUID
    criado_em: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


# ── Ambiente ─────────────────────────────────────────
class AmbienteBase(BaseModel):
    nome: str
    andar: str | None = None


class AmbienteCreate(AmbienteBase):
    local_id: UUID


class AmbienteUpdate(BaseModel):
    nome: str | None = None
    andar: str | None = None


class AmbienteRead(AmbienteBase):
    id: UUID
    local_id: UUID
    criado_em: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


# ── Equipamento ──────────────────────────────────────
class EquipamentoBase(BaseModel):
    marca: str
    linha: str | None = None
    modelo: str | None = None
    capacidade_btu: int | None = None
    voltagem: str | None = None
    cor: str = "Branca"
    numero_serie: str | None = None
    data_instalacao: date | None = None
    status: str = "ATIVO"


class EquipamentoCreate(EquipamentoBase):
    ambiente_id: UUID


class EquipamentoUpdate(BaseModel):
    marca: str | None = None
    linha: str | None = None
    modelo: str | None = None
    capacidade_btu: int | None = None
    voltagem: str | None = None
    cor: str | None = None
    numero_serie: str | None = None
    data_instalacao: date | None = None
    ultima_manutencao: date | None = None
    status: str | None = None


class EquipamentoRead(EquipamentoBase):
    id: UUID
    ambiente_id: UUID
    ultima_manutencao: date | None = None
    criado_em: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


# ── Técnico ──────────────────────────────────────────
class TecnicoBase(BaseModel):
    nome: str
    telefone: str | None = None
    email: str | None = None
    ativo: bool = True


class TecnicoCreate(TecnicoBase):
    pass


class TecnicoUpdate(BaseModel):
    nome: str | None = None
    telefone: str | None = None
    email: str | None = None
    ativo: bool | None = None


class TecnicoRead(TecnicoBase):
    id: UUID
    criado_em: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


# ── Ordem de Serviço ─────────────────────────────────
class OSCreate(BaseModel):
    cliente_id: UUID
    local_id: UUID
    tipo_servico: str
    descricao_problema: str | None = None
    fabricante_garantia: str | None = None
    tecnico_responsavel_id: UUID | None = None
    data_agendamento: datetime | None = None
    equipamento_ids: list[UUID] = Field(default_factory=list)


class OSUpdate(BaseModel):
    status: OrdemStatus | None = None
    descricao_problema: str | None = None
    diagnostico_tecnico: str | None = None
    descricao_servico: str | None = None
    motivo_cancelamento: str | None = None
    fabricante_garantia: str | None = None
    valor_mao_obra: float | None = None
    valor_materiais: float | None = None
    valor_total: float | None = None
    km_percorrido: float | None = None
    data_primeira_visita: date | None = None
    data_segunda_visita: date | None = None
    data_agendamento: datetime | None = None
    data_conclusao: datetime | None = None
    tecnico_responsavel_id: UUID | None = None
    assinatura_cliente: str | None = None


class OSRead(BaseModel):
    id: UUID
    numero_os: int | None = None
    cliente_id: UUID
    local_id: UUID
    contrato_id: UUID | None = None
    tipo_servico: str
    status: OrdemStatus
    created_by: OrdemOrigem
    criado_por_usuario: int | None = None
    descricao_problema: str | None = None
    diagnostico_tecnico: str | None = None
    descricao_servico: str | None = None
    motivo_cancelamento: str | None = None
    fabricante_garantia: str | None = None
    valor_mao_obra: float | None = None
    valor_materiais: float | None = None
    valor_total: float | None = None
    km_percorrido: float | None = None
    data_primeira_visita: date | None = None
    data_segunda_visita: date | None = None
    data_agendamento: datetime | None = None
    data_conclusao: datetime | None = None
    data_encerramento: datetime | None = None
    tecnico_responsavel_id: UUID | None = None
    criado_em: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


# ── Checklist ────────────────────────────────────────
class ChecklistCreate(BaseModel):
    ordem_servico_id: UUID
    tamanho_tubulacao: str | None = None
    pressao_fluido: str | None = None
    distancia_condensador_teto: str | None = None
    distancia_evaporador_teto: str | None = None
    erro_instalacao_previa: bool = False
    observacoes: str | None = None


class ChecklistRead(ChecklistCreate):
    id: UUID
    criado_em: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


# ── Materiais ────────────────────────────────────────
class MaterialCreate(BaseModel):
    ordem_servico_id: UUID
    item: str
    quantidade: float = 1
    unidade: str = "unidades"
    valor_unitario: float = 0


class MaterialRead(MaterialCreate):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


# ── Fotos ────────────────────────────────────────────
class FotoCreate(BaseModel):
    ordem_servico_id: UUID
    url_arquivo: str
    url_thumb: str | None = None
    categoria: FotoCategoria
    descricao: str | None = None
    mime_type: str | None = None
    tamanho_bytes: int | None = None
    largura_px: int | None = None
    altura_px: int | None = None
    hash_sha256: str | None = None
    duplicada_de_foto_id: UUID | None = None
    foto_principal: bool = False
    status_arquivo: str = "ATIVO"
    criado_por_usuario: int | None = None


class FotoRead(FotoCreate):
    id: UUID
    criado_em: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class FotoListRead(BaseModel):
    items: list[FotoRead]
    page: int
    limit: int
    total: int


class HistoricoRead(BaseModel):
    id: UUID
    ordem_servico_id: UUID
    status_anterior: OrdemStatus | None = None
    status_novo: OrdemStatus
    observacao: str | None = None
    usuario_id: int | None = None
    criado_em: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


# ── Contrato de Manutenção ───────────────────────────
class ContratoCreate(BaseModel):
    cliente_id: UUID
    descricao: str | None = None
    periodicidade_dias: int | None = None
    tipo_servico: str | None = None
    ativo: bool = True
    data_inicio: date | None = None
    data_fim: date | None = None
    local_ids: list[UUID] = []


class ContratoUpdate(BaseModel):
    descricao: str | None = None
    periodicidade_dias: int | None = None
    tipo_servico: str | None = None
    ativo: bool | None = None
    data_inicio: date | None = None
    data_fim: date | None = None


class ContratoRead(BaseModel):
    id: UUID
    cliente_id: UUID
    descricao: str | None = None
    periodicidade_dias: int | None = None
    tipo_servico: str | None = None
    ativo: bool
    data_inicio: date | None = None
    data_fim: date | None = None
    criado_em: datetime | None = None
    model_config = ConfigDict(from_attributes=True)
