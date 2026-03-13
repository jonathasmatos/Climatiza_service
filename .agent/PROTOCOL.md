# 📜 Protocolo de Desenvolvimento e Automação

Este documento define as regras obrigatórias para o uso de agentes e a execução de tarefas críticas neste projeto.

## 1. Consulta aos Agentes (`.agent/`)

Sempre que iniciar uma nova fase de desenvolvimento ou encontrar um problema complexo, os seguintes diretórios **DEVEM** ser consultados:

- **`/antigravity-workflows`**: Para orquestração de tarefas multi-fase (SaaS MVP, Auditorias, QA).
- **`/skills`**: Para padrões de implementação específicos (ex: `backend-dev-guidelines`, `frontend-dev-guidelines`).
- **`/deploy`**: Em `.agent/workflows/deploy.md` para as regras de sobrevivência em produção.

## 2. A Lei do Deploy (JRInovacoes)

O deploy para o website JRInovacoes segue regras específicas de caminho e integridade:

1.  **Diretório de Destino**: `/opt/apps/landing-page/JRInovacoes`
2.  **URL Oficial**: `https://jrinovacoes.topmarcas.site/`
3.  **Método**: Uso estrito de `tar.gz` via script de deploy automatizado para evitar corrupção de arquivos e garantir permissões Linux.
4.  **Atomicidade**: A extração deve ocorrer em `/tmp` antes de mover para o diretório final.

## 3. Base de Conhecimento

O desenvolvimento do website deve respeitar integralmente as diretrizes em `d:\Websites\website_knowledge_base`:
- **Stack**: Vue 3 + Vite.
- **Estética**: Glassmorphism e Dark Mode.
- **Copy**: Focado em Proposta de Valor e Diferenciais (Oceano Azul).

---
*Assinado: Antigravity Agent*
