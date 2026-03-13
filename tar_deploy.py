"""
Climatiza Service — Tar Deploy Packager
Empacota backend + docker-compose.yml em deploy_package.tar.gz
"""

import tarfile
import os

PACKAGE = "deploy_package.tar.gz"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Arquivos/pastas a incluir no pacote
INCLUDES = [
    ("backend", "backend"),
    ("docker-compose.yml", "docker-compose.yml"),
]

# Pastas/arquivos a ignorar
EXCLUDES = {
    "__pycache__", ".git", ".venv", "venv", "node_modules",
    ".pytest_cache", "*.pyc", ".mypy_cache", "deploy_package.tar.gz",
    "zeladoria",  # Nunca empacotar pasta zeladoria
}


def should_exclude(name: str) -> bool:
    parts = name.replace("\\", "/").split("/")
    for part in parts:
        if part in EXCLUDES:
            return True
        for pattern in EXCLUDES:
            if pattern.startswith("*") and part.endswith(pattern[1:]):
                return True
    return False


def create_package():
    print(f"📦 Criando pacote {PACKAGE}...")
    with tarfile.open(os.path.join(BASE_DIR, PACKAGE), "w:gz") as tar:
        for src, arcname in INCLUDES:
            full_path = os.path.join(BASE_DIR, src)
            if not os.path.exists(full_path):
                print(f"  ⚠️  Ignorando (não existe): {src}")
                continue

            if os.path.isdir(full_path):
                for root, dirs, files in os.walk(full_path):
                    # Filtrar diretórios
                    dirs[:] = [d for d in dirs if not should_exclude(d)]
                    for f in files:
                        filepath = os.path.join(root, f)
                        relative = os.path.relpath(filepath, BASE_DIR)
                        if not should_exclude(relative):
                            tar.add(filepath, arcname=relative)
                            print(f"  ✅ {relative}")
            else:
                tar.add(full_path, arcname=arcname)
                print(f"  ✅ {arcname}")

    size_mb = os.path.getsize(os.path.join(BASE_DIR, PACKAGE)) / (1024 * 1024)
    print(f"\n🎁 Pacote criado: {PACKAGE} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    create_package()
