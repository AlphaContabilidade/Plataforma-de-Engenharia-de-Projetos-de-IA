---
volume: "31"
volume_nome: TESTING
tipo: PROCESSO
secao: 11-Implementacao
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Implementação

Esta seção descreve como as regras aparecem em código, usando a suíte deste repositório — que roda,
pode ser lida, e por isso não exige acreditar em ninguém.

## Determinismo por injeção, não por truque

A forma que funciona para tirar relógio e configuração de dentro da lógica é recebê-los como
parâmetro com valor padrão. Os motores dos volumes `03` e `12` fazem isso: o limiar de decisão e o
catálogo são injetados, e a data também. O ganho é duplo — o comportamento de parada é testável sem
depender do conteúdo real do catálogo, e o catálogo real é testável sem depender do limiar padrão.

Truques de substituição de módulo resolvem o mesmo problema e custam mais: acoplam o teste ao nome
interno da coisa substituída, e quebram na primeira refatoração que renomeia sem mudar comportamento.

## Import sem colisão de pacote

Um detalhe operacional que custou tempo e vale registrar. Duas pastas `exemplos/<vol>/tests/` com
`__init__.py` reivindicam o mesmo nome de pacote `tests`, e rodar a suíte inteira falha com erro de
módulo na segunda pasta coletada — a primeira ganha o nome e a segunda procura seus módulos dentro
dela. Sem `__init__.py`, cada arquivo é importado pelo nome-base, único no acervo, e a colisão
desaparece. O caminho de import é resolvido por um `conftest.py` que insere a pasta do exemplo no
caminho de busca.

## Testar prosa que contém asserções

Quando a documentação tem blocos de código com `assert` escritos para o leitor, eles podem ser
executados. O teste extrai os blocos do Markdown por expressão regular e os roda **em sequência, no
mesmo escopo**, como quem lê de cima para baixo — escopo compartilhado é proposital, porque um passo
depende do que o anterior construiu.

Esse teste precisa de um guarda contra o próprio modo de falha: seção renomeada, zero blocos
encontrados, laço que não itera e tudo verde. Por isso ele exige que os blocos **existam** antes de
qualquer coisa. É a aplicação de E1 ao teste que combate E1.

## O que a suíte deste acervo não faz

Não toca rede, disco nem relógio. Não roda pytest de dentro de pytest. Não depende de ordem entre
arquivos. E cita comandos com escopo na documentação, pela regra T8 — o número que um comando sem
escopo imprime cresce a cada volume novo, e a prosa que o cita apodrece sozinha.
