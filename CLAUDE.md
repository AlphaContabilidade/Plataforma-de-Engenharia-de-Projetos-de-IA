# CLAUDE.md — AI-ENGINEERING-OS

Contexto local **desta pasta**. Vale para qualquer agente trabalhando dentro de
`AI-ENGINEERING-OS/`.

## ⚠️ A raiz do repositório é outro projeto

O diretório pai (`C:\Users\Usuário\Desktop\CLAUDE\`) **não** é esta plataforma. É a
**rotina de conciliação Sicoob × Omie** do grupo Rezoluti: automação financeira que
escreve de verdade em sistema contábil, com dinheiro real do outro lado. Ela tem o seu
próprio `CLAUDE.md` na raiz, com regras de segurança próprias.

Consequências operacionais, sem exceção:

- **Nada fora de `AI-ENGINEERING-OS/` é criado, editado ou apagado** por trabalho desta
  plataforma. A única exceção combinada são o spec e o plano em `docs/`.
- **Não rode, não teste e não "conserte" nada da conciliação.** `scripts/`, `casos/`,
  `cloud_state/`, `tests/` da raiz e `omie_client.py` não são assunto daqui.
- O `CLAUDE.md` da raiz tem precedência absoluta sobre este arquivo em qualquer questão
  que toque a conciliação. Este arquivo só governa o conteúdo desta subpasta.
- Se uma tarefa parecer exigir mudança fora desta pasta, pare e pergunte. Provavelmente é
  contexto trocado.

## Missão

Construir e manter um acervo técnico de engenharia de IA em 42 volumes, cada um com 18
seções fixas, onde **a máquina de produção é o ativo — não a contagem de arquivos**. O
diferencial não é escrever muito: é que nada entra no acervo sem passar por porta de
qualidade executável. Um volume só se declara pronto quando um programa confirma que ele é.

## Modelo criador/auditor

A produção de qualquer volume tem dois papéis distintos, e eles não se misturam:

- **Criador (Opus 5).** Lê o contrato, os volumes dos quais o novo depende e o
  `CHANGELOG.md`; escreve as seções aplicáveis ao tipo; cria os exemplos `.py` com teste;
  roda os gates; grava o status que o resultado permitir.
- **Auditor (subagente `auditor-fable`, modelo Fable 5).** Recebe o volume já verde no gate
  estrutural e o julga por seção, de 0 a 10, com problemas e sugestões concretas. Grava
  `auditorias/VOL-NN-auditoria-YYYY-MM-DD.md`. O auditor **não edita o volume** — só relata.
- **Incorporação (Opus 5).** Aplica o feedback e roda o terceiro gate.

Quem escreve não se aprova. É por isso que o auditor é outro modelo, em outra sessão, com
outro contexto: revisar o próprio texto no mesmo contexto tende a confirmar o que já está
lá em vez de encontrar o que falta.

## `contrato.json` é a fonte única de verdade

`00-INTRODUCAO/contrato.json` define seções, tipos de volume, status válidos, limiares de
palavras, marcadores proibidos, diagramas obrigatórios e os 42 volumes. Toda ferramenta lê
esse arquivo; nenhuma tem regra duplicada em código.

`00-INTRODUCAO/Convencoes.md` é a **mesma informação em forma humana**, e não é opcional
mantê-la sincronizada: `ferramentas/tests/test_contrato.py::test_convencoes_nao_derivou`
compara a tabela de tipos do Markdown com o JSON e reprova a suíte se divergirem.

Ordem para mudar qualquer regra: **JSON primeiro, `Convencoes.md` depois, teste em
seguida.** Nunca ajuste o teste para acomodar a prosa.

## Os três gates, na ordem em que rodam

| Ordem | Gate | Comando | O que reprova |
|---|---|---|---|
| 1 | Estrutural | `python -m ferramentas.validar NN` | front-matter, seção ausente, substância curta, marcador proibido, Mermaid sem descrição, exemplo sem teste, link morto |
| 2 | Executável | `python -m pytest exemplos/<vol> -q` | código citado pelo volume que não roda ou não passa nos próprios testes |
| 3 | Referências cruzadas | `python -m ferramentas.validar --cross-refs` | `depende_de` apontando para volume inexistente, ciclo no grafo de pré-requisitos |

A auditoria do Fable entra **entre o gate 2 e o gate 3**: audita-se o que já é
estruturalmente válido e executável, porque julgar o texto de um volume que nem compila é
desperdiçar a auditoria no problema errado. Toda falha volta para geração ou incorporação;
nenhum caminho segue adiante com gate vermelho.

## Os cinco comandos

| Comando | O que faz |
|---|---|
| `/novo-volume N nome` | resolve o tipo pelo contrato, gera as seções aplicáveis, cria exemplos com teste, roda os gates 1 e 2, grava o status honesto e registra no `CHANGELOG.md` |
| `/auditar N` | dispara o subagente `auditor-fable`, grava o relatório datado em `auditorias/` e atualiza o `status` conforme a média |
| `/status` | roda `ferramentas/status.py`: tabela dos 42 volumes com tipo, status, seções presentes, nota da última auditoria e marca de perecível |
| `/cross-reference` | roda o gate 3 determinístico e, depois, um passe semântico procurando contradições entre volumes |
| `/exportar` | roda `ferramentas/exportar.py`: gera `mkdocs.yml` do que existe em disco e valida o build quando `mkdocs` está instalado |

Os mesmos gates rodam à mão, sem skill: `python -m ferramentas.validar`,
`python -m ferramentas.status`, `python -m ferramentas.scaffold`,
`python -m ferramentas.exportar`. Sempre **de dentro de `AI-ENGINEERING-OS/`** — os
imports `ferramentas.*` dependem disso.

## Proibições

Estas não são preferências. São o que separa o acervo de um gerador de texto convincente.

1. **Nunca gravar `PRONTO` com gate vermelho.** Nem "só o link morto", nem "o teste falha
   por outro motivo", nem "corrijo depois". Gate vermelho grava `RASCUNHO` e reporta as
   violações. Auditoria com média abaixo de 8,0 grava `REQUER_REVISAO`. Status que mente
   destrói o valor de todos os outros status do acervo.
2. **Nunca inventar framework, número ou fonte.** Nome de framework sem definição vai para
   `frameworks/_backlog.md` com a frase padronizada de que não foi inventado. Número sem
   fonte não entra. Paper, livro ou autor que você não pode verificar não é citado — se a
   lista de referências ficar curta, ela fica curta. Atribuição errada é pior que ausência
   de atribuição.
3. **Nunca afirmar sucesso sem ter olhado.** Rodou o gate? Cole a saída. Não rodou? Diga
   que não rodou. "Deve passar" não é resultado.
4. **Nunca ajustar o teste para o conteúdo passar.** O teste é o contrato; o conteúdo é que
   cede.
5. **Nunca marcar pendência com `TODO`/`TBD`/`FIXME` na prosa de um volume.** Pendência tem
   lugar próprio: `16-Roadmap` do volume, `ROADMAP.md` da plataforma, ou
   `frameworks/_backlog.md`.

## Onde as coisas ficam

| Caminho | Conteúdo |
|---|---|
| `00-INTRODUCAO/` | contrato (`contrato.json`), convenções, prefácio, glossário, arquitetura geral |
| `NN-NOME/` | um volume: `_VOLUME.yml` mais um `.md` por seção |
| `ferramentas/` | a máquina, em Python de biblioteca padrão, com testes em `ferramentas/tests/` |
| `exemplos/<vol>/` | código executável citado pelos volumes, com `tests/` ao lado |
| `auditorias/` | relatórios do auditor, um por volume por data |
| `frameworks/`, `agentes/`, `prompts/`, `templates/`, `diagramas/`, `referencias/`, `sdk/` | bibliotecas transversais |
| `ROADMAP.md`, `CHANGELOG.md` | o que falta e o que já aconteceu, com data |

Ferramentas usam **apenas a biblioteca padrão** — sem PyYAML. O front-matter é um
subconjunto YAML restrito de propósito: restringir a gramática é o que permite validá-la
sem dependência e com erro na linha exata.

Datas sempre em ISO `YYYY-MM-DD`. Prosa em português do Brasil. Identificadores em
português no domínio da plataforma (`Violacao`, `Secao`) e em inglês no domínio de prompt
engineering (`PromptTemplate`, `PromptRegistry`).
