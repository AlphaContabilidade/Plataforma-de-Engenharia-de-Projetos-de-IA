# Convenções — o contrato da plataforma

Este é o arquivo mais importante do acervo. Ele descreve, em forma legível por humanos,
exatamente o que `00-INTRODUCAO/contrato.json` descreve em forma legível por máquina.
Quando os dois divergem, o teste `ferramentas/tests/test_contrato.py::test_convencoes_nao_derivou`
reprova a suíte — de propósito. Documentação que envelhece sozinha não é contrato, é folclore.

Regra de precedência: **`contrato.json` vence.** Se você mudar uma regra, mude o JSON
primeiro e ajuste este arquivo depois; o teste vai te obrigar a fazer as duas coisas.

---

## 1. As 18 seções e o que cada uma responde

Todo volume é uma pasta `NN-NOME/` com um `_VOLUME.yml` e um arquivo Markdown por seção.
Os nomes de arquivo são fixos (`04-Arquitetura.md`), porque o validador procura por eles
e `status.py` conta quantos existem. As 18 seções da base, na ordem canônica:

| Seção | Pergunta que ela responde |
|---|---|
| `01-Introducao` | Que problema este volume resolve, e por que ele merece existir separado dos outros? |
| `02-Objetivos` | O que o leitor consegue fazer depois de ler — em verbos verificáveis, não em adjetivos. |
| `03-Escopo` | O que está dentro, o que está fora, e qual volume cobre o que ficou fora. |
| `04-Arquitetura` | Como as partes se encaixam: contexto, containers, componentes (nível C4). |
| `05-Diagramas` | As visões formais: sequência, máquina de estados, entidade-relacionamento, mapa mental. |
| `06-Fluxogramas` | O caminho de execução passo a passo, incluindo os ramos de erro. |
| `07-Regras` | As invariantes: o que nunca pode acontecer, e o que sempre tem de acontecer. |
| `08-Modelos` | Os contratos de dados e as interfaces — tipos, campos, assinaturas. |
| `09-Boas-Praticas` | O que fazer, com a razão explícita. Prática sem razão é superstição. |
| `10-Anti-Patterns` | O que não fazer, com o custo concreto de fazer errado. |
| `11-Implementacao` | Como construir de fato, apontando para código executável. |
| `12-Exemplos` | Casos completos, cada um citando um arquivo real de `exemplos/`. |
| `13-Testes` | Como se prova que a implementação está correta, e o que os testes cobrem. |
| `14-Metricas` | O que medir em produção, com unidade e fonte do número. |
| `15-Checklist` | A lista operacional de conferência antes de considerar o trabalho feito. |
| `16-Roadmap` | O que este volume ainda não cobre e em que ordem pretende cobrir. |
| `17-Conclusao` | O que se aprendeu, e o que o leitor deve levar embora. |
| `18-Referencias-Cruzadas` | Links resolvíveis para os volumes vizinhos e para fontes externas. |

Duas seções trocam de nome em um tipo específico: a `BIBLIOTECA` não tem arquitetura
própria e ganha `04-Catalogo` no lugar de `04-Arquitetura` e `05-Diagramas`. Isso está
declarado em `contrato.json` como `opcionais` e `extras`, e é resolvido por
`Contrato.secoes_de(tipo)`.

---

## 2. Tipos de volume

O tipo de um volume determina quais das 18 seções são obrigatórias. Foi introduzido para
resolver um problema real: exigir "máquina de estados" de um volume de templates força
enchimento, e enchimento contradiz a regra de não gerar conteúdo superficial. Em vez de
relaxar a regra, relaxamos a lista de seções — por tipo, de forma explícita e auditável.

A tabela abaixo é a **projeção humana de `contrato.json`**. A segunda célula lista os ids
de volume de cada tipo, e é ela que `test_convencoes_nao_derivou` compara com o JSON.
Nenhum número entra nessa célula que não seja um id de volume.

| Tipo | Volumes | Ajuste sobre as dezoito seções da base |
|---|---|---|
| `ENGINE` | 07, 08, 09, 10, 11, 12, 13, 14, 15, 26, 27, 28, 29, 37, 41, 42 | todas as seções da base são obrigatórias; exige diagramas `C4Context`, `sequenceDiagram` e `stateDiagram-v2` |
| `ARQUITETURA` | 02, 06, 16, 19, 20, 22, 23, 24, 25 | todas as seções da base; exige `C4Context` e `sequenceDiagram`, sem máquina de estados obrigatória |
| `PROCESSO` | 03, 04, 05, 18, 31, 32, 33, 34, 38, 39 | `08-Modelos` é opcional (o fluxo importa mais que o modelo de dados); exige `flowchart` |
| `BIBLIOTECA` | 36, 40 | sem `04-Arquitetura` e sem `05-Diagramas`; ganha `04-Catalogo`; nenhum diagrama obrigatório |
| `GOVERNANCA` | 01, 17, 21, 30, 35 | todas as seções da base; exige `flowchart` e uma matriz de controles em `07-Regras` |

Quem implementa: `Contrato.secoes_de` e `Contrato.diagramas_de` em
`ferramentas/contrato.py`. Um `tipo` fora dessa lista faz `validar.py` emitir a regra
`volume-tipo` com os tipos aceitos na mensagem; um `tipo` que contradiz o contrato emite
a mesma regra apontando a divergência.

---

## 3. Front-matter obrigatório

Todo arquivo de seção começa com um bloco delimitado por `---`. A gramática aceita é um
subconjunto deliberadamente restrito de YAML: escalares, booleanos, inteiros e listas em
linha. A restrição é o que permite validar sem dependência externa e apontar o erro na
linha exata.

```yaml
---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 04-Arquitetura
status: RASCUNHO
atualizado_em: 2026-07-29
---
```

Os seis campos acima são obrigatórios (`campos_frontmatter` no contrato). Detalhes que
custam tempo quando ignorados:

- **`volume` é sempre string de dois dígitos, entre aspas.** `"07"` e `07` divergiriam no
  resto da máquina; o parser mantém como string qualquer número com zero à esquerda, e as
  aspas tornam a intenção visível para quem lê.
- **`secao` tem de ser idêntico ao nome do arquivo sem `.md`.** Copiar um arquivo e
  esquecer de trocar esse campo é o erro mais comum.
- **`volume`, `volume_nome` e `tipo` têm de coincidir com o `_VOLUME.yml` da pasta.**
- **`status` só aceita três valores:** `RASCUNHO`, `REQUER_REVISAO`, `PRONTO`. `PENDENTE`
  não é gravável — é estado derivado, calculado por `status.py` quando a pasta do volume
  não existe.
- **`atualizado_em` em ISO `YYYY-MM-DD`.**

O `_VOLUME.yml` da pasta usa a mesma gramática, sem os delimitadores, e carrega `volume`,
`nome`, `tipo`, `status`, `perecivel`, `depende_de` e `escopo`. `depende_de` usa **ids de
dois dígitos** (`["01", "02"]`) e significa **pré-requisito de leitura** — uma relação
acíclica. Vizinhança bidirecional entre volumes ("assunto próximo") mora em
`18-Referencias-Cruzadas.md` e não entra no grafo, senão 07 e 28 formariam um ciclo falso.

Quem implementa: `ferramentas/frontmatter.py` (gramática) e as regras `frontmatter`,
`frontmatter-campo`, `frontmatter-status` e `frontmatter-coerencia` em
`ferramentas/regras.py`. `volume-yml` e `volume-tipo` cobrem o `_VOLUME.yml`;
`depende-de-inexistente` e `depende-de-ciclo` cobrem o grafo de dependências em
`validar.py --cross-refs`.

---

## 4. Definição de PRONTO

Contagem de páginas não mede qualidade — mede volume de texto, e otimizar por volume de
texto produz enchimento. Um volume é `PRONTO` quando, e somente quando, os quatro
critérios abaixo estão satisfeitos ao mesmo tempo:

1. **`python -m ferramentas.validar NN` retorna exit 0** para o volume.
2. **`python -m pytest exemplos/<vol>` passa** nos exemplos citados pelo volume.
3. **A auditoria registra média maior ou igual a 8,0 e nenhuma seção abaixo de 6.** O
   relatório fica em `auditorias/VOL-NN-auditoria-YYYY-MM-DD.md`, com uma linha
   `media: <nota>` que `status.py` lê.
4. **O resultado está registrado no `CHANGELOG.md`** com a data do dia.

Falta um dos quatro, o volume não é `PRONTO`. Gravar `PRONTO` com qualquer gate vermelho é
proibido — não é uma questão de estilo, é a única coisa que impede o acervo de mentir
sobre o próprio estado. Auditoria com média abaixo de 8,0 grava `REQUER_REVISAO`; gate
estrutural vermelho mantém `RASCUNHO` e reporta as violações.

---

## 5. Regra de diagrama

Diagramas são sempre Mermaid, em bloco cercado com a linguagem declarada, e **todo bloco
Mermaid é seguido imediatamente por um parágrafo de prosa descrevendo o que o diagrama
mostra**. A razão é dupla: um diagrama sem legenda é ilegível para quem chega depois, e é
irrecuperável para leitor de tela ou para busca textual.

O parágrafo tem de ser prosa. Uma linha que começa com `#`, com nova cerca, com `|`, com
`-`, com `*` ou com comentário HTML não conta como descrição — é outra estrutura, não
explicação.

O tipo do diagrama tem de ser um dos reconhecidos (`flowchart`, `sequenceDiagram`,
`stateDiagram-v2`, `erDiagram`, `C4Context`, `mindmap`, entre outros). Tipo desconhecido
costuma ser erro de digitação, e erro de digitação em Mermaid rende uma página em branco
no site exportado.

Quem implementa: `mermaid-nao-fechado`, `mermaid-vazio`, `mermaid-tipo` e
`mermaid-sem-descricao` em `regras.checar_mermaid`; a exigência por tipo de volume vem de
`diagrama-obrigatorio` em `regras.checar_diagramas_obrigatorios`.

---

## 6. Regra de código

Código citado por um volume tem de existir como arquivo e tem de ter teste. Bloco de
código em Markdown que ninguém executa é afirmação não verificada, e este acervo não
publica afirmação não verificada.

A citação usa um comentário HTML, na linha anterior ao bloco:

```markdown
<!-- exemplo: exemplos/07-prompt-engine/prompt_template.py -->
```

O validador então exige duas coisas: que `exemplos/07-prompt-engine/prompt_template.py`
exista, e que exista `exemplos/07-prompt-engine/tests/test_prompt_template.py`. A
convenção de nome do teste é rígida (`tests/test_<arquivo>.py`) porque convenção rígida
dispensa configuração.

Links Markdown relativos também são verificados: todo link para caminho relativo tem de
resolver no disco. Links `http://`, `https://`, `mailto:` e âncoras internas são
ignorados — o validador não faz rede.

Quem implementa: `exemplo-inexistente` e `exemplo-sem-teste` em `regras.checar_exemplos`;
`link-morto` em `regras.checar_links`.

---

## 7. Marcadores proibidos e o escape por code span

Estes marcadores não podem aparecer na prosa de nenhuma seção: `TBD`, `TODO`, `PENDENTE`,
`FIXME`, `XXX` e `preencher aqui`. Um marcador de trabalho inacabado dentro de um volume
significa que o volume não está pronto e está se apresentando como se estivesse. Pendência
de verdade vai para `frameworks/_backlog.md` ou para a seção `16-Roadmap` do volume, com
frase completa dizendo o que falta e por quê.

Existe um escape legítimo, e um só: **mencionar o marcador dentro de um code span**, ou
seja, entre acentos graves. É o que permite a seção `10-Anti-Patterns` escrever que
"deixar TODO no volume é anti-pattern" sem se autoincriminar. Blocos de código cercados
inteiros também ficam fora da varredura.

Quem implementa: `marcador-proibido` em `regras.sem_marcadores`, que remove code spans da
linha antes de procurar o marcador.

---

## 8. Substância mínima

Cada seção tem um mínimo de palavras **de prosa**. Código não conta: `palavras_de_prosa`
ignora tudo entre cercas, e ignora linhas de cabeçalho. Sem isso, colar duzentas linhas de
Python satisfaria o limiar sem entregar uma frase de explicação.

O mínimo global é 200 palavras. Quatro seções têm mínimo próprio, porque são naturalmente
mais curtas e forçá-las a 200 palavras produziria enchimento: `15-Checklist` (120),
`16-Roadmap` (120), `17-Conclusao` (150) e `18-Referencias-Cruzadas` (80). Os números vivem
em `min_palavras_por_secao`, no contrato.

O limiar é piso, não meta. Ele não prova qualidade — só reprova vazio. A qualidade é
julgada pela auditoria, no critério 3 da Definição de PRONTO.

Quem implementa: `substancia-curta` em `regras.checar_substancia`, com o mínimo resolvido
por `Contrato.minimo_de(secao)`.

---

## 9. Regra de volume perecível

Três volumes tratam de assunto que muda em semanas: `26-AI-MODELS`, `27-LLM-ROUTER` e
`34-COST-OPTIMIZATION`. Eles carregam `perecivel: true` no `_VOLUME.yml`, e `status.py`
mostra a marca na coluna correspondente.

Volume perecível segue duas regras adicionais:

- **Não fixa números que expiram.** Preço por milhão de tokens, janela de contexto, limite
  de requisição por minuto e nome de modelo específico não entram como valor fixo no
  corpo. O volume descreve o **método** de decidir — como comparar custo por tarefa, como
  medir deriva entre versões — e aponta para a fonte viva onde o número atual é consultado.
- **É deliberadamente fino.** Um volume perecível longo é dívida: cada parágrafo é uma
  afirmação que vai envelhecer e que alguém vai ter de revisar. Menos texto, mais ponteiro.

Um número concreto só entra com data e fonte explícitas na mesma frase, e sempre como
ilustração de método, nunca como referência a ser reutilizada.

---

## 10. Onde cada regra é aplicada

O validador roda por volume e aplica, arquivo por arquivo, na ordem: front-matter,
substância, marcadores, Mermaid, exemplos, links; depois checa os diagramas obrigatórios
contra o volume inteiro. Cada violação sai no formato `arquivo:linha: [regra] mensagem`, e
`linha` igual a zero significa "o arquivo como um todo".

O catálogo completo de nomes de regra vive em `ferramentas/regras.py`. Se você precisa
argumentar sobre uma regra, cite o nome dela — é assim que a discussão fica ancorada no
que a máquina de fato verifica, e não em impressão sobre o texto.
