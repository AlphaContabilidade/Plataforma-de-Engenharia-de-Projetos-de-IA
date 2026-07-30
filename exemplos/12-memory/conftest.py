"""Poe os tres modulos deste exemplo no caminho de import da suite.

Existe por um motivo concreto, e nao por convencao: dois exemplos da plataforma
teriam, cada um, uma pasta `tests/` com `__init__.py`, e as duas reivindicariam o
mesmo nome de pacote `tests`. Rodar a suite dos exemplos inteira falharia com
`ModuleNotFoundError` na segunda pasta coletada -- a primeira ganha o nome e a
segunda procura seus modulos dentro dela.

Sem `__init__.py`, cada arquivo de teste e importado pelo nome-base
(`test_precedencia`), que e unico no acervo, e a colisao desaparece. O preco e que
a pasta do exemplo deixa de entrar no caminho de import automaticamente, e este
arquivo paga esse preco explicitamente, em tres linhas, sem configuracao global.
"""

import sys
from pathlib import Path

_AQUI = str(Path(__file__).parent)
if _AQUI not in sys.path:
    sys.path.insert(0, _AQUI)
