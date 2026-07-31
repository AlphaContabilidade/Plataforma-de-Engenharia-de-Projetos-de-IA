"""Refinador Iterativo via Chat — Select & Edit.

Usuário descreve mudança em português.
Claude Code regenera apenas aquela parte.
Sem HTTP, sem API.

Uso:
  resultado = refinar_arquivo_iterativo(
      Path("projeto/frontend/src/App.jsx"),
      "Adicione um botão de logout"
  )
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Refinacao:
    """Resultado de uma refinação via chat."""

    arquivo: Path
    descricao: str
    status: str  # "pendente_confirmacao", "confirmado", "erro"
    conteudo_antes: str
    conteudo_depois: Optional[str] = None
    notas: Optional[str] = None


def gerar_prompt_refinacao(
    arquivo: Path,
    conteudo_atual: str,
    descricao: str,
) -> str:
    """Gera prompt para refinar um arquivo via chat.

    Resultado é um prompt que Claude Code deve receber para gerar código novo.
    """
    nome = arquivo.name
    tipo = "React" if ".jsx" in nome else "Node.js/Express"

    return f"""Você precisa refatorar um arquivo {tipo}.

ARQUIVO: {nome}
MUDANCA SOLICITADA: {descricao}

CODIGO ATUAL:
```
{conteudo_atual}
```

INSTRUCOES:
1. Mantenha estrutura existente
2. So mude o que foi pedido
3. Se pedir para adicionar, integre naturalmente
4. Se pedir para remover, ajuste imports
5. Retorne APENAS o codigo novo, sem explicacoes

CODIGO REFATORADO:
```"""


def criar_plano_refinacao(
    projeto_dir: Path,
    mudancas: list[str],
) -> list[Refinacao]:
    """Lista de arquivos que podem ser refinados com as mudancas.

    mudancas: lista de descricoes como ["Adicione validacao", "Use TypeScript"]

    Retorna plano de refinacoes a fazer.
    """
    refinacoes = []

    # Descobre arquivos refinaveis
    app_jsx = projeto_dir / "frontend" / "src" / "App.jsx"
    index_js = projeto_dir / "backend" / "src" / "index.js"

    if app_jsx.exists():
        for mudanca in mudancas:
            if any(palavra in mudanca.lower() for palavra in ["ui", "frontend", "react", "botao", "componente", "estilo"]):
                refinacoes.append(
                    Refinacao(
                        arquivo=app_jsx,
                        descricao=mudanca,
                        status="pendente_confirmacao",
                        conteudo_antes=app_jsx.read_text(),
                    )
                )

    if index_js.exists():
        for mudanca in mudancas:
            if any(palavra in mudanca.lower() for palavra in ["api", "backend", "rota", "banco", "autenticacao", "validacao"]):
                refinacoes.append(
                    Refinacao(
                        arquivo=index_js,
                        descricao=mudanca,
                        status="pendente_confirmacao",
                        conteudo_antes=index_js.read_text(),
                    )
                )

    return refinacoes


def refinar_arquivo_iterativo(
    arquivo: Path,
    descricao: str,
) -> Refinacao:
    """Cria plano de refinacao.

    Retorna Refinacao com status "pendente_confirmacao".
    Usuario deve gerar o codigo novo via chat e confirmar.

    Uso no chat:
      resultado = refinar_arquivo_iterativo(Path(...), "Adicione autenticacao")
      print(resultado.prompt_para_gerar_codigo)
      # Claude Code gera codigo novo
      # Usuario copia e cola no chat
      # Sistema faz: resultado.confirmar(codigo_novo)
    """
    conteudo = arquivo.read_text()

    return Refinacao(
        arquivo=arquivo,
        descricao=descricao,
        status="pendente_confirmacao",
        conteudo_antes=conteudo,
        notas=gerar_prompt_refinacao(arquivo, conteudo, descricao),
    )


def confirmar_refinacao(refinacao: Refinacao, conteudo_novo: str) -> Refinacao:
    """Confirma e salva a refinacao."""
    refinacao.arquivo.write_text(conteudo_novo)
    refinacao.conteudo_depois = conteudo_novo
    refinacao.status = "confirmado"
    return refinacao
