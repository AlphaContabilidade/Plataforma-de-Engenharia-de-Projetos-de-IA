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
