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
