"""Testes para gerador_scaffold.py."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from ferramentas.gerador_scaffold import (
    Scaffold,
    gerar_scaffold,
    normalizar_nome,
)


class TestNormalizarNome:
    def test_minusculas(self):
        assert normalizar_nome("MeuProjeto") == "meuprojeto"

    def test_espacos_para_hifen(self):
        assert normalizar_nome("Meu Projeto") == "meu-projeto"

    def test_underscores_para_hifen(self):
        assert normalizar_nome("meu_projeto") == "meu-projeto"

    def test_trunca_em_50_chars(self):
        longo = "a" * 100
        resultado = normalizar_nome(longo)
        assert len(resultado) <= 50


class TestGerarScaffold:
    def test_cria_scaffold_basico(self):
        with TemporaryDirectory() as tmpdir:
            blueprint = {
                "nome": "Meu App",
                "objetivo_transformacao": "App de tarefas",
                "resumo": "Um app simples",
                "motor_elaboracao": "AI-ENGINEERING-OS v1",
            }
            resultado = gerar_scaffold(blueprint, Path(tmpdir))

            assert resultado.status == "criado"
            assert resultado.nome_projeto == "meu-app"
            assert resultado.diretorio_raiz.exists()
            assert len(resultado.arquivos_criados) > 0

    def test_cria_estrutura_frontend(self):
        with TemporaryDirectory() as tmpdir:
            blueprint = {"nome": "Test"}
            resultado = gerar_scaffold(blueprint, Path(tmpdir))

            raiz = resultado.diretorio_raiz
            assert (raiz / "frontend" / "index.html").exists()
            assert (raiz / "frontend" / "src" / "main.jsx").exists()
            assert (raiz / "frontend" / "src" / "App.jsx").exists()
            assert (raiz / "frontend" / "src" / "index.css").exists()

    def test_cria_estrutura_backend(self):
        with TemporaryDirectory() as tmpdir:
            blueprint = {"nome": "Test"}
            resultado = gerar_scaffold(blueprint, Path(tmpdir))

            raiz = resultado.diretorio_raiz
            assert (raiz / "backend" / "src" / "index.js").exists()
            assert (raiz / "backend" / ".env.example").exists()

    def test_cria_readme_com_blueprint_data(self):
        with TemporaryDirectory() as tmpdir:
            blueprint = {
                "nome": "Teste Project",
                "resumo": "Um projeto de teste",
            }
            resultado = gerar_scaffold(blueprint, Path(tmpdir))

            readme = (resultado.diretorio_raiz / "README.md").read_text()
            assert "Teste Project" in readme
            assert "Um projeto de teste" in readme

    def test_package_json_frontend_valido(self):
        with TemporaryDirectory() as tmpdir:
            blueprint = {"nome": "Test"}
            resultado = gerar_scaffold(blueprint, Path(tmpdir))

            pkg = resultado.pacote_json_frontend
            assert pkg["name"] == "test-frontend"
            assert "react" in pkg["dependencies"]
            assert "scripts" in pkg
            assert "dev" in pkg["scripts"]

    def test_package_json_backend_valido(self):
        with TemporaryDirectory() as tmpdir:
            blueprint = {"nome": "Test"}
            resultado = gerar_scaffold(blueprint, Path(tmpdir))

            pkg = resultado.pacote_json_backend
            assert pkg["name"] == "test-backend"
            assert "express" in pkg["dependencies"]
            assert "scripts" in pkg
            assert "start" in pkg["scripts"]

    def test_arquivos_sao_reproduziveis(self):
        """Mesmo blueprint → mesmo scaffold (determinístico)."""
        with TemporaryDirectory() as tmpdir1:
            with TemporaryDirectory() as tmpdir2:
                blueprint = {
                    "nome": "Reproduzível",
                    "objetivo_transformacao": "Test",
                    "resumo": "Test",
                }

                r1 = gerar_scaffold(blueprint, Path(tmpdir1))
                r2 = gerar_scaffold(blueprint, Path(tmpdir2))

                # Compara conteúdo de arquivos-chave
                app1 = (r1.diretorio_raiz / "frontend" / "src" / "App.jsx").read_text()
                app2 = (r2.diretorio_raiz / "frontend" / "src" / "App.jsx").read_text()
                assert app1 == app2

    def test_gitignore_em_multiplos_niveis(self):
        with TemporaryDirectory() as tmpdir:
            blueprint = {"nome": "Test"}
            resultado = gerar_scaffold(blueprint, Path(tmpdir))

            raiz = resultado.diretorio_raiz
            assert (raiz / ".gitignore").exists()
            assert (raiz / "frontend" / ".gitignore").exists()
            assert (raiz / "backend" / ".gitignore").exists()

    def test_cria_readme_na_raiz(self):
        with TemporaryDirectory() as tmpdir:
            blueprint = {"nome": "Test"}
            resultado = gerar_scaffold(blueprint, Path(tmpdir))

            assert (resultado.diretorio_raiz / "README.md").exists()
