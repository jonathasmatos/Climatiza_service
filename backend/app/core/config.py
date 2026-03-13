import os
from pathlib import Path


class Settings:
    # Core
    DATABASE_URL: str
    APP_ENV: str
    CORS_ORIGINS: str

    # Auth
    AUTH_JWT_SECRET: str
    AUTH_ACCESS_EXPIRES: int
    AUTH_REFRESH_EXPIRES: int
    AUTH_RESET_EXPIRES: int
    AUTH_REFRESH_ENABLED: str
    AUTH_FORGOT_LIMIT_ENABLED: str
    AUTH_FORGOT_LIMIT_PER_MIN: int

    # Infra
    REDIS_URL: str
    INTERNAL_TOKEN: str

    # Seed Admin
    SEED_ADMIN_EMAIL: str
    SEED_ADMIN_PASSWORD: str
    SEED_ADMIN_NAME: str

    # Integrações (Ticketz / n8n)
    TICKETZ_API_URL: str
    TICKETZ_API_KEY: str
    N8N_NOTIFICACAO_WEBHOOK_URL: str

    # Imagens
    IMAGE_STORAGE_ROOT: str
    IMAGE_MAX_BYTES: int
    IMAGE_MAX_PER_OS: int
    IMAGE_MAX_INPUT_DIMENSION: int
    IMAGE_MAX_WIDTH: int
    IMAGE_THUMB_WIDTH: int

    def __init__(self) -> None:
        self._load_env_file()

        # Core
        self.DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
        self.AUTH_JWT_SECRET = os.getenv("AUTH_JWT_SECRET", "dev-secret-climatiza").strip()
        self.APP_ENV = os.getenv("APP_ENV", "").strip().lower()
        self.CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").strip()

        # Auth timings
        self.AUTH_ACCESS_EXPIRES = self._int("AUTH_ACCESS_EXPIRES", 3600)
        self.AUTH_REFRESH_EXPIRES = self._int("AUTH_REFRESH_EXPIRES", 604800)
        self.AUTH_RESET_EXPIRES = self._int("AUTH_RESET_EXPIRES", 1800)
        self.AUTH_FORGOT_LIMIT_PER_MIN = self._int("AUTH_FORGOT_LIMIT_PER_MIN", 10)

        self.AUTH_REFRESH_ENABLED = os.getenv("AUTH_REFRESH_ENABLED", "1").strip()
        self.AUTH_FORGOT_LIMIT_ENABLED = os.getenv("AUTH_FORGOT_LIMIT_ENABLED", "1").strip()

        # Infra
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0").strip()
        self.INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "").strip()

        # Seed Admin
        self.SEED_ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "admin@climatiza.local").strip()
        self.SEED_ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "admin123").strip()
        self.SEED_ADMIN_NAME = os.getenv("SEED_ADMIN_NAME", "Admin").strip()

        # Integrações
        self.TICKETZ_API_URL = os.getenv("TICKETZ_API_URL", "").strip()
        self.TICKETZ_API_KEY = os.getenv("TICKETZ_API_KEY", "").strip()
        self.N8N_NOTIFICACAO_WEBHOOK_URL = os.getenv("N8N_NOTIFICACAO_WEBHOOK_URL", "").strip()

        # Imagens
        self.IMAGE_STORAGE_ROOT = os.getenv("IMAGE_STORAGE_ROOT", "./storage/climatiza").strip()
        self.IMAGE_MAX_BYTES = self._int("IMAGE_MAX_BYTES", 5 * 1024 * 1024)
        self.IMAGE_MAX_PER_OS = self._int("IMAGE_MAX_PER_OS", 50)
        self.IMAGE_MAX_INPUT_DIMENSION = self._int("IMAGE_MAX_INPUT_DIMENSION", 8000)
        self.IMAGE_MAX_WIDTH = self._int("IMAGE_MAX_WIDTH", 1920)
        self.IMAGE_THUMB_WIDTH = self._int("IMAGE_THUMB_WIDTH", 320)

    @staticmethod
    def _int(key: str, default: int) -> int:
        try:
            return int(os.getenv(key, str(default)).strip())
        except Exception:
            return default

    def _load_env_file(self) -> None:
        try:
            base_dir = Path(__file__).resolve().parents[2]
            env_path = base_dir / ".env"
            if env_path.exists():
                for line in env_path.read_text(encoding="utf-8").splitlines():
                    if not line or line.strip().startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip()
                    if k and k not in os.environ:
                        os.environ[k] = v
        except Exception:
            pass


def get_settings() -> Settings:
    return Settings()
