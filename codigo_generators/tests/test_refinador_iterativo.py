"""Testes para refinador iterativo."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import pytest

from codigo_generators.refinador_iterativo import (
    Refinacao,
    RefinadorIterativo,
    refinar_iterativo,
)


@pytest.fixture
def arquivo_teste():
    """Arquivo de teste temporário."""
    with TemporaryDirectory() as tmpdir:
        arquivo = Path(tmpdir) / "App.jsx"
        arquivo.write_text(
            "export default function App() { return <div>Hello</div> }"
        )
        yield arquivo


class TestRefinadorIterativo:
    def test_init_sem_api_key_falha(self):
        """Sem API key, deve falhar."""
        import os

        chave_original = os.getenv("ANTHROPIC_API_KEY")
        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]

        try:
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                RefinadorIterativo(api_key=None)
        finally:
            if chave_original:
                os.environ["ANTHROPIC_API_KEY"] = chave_original

    def test_init_com_api_key_direto(self):
        """Com api_key passada, funciona."""
        refinador = RefinadorIterativo(api_key="test-key")
        assert refinador.api_key == "test-key"

    def test_gerar_prompt_refinacao(self, arquivo_teste):
        """Prompt de refinação é gerado corretamente."""
        refinador = RefinadorIterativo(api_key="test-key")

        prompt = refinador._gerar_prompt_refinacao(
            arquivo_teste,
            "código original",
            "Adicione um título",
            {},
        )

        assert "App.jsx" in prompt
        assert "Adicione um título" in prompt
        assert "código original" in prompt

    @patch("codigo_generators.refinador_iterativo.Anthropic")
    def test_refinar_arquivo_sucesso(
        self, mock_anthropic_class, arquivo_teste
    ):
        """Refina arquivo com sucesso."""
        mock_resposta = MagicMock()
        mock_resposta.content = [
            MagicMock(
                text="export default function App() { return <div><h1>Hello</h1></div> }"
            )
        ]
        mock_resposta.usage.input_tokens = 100
        mock_resposta.usage.output_tokens = 50

        mock_cliente = MagicMock()
        mock_cliente.messages.create.return_value = mock_resposta
        mock_anthropic_class.return_value = mock_cliente

        refinador = RefinadorIterativo(api_key="test-key")
        refinador.cliente = mock_cliente

        resultado = refinador.refinar_arquivo(
            arquivo_teste,
            "Adicione um h1",
        )

        assert resultado.status == "sucesso"
        assert "h1" in resultado.conteudo_depois
        assert resultado.tokens_input == 100

    @patch("codigo_generators.refinador_iterativo.Anthropic")
    def test_refinar_arquivo_com_code_fence(
        self, mock_anthropic_class, arquivo_teste
    ):
        """Extrai código com code fence."""
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

        refinador = RefinadorIterativo(api_key="test-key")
        refinador.cliente = mock_cliente

        resultado = refinador.refinar_arquivo(
            arquivo_teste,
            "Mudança teste",
        )

        assert resultado.status == "sucesso"
        assert "```" not in resultado.conteudo_depois

    @patch("codigo_generators.refinador_iterativo.Anthropic")
    def test_refinar_arquivo_erro(
        self, mock_anthropic_class, arquivo_teste
    ):
        """Erro na API é capturado."""
        mock_cliente = MagicMock()
        mock_cliente.messages.create.side_effect = Exception("API Error")
        mock_anthropic_class.return_value = mock_cliente

        refinador = RefinadorIterativo(api_key="test-key")
        refinador.cliente = mock_cliente

        resultado = refinador.refinar_arquivo(
            arquivo_teste,
            "Mudança",
        )

        assert resultado.status == "erro"
        assert "API Error" in resultado.mensagem_erro

    @patch("codigo_generators.refinador_iterativo.Anthropic")
    def test_refinar_iterativo_function(
        self, mock_anthropic_class, arquivo_teste
    ):
        """Função de conveniência funciona."""
        mock_resposta = MagicMock()
        mock_resposta.content = [MagicMock(text="novo código")]
        mock_resposta.usage.input_tokens = 100
        mock_resposta.usage.output_tokens = 50

        mock_cliente = MagicMock()
        mock_cliente.messages.create.return_value = mock_resposta
        mock_anthropic_class.return_value = mock_cliente

        resultado = refinar_iterativo(
            arquivo_teste,
            "Mudança",
            api_key="test-key",
        )

        assert resultado.status == "sucesso"


class TestRefinacao:
    def test_dataclass_criacao(self):
        """Refinacao é criada corretamente."""
        refinacao = Refinacao(
            caminho_arquivo=Path("test.jsx"),
            descricao_mudanca="Adicione h1",
            conteudo_antes="antes",
            conteudo_depois="depois",
            tokens_input=100,
            tokens_output=50,
            status="sucesso",
        )

        assert refinacao.status == "sucesso"
        assert "h1" in refinacao.descricao_mudanca
