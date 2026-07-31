---
volume: "04"
volume_nome: REQUIREMENTS
tipo: PROCESSO
secao: 03-Escopo
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Escopo

Este volume trata da **transformação de uma especificação em requisitos rastreáveis e verificáveis**,
e da manutenção desse conjunto ao longo do projeto.

## O que pertence a este volume

A anatomia de um requisito; o critério de falsificabilidade; os dois rastros — para a evidência que o
originou e para a verificação que o confere; a distinção entre requisito, restrição e decisão de
projeto; e o registro de mudança.

## O que pertence ao vizinho

**Descobrir o que a pessoa quer** é do [`03-DISCOVERY`](../03-DISCOVERY/01-Introducao.md), que já está
escrito. A fronteira é nítida e vale enunciar: aquele volume entrega uma **especificação** — um
conjunto de lacunas, algumas respondidas, outras declaradas em aberto. Este volume recebe essa
especificação e produz requisitos. Uma lacuna respondida vira requisito; uma lacuna aberta vira
decisão pendente, **nunca** requisito com valor assumido.

**Viabilidade e modelo de negócio** — vale a pena fazer, quanto custa, quem paga — são do
`05-BUSINESS`. Este volume não julga se um requisito merece existir; julga se ele é verificável.

**Prioridade, prazo e sequência de entrega** são do `38-PROJECT-PLANNER` e do `39-ROADMAP`. Um
requisito daqui não carrega prazo: carregar prazo faria o conjunto envelhecer junto com o plano, e
plano muda mais que requisito.

**Técnica de verificação** — como se escreve o teste que confere — é do `31-TESTING`. Aqui se exige
que a verificação exista e esteja associada; lá se trata de como escrevê-la bem.

**Requisito de segurança** tem tratamento próprio no `17-SECURITY`, porque a forma de falsificá-lo é
diferente: não basta observar o comportamento normal, é preciso construir o ataque.

Dos volumes citados, apenas o `03-DISCOVERY` tem seção escrita, e por isso é o único com link.
