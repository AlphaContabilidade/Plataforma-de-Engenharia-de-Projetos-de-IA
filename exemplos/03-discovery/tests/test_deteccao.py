"""Inferencia com evidencia, ou nenhuma inferencia."""

from __future__ import annotations

import pytest

from catalogo import Contexto, Plataforma
from deteccao import (
    CONFIANCA_BAIXA,
    Origem,
    Palpite,
    detectar_contextos,
    detectar_plataformas,
)


def _valores(palpites) -> list[str]:
    return [p.valor for p in palpites]


def test_frase_tipica_de_celular_infere_mobile_com_evidencia():
    ideia = "Preciso de um aplicativo de celular para os pedidos da minha loja de bairro."
    palpites = detectar_plataformas(ideia)
    assert _valores(palpites) == [Plataforma.MOBILE]
    unico = palpites[0]
    assert unico.origem is Origem.INFERIDO
    assert unico.evidencia == "um aplicativo de celular para os pedidos"
    assert unico.evidencia in ideia


def test_evidencia_nao_atravessa_o_ponto_final():
    """A janela para na fronteira da frase; a segunda frase nao entra na evidencia."""
    ideia = "A recepcao usa um navegador antigo. O cadastro nao pode mudar."
    palpites = detectar_plataformas(ideia)
    assert _valores(palpites) == [Plataforma.WEB]
    assert palpites[0].evidencia == "recepcao usa um navegador antigo"
    assert "cadastro" not in palpites[0].evidencia


def test_acento_no_texto_nao_impede_o_casamento_e_sai_intacto_na_evidencia():
    ideia = "Quero automatizar a emissão do relatório toda semana."
    palpites = detectar_plataformas(ideia)
    assert _valores(palpites) == [Plataforma.AUTOMACAO]
    assert palpites[0].evidencia == "Quero automatizar a emissão do"
    assert palpites[0].evidencia in ideia


def test_palpites_da_mesma_frase_tem_evidencias_distintas():
    """Regressao: a versao que devolvia a frase inteira dava a mesma evidencia aos tres.

    Evidencia identica em palpites diferentes nao explica nenhum deles -- a pessoa
    pergunta por que o motor concluiu uma coisa e recebe de volta o texto que
    tambem sustentava as outras duas.
    """
    ideia = (
        "Quero um app para a minha loja de bairro, com pagamento no cartao de "
        "credito e um cadastro de clientes para avisar das promocoes."
    )
    palpites = (*detectar_plataformas(ideia), *detectar_contextos(ideia))
    assert len(palpites) == 3
    evidencias = [p.evidencia for p in palpites]
    assert len(set(evidencias)) == 3
    assert all(len(e) < len(ideia) for e in evidencias)


def test_todo_palpite_tem_evidencia_nao_vazia():
    ideia = (
        "Um site para a clinica agendar consulta de paciente, com pagamento por "
        "cartao de credito e integracao com o sistema de agenda da equipe."
    )
    for palpite in (*detectar_plataformas(ideia), *detectar_contextos(ideia)):
        assert palpite.evidencia.strip()
        assert palpite.evidencia in ideia


@pytest.mark.parametrize("vazia", ["", "   ", "\n\t "])
def test_frase_vazia_nao_gera_palpite(vazia):
    assert detectar_plataformas(vazia) == ()
    assert detectar_contextos(vazia) == ()


def test_frase_sem_sinal_nao_gera_palpite_generico():
    """Sem termo conhecido, a resposta e nenhuma -- nunca um valor de fallback."""
    ideia = "Quero uma coisa melhor do que a que eu tenho hoje."
    assert detectar_plataformas(ideia) == ()
    assert detectar_contextos(ideia) == ()


def test_app_e_palpite_de_confianca_baixa_porque_e_ambiguo():
    palpites = detectar_plataformas("Quero um app para a minha loja")
    assert _valores(palpites) == [Plataforma.MOBILE]
    assert palpites[0].confianca == CONFIANCA_BAIXA


def test_fronteira_de_palavra_impede_casamento_dentro_de_outra_palavra():
    """`app` nao casa dentro de `aplicativo`; `site` nao casa dentro de `deposite`."""
    palpites = detectar_plataformas("Um aplicativo simples")
    assert [p.confianca for p in palpites] != [CONFIANCA_BAIXA]
    assert detectar_plataformas("Deposite o arquivo na pasta") == ()


def test_duas_plataformas_no_mesmo_texto_produzem_dois_palpites():
    ideia = "Um site para o cliente e um aplicativo de celular para o entregador."
    assert _valores(detectar_plataformas(ideia)) == [Plataforma.WEB, Plataforma.MOBILE]


def test_um_palpite_por_alvo_mesmo_com_varios_termos_casando():
    ideia = "Site no navegador, pagina web, portal do cliente."
    palpites = detectar_plataformas(ideia)
    assert _valores(palpites) == [Plataforma.WEB]


def test_contextos_sobrepostos_sao_detectados_juntos():
    ideia = "A clinica precisa cobrar a consulta do paciente e guardar o cpf dele."
    detectados = _valores(detectar_contextos(ideia))
    assert Contexto.LOJA_PAGAMENTOS in detectados
    assert Contexto.SAUDE in detectados
    assert Contexto.DADO_PESSOAL in detectados


def test_saida_e_deterministica_para_a_mesma_frase():
    ideia = "Automacao que sincronizar com o sistema da equipe em tempo real."
    assert detectar_plataformas(ideia) == detectar_plataformas(ideia)
    assert detectar_contextos(ideia) == detectar_contextos(ideia)


def test_palpite_e_congelado():
    palpite = Palpite(valor="WEB", origem=Origem.INFERIDO, evidencia="um site", confianca="MEDIA")
    with pytest.raises(Exception):
        palpite.valor = "MOBILE"  # type: ignore[misc]
