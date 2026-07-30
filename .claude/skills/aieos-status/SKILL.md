---
name: aieos-status
description: Reporta o estado dos 42 volumes do acervo AI-ENGINEERING-OS — tipo, status, seções presentes, nota da última auditoria e marca de perecível — rodando `python -m ferramentas.status`. Use quando o pedido for `/status`, "como está o acervo", "quais volumes estão prontos" ou "quanto falta".
---

# `/status`

Procedimento. Leitura pura: `status.py` **nunca escreve nada**. Se o estado reportado está
errado, o que está errado é o disco, não a ferramenta.

**Rode de dentro de `AI-ENGINEERING-OS/`.**

## 1. Rodar

```bash
python -m ferramentas.status
```

Saída: uma tabela Markdown dos 42 volumes declarados no contrato, mais uma linha de resumo
com a contagem por status. Exit 0 normal; exit 2 se o contrato estiver ausente ou inválido.

## 2. Colar a tabela

Cole a saída **literal** na resposta. Não reescreva a tabela de memória nem resuma "está tudo
em rascunho": a tabela é a evidência, e a contagem por status é o que responde "quanto falta".

## 3. Como ler cada coluna

| Coluna | O que significa |
|---|---|
| `Vol` | id de 2 dígitos, sempre string (`07`), como no contrato |
| `Nome` | nome declarado em `contrato.json`; a pasta é `NN-NOME` |
| `Tipo` | `ENGINE`, `ARQUITETURA`, `PROCESSO`, `BIBLIOTECA` ou `GOVERNANCA` — determina quais seções são obrigatórias |
| `Status` | valor lido do `_VOLUME.yml`, ou `PENDENTE` derivado |
| `Secoes` | `presentes/esperadas` |
| `Auditoria` | média da auditoria mais recente do volume, ou `-` se não houver |
| `Perecivel` | `sim` nos volumes 26, 27 e 34; `-` nos demais |

### A coluna `Secoes` é `presentes/esperadas`

- **`esperadas`** vem de `Contrato.secoes_de(tipo)` — **não é 18 para todo mundo**.
  `BIBLIOTECA` troca `04-Arquitetura` e `05-Diagramas` por `04-Catalogo` (17); `PROCESSO`
  dispensa `08-Modelos` (17). Comparar `12/18` de um `PROCESSO` com `12/17` de outro tipo é
  comparar coisas diferentes.
- **`presentes`** conta quantos `<secao>.md` existem em disco, e só isso: **existência de
  arquivo, não qualidade dele.** Uma seção de duas linhas conta como presente e é reprovada
  pelo gate 1 em `substancia-curta`. `18/18` não significa volume bom — significa volume
  completo em arquivos.
- `0/18` numa pasta que existe é o estado normal de volume só materializado por
  `scaffold.py`: tem `_VOLUME.yml`, ainda não tem seção escrita.

### `PENDENTE` é estado derivado, nunca gravado

`status` só aceita três valores graváveis: `RASCUNHO`, `REQUER_REVISAO`, `PRONTO`.
`PENDENTE` **não é um deles** — é calculado por `status.py` em duas situações:

1. o volume está declarado no contrato mas **a pasta não existe** em disco (rode
   `python -m ferramentas.scaffold` para materializar); ou
2. a pasta existe **sem `_VOLUME.yml`**.

Se você vê `PENDENTE` na tabela, não vá "corrigir o `_VOLUME.yml` para PENDENTE" — esse
valor reprova o gate 1 em `frontmatter-status`. O caminho é criar o que falta.

`_VOLUME.yml` presente mas com front-matter malformado aparece como `RASCUNHO`, não como
erro: a ferramenta prefere reportar o estado mais conservador a explodir no meio de um
levantamento.

## 4. Nota de auditoria, e o que ela não prova

A coluna `Auditoria` é a linha `media:` do relatório vigente do volume, escolhido por
`status.relatorio_mais_recente()`. A escolha é por `(data, revisão)` extraídas do nome, na
gramática `VOL-NN-auditoria-AAAA-MM-DD[-rN].md` — revisão ausente equivale a 1, e é comparada
como inteiro. **Não é ordem alfabética**, e não pode ser: `-r2.md` ordena *antes* de `.md`
porque o hífen é 0x2D e o ponto é 0x2E, então uma reauditoria do mesmo dia perderia para a
auditoria antiga em silêncio; e `-r10` perderia para `-r2`. Relatório com nome fora da
gramática é ignorado de propósito — nome inválido não vira nota. `-` significa
"nenhuma auditoria" **ou** "o arquivo existe mas a linha `media:` não casou o formato" — as
duas aparecem iguais na tabela. Se você esperava uma nota e veio `-`, verifique o formato da
linha com:

```bash
python -c "from pathlib import Path; from ferramentas.status import nota_da_ultima_auditoria; print(nota_da_ultima_auditoria(Path('.'), 'NN'))"
```

A nota é histórica: ela reflete o relatório, não o disco de agora. Volume editado depois da
auditoria continua exibindo a nota antiga. Só os gates dizem o estado atual —
`python -m ferramentas.validar --tudo`.

## 5. Se o pedido for "quanto falta"

Responda com a linha de resumo (`PENDENTE=n RASCUNHO=n ...`) e o que ela implica, sem
inventar prazo nem projeção de páginas. `ROADMAP.md` guarda as metas numéricas do autor e
registra explicitamente que elas **não** são critério de aceite; o critério é a Definição de
PRONTO em `00-INTRODUCAO/Convencoes.md`.
