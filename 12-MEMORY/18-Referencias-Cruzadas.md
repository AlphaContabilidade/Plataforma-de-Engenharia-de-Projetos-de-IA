---
volume: "12"
volume_nome: MEMORY
tipo: ENGINE
secao: 18-Referencias-Cruzadas
status: RASCUNHO
atualizado_em: 2026-07-30
---

# Referências cruzadas

Esta seção registra as relações deste volume com o resto da plataforma, e distingue dois tipos de
relação. **Pré-requisito de leitura** entra no campo `depende_de` do `_VOLUME.yml` e é verificado
como grafo acíclico pelo terceiro gate. **Vizinhança de assunto** é bidirecional, fica descrita
aqui em prosa, e não entra no grafo — sem essa separação, a relação recíproca entre este volume e
o 11 apareceria como ciclo falso.

O campo `depende_de` está **vazio**, e isso é uma afirmação e não uma omissão. O volume 11,
`KNOWLEDGE`, é o vizinho mais próximo e a fonte natural da origem `BASE_CONGELADA`, mas ele ainda
não tem seção escrita: existe apenas como pasta com metadados. Apontar `depende_de` para um
volume sem conteúdo passaria o gate de existência e produziria um pré-requisito de leitura que
não pode ser lido, o que é pior que dependência nenhuma. Por isso, nenhuma linha desta seção
aponta para um arquivo de seção dentro dos volumes vizinhos: link para arquivo inexistente é
reprovado pela regra `link-morto`. As relações estão em prosa e serão convertidas em link quando
os vizinhos tiverem conteúdo.

## Vizinhança de assunto

| Volume vizinho | Relação | Direção |
|---|---|---|
| 11, `KNOWLEDGE` — [`../11-KNOWLEDGE/_VOLUME.yml`](../11-KNOWLEDGE/_VOLUME.yml) | Cura a base congelada: autoridade, validade e recuratoria do documento | O 11 alimenta a origem `BASE_CONGELADA` e recebe as contradições abertas |
| 13, `RAG` — [`../13-RAG/_VOLUME.yml`](../13-RAG/_VOLUME.yml) | Recupera por proximidade quando a igualdade de chave falha | O 13 consome a chave; a memória não ranqueia |
| 15, `CONTEXT` — [`../15-CONTEXT/_VOLUME.yml`](../15-CONTEXT/_VOLUME.yml) | Orça a janela do modelo; o veredicto é um item candidato a entrar nela | O 15 consome o `Veredicto` |
| 14, `VECTOR` — [`../14-VECTOR/_VOLUME.yml`](../14-VECTOR/_VOLUME.yml) | Índice e similaridade; nenhuma estrutura daqui é vetorial | Sem dependência de leitura |
| 08, `AGENT-ENGINE` — [`../08-AGENT-ENGINE/_VOLUME.yml`](../08-AGENT-ENGINE/_VOLUME.yml) | O laço de agente pergunta e age, ou para quando o veredicto é indeciso | O 08 consome este volume |
| 07, `PROMPT-ENGINE` — [`../07-PROMPT-ENGINE/03-Escopo.md`](../07-PROMPT-ENGINE/03-Escopo.md) | Assunto disjunto; serve de implementação de referência para a declaração de fronteira | Complementar |
| 21, `OBSERVABILITY` — [`../21-OBSERVABILITY/_VOLUME.yml`](../21-OBSERVABILITY/_VOLUME.yml) | Coleta e exibe as métricas que este volume define | O 21 consome as métricas |

## Links que resolvem hoje

| Destino | O que é |
|---|---|
| [`../00-INTRODUCAO/contrato.json`](../00-INTRODUCAO/contrato.json) | Contrato legível por máquina: seções, tipos, mínimos e marcadores proibidos |
| [`../00-INTRODUCAO/Convencoes.md`](../00-INTRODUCAO/Convencoes.md) | O mesmo contrato em forma humana, com a definição de pronto |
| [`../ROADMAP.md`](../ROADMAP.md) | A decisão de resolver sobreposição por fronteira, que esta seção e o escopo obedecem |
| [`../exemplos/12-memory/memoria_observada.py`](../exemplos/12-memory/memoria_observada.py) | Armazém com procedência |
| [`../exemplos/12-memory/contaminacao.py`](../exemplos/12-memory/contaminacao.py) | Guarda de contaminação e relatório de contradição |
| [`../exemplos/12-memory/precedencia.py`](../exemplos/12-memory/precedencia.py) | Regra de precedência e veredicto |
| [`../exemplos/12-memory/tests/test_contaminacao.py`](../exemplos/12-memory/tests/test_contaminacao.py) | O teste que impede o eco de silenciar a contradição |
| [`../exemplos/12-memory/tests/test_precedencia.py`](../exemplos/12-memory/tests/test_precedencia.py) | O teste que impede a precedência de virar cascata |

## Navegação interna

A leitura mínima, para quem vai escrever código contra o componente, é
[`08-Modelos.md`](08-Modelos.md) seguido de [`12-Exemplos.md`](12-Exemplos.md). Para quem vai
operar as pendências e as contradições, é [`07-Regras.md`](07-Regras.md), depois
[`06-Fluxogramas.md`](06-Fluxogramas.md) e [`15-Checklist.md`](15-Checklist.md). Para quem vai
estender, é [`04-Arquitetura.md`](04-Arquitetura.md), [`03-Escopo.md`](03-Escopo.md) e
[`16-Roadmap.md`](16-Roadmap.md), nessa ordem — a fronteira antes da extensão.
