# CrewAI

> Framework de software (terceiro) · atualizado em 2026-07-29
> **Estado de atribuição:** `VERIFICADO` — documentação oficial consultada em 2026-07-29:
> <https://docs.crewai.com/>
> **Perecível: sim.** Sem versão, sem assinatura de API neste arquivo.

## O que é

Framework Python para construir sistemas multiagente. A documentação oficial descreve o
produto como uma forma de "projetar agentes, orquestrar equipes e automatizar fluxos" com
guarda-corpos, memória, conhecimento e observabilidade incorporados.

O que distingue o CrewAI dos demais desta pasta é a metáfora de organização: em vez de
modelar o sistema como um grafo de nós ou uma troca de mensagens entre pares, ele o modela
como uma **equipe de trabalho com papéis**.

## As quatro primitivas

Segundo a documentação consultada:

| Primitiva | O que é |
|---|---|
| **Agent** | a entidade individual, composta com ferramentas, memória e conhecimento; pode produzir saída estruturada (via Pydantic) |
| **Task** | a unidade de trabalho, com guarda-corpos, retornos de chamada e ponto de intervenção humana |
| **Crew** | o conjunto de agentes orquestrado para cumprir um objetivo composto |
| **Flow** | o controle de execução — passos de início, escuta e roteamento, com estado, persistência e retomada de processos longos |

Os processos de uma `Crew` podem ser sequenciais, hierárquicos ou híbridos.

A observação de arquitetura que vale registrar: `Crew` e `Flow` respondem a perguntas
diferentes, e confundi-las é o erro de projeto mais comum com este framework. `Crew`
responde "quem faz o quê"; `Flow` responde "em que ordem, com que estado, e o que acontece
se parar no meio". Sistema com muitos agentes e nenhum `Flow` é sistema que não sabe retomar.

## O acerto conceitual: papel como redutor de escopo

A ideia forte do CrewAI é usar papel, objetivo e histórico do agente para **estreitar** o que
cada um decide. Um agente com escopo estreito é mais previsível, mais fácil de avaliar e mais
fácil de depurar do que um agente generalista com vinte ferramentas — e essa é uma lição de
engenharia, não de marketing.

O acerto correlato é a saída estruturada por esquema. Agente que devolve texto livre obriga
o próximo agente a interpretar; agente que devolve objeto validado permite que o erro apareça
na fronteira, e não três etapas adiante.

## O risco: papel confundido com competência

O mesmo mecanismo que estreita escopo pode virar teatro. Escrever que o agente "é um auditor
de processos com 20 anos de experiência" não lhe dá conhecimento do processo — dá-lhe o
registro linguístico de quem tem. É a limitação 1 do [`RTF.md`](RTF.md) elevada à escala de sistema, e
com um agravante: num sistema multiagente, o agente seguinte trata a saída do anterior como
insumo confiável. Uma afirmação inventada com tom de especialista, produzida no primeiro
agente, propaga-se pela equipe inteira sem que nenhum agente tenha razão para duvidar dela.

Daí a regra prática: **fronteira entre agentes é lugar de validação, não de confiança.** Se a
saída de um agente pode ser verificada por código, verifique por código.

## Quando serve

- Trabalho que se decompõe naturalmente em **especialidades distintas** com um artefato
  passando de mão em mão (pesquisar → redigir → revisar → formatar).
- Quando a **revisão por um segundo agente com objetivo diferente** agrega — o mesmo princípio
  do par criador/auditor desta plataforma (ver
  [`proprietarios/AI-ENGINEERING-FRAMEWORK.md`](../proprietarios/AI-ENGINEERING-FRAMEWORK.md)).
- Automação de processo longo, com estado e retomada, usando `Flow`.
- Prototipagem rápida de sistema multiagente por quem quer pensar em papéis, não em grafos.

## Quando NÃO serve

- **Tarefa que um agente resolve.** Multiagente multiplica custo, latência e superfície de
  falha. A pergunta a fazer antes de adotar é: que decisão exige um segundo ponto de vista?
  Se não houver resposta concreta, não há sistema multiagente — há sobrecusto.
- **Quando não há como avaliar o resultado.** Sem casos de ouro, mais agentes só produzem mais
  texto plausível. Um sistema multiagente sem avaliação é uma máquina de gerar concordância.
- **Quando a saída de um agente não é verificável.** O risco de propagação descrito acima
  torna-se dominante.
- **Quando o determinismo é requisito.** Fluxos de negócio com efeito irreversível
  (encerrar item de fila, notificar solicitante, emitir documento) precisam de código no caminho crítico
  e de agente no caminho de recomendação — nunca o contrário.

## Relação com esta plataforma

Esta plataforma não usa CrewAI. Ela implementa a separação criador/auditor com os recursos do
Claude Code: a skill `/novo-volume` gera, o subagente `auditor-fable` audita com outro modelo,
e três gates determinísticos ficam **fora** de ambos. O que torna esse arranjo diferente de uma
equipe de agentes que se avaliam mutuamente é exatamente isso: o veredicto final não é
opinião de agente, é `exit code` de programa. Ver
[`agentes/_catalogo.md`](../../agentes/_catalogo.md).

O framework é referência externa dos volumes `08-AGENT-ENGINE` e `09-ORCHESTRATOR`.

## Nota sobre colisão de nome

A primitiva `Flow` do CrewAI **não tem relação** com o nome `FLOW` listado em
[`_backlog.md`](../_backlog.md). A coincidência não autoriza supor que o autor da
especificação original se referia a isto. Ver a nota sobre colisão de nomes naquele arquivo.

## Fonte consultada

- <https://docs.crewai.com/> — consultada em 2026-07-29.
