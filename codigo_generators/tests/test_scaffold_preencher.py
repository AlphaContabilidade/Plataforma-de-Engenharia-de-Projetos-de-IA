"""Testes para scaffold_preencher nativo."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from codigo_generators.scaffold_preencher import (
    gerar_app_jsx,
    gerar_app_css,
    gerar_index_js,
    gerar_env_example,
    gerar_package_json_frontend,
    gerar_package_json_backend,
    listar_arquivos_para_preencher,
    gerar_readme,
)


class TestGeradorReact:
    def test_gera_app_jsx_com_blueprint(self):
        """Gera App.jsx com dados do blueprint."""
        blueprint = {
            "nome": "Meu App",
            "objetivo_transformacao": "Gerenciar tarefas",
            "mvp": ["Criar tarefa", "Listar tarefas"],
        }

        codigo = gerar_app_jsx(blueprint)

        assert "Meu App" in codigo
        assert "Gerenciar tarefas" in codigo
        assert "Criar tarefa" in codigo
        assert "Listar tarefas" in codigo
        assert "useState" in codigo
        assert "export default" in codigo

    def test_gera_app_jsx_sem_mvp(self):
        """Funciona sem MVP."""
        blueprint = {"nome": "App"}
        codigo = gerar_app_jsx(blueprint)

        assert "App" in codigo
        assert "<li>MVP</li>" in codigo

    def test_gera_css_valido(self):
        """CSS é válido."""
        css = gerar_app_css()

        assert ".app {" in css
        assert ".app-header" in css
        assert "background" in css
        assert "flex" in css
        assert "@media" in css  # Responsivo


class TestGeradorNodeJS:
    def test_gera_index_js_com_rotas(self):
        """Gera Express com rotas CRUD."""
        codigo = gerar_index_js({})

        assert "express()" in codigo
        assert "cors()" in codigo
        assert "/api/health" in codigo
        assert "/api/items" in codigo
        assert "GET" in codigo or "app.get" in codigo
        assert "POST" in codigo or "app.post" in codigo
        assert "PUT" in codigo or "app.put" in codigo
        assert "DELETE" in codigo or "app.delete" in codigo

    def test_gera_env_example(self):
        """Gera .env.example."""
        env = gerar_env_example()

        assert "PORT=3000" in env
        assert "NODE_ENV=development" in env


class TestGeradorPackageJson:
    def test_gera_package_json_frontend(self):
        """package.json frontend é JSON válido."""
        import json

        pkg_str = gerar_package_json_frontend("test-app")
        pkg = json.loads(pkg_str)

        assert pkg["name"] == "test-app-frontend"
        assert "react" in pkg["dependencies"]
        assert "dev" in pkg["scripts"]

    def test_gera_package_json_backend(self):
        """package.json backend é JSON válido."""
        import json

        pkg_str = gerar_package_json_backend("test-app")
        pkg = json.loads(pkg_str)

        assert pkg["name"] == "test-app-backend"
        assert "express" in pkg["dependencies"]
        assert "start" in pkg["scripts"]


class TestListarArquivos:
    def test_lista_arquivos_existentes(self):
        """Lista apenas arquivos que existem."""
        with TemporaryDirectory() as tmpdir:
            raiz = Path(tmpdir)

            # Cria estrutura
            (raiz / "frontend" / "src").mkdir(parents=True)
            (raiz / "backend" / "src").mkdir(parents=True)

            (raiz / "frontend" / "src" / "App.jsx").write_text("placeholder")
            (raiz / "backend" / "src" / "index.js").write_text("placeholder")

            arquivos = listar_arquivos_para_preencher(raiz)

            assert "frontend/src/App.jsx" in arquivos
            assert "backend/src/index.js" in arquivos


class TestGeradorReadme:
    def test_gera_readme_com_blueprint(self):
        """README contém dados do blueprint."""
        with TemporaryDirectory() as tmpdir:
            raiz = Path(tmpdir) / "meu-app"
            blueprint = {
                "nome": "Meu App",
                "resumo": "Um app legal",
                "objetivo_transformacao": "Fazer algo",
            }

            readme = gerar_readme(blueprint, raiz)

            assert "Meu App" in readme
            assert "Um app legal" in readme
            assert "Fazer algo" in readme
            assert "npm install" in readme
            assert "http://localhost:5173" in readme
            assert "http://localhost:3000" in readme
