---
volume: "02"
volume_nome: CORE
tipo: ARQUITETURA
secao: 03-Escopo
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Escopo

Este volume trata da **anatomia mínima de um sistema que usa modelo de linguagem** e das regras
estruturais que a organizam. É a camada abaixo de qualquer decisão sobre agentes, prompts ou
provedores: vale igual para um script de uma função e para uma plataforma inteira.

## O que pertence a este volume

As seis partes de um sistema de IA e o que cada uma pode e não pode fazer; a fronteira entre
determinístico e probabilístico e a regra de não vazamento; o contrato de saída; o tratamento da
resposta do modelo como entrada não confiável; e a decisão de quantas chamadas um caminho faz.

## O que pertence ao vizinho

**Agente** — laço de decisão, escolha de ferramenta, critério de parada — é do `08-AGENT-ENGINE`.
Aqui se estabelece que a saída do modelo precisa de fronteira; lá se trata do que fazer quando o
modelo decide **chamar** algo em vez de responder.

**Orquestração** entre vários agentes ou etapas é do `09-ORCHESTRATOR`, e **fluxo de trabalho** de
longa duração é do `10-WORKFLOW`. A diferença é o número de participantes: este volume descreve um
sistema; aqueles descrevem sistemas conversando.

**Prompt** — estrutura, variável tipada, versão — é do `07-PROMPT-ENGINE`, que já está escrito. A
relação com este volume é direta e vale enunciar: um modelo de prompt com assinatura tipada **é** a
fronteira de entrada do contexto feita explícita.

**Escolha e roteamento de modelo** são do `26-AI-MODELS` e do `27-LLM-ROUTER`. Aqui o modelo é uma
caixa com latência, preço e resposta em texto; qual caixa usar é decisão de lá.

**Camada de serviço, persistência e contrato de API** são do `23-BACKEND-ARCHITECT`, do
`24-DATABASE-ARCHITECT` e do `25-API-ARCHITECT`. Este volume diz que a saída vira dado com tipo; o
que se faz com esse dado depois é assunto deles.

Dos volumes citados acima, apenas o `07-PROMPT-ENGINE` tem seção escrita. As demais menções ficam em
prosa, sem link, porque link para arquivo inexistente produz pré-requisito de leitura que não pode
ser lido.
