---
volume: "04"
volume_nome: REQUIREMENTS
tipo: PROCESSO
secao: 13-Testes
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Testes

Este volume descreve um processo e não publica exemplo de código próprio. O que se verifica aqui é o
conjunto de requisitos, e a verificação é uma revisão com critérios objetivos — objetivos o bastante
para que duas pessoas cheguem ao mesmo resultado.

## As quatro verificações do conjunto

**Falsificabilidade, por amostragem cruzada.** Alguém que não escreveu o requisito tenta descrever o
que veria se ele estivesse sendo descumprido. Falhar em descrever é reprovação, e a escolha de ser
**outra pessoa** é o mesmo princípio do controle C6 do volume `01`: quem escreveu lê o que quis dizer.

**Rastro para trás completo.** Para cada requisito, seguir até a origem. O resultado esperado é uma
das origens válidas; chegar em `PADRAO_ASSUMIDO`, ou não chegar a lugar nenhum, é achado.

**Rastro para frente completo.** Para cada requisito, existe verificação nomeada. A lista dos que não
têm é a métrica de [`14-Metricas.md`](14-Metricas.md), e ela deveria ser vazia.

**Ausência de mistura.** Nenhum item da lista de requisitos é restrição ou decisão de projeto. A
verificação é a pergunta do fluxo: o projeto pode escolher diferente? Isto é sobre comportamento ou
sobre construção?

## O que não se verifica aqui

Não se verifica se o requisito é **bom** — se resolve o problema certo, se vale o custo. Isso é
julgamento de produto e de negócio, e pertence ao `05-BUSINESS`. Um conjunto de requisitos
impecavelmente falsificáveis para um produto que ninguém quer passa em todas as quatro verificações
acima, e a plataforma prefere dizer isso a fingir que rigor de forma substitui julgamento.
