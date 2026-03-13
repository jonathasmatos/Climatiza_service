# Projeto: Climatiza Service

Este projeto é uma adaptação do sistema **Zeladoria**, originalmente criado para gestão de chamados de manutenção em condomínios.

O objetivo agora é evoluir essa base arquitetural para um sistema de **gestão de ordens de serviço para manutenção de climatização (ar-condicionado)**.

A arquitetura central da Zeladoria deve ser preservada sempre que possível.

O que muda é o **domínio de negócio**.

---

# Princípios Arquiteturais

A aplicação deve manter os princípios originais do sistema Zeladoria:

1. Backend como fonte da verdade.
2. Regras de negócio centralizadas no backend.
3. Máquina de estados formal para controle do ciclo de vida das ordens de serviço.
4. Histórico auditável de eventos.
5. Frontend atuando apenas como consumidor da API.

O sistema deve ser **API-first**, permitindo futuras integrações com ferramentas de automação como n8n.

---

# Operação Inicial do Sistema

Na fase inicial do projeto:

* clientes **não abrirão chamados diretamente**
* não haverá integração com WhatsApp
* toda criação de ordens de serviço será feita manualmente por um usuário **ADMIN**

Fluxo operacional inicial:

Cliente solicita atendimento por telefone ou mensagem externa
↓
ADMIN registra a Ordem de Serviço no sistema
↓
ADMIN agenda técnico responsável
↓
Técnico executa serviço
↓
Técnico registra diagnóstico e evidências
↓
ADMIN encerra administrativamente a OS

Mesmo sendo manual inicialmente, o sistema deve ser preparado para automação futura.

---

# Preparação para Automação

O sistema deve permitir integração futura com automações via API.

Exemplo de automação futura:

WhatsApp ou formulário externo
↓
n8n recebe mensagem
↓
n8n interpreta dados
↓
n8n chama API do Climatiza Service
↓
criação automática de Ordem de Serviço

Para isso, todas as operações principais devem possuir endpoints claros.

Exemplos:

POST /clientes
POST /equipamentos
POST /ordens-servico
PATCH /ordens-servico/{id}/status

Além disso, o sistema deve permitir identificar a origem da criação da OS.

Campo sugerido:

created_by
Valores possíveis:
ADMIN
EXECUTOR
SISTEMA

---

# Entidades do Domínio

O sistema deve trabalhar com um inventário estruturado de equipamentos.

Entidades principais:

Cliente
Local ou Filial
Ambiente
Equipamento
Ordem de Serviço
Registro Técnico
Fotos
Deslocamento (KM)

Relacionamentos:

Cliente (1:N) Local
Local (1:N) Ambiente
Ambiente (1:N) Equipamento

Uma Ordem de Serviço pode envolver múltiplos equipamentos.

---

# Estrutura do Equipamento

Cada equipamento deve possuir os seguintes atributos mínimos:

marca
tipo (split, cassete, piso teto)
capacidade em BTU
voltagem
localização (ambiente)
cliente proprietário

Esse inventário é fundamental para manter o histórico de manutenção.

---

# Ordens de Serviço

A Ordem de Serviço é o núcleo do sistema.

Cada OS deve registrar:

cliente
local
equipamentos atendidos
técnico responsável
status da OS
diagnóstico técnico
serviço executado
peças utilizadas
fotos da execução
KM percorrido

---

# Fluxo de Estados da Ordem de Serviço

A máquina de estados da Zeladoria deve ser reaproveitada.

Estados equivalentes:

NOVO → OS Aberta
AGENDADO → OS Agendada
EM_ATENDIMENTO → OS em Execução
AGUARDANDO → Aguardando peças ou fabricante
RESOLVIDO → Execução técnica concluída
FECHADO → Encerramento administrativo

Todas as mudanças de estado devem gerar eventos registrados no histórico.

---

# Gestão de Fotos

Fotos são obrigatórias para registro técnico.

Requisitos:

* imagens não devem ser armazenadas no banco
* banco deve guardar apenas URL
* armazenamento em object storage
* formato permitido: JPG ou WEBP
* tamanho máximo de upload: 5MB
* gerar thumbnails automaticamente

Cada OS pode possuir múltiplas imagens.

---

# Registro Técnico

Durante ou após a execução do serviço, o técnico deve registrar:

diagnóstico do problema
serviço executado
peças utilizadas
observações técnicas

Esse registro compõe o histórico do equipamento.

---

# Gestão de Deslocamento

No encerramento da OS deve ser possível registrar:

KM ida
KM volta

Esse dado é necessário para faturamento de deslocamento junto a fabricantes.

---

# Manutenção Preventiva (Evolução Futura)

O sistema deve futuramente permitir criação de planos de manutenção preventiva.

Exemplo:

limpeza de filtros a cada 30 dias
manutenção preventiva trimestral

Esses planos deverão gerar automaticamente ordens de serviço preventivas.

---

# Objetivo Final do Sistema

Criar uma plataforma de gestão de manutenção técnica capaz de:

gerenciar inventário de equipamentos
registrar histórico completo de manutenção
documentar intervenções com evidências
automatizar manutenção preventiva
integrar-se futuramente com sistemas externos e automações

O foco do desenvolvimento deve ser reutilizar a arquitetura existente da Zeladoria e adaptar seu domínio para o contexto de manutenção de climatização.
