"""Testes para LLM Filler."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import pytest

from codigo_generators.llm_filler import (
    ArquivoPreenchido,
    PreenchedorComLLM,
    ScaffoldPreenchido,
)


@pytest.fixture
def blueprint_teste():
    """Blueprint padrão para testes."""
    return {
        "nome": "App Teste",
        "objetivo_transformacao": "Testar preenchimento",
        "resumo": "Um app para testar",
        "mvp": ["Dashboard", "Autenticação básica"],
    }


@pytest.fixture
def scaffold_teste():
    """Cria um scaffold temporário para testes."""
    with TemporaryDirectory() as tmpdir:
        raiz = Path(tmpdir)

        # Estrutura
        (raiz / "frontend" / "src").mkdir(parents=True)
        (raiz / "backend" / "src").mkdir(parents=True)

        # Arquivos placeholder
        (raiz / "frontend" / "src" / "App.jsx").write_text(
            "export default function App() { return <div>TODO</div> }"
        )
        (raiz / "backend" / "src" / "index.js").write_text(
            "const express = require('express')\n// TODO: implement"
        )

        yield raiz


class TestPreenchedorComLLM:
    def test_init_sem_api_key_falha(self):
        """Sem chave API, deve falhar."""
        import os

        # Limpa variável de ambiente temporariamente
        chave_original = os.getenv("ANTHROPIC_API_KEY")
        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]

        try:
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                PreenchedorComLLM(api_key=None)
        finally:
            # Restaura
            if chave_original:
                os.environ["ANTHROPIC_API_KEY"] = chave_original

    def test_init_com_api_key_direto(self):
        """Com api_key passada, inicializa OK."""
        preenchedor = PreenchedorComLLM(api_key="test-key-123")
        assert preenchedor.api_key == "test-key-123"

    def test_descobrir_arquivos_vazios(self, scaffold_teste):
        """Descobre arquivos com placeholder."""
        preenchedor = PreenchedorComLLM(api_key="test-key")
        arquivos = preenchedor._descobrir_arquivos_vazios(scaffold_teste)

        # Deve encontrar App.jsx (tem TODO)
        assert any("App.jsx" in a for a in arquivos)

    def test_gerar_prompt_react(self):
        """Prompt para React é gerado corretamente."""
        preenchedor = PreenchedorComLLM(api_key="test-key")

        prompt = preenchedor._prompt_react(
            "App.jsx",
            "TestApp",
            "Um teste",
            "Resumo teste",
            ["Feature 1"],
        )

        assert "React" in prompt
        assert "TestApp" in prompt
        assert "className" in prompt  # Tailwind

    def test_gerar_prompt_nodejs(self):
        """Prompt para Node.js é gerado corretamente."""
        preenchedor = PreenchedorComLLM(api_key="test-key")

        prompt = preenchedor._prompt_nodejs(
            "index.js",
            "TestApp",
            "Um teste",
            "Resumo teste",
            ["Feature 1"],
        )

        assert "Express" in prompt
        assert "TestApp" in prompt
        assert "Node.js" in prompt

    @patch("codigo_generators.llm_filler.Anthropic")
    def test_preencher_arquivo_sucesso(self, mock_anthropic_class, scaffold_teste):
        """Preenche arquivo com sucesso ao chamar Claude."""
        # Mock da resposta Claude
        mock_resposta = MagicMock()
        mock_resposta.content = [MagicMock(text="export default function App() { return <div>Hello</div> }")]
        mock_resposta.usage.input_tokens = 100
        mock_resposta.usage.output_tokens = 50

        mock_cliente = MagicMock()
        mock_cliente.messages.create.return_value = mock_resposta
        mock_anthropic_class.return_value = mock_cliente

        preenchedor = PreenchedorComLLM(api_key="test-key")
        preenchedor.cliente = mock_cliente

        arquivo_jsx = scaffold_teste / "frontend" / "src" / "App.jsx"

        resultado = preenchedor._preencher_arquivo(arquivo_jsx, {})

        assert resultado.status == "sucesso"
        assert "Hello" in resultado.conteudo_gerado
        assert resultado.tokens_input == 100
        assert resultado.tokens_output == 50

    @patch("codigo_generators.llm_filler.Anthropic")
    def test_preencher_arquivo_com_code_fence(
        self, mock_anthropic_class, scaffold_teste
    ):
        """Extrai código de resposta com markdown code fence."""
        mock_resposta = MagicMock()
        mock_resposta.content = [
            MagicMock(
                text="```jsx\nexport default function App() { return <div>OK</div> }\n```"
            )
        ]
        mock_resposta.usage.input_tokens = 100
        mock_resposta.usage.output_tokens = 50

        mock_cliente = MagicMock()
        mock_cliente.messages.create.return_value = mock_resposta
        mock_anthropic_class.return_value = mock_cliente

        preenchedor = PreenchedorComLLM(api_key="test-key")
        preenchedor.cliente = mock_cliente

        arquivo_jsx = scaffold_teste / "frontend" / "src" / "App.jsx"

        resultado = preenchedor._preencher_arquivo(arquivo_jsx, {})

        assert resultado.status == "sucesso"
        assert "OK" in resultado.conteudo_gerado
        # Não deve conter as markers de code fence
        assert "```" not in resultado.conteudo_gerado

    @patch("codigo_generators.llm_filler.Anthropic")
    def test_preencher_arquivo_erro_api(self, mock_anthropic_class, scaffold_teste):
        """Erro na API é capturado e reportado."""
        mock_cliente = MagicMock()
        mock_cliente.messages.create.side_effect = Exception("API Error")
        mock_anthropic_class.return_value = mock_cliente

        preenchedor = PreenchedorComLLM(api_key="test-key")
        preenchedor.cliente = mock_cliente

        arquivo_jsx = scaffold_teste / "frontend" / "src" / "App.jsx"

        resultado = preenchedor._preencher_arquivo(arquivo_jsx, {})

        assert resultado.status == "erro_api"
        assert "API Error" in resultado.mensagem_erro

    @patch("codigo_generators.llm_filler.Anthropic")
    def test_preencher_scaffold_completo(
        self, mock_anthropic_class, scaffold_teste, blueprint_teste
    ):
        """Preenche scaffold inteiro."""
        mock_resposta = MagicMock()
        mock_resposta.content = [MagicMock(text="// código")]
        mock_resposta.usage.input_tokens = 100
        mock_resposta.usage.output_tokens = 50

        mock_cliente = MagicMock()
        mock_cliente.messages.create.return_value = mock_resposta
        mock_anthropic_class.return_value = mock_cliente

        preenchedor = PreenchedorComLLM(api_key="test-key")
        preenchedor.cliente = mock_cliente

        resultado = preenchedor.preencher_scaffold(scaffold_teste, blueprint_teste)

        assert resultado.status in ("completo", "parcial")
        assert len(resultado.arquivos_preenchidos) > 0

    def test_preencher_scaffold_nao_existe(self, blueprint_teste):
        """Scaffold inexistente retorna erro."""
        preenchedor = PreenchedorComLLM(api_key="test-key")

        resultado = preenchedor.preencher_scaffold(
            Path("/nao/existe"), blueprint_teste
        )

        assert resultado.status == "erro"
        assert len(resultado.arquivos_preenchidos) == 0


class TestArquivoPreenchido:
    def test_dataclass_criacao(self):
        """ArquivoPreenchido é criado corretamente."""
        arquivo = ArquivoPreenchido(
            caminho=Path("test.jsx"),
            conteudo_original="original",
            conteudo_gerado="gerado",
            prompt_usado="prompt",
            tokens_input=100,
            tokens_output=50,
            modelo="claude-test",
            status="sucesso",
        )

        assert arquivo.status == "sucesso"
        assert arquivo.tokens_input == 100


class TestScaffoldPreenchido:
    def test_dataclass_criacao(self):
        """ScaffoldPreenchido é criado corretamente."""
        scaffold = ScaffoldPreenchido(
            diretorio_raiz=Path("/test"),
            arquivos_preenchidos=[],
            status="completo",
            resumo="Teste",
        )

        assert scaffold.status == "completo"
