"""Estado do acervo: o que esta pronto, pendente ou reprovado.

Leitura pura - nunca escreve. `PENDENTE` e estado derivado (a pasta do volume
nao existe), nao um valor gravavel de `status`.

Uso: python -m ferramentas.status
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from .contrato import Contrato, ContratoInvalido, carregar
from .frontmatter import FrontMatterInvalido, ler_volume_yml
from .validar import volumes_existentes

PENDENTE = "PENDENTE"
_MEDIA = re.compile(r"^\s*media:\s*([0-9]+(?:[.,][0-9]+)?)\s*$", re.MULTILINE)
# Gramatica do nome do relatorio de auditoria. A revisao e opcional; ausente
# equivale a 1. Ver relatorio_mais_recente para o porque de nao usar sorted().
_NOME_RELATORIO = re.compile(r"^VOL-\d{2}-auditoria-(\d{4}-\d{2}-\d{2})(?:-r(\d+))?\.md$")


@dataclass(frozen=True, slots=True)
class EstadoVolume:
    vol_id: str
    nome: str
    tipo: str
    status: str
    secoes_presentes: int
    secoes_esperadas: int
    perecivel: bool
    nota_auditoria: float | None


def _ordem_do_relatorio(nome: str) -> tuple[str, int] | None:
    """Devolve (data ISO, revisao) do nome, ou None se o nome nao e valido."""
    casado = _NOME_RELATORIO.match(nome)
    if not casado:
        return None
    return casado.group(1), int(casado.group(2) or 1)


def relatorio_mais_recente(raiz: Path, vol_id: str) -> Path | None:
    """O relatorio de auditoria vigente do volume, ou None se nao houver.

    A escolha e por (data, revisao) extraidas do nome, nunca por ordem
    alfabetica: `-r2` tem hifen (0x2D), que ordena ANTES do ponto (0x2E) de
    `.md`, entao uma reauditoria no mesmo dia perderia para a auditoria antiga
    em silencio. E `-r10` perderia para `-r2` por comparacao de texto.

    Relatorio com nome fora da gramatica `VOL-NN-auditoria-AAAA-MM-DD[-rN].md`
    e ignorado de proposito - o nome e contrato, e nome invalido nao vira nota.
    """
    pasta = raiz / "auditorias"
    if not pasta.is_dir():
        return None
    candidatos = []
    for arq in pasta.glob(f"VOL-{vol_id}-auditoria-*.md"):
        ordem = _ordem_do_relatorio(arq.name)
        if ordem is not None:
            candidatos.append((ordem, arq))
    return max(candidatos)[1] if candidatos else None


def nota_da_ultima_auditoria(raiz: Path, vol_id: str) -> float | None:
    """Media da auditoria vigente do volume."""
    arq = relatorio_mais_recente(raiz, vol_id)
    if arq is None:
        return None
    casado = _MEDIA.search(arq.read_text(encoding="utf-8"))
    return float(casado.group(1).replace(",", ".")) if casado else None


def levantar(raiz: Path, ct: Contrato) -> list[EstadoVolume]:
    """Estado dos 42 volumes declarados no contrato."""
    materializados = set(volumes_existentes(raiz))
    estados: list[EstadoVolume] = []
    for vol_id in sorted(ct.volumes):
        meta = ct.volume(vol_id)
        esperadas = len(ct.secoes_de(meta["tipo"]))
        if vol_id not in materializados:
            estados.append(
                EstadoVolume(vol_id, meta["nome"], meta["tipo"], PENDENTE, 0, esperadas,
                             meta["perecivel"], None)
            )
            continue
        pasta = raiz / f"{vol_id}-{meta['nome']}"
        presentes = sum(1 for s in ct.secoes_de(meta["tipo"]) if (pasta / f"{s}.md").exists())
        status = PENDENTE
        yml = pasta / "_VOLUME.yml"
        if yml.exists():
            try:
                status = str(ler_volume_yml(yml).get("status", PENDENTE))
            except FrontMatterInvalido:
                status = "RASCUNHO"
        estados.append(
            EstadoVolume(vol_id, meta["nome"], meta["tipo"], status, presentes, esperadas,
                         meta["perecivel"], nota_da_ultima_auditoria(raiz, vol_id))
        )
    return estados


def tabela(estados: list[EstadoVolume]) -> str:
    """Tabela markdown do acervo, mais um resumo por status."""
    linhas = [
        "| Vol | Nome | Tipo | Status | Secoes | Auditoria | Perecivel |",
        "|---|---|---|---|---|---|---|",
    ]
    for e in estados:
        nota = f"{e.nota_auditoria:.1f}" if e.nota_auditoria is not None else "-"
        marca = "sim" if e.perecivel else "-"
        linhas.append(
            f"| {e.vol_id} | {e.nome} | {e.tipo} | {e.status} | "
            f"{e.secoes_presentes}/{e.secoes_esperadas} | {nota} | {marca} |"
        )
    contagem: dict[str, int] = {}
    for e in estados:
        contagem[e.status] = contagem.get(e.status, 0) + 1
    resumo = "  ".join(f"{k}={v}" for k, v in sorted(contagem.items()))
    return "\n".join(linhas) + f"\n\nResumo: {resumo}\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="status", description="Estado do acervo")
    parser.add_argument("--raiz", default=".")
    args = parser.parse_args(argv)
    raiz = Path(args.raiz).resolve()
    try:
        ct = carregar(raiz)
    except ContratoInvalido as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 2
    print(tabela(levantar(raiz, ct)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
