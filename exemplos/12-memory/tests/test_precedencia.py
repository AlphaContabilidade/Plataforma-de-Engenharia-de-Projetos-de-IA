"""Testa a regra de precedencia e o veredicto indeciso de primeira classe.

Tres testes deste arquivo travam invariantes que custaram dinheiro quando
faltaram. `test_observacao_indecisa_nao_cai_para_a_base_congelada` fixa que
precedencia nao e cascata de fallback: se a fonte de maior precedencia presente
nao decide, a resposta e indeciso, e nao a resposta da fonte seguinte.
`test_eco_do_agente_e_descartado_e_contado` fixa que a autoconfirmacao nao
inverte o veredicto. `test_dominancia_6_em_10_nao_decide` fixa que evidencia que
nao decide devolve `None` com justificativa, em vez de um chute rotulado como
confianca baixa.
"""

from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from memoria_observada import ChaveInvalida, Entrada, MemoriaObservada, Origem
from precedencia import PRECEDENCIA, Confianca, Veredicto, resolver

HOJE = date(2026, 3, 1)
RECENTE = date(2026, 2, 20)
VELHA = date(2025, 1, 1)


def _mem(*entradas: Entrada) -> MemoriaObservada:
    mem = MemoriaObservada()
    for entrada in entradas:
        mem.registrar(entrada)
    return mem


def _e(decisao, origem=Origem.OBSERVADO, chave="chave-a", em=RECENTE):
    return Entrada(chave=chave, decisao=decisao, origem=origem, em=em)


def _obs(decisao, n, em=RECENTE):
    return [_e(decisao, em=em) for _ in range(n)]


def test_precedencia_exclui_o_eco_do_agente():
    assert PRECEDENCIA == (
        Origem.DECIDIDO_POR_HUMANO,
        Origem.OBSERVADO,
        Origem.BASE_CONGELADA,
    )
    assert Origem.ESCRITO_PELO_AGENTE not in PRECEDENCIA


def test_confianca_tem_exatamente_tres_niveis():
    assert [c.name for c in Confianca] == ["ALTA", "MEDIA", "BAIXA"]


def test_memoria_vazia_devolve_indeciso_sem_excecao():
    veredicto = resolver(MemoriaObservada(), "nunca-vista", hoje=HOJE)
    assert veredicto.decisao is None
    assert veredicto.confianca is None
    assert veredicto.justificativa
    assert veredicto.descartadas == 0
    assert veredicto.contradicoes == ()


def test_dominancia_7_em_10_decide():
    """Limite inclusivo: 0,7 com minimo 0,7 decide. O piso e piso, nao barreira."""
    mem = _mem(*_obs("alfa", 7), *_obs("beta", 3))
    veredicto = resolver(mem, "chave-a", hoje=HOJE, dominancia_minima=0.7)
    assert veredicto.decisao == "alfa"
    assert veredicto.confianca is Confianca.ALTA
    assert "7/10" in veredicto.justificativa


def test_dominancia_6_em_10_nao_decide():
    mem = _mem(*_obs("alfa", 6), *_obs("beta", 4))
    veredicto = resolver(mem, "chave-a", hoje=HOJE, dominancia_minima=0.7)
    assert veredicto.decisao is None
    assert veredicto.confianca is None
    assert "abaixo do minimo" in veredicto.justificativa


def test_empate_nao_decide():
    mem = _mem(*_obs("alfa", 3), *_obs("beta", 3))
    veredicto = resolver(mem, "chave-a", hoje=HOJE, dominancia_minima=0.5)
    assert veredicto.decisao is None
    assert "empate" in veredicto.justificativa


def test_entrada_fora_da_janela_expira():
    """Oito observacoes velhas nao vencem duas recentes: expirada nao conta."""
    mem = _mem(*_obs("alfa", 8, em=VELHA), *_obs("beta", 2))
    veredicto = resolver(mem, "chave-a", hoje=HOJE, janela_dias=365)
    assert veredicto.decisao == "beta"
    assert "expirada" in veredicto.justificativa


def test_janela_maior_muda_o_veredicto():
    mem = _mem(*_obs("alfa", 8, em=VELHA), *_obs("beta", 2))
    assert resolver(mem, "chave-a", hoje=HOJE, janela_dias=3650).decisao == "alfa"


def test_decisao_humana_vence_dominancia_contraria():
    mem = _mem(*_obs("alfa", 9), _e("beta", origem=Origem.DECIDIDO_POR_HUMANO))
    veredicto = resolver(mem, "chave-a", hoje=HOJE)
    assert veredicto.decisao == "beta"
    assert veredicto.confianca is Confianca.ALTA


def test_decisao_humana_mais_recente_vence_a_anterior():
    mem = _mem(
        _e("beta", origem=Origem.DECIDIDO_POR_HUMANO, em=date(2026, 1, 5)),
        _e("gama", origem=Origem.DECIDIDO_POR_HUMANO, em=date(2026, 2, 5)),
    )
    assert resolver(mem, "chave-a", hoje=HOJE).decisao == "gama"


def test_base_congelada_sozinha_decide_com_confianca_baixa():
    mem = _mem(_e("beta", origem=Origem.BASE_CONGELADA, em=date(2026, 1, 5)))
    veredicto = resolver(mem, "chave-a", hoje=HOJE)
    assert veredicto.decisao == "beta"
    assert veredicto.confianca is Confianca.BAIXA
    assert "sem confirmacao observada" in veredicto.justificativa


def test_contradicao_rebaixa_a_confianca_e_entra_no_veredicto():
    mem = _mem(
        _e("beta", origem=Origem.BASE_CONGELADA, em=date(2026, 1, 5)),
        *_obs("alfa", 3),
    )
    veredicto = resolver(mem, "chave-a", hoje=HOJE)
    assert veredicto.decisao == "alfa"
    assert veredicto.confianca is Confianca.MEDIA
    assert len(veredicto.contradicoes) == 1
    assert veredicto.contradicoes[0].decisao_congelada == "beta"
    assert "contradicao" in veredicto.justificativa


def test_contradicao_rebaixa_ate_a_decisao_humana():
    """Chave conhecidamente inconsistente nao produz confianca alta, nem decidida por pessoa.

    A contradicao continua sendo emitida depois da decisao humana: a precedencia a
    torna irrelevante para o veredicto, e nao resolve a fonte que discorda.
    """
    mem = _mem(
        *_obs("alfa", 4),
        _e("gama", origem=Origem.BASE_CONGELADA, em=date(2026, 1, 20)),
        _e("beta", origem=Origem.DECIDIDO_POR_HUMANO, em=HOJE),
    )
    veredicto = resolver(mem, "chave-a", hoje=HOJE)
    assert veredicto.decisao == "beta"
    assert veredicto.confianca is Confianca.MEDIA
    assert len(veredicto.contradicoes) == 1


def test_eco_do_agente_e_descartado_e_contado():
    """Cinco escritas do proprio agente inverteriam o veredicto se contassem."""
    mem = _mem(*_obs("alfa", 2), *[_e("beta", origem=Origem.ESCRITO_PELO_AGENTE)] * 5)
    assert mem.dominancia("chave-a") == ("beta", 5 / 7)
    veredicto = resolver(mem, "chave-a", hoje=HOJE)
    assert veredicto.decisao == "alfa"
    assert veredicto.descartadas == 5
    assert "descartada" in veredicto.justificativa


def test_observacao_indecisa_nao_cai_para_a_base_congelada():
    """Precedencia nao e cascata: fonte presente que nao decide encerra a resolucao."""
    mem = _mem(
        _e("gama", origem=Origem.BASE_CONGELADA, em=date(2026, 1, 5)),
        *_obs("alfa", 6),
        *_obs("beta", 4),
    )
    veredicto = resolver(mem, "chave-a", hoje=HOJE)
    assert veredicto.decisao is None
    assert veredicto.confianca is None
    assert len(veredicto.contradicoes) == 1


def test_so_eco_do_agente_e_o_mesmo_que_nada():
    mem = _mem(*[_e("alfa", origem=Origem.ESCRITO_PELO_AGENTE)] * 4)
    veredicto = resolver(mem, "chave-a", hoje=HOJE)
    assert veredicto.decisao is None
    assert veredicto.descartadas == 4


def test_tudo_expirado_e_o_mesmo_que_nada():
    mem = _mem(*_obs("alfa", 5, em=VELHA))
    veredicto = resolver(mem, "chave-a", hoje=HOJE, janela_dias=30)
    assert veredicto.decisao is None
    assert "expirada" in veredicto.justificativa


def test_chave_em_branco_levanta():
    """Levantar e para erro de programa; falta de evidencia nunca levanta."""
    with pytest.raises(ChaveInvalida):
        resolver(MemoriaObservada(), "   ", hoje=HOJE)


def test_veredicto_e_congelado():
    veredicto = resolver(MemoriaObservada(), "chave-a", hoje=HOJE)
    assert isinstance(veredicto, Veredicto)
    with pytest.raises(FrozenInstanceError):
        veredicto.decisao = "alfa"
