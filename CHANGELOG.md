# CHANGELOG

Registro de estado do acervo. Toda mudança de status de volume passa por aqui com data — o
critério 4 da Definição de PRONTO é exatamente a entrada neste arquivo. Datas em ISO
`YYYY-MM-DD`, mais recente no topo.

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

**Ressalva honesta:** o relatório de auditoria é de **antes** das correções acima. As cinco
mudanças foram verificadas por execução e pelos três gates, mas o texto corrigido não passou
por uma segunda auditoria independente. Quem quiser o selo refletindo o texto atual roda
`/auditar 07` de novo — o relatório antigo permanece no acervo como registro do que foi
encontrado, e não foi editado depois das correções.

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
