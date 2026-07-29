---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 07-Regras
status: RASCUNHO
atualizado_em: 2026-07-29
---

# Regras

As regras abaixo são invioláveis no sentido preciso de que não dependem de disciplina de
quem opera: cada uma está implementada no código do motor e verificada por teste. Uma
regra que existisse apenas como recomendação escrita seria uma convenção, não uma regra, e
convenção se erode. A coluna "onde vive" aponta o mecanismo que a torna impossível de
violar por descuido.

| Id | Regra | Onde vive |
|---|---|---|
| R1 | Prompt sem caso de ouro não é promovido | Ausência da aresta `VERSIONADO` para `PROMOVIDO` em `TRANSICOES`, somada a `taxa_acerto` devolver `0.0` para bateria vazia |
| R2 | O hash cobre o corpo **e** a assinatura | `hash` calcula `sha256` sobre `corpo + "\x00" + assinatura` |
| R3 | No máximo uma versão `PROMOVIDO` por nome | `transicionar` rebaixa a promovida anterior para `DEPRECIADO` no mesmo passo |
| R4 | Corpo e contrato concordam nas duas direções | `__post_init__` levanta `ContratoViolado` para placeholder sem declaração e para variável declarada e não usada |
| R5 | Registrar o mesmo conteúdo é idempotente | `registrar` compara o hash contra as entradas existentes antes de criar versão |
| R6 | `DEPRECIADO` é terminal | O valor de `TRANSICOES[Estado.DEPRECIADO]` é um conjunto congelado vazio |
| R7 | Erro de renderização é falha do caso, não exceção da bateria | `avaliar` captura `ContratoViolado` e registra `Falha` com o motivo |
| R8 | Bateria vazia vale zero, não um | `taxa_acerto` devolve `0.0` quando `total` é zero |
| R9 | Comparação de versões usa a mesma amostra | `comparar` materializa os casos em tupla antes de avaliar os dois lados |
| R10 | O motor não conhece provedor | Nenhum dos três módulos importa cliente de modelo; o único ponto de contato é o `Callable` recebido em `PromptEvaluator.__init__` |

## Por que R1 é a regra que sustenta as outras

Sem R1, o registro degenera em um armário de strings com data. A regra é implementada por
ausência: não existe chave que leve de `VERSIONADO` a `PROMOVIDO`, então a única rota até
a produção passa por `EM_AVALIACAO`. Esse desenho é preferível a uma verificação dentro de
`transicionar` que consultasse um resultado de avaliação, porque a verificação exigiria que
o registro conhecesse o avaliador, e o acoplamento resultante faria de registrar uma
operação caro o suficiente para deixar de ser idempotente sem penalidade. Vale registrar o
limite honesto disso: a máquina de estados garante que a versão passou pelo estado de
avaliação, não que a avaliação teve resultado bom. O julgamento do resultado é do operador
ou da esteira, e é o quarto ponto de decisão do fluxograma em
[`06-Fluxogramas.md`](06-Fluxogramas.md).

## Por que R2 não é detalhe de implementação

Se o hash cobrisse apenas o texto, duas versões com o mesmo corpo e tipos diferentes de
variável colidiriam, e a segunda nunca seria criada por causa de R5. O resultado seria
silencioso e grave: uma mudança real de contrato ficaria invisível no histórico. Trocar o
tipo de uma variável de texto para número altera o que o modelo recebe, altera o que a
validação aceita e portanto é uma versão nova. O separador nulo entre os dois campos existe
para que nenhuma concatenação de corpo e assinatura possa colidir com outra combinação dos
mesmos caracteres.

## Regras de operação derivadas

Três consequências práticas seguem das dez regras e valem ser ditas explicitamente. A
primeira é que renomear um prompt cria um espaço de versões novo, com numeração começando
em `v1`, porque o nome é a chave de agrupamento — renomear não é editar. A segunda é que
depreciar todas as versões de um nome deixa `promovida` devolvendo vazio, e uma chamada de
`obter` sem versão passa a devolver a última registrada; quem depende de comportamento em
produção precisa tratar esse caso em vez de presumir promoção. A terceira é que o histórico
nunca é reescrito: correção de rota é sempre uma versão nova, e a versão errada permanece
visível com o estado que recebeu.
