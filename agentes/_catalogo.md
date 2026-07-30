# Catálogo de agentes

> Biblioteca transversal · atualizado em 2026-07-29
> **Agentes especificados neste acervo: 1.** O número é este mesmo. A razão está abaixo.

## O catálogo

| Agente | Definição | Missão em uma linha | Modelo | Estado |
|---|---|---|---|---|
| `auditor-fable` | `.claude/agents/auditor-fable.md` | Auditar um volume contra o contrato da plataforma e emitir nota por seção, com veredicto | Fable (diferente do gerador) | **Previsto** — criado na Task 16 do plano de implementação |

Nada mais. Não há segundo agente, e a tabela não vai crescer por conveniência.

## `auditor-fable` — o que se sabe hoje

O agente que existirá é o auditor da **fase 5** do
[`AI-ENGINEERING-FRAMEWORK`](../frameworks/proprietarios/AI-ENGINEERING-FRAMEWORK.md). Do
plano de implementação e da especificação de projeto, o contrato dele já está determinado nos
pontos que importam:

- **Disparo:** o comando `/auditar N`.
- **Entrada:** o volume `NN-NOME/` completo, mais o contrato (`00-INTRODUCAO/contrato.json`) e
  as convenções (`00-INTRODUCAO/Convencoes.md`).
- **Saída:** `auditorias/VOL-NN-auditoria-YYYY-MM-DD.md`, com nota de 0 a 10 por seção,
  problemas, sugestões e veredicto; e a atualização do `status` no front-matter.
- **Regra de estado:** média abaixo de 8,0 grava `REQUER_REVISAO`. Ele **não** grava `PRONTO`
  — nenhum agente grava; `PRONTO` é consequência verificada das quatro condições da Definição
  de PRONTO.
- **Independência:** roda em **modelo diferente** do que gerou o volume. É essa diferença que
  faz a auditoria valer algo: gerador que avalia o próprio texto tende a ratificá-lo, porque
  os vieses que produziram o defeito são os mesmos que o julgam aceitável.
- **Indisponibilidade:** se o subagente não estiver disponível, `/auditar` **falha
  reportando** e o status permanece `RASCUNHO`. Ausência de auditoria nunca é lida como
  aprovação.

Quando o arquivo for escrito, ele deve preencher as 13 rubricas de
[`_template-agente.md`](_template-agente.md). Duas delas merecem atenção antecipada:

- **Ferramentas:** o auditor **não escreve** nos arquivos do volume. Ele lê o volume e escreve
  apenas o relatório e o campo `status`. Auditor que corrige o que audita deixa de ser
  auditor — passa a ser um segundo gerador, e o acervo perde a única leitura externa que tem.
- **Memória:** nenhuma entre execuções, de propósito. Cada auditoria precisa poder chegar a
  conclusão diferente da anterior sem ter de justificar a mudança. Auditor com memória tende à
  coerência com o próprio parecer passado, que é exatamente o viés que se quis evitar
  contratando um segundo modelo.

## Por que só um

A especificação original desta plataforma projetava "300+ agentes". Esse número está registrado
no `ROADMAP.md` como **estimativa do autor, explicitamente não usada como critério de aceite** —
o critério é a Definição de PRONTO.

Publicar aqui um catálogo de 300 agentes exigiria inventar 299 missões, 299 conjuntos de
entradas e saídas e 299 listas de limitações. Seria o mesmo erro descrito em
[`frameworks/_backlog.md`](../frameworks/_backlog.md), com um agravante: um agente inventado é
mais perigoso que um framework inventado, porque tem aparência de coisa executável. Alguém lê
`agentes/revisor-de-catalogo.md`, supõe que existe, e planeja trabalho em cima de um arquivo que
nunca foi mais que texto.

O critério para um agente entrar neste catálogo, portanto, é o mesmo dos volumes: **ele existe
como definição executável** (`.claude/agents/<nome>.md` ou equivalente) **ou está previsto numa
task de plano com contrato determinado**. As duas linhas de estado admitidas são `Previsto` e
`Ativo`. Não há estado "planejado genericamente".

## Backlog de agentes

Todos os demais agentes da especificação original estão em **backlog**, e o backlog é
deliberadamente **sem lista de nomes**. Essa escolha merece explicação, porque contrasta com
[`frameworks/_backlog.md`](../frameworks/_backlog.md), que nomeia treze itens.

A diferença é que lá havia treze nomes concretos presentes na especificação, e registrar os
nomes preserva informação — alguém pediu aquilo, e o pedido é rastreável. Aqui não há uma lista
de 300 nomes: há um número agregado. Transformar "300+ agentes" em 300 nomes inventados seria
fabricar a informação que falta, não registrá-la.

Um agente sai do backlog quando alguém puder responder às três perguntas que tornam um agente
justificável:

1. **Que decisão ele toma que um humano não deveria tomar toda vez?** Se não há decisão
   repetitiva, não há agente — há uma tarefa.
2. **Contra o que a saída dele é verificada?** Sem gate determinístico ou caso de ouro, mais um
   agente é mais texto plausível. Ver o risco de convergência em
   [`frameworks/conhecidos/autogen.md`](../frameworks/conhecidos/autogen.md).
3. **O que quebra se ele estiver errado, e como se descobre?** Agente cujo erro não tem sintoma
   é agente que erra por muito tempo.

Com as três respostas, escreve-se a especificação pelo template e a linha entra na tabela deste
arquivo. Sem elas, permanece no backlog — o que não é uma falha do acervo, é o acervo
funcionando.

## Relacionados

- [`_template-agente.md`](_template-agente.md) — as 13 rubricas obrigatórias.
- [`frameworks/proprietarios/AI-ENGINEERING-FRAMEWORK.md`](../frameworks/proprietarios/AI-ENGINEERING-FRAMEWORK.md)
  — onde a auditoria se encaixa no ciclo de seis fases.
- [`frameworks/_backlog.md`](../frameworks/_backlog.md) — a mesma política aplicada a
  frameworks.
