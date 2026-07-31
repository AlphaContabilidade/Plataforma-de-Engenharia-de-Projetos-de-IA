"""Servidor MCP que leva a AI-ENGINEERING-OS para dentro do ChatGPT.

As ferramentas desta primeira versao sao somente leitura: organizam respostas,
consultam o acervo e devolvem um plano de solucao. Nenhuma delas cria arquivos de projeto
ou executa comandos. Essa separacao deixa a conexao inicial segura e permite que
uma futura ferramenta de construcao tenha confirmacao e auditoria proprias.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, Any

import mcp.types as types
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import Field
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse

from ferramentas import painel
from ferramentas.contrato import carregar
from ferramentas.projetos import (
    ProjetoInvalido,
    gerar_blueprint,
    gerar_perguntas_personalizadas,
)
from ferramentas.status import levantar


RAIZ = Path(__file__).resolve().parents[1]
WIDGET = Path(__file__).with_name("widget.html")
WIDGET_URI = "ui://ai-engineering-os/construtor-v1.html"
MIME_TYPE = "text/html;profile=mcp-app"

LEITURA = types.ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)


def _lista_env(nome: str) -> list[str]:
    return [
        item.strip()
        for item in (os.getenv(nome) or "").split(",")
        if item.strip()
    ]


def _seguranca_transporte() -> TransportSecuritySettings:
    hosts = _lista_env("MCP_ALLOWED_HOSTS")
    origens = _lista_env("MCP_ALLOWED_ORIGINS")
    if not hosts and not origens:
        return TransportSecuritySettings(enable_dns_rebinding_protection=False)
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=hosts,
        allowed_origins=origens,
    )


def _meta_widget(acao: str) -> dict[str, Any]:
    return {
        "ui": {"resourceUri": WIDGET_URI},
        "openai/outputTemplate": WIDGET_URI,
        "openai/toolInvocation/invoking": acao,
        "openai/toolInvocation/invoked": "Pronto",
        "openai/widgetAccessible": True,
    }


mcp = FastMCP(
    name="ai-engineering-os",
    instructions=(
        "Use abrir_construtor quando a pessoa quiser transformar uma ideia em software. "
        "Reuna ideia, publico e problema em linguagem simples; depois use planejar_software. "
        "As ferramentas sao somente leitura e nunca afirmam que o codigo foi construido."
    ),
    stateless_http=True,
    transport_security=_seguranca_transporte(),
)


@mcp.resource(
    WIDGET_URI,
    name="Construtor de software",
    title="AI-ENGINEERING-OS — Construtor",
    description="Formulario e plano de solucao interativos dentro do ChatGPT.",
    mime_type=MIME_TYPE,
    meta={
        "ui": {
            "prefersBorder": True,
            "csp": {"connectDomains": [], "resourceDomains": []},
        },
        "openai/widgetDescription": (
            "Construtor guiado que transforma uma ideia em um plano profissional de solucao."
        ),
    },
)
async def recurso_do_construtor() -> str:
    return WIDGET.read_text(encoding="utf-8")


@mcp.tool(
    name="abrir_construtor",
    title="Abrir construtor de software",
    description=(
        "Use quando a pessoa quiser descrever uma ideia, responder perguntas simples "
        "ou iniciar o planejamento personalizado de um software."
    ),
    annotations=LEITURA,
    meta=_meta_widget("Abrindo o construtor"),
    structured_output=True,
)
async def abrir_construtor() -> types.CallToolResult:
    dado = {
        "modo": "formulario",
        "etapa": 1,
        "totalEtapas": 4,
        "mensagem": "Descreva a ideia em linguagem simples para comecar.",
    }
    return types.CallToolResult(
        content=[
            types.TextContent(
                type="text",
                text=(
                    "Construtor aberto. Ajude a pessoa a definir ideia, publico, problema, "
                    "formato, prioridade, integracoes e restricoes."
                ),
            )
        ],
        structuredContent=dado,
        _meta=_meta_widget("Abrindo o construtor"),
        isError=False,
    )


@mcp.tool(
    name="personalizar_descoberta",
    title="Criar perguntas personalizadas",
    description=(
        "Use depois que a pessoa descrever a ideia. Identifica o contexto e devolve "
        "perguntas curtas e específicas para web, mobile, desktop ou automação."
    ),
    annotations=LEITURA,
    meta=_meta_widget("Personalizando as perguntas"),
    structured_output=True,
)
async def personalizar_descoberta(
    ideia: Annotated[str, Field(min_length=20, max_length=4000)],
    tipo: Annotated[
        str, Field(description="Um de: auto, web, mobile, desktop, automacao ou extensao.")
    ] = "auto",
    modo: Annotated[
        str, Field(description="novo para criar ou existente para analisar e evoluir.")
    ] = "novo",
) -> types.CallToolResult:
    try:
        descoberta = gerar_perguntas_personalizadas(ideia, tipo, modo)
    except ProjetoInvalido as erro:
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Entrada invalida: {erro}")],
            structuredContent={"modo": "erro", "erro": str(erro)},
            _meta=_meta_widget("Personalizando as perguntas"),
            isError=True,
        )
    return types.CallToolResult(
        content=[
            types.TextContent(
                type="text",
                text=(
                    f"Descoberta preparada para {descoberta['tipo_inferido']}. "
                    "Faça uma pergunta por vez e preserve as respostas."
                ),
            )
        ],
        structuredContent={"modo": "descoberta", **descoberta},
        _meta=_meta_widget("Personalizando as perguntas"),
        isError=False,
    )


@mcp.tool(
    name="planejar_software",
    title="Planejar software",
    description=(
        "Use quando ideia, publico e problema ja estiverem claros. Gera um plano de solucao "
        "personalizado com MVP, arquitetura, fases, riscos e conhecimento recomendado."
    ),
    annotations=LEITURA,
    meta=_meta_widget("Elaborando o plano de solucao"),
    structured_output=True,
)
async def planejar_software(
    ideia: Annotated[str, Field(min_length=20, max_length=4000)],
    publico: Annotated[str, Field(min_length=3, max_length=4000)],
    problema: Annotated[str, Field(min_length=3, max_length=4000)],
    nome: Annotated[str, Field(max_length=200)] = "",
    tipo: Annotated[
        str, Field(description="Um de: web, mobile, automacao, api, desktop ou extensao.")
    ] = "web",
    prioridade: Annotated[
        str, Field(description="Uma de: qualidade, velocidade, custo ou escala.")
    ] = "qualidade",
    usuarios: Annotated[str, Field(max_length=200)] = "",
    integracoes: Annotated[list[str] | None, Field(max_length=20)] = None,
    dados_sensiveis: bool = False,
    prazo: Annotated[str, Field(max_length=300)] = "",
    restricoes: Annotated[str, Field(max_length=1000)] = "",
    modo_projeto: Annotated[
        str, Field(description="novo ou existente.")
    ] = "novo",
    documentos: Annotated[
        list[dict[str, Any]] | None,
        Field(
            max_length=30,
            description=(
                "Documentos de referencia com nome, tipo, tamanho e conteudo textual "
                "opcional. Arquivos binarios podem ser registrados sem conteudo."
            ),
        ),
    ] = None,
    respostas_descoberta: Annotated[
        dict[str, str] | None,
        Field(description="Respostas coletadas pelo diagnóstico personalizado."),
    ] = None,
) -> types.CallToolResult:
    try:
        blueprint = gerar_blueprint(
            {
                "nome": nome,
                "ideia": ideia,
                "publico": publico,
                "problema": problema,
                "tipo": tipo,
                "prioridade": prioridade,
                "usuarios": usuarios,
                "integracoes": integracoes or [],
                "dados_sensiveis": dados_sensiveis,
                "prazo": prazo,
                "restricoes": restricoes,
                "modo_projeto": modo_projeto,
                "documentos": documentos or [],
                "respostas_descoberta": respostas_descoberta or {},
            }
        ).para_dict()
    except ProjetoInvalido as erro:
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Entrada invalida: {erro}")],
            structuredContent={"modo": "erro", "erro": str(erro)},
            _meta=_meta_widget("Elaborando o plano de solucao"),
            isError=True,
        )
    estruturado = {"modo": "blueprint", "blueprint": blueprint, "stateVersion": 1}
    return types.CallToolResult(
        content=[
            types.TextContent(
                type="text",
                text=(
                    f"Plano de solucao de {blueprint['nome']} elaborado. Ele ainda e um plano, "
                    "nao software implementado. Revise as perguntas abertas antes do codigo."
                ),
            )
        ],
        structuredContent=estruturado,
        _meta=_meta_widget("Elaborando o plano de solucao"),
        isError=False,
    )


@mcp.tool(
    name="consultar_acervo",
    title="Consultar estado do acervo",
    description=(
        "Use quando a pessoa perguntar quais volumes existem, quais estao prontos "
        "ou qual conhecimento tecnico esta disponivel na plataforma."
    ),
    annotations=LEITURA,
    structured_output=True,
)
async def consultar_acervo() -> dict[str, Any]:
    ct = carregar(RAIZ)
    estados = levantar(RAIZ, ct)
    return {
        "total": len(estados),
        "volumes": [
            {
                "id": e.vol_id,
                "nome": e.nome,
                "tipo": e.tipo,
                "status": e.status,
                "secoes": f"{e.secoes_presentes}/{e.secoes_esperadas}",
                "nota": e.nota_auditoria,
            }
            for e in estados
        ],
    }


@mcp.tool(
    name="consultar_volume",
    title="Consultar volume tecnico",
    description=(
        "Use quando a pessoa quiser entender o escopo, dependencias, secoes ou "
        "regras de um volume especifico da AI-ENGINEERING-OS."
    ),
    annotations=LEITURA,
    structured_output=True,
)
async def consultar_volume(
    volume: Annotated[
        str, Field(pattern=r"^\d{2}$", description="ID com dois digitos.")
    ],
) -> dict[str, Any]:
    ct = carregar(RAIZ)
    briefing = painel.briefing_de(RAIZ, volume, ct)
    return {
        "id": briefing.vol_id,
        "nome": briefing.nome,
        "tipo": briefing.tipo,
        "status": briefing.status,
        "depende_de": list(briefing.depende_de),
        "secoes_ausentes": list(briefing.secoes_ausentes),
        "diagramas_obrigatorios": list(briefing.diagramas_obrigatorios),
        "escopo": briefing.escopo,
    }


app = mcp.streamable_http_app()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)


async def saude(_request):
    return JSONResponse(
        {
            "nome": "AI-ENGINEERING-OS ChatGPT App",
            "status": "ok",
            "mcp": "/mcp",
            "interface": "/widget.html",
        }
    )


async def interface_local(_request: Request):
    """Entrega o mesmo widget fora do ChatGPT para uso e teste local."""
    return HTMLResponse(WIDGET.read_text(encoding="utf-8"))


async def perguntas_locais(request: Request):
    """API do navegador local; reutiliza exatamente o motor exposto pelo MCP."""
    try:
        entrada = await request.json()
        descoberta = gerar_perguntas_personalizadas(
            entrada.get("ideia", ""),
            entrada.get("tipo", "auto"),
            entrada.get("modo", "novo"),
        )
        return JSONResponse({"modo": "descoberta", **descoberta})
    except (AttributeError, ValueError, ProjetoInvalido) as erro:
        return JSONResponse({"modo": "erro", "erro": str(erro)}, status_code=400)


async def planejar_local(request: Request):
    """Elabora o plano no navegador local sem depender da ponte do ChatGPT."""
    try:
        entrada = await request.json()
        blueprint = gerar_blueprint(entrada).para_dict()
        return JSONResponse(
            {"modo": "blueprint", "blueprint": blueprint, "stateVersion": 1}
        )
    except (AttributeError, ValueError, ProjetoInvalido) as erro:
        return JSONResponse({"modo": "erro", "erro": str(erro)}, status_code=400)


app.add_route("/", saude, methods=["GET"])
app.add_route("/widget.html", interface_local, methods=["GET"])
app.add_route("/api/perguntas", perguntas_locais, methods=["POST"])
app.add_route("/api/planejar", planejar_local, methods=["POST"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT", "8000")))
