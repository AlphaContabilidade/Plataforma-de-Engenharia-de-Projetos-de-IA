---
name: aieos-cross-reference
description: Roda o gate 3 do acervo AI-ENGINEERING-OS — `python -m ferramentas.validar --cross-refs`, que checa `depende_de` inexistente e ciclo no grafo de pré-requisitos — e, se verde, despacha o subagente `auditor-fable` para um passe semântico procurando contradições entre volumes. Use quando o pedido for `/cross-reference`, "checar referências cruzadas", "os volumes se contradizem?" ou "rodar o gate 3".
---

# `/cross-reference`

Procedimento em duas metades, e a ordem importa: primeiro a checagem **determinística**,
depois a **semântica**. Rodar o passe semântico sobre um grafo quebrado produz achados sobre
o problema errado.

**Rode de dentro de `AI-ENGINEERING-OS/`.**

## 1. Gate 3 — determinístico

```bash
python -m ferramentas.validar --cross-refs
```

Exit 0 e "ok: referencias cruzadas sem violacoes" é o resultado verde. Exit 1 lista as
violações; exit 2 é erro de contrato.

Duas regras, e só estas duas, são checadas aqui:

| Regra | O que significa | Como corrigir |
|---|---|---|
| `depende-de-inexistente` | um `depende_de` aponta para um id que **não está declarado** em `contrato.json` | corrija o id no `_VOLUME.yml`; ids são **strings de 2 dígitos** (`"08"`, não `8` nem `AGENT-ENGINE`) |
| `depende-de-ciclo` | há ciclo no grafo de pré-requisitos, com o caminho impresso na mensagem | remova a aresta errada — quase sempre é "assunto vizinho" disfarçado de pré-requisito |

Cole a saída na resposta. Se estiver vermelha, **pare**: corrija os `_VOLUME.yml` apontados,
rode de novo até exit 0 e só então siga para o passo 2.

## 2. O que `depende_de` significa — a causa da maioria dos ciclos falsos

`depende_de` é **pré-requisito de leitura**, uma relação **acíclica e direcionada**: "não dá
para entender este volume sem ter lido aquele". Não é "assunto próximo".

Vizinhança bidirecional entre volumes mora em `18-Referencias-Cruzadas.md` e **não entra no
grafo** — de propósito. Se entrasse, `07-PROMPT-ENGINE` e `28-PROMPT-COMPILER`, que se citam
mutuamente, formariam um ciclo falso e o gate 3 reprovaria por nada.

Diante de um `depende-de-ciclo`, a pergunta certa não é "como faço o validador aceitar", é
**"qual das duas arestas é só vizinhança?"** — essa sai do `_VOLUME.yml` e vai para
`18-Referencias-Cruzadas.md`. Nunca ajuste a regra nem o teste para o grafo passar.

Só volumes **materializados** (pasta em disco) entram no grafo. Volume declarado no contrato
e ainda sem pasta não é violação; `depende_de` apontando para ele também não é, desde que o
id exista no contrato.

## 3. Passe semântico — só com o gate 3 verde

Despache o subagente `auditor-fable` (`.claude/agents/auditor-fable.md`, modelo Fable 5) em
**modo `/cross-reference`**. O que ele procura é o que nenhum programa pega:

- **mesma sigla ou termo com dois significados** em volumes diferentes;
- **decisão arquitetural afirmada em um volume e negada em outro**;
- **número divergente para a mesma grandeza** (limiar, unidade, alíquota de custo);
- **assunto reivindicado como "fonte" por dois volumes** ao mesmo tempo;
- **`depende_de` que está tecnicamente válido mas semanticamente invertido** — B declarado
  pré-requisito de A quando é A que introduz o vocabulário de B.

No prompt do despacho, informe: os volumes com seções escritas (a coluna `Secoes` de
`/status` diz quais), o grafo `depende_de` resolvido, e a instrução de devolver **apenas** a
lista de contradições com os dois arquivos envolvidos e a frase de cada lado. Nesse modo
**não há nota por seção nem linha `media:`**, e **nada é gravado em `auditorias/`** — o
formato de `status.py::nota_da_ultima_auditoria` é para auditoria de volume, e um arquivo
`VOL-NN-auditoria-*.md` escrito aqui poluiria a nota daquele volume.

Ele **não edita volume nenhum**. Contradição encontrada é achado; a correção é passada
seguinte, com `/novo-volume` ou incorporação manual, e cada lado corrigido volta ao gate 1.

## 4. Reportar

- a saída colada de `python -m ferramentas.validar --cross-refs`;
- se rodou o passe semântico, as contradições encontradas com os dois arquivos e as duas
  frases; se não rodou (gate 3 vermelho), diga que não rodou e por quê;
- o que precisa ser corrigido e em qual arquivo.

Nenhuma contradição encontrada é resultado legítimo — escreva isso. O que não é legítimo é
afirmar que o acervo é coerente sem ter rodado o passe.
