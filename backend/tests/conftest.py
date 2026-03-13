import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("AUTH_JWT_SECRET", "test-secret")
os.environ.setdefault("APP_ENV", "test")

from app.auth.services import create_user
from app.db.base import Base
from app.db.models import Ambiente, Cliente, Equipamento, Local, OrdemServico, Tecnico


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def admin_user(db_session):
    return create_user(db_session, "Admin Teste", "admin@test.local", "senha12345", "ADMIN")


@pytest.fixture
def tecnico_user(db_session):
    return create_user(db_session, "Tecnico Teste", "tecnico@test.local", "senha12345", "TECNICO")


@pytest.fixture
def cliente_ativo(db_session):
    cliente = Cliente(
        nome="Cliente Teste",
        email="cliente@test.local",
        ativo=True,
        plano_manutencao_ativo=True,
    )
    db_session.add(cliente)
    db_session.commit()
    db_session.refresh(cliente)
    return cliente


@pytest.fixture
def local_ativo(db_session, cliente_ativo):
    local = Local(cliente_id=cliente_ativo.id, nome="Matriz")
    db_session.add(local)
    db_session.commit()
    db_session.refresh(local)
    return local


@pytest.fixture
def ambiente_ativo(db_session, local_ativo):
    ambiente = Ambiente(local_id=local_ativo.id, nome="Recepcao")
    db_session.add(ambiente)
    db_session.commit()
    db_session.refresh(ambiente)
    return ambiente


@pytest.fixture
def equipamento_ativo(db_session, ambiente_ativo):
    equipamento = Equipamento(
        ambiente_id=ambiente_ativo.id,
        marca="LG",
        modelo="Split 12000",
        status="ATIVO",
    )
    db_session.add(equipamento)
    db_session.commit()
    db_session.refresh(equipamento)
    return equipamento


@pytest.fixture
def tecnico_responsavel(db_session):
    tecnico = Tecnico(nome="Tecnico Campo", ativo=True)
    db_session.add(tecnico)
    db_session.commit()
    db_session.refresh(tecnico)
    return tecnico


@pytest.fixture
def ordem_basica(db_session, cliente_ativo, local_ativo):
    os = OrdemServico(
        cliente_id=cliente_ativo.id,
        local_id=local_ativo.id,
        tipo_servico="CORRETIVA",
        status="NOVO",
        created_by="ADMIN",
    )
    db_session.add(os)
    db_session.commit()
    db_session.refresh(os)
    return os
