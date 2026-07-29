# Auditoria — Volume 07 PROMPT-ENGINE

**Data:** 2026-07-29
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
....................................                                     [100%]
36 passed in 0.17s
(exit 0)
```

## Método

Os seis eixos foram auditados com execução, não só leitura. Além dos três gates acima:
o passo a passo completo de `12-Exemplos.md` foi reproduzido literalmente em script
contra `exemplos/07-prompt-engine/` (todos os `assert` dos cinco blocos passaram,
incluindo as afirmações de prosa — `render` reprovando `"1200"` como texto, `obter`
sem promovida devolvendo a última, atalho `VERSIONADO → PROMOVIDO` levantando
`TransicaoInvalida`, e a trilha final `v1 DEPRECIADO / v2 PROMOVIDO`); a contagem do
`stateDiagram-v2` foi conferida transição a transição contra `TRANSICOES`; os três
testes nomeados em `13-Testes.md` foram localizados por nome; e dois experimentos
ad-hoc verificaram cardinalidade do ER e cobertura do hash (problemas 1 e 2 abaixo).

## Notas por seção

| Seção | Nota | Justificativa |
|---|---|---|
| 01-Introducao | 9 | Problema, entrega e — raro — o anti-público ("experimento descartável não tem o problema que este volume resolve"). Nenhuma afirmação desmentida pelo código. |
| 02-Objetivos | 9 | Tabela de critérios verificáveis; todos os sete conferidos contra os testes reais (`test_promover_uma_segunda_versao_deprecia_a_anterior`, `test_hash_muda_quando_o_tipo_de_uma_variavel_muda`, `len(hash)==12` em `test_hash_estavel_entre_instancias_iguais`, ausência da aresta em `TRANSICOES`). |
| 03-Escopo | 9 | Fronteira em tabela com volume responsável e razão; a fronteira interna (registro não conhece avaliador) bate com os imports reais dos módulos. |
| 04-Arquitetura | 9 | `C4Context` e `C4Container` corretos; os parágrafos pós-diagrama explicam (interlocutores, forma de árvore do grafo) em vez de repetir o título; decisões vêm com custo declarado. |
| 05-Diagramas | 7 | Sequência e máquina de estados exatas (7 transições conferidas contra `TRANSICOES`), mas o ER contradiz o código: `CONTRATO \|\|--\|{ VARIAVEL` declara "uma ou muitas" e o código aceita contrato com zero variáveis (problema 1). |
| 06-Fluxogramas | 8 | Quatro pontos de decisão reais e o segundo fluxograma (incidente) é operacionalmente útil; um rótulo de nó agramatical compromete a legibilidade (problema 4). |
| 07-Regras | 8 | As dez regras conferidas uma a uma contra o código — todas verdadeiras; mas a defesa de R2 sugere cobertura total do contrato pelo hash, e `obrigatoria` fica fora (problema 2). |
| 08-Modelos | 8 | Assinaturas conferidas linha a linha contra os três `.py` — batem literalmente; perde ponto por não registrar o limite do hash sobre `obrigatoria`/`descricao` (problema 2), num volume que se orgulha de registrar limites honestos. |
| 09-Boas-Praticas | 9 | Pareamento P1–P8 com A1–A8 mantido na ordem; toda prática traz a razão; P3 e P4 são aplicadas de fato em `12-Exemplos.md`. |
| 10-Anti-Patterns | 9 | Consequência observável em todos; o parágrafo sobre o escape do `marcador-proibido` em A9 documenta inclusive o abuso possível do escape — autocrítica correta. |
| 11-Implementacao | 9 | Descreve o código que existe, decisão por decisão (regex vs `str.format`, contador próprio vs `len`, `re.search` vs `re.fullmatch`); citações verificadas pelo gate 1. |
| 12-Exemplos | 10 | Executado ponta a ponta contra o código real: os cinco blocos e todas as afirmações de prosa confirmadas por máquina, incluindo as duas notas de limite (granularidade 0,25; rebaixamento automático só alcança a promovida). Nada a corrigir. |
| 13-Testes | 7 | Os três testes nomeados existem e a estratégia é bem defendida, mas a contagem "trinta e quatro testes... onze para o avaliador" diverge da saída do próprio comando que a seção manda rodar: `36 passed` (problema 3). |
| 14-Metricas | 8 | Unidade e origem em todas; a discussão de granularidade é o melhor parágrafo do volume; "Falhas por categoria de motivo" tem definição operacional frágil (problema 5). |
| 15-Checklist | 8 | Acionável e amarrado às chamadas reais (`registrar` duas vezes, `historico`, `promovida`); dois itens não são verificáveis "em segundos" como a abertura promete (ver sugestão 4). |
| 16-Roadmap | 9 | Cada item com "por que não entrou agora"; a regra de revisão de fronteira ("revisar aqui antes de contornar lá") é governança concreta, não desejo. |
| 17-Conclusao | 8 | Fecha com o limite honesto certo (estado ≠ resultado bom), mas repete o número "trinta e quatro testes" (problema 3). |
| 18-Referencias-Cruzadas | 9 | A separação pré-requisito vs vizinhança está correta e o `depende_de` vazio é justificado; os sete links listados resolvem (gate 1 verde). |

media: 8.5

## Problemas encontrados

1. **Cardinalidade do ER contradiz o código** — `07-PROMPT-ENGINE/05-Diagramas.md`
   (seção "Modelo de dados do registro"). `CONTRATO ||--|{ VARIAVEL` declara "uma ou
   muitas variáveis por contrato". Verificado executando:
   `PromptTemplate('estatico', 'corpo sem placeholder algum', ())` constrói sem erro —
   contrato com **zero** variáveis é válido em `prompt_template.py`. A cardinalidade
   correta é `||--o{`. Agrava que o parágrafo seguinte justifica a cardinalidade com
   uma restrição diferente ("corpo sem placeholder e **com** variáveis declaradas é
   reprovado"), que é verdadeira mas não implica mínimo de uma variável.

2. **O hash não cobre `obrigatoria`, e nenhuma seção registra esse limite** —
   `07-PROMPT-ENGINE/07-Regras.md` (R2) e `08-Modelos.md`; código em
   `exemplos/07-prompt-engine/prompt_template.py` (propriedades `assinatura`/`hash`) e
   `prompt_registry.py:71-84`. Verificado executando: dois templates idênticos exceto
   por `obrigatoria=True` vs `obrigatoria=False` têm o **mesmo hash**, e
   `registrar` do segundo devolve `v1` — mudança de obrigatoriedade, que altera o
   comportamento de `render` (ausência vira `""` em vez de levantar), não gera versão.
   A afirmação do volume "o hash cobre o corpo **e** a assinatura" é exata, mas o
   docstring de `registrar` diz "o hash cobre o contrato inteiro", o que é falso, e a
   prosa de R2/08-Modelos nunca registra a exceção. Num volume que registra limites
   honestos em três outras seções, este ficou de fora.

3. **Contagem de testes diverge da saída do comando citado** —
   `07-PROMPT-ENGINE/13-Testes.md` (abertura) e `17-Conclusao.md` (primeiro parágrafo)
   afirmam "trinta e quatro testes: onze para o contrato, doze para o registro e onze
   para o avaliador". A contagem por função está certa (11+12+11 `def test_`,
   verificado por grep), mas `python -m pytest exemplos -q` — o comando que a própria
   seção manda rodar — reporta **36 passed**, porque
   `test_taxa_acerto_em_valores_de_fronteira` é parametrizado em 3 casos (avaliador
   coleta 13 itens). O leitor que rodar o comando verá um número diferente do texto.

4. **Rótulo de nó agramatical no fluxograma principal** —
   `07-PROMPT-ENGINE/06-Fluxogramas.md`, nó `O`:
   `{comparar contra a versao promovida da deriva positiva?}`. Sem acento (convenção
   dos diagramas), "da" lê como preposição e a pergunta fica sem verbo inteligível.
   Deveria ser algo como `{a comparacao contra a versao promovida mostra deriva
   positiva?}`.

5. **Métrica "Falhas por categoria de motivo" não agrupa como promete** —
   `07-PROMPT-ENGINE/14-Metricas.md` (tabela). O campo `motivo` de `Falha` é texto
   livre com conteúdo específico do caso (`"saida nao casa com o padrao '\\b2\\.04\\.07\\b'"` —
   ver `prompt_evaluator.py:109,114`), então agrupar pelo campo produz um grupo por
   padrão distinto, não por categoria. A métrica só funciona agrupando por prefixo
   ("render falhou" vs "saida nao casa"), e isso não está dito.

Nos eixos "contradições internas" e "funcionalidade dos exemplos" **não encontrei
problema real**: as seções são mutuamente consistentes (regras, diagramas, exemplos e
código contam a mesma história, conferida contra os `.py`), e o passo a passo de
`12-Exemplos.md` reproduz exatamente o que afirma, assert por assert.

## Sugestões de melhoria

1. Trocar `||--|{` por `||--o{` na relação CONTRATO–VARIAVEL do ER em
   `05-Diagramas.md` e ajustar o parágrafo seguinte para citar a restrição que o
   código de fato impõe (divergência bidirecional corpo × declaração), não um mínimo
   de variáveis que não existe.
2. Para o problema 2, escolher um dos dois caminhos e registrá-lo: (a) incluir a
   obrigatoriedade na `assinatura` (ex.: `tom?:str` para opcional), o que muda o hash
   e vira versão nova — exigiria nota de migração; ou (b) manter o comportamento e
   acrescentar o limite honesto em R2 e em `08-Modelos.md` ("mudança só de
   `obrigatoria` ou `descricao` não gera versão; trate como edição de contrato e mude
   o corpo ou o tipo junto"). Corrigir também o docstring "o hash cobre o contrato
   inteiro" em `prompt_registry.registrar`.
3. Em `13-Testes.md` e `17-Conclusao.md`, ou citar "34 funções de teste (36 casos
   coletados, um deles parametrizado em três valores de fronteira)", ou simplesmente
   dizer 36 e alinhar a distribuição (11/12/13). O número do texto tem de ser o número
   que o comando imprime.
4. Em `15-Checklist.md`, reformular os dois itens não verificáveis em segundos:
   "nenhuma tentativa de atalho foi feita" não deixa rastro (o registro não grava
   tentativas rejeitadas) — trocar por "o `estado` atual é `PROMOVIDO` e o
   `historico` mostra a passagem por `EM_AVALIACAO`" exigiria histórico de estados,
   que não existe; a alternativa verificável é "a sequência de `transicionar` do
   script de promoção passa por `EM_AVALIACAO`". E o item de custo por execução
   depende do envelope de instrumentação que o próprio `16-Roadmap.md` diz não
   existir ainda — o item deveria apontar isso ("com o envelope descrito em
   14-Metricas") para não pedir evidência que o motor não produz.
5. Em `14-Metricas.md`, definir "categoria de motivo" operacionalmente: prefixo do
   campo `motivo` antes do primeiro `:` ("render falhou" vs "saida nao casa"), ou
   acrescentar um campo enumerado `tipo` a `Falha` no roadmap.

## Veredicto

Aprovado

Média 8,5, nenhuma seção abaixo de 6. Os cinco problemas são reais e devem entrar na
incorporação — os problemas 1 e 2 são os únicos com potencial de enganar um leitor que
confie no volume — mas nenhum deles derruba seção alguma abaixo do corte, e os seis
eixos pedidos foram cobertos com evidência executada.
