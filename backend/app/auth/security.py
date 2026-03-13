import json
import hmac
import hashlib
import time
import base64
from typing import Any, Dict
from app.core.config import get_settings


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def b64urldecode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


def jwt_encode(payload: Dict[str, Any]) -> str:
    settings = get_settings()
    header = {"alg": "HS256", "typ": "JWT"}
    h_b64 = b64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    p_b64 = b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    msg = f"{h_b64}.{p_b64}".encode("utf-8")
    sig = hmac.new(settings.AUTH_JWT_SECRET.encode("utf-8"), msg, hashlib.sha256).digest()
    return f"{h_b64}.{p_b64}.{b64url(sig)}"


def jwt_decode(token: str) -> Dict[str, Any]:
    settings = get_settings()
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("invalid")
    h_b64, p_b64, s_b64 = parts
    msg = f"{h_b64}.{p_b64}".encode("utf-8")
    sig = b64urldecode(s_b64)
    calc = hmac.new(settings.AUTH_JWT_SECRET.encode("utf-8"), msg, hashlib.sha256).digest()
    if not hmac.compare_digest(sig, calc):
        raise ValueError("invalid")
    payload = json.loads(b64urldecode(p_b64))
    if "exp" in payload and int(payload["exp"]) < int(time.time()):
        raise ValueError("expired")
    return payload


def hash_password(plain: str) -> str:
    salt = base64.urlsafe_b64encode(hashlib.sha256(str(time.time()).encode()).digest())[:16].decode()
    dk = hashlib.pbkdf2_hmac("sha256", plain.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"pbkdf2:sha256:100000:{salt}:{base64.urlsafe_b64encode(dk).decode()}"


def verify_password(plain: str, hashed: str) -> bool:
    try:
        _, _, iters, salt, hv = hashed.split(":")
        dk = hashlib.pbkdf2_hmac("sha256", plain.encode("utf-8"), salt.encode("utf-8"), int(iters))
        return hmac.compare_digest(base64.urlsafe_b64encode(dk).decode(), hv)
    except Exception:
        return False


def now_ts() -> int:
    return int(time.time())
