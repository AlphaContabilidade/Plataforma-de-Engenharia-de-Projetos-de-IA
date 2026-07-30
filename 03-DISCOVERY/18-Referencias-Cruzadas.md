---
volume: "03"
volume_nome: DISCOVERY
tipo: PROCESSO
secao: 18-Referencias-Cruzadas
status: PRONTO
atualizado_em: 2026-07-30
---

# Referências cruzadas

Esta seção distingue dois tipos de relação. **Pré-requisito de leitura** entra no campo `depende_de` do
`_VOLUME.yml` e é verificado como grafo acíclico pelo terceiro gate. **Vizinhança de assunto** é
bidirecional, fica descrita aqui em prosa, e não entra no grafo — sem essa separação, a relação
recíproca entre este volume e o 04 apareceria como ciclo falso.

O campo `depende_de` está **vazio**, e isso é uma afirmação e não uma omissão. Os três vizinhos mais
próximos — 04, 05 e 38 — ainda não têm seção escrita: existem apenas como pasta com metadados. Apontar
`depende_de` para volume sem conteúdo passaria o gate de existência e produziria um pré-requisito de
leitura que não pode ser lido, o que é pior que dependência nenhuma. Por isso nenhuma linha desta seção
aponta para arquivo de seção dentro desses três volumes: link para arquivo inexistente é reprovado pela
regra `link-morto`.

## Vizinhança de assunto

| Volume vizinho | Relação | Direção |
|---|---|---|
| 04, `REQUIREMENTS` — [`../04-REQUIREMENTS/_VOLUME.yml`](../04-REQUIREMENTS/_VOLUME.yml) | Recebe a especificação e a converte em requisito numerado, com critério de aceite e rastreabilidade | O 04 consome a saída deste volume |
| 05, `BUSINESS` — [`../05-BUSINESS/_VOLUME.yml`](../05-BUSINESS/_VOLUME.yml) | Julga se a ideia compensa; consome a resposta de sucesso e a lista de decisões abertas | O 05 consome a saída; este volume não opina sobre viabilidade |
| 38, `PROJECT-PLANNER` — [`../38-PROJECT-PLANNER/_VOLUME.yml`](../38-PROJECT-PLANNER/_VOLUME.yml) | Sequencia e estima; trata decisão aberta como risco que pode mudar estimativa já dada | O 38 consome as decisões abertas |
| 12, `MEMORY` — [`../12-MEMORY/03-Escopo.md`](../12-MEMORY/03-Escopo.md) | Origem da ideia de procedência e do resultado indeciso de primeira classe; dono da persistência entre sessões | Fonte conceitual e implementação de referência |
| 07, `PROMPT-ENGINE` — [`../07-PROMPT-ENGINE/03-Escopo.md`](../07-PROMPT-ENGINE/03-Escopo.md) | Contrato do prompt de quem colocar um modelo conduzindo a conversa; padrão de rigor para a declaração de fronteira | Complementar; assunto disjunto |
| 22, `FRONTEND-ARCHITECT` — [`../22-FRONTEND-ARCHITECT/_VOLUME.yml`](../22-FRONTEND-ARCHITECT/_VOLUME.yml) | Apresenta pergunta, motivo e opções; o motor não conhece tela | O 22 consome a interface deste volume |
| 21, `OBSERVABILITY` — [`../21-OBSERVABILITY/_VOLUME.yml`](../21-OBSERVABILITY/_VOLUME.yml) | Coleta e exibe as sete métricas definidas aqui | O 21 consome as métricas |

## Links que resolvem hoje

| Destino | O que é |
|---|---|
| [`../00-INTRODUCAO/contrato.json`](../00-INTRODUCAO/contrato.json) | Contrato legível por máquina: seções por tipo, mínimos, marcadores proibidos |
| [`../00-INTRODUCAO/Convencoes.md`](../00-INTRODUCAO/Convencoes.md) | O mesmo contrato em forma humana, com a definição de pronto |
| [`../ROADMAP.md`](../ROADMAP.md) | A decisão de resolver sobreposição por fronteira e a dívida técnica do caminho de import |
| [`../exemplos/03-discovery/catalogo.py`](../exemplos/03-discovery/catalogo.py) | As lacunas e os gatilhos |
| [`../exemplos/03-discovery/deteccao.py`](../exemplos/03-discovery/deteccao.py) | Inferência com evidência |
| [`../exemplos/03-discovery/entrevista.py`](../exemplos/03-discovery/entrevista.py) | Ordem, destravamento e parada |
| [`../exemplos/03-discovery/especificacao.py`](../exemplos/03-discovery/especificacao.py) | As três listas e a completude |
| [`../exemplos/03-discovery/tests/test_deteccao.py`](../exemplos/03-discovery/tests/test_deteccao.py) | O teste que impede a evidência de voltar a ser idêntica entre palpites |
| [`../exemplos/03-discovery/tests/test_especificacao.py`](../exemplos/03-discovery/tests/test_especificacao.py) | O teste que impede a especificação de se declarar completa sem estar |

## Navegação interna

Para quem vai escrever código contra o motor, a leitura mínima é [`11-Implementacao.md`](11-Implementacao.md)
seguido de [`12-Exemplos.md`](12-Exemplos.md). Para quem vai conduzir entrevistas, é
[`07-Regras.md`](07-Regras.md), depois [`06-Fluxogramas.md`](06-Fluxogramas.md) e
[`15-Checklist.md`](15-Checklist.md). Para quem vai estender o catálogo, é [`03-Escopo.md`](03-Escopo.md),
[`09-Boas-Praticas.md`](09-Boas-Praticas.md) e [`16-Roadmap.md`](16-Roadmap.md), nessa ordem — a fronteira
antes da extensão.
