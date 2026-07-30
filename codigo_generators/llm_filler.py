"""Preenchedor de scaffold usando Claude (LLM Filler).

Transforma scaffold vazio em código funcional, arquivo por arquivo.
Usa prompts compilados (volume 28) e chamadas à Claude API.

Fluxo:
  1. Recebe scaffold criado + Blueprint
  2. Para cada arquivo, gera um prompt contextualizado
  3. Chama Claude para gerar código
  4. Substitui conteúdo vazio → código gerado
  5. Retorna scaffold preenchido
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


@dataclass
class ArquivoPreenchido:
    """Resultado do preenchimento de um arquivo."""

    caminho: Path
    conteudo_original: str
    conteudo_gerado: str
    prompt_usado: str
    tokens_input: int
    tokens_output: int
    modelo: str
    status: str  # "sucesso", "erro_api", "erro_parsing"
    mensagem_erro: Optional[str] = None


@dataclass
class ScaffoldPreenchido:
    """Scaffold após preenchimento com código."""

    diretorio_raiz: Path
    arquivos_preenchidos: list[ArquivoPreenchido]
    status: str  # "completo", "parcial", "erro"
    resumo: str


class PreenchedorComLLM:
    """Preenche scaffold com código usando Claude."""

    MODELO_PADRAO = "claude-3-5-sonnet-20241022"

    def __init__(
        self,
        api_key: Optional[str] = None,
        modelo: str = MODELO_PADRAO,
    ):
        """Inicializa preenchedor.

        Args:
            api_key: Chave da API Claude (padrão: env ANTHROPIC_API_KEY)
            modelo: Modelo Claude a usar
        """
        if Anthropic is None:
            raise ImportError(
                "Instale 'anthropic' para usar o LLM Filler: "
                "pip install anthropic"
            )

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY não configurada. "
                "Set env var ou passe api_key="
            )

        self.cliente = Anthropic(api_key=self.api_key)
        self.modelo = modelo

    def preencher_scaffold(
        self,
        diretorio_scaffold: Path,
        blueprint: dict[str, Any],
        arquivos_alvo: Optional[list[str]] = None,
    ) -> ScaffoldPreenchido:
        """Preenche scaffold com código gerado.

        Args:
            diretorio_scaffold: Raiz do scaffold (criado por gerador_scaffold)
            blueprint: Plano de Solução (dict)
            arquivos_alvo: Lista de caminhos relativos para preencher.
                          Padrão: todos os .jsx e .js não-preenchidos

        Returns:
            ScaffoldPreenchido com lista de arquivos preenchidos
        """
        if not diretorio_scaffold.exists():
            return ScaffoldPreenchido(
                diretorio_raiz=diretorio_scaffold,
                arquivos_preenchidos=[],
                status="erro",
                resumo="Diretório não existe",
            )

        # Se não especificou arquivos, descobre automaticamente
        if arquivos_alvo is None:
            arquivos_alvo = self._descobrir_arquivos_vazios(diretorio_scaffold)

        preenchidos = []
        for caminho_relativo in arquivos_alvo:
            caminho_completo = diretorio_scaffold / caminho_relativo

            if not caminho_completo.exists():
                continue

            arquivo = self._preencher_arquivo(
                caminho_completo,
                blueprint,
            )
            preenchidos.append(arquivo)

        status = "completo" if len(preenchidos) == len(arquivos_alvo) else "parcial"
        resumo = f"{len(preenchidos)} arquivo(s) preenchido(s)"

        return ScaffoldPreenchido(
            diretorio_raiz=diretorio_scaffold,
            arquivos_preenchidos=preenchidos,
            status=status,
            resumo=resumo,
        )

    def _descobrir_arquivos_vazios(self, diretorio: Path) -> list[str]:
        """Encontra arquivos .jsx e .js que precisam preenchimento."""
        arquivos = []
        for arquivo in diretorio.rglob("*.jsx"):
            # Se é placeholder vazio, marca para preencher
            conteudo = arquivo.read_text()
            if "TODO" in conteudo or len(conteudo) < 200:
                arquivos.append(str(arquivo.relative_to(diretorio)))

        for arquivo in diretorio.rglob("*.js"):
            if "src/" in str(arquivo) or "backend/src" in str(arquivo):
                conteudo = arquivo.read_text()
                if "TODO" in conteudo or len(conteudo) < 300:
                    arquivos.append(str(arquivo.relative_to(diretorio)))

        return arquivos

    def _preencher_arquivo(
        self,
        caminho_arquivo: Path,
        blueprint: dict[str, Any],
    ) -> ArquivoPreenchido:
        """Preenche um arquivo individual."""
        try:
            conteudo_original = caminho_arquivo.read_text()

            # Identifica tipo de arquivo e gera prompt apropriado
            prompt = self._gerar_prompt(caminho_arquivo, blueprint, conteudo_original)

            # Chama Claude
            resposta = self.cliente.messages.create(
                model=self.modelo,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            # Extrai código da resposta
            conteudo_gerado = resposta.content[0].text

            # Se respondeu com markdown code fence, extrai
            if "```" in conteudo_gerado:
                partes = conteudo_gerado.split("```")
                if len(partes) >= 3:
                    conteudo_gerado = partes[1]
                    # Remove "jsx", "js", etc se estiver após os backticks
                    if conteudo_gerado.startswith(("jsx", "js", "python")):
                        conteudo_gerado = conteudo_gerado.split("\n", 1)[1]

            # Salva arquivo preenchido
            caminho_arquivo.write_text(conteudo_gerado)

            return ArquivoPreenchido(
                caminho=caminho_arquivo,
                conteudo_original=conteudo_original,
                conteudo_gerado=conteudo_gerado,
                prompt_usado=prompt,
                tokens_input=resposta.usage.input_tokens,
                tokens_output=resposta.usage.output_tokens,
                modelo=self.modelo,
                status="sucesso",
            )

        except Exception as e:
            return ArquivoPreenchido(
                caminho=caminho_arquivo,
                conteudo_original="",
                conteudo_gerado="",
                prompt_usado="",
                tokens_input=0,
                tokens_output=0,
                modelo=self.modelo,
                status="erro_api",
                mensagem_erro=str(e),
            )

    def _gerar_prompt(
        self,
        caminho_arquivo: Path,
        blueprint: dict[str, Any],
        conteudo_placeholder: str,
    ) -> str:
        """Gera prompt compilado para um arquivo (volume 28)."""

        nome_arquivo = caminho_arquivo.name
        tipo_arquivo = "React" if ".jsx" in nome_arquivo else "Node.js"

        # Contexto do Blueprint
        nome_projeto = blueprint.get("nome", "Projeto")
        objetivo = blueprint.get("objetivo_transformacao", "")
        resumo = blueprint.get("resumo", "")
        mvp = blueprint.get("mvp", [])

        if ".jsx" in nome_arquivo:
            return self._prompt_react(
                nome_arquivo, nome_projeto, objetivo, resumo, mvp
            )
        else:
            return self._prompt_nodejs(
                nome_arquivo, nome_projeto, objetivo, resumo, mvp
            )

    @staticmethod
    def _prompt_react(
        nome_arquivo: str,
        nome_projeto: str,
        objetivo: str,
        resumo: str,
        mvp: list,
    ) -> str:
        """Gera prompt para componentes React."""
        return f"""Você é um engenheiro frontend React experiente.

Projeto: {nome_projeto}
Objetivo: {objetivo}
Resumo: {resumo}
MVP: {', '.join(mvp) if mvp else 'Não especificado'}

Arquivo a implementar: {nome_arquivo}

Implemente este arquivo React seguindo estas regras:
1. Use React 18+ com hooks (useState, useEffect)
2. Estilo: Tailwind CSS inline (className)
3. Sem bibliotecas externas além de React
4. Componentes funcionais apenas
5. Prop drilling OK para MVP
6. Esporte um componente padrão

Código:
"""

    @staticmethod
    def _prompt_nodejs(
        nome_arquivo: str,
        nome_projeto: str,
        objetivo: str,
        resumo: str,
        mvp: list,
    ) -> str:
        """Gera prompt para código Node.js."""
        return f"""Você é um engenheiro backend Node.js experiente.

Projeto: {nome_projeto}
Objetivo: {objetivo}
Resumo: {resumo}
MVP: {', '.join(mvp) if mvp else 'Não especificado'}

Arquivo a implementar: {nome_arquivo}

Implemente este arquivo Node.js/Express seguindo estas regras:
1. Use Express.js
2. Sem ORMs (raw SQL ou simples arrays por enquanto)
3. Sem autenticação complexa no MVP
4. Rotas REST simples
5. Erros com status HTTP apropriado
6. Sem setup de banco até passar em testes

Código:
"""


def preencher_com_claude(
    diretorio_scaffold: Path,
    blueprint: dict[str, Any],
    api_key: Optional[str] = None,
) -> ScaffoldPreenchido:
    """Função de conveniência: preenche scaffold com um comando."""
    preenchedor = PreenchedorComLLM(api_key=api_key)
    return preenchedor.preencher_scaffold(diretorio_scaffold, blueprint)
