---
volume: "31"
volume_nome: TESTING
tipo: PROCESSO
secao: 03-Escopo
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Escopo

Este volume trata da **técnica de escrever verificação executável** e do que distingue um teste real
de um que só parece.

## O que pertence a este volume

O critério do defeito nomeável; a asserção negativa; a mutação como prova de que o teste pega alguma
coisa; a exigência de determinismo — sem rede, disco ou relógio; a distinção entre testar o mecanismo
e testar o dado; a substituição da parte probabilística; e a leitura correta das métricas de suíte.

## O que pertence ao vizinho

**Exigir que a verificação exista** é do [`04-REQUIREMENTS`](../04-REQUIREMENTS/01-Introducao.md).
Aquele volume estabelece que todo requisito carrega rastro para frente — uma verificação nomeada.
Este trata de como escrevê-la bem. A fronteira é entre *tem* e *presta*.

**Qualidade como processo** — revisão, critério de aceite, ciclo de correção — é do `32-QUALITY`.
Aqui se escreve o teste; lá se decide o que acontece quando ele falha e quem revisa o quê.

**Segurança** é do `17-SECURITY`, e a diferença é o adversário. Um teste comum observa o
comportamento normal; um teste de segurança constrói o ataque. A técnica de construir o ataque não
está aqui.

**Avaliação de qualidade de resposta de modelo** é assunto de `26-AI-MODELS` e do instrumental de
avaliação. Não cabe numa suíte que precisa rodar em segundos e sem rede, e misturar as duas coisas
produz suíte lenta, cara e intermitente — e a reação previsível a suíte intermitente é desligá-la.

**Desempenho** é do `33-PERFORMANCE`. Aqui se mede o tempo da suíte para que ela continue sendo
rodada; lá se mede o tempo do produto.

Dos volumes citados, apenas o `04-REQUIREMENTS` tem seção escrita, e por isso é o único com link.
