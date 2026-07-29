"""Testa a avaliacao de prompt contra casos de ouro, offline.

Nenhum teste deste arquivo toca a rede: o executor e injetado. E esse o ponto do
exemplo -- se avaliar prompt exigisse chamar um provedor, a avaliacao nao caberia
no gate de CI, e prompt sem teste chegaria a producao.
"""

import pytest

from prompt_evaluator import CasoDeOuro, Comparacao, PromptEvaluator, Resultado
from prompt_template import PromptTemplate, Variavel

SAUDACAO = PromptTemplate(
    nome="saudacao",
    corpo="Diga ola para {nome}",
    variaveis=(Variavel("nome", str),),
)
OUTRO = PromptTemplate(
    nome="saudacao",
    corpo="Cumprimente {nome}",
    variaveis=(Variavel("nome", str),),
)

CASOS = (
    CasoDeOuro("ana", {"nome": "Ana"}, esperado=r"ola para Ana$"),
    CasoDeOuro("bruno", {"nome": "Bruno"}, esperado=r"ola para \w+$"),
)


class _Eco:
    """Executor fake: devolve o proprio prompt e conta quantas vezes foi chamado."""

    def __init__(self) -> None:
        self.chamadas = 0

    def __call__(self, prompt: str) -> str:
        self.chamadas += 1
        return prompt


def test_todos_os_casos_passando_da_taxa_um():
    resultado = PromptEvaluator(_Eco()).avaliar(SAUDACAO, CASOS)
    assert resultado.taxa_acerto == 1.0
    assert resultado.acertos == 2 and resultado.falhas == ()


def test_caso_que_nao_casa_entra_em_falhas_com_a_saida():
    casos = (CasoDeOuro("errado", {"nome": "Ana"}, esperado="tchau"),)
    resultado = PromptEvaluator(_Eco()).avaliar(SAUDACAO, casos)
    assert resultado.taxa_acerto == 0.0
    assert len(resultado.falhas) == 1
    falha = resultado.falhas[0]
    assert falha.caso == "errado"
    assert falha.saida == "Diga ola para Ana"
    assert "tchau" in falha.motivo


def test_esperado_e_tratado_como_regex():
    casos = (CasoDeOuro("regex", {"nome": "Ana"}, esperado=r"^Diga\s+ola\s+para\s+\w+$"),)
    assert PromptEvaluator(_Eco()).avaliar(SAUDACAO, casos).taxa_acerto == 1.0


def test_lista_vazia_nao_divide_por_zero():
    resultado = PromptEvaluator(_Eco()).avaliar(SAUDACAO, ())
    assert resultado.total == 0
    assert resultado.taxa_acerto == 0.0


def test_taxa_acerto_de_resultado_construido_a_mao_com_total_zero():
    assert Resultado(total=0, falhas=()).taxa_acerto == 0.0


def test_erro_de_render_conta_como_falha_e_nao_sobe():
    """Caso de ouro malformado nao pode derrubar a suite inteira de avaliacao."""
    executor = _Eco()
    casos = (
        CasoDeOuro("sem_variavel", {}, esperado=".*"),
        CasoDeOuro("ok", {"nome": "Ana"}, esperado="ola"),
    )
    resultado = PromptEvaluator(executor).avaliar(SAUDACAO, casos)
    assert resultado.total == 2 and resultado.acertos == 1
    assert resultado.falhas[0].caso == "sem_variavel"
    assert "nome" in resultado.falhas[0].motivo
    assert executor.chamadas == 1  # o caso que nem renderizou nao chega ao executor


def test_executor_e_chamado_uma_vez_por_caso():
    executor = _Eco()
    casos = CASOS + (CasoDeOuro("carla", {"nome": "Carla"}, esperado="ola"),)
    PromptEvaluator(executor).avaliar(SAUDACAO, casos)
    assert executor.chamadas == 3


def test_comparar_calcula_deriva_negativa():
    comparacao = PromptEvaluator(_Eco()).comparar(SAUDACAO, OUTRO, CASOS)
    assert comparacao.taxa_a == 1.0 and comparacao.taxa_b == 0.0
    assert comparacao.deriva == -1.0
    assert comparacao.vencedor == "a"


def test_comparar_calcula_deriva_positiva():
    comparacao = PromptEvaluator(_Eco()).comparar(OUTRO, SAUDACAO, CASOS)
    assert comparacao.deriva == 1.0
    assert comparacao.vencedor == "b"


def test_vencedor_e_empate_em_taxas_iguais():
    comparacao = PromptEvaluator(_Eco()).comparar(SAUDACAO, SAUDACAO, CASOS)
    assert comparacao.deriva == 0.0
    assert comparacao.vencedor == "empate"
    assert Comparacao(taxa_a=0.5, taxa_b=0.5).vencedor == "empate"


@pytest.mark.parametrize(
    ("total", "falhas", "esperado"),
    [(4, 1, 0.75), (2, 2, 0.0), (0, 0, 0.0)],
)
def test_taxa_acerto_em_valores_de_fronteira(total, falhas, esperado):
    from prompt_evaluator import Falha

    resultado = Resultado(
        total=total,
        falhas=tuple(Falha(f"c{i}", "", "motivo") for i in range(falhas)),
    )
    assert resultado.taxa_acerto == esperado
