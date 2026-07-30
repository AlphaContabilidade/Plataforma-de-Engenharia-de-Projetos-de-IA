"""Poe os quatro modulos deste exemplo no caminho de import da suite.

Existe pelo mesmo motivo concreto do `conftest.py` de `exemplos/12-memory`, e a
razao esta registrada em `ROADMAP.md` como divida tecnica: duas pastas
`exemplos/<vol>/tests/` com `__init__.py` reivindicam o mesmo nome de pacote
`tests`, e rodar a suite dos exemplos inteira falha com `ModuleNotFoundError` na
segunda pasta coletada -- a primeira ganha o nome e a segunda procura seus modulos
dentro dela.

Sem `__init__.py`, cada arquivo de teste e importado pelo nome-base
(`test_catalogo`), que e unico no acervo, e a colisao desaparece. O preco e que a
pasta do exemplo deixa de entrar no caminho de import automaticamente, e este
arquivo paga esse preco explicitamente, em tres linhas, sem configuracao global.
"""

import sys
from pathlib import Path

_AQUI = str(Path(__file__).parent)
if _AQUI not in sys.path:
    sys.path.insert(0, _AQUI)
