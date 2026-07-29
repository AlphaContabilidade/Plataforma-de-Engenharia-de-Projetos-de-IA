---
name: auditar
description: Audita um volume do acervo AI-ENGINEERING-OS despachando o subagente `auditor-fable`, grava o relatório datado em `auditorias/` e atualiza o status do volume conforme a média (≥ 8,0 e nenhuma seção < 6). Use quando o pedido for `/auditar N`, "auditar o volume NN", "rodar a auditoria do piloto" ou equivalente.
---

# `/auditar N`

Procedimento. A auditoria roda **entre o gate 2 e o gate 3**: julga-se o que já é
estruturalmente válido e executável, porque julgar o texto de um volume que nem compila é
gastar a auditoria no problema errado.

**Rode tudo de dentro de `AI-ENGINEERING-OS/`.** Datas em ISO `YYYY-MM-DD`; hoje é
`2026-07-29`.

## 1. Confirmar que o volume está auditável

```bash
python -m ferramentas.validar NN
python -m pytest exemplos/<vol> -q
```

Gate 1 ou gate 2 vermelho: **pare aqui.** Reporte as violações, mantenha o `status` em
`RASCUNHO` e devolva o volume para `/novo-volume`. Não despache o auditor — auditoria de
volume inválido é desperdício de passe.

## 2. Despachar o subagente `auditor-fable`

Chame o subagente `auditor-fable` (modelo Fable 5, definido em
`.claude/agents/auditor-fable.md`). O prompt do despacho tem de conter, no mínimo:

- o id e o nome do volume (`NN-NOME`) e o `tipo` lido do `_VOLUME.yml`;
- a lista dos arquivos de seção a auditar;
- os volumes em `depende_de`, para ele medir coerência técnica contra eles;
- a ordem explícita de **rodar os gates e os testes dos exemplos** em vez de acreditar nas
  afirmações do volume;
- a lembrança de que ele **não edita o volume** — só relata;
- o formato de saída obrigatório, incluindo a linha `media: N.N`.

**Um volume por despacho.** Auditar dois volumes no mesmo passe mistura os contextos e
produz nota média de coisas diferentes.

## 3. Gravar o relatório

Grave a saída do auditor **literalmente** em:

```
auditorias/VOL-NN-auditoria-AAAA-MM-DD.md
```

O nome do arquivo é contrato: `status.py::nota_da_ultima_auditoria` faz
`glob("VOL-{vol_id}-auditoria-*.md")` e pega o **último em ordem alfabética** — que com data
ISO é o mais recente. Data fora do padrão ISO quebra essa ordenação silenciosamente.

Antes de considerar gravado, confirme que a nota é legível pela máquina:

```bash
python -c "from pathlib import Path; from ferramentas.status import nota_da_ultima_auditoria; print(nota_da_ultima_auditoria(Path('.'), 'NN'))"
```

Saída `None` significa que a linha `media:` não casou o regex
`^\s*media:\s*([0-9]+(?:[.,][0-9]+)?)\s*$`. Causas usuais: a linha está em negrito, dentro
de tabela, com sufixo `/10`, com maiúscula ou com acento. **Corrija o formato da linha — não
o regex.** Se o auditor não emitiu a linha, devolva o relatório para ele; não a escreva você
mesmo, porque a média é dele.

## 4. Aplicar o critério da Definição de PRONTO, item 3

Aprovado **se e somente se**:

- `media` ≥ **8,0**; **e**
- **nenhuma seção com nota abaixo de 6**.

Uma seção com 5 reprova o volume mesmo com média 9,2. Confira as duas condições lendo a
tabela de notas por seção do relatório — a linha `media:` sozinha não decide.

## 5. Rodar o gate 3

```bash
python -m ferramentas.validar --cross-refs
```

`PRONTO` exige os **três** gates verdes, não só os dois do passo 1.

## 6. Atualizar o `status`

| Situação | `status` no `_VOLUME.yml` e nas seções |
|---|---|
| aprovado (média ≥ 8,0, nenhuma seção < 6) **e** gates 1, 2 e 3 em exit 0 | `PRONTO` |
| média < 8,0 **ou** alguma seção < 6 | `REQUER_REVISAO` |
| qualquer gate vermelho | `RASCUNHO`, com as violações reportadas |

Grave o mesmo `status` no `_VOLUME.yml` **e** no front-matter de todas as seções, e atualize
`atualizado_em` nas seções que você tocou. **Nunca grave `PRONTO` com gate vermelho** — nem
"só o link morto", nem "corrijo depois". Não arredonde 7,95 para 8,0.

Reprovado: registre no `CHANGELOG.md`, aplique o feedback nas seções apontadas (isso é
trabalho de criador, não de auditor) e **repita o ciclo do passo 1**. O relatório antigo
permanece em `auditorias/` — histórico de auditoria não se apaga; a próxima passada grava um
arquivo novo com a data nova.

## 7. Registrar e reportar

- `CHANGELOG.md`: entrada no topo, sob `## AAAA-MM-DD`, com o volume, a média, o veredicto, o
  caminho do relatório e o `status` gravado.
- Na resposta: a média, as notas por seção abaixo de 8, os problemas apontados, o caminho do
  relatório, **a saída colada** dos três gates e o `status` final com a razão.

Se você não rodou um gate, diga que não rodou. "Deve passar" não é resultado.
