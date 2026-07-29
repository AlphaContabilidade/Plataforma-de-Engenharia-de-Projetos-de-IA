# ROADMAP

**Atualizado em:** 2026-07-29

Estado hoje: a máquina de produção está completa e testada, o contrato está em v1.0.0, e um
volume-piloto padrão-ouro (`07-PROMPT-ENGINE`) atravessou a linha inteira. Os outros **41
volumes** estão declarados no contrato e materializados como pasta com `_VOLUME.yml`, em
`RASCUNHO`, sem seções escritas.

A ordem de produção não é a ordem numérica. Um volume só deve ser escrito depois dos volumes
que ele declara em `depende_de`, porque `depende_de` significa pré-requisito de leitura — e
escrever fora de ordem produz seções que citam contrato que ainda não existe.

## Metas numéricas do autor

A especificação original declarava, como resultado esperado:

- 8.000+ páginas
- 2.000+ prompts
- 300+ agentes
- 500+ exemplos de código funcionais

**Estes números são estimativa da especificação original e explicitamente não são critério de
aceite desta plataforma.** Ficam registrados aqui para preservar a intenção do autor, não
para medir progresso.

A razão é direta: **contagem de páginas premia enchimento.** Um acervo avaliado por volume de
texto tem incentivo para escrever mais, não melhor — e a única forma de preencher 42 volumes
por 18 seções, ou seja 744 arquivos de seção, é deixar o conteúdo genérico. Isso contradiz a
regra que a própria especificação estabeleceu: nunca gerar conteúdo superficial. Duas metas
que se anulam não são duas metas; são uma escolha adiada.

O critério de aceite é a **Definição de PRONTO**, descrita em
[00-INTRODUCAO/Convencoes.md](00-INTRODUCAO/Convencoes.md): gate estrutural verde, testes dos
exemplos verdes, auditoria com média maior ou igual a 8,0 sem nenhuma seção abaixo de 6, e
registro datado no `CHANGELOG.md`. É um critério que o **gate mede** em vez de estimar — ele
reprova prosa abaixo do mínimo, diagrama sem descrição, exemplo sem teste e link morto, e não
tem nenhuma opinião sobre quantas páginas o volume tem.

Consequência prática, para quem for produzir: se um volume ficar mais curto do que a
estimativa sugeria e passar nos três gates com auditoria acima de 8,0, ele está pronto. Se
ficar longo e reprovar, não está. O número de páginas nunca entra na decisão.

Um contraponto honesto: o limiar de palavras por seção (200 no geral, menos em quatro seções
naturalmente curtas) é uma contagem, e portanto tem o mesmo defeito em miniatura. Ele existe
como **piso, não como meta** — reprova vazio, não premia extensão — e conta apenas palavras
de prosa, ignorando código, justamente para não poder ser satisfeito colando arquivos.

## Volumes pendentes

Quantidade de seções por tipo: `ENGINE`, `ARQUITETURA` e `GOVERNANCA` exigem as 18 da base;
`PROCESSO` dispensa `08-Modelos` (17); `BIBLIOTECA` troca `04-Arquitetura` e `05-Diagramas`
por `04-Catalogo` (17). Somados, os 41 pendentes representam 726 arquivos de seção.

| Vol | Nome | Tipo | Seções | Observação |
|---|---|---|---|---|
| 01 | FUNDACAO | GOVERNANCA | 18 | base conceitual; candidato natural a ser o próximo |
| 02 | CORE | ARQUITETURA | 18 | depende de 01 |
| 03 | DISCOVERY | PROCESSO | 17 | |
| 04 | REQUIREMENTS | PROCESSO | 17 | |
| 05 | BUSINESS | PROCESSO | 17 | |
| 06 | ENTERPRISE-ARCHITECTURE | ARQUITETURA | 18 | |
| 08 | AGENT-ENGINE | ENGINE | 18 | vizinho direto do piloto; exemplos executáveis obrigatórios |
| 09 | ORCHESTRATOR | ENGINE | 18 | fronteira com 10 precisa ser explícita |
| 10 | WORKFLOW | ENGINE | 18 | fronteira com 09 precisa ser explícita |
| 11 | KNOWLEDGE | ENGINE | 18 | domínio sobreposto a 13, 14 e 15; escopo precisa ser negociado antes de escrever |
| 12 | MEMORY | ENGINE | 18 | |
| 13 | RAG | ENGINE | 18 | domínio sobreposto a 11, 14 e 15 |
| 14 | VECTOR | ENGINE | 18 | domínio sobreposto a 11, 13 e 15 |
| 15 | CONTEXT | ENGINE | 18 | domínio sobreposto a 11, 13 e 14 |
| 16 | INTEGRATION | ARQUITETURA | 18 | fronteira com 22 a 25 precisa ser explícita |
| 17 | SECURITY | GOVERNANCA | 18 | domínio sobreposto a 18 |
| 18 | DEVSECOPS | PROCESSO | 17 | domínio sobreposto a 17 |
| 19 | DEVOPS | ARQUITETURA | 18 | |
| 20 | CLOUD | ARQUITETURA | 18 | |
| 21 | OBSERVABILITY | GOVERNANCA | 18 | |
| 22 | FRONTEND-ARCHITECT | ARQUITETURA | 18 | quatro volumes `*-ARCHITECT` competem com 16 |
| 23 | BACKEND-ARCHITECT | ARQUITETURA | 18 | |
| 24 | DATABASE-ARCHITECT | ARQUITETURA | 18 | |
| 25 | API-ARCHITECT | ARQUITETURA | 18 | |
| 26 | AI-MODELS | ENGINE | 18 | **perecível**: fino, sem preço nem nome de modelo fixado |
| 27 | LLM-ROUTER | ENGINE | 18 | **perecível**: método de roteamento, não tabela de custo |
| 28 | PROMPT-COMPILER | ENGINE | 18 | mesmo domínio de 07 e 29; escopo precisa ser negociado |
| 29 | PROMPT-OPTIMIZER | ENGINE | 18 | mesmo domínio de 07 e 28 |
| 30 | AI-GOVERNANCE | GOVERNANCA | 18 | |
| 31 | TESTING | PROCESSO | 17 | domínio sobreposto a 32 |
| 32 | QUALITY | PROCESSO | 17 | domínio sobreposto a 31 |
| 33 | PERFORMANCE | PROCESSO | 17 | |
| 34 | COST-OPTIMIZATION | PROCESSO | 17 | **perecível**: método de medir custo por tarefa |
| 35 | DOCUMENTATION | GOVERNANCA | 18 | |
| 36 | DIAGRAMS | BIBLIOTECA | 17 | catálogo em `04-Catalogo`, sem arquitetura própria |
| 37 | CODE-GENERATION | ENGINE | 18 | |
| 38 | PROJECT-PLANNER | PROCESSO | 17 | |
| 39 | ROADMAP | PROCESSO | 17 | |
| 40 | TEMPLATES | BIBLIOTECA | 17 | catálogo em `04-Catalogo` |
| 41 | SDK | ENGINE | 18 | hoje só esqueleto e `README` de intenção |
| 42 | PLUGINS | ENGINE | 18 | |

## Decisão pendente: sobreposição de domínios

Os 42 rótulos cobrem cerca de 25 domínios distintos. Quatro grupos se sobrepõem de forma que
vai gerar contradição entre volumes se não for resolvida antes da escrita:

1. `07` / `28` / `29` — o domínio de prompts.
2. `11` / `13` / `14` / `15` — o domínio de conhecimento e contexto.
3. `17` / `18` e `31` / `32` — segurança e qualidade, cada par com dois nomes para um assunto.
4. `22` a `25` contra `16` — arquitetura por camada contra integração.

Duas saídas possíveis: fundir volumes, reduzindo a contagem; ou manter os 42 e escrever
`03-Escopo` de cada um declarando explicitamente o que pertence ao vizinho. A segunda é mais
trabalhosa e preserva a estrutura pedida pelo autor. **Decisão do autor, não da máquina** —
até que ela seja tomada, escrever qualquer volume desses grupos é assumir risco de retrabalho.

## Fora de escopo neste ciclo

Registrado, não construído agora:

- os 41 volumes com conteúdo (apenas `_VOLUME.yml` e registro de pendência);
- o SDK além do esqueleto e um `README` de intenção;
- a biblioteca de agentes além do `_template-agente.md` e do `_catalogo.md`;
- as bibliotecas de prompts por stack, banco e framework além do que o piloto usa;
- diagramas soltos em `diagramas/` (o piloto tem os seus dentro do volume);
- integração contínua rodando os gates a cada push;
- os frameworks sem definição listados em `frameworks/_backlog.md`, que aguardam o autor
  definir escopo, entradas e saídas — não serão inventados.
