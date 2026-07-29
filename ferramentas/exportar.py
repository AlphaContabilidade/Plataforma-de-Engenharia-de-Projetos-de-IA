"""Exporta o acervo para um site MkDocs.

A navegacao e derivada do disco, nao do contrato: volume declarado mas nao
materializado fica fora do site, porque publicar um item de menu sem pagina
seria prometer conteudo que nao existe.

O YAML e escrito a mao de proposito - as ferramentas usam so a biblioteca
padrao, e o arquivo gerado precisa carregar o tag `!!python/name:` que o
`pymdownx.superfences` exige para renderizar Mermaid.

Uso: python -m ferramentas.exportar [--raiz .]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from .contrato import Contrato, ContratoInvalido, carregar
from .validar import volumes_existentes

ARQUIVO = "mkdocs.yml"
INTRODUCAO = "00-INTRODUCAO"
SITE_NAME = "AI-ENGINEERING-OS"

_CABECALHO = f"""# Gerado por ferramentas/exportar.py - nao edite a mao.
site_name: {SITE_NAME}
theme:
  name: material
markdown_extensions:
  - admonition
  - attr_list
  - tables
  - toc:
      permalink: true
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
nav:
"""


def montar_nav(raiz: Path, ct: Contrato) -> list[dict]:
    """Navegacao MkDocs: `00-INTRODUCAO` primeiro, depois os volumes existentes.

    Cada item e `{titulo_da_pasta: [{titulo_da_pagina: caminho_relativo}, ...]}`.
    Secao declarada no contrato mas ausente em disco nao entra.
    """
    nav: list[dict] = []

    pasta_intro = raiz / INTRODUCAO
    if pasta_intro.is_dir():
        paginas = [
            {arq.stem: f"{INTRODUCAO}/{arq.name}"}
            for arq in sorted(pasta_intro.glob("*.md"))
        ]
        if paginas:
            nav.append({INTRODUCAO: paginas})

    for vol_id in volumes_existentes(raiz):
        meta = ct.volume(vol_id)
        nome_pasta = f"{vol_id}-{meta['nome']}"
        pasta = raiz / nome_pasta
        paginas = [
            {secao: f"{nome_pasta}/{secao}.md"}
            for secao in ct.secoes_de(meta["tipo"])
            if (pasta / f"{secao}.md").exists()
        ]
        if paginas:
            nav.append({nome_pasta: paginas})
    return nav


def _nav_yaml(nav: list[dict]) -> str:
    linhas: list[str] = []
    for item in nav:
        for titulo, paginas in item.items():
            linhas.append(f"  - {titulo}:")
            for pagina in paginas:
                for rotulo, caminho in pagina.items():
                    linhas.append(f"      - {rotulo}: {caminho}")
    return "\n".join(linhas) + "\n"


def gerar_mkdocs(raiz: Path, ct: Contrato) -> str:
    """Gera o YAML da configuracao e grava `raiz/mkdocs.yml`. Devolve o YAML."""
    yaml = _CABECALHO + _nav_yaml(montar_nav(raiz, ct))
    (raiz / ARQUIVO).write_text(yaml, encoding="utf-8")
    return yaml


def _construir(raiz: Path) -> int:
    """Roda `mkdocs build --strict` e devolve o codigo de saida do mkdocs.

    O build usa um config-file temporario FORA da raiz apontando `docs_dir` para
    a raiz absoluta. Motivo: o MkDocs recusa `docs_dir` igual a pasta do proprio
    config-file, e aqui o acervo E a pasta de conteudo. Sem esse desvio o build
    falharia por layout, nao por conteudo - e o gate perderia o sentido.
    """
    with tempfile.TemporaryDirectory() as tmp:
        cfg = Path(tmp) / ARQUIVO
        cfg.write_text(
            (raiz / ARQUIVO).read_text(encoding="utf-8")
            + f"docs_dir: {raiz.as_posix()}\n",
            encoding="utf-8",
        )
        return subprocess.run(
            ["mkdocs", "build", "--strict", "--config-file", str(cfg)],
            cwd=str(raiz),
        ).returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="exportar", description="Gera mkdocs.yml do acervo")
    parser.add_argument("--raiz", default=".", help="raiz da plataforma (default: .)")
    args = parser.parse_args(argv)

    raiz = Path(args.raiz).resolve()
    try:
        ct = carregar(raiz)
    except ContratoInvalido as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 2

    yaml = gerar_mkdocs(raiz, ct)
    paginas = yaml.count("      - ")
    print(f"ok: {raiz / ARQUIVO} gerado com {paginas} pagina(s)")

    if shutil.which("mkdocs") is None:
        print("aviso: mkdocs nao encontrado, build nao validado")
        return 0
    if _construir(raiz) != 0:
        print("FALHA: mkdocs build --strict reprovou", file=sys.stderr)
        return 1
    print("ok: mkdocs build --strict validado com sucesso")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
