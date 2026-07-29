---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 18-Referencias-Cruzadas
status: PRONTO
atualizado_em: 2026-07-29
---

# Referências cruzadas

Esta seção registra as relações deste volume com o resto da plataforma. Ela distingue dois tipos
de relação, e a distinção é operacional: **pré-requisito de leitura** entra no campo `depende_de`
do `_VOLUME.yml` e é verificado como grafo acíclico pelo terceiro gate; **vizinhança de assunto**
é bidirecional, fica descrita aqui em prosa, e não entra no grafo. Sem essa separação, a relação
recíproca entre o volume 07 e o volume 28 apareceria como ciclo falso e reprovaria a verificação
cruzada.

O campo `depende_de` deste volume está **vazio**, e isso é uma afirmação, não uma omissão: o motor
descrito aqui não exige leitura prévia de nenhum outro volume para ser compreendido ou usado. Os
volumes vizinhos listados abaixo ainda não foram materializados como pasta — nesta data existem
apenas `00-INTRODUCAO` e este volume. Por isso nenhuma linha desta seção aponta para arquivo
dentro deles: um link para seção inexistente seria reprovado pela regra `link-morto`, e apontar
para volume não declarado seria reprovado por `depende-de-inexistente`. A relação está descrita
em texto e será convertida em link quando o volume vizinho existir.

## Vizinhança de assunto

| Volume vizinho | Relação | Direção da dependência |
|---|---|---|
| 01, `FUNDACAO` | Define a governança de estado e a definição de pronto que este volume obedece | O 07 obedece; a leitura do 01 não é pré-requisito para usar o motor |
| 08, `AGENT-ENGINE` | O laço de agente é consumidor do motor: pede a versão promovida e não conhece o registro | O 08 consome o 07 |
| 27, `LLM-ROUTER` | Decide onde executar; mora atrás do executor injetado e é invisível para o motor | O 27 é implementação possível do executor |
| 28, `PROMPT-COMPILER` | Compila o mesmo contrato para dialetos de provedores diferentes | O 28 consome o par corpo e assinatura deste volume |
| 29, `PROMPT-OPTIMIZER` | Usa `avaliar` como função objetivo de um laço de busca sobre variações do corpo | O 29 consome o avaliador deste volume |
| 31, `TESTING` | Define a estratégia geral de teste; aqui fica apenas a do motor | Complementar, sem dependência de leitura |
| 34, `COST-OPTIMIZATION` | Otimiza o custo que este volume apenas mede | O 34 consome a métrica de custo por execução |

## Links que resolvem hoje

| Destino | O que é |
|---|---|
| [`../00-INTRODUCAO/contrato.json`](../00-INTRODUCAO/contrato.json) | Contrato legível por máquina: seções, tipos, mínimos e marcadores proibidos |
| [`../exemplos/07-prompt-engine/prompt_template.py`](../exemplos/07-prompt-engine/prompt_template.py) | Contrato tipado do prompt |
| [`../exemplos/07-prompt-engine/prompt_registry.py`](../exemplos/07-prompt-engine/prompt_registry.py) | Registro versionado e máquina de estados |
| [`../exemplos/07-prompt-engine/prompt_evaluator.py`](../exemplos/07-prompt-engine/prompt_evaluator.py) | Avaliador com executor injetado |
| [`../prompts/prompt-engineering/_indice.md`](../prompts/prompt-engineering/_indice.md) | Os três prompts extraídos deste volume |
| [`../frameworks/_catalogo.md`](../frameworks/_catalogo.md) | Catálogo de técnicas de estruturação de prompt, com estado de atribuição declarado |
| [`../frameworks/conhecidos/RTF.md`](../frameworks/conhecidos/RTF.md) | Exemplo de técnica de escrita aplicável ao corpo de um `PromptTemplate` |

## Navegação interna

A leitura mínima deste volume, para quem vai escrever código contra o motor, é
[`08-Modelos.md`](08-Modelos.md) seguido de [`12-Exemplos.md`](12-Exemplos.md). Para quem vai
operar promoções, é [`07-Regras.md`](07-Regras.md) seguido de
[`15-Checklist.md`](15-Checklist.md) e [`14-Metricas.md`](14-Metricas.md). Para quem vai estender
o motor, é [`04-Arquitetura.md`](04-Arquitetura.md), [`03-Escopo.md`](03-Escopo.md) e
[`16-Roadmap.md`](16-Roadmap.md), nessa ordem — a fronteira antes da extensão.
