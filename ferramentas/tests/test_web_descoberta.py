"""Testa a tela de descoberta pela funcao pura de roteamento.

Mesmo padrao de `test_web.py`: nenhum teste abre socket, escolhe porta ou fala com
navegador. `web.responder` recebe metodo, caminho, raiz, contrato, o corpo do POST e
o registro de sessoes, e devolve `(status, content_type, corpo)`.

Duas escolhas deste arquivo merecem registro.

**Registro de sessoes proprio em cada teste.** `web.SESSOES` e estado de processo, e
teste que o usasse herdaria entrevista de outro teste - com a agravante de que o teto
de sessoes tornaria a suite dependente da ordem de coleta. Cada teste recebe um
`RegistroDeSessoes` novo pela fixture `sessoes`.

**Acervo sintetico de proposito.** Os testes passam a raiz de `volume_engine`, que e
um acervo em `tmp_path` sem pasta `exemplos/`. Isso prova uma propriedade que importa:
o motor de descoberta vem de `raiz_da_plataforma()` - a pasta desta plataforma,
deduzida de `__file__` - e nao da raiz que a requisicao ou o `--raiz` indicaram. Se
alguem trocar isso por um caminho vindo de fora, estes testes falham com
`MotorAusente`.
"""
import json
from pathlib import Path

import pytest

from ferramentas import contrato as C
from ferramentas import web as W

IDEIA_NEUTRA = "Controle de estoque de uma padaria: quanto sobrou de cada massa no fim do dia."
IDEIA_COM_CONTEXTO = "Agenda de uma clinica de fisioterapia, com remarcacao pela recepcao."

# As cinco universais que sobram depois de a plataforma ser escolhida no seletor:
# `onde_roda` ja entra respondida, e sem estas cinco a especificacao nunca fecha.
UNIVERSAIS_RESTANTES = (
    "problema",
    "usuario",
    "capacidade_nova",
    "sucesso",
    "fora_de_escopo",
)


@pytest.fixture
def sessoes():
    return W.RegistroDeSessoes()


def _chamar(raiz, ct, metodo, caminho, sessoes, dado=None):
    corpo = None if dado is None else json.dumps(dado).encode("utf-8")
    status, tipo, bruto = W.responder(
        metodo, caminho, raiz, ct, corpo=corpo, sessoes=sessoes
    )
    if tipo == W.HTML_UTF8:
        return status, bruto.decode("utf-8")
    assert tipo == W.JSON_UTF8, tipo
    return status, json.loads(bruto.decode("utf-8"))


def _iniciar(raiz, ct, sessoes, ideia=IDEIA_NEUTRA, plataforma="WEB"):
    status, dado = _chamar(
        raiz,
        ct,
        "POST",
        "/api/descoberta/iniciar",
        sessoes,
        {"ideia": ideia, "plataforma": plataforma},
    )
    assert status == 200, dado
    return dado


# --- a tela ---------------------------------------------------------------


def test_descoberta_devolve_a_pagina_html(volume_engine):
    raiz, _ = volume_engine
    status, tipo, corpo = W.responder("GET", "/descoberta", raiz, C.carregar(raiz))
    assert status == 200
    assert tipo == W.HTML_UTF8
    texto = corpo.decode("utf-8")
    assert texto.startswith("<!doctype html>")
    assert "Descobrir o que construir" in texto


def test_a_tela_oferece_as_quatro_plataformas_do_catalogo(volume_engine):
    """O seletor sai do catalogo, nao de uma lista escrita na pagina.

    A lista e injetada pelo servidor a partir da enumeracao `Plataforma`. Se o volume
    03 ganhar uma quinta plataforma, ela aparece na tela sem ninguem editar a camada
    web - e este teste passa a exigir as cinco.
    """
    raiz, _ = volume_engine
    _, texto = _chamar(raiz, C.carregar(raiz), "GET", "/descoberta", W.RegistroDeSessoes())
    for nome in W.plataformas_do_catalogo():
        assert json.dumps(nome) in texto, nome
    assert set(W.plataformas_do_catalogo()) == {"WEB", "MOBILE", "DESKTOP", "AUTOMACAO"}


def test_a_tela_tem_cinco_ideias_de_exemplo_clicaveis(volume_engine):
    raiz, _ = volume_engine
    _, texto = _chamar(raiz, C.carregar(raiz), "GET", "/descoberta", W.RegistroDeSessoes())
    bloco = texto.split("var EXEMPLOS = [", 1)[1].split("];", 1)[0]
    assert bloco.count('",') + 1 == 5, bloco
    assert 'criar("button", "exemplo"' in texto


def test_a_tela_nao_busca_nada_de_fora(volume_engine):
    """Sem CDN, sem framework, sem icone externo - igual ao resto do modulo."""
    raiz, _ = volume_engine
    _, texto = _chamar(raiz, C.carregar(raiz), "GET", "/descoberta", W.RegistroDeSessoes())
    assert "http://" not in texto.replace("http://127.0.0.1", "")
    assert "https://" not in texto
    assert "<script src" not in texto
    assert texto.count("<link") == 1
    assert '<link rel="icon" href="data:,">' in texto


def test_as_duas_telas_se_alcancam_e_usam_os_mesmos_tokens(volume_engine):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    _, painel = _chamar(raiz, ct, "GET", "/", W.RegistroDeSessoes())
    _, descoberta = _chamar(raiz, ct, "GET", "/descoberta", W.RegistroDeSessoes())
    assert 'href="/descoberta"' in painel
    assert 'href="/"' in descoberta
    for token in ("#2E3A8C", "#93A0F0", "#1B7F6B", "#4FBFA3", "#A8641B", "#D69A4C"):
        assert token in painel, token
        assert token in descoberta, token
    assert 'data-theme="dark"' in descoberta
    assert 'data-theme="light"' in descoberta


def test_a_tela_nao_usa_innerhtml(volume_engine):
    """Evidencia e resposta sao texto de quem usa; texto de quem usa nao vira marcacao."""
    raiz, _ = volume_engine
    _, texto = _chamar(raiz, C.carregar(raiz), "GET", "/descoberta", W.RegistroDeSessoes())
    assert "innerHTML" not in texto
    assert "outerHTML" not in texto
    assert "insertAdjacentHTML" not in texto


# --- iniciar --------------------------------------------------------------


def test_plataforma_escolhida_traz_o_bloco_de_aparelho_de_mao_e_nao_o_de_navegador(
    volume_engine, sessoes
):
    """A escolha do seletor destrava um bloco e cala os outros tres.

    E a propriedade que justifica o seletor existir: `MOBILE` faz aparecer a pergunta
    de funcionar sem rede e a de loja de aplicativos, e faz **desaparecer** a de
    navegador minimo. Pergunta irrelevante nao entra desabilitada nem no fim da lista -
    ela nao existe para esta entrevista (regra R3 do volume 03).
    """
    dado = _iniciar(volume_engine[0], C.carregar(volume_engine[0]), sessoes, plataforma="MOBILE")
    assert dado["plataformas"] == ["MOBILE"]
    assert "mobile_offline" in dado["pendentes"]
    assert "mobile_loja" in dado["pendentes"]
    for de_navegador in ("web_navegador", "web_autenticacao", "web_hospedagem"):
        assert de_navegador not in dado["pendentes"], de_navegador


def test_a_plataforma_entra_como_respondida_e_nao_como_palpite(volume_engine, sessoes):
    """O seletor SUBSTITUI a inferencia de plataforma - nao a alimenta.

    A ideia deste teste diz "no celular", que a deteccao le como `MOBILE` com
    confianca alta. Com `WEB` escolhido no seletor, o resultado correto e: nenhuma
    plataforma pendente de confirmacao, `onde_roda` respondida com origem
    `RESPONDIDO`, e o palpite descartado visivel com a evidencia que o produziu -
    para a pessoa ver que a escolha dela venceu, e nao que o palpite foi engolido.
    """
    raiz, _ = volume_engine
    dado = _iniciar(
        raiz,
        C.carregar(raiz),
        sessoes,
        ideia="Catalogo de pecas de uma oficina, para consultar no celular do balcao.",
        plataforma="WEB",
    )
    assert dado["plataformas"] == ["WEB"]
    assert [p["valor"] for p in dado["palpites"]] == []
    assert ("onde_roda", "WEB", "RESPONDIDO") in [
        (r["lacuna_id"], r["valor"], r["origem"]) for r in dado["respostas"]
    ]
    descartada = dado["plataforma_inferida_descartada"]
    assert [p["valor"] for p in descartada] == ["MOBILE"]
    assert "celular" in descartada[0]["evidencia"]


def test_plataforma_invalida_devolve_400_dizendo_as_aceitas(volume_engine, sessoes):
    raiz, _ = volume_engine
    status, dado = _chamar(
        raiz,
        C.carregar(raiz),
        "POST",
        "/api/descoberta/iniciar",
        sessoes,
        {"ideia": IDEIA_NEUTRA, "plataforma": "TABLET"},
    )
    assert status == 400
    assert "WEB" in dado["erro"] and "AUTOMACAO" in dado["erro"]
    assert len(sessoes) == 0


def test_ideia_acima_do_teto_devolve_400_sem_criar_sessao(volume_engine, sessoes):
    """Texto sem limite entra no motor de deteccao e vira CPU do servidor."""
    raiz, _ = volume_engine
    status, dado = _chamar(
        raiz,
        C.carregar(raiz),
        "POST",
        "/api/descoberta/iniciar",
        sessoes,
        {"ideia": "a" * (W.LIMITE_DA_IDEIA + 1), "plataforma": "WEB"},
    )
    assert status == 400
    assert str(W.LIMITE_DA_IDEIA) in dado["erro"]
    assert len(sessoes) == 0


def test_ideia_em_branco_devolve_400_com_o_que_fazer(volume_engine, sessoes):
    raiz, _ = volume_engine
    status, dado = _chamar(
        raiz,
        C.carregar(raiz),
        "POST",
        "/api/descoberta/iniciar",
        sessoes,
        {"ideia": "   ", "plataforma": "WEB"},
    )
    assert status == 400
    assert "exemplos" in dado["erro"]


def test_corpo_ausente_ou_nao_json_devolve_400(volume_engine, sessoes):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    for corpo in (None, b"", b"nao sou json", b'"texto solto"', b"[]"):
        status, tipo, bruto = W.responder(
            "POST", "/api/descoberta/iniciar", raiz, ct, corpo=corpo, sessoes=sessoes
        )
        assert status == 400, corpo
        assert tipo == W.JSON_UTF8


def test_corpo_acima_do_teto_json_devolve_400(volume_engine, sessoes):
    raiz, _ = volume_engine
    gordo = b"x" * (W.LIMITE_DE_CORPO_JSON + 1)
    status, _, bruto = W.responder(
        "POST",
        "/api/descoberta/iniciar",
        raiz,
        C.carregar(raiz),
        corpo=gordo,
        sessoes=sessoes,
    )
    assert status == 400
    assert str(W.LIMITE_DE_CORPO_JSON) in json.loads(bruto)["erro"]


# --- responder ------------------------------------------------------------


def test_responder_devolve_a_proxima_pergunta_e_o_progresso_coerente(
    volume_engine, sessoes
):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    dado = _iniciar(raiz, ct, sessoes)
    primeira = dado["pergunta"]
    antes = dado["progresso"]
    assert antes["respondidas"] == 1  # `onde_roda`, vinda do seletor
    assert antes["total"] > antes["respondidas"]

    status, depois = _chamar(
        raiz,
        ct,
        "POST",
        "/api/descoberta/responder",
        sessoes,
        {
            "sessao": dado["sessao"],
            "lacuna_id": primeira["id"],
            "valor": "quem cuida do balcao perde tempo contando na mao",
        },
    )
    assert status == 200
    assert depois["progresso"]["respondidas"] == antes["respondidas"] + 1
    assert depois["progresso"]["total"] == antes["total"]
    assert depois["pergunta"]["id"] != primeira["id"]
    assert primeira["id"] not in depois["pendentes"]
    # A pergunta chega com o motivo dela, que e o que o botao "Por que essa
    # pergunta?" revela. Justificativa e conteudo revisado do catalogo, nunca texto
    # montado na tela.
    assert depois["pergunta"]["porque"].strip()


def test_uma_pergunta_por_vez_e_sempre_a_de_maior_peso(volume_engine, sessoes):
    raiz, _ = volume_engine
    dado = _iniciar(raiz, C.carregar(raiz), sessoes)
    assert dado["pergunta"]["id"] == dado["pendentes"][0]
    assert dado["pergunta"]["peso"] == 10


def test_sessao_desconhecida_devolve_400(volume_engine, sessoes):
    raiz, _ = volume_engine
    status, dado = _chamar(
        raiz,
        C.carregar(raiz),
        "POST",
        "/api/descoberta/responder",
        sessoes,
        {"sessao": "id-que-nunca-existiu", "lacuna_id": "problema", "valor": "x"},
    )
    assert status == 400
    assert "descoberta" in dado["erro"]
    # A mensagem nao ecoa o id recebido: nao ha nada a ganhar devolvendo para dentro
    # da pagina o texto que chegou na requisicao.
    assert "id-que-nunca-existiu" not in dado["erro"]


def test_lacuna_fora_do_catalogo_devolve_400(volume_engine, sessoes):
    """Id validado contra o catalogo ANTES de qualquer uso.

    Sem esta validacao, `Entrevista.responder` levantaria `LacunaDesconhecida` e a
    resposta viraria 500 - erro de servidor para o que e erro de quem pediu.
    """
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    dado = _iniciar(raiz, ct, sessoes)
    # `problema ` com espaco sobrando **e** aceito: espaco em volta e acidente de
    # digitacao e nao id diferente. Diferenca de caixa nao: os ids do catalogo sao
    # minusculos e `PROBLEMA` seria outro id.
    for inventado in ("nao_existe", "../catalogo", "", "PROBLEMA", "problema.md"):
        status, erro = _chamar(
            raiz,
            ct,
            "POST",
            "/api/descoberta/responder",
            sessoes,
            {"sessao": dado["sessao"], "lacuna_id": inventado, "valor": "x"},
        )
        assert status == 400, inventado
        assert "catalogo de lacunas" in erro["erro"]


def test_resposta_em_branco_devolve_400(volume_engine, sessoes):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    dado = _iniciar(raiz, ct, sessoes)
    status, erro = _chamar(
        raiz,
        ct,
        "POST",
        "/api/descoberta/responder",
        sessoes,
        {"sessao": dado["sessao"], "lacuna_id": "problema", "valor": "  "},
    )
    assert status == 400
    assert "opcoes" in erro["erro"]


# --- palpite de contexto --------------------------------------------------


def test_confirmar_palpite_de_contexto_destrava_lacunas_novas(volume_engine, sessoes):
    """O denominador CRESCE, e crescer e o comportamento correto.

    Confirmar saude acrescenta tres lacunas ao conjunto ativo. Uma barra que so
    avanca exigiria um total conhecido desde o inicio, e num grafo de decisao ele nao
    e - por isso o campo `total_pode_crescer` viaja junto em vez de a tela fingir.
    """
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    dado = _iniciar(raiz, ct, sessoes, ideia=IDEIA_COM_CONTEXTO)
    assert [p["valor"] for p in dado["palpites"]] == ["SAUDE"]
    assert dado["palpites"][0]["origem"] == "INFERIDO"
    assert "clinica" in dado["palpites"][0]["evidencia"]
    assert dado["progresso"]["total_pode_crescer"] is True
    antes = dado["progresso"]["total"]

    status, depois = _chamar(
        raiz,
        ct,
        "POST",
        "/api/descoberta/palpite",
        sessoes,
        {"sessao": dado["sessao"], "valor": "SAUDE", "aceitar": True},
    )
    assert status == 200
    assert depois["contextos"] == ["SAUDE"]
    assert depois["progresso"]["total"] > antes
    assert depois["palpites"] == []
    assert depois["progresso"]["total_pode_crescer"] is False
    for da_saude in ("saude_dado_sensivel", "saude_quem_ve", "saude_retencao"):
        assert da_saude in depois["pendentes"], da_saude


def test_recusar_palpite_nao_destrava_nada(volume_engine, sessoes):
    """Recusar e um clique, e recusado nao deixa rastro de valor assumido."""
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    dado = _iniciar(raiz, ct, sessoes, ideia=IDEIA_COM_CONTEXTO)
    antes = dado["progresso"]["total"]

    status, depois = _chamar(
        raiz,
        ct,
        "POST",
        "/api/descoberta/palpite",
        sessoes,
        {"sessao": dado["sessao"], "valor": "SAUDE", "aceitar": False},
    )
    assert status == 200
    assert depois["contextos"] == []
    assert depois["progresso"]["total"] == antes
    assert depois["palpites"] == []
    assert "saude_dado_sensivel" not in depois["pendentes"]
    assert [r["lacuna_id"] for r in depois["respostas"]] == ["onde_roda"]


def test_palpite_exige_aceitar_booleano(volume_engine, sessoes):
    """Sem padrao para `aceitar`: omissao lida como sim seria a violacao da regra R1."""
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    dado = _iniciar(raiz, ct, sessoes, ideia=IDEIA_COM_CONTEXTO)
    for corpo in (
        {"sessao": dado["sessao"], "valor": "SAUDE"},
        {"sessao": dado["sessao"], "valor": "SAUDE", "aceitar": "sim"},
        {"sessao": dado["sessao"], "valor": "SAUDE", "aceitar": 1},
    ):
        status, erro = _chamar(
            raiz, ct, "POST", "/api/descoberta/palpite", sessoes, corpo
        )
        assert status == 400, corpo
        assert "aceitar" in erro["erro"]


def test_palpite_que_nao_esta_pendente_devolve_400(volume_engine, sessoes):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    dado = _iniciar(raiz, ct, sessoes, ideia=IDEIA_NEUTRA)
    status, erro = _chamar(
        raiz,
        ct,
        "POST",
        "/api/descoberta/palpite",
        sessoes,
        {"sessao": dado["sessao"], "valor": "SAUDE", "aceitar": True},
    )
    assert status == 400
    assert "pendente" in erro["erro"]


# --- especificacao --------------------------------------------------------


def test_especificacao_com_lacuna_universal_aberta_nao_se_declara_completa(
    volume_engine, sessoes
):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    dado = _iniciar(raiz, ct, sessoes)
    status, spec = _chamar(
        raiz, ct, "GET", "/api/descoberta/especificacao/" + dado["sessao"], sessoes
    )
    assert status == 200
    assert spec["completa"] is False
    assert spec["por_que_nao_completa"], spec
    assert any("qualquer software" in motivo for motivo in spec["por_que_nao_completa"])
    abertas = {lacuna["id"] for lacuna in spec["decisoes_abertas"]}
    assert "problema" in abertas
    assert "# Especificacao" in spec["markdown"]
    assert "## Decisoes abertas" in spec["markdown"]
    assert "## Inferencias nao confirmadas" in spec["markdown"]
    # Nenhum valor adotado por falta de resposta aparece como decidido.
    assert "PADRAO_ASSUMIDO" not in spec["markdown"]


def test_palpite_pendente_sozinho_ja_impede_a_completude(volume_engine, sessoes):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    dado = _iniciar(raiz, ct, sessoes, ideia=IDEIA_COM_CONTEXTO)
    for lacuna_id in UNIVERSAIS_RESTANTES:
        _chamar(
            raiz,
            ct,
            "POST",
            "/api/descoberta/responder",
            sessoes,
            {"sessao": dado["sessao"], "lacuna_id": lacuna_id, "valor": "decidido"},
        )
    _, spec = _chamar(
        raiz, ct, "GET", "/api/descoberta/especificacao/" + dado["sessao"], sessoes
    )
    assert spec["completa"] is False
    assert [p["valor"] for p in spec["inferencias_pendentes"]] == ["SAUDE"]
    assert any("supos" in motivo for motivo in spec["por_que_nao_completa"])


def test_caminho_feliz_traz_completa_true(volume_engine, sessoes):
    """Sem universal aberta e sem palpite pendente, e so nesse caso.

    Decisao aberta de peso baixo continua existindo (`web_idioma` nunca e perguntada)
    e nao impede a completude - a assimetria e do motor, e a tela nao a reescreve.
    """
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    dado = _iniciar(raiz, ct, sessoes, ideia=IDEIA_NEUTRA, plataforma="WEB")
    assert dado["palpites"] == []
    for lacuna_id in UNIVERSAIS_RESTANTES:
        status, dado = _chamar(
            raiz,
            ct,
            "POST",
            "/api/descoberta/responder",
            sessoes,
            {"sessao": dado["sessao"], "lacuna_id": lacuna_id, "valor": "decidido"},
        )
        assert status == 200, lacuna_id
    _, spec = _chamar(
        raiz, ct, "GET", "/api/descoberta/especificacao/" + dado["sessao"], sessoes
    )
    assert spec["completa"] is True
    assert spec["por_que_nao_completa"] == []
    assert spec["inferencias_pendentes"] == []
    assert not any(lacuna["universal"] for lacuna in spec["decisoes_abertas"])
    assert "web_idioma" in {lacuna["id"] for lacuna in spec["decisoes_abertas"]}
    assert "**Estado:** completa" in spec["markdown"]


def test_especificacao_sem_id_de_sessao_devolve_400(volume_engine, sessoes):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    for rota in ("/api/descoberta/especificacao", "/api/descoberta/especificacao/"):
        status, erro = _chamar(raiz, ct, "GET", rota, sessoes)
        assert status == 400, rota
        assert "descoberta" in erro["erro"]


# --- sessoes --------------------------------------------------------------


def test_id_de_sessao_nao_e_sequencial(volume_engine, sessoes):
    """Id previsivel deixaria outra aba ler entrevista alheia nesta maquina.

    O id **e** a credencial da entrevista: nao ha login, e qualquer pagina aberta no
    navegador alcanca `127.0.0.1`. Por isso ele vem de `secrets.token_urlsafe` e nao
    de um contador.
    """
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    ids = [_iniciar(raiz, ct, sessoes)["sessao"] for _ in range(4)]
    assert len(set(ids)) == 4
    for chave in ids:
        assert len(chave) >= 22, chave
        assert not chave.isdigit()
    assert "1" not in ids and "0" not in ids
    fonte = Path(W.__file__).read_text(encoding="utf-8")
    assert "secrets.token_urlsafe" in fonte


def test_teto_de_sessoes_descarta_a_mais_antiga_sem_quebrar_as_outras(
    volume_engine,
):
    """Sem teto, um cliente em laco consome memoria do servidor sem limite.

    O descarte e da mais antiga (ordem de chegada, que `dict` preserva), e ele nao
    pode encostar nas demais: a que caiu responde 400 com instrucao, e as que ficaram
    continuam respondendo 200.
    """
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    pequeno = W.RegistroDeSessoes(teto=3)
    ids = [_iniciar(raiz, ct, pequeno)["sessao"] for _ in range(4)]
    assert len(pequeno) == 3
    assert ids[0] not in pequeno.ids()

    status, erro = _chamar(
        raiz, ct, "GET", "/api/descoberta/especificacao/" + ids[0], pequeno
    )
    assert status == 400
    assert "teto de 3" in erro["erro"]

    for viva in ids[1:]:
        status, spec = _chamar(
            raiz, ct, "GET", "/api/descoberta/especificacao/" + viva, pequeno
        )
        assert status == 200, viva
        assert spec["sessao"] == viva


def test_registro_recusa_id_gigante_antes_de_procurar(volume_engine, sessoes):
    raiz, _ = volume_engine
    status, erro = _chamar(
        raiz,
        C.carregar(raiz),
        "GET",
        "/api/descoberta/especificacao/" + "z" * (W.LIMITE_DO_ID_DE_SESSAO + 1),
        sessoes,
    )
    assert status == 400
    assert "formato" in erro["erro"]


def test_teto_padrao_do_processo_e_declarado():
    assert W.TETO_DE_SESSOES == 32
    assert W.SESSOES.teto == W.TETO_DE_SESSOES


# --- rota e metodo --------------------------------------------------------


def test_metodo_trocado_nas_rotas_de_descoberta_devolve_405(volume_engine, sessoes):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    for metodo, rota in (
        ("GET", "/api/descoberta/iniciar"),
        ("GET", "/api/descoberta/responder"),
        ("GET", "/api/descoberta/palpite"),
        ("POST", "/descoberta"),
        ("POST", "/api/descoberta/especificacao/qualquer"),
        ("PUT", "/descoberta"),
    ):
        status, erro = _chamar(raiz, ct, metodo, rota, sessoes)
        assert status == 405, (metodo, rota)
        assert metodo in erro["erro"]


def test_404_lista_as_rotas_de_descoberta(volume_engine, sessoes):
    raiz, _ = volume_engine
    status, erro = _chamar(raiz, C.carregar(raiz), "GET", "/api/descoberta", sessoes)
    assert status == 404
    assert "/api/descoberta/iniciar" in erro["erro"]
    assert "/api/descoberta/especificacao/<sessao>" in erro["erro"]


def test_query_e_barra_final_nao_criam_recurso_novo(volume_engine, sessoes):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    dado = _iniciar(raiz, ct, sessoes)
    status, spec = _chamar(
        raiz,
        ct,
        "GET",
        "/api/descoberta/especificacao/" + dado["sessao"] + "/?x=1",
        sessoes,
    )
    assert status == 200
    assert spec["sessao"] == dado["sessao"]


# --- procedencia do motor -------------------------------------------------


def test_o_motor_vem_da_pasta_desta_plataforma_e_nao_da_requisicao():
    """Codigo importado nao pode ser escolhido por quem faz a chamada.

    `--raiz` aponta para outro acervo de volumes em Markdown; deixar esse parametro
    escolher de onde os modulos do motor sao importados transformaria uma opcao de
    leitura em carregamento de codigo arbitrario.
    """
    esperada = W.raiz_padrao() / "exemplos" / "03-discovery"
    motor = W.motor_de_descoberta()
    for modulo in motor:
        assert Path(modulo.__file__).parent == esperada, modulo.__name__
    assert motor is W.motor_de_descoberta()  # carregado uma vez


def test_nenhuma_regra_do_motor_e_reimplementada_na_camada_web(volume_engine, sessoes):
    """Pergunta, peso, motivo e completude saem do volume 03, nao daqui.

    O texto de toda pergunta que a tela mostra e o texto do catalogo, caractere a
    caractere. Regra duplicada em camada de apresentacao e como a interface passa a
    mentir sobre o motor.
    """
    raiz, _ = volume_engine
    catalogo = W.motor_de_descoberta().catalogo
    do_catalogo = {lacuna.id: lacuna for lacuna in catalogo.CATALOGO}
    dado = _iniciar(raiz, C.carregar(raiz), sessoes, plataforma="AUTOMACAO")
    for lacuna_id in dado["pendentes"]:
        assert lacuna_id in do_catalogo, lacuna_id
    pergunta = dado["pergunta"]
    assert pergunta["pergunta"] == do_catalogo[pergunta["id"]].pergunta
    assert pergunta["porque"] == do_catalogo[pergunta["id"]].porque
    assert pergunta["peso"] == do_catalogo[pergunta["id"]].peso
    assert "auto_disparo" in dado["pendentes"]
    assert "mobile_offline" not in dado["pendentes"]
