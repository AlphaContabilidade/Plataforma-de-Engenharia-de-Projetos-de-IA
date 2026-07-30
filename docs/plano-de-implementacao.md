# AI-ENGINEERING-OS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir a máquina de produção da plataforma AI-ENGINEERING-OS (contrato + validador + 5 skills + agente auditor) e um volume-piloto completo e auditado (`07-PROMPT-ENGINE`), dentro de `AI-ENGINEERING-OS/`.

**Architecture:** Um contrato legível por máquina (`00-INTRODUCAO/contrato.json`) define seções, tipos de volume, status e limiares. Ferramentas Python de stdlib leem esse contrato e reprovam conteúdo superficial (`validar.py`), reportam estado (`status.py`) e exportam para MkDocs (`exportar.py`). Cinco skills escopadas à pasta orquestram criação, auditoria por subagente Fable, inspeção, checagem cruzada e exportação. Nenhum volume atinge `PRONTO` sem os três gates verdes.

**Tech Stack:** Python 3.14.6 (stdlib apenas nas ferramentas), pytest 9.1.1, Markdown, Mermaid, MkDocs (opcional, só em `/exportar`).

**Spec:** [2026-07-29-ai-engineering-os-design.md](../specs/2026-07-29-ai-engineering-os-design.md)

## Global Constraints

- **Raiz do trabalho:** `AI-ENGINEERING-OS/`. Nada fora dela é modificado, exceto `docs/superpowers/`.
- **Python ≥ 3.11** (usa `X | Y` em anotações e `enum.StrEnum` na Task 11). Ambiente: 3.14.6, pytest 9.1.1. Se ≥3.10 virar requisito duro, a única troca necessária é `class Estado(str, Enum)` — nenhuma chamada muda.
- **Ferramentas usam apenas a biblioteca padrão.** Sem PyYAML. O front-matter é um subconjunto YAML restrito de propósito — restringir a gramática é o que permite validá-la sem dependência e com erro preciso.
- **`contrato.json` é a única fonte de verdade legível por máquina.** `Convencoes.md` documenta a mesma tabela para humanos, e `test_contrato.py::test_convencoes_nao_derivou` falha se divergirem. Satisfaz "fonte única" (spec §4.1) sem parsear prosa.
- **Idioma:** pt-BR na prosa. Identificadores em português no domínio da plataforma (`Violacao`, `Secao`), em inglês no domínio de prompt engineering (`PromptTemplate`).
- **Datas ISO `YYYY-MM-DD`.** Ciclo corrente: `2026-07-29`.
- **`volume` é sempre string de 2 dígitos** (`"07"`) — evita ambiguidade octal/int.
- **Status válidos, e só estes três:** `RASCUNHO`, `REQUER_REVISAO`, `PRONTO`.
- **Nunca gravar `PRONTO` com gate vermelho. Nunca inventar** framework, número ou fonte — pendência vai para `_backlog.md`.
- **Commits:** um por task; prefixos `feat(aieos):`, `test(aieos):`, `docs(aieos):`.
- **Executar pytest sempre de dentro de `AI-ENGINEERING-OS/`** (imports `ferramentas.*` dependem disso).

---

## Estrutura de arquivos

| Arquivo | Responsabilidade única |
|---|---|
| `ferramentas/modelo.py` | `Violacao` — o tipo que atravessa todas as ferramentas |
| `ferramentas/frontmatter.py` | Parser do subconjunto YAML (front-matter e `_VOLUME.yml`) |
| `ferramentas/contrato.py` | Carrega `contrato.json`; resolve seções/diagramas por tipo |
| `ferramentas/regras.py` | As regras de qualidade, uma função pura por regra |
| `ferramentas/validar.py` | Orquestra as regras + CLI dos gates |
| `ferramentas/status.py` | Leitura de estado do acervo |
| `ferramentas/exportar.py` | Geração de `mkdocs.yml` |
| `ferramentas/scaffold.py` | Cria pastas de volume e `_VOLUME.yml` do contrato (idempotente) |
| `ferramentas/tests/` | Testa a máquina com fixtures boas e ruins |
| `exemplos/07-prompt-engine/*.py` | Código executável citado pelo piloto |
| `07-PROMPT-ENGINE/NN-*.md` | O volume-piloto |
| `.claude/skills/*/SKILL.md` | Os 5 comandos operacionais |
| `.claude/agents/auditor-fable.md` | Subagente de auditoria |

Ordem das tasks: a máquina antes do conteúdo, porque a máquina é o gate do conteúdo.

---

## Task 1: Parser de front-matter

**Files:**
- Create: `AI-ENGINEERING-OS/ferramentas/__init__.py` (vazio), `AI-ENGINEERING-OS/ferramentas/tests/__init__.py` (vazio)
- Create: `AI-ENGINEERING-OS/ferramentas/frontmatter.py`
- Test: `AI-ENGINEERING-OS/ferramentas/tests/test_frontmatter.py`

**Interfaces:**
- Consumes: nada.
- Produces:
  - `class FrontMatterInvalido(ValueError)`
  - `def extrair_bloco(texto: str) -> tuple[str, int]` — `(corpo, linha_1indexed_do_inicio_do_conteudo)`; levanta se falta `---` de abertura ou fechamento.
  - `def parse_bloco(bloco: str) -> dict[str, object]` — levanta em linha sem `:`, chave duplicada ou vazia.
  - `def ler(caminho: Path) -> tuple[dict[str, object], int]`
  - `def ler_volume_yml(caminho: Path) -> dict[str, object]`

- [ ] **Step 1: Write the failing test**

Create `AI-ENGINEERING-OS/ferramentas/tests/test_frontmatter.py`:

```python
"""Testa o parser do subconjunto YAML do front-matter."""
import pytest

from ferramentas.frontmatter import (
    FrontMatterInvalido, extrair_bloco, ler, ler_volume_yml, parse_bloco,
)

BLOCO_OK = """---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 04-Arquitetura
status: RASCUNHO
atualizado_em: 2026-07-29
perecivel: false
depende_de: [08-AGENT-ENGINE, 28-PROMPT-COMPILER]
---

# Arquitetura

Conteudo.
"""


def test_extrair_bloco_devolve_corpo_e_linha_do_conteudo():
    corpo, linha = extrair_bloco(BLOCO_OK)
    assert "tipo: ENGINE" in corpo
    assert linha == 11  # fechamento na linha 10; conteudo comeca na 11


def test_volume_permanece_string():
    campos = parse_bloco(extrair_bloco(BLOCO_OK)[0])
    assert campos["volume"] == "07" and isinstance(campos["volume"], str)


def test_le_lista_em_linha():
    campos = parse_bloco(extrair_bloco(BLOCO_OK)[0])
    assert campos["depende_de"] == ["08-AGENT-ENGINE", "28-PROMPT-COMPILER"]


def test_le_booleano():
    assert parse_bloco(extrair_bloco(BLOCO_OK)[0])["perecivel"] is False


def test_lista_vazia():
    assert parse_bloco("depende_de: []")["depende_de"] == []


def test_inteiro_sem_zero_a_esquerda():
    assert parse_bloco("minimo: 200")["minimo"] == 200


def test_ignora_comentario_e_linha_vazia():
    assert parse_bloco("# comentario\n\ntipo: ENGINE\n") == {"tipo": "ENGINE"}


def test_sem_abertura_falha():
    with pytest.raises(FrontMatterInvalido, match="ausente"):
        extrair_bloco("# Titulo\n\nsem front-matter\n")


def test_sem_fechamento_falha():
    with pytest.raises(FrontMatterInvalido, match="fechamento"):
        extrair_bloco("---\ntipo: ENGINE\n\n# Titulo\n")


def test_linha_sem_dois_pontos_falha():
    with pytest.raises(FrontMatterInvalido, match="linha 1"):
        parse_bloco("tipo ENGINE\n")


def test_chave_duplicada_falha():
    with pytest.raises(FrontMatterInvalido, match="duplicada"):
        parse_bloco("tipo: ENGINE\ntipo: PROCESSO\n")


def test_chave_vazia_falha():
    with pytest.raises(FrontMatterInvalido, match="vazia"):
        parse_bloco(": ENGINE\n")


def test_ler_arquivo(tmp_path):
    arq = tmp_path / "04-Arquitetura.md"
    arq.write_text(BLOCO_OK, encoding="utf-8")
    campos, linha = ler(arq)
    assert campos["secao"] == "04-Arquitetura" and linha == 11


def test_ler_volume_yml(tmp_path):
    arq = tmp_path / "_VOLUME.yml"
    arq.write_text('volume: "07"\nnome: PROMPT-ENGINE\ntipo: ENGINE\n', encoding="utf-8")
    assert ler_volume_yml(arq)["nome"] == "PROMPT-ENGINE"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd AI-ENGINEERING-OS && python -m pytest ferramentas/tests/test_frontmatter.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'ferramentas.frontmatter'`

- [ ] **Step 3: Write minimal implementation**

`AI-ENGINEERING-OS/ferramentas/frontmatter.py`:

```python
"""Parser do subconjunto YAML usado no front-matter e nos _VOLUME.yml.

O front-matter da plataforma e um contrato restrito de proposito: escalares,
booleanos, inteiros e listas em linha. Restringir a gramatica e o que permite
valida-la sem dependencia externa e com mensagens de erro precisas.

Coercao deliberada: numero com zero a esquerda permanece string, para que
`volume: "07"` e `volume: 07` nunca divirjam no resto da maquina.
"""

from __future__ import annotations

import re
from pathlib import Path

DELIMITADOR = "---"
_INTEIRO = re.compile(r"-?[1-9][0-9]*|0")


class FrontMatterInvalido(ValueError):
    """Front-matter ausente, malformado ou com chave invalida."""


def extrair_bloco(texto: str) -> tuple[str, int]:
    """Devolve (corpo do front-matter, linha 1-indexed onde o conteudo comeca)."""
    linhas = texto.splitlines()
    if not linhas or linhas[0].strip() != DELIMITADOR:
        raise FrontMatterInvalido("front-matter ausente: arquivo nao comeca com '---'")
    for i in range(1, len(linhas)):
        if linhas[i].strip() == DELIMITADOR:
            return "\n".join(linhas[1:i]), i + 2
    raise FrontMatterInvalido("front-matter sem delimitador de fechamento '---'")


def _coagir(valor: str) -> object:
    valor = valor.strip()
    if valor.startswith("[") and valor.endswith("]"):
        interno = valor[1:-1].strip()
        return [] if not interno else [x.strip().strip("\"'") for x in interno.split(",")]
    if valor in ("true", "false"):
        return valor == "true"
    if _INTEIRO.fullmatch(valor):
        return int(valor)
    return valor.strip("\"'")


def parse_bloco(bloco: str) -> dict[str, object]:
    """Converte o corpo do front-matter em dict, validando a gramatica."""
    campos: dict[str, object] = {}
    for n, linha in enumerate(bloco.splitlines(), start=1):
        crua = linha.strip()
        if not crua or crua.startswith("#"):
            continue
        if ":" not in crua:
            raise FrontMatterInvalido(f"linha {n}: esperado 'chave: valor', obtido {crua!r}")
        chave, _, valor = crua.partition(":")
        chave = chave.strip()
        if not chave:
            raise FrontMatterInvalido(f"linha {n}: chave vazia")
        if chave in campos:
            raise FrontMatterInvalido(f"linha {n}: chave duplicada {chave!r}")
        campos[chave] = _coagir(valor)
    return campos


def ler(caminho: Path) -> tuple[dict[str, object], int]:
    """Le um arquivo de secao: devolve (campos, linha inicial do conteudo)."""
    bloco, linha_conteudo = extrair_bloco(caminho.read_text(encoding="utf-8"))
    return parse_bloco(bloco), linha_conteudo


def ler_volume_yml(caminho: Path) -> dict[str, object]:
    """Le um _VOLUME.yml (arquivo inteiro, sem delimitadores)."""
    return parse_bloco(caminho.read_text(encoding="utf-8"))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd AI-ENGINEERING-OS && python -m pytest ferramentas/tests/test_frontmatter.py -q`
Expected: PASS — 14 passed

- [ ] **Step 5: Commit**

```bash
git add AI-ENGINEERING-OS/ferramentas
git commit -m "feat(aieos): parser do subconjunto YAML do front-matter"
```

---

## Task 2: Contrato legível por máquina

**Files:**
- Create: `AI-ENGINEERING-OS/ferramentas/modelo.py`
- Create: `AI-ENGINEERING-OS/00-INTRODUCAO/contrato.json`
- Create: `AI-ENGINEERING-OS/ferramentas/contrato.py`
- Test: `AI-ENGINEERING-OS/ferramentas/tests/test_contrato.py`

**Interfaces:**
- Consumes: nada de Task 1.
- Produces:
  - `modelo.Violacao` — `dataclass(frozen=True, slots=True)`: `arquivo: str`, `linha: int`, `regra: str`, `mensagem: str`; `__str__` → `"{arquivo}:{linha}: [{regra}] {mensagem}"`. `linha=0` significa "o arquivo como um todo".
  - `contrato.ContratoInvalido(ValueError)`
  - `contrato.Contrato` — `dataclass(frozen=True, slots=True)` com `versao: str`, `min_palavras: int`, `min_palavras_por_secao: dict[str,int]`, `status_validos: tuple[str,...]`, `campos_frontmatter: tuple[str,...]`, `marcadores_proibidos: tuple[str,...]`, `secoes_base: tuple[str,...]`, `tipos: dict[str,dict]`, `volumes: dict[str,dict]`.
  - `Contrato.secoes_de(tipo) -> tuple[str,...]`, `Contrato.diagramas_de(tipo) -> tuple[str,...]`, `Contrato.minimo_de(secao) -> int`, `Contrato.volume(vol_id) -> dict`
  - `contrato.carregar(raiz: Path) -> Contrato`

- [ ] **Step 1: Write the failing test**

Create `AI-ENGINEERING-OS/ferramentas/tests/test_contrato.py`:

```python
"""Testa o carregamento do contrato e a resolucao de secoes por tipo."""
import re
from pathlib import Path

import pytest

from ferramentas import contrato as C

RAIZ = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def ct():
    return C.carregar(RAIZ)


def test_dezoito_secoes_base(ct):
    assert len(ct.secoes_base) == 18
    assert ct.secoes_base[0] == "01-Introducao"
    assert ct.secoes_base[-1] == "18-Referencias-Cruzadas"


def test_status_validos_sao_exatamente_tres(ct):
    assert ct.status_validos == ("RASCUNHO", "REQUER_REVISAO", "PRONTO")


def test_engine_usa_todas_as_dezoito(ct):
    assert ct.secoes_de("ENGINE") == ct.secoes_base


def test_biblioteca_troca_arquitetura_por_catalogo(ct):
    secoes = ct.secoes_de("BIBLIOTECA")
    assert "04-Arquitetura" not in secoes
    assert "05-Diagramas" not in secoes
    assert "04-Catalogo" in secoes


def test_processo_dispensa_modelos(ct):
    assert "08-Modelos" not in ct.secoes_de("PROCESSO")


def test_secoes_saem_em_ordem_numerica(ct):
    for tipo in ct.tipos:
        prefixos = [int(s[:2]) for s in ct.secoes_de(tipo)]
        assert prefixos == sorted(prefixos), tipo


def test_tipo_desconhecido_lista_os_aceitos(ct):
    with pytest.raises(C.ContratoInvalido) as erro:
        ct.secoes_de("INVENTADO")
    assert "ENGINE" in str(erro.value)


def test_os_42_volumes_estao_declarados(ct):
    assert set(ct.volumes) == {f"{n:02d}" for n in range(1, 43)}


def test_todo_volume_tem_tipo_conhecido(ct):
    for vol_id, meta in ct.volumes.items():
        assert meta["tipo"] in ct.tipos, f"{vol_id} tem tipo invalido"


def test_volume_07_e_prompt_engine_do_tipo_engine(ct):
    assert ct.volume("07") == {"nome": "PROMPT-ENGINE", "tipo": "ENGINE", "perecivel": False}


def test_pereciveis_sao_os_tres_previstos(ct):
    assert {v for v, m in ct.volumes.items() if m["perecivel"]} == {"26", "27", "34"}


def test_volume_inexistente_falha(ct):
    with pytest.raises(C.ContratoInvalido, match="99"):
        ct.volume("99")


def test_minimo_por_secao_tem_fallback(ct):
    assert ct.minimo_de("04-Arquitetura") == ct.min_palavras
    assert ct.minimo_de("15-Checklist") == 120


def test_convencoes_nao_derivou(ct):
    """A tabela de tipos em Convencoes.md tem de refletir contrato.json."""
    texto = (RAIZ / "00-INTRODUCAO" / "Convencoes.md").read_text(encoding="utf-8")
    for tipo in ct.tipos:
        linha = next(
            (ln for ln in texto.splitlines() if ln.strip().startswith(f"| `{tipo}`")), None
        )
        assert linha, f"tipo {tipo} ausente da tabela de Convencoes.md"
        declarados = set(re.findall(r"\b(\d{2})\b", linha.split("|")[2]))
        esperados = {v for v, m in ct.volumes.items() if m["tipo"] == tipo}
        assert declarados == esperados, f"{tipo}: Convencoes.md diverge de contrato.json"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd AI-ENGINEERING-OS && python -m pytest ferramentas/tests/test_contrato.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'ferramentas.contrato'`

- [ ] **Step 3: Write `modelo.py`**

```python
"""Tipos compartilhados pelas ferramentas da plataforma."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Violacao:
    """Uma quebra de contrato encontrada no acervo.

    `linha` e 1-indexed. Use 0 quando a violacao e do arquivo como um todo
    (ausente, por exemplo) e nao de uma linha especifica.
    """

    arquivo: str
    linha: int
    regra: str
    mensagem: str

    def __str__(self) -> str:
        return f"{self.arquivo}:{self.linha}: [{self.regra}] {self.mensagem}"
```

- [ ] **Step 4: Write `00-INTRODUCAO/contrato.json`**

Atribuição de tipos conforme spec §4.1. Os 42 volumes ficam declarados aqui — é
esta a lista que `scaffold.py` materializa em pastas na Task 8.

```json
{
  "versao": "1.0.0",
  "atualizado_em": "2026-07-29",
  "min_palavras": 200,
  "min_palavras_por_secao": {
    "15-Checklist": 120,
    "16-Roadmap": 120,
    "17-Conclusao": 150,
    "18-Referencias-Cruzadas": 80
  },
  "status_validos": ["RASCUNHO", "REQUER_REVISAO", "PRONTO"],
  "campos_frontmatter": ["volume", "volume_nome", "tipo", "secao", "status", "atualizado_em"],
  "marcadores_proibidos": ["TBD", "TODO", "PENDENTE", "FIXME", "XXX", "preencher aqui"],
  "secoes_base": [
    "01-Introducao", "02-Objetivos", "03-Escopo", "04-Arquitetura",
    "05-Diagramas", "06-Fluxogramas", "07-Regras", "08-Modelos",
    "09-Boas-Praticas", "10-Anti-Patterns", "11-Implementacao", "12-Exemplos",
    "13-Testes", "14-Metricas", "15-Checklist", "16-Roadmap",
    "17-Conclusao", "18-Referencias-Cruzadas"
  ],
  "tipos": {
    "ENGINE": {
      "descricao": "Motor com contratos, estado e codigo executavel.",
      "opcionais": [],
      "extras": [],
      "diagramas_obrigatorios": ["C4Context", "sequenceDiagram", "stateDiagram-v2"]
    },
    "ARQUITETURA": {
      "descricao": "Camada arquitetural; nem sempre tem ciclo de vida proprio.",
      "opcionais": [],
      "extras": [],
      "diagramas_obrigatorios": ["C4Context", "sequenceDiagram"]
    },
    "PROCESSO": {
      "descricao": "Processo de trabalho; o fluxo importa mais que o modelo de dados.",
      "opcionais": ["08-Modelos"],
      "extras": [],
      "diagramas_obrigatorios": ["flowchart"]
    },
    "BIBLIOTECA": {
      "descricao": "Acervo catalogado; nao tem arquitetura propria.",
      "opcionais": ["04-Arquitetura", "05-Diagramas"],
      "extras": ["04-Catalogo"],
      "diagramas_obrigatorios": []
    },
    "GOVERNANCA": {
      "descricao": "Politica e controle; exige matriz de controles.",
      "opcionais": [],
      "extras": [],
      "diagramas_obrigatorios": ["flowchart"]
    }
  },
  "volumes": {
    "01": {"nome": "FUNDACAO", "tipo": "GOVERNANCA", "perecivel": false},
    "02": {"nome": "CORE", "tipo": "ARQUITETURA", "perecivel": false},
    "03": {"nome": "DISCOVERY", "tipo": "PROCESSO", "perecivel": false},
    "04": {"nome": "REQUIREMENTS", "tipo": "PROCESSO", "perecivel": false},
    "05": {"nome": "BUSINESS", "tipo": "PROCESSO", "perecivel": false},
    "06": {"nome": "ENTERPRISE-ARCHITECTURE", "tipo": "ARQUITETURA", "perecivel": false},
    "07": {"nome": "PROMPT-ENGINE", "tipo": "ENGINE", "perecivel": false},
    "08": {"nome": "AGENT-ENGINE", "tipo": "ENGINE", "perecivel": false},
    "09": {"nome": "ORCHESTRATOR", "tipo": "ENGINE", "perecivel": false},
    "10": {"nome": "WORKFLOW", "tipo": "ENGINE", "perecivel": false},
    "11": {"nome": "KNOWLEDGE", "tipo": "ENGINE", "perecivel": false},
    "12": {"nome": "MEMORY", "tipo": "ENGINE", "perecivel": false},
    "13": {"nome": "RAG", "tipo": "ENGINE", "perecivel": false},
    "14": {"nome": "VECTOR", "tipo": "ENGINE", "perecivel": false},
    "15": {"nome": "CONTEXT", "tipo": "ENGINE", "perecivel": false},
    "16": {"nome": "INTEGRATION", "tipo": "ARQUITETURA", "perecivel": false},
    "17": {"nome": "SECURITY", "tipo": "GOVERNANCA", "perecivel": false},
    "18": {"nome": "DEVSECOPS", "tipo": "PROCESSO", "perecivel": false},
    "19": {"nome": "DEVOPS", "tipo": "ARQUITETURA", "perecivel": false},
    "20": {"nome": "CLOUD", "tipo": "ARQUITETURA", "perecivel": false},
    "21": {"nome": "OBSERVABILITY", "tipo": "GOVERNANCA", "perecivel": false},
    "22": {"nome": "FRONTEND-ARCHITECT", "tipo": "ARQUITETURA", "perecivel": false},
    "23": {"nome": "BACKEND-ARCHITECT", "tipo": "ARQUITETURA", "perecivel": false},
    "24": {"nome": "DATABASE-ARCHITECT", "tipo": "ARQUITETURA", "perecivel": false},
    "25": {"nome": "API-ARCHITECT", "tipo": "ARQUITETURA", "perecivel": false},
    "26": {"nome": "AI-MODELS", "tipo": "ENGINE", "perecivel": true},
    "27": {"nome": "LLM-ROUTER", "tipo": "ENGINE", "perecivel": true},
    "28": {"nome": "PROMPT-COMPILER", "tipo": "ENGINE", "perecivel": false},
    "29": {"nome": "PROMPT-OPTIMIZER", "tipo": "ENGINE", "perecivel": false},
    "30": {"nome": "AI-GOVERNANCE", "tipo": "GOVERNANCA", "perecivel": false},
    "31": {"nome": "TESTING", "tipo": "PROCESSO", "perecivel": false},
    "32": {"nome": "QUALITY", "tipo": "PROCESSO", "perecivel": false},
    "33": {"nome": "PERFORMANCE", "tipo": "PROCESSO", "perecivel": false},
    "34": {"nome": "COST-OPTIMIZATION", "tipo": "PROCESSO", "perecivel": true},
    "35": {"nome": "DOCUMENTATION", "tipo": "GOVERNANCA", "perecivel": false},
    "36": {"nome": "DIAGRAMS", "tipo": "BIBLIOTECA", "perecivel": false},
    "37": {"nome": "CODE-GENERATION", "tipo": "ENGINE", "perecivel": false},
    "38": {"nome": "PROJECT-PLANNER", "tipo": "PROCESSO", "perecivel": false},
    "39": {"nome": "ROADMAP", "tipo": "PROCESSO", "perecivel": false},
    "40": {"nome": "TEMPLATES", "tipo": "BIBLIOTECA", "perecivel": false},
    "41": {"nome": "SDK", "tipo": "ENGINE", "perecivel": false},
    "42": {"nome": "PLUGINS", "tipo": "ENGINE", "perecivel": false}
  }
}
```

- [ ] **Step 5: Write `contrato.py`**

```python
"""Carrega o contrato da plataforma.

`00-INTRODUCAO/contrato.json` e a unica fonte de verdade legivel por maquina.
`Convencoes.md` documenta a mesma tabela para humanos; o teste
`test_contrato.py::test_convencoes_nao_derivou` falha se as duas divergirem.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ARQUIVO = Path("00-INTRODUCAO") / "contrato.json"


class ContratoInvalido(ValueError):
    """Contrato ausente, malformado, ou consultado com chave inexistente."""


@dataclass(frozen=True, slots=True)
class Contrato:
    versao: str
    min_palavras: int
    min_palavras_por_secao: dict[str, int]
    status_validos: tuple[str, ...]
    campos_frontmatter: tuple[str, ...]
    marcadores_proibidos: tuple[str, ...]
    secoes_base: tuple[str, ...]
    tipos: dict[str, dict]
    volumes: dict[str, dict]

    def _regra(self, tipo: str) -> dict:
        if tipo not in self.tipos:
            aceitos = ", ".join(sorted(self.tipos))
            raise ContratoInvalido(f"tipo desconhecido {tipo!r}; aceitos: {aceitos}")
        return self.tipos[tipo]

    def secoes_de(self, tipo: str) -> tuple[str, ...]:
        """Secoes obrigatorias para o tipo, em ordem numerica."""
        regra = self._regra(tipo)
        opcionais = set(regra.get("opcionais", ()))
        secoes = [s for s in self.secoes_base if s not in opcionais]
        secoes.extend(regra.get("extras", ()))
        return tuple(sorted(secoes, key=lambda s: (s[:2], s)))

    def diagramas_de(self, tipo: str) -> tuple[str, ...]:
        return tuple(self._regra(tipo).get("diagramas_obrigatorios", ()))

    def minimo_de(self, secao: str) -> int:
        return self.min_palavras_por_secao.get(secao, self.min_palavras)

    def volume(self, vol_id: str) -> dict:
        if vol_id not in self.volumes:
            raise ContratoInvalido(f"volume {vol_id!r} nao declarado no contrato")
        return self.volumes[vol_id]


def carregar(raiz: Path) -> Contrato:
    caminho = raiz / ARQUIVO
    if not caminho.exists():
        raise ContratoInvalido(f"contrato ausente: {caminho}")
    try:
        bruto = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError as erro:
        raise ContratoInvalido(f"{caminho}: JSON invalido - {erro}") from erro
    return Contrato(
        versao=bruto["versao"],
        min_palavras=bruto["min_palavras"],
        min_palavras_por_secao=bruto["min_palavras_por_secao"],
        status_validos=tuple(bruto["status_validos"]),
        campos_frontmatter=tuple(bruto["campos_frontmatter"]),
        marcadores_proibidos=tuple(bruto["marcadores_proibidos"]),
        secoes_base=tuple(bruto["secoes_base"]),
        tipos=bruto["tipos"],
        volumes=bruto["volumes"],
    )
```

- [ ] **Step 6: Run tests**

Run: `cd AI-ENGINEERING-OS && python -m pytest ferramentas/tests/test_contrato.py -q`
Expected: 13 passed, 1 failed — `test_convencoes_nao_derivou` falha porque `Convencoes.md`
só nasce na Task 8. É intencional: o teste existe antes do artefato que ele guarda.

- [ ] **Step 7: Commit**

```bash
git add AI-ENGINEERING-OS/ferramentas AI-ENGINEERING-OS/00-INTRODUCAO/contrato.json
git commit -m "feat(aieos): contrato legivel por maquina e tipos de volume

test_convencoes_nao_derivou fica vermelho ate a Task 8 criar Convencoes.md."
```

---

## Task 3: Regras estruturais de qualidade

**Refinamento sobre o spec §4.2:** `depende_de` passa a viver no `_VOLUME.yml` (nível de
volume) e usa **ids de 2 dígitos** (`["01", "02"]`), não nomes. Motivo: ids são
validáveis contra `contrato.json` e permitem detectar ciclo sem ambiguidade de grafia.
E `depende_de` significa **pré-requisito de leitura** (acíclico por definição) — a relação
bidirecional "assunto vizinho" fica em `18-Referencias-Cruzadas.md`, que não entra no
grafo. Sem isso, 07↔28 seria um ciclo falso.

**Files:**
- Create: `AI-ENGINEERING-OS/ferramentas/regras.py`
- Test: `AI-ENGINEERING-OS/ferramentas/tests/conftest.py`, `AI-ENGINEERING-OS/ferramentas/tests/test_regras_estrutura.py`

**Interfaces:**
- Consumes: `contrato.Contrato`, `frontmatter.ler`, `frontmatter.FrontMatterInvalido`, `modelo.Violacao`.
- Produces:
  - `def corpo_de(caminho: Path) -> tuple[list[str], int]` — `(linhas_do_arquivo, linha_inicio_conteudo)`.
  - `def palavras_de_prosa(linhas: list[str], inicio: int) -> int` — conta palavras ignorando blocos cercados por ``` (senão código infla a contagem).
  - `def checar_frontmatter(rel: str, caminho: Path, secao: str, vol: dict, ct: Contrato) -> list[Violacao]`
  - `def checar_substancia(rel: str, linhas: list[str], inicio: int, secao: str, ct: Contrato) -> list[Violacao]`
  - `def sem_marcadores(rel: str, linhas: list[str], inicio: int, ct: Contrato) -> list[Violacao]`
  - Constante `REGRAS_ESTRUTURA: tuple[str, ...]` com os nomes de regra emitidos, para os testes se ancorarem em nomes estáveis: `("frontmatter", "frontmatter-campo", "frontmatter-status", "frontmatter-coerencia", "substancia-curta", "marcador-proibido")`.

- [ ] **Step 1: Write the fixture helper**

Create `AI-ENGINEERING-OS/ferramentas/tests/conftest.py`:

```python
"""Fixtures para testar a maquina: constroi acervos sinteticos em tmp_path."""
import json
import shutil
from pathlib import Path

import pytest

RAIZ_REAL = Path(__file__).resolve().parents[2]

FRONT_OK = """---
volume: "{vol}"
volume_nome: {nome}
tipo: {tipo}
secao: {secao}
status: RASCUNHO
atualizado_em: 2026-07-29
---
"""

# 210 palavras de prosa: acima do minimo global de 200.
PROSA = ("palavra " * 210).strip()


@pytest.fixture
def acervo(tmp_path):
    """Acervo minimo valido: contrato real copiado + volume 07 completo."""
    (tmp_path / "00-INTRODUCAO").mkdir()
    shutil.copy(
        RAIZ_REAL / "00-INTRODUCAO" / "contrato.json",
        tmp_path / "00-INTRODUCAO" / "contrato.json",
    )
    return tmp_path


@pytest.fixture
def volume_engine(acervo):
    """Cria 07-PROMPT-ENGINE valido e devolve (raiz, pasta_do_volume)."""
    from ferramentas import contrato as C

    ct = C.carregar(acervo)
    pasta = acervo / "07-PROMPT-ENGINE"
    pasta.mkdir()
    (pasta / "_VOLUME.yml").write_text(
        'volume: "07"\nnome: PROMPT-ENGINE\ntipo: ENGINE\n'
        'status: RASCUNHO\nperecivel: false\ndepende_de: []\n',
        encoding="utf-8",
    )
    for secao in ct.secoes_de("ENGINE"):
        cabeca = FRONT_OK.format(vol="07", nome="PROMPT-ENGINE", tipo="ENGINE", secao=secao)
        (pasta / f"{secao}.md").write_text(
            f"{cabeca}\n# {secao}\n\n{PROSA}\n", encoding="utf-8"
        )
    return acervo, pasta


def escrever(caminho: Path, texto: str) -> None:
    caminho.write_text(texto, encoding="utf-8")
```

- [ ] **Step 2: Write the failing test**

Create `AI-ENGINEERING-OS/ferramentas/tests/test_regras_estrutura.py`:

```python
"""Fixtures deliberadamente ruins: cada uma precisa ser detectada."""
from ferramentas import contrato as C
from ferramentas import regras as R
from ferramentas.tests.conftest import FRONT_OK, PROSA


def _regras(violacoes):
    return {v.regra for v in violacoes}


def test_secao_valida_nao_gera_violacao(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "04-Arquitetura.md"
    linhas, inicio = R.corpo_de(arq)
    vol = {"volume": "07", "nome": "PROMPT-ENGINE", "tipo": "ENGINE"}
    assert R.checar_frontmatter("04-Arquitetura.md", arq, "04-Arquitetura", vol, ct) == []
    assert R.checar_substancia("04-Arquitetura.md", linhas, inicio, "04-Arquitetura", ct) == []


def test_secao_sem_frontmatter_e_detectada(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "04-Arquitetura.md"
    arq.write_text("# Arquitetura\n\n" + PROSA + "\n", encoding="utf-8")
    vol = {"volume": "07", "nome": "PROMPT-ENGINE", "tipo": "ENGINE"}
    assert "frontmatter" in _regras(
        R.checar_frontmatter("04-Arquitetura.md", arq, "04-Arquitetura", vol, ct)
    )


def test_campo_obrigatorio_ausente_e_detectado(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "04-Arquitetura.md"
    arq.write_text(
        '---\nvolume: "07"\ntipo: ENGINE\nsecao: 04-Arquitetura\n'
        "status: RASCUNHO\natualizado_em: 2026-07-29\n---\n\n" + PROSA + "\n",
        encoding="utf-8",
    )
    vol = {"volume": "07", "nome": "PROMPT-ENGINE", "tipo": "ENGINE"}
    saida = R.checar_frontmatter("04-Arquitetura.md", arq, "04-Arquitetura", vol, ct)
    assert "frontmatter-campo" in _regras(saida)
    assert "volume_nome" in str(saida[0])


def test_status_invalido_e_detectado(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "04-Arquitetura.md"
    texto = arq.read_text(encoding="utf-8").replace("status: RASCUNHO", "status: QUASE")
    arq.write_text(texto, encoding="utf-8")
    vol = {"volume": "07", "nome": "PROMPT-ENGINE", "tipo": "ENGINE"}
    assert "frontmatter-status" in _regras(
        R.checar_frontmatter("04-Arquitetura.md", arq, "04-Arquitetura", vol, ct)
    )


def test_secao_do_frontmatter_diferente_do_nome_do_arquivo(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "04-Arquitetura.md"
    texto = arq.read_text(encoding="utf-8").replace("secao: 04-Arquitetura", "secao: 05-Diagramas")
    arq.write_text(texto, encoding="utf-8")
    vol = {"volume": "07", "nome": "PROMPT-ENGINE", "tipo": "ENGINE"}
    assert "frontmatter-coerencia" in _regras(
        R.checar_frontmatter("04-Arquitetura.md", arq, "04-Arquitetura", vol, ct)
    )


def test_tipo_divergente_do_volume_yml(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "04-Arquitetura.md"
    texto = arq.read_text(encoding="utf-8").replace("tipo: ENGINE", "tipo: PROCESSO")
    arq.write_text(texto, encoding="utf-8")
    vol = {"volume": "07", "nome": "PROMPT-ENGINE", "tipo": "ENGINE"}
    assert "frontmatter-coerencia" in _regras(
        R.checar_frontmatter("04-Arquitetura.md", arq, "04-Arquitetura", vol, ct)
    )


def test_secao_curta_e_detectada(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "04-Arquitetura.md"
    cabeca = FRONT_OK.format(vol="07", nome="PROMPT-ENGINE", tipo="ENGINE", secao="04-Arquitetura")
    arq.write_text(cabeca + "\n# Arquitetura\n\nCurto demais.\n", encoding="utf-8")
    linhas, inicio = R.corpo_de(arq)
    saida = R.checar_substancia("04-Arquitetura.md", linhas, inicio, "04-Arquitetura", ct)
    assert "substancia-curta" in _regras(saida)


def test_codigo_nao_conta_como_prosa(volume_engine):
    """Uma secao so de codigo tem de reprovar por curta."""
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "04-Arquitetura.md"
    cabeca = FRONT_OK.format(vol="07", nome="PROMPT-ENGINE", tipo="ENGINE", secao="04-Arquitetura")
    codigo = "```python\n" + ("x = 1  # palavra palavra palavra\n" * 120) + "```\n"
    arq.write_text(cabeca + "\n# Arquitetura\n\n" + codigo, encoding="utf-8")
    linhas, inicio = R.corpo_de(arq)
    assert "substancia-curta" in _regras(
        R.checar_substancia("04-Arquitetura.md", linhas, inicio, "04-Arquitetura", ct)
    )


def test_marcador_proibido_e_detectado(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "04-Arquitetura.md"
    cabeca = FRONT_OK.format(vol="07", nome="PROMPT-ENGINE", tipo="ENGINE", secao="04-Arquitetura")
    arq.write_text(cabeca + "\n# Arquitetura\n\nTODO: escrever isso.\n\n" + PROSA + "\n",
                   encoding="utf-8")
    linhas, inicio = R.corpo_de(arq)
    saida = R.sem_marcadores("04-Arquitetura.md", linhas, inicio, ct)
    assert "marcador-proibido" in _regras(saida)
    assert saida[0].linha == 10


def test_marcador_em_code_span_e_permitido(volume_engine):
    """Mencionar `TODO` em fonte de codigo e legitimo; a regra nao pode pegar."""
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "10-Anti-Patterns.md"
    cabeca = FRONT_OK.format(vol="07", nome="PROMPT-ENGINE", tipo="ENGINE", secao="10-Anti-Patterns")
    arq.write_text(
        cabeca + "\n# Anti-Patterns\n\nDeixar `TODO` no volume e anti-pattern.\n\n" + PROSA + "\n",
        encoding="utf-8",
    )
    linhas, inicio = R.corpo_de(arq)
    assert R.sem_marcadores("10-Anti-Patterns.md", linhas, inicio, ct) == []
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd AI-ENGINEERING-OS && python -m pytest ferramentas/tests/test_regras_estrutura.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'ferramentas.regras'`

- [ ] **Step 4: Write `regras.py` (parte estrutural)**

```python
"""As regras de qualidade da plataforma, uma funcao pura por regra.

Cada funcao recebe o que precisa e devolve `list[Violacao]` - nunca imprime,
nunca levanta por conteudo ruim. Levantar e para erro de programa; conteudo
ruim e violacao reportada.
"""

from __future__ import annotations

import re
from pathlib import Path

from .contrato import Contrato
from .frontmatter import FrontMatterInvalido, extrair_bloco, parse_bloco
from .modelo import Violacao

REGRAS_ESTRUTURA = (
    "frontmatter",
    "frontmatter-campo",
    "frontmatter-status",
    "frontmatter-coerencia",
    "substancia-curta",
    "marcador-proibido",
)

_FENCE = re.compile(r"^\s*```")
_CODE_SPAN = re.compile(r"`[^`]*`")


def corpo_de(caminho: Path) -> tuple[list[str], int]:
    """Devolve (linhas do arquivo, linha 1-indexed onde o conteudo comeca).

    Se o front-matter esta ausente, `inicio` e 1: o arquivo todo e conteudo.
    """
    texto = caminho.read_text(encoding="utf-8")
    linhas = texto.splitlines()
    try:
        _, inicio = extrair_bloco(texto)
    except FrontMatterInvalido:
        inicio = 1
    return linhas, inicio


def _fora_de_codigo(linhas: list[str], inicio: int):
    """Itera (numero_da_linha, texto) apenas fora de blocos cercados."""
    dentro = False
    for n in range(inicio, len(linhas) + 1):
        linha = linhas[n - 1]
        if _FENCE.match(linha):
            dentro = not dentro
            continue
        if not dentro:
            yield n, linha


def palavras_de_prosa(linhas: list[str], inicio: int) -> int:
    """Conta palavras de prosa, ignorando blocos de codigo e cabecalhos."""
    total = 0
    for _, linha in _fora_de_codigo(linhas, inicio):
        limpa = linha.strip()
        if not limpa or limpa.startswith("#"):
            continue
        total += len(limpa.split())
    return total


def checar_frontmatter(
    rel: str, caminho: Path, secao: str, vol: dict, ct: Contrato
) -> list[Violacao]:
    """Front-matter presente, completo, com status valido e coerente com o volume."""
    texto = caminho.read_text(encoding="utf-8")
    try:
        bloco, _ = extrair_bloco(texto)
        campos = parse_bloco(bloco)
    except FrontMatterInvalido as erro:
        return [Violacao(rel, 1, "frontmatter", str(erro))]

    saida: list[Violacao] = []
    for campo in ct.campos_frontmatter:
        if campo not in campos or campos[campo] in ("", None):
            saida.append(
                Violacao(rel, 1, "frontmatter-campo", f"campo obrigatorio ausente: {campo}")
            )
    if campos.get("status") not in ct.status_validos and "status" in campos:
        aceitos = ", ".join(ct.status_validos)
        saida.append(
            Violacao(
                rel, 1, "frontmatter-status",
                f"status {campos['status']!r} invalido; aceitos: {aceitos}",
            )
        )
    esperado = {"volume": vol["volume"], "volume_nome": vol["nome"], "tipo": vol["tipo"]}
    for campo, valor in esperado.items():
        if campo in campos and campos[campo] != valor:
            saida.append(
                Violacao(
                    rel, 1, "frontmatter-coerencia",
                    f"{campo}={campos[campo]!r} divergente do _VOLUME.yml ({valor!r})",
                )
            )
    if campos.get("secao") != secao:
        saida.append(
            Violacao(
                rel, 1, "frontmatter-coerencia",
                f"secao={campos.get('secao')!r} nao corresponde ao arquivo ({secao!r})",
            )
        )
    return saida


def checar_substancia(
    rel: str, linhas: list[str], inicio: int, secao: str, ct: Contrato
) -> list[Violacao]:
    """Prosa suficiente para a secao. Codigo nao conta."""
    minimo = ct.minimo_de(secao)
    total = palavras_de_prosa(linhas, inicio)
    if total < minimo:
        return [
            Violacao(
                rel, inicio, "substancia-curta",
                f"{total} palavras de prosa; minimo para {secao} e {minimo}",
            )
        ]
    return []


def sem_marcadores(rel: str, linhas: list[str], inicio: int, ct: Contrato) -> list[Violacao]:
    """Nenhum marcador de trabalho inacabado fora de codigo.

    Mencionar o marcador em fonte de codigo (`TODO`) e permitido de proposito:
    o volume 10-Anti-Patterns precisa poder falar sobre ele.
    """
    saida: list[Violacao] = []
    for n, linha in _fora_de_codigo(linhas, inicio):
        limpa = _CODE_SPAN.sub("", linha)
        for marcador in ct.marcadores_proibidos:
            if marcador in limpa:
                saida.append(
                    Violacao(rel, n, "marcador-proibido", f"marcador {marcador!r} no conteudo")
                )
    return saida
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd AI-ENGINEERING-OS && python -m pytest ferramentas/tests/test_regras_estrutura.py -q`
Expected: PASS — 10 passed

- [ ] **Step 6: Commit**

```bash
git add AI-ENGINEERING-OS/ferramentas
git commit -m "feat(aieos): regras estruturais - frontmatter, substancia, marcadores"
```

---

## Task 4: Regras de diagrama, exemplos e links

**Files:**
- Modify: `AI-ENGINEERING-OS/ferramentas/regras.py` (acrescenta funções ao fim)
- Test: `AI-ENGINEERING-OS/ferramentas/tests/test_regras_diagramas.py`

**Interfaces:**
- Consumes: tudo de Task 3.
- Produces (acrescentado a `regras.py`):
  - `TIPOS_MERMAID: frozenset[str]` — tokens aceitos na primeira linha de um bloco mermaid.
  - `def checar_mermaid(rel: str, linhas: list[str], inicio: int) -> list[Violacao]` — regras `mermaid-vazio`, `mermaid-tipo`, `mermaid-sem-descricao`, `mermaid-nao-fechado`.
  - `def checar_diagramas_obrigatorios(rel: str, texto_do_volume: str, tipo: str, ct: Contrato) -> list[Violacao]` — regra `diagrama-obrigatorio` (nível de volume).
  - `def checar_exemplos(raiz: Path, rel: str, linhas: list[str], inicio: int) -> list[Violacao]` — regras `exemplo-inexistente`, `exemplo-sem-teste`.
  - `def checar_links(raiz: Path, caminho: Path, rel: str, linhas: list[str], inicio: int) -> list[Violacao]` — regra `link-morto`.
  - Sintaxe de citação de exemplo, fixada aqui: `<!-- exemplo: exemplos/07-prompt-engine/prompt_template.py -->`. O teste esperado é `exemplos/<pasta>/tests/test_<stem>.py`.

- [ ] **Step 1: Write the failing test**

Create `AI-ENGINEERING-OS/ferramentas/tests/test_regras_diagramas.py`:

```python
"""Regras de diagrama, exemplo executavel e link interno."""
from ferramentas import contrato as C
from ferramentas import regras as R
from ferramentas.tests.conftest import FRONT_OK, PROSA

CABECA = FRONT_OK.format(vol="07", nome="PROMPT-ENGINE", tipo="ENGINE", secao="05-Diagramas")


def _regras(violacoes):
    return {v.regra for v in violacoes}


def _escrever(pasta, nome, miolo):
    arq = pasta / nome
    arq.write_text(CABECA + "\n" + miolo, encoding="utf-8")
    return arq


def test_mermaid_valido_com_descricao_passa(volume_engine):
    _, pasta = volume_engine
    arq = _escrever(
        pasta, "05-Diagramas.md",
        "# Diagramas\n\n```mermaid\nflowchart TD\n  A --> B\n```\n\n"
        "O diagrama mostra o fluxo de A para B.\n\n" + PROSA + "\n",
    )
    linhas, inicio = R.corpo_de(arq)
    assert R.checar_mermaid("05-Diagramas.md", linhas, inicio) == []


def test_mermaid_sem_paragrafo_descritivo_e_detectado(volume_engine):
    _, pasta = volume_engine
    arq = _escrever(
        pasta, "05-Diagramas.md",
        "# Diagramas\n\n```mermaid\nflowchart TD\n  A --> B\n```\n\n## Outra secao\n\n" + PROSA + "\n",
    )
    linhas, inicio = R.corpo_de(arq)
    assert "mermaid-sem-descricao" in _regras(R.checar_mermaid("05-Diagramas.md", linhas, inicio))


def test_mermaid_com_tipo_desconhecido_e_detectado(volume_engine):
    _, pasta = volume_engine
    arq = _escrever(
        pasta, "05-Diagramas.md",
        "# Diagramas\n\n```mermaid\ndiagramaInventado XY\n  A --> B\n```\n\nDescricao.\n\n" + PROSA,
    )
    linhas, inicio = R.corpo_de(arq)
    assert "mermaid-tipo" in _regras(R.checar_mermaid("05-Diagramas.md", linhas, inicio))


def test_mermaid_vazio_e_detectado(volume_engine):
    _, pasta = volume_engine
    arq = _escrever(pasta, "05-Diagramas.md", "# Diagramas\n\n```mermaid\n```\n\nDescricao.\n\n" + PROSA)
    linhas, inicio = R.corpo_de(arq)
    assert "mermaid-vazio" in _regras(R.checar_mermaid("05-Diagramas.md", linhas, inicio))


def test_mermaid_nao_fechado_e_detectado(volume_engine):
    _, pasta = volume_engine
    arq = _escrever(pasta, "05-Diagramas.md", "# Diagramas\n\n```mermaid\nflowchart TD\n  A --> B\n")
    linhas, inicio = R.corpo_de(arq)
    assert "mermaid-nao-fechado" in _regras(R.checar_mermaid("05-Diagramas.md", linhas, inicio))


def test_engine_sem_state_machine_e_detectado(volume_engine):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    texto = "```mermaid\nC4Context\n```\n```mermaid\nsequenceDiagram\n```\n"
    saida = R.checar_diagramas_obrigatorios("07-PROMPT-ENGINE", texto, "ENGINE", ct)
    assert "diagrama-obrigatorio" in _regras(saida)
    assert "stateDiagram-v2" in str(saida[0])


def test_engine_com_os_tres_diagramas_passa(volume_engine):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    texto = (
        "```mermaid\nC4Context\n```\n```mermaid\nsequenceDiagram\n```\n"
        "```mermaid\nstateDiagram-v2\n```\n"
    )
    assert R.checar_diagramas_obrigatorios("07-PROMPT-ENGINE", texto, "ENGINE", ct) == []


def test_biblioteca_nao_exige_diagrama(volume_engine):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    assert R.checar_diagramas_obrigatorios("40-TEMPLATES", "", "BIBLIOTECA", ct) == []


def test_exemplo_inexistente_e_detectado(volume_engine):
    raiz, pasta = volume_engine
    arq = _escrever(
        pasta, "12-Exemplos.md",
        "# Exemplos\n\n<!-- exemplo: exemplos/07-prompt-engine/fantasma.py -->\n\n" + PROSA,
    )
    linhas, inicio = R.corpo_de(arq)
    assert "exemplo-inexistente" in _regras(R.checar_exemplos(raiz, "12-Exemplos.md", linhas, inicio))


def test_exemplo_sem_teste_e_detectado(volume_engine):
    raiz, pasta = volume_engine
    alvo = raiz / "exemplos" / "07-prompt-engine"
    alvo.mkdir(parents=True)
    (alvo / "prompt_template.py").write_text("VALOR = 1\n", encoding="utf-8")
    arq = _escrever(
        pasta, "12-Exemplos.md",
        "# Exemplos\n\n<!-- exemplo: exemplos/07-prompt-engine/prompt_template.py -->\n\n" + PROSA,
    )
    linhas, inicio = R.corpo_de(arq)
    assert "exemplo-sem-teste" in _regras(R.checar_exemplos(raiz, "12-Exemplos.md", linhas, inicio))


def test_exemplo_com_teste_passa(volume_engine):
    raiz, pasta = volume_engine
    alvo = raiz / "exemplos" / "07-prompt-engine"
    (alvo / "tests").mkdir(parents=True)
    (alvo / "prompt_template.py").write_text("VALOR = 1\n", encoding="utf-8")
    (alvo / "tests" / "test_prompt_template.py").write_text("def test_x():\n    pass\n", encoding="utf-8")
    arq = _escrever(
        pasta, "12-Exemplos.md",
        "# Exemplos\n\n<!-- exemplo: exemplos/07-prompt-engine/prompt_template.py -->\n\n" + PROSA,
    )
    linhas, inicio = R.corpo_de(arq)
    assert R.checar_exemplos(raiz, "12-Exemplos.md", linhas, inicio) == []


def test_link_morto_e_detectado(volume_engine):
    raiz, pasta = volume_engine
    arq = _escrever(
        pasta, "18-Referencias-Cruzadas.md",
        "# Referencias\n\nVeja [Volume 99](../99-INEXISTENTE/01-Introducao.md).\n\n" + PROSA,
    )
    linhas, inicio = R.corpo_de(arq)
    assert "link-morto" in _regras(
        R.checar_links(raiz, arq, "18-Referencias-Cruzadas.md", linhas, inicio)
    )


def test_link_vivo_e_externo_passam(volume_engine):
    raiz, pasta = volume_engine
    arq = _escrever(
        pasta, "18-Referencias-Cruzadas.md",
        "# Referencias\n\nVeja [Arquitetura](04-Arquitetura.md) e "
        "[Mermaid](https://mermaid.js.org/) e [ancora](#secao).\n\n" + PROSA,
    )
    linhas, inicio = R.corpo_de(arq)
    assert R.checar_links(raiz, arq, "18-Referencias-Cruzadas.md", linhas, inicio) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd AI-ENGINEERING-OS && python -m pytest ferramentas/tests/test_regras_diagramas.py -q`
Expected: FAIL — `AttributeError: module 'ferramentas.regras' has no attribute 'checar_mermaid'`

- [ ] **Step 3: Append to `regras.py`**

```python
TIPOS_MERMAID = frozenset(
    {
        "flowchart", "graph", "sequenceDiagram", "stateDiagram", "stateDiagram-v2",
        "erDiagram", "classDiagram", "journey", "gantt", "gitGraph", "mindmap",
        "timeline", "quadrantChart", "block-beta", "requirementDiagram",
        "C4Context", "C4Container", "C4Component", "C4Dynamic", "C4Deployment",
    }
)

_ABRE_MERMAID = re.compile(r"^\s*```mermaid\s*$")
_CITA_EXEMPLO = re.compile(r"<!--\s*exemplo:\s*([^\s>]+?)\s*-->")
_LINK = re.compile(r"\[[^\]]*\]\(\s*([^)\s#]+)(?:#[^)]*)?\s*\)")


def _blocos_mermaid(linhas: list[str], inicio: int) -> list[tuple[int, int | None, list[str]]]:
    """Devolve [(linha_da_abertura, linha_do_fechamento_ou_None, linhas_internas)]."""
    blocos: list[tuple[int, int | None, list[str]]] = []
    n = inicio
    while n <= len(linhas):
        if _ABRE_MERMAID.match(linhas[n - 1]):
            interno: list[str] = []
            fecha = None
            m = n + 1
            while m <= len(linhas):
                if _FENCE.match(linhas[m - 1]):
                    fecha = m
                    break
                interno.append(linhas[m - 1])
                m += 1
            blocos.append((n, fecha, interno))
            n = (fecha or len(linhas)) + 1
            continue
        n += 1
    return blocos


def checar_mermaid(rel: str, linhas: list[str], inicio: int) -> list[Violacao]:
    """Todo bloco mermaid e tipado, nao vazio, fechado e seguido de descricao.

    A exigencia de descricao vem do CLAUDE.md: 'diagramas sempre em Mermaid e
    seguidos de descricao textual'. Aqui ela deixa de ser recomendacao.
    """
    saida: list[Violacao] = []
    for abre, fecha, interno in _blocos_mermaid(linhas, inicio):
        if fecha is None:
            saida.append(Violacao(rel, abre, "mermaid-nao-fechado", "bloco mermaid sem '```'"))
            continue
        uteis = [ln.strip() for ln in interno if ln.strip()]
        if not uteis:
            saida.append(Violacao(rel, abre, "mermaid-vazio", "bloco mermaid sem conteudo"))
            continue
        token = uteis[0].split()[0].rstrip(":")
        if token not in TIPOS_MERMAID:
            aceitos = ", ".join(sorted(TIPOS_MERMAID))
            saida.append(
                Violacao(
                    rel, abre + 1, "mermaid-tipo",
                    f"tipo de diagrama {token!r} desconhecido; aceitos: {aceitos}",
                )
            )
        seguinte = next(
            (ln.strip() for ln in linhas[fecha:] if ln.strip()), ""
        )
        if not seguinte or seguinte.startswith(("#", "```", "|", "-", "*", "<!--")):
            saida.append(
                Violacao(
                    rel, fecha, "mermaid-sem-descricao",
                    "diagrama sem paragrafo descritivo imediatamente apos o bloco",
                )
            )
    return saida


def checar_diagramas_obrigatorios(
    rel: str, texto_do_volume: str, tipo: str, ct: Contrato
) -> list[Violacao]:
    """O volume inteiro precisa conter os diagramas exigidos pelo seu tipo."""
    saida: list[Violacao] = []
    for exigido in ct.diagramas_de(tipo):
        if exigido not in texto_do_volume:
            saida.append(
                Violacao(
                    rel, 0, "diagrama-obrigatorio",
                    f"tipo {tipo} exige um diagrama {exigido} em algum lugar do volume",
                )
            )
    return saida


def checar_exemplos(raiz: Path, rel: str, linhas: list[str], inicio: int) -> list[Violacao]:
    """Exemplo citado existe como arquivo e tem teste correspondente.

    Sintaxe da citacao: <!-- exemplo: exemplos/<pasta>/<arquivo>.py -->
    Teste esperado:     exemplos/<pasta>/tests/test_<arquivo>.py
    """
    saida: list[Violacao] = []
    for n, linha in _fora_de_codigo(linhas, inicio):
        for citado in _CITA_EXEMPLO.findall(linha):
            alvo = raiz / citado
            if not alvo.exists():
                saida.append(
                    Violacao(rel, n, "exemplo-inexistente", f"exemplo citado nao existe: {citado}")
                )
                continue
            teste = alvo.parent / "tests" / f"test_{alvo.stem}.py"
            if not teste.exists():
                saida.append(
                    Violacao(
                        rel, n, "exemplo-sem-teste",
                        f"exemplo {citado} nao tem teste em {teste.relative_to(raiz).as_posix()}",
                    )
                )
    return saida


def checar_links(
    raiz: Path, caminho: Path, rel: str, linhas: list[str], inicio: int
) -> list[Violacao]:
    """Todo link relativo resolve. Links http(s)/mailto e ancoras sao ignorados."""
    saida: list[Violacao] = []
    for n, linha in _fora_de_codigo(linhas, inicio):
        for destino in _LINK.findall(linha):
            if destino.startswith(("http://", "https://", "mailto:", "#")):
                continue
            alvo = (caminho.parent / destino).resolve()
            if not alvo.exists():
                saida.append(Violacao(rel, n, "link-morto", f"link nao resolve: {destino}"))
    return saida
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd AI-ENGINEERING-OS && python -m pytest ferramentas/tests/test_regras_diagramas.py -q`
Expected: PASS — 13 passed

- [ ] **Step 5: Commit**

```bash
git add AI-ENGINEERING-OS/ferramentas
git commit -m "feat(aieos): regras de mermaid, exemplo executavel e link interno"
```

---

## Task 5: `validar.py` — orquestração, cross-refs e CLI

**Files:**
- Create: `AI-ENGINEERING-OS/ferramentas/validar.py`
- Test: `AI-ENGINEERING-OS/ferramentas/tests/test_validar.py`

**Interfaces:**
- Consumes: `contrato.carregar`, `contrato.Contrato`, `contrato.ContratoInvalido`, `frontmatter.ler_volume_yml`, `regras.*`, `modelo.Violacao`.
- Produces:
  - `def volumes_existentes(raiz: Path) -> list[str]` — ids de 2 dígitos das pastas `NN-NOME` presentes, ordenados.
  - `def validar_volume(raiz: Path, vol_id: str, ct: Contrato) -> list[Violacao]` — regras `volume-yml`, `volume-tipo`, `secao-ausente` mais tudo de Tasks 3–4.
  - `def validar_tudo(raiz: Path, ct: Contrato) -> list[Violacao]` — só volumes existentes; volume não materializado não é violação.
  - `def validar_cross_refs(raiz: Path, ct: Contrato) -> list[Violacao]` — regras `depende-de-inexistente`, `depende-de-ciclo`.
  - `def main(argv: list[str] | None = None) -> int` — exit 0 sem violação, 1 com violação, 2 em erro de uso/contrato.

- [ ] **Step 1: Write the failing test**

Create `AI-ENGINEERING-OS/ferramentas/tests/test_validar.py`:

```python
"""Testa a orquestracao dos gates e a CLI."""
from ferramentas import contrato as C
from ferramentas import validar as V


def _regras(violacoes):
    return {v.regra for v in violacoes}


def _dep(pasta, valor):
    yml = pasta / "_VOLUME.yml"
    texto = yml.read_text(encoding="utf-8").replace("depende_de: []", f"depende_de: {valor}")
    yml.write_text(texto, encoding="utf-8")


def test_volume_completo_e_valido(volume_engine):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    assert V.validar_volume(raiz, "07", ct) == []


def test_secao_obrigatoria_ausente_e_detectada(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    (pasta / "14-Metricas.md").unlink()
    saida = V.validar_volume(raiz, "07", ct)
    assert "secao-ausente" in _regras(saida)
    assert "14-Metricas" in str(saida[0])


def test_volume_yml_ausente_e_detectado(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    (pasta / "_VOLUME.yml").unlink()
    assert "volume-yml" in _regras(V.validar_volume(raiz, "07", ct))


def test_tipo_invalido_no_volume_yml_lista_os_aceitos(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    yml = pasta / "_VOLUME.yml"
    yml.write_text(
        'volume: "07"\nnome: PROMPT-ENGINE\ntipo: INVENTADO\nstatus: RASCUNHO\ndepende_de: []\n',
        encoding="utf-8",
    )
    saida = V.validar_volume(raiz, "07", ct)
    assert "volume-tipo" in _regras(saida)
    assert "ENGINE" in str(saida[0])


def test_volumes_existentes_ignora_pasta_nao_volume(volume_engine):
    raiz, _ = volume_engine
    (raiz / "ferramentas").mkdir(exist_ok=True)
    assert V.volumes_existentes(raiz) == ["07"]


def test_validar_tudo_nao_cobra_volume_nao_materializado(volume_engine):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    assert V.validar_tudo(raiz, ct) == []


def test_depende_de_inexistente_e_detectado(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    _dep(pasta, '["99"]')
    assert "depende-de-inexistente" in _regras(V.validar_cross_refs(raiz, ct))


def test_ciclo_em_depende_de_e_detectado(volume_engine):
    raiz, pasta7 = volume_engine
    ct = C.carregar(raiz)
    pasta28 = raiz / "28-PROMPT-COMPILER"
    pasta28.mkdir()
    (pasta28 / "_VOLUME.yml").write_text(
        'volume: "28"\nnome: PROMPT-COMPILER\ntipo: ENGINE\n'
        'status: RASCUNHO\ndepende_de: ["07"]\n',
        encoding="utf-8",
    )
    _dep(pasta7, '["28"]')
    saida = V.validar_cross_refs(raiz, ct)
    assert "depende-de-ciclo" in _regras(saida)


def test_dependencia_acicilica_passa(volume_engine):
    raiz, pasta7 = volume_engine
    ct = C.carregar(raiz)
    pasta1 = raiz / "01-FUNDACAO"
    pasta1.mkdir()
    (pasta1 / "_VOLUME.yml").write_text(
        'volume: "01"\nnome: FUNDACAO\ntipo: GOVERNANCA\nstatus: RASCUNHO\ndepende_de: []\n',
        encoding="utf-8",
    )
    _dep(pasta7, '["01"]')
    assert V.validar_cross_refs(raiz, ct) == []


def test_cli_volume_valido_retorna_zero(volume_engine, capsys, monkeypatch):
    raiz, _ = volume_engine
    monkeypatch.chdir(raiz)
    assert V.main(["07"]) == 0
    assert "ok" in capsys.readouterr().out.lower()


def test_cli_volume_invalido_retorna_um(volume_engine, capsys, monkeypatch):
    raiz, pasta = volume_engine
    (pasta / "14-Metricas.md").unlink()
    monkeypatch.chdir(raiz)
    assert V.main(["07"]) == 1
    assert "secao-ausente" in capsys.readouterr().out


def test_cli_volume_desconhecido_retorna_dois(volume_engine, monkeypatch):
    raiz, _ = volume_engine
    monkeypatch.chdir(raiz)
    assert V.main(["99"]) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd AI-ENGINEERING-OS && python -m pytest ferramentas/tests/test_validar.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'ferramentas.validar'`

- [ ] **Step 3: Write `validar.py`**

```python
"""Os gates de qualidade da plataforma.

Uso:
    python -m ferramentas.validar 07          # um volume
    python -m ferramentas.validar --tudo      # todos os volumes materializados
    python -m ferramentas.validar --cross-refs

Codigos de saida: 0 sem violacao, 1 com violacao, 2 em erro de uso ou contrato.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from . import regras as R
from .contrato import Contrato, ContratoInvalido, carregar
from .frontmatter import FrontMatterInvalido, ler_volume_yml
from .modelo import Violacao

# O prefixo 00 e reservado para 00-INTRODUCAO, que nao e volume. Aceitar \d{2}
# aqui fazia volumes_existentes() devolver "00" e derrubava --tudo/--cross-refs.
PASTA_VOLUME = re.compile(r"^(0[1-9]|[1-9][0-9])-[A-Z0-9-]+$")


def volumes_existentes(raiz: Path) -> list[str]:
    """Ids dos volumes que ja foram materializados como pasta."""
    achados = []
    for item in raiz.iterdir():
        if item.is_dir():
            casado = PASTA_VOLUME.match(item.name)
            if casado:
                achados.append(casado.group(1))
    return sorted(achados)


def _pasta_de(raiz: Path, vol_id: str, ct: Contrato) -> Path:
    return raiz / f"{vol_id}-{ct.volume(vol_id)['nome']}"


def validar_volume(raiz: Path, vol_id: str, ct: Contrato) -> list[Violacao]:
    """Aplica todas as regras de um volume. Nao levanta por conteudo ruim."""
    meta = ct.volume(vol_id)
    pasta = _pasta_de(raiz, vol_id, ct)
    rel_pasta = pasta.name
    yml = pasta / "_VOLUME.yml"
    if not yml.exists():
        return [Violacao(f"{rel_pasta}/_VOLUME.yml", 0, "volume-yml", "_VOLUME.yml ausente")]
    try:
        vol = ler_volume_yml(yml)
    except FrontMatterInvalido as erro:
        return [Violacao(f"{rel_pasta}/_VOLUME.yml", 0, "volume-yml", str(erro))]

    faltando = [c for c in ("volume", "nome", "tipo", "status") if c not in vol]
    if faltando:
        return [
            Violacao(
                f"{rel_pasta}/_VOLUME.yml", 0, "volume-yml",
                f"campos ausentes: {', '.join(faltando)}",
            )
        ]
    if vol["tipo"] not in ct.tipos:
        aceitos = ", ".join(sorted(ct.tipos))
        return [
            Violacao(
                f"{rel_pasta}/_VOLUME.yml", 0, "volume-tipo",
                f"tipo {vol['tipo']!r} invalido; aceitos: {aceitos}",
            )
        ]
    if vol["tipo"] != meta["tipo"]:
        return [
            Violacao(
                f"{rel_pasta}/_VOLUME.yml", 0, "volume-tipo",
                f"tipo {vol['tipo']!r} divergente do contrato ({meta['tipo']!r})",
            )
        ]

    saida: list[Violacao] = []
    texto_do_volume: list[str] = []
    for secao in ct.secoes_de(vol["tipo"]):
        arq = pasta / f"{secao}.md"
        rel = f"{rel_pasta}/{secao}.md"
        if not arq.exists():
            saida.append(Violacao(rel, 0, "secao-ausente", f"secao obrigatoria ausente: {secao}"))
            continue
        texto_do_volume.append(arq.read_text(encoding="utf-8"))
        linhas, inicio = R.corpo_de(arq)
        saida.extend(R.checar_frontmatter(rel, arq, secao, vol, ct))
        saida.extend(R.checar_substancia(rel, linhas, inicio, secao, ct))
        saida.extend(R.sem_marcadores(rel, linhas, inicio, ct))
        saida.extend(R.checar_mermaid(rel, linhas, inicio))
        saida.extend(R.checar_exemplos(raiz, rel, linhas, inicio))
        saida.extend(R.checar_links(raiz, arq, rel, linhas, inicio))
    saida.extend(
        R.checar_diagramas_obrigatorios(rel_pasta, "\n".join(texto_do_volume), vol["tipo"], ct)
    )
    return saida


def validar_tudo(raiz: Path, ct: Contrato) -> list[Violacao]:
    """Valida apenas volumes materializados. Volume pendente nao e violacao."""
    saida: list[Violacao] = []
    for vol_id in volumes_existentes(raiz):
        saida.extend(validar_volume(raiz, vol_id, ct))
    return saida


def validar_cross_refs(raiz: Path, ct: Contrato) -> list[Violacao]:
    """`depende_de` aponta para volume declarado e o grafo e aciclico.

    `depende_de` e pre-requisito de leitura, nao 'assunto vizinho' - a relacao
    bidirecional vive em 18-Referencias-Cruzadas.md e nao entra neste grafo.
    """
    saida: list[Violacao] = []
    grafo: dict[str, list[str]] = {}
    for vol_id in volumes_existentes(raiz):
        pasta = _pasta_de(raiz, vol_id, ct)
        yml = pasta / "_VOLUME.yml"
        rel = f"{pasta.name}/_VOLUME.yml"
        if not yml.exists():
            continue
        try:
            vol = ler_volume_yml(yml)
        except FrontMatterInvalido:
            continue
        deps = vol.get("depende_de", []) or []
        if isinstance(deps, str):
            deps = [deps]
        validas = []
        for dep in deps:
            if dep not in ct.volumes:
                saida.append(
                    Violacao(rel, 0, "depende-de-inexistente", f"volume {dep!r} nao existe")
                )
            else:
                validas.append(dep)
        grafo[vol_id] = validas

    VISITANDO, PRONTO = 1, 2
    estado: dict[str, int] = {}

    def desce(no: str, caminho: list[str]) -> None:
        estado[no] = VISITANDO
        for viz in grafo.get(no, ()):
            if estado.get(viz) == VISITANDO:
                ciclo = " -> ".join([*caminho, no, viz])
                saida.append(
                    Violacao(
                        f"{no}/_VOLUME.yml", 0, "depende-de-ciclo",
                        f"ciclo em depende_de: {ciclo}",
                    )
                )
            elif viz not in estado:
                desce(viz, [*caminho, no])
        estado[no] = PRONTO

    for no in sorted(grafo):
        if no not in estado:
            desce(no, [])
    return saida


def _reportar(violacoes: list[Violacao], rotulo: str) -> int:
    if not violacoes:
        print(f"ok: {rotulo} sem violacoes")
        return 0
    for v in violacoes:
        print(v)
    print(f"\nFALHA: {len(violacoes)} violacao(oes) em {rotulo}")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="validar", description="Gates da AI-ENGINEERING-OS")
    parser.add_argument("volume", nargs="?", help="id de 2 digitos, ex.: 07")
    parser.add_argument("--tudo", action="store_true", help="valida todos os volumes existentes")
    parser.add_argument("--cross-refs", action="store_true", help="checa dependencias e ciclos")
    parser.add_argument("--raiz", default=".", help="raiz da plataforma (default: .)")
    args = parser.parse_args(argv)

    raiz = Path(args.raiz).resolve()
    try:
        ct = carregar(raiz)
    except ContratoInvalido as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 2

    try:
        if args.cross_refs:
            return _reportar(validar_cross_refs(raiz, ct), "referencias cruzadas")
        if args.tudo:
            return _reportar(validar_tudo(raiz, ct), "acervo")
        if not args.volume:
            parser.print_usage(sys.stderr)
            return 2
        return _reportar(validar_volume(raiz, args.volume, ct), f"volume {args.volume}")
    except ContratoInvalido as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd AI-ENGINEERING-OS && python -m pytest ferramentas/tests/test_validar.py -q`
Expected: PASS — 12 passed

- [ ] **Step 5: Commit**

```bash
git add AI-ENGINEERING-OS/ferramentas
git commit -m "feat(aieos): validar.py - orquestracao dos gates, cross-refs e CLI"
```

---

## Task 6: `status.py` — leitura de estado do acervo

**Files:**
- Create: `AI-ENGINEERING-OS/ferramentas/status.py`
- Test: `AI-ENGINEERING-OS/ferramentas/tests/test_status.py`

**Interfaces:**
- Consumes: `contrato.carregar`, `validar.volumes_existentes`, `frontmatter.ler_volume_yml`.
- Produces:
  - `class EstadoVolume` — `dataclass(frozen=True, slots=True)`: `vol_id: str`, `nome: str`, `tipo: str`, `status: str`, `secoes_presentes: int`, `secoes_esperadas: int`, `perecivel: bool`, `nota_auditoria: float | None`.
  - `def levantar(raiz: Path, ct: Contrato) -> list[EstadoVolume]` — ordenado por `vol_id`; volume sem pasta entra com `status="PENDENTE"` e `secoes_presentes=0`.
  - `def nota_da_ultima_auditoria(raiz: Path, vol_id: str) -> float | None` — lê o `auditorias/VOL-NN-auditoria-*.md` mais recente por nome e extrai a linha `media: N.N`; devolve `None` se não houver auditoria.
  - `def tabela(estados: list[EstadoVolume]) -> str` — tabela markdown.
  - `def main(argv: list[str] | None = None) -> int` — sempre 0 (é leitura), 2 se contrato inválido.
- Nota: `PENDENTE` aqui é estado derivado (pasta não existe), não um valor gravável de `status` no front-matter — os graváveis continuam sendo só os três do contrato.

- [ ] **Step 1: Write the failing test**

Create `AI-ENGINEERING-OS/ferramentas/tests/test_status.py`:

```python
"""Testa o levantamento de estado do acervo."""
from ferramentas import contrato as C
from ferramentas import status as S


def _por_id(estados):
    return {e.vol_id: e for e in estados}


def test_volume_materializado_aparece_com_seu_status(volume_engine):
    raiz, _ = volume_engine
    estados = _por_id(S.levantar(raiz, C.carregar(raiz)))
    assert estados["07"].status == "RASCUNHO"
    assert estados["07"].secoes_presentes == 18
    assert estados["07"].secoes_esperadas == 18


def test_volume_sem_pasta_e_pendente(volume_engine):
    raiz, _ = volume_engine
    estados = _por_id(S.levantar(raiz, C.carregar(raiz)))
    assert estados["13"].status == "PENDENTE"
    assert estados["13"].secoes_presentes == 0


def test_todos_os_42_aparecem(volume_engine):
    raiz, _ = volume_engine
    assert len(S.levantar(raiz, C.carregar(raiz))) == 42


def test_secao_faltante_reduz_a_contagem(volume_engine):
    raiz, pasta = volume_engine
    (pasta / "14-Metricas.md").unlink()
    estados = _por_id(S.levantar(raiz, C.carregar(raiz)))
    assert estados["07"].secoes_presentes == 17


def test_perecivel_vem_do_contrato(volume_engine):
    raiz, _ = volume_engine
    estados = _por_id(S.levantar(raiz, C.carregar(raiz)))
    assert estados["26"].perecivel is True
    assert estados["07"].perecivel is False


def test_nota_da_auditoria_e_lida(volume_engine):
    raiz, _ = volume_engine
    pasta = raiz / "auditorias"
    pasta.mkdir()
    (pasta / "VOL-07-auditoria-2026-07-29.md").write_text(
        "# Auditoria\n\nmedia: 8.4\n", encoding="utf-8"
    )
    estados = _por_id(S.levantar(raiz, C.carregar(raiz)))
    assert estados["07"].nota_auditoria == 8.4


def test_sem_auditoria_a_nota_e_none(volume_engine):
    raiz, _ = volume_engine
    estados = _por_id(S.levantar(raiz, C.carregar(raiz)))
    assert estados["07"].nota_auditoria is None


def test_auditoria_mais_recente_vence(volume_engine):
    raiz, _ = volume_engine
    pasta = raiz / "auditorias"
    pasta.mkdir()
    (pasta / "VOL-07-auditoria-2026-07-28.md").write_text("media: 6.0\n", encoding="utf-8")
    (pasta / "VOL-07-auditoria-2026-07-29.md").write_text("media: 9.1\n", encoding="utf-8")
    assert S.nota_da_ultima_auditoria(raiz, "07") == 9.1


def test_tabela_tem_uma_linha_por_volume(volume_engine):
    raiz, _ = volume_engine
    saida = S.tabela(S.levantar(raiz, C.carregar(raiz)))
    assert saida.count("\n| ") >= 42
    assert "PROMPT-ENGINE" in saida


def test_cli_retorna_zero(volume_engine, capsys, monkeypatch):
    raiz, _ = volume_engine
    monkeypatch.chdir(raiz)
    assert S.main([]) == 0
    assert "PROMPT-ENGINE" in capsys.readouterr().out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd AI-ENGINEERING-OS && python -m pytest ferramentas/tests/test_status.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'ferramentas.status'`

- [ ] **Step 3: Write `status.py`**

```python
"""Estado do acervo: o que esta pronto, pendente ou reprovado.

Leitura pura - nunca escreve. `PENDENTE` e estado derivado (a pasta do volume
nao existe), nao um valor gravavel de `status`.

Uso: python -m ferramentas.status
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from .contrato import Contrato, ContratoInvalido, carregar
from .frontmatter import FrontMatterInvalido, ler_volume_yml
from .validar import volumes_existentes

PENDENTE = "PENDENTE"
_MEDIA = re.compile(r"^\s*media:\s*([0-9]+(?:[.,][0-9]+)?)\s*$", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class EstadoVolume:
    vol_id: str
    nome: str
    tipo: str
    status: str
    secoes_presentes: int
    secoes_esperadas: int
    perecivel: bool
    nota_auditoria: float | None


def nota_da_ultima_auditoria(raiz: Path, vol_id: str) -> float | None:
    """Media da auditoria mais recente. O nome do arquivo carrega a data ISO."""
    pasta = raiz / "auditorias"
    if not pasta.is_dir():
        return None
    achados = sorted(pasta.glob(f"VOL-{vol_id}-auditoria-*.md"))
    if not achados:
        return None
    casado = _MEDIA.search(achados[-1].read_text(encoding="utf-8"))
    return float(casado.group(1).replace(",", ".")) if casado else None


def levantar(raiz: Path, ct: Contrato) -> list[EstadoVolume]:
    """Estado dos 42 volumes declarados no contrato."""
    materializados = set(volumes_existentes(raiz))
    estados: list[EstadoVolume] = []
    for vol_id in sorted(ct.volumes):
        meta = ct.volume(vol_id)
        esperadas = len(ct.secoes_de(meta["tipo"]))
        if vol_id not in materializados:
            estados.append(
                EstadoVolume(vol_id, meta["nome"], meta["tipo"], PENDENTE, 0, esperadas,
                             meta["perecivel"], None)
            )
            continue
        pasta = raiz / f"{vol_id}-{meta['nome']}"
        presentes = sum(1 for s in ct.secoes_de(meta["tipo"]) if (pasta / f"{s}.md").exists())
        status = PENDENTE
        yml = pasta / "_VOLUME.yml"
        if yml.exists():
            try:
                status = str(ler_volume_yml(yml).get("status", PENDENTE))
            except FrontMatterInvalido:
                status = "RASCUNHO"
        estados.append(
            EstadoVolume(vol_id, meta["nome"], meta["tipo"], status, presentes, esperadas,
                         meta["perecivel"], nota_da_ultima_auditoria(raiz, vol_id))
        )
    return estados


def tabela(estados: list[EstadoVolume]) -> str:
    """Tabela markdown do acervo, mais um resumo por status."""
    linhas = [
        "| Vol | Nome | Tipo | Status | Secoes | Auditoria | Perecivel |",
        "|---|---|---|---|---|---|---|",
    ]
    for e in estados:
        nota = f"{e.nota_auditoria:.1f}" if e.nota_auditoria is not None else "-"
        marca = "sim" if e.perecivel else "-"
        linhas.append(
            f"| {e.vol_id} | {e.nome} | {e.tipo} | {e.status} | "
            f"{e.secoes_presentes}/{e.secoes_esperadas} | {nota} | {marca} |"
        )
    contagem: dict[str, int] = {}
    for e in estados:
        contagem[e.status] = contagem.get(e.status, 0) + 1
    resumo = "  ".join(f"{k}={v}" for k, v in sorted(contagem.items()))
    return "\n".join(linhas) + f"\n\nResumo: {resumo}\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="status", description="Estado do acervo")
    parser.add_argument("--raiz", default=".")
    args = parser.parse_args(argv)
    try:
        ct = carregar(Path(args.raiz).resolve())
    except ContratoInvalido as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 2
    print(tabela(levantar(Path(args.raiz).resolve(), ct)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd AI-ENGINEERING-OS && python -m pytest ferramentas/tests/test_status.py -q`
Expected: PASS — 10 passed

- [ ] **Step 5: Commit**

```bash
git add AI-ENGINEERING-OS/ferramentas
git commit -m "feat(aieos): status.py - estado do acervo com nota de auditoria"
```

---

## Task 7: `scaffold.py` e `exportar.py`

**Files:**
- Create: `AI-ENGINEERING-OS/ferramentas/scaffold.py`, `AI-ENGINEERING-OS/ferramentas/exportar.py`
- Test: `AI-ENGINEERING-OS/ferramentas/tests/test_scaffold.py`, `AI-ENGINEERING-OS/ferramentas/tests/test_exportar.py`

**Interfaces produzidas:**
- `scaffold.criar_volumes(raiz: Path, ct: Contrato) -> list[str]` — cria `NN-NOME/` e `_VOLUME.yml` para cada volume do contrato que ainda não tem pasta; devolve os ids criados. **Idempotente: nunca sobrescreve `_VOLUME.yml` existente.** O `_VOLUME.yml` gerado tem `volume`, `nome`, `tipo`, `status: RASCUNHO`, `perecivel`, `depende_de: []`, `escopo` (uma linha vinda de `contrato.json`→`volumes[id].escopo`, ou string vazia se ausente).
- `scaffold.main(argv) -> int`
- `exportar.montar_nav(raiz: Path, ct: Contrato) -> list[dict]` — navegação MkDocs: `00-INTRODUCAO` primeiro, depois cada volume materializado com suas seções existentes em ordem.
- `exportar.gerar_mkdocs(raiz: Path, ct: Contrato) -> str` — devolve o YAML e grava `raiz/mkdocs.yml`. Escreve YAML à mão (stdlib): `site_name`, `theme: name: material`, `markdown_extensions` com `pymdownx.superfences` configurado para mermaid, `nav`.
- `exportar.main(argv) -> int` — 0 sempre que gerou; imprime aviso explícito `aviso: mkdocs nao encontrado, build nao validado` quando `shutil.which("mkdocs")` é `None`, e roda `mkdocs build --strict` quando existe (exit 1 se o build falhar).

**Testes exigidos:**
- `test_scaffold_cria_os_42`, `test_scaffold_e_idempotente` (segunda chamada devolve `[]` e não altera mtime do yml), `test_scaffold_nao_sobrescreve_yml_editado`, `test_volume_yml_gerado_e_valido_para_o_parser`.
- `test_nav_comeca_por_introducao`, `test_nav_ignora_volume_nao_materializado`, `test_nav_lista_secoes_em_ordem`, `test_mkdocs_yml_tem_superfences_mermaid`, `test_cli_avisa_quando_mkdocs_ausente` (com `monkeypatch.setattr(exportar.shutil, "which", lambda _: None)`).

- [ ] **Step 1:** Escreva `test_scaffold.py` e `test_exportar.py` com os testes acima.
- [ ] **Step 2:** Rode — `cd AI-ENGINEERING-OS && python -m pytest ferramentas/tests/test_scaffold.py ferramentas/tests/test_exportar.py -q`. Expected: FAIL, `ModuleNotFoundError`.
- [ ] **Step 3:** Implemente `scaffold.py` e `exportar.py` conforme as interfaces.
- [ ] **Step 4:** Rode de novo. Expected: PASS.
- [ ] **Step 5:** Commit — `git commit -m "feat(aieos): scaffold idempotente e exportacao MkDocs"`

---

## Task 8: Esqueleto da plataforma e `00-INTRODUCAO`

Esta task fecha `test_convencoes_nao_derivou`, que está vermelho desde a Task 2.

**Files:**
- Create: `AI-ENGINEERING-OS/CLAUDE.md`, `README.md`, `CHANGELOG.md`, `ROADMAP.md`, `CONTRIBUTING.md`, `LICENSE`
- Create: `AI-ENGINEERING-OS/00-INTRODUCAO/{Prefacio,Como-Utilizar,Glossario,Convencoes,Arquitetura-Geral}.md`
- Run: `scaffold.py` → 42 pastas com `_VOLUME.yml`

**Conteúdo obrigatório de cada arquivo:**

- **`CLAUDE.md`** (contexto local da plataforma, não da raiz): missão; modelo criador/auditor; a regra de que `contrato.json` é a fonte única; os três gates e a ordem em que rodam; os cinco comandos; **a proibição de gravar `PRONTO` com gate vermelho**; a proibição de inventar framework/número/fonte; o aviso de que a raiz do repositório é outro projeto (conciliação financeira) e não deve ser tocada.
- **`Convencoes.md`** — o contrato em forma humana. Precisa conter, na ordem: (1) as 18 seções e o que cada uma responde; (2) **a tabela de tipos no formato exato que o teste espera** — linha começando com `` | `TIPO` `` e a segunda célula listando os ids de 2 dígitos daquele tipo, coerente com `contrato.json`; (3) o esquema de front-matter com exemplo; (4) a Definição de PRONTO (4 critérios); (5) regra de diagrama (Mermaid + parágrafo descritivo obrigatório logo após o bloco); (6) regra de código (`<!-- exemplo: ... -->` + teste obrigatório); (7) regra dos marcadores proibidos e o escape por code span; (8) regra de volume perecível.
- **`Prefacio.md`** — por que a plataforma existe, para quem, e o que ela deliberadamente não é.
- **`Como-Utilizar.md`** — os 5 comandos com exemplo de invocação, o ciclo de produção de um volume, e como rodar os gates na mão.
- **`Glossario.md`** — termos usados de forma consistente pelo acervo (volume, seção, tipo, gate, contrato, perecível, padrão-ouro, prompt template, registry, avaliador).
- **`Arquitetura-Geral.md`** — visão da plataforma com o diagrama de fluxo dos gates (o mesmo do spec §8), cada bloco Mermaid seguido de parágrafo.
- **`ROADMAP.md`** — os 41 volumes pendentes com seu tipo; **e a seção "Metas numéricas do autor" registrando explicitamente que "8.000+ páginas / 2.000+ prompts / 300+ agentes / 500+ exemplos" são estimativa e não critério de aceite** (spec §7.2).
- **`CHANGELOG.md`** — entrada `2026-07-29` com: máquina construída, piloto 07 em produção, contrato v1.0.0.
- **`README.md`** — o que é, estrutura, como validar, link para o spec e para `Convencoes.md`.
- **`CONTRIBUTING.md`** — como propor volume novo, como o gate reprova, o que nunca fazer.
- **`LICENSE`** — MIT com titular `Alpha Contabilidade`.

- [ ] **Step 1:** Escreva os 6 arquivos de raiz e os 5 de `00-INTRODUCAO`.
- [ ] **Step 2:** Rode o scaffold — `cd AI-ENGINEERING-OS && python -m ferramentas.scaffold`. Expected: cria 41 pastas (07 já existe se a Task 10+ rodou antes; a ordem correta é scaffold antes).
- [ ] **Step 3:** Rode `python -m pytest ferramentas/tests -q`. Expected: **toda a suíte verde, incluindo `test_convencoes_nao_derivou`.** Se esse teste falhar, corrija `Convencoes.md` — não o teste.
- [ ] **Step 4:** Rode `python -m ferramentas.status`. Expected: 42 linhas, 41 `PENDENTE`/`RASCUNHO`.
- [ ] **Step 5:** Commit — `git commit -m "docs(aieos): esqueleto, convencoes e os 42 volumes registrados"`

---

## Task 9: Bibliotecas transversais e o backlog honesto

**Files:**
- Create: `AI-ENGINEERING-OS/frameworks/_catalogo.md`, `_backlog.md`, `conhecidos/{RTF,CARE,RISE,TAG,BAB,RAPPEL}.md`, `conhecidos/{langchain,crewai,autogen,semantic-kernel}.md`, `proprietarios/AI-ENGINEERING-FRAMEWORK.md`
- Create: `AI-ENGINEERING-OS/agentes/_template-agente.md`, `agentes/_catalogo.md`
- Create: `AI-ENGINEERING-OS/prompts/_indice.md`, `prompts/prompt-engineering/` (populado na Task 15)
- Create: `AI-ENGINEERING-OS/templates/README.md`, `diagramas/README.md`, `referencias/{papers,livros,links}.md`, `sdk/README.md`, `exemplos/_template-exemplo.md`

**Regras de conteúdo (spec §7.1):**
- `conhecidos/*.md` para RTF, CARE, RISE, TAG, BAB, RAPPEL: descritos como **técnicas públicas de prompt**, cada um com o que a sigla expande, quando serve, quando não serve, e um exemplo. **Sem atribuição inventada** — se a origem exata não é conhecida com segurança, escrever "técnica de domínio público, origem não atribuída com segurança" em vez de citar um autor.
- `proprietarios/AI-ENGINEERING-FRAMEWORK.md`: o único proprietário; é a síntese que esta plataforma propõe (contrato → geração → gate → auditoria → promoção), amarrada aos cinco comandos.
- **`_backlog.md`**: lista ORBIT, FLOW, NEXUS, FUSION, GENESIS, ATLAS, EVEREST, QUANTUM, IDEA+, PACE, BUILD, SMART-AI, ENTERPRISE-AI com a frase exata: *"nome presente na especificação original sem definição; aguardando o autor definir escopo, entradas e saídas. Não foi inventado."*
- `agentes/_template-agente.md`: as 13 rubricas da especificação original (Missão, Objetivos, Entradas, Saídas, Ferramentas, Prompts, Fluxos, Limitações, Memória, Conhecimento, Eventos, Exemplos, Integrações).
- `agentes/_catalogo.md`: apenas o agente que existe de fato (`auditor-fable`, criado na Task 16) + nota de que os demais são backlog.
- `referencias/*.md`: **só fontes que existem e podem ser verificadas.** Nenhum paper inventado. Se a lista ficar curta, ela fica curta.

- [ ] **Step 1:** Escreva os arquivos acima.
- [ ] **Step 2:** Rode `python -m pytest ferramentas/tests -q`. Expected: verde (as bibliotecas não são volumes; nenhum gate novo).
- [ ] **Step 3:** Commit — `git commit -m "docs(aieos): bibliotecas transversais e backlog dos frameworks sem definicao"`

---

## Task 10: `prompt_template.py`

**Files:**
- Create: `AI-ENGINEERING-OS/exemplos/07-prompt-engine/prompt_template.py`
- Test: `AI-ENGINEERING-OS/exemplos/07-prompt-engine/tests/__init__.py`, `.../tests/test_prompt_template.py`

**Interfaces produzidas:**
- `class ContratoViolado(ValueError)`
- `@dataclass(frozen=True, slots=True) class Variavel` — `nome: str`, `tipo: type`, `obrigatoria: bool = True`, `descricao: str = ""`
- `@dataclass(frozen=True) class PromptTemplate` — `nome: str`, `corpo: str`, `variaveis: tuple[Variavel, ...]`
  - `__post_init__` levanta `ContratoViolado` se os placeholders `{x}` do corpo divergirem dos nomes declarados (em qualquer direção), com a diferença na mensagem.
  - `render(**valores) -> str` — levanta `ContratoViolado` em obrigatória ausente, tipo errado (`isinstance`) ou chave extra. Opcional ausente vira `""`.
  - `assinatura -> str` (property) — `"nome(v1:int, v2:str)"`, variáveis em ordem alfabética.
  - `hash -> str` (property) — `sha256` de `corpo + "\x00" + assinatura`, 12 primeiros hexdígitos.

**Testes exigidos:** render feliz; obrigatória ausente levanta; tipo errado levanta; chave extra levanta; opcional ausente vira vazio; placeholder não declarado levanta no construtor; variável declarada e não usada levanta no construtor; `hash` estável entre instâncias iguais; `hash` muda quando o corpo muda; `hash` muda quando o tipo de uma variável muda (o hash cobre a assinatura, não só o texto).

- [ ] **Step 1:** Escreva o teste. - [ ] **Step 2:** Rode, veja falhar (`ModuleNotFoundError`). - [ ] **Step 3:** Implemente. - [ ] **Step 4:** Rode `cd AI-ENGINEERING-OS && python -m pytest exemplos/07-prompt-engine -q`, veja passar. - [ ] **Step 5:** Commit `feat(aieos): exemplo prompt_template com contrato tipado`

---

## Task 11: `prompt_registry.py`

**Files:**
- Create: `AI-ENGINEERING-OS/exemplos/07-prompt-engine/prompt_registry.py`
- Test: `.../tests/test_prompt_registry.py`

**Interfaces:**
- Consumes: `PromptTemplate`, `ContratoViolado` da Task 10.
- Produces:
  - `class Estado(StrEnum)` — `RASCUNHO`, `VERSIONADO`, `EM_AVALIACAO`, `PROMOVIDO`, `DEPRECIADO`. **Os mesmos nomes do `stateDiagram-v2` de `05-Diagramas.md`** — a máquina de estados do volume e a do código são a mesma.
  - `class TransicaoInvalida(ValueError)`, `class NaoRegistrado(KeyError)`
  - `TRANSICOES: dict[Estado, frozenset[Estado]]` — `RASCUNHO→{VERSIONADO}`, `VERSIONADO→{EM_AVALIACAO, DEPRECIADO}`, `EM_AVALIACAO→{PROMOVIDO, VERSIONADO, DEPRECIADO}`, `PROMOVIDO→{DEPRECIADO}`, `DEPRECIADO→frozenset()`
  - `class PromptRegistry`:
    - `registrar(template) -> str` — devolve `"v1"`, `"v2"`, … . **Idempotente por hash:** registrar o mesmo conteúdo devolve a versão já existente sem criar nova. Estado inicial `VERSIONADO`.
    - `obter(nome, versao=None) -> PromptTemplate` — `None` = versão `PROMOVIDO`; se nenhuma promovida, a última registrada; `NaoRegistrado` se o nome não existe.
    - `transicionar(nome, versao, destino: Estado) -> None` — valida contra `TRANSICOES`, levanta `TransicaoInvalida` com origem e destinos válidos na mensagem.
    - `estado(nome, versao) -> Estado`
    - `historico(nome) -> tuple[tuple[str, str, Estado], ...]` — `(versao, hash, estado)` em ordem de registro.
    - `promovida(nome) -> str | None`
    - Invariante: **no máximo uma versão `PROMOVIDO` por nome** — promover a v3 rebaixa automaticamente a v2 promovida para `DEPRECIADO`, e isso é testado.

**Testes exigidos:** primeira versão é v1; segunda com corpo diferente é v2; mesmo conteúdo é idempotente (devolve v1, `historico` tem 1 entrada); `obter` sem versão devolve a promovida; `obter` sem promovida devolve a última; nome inexistente levanta `NaoRegistrado`; transição válida muda o estado; `DEPRECIADO→PROMOVIDO` levanta `TransicaoInvalida` com a lista de destinos; promover uma segunda versão deprecia a anterior; `historico` preserva ordem.

- [ ] **Step 1–5:** Mesmo ciclo TDD da Task 10. Commit `feat(aieos): exemplo prompt_registry versionado com maquina de estados`

---

## Task 12: `prompt_evaluator.py`

**Files:**
- Create: `AI-ENGINEERING-OS/exemplos/07-prompt-engine/prompt_evaluator.py`
- Test: `.../tests/test_prompt_evaluator.py`

**Interfaces:**
- Consumes: `PromptTemplate` (Task 10).
- Produces:
  - `@dataclass(frozen=True, slots=True) class CasoDeOuro` — `nome: str`, `entradas: dict[str, object]`, `esperado: str` (regex), `descricao: str = ""`
  - `@dataclass(frozen=True, slots=True) class Falha` — `caso: str`, `saida: str`, `motivo: str`
  - `@dataclass(frozen=True, slots=True) class Resultado` — `total: int`, `falhas: tuple[Falha, ...]`; `acertos` e `taxa_acerto` (0.0 quando `total == 0`) como properties.
  - `@dataclass(frozen=True, slots=True) class Comparacao` — `taxa_a: float`, `taxa_b: float`; `deriva -> float` (`taxa_b - taxa_a`), `vencedor -> str` (`"a"`, `"b"` ou `"empate"`).
  - `class PromptEvaluator` — `__init__(self, executor: Callable[[str], str])`. **A injeção do executor é o ponto do exemplo:** avaliar prompt não exige chamar LLM, e é por isso que o teste roda offline e determinístico.
    - `avaliar(template, casos) -> Resultado` — erro ao renderizar conta como falha com `motivo`, não propaga.
    - `comparar(a, b, casos) -> Comparacao`

**Testes exigidos:** todos os casos passando dá `taxa_acerto == 1.0`; caso que não casa entra em `falhas` com a saída; lista vazia dá `taxa_acerto == 0.0` sem `ZeroDivisionError`; erro de render conta como falha e não sobe; `esperado` é tratado como regex; `comparar` calcula deriva positiva e negativa; `vencedor` devolve `"empate"` em taxas iguais; o executor é chamado uma vez por caso (contador no fake).

- [ ] **Step 1–5:** Mesmo ciclo TDD. Commit `feat(aieos): exemplo prompt_evaluator com executor injetado`

---

## Tasks 13–15: O volume-piloto `07-PROMPT-ENGINE`

Três tasks, seis seções cada, porque seis seções é o que um revisor consegue avaliar de
uma vez. Todas as seções levam o front-matter do §4.2 com `status: RASCUNHO`,
`volume: "07"`, `volume_nome: PROMPT-ENGINE`, `tipo: ENGINE`, `atualizado_em: 2026-07-29`.
Mínimo de 200 palavras de prosa por seção (120 em Checklist e Roadmap, 150 em Conclusão,
80 em Referências-Cruzadas) — **prosa, código não conta.**

### Task 13: seções 01–06

- `01-Introducao` — o que é um motor de prompts e por que prompt solto em código é dívida.
- `02-Objetivos` — objetivos verificáveis (prompt versionado, avaliável, promovível, auditável).
- `03-Escopo` — dentro: template, registry, avaliação, promoção. Fora: compilação multi-modelo (vol. 28), otimização automática (vol. 29), roteamento (vol. 27). Declarar essas fronteiras é o que impede a sobreposição apontada na revisão da especificação.
- `04-Arquitetura` — **`C4Context` obrigatório** (autor de prompt, plataforma, provedores LLM) e um `C4Container` (template, registry, avaliador, executor). Cada bloco seguido de parágrafo.
- `05-Diagramas` — **`sequenceDiagram`** (render → executor → avaliação), **`stateDiagram-v2`** com exatamente os cinco estados de `Estado` da Task 11, `erDiagram` do registry, `mindmap` do domínio. Cada um com parágrafo.
- `06-Fluxogramas` — `flowchart` do ciclo rascunho→promoção com os pontos de decisão.

- [ ] **Step 1:** Escreva as 6 seções. - [ ] **Step 2:** `cd AI-ENGINEERING-OS && python -m ferramentas.validar 07` — espere violações `secao-ausente` **apenas** das seções 07–18; nenhuma outra regra deve aparecer. - [ ] **Step 3:** Commit `docs(aieos): volume 07 secoes 01-06`

### Task 14: seções 07–12

- `07-Regras` — regras invioláveis do motor (prompt sem teste não promove; hash cobre a assinatura; uma promovida por nome).
- `08-Modelos` — os contratos das Tasks 10–12 **com as assinaturas exatas** (`PromptTemplate`, `Variavel`, `PromptRegistry`, `Estado`, `PromptEvaluator`, `CasoDeOuro`, `Resultado`).
- `09-Boas-Praticas` / `10-Anti-Patterns` — pares concretos. O anti-pattern "deixar marcador de trabalho inacabado" deve citá-lo em code span (`` `TODO` ``) para não disparar a própria regra — e o texto explica isso, o que documenta o escape.
- `11-Implementacao` — passo a passo dos três módulos, **com `<!-- exemplo: exemplos/07-prompt-engine/prompt_template.py -->`** e os outros dois.
- `12-Exemplos` — uso ponta a ponta citando os três arquivos com a sintaxe de exemplo.

- [ ] **Step 1:** Escreva as 6 seções. - [ ] **Step 2:** `python -m ferramentas.validar 07` — só `secao-ausente` de 13–18; as regras `exemplo-inexistente`/`exemplo-sem-teste` **têm de estar limpas** (Tasks 10–12 já criaram arquivos e testes). - [ ] **Step 3:** Commit `docs(aieos): volume 07 secoes 07-12`

### Task 15: seções 13–18, gates verdes e biblioteca de prompts

- `13-Testes` — estratégia de teste do motor; como os testes dos exemplos são o gate 2.
- `14-Metricas` — métricas observáveis: taxa de acerto por versão, deriva entre versões, custo por execução, cobertura de casos de ouro. Sem adjetivo sem número.
- `15-Checklist` — checklist acionável de "meu prompt está pronto?".
- `16-Roadmap` — evolução do motor e a ligação com 28/29.
- `17-Conclusao` — o que o volume entregou.
- `18-Referencias-Cruzadas` — links **resolvíveis** para `../01-FUNDACAO/`, `../08-AGENT-ENGINE/`, `../28-PROMPT-COMPILER/`, `../29-PROMPT-OPTIMIZER/`, `../31-TESTING/`. **Só aponte para arquivo que existe** — volume pendente só tem `_VOLUME.yml`, então linke para ele, não para `01-Introducao.md` inexistente. É aqui que `link-morto` costuma pegar.
- Popular `prompts/prompt-engineering/` com 3 prompts reais extraídos do volume + `_indice.md`.

- [ ] **Step 1:** Escreva as 6 seções e os prompts. - [ ] **Step 2:** `python -m ferramentas.validar 07` — **exit 0, zero violações.** - [ ] **Step 3:** `python -m ferramentas.validar --cross-refs` — exit 0. - [ ] **Step 4:** `python -m pytest ferramentas/tests exemplos -q` — tudo verde. - [ ] **Step 5:** Commit `docs(aieos): volume 07 completo, gates 1-3 verdes`

---

## Task 16: As 5 skills e o agente auditor

**Files:**
- Create: `AI-ENGINEERING-OS/.claude/agents/auditor-fable.md`
- Create: `AI-ENGINEERING-OS/.claude/skills/{novo-volume,auditar,status,cross-reference,exportar}/SKILL.md`

**`auditor-fable.md`** — front-matter `name: auditor-fable`, `description` (auditor técnico da plataforma; usado por `/auditar`), `tools: Read, Grep, Glob, Bash`, `model: fable`. Corpo: o prompt de auditoria da especificação original (coerência com volumes anteriores, lacunas, contradições, qualidade dos Mermaid, funcionalidade dos exemplos, completude do checklist) e o **formato de saída obrigatório**, que precisa incluir a linha `media: N.N` porque `status.py::nota_da_ultima_auditoria` a lê.

**Cada `SKILL.md`** com front-matter `name` e `description` e um corpo que é um procedimento, não uma sugestão:
- `novo-volume`: ler `Convencoes.md` + `contrato.json` + `CHANGELOG.md` + volumes em `depende_de`; resolver o tipo; gerar seções; criar exemplos com teste; rodar `validar.py <N>`; rodar `pytest`; **gravar `status` conforme resultado, nunca `PRONTO` com gate vermelho**; registrar no `CHANGELOG.md`.
- `auditar`: despachar `auditor-fable`; gravar `auditorias/VOL-NN-auditoria-<data>.md`; aplicar a regra média ≥ 8,0 e nenhuma seção < 6; atualizar `status`.
- `status`: rodar `python -m ferramentas.status`.
- `cross-reference`: rodar `python -m ferramentas.validar --cross-refs`; se verde, despachar o Fable para o passe semântico de contradições.
- `exportar`: rodar `python -m ferramentas.exportar`.

- [ ] **Step 1:** Escreva os 6 arquivos. - [ ] **Step 2:** Verifique que aparecem na listagem de skills (as skills são escopadas por diretório; se não aparecerem, registre o achado no `CHANGELOG.md` e documente a invocação direta por `python -m` em `Como-Utilizar.md` — **não afirme que funcionam sem ter visto**). - [ ] **Step 3:** Commit `feat(aieos): 5 skills operacionais e subagente auditor Fable`

---

## Task 17: Auditoria do piloto, incorporação e exportação

- [ ] **Step 1:** Rode a auditoria despachando o subagente `auditor-fable` sobre `07-PROMPT-ENGINE`, com o prompt de auditoria da especificação.
- [ ] **Step 2:** Grave `auditorias/VOL-07-auditoria-2026-07-29.md` no formato exigido, com a linha `media: N.N`.
- [ ] **Step 3:** Incorpore o feedback nas seções apontadas. Se a média < 8,0 ou alguma seção < 6, o `status` do volume vai para `REQUER_REVISAO` e o ciclo repete — **não force `PRONTO`**.
- [ ] **Step 4:** Rode os três gates: `python -m ferramentas.validar 07`, `--cross-refs`, e `python -m pytest ferramentas/tests exemplos -q`. Todos verdes.
- [ ] **Step 5:** Só então grave `status: PRONTO` no `_VOLUME.yml` do 07 e nas 18 seções, e registre no `CHANGELOG.md` com a data e a média da auditoria.
- [ ] **Step 6:** Rode `python -m ferramentas.exportar` e reporte se o build do MkDocs foi validado ou apenas o `mkdocs.yml` gerado.
- [ ] **Step 7:** Rode `python -m ferramentas.status` e cole a tabela no relatório final.
- [ ] **Step 8:** Commit `feat(aieos): volume 07 auditado e promovido a PRONTO`

---

## Self-review deste plano

**Cobertura do spec:** §3 estrutura → Tasks 7,8,9. §4.1 tipos → Task 2 (`contrato.json`) + Task 8 (`Convencoes.md`) + `test_convencoes_nao_derivou`. §4.2 front-matter → Tasks 1,3. §4.3 PRONTO → Task 17. §5.1 validador (as 9 regras) → Tasks 3,4,5. §5.2 skills → Task 16. §5.3 honestidade de estado → Tasks 5,16,17. §6 piloto → Tasks 10–15. §7.1 frameworks → Task 9. §7.2 metas numéricas → Task 8 (`ROADMAP.md`). §7.3 perecível → Task 2 (`perecivel` no contrato) + Task 8. §8 fluxo → Task 8 (`Arquitetura-Geral.md`). §9 erros → Tasks 2,5,7. §10 testes da máquina → Tasks 1–7.

**Divergências deliberadas do spec, todas justificadas no corpo:**
1. `contrato.json` em vez de parsear a tabela de `Convencoes.md`, com teste de drift — mais robusto, mesmo efeito de fonte única.
2. `depende_de` no `_VOLUME.yml` com ids de 2 dígitos e semântica de pré-requisito — sem isso, 07↔28 seria ciclo falso. O exemplo do spec §4.2 (07 dependendo de 08 e 28) está invertido e não deve ser copiado.
3. Contagem de palavras ignora blocos de código — senão uma seção só de código passaria o mínimo.
4. Marcador proibido é permitido em code span — o volume `10-Anti-Patterns` precisa poder falar de `TODO`.
5. `PENDENTE` é estado derivado em `status.py`, não um `status` gravável.

**Consistência de tipos:** `Violacao(arquivo, linha, regra, mensagem)` idêntico em todas as tasks. `Contrato.secoes_de/diagramas_de/minimo_de/volume` usados com a mesma assinatura nas Tasks 3–7. `Estado` da Task 11 tem os mesmos cinco nomes do `stateDiagram-v2` da Task 13. `PromptTemplate.render/assinatura/hash` referenciados sem renomear nas Tasks 11, 12, 14.

**Sem placeholders:** nenhum passo diz "implemente depois". As tasks 7 e 9–17 carregam brief de conteúdo com interfaces e critérios de aceite exatos em vez de prosa literal, porque o entregável delas *é* prosa — o critério verificável é o gate, e ele está especificado.

