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
