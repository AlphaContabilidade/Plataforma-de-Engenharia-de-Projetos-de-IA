"""A especificacao nunca se declara completa quando nao esta."""

from __future__ import annotations

from catalogo import Plataforma
from deteccao import Origem
from entrevista import Entrevista
from especificacao import gerar

IDEIA_MOBILE = "Quero um aplicativo de celular para os pedidos da loja."


def _responder_tudo(e: Entrevista, valor: str = "decidido") -> None:
    while e.proxima() is not None:
        e.responder(e.proxima().id, valor)


def _caminho_feliz() -> Entrevista:
    """Web sem palpite pendente, com todas as universais e todo o bloco web resolvidos."""
    e = Entrevista("Preciso de uma forma melhor de organizar o estoque da papelaria")
    assert e.palpites_pendentes() == ()
    e.responder("onde_roda", "WEB")
    _responder_tudo(e)
    return e


def test_completa_e_falsa_com_inferencia_pendente():
    e = Entrevista(IDEIA_MOBILE)
    palpite = next(p for p in e.palpites_pendentes() if p.valor == Plataforma.MOBILE)
    e.responder("onde_roda", "MOBILE")
    _responder_tudo(e)
    spec = gerar(e)
    assert palpite in spec.inferencias_pendentes
    assert spec.completa is False


def test_confirmar_a_inferencia_remove_o_impedimento():
    e = Entrevista(IDEIA_MOBILE)
    for palpite in e.palpites_pendentes():
        e.confirmar(palpite)
    _responder_tudo(e)
    spec = gerar(e)
    assert spec.inferencias_pendentes == ()
    assert spec.completa is True


def test_recusar_a_inferencia_tambem_remove_o_impedimento_sem_aplicar():
    e = Entrevista(IDEIA_MOBILE)
    for palpite in e.palpites_pendentes():
        e.recusar(palpite)
    e.responder("onde_roda", "DESKTOP")
    _responder_tudo(e)
    spec = gerar(e)
    assert spec.plataformas == (Plataforma.DESKTOP,)
    assert spec.completa is True


def test_completa_e_falsa_com_lacuna_universal_aberta():
    e = Entrevista("Preciso organizar o estoque da papelaria")
    e.responder("onde_roda", "WEB")
    e.responder("problema", "controle de estoque no papel se perde")
    spec = gerar(e)
    abertas_universais = [lacuna.id for lacuna in spec.decisoes_abertas if lacuna.universal]
    assert abertas_universais
    assert spec.completa is False


def test_completa_e_verdadeira_no_caminho_feliz():
    spec = gerar(_caminho_feliz())
    assert spec.inferencias_pendentes == ()
    assert all(not lacuna.universal for lacuna in spec.decisoes_abertas)
    assert spec.completa is True


def test_decisao_aberta_de_peso_baixo_nao_impede_a_completude_mas_consta():
    spec = gerar(_caminho_feliz())
    abertas = [lacuna.id for lacuna in spec.decisoes_abertas]
    assert "web_idioma" in abertas
    assert spec.completa is True


def test_respostas_carregam_a_origem_declarada():
    e = Entrevista("")
    e.responder("problema", "estoque no papel se perde")
    e.responder("usuario", "duas pessoas do balcao", origem=Origem.INFERIDO)
    spec = gerar(e)
    por_id = {chave: (valor, origem) for chave, valor, origem in spec.respostas}
    assert por_id["problema"][1] is Origem.RESPONDIDO
    assert por_id["usuario"][1] is Origem.INFERIDO


def test_markdown_traz_as_duas_secoes_sempre():
    incompleta = gerar(Entrevista(IDEIA_MOBILE))
    completa = gerar(_caminho_feliz())
    for texto in (incompleta.markdown(), completa.markdown()):
        assert "## Decisoes abertas" in texto
        assert "## Inferencias nao confirmadas" in texto


def test_markdown_mostra_a_pergunta_e_nunca_um_valor_assumido():
    spec = gerar(Entrevista(IDEIA_MOBILE))
    texto = spec.markdown()
    assert "Que problema isso resolve hoje" in texto
    assert "PADRAO_ASSUMIDO" not in texto
    assert "incompleta" in texto


def test_markdown_de_especificacao_vazia_diz_nenhuma_em_vez_de_omitir():
    spec = gerar(Entrevista(""))
    texto = spec.markdown()
    assert "Nenhuma. Toda inferencia foi confirmada ou recusada." in texto
    assert "Nada decidido." in texto
    assert "Nenhuma confirmada" in texto


def test_markdown_lista_a_evidencia_de_cada_inferencia_pendente():
    spec = gerar(Entrevista(IDEIA_MOBILE))
    texto = spec.markdown()
    for palpite in spec.inferencias_pendentes:
        assert palpite.evidencia in texto
        assert palpite.confianca in texto


def test_especificacao_e_um_retrato_e_nao_acompanha_a_entrevista():
    e = Entrevista("")
    antes = gerar(e)
    e.responder("problema", "resolvido depois do retrato")
    depois = gerar(e)
    assert antes.respostas == ()
    assert len(depois.respostas) == 1
