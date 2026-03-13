## Plan: Fundacao Climatiza para Producao

Objetivo: consolidar a fundacao de negocio e infraestrutura para permitir evolucao segura da aplicacao, com prioridade em schema versionado, maquina de estados formal, validacoes criticas de OS e automacao preventiva na mesma leva. Abordagem: executar em fases verificaveis, começando por P0 bloqueante e seguindo para P1 operacional, com testes de regressao em cada fase.

**Steps**
1. Fase 1 - Estabilizacao P0: migracoes Alembic e governanca de schema.
2. Em [backend/alembic/env.py](backend/alembic/env.py), ajustar target metadata para carregar Base e models do dominio/auth; em [backend/alembic.ini](backend/alembic.ini), alinhar conexao para ambiente de deploy e local.
3. Gerar migration inicial em [backend/alembic/versions/](backend/alembic/versions/) e revisar constraints/indices/chaves para aderencia com [backend/app/db/models.py](backend/app/db/models.py).
4. Ajustar bootstrap em [backend/app/main.py](backend/app/main.py) para evitar dependencia de create_all em producao; manter fluxo controlado por alembic upgrade. Depende de 1-3.
5. Fase 2 - Maquina de estados formal com nomenclatura do documento (NOVO, AGENDADO, EM_ATENDIMENTO, AGUARDANDO, RESOLVIDO, FECHADO).
6. Criar modulo de estados em [backend/app/core/states.py](backend/app/core/states.py) com transicoes validas e validacao explicita de transicao; integrar no patch de OS em [backend/app/rotas/dominio_routes.py](backend/app/rotas/dominio_routes.py).
7. Migrar nomenclatura de status no modelo/schemas/rotas: [backend/app/db/models.py](backend/app/db/models.py), [backend/app/schemas/dominio.py](backend/app/schemas/dominio.py), [backend/app/rotas/dominio_routes.py](backend/app/rotas/dominio_routes.py). Depende de 6.
8. Ajustar historico para manter rastreabilidade consistente de status anterior/novo durante migracao de nomenclatura. Depende de 6-7.
9. Fase 3 - Validacoes de negocio de OS e auditoria de origem.
10. Em criacao de OS, exigir ao menos 1 equipamento associado e validar existencia/pertinencia dos ids em [backend/app/rotas/dominio_routes.py](backend/app/rotas/dominio_routes.py).
11. Em transicao para RESOLVIDO, exigir checklist e evidencias minimas de foto; em transicao para FECHADO, manter regra atual de km_percorrido obrigatorio (sem separar ida/volta nesta etapa) em [backend/app/rotas/dominio_routes.py](backend/app/rotas/dominio_routes.py).
12. Adicionar created_by e criado_por_usuario em [backend/app/db/models.py](backend/app/db/models.py), refletir em [backend/app/schemas/dominio.py](backend/app/schemas/dominio.py) e popular automaticamente no create de OS em [backend/app/rotas/dominio_routes.py](backend/app/rotas/dominio_routes.py). Depende de 3.
13. Expor consulta de historico por OS em [backend/app/rotas/dominio_routes.py](backend/app/rotas/dominio_routes.py) com schema dedicado em [backend/app/schemas/dominio.py](backend/app/schemas/dominio.py). Paralelo com 10-12.
14. Fase 4 - Automacao preventiva na mesma leva.
15. Criar servico de geracao de preventivas em [backend/app/services/preventiva_scheduler.py](backend/app/services/preventiva_scheduler.py), usando contratos ativos e data base de ultima OS concluida.
16. Integrar gatilho administrativo via rota e agendamento recorrente inicial no lifecycle do app (ou job externo documentado), em [backend/app/main.py](backend/app/main.py) e [backend/app/rotas/dominio_routes.py](backend/app/rotas/dominio_routes.py). Depende de 15.
17. Garantir que OS preventiva criada automaticamente registre origem SISTEMA e evento no historico. Depende de 12 e 15.
18. Fase 5 - Hardening de API e qualidade.
19. Adicionar validacoes de schema para enums/campos sensiveis (categoria de foto, status, tipo_servico) em [backend/app/schemas/dominio.py](backend/app/schemas/dominio.py), alinhando mensagens de erro HTTP.
20. Criar testes de integracao para fluxo critico (criar OS, transicoes validas/invalidas, historico, preventiva automatica) em [backend/tests/](backend/tests/). Depende de 6-17.
21. Atualizar README operacional e playbook de deploy/migracao em [README.md](README.md) e [Documentacao_apoio_Climatiza_service.md](Documentacao_apoio_Climatiza_service.md), incluindo ordem correta: alembic upgrade antes de subir app. Depende de 1-20.

22. Fase 6 - Refatoracao estrutural anti-boilerplate (sem quebra de API).
23. Extrair helpers compartilhados de data/hora e utilitarios de parse para [backend/app/core/utils.py](backend/app/core/utils.py), removendo duplicacoes em [backend/app/auth/services.py](backend/app/auth/services.py), [backend/app/db/models.py](backend/app/db/models.py) e [backend/app/rotas/dominio_routes.py](backend/app/rotas/dominio_routes.py).
24. Introduzir base CRUD reutilizavel em [backend/app/core/crud_base.py](backend/app/core/crud_base.py) e migrar gradualmente entidades simples (clientes, locais, ambientes, equipamentos, tecnicos) em [backend/app/rotas/dominio_routes.py](backend/app/rotas/dominio_routes.py). Paralelo com 19-21.
25. Fatiar [backend/app/rotas/dominio_routes.py](backend/app/rotas/dominio_routes.py) por contexto de dominio em novos modulos de rota com APIRouter por agregado, mantendo os mesmos paths publicos para compatibilidade.
26. Reorganizar schemas extensos de [backend/app/schemas/dominio.py](backend/app/schemas/dominio.py) por entidade/contexto para reduzir acoplamento e facilitar evolucao de contratos de API.
27. Definir limite de tamanho de arquivo como regra de manutencao (meta: preferencialmente ate ~200-250 linhas por modulo de aplicacao, salvo excecoes justificadas) e aplicar em revisoes futuras.

**Relevant files**
- [backend/alembic/env.py](backend/alembic/env.py) — registrar metadata correta para autogenerate.
- [backend/alembic.ini](backend/alembic.ini) — fonte de conexao para migracoes.
- [backend/alembic/versions/](backend/alembic/versions/) — migration inicial e evolutivas.
- [backend/app/main.py](backend/app/main.py) — bootstrap seguro e scheduler entrypoint.
- [backend/app/core/states.py](backend/app/core/states.py) — regras formais de transicao de status.
- [backend/app/db/models.py](backend/app/db/models.py) — campos created_by e compatibilidade de status.
- [backend/app/schemas/dominio.py](backend/app/schemas/dominio.py) — validacoes pydantic e respostas.
- [backend/app/rotas/dominio_routes.py](backend/app/rotas/dominio_routes.py) — regras de negocio e endpoints de OS/historico/automacao.
- [backend/app/services/preventiva_scheduler.py](backend/app/services/preventiva_scheduler.py) — motor de preventivas.
- [backend/app/core/utils.py](backend/app/core/utils.py) — funcoes utilitarias compartilhadas para reduzir duplicacao.
- [backend/app/core/crud_base.py](backend/app/core/crud_base.py) — base reutilizavel para operacoes CRUD e reducao de boilerplate.
- [backend/app/rotas/](backend/app/rotas/) — particionamento de rotas por agregado de dominio mantendo compatibilidade de endpoint.

- [backend/tests/](backend/tests/) — cobertura de regressao.
- [README.md](README.md) — guia de execucao e migracao.
- [Documentacao_apoio_Climatiza_service.md](Documentacao_apoio_Climatiza_service.md) — alinhamento funcional.

**Verification**
1. Rodar migracoes em base limpa e base existente; confirmar alembic current/head e integridade das tabelas.
2. Executar testes de transicao de estado com matriz de casos validos e invalidos (incluindo bloqueio de regressao de status).
3. Validar API manualmente no swagger: create OS com equipamento, patch para RESOLVIDO e FECHADO com validacoes obrigatorias.
4. Testar historico por OS e confirmar eventos de criacao/mudanca com usuario e origem.
5. Simular contratos ativos e rodar gatilho de preventiva; confirmar criacao automatica de OS com origem SISTEMA.
- Status do plano: APROVADO pelo usuario em 12/03/2026; execucao pode iniciar direto na Fase 1 (P0) sem novo alinhamento.

6. Executar deploy em homologacao com ordem operacional revisada e smoke test de endpoints principais.

**Decisions**
- Status da OS: migrar para nomenclatura do documento (NOVO, AGENDADO, EM_ATENDIMENTO, AGUARDANDO, RESOLVIDO, FECHADO).
- KM de encerramento: manter km_percorrido unico nesta etapa.
- Automacao preventiva: implementar agora na mesma leva apos P0.
- Escopo fora desta leva: upload real para object storage e webhook n8n podem entrar na proxima iteracao se prazo apertar, sem bloquear fundacao.
- Prioridade confirmada pelo usuario em 12/03/2026: continuar primeiro no back-end; frontend (Vue/Vite) fica pos-fundacao P0/P1.

**Further Considerations**
1. Compatibilidade retroativa de status antigos no banco: fazer script de data migration e fallback temporario na API para evitar quebra de consumidores.
2. Scheduler interno vs job externo: se houver apenas uma replica, scheduler interno simplifica; com multiplas replicas, preferir job externo para evitar duplicidade.
3. Performance de filtros/listagens: incluir paginacao padrao consistente antes de liberar frontend em escala.
