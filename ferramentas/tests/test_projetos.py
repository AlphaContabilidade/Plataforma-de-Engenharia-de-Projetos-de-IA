"""Testa o construtor guiado sem navegador e sem modelo externo."""

import pytest

from ferramentas.projetos import (
    ProjetoInvalido,
    gerar_blueprint,
    gerar_perguntas_personalizadas,
)


IDEIA = {
    "nome": "Agenda Facil",
    "ideia": "Organizar os agendamentos e reduzir faltas em clinicas pequenas.",
    "publico": "recepcionistas e donos de clinicas",
    "problema": "horarios espalhados e confirmacoes manuais",
    "tipo": "web",
    "prioridade": "qualidade",
    "usuarios": "de 10 a 100 usuarios",
    "integracoes": ["WhatsApp", "Google Agenda"],
    "dados_sensiveis": True,
    "prazo": "piloto em 60 dias",
    "restricoes": "equipe de duas pessoas",
}


def test_blueprint_personaliza_arquitetura_e_volumes():
    dado = gerar_blueprint(IDEIA).para_dict()
    assert dado["nome"] == "Agenda Facil"
    assert dado["motor_elaboracao"] == "Planejador determinístico AI-ENGINEERING-OS v1"
    assert "recepcionistas" in dado["resumo"]
    assert any("WhatsApp" in item for item in dado["mvp"])
    ids = {volume["id"] for volume in dado["volumes_recomendados"]}
    assert {"03", "04", "16", "17", "22", "23", "30", "31", "38"} <= ids
    assert "# Plano de Solução" in dado["markdown"]
    assert "**Modelo de IA no servidor:** nenhum" in dado["markdown"]
    assert "Perguntas ainda abertas" in dado["markdown"]


def test_automacao_inclui_fila_de_excecoes():
    entrada = dict(IDEIA, tipo="automacao", dados_sensiveis=False, integracoes=[])
    dado = gerar_blueprint(entrada)
    assert any("excecoes" in item for item in dado.mvp)
    ids = {volume["id"] for volume in dado.volumes_recomendados}
    assert {"10", "16"} <= ids


@pytest.mark.parametrize("campo", ["ideia", "publico", "problema"])
def test_campos_humanos_essenciais_sao_obrigatorios(campo):
    entrada = dict(IDEIA)
    entrada[campo] = ""
    with pytest.raises(ProjetoInvalido, match=campo):
        gerar_blueprint(entrada)


def test_tipo_desconhecido_nao_e_inventado():
    with pytest.raises(ProjetoInvalido, match="tipo desconhecido"):
        gerar_blueprint(dict(IDEIA, tipo="metaverso-quantico"))


def test_sem_detalhes_ganha_perguntas_pendentes():
    entrada = dict(
        IDEIA,
        prazo="",
        usuarios="",
        integracoes=[],
        restricoes="",
        dados_sensiveis=False,
    )
    perguntas = gerar_blueprint(entrada).perguntas_pendentes
    assert any("data real" in item for item in perguntas)
    assert any("Quantas pessoas" in item for item in perguntas)
    assert any("orcamento" in item for item in perguntas)


def test_documentos_entram_no_plano_com_limites():
    entrada = dict(
        IDEIA,
        documentos=[
            {
                "nome": "requisitos.md",
                "tipo": "text/markdown",
                "tamanho": 123,
                "conteudo": "# Requisitos\nConfirmacao por WhatsApp",
            },
            {
                "nome": "contrato.pdf",
                "tipo": "application/pdf",
                "tamanho": 456,
                "conteudo": "",
            },
        ],
    )
    dado = gerar_blueprint(entrada).para_dict()
    assert [d["nome"] for d in dado["documentos_referencia"]] == [
        "requisitos.md",
        "contrato.pdf",
    ]
    assert "texto disponível para análise" in dado["markdown"]
    assert "sem extração automática" in dado["markdown"]
    assert any("contrato.pdf" in pergunta for pergunta in dado["perguntas_pendentes"])


def test_documento_maior_que_cinco_mb_e_recusado():
    entrada = dict(
        IDEIA,
        documentos=[
            {
                "nome": "grande.pdf",
                "tipo": "application/pdf",
                "tamanho": 5 * 1024 * 1024 + 1,
            }
        ],
    )
    with pytest.raises(ProjetoInvalido, match="5 MB"):
        gerar_blueprint(entrada)


def test_perguntas_mobile_sao_especificas_para_o_aparelho():
    descoberta = gerar_perguntas_personalizadas(
        "Aplicativo para técnicos registrarem visitas e fotos no celular.", "auto"
    )
    assert descoberta["tipo_inferido"] == "mobile"
    perguntas = {p["id"]: p for p in descoberta["perguntas"]}
    assert "Câmera ou leitura de código" in perguntas["recurso_plataforma"]["opcoes"]


def test_perguntas_de_loja_incluem_decisao_de_pagamento():
    descoberta = gerar_perguntas_personalizadas(
        "Loja virtual para vender roupas com catálogo, pedidos e entrega.", "web"
    )
    perguntas = {p["id"]: p for p in descoberta["perguntas"]}
    assert "decisao_especifica" in perguntas
    assert "Pix e cartão" in perguntas["decisao_especifica"]["opcoes"]


def test_respostas_personalizadas_entram_no_plano():
    entrada = dict(
        IDEIA,
        respostas_descoberta={
            "recurso_plataforma": "Uso offline",
            "estilo_visual": "Profissional e discreta",
        },
    )
    dado = gerar_blueprint(entrada).para_dict()
    assert dado["decisoes_descoberta"]["recurso_plataforma"] == "Uso offline"
    assert "Decisões da descoberta personalizada" in dado["markdown"]
    assert any("Uso offline" in item for item in dado["mvp"])
