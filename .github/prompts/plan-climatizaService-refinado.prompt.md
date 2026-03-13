## Refinamentos Validados - 12/03/2026

1. Regra cultural de migrations:
Nenhuma alteracao em [backend/app/db/models.py](backend/app/db/models.py) pode ir para producao sem migration correspondente em [backend/alembic/versions/](backend/alembic/versions/) e execucao de alembic upgrade no pipeline.

2. Maquina de estados:
Adicionar CANCELADO ao fluxo oficial, com transicoes permitidas a partir de NOVO e AGENDADO, exigindo motivo de cancelamento.

3. Matriz de transicoes validas:
NOVO -> AGENDADO
NOVO -> CANCELADO
AGENDADO -> EM_ATENDIMENTO
AGENDADO -> CANCELADO
EM_ATENDIMENTO -> RESOLVIDO
EM_ATENDIMENTO -> AGUARDANDO
AGUARDANDO -> EM_ATENDIMENTO
RESOLVIDO -> FECHADO
Qualquer outra transicao deve ser bloqueada.

4. Regra de equipamento:
Criacao de OS exige ao menos 1 equipamento associado.

5. Evidencias de execucao:
RESOLVIDO exige checklist e fotos obrigatorias.
Formalizar enum de categoria no schema:
ANTES
DEPOIS
PLACA_EQUIPAMENTO
DEFEITO

6. Rastreabilidade de origem:
Manter created_by e criado_por_usuario.
created_by deve ser enum fechado:
ADMIN
EXECUTOR
SISTEMA

7. Prevencao de duplicidade em integracao:
Adicionar idempotency_key na criacao de OS para suportar integracoes como n8n.

8. Automacao preventiva sem duplicacao:
Obrigatorio adotar uma das estrategias:
feature flag singleton
ou lock em banco
ou job externo

9. Uso de crud_base:
Aplicar apenas em agregados simples:
clientes, locais, ambientes, equipamentos, tecnicos
Nao aplicar em ordens de servico.

10. Decisao estrutural de equipe tecnica:
Fase atual: 1 tecnico responsavel por OS.
Planejar extensao futura para tecnicos auxiliares sem quebra de contrato.

11. Ordem das fases permanece:
P0 infraestrutura
maquina de estados
regras de negocio
automacao
hardening
refatoracao

12. Continuacao:
Frontend permanece fora do escopo atual; prioridade segue 100% no back-end ate consolidacao P0/P1.

## Status de Execucao P0

Concluido:
- Ajuste de metadata e URL de banco no Alembic em [backend/alembic/env.py](backend/alembic/env.py)
- Remocao de create_all no startup em [backend/app/main.py](backend/app/main.py)

Em andamento:
- Geracao da migration inicial

Bloqueio atual do ambiente local:
- Docker indisponivel no host local (comando docker nao reconhecido), impedindo subir Postgres local para autogenerate.

## Proximo Passo Operacional

Assim que Docker (ou acesso ao Postgres do ambiente) estiver disponivel:
1. Rodar revision autogenerate.
2. Revisar migration inicial.
3. Rodar upgrade head.
4. Validar current/head e smoke de aplicacao.
