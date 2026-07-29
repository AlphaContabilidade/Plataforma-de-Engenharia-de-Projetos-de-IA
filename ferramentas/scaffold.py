"""Materializa em disco os volumes declarados no contrato.

Idempotente por construcao: a ferramenta so escreve `_VOLUME.yml` que ainda nao
existe. Nunca reescreve um que exista - o `_VOLUME.yml` acumula estado editado a
mao (`status`, `depende_de`, `escopo`), e sobrescrever apagaria trabalho humano.
Por isso o retorno lista apenas o que foi criado nesta passada.

Uso: python -m ferramentas.scaffold [--raiz .]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .contrato import Contrato, ContratoInvalido, carregar

ARQUIVO_VOLUME = "_VOLUME.yml"
STATUS_INICIAL = "RASCUNHO"


def pasta_de(raiz: Path, vol_id: str, ct: Contrato) -> Path:
    """Pasta canonica do volume: `NN-NOME`."""
    return raiz / f"{vol_id}-{ct.volume(vol_id)['nome']}"


def corpo_do_yml(vol_id: str, meta: dict) -> str:
    """Conteudo do `_VOLUME.yml` inicial.

    Gramatica identica a que `frontmatter.ler_volume_yml` aceita, e com os
    quatro campos que `validar.validar_volume` exige (`volume`, `nome`, `tipo`,
    `status`). `volume` sai entre aspas porque e string de 2 digitos.
    """
    escopo = str(meta.get("escopo", "") or "").strip()
    # Escopo ausente vira `escopo:` sem valor (le como string vazia). Nao
    # inventamos uma frase de escopo aqui: quem escreve o volume e que decide.
    linha_escopo = f"escopo: {escopo}" if escopo else "escopo:"
    return (
        f'volume: "{vol_id}"\n'
        f"nome: {meta['nome']}\n"
        f"tipo: {meta['tipo']}\n"
        f"status: {STATUS_INICIAL}\n"
        f"perecivel: {'true' if meta.get('perecivel') else 'false'}\n"
        f"depende_de: []\n"
        f"{linha_escopo}\n"
    )


def criar_volumes(raiz: Path, ct: Contrato) -> list[str]:
    """Cria `NN-NOME/_VOLUME.yml` para todo volume que ainda nao o tem.

    Devolve os ids criados, em ordem. Pasta que existe sem `_VOLUME.yml` conta
    como lacuna e e completada; pasta com yml e deixada intacta.
    """
    criados: list[str] = []
    for vol_id in sorted(ct.volumes):
        meta = ct.volume(vol_id)
        pasta = pasta_de(raiz, vol_id, ct)
        yml = pasta / ARQUIVO_VOLUME
        if yml.exists():
            continue
        pasta.mkdir(parents=True, exist_ok=True)
        yml.write_text(corpo_do_yml(vol_id, meta), encoding="utf-8")
        criados.append(vol_id)
    return criados


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scaffold", description="Cria as pastas de volume do contrato (idempotente)"
    )
    parser.add_argument("--raiz", default=".", help="raiz da plataforma (default: .)")
    args = parser.parse_args(argv)

    raiz = Path(args.raiz).resolve()
    try:
        ct = carregar(raiz)
    except ContratoInvalido as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 2

    criados = criar_volumes(raiz, ct)
    if not criados:
        print("nada a criar: todos os volumes do contrato ja estao materializados")
        return 0
    print(f"criados {len(criados)} volume(s): {', '.join(criados)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
