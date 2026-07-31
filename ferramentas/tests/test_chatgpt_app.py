"""Contrato minimo do ChatGPT App: ferramentas, recurso e respostas."""

import asyncio

from starlette.testclient import TestClient

from chatgpt_app import server as S


def rodar(coro):
    return asyncio.run(coro)


def test_app_expoe_as_cinco_intencoes():
    ferramentas = {tool.name: tool for tool in rodar(S.mcp.list_tools())}
    assert set(ferramentas) == {
        "abrir_construtor",
        "personalizar_descoberta",
        "planejar_software",
        "consultar_acervo",
        "consultar_volume",
    }
    assert all(tool.annotations.readOnlyHint for tool in ferramentas.values())
    assert all(not tool.annotations.destructiveHint for tool in ferramentas.values())


def test_ferramentas_do_construtor_apontam_para_o_widget():
    ferramentas = {tool.name: tool for tool in rodar(S.mcp.list_tools())}
    for nome in ("abrir_construtor", "personalizar_descoberta", "planejar_software"):
        assert ferramentas[nome].meta["ui"]["resourceUri"] == S.WIDGET_URI


def test_recurso_do_widget_usa_mime_e_bridge_mcp_apps():
    recursos = rodar(S.mcp.list_resources())
    assert len(recursos) == 1
    assert str(recursos[0].uri) == S.WIDGET_URI
    assert recursos[0].mimeType == S.MIME_TYPE
    html = rodar(S.recurso_do_construtor())
    assert html.startswith("<!doctype html>")
    assert '"ui/initialize"' in html
    assert '"tools/call"' in html
    assert '"ui/message"' in html
    assert 'type="file"' in html
    assert "Plano de Solução" in html
    assert "Obrigatório" in html
    assert "Opcional" in html
    assert "sem modelo de IA no servidor" in html
    assert "Começar diagnóstico" in html
    assert "Analisar projeto existente" in html
    assert "Caminhos de evolução recomendados" in html
    assert "Pergunta 1" in html
    assert "Suplemento" in html
    assert "Agente de produto" in html
    assert ">Prévia<" in html
    assert ">Gerenciar<" in html
    assert "Aplicar ajuste" in html
    assert "Publicar versão" in html
    assert "https://" not in html


def test_planejar_software_reusa_o_motor_da_plataforma():
    resposta = rodar(
        S.planejar_software(
            ideia="Organizar agendamentos e reduzir faltas em clinicas pequenas.",
            publico="recepcionistas e donos de clinicas",
            problema="confirmacoes manuais causam faltas",
            integracoes=["WhatsApp"],
            dados_sensiveis=True,
            documentos=[
                {
                    "nome": "requisitos.md",
                    "tipo": "text/markdown",
                    "tamanho": 42,
                    "conteudo": "Confirmar todos os agendamentos.",
                }
            ],
        )
    )
    assert resposta.isError is False
    assert resposta.structuredContent["modo"] == "blueprint"
    blueprint = resposta.structuredContent["blueprint"]
    assert "WhatsApp" in blueprint["markdown"]
    assert "requisitos.md" in blueprint["markdown"]
    assert blueprint["motor_elaboracao"].startswith("Planejador determinístico")
    assert any(v["id"] == "17" for v in blueprint["volumes_recomendados"])


def test_descoberta_mcp_personaliza_mobile():
    resposta = rodar(
        S.personalizar_descoberta(
            "Aplicativo para técnicos registrarem fotos e visitas no celular.",
            "auto",
        )
    )
    assert resposta.isError is False
    assert resposta.structuredContent["modo"] == "descoberta"
    assert resposta.structuredContent["tipo_inferido"] == "mobile"


def test_interface_local_funciona_sem_ponte_mcp():
    with TestClient(S.app) as cliente:
        pagina = cliente.get("/widget.html")
        assert pagina.status_code == 200
        assert "Começar diagnóstico" in pagina.text

        descoberta = cliente.post(
            "/api/perguntas",
            json={
                "ideia": "Programa para PC que controla estoque mesmo sem internet.",
                "tipo": "auto",
            },
        )
        assert descoberta.status_code == 200
        assert descoberta.json()["tipo_inferido"] == "desktop"

        suplemento = cliente.post(
            "/api/perguntas",
            json={
                "ideia": "Suplemento do Excel para analisar células e gerar fórmulas.",
                "tipo": "auto",
            },
        )
        assert suplemento.status_code == 200
        assert suplemento.json()["tipo_inferido"] == "extensao"

        existente = cliente.post(
            "/api/perguntas",
            json={
                "ideia": "Temos planilhas e um sistema antigo de vendas sem integração.",
                "tipo": "web",
                "modo": "existente",
            },
        )
        assert existente.status_code == 200
        assert existente.json()["modo"] == "descoberta"
        assert existente.json()["modo_projeto"] == "existente"
        assert any(
            p["id"] == "objetivo_transformacao"
            for p in existente.json()["perguntas"]
        )

        plano = cliente.post(
            "/api/planejar",
            json={
                "ideia": "Programa para PC que controla estoque mesmo sem internet.",
                "publico": "equipe do estoque",
                "problema": "planilhas divergentes e falta de rastreabilidade",
                "tipo": "desktop",
                "prioridade": "qualidade",
            },
        )
        assert plano.status_code == 200
        assert plano.json()["modo"] == "blueprint"
        assert "Plano de Solução" in plano.json()["blueprint"]["markdown"]


def test_consultas_leem_o_acervo_real():
    acervo = rodar(S.consultar_acervo())
    assert acervo["total"] == 42
    volume = rodar(S.consultar_volume("07"))
    assert volume["nome"] == "PROMPT-ENGINE"
    assert volume["status"] == "PRONTO"
