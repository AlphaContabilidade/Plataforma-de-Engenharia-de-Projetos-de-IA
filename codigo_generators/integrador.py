"""Integrador: cria scaffold + preenche tudo de uma vez.

Tudo rodando aqui, sem API externa. Claude Code gera código direto.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ferramentas.gerador_scaffold import gerar_scaffold
from codigo_generators.scaffold_preencher import (
    gerar_app_jsx,
    gerar_app_css,
    gerar_index_js,
    gerar_env_example,
    gerar_package_json_frontend,
    gerar_package_json_backend,
    gerar_readme,
    listar_arquivos_para_preencher,
)


@dataclass
class ProjetoGerado:
    """Resultado completo: scaffold + codigo preenchido."""

    nome: str
    diretorio: Path
    arquivos_preenchidos: list[str]
    status: str  # "sucesso", "erro"
    mensagem: str
    passos: list[str]  # Registra cada passo


def gerar_projeto_completo(
    blueprint: dict[str, Any],
    destino: Path,
) -> ProjetoGerado:
    """Cria scaffold + preenche tudo em um comando.

    Args:
        blueprint: Plano de Solucao
        destino: Onde criar o projeto

    Returns:
        ProjetoGerado com projeto completo e executavel
    """
    passos = []
    arquivos_preenchidos = []

    try:
        nome_projeto = blueprint.get("nome", "novo-projeto")
        passos.append(f"[INICIANDO] {nome_projeto}")

        # Fase 1: Cria scaffold
        passos.append("[1/2] Gerando scaffold vazio...")
        scaffold = gerar_scaffold(blueprint, destino)

        if scaffold.status != "criado":
            return ProjetoGerado(
                nome=nome_projeto,
                diretorio=scaffold.diretorio_raiz,
                arquivos_preenchidos=[],
                status="erro",
                mensagem=f"Scaffold falhou: {scaffold.status}",
                passos=passos,
            )

        passos.append(f"OK Scaffold criado em {scaffold.diretorio_raiz}")
        raiz = scaffold.diretorio_raiz

        # Fase 2: Preenche arquivos
        passos.append("[2/2] Preenchendo arquivos com codigo...")

        # Helper: escreve com ASCII puro
        def escrever_ascii(path: Path, conteudo: str) -> None:
            path.write_text(conteudo.encode('ascii', errors='ignore').decode('ascii'))

        # App.jsx
        arquivo_app = raiz / "frontend" / "src" / "App.jsx"
        if arquivo_app.exists():
            escrever_ascii(arquivo_app, gerar_app_jsx(blueprint))
            arquivos_preenchidos.append("frontend/src/App.jsx")
            passos.append("OK App.jsx preenchido")

        # App.css
        arquivo_css = raiz / "frontend" / "src" / "index.css"
        if arquivo_css.exists():
            escrever_ascii(arquivo_css, gerar_app_css())
            arquivos_preenchidos.append("frontend/src/index.css")
            passos.append("OK index.css preenchido")

        # index.js (backend)
        arquivo_backend = raiz / "backend" / "src" / "index.js"
        if arquivo_backend.exists():
            escrever_ascii(arquivo_backend, gerar_index_js(blueprint))
            arquivos_preenchidos.append("backend/src/index.js")
            passos.append("OK backend/src/index.js preenchido")

        # .env.example
        arquivo_env = raiz / "backend" / ".env.example"
        if arquivo_env.exists():
            escrever_ascii(arquivo_env, gerar_env_example())
            arquivos_preenchidos.append("backend/.env.example")
            passos.append("OK .env.example preenchido")

        # package.json files
        pkg_frontend = raiz / "frontend" / "package.json"
        if pkg_frontend.exists():
            escrever_ascii(pkg_frontend, gerar_package_json_frontend(scaffold.nome_projeto))
            passos.append("OK frontend/package.json atualizado")

        pkg_backend = raiz / "backend" / "package.json"
        if pkg_backend.exists():
            escrever_ascii(pkg_backend, gerar_package_json_backend(scaffold.nome_projeto))
            passos.append("OK backend/package.json atualizado")

        # README.md
        arquivo_readme = raiz / "README.md"
        if arquivo_readme.exists():
            escrever_ascii(arquivo_readme, gerar_readme(blueprint, raiz))
            passos.append("OK README.md gerado")

        passos.append("")
        passos.append("PROJETO PRONTO!")
        passos.append("")
        passos.append("Proximos passos:")
        passos.append(f"  cd {raiz.name}")
        passos.append("")
        passos.append("  # Backend")
        passos.append("  cd backend")
        passos.append("  npm install")
        passos.append("  npm start")
        passos.append("")
        passos.append("  # Frontend (em outro terminal)")
        passos.append("  cd ../frontend")
        passos.append("  npm install")
        passos.append("  npm run dev")

        return ProjetoGerado(
            nome=scaffold.nome_projeto,
            diretorio=raiz,
            arquivos_preenchidos=arquivos_preenchidos,
            status="sucesso",
            mensagem=f"Projeto '{nome_projeto}' gerado com sucesso!",
            passos=passos,
        )

    except Exception as e:
        passos.append(f"ERRO: {str(e)}")
        return ProjetoGerado(
            nome=nome_projeto,
            diretorio=destino / nome_projeto,
            arquivos_preenchidos=arquivos_preenchidos,
            status="erro",
            mensagem=str(e),
            passos=passos,
        )


def exibir_resultado(resultado: ProjetoGerado) -> None:
    """Exibe resultado de forma formatada."""
    print("\n" + "=" * 70)
    for passo in resultado.passos:
        print(passo)
    print("=" * 70 + "\n")
