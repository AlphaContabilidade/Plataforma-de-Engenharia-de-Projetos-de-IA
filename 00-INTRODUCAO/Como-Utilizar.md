# Como utilizar

Tudo aqui roda **de dentro de `AI-ENGINEERING-OS/`**. Os imports das ferramentas são
`ferramentas.*`, e eles só resolvem com esta pasta como diretório de trabalho. Rodar de
fora dá `ModuleNotFoundError` e não é bug — é o caminho errado.

```bash
cd AI-ENGINEERING-OS
```

## Os cinco comandos

| Comando | Invocação | O que acontece |
|---|---|---|
| `/novo-volume` | `/novo-volume 13 RAG` | lê o contrato e resolve o tipo do volume 13; lê `Convencoes.md`, o `CHANGELOG.md` e os volumes listados em `depende_de`; gera as seções aplicáveis ao tipo; cria os exemplos `.py` com teste ao lado; roda o gate 1 e o gate 2; grava `RASCUNHO` se algum reprovou, com a lista de violações; registra a passada no `CHANGELOG.md` |
| `/auditar` | `/auditar 13` | dispara o subagente `auditor-fable` sobre o volume 13; recebe nota de 0 a 10 por seção, problemas e sugestões; grava `auditorias/VOL-13-auditoria-2026-07-29.md` com uma linha `media:`; atualiza o `status` no `_VOLUME.yml` conforme a média |
| `/status` | `/status` | tabela dos 42 volumes: id, nome, tipo, status, seções presentes sobre esperadas, nota da última auditoria e marca de perecível, mais o resumo por status |
| `/cross-reference` | `/cross-reference` | roda o gate 3 determinístico (`depende_de` válido e acíclico) e depois um passe semântico procurando afirmações contraditórias entre volumes |
| `/exportar` | `/exportar` | gera `mkdocs.yml` a partir do que existe em disco e valida o build quando `mkdocs` está instalado; avisa explicitamente quando não está |

As skills não têm regra própria: cada uma chama as ferramentas em `ferramentas/`. Isso é
deliberado — regra duplicada entre skill e código divergiria em uma semana.

## O ciclo de produção de um volume

Sete passos, na ordem. Pular passo é como o acervo passa a mentir sobre o próprio estado.

1. **Materializar.** `python -m ferramentas.scaffold` cria `NN-NOME/` com `_VOLUME.yml`
   preenchido a partir do contrato (`status: RASCUNHO`, `perecivel` conforme o contrato,
   `depende_de: []`). A ferramenta é idempotente e **nunca sobrescreve** um `_VOLUME.yml`
   existente, porque esse arquivo acumula estado editado à mão.
2. **Declarar as dependências.** Edite `depende_de` no `_VOLUME.yml` com os ids de dois
   dígitos dos volumes que são **pré-requisito de leitura**. Vizinhança bidirecional não
   entra aqui — vai em prosa em `18-Referencias-Cruzadas.md`, senão o grafo ganha ciclo
   falso.
3. **Escrever as seções.** Uma por arquivo, com o front-matter completo dos seis campos, na
   lista que `Contrato.secoes_de(tipo)` devolve para o tipo do volume. Diagrama Mermaid
   sempre seguido de parágrafo descritivo; código sempre citado por
   `<!-- exemplo: exemplos/... -->`.
4. **Escrever os exemplos.** Cada `.py` citado precisa existir e precisa ter
   `tests/test_<arquivo>.py` ao lado. Teste primeiro, implementação depois — é assim que se
   descobre que a interface descrita em `08-Modelos` era inviável antes de escrever a
   seção inteira sobre ela.
5. **Rodar os gates 1 e 2.** Reprovou, corrija e rode de novo. O status continua
   `RASCUNHO` até os dois ficarem verdes.
6. **Auditar.** `/auditar NN`. Média abaixo de 8,0, ou qualquer seção abaixo de 6, grava
   `REQUER_REVISAO`; incorpore o feedback e reaudite.
7. **Fechar.** Gate 3 verde, auditoria aprovada e entrada no `CHANGELOG.md` com a data.
   Só então `status: PRONTO`.

## Rodando os gates na mão

Nada depende de skill. Os mesmos gates são módulos Python invocáveis diretamente, e é assim
que se confere um resultado sem confiar no relato de ninguém.

```bash
# Gate 1 — estrutural, um volume
python -m ferramentas.validar 07

# Gate 1 — todo o acervo materializado
python -m ferramentas.validar --tudo

# Gate 2 — os exemplos do volume
python -m pytest exemplos/07-prompt-engine -q

# Gate 3 — dependencias declaradas e grafo aciclico
python -m ferramentas.validar --cross-refs

# Estado do acervo
python -m ferramentas.status

# Materializar volumes declarados no contrato (idempotente)
python -m ferramentas.scaffold

# Gerar o site
python -m ferramentas.exportar

# A propria maquina: os testes das ferramentas
python -m pytest ferramentas/tests -q
```

Códigos de saída de `validar.py`: `0` sem violação, `1` com violação, `2` em erro de uso ou
de contrato. Cada violação sai no formato `arquivo:linha: [regra] mensagem`, com `linha`
igual a zero quando o problema é do arquivo como um todo. O nome entre colchetes é o nome da
regra em `ferramentas/regras.py` — use esse nome para discutir a violação, em vez de
descrever a impressão que o texto causou.

## Quando o gate reprova e você acha que ele está errado

Acontece, e o procedimento é fixo: **o teste não cede.** Se a regra está errada, mude
`contrato.json`, ajuste a tabela correspondente em [Convencoes.md](Convencoes.md), rode
`python -m pytest ferramentas/tests -q` e veja o
`test_convencoes_nao_derivou` confirmar que os dois lados voltaram a concordar. Ajustar o
teste para o conteúdo passar transforma o gate em enfeite, e a partir daí o status de todo o
acervo perde valor.

Detalhe prático que economiza uma hora: `substancia-curta` conta **palavras de prosa**.
Blocos de código cercados e linhas de cabeçalho não contam. Uma seção que parece longa e
reprova por curta quase sempre é uma seção de código com uma frase de introdução.
