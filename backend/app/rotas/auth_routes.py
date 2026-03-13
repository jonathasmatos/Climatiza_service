"""Climatiza — Rotas de Auth"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Usuario
from app.auth.dependencies import get_current_user, require_roles
from app.auth import services as auth_svc
from app.auth.security import hash_password
from app.schemas.auth import LoginRequest, LoginResponse, RefreshRequest, UserRead, UserCreate, UserUpdate

router = APIRouter(prefix="/auth", tags=["Auth"])

PERFIS_VALIDOS = {"ADMIN", "GESTOR", "TECNICO"}


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    result = auth_svc.login(db, body.email, body.senha)
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    return result


@router.post("/refresh", response_model=LoginResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    result = auth_svc.refresh(db, body.refresh_token)
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh inválido ou expirado")
    return result


@router.post("/logout")
def logout(body: RefreshRequest, db: Session = Depends(get_db)):
    auth_svc.logout(db, body.refresh_token)
    return {"ok": True}


@router.get("/me", response_model=UserRead)
def me(user: Usuario = Depends(get_current_user)):
    return user


@router.post("/change-password")
def change_password(body: dict, user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    ok = auth_svc.change_password(db, user, body.get("senha_atual", ""), body.get("nova_senha", ""))
    if not ok:
        raise HTTPException(400, "Senha atual incorreta ou nova senha fraca (mín. 8 chars)")
    return {"ok": True}


@router.post("/forgot-password")
def forgot(body: dict, db: Session = Depends(get_db)):
    auth_svc.request_password_reset(db, body.get("email", ""))
    return {"ok": True, "mensagem": "Se o email existir, link de reset será enviado"}


@router.post("/reset-password")
def reset(body: dict, db: Session = Depends(get_db)):
    ok = auth_svc.reset_password(db, body.get("token", ""), body.get("nova_senha", ""))
    if not ok:
        raise HTTPException(400, "Token inválido ou expirado")
    return {"ok": True}


# ── CRUD Usuários (ADMIN only) ──────────────────────

@router.get("/users", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db), admin: Usuario = Depends(require_roles("ADMIN"))):
    return db.query(Usuario).all()


@router.post("/users", response_model=UserRead, status_code=201)
def create_user(body: UserCreate, db: Session = Depends(get_db), admin: Usuario = Depends(require_roles("ADMIN"))):
    if body.perfil not in PERFIS_VALIDOS:
        raise HTTPException(400, f"Perfil inválido. Use: {PERFIS_VALIDOS}")
    exists = db.query(Usuario).filter(Usuario.email == body.email).first()
    if exists:
        raise HTTPException(409, "Email já cadastrado")
    u = auth_svc.create_user(db, body.nome, body.email, body.senha, body.perfil, body.telefone)
    return u


@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db), admin: Usuario = Depends(require_roles("ADMIN"))):
    u = db.get(Usuario, user_id)
    if not u:
        raise HTTPException(404, "Usuário não encontrado")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(u, k, v)
    db.commit()
    db.refresh(u)
    return u


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: Usuario = Depends(require_roles("ADMIN"))):
    u = db.get(Usuario, user_id)
    if not u:
        raise HTTPException(404, "Usuário não encontrado")
    u.ativo = False
    db.commit()
    return {"ok": True}


@router.post("/users/{user_id}/reset-password")
def admin_reset(user_id: int, db: Session = Depends(get_db), admin: Usuario = Depends(require_roles("ADMIN"))):
    token, expires = auth_svc.admin_generate_reset(db, admin, user_id)
    if not token:
        raise HTTPException(400, "Usuário não encontrado ou inelegível")
    return {"token": token, "expires_at": str(expires)}
