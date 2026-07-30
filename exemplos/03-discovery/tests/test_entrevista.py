"""O controle: ordem por peso, determinismo no empate, destravamento e parada."""

from __future__ import annotations

import pytest

from catalogo import Contexto, Lacuna, Plataforma
from deteccao import Origem, Palpite, detectar_plataformas
from entrevista import Entrevista, LacunaDesconhecida, PalpiteDesconhecido

IDEIA_MOBILE = "Quero um aplicativo de celular para os pedidos da loja."


def _ids(lacunas) -> list[str]:
    return [lacuna.id for lacuna in lacunas]


def test_proxima_devolve_a_de_maior_peso_entre_as_ativas():
    e = Entrevista("Nenhum sinal reconhecivel aqui")
    primeira = e.proxima()
    assert primeira is not None
    assert primeira.peso == max(lacuna.peso for lacuna in e.pendentes())


def test_empate_de_peso_resolve_pela_ordem_do_catalogo_e_nao_por_sorteio():
    """`problema` e `onde_roda` tem peso 10; `problema` vem antes no catalogo."""
    for _ in range(5):
        e = Entrevista("")
        assert e.proxima().id == "problema"
    e = Entrevista("")
    assert _ids(e.pendentes())[:2] == ["problema", "onde_roda"]


def test_pendentes_esta_ordenada_por_peso_decrescente():
    e = Entrevista("")
    pesos = [lacuna.peso for lacuna in e.pendentes()]
    assert pesos == sorted(pesos, reverse=True)


def test_responder_remove_a_lacuna_da_fila():
    e = Entrevista("")
    alvo = e.proxima()
    e.responder(alvo.id, "resposta qualquer")
    assert alvo.id not in _ids(e.pendentes())
    assert e.proxima().id != alvo.id


def test_lacuna_desconhecida_ao_responder_id_inexistente():
    e = Entrevista("")
    with pytest.raises(LacunaDesconhecida):
        e.responder("nao_existe", "valor")


def test_lacuna_desconhecida_tambem_ao_pedir_o_motivo():
    e = Entrevista("")
    with pytest.raises(LacunaDesconhecida):
        e.porque("nao_existe")


def test_porque_devolve_o_motivo_declarado_no_catalogo():
    e = Entrevista("")
    assert "criterio para escolher" in e.porque("problema")


def test_palpite_nao_confirmado_nao_entra_em_respostas():
    e = Entrevista(IDEIA_MOBILE)
    assert len(e.palpites_pendentes()) >= 1
    assert e.respostas() == ()
    assert e.plataformas() == ()
    assert "mobile_offline" not in _ids(e.pendentes())


def test_confirmar_mobile_destrava_lacunas_novas():
    e = Entrevista(IDEIA_MOBILE)
    antes = set(_ids(e.pendentes()))
    palpite = next(p for p in e.palpites_pendentes() if p.valor == Plataforma.MOBILE)
    e.confirmar(palpite)
    depois = set(_ids(e.pendentes()))
    assert e.plataformas() == (Plataforma.MOBILE,)
    assert {"mobile_offline", "mobile_loja"} <= depois - antes
    assert palpite not in e.palpites_pendentes()


def test_recusar_remove_da_pendencia_sem_aplicar_nada():
    e = Entrevista(IDEIA_MOBILE)
    palpite = next(p for p in e.palpites_pendentes() if p.valor == Plataforma.MOBILE)
    e.recusar(palpite)
    assert e.palpites_pendentes() == ()
    assert e.plataformas() == ()
    assert "mobile_offline" not in _ids(e.pendentes())
    assert e.respostas() == ()


def test_confirmar_contexto_destrava_o_bloco_do_contexto():
    e = Entrevista("Preciso cobrar pelo pedido no site da loja.")
    for palpite in e.palpites_pendentes():
        e.confirmar(palpite)
    assert Contexto.LOJA_PAGAMENTOS in e.contextos()
    assert "pag_cobranca_dupla" in _ids(e.pendentes())


def test_confirmar_palpite_com_valor_invalido_levanta():
    e = Entrevista("")
    with pytest.raises(PalpiteDesconhecido):
        e.confirmar(Palpite(valor="NUVEM", origem=Origem.INFERIDO, evidencia="x", confianca="ALTA"))


def test_responder_onde_roda_tambem_destrava_sem_caso_especial_por_id():
    e = Entrevista("")
    assert "desktop_sistema" not in _ids(e.pendentes())
    e.responder("onde_roda", "DESKTOP")
    assert e.plataformas() == (Plataforma.DESKTOP,)
    assert "desktop_sistema" in _ids(e.pendentes())


def test_responder_de_novo_substitui_e_preserva_a_posicao():
    e = Entrevista("")
    e.responder("problema", "primeira")
    e.responder("usuario", "dono da loja")
    e.responder("problema", "segunda")
    assert [chave for chave, _, _ in e.respostas()] == ["problema", "usuario"]
    assert e.respostas()[0][1] == "segunda"


def test_origem_padrao_e_respondido_e_a_declarada_viaja():
    e = Entrevista("")
    e.responder("problema", "dor real")
    e.responder("sucesso", "meta estimada", origem=Origem.INFERIDO)
    origens = {chave: origem for chave, _, origem in e.respostas()}
    assert origens["problema"] is Origem.RESPONDIDO
    assert origens["sucesso"] is Origem.INFERIDO


def test_lacuna_abaixo_do_peso_minimo_nao_e_perguntada_e_fica_aberta():
    e = Entrevista("")
    e.responder("onde_roda", "WEB")
    assert "web_idioma" not in _ids(e.pendentes())
    while e.proxima() is not None:
        e.responder(e.proxima().id, "decidido")
    assert e.proxima() is None
    assert "web_idioma" in _ids(e.decisoes_abertas())


def test_peso_minimo_e_parametrizavel_e_muda_o_que_se_pergunta():
    baixo = Entrevista("", peso_minimo=1)
    baixo.responder("onde_roda", "WEB")
    assert "web_idioma" in _ids(baixo.pendentes())

    alto = Entrevista("", peso_minimo=9)
    assert all(lacuna.peso >= 9 for lacuna in alto.pendentes())
    assert "fora_de_escopo" not in _ids(alto.pendentes())
    assert "fora_de_escopo" in _ids(alto.decisoes_abertas())


def test_decisoes_abertas_contem_as_pendentes_e_mais_as_de_peso_baixo():
    e = Entrevista("")
    e.responder("onde_roda", "MOBILE")
    abertas = set(_ids(e.decisoes_abertas()))
    assert set(_ids(e.pendentes())) < abertas
    assert "mobile_tablet" in abertas


def test_progresso_cresce_no_denominador_quando_o_contexto_destrava():
    e = Entrevista("")
    _, alvo_antes = e.progresso()
    e.responder("onde_roda", "MOBILE")
    respondidas, alvo_depois = e.progresso()
    assert respondidas == 1
    assert alvo_depois > alvo_antes


def test_progresso_termina_com_numerador_igual_ao_denominador():
    e = Entrevista("")
    while e.proxima() is not None:
        e.responder(e.proxima().id, "decidido")
    respondidas, alvo = e.progresso()
    assert respondidas == alvo > 0


def test_catalogo_injetado_e_respeitado():
    catalogo = (
        Lacuna(id="a", pergunta="A?", porque="pq", peso=5, universal=True),
        Lacuna(id="b", pergunta="B?", porque="pq", peso=9, universal=True),
    )
    e = Entrevista("", catalogo=catalogo)
    assert _ids(e.pendentes()) == ["b", "a"]
    with pytest.raises(LacunaDesconhecida):
        e.responder("problema", "x")


def test_deteccao_do_construtor_e_a_mesma_da_funcao_pura():
    e = Entrevista(IDEIA_MOBILE)
    esperados = detectar_plataformas(IDEIA_MOBILE)
    assert all(p in e.palpites_pendentes() for p in esperados)
