# AI-ENGINEERING-OS

Acervo técnico de engenharia de IA em 42 volumes, com **linha de produção verificável**: um
contrato legível por máquina, três gates executáveis e auditoria por um segundo modelo.
Nenhum volume se declara pronto sem que um programa confirme que ele é.

> Esta pasta é um projeto independente. O diretório pai deste repositório é outro projeto
> e **não é tocado** por trabalho feito aqui.

## O que é

A especificação original pedia mais de oito mil páginas distribuídas em 42 volumes de 18
seções fixas. Revisada, ela se contradizia: preencher 756 seções obriga o conteúdo a ficar
genérico, e conteúdo genérico viola a própria regra de não gerar conteúdo superficial.

A decisão foi inverter a prioridade — construir primeiro a **máquina que só aceita conteúdo
bom**, e depois produzir volumes atravessando a máquina, um por vez. O ativo é a linha de
produção; o acervo é a consequência.

Estado atual: máquina completa e funcional, contrato v1.0.0, um volume-piloto padrão-ouro
(`07-PROMPT-ENGINE`) e os outros 41 volumes registrados como pendentes com `_VOLUME.yml`.
O que falta está em [ROADMAP.md](ROADMAP.md); o que já aconteceu está em
[CHANGELOG.md](CHANGELOG.md).

## Estrutura

```
AI-ENGINEERING-OS/
├── CLAUDE.md               contexto local para agentes
├── README.md  CHANGELOG.md  ROADMAP.md  CONTRIBUTING.md  LICENSE
├── 00-INTRODUCAO/
│   ├── contrato.json       fonte unica de verdade legivel por maquina
│   ├── Convencoes.md       o contrato em forma humana
│   ├── Prefacio.md  Como-Utilizar.md  Glossario.md  Arquitetura-Geral.md
├── 01-FUNDACAO/ … 42-PLUGINS/    um _VOLUME.yml + um .md por secao
├── ferramentas/            a maquina (Python, so biblioteca padrao)
│   ├── frontmatter.py  contrato.py  modelo.py  regras.py
│   ├── validar.py  status.py  scaffold.py  exportar.py
│   └── tests/              a maquina testada com fixtures ruins de proposito
├── exemplos/<vol>/         codigo executavel citado pelos volumes, com tests/
├── auditorias/             relatorios do auditor, um por volume por data
├── frameworks/ agentes/ prompts/ templates/ diagramas/ referencias/ sdk/
└── mkdocs.yml              gerado por ferramentas/exportar.py
```

## Como validar

Sempre **de dentro desta pasta** — os imports `ferramentas.*` dependem disso.

```bash
cd AI-ENGINEERING-OS

python -m pytest ferramentas/tests -q        # a propria maquina
python -m ferramentas.status                 # estado dos 42 volumes
python -m ferramentas.validar 07             # gate 1, um volume
python -m ferramentas.validar --tudo         # gate 1, todo o acervo materializado
python -m pytest exemplos/07-prompt-engine -q # gate 2, exemplos do volume
python -m ferramentas.validar --cross-refs   # gate 3, dependencias e ciclos
python -m ferramentas.scaffold               # materializa volumes do contrato
python -m ferramentas.exportar               # gera mkdocs.yml
```

`validar.py` devolve `0` sem violação, `1` com violação e `2` em erro de uso ou de contrato.
Cada violação sai como `arquivo:linha: [regra] mensagem`.

## Interface interativa

Para quem quer começar por uma ideia de software, sem conhecer os comandos ou a estrutura
dos 42 volumes:

```bash
python -m ferramentas.web
```

O navegador abre uma jornada guiada em quatro etapas:

1. ideia do software em linguagem simples;
2. público e problema que precisa ser resolvido;
3. formato do produto, quantidade de usuários e prioridade;
4. integrações, dados sensíveis, prazo e restrições.

Ao final, a plataforma gera um **Plano de Solução** personalizado com escopo inicial do
MVP, direção de arquitetura, fases, riscos, perguntas ainda abertas e os volumes do acervo
recomendados para aquele projeto. O formulário também aceita até dez documentos de
referência; arquivos textuais entram no plano e formatos binários ficam registrados para
aprofundamento no chat. O rascunho das respostas fica salvo apenas no armazenamento local
do navegador. A interface funciona sem CDN e sem conta externa.

O Plano de Solução é um contrato de descoberta, não uma alegação de que o software já foi
implementado. Ele pode ser copiado e entregue a um agente construtor; geração e alteração
de código devem continuar sujeitas a revisão humana, testes e gates.

O formulário distingue visualmente campos **Obrigatórios** e **Opcionais**. A elaboração
inicial usa o `Planejador determinístico AI-ENGINEERING-OS v1`, baseado em regras locais e
sem chamada a um modelo de IA. Ao continuar dentro do ChatGPT, entra em ação o modelo
selecionado para aquela conversa; o servidor MCP não presume nem inventa esse nome.

Antes do formulário completo, o construtor executa uma descoberta conversacional: recebe
a ideia, identifica se o produto é web, mobile, desktop ou automação e apresenta uma
pergunta por vez. A trilha muda conforme o contexto — lojas recebem decisões sobre
pagamento, saúde recebe perguntas sobre dados clínicos, mobile recebe recursos do aparelho
e desktop recebe decisões sobre instalação, nuvem e operação offline. As respostas são
transferidas para a revisão e registradas no Plano de Solução.

### Usar dentro do ChatGPT

O adaptador em [`chatgpt_app/`](chatgpt_app/) expõe o mesmo construtor como um ChatGPT App:
o modelo faz as perguntas, o servidor MCP consulta o acervo e o widget aparece dentro da
conversa. A versão inicial oferece apenas ferramentas de leitura e planejamento; não grava
código nem executa comandos.

```bash
python -m pip install -r chatgpt_app/requirements.txt
python -m chatgpt_app.server
```

O endpoint local é `http://127.0.0.1:8000/mcp`. Consulte
[`chatgpt_app/README.md`](chatgpt_app/README.md) para conectar por HTTPS ao modo de
desenvolvedor do ChatGPT.

## Os três gates

| Gate | Comando | Reprova |
|---|---|---|
| 1 — estrutural | `python -m ferramentas.validar NN` | front-matter incompleto ou incoerente, seção obrigatória ausente, prosa abaixo do mínimo, marcador proibido, Mermaid sem parágrafo descritivo, exemplo citado sem arquivo ou sem teste, link relativo morto |
| 2 — executável | `python -m pytest exemplos/<vol> -q` | código citado pelo volume que não roda ou falha nos próprios testes |
| 3 — cruzado | `python -m ferramentas.validar --cross-refs` | `depende_de` apontando para volume inexistente, ciclo no grafo de pré-requisitos |

A auditoria por outro modelo entra entre o gate 2 e o gate 3. Um volume é `PRONTO` só com os
três gates verdes, auditoria com média maior ou igual a 8,0 sem nenhuma seção abaixo de 6, e
registro datado no `CHANGELOG.md`.

## Requisitos

Python 3.11 ou superior (o ambiente de referência é 3.14.6) e pytest para rodar os testes.
As ferramentas usam **apenas a biblioteca padrão** — sem PyYAML: o front-matter é um
subconjunto YAML restrito de propósito, e a restrição é o que permite validar sem dependência
e apontar o erro na linha exata. `mkdocs` e o tema Material são opcionais, usados só para
validar o build do site exportado.

## Leia em seguida

- [00-INTRODUCAO/Convencoes.md](00-INTRODUCAO/Convencoes.md) — o contrato: seções, tipos,
  front-matter, Definição de PRONTO, regras de diagrama e de código.
- [00-INTRODUCAO/Como-Utilizar.md](00-INTRODUCAO/Como-Utilizar.md) — os cinco comandos e o
  ciclo de produção de um volume.
- [00-INTRODUCAO/Arquitetura-Geral.md](00-INTRODUCAO/Arquitetura-Geral.md) — as camadas e o
  fluxo dos gates.
- [00-INTRODUCAO/Prefacio.md](00-INTRODUCAO/Prefacio.md) — por que existe, para quem, e o que
  deliberadamente não é.
- [00-INTRODUCAO/Glossario.md](00-INTRODUCAO/Glossario.md) — os termos, sempre no mesmo
  sentido.
- [CONTRIBUTING.md](CONTRIBUTING.md) — como propor volume novo e como o gate reprova.
- Design e plano: `../docs/superpowers/specs/2026-07-29-ai-engineering-os-design.md` e
  `../docs/superpowers/plans/2026-07-29-ai-engineering-os.md`.

## Licença

MIT. Ver [LICENSE](LICENSE).
