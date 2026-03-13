"""Climatiza — Rotas de domínio (CRUD completo de todas entidades)"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import (
    Usuario, Cliente, Local, Ambiente, Equipamento, Tecnico,
    OrdemServico, OSEquipamento, ChecklistTecnico, OSMaterial, OSFoto,
    HistoricoOS, ContratoManutencao, ContratoLocal
)
from app.auth.dependencies import get_current_user
from app.core.states import (
    FotoCategoria,
    OrdemOrigem,
    OrdemStatus,
    can_transition_ordem_status,
    ensure_valid_ordem_status,
)
from app.schemas.dominio import (
    ClienteCreate, ClienteUpdate, ClienteRead,
    LocalCreate, LocalUpdate, LocalRead,
    AmbienteCreate, AmbienteUpdate, AmbienteRead,
    EquipamentoCreate, EquipamentoUpdate, EquipamentoRead,
    TecnicoCreate, TecnicoUpdate, TecnicoRead,
    OSCreate, OSUpdate, OSRead,
    ChecklistCreate, ChecklistRead,
    MaterialCreate, MaterialRead,
    FotoCreate, FotoRead, FotoListRead, HistoricoRead,
    ContratoCreate, ContratoUpdate, ContratoRead,
)

from datetime import datetime, timezone
from app.services.preventiva_scheduler import gerar_os_preventivas
from app.services.image_storage import processar_upload_foto

router = APIRouter(tags=["Climatiza"])


def _now():
    return datetime.now(timezone.utc)


def _resolver_origem_os(user: Usuario) -> OrdemOrigem:
    return OrdemOrigem.ADMIN if user.perfil == "ADMIN" else OrdemOrigem.EXECUTOR


def _carregar_equipamentos_validos(db: Session, equipamento_ids: list[UUID]) -> list[Equipamento]:
    equipamentos = db.query(Equipamento).filter(Equipamento.id.in_(equipamento_ids)).all()
    if len(equipamentos) != len(set(equipamento_ids)):
        raise HTTPException(422, "Todos os equipamentos da OS devem existir")
    return equipamentos


def _validar_equipamentos_da_os(db: Session, cliente_id: UUID, local_id: UUID, equipamento_ids: list[UUID]) -> list[Equipamento]:
    if not equipamento_ids:
        raise HTTPException(422, "A OS deve possuir pelo menos 1 equipamento")
    equipamentos = _carregar_equipamentos_validos(db, equipamento_ids)
    for equipamento in equipamentos:
        ambiente = equipamento.ambiente
        if ambiente is None or ambiente.local is None:
            raise HTTPException(422, "Equipamento sem vinculo completo de ambiente/local")
        if ambiente.local_id != local_id:
            raise HTTPException(422, "Todos os equipamentos devem pertencer ao local informado")
        if ambiente.local.cliente_id != cliente_id:
            raise HTTPException(422, "Todos os equipamentos devem pertencer ao cliente informado")
    return equipamentos


def _validar_requisitos_resolucao(os: OrdemServico) -> None:
    if os.checklist is None:
        raise HTTPException(422, "Checklist técnico é obrigatório para marcar a OS como RESOLVIDO")
    categorias = {foto.categoria for foto in os.fotos}
    obrigatorias = {FotoCategoria.ANTES.value, FotoCategoria.DEPOIS.value}
    faltantes = obrigatorias - categorias
    if faltantes:
        faltantes_str = ", ".join(sorted(faltantes))
        raise HTTPException(422, f"Faltam evidências obrigatórias para RESOLVIDO: {faltantes_str}")


def _validar_requisitos_fechamento(os: OrdemServico, updates: dict) -> None:
    km = updates.get("km_percorrido", os.km_percorrido)
    if km is None:
        raise HTTPException(422, "km_percorrido é obrigatório para FECHADO")
    if float(km) <= 0:
        raise HTTPException(422, "km_percorrido deve ser maior que zero para FECHADO")


# ═══════════════════════════════════════════════════
# CLIENTES
# ═══════════════════════════════════════════════════

@router.get("/clientes", response_model=list[ClienteRead])
def listar_clientes(
    skip: int = 0,
    limit: int = 100,
    ativo: bool | None = Query(None, description="Filtrar por ativo (true/false)"),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    q = db.query(Cliente)
    if ativo is not None:
        q = q.filter(Cliente.ativo == ativo)
    return q.offset(skip).limit(limit).all()


@router.get("/clientes/{id}", response_model=ClienteRead)
def obter_cliente(id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    c = db.get(Cliente, id)
    if not c:
        raise HTTPException(404, "Cliente não encontrado")
    return c


@router.post("/clientes", response_model=ClienteRead, status_code=201)
def criar_cliente(body: ClienteCreate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    c = Cliente(**body.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.patch("/clientes/{id}", response_model=ClienteRead)
def atualizar_cliente(id: UUID, body: ClienteUpdate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    c = db.get(Cliente, id)
    if not c:
        raise HTTPException(404, "Cliente não encontrado")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/clientes/{id}")
def deletar_cliente(id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    c = db.get(Cliente, id)
    if not c:
        raise HTTPException(404, "Cliente não encontrado")
    db.delete(c)
    db.commit()
    return {"ok": True}


# ═══════════════════════════════════════════════════
# LOCAIS
# ═══════════════════════════════════════════════════

@router.get("/locais", response_model=list[LocalRead])
def listar_locais(cliente_id: UUID | None = None, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    q = db.query(Local)
    if cliente_id:
        q = q.filter(Local.cliente_id == cliente_id)
    return q.all()


@router.get("/locais/{id}", response_model=LocalRead)
def obter_local(id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.get(Local, id)
    if not r:
        raise HTTPException(404, "Local não encontrado")
    return r


@router.post("/locais", response_model=LocalRead, status_code=201)
def criar_local(body: LocalCreate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = Local(**body.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.patch("/locais/{id}", response_model=LocalRead)
def atualizar_local(id: UUID, body: LocalUpdate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.get(Local, id)
    if not r:
        raise HTTPException(404, "Local não encontrado")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/locais/{id}")
def deletar_local(id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.get(Local, id)
    if not r:
        raise HTTPException(404, "Local não encontrado")
    db.delete(r)
    db.commit()
    return {"ok": True}


# ═══════════════════════════════════════════════════
# AMBIENTES
# ═══════════════════════════════════════════════════

@router.get("/ambientes", response_model=list[AmbienteRead])
def listar_ambientes(local_id: UUID | None = None, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    q = db.query(Ambiente)
    if local_id:
        q = q.filter(Ambiente.local_id == local_id)
    return q.all()


@router.get("/ambientes/{id}", response_model=AmbienteRead)
def obter_ambiente(id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.get(Ambiente, id)
    if not r:
        raise HTTPException(404, "Ambiente não encontrado")
    return r


@router.post("/ambientes", response_model=AmbienteRead, status_code=201)
def criar_ambiente(body: AmbienteCreate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = Ambiente(**body.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.patch("/ambientes/{id}", response_model=AmbienteRead)
def atualizar_ambiente(id: UUID, body: AmbienteUpdate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.get(Ambiente, id)
    if not r:
        raise HTTPException(404, "Ambiente não encontrado")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/ambientes/{id}")
def deletar_ambiente(id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.get(Ambiente, id)
    if not r:
        raise HTTPException(404, "Ambiente não encontrado")
    db.delete(r)
    db.commit()
    return {"ok": True}


# ═══════════════════════════════════════════════════
# EQUIPAMENTOS
# ═══════════════════════════════════════════════════

@router.get("/equipamentos", response_model=list[EquipamentoRead])
def listar_equipamentos(
    ambiente_id: UUID | None = None,
    status: str | None = Query(None, description="Filtrar por status: ATIVO, INATIVO, EM_GARANTIA"),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    q = db.query(Equipamento)
    if ambiente_id:
        q = q.filter(Equipamento.ambiente_id == ambiente_id)
    if status:
        q = q.filter(Equipamento.status == status.upper())
    return q.all()


@router.get("/equipamentos/{id}", response_model=EquipamentoRead)
def obter_equipamento(id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.get(Equipamento, id)
    if not r:
        raise HTTPException(404, "Equipamento não encontrado")
    return r


@router.post("/equipamentos", response_model=EquipamentoRead, status_code=201)
def criar_equipamento(body: EquipamentoCreate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = Equipamento(**body.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.patch("/equipamentos/{id}", response_model=EquipamentoRead)
def atualizar_equipamento(id: UUID, body: EquipamentoUpdate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.get(Equipamento, id)
    if not r:
        raise HTTPException(404, "Equipamento não encontrado")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/equipamentos/{id}")
def deletar_equipamento(id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.get(Equipamento, id)
    if not r:
        raise HTTPException(404, "Equipamento não encontrado")
    db.delete(r)
    db.commit()
    return {"ok": True}


# ═══════════════════════════════════════════════════
# TÉCNICOS
# ═══════════════════════════════════════════════════

@router.get("/tecnicos", response_model=list[TecnicoRead])
def listar_tecnicos(db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    return db.query(Tecnico).all()


@router.get("/tecnicos/{id}", response_model=TecnicoRead)
def obter_tecnico(id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.get(Tecnico, id)
    if not r:
        raise HTTPException(404, "Técnico não encontrado")
    return r


@router.post("/tecnicos", response_model=TecnicoRead, status_code=201)
def criar_tecnico(body: TecnicoCreate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = Tecnico(**body.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.patch("/tecnicos/{id}", response_model=TecnicoRead)
def atualizar_tecnico(id: UUID, body: TecnicoUpdate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.get(Tecnico, id)
    if not r:
        raise HTTPException(404, "Técnico não encontrado")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/tecnicos/{id}")
def deletar_tecnico(id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.get(Tecnico, id)
    if not r:
        raise HTTPException(404, "Técnico não encontrado")
    r.ativo = False
    db.commit()
    return {"ok": True}


# ═══════════════════════════════════════════════════
# ORDENS DE SERVIÇO
# ═══════════════════════════════════════════════════

@router.get("/ordens", response_model=list[OSRead])
def listar_ordens(
    status: str | None = None,
    cliente_id: UUID | None = None,
    tecnico_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    q = db.query(OrdemServico)
    if status:
        try:
            status = ensure_valid_ordem_status(status)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        q = q.filter(OrdemServico.status == status)
    if cliente_id:
        q = q.filter(OrdemServico.cliente_id == cliente_id)
    if tecnico_id:
        q = q.filter(OrdemServico.tecnico_responsavel_id == tecnico_id)
    return q.order_by(OrdemServico.criado_em.desc()).offset(skip).limit(limit).all()


@router.get("/ordens/{id}", response_model=OSRead)
def obter_ordem(id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.get(OrdemServico, id)
    if not r:
        raise HTTPException(404, "OS não encontrada")
    return r


@router.post("/ordens", response_model=OSRead, status_code=201)
def criar_ordem(body: OSCreate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    _validar_equipamentos_da_os(db, body.cliente_id, body.local_id, body.equipamento_ids)
    data = body.model_dump(exclude={"equipamento_ids"})
    data["status"] = OrdemStatus.NOVO.value
    data["created_by"] = _resolver_origem_os(user).value
    data["criado_por_usuario"] = user.id
    os = OrdemServico(**data)
    db.add(os)
    db.flush()
    for eq_id in body.equipamento_ids:
        db.add(OSEquipamento(ordem_servico_id=os.id, equipamento_id=eq_id))
    db.add(HistoricoOS(
        ordem_servico_id=os.id, status_anterior=None, status_novo=OrdemStatus.NOVO.value,
        observacao="OS criada", usuario_id=user.id, criado_em=_now()
    ))
    db.commit()
    db.refresh(os)
    return os


@router.get("/ordens/{id}/historico", response_model=list[HistoricoRead])
def listar_historico_ordem(id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    os = db.get(OrdemServico, id)
    if not os:
        raise HTTPException(404, "OS não encontrada")
    return db.query(HistoricoOS).filter(HistoricoOS.ordem_servico_id == id).order_by(HistoricoOS.criado_em.asc()).all()


@router.post("/ordens/{id}/fotos", response_model=FotoRead, status_code=201)
def upload_foto_ordem(
    id: UUID,
    categoria: FotoCategoria = Form(...),
    arquivo: UploadFile = File(...),
    descricao: str | None = Form(None),
    foto_principal: bool = Form(False),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    return processar_upload_foto(
        db=db,
        ordem_servico_id=id,
        upload=arquivo,
        categoria=categoria.value,
        descricao=descricao,
        foto_principal=foto_principal,
        criado_por_usuario=user.id,
    )


@router.get("/ordens/{id}/fotos", response_model=FotoListRead)
def listar_fotos_ordem(
    id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    os = db.get(OrdemServico, id)
    if not os:
        raise HTTPException(404, "OS não encontrada")

    total = db.query(OSFoto).filter(OSFoto.ordem_servico_id == id).count()
    items = (
        db.query(OSFoto)
        .filter(OSFoto.ordem_servico_id == id)
        .order_by(OSFoto.criado_em.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return {"items": items, "page": page, "limit": limit, "total": total}


@router.patch("/ordens/{id}", response_model=OSRead)
def atualizar_ordem(id: UUID, body: OSUpdate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    os = db.get(OrdemServico, id)
    if not os:
        raise HTTPException(404, "OS não encontrada")
    old_status = ensure_valid_ordem_status(os.status)
    os.status = old_status
    updates = body.model_dump(exclude_unset=True)
    if "status" in updates and updates["status"] is not None:
        try:
            updates["status"] = ensure_valid_ordem_status(updates["status"])
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
    new_status = updates.get("status")
    if new_status and not can_transition_ordem_status(old_status, new_status):
        raise HTTPException(422, f"Transição inválida: {old_status} -> {new_status}")
    if new_status == OrdemStatus.CANCELADO.value:
        motivo_cancelamento = (updates.get("motivo_cancelamento") or os.motivo_cancelamento or "").strip()
        if not motivo_cancelamento:
            raise HTTPException(422, "Motivo de cancelamento é obrigatório para status CANCELADO")
        updates["motivo_cancelamento"] = motivo_cancelamento
    elif new_status == OrdemStatus.RESOLVIDO.value:
        _validar_requisitos_resolucao(os)
    elif new_status == OrdemStatus.FECHADO.value:
        _validar_requisitos_fechamento(os, updates)
    elif "motivo_cancelamento" in updates and updates["motivo_cancelamento"] is not None:
        updates["motivo_cancelamento"] = updates["motivo_cancelamento"].strip() or None
    for k, v in updates.items():
        setattr(os, k, v)
    if new_status and new_status != old_status:
        db.add(HistoricoOS(
            ordem_servico_id=os.id, status_anterior=old_status, status_novo=new_status,
            usuario_id=user.id, criado_em=_now()
        ))
        if new_status == OrdemStatus.RESOLVIDO.value:
            os.data_conclusao = _now()
            for os_equipamento in os.os_equipamentos:
                os_equipamento.equipamento.ultima_manutencao = _now().date()
        elif new_status in {OrdemStatus.FECHADO.value, OrdemStatus.CANCELADO.value}:
            os.data_encerramento = _now()
    db.commit()
    db.refresh(os)
    return os


@router.delete("/ordens/{id}")
def deletar_ordem(id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    os = db.get(OrdemServico, id)
    if not os:
        raise HTTPException(404, "OS não encontrada")
    db.delete(os)
    db.commit()
    return {"ok": True}


# ═══════════════════════════════════════════════════
# AUTOMAÇÃO PREVENTIVA
# ═══════════════════════════════════════════════════

@router.post("/admin/preventivas/gerar", status_code=200, tags=["Admin"])
def forcar_geracao_preventivas(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    """
    Dispara manualmente a geração de OS preventivas para todos os contratos ativos.
    Proteção anti-duplicidade garantida: não gera OS se já existe uma aberta
    para o mesmo contrato + local.
    Restrito a perfil ADMIN.
    """
    if user.perfil != "ADMIN":
        raise HTTPException(403, "Apenas administradores podem forçar a geração de preventivas")
    geradas = gerar_os_preventivas(db)
    return {"geradas": len(geradas), "detalhe": geradas}


# ═══════════════════════════════════════════════════
# CHECKLIST TÉCNICO
# ═══════════════════════════════════════════════════

@router.post("/checklist", response_model=ChecklistRead, status_code=201)
def criar_checklist(body: ChecklistCreate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = ChecklistTecnico(**body.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.get("/checklist/{os_id}", response_model=ChecklistRead)
def obter_checklist(os_id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.query(ChecklistTecnico).filter(ChecklistTecnico.ordem_servico_id == os_id).first()
    if not r:
        raise HTTPException(404, "Checklist não encontrado")
    return r


# ═══════════════════════════════════════════════════
# MATERIAIS
# ═══════════════════════════════════════════════════

@router.post("/materiais", response_model=MaterialRead, status_code=201)
def criar_material(body: MaterialCreate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = OSMaterial(**body.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.get("/materiais", response_model=list[MaterialRead])
def listar_materiais(os_id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    return db.query(OSMaterial).filter(OSMaterial.ordem_servico_id == os_id).all()


@router.delete("/materiais/{id}")
def deletar_material(id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.get(OSMaterial, id)
    if not r:
        raise HTTPException(404, "Material não encontrado")
    db.delete(r)
    db.commit()
    return {"ok": True}


# ═══════════════════════════════════════════════════
# FOTOS
# ═══════════════════════════════════════════════════

@router.post("/fotos", response_model=FotoRead, status_code=201)
def criar_foto(body: FotoCreate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = OSFoto(**body.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.get("/fotos", response_model=list[FotoRead])
def listar_fotos(os_id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    return db.query(OSFoto).filter(OSFoto.ordem_servico_id == os_id).all()


@router.get("/fotos/{id}", response_model=FotoRead)
def obter_foto(id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.get(OSFoto, id)
    if not r:
        raise HTTPException(404, "Foto não encontrada")
    return r


@router.delete("/fotos/{id}")
def deletar_foto(id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.get(OSFoto, id)
    if not r:
        raise HTTPException(404, "Foto não encontrada")
    db.delete(r)
    db.commit()
    return {"ok": True}


# ═══════════════════════════════════════════════════
# CONTRATOS DE MANUTENÇÃO
# ═══════════════════════════════════════════════════

@router.get("/contratos", response_model=list[ContratoRead])
def listar_contratos(cliente_id: UUID | None = None, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    q = db.query(ContratoManutencao)
    if cliente_id:
        q = q.filter(ContratoManutencao.cliente_id == cliente_id)
    return q.all()


@router.get("/contratos/{id}", response_model=ContratoRead)
def obter_contrato(id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.get(ContratoManutencao, id)
    if not r:
        raise HTTPException(404, "Contrato não encontrado")
    return r


@router.post("/contratos", response_model=ContratoRead, status_code=201)
def criar_contrato(body: ContratoCreate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    data = body.model_dump(exclude={"local_ids"})
    c = ContratoManutencao(**data)
    db.add(c)
    db.flush()
    for lid in body.local_ids:
        db.add(ContratoLocal(contrato_id=c.id, local_id=lid))
    db.commit()
    db.refresh(c)
    return c


@router.patch("/contratos/{id}", response_model=ContratoRead)
def atualizar_contrato(id: UUID, body: ContratoUpdate, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.get(ContratoManutencao, id)
    if not r:
        raise HTTPException(404, "Contrato não encontrado")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/contratos/{id}")
def deletar_contrato(id: UUID, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.get(ContratoManutencao, id)
    if not r:
        raise HTTPException(404, "Contrato não encontrado")
    db.delete(r)
    db.commit()
    return {"ok": True}
