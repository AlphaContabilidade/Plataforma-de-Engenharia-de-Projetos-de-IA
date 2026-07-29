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
