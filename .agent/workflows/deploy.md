---
description: Definitive Deployment Process (The Law of Deployment)
---

# ⚖️ A LEI SUPREMA DO DEPLOY

Este documento define o **ÚNICO E EXCLUSIVO** método aceitável para implantar código no servidor de produção da Zeladoria. Qualquer tentativa de criar novos scripts ou métodos alternativos será considerada uma violação de integridade.

## 🛠️ Components
1. **`tar_deploy.py`**: The "Packager". It maps local folders to the expected server structure.
2. **`deploy.ps1`**: The "Orchestrator". Handles transport, extraction, and container lifecycle.
3. **`ops/docker-compose.prod.yml`**: The "Blueprint". Defines the production environment.

## 📜 The Rules

### 1. Zero Binary Corruption (TAR.GZ Only)
- **NEVER** use ZIP-based deployment.
- **ALWAYS** use `tar.gz` with `tar_deploy.py`. This ensures that line endings and binary permissions are preserved correctly for the Linux environment.

### 2. Path Mapping
The project structure is heterogeneous and must be flattened during packaging:
- `zeladoria/backend` ➡️ `backend/`
- `frontend/` ➡️ `frontend/`
- `ops/docker-compose.prod.yml` ➡️ `docker-compose.yml`

### 3. Server-Side Atomicity
The deployment on the server must:
1. Extract to a temporary directory (`/tmp/deploy_extracted`).
2. Atomically move components to `/opt/apps/zeladoria`.
3. Rebuild images with `--no-cache` to ensure the latest code and dependencies are used.

### 4. Infrastructure Protection
- **NEVER** overwrite the `.env` file on the server.
- **ALWAYS** ensure `ticketz-traefik_ticketz` and `rede-interna` networks are present.

## 🚀 Execution
To deploy, run the following from the project root:
```powershell
powershell -File deploy.ps1
```

> [!IMPORTANT]
> **Server Password**: `JH232931`.
> Use `send_command_input` to provide this password when prompted by the terminal (usually twice).

// turbo-all
#### Deploy Steps:
1. **Local**: `python tar_deploy.py` (Generates `deploy_package.tar.gz`).
2. **Transport**: `scp deploy_package.tar.gz server-automacao@192.168.3.13:/tmp/`.
3. **Remote**:
   - Clean previous extraction: `rm -rf /tmp/deploy_extracted`.
   - Extract: `tar -xzf /tmp/deploy_package.tar.gz -C /tmp/deploy_extracted`.
   - Update code: `mv /tmp/deploy_extracted/* /opt/apps/zeladoria/`.
   - Build: `docker compose build --no-cache`.
   - Start: `docker compose up -d --force-recreate`.
