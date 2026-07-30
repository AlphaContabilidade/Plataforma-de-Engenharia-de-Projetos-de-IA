# Como contribuir

Regra de ouro: **o gate é o revisor.** Antes de pedir revisão humana, rode os três gates e
cole a saída. Contribuição que não passa nos gates não é discutida por mérito de conteúdo —
ela é devolvida com a lista de violações, e a lista é objetiva.

Tudo roda de dentro de `AI-ENGINEERING-OS/`.

## Propor um volume novo

Os 42 volumes já estão declarados em `00-INTRODUCAO/contrato.json`. "Volume novo" quase sempre
significa **escrever um volume declarado e ainda pendente**, não acrescentar o 43º.

### Escrever um volume declarado

1. **Confirme o tipo.** `python -m ferramentas.status` mostra tipo e quantidade de seções
   esperadas. O tipo determina quais seções são obrigatórias; não invente seção fora da lista
   e não pule seção da lista.
2. **Materialize.** `python -m ferramentas.scaffold` cria a pasta e o `_VOLUME.yml` se ainda
   não existirem. A ferramenta é idempotente e nunca sobrescreve um `_VOLUME.yml` existente.
3. **Declare `depende_de`.** Ids de dois dígitos dos volumes que são **pré-requisito de
   leitura**, e só esses. Vizinhança bidirecional vai em prosa em `18-Referencias-Cruzadas.md`
   — colocá-la em `depende_de` cria ciclo e o gate 3 reprova.
4. **Escreva as seções**, uma por arquivo, com os seis campos de front-matter completos e
   coerentes com o `_VOLUME.yml`.
5. **Escreva os exemplos antes da seção que os descreve.** Teste primeiro. É assim que se
   descobre que a interface prometida em `08-Modelos` era inviável, em vez de descobrir depois
   de escrever a seção inteira sobre ela.
6. **Rode os gates 1 e 2**, corrija, repita até verde.
7. **Peça a auditoria** (`/auditar NN`) e incorpore o feedback.
8. **Feche**: gate 3 verde e entrada no `CHANGELOG.md` com a data. Só então `PRONTO`.

### Acrescentar um volume à lista

Exige mudar o contrato, e a ordem é fixa:

1. Acrescente a entrada em `contrato.json` (`nome`, `tipo`, `perecivel`).
2. Ajuste a célula de volumes do tipo correspondente em
   [00-INTRODUCAO/Convencoes.md](00-INTRODUCAO/Convencoes.md).
3. Rode `python -m pytest ferramentas/tests -q`. O teste `test_convencoes_nao_derivou` confirma
   que os dois lados voltaram a concordar; `test_os_42_volumes_estao_declarados` vai reprovar e
   precisa ser atualizado junto com o contrato, porque ele afirma um fato sobre o contrato.
4. Registre a mudança no `CHANGELOG.md` e no `ROADMAP.md`.

## Mudar uma regra

**JSON primeiro, prosa depois, teste em seguida.** `contrato.json` é a fonte única; mudar
apenas `Convencoes.md` deixa o acervo com duas verdades, e o teste existe justamente para não
permitir isso.

Se a regra é nova e não cabe no contrato (uma verificação estrutural inédita), ela entra como
função pura em `ferramentas/regras.py`, com nome estável de regra, e ganha teste com fixture
deliberadamente ruim em `ferramentas/tests/` — a fixture tem de reprovar antes de a regra
existir. Regra sem teste que a exercite não é regra; é intenção.

## Como o gate reprova

Saída no formato `arquivo:linha: [regra] mensagem`, com `linha` igual a zero quando o problema
é do arquivo como um todo. Códigos de saída de `validar.py`: `0` limpo, `1` com violação, `2`
erro de uso ou de contrato.

| Regra | Reprova quando |
|---|---|
| `frontmatter` | o bloco `---` está ausente ou malformado |
| `frontmatter-campo` | falta um dos seis campos obrigatórios, ou ele está vazio |
| `frontmatter-status` | `status` fora de `RASCUNHO`, `REQUER_REVISAO`, `PRONTO` |
| `frontmatter-coerencia` | `secao` diferente do nome do arquivo, ou `volume`/`volume_nome`/`tipo` divergentes do `_VOLUME.yml` |
| `volume-yml`, `volume-tipo` | `_VOLUME.yml` ausente, incompleto, ou com tipo inválido ou divergente do contrato |
| `secao-ausente` | falta uma seção obrigatória para o tipo do volume |
| `substancia-curta` | prosa abaixo do mínimo da seção — **código e cabeçalho não contam** |
| `marcador-proibido` | `TBD`, `TODO`, `PENDENTE`, `FIXME`, `XXX` ou `preencher aqui` na prosa |
| `mermaid-sem-descricao` | bloco Mermaid sem parágrafo de prosa imediatamente depois |
| `mermaid-nao-fechado`, `mermaid-vazio`, `mermaid-tipo` | cerca sem fechamento, bloco vazio, ou tipo de diagrama desconhecido |
| `diagrama-obrigatorio` | falta no volume um diagrama exigido pelo seu tipo |
| `exemplo-inexistente` | `<!-- exemplo: ... -->` aponta para arquivo que não existe |
| `exemplo-sem-teste` | o exemplo existe mas não há `tests/test_<arquivo>.py` ao lado |
| `link-morto` | link Markdown relativo que não resolve em disco |
| `depende-de-inexistente`, `depende-de-ciclo` | dependência para volume não declarado, ou ciclo no grafo |

Falso positivo aparente costuma ter explicação prosaica. Dois casos frequentes:
`substancia-curta` em seção que parece longa quase sempre é seção de código com uma frase de
introdução; `marcador-proibido` em texto que fala legitimamente sobre o marcador se resolve
colocando o marcador em code span, entre acentos graves — que é o escape previsto e o que
permite a seção `10-Anti-Patterns` existir.

## O que nunca fazer

1. **Nunca gravar `PRONTO` com gate vermelho.** Nem parcialmente, nem "corrijo em seguida".
   Status que mente destrói o valor de todos os outros status do acervo.
2. **Nunca ajustar o teste para o conteúdo passar.** O teste é o contrato; o conteúdo cede. Se
   a regra está errada, mude a regra pelo caminho descrito acima — e assuma a mudança no
   `CHANGELOG.md`.
3. **Nunca inventar framework, número ou fonte.** Nome sem definição vai para
   `frameworks/_backlog.md` com a declaração de que não foi inventado. Número sem fonte não
   entra. Paper, livro ou autor que você não pode verificar não é citado; atribuição errada é
   pior que ausência de atribuição. Se a lista de referências ficar curta, ela fica curta.
4. **Nunca afirmar sucesso sem ter olhado.** Cole a saída do gate. "Deve passar" não é
   resultado.
5. **Nunca deixar marcador de pendência na prosa.** Pendência tem três lugares próprios:
   `16-Roadmap` do volume, `ROADMAP.md` da plataforma, `frameworks/_backlog.md`.
6. **Nunca acrescentar dependência de terceiros às ferramentas.** `ferramentas/` usa apenas a
   biblioteca padrão. A restrição do front-matter a um subconjunto YAML existe exatamente para
   dispensar PyYAML e ainda apontar o erro na linha certa.
7. **Nunca tocar em nada fora de `AI-ENGINEERING-OS/`.** O diretório pai é outro projeto — a
   outro projeto, de assunto diferente. As únicas
   exceções combinadas são o spec e o plano em `docs/superpowers/`.
8. **Nunca publicar diagrama sem parágrafo descritivo.** Diagrama sem legenda é ilegível para
   quem chega depois e irrecuperável para leitor de tela e para busca textual.

## Antes de abrir a contribuição

```bash
cd AI-ENGINEERING-OS
python -m pytest ferramentas/tests -q
python -m ferramentas.validar --tudo
python -m ferramentas.validar --cross-refs
python -m pytest exemplos -q
```

As quatro saídas, coladas. É o mínimo para que a conversa seja sobre conteúdo.
