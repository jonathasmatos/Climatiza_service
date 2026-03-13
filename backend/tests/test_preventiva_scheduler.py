from datetime import date, timedelta

from app.db.models import ContratoLocal, ContratoManutencao, OrdemServico
from app.services.preventiva_scheduler import gerar_os_preventivas


def test_scheduler_gera_preventiva_e_evitaria_duplicidade(db_session, cliente_ativo, local_ativo, equipamento_ativo):
    equipamento_ativo.ultima_manutencao = date.today() - timedelta(days=45)
    contrato = ContratoManutencao(
        cliente_id=cliente_ativo.id,
        descricao="Preventiva mensal",
        periodicidade_dias=30,
        tipo_servico="PREVENTIVA",
        ativo=True,
    )
    db_session.add(contrato)
    db_session.flush()
    db_session.add(ContratoLocal(contrato_id=contrato.id, local_id=local_ativo.id))
    db_session.commit()

    primeira_execucao = gerar_os_preventivas(db_session)
    segunda_execucao = gerar_os_preventivas(db_session)

    ordens = db_session.query(OrdemServico).all()
    assert len(primeira_execucao) == 1
    assert segunda_execucao == []
    assert len(ordens) == 1
    assert ordens[0].created_by == "SISTEMA"


def test_scheduler_ignora_cliente_inativo(db_session, cliente_ativo, local_ativo, equipamento_ativo):
    cliente_ativo.ativo = False
    equipamento_ativo.ultima_manutencao = date.today() - timedelta(days=45)
    contrato = ContratoManutencao(
        cliente_id=cliente_ativo.id,
        descricao="Preventiva mensal",
        periodicidade_dias=30,
        tipo_servico="PREVENTIVA",
        ativo=True,
    )
    db_session.add(contrato)
    db_session.flush()
    db_session.add(ContratoLocal(contrato_id=contrato.id, local_id=local_ativo.id))
    db_session.commit()

    resultado = gerar_os_preventivas(db_session)

    assert resultado == []