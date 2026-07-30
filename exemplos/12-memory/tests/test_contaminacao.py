"""Testa a guarda que separa evidencia de eco, e o relatorio de contradicao.

O teste `test_eco_nao_silencia_a_contradicao` e o motivo de este arquivo
existir. Ele monta o cenario exato do defeito de producao: a base congelada diz
uma coisa, a observacao independente diz outra, e o agente escreveu cinco vezes
concordando com a base congelada. Se o eco contasse, a dominancia apontaria para
a base e a contradicao desapareceria -- que e precisamente como uma decisao
errada se consolida sem deixar sinal.
"""

from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from contaminacao import Contradicao, contradicoes, filtrar_contaminacao
from memoria_observada import Entrada, Origem

EM = date(2026, 3, 1)
ANTES = date(2026, 1, 15)


def _e(decisao, origem=Origem.OBSERVADO, chave="chave-a", em=EM):
    return Entrada(chave=chave, decisao=decisao, origem=origem, em=em)


def test_escrito_pelo_agente_nunca_e_evidencia():
    validas, descartadas = filtrar_contaminacao(
        [_e("alfa"), _e("beta", origem=Origem.ESCRITO_PELO_AGENTE)]
    )
    assert [e.decisao for e in validas] == ["alfa"]
    assert [e.decisao for e in descartadas] == ["beta"]


def test_as_outras_tres_origens_passam():
    entradas = [
        _e("alfa", origem=Origem.OBSERVADO),
        _e("beta", origem=Origem.BASE_CONGELADA),
        _e("gama", origem=Origem.DECIDIDO_POR_HUMANO),
    ]
    validas, descartadas = filtrar_contaminacao(entradas)
    assert len(validas) == 3 and descartadas == ()


def test_filtrar_devolve_tuplas_e_preserva_a_ordem():
    entradas = [_e("a"), _e("x", origem=Origem.ESCRITO_PELO_AGENTE), _e("b")]
    validas, descartadas = filtrar_contaminacao(entradas)
    assert isinstance(validas, tuple) and isinstance(descartadas, tuple)
    assert [e.decisao for e in validas] == ["a", "b"]


def test_filtrar_vazio_devolve_duas_tuplas_vazias():
    assert filtrar_contaminacao(()) == ((), ())


def test_base_congelada_que_discorda_da_dominante_gera_contradicao():
    entradas = [
        _e("beta", origem=Origem.BASE_CONGELADA, em=ANTES),
        _e("alfa"),
        _e("alfa"),
        _e("alfa"),
    ]
    assert contradicoes(entradas) == (
        Contradicao(
            chave="chave-a",
            decisao_congelada="beta",
            decisao_observada="alfa",
            n_observacoes=3,
            congelada_em=ANTES,
        ),
    )


def test_base_congelada_que_concorda_nao_gera_contradicao():
    entradas = [_e("alfa", origem=Origem.BASE_CONGELADA, em=ANTES), _e("alfa"), _e("alfa")]
    assert contradicoes(entradas) == ()


def test_sem_observacao_nao_ha_o_que_contradizer():
    entradas = [
        _e("beta", origem=Origem.BASE_CONGELADA, em=ANTES),
        _e("beta", origem=Origem.ESCRITO_PELO_AGENTE),
    ]
    assert contradicoes(entradas) == ()


def test_sem_base_congelada_nao_ha_contradicao():
    assert contradicoes([_e("alfa"), _e("beta")]) == ()


def test_eco_nao_silencia_a_contradicao():
    """O defeito real: cinco escritas do proprio agente concordando com a base congelada.

    Sem a exclusao do eco, a dominancia seria `beta` 5/8 e a base congelada
    apareceria confirmada -- a contradicao existiria e ninguem a veria.
    """
    entradas = [_e("beta", origem=Origem.BASE_CONGELADA, em=ANTES)]
    entradas += [_e("beta", origem=Origem.ESCRITO_PELO_AGENTE) for _ in range(5)]
    entradas += [_e("alfa") for _ in range(3)]
    achadas = contradicoes(entradas)
    assert len(achadas) == 1
    assert achadas[0].decisao_observada == "alfa"
    assert achadas[0].n_observacoes == 3


def test_uma_observacao_isolada_ja_contradiz():
    """O limiar de reporte e zero de proposito: suprimir contradicao fraca e resolver em silencio."""
    achadas = contradicoes([_e("beta", origem=Origem.BASE_CONGELADA, em=ANTES), _e("alfa")])
    assert achadas[0].n_observacoes == 1


def test_contradicoes_sao_por_chave():
    entradas = [
        _e("beta", origem=Origem.BASE_CONGELADA, chave="chave-a", em=ANTES),
        _e("alfa", chave="chave-a"),
        _e("beta", origem=Origem.BASE_CONGELADA, chave="chave-b", em=ANTES),
        _e("beta", chave="chave-b"),
    ]
    achadas = contradicoes(entradas)
    assert [c.chave for c in achadas] == ["chave-a"]


def test_duas_bases_congeladas_discordantes_geram_duas_contradicoes():
    entradas = [
        _e("gama", origem=Origem.BASE_CONGELADA, em=date(2026, 2, 1)),
        _e("beta", origem=Origem.BASE_CONGELADA, em=ANTES),
        _e("alfa"),
    ]
    achadas = contradicoes(entradas)
    assert [c.congelada_em for c in achadas] == [ANTES, date(2026, 2, 1)]
    assert [c.decisao_congelada for c in achadas] == ["beta", "gama"]


def test_contradicao_e_congelada():
    achada = contradicoes([_e("beta", origem=Origem.BASE_CONGELADA, em=ANTES), _e("alfa")])[0]
    with pytest.raises(FrozenInstanceError):
        achada.n_observacoes = 99
