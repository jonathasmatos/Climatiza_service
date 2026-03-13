import pytest
from fastapi import HTTPException

from app.core.states import FotoCategoria, OrdemStatus
from app.db.models import ChecklistTecnico, OSFoto
from app.rotas.dominio_routes import atualizar_ordem, criar_ordem
from app.schemas.dominio import OSCreate, OSUpdate


def test_criar_ordem_exige_pelo_menos_um_equipamento(db_session, admin_user, cliente_ativo, local_ativo):
    body = OSCreate(
        cliente_id=cliente_ativo.id,
        local_id=local_ativo.id,
        tipo_servico="CORRETIVA",
        equipamento_ids=[],
    )

    with pytest.raises(HTTPException) as exc:
        criar_ordem(body, db_session, admin_user)

    assert exc.value.status_code == 422
    assert "pelo menos 1 equipamento" in exc.value.detail


def test_resolvido_exige_checklist_e_fotos(db_session, admin_user, cliente_ativo, local_ativo, equipamento_ativo):
    ordem = criar_ordem(
        OSCreate(
            cliente_id=cliente_ativo.id,
            local_id=local_ativo.id,
            tipo_servico="CORRETIVA",
            equipamento_ids=[equipamento_ativo.id],
        ),
        db_session,
        admin_user,
    )

    atualizar_ordem(ordem.id, OSUpdate(status=OrdemStatus.AGENDADO), db_session, admin_user)
    atualizar_ordem(ordem.id, OSUpdate(status=OrdemStatus.EM_ATENDIMENTO), db_session, admin_user)

    with pytest.raises(HTTPException) as exc:
        atualizar_ordem(ordem.id, OSUpdate(status=OrdemStatus.RESOLVIDO), db_session, admin_user)

    assert exc.value.status_code == 422
    assert "Checklist técnico é obrigatório" in exc.value.detail


def test_fechado_exige_km_positivo(db_session, admin_user, cliente_ativo, local_ativo, equipamento_ativo):
    ordem = criar_ordem(
        OSCreate(
            cliente_id=cliente_ativo.id,
            local_id=local_ativo.id,
            tipo_servico="CORRETIVA",
            equipamento_ids=[equipamento_ativo.id],
        ),
        db_session,
        admin_user,
    )

    atualizar_ordem(ordem.id, OSUpdate(status=OrdemStatus.AGENDADO), db_session, admin_user)
    atualizar_ordem(ordem.id, OSUpdate(status=OrdemStatus.EM_ATENDIMENTO), db_session, admin_user)

    db_session.add(ChecklistTecnico(ordem_servico_id=ordem.id))
    db_session.add(OSFoto(ordem_servico_id=ordem.id, url_arquivo="antes.jpg", categoria=FotoCategoria.ANTES.value))
    db_session.add(OSFoto(ordem_servico_id=ordem.id, url_arquivo="depois.jpg", categoria=FotoCategoria.DEPOIS.value))
    db_session.commit()

    atualizar_ordem(ordem.id, OSUpdate(status=OrdemStatus.RESOLVIDO), db_session, admin_user)

    with pytest.raises(HTTPException) as exc:
        atualizar_ordem(ordem.id, OSUpdate(status=OrdemStatus.FECHADO, km_percorrido=0), db_session, admin_user)

    assert exc.value.status_code == 422
    assert "km_percorrido deve ser maior que zero" in exc.value.detail
