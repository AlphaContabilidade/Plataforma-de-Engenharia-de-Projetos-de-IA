---
volume: "04"
volume_nome: REQUIREMENTS
tipo: PROCESSO
secao: 11-Implementacao
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Implementação

Requisito não precisa de ferramenta. Precisa de um formato estável, de um lugar único e de dois
campos que quase nunca são preenchidos. Esta seção descreve a forma mínima que funciona e mostra o
que este acervo já usa.

## A forma mínima

Um arquivo de texto versionado, um bloco por requisito, com identificador, enunciado, critério de
aceite, lacuna de origem, origem da resposta e verificação associada. Texto versionado ganha de
ferramenta especializada em duas coisas que importam mais que as outras: o histórico de mudança vem
de graça e com autor, e a revisão acontece no mesmo lugar da revisão de código.

O que ferramenta especializada dá de melhor — relatório, filtro, campo obrigatório — só compensa
quando o conjunto passa de algumas centenas. Antes disso, o custo de manter a ferramenta sincronizada
com o código costuma ser maior que o benefício, e o sintoma clássico é uma base de requisitos que
ninguém abre há meses.

## O que o acervo já tem pronto para isto

O volume [`03-DISCOVERY`](../03-DISCOVERY/11-Implementacao.md) entrega exatamente a entrada que este
processo consome. O motor dele produz uma especificação com três propriedades que este volume exige e
não precisaria construir de novo:

Cada resposta carrega **origem** — respondida, inferida, decidida por humano —, o que alimenta a
porta de entrada do fluxo. Cada inferência carrega o **trecho** do texto original que a produziu, o
que torna o rastro para trás verificável em vez de declarado. E cada lacuna sem resposta sai como
**decisão aberta**, com peso, o que já é a lista de pendências que a regra Q2 exige — não é preciso
montá-la à mão.

A propriedade de completude daquela especificação é falsa enquanto houver inferência não confirmada
ou lacuna universal aberta. Consumir uma especificação incompleta é legítimo e frequente; o que a
regra Q2 proíbe é consumi-la **como se fosse completa**, transformando decisão aberta em requisito.

## Os dois campos que faltam

Na prática, os campos que ficam vazios são sempre os mesmos: o critério de aceite e a verificação
associada. O primeiro fica vazio porque exige pensar em número e entrada; o segundo porque só se
sabe depois. A forma de não perder os dois é a mesma: um requisito sem critério não sai da fila de
escrita, e um requisito sem verificação entra numa lista à parte que é revisada a cada entrega — não
na lista principal, onde ele pareceria completo.
