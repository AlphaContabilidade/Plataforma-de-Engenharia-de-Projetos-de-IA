"""Os gates de qualidade da plataforma.

Uso:
    python -m ferramentas.validar 07          # um volume
    python -m ferramentas.validar --tudo      # todos os volumes materializados
    python -m ferramentas.validar --cross-refs

Codigos de saida: 0 sem violacao, 1 com violacao, 2 em erro de uso ou contrato.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from . import regras as R
from .contrato import Contrato, ContratoInvalido, carregar
from .frontmatter import FrontMatterInvalido, ler_volume_yml
from .modelo import Violacao

# Volume vai de 01 a 99. O prefixo 00 e reservado a `00-INTRODUCAO`, que guarda o
# contrato e nao e um volume - sem excluir o 00 aqui, todo levantamento tentaria
# resolver `ct.volume("00")` e explodiria com ContratoInvalido.
PASTA_VOLUME = re.compile(r"^(0[1-9]|[1-9][0-9])-[A-Z0-9-]+$")


def volumes_existentes(raiz: Path) -> list[str]:
    """Ids dos volumes que ja foram materializados como pasta."""
    achados = []
    for item in raiz.iterdir():
        if item.is_dir():
            casado = PASTA_VOLUME.match(item.name)
            if casado:
                achados.append(casado.group(1))
    return sorted(achados)


def _pasta_de(raiz: Path, vol_id: str, ct: Contrato) -> Path:
    return raiz / f"{vol_id}-{ct.volume(vol_id)['nome']}"


def validar_volume(raiz: Path, vol_id: str, ct: Contrato) -> list[Violacao]:
    """Aplica todas as regras de um volume. Nao levanta por conteudo ruim."""
    meta = ct.volume(vol_id)
    pasta = _pasta_de(raiz, vol_id, ct)
    rel_pasta = pasta.name
    yml = pasta / "_VOLUME.yml"
    if not yml.exists():
        return [Violacao(f"{rel_pasta}/_VOLUME.yml", 0, "volume-yml", "_VOLUME.yml ausente")]
    try:
        vol = ler_volume_yml(yml)
    except FrontMatterInvalido as erro:
        return [Violacao(f"{rel_pasta}/_VOLUME.yml", 0, "volume-yml", str(erro))]

    faltando = [c for c in ("volume", "nome", "tipo", "status") if c not in vol]
    if faltando:
        return [
            Violacao(
                f"{rel_pasta}/_VOLUME.yml", 0, "volume-yml",
                f"campos ausentes: {', '.join(faltando)}",
            )
        ]
    if vol["tipo"] not in ct.tipos:
        aceitos = ", ".join(sorted(ct.tipos))
        return [
            Violacao(
                f"{rel_pasta}/_VOLUME.yml", 0, "volume-tipo",
                f"tipo {vol['tipo']!r} invalido; aceitos: {aceitos}",
            )
        ]
    if vol["tipo"] != meta["tipo"]:
        return [
            Violacao(
                f"{rel_pasta}/_VOLUME.yml", 0, "volume-tipo",
                f"tipo {vol['tipo']!r} divergente do contrato ({meta['tipo']!r})",
            )
        ]

    saida: list[Violacao] = []
    texto_do_volume: list[str] = []
    for secao in ct.secoes_de(vol["tipo"]):
        arq = pasta / f"{secao}.md"
        rel = f"{rel_pasta}/{secao}.md"
        if not arq.exists():
            saida.append(Violacao(rel, 0, "secao-ausente", f"secao obrigatoria ausente: {secao}"))
            continue
        texto_do_volume.append(arq.read_text(encoding="utf-8"))
        linhas, inicio = R.corpo_de(arq)
        saida.extend(R.checar_frontmatter(rel, arq, secao, vol, ct))
        saida.extend(R.checar_substancia(rel, linhas, inicio, secao, ct))
        saida.extend(R.sem_marcadores(rel, linhas, inicio, ct))
        saida.extend(R.checar_mermaid(rel, linhas, inicio))
        saida.extend(R.checar_exemplos(raiz, rel, linhas, inicio))
        saida.extend(R.checar_links(raiz, arq, rel, linhas, inicio))
    saida.extend(
        R.checar_diagramas_obrigatorios(rel_pasta, "\n".join(texto_do_volume), vol["tipo"], ct)
    )
    return saida


def validar_tudo(raiz: Path, ct: Contrato) -> list[Violacao]:
    """Valida apenas volumes materializados. Volume pendente nao e violacao."""
    saida: list[Violacao] = []
    for vol_id in volumes_existentes(raiz):
        saida.extend(validar_volume(raiz, vol_id, ct))
    return saida


def validar_cross_refs(raiz: Path, ct: Contrato) -> list[Violacao]:
    """`depende_de` aponta para volume declarado e o grafo e aciclico.

    `depende_de` e pre-requisito de leitura, nao 'assunto vizinho' - a relacao
    bidirecional vive em 18-Referencias-Cruzadas.md e nao entra neste grafo.
    """
    saida: list[Violacao] = []
    grafo: dict[str, list[str]] = {}
    for vol_id in volumes_existentes(raiz):
        pasta = _pasta_de(raiz, vol_id, ct)
        yml = pasta / "_VOLUME.yml"
        rel = f"{pasta.name}/_VOLUME.yml"
        if not yml.exists():
            continue
        try:
            vol = ler_volume_yml(yml)
        except FrontMatterInvalido:
            continue
        deps = vol.get("depende_de", []) or []
        if isinstance(deps, str):
            deps = [deps]
        validas = []
        for dep in deps:
            if dep not in ct.volumes:
                saida.append(
                    Violacao(rel, 0, "depende-de-inexistente", f"volume {dep!r} nao existe")
                )
            else:
                validas.append(dep)
        grafo[vol_id] = validas

    VISITANDO, PRONTO = 1, 2
    estado: dict[str, int] = {}

    def desce(no: str, caminho: list[str]) -> None:
        estado[no] = VISITANDO
        for viz in grafo.get(no, ()):
            if estado.get(viz) == VISITANDO:
                ciclo = " -> ".join([*caminho, no, viz])
                saida.append(
                    Violacao(
                        f"{no}/_VOLUME.yml", 0, "depende-de-ciclo",
                        f"ciclo em depende_de: {ciclo}",
                    )
                )
            elif viz not in estado:
                desce(viz, [*caminho, no])
        estado[no] = PRONTO

    for no in sorted(grafo):
        if no not in estado:
            desce(no, [])
    return saida


def _reportar(violacoes: list[Violacao], rotulo: str) -> int:
    if not violacoes:
        print(f"ok: {rotulo} sem violacoes")
        return 0
    for v in violacoes:
        print(v)
    print(f"\nFALHA: {len(violacoes)} violacao(oes) em {rotulo}")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="validar", description="Gates da AI-ENGINEERING-OS")
    parser.add_argument("volume", nargs="?", help="id de 2 digitos, ex.: 07")
    parser.add_argument("--tudo", action="store_true", help="valida todos os volumes existentes")
    parser.add_argument("--cross-refs", action="store_true", help="checa dependencias e ciclos")
    parser.add_argument("--raiz", default=".", help="raiz da plataforma (default: .)")
    args = parser.parse_args(argv)

    raiz = Path(args.raiz).resolve()
    try:
        ct = carregar(raiz)
    except ContratoInvalido as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 2

    try:
        if args.cross_refs:
            return _reportar(validar_cross_refs(raiz, ct), "referencias cruzadas")
        if args.tudo:
            return _reportar(validar_tudo(raiz, ct), "acervo")
        if not args.volume:
            parser.print_usage(sys.stderr)
            return 2
        return _reportar(validar_volume(raiz, args.volume, ct), f"volume {args.volume}")
    except ContratoInvalido as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
