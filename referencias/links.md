# Links

> Biblioteca transversal · atualizado em 2026-07-29

## Como esta lista foi montada

**Todas as URLs abaixo foram abertas em 2026-07-29** e o conteúdo conferido contra o que a
linha afirma. Nenhuma foi escrita de memória. A verificação apanhou uma mudança relevante: a
documentação do LangChain, antes em `python.langchain.com/docs/introduction`, responde hoje com
redirecionamento permanente para `docs.langchain.com` — motivo pelo qual o endereço registrado
aqui é o de destino, não o antigo.

**Esta é a mais perecível das três listas de `referencias/`.** URL não avisa quando quebra, e
página que continua respondendo pode ter mudado de conteúdo sem mudar de endereço — que é a
falha pior, porque é silenciosa. Por isso cada linha tem data de consulta: ela não garante que
o link esteja bom hoje, mas diz quando alguém olhou.

**Regra de manutenção:** só entra URL que você abriu. Ao revisar, reabra e atualize a data —
não presuma que continua válida porque estava aqui.

## Documentação de frameworks citados neste acervo

| Recurso | URL | Consultado | Observação |
|---|---|---|---|
| LangChain — documentação oficial (Python) | <https://docs.langchain.com/oss/python/langchain/overview> | 2026-07-29 | Endereço atual; o anterior redireciona. Ver [`frameworks/conhecidos/langchain.md`](../frameworks/conhecidos/langchain.md). |
| CrewAI — documentação oficial | <https://docs.crewai.com/> | 2026-07-29 | Primitivas Agent, Task, Crew, Flow. |
| AutoGen — documentação estável (Microsoft) | <https://microsoft.github.io/autogen/stable/> | 2026-07-29 | Pacotes Core, AgentChat, Studio, Extensions. Cuidado com material anterior à reescrita de arquitetura. |
| Semantic Kernel — visão geral (Microsoft Learn) | <https://learn.microsoft.com/en-us/semantic-kernel/overview/> | 2026-07-29 | C#, Python e Java; kernel, plugins, conectores, filtros. |
| Model Context Protocol | <https://modelcontextprotocol.io/> | 2026-07-29 | Padrão aberto para conectar aplicações de IA a dados, ferramentas e fluxos. Relevante para `16-INTEGRATION` e `42-PLUGINS`. |

## Guias de engenharia de prompt

| Recurso | URL | Consultado | Observação |
|---|---|---|---|
| Prompt Engineering Guide (DAIR.AI) | <https://www.promptingguide.ai/> | 2026-07-29 | Guia aberto, com repositório público; cobre técnicas, modelos e artigos. Bom ponto de entrada e razoavelmente bem referenciado. |
| Learn Prompting | <https://learnprompting.org/> | 2026-07-29 | Plataforma educacional conduzida por Sander Schulhoff — o mesmo primeiro autor do levantamento *The Prompt Report* em [`papers.md`](papers.md). Parte do conteúdo é pago. |

## Padrões, normas e ferramentas da plataforma

| Recurso | URL | Consultado | Observação |
|---|---|---|---|
| Mermaid — biblioteca de diagramas | <https://mermaid.js.org/> | 2026-07-29 | Biblioteca JavaScript de código aberto para diagramas em texto. É o formato exigido pelo contrato desta plataforma, com a regra do parágrafo descritivo após cada bloco. |
| MkDocs | <https://www.mkdocs.org/> | 2026-07-29 | Gerador de site estático a partir de Markdown, configurado por um único arquivo YAML — é o `mkdocs.yml` que `/exportar` gera. |
| pytest — documentação oficial | <https://docs.pytest.org/> | 2026-07-29 | O gate 4 da plataforma (teste dos exemplos) é uma execução de pytest. |
| C4 model | <https://c4model.com/> | 2026-07-29 | Modelo de Simon Brown para diagramar arquitetura em quatro níveis (sistema, contêiner, componente, código). Os tipos `ENGINE` e `ARQUITETURA` exigem diagrama de contexto C4. |
| Architectural Decision Records | <https://adr.github.io/> | 2026-07-29 | Vocabulário e ferramentas para registrar decisão de arquitetura com razão e consequências — a forma canônica do padrão descrito em [`frameworks/conhecidos/BAB.md`](../frameworks/conhecidos/BAB.md). |
| OWASP Top 10 for Large Language Model Applications | <https://owasp.org/www-project-top-10-for-large-language-model-applications/> | 2026-07-29 | Riscos críticos em aplicações com LLM (injeção de prompt, tratamento inseguro de saída, envenenamento de dados de treino, entre outros). Referência obrigatória dos volumes `17-SECURITY` e `30-AI-GOVERNANCE`. |
| arXiv | <https://arxiv.org/> | 2026-07-29 | Repositório onde estão os quinze artigos de [`papers.md`](papers.md); cada identificador foi conferido individualmente na página de resumo. |

## O que não está aqui, e por quê

- **Nenhuma página de preços de provedor de modelo.** Preço muda sem aviso e um número
  desatualizado num arquivo de acervo é pior que nenhum número, porque parece atual. Esse
  material pertence aos volumes marcados `perecivel: true` (`26-AI-MODELS`, `27-LLM-ROUTER`,
  `34-COST-OPTIMIZATION`), cuja instrução é apontar para a fonte viva no momento da consulta.
- **Nenhum comparativo de desempenho ou placar de modelos.** Mesma razão, agravada: placar cuja
  metodologia não foi lida é opinião com aparência de medida.
- **Nenhum blog, vídeo ou fio de rede social.** Não porque não haja bom material assim, mas
  porque a taxa de link quebrado é alta e a de conteúdo alterado sem aviso é maior ainda.
  Quando uma ideia vinda de post importa, ela entra no volume com a ideia explicada — não como
  link a ser clicado.
- **Nenhuma URL que eu não abri.** Havia candidatas óbvias, inclusive de páginas que
  provavelmente existem. "Provavelmente existe" não é o critério desta pasta.
