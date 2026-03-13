"""
Climatiza Service — Scheduler de OS Preventivas

Lógica por contrato ativo:
  Para cada local coberto pelo contrato:
    1. Coleta equipamentos ATIVO do local.
    2. Verifica se algum está vencido: ultima_manutencao + periodicidade_dias <= hoje
       (ou ultima_manutencao é None).
    3. Proteção anti-duplicidade: pula se já existe OS PREVENTIVA em aberto
       para o mesmo contrato + local (identifica via contrato_id na OS).
    4. Cria OS com tipo_servico=PREVENTIVA (ou o tipo do contrato),
       created_by=SISTEMA, criado_por_usuario=None.
    5. Registra HistoricoOS com observação de origem automática.

Retorna lista de dicts {os_id, numero_os, local_id, contrato_id} para cada OS criada.
"""

import logging
from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.states import OrdemOrigem, OrdemStatus
from app.db.models import (
    Ambiente,
    ContratoManutencao,
    Equipamento,
    HistoricoOS,
    Local,
    OrdemServico,
    OSEquipamento,
)

logger = logging.getLogger("climatiza.preventiva")

# Statuses que indicam OS ainda em aberto (não encerrada)
_STATUSES_ABERTOS = {
    OrdemStatus.NOVO.value,
    OrdemStatus.AGENDADO.value,
    OrdemStatus.EM_ATENDIMENTO.value,
    OrdemStatus.AGUARDANDO.value,
    OrdemStatus.RESOLVIDO.value,
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _equipamentos_ativos_do_local(db: Session, local_id: UUID) -> list[Equipamento]:
    """Retorna todos os equipamentos ATIVO vinculados ao local via Ambiente."""
    return (
        db.query(Equipamento)
        .join(Ambiente, Equipamento.ambiente_id == Ambiente.id)
        .filter(
            Ambiente.local_id == local_id,
            Equipamento.status == "ATIVO",
        )
        .all()
    )


def _precisa_manutencao(eq: Equipamento, periodicidade_dias: int) -> bool:
    """True se o equipamento nunca foi mantido ou está com a manutenção vencida."""
    if eq.ultima_manutencao is None:
        return True
    return (date.today() - eq.ultima_manutencao).days >= periodicidade_dias


def _os_preventiva_aberta_existe(db: Session, contrato_id: UUID, local_id: UUID) -> bool:
    """
    Proteção anti-duplicidade: verifica se já existe uma OS PREVENTIVA aberta
    gerada pelo mesmo contrato para o mesmo local.
    """
    return (
        db.query(OrdemServico)
        .filter(
            OrdemServico.contrato_id == contrato_id,
            OrdemServico.local_id == local_id,
            OrdemServico.tipo_servico == "PREVENTIVA",
            OrdemServico.status.in_(_STATUSES_ABERTOS),
        )
        .first()
        is not None
    )


def gerar_os_preventivas(db: Session) -> list[dict]:
    """
    Verifica todos os contratos ativos e gera OS preventivas onde necessário.

    Anti-duplicidade garantida por:
      - Verificação de OS aberta com mesmo contrato_id + local_id + tipo PREVENTIVA.

    Returns:
        Lista de dicts com {os_id, numero_os, local_id, contrato_id} para cada OS criada.
    """
    hoje = date.today()
    geradas: list[dict] = []

    contratos = (
        db.query(ContratoManutencao)
        .filter(
            ContratoManutencao.ativo == True,  # noqa: E712
            ContratoManutencao.periodicidade_dias.isnot(None),
        )
        .all()
    )

    for contrato in contratos:
        # Respeita data de encerramento do contrato
        if contrato.data_fim and contrato.data_fim < hoje:
            logger.debug("Contrato %s encerrado em %s — pulando", contrato.id, contrato.data_fim)
            continue

        tipo_servico = contrato.tipo_servico or "PREVENTIVA"

        for contrato_local in contrato.locais:
            local: Local | None = contrato_local.local
            if local is None:
                continue

            # Anti-duplicidade
            if _os_preventiva_aberta_existe(db, contrato.id, local.id):
                logger.debug(
                    "OS preventiva já aberta — contrato=%s local=%s — pulando",
                    contrato.id,
                    local.id,
                )
                continue

            equipamentos = _equipamentos_ativos_do_local(db, local.id)
            if not equipamentos:
                logger.debug("Nenhum equipamento ativo no local %s — pulando", local.id)
                continue

            # Não gera OS para clientes inativos
            if local.cliente and not local.cliente.ativo:
                logger.debug("Cliente %s inativo — pulando local %s", local.cliente_id, local.id)
                continue

            # Gera OS somente se ao menos 1 equipamento está vencido
            vencidos = [eq for eq in equipamentos if _precisa_manutencao(eq, contrato.periodicidade_dias)]
            if not vencidos:
                continue

            descricao = (
                f"OS preventiva gerada automaticamente pelo sistema. "
                f"Contrato: {contrato.descricao or str(contrato.id)}. "
                f"Periodicidade: {contrato.periodicidade_dias} dias. "
                f"Equipamentos vencidos: {len(vencidos)}/{len(equipamentos)}."
            )

            os = OrdemServico(
                cliente_id=local.cliente_id,
                local_id=local.id,
                contrato_id=contrato.id,
                tipo_servico=tipo_servico,
                status=OrdemStatus.NOVO.value,
                created_by=OrdemOrigem.SISTEMA.value,
                criado_por_usuario=None,
                descricao_problema=descricao,
            )
            db.add(os)
            db.flush()  # obtém os.id antes do commit

            # Vincula TODOS os equipamentos ativos do local (não apenas os vencidos)
            for eq in equipamentos:
                db.add(OSEquipamento(ordem_servico_id=os.id, equipamento_id=eq.id))

            db.add(
                HistoricoOS(
                    ordem_servico_id=os.id,
                    status_anterior=None,
                    status_novo=OrdemStatus.NOVO.value,
                    observacao=f"OS preventiva gerada automaticamente | contrato {contrato.id}",
                    usuario_id=None,
                    criado_em=_now(),
                )
            )

            db.commit()
            db.refresh(os)

            geradas.append(
                {
                    "os_id": str(os.id),
                    "numero_os": os.numero_os,
                    "local_id": str(local.id),
                    "contrato_id": str(contrato.id),
                }
            )
            logger.info(
                "OS preventiva criada: numero_os=%s | local=%s | contrato=%s",
                os.numero_os,
                local.id,
                contrato.id,
            )

    return geradas
