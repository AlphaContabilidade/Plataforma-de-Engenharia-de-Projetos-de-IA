---
volume: "02"
volume_nome: CORE
tipo: ARQUITETURA
secao: 18-Referencias-Cruzadas
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Referências Cruzadas

`depende_de` aponta para `01`. A leitura da fundação vem antes porque este volume usa o vocabulário
de lá — procedência, controle executável, os anti-padrões de processo — e reescrevê-lo aqui criaria
duas definições da mesma coisa, que é como um acervo adquire regras contraditórias.

**Dentro deste volume**, quem vai desenhar um sistema lê [`04-Arquitetura.md`](04-Arquitetura.md) e
[`07-Regras.md`](07-Regras.md). Quem vai revisar um sistema existente começa por
[`10-Anti-Patterns.md`](10-Anti-Patterns.md), porque o diagnóstico é mais rápido pelo sintoma.

**Vizinhança com seção escrita:** o `07-PROMPT-ENGINE` realiza a fronteira de entrada do contexto com
assinatura tipada; o `03-DISCOVERY` é o exemplo vivo da regra N8, um motor que resolve por tabela
auditável o que se resolveria por chamada a modelo; e o `12-MEMORY` trata do que persiste entre
execuções e herda deste volume a exigência de procedência.

**Vizinhança em prosa e sem link**, porque os volumes existem como pasta sem seção escrita:
`08-AGENT-ENGINE` (o laço de decisão), `09-ORCHESTRATOR` e `10-WORKFLOW` (vários participantes),
`26-AI-MODELS` e `27-LLM-ROUTER` (qual caixa usar), `23-BACKEND-ARCHITECT`, `24-DATABASE-ARCHITECT` e
`25-API-ARCHITECT` (o que se faz com o dado depois da fronteira).
