"""Avaliacao de prompt contra casos de ouro, com o executor injetado.

Prompt sem avaliacao nao tem como ser promovido: "melhorou" sem numero e opiniao.
Este modulo mede -- taxa de acerto sobre casos de ouro e deriva entre duas
versoes -- e faz isso sem saber quem executa o prompt.

A injecao do executor e o ponto do exemplo. Com ela, o mesmo avaliador roda com
um provedor real em producao e com um fake deterministico no CI; sem ela, avaliar
custaria dinheiro e rede, o gate seria desligado, e prompt sem teste passaria.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from prompt_template import ContratoViolado, PromptTemplate


@dataclass(frozen=True, slots=True)
class CasoDeOuro:
    """Uma expectativa verificavel: entradas e o padrao que a saida deve casar.

    `esperado` e regex e nao igualdade literal porque saida de LLM varia em
    detalhe irrelevante; exigir o texto exato produziria teste que quebra sem
    que nada tenha piorado.
    """

    nome: str
    entradas: dict[str, object]
    esperado: str
    descricao: str = ""


@dataclass(frozen=True, slots=True)
class Falha:
    """Um caso que nao passou. Guarda a saida porque diagnostico sem ela e adivinhacao."""

    caso: str
    saida: str
    motivo: str


@dataclass(frozen=True, slots=True)
class Resultado:
    """Resultado de uma rodada: quantos casos rodaram e quais falharam."""

    total: int
    falhas: tuple[Falha, ...]

    @property
    def acertos(self) -> int:
        return self.total - len(self.falhas)

    @property
    def taxa_acerto(self) -> float:
        """Fracao de acertos; 0.0 quando nao houve caso algum.

        Suite vazia devolve 0.0 e nao 1.0: nenhuma evidencia nao e evidencia de
        acerto, e devolver 1.0 promoveria prompt sem caso de ouro.
        """
        if self.total == 0:
            return 0.0
        return self.acertos / self.total


@dataclass(frozen=True, slots=True)
class Comparacao:
    """Duas taxas lado a lado -- a leitura de A/B entre versoes de prompt."""

    taxa_a: float
    taxa_b: float

    @property
    def deriva(self) -> float:
        """`taxa_b - taxa_a`: positivo significa que B melhorou sobre A."""
        return self.taxa_b - self.taxa_a

    @property
    def vencedor(self) -> str:
        if self.taxa_a > self.taxa_b:
            return "a"
        if self.taxa_b > self.taxa_a:
            return "b"
        return "empate"


class PromptEvaluator:
    """Roda casos de ouro contra um template usando o executor recebido."""

    def __init__(self, executor: Callable[[str], str]) -> None:
        self._executor = executor

    def avaliar(self, template: PromptTemplate, casos: Iterable[CasoDeOuro]) -> Resultado:
        """Executa cada caso e devolve o resultado agregado.

        Erro de render conta como falha em vez de propagar: um caso de ouro
        malformado nao pode derrubar a avaliacao dos outros, senao o primeiro
        caso errado esconde o estado real de todo o resto.
        """
        falhas: list[Falha] = []
        total = 0
        for caso in casos:
            total += 1
            try:
                prompt = template.render(**caso.entradas)
            except ContratoViolado as erro:
                falhas.append(Falha(caso.nome, "", f"render falhou: {erro}"))
                continue
            saida = self._executor(prompt)
            if re.search(caso.esperado, saida) is None:
                falhas.append(
                    Falha(caso.nome, saida, f"saida nao casa com o padrao {caso.esperado!r}")
                )
        return Resultado(total=total, falhas=tuple(falhas))

    def comparar(
        self, a: PromptTemplate, b: PromptTemplate, casos: Iterable[CasoDeOuro]
    ) -> Comparacao:
        """Avalia dois templates sobre os MESMOS casos.

        Os casos sao materializados antes: um iterador seria consumido na primeira
        avaliacao e a segunda mediria zero caso, dando deriva falsa.
        """
        materializados = tuple(casos)
        return Comparacao(
            taxa_a=self.avaliar(a, materializados).taxa_acerto,
            taxa_b=self.avaliar(b, materializados).taxa_acerto,
        )
