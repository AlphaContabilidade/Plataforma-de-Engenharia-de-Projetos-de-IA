# Auditoria — Volume 12 MEMORY

**Data:** 2026-07-30
**Revisao:** 1
**Auditor:** auditor-fable (Fable 5)
**Gates na entrada:**

```
$ python -m ferramentas.validar 12
ok: volume 12 sem violacoes

$ python -m pytest exemplos/12-memory -q
...............................................                          [100%]
47 passed in 0.11s

$ python -m ferramentas.validar --cross-refs
ok: referencias cruzadas sem violacoes
```

## Método

Além dos três gates, esta auditoria **reproduziu por execução** os sete passos de
`12-Exemplos.md` em script independente contra os módulos reais, com asserções em cada
passo, e varreu prosa, código e testes por dado do domínio de origem (nomes de sistemas,
identificadores fiscais, valores monetários, códigos de categoria contábil). Assinaturas,
enums, `PRECEDENCIA` e parâmetros de `resolver` foram conferidos item a item contra
`exemplos/12-memory/{memoria_observada,contaminacao,precedencia}.py`.

**Resultado da checagem de dado de cliente: limpo.** Nenhuma menção a sistema bancário ou
contábil nomeado, CNPJ, boleto, conta bancária, valor monetário real ou código de categoria
contábil nas 18 seções, nos 3 módulos ou nos 3 arquivos de teste. O único match do padrão
foi "banco de dados" (genérico, em 16-Roadmap). A proveniência ("rotina de conciliação
financeira em produção") é citada em termos genéricos, sem identificar cliente, sistema ou
número — a generalização afirmada em 01-Introducao se sustenta.

## Notas por seção

| Seção | Nota | Justificativa |
|---|---|---|
| 01-Introducao | 9 | Os três defeitos motivadores são concretos, distintos e reaparecem consistentemente no resto do volume. Responde "para quem é" com um critério de exclusão real ("agente que responde e esquece não tem este problema"). Sem dado do domínio de origem. |
| 02-Objetivos | 9 | Tabela de dez objetivos com critério verificável e local de conferência; todos os seis nomes de teste citados existem na suíte e testam o que a tabela afirma. "O que não é objetivo" delimita em vez de encher. |
| 03-Escopo | 9 | Fronteira em tabela com volume responsável e razão por linha; nomes e números dos vizinhos (11 KNOWLEDGE, 13 RAG, 14 VECTOR, 15 CONTEXT, 08 AGENT-ENGINE, 07 PROMPT-ENGINE) conferem com `contrato.json`. A "fronteira interna" declara o custo aceito (dominância crua) em vez de escondê-lo. |
| 04-Arquitetura | 9 | C4Context e C4Container corretos e correspondentes ao grafo real de imports (guarda→armazém, regra→ambos). Os parágrafos explicam a seta de risco e o preço da cadeia, não repetem o título. As três decisões vêm com ganho E custo. |
| 05-Diagramas | 7 | O stateDiagram-v2 corresponde ao código: `descartada_por_contaminacao` terminal confere com a ausência de parâmetro em `filtrar_contaminacao`, e a seta de volta de `expirada` confere com expiração calculada por consulta. **Mas a prosa do ER está errada**: diz "zero ou uma contradição" quando o diagrama declara `\|\|--o{` (zero ou muitas) e o código produz múltiplas `Contradicao` por chave (`test_duas_bases_congeladas_discordantes_geram_duas_contradicoes`). "Cinco transições" só fecha excluindo as duas setas de término (o diagrama tem sete). |
| 06-Fluxogramas | 8.5 | Os dois fluxogramas percorrem o código real; o segundo (triagem de contradição) é o mais operacional do volume e não existe em lugar nenhum do código — é conteúdo, não paráfrase. Imprecisão menor: a checagem "chave em branco?" aparece depois do nó "entradas da chave", quando no código ela ocorre dentro da própria chamada `entradas`. |
| 07-Regras | 8 | Nove das dez regras conferem com código e teste, inclusive R5 (forma do laço), R6 (empate explícito) e R9 (janela antes de `contradicoes` — conferido na linha). **R8 erra a contagem: "os quatro retornos indecisos" — o código tem três** (empate, dominância abaixo do mínimo, nenhuma evidência vigente). O "limite honesto de R1" (eco mal marcado passa) é o parágrafo mais valioso da seção. |
| 08-Modelos | 10 | Conferido item a item: `Origem` (4 valores, mesma ordem), `Entrada` (5 campos, default só em `evidencia`), `Contradicao` (5 campos), `Confianca` (3 valores), `PRECEDENCIA` (3 valores, ordem exata), `resolver` (keyword-only, `hoje` sem default, `janela_dias=365`, `dominancia_minima=0.7`), `ChaveInvalida(ValueError)`. Zero divergência com o código. A prosa explica o porquê de cada forma. |
| 09-Boas-Praticas | 9 | Oito práticas pareadas 1:1 com os anti-padrões, cada uma com o comportamento concreto trocado. P2 (marcar na escrita, não na leitura) e P7 (registrar decisão humana na memória) são as duas que o código sozinho não garante — a seção cobre exatamente o buraco certo. |
| 10-Anti-Patterns | 9 | Cada anti-padrão com consequência observável; A2 ("melhora os números enquanto piora o resultado") e A6 ("reproduzível, defensável e mede a preferência de quem ampliou") são formulações precisas de defeitos difíceis de nomear. A9 explica o próprio escape da regra `marcador-proibido` com honestidade. |
| 11-Implementacao | 8 | Descreve decisões de implementação reais e verificáveis (`_chave_valida` nos dois lados, `_mais_recente` com índice, laço que retorna quando há candidatas). **Inconsistência numérica: "no defeito real, dez escritas do próprio agente" — o docstring de `contaminacao.py`, o teste do defeito e 13-Testes dizem cinco.** O "dez" parece contaminação do exemplo do passo 2 de 12-Exemplos. |
| 12-Exemplos | 7.5 | Os sete passos foram reproduzidos por execução independente: todas as asserções passam e as cinco justificativas citadas em comentário são idênticas byte a byte à saída real. **Mas o parágrafo de correção contém um número falso: afirma que dez "é o menor valor que de fato inverte a liderança nesta amostra" — medido, nove já inverte** (fila-suporte 10×9, fração 0,5263). O parágrafo que existe para demonstrar correção por medição afirma um mínimo que não foi medido. "Últimos oitenta dias" também é impreciso: a observação mais antiga tem 81 dias. |
| 13-Testes | 9.5 | As contagens conferem exatamente: 15+13+19=47 funções, nenhuma parametrizada, e o próprio texto explica por que essa distinção importa. Os "quatro testes que carregam o volume" existem e afirmam o que a seção diz. "O que a estratégia deliberadamente não faz" é fronteira honesta, não lacuna. |
| 14-Metricas | 9 | Seis métricas com definição operacional, unidade e origem; as três instrumentadas estão marcadas como tal. Números citados conferem com a execução (10/20, 0,55, 11×9, n_observacoes=9, uma contradição aberta ao final). "Fração de eco zero é motivo de suspeita" é a leitura não óbvia que salva a métrica de virar teatro. |
| 15-Checklist | 9 | Acionável: cada item se marca com evidência nomeada (uma chamada, um número, uma linha), e os dois itens que dependem de instrumentação externa dizem de onde vem a evidência. Nenhum item é "verifique que está bom". Responde à pergunta única declarada no topo. |
| 16-Roadmap | 8.5 | Seis evoluções, cada uma com o que acrescenta e por que não entrou — e as razões são de fronteira, não de preguiça. A justificativa da "rejeição de decisão em branco" é a mais fraca das seis (ver julgamento 3 abaixo). A seção de ligação com 11/13/15 declara os três pontos de extensão sem exigir mudança de interface. |
| 17-Conclusao | 8.5 | Fecha com as três decisões e com o limite honesto (eco mal marcado) em vez de autocongratulação. Herda dois números imprecisos do exemplo: "oitenta dias" (são 81) — os demais ("dez descartados", "base de janeiro", "nove de dez") conferem com a execução. |
| 18-Referencias-Cruzadas | 9 | Distingue pré-requisito de leitura (grafo, vazio com razão documentada) de vizinhança (prosa) — a razão para `depende_de: []` é sólida e está também no `_VOLUME.yml`. Todos os links resolvem (gate 1 verde) e os nomes dos vizinhos conferem com o contrato. |

media: 8.7

## Problemas encontrados

1. **[Média] 12-Exemplos.md, passo 2 — afirmação de mínimo falsa.** "O número foi
   corrigido para dez, que é o menor valor que de fato inverte a liderança nesta amostra."
   Medido por execução: com **nove** escritas do agente a liderança já inverte
   (fila-suporte 10 × fila-financeiro 9, fração 0,5263). Dez inverte, mas não é o menor.
   O defeito é agravado pelo contexto: o parágrafo existe justamente para exemplificar que
   número não medido não entra — e contém um número não medido. Nenhum gate pega, porque
   não há asserção sobre "menor".
2. **[Média] 07-Regras.md, R8 — contagem errada de retornos.** "Os quatro retornos
   indecisos" — `resolver` tem **três** retornos com `decisao=None` (empate, dominância
   abaixo do mínimo, nenhuma evidência vigente). Num volume cujo eixo dominante é coerência
   texto×código, contagem de caminhos de retorno errada na tabela de regras invioláveis pesa.
3. **[Média] 05-Diagramas.md — prosa do ER contradiz o diagrama e o código.** A prosa diz
   "a chave agrupa [...] zero ou uma contradição", mas o diagrama declara `CHAVE ||--o{
   CONTRADICAO` (zero ou muitas) e o código emite uma `Contradicao` por base congelada
   discordante — duas bases discordantes geram duas, com teste provando. O diagrama está
   certo; a prosa está errada.
4. **[Baixa] 11-Implementacao.md — "dez escritas" no defeito real.** O docstring de
   `contaminacao.py`, `test_eco_nao_silencia_a_contradicao` e 13-Testes descrevem o defeito
   real com **cinco** escritas do agente. O "dez" de 11-Implementacao parece vazamento do
   número do exemplo sintético do passo 2.
5. **[Baixa] "Últimos oitenta dias" (12-Exemplos passo 1 e 17-Conclusao).** A observação
   mais antiga é de 2026-05-10; com HOJE=2026-07-30 são 81 dias. Num volume que se declara
   medido, aproximação não anunciada é dissonante.
6. **[Nit] 05-Diagramas: "cinco transições"** só fecha excluindo as duas setas de término
   (o stateDiagram tem sete setas). **06-Fluxogramas:** a checagem de chave em branco
   aparece como nó posterior a "entradas da chave", quando no código ela ocorre dentro da
   própria chamada.

**Onde procurei e não encontrei problema:** contradição entre 07-Regras e
14-Metricas/16-Roadmap — não existe; o roadmap adia "fechamento de contradição por revisão"
citando explicitamente R3, e as métricas reforçam A4/R7 em vez de contradizê-los. Assinaturas
de 08-Modelos: zero divergência. Passos 1–7 do exemplo: todas as asserções e todas as
justificativas citadas conferem com a execução. Dado de cliente: nenhum.

## Julgamento das tres decisoes discutiveis

1. **Contradição rebaixa para `MEDIA` mesmo com decisão humana — correta.** `Confianca` não
   mede a autoridade de quem decidiu (isso a precedência já garante: a decisão humana vence);
   mede o estado epistêmico da chave. Uma chave com base congelada e observação em desacordo
   é conhecidamente inconsistente, e emitir `ALTA` sobre ela apagaria do painel de
   distribuição de confiança exatamente o sinal que mantém a contradição viva — o caminho de
   A10 por via estatística. A leitura oposta (a contradição não envolve o julgamento humano)
   é defensável, mas otimiza a percepção de quem lê um veredicto isolado ao custo de quem
   opera o agregado. O custo real da escolha do autor é pequeno: a decisão vence do mesmo
   jeito e a justificativa diz por quê. Ressalva: valeria uma frase em 08-Modelos dizendo
   explicitamente que `Confianca` qualifica a chave, não o decisor — hoje isso está implícito.
2. **Limiar de reporte zero — rigor, não ruído.** O argumento do autor fecha porque a
   estrutura acompanha: `n_observacoes` viaja na `Contradicao`, e a triagem de
   06-Fluxogramas tem o ramo explícito "manter em observação e coletar mais evidência" para
   o sinal fraco. Suprimir no componente seria decidir em silêncio que a base está certa —
   com um agravante prático: qualquer limiar interno de supressão seria calibrado no dia em
   que a fila de contradições incomodasse, que é o mesmo mecanismo de erosão de A4. Ruído é
   problema de apresentação (ordenar por `n_observacoes` no painel), não de detecção.
3. **`decisao` em branco no roadmap — concordo pela metade.** A justificativa do roadmap
   vale para **valores-marcador do domínio** (a "categoria genérica que não ensinava nada"):
   essa lista é conhecimento de quem usa e fixá-la aqui seria inventar. Mas ela não vale
   para a **string vazia ou só espaço**, que não é marcador de domínio nenhum — é o mesmo
   erro de programa que `ChaveInvalida` já rejeita na chave, e a assimetria é difícil de
   defender: `Entrada(chave="k", decisao="")` entra hoje como alternativa legítima, pode
   empatar com decisão real e aparecer num veredicto. Rejeitar branco agora (mesma
   `_chave_valida`, exceção própria) não requer conhecimento de domínio; a lista de
   marcadores, sim, fica no roadmap. Sugiro dividir o item em dois.

## Sugestões de melhoria

1. Corrigir o "menor valor" do passo 2 de 12-Exemplos: ou trocar para nove, ou manter dez e
   remover a alegação de mínimo — e acrescentar uma asserção que fixe a inversão
   (`assert mem.dominancia(CHAVE)[0] == "fila-suporte"` já existe; falta uma sobre o mínimo,
   se a alegação ficar).
2. Corrigir R8 para "os três retornos indecisos" (ou reformular sem número).
3. Corrigir a prosa do ER em 05-Diagramas para "zero ou mais contradições" e ajustar a
   contagem de transições do stateDiagram (sete setas, ou declarar o critério de contagem).
4. Unificar o número do defeito real em 11-Implementacao (cinco, como no código e em
   13-Testes) e trocar "oitenta dias" por "81 dias" (ou "cerca de três meses") nos dois
   lugares.
5. Dividir o item "rejeição de decisão em branco" do 16-Roadmap em dois: branco literal
   (implementável já, simétrico a `ChaveInvalida`) e lista de valores-marcador (fica no
   roadmap com a justificativa atual).
6. Em 08-Modelos, uma frase declarando que `Confianca` qualifica o estado da evidência da
   chave, e não a autoridade do decisor — é a defesa escrita da decisão discutível 1.

## Veredicto

Aprovado

Média 8,7, nenhuma seção abaixo de 6, três gates verdes na entrada, exemplo reproduzido por
execução independente, checagem de dado de cliente limpa. Os cinco problemas encontrados são
de precisão numérica e de prosa-versus-diagrama — nenhum toca o comportamento do código, as
assinaturas de 08-Modelos ou as dez regras enquanto implementação. A aprovação não os
absolve: os itens 1–4 das sugestões são correções de uma linha cada e deveriam entrar na
incorporação.
