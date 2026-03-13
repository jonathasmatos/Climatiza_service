"""
Climatiza Service — Main Application
"""

import asyncio
import json
import logging
import traceback
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.errors import DomainError
from app.core.middleware import CorrelationIdMiddleware
from app.db.models import *  # noqa: F401,F403 — registra modelos no metadata
from app.auth.services import seed_admin_user
from app.db.session import SessionLocal
from app.services.preventiva_scheduler import gerar_os_preventivas

from app.rotas.auth_routes import router as auth_router
from app.rotas.dominio_routes import router as dominio_router

logger = logging.getLogger("climatiza.main")

_PREVENTIVA_INTERVALO_HORAS = 24


def _executar_preventivas_sync() -> None:
    """Executa a geração de OS preventivas em uma sessão de banco isolada."""
    db = SessionLocal()
    try:
        resultado = gerar_os_preventivas(db)
        if resultado:
            logger.info("Preventivas agendadas: %d OS geradas", len(resultado))
        else:
            logger.debug("Nenhuma nova OS preventiva gerada neste ciclo")
    except Exception:
        logger.exception("Erro ao executar geração de OS preventivas")
    finally:
        db.close()


async def _preventiva_loop() -> None:
    """
    Loop assíncrono que dispara a geração de OS preventivas periodicamente.
    Executa a função síncrona em thread pool para não bloquear o event loop.
    Aguarda o intervalo configurado antes de cada execução.
    """
    loop = asyncio.get_event_loop()
    while True:
        await asyncio.sleep(_PREVENTIVA_INTERVALO_HORAS * 3600)
        try:
            await loop.run_in_executor(None, _executar_preventivas_sync)
        except Exception:
            logger.exception("Erro inesperado no loop de preventivas")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: seed admin + inicia scheduler preventivo
    db = SessionLocal()
    try:
        seed_admin_user(db)
    finally:
        db.close()

    task = asyncio.create_task(_preventiva_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


settings = get_settings()

app = FastAPI(
    title="Climatiza Service API",
    description="Backend completo para gestão de ordens de serviço de climatização",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Correlation ID
app.add_middleware(CorrelationIdMiddleware)

# Static files (imagens)
storage_root = Path(settings.IMAGE_STORAGE_ROOT)
storage_root.mkdir(parents=True, exist_ok=True)
app.mount("/files", StaticFiles(directory=str(storage_root)), name="files")


# Handler de erros de domínio
@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    body = {"error": exc.code, "message": exc.message}
    if exc.hint:
        body["hint"] = exc.hint
    if exc.action:
        body["action"] = exc.action
    return JSONResponse(status_code=exc.status_code, content=body)


# Handler genérico
@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    import sys
    sys.stderr.write(f"[Climatiza] Unhandled: {traceback.format_exc()}\n")
    return JSONResponse(status_code=500, content={"error": "INTERNAL", "message": "Erro interno do servidor"})


# Registrar rotas
app.include_router(auth_router)
app.include_router(dominio_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "climatiza"}


@app.get("/")
def root():
    return {
        "service": "climatiza",
        "status": "ok",
        "docs": "/docs",
        "health": "/health"
    }
