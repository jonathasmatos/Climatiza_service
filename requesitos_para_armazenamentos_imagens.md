# Plano Maduro de Gerenciamento de Imagens (Climatiza)

## 1. Objetivo
Garantir armazenamento de imagens de OS com confiabilidade, rastreabilidade, seguranca, performance e custo controlado, mantendo boa experiencia para tecnicos em campo e frontend em listagens.

## 2. Arquitetura alvo
Fluxo principal:

Frontend (Vue 3)
-> API FastAPI (upload + autorizacao + validacao)
-> Processamento (normalizacao/compressao/hash/thumb)
-> Storage de arquivos (SSD local, caminho controlado)
-> Metadados no PostgreSQL (nunca armazenar binario no banco)

Campos obrigatorios no banco para fotos:
- id
- ordem_servico_id
- url_arquivo
- url_thumb
- categoria
- descricao
- mime_type
- tamanho_bytes
- largura_px
- altura_px
- hash_sha256
- duplicada_de_foto_id (nullable)
- foto_principal (bool)
- status_arquivo (ATIVO | CORROMPIDO | EXCLUIDO_LOGICO)
- criado_em
- criado_por_usuario (quando houver)

Observacoes:
- hash permite detectar duplicidade e integridade.
- foto_principal permite capa unica por OS.

## 3. Estrutura de diretorios
Padrao recomendado:

/storage/climatiza/os/{ano}/{mes}/{id_os}/

Exemplo:
- /storage/climatiza/os/2026/03/102/
  - antes_4f2a9e.webp
  - antes_4f2a9e_thumb.webp
  - depois_c10d8b.webp
  - depois_c10d8b_thumb.webp

Regras:
- uma pasta por OS
- sem confiar em nome original do arquivo
- sem espacos, sem acentos, sem caracteres especiais no nome final
- criacao de diretorio com mkdir seguro (`parents=True, exist_ok=True`)

## 4. Convencao de nomes
Formato principal:
- {categoria}_{uuid_curto}.webp

Formato thumbnail:
- {categoria}_{uuid_curto}_thumb.webp

Exemplos:
- antes_a7f29c.webp
- antes_a7f29c_thumb.webp
- placa_equipamento_0ff22a.webp

Motivacao:
- evita colisao
- evita problemas de encoding
- facilita busca por categoria

## 5. Regras de upload (hard requirements)
Validacoes obrigatorias na API:
- tamanho maximo por arquivo: 5 MB
- tipos aceitos: image/jpeg, image/png, image/webp
- bloquear SVG e formatos executaveis
- validar mime real (nao confiar apenas na extensao)
- limite de dimensao de entrada (ex.: max 8000x8000)
- rejeitar upload vazio/corrompido
- limite maximo por OS: 50 fotos

Pos-processamento obrigatorio:
- auto-orientacao por EXIF
- remover EXIF sensivel (privacidade)
- converter para WEBP
- redimensionar original para largura maxima 1920 px (mantendo proporcao)
- gerar thumbnail 320 px (mantendo proporcao)
- qualidade WEBP controlada (ex.: 75 a 82)

## 6. Controle de concorrencia e resiliencia
### 6.1 Limite de concorrencia
Aplicar semaforo/lock para evitar overload por uploads paralelos.

Padrao inicial:
- max 3 uploads simultaneos por usuario
- max 5 uploads simultaneos por OS

Comportamento ao exceder:
- retornar HTTP 429 com mensagem de tentativa posterior.

### 6.2 Timeout de processamento
Processamento de imagem deve ter timeout hard.

Padrao inicial:
- timeout de 5 segundos por arquivo

Comportamento ao exceder:
- abortar processamento
- remover arquivo temporario
- retornar HTTP 408/422 com motivo "processing timeout"

### 6.3 Escrita segura no filesystem
Regras:
- escrever em arquivo temporario na mesma pasta
- mover com rename atomico para nome final
- nunca expor arquivo parcial em caso de erro

## 7. Politica de duplicidade
Caso o mesmo conteudo (hash igual) seja enviado novamente para a mesma OS:
- permitir upload
- marcar como duplicado preenchendo `duplicada_de_foto_id`
- registrar evento de auditoria

Motivo:
- tecnicos repetem fotos em campo; bloquear pode atrapalhar operacao.

## 8. Seguranca e LGPD
Controles minimos:
- autorizacao por perfil e vinculo da OS (tecnico/gestor/admin)
- impedir acesso a foto de OS sem permissao
- sanitizar caminhos de arquivo (bloquear path traversal)
- nunca expor caminho fisico real no retorno da API
- retornar URL logica (ex.: /files/os/...)
- rate limit por usuario para upload (ex.: 30 uploads/min)
- log de auditoria: quem enviou, quando, OS, categoria, IP, hash

Boas praticas recomendadas:
- hash SHA-256 no upload
- antivirus assincrono quando exigido
- token temporario para download externo

## 9. Endpoints (padrao final)
Upload:
- POST /ordens/{id}/fotos
- multipart/form-data
- campos: arquivo, categoria, descricao (opcional), foto_principal (opcional)

Listagem paginada (metadata):
- GET /ordens/{id}/fotos?page=1&limit=20

Detalhe completo de metadata:
- GET /fotos/{id}

Exclusao:
- DELETE /fotos/{id}

Download autorizado (opcional em ambientes restritos):
- GET /fotos/{id}/download

Resposta do upload (exemplo):
```json
{
  "id": "uuid",
  "ordem_servico_id": "uuid",
  "categoria": "ANTES",
  "url": "/files/os/2026/03/102/antes_a7f29c.webp",
  "url_thumb": "/files/os/2026/03/102/antes_a7f29c_thumb.webp",
  "foto_principal": true,
  "tamanho_bytes": 312455,
  "largura_px": 1600,
  "altura_px": 1200,
  "hash_sha256": "...",
  "duplicada_de_foto_id": null
}
```

## 10. Servir arquivos e cache HTTP
Fase atual (simples):
- FastAPI com StaticFiles para /files

Fase madura (recomendada):
- Traefik/Nginx servindo estaticos
- API valida permissao e entrega URL autorizada

Headers obrigatorios para imagem imutavel:
- Content-Type correto (ex.: image/webp)
- Cache-Control: public, max-age=31536000, immutable

Regra:
- backend nao deve carregar arquivo inteiro em memoria para download comum.

## 11. Integridade banco <-> disco
Validar os dois sentidos em job periodico:

1) Arquivo no disco sem registro no banco
- acao: classificar como orfao e mover para quarentena/limpeza

2) Registro no banco sem arquivo no disco
- acao: marcar `status_arquivo = CORROMPIDO`
- registrar alerta e evento de auditoria

Frequencia sugerida:
- job diario em horario de baixa carga

## 12. Retencao e ciclo de vida
Politica sugerida:
- fotos de OS: manter por 5 anos
- exclusao logica primeiro, fisica apos 30 dias
- limpeza automatica de orfaos

## 13. Backup e recuperacao (critico)
Requisito minimo:
- backup diario do storage + banco
- politica 3-2-1 (3 copias, 2 midias, 1 fora do servidor)
- teste de restauracao mensal

Exemplo operacional:
- 02:00 backup incremental de /storage/climatiza
- 03:00 backup PostgreSQL
- alerta em falha

RPO/RTO sugeridos:
- RPO: 24h
- RTO: 4h

## 14. Observabilidade e operacao
Metricas importantes:
- uploads por minuto
- taxa de falha de upload
- latencia p95 do endpoint
- volume diario gravado (GB)
- ocupacao do disco (%)
- tempo medio de processamento por imagem
- timeouts de processamento por hora
- rejeicoes por concorrencia (HTTP 429)

Alertas:
- disco > 80% (warning)
- disco > 90% (critical)
- falha de backup
- aumento anormal de erro 5xx
- aumento de timeouts de processamento

## 15. Estimativa de crescimento
Premissas:
- 10 fotos/OS
- 1 thumbnail por foto
- 400 KB/foto original apos compressao
- 40 KB/thumbnail media
- 20 OS/dia

Conta:
- 4.4 MB/OS
- 88 MB/dia
- ~32 GB/ano

Planejamento:
- SSD 120 GB: ~3.7 anos no cenario base
- manter margem operacional minima de 30%

## 16. Plano de implementacao por fases
Fase A (imediata):
- validacao de mime/tamanho
- conversao para WEBP
- thumbnails
- nomes seguros
- metadados adicionais no banco
- limite de 50 fotos por OS
- paginação em GET /ordens/{id}/fotos

Fase B (confiabilidade):
- concorrencia por usuario/OS
- timeout hard de processamento
- escrita atomica
- politica de duplicidade (marcar duplicado)
- campo foto_principal com regra de unicidade por OS

Fase C (governanca e escala):
- job de integridade banco/disco
- backup com alerta e teste de restore
- cache HTTP forte + content-type garantido
- proxy dedicado para estaticos
- opcional: migracao para object storage sem quebrar API

## 17. Criterios de aceite (Definition of Done)
Para considerar o modulo maduro:
- upload valida tipo, tamanho, permissao e limite por OS
- processamento respeita timeout de 5s
- concorrencia limitada por usuario e por OS
- original + thumbnail gerados e salvos com escrita atomica
- duplicidade marcada corretamente por hash
- foto_principal gerenciada sem ambiguidade
- listagem paginada de fotos funcionando
- checagem de integridade banco/disco ativa
- content-type e cache HTTP corretos para arquivos
- backup diario ativo e restore testado
- testes automatizados cobrindo sucesso e erro

## 18. Riscos principais e mitigacao
Risco: servidor encher disco
- mitigacao: alertas + retencao + limite por OS + capacidade reservada

Risco: acesso indevido a provas fotograficas
- mitigacao: autorizacao por OS + logs de auditoria + URLs controladas

Risco: perda de dados por falha de disco
- mitigacao: backup 3-2-1 + teste de restauracao

Risco: upload malicioso ou custoso
- mitigacao: mime real + timeout + limite de concorrencia + sanitizacao

---

Este plano foi desenhado para funcionar hoje com SSD local e evoluir sem retrabalho para storage em nuvem no futuro.
