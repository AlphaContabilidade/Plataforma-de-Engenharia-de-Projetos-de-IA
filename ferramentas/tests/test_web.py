"""Testa a interface web pela funcao pura de roteamento.

Nenhum teste abre socket, escolhe porta ou fala com navegador. `web.responder` e
uma funcao pura de `(metodo, caminho, raiz, contrato)` para
`(status, content_type, corpo)`, e e ela que carrega toda a decisao da interface -
o handler de `http.server` so converte a tripla em resposta HTTP. Teste que
subisse servidor de verdade verificaria o `http.server` da biblioteca padrao e
ficaria dependente de porta livre na maquina de quem roda a suite.

O gate 2 chama `pytest` em subprocesso. Nos testes que exercitam
`POST /api/gates/NN` isso e desligado com `rodar_testes=False`: pytest dentro de
pytest e lento e frageis por conta do plugin de cobertura e do cwd herdado. O
proprio veredicto do gate 2 diz "execucao desligada", e o teste confere essa
frase em vez de fingir que houve execucao.
"""
import json
from pathlib import Path

import pytest

from ferramentas import contrato as C
from ferramentas import web as W

RELATORIO = "VOL-07-auditoria-2026-07-29.md"


def _json_de(resposta):
    status, tipo, corpo = resposta
    assert tipo == W.JSON_UTF8, tipo
    return status, json.loads(corpo.decode("utf-8"))


def _com_auditoria(raiz: Path) -> str:
    """Grava um relatorio de auditoria valido no acervo sintetico."""
    pasta = raiz / "auditorias"
    pasta.mkdir(exist_ok=True)
    (pasta / RELATORIO).write_text(
        "# Auditoria do volume 07\n\nmedia: 8.9\n", encoding="utf-8"
    )
    return RELATORIO


# --- a pagina -------------------------------------------------------------


def test_raiz_devolve_a_pagina_html(volume_engine):
    raiz, _ = volume_engine
    status, tipo, corpo = W.responder("GET", "/", raiz, C.carregar(raiz))
    assert status == 200
    assert tipo == W.HTML_UTF8
    texto = corpo.decode("utf-8")
    assert texto.startswith("<!doctype html>")
    assert "AI-ENGINEERING-OS" in texto


def test_a_pagina_explica_os_tres_gates_e_a_definicao_de_pronto(volume_engine):
    """O bloco "Como funciona" e requisito, nao enfeite: e o que responde "como usar"."""
    raiz, _ = volume_engine
    _, _, corpo = W.responder("GET", "/", raiz, C.carregar(raiz))
    texto = corpo.decode("utf-8")
    for pedaco in (
        "ferramentas.validar NN",
        "pytest exemplos",
        "--cross-refs",
        "Definicao de PRONTO",
    ):
        assert pedaco in texto, pedaco


def test_a_pagina_nao_busca_nada_de_fora(volume_engine):
    """Sem CDN: CSS e JS embutidos. Um acervo local nao depende de rede para abrir."""
    raiz, _ = volume_engine
    _, _, corpo = W.responder("GET", "/", raiz, C.carregar(raiz))
    texto = corpo.decode("utf-8")
    assert "http://" not in texto.replace("http://127.0.0.1", "")
    assert "https://" not in texto
    assert "<script src" not in texto
    # O unico <link> e o icone vazio embutido como data URI, para o navegador nao
    # pedir /favicon.ico e sujar o log do servidor com um 404 que nao e defeito.
    assert texto.count("<link") == 1
    assert '<link rel="icon" href="data:,">' in texto


# --- acervo ---------------------------------------------------------------


def test_acervo_devolve_os_42_e_o_resumo(volume_engine):
    raiz, _ = volume_engine
    status, dado = _json_de(W.responder("GET", "/api/acervo", raiz, C.carregar(raiz)))
    assert status == 200
    assert dado["total"] == 42
    assert len(dado["volumes"]) == 42
    assert dado["contagem"]["RASCUNHO"] == 1
    assert dado["contagem"]["PENDENTE"] == 41
    assert dado["mais_avancado"]["id"] == "07"
    assert "gates" in dado["proxima_acao"].lower()


def test_acervo_traz_todos_os_campos_de_cada_volume(volume_engine):
    raiz, _ = volume_engine
    _, dado = _json_de(W.responder("GET", "/api/acervo", raiz, C.carregar(raiz)))
    esperados = {
        "id", "nome", "tipo", "status",
        "secoes_presentes", "secoes_esperadas", "nota", "perecivel",
    }
    for item in dado["volumes"]:
        assert set(item) == esperados
    primeiro = dado["volumes"][0]
    assert primeiro["id"] == "01"
    assert primeiro["nome"] == "FUNDACAO"
    assert primeiro["secoes_esperadas"] == 18


def test_acervo_nao_afirma_que_a_suite_esta_verde(volume_engine):
    """Contagem estatica de teste nao e veredicto de execucao.

    A proibicao 3 da plataforma - nunca afirmar sucesso sem ter olhado - vale para
    a propria interface. O campo `verificado` sai False e o comando que produz o
    veredicto viaja junto.
    """
    raiz, _ = volume_engine
    _, dado = _json_de(W.responder("GET", "/api/acervo", raiz, C.carregar(raiz)))
    testes = dado["testes"]
    assert testes["verificado"] is False
    assert testes["comando"] == W.COMANDO_DA_SUITE
    # No acervo sintetico nao existe pasta de testes: a contagem e zero, nao um
    # numero herdado do repositorio de verdade.
    assert testes["funcoes_de_teste"] == 0


def test_contagem_de_testes_encontra_a_suite_real():
    raiz = W.raiz_padrao()
    testes = W.contagem_de_testes(raiz)
    assert testes["arquivos"] >= 10
    assert testes["funcoes_de_teste"] > 100
    assert testes["verificado"] is False


# --- detalhe do volume ----------------------------------------------------


def test_volume_07_completo_nao_tem_secao_ausente_e_mostra_a_auditoria(volume_engine):
    raiz, _ = volume_engine
    nome = _com_auditoria(raiz)
    status, dado = _json_de(W.responder("GET", "/api/volume/07", raiz, C.carregar(raiz)))
    assert status == 200
    assert dado["id"] == "07"
    assert dado["nome"] == "PROMPT-ENGINE"
    assert dado["tipo"] == "ENGINE"
    assert dado["secoes_ausentes"] == []
    assert len(dado["secoes_presentes"]) == 18
    assert dado["auditoria"]["relatorio"] == nome
    assert dado["auditoria"]["nota"] == 8.9


def test_volume_01_sem_pasta_lista_as_18_secoes_ausentes(volume_engine):
    raiz, _ = volume_engine
    _, dado = _json_de(W.responder("GET", "/api/volume/01", raiz, C.carregar(raiz)))
    assert dado["tipo"] == "GOVERNANCA"
    assert len(dado["secoes_ausentes"]) == 18
    assert dado["secoes_presentes"] == []
    assert dado["auditoria"] == {"relatorio": None, "nota": None}


def test_volume_traz_dependencias_e_fronteira(volume_engine):
    raiz, pasta = volume_engine
    (pasta / "_VOLUME.yml").write_text(
        'volume: "07"\nnome: PROMPT-ENGINE\ntipo: ENGINE\n'
        'status: RASCUNHO\nperecivel: false\ndepende_de: ["01"]\n',
        encoding="utf-8",
    )
    _, dado = _json_de(W.responder("GET", "/api/volume/07", raiz, C.carregar(raiz)))
    assert dado["depende_de"] == ["01"]
    assert dado["pre_requisitos"] == [
        {"id": "01", "nome": "FUNDACAO", "status": "PENDENTE"}
    ]
    # Sem ROADMAP.md em disco a fronteira e None, nunca inventada.
    assert dado["fronteira"] is None


def test_fronteira_do_acervo_real_chega_ao_json():
    raiz = W.raiz_padrao()
    _, dado = _json_de(W.responder("GET", "/api/volume/07", raiz, C.carregar(raiz)))
    assert dado["fronteira"] is not None
    assert set(dado["fronteira"]["volumes"]) == {"07", "28", "29"}


# --- briefing -------------------------------------------------------------


def test_briefing_08_sai_em_markdown_com_as_18_secoes(volume_engine):
    raiz, _ = volume_engine
    status, dado = _json_de(
        W.responder("GET", "/api/briefing/08", raiz, C.carregar(raiz))
    )
    assert status == 200
    assert dado["volume"] == "08"
    md = dado["markdown"]
    assert "AGENT-ENGINE" in md
    ct = C.carregar(raiz)
    for secao in ct.secoes_de("ENGINE"):
        assert f"`{secao}`" in md
    assert len(ct.secoes_de("ENGINE")) == 18


# --- gates ----------------------------------------------------------------


def test_gates_do_volume_07_aprovam_os_tres(volume_engine):
    """Os tres gates verdes no volume-piloto sintetico.

    `rodar_testes=False` desliga o subprocesso pytest do gate 2 - ver o docstring
    do modulo. O veredicto declara isso no detalhe, e o teste confere.
    """
    raiz, _ = volume_engine
    status, dado = _json_de(
        W.responder(
            "POST", "/api/gates/07", raiz, C.carregar(raiz), rodar_testes=False
        )
    )
    assert status == 200
    assert dado["volume"] == "07"
    assert dado["aprovado"] is True
    assert [g["gate"] for g in dado["gates"]] == [1, 2, 3]
    assert all(g["aprovado"] for g in dado["gates"]), dado["gates"]
    # No acervo sintetico nao existe `exemplos/07-prompt-engine`, e o gate 2 relata
    # "nada a rodar" antes de olhar `rodar_testes` - ausencia de exemplo nao e falha.
    assert "nada a rodar" in dado["gates"][1]["detalhe"]


def test_gates_respeitam_rodar_testes_desligado(volume_engine):
    """Com pasta de exemplos em disco, `rodar_testes=False` nao chama pytest.

    O veredicto diz "execucao desligada" em vez de fingir que houve execucao: e a
    diferenca entre nao ter rodado e ter passado.
    """
    raiz, _ = volume_engine
    (raiz / "exemplos" / "07-prompt-engine").mkdir(parents=True)
    _, dado = _json_de(
        W.responder(
            "POST", "/api/gates/07", raiz, C.carregar(raiz), rodar_testes=False
        )
    )
    assert dado["gates"][1]["detalhe"] == "execucao desligada"


def test_gates_agrupam_as_violacoes_por_regra(volume_engine):
    raiz, pasta = volume_engine
    for secao in ("09-Boas-Praticas", "10-Anti-Patterns", "13-Testes"):
        (pasta / f"{secao}.md").unlink()
    _, dado = _json_de(
        W.responder(
            "POST", "/api/gates/07", raiz, C.carregar(raiz), rodar_testes=False
        )
    )
    assert dado["aprovado"] is False
    gate1 = dado["gates"][0]
    assert gate1["aprovado"] is False
    grupos = gate1["violacoes_por_regra"]
    assert grupos[0]["regra"] == "secao-ausente"
    assert grupos[0]["quantidade"] == 3
    assert len(grupos[0]["itens"]) == 3
    assert grupos[0]["omitidas"] == 0


def test_gate_2_roda_de_verdade_quando_nao_e_desligado(volume_engine):
    """Sem pasta de exemplos nao ha subprocesso: 'nada a rodar' e aprovado."""
    raiz, _ = volume_engine
    _, dado = _json_de(W.responder("POST", "/api/gates/07", raiz, C.carregar(raiz)))
    gate2 = dado["gates"][1]
    assert gate2["aprovado"] is True
    assert "nada a rodar" in gate2["detalhe"]


# --- id invalido ----------------------------------------------------------


@pytest.mark.parametrize(
    "rota",
    ["/api/volume/99", "/api/briefing/99"],
)
def test_id_com_forma_valida_mas_inexistente_devolve_400(volume_engine, rota):
    raiz, _ = volume_engine
    status, dado = _json_de(W.responder("GET", rota, raiz, C.carregar(raiz)))
    assert status == 400
    assert "nao existe volume 99" in dado["erro"]


def test_gates_de_id_inexistente_devolve_400(volume_engine):
    raiz, _ = volume_engine
    status, dado = _json_de(
        W.responder("POST", "/api/gates/99", raiz, C.carregar(raiz))
    )
    assert status == 400
    assert "99" in dado["erro"]


@pytest.mark.parametrize("bruto", ["abc", "7", "007", "0x7", "07a", "..", "%2e%2e"])
def test_id_fora_da_forma_de_dois_digitos_devolve_400(volume_engine, bruto):
    """Forma antes de existencia: `..` e `%2e%2e` morrem sem tocar o disco."""
    raiz, _ = volume_engine
    status, dado = _json_de(
        W.responder("GET", f"/api/volume/{bruto}", raiz, C.carregar(raiz))
    )
    assert status == 400
    assert "dois digitos" in dado["erro"]


def test_rota_com_id_vazio_devolve_404(volume_engine):
    """`/api/volume/` sem id nao e volume nenhum: rota inexistente, nao id ruim."""
    raiz, _ = volume_engine
    status, _ = _json_de(W.responder("GET", "/api/volume/", raiz, C.carregar(raiz)))
    assert status == 404


def test_validar_id_recusa_forma_e_inexistencia(volume_engine):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    assert W.validar_id("07", ct) == "07"
    with pytest.raises(W.IdRecusado):
        W.validar_id("7", ct)
    with pytest.raises(W.IdRecusado):
        W.validar_id("99", ct)


# --- rota e metodo --------------------------------------------------------


def test_rota_desconhecida_devolve_404(volume_engine):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    for rota in ("/api/nada", "/favicon.ico", "/api", "/index.html"):
        status, dado = _json_de(W.responder("GET", rota, raiz, ct))
        assert status == 404, rota
        assert "/api/acervo" in dado["erro"]


def test_put_devolve_405(volume_engine):
    """PUT nao existe nesta interface: 405, com a lista de metodos que valem.

    Escolhido 405 em vez de 404 porque o recurso existe - o que nao existe e a
    intencao de escrever. Esta interface nao altera o acervo por HTTP.

    Sobre socket real, quem responde antes e o `http.server`: como o handler nao
    declara `do_PUT`, um PUT de verdade recebe 501 sem chegar a `responder`. Os
    dois numeros dizem a mesma coisa - o servidor nao aceita escrita - e o 501 e
    ate mais forte, porque nega no adaptador em vez de na regra.
    """
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    for rota in ("/", "/api/acervo", "/api/volume/07", "/api/gates/07"):
        status, dado = _json_de(W.responder("PUT", rota, raiz, ct))
        assert status == 405, rota
        assert "PUT" in dado["erro"]


def test_metodo_trocado_na_rota_certa_devolve_405(volume_engine):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    status, _ = _json_de(W.responder("POST", "/api/acervo", raiz, ct))
    assert status == 405
    status, _ = _json_de(W.responder("GET", "/api/gates/07", raiz, ct))
    assert status == 405


def test_caminho_normaliza_query_e_barra_final(volume_engine):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    assert W.normalizar_caminho("/api/volume/07?x=1#a") == "/api/volume/07"
    assert W.normalizar_caminho("/api/acervo/") == "/api/acervo"
    assert W.normalizar_caminho("/") == "/"
    status, dado = _json_de(W.responder("GET", "/api/volume/07/?forcar=1", raiz, ct))
    assert status == 200
    assert dado["id"] == "07"


# --- independencia do diretorio de lancamento -----------------------------


def test_raiz_padrao_sai_do_modulo_e_nao_do_cwd(monkeypatch, tmp_path):
    """Lancar o servidor de outro diretorio nao pode quebrar o arranque.

    Quem sobe esta interface pelo mecanismo de preview do harness lanca o processo
    da raiz do repositorio, nao de dentro de `AI-ENGINEERING-OS/`. Se a raiz da
    plataforma viesse de `Path(".")`, o contrato nao seria encontrado e o servidor
    morreria por um detalhe de cwd - com uma mensagem culpando o contrato.
    """
    esperada = Path(W.__file__).resolve().parents[1]
    monkeypatch.chdir(tmp_path)
    assert W.raiz_padrao() == esperada
    assert (W.raiz_padrao() / "00-INTRODUCAO" / "contrato.json").is_file()

    ct = C.carregar(W.raiz_padrao())
    status, dado = _json_de(W.responder("GET", "/api/acervo", W.raiz_padrao(), ct))
    assert status == 200
    assert dado["total"] == 42
    assert len(dado["volumes"]) == 42


def test_main_recusa_raiz_sem_contrato(tmp_path, capsys):
    assert W.main(["--raiz", str(tmp_path), "--sem-navegador", "--porta", "0"]) == 2
    assert "contrato ausente" in capsys.readouterr().err


# --- servidor -------------------------------------------------------------


def test_servidor_sobe_apenas_em_loopback():
    """A garantia central: o servidor executa pytest, e por isso nao vai para a rede."""
    assert W.HOST == "127.0.0.1"
    fonte = Path(W.__file__).read_text(encoding="utf-8")
    # Um unico bind no modulo, e ele usa a constante HOST. Se alguem trocar o
    # endereco por parametro configuravel, este teste reprova antes de a interface
    # virar executor remoto.
    assert fonte.count("super().__init__(endereco") == 1
    assert "ServidorDoPainel((HOST, porta + tentativa)" in fonte
    assert "shell=True" not in fonte


def test_porta_zero_pede_uma_livre_ao_sistema():
    """Porta 0 e a forma portavel de nao competir por numero fixo no teste."""
    raiz = W.raiz_padrao()
    servidor = W.subir(raiz, C.carregar(raiz), 0, fixa=True)
    try:
        endereco, porta = servidor.server_address[:2]
        assert endereco == "127.0.0.1"
        assert porta > 0
        assert servidor.raiz == raiz
    finally:
        servidor.server_close()


def test_porta_ocupada_cai_para_a_seguinte():
    raiz = W.raiz_padrao()
    ct = C.carregar(raiz)
    primeiro = W.subir(raiz, ct, 0, fixa=True)
    ocupada = primeiro.server_address[1]
    try:
        segundo = W.subir(raiz, ct, ocupada, fixa=False)
        try:
            assert segundo.server_address[1] != ocupada
            assert segundo.server_address[1] > ocupada
        finally:
            segundo.server_close()
    finally:
        primeiro.server_close()


def test_porta_fixa_ocupada_falha_com_instrucao():
    raiz = W.raiz_padrao()
    ct = C.carregar(raiz)
    primeiro = W.subir(raiz, ct, 0, fixa=True)
    try:
        with pytest.raises(OSError) as erro:
            W.subir(raiz, ct, primeiro.server_address[1], fixa=True)
        assert "--porta" in str(erro.value)
    finally:
        primeiro.server_close()
