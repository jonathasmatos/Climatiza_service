from enum import Enum


class OrdemStatus(str, Enum):
    NOVO = "NOVO"
    AGENDADO = "AGENDADO"
    EM_ATENDIMENTO = "EM_ATENDIMENTO"
    AGUARDANDO = "AGUARDANDO"
    RESOLVIDO = "RESOLVIDO"
    FECHADO = "FECHADO"
    CANCELADO = "CANCELADO"


class OrdemOrigem(str, Enum):
    ADMIN = "ADMIN"
    EXECUTOR = "EXECUTOR"
    SISTEMA = "SISTEMA"


class FotoCategoria(str, Enum):
    ANTES = "ANTES"
    DEPOIS = "DEPOIS"
    PLACA_EQUIPAMENTO = "PLACA_EQUIPAMENTO"
    DEFEITO = "DEFEITO"


LEGACY_STATUS_MAP = {
    "ABERTA": OrdemStatus.NOVO.value,
    "AGENDADA": OrdemStatus.AGENDADO.value,
    "CONCLUIDA": OrdemStatus.RESOLVIDO.value,
    "ENCERRADA": OrdemStatus.FECHADO.value,
}


VALID_STATUS_TRANSITIONS = {
    OrdemStatus.NOVO.value: {OrdemStatus.AGENDADO.value, OrdemStatus.CANCELADO.value},
    OrdemStatus.AGENDADO.value: {OrdemStatus.EM_ATENDIMENTO.value, OrdemStatus.CANCELADO.value},
    OrdemStatus.EM_ATENDIMENTO.value: {OrdemStatus.RESOLVIDO.value, OrdemStatus.AGUARDANDO.value},
    OrdemStatus.AGUARDANDO.value: {OrdemStatus.EM_ATENDIMENTO.value},
    OrdemStatus.RESOLVIDO.value: {OrdemStatus.FECHADO.value},
    OrdemStatus.FECHADO.value: set(),
    OrdemStatus.CANCELADO.value: set(),
}


def normalize_ordem_status(status: str | None) -> str | None:
    if status is None:
        return None
    normalized = status.strip().upper()
    return LEGACY_STATUS_MAP.get(normalized, normalized)


def ensure_valid_ordem_status(status: str | None) -> str | None:
    normalized = normalize_ordem_status(status)
    if normalized is None:
        return None
    if normalized not in OrdemStatus._value2member_map_:
        valid = ", ".join(item.value for item in OrdemStatus)
        raise ValueError(f"Status inválido: {status}. Use um de: {valid}")
    return normalized


def can_transition_ordem_status(from_status: str | None, to_status: str) -> bool:
    origin = ensure_valid_ordem_status(from_status)
    target = ensure_valid_ordem_status(to_status)
    if origin is None:
        return target == OrdemStatus.NOVO.value
    return target in VALID_STATUS_TRANSITIONS[origin]