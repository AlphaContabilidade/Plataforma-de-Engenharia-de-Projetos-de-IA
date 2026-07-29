# Catálogo de frameworks

> Biblioteca transversal · atualizado em 2026-07-29
> Esta pasta **não é um volume**: não tem front-matter de seção e não passa pelos
> gates de volume. Ela é insumo dos volumes 07, 08, 09, 28 e 29.

## Para que esta pasta existe

Um acervo de engenharia de IA acumula siglas depressa. Sem um lugar único onde cada
sigla é registrada com o seu **estado de atribuição**, o acervo passa a citar como se
fosse consolidado aquilo que é apenas repetido. Este catálogo existe para que essa
confusão seja detectável: cada arquivo declara de onde vem o que afirma.

## Estados de atribuição

Todo item desta biblioteca fica em exatamente um destes três estados. O estado é
declarado no topo do arquivo do item, e o catálogo abaixo o repete.

| Estado | Significa | Como se escreve o arquivo |
|---|---|---|
| `VERIFICADO` | Existe fonte primária consultável (documentação oficial, artigo, repositório) e ela foi lida. | Cita a fonte com URL e data da consulta. |
| `DOMINIO-PUBLICO-SEM-ATRIBUICAO-SEGURA` | A técnica circula amplamente, é útil e reproduzível, mas não se sabe com segurança quem a originou. | Escreve literalmente *"técnica de domínio público, origem não atribuída com segurança"*. **Não** cita autor, ano, empresa ou artigo. |
| `PROPRIETARIO` | Foi formulado por esta plataforma. | Diz o que propõe, contra o que se compara e onde pode falhar. |

A regra que sustenta os três estados é a mesma do `CLAUDE.md` da plataforma: **nunca
inventar fonte.** Um autor plausível escrito por conveniência é indistinguível, para
quem lê depois, de um autor real — e é exatamente por isso que não pode ser escrito.

## Itens catalogados

### Técnicas públicas de estruturação de prompt

São *formatos de escrita*, não software. Não têm versão, não quebram, não têm
dependência. O que elas fazem é impor uma ordem de campos ao prompt para que o autor
não esqueça de dizer alguma coisa.

| Arquivo | Sigla expande | Estado de atribuição | Serve melhor para |
|---|---|---|---|
| [`conhecidos/RTF.md`](conhecidos/RTF.md) | Role, Task, Format | `DOMINIO-PUBLICO-SEM-ATRIBUICAO-SEGURA` | Pedido único, saída de formato previsível |
| [`conhecidos/CARE.md`](conhecidos/CARE.md) | Context, Action, Result, Example | `DOMINIO-PUBLICO-SEM-ATRIBUICAO-SEGURA` | Tarefa em que o contexto de negócio decide a resposta |
| [`conhecidos/RISE.md`](conhecidos/RISE.md) | Role, Input, Steps, Expectation | `DOMINIO-PUBLICO-SEM-ATRIBUICAO-SEGURA` | Procedimento com etapas que precisam ser seguidas na ordem |
| [`conhecidos/TAG.md`](conhecidos/TAG.md) | Task, Action, Goal | `DOMINIO-PUBLICO-SEM-ATRIBUICAO-SEGURA` | Pedido curto onde o critério de sucesso é o que falta |
| [`conhecidos/BAB.md`](conhecidos/BAB.md) | Before, After, Bridge | `DOMINIO-PUBLICO-SEM-ATRIBUICAO-SEGURA` | Diagnóstico e proposta de mudança de estado |
| [`conhecidos/RAPPEL.md`](conhecidos/RAPPEL.md) | expansão **não padronizada** — ver o arquivo | `DOMINIO-PUBLICO-SEM-ATRIBUICAO-SEGURA` | Uso com cautela; preferir RTF ou RISE |

### Frameworks de software para aplicações e agentes

São *código de terceiros*. Têm versão, quebram entre versões e são o material mais
perecível desta biblioteca. Cada arquivo registra a data da consulta e evita fixar
número de versão, assinatura de função ou preço.

| Arquivo | O que é | Estado de atribuição | Perecível |
|---|---|---|---|
| [`conhecidos/langchain.md`](conhecidos/langchain.md) | Framework de composição de aplicações e agentes com LLM (Python/JS) | `VERIFICADO` | Sim — alta rotatividade de API |
| [`conhecidos/crewai.md`](conhecidos/crewai.md) | Orquestração multiagente por papéis (Python) | `VERIFICADO` | Sim |
| [`conhecidos/autogen.md`](conhecidos/autogen.md) | Framework multiagente orientado a eventos (Microsoft) | `VERIFICADO` | Sim — houve reescrita de arquitetura |
| [`conhecidos/semantic-kernel.md`](conhecidos/semantic-kernel.md) | SDK de integração de modelos a código corporativo (C#/Python/Java) | `VERIFICADO` | Sim |

### Framework proprietário

| Arquivo | O que propõe | Estado |
|---|---|---|
| [`proprietarios/AI-ENGINEERING-FRAMEWORK.md`](proprietarios/AI-ENGINEERING-FRAMEWORK.md) | O ciclo de produção auditada de conhecimento técnico desta plataforma: contrato → geração → gate estrutural → teste dos exemplos → auditoria independente → promoção | `PROPRIETARIO` |

**É o único.** Não há segundo framework proprietário nesta plataforma, e a razão está
em [`_backlog.md`](_backlog.md).

### Backlog

[`_backlog.md`](_backlog.md) lista treze nomes que apareceram na especificação original
sem definição. Nenhum deles foi escrito, porque escrever teria significado inventar.
Ler esse arquivo é parte de entender o que esta biblioteca é.

## Como acrescentar um item

1. Decida o estado de atribuição **antes** de escrever o conteúdo. O estado determina
   o que o arquivo pode afirmar.
2. Se o estado é `VERIFICADO`, consulte a fonte primária e registre URL e data. Se a
   fonte não abre, o estado não é `VERIFICADO`.
3. Se você está tentado a escrever "criado por X em 20NN" e não leu isso numa fonte,
   o estado é `DOMINIO-PUBLICO-SEM-ATRIBUICAO-SEGURA`.
4. Se o item é software, marque-o perecível e não fixe versão nem assinatura de API no
   texto — aponte para a documentação oficial.
5. Acrescente a linha na tabela deste catálogo. Um item fora do catálogo é um item que
   ninguém encontra.
