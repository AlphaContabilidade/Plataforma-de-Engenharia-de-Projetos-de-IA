"""Geradores de código — tudo aqui, sem API externa.

Módulos:
  - scaffold_preencher: Gera React/Node.js funcionais (nativo)
  - integrador: Cria scaffold + preenche tudo de uma vez
  - [antigo] llm_filler, refinador_iterativo: Removidos (usavam API)
"""

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
from codigo_generators.integrador import (
    ProjetoGerado,
    gerar_projeto_completo,
    exibir_resultado,
)

__all__ = [
    "gerar_app_jsx",
    "gerar_app_css",
    "gerar_index_js",
    "gerar_env_example",
    "gerar_package_json_frontend",
    "gerar_package_json_backend",
    "gerar_readme",
    "listar_arquivos_para_preencher",
    "ProjetoGerado",
    "gerar_projeto_completo",
    "exibir_resultado",
]
