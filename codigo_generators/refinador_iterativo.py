"""Refinador iterativo — Select & Edit para código gerado.

Permite refinar código através de descrição em linguagem natural:
  1. Usuário seleciona arquivo ou seção
  2. Descreve mudança em português simples
  3. Sistema regenera aquela parte
  4. Repete até satisfeito

Similar ao "Select & Edit" do LOVABLE.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


@dataclass
class Refinacao:
    """Resultado de uma refinação."""

    caminho_arquivo: Path
    descricao_mudanca: str
    conteudo_antes: str
    conteudo_depois: str
    tokens_input: int
    tokens_output: int
    status: str  # "sucesso", "erro"
    mensagem_erro: Optional[str] = None


class RefinadorIterativo:
    """Refina código através de feedback em linguagem natural."""

    MODELO_PADRAO = "claude-3-5-sonnet-20241022"

    def __init__(
        self,
        api_key: Optional[str] = None,
        modelo: str = MODELO_PADRAO,
    ):
        """Inicializa refinador.

        Args:
            api_key: Chave Claude (padrão: env ANTHROPIC_API_KEY)
            modelo: Modelo Claude
        """
        if Anthropic is None:
            raise ImportError(
                "Instale 'anthropic': pip install anthropic"
            )

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY não configurada")

        self.cliente = Anthropic(api_key=self.api_key)
        self.modelo = modelo

    def refinar_arquivo(
        self,
        caminho_arquivo: Path,
        descricao_mudanca: str,
        contexto: Optional[dict] = None,
    ) -> Refinacao:
        """Refina um arquivo com base em feedback do usuário.

        Args:
            caminho_arquivo: Arquivo a refinar
            descricao_mudanca: O que o usuário quer mudar (linguagem natural)
            contexto: Contexto adicional (blueprint, etc)

        Returns:
            Refinacao com resultado
        """
        try:
            conteudo_antes = caminho_arquivo.read_text()

            # Gera prompt de refinação
            prompt = self._gerar_prompt_refinacao(
                caminho_arquivo,
                conteudo_antes,
                descricao_mudanca,
                contexto or {},
            )

            # Chama Claude
            resposta = self.cliente.messages.create(
                model=self.modelo,
                max_tokens=3000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            # Extrai código
            conteudo_depois = resposta.content[0].text

            # Remove code fence se presente
            if "```" in conteudo_depois:
                partes = conteudo_depois.split("```")
                if len(partes) >= 3:
                    conteudo_depois = partes[1]
                    # Remove language marker
                    if conteudo_depois.startswith(("jsx", "js", "python")):
                        conteudo_depois = conteudo_depois.split("\n", 1)[1]

            # Salva arquivo refinado
            caminho_arquivo.write_text(conteudo_depois)

            return Refinacao(
                caminho_arquivo=caminho_arquivo,
                descricao_mudanca=descricao_mudanca,
                conteudo_antes=conteudo_antes,
                conteudo_depois=conteudo_depois,
                tokens_input=resposta.usage.input_tokens,
                tokens_output=resposta.usage.output_tokens,
                status="sucesso",
            )

        except Exception as e:
            return Refinacao(
                caminho_arquivo=caminho_arquivo,
                descricao_mudanca=descricao_mudanca,
                conteudo_antes="",
                conteudo_depois="",
                tokens_input=0,
                tokens_output=0,
                status="erro",
                mensagem_erro=str(e),
            )

    def _gerar_prompt_refinacao(
        self,
        caminho_arquivo: Path,
        conteudo_atual: str,
        descricao_mudanca: str,
        contexto: dict,
    ) -> str:
        """Gera prompt para refinar arquivo."""
        nome_arquivo = caminho_arquivo.name
        tipo = "React" if ".jsx" in nome_arquivo else "Node.js"

        return f"""Você é um engenheiro {tipo} experiente refazendo código.

ARQUIVO: {nome_arquivo}
PEDIDO DO USUÁRIO: {descricao_mudanca}

CÓDIGO ATUAL:
```
{conteudo_atual}
```

Reescreva APENAS a parte relevante ao pedido. Mantenha o resto do código.
Se o pedido pedir para adicionar algo, integre naturalmente.
Se pedir para remover, remova e ajuste imports/dependências.

CÓDIGO REFINADO:
"""


def refinar_iterativo(
    caminho_arquivo: Path,
    descricao: str,
    api_key: Optional[str] = None,
) -> Refinacao:
    """Função de conveniência: refina um arquivo em um comando."""
    refinador = RefinadorIterativo(api_key=api_key)
    return refinador.refinar_arquivo(caminho_arquivo, descricao)
