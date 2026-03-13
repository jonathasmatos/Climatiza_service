from pydantic import BaseModel, ConfigDict


# ── Auth ─────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    senha: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    perfil: str
    nome: str
    model_config = ConfigDict(from_attributes=True)


class RefreshRequest(BaseModel):
    refresh_token: str


class UserRead(BaseModel):
    id: int
    nome: str
    email: str
    perfil: str
    telefone: str | None = None
    ativo: bool
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None
    telefone: str | None = None
    ativo: bool | None = None


class UserCreate(BaseModel):
    nome: str
    email: str
    senha: str
    telefone: str | None = None
    perfil: str = "ADMIN"
