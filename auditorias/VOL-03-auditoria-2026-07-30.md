# Auditoria — Volume 03 DISCOVERY

**Data:** 2026-07-30
**Revisao:** 1
**Auditor:** auditor-fable (Fable 5)
**Gates na entrada:**

```
$ python -m ferramentas.validar 03
ok: volume 03 sem violacoes

$ python -m pytest exemplos/03-discovery -q
.....................................................................    [100%]
69 passed in 0.32s

$ python -m ferramentas.validar --cross-refs
ok: referencias cruzadas sem violacoes
```

## Método

Além dos três gates, esta auditoria **reproduziu por execução** os dez blocos de
`12-Exemplos.md` em script independente, num único ambiente, com todas as asserções
originais — os dez passaram. Conferiu por execução: as contagens do catálogo contra o
mindmap de `05-Diagramas.md` (universais 6; WEB 4, MOBILE 5, DESKTOP 4, AUTOMACAO 4;
LOJA 3, SAUDE 3, DADO_PESSOAL 2, MULTIUSUARIO 2, TEMPO_REAL 2, INTEGRACAO_EXTERNA 2 —
soma 37, zero divergência); o princípio das evidências distintas contra uma frase nova
com sinal para 2 plataformas e 6 contextos (8 palpites, 8 evidências distintas, acento
preservado); e o contrafactual do critério de parada (`peso_minimo` padrão, 1 e 8).
Todos os 12 nomes de teste citados na prosa (02, 07, 11, 13) foram conferidos um a um
contra a suíte, e as assinaturas, enums e o `CATALOGO` foram conferidos contra os
quatro módulos reais.

## Notas por seção

| Seção | Nota | Justificativa |
|---|---|---|
| 01-Introducao | 9 | Os dois modos de falha (construir da frase; formulário de quarenta) são concretos e reaparecem no resto do volume. O número central — sete das quinze perguntas erradas ao aceitar a inferência em silêncio — foi reproduzido por execução (passo 8). A ligação com a procedência do volume 12 é conceitual, sem citar domínio de origem. |
| 02-Objetivos | 9 | Tabela de sete objetivos com local de verificação; os seis nomes de teste citados existem exatamente como escritos e testam o que a tabela afirma. O valor 1/3 da recusa confere com a execução. "Parar quando não vale" declara o caso medido (15→14 com a décima quinta por escrito) e ele confere. |
| 03-Escopo | 9 | Fronteira em tabela com volume responsável e razão por linha; 04/05/38/07/12/22 conferem com `contrato.json`. A distinção peso ≠ prioridade de execução (linha do 38) é a mais útil da tabela. A fronteira interna declara o custo aceito (`lacunas_ativas` não prioriza) e aponta o lugar da política (`Entrevista._ordenar`), que confere com o código. |
| 04-Arquitetura | 9 | O flowchart de dependências confere com o grafo real de imports (catalogo→deteccao→entrevista→especificacao, sem seta de volta — `gerar` lê e não escreve, conferido). A seção "o que cada módulo é responsável por NÃO fazer" é fiel: não há ordenação em `lacunas_ativas`, não há `if lacuna_id ==` no controle, não há `PADRAO_ASSUMIDO` na saída. |
| 05-Diagramas | 9.5 | O stateDiagram-v2 do ciclo do palpite corresponde ao código (recusa sem rastro, `NaoProduzido` legítimo, pendente bloqueia `completa`). O mindmap foi conferido por contagem executada: todas as onze contagens e os pesos citados (teto 9 nos condicionais, piso 2) estão corretos. A leitura 37→15 confere com `len(tudo.ativas()) == 15` medido. |
| 06-Fluxogramas | 8 | Os dois fluxogramas percorrem o código real e o segundo (o "por que você quer saber isso?") é conteúdo operacional que não existe no código — é o melhor da seção. **Mas a contagem da prosa é confusa: "cinco pontos de decisão e nenhum deles depende de julgamento humano" — o diagrama tem seis losangos (C, F, H, L, P, R); cinco só fecha excluindo H, e a frase seguinte diz "os dois que dependem de pessoa (H, e implicitamente N e O)", que nomeia três nós chamando-os de dois.** |
| 07-Regras | 9.5 | As sete regras têm os sete testes citados, todos existentes com o nome exato, e cada um testa o que a regra afirma (conferido no fonte). O corolário de R2 (evidência que não distingue não explica) tem teste de regressão real. A assimetria de R4 (condicional aberta não impede completude) confere com `completa` e com o teste do quarto caso. |
| 09-Boas-Praticas | 9 | Cada prática com a razão e com o comportamento concreto trocado. "Não existe `if lacuna_id == 'onde_roda'`" conferido no fonte. O denominador 6→11→14 conferido por execução. "Não se aplica é resposta" e "taxa de recusa revisa o catálogo" são as duas práticas que o código sozinho não garante — a seção cobre o buraco certo. |
| 10-Anti-Patterns | 9 | Seis padrões com custo concreto; os números de A1 (37/15/14) e A2 (7 de 15 erradas, 4 de aparelho de mão, 3 de navegador nunca feitas) foram reproduzidos por execução. A6 fecha o par com `completa` sem parâmetro e a distinção "perguntar menos é economia, declarar-se completa sem estar é afirmação falsa" é a formulação certa. |
| 11-Implementacao | 8.5 | Descreve decisões reais e verificáveis (`_dobrar` com mapa de posições, conjunção de portas, detecção no construtor). **Imprecisão: "site casaria dentro de deposite — o segundo caso tem teste próprio" — não tem; os dois casos vivem no mesmo teste (`test_fronteira_de_palavra_impede_casamento_dentro_de_outra_palavra`), como asserções separadas.** |
| 12-Exemplos | 9.5 | Os dez blocos foram executados em sequência num ambiente independente: todos passam, e cada número da prosa (37/6, três evidências distintas, fila 6→11→14, ordem das doze perguntas, 44 linhas de markdown, 15 vs 14, só `web_idioma` abaixo do mínimo) confere com a saída real. O parágrafo da correção (evidência idêntica → janela de palavras) é honesto e tem o teste de regressão que promete. A comparação final "15 contra 37, não 14 contra 15" é o argumento certo no lugar certo. |
| 13-Testes | 8 | As contagens 19+16+22+12=69 conferem com a coleta do pytest (com parametrização; são 64 funções — a prosa não faz a distinção, que o volume 12 fez). O "repetido cinco vezes" do empate confere (`for _ in range(5)`). **Erro factual: "dois testes de fronteira de palavra" — é um teste cobrindo os dois casos.** A seção "o que os testes não cobrem" é fronteira honesta. |
| 14-Metricas | 9 | Sete métricas com definição operacional, unidade e origem; todos os valores citados conferem com a execução (0,125; 1/3; 0,595; uma aberta, nenhuma universal; zero pendentes). "Recusa zero é motivo de suspeita" e "perguntas até fechar não deve ser minimizada" são as duas leituras que salvam as métricas de virar teatro. |
| 15-Checklist | 7 | Acionável na maior parte, e a segunda lista (antes de entregar) tem verificação nomeada por item. **Mas o item de fechamento da primeira lista afirma um teste que não existe: "um teste que conta lacunas por bloco quebra de propósito quando o catálogo muda" — nenhum teste da suíte conta lacunas por bloco ou no total; as contagens vivem só nos blocos de `12-Exemplos.md`, que os gates não executam.** O item, como escrito, não pode ser seguido. |
| 16-Roadmap | 9 | Cinco itens, cada um com o que falta e por que não agora — e as razões são de desenho (conjunto anotado mediria a própria escrita; gatilho por resposta exige opções fechadas antes), não de preguiça. Item 4 delega persistência ao volume 12 em vez de reimplementar, coerente com o escopo. |
| 17-Conclusao | 9 | Fecha com as três lições, todas apoiadas em números que esta auditoria reproduziu. O parágrafo final — o defeito da evidência idêntica passava por todos os gates e só a execução do passo a passo pegou — é autocrítica verificável, e é verdadeira: gate confere que o código roda, não que a prosa mediu. |
| 18-Referencias-Cruzadas | 9 | Distingue pré-requisito (grafo) de vizinhança (prosa); `depende_de: []` está justificado aqui e no `_VOLUME.yml` com a mesma razão (04/05/38 sem seção escrita). Todos os links resolvem (gate 1). A navegação interna por perfil de leitor é útil e curta. |

media: 8.8

## Problemas encontrados

1. **(médio) 15-Checklist afirma um teste inexistente.** "Um teste que conta lacunas
   por bloco quebra de propósito quando o catálogo muda, e ajustar a contagem é parte
   da mudança" — não há teste de contagem em `exemplos/03-discovery/tests/` (verificado
   por grep de `len(CATALOGO)`, `== 37`, contagens por bloco: zero ocorrências). As
   únicas contagens estão nos blocos de `12-Exemplos.md`, que nenhum gate executa. O
   item de checklist mais importante para quem estende o catálogo aponta para uma
   proteção que não existe.
2. **(menor) 13-Testes: "dois testes de fronteira de palavra".** Existe um teste
   (`test_fronteira_de_palavra_impede_casamento_dentro_de_outra_palavra`) cobrindo os
   dois casos (`app`/`aplicativo` e `site`/`deposite`) como duas asserções.
   `11-Implementacao.md` repete a imprecisão com "o segundo caso tem teste próprio".
3. **(menor) 06-Fluxogramas: contagem de pontos de decisão confusa.** O primeiro
   fluxograma tem seis losangos; a prosa diz "cinco pontos de decisão e nenhum deles
   depende de julgamento humano" e em seguida "os dois que dependem de pessoa (H, e
   implicitamente N e O)" — nomeando três nós sob o numeral dois. O leitor não consegue
   fechar a conta com o diagrama.
4. **(observação, não defeito) 13-Testes conta itens coletados, não funções.** 19/16/22/12
   são contagens com parametrização (64 funções definidas). A frase é verdadeira para a
   saída do pytest, mas o volume 12 fez essa distinção explícita e este não faz.

## Verificacao do dominio neutro

```
$ grep -rin "extrato\|lancamento\|lançamento\|contabil\|contábil\|omie\|sicoob\|reforma tribut\|concilia" 03-DISCOVERY/ exemplos/03-discovery/
(saida vazia — exit 1)
```

**Limpo.** Nenhuma ocorrência nas 17 seções, nos 4 módulos ou nos 4 arquivos de teste.
O domínio dos exemplos (loja de bairro, clínica, automação de relatório) é neutro e
inventado; a referência ao volume 12 é conceitual (procedência), sem nomear sistema,
cliente ou domínio de origem.

## Julgamento do criterio de parada (peso_minimo)

**A existência do limiar é justificada com argumento real; o valor padrão 4 é coerente
mas a conexão nunca é escrita.** O argumento de existência (entrevista.py, 01, 02, 14):
o interrogatório de quarenta itens é abandonado no décimo quinto, e a lacuna não
perguntada continua constando como decisão aberta — não é omissão, é economia declarada.
O argumento é reforçado pelo lugar mais honesto do volume: o passo 9 de `12-Exemplos.md`
admite que a economia do limiar é marginal (uma pergunta) e que a economia grande (22
perguntas) vem da relevância — o texto não infla o próprio mecanismo.

Sobre o número 4: o catálogo define implicitamente a faixa — as quatro lacunas de peso
2–3 (`web_idioma`, `mobile_tablet`, `desktop_aparencia`, `auto_saida_formato`) declaram
no próprio `porque` que "existem para sair como decisão aberta em vez de gastar um
turno". O padrão 4 é exatamente o corte acima dessa faixa. Mas **nenhuma seção escreve
essa frase**: o 4 aparece em `PESO_MINIMO_PADRAO` e no passo 6 sem a ligação explícita
com a semântica dos pesos 2–3. Falta uma frase, não um argumento.

**Comportamento verificado por execução** (mesmo caminho do passo a passo, variando só
o limiar):

```
padrao (4):    14 perguntas, 1 decisao aberta,  completa=True
peso_minimo=1: 15 perguntas, 0 decisoes abertas, completa=True
peso_minimo=8:  8 perguntas, 7 decisoes abertas, completa=False
```

`peso_minimo=1` produz mais perguntas e menos decisões abertas, como o texto promete. O
caso 8 confirma a assimetria de R4 na direção difícil: `fora_de_escopo` (universal, peso
7) cai abaixo do limiar, fica aberta, e `completa` devolve `False` — subir o limiar não
compra uma especificação fechada, o que é exatamente a proteção que A6 descreve.

**Verificação do princípio central por execução:** frase nova com sinal para 2
plataformas e 6 contextos produziu 8 palpites com 8 evidências distintas entre si, todas
trechos reais do texto original com acento preservado, cada uma centrada no termo que a
produziu. O princípio "evidências de palpites diferentes são distintas" se sustenta fora
do caso ensaiado pela prosa.

## Sugestões de melhoria

1. **Criar o teste que 15-Checklist promete** (ou reescrever o item): um
   `test_contagem_do_catalogo_por_bloco` em `test_catalogo.py` afirmando 37 no total, 6
   universais e as contagens por plataforma e contexto. Custo de dez linhas, e o item do
   checklist passa a ser verdadeiro.
2. **Corrigir "dois testes de fronteira" em 13-Testes e "teste próprio" em
   11-Implementacao** — ou dividir o teste em dois, que é o que a prosa já acha que
   existe.
3. **Reescrever a frase dos pontos de decisão em 06-Fluxogramas** para fechar com o
   diagrama: seis losangos, cinco do motor e um (H) da pessoa, com N e O como interação
   e não decisão.
4. **Uma frase em 07-Regras ou 11-Implementacao ligando o padrão 4 à faixa 2–3 do
   catálogo** ("o padrão corta exatamente abaixo da faixa que o próprio catálogo declara
   não valer um turno"), fechando o julgamento acima.
5. (Menor) Em 13-Testes, distinguir funções de itens coletados, como o volume 12 faz.

## Veredicto

**Aprovado.** Média 8.8, nenhuma seção abaixo de 6. Os três gates estão verdes, o
domínio é neutro, todos os números da prosa que esta auditoria reproduziu conferem com a
execução — incluindo o contrafactual do palpite errado aceito e o contrafactual do
limiar — e os problemas encontrados são de precisão de prosa (um item de checklist
apontando para teste inexistente é o único que engana o leitor em algo acionável),
não de desenho nem de código.
