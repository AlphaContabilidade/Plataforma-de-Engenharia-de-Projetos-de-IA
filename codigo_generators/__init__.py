"""Geradores de código (adaptadores opcionais).

Camada de adaptadores que preenchem scaffold com código real usando LLMs.

Módulos:
  - llm_filler: Preenche scaffold vazio com código
  - refinador_iterativo: Select & Edit para refinar código
  - [futuro] local_generator: Preenche com modelos locais
  - [futuro] templates_expander: Expande templates (pós-fase 4)
"""

from codigo_generators.llm_filler import (
    ArquivoPreenchido,
    PreenchedorComLLM,
    ScaffoldPreenchido,
    preencher_com_claude,
)
from codigo_generators.refinador_iterativo import (
    Refinacao,
    RefinadorIterativo,
    refinar_iterativo,
)

__all__ = [
    "ArquivoPreenchido",
    "PreenchedorComLLM",
    "ScaffoldPreenchido",
    "preencher_com_claude",
    "Refinacao",
    "RefinadorIterativo",
    "refinar_iterativo",
]
