from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db.models import Usuario, RefreshToken, PasswordResetToken, AuthEvento
from app.auth.security import hash_password, verify_password, jwt_encode, now_ts
from app.core.config import get_settings
import hashlib
import uuid


def create_user(db: Session, nome: str, email: str, senha: str, perfil: str, telefone: str | None = None) -> Usuario:
    u = Usuario(
        nome=nome, email=email, senha_hash=hash_password(senha),
        perfil=perfil, telefone=telefone, ativo=True,
        criado_em=datetime.now(timezone.utc)
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def issue_tokens(u: Usuario) -> dict:
    s = get_settings()
    access = jwt_encode({"sub": u.id, "perfil": u.perfil, "exp": now_ts() + s.AUTH_ACCESS_EXPIRES})
    refresh_raw = jwt_encode({"sub": u.id, "typ": "refresh", "exp": now_ts() + s.AUTH_REFRESH_EXPIRES})
    return {
        "access_token": access,
        "refresh_token": refresh_raw,
        "expires_in": s.AUTH_ACCESS_EXPIRES,
        "perfil": u.perfil,
        "nome": u.nome
    }


def login(db: Session, email: str, senha: str) -> dict:
    u = db.query(Usuario).filter(Usuario.email == email).first()
    if not u or not u.ativo or not verify_password(senha, u.senha_hash):
        return {}
    tokens = issue_tokens(u)
    s = get_settings()
    if s.AUTH_REFRESH_ENABLED == "1":
        try:
            token_hash = hashlib.sha256(tokens["refresh_token"].encode("utf-8")).hexdigest()
            rt = RefreshToken(
                usuario_id=u.id, token_hash=token_hash,
                expira_em=datetime.now(timezone.utc) + timedelta(seconds=s.AUTH_REFRESH_EXPIRES),
                revogado=False, criado_em=datetime.now(timezone.utc)
            )
            db.add(rt)
            db.commit()
        except Exception:
            pass
    else:
        tokens["refresh_token"] = ""
    return tokens


def _audit(db: Session, usuario_id: int | None, tipo: str):
    db.add(AuthEvento(usuario_id=usuario_id, tipo_evento=tipo, criado_em=datetime.now(timezone.utc)))
    db.commit()


def change_password(db: Session, user: Usuario, senha_atual: str, nova_senha: str) -> bool:
    if not verify_password(senha_atual, user.senha_hash):
        return False
    if len(nova_senha) < 8:
        return False
    user.senha_hash = hash_password(nova_senha)
    db.query(RefreshToken).filter(RefreshToken.usuario_id == user.id).delete()
    db.commit()
    _audit(db, user.id, "USUARIO_SENHA_ALTERADA")
    return True


def request_password_reset(db: Session, email: str) -> None:
    u = db.query(Usuario).filter(Usuario.email == email).first()
    if u and u.ativo:
        s = get_settings()
        token_raw = str(uuid.uuid4())
        token_hash = hashlib.sha256(token_raw.encode("utf-8")).hexdigest()
        expires = datetime.now(timezone.utc) + timedelta(seconds=s.AUTH_RESET_EXPIRES)
        pr = PasswordResetToken(
            user_id=u.id, token_hash=token_hash,
            expires_at=expires, used=False, criado_em=datetime.now(timezone.utc)
        )
        db.add(pr)
        _audit(db, u.id, "USUARIO_RESET_SOLICITADO")
        db.commit()
    return None


def reset_password(db: Session, token: str, nova_senha: str) -> bool:
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    pr = db.query(PasswordResetToken).filter(PasswordResetToken.token_hash == token_hash).first()
    if not pr or pr.used:
        return False
    expires_at = pr.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= datetime.now(timezone.utc):
        return False
    u = db.get(Usuario, pr.user_id)
    if not u or not u.ativo or len(nova_senha) < 8:
        return False
    u.senha_hash = hash_password(nova_senha)
    pr.used = True
    db.query(RefreshToken).filter(RefreshToken.usuario_id == u.id).delete()
    db.commit()
    _audit(db, u.id, "USUARIO_SENHA_RESETADA")
    return True


def admin_generate_reset(db: Session, admin: Usuario, usuario_id: int) -> tuple[str, datetime]:
    if admin.perfil not in ("ADMIN",):
        return "", datetime.now(timezone.utc)
    u = db.get(Usuario, usuario_id)
    if not u or not u.ativo:
        return "", datetime.now(timezone.utc)
    s = get_settings()
    token_raw = str(uuid.uuid4())
    token_hash = hashlib.sha256(token_raw.encode("utf-8")).hexdigest()
    expires = datetime.now(timezone.utc) + timedelta(seconds=s.AUTH_RESET_EXPIRES)
    pr = PasswordResetToken(
        user_id=u.id, token_hash=token_hash,
        expires_at=expires, used=False, criado_em=datetime.now(timezone.utc)
    )
    db.add(pr)
    db.commit()
    _audit(db, admin.id, "ADMIN_RESET_SENHA")
    return token_raw, expires


def refresh(db: Session, refresh_token: str) -> dict:
    import logging
    token_hash = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
    rt = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if not rt:
        return {}
    if rt.revogado:
        logging.warning("refresh_reason=REUSE_DETECTED revoke_all_for_user=1")
        db.query(RefreshToken).filter(RefreshToken.usuario_id == rt.usuario_id).update({"revogado": True})
        db.commit()
        return {}
    exp = rt.expira_em
    now = datetime.now(timezone.utc)
    if exp is None:
        return {}
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if exp <= now:
        return {}
    u = db.get(Usuario, rt.usuario_id)
    if not u or not u.ativo:
        return {}
    rt.revogado = True
    tokens = issue_tokens(u)
    try:
        new_hash = hashlib.sha256(tokens["refresh_token"].encode("utf-8")).hexdigest()
        new_rt = RefreshToken(
            usuario_id=u.id, token_hash=new_hash,
            expira_em=datetime.now(timezone.utc) + timedelta(seconds=get_settings().AUTH_REFRESH_EXPIRES),
            revogado=False, criado_em=datetime.now(timezone.utc)
        )
        db.add(new_rt)
        db.commit()
    except Exception as e:
        logging.error(f"refresh_error={str(e)}")
        return {}
    return tokens


def logout(db: Session, refresh_token: str) -> None:
    token_hash = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
    db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).update({"revogado": True})
    db.commit()


def seed_admin_user(db: Session, email: str | None = None, password: str | None = None, name: str | None = None, role: str | None = None):
    import os
    e = email or os.getenv("SEED_ADMIN_EMAIL") or "jonathasvirtual@gmail.com"
    p = password or os.getenv("SEED_ADMIN_PASSWORD") or "JH232931"
    n = name or os.getenv("SEED_ADMIN_NAME") or "Jonathas"
    r = role or os.getenv("SEED_ROLE") or "ADMIN"

    if e and p:
        u = db.query(Usuario).filter(Usuario.email == e).first()
        if not u:
            create_user(db, n, e, p, r)
            print(f"[Climatiza] Admin seeded: {e}")
        else:
            u.ativo = True
            u.perfil = r or u.perfil
            try:
                if not verify_password(p, u.senha_hash):
                    u.senha_hash = hash_password(p)
                    db.query(RefreshToken).filter(RefreshToken.usuario_id == u.id).delete()
                    print(f"[Climatiza] Admin password reset: {e}")
            except Exception:
                pass
            db.commit()
            print(f"[Climatiza] Admin healed: {e}")
