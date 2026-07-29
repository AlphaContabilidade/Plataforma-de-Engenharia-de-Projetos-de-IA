# Artigos

> Biblioteca transversal · atualizado em 2026-07-29

## Como esta lista foi montada

**Todos os quinze artigos abaixo foram verificados um por um em 2026-07-29**, buscando a
página de resumo do próprio arXiv no identificador indicado e conferindo título exato, primeiro
autor e ano. Nenhum item foi escrito de memória e depois deixado sem checagem.

A verificação apanhou pelo menos um erro que teria entrado no acervo: o título do artigo de
Schulhoff era "A Systematic Survey of Prompt**ing** Techniques" no rascunho e é "A Systematic
Survey of Prompt **Engineering** Techniques" na fonte. Erro pequeno, e exatamente do tipo que
se propaga por citação em cadeia até ninguém saber mais qual é o título.

**A lista é curta de propósito e não pretende ser um panorama da área.** São os artigos que
sustentam afirmações feitas em algum lugar deste acervo. Artigo que não sustenta nada aqui não
entra, mesmo sendo importante — biblioteca de referência inflada é biblioteca que ninguém abre.

**Regra de manutenção:** só entra artigo cuja página de resumo tenha sido aberta e cujo título,
primeiro autor e ano tenham sido conferidos. Se você não abriu, não acrescente. Não registramos
número de página, veículo de publicação nem contagem de citações — são os campos em que o erro
entra sem ser notado.

## Fundação

| Artigo | Primeiro autor | Ano | arXiv | Por que está aqui |
|---|---|---|---|---|
| Attention Is All You Need | Ashish Vaswani | 2017 | [1706.03762](https://arxiv.org/abs/1706.03762) | Introduz a arquitetura Transformer. É a base técnica de tudo o que o acervo trata; citado pelos volumes de fundação. |
| Language Models are Few-Shot Learners | Tom B. Brown | 2020 | [2005.14165](https://arxiv.org/abs/2005.14165) | Estabelece que a tarefa pode ser especificada por texto, com demonstrações, sem ajuste de pesos. É a premissa de que engenharia de prompt existe como disciplina. |
| Training language models to follow instructions with human feedback | Long Ouyang | 2022 | [2203.02155](https://arxiv.org/abs/2203.02155) | InstructGPT. Explica por que modelos alinhados respondem a instrução — e por que o tamanho não é a variável dominante. |
| Constitutional AI: Harmlessness from AI Feedback | Yuntao Bai | 2022 | [2212.08073](https://arxiv.org/abs/2212.08073) | Avaliação e revisão guiadas por princípios explícitos, em vez de rótulo humano caso a caso. É o parentesco conceitual mais próximo da fase de auditoria desta plataforma. |

## Prompt e raciocínio

| Artigo | Primeiro autor | Ano | arXiv | Por que está aqui |
|---|---|---|---|---|
| Chain-of-Thought Prompting Elicits Reasoning in Large Language Models | Jason Wei | 2022 | [2201.11903](https://arxiv.org/abs/2201.11903) | Fundamento do ganho em tarefas de múltiplos passos; citado por [`RISE.md`](../frameworks/conhecidos/RISE.md). |
| Large Language Models are Zero-Shot Reasoners | Takeshi Kojima | 2022 | [2205.11916](https://arxiv.org/abs/2205.11916) | A versão mínima da mesma ideia ("vamos pensar passo a passo"), sem exemplos. |
| Self-Consistency Improves Chain of Thought Reasoning in Language Models | Xuezhi Wang | 2022 | [2203.11171](https://arxiv.org/abs/2203.11171) | Amostrar vários caminhos e marginalizar. Base do argumento de que uma execução única não é medida. |
| Least-to-Most Prompting Enables Complex Reasoning in Large Language Models | Denny Zhou | 2022 | [2205.10625](https://arxiv.org/abs/2205.10625) | Decomposição de problema em subproblemas ordenados — o fundamento de decompor em vez de alongar o prompt. |
| Tree of Thoughts: Deliberate Problem Solving with Large Language Models | Shunyu Yao | 2023 | [2305.10601](https://arxiv.org/abs/2305.10601) | Exploração com autoavaliação e retrocesso, em vez de um caminho único. |
| The Prompt Report: A Systematic Survey of Prompt Engineering Techniques | Sander Schulhoff | 2024 | [2406.06608](https://arxiv.org/abs/2406.06608) | Levantamento sistemático com taxonomia de técnicas. É o ponto de partida para quem quer o panorama que esta lista deliberadamente não é. |

## Contexto, ferramentas e agentes

| Artigo | Primeiro autor | Ano | arXiv | Por que está aqui |
|---|---|---|---|---|
| Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks | Patrick Lewis | 2020 | [2005.11401](https://arxiv.org/abs/2005.11401) | Origem do termo RAG; combina memória paramétrica e índice recuperável. Base do volume `13-RAG`. |
| Lost in the Middle: How Language Models Use Long Contexts | Nelson F. Liu | 2023 | [2307.03172](https://arxiv.org/abs/2307.03172) | Informação no meio de contexto longo é usada pior que no começo ou no fim. Sustenta o argumento de curadoria de contexto em [`CARE.md`](../frameworks/conhecidos/CARE.md) e [`RISE.md`](../frameworks/conhecidos/RISE.md). |
| ReAct: Synergizing Reasoning and Acting in Language Models | Shunyu Yao | 2022 | [2210.03629](https://arxiv.org/abs/2210.03629) | Raciocínio intercalado com ação. É o padrão conceitual por trás de agente com ferramentas. |
| Toolformer: Language Models Can Teach Themselves to Use Tools | Timo Schick | 2023 | [2302.04761](https://arxiv.org/abs/2302.04761) | Delegar a ferramenta o que o modelo faz mal (aritmética, busca factual) em vez de melhorar o prompt. |
| Reflexion: Language Agents with Verbal Reinforcement Learning | Noah Shinn | 2023 | [2303.11366](https://arxiv.org/abs/2303.11366) | Melhoria por reflexão verbal sobre o retorno da tarefa, sem atualizar pesos. Parentesco com o laço geração → auditoria → incorporação. |

## Avaliação

| Artigo | Primeiro autor | Ano | arXiv | Por que está aqui |
|---|---|---|---|---|
| Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena | Lianmin Zheng | 2023 | [2306.05685](https://arxiv.org/abs/2306.05685) | Estuda usar um modelo como avaliador, com seus vieses. É a referência mais direta para a fase 5 do framework proprietário — e para não tratar nota de modelo como medida objetiva. |

## O que não está aqui, e por quê

- **Nada sobre modelos, preços ou limites de contexto específicos.** Esse material pertence aos
  volumes perecíveis (`26-AI-MODELS`, `27-LLM-ROUTER`, `34-COST-OPTIMIZATION`), que devem
  apontar para fonte viva e não fixar números. Artigo científico não é o lugar de consultar
  preço.
- **Nenhum artigo de sustentação para RTF, CARE, RISE, TAG, BAB ou RAPPEL.** Não foi encontrada
  fonte primária atribuível para nenhuma das seis siglas, e por isso todas estão marcadas
  `DOMINIO-PUBLICO-SEM-ATRIBUICAO-SEGURA` em
  [`frameworks/_catalogo.md`](../frameworks/_catalogo.md). Citar um artigo genérico de prompt
  como se fosse a origem da sigla seria atribuição inventada por outro caminho.
- **Nenhum artigo cujo identificador não pôde ser conferido.** Houve candidatos que ficaram de
  fora exatamente por isso.
