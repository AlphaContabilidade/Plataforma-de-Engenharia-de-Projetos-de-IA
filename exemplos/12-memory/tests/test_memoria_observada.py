"""Testa o armazem de decisoes observadas.

O teste da chave em branco parece trivial e nao e: a chave e a identidade da
decisao, e um balde de identidade vazia soma observacoes que nao tem relacao
alguma entre si. Dominancia calculada sobre esse balde e um numero inventado
com aparencia de evidencia -- pior que numero nenhum.

O outro teste que carrega o arquivo e `test_dominancia_e_bruta_e_inclui_o_eco`:
ele fixa que o armazem NAO filtra. A filtragem e visivel, mora em
`contaminacao.py`, e quem esquecer de passar por ela le um numero contaminado.
Se o armazem filtrasse por conta propria, essa decisao ficaria invisivel.
"""

from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from memoria_observada import (
    ChaveInvalida,
    DecisaoInvalida,
    Entrada,
    MemoriaObservada,
    Origem,
    contagem_de,
    dominancia_de,
)

EM = date(2026, 3, 1)


def _e(decisao, origem=Origem.OBSERVADO, chave="chave-a", em=EM, evidencia=""):
    return Entrada(chave=chave, decisao=decisao, origem=origem, em=em, evidencia=evidencia)


def test_origem_tem_exatamente_os_quatro_nomes_do_documento():
    assert [o.name for o in Origem] == [
        "OBSERVADO",
        "ESCRITO_PELO_AGENTE",
        "BASE_CONGELADA",
        "DECIDIDO_POR_HUMANO",
    ]


def test_chave_vazia_levanta_chave_invalida():
    with pytest.raises(ChaveInvalida):
        _e("alfa", chave="")


def test_chave_so_com_espaco_levanta_chave_invalida():
    with pytest.raises(ChaveInvalida, match="identidade"):
        _e("alfa", chave="   ")


def test_decisao_em_branco_levanta_decisao_invalida():
    """Simetria com a chave: branco na decisao e erro de programa, nao pendencia.

    Sem esta guarda, `Entrada(chave="k", decisao="")` entrava como alternativa
    legitima: somava contagem, podia empatar com uma decisao real e chegar ao
    chamador dentro de um veredicto -- string vazia com confianca alta.
    """
    for branco in ("", "   ", "\t"):
        with pytest.raises(DecisaoInvalida):
            _e(branco)


def test_decisao_em_branco_nao_e_chave_invalida():
    """As duas excecoes sao irmas e nao se confundem: cada campo tem a sua."""
    with pytest.raises(DecisaoInvalida) as erro:
        _e("  ")
    assert not isinstance(erro.value, ChaveInvalida)
    assert issubclass(DecisaoInvalida, ValueError)


def test_decisao_e_normalizada_na_borda():
    """`"alfa"` e `" alfa "` sao a mesma decisao; contar separado partiria a dominancia."""
    mem = MemoriaObservada()
    mem.registrar(_e("alfa"))
    mem.registrar(_e("  alfa  "))
    assert mem.contagem("chave-a") == {"alfa": 2}


def test_chave_e_normalizada_na_borda():
    """Espaco na borda nao e identidade: sem normalizar, dois baldes para a mesma coisa."""
    assert _e("alfa", chave="  chave-a  ").chave == "chave-a"


def test_consulta_com_chave_em_branco_levanta():
    mem = MemoriaObservada()
    for consulta in (mem.entradas, mem.contagem, mem.dominancia):
        with pytest.raises(ChaveInvalida):
            consulta("  ")


def test_chave_desconhecida_nao_levanta_e_devolve_vazio():
    """Ausencia de evidencia e estado normal do dominio, nao erro de programa."""
    mem = MemoriaObservada()
    assert mem.entradas("nunca-vista") == ()
    assert mem.contagem("nunca-vista") == {}


def test_dominancia_de_chave_desconhecida_e_none():
    assert MemoriaObservada().dominancia("nunca-vista") is None


def test_entradas_preservam_a_ordem_de_registro():
    mem = MemoriaObservada()
    for decisao in ("alfa", "beta", "alfa"):
        mem.registrar(_e(decisao))
    assert [e.decisao for e in mem.entradas("chave-a")] == ["alfa", "beta", "alfa"]


def test_registrar_nao_mistura_chaves():
    mem = MemoriaObservada()
    mem.registrar(_e("alfa", chave="chave-a"))
    mem.registrar(_e("beta", chave="chave-b"))
    assert mem.contagem("chave-a") == {"alfa": 1}
    assert mem.contagem("chave-b") == {"beta": 1}
    assert mem.chaves() == ("chave-a", "chave-b")


def test_contagem_ignora_a_origem():
    mem = MemoriaObservada()
    mem.registrar(_e("alfa"))
    mem.registrar(_e("alfa", origem=Origem.ESCRITO_PELO_AGENTE))
    mem.registrar(_e("beta", origem=Origem.BASE_CONGELADA))
    assert mem.contagem("chave-a") == {"alfa": 2, "beta": 1}


def test_dominancia_e_bruta_e_inclui_o_eco():
    """O armazem conta tudo, de proposito. Limpar e trabalho de `contaminacao`."""
    mem = MemoriaObservada()
    mem.registrar(_e("alfa"))
    for _ in range(3):
        mem.registrar(_e("beta", origem=Origem.ESCRITO_PELO_AGENTE))
    assert mem.dominancia("chave-a") == ("beta", 0.75)


def test_dominancia_de_empate_vale_meio_e_e_deterministica():
    mem = MemoriaObservada()
    mem.registrar(_e("zeta"))
    mem.registrar(_e("alfa"))
    assert mem.dominancia("chave-a") == ("alfa", 0.5)


def test_entrada_e_congelada():
    with pytest.raises(FrozenInstanceError):
        _e("alfa").decisao = "beta"


def test_helpers_operam_sobre_qualquer_iteravel():
    entradas = (_e("alfa"), _e("alfa"), _e("beta"))
    assert contagem_de(entradas) == {"alfa": 2, "beta": 1}
    assert dominancia_de(entradas) == ("alfa", 2 / 3)
    assert contagem_de(()) == {}
    assert dominancia_de(()) is None


def test_contagem_sai_em_ordem_decrescente_com_desempate_alfabetico():
    """A ordem e estavel para que a dominancia nao dependa da ordem de registro."""
    entradas = (_e("zeta"), _e("beta"), _e("beta"), _e("alfa"))
    assert list(contagem_de(entradas)) == ["beta", "alfa", "zeta"]
