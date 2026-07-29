---
name: novo-volume
description: Produz um volume do acervo AI-ENGINEERING-OS de ponta a ponta — resolve o tipo pelo contrato, lê os pré-requisitos, escreve as seções aplicáveis, cria os exemplos executáveis com teste, roda os gates 1 e 2, grava o status honesto e registra no CHANGELOG. Use quando o pedido for `/novo-volume N nome`, "escrever o volume NN", "produzir o volume de MEMORY" ou equivalente.
---

# `/novo-volume N nome`

Procedimento. Não é sugestão: cada passo tem saída verificável, e nenhum passo é pulado
porque "provavelmente está ok".

**Rode tudo de dentro de `AI-ENGINEERING-OS/`.** Os imports `ferramentas.*` dependem disso.
Datas em ISO `YYYY-MM-DD`.

## 1. Resolver o volume no contrato

1. Leia `00-INTRODUCAO/contrato.json`. Ele é a **única fonte de verdade legível por
   máquina**: seções, tipos, status válidos, limiares de palavras, marcadores proibidos,
   diagramas obrigatórios e os 42 volumes.
2. Ache a entrada do volume em `volumes["NN"]` — id é **string de 2 dígitos** (`"07"`).
   Confirme que o `nome` que o usuário passou é o `nome` declarado. Se divergir, **pare e
   pergunte**: renomear volume é mudança de contrato, não de conteúdo.
3. Leia o `tipo` (`ENGINE`, `ARQUITETURA`, `PROCESSO`, `BIBLIOTECA`, `GOVERNANCA`) e resolva
   as seções aplicáveis e os diagramas obrigatórios:

   ```bash
   python -c "from pathlib import Path; from ferramentas.contrato import carregar; ct=carregar(Path('.')); m=ct.volume('NN'); print(m); print(ct.secoes_de(m['tipo'])); print(ct.diagramas_de(m['tipo']))"
   ```

   Não deduza a lista de seções de memória nem copie de outro volume: `BIBLIOTECA` troca
   `04-Arquitetura` e `05-Diagramas` por `04-Catalogo`, e `PROCESSO` dispensa `08-Modelos`.

## 2. Ler o contexto antes de escrever uma linha

1. `00-INTRODUCAO/Convencoes.md` — as convenções em forma humana, incluindo a Definição de
   PRONTO e a tabela de "pergunta que cada seção responde". Escrever seção sem saber que
   pergunta ela responde é como se produz enchimento.
2. `CHANGELOG.md` — o que já foi decidido. Não reabra decisão registrada como se fosse nova.
3. Os volumes listados em `depende_de` no `_VOLUME.yml` do volume. **`depende_de` é
   pré-requisito de leitura**, e o vocabulário deles manda: se o volume 01 chamou de
   "gate", este volume não chama de "checkpoint".
4. `00-INTRODUCAO/Glossario.md`, se o volume introduzir termo novo.

## 3. Materializar a pasta, se ainda não existe

```bash
python -m ferramentas.scaffold
```

Idempotente: cria `NN-NOME/_VOLUME.yml` só onde falta e **nunca sobrescreve** um
`_VOLUME.yml` existente (ele acumula `status`, `depende_de` e `escopo` editados à mão).
Preencha `escopo` e `depende_de` à mão depois, se ainda estiverem vazios.

## 4. Escrever as seções

Um arquivo `NN-Nome.md` por seção resolvida no passo 1, cada um com o front-matter completo:

```yaml
---
volume: "NN"
volume_nome: <NOME>
tipo: <TIPO>
secao: <NN-Nome>
status: RASCUNHO
atualizado_em: 2026-07-29
---
```

- `secao` tem de ser **idêntico ao nome do arquivo sem `.md`** — esquecer de trocar esse
  campo ao copiar um arquivo é o erro mais comum do acervo.
- `volume`, `volume_nome` e `tipo` têm de coincidir com o `_VOLUME.yml`.
- `status` só aceita `RASCUNHO`, `REQUER_REVISAO`, `PRONTO`. `PENDENTE` **não é gravável**.

## 5. Criar os exemplos executáveis

Todo código citado por uma seção existe como arquivo e tem teste. A citação é um comentário
HTML na linha anterior ao bloco:

```markdown
<!-- exemplo: exemplos/<vol>/nome_do_modulo.py -->
```

O validador exige então `exemplos/<vol>/nome_do_modulo.py` **e**
`exemplos/<vol>/tests/test_nome_do_modulo.py` — convenção rígida, sem configuração. Use
`<vol>` em minúsculas com hífen (`07-prompt-engine`). Crie `exemplos/<vol>/tests/__init__.py`.

## 6. Gate 1 — estrutural

```bash
python -m ferramentas.validar NN
```

Exit 0 e "sem violacoes" é o único resultado que conta. Cada violação sai como
`arquivo:linha: [regra] mensagem`; `linha` igual a 0 significa "o arquivo como um todo".
Corrija o conteúdo, **nunca a regra nem o teste**.

## 7. Gate 2 — executável

```bash
python -m pytest exemplos/<vol> -q
```

Código citado que não roda é afirmação não verificada, e este acervo não publica afirmação
não verificada.

## 8. Gravar o status conforme o resultado — o passo que não se negocia

| Resultado dos gates 1 e 2 | `status` a gravar no `_VOLUME.yml` e nas seções |
|---|---|
| ambos exit 0 | `RASCUNHO` — pronto para `/auditar` |
| qualquer um vermelho | **`RASCUNHO`**, e reporte as violações na resposta |

**Nunca grave `PRONTO` aqui.** `PRONTO` exige os quatro critérios da Definição de PRONTO, e
o terceiro é a auditoria — que ainda não aconteceu. `PRONTO` só é gravado no fim de
`/auditar`, com média ≥ 8,0, nenhuma seção < 6 e os três gates verdes.

Com gate vermelho: grave `RASCUNHO`, cole a saída do gate na resposta e liste o que falta.
Não escreva "deve passar depois de um ajuste". Status que mente destrói o valor de todos os
outros status do acervo.

## 9. Registrar no `CHANGELOG.md`

Entrada nova no topo, sob o cabeçalho da data de hoje (`## AAAA-MM-DD`), dizendo: o volume,
o tipo, quantas seções foram escritas, quais exemplos foram criados, o resultado exato de
cada gate e o `status` gravado. Se algo ficou pendente, aponte para `16-Roadmap` do volume ou
para `frameworks/_backlog.md` — **nunca** com `TODO`/`TBD`/`FIXME` na prosa.

## 10. Reportar

Na resposta: seções escritas, exemplos criados, **a saída colada** dos dois gates, o status
gravado e a razão dele, e o que ficou pendente. "Rodou e passou" sem a saída não é resultado.

---

## Armadilhas conhecidas

- **A contagem de palavras ignora blocos de código.** `palavras_de_prosa` pula tudo entre
  cercas e as linhas de cabeçalho. Colar 200 linhas de Python **não** satisfaz o mínimo — a
  seção reprova por `substancia-curta`. Mínimo global 200 palavras de prosa; `15-Checklist`
  e `16-Roadmap` 120, `17-Conclusao` 150, `18-Referencias-Cruzadas` 80.
- **Todo bloco Mermaid precisa de parágrafo descritivo imediatamente depois.** E tem de ser
  prosa: linha começando com `#`, com nova cerca, com `|`, com `-`, com `*` ou com
  comentário HTML **não conta** — reprova em `mermaid-sem-descricao`. O tipo do diagrama
  também tem de ser reconhecido (`flowchart`, `sequenceDiagram`, `stateDiagram-v2`,
  `erDiagram`, `C4Context`, `mindmap`); tipo com erro de digitação rende página em branco no
  site exportado.
- **`depende_de` usa ids de 2 dígitos** (`["01", "02"]`) e significa **pré-requisito de
  leitura — acíclico por definição**, não "assunto vizinho". Vizinhança bidirecional mora em
  `18-Referencias-Cruzadas.md` e não entra no grafo; se entrasse, 07 e 28 formariam um ciclo
  falso e o gate 3 reprovaria por nada.
- **Não linke para arquivo de volume que ainda não existe.** Todo link Markdown relativo tem
  de resolver no disco, senão `link-morto` reprova. Volume ainda pendente só tem
  `_VOLUME.yml`: linke para `../NN-NOME/_VOLUME.yml`, não para um `01-Introducao.md` que
  ninguém escreveu. Links `http://`, `https://`, `mailto:` e âncoras internas são ignorados
  pelo validador — ele não faz rede.
- **Marcador proibido escapa só dentro de code span.** `` `TODO` `` entre acentos graves é
  permitido (é o que deixa `10-Anti-Patterns` falar do assunto); `TODO:` na prosa reprova.
- **Nunca invente framework, número ou fonte.** Nome de framework sem definição vai para
  `frameworks/_backlog.md` com a frase padronizada de que não foi inventado. Número sem
  fonte não entra. Referência que você não pode verificar não é citada — lista curta é
  melhor que atribuição errada.
- **Volume perecível** (`perecivel: true`: 26, 27, 34) é deliberadamente fino e **não fixa
  número que expira** — preço por token, janela de contexto, nome de modelo. Descreve o
  método e aponta para a fonte viva.
