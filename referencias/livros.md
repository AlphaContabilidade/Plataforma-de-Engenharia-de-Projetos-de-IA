# Livros

> Biblioteca transversal · atualizado em 2026-07-29

## Como esta lista foi montada, e por que ela é curta

**Esta lista é curta, e a brevidade é o resultado da regra, não uma falha de esforço.** São
onze livros. Um levantamento honesto de bibliografia de engenharia de IA teria dezenas; o que
esta lista tem são os livros que (a) existem com o título, os autores e a editora indicados, e
(b) sustentam alguma afirmação feita em algum lugar deste acervo.

Cinco títulos foram **verificados por consulta em 2026-07-29** — busca por título e autores,
com conferência de editora e ano de publicação. Estão marcados `consultado` na coluna de
verificação. Os outros seis são obras canônicas de engenharia de software, com título, autoria e
editora conhecidos sem margem de dúvida; estão marcados `canônico` e a diferença de método está
declarada em vez de escondida atrás de uma marca única.

**O que não registramos, de propósito:** ISBN, número de páginas, número de edição corrente e
número de capítulo. São exatamente os campos em que o erro entra sem ser notado e viaja por
citação. Quem precisa do ISBN abre o catálogo da editora, onde ele está certo.

**Regra de manutenção:** só entra livro cujo título e cuja autoria você conferiu numa fonte, e
que seja citado por algum volume ou arquivo deste acervo. Livro que não sustenta nada aqui não
entra, por importante que seja.

## Engenharia de IA e prompt

| Livro | Autoria | Editora / ano | Verificação | Por que está aqui |
|---|---|---|---|---|
| AI Engineering: Building Applications with Foundation Models | Chip Huyen | O'Reilly, 2025 | `consultado` | Trata a construção de aplicações sobre modelos de fundação como disciplina de engenharia, distinta de engenharia de ML. É a referência externa mais próxima do recorte desta plataforma. |
| Designing Machine Learning Systems | Chip Huyen | O'Reilly, 2022 | `canônico` | Sistema de ML em produção: dados, treino, serviço, monitoramento. O que envelheceu do livro foi o modelo; o que não envelheceu foi a disciplina de sistema, que é a parte citada aqui. |
| Prompt Engineering for LLMs: The Art and Science of Building Large Language Model–Based Applications | John Berryman, Albert Ziegler | O'Reilly, 2024 | `consultado` | Prompt como componente de aplicação — e não como texto avulso. Referência dos volumes `07-PROMPT-ENGINE`, `28-PROMPT-COMPILER` e `29-PROMPT-OPTIMIZER`. |
| Natural Language Processing with Transformers | Lewis Tunstall, Leandro von Werra, Thomas Wolf | O'Reilly, 2022 (edição revisada) | `consultado` | O nível abaixo da API: tokenização, atenção, ajuste fino. Serve a quem precisa entender por que o prompt se comporta como se comporta. |

## Sistemas, arquitetura e dados

| Livro | Autoria | Editora / ano | Verificação | Por que está aqui |
|---|---|---|---|---|
| Designing Data-Intensive Applications | Martin Kleppmann | O'Reilly, 2017 | `canônico` | Confiabilidade, replicação, consistência. Sustenta os volumes `24-DATABASE-ARCHITECT` e `14-VECTOR`, e o argumento recorrente de que estado durável é uma escolha de projeto. |
| Fundamentals of Software Architecture: An Engineering Approach | Mark Richards, Neal Ford | O'Reilly, 2020 | `consultado` | Arquitetura como disciplina de engenharia, com métricas e características mensuráveis em lugar de adjetivos. Base dos volumes `02-CORE`, `06-ENTERPRISE-ARCHITECTURE` e `22`–`25`. |
| Building Microservices | Sam Newman | O'Reilly | `canônico` | Fronteiras de serviço, contratos e o custo real do desacoplamento. Referência do volume `16-INTEGRATION`. |
| Clean Architecture | Robert C. Martin | Pearson / Prentice Hall | `canônico` | Regras de dependência e separação de camadas. Citado onde o acervo defende que a regra de negócio não pertence ao prompt. |

## Prática de engenharia e operação

| Livro | Autoria | Editora / ano | Verificação | Por que está aqui |
|---|---|---|---|---|
| Software Engineering at Google: Lessons Learned from Programming Over Time | Titus Winters, Tom Manshreck, Hyrum Wright | O'Reilly, 2020 | `consultado` | Sustentabilidade de base de código ao longo do tempo — teste, revisão, documentação como parte da engenharia. É a defesa mais completa da tese central desta plataforma: gate automatizado supera intenção declarada. |
| Site Reliability Engineering | Betsy Beyer, Chris Jones, Jennifer Petoff, Niall Richard Murphy (orgs.) | O'Reilly, 2016 | `canônico` | Objetivos de nível de serviço, orçamento de erro, análise de incidente sem culpa. Base do volume `21-OBSERVABILITY`. |
| Accelerate: The Science of Lean Software and DevOps | Nicole Forsgren, Jez Humble, Gene Kim | IT Revolution, 2018 | `canônico` | Mede o efeito de práticas de entrega em desempenho organizacional. Citado onde o acervo argumenta com evidência em vez de preferência. |
| Team Topologies: Organizing Business and Technology Teams for Fast Flow | Matthew Skelton, Manuel Pais | IT Revolution, 2019 | `consultado` | Desenho de equipe e modos de interação. Aparece na discussão de sistemas multiagente: papel estreito e interface explícita valem para pessoas e para agentes pelo mesmo motivo. |

## O que ficou de fora, e por quê

- **Livros sobre modelos ou APIs específicas.** Envelhecem em meses. Material perecível aponta
  para fonte viva — ver [`links.md`](links.md) e a marca `perecivel: true` no contrato.
- **Livros de "prompts prontos" e coletâneas de fórmulas.** Ensinam o formato e não o critério.
  As seis técnicas em [`frameworks/conhecidos/`](../frameworks/conhecidos/) cobrem o formato com
  as limitações declaradas, o que essas coletâneas em geral não fazem.
- **Todo título cuja autoria ou editora eu não pude confirmar.** Alguns candidatos plausíveis
  ficaram fora por isso. Um livro a mais na lista não vale a chance de mandar alguém procurar
  uma obra que não existe com aquele nome.
- **Números de edição atual.** Ao menos três dos livros acima têm edição posterior à indicada
  (arquitetura, topologias de equipe, transformers). Registramos a edição verificada e não a
  "atual", porque "atual" é um campo que fica falso sozinho, sem que ninguém edite o arquivo.
