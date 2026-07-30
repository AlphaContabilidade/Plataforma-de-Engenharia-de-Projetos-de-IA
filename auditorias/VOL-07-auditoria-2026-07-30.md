# Auditoria — Volume 07 PROMPT-ENGINE

**Data:** 2026-07-30
**Revisao:** 1
**Auditor:** auditor-fable (Fable 5)
**Motivo desta auditoria:** o texto mudou depois do selo de 2026-07-29 — o exemplo canônico foi reescrito de `classificar-lancamento(historico:str, valor:float)` para `classificar-solicitacao(descricao:str, horas:float)`, com casos de ouro de triagem de solicitações e códigos de catálogo neutros (`INF-104`, `SUP-210`, `DAD-330`, `REVISAR`), para remover vocabulário de outros projetos do autor.
**Gates na entrada:**

```
$ python -m ferramentas.validar 07
ok: volume 07 sem violacoes
(exit 0)

$ python -m ferramentas.validar --cross-refs
ok: referencias cruzadas sem violacoes
(exit 0)

$ python -m pytest exemplos/07-prompt-engine -q
.......................................                                  [100%]
39 passed in 0.21s
(exit 0)
```

## Método

Julgamento formado antes de abrir os relatórios de 2026-07-29, com execução e não só
leitura. Além dos gates acima: reprodução literal dos cinco blocos `python` de
`12-Exemplos.md` em um único script contra `exemplos/07-prompt-engine/` — todos os
`assert` passaram (`total == 4`, `acertos == 3`, `taxa_acerto == 0.75`, falha única no
caso `ambiguo`, `taxa_b == 1.0`, `deriva == 0.25`, `vencedor == "b"`, trilha final
`v1 <hash> DEPRECIADO / v2 <hash> PROMOVIDO`), incluindo as afirmações de prosa: a
lição de tipo confirmada (`render(descricao="X", horas="6")` com `"6"` texto levanta
`ContratoViolado: variavel horas esperava float, recebeu str`) e o atalho
`VERSIONADO → PROMOVIDO` levantando `TransicaoInvalida` com a lista de destinos.
Máquina de estados conferida transição a transição contra `TRANSICOES`
(1+2+3+1+0 = 7, cinco estados). Assinaturas de `08-Modelos.md` conferidas linha a
linha contra os três `.py`. Contagem 13+13+11 = 37 funções `def test_` conferida por
grep, e a parametrização em três do teste de fronteira localizada
(`test_taxa_acerto_em_valores_de_fronteira`). Os cinco testes nomeados em
`13-Testes.md` localizados por nome. Grep de domínio neutro rodado sobre
`07-PROMPT-ENGINE/`, `exemplos/07-prompt-engine/` e os arquivos ligados em
`18-Referencias-Cruzadas.md`. Coerência da narrativa do exemplo conferida: sobre os
três primeiros casos a v1 acerta 3/3 (o `executor_fake` devolve o código certo para os
três), o que torna consistente a história de que ela foi promovida quando a bateria
tinha três casos e hoje, com o quarto caso vindo de incidente, mede 0,75.

## Notas por seção

| Seção | Nota | Justificativa |
|---|---|---|
| 01-Introducao | 9 | Problema, entrega e anti-público declarados; nenhuma afirmação desmentida pelo código; intocada pelo rewrite e continua consistente com o exemplo novo (não cita domínio algum). |
| 02-Objetivos | 9 | Sete objetivos com critério verificável e local de conferência; todos reconferidos contra os testes reais e contra `TRANSICOES` (ausência da aresta `VERSIONADO → PROMOVIDO` confirmada no código e em execução). |
| 03-Escopo | 9 | Fronteira em tabela com volume responsável e razão de cada corte; fronteira interna (registro não importa avaliador e vice-versa) bate com os imports reais. |
| 04-Arquitetura | 9 | `C4Context` e `C4Container` corretos e explicados; decisões com custo declarado; nada citando o exemplo antigo. |
| 05-Diagramas | 9 | Os quatro diagramas batem com o código: sequência confere com `avaliar`/`transicionar`; máquina de estados com as sete transições de `TRANSICOES` e a contagem do parágrafo exata; ER com `CONTRATO \|\|--o{ VARIAVEL` (o achado da primeira auditoria não voltou); mindmap coerente. |
| 06-Fluxogramas | 9 | Quatro pontos de decisão ancorados em mecanismo (construtor, hash, R8, `comparar`); o nó `O` segue gramatical; fluxograma de incidente termina em regra operacional concreta. |
| 07-Regras | 9 | As dez regras reconferidas uma a uma contra o código — todas verdadeiras; R2 declara o alcance completo (nome, tipo, obrigatoriedade dentro; `descricao` fora, com razão) e o limite é coberto por `test_hash_ignora_descricao`. |
| 08-Modelos | 9 | Assinaturas idênticas às dos três `.py`, incluindo `nome(v1:int, v2?:str)`; o limite do hash registrado com os testes que o fixam. |
| 09-Boas-Praticas | 9 | Pareamento P1–P8 com A1–A8 mantido; P3 e P4 aplicadas de fato no exemplo novo (padrões ancorados nos códigos de catálogo; promoção por deriva com a ressalva de granularidade). |
| 10-Anti-Patterns | 8 | Consequência observável em todos e o parágrafo do escape do `marcador-proibido` continua sendo autocrítica correta; perde ponto por imprecisão na abertura: "cada anti-padrão corresponde, pelo identificador, a uma prática de 09" é falso para A9 e A10, que não têm P9/P10 (problema 3). |
| 11-Implementacao | 9 | Descreve o código que existe, decisão por decisão (regex vs `str.format`, contador próprio vs tamanho, `re.search` vs `re.fullmatch`); as três citações verificadas pelo gate 1. |
| 12-Exemplos | 9 | Reescrita executada ponta a ponta por script: todos os `assert` e as afirmações de prosa confirmados por máquina, incluindo a lição de tipo (`"6"` texto reprovado) e o limite do rebaixamento automático. O "três casos" da r2 foi corrigido ("quatro casos de ouro"). A narrativa da incumbente a 0,75 é internamente coerente (v1 = 3/3 sobre os três primeiros casos). Deslize de palavra: "os dois hexdígitos" onde se quer dizer "os dois hashes" (problema 2). |
| 13-Testes | 6.5 | A distribuição 13+13+11 = 37 funções / 39 casos está certa e os cinco testes nomeados existem; mas a âncora da seção — "Trinta e nove é o número que `python -m pytest exemplos -q` imprime, e é ele que vale" — é falsa hoje: o comando imprime **89**, porque `exemplos/12-memory/` passou a existir (problema 1). A seção afirma exatamente o que ela mesma adverte que destrói a confiança do leitor que roda o comando. |
| 14-Metricas | 9 | Unidade e origem em todas; "falhas por classe de origem" com definição operacional exata (prefixos conferidos contra os dois pontos de saída de `avaliar`); granularidade e as duas métricas não calculadas continuam o ponto alto do volume. |
| 15-Checklist | 9 | Dezesseis itens acionáveis em quatro grupos cobrindo contrato, registro, evidência e promoção; os dois itens de evidência externa declaram a fonte (script de promoção; envelope de instrumentação); completo para a pergunta que se propõe a responder. |
| 16-Roadmap | 9 | Cada evolução com "por que não entrou agora" concreta; a regra de revisar a fronteira aqui antes de contorná-la lá é governança, não desejo. |
| 17-Conclusao | 7 | O fechamento continua forte (lição da obrigatoriedade no hash, limite honesto estado ≠ resultado bom) e o exemplo novo está corretamente citado (`classificar-solicitacao`); mas repete a atribuição falsa "o número que `python -m pytest exemplos -q` imprime" para 39 (problema 1). |
| 18-Referencias-Cruzadas | 9 | Separação pré-requisito vs vizinhança correta; `depende_de` vazio justificado; os sete links resolvem no disco (gate 1 verde) e nenhum arquivo ligado carrega vocabulário do domínio antigo. |

media: 8.7

## Problemas encontrados

1. **A contagem de testes está certa, mas o comando a que ela é atribuída imprime outro
   número** — `07-PROMPT-ENGINE/13-Testes.md` (abertura) e `17-Conclusao.md` (primeiro
   parágrafo). Ambos afirmam que 39 "é o número que `python -m pytest exemplos -q`
   imprime". Verificado executando: esse comando imprime **`89 passed`**, porque
   `exemplos/12-memory/` foi criado depois do selo e a suíte de `exemplos/` deixou de
   ser só a deste volume. O número 39 continua exato para a suíte do volume — mas para
   o comando com escopo: `python -m pytest exemplos/07-prompt-engine -q` (39 passed,
   conferido). O defeito não veio do rename do exemplo: veio do crescimento da
   plataforma, e é precisamente a classe de defeito que `13-Testes.md` adverte
   ("citar a primeira como se fosse a segunda faz o leitor que roda o comando duvidar
   do resto da seção"). Correção de uma linha em cada arquivo: citar o comando com o
   caminho do volume, que é aliás a forma do gate 2 em `Convencoes.md` e no
   `CLAUDE.md` da pasta (`python -m pytest exemplos/<vol>`).

2. **Deslize de palavra na seção "A trilha que sobra"** —
   `07-PROMPT-ENGINE/12-Exemplos.md`, último parágrafo: "Os dois **hexdígitos** ficam
   escritos como marcador de forma" — o que fica como marcador são os dois **hashes**
   (cada um de 12 hexdígitos). O sentido se recupera pelo contexto, mas a frase, lida
   literalmente, não descreve o que o bloco mostra. Correção de uma palavra.

3. **A abertura de `10-Anti-Patterns.md` promete correspondência que A9 e A10 não têm** —
   "Cada anti-padrão abaixo corresponde, pelo identificador, a uma prática de
   09-Boas-Praticas". Vale para A1–A8; A9 (marcador de trabalho inacabado) e A10
   (bateria vazia como aprovação) não têm P9/P10. O conteúdo dos dois é bom e A10
   remete corretamente a R8 — o defeito é só a promessa da abertura, que deveria
   dizer que os oito primeiros pareiam e os dois últimos são adicionais. Este problema
   é anterior ao rewrite e não foi apontado pelas auditorias de 2026-07-29.

Fora isso, não encontrei problema real nos seis eixos, e digo explicitamente em vez de
inventar crítica: as assinaturas, nomes de estado, transições e limiares batem com os
`.py` (eixo 1 — e nenhum lugar do volume cita hash literal: o grep por 12 hexdígitos
em prosa devolve vazio, então o rename não invalidou número algum além do problema 1,
que tem outra causa); o exemplo novo fecha entre si (eixo 2 — casos, códigos de
catálogo, executor substituto e as taxas 0,75 / 1,0 / deriva 0,25 confirmados por
execução, e a história da v1 incumbente é aritmética consistente: 3/3 na bateria de
três, 3/4 na de quatro); nenhuma seção cumpre palavra sem responder à pergunta (eixo
3); as 16 seções não tocadas continuam consistentes com `12-Exemplos` e `17-Conclusao`
reescritas — nenhuma cita as variáveis, os casos ou o domínio antigos (eixo 4); os
exemplos executam exatamente como o texto afirma, incluindo a lição de tipo (eixo 5);
os seis diagramas Mermaid estão sintaticamente corretos, com parágrafo descritivo, e o
`15-Checklist` é completo e acionável (eixo 6).

## Verificacao do dominio neutro

Comando e saída literais:

```
$ grep -rin "extrato\|lancamento\|lançamento\|contabil\|contábil\|plano de contas\|bancári\|omie\|sicoob\|reforma tribut" 07-PROMPT-ENGINE/
(saida vazia, exit 1)
```

**Saída vazia — nenhuma ocorrência.** O mesmo grep sobre `exemplos/07-prompt-engine/`
e sobre os arquivos ligados em `18-Referencias-Cruzadas.md`
(`prompts/prompt-engineering/`, `frameworks/_catalogo.md`,
`frameworks/conhecidos/RTF.md`) também devolve vazio. Os códigos de catálogo do
exemplo novo (`INF-104`, `SUP-210`, `DAD-330`, `REVISAR`) e as variáveis
(`descricao`, `horas`) são neutros. O rewrite cumpriu o objetivo: o volume não carrega
vocabulário dos outros projetos do autor.

Sobre a seção "A trilha que sobra": os hashes aparecem como marcador de forma
(`<12 hexdigitos>`), não como valor literal, e a escolha está **bem justificada no
próprio texto** — o hash deriva do corpo e da assinatura, e fixá-lo na prosa criaria
um número que envelhece na primeira edição do corpo sem que nenhum gate perceba. Não é
omissão: é a mesma disciplina da regra de volume perecível, aplicada a um número que o
leitor reproduz rodando o bloco. A execução desta auditoria confirmou a forma
(`v1 ff834d82024f DEPRECIADO / v2 c802144c34e8 PROMOVIDO` — valores citados aqui, no
relatório datado, onde envelhecer é esperado; não no volume).

## Comparacao com a auditoria anterior

- **O único problema da r2 foi resolvido pelo rewrite.** A abertura de `12-Exemplos.md`
  agora diz "quatro casos de ouro", em acordo com `resultado.total == 4` e com a nota
  de granularidade 0,25.
- **Nenhum dos cinco problemas da primeira auditoria voltou.** Reconferido:
  ER com `\|\|--o{` (1); obrigatoriedade dentro da assinatura e do hash, com os três
  testes de limite passando (2); contagem 37 funções / 39 casos correta para a suíte
  do volume (3); nó `O` do fluxograma gramatical (4); métrica de falhas com definição
  operacional por prefixo (5).
- **O rewrite não degradou as 16 seções não tocadas** — elas nunca citaram o domínio do
  exemplo, então trocá-lo não abriu contradição. `17-Conclusao.md` cita corretamente
  `classificar-solicitacao`.
- **A média cai de 8,9 para 8,7 por um defeito novo, externo ao rewrite:** a atribuição
  do número 39 ao comando `python -m pytest exemplos -q` (problema 1), que era
  verdadeira em 2026-07-29 (a r2 registrou `39 passed` para esse exato comando) e
  deixou de ser quando `exemplos/12-memory/` entrou na plataforma. Não é cortesia nem
  rigor teatral: é um número que o selo anterior validou e que hoje está errado, em
  duas seções. Somam-se dois achados menores (problemas 2 e 3), um deles pré-existente
  e não apontado antes.
- A sugestão opcional da r2 (teste que compara as arestas do `stateDiagram-v2` com
  `TRANSICOES`) segue não implementada; continua opcional e sem custo de nota.

## Sugestões de melhoria

1. Em `13-Testes.md` e `17-Conclusao.md`, trocar `python -m pytest exemplos -q` por
   `python -m pytest exemplos/07-prompt-engine -q` nas duas frases que atribuem o 39 ao
   comando — o escopo por volume é a forma do gate 2 e blinda o número contra o
   crescimento do resto da plataforma. Uma linha em cada arquivo.
2. Em `12-Exemplos.md`, trocar "Os dois hexdígitos ficam escritos como marcador de
   forma" por "Os dois hashes ficam escritos como marcador de forma". Uma palavra.
3. Em `10-Anti-Patterns.md`, ajustar a abertura para "Os oito primeiros anti-padrões
   correspondem, pelo identificador, às práticas de 09-Boas-Praticas; A9 e A10 são
   adicionais" — ou criar P9/P10, o que custa mais e não é necessário.

## Veredicto

Aprovado

Média 8,7, nenhuma seção abaixo de 6 — as duas condições do selo estão satisfeitas. A
queda em relação aos 8,9 de 2026-07-29 reflete um defeito real e novo (o comando de
teste citado imprime 89, não 39), não o rewrite: o exemplo novo, executado bloco a
bloco, reproduz integralmente o que afirma, e o grep de domínio neutro devolve vazio.
As três correções sugeridas somam quatro linhas de edição.
