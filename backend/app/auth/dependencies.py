from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Usuario
from app.auth.security import jwt_decode


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Usuario:
    token = ""
    auth = request.headers.get("Authorization") or ""
    if auth.lower().startswith("bearer "):
        token = auth.split(" ", 1)[1].strip()

    if not token:
        token = request.cookies.get("access_token") or ""

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ausente ou sessão expirada")

    try:
        payload = jwt_decode(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    uid = int(payload.get("sub", 0))
    u = db.get(Usuario, uid)
    if not u or not u.ativo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inválido")
    return u


def require_roles(*roles: str):
    def dep(user: Usuario = Depends(get_current_user)):
        if roles and user.perfil not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente")
        return user
    return dep
