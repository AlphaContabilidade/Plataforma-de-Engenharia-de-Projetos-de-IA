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

# Um volume ENGINE valido precisa dos tres diagramas que o contrato exige
# (C4Context, sequenceDiagram, stateDiagram-v2), cada um seguido de paragrafo
# descritivo. Sem isso a fixture nao seria um volume valido de verdade.
DIAGRAMAS = """```mermaid
C4Context
  title Contexto do motor de prompts
```

O diagrama de contexto mostra o motor e os sistemas vizinhos.

```mermaid
sequenceDiagram
  Autor->>Motor: compila o template
```

A sequencia mostra a compilacao de um template ate o prompt final.

```mermaid
stateDiagram-v2
  [*] --> RASCUNHO
```

A maquina de estado mostra o ciclo de vida de um template.
"""


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
        miolo = f"{DIAGRAMAS}\n" if secao == "05-Diagramas" else ""
        (pasta / f"{secao}.md").write_text(
            f"{cabeca}\n# {secao}\n\n{miolo}{PROSA}\n", encoding="utf-8"
        )
    return acervo, pasta


def escrever(caminho: Path, texto: str) -> None:
    caminho.write_text(texto, encoding="utf-8")
