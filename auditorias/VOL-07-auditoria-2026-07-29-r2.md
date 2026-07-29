# Auditoria (r2) — Volume 07 PROMPT-ENGINE

**Data:** 2026-07-29
**Revisao:** 2
**Auditor:** auditor-fable (Fable 5)
**Gates na entrada:**

```
$ python -m ferramentas.validar 07
ok: volume 07 sem violacoes
(exit 0)

$ python -m ferramentas.validar --cross-refs
ok: referencias cruzadas sem violacoes
(exit 0)

$ python -m pytest exemplos -q
.......................................                                  [100%]
39 passed in 0.19s
(exit 0)
```

## Método

Julgamento formado antes de abrir o relatório anterior, com execução e não só leitura:
os três gates acima; reprodução literal dos cinco blocos de `12-Exemplos.md` em script
contra `exemplos/07-prompt-engine/` (todos os `assert` passaram, incluindo as afirmações
de prosa — trilha final `v1 DEPRECIADO / v2 PROMOVIDO`, atalho `VERSIONADO → PROMOVIDO`
levantando `TransicaoInvalida` com a lista de destinos, `obter` sem versão devolvendo a
v2 por identidade); contagem do `stateDiagram-v2` conferida transição a transição contra
`TRANSICOES` (1+2+3+1+0 = 7); assinaturas de `08-Modelos.md` conferidas linha a linha
contra os três `.py`; os três testes nomeados em `13-Testes.md` localizados por nome;
contagem 13+13+11 = 37 funções e 39 casos conferida contra os arquivos e contra a saída
do pytest; template com zero variáveis construído sem erro (cardinalidade do ER); os
sete links de `18-Referencias-Cruzadas.md` resolvidos no disco.

## Notas por seção

| Seção | Nota | Justificativa |
|---|---|---|
| 01-Introducao | 9 | Responde por que o volume existe separado, com o anti-público declarado ("experimento descartável não tem o problema"); nenhuma afirmação desmentida pelo código. |
| 02-Objetivos | 9 | Sete objetivos com critério verificável e local de conferência; todos conferidos contra os testes reais e contra `TRANSICOES` (ausência da aresta `VERSIONADO → PROMOVIDO` confirmada no código). |
| 03-Escopo | 9 | Fronteira em tabela com volume responsável e razão de cada corte; a fronteira interna (registro não importa avaliador e vice-versa) bate com os imports reais. |
| 04-Arquitetura | 9 | `C4Context` e `C4Container` corretos; os parágrafos pós-diagrama explicam (quatro interlocutores, grafo em árvore com raiz no contrato) em vez de repetir o título; cada decisão vem com o custo. |
| 05-Diagramas | 9 | Os quatro diagramas batem com o código: sequência confere com `avaliar`/`transicionar`, máquina de estados tem as sete transições de `TRANSICOES`, ER agora com `CONTRATO \|\|--o{ VARIAVEL` — confirmado executando template de zero variáveis, que constrói sem erro como o parágrafo afirma. |
| 06-Fluxogramas | 9 | Quatro pontos de decisão reais, todos ancorados em mecanismo (construtor, hash, R8, `comparar`); o nó `O` agora é gramatical; o fluxograma de incidente termina com regra operacional concreta (incidente vira caso de ouro). |
| 07-Regras | 9 | As dez regras conferidas uma a uma contra o código — todas verdadeiras; R2 agora declara o alcance completo (nome, tipo, obrigatoriedade dentro; `descricao` fora, com a razão) e o limite é coberto por teste. |
| 08-Modelos | 9 | Assinaturas idênticas às dos três `.py`, incluindo o formato `nome(v1:int, v2?:str)` observado em execução; o limite do hash (`descricao` fora) está registrado com os testes que o fixam. |
| 09-Boas-Praticas | 8 | Pareamento P1–P8 com A1–A8 mantido, toda prática com razão; P2 e P4 são as menos amarradas a mecanismo do motor (dependem de disciplina), o que a própria seção não esconde. |
| 10-Anti-Patterns | 9 | Consequência observável em todos; o parágrafo sobre o escape do `marcador-proibido` em A9 documenta inclusive o abuso possível do escape, e A10 remete corretamente a R8. |
| 11-Implementacao | 9 | Descreve o código que existe, decisão por decisão (regex vs `str.format`, contador próprio vs tamanho, `re.search` vs `re.fullmatch`); as três citações de exemplo verificadas pelo gate 1. |
| 12-Exemplos | 8 | Reproduzido ponta a ponta por script: todos os `assert` e as afirmações de prosa confirmados por máquina, incluindo a nota de granularidade e o limite do rebaixamento automático. Perde ponto por um deslize factual na abertura: "avaliá-lo contra três casos de ouro" quando a bateria executada tem quatro (problema 1). |
| 13-Testes | 9 | A contagem agora é a que o comando imprime: 39 casos, 37 funções (13+13+11), com a razão da divergência (parametrização) explicada; os três testes nomeados existem; a estratégia declara honestamente o que a suíte não prova. |
| 14-Metricas | 9 | Unidade e origem em todas; "falhas por classe de origem" agora tem definição operacional exata (prefixo do `motivo`, conferido contra os dois pontos de saída de `avaliar`); as duas métricas que o motor não calcula estão ditas como tais. |
| 15-Checklist | 9 | Acionável e amarrado a chamadas reais; os dois itens que dependem de evidência externa (passagem por `EM_AVALIACAO` via script, custo via envelope) declaram de onde vem a evidência em vez de supor que existe. |
| 16-Roadmap | 9 | Cada evolução com "por que não entrou agora" concreta (inclusive o novo item do campo enumerado de `Falha`); a regra de revisão de fronteira antes de contorno é governança, não desejo. |
| 17-Conclusao | 9 | Números corretos (39 casos / 37 funções); registra a correção da obrigatoriedade no hash como lição, com o reparo no código e não na prosa; fecha com o limite honesto (estado ≠ resultado bom). |
| 18-Referencias-Cruzadas | 9 | Separação pré-requisito vs vizinhança correta e justificada; `depende_de` vazio explicado; os sete links resolvem no disco (conferido). |

media: 8.9

## Problemas encontrados

1. **`12-Exemplos.md` (parágrafo de abertura): "três casos de ouro" contradiz o próprio
   código da seção.** A abertura descreve o caminho como "avaliá-lo contra três casos de
   ouro", mas a tupla `CASOS` tem **quatro** casos (`tarifa-bancaria`, `energia`,
   `recebimento`, `ambiguo`), o bloco de avaliação assevera `resultado.total == 4`, e o
   parágrafo final da seção fala corretamente em "quatro casos dão granularidade de 0,25".
   O código está certo e reproduz; é a frase de abertura que ficou para trás —
   provavelmente resquício da narrativa em que a v1 foi promovida quando a bateria tinha
   só os três primeiros casos. Correção de uma palavra.

Fora isso, não encontrei problema real nos seis eixos: as assinaturas e nomes de estado
batem com os `.py`, nenhuma seção cumpre palavra sem responder à pergunta, não há
contradição entre seções (a área sensível — formato da assinatura com `?` e alcance do
hash — está consistente em 02, 07, 08, 13 e 17, e coberta por
`test_hash_muda_quando_a_obrigatoriedade_de_uma_variavel_muda`,
`test_hash_ignora_descricao` e `test_mudanca_so_de_obrigatoriedade_gera_v2`), os
diagramas Mermaid estão corretos e explicados, os exemplos executam exatamente como o
texto afirma, e o checklist é acionável. Digo isso explicitamente em vez de inventar
crítica para parecer criterioso.

## Verificação dos achados da auditoria anterior

1. **Cardinalidade do ER (`05-Diagramas.md`)** — **Resolvido.** O ER agora traz
   `CONTRATO ||--o{ VARIAVEL` (zero ou muitas), e o parágrafo seguinte afirma o que o
   código de fato impõe: template estático com tupla vazia é válido (confirmei
   executando — `PromptTemplate('estatico', 'corpo sem placeholder algum', ())` constrói
   e devolve assinatura `estatico()`), e a restrição real é a concordância bidirecional.

2. **Hash não cobria `obrigatoria` e o limite não era registrado** — **Resolvido, pelo
   caminho (a) da sugestão.** `assinatura` agora escreve a opcional como `tom?:str`
   (conferido em execução e em `test_assinatura_em_ordem_alfabetica_e_marca_a_opcional`),
   dois templates que diferem só em `obrigatoria` têm hashes distintos e `registrar`
   devolve `v2` (`test_hash_muda_quando_a_obrigatoriedade_de_uma_variavel_muda`,
   `test_mudanca_so_de_obrigatoriedade_gera_v2`), o limite restante (`descricao` fora do
   hash) está declarado em R2, `08-Modelos.md` e fixado por `test_hash_ignora_descricao`,
   e o docstring de `registrar` não afirma mais "contrato inteiro" — nomeia corpo, nome,
   tipo e obrigatoriedade e declara `descricao` como única exclusão.

3. **Contagem de testes divergia da saída do comando** — **Resolvido.** `13-Testes.md` e
   `17-Conclusao.md` agora dizem 37 funções / 39 casos e explicam a diferença
   (parametrização em três do teste de fronteira). Conferido: 13+13+11 funções `def test_`
   nos três arquivos, e `python -m pytest exemplos -q` imprime `39 passed`.

4. **Rótulo agramatical do nó `O` em `06-Fluxogramas.md`** — **Resolvido.** O nó lê
   `{a comparacao contra a versao promovida mostra deriva positiva?}` — exatamente a
   reformulação sugerida.

5. **Métrica de falhas sem definição operacional (`14-Metricas.md`)** — **Resolvido.**
   A métrica virou "Falhas por classe de origem", definida pelo prefixo fixo do campo
   `motivo` (`render falhou` / `saida nao casa`, que conferem com os dois pontos de
   saída em `prompt_evaluator.py`), com uma subseção inteira explicando por que duas
   classes e não mais, e o campo enumerado futuro registrado em `16-Roadmap.md` com a
   razão de não ter entrado agora.

As sugestões acessórias da auditoria anterior também foram incorporadas: os dois itens
do checklist que pediam evidência inexistente agora apontam o script de promoção e o
envelope de instrumentação como fonte.

## Sugestões de melhoria

1. Em `12-Exemplos.md`, trocar "três casos de ouro" por "quatro casos de ouro" no
   parágrafo de abertura (ou "uma bateria que cresce de três para quatro casos", se a
   intenção era contar a narrativa do incidente). É a única correção pendente do volume.
2. Opcional, sem custo de nota: `13-Testes.md` afirma que "o lado do documento continua
   sendo responsabilidade da auditoria" quanto à sincronia do `stateDiagram-v2` com
   `TRANSICOES`. Um teste que parseasse as arestas do bloco Mermaid de `05-Diagramas.md`
   e as comparasse com o dicionário fecharia esse elo por máquina, no espírito de
   `test_convencoes_nao_derivou`.

## Veredicto

Aprovado

Média 8,9, nenhuma seção abaixo de 6. As duas condições do selo estão satisfeitas. A
subida em relação aos 8,5 da primeira auditoria não é cortesia: cada um dos cinco
achados foi verificado como corrigido por execução ou leitura direta do trecho, e as
seções que subiram (05, 07, 08, 13, 14, 17) subiram exatamente onde os problemas
moravam. O único achado novo (problema 1) é um deslize de uma palavra numa seção que,
executada, reproduz integralmente o que afirma — mantém o volume `PRONTO`.
