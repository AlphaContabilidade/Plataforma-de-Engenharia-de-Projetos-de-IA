"""O catalogo real e valido, e as lacunas condicionais entram somente quando devem."""

from __future__ import annotations

import pytest

from catalogo import (
    CATALOGO,
    CatalogoInvalido,
    Contexto,
    Lacuna,
    Plataforma,
    lacunas_ativas,
    validar_catalogo,
)


def _ids(lacunas) -> set[str]:
    return {lacuna.id for lacuna in lacunas}


def test_catalogo_real_passa_na_propria_validacao():
    """O catalogo publicado nao pode violar as regras que ele impoe a outros."""
    assert validar_catalogo(CATALOGO) == CATALOGO


def test_ids_sao_unicos_e_pesos_estao_na_faixa():
    ids = [lacuna.id for lacuna in CATALOGO]
    assert len(ids) == len(set(ids))
    assert all(1 <= lacuna.peso <= 10 for lacuna in CATALOGO)


def test_todo_id_e_pergunta_e_motivo_sao_nao_vazios():
    for lacuna in CATALOGO:
        assert lacuna.id.strip()
        assert lacuna.pergunta.strip()
        assert lacuna.porque.strip()


def test_lacuna_nao_universal_sempre_tem_gatilho():
    """Sem plataforma e sem contexto, ela seria universal com a marca errada."""
    for lacuna in CATALOGO:
        if not lacuna.universal:
            assert lacuna.plataformas or lacuna.contextos


def test_id_duplicado_reprova():
    base = Lacuna(id="x", pergunta="p", porque="pq", peso=5, universal=True)
    with pytest.raises(CatalogoInvalido, match="duplicado"):
        validar_catalogo((base, base))


@pytest.mark.parametrize("peso", [0, -1, 11, 99])
def test_peso_fora_da_faixa_reprova(peso):
    ruim = Lacuna(id="x", pergunta="p", porque="pq", peso=peso, universal=True)
    with pytest.raises(CatalogoInvalido, match="fora de 1..10"):
        validar_catalogo((ruim,))


def test_lacuna_sem_gatilho_e_nao_universal_reprova():
    orfa = Lacuna(id="orfa", pergunta="p", porque="pq", peso=5, universal=False)
    with pytest.raises(CatalogoInvalido, match="nao tem gatilho"):
        validar_catalogo((orfa,))


def test_motivo_vazio_reprova():
    muda = Lacuna(id="muda", pergunta="p", porque="   ", peso=5, universal=True)
    with pytest.raises(CatalogoInvalido, match="sem motivo"):
        validar_catalogo((muda,))


def test_sem_plataforma_nem_contexto_sobram_apenas_as_universais():
    ativas = lacunas_ativas((), ())
    assert _ids(ativas) == {lacuna.id for lacuna in CATALOGO if lacuna.universal}
    assert "problema" in _ids(ativas)


def test_mobile_traz_offline_e_loja_e_nao_traz_as_de_desktop():
    """O teste central da ideia de lacuna condicional: a pergunta que nao faz sentido nao entra."""
    ativas = _ids(lacunas_ativas((Plataforma.MOBILE,), ()))
    assert "mobile_offline" in ativas
    assert "mobile_loja" in ativas
    assert "mobile_notificacao" in ativas
    assert "mobile_permissao" in ativas
    for de_desktop in ("desktop_sistema", "desktop_instalacao", "desktop_arquivo_local"):
        assert de_desktop not in ativas
    for de_web in ("web_navegador", "web_autenticacao", "web_hospedagem"):
        assert de_web not in ativas


def test_duas_plataformas_juntas_dao_a_uniao_dos_dois_blocos():
    ativas = _ids(lacunas_ativas((Plataforma.WEB, Plataforma.MOBILE), ()))
    assert {"web_autenticacao", "mobile_offline"} <= ativas
    assert "desktop_sistema" not in ativas


def test_contexto_de_pagamento_destrava_a_pergunta_da_cobranca_dupla():
    sem = _ids(lacunas_ativas((Plataforma.WEB,), ()))
    com = _ids(lacunas_ativas((Plataforma.WEB,), (Contexto.LOJA_PAGAMENTOS,)))
    assert "pag_cobranca_dupla" not in sem
    assert {"pag_cobranca_dupla", "pag_provedor", "pag_estorno"} <= com


def test_contexto_de_saude_destrava_dado_sensivel():
    sem = _ids(lacunas_ativas((Plataforma.WEB,), ()))
    com = _ids(lacunas_ativas((Plataforma.WEB,), (Contexto.SAUDE,)))
    assert "saude_dado_sensivel" not in sem
    assert {"saude_dado_sensivel", "saude_quem_ve", "saude_retencao"} <= com
    assert "pag_cobranca_dupla" not in com


def test_lacuna_de_contexto_nao_depende_de_plataforma():
    """Contexto vale em qualquer plataforma; e risco de dominio, nao de meio de entrega."""
    for plataforma in Plataforma:
        ativas = _ids(lacunas_ativas((plataforma,), (Contexto.DADO_PESSOAL,)))
        assert {"pessoal_base_legal", "pessoal_exclusao"} <= ativas


def test_ordem_de_lacunas_ativas_e_a_do_catalogo():
    ativas = lacunas_ativas((Plataforma.MOBILE,), (Contexto.TEMPO_REAL,))
    posicao = {lacuna.id: n for n, lacuna in enumerate(CATALOGO)}
    indices = [posicao[lacuna.id] for lacuna in ativas]
    assert indices == sorted(indices)


def test_lacunas_ativas_aceita_qualquer_iteravel_e_nao_consome_o_catalogo():
    """Chamar duas vezes com geradores devolve o mesmo resultado."""
    primeira = lacunas_ativas(iter([Plataforma.WEB]), iter([]))
    segunda = lacunas_ativas(iter([Plataforma.WEB]), iter([]))
    assert primeira == segunda and primeira
