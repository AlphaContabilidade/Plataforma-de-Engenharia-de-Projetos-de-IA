# CHANGELOG

Registro de estado do acervo. Toda mudança de status de volume passa por aqui com data — o
critério 4 da Definição de PRONTO é exatamente a entrada neste arquivo. Datas em ISO
`YYYY-MM-DD`, mais recente no topo.

## 2026-07-30

### Volume `12-MEMORY` auditado e promovido a `PRONTO`

Primeiro volume cujo código foi **extraído de um sistema em produção** e generalizado, em vez
de escrito para o volume. A plataforma passou a servir para construir software, e não para
acumular prosa: o produto de cada volume é o componente executável, e o texto é o manual dele.

Auditoria independente em Fable 5: `auditorias/VOL-12-auditoria-2026-07-30.md`.
**Veredicto Aprovado, média 8.7**, nenhuma seção abaixo de 6 (menor nota 7, em `05-Diagramas`).
`08-Modelos` recebeu 10 — zero divergência com o código, conferida item por item.

Os quatro critérios de PRONTO: gate 1 `exit 0`, gate 2 **271 testes verdes**, gate 3 `exit 0`,
auditoria 8.7 — e esta entrada é o critério 4.

**O componente.** Três módulos em `exemplos/12-memory/`, sem nada do domínio de origem nas
assinaturas: `memoria_observada.py` (armazém de decisões em que cada entrada carrega a
**origem** — observada, escrita pelo próprio agente, base congelada, decidida por humano),
`contaminacao.py` (entrada escrita pelo agente **nunca** conta como evidência, e a contradição
entre base congelada e histórico observado é **reportada**, nunca resolvida em silêncio) e
`precedencia.py` (veredicto **indeciso de primeira classe**, com justificativa — evidência que
não decide não vira chute de confiança baixa).

**Os três defeitos reais que o componente torna impossíveis** estão descritos em
`10-Anti-Patterns.md` como padrão, sem nenhum identificador de cliente: base congelada
contradizendo o histórico sem sinalizar; o sistema lendo a própria escrita como evidência
independente e se autoconfirmando; e evidência insuficiente sendo tratada como se decidisse.

Verificado por varredura: nenhuma menção a Omie, Sicoob, boleto, CNPJ, conta bancária, valor
monetário real ou código de categoria contábil no código, nos testes ou nas seções. O auditor
repetiu a varredura de forma independente e confirmou.

**Cinco achados da auditoria, todos incorporados antes da promoção.** Todos de texto — nenhum
tocava o comportamento do código:

1. `12-Exemplos` afirmava que **dez** escritas do agente invertem a dominância. O auditor
   mediu: **nove**. O parágrafo era justamente o que documenta uma correção feita por medição,
   e continha um número que ninguém mediu. A correção não aceitou nem o número do autor nem o
   do auditor: um script varreu `n` de 1 a 15 e o volume passou a trazer o valor medido, com a
   fração exata. O detalhe que só aparece medindo: com **oito** a contagem empata em 9 × 9 e o
   desempate alfabético mantém a liderança anterior — por isso oito não basta. Há agora
   asserção que **fixa o mínimo** nos dois lados (8 não inverte, 9 inverte).
2. `07-Regras` R8 dizia "quatro retornos indecisos"; o código tem **três** — empate, dominância
   abaixo do mínimo, nenhuma evidência vigente. Corrigido nomeando os três.
3. `05-Diagramas` dizia "zero ou uma contradição"; o diagrama e o código permitem **várias** por
   chave, e há teste que prova duas.
4. `11-Implementacao` citava "dez escritas" onde o teste diz **cinco**.
5. "Oitenta dias" onde são **oitenta e um**.

**Uma discordância parcial do auditor, aplicada.** O autor havia deixado no roadmap a rejeição
de `decisao` em branco, argumentando que a lista de valores que significam ausência é
conhecimento de domínio. O auditor concordou pela metade: a lista é domínio, mas string vazia é
erro de programa simétrico ao de chave vazia e deveria ser rejeitada já. Entrou
`DecisaoInvalida`, irmã de `ChaveInvalida` e não subclasse dela, com três testes — a suíte dos
exemplos foi de 47 para 50 casos. O item do roadmap foi dividido para refletir que metade saiu.

**Julgamento do auditor sobre as decisões discutíveis:** contradição aberta rebaixar a confiança
mesmo com decisão humana — autor correto, porque `Confianca` qualifica o estado da evidência da
chave, não a autoridade de quem decidiu; limiar zero de contradição — rigor e não ruído, porque
`n_observacoes` viaja no relatório e suprimir sinal fraco é a erosão silenciosa que o volume
existe para impedir.

### Interface web local

`ferramentas/web.py`, servidor de biblioteca padrão que abre no navegador. Grade dos 42 volumes
clicável, ficha do volume com seções presentes e ausentes, botão que roda os três gates e mostra
as violações agrupadas por regra, botão que gera e copia o briefing de produção. Verificada no
navegador de verdade: clique no volume 07, os três gates aprovaram, o gate 2 executou pytest.

Segurança, porque um endpoint que dispara processo é um executor: bind estritamente em
`127.0.0.1`, id de volume validado contra o contrato antes de qualquer toque em disco, nenhum
caminho de arquivo vindo da requisição, sem `shell=True`, e `Host`/`Origin` conferidos contra
DNS rebinding e POST de outra origem.

A placa de testes **não afirma verde**: mostra a contagem estática de funções em disco com o
comando que produz o veredicto, e o JSON carrega `verificado: false`. Cravar "271 testes verdes"
numa página estática seria a proibição 3 aplicada a todos menos a nós mesmos.

Corrigido no caminho: os códigos de cor ANSI do pytest apareciam literais na página. `--color=no`
na chamada e limpeza defensiva na camada de apresentação, que não sabe renderizar ANSI.

### Skills renomeadas e o mecanismo confirmado

As cinco skills ganharam prefixo — `aieos-novo-volume`, `aieos-auditar`, `aieos-status`,
`aieos-cross-reference`, `aieos-exportar`. Duas razões: `status` colidia com um comando embutido
do harness, e o prefixo torna a procedência óbvia na listagem.

**Confirmado por invocação, não por suposição:** o harness descobre skills de `.claude/skills/`
aninhado em subpasta, escopadas ao diretório (`AI-ENGINEERING-OS:aieos-*`). A descoberta acontece
no início da sessão, então arquivo criado no meio dela não aparece até a sessão seguinte — foi o
que produziu o `Unknown skill` inicial e a hipótese errada de que aninhamento não funcionava.
`ferramentas/instalar_skills.py` permanece como alternativa para harness sem esse suporte.

## 2026-07-29

### Máquina de produção construída

`ferramentas/` completo, em Python de biblioteca padrão apenas, com suíte de testes própria
usando fixtures deliberadamente ruins — cada violação prevista tem um teste que exige que ela
seja detectada:

- `frontmatter.py` — parser do subconjunto YAML restrito do front-matter e dos `_VOLUME.yml`;
  número com zero à esquerda permanece string, de modo que `volume: "07"` e `volume: 07` nunca
  divergem no resto da máquina.
- `modelo.py` — `Violacao`, o tipo que atravessa todas as ferramentas.
- `contrato.py` — carregamento do contrato e resolução de seções e diagramas por tipo.
- `regras.py` — uma função pura por regra: `frontmatter`, `frontmatter-campo`,
  `frontmatter-status`, `frontmatter-coerencia`, `substancia-curta`, `marcador-proibido`,
  `mermaid-nao-fechado`, `mermaid-vazio`, `mermaid-tipo`, `mermaid-sem-descricao`,
  `diagrama-obrigatorio`, `exemplo-inexistente`, `exemplo-sem-teste`, `link-morto`.
- `validar.py` — orquestração dos gates 1 e 3, com CLI (`NN`, `--tudo`, `--cross-refs`) e
  códigos de saída 0, 1 e 2.
- `status.py` — leitura de estado do acervo, sem escrever nada; `PENDENTE` como estado
  derivado.
- `scaffold.py` — materialização idempotente das pastas de volume, que nunca sobrescreve um
  `_VOLUME.yml` existente.
- `exportar.py` — geração de `mkdocs.yml` a partir do que existe em disco, com aviso explícito
  quando `mkdocs` não está instalado.

### Contrato v1.0.0

`00-INTRODUCAO/contrato.json` publicado como **única fonte de verdade legível por máquina**:
18 seções na base, cinco tipos de volume (`ENGINE`, `ARQUITETURA`, `PROCESSO`, `BIBLIOTECA`,
`GOVERNANCA`), três status graváveis, mínimo global de 200 palavras de prosa com mínimo
próprio para quatro seções curtas, seis marcadores proibidos, diagramas obrigatórios por tipo
e os 42 volumes com nome, tipo e marca de perecível.

O contrato ganhou um guardião: `ferramentas/tests/test_contrato.py::test_convencoes_nao_derivou`
compara a tabela de tipos de `00-INTRODUCAO/Convencoes.md` com o JSON e reprova a suíte se as
duas divergirem. Documentação que pode envelhecer sozinha não é contrato.

### Esqueleto da plataforma e `00-INTRODUCAO`

Criados `CLAUDE.md` (contexto local, com o aviso explícito de que a raiz do repositório é
outro projeto e não deve ser tocada), `README.md`, `CHANGELOG.md`, `ROADMAP.md`,
`CONTRIBUTING.md` e `LICENSE` (MIT, titular Alpha Contabilidade); e em `00-INTRODUCAO/` os
arquivos `Prefacio.md`, `Como-Utilizar.md`, `Glossario.md`, `Convencoes.md` e
`Arquitetura-Geral.md`.

Os 42 volumes declarados no contrato foram materializados como pasta com `_VOLUME.yml` em
`RASCUNHO` — 41 deles sem seções escritas, registrados como pendentes no `ROADMAP.md`.

### Volume-piloto `07-PROMPT-ENGINE` em produção

Tipo `ENGINE`, 18 seções, com exemplos executáveis em `exemplos/07-prompt-engine/`
(`prompt_template.py`, `prompt_registry.py`, `prompt_evaluator.py`), cada um com teste pytest
ao lado. Serve como padrão-ouro e como teste de estresse das próprias convenções: foi
escrevendo o piloto que se verificou que o contrato é satisfazível com conteúdo substantivo.

### Comandos e subagente auditor

Criados `.claude/agents/auditor-fable.md` (`model: fable`, com ferramentas de leitura mais
`Bash`, porque o auditor precisa **rodar** os gates e os testes em vez de acreditar no que o
volume afirma) e as cinco skills em `.claude/skills/`: `novo-volume`, `auditar`, `status`,
`cross-reference` e `exportar`.

Dois contratos ocultos foram descobertos e documentados ao escrevê-los:

- A linha `media: N.N` do relatório de auditoria é **contrato de máquina**:
  `status.py::nota_da_ultima_auditoria` a lê com regex ancorado. Negrito, maiúscula, dentro
  de tabela ou seguida de `/10` não casam, e a nota some do `/status` em silêncio. As quatro
  formas inválidas estão listadas como proibidas no arquivo do agente.
- O nome `VOL-NN-auditoria-<data>.md` só ordena corretamente porque a data é ISO — a função
  pega o último alfabético. Data em outro formato quebraria a escolha do relatório mais
  recente sem erro nenhum.

`/novo-volume` **nunca** grava `PRONTO`, nem com os gates 1 e 2 verdes: o critério 3 da
Definição de PRONTO ainda não foi avaliado naquele ponto. `PRONTO` só pode sair de
`/auditar`.

**Limitação registrada:** não foi possível confirmar nesta sessão que as skills aparecem
como `/novo-volume` e afins, porque skills escopadas por diretório exigem uma sessão
iniciada com o diretório de trabalho dentro de `AI-ENGINEERING-OS/`. O caminho verificado com
saída real é a invocação direta por `python -m ferramentas.*`.

### Volume `07-PROMPT-ENGINE` auditado e promovido a `PRONTO`

Auditoria independente em Fable 5: `auditorias/VOL-07-auditoria-2026-07-29.md`.
**Veredicto Aprovado, média 8.5, nenhuma seção abaixo de 6** (menor nota 7, em
`05-Diagramas` e `13-Testes`).

O auditor verificou executando: rodou os gates, rodou o pytest, e reproduziu os cinco blocos
de `12-Exemplos.md` em script para conferir se as afirmações de prosa se sustentam. Nos eixos
"contradições internas" e "funcionalidade dos exemplos" declarou explicitamente que **não**
encontrou problema, tendo conferido o `stateDiagram-v2` contra `TRANSICOES` transição por
transição.

Cinco problemas encontrados, todos incorporados antes da promoção:

1. **Bug de código, o mais grave.** O `hash` de `PromptTemplate` não cobria o campo
   `obrigatoria`: dois templates que se comportam de forma diferente no `render` produziam o
   mesmo hash, e `PromptRegistry.registrar` os tratava como a mesma versão — invalidando a
   regra R2 do próprio volume. Corrigido no **código**, não na prosa, porque a invariante
   pretendida estava certa: a obrigatoriedade entrou na `assinatura`, que passou de
   `nome(v:str)` para `nome(v?:str)` quando a variável é opcional. Dois testes novos travam a
   distinção, e um terceiro trava o limite do outro lado — `descricao` **não** entra no hash,
   de propósito, porque não altera o que `render` produz. Critério agora escrito em
   `07-Regras.md`: entra na assinatura o campo que muda a saída.
2. `05-Diagramas.md` declarava `CONTRATO ||--|{ VARIAVEL`, mas template com zero variáveis
   constrói sem erro (prompt estático). Corrigido para `||--o{`.
3. `13-Testes.md` e `17-Conclusao.md` diziam "34 testes"; o comando que a própria seção manda
   rodar imprime outro número, porque um teste é parametrizado em três casos. Corrigido para
   37 funções coletadas como 39 casos.
4. Rótulo agramatical num nó de decisão de `06-Fluxogramas.md`.
5. `14-Metricas.md` trazia métrica que agrupava por campo de texto livre — na prática daria um
   grupo por expressão regular, não por categoria. Redefinida sobre prefixo estável, com a
   versão enumerada movida para `16-Roadmap.md`.

Estado final na promoção, com os quatro critérios satisfeitos: gate 1 `exit 0`, gate 2
**133 testes verdes**, gate 3 `exit 0`, auditoria 8.5 — e esta entrada é o critério 4.

### Reauditoria (r2): selo fechado sobre o texto corrigido

`auditorias/VOL-07-auditoria-2026-07-29-r2.md`. **Veredicto Aprovado, média 8.9**, nenhuma
seção abaixo de 6 (menor nota 8). A ressalva do parágrafo anterior está resolvida: o selo
agora reflete o texto que está no acervo, não o texto anterior às correções.

O auditor formou as 18 notas **antes** de abrir o relatório anterior, e só depois o usou para
verificar se os cinco achados haviam sido resolvidos — os cinco confirmados por execução ou
leitura direta. Reproduziu novamente os blocos de `12-Exemplos.md` contra o código, conferiu as
sete transições do `stateDiagram-v2`, construiu um template de zero variáveis para checar a
cardinalidade do ER, e resolveu os sete links de `18-Referencias-Cruzadas`.

A média subiu de 8.5 para 8.9, e as seções que subiram (`05`, `07`, `08`, `13`, `14`, `17`) são
exatamente as que carregavam os problemas corrigidos — não houve subida por cortesia em seção
que não mudou.

Um problema novo, corrigido: a abertura de `12-Exemplos.md` dizia "três casos de ouro" quando a
bateria executada tem quatro — o próprio bloco assevera `total == 4`. Uma palavra.

**Bug de máquina descoberto ao preparar esta reauditoria.** `status.py::nota_da_ultima_auditoria`
escolhia o relatório por ordem alfabética, e `VOL-07-auditoria-2026-07-29-r2.md` **perde** para
`VOL-07-auditoria-2026-07-29.md` nessa comparação, porque o hífen (0x2D) ordena antes do ponto
(0x2E) de `.md`. A plataforma teria lido a nota antiga e reportado como se fosse a nova — em
silêncio, que é o pior modo de falhar. A escolha passou a ser por `(data, revisão)` extraídas do
nome, com a revisão comparada como inteiro (`-r10` ganha de `-r2`), e nome fora da gramática
`VOL-NN-auditoria-AAAA-MM-DD[-rN].md` é ignorado de propósito. Nova função pública
`relatorio_mais_recente()`. Seis testes novos; suíte em **139**.

### Decisão de escopo: sobreposição de domínios resolvida por fronteira

Registrada em `ROADMAP.md`. Mantidos os 42 volumes; cada volume de grupo sobreposto declara a
fronteira no seu `03-Escopo`, nomeando o vizinho e o que pertence a ele. Fundir reduziria a
contagem mas destruiria o índice do autor, e cada rótulo é um lugar onde alguém vai procurar
informação. Eixos definidos para os quatro grupos: `07`/`28`/`29` pelo que cada um faz com um
prompt; `11`/`13`/`14`/`15` por fonte, índice, pipeline e janela; `17`/`18` e `31`/`32` por "o
que precisa ser verdade" contra "como se verifica"; `22`–`25` contra `16` pela fronteira do
produto.

Os 13 frameworks sem definição **não** foram decididos, e a razão está escrita: atribuir escopo
a nome sem definição seria invenção. Permanecem no backlog aguardando o autor.

### Correções de conteúdo aplicadas sobre a especificação original

- **Frameworks.** RTF, CARE, RISE, TAG, BAB e RAPPEL documentados como **técnicas públicas de
  prompt**, não como proprietárias. Único framework proprietário: `AI-ENGINEERING-FRAMEWORK`,
  que é a síntese que esta plataforma propõe.
- **Backlog honesto.** ORBIT, FLOW, NEXUS, FUSION, GENESIS, ATLAS, EVEREST, QUANTUM, IDEA+,
  PACE, BUILD, SMART-AI e ENTERPRISE-AI registrados em `frameworks/_backlog.md` como nomes
  presentes na especificação sem definição, aguardando o autor. **Não foram inventados.**
- **Metas numéricas.** "8.000+ páginas", "2.000+ prompts", "300+ agentes" e "500+ exemplos"
  registrados no `ROADMAP.md` como estimativa do autor e **explicitamente não usados como
  critério de aceite**. O critério é a Definição de PRONTO.
- **Conteúdo perecível.** `26-AI-MODELS`, `27-LLM-ROUTER` e `34-COST-OPTIMIZATION` marcados
  `perecivel: true`, com regra própria em `Convencoes.md`: finos, sem fixar preço ou nome de
  modelo, apontando para fonte viva.
- **Conflito de `CLAUDE.md` resolvido.** O `CLAUDE.md` da plataforma vive nesta subpasta; o da
  raiz, da rotina de conciliação Sicoob × Omie, permanece intocado e tem precedência em
  qualquer questão que toque aquele projeto.
