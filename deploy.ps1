# ═══════════════════════════════════════════════════════
# Climatiza Service — Deploy Script
# Servidor: 192.168.3.13 | Dir: /opt/apps/os_microSas
# Domínio: climatizaservice.topmarcas.site
#
# ⚠️  NÃO TOCA no Zeladoria, Ticketz, n8n ou qualquer
#     outro serviço do servidor!
# ═══════════════════════════════════════════════════════
$ErrorActionPreference = 'Stop'
$User = "server-automacao"
$Server = "192.168.3.13"
$IdentityFile = "$env:USERPROFILE\.ssh\id_ed25519_antigravity"
$RemotePath = "/opt/apps/os_microSas"

Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   CLIMATIZA SERVICE — Deploy Pipeline     " -ForegroundColor Cyan
Write-Host "   Servidor: $User@$Server                 " -ForegroundColor Cyan
Write-Host "   Destino:  $RemotePath                   " -ForegroundColor Cyan
Write-Host "   Domínio:  climatizaservice.topmarcas.site" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ── [1/3] Empacotando ──────────────────────────────
Write-Host "[1/3] Criando pacote de deploy..." -ForegroundColor Yellow
python tar_deploy.py
if ($LASTEXITCODE -ne 0) { throw "tar_deploy.py falhou" }

# ── [2/3] Enviando ao servidor ─────────────────────
Write-Host "[2/3] Enviando pacote e compose via SCP..." -ForegroundColor Yellow
scp -i $IdentityFile deploy_package.tar.gz "$User@$Server`:/tmp/deploy_package.tar.gz"
if ($LASTEXITCODE -ne 0) { throw "SCP falhou com exit code $LASTEXITCODE" }
# Enviar o compose separadamente garante que é sempre a versão atual do disco
scp -i $IdentityFile docker-compose.yml "$User@$Server`:/tmp/climatiza-docker-compose.yml"
if ($LASTEXITCODE -ne 0) { throw "SCP compose falhou com exit code $LASTEXITCODE" }

# ── [3/3] Deploy Climatiza ─────────────────────────
Write-Host "[3/3] Extraindo e subindo Climatiza..." -ForegroundColor Yellow

# Usa here-string @'...'@ para que o PowerShell NÃO expanda nada — bash recebe o texto cru
$deployScript = @'
#!/bin/bash
set -e
cd /opt/apps/os_microSas

echo "--- Parando climatiza containers antigos (se existirem) ---"
docker stop climatiza-backend climatiza-postgres climatiza-redis 2>/dev/null || true
docker rm   climatiza-backend climatiza-postgres climatiza-redis 2>/dev/null || true

echo "--- Limpeza atomica ---"
rm -rf backend docker-compose.yml

echo "--- Extraindo pacote ---"
mkdir -p /tmp/climatiza_deploy
tar -xzf /tmp/deploy_package.tar.gz -C /tmp/climatiza_deploy
mv /tmp/climatiza_deploy/backend /opt/apps/os_microSas/backend

echo "--- Aplicando docker-compose atualizado ---"
mv /tmp/climatiza-docker-compose.yml /opt/apps/os_microSas/docker-compose.yml

echo "--- Limpando temporarios ---"
rm -rf /tmp/climatiza_deploy /tmp/deploy_package.tar.gz

echo "--- Build das imagens ---"
docker compose build --no-cache

echo "--- Subindo containers ---"
docker compose up -d --force-recreate

echo "--- Verificando containers ---"
docker ps --filter "name=climatiza" --format "table {{.Names}}\t{{.Status}}"

echo "--- Labels no climatiza-backend ---"
docker inspect climatiza-backend --format "{{json .Config.Labels}}"

echo "--- Roteamento Traefik interno ---"
HSTATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "Host: climatizaservice.topmarcas.site" "http://127.0.0.1/health")
echo "Traefik /health => ${HSTATUS}"
if [ "${HSTATUS}" != "200" ]; then
  echo "AVISO: Traefik ainda nao roteia /health (${HSTATUS}). Verifique rede e labels acima."
fi

echo "--- Faxina de imagens sem uso ---"
docker image prune -f
'@

# Gravar script com line endings Unix em arquivo temp e enviar via SCP
$normalizedDeploy = $deployScript.Replace("`r`n", "`n").Replace("`r", "`n")
$tmpScript = [System.IO.Path]::GetTempFileName()
[System.IO.File]::WriteAllText($tmpScript, $normalizedDeploy, (New-Object System.Text.UTF8Encoding $false))
scp -i $IdentityFile $tmpScript "$User@$Server`:/tmp/climatiza_deploy.sh"
Remove-Item $tmpScript
ssh -i $IdentityFile "$User@$Server" "bash /tmp/climatiza_deploy.sh; rm -f /tmp/climatiza_deploy.sh"
if ($LASTEXITCODE -ne 0) { throw "Deploy SSH falhou com exit code $LASTEXITCODE" }

Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
Write-Host "   ✅ CLIMATIZA DEPLOY CONCLUÍDO!          " -ForegroundColor Green
Write-Host "   URL: https://climatizaservice.topmarcas.site" -ForegroundColor Green
Write-Host "   Health: https://climatizaservice.topmarcas.site/health" -ForegroundColor Green
Write-Host "   Docs: https://climatizaservice.topmarcas.site/docs" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
