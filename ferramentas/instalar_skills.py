"""Instala as cinco skills `aieos-*` num diretorio que o harness descobre.

Por que existe: as skills desta plataforma moram em
`AI-ENGINEERING-OS/.claude/skills/`, e esse caminho **nao foi descoberto** pelo
harness nesta sessao - os comandos `/aieos-*` nao aparecem na listagem. O
diretorio comprovadamente descoberto e o `.claude/skills/` da raiz do
repositorio, porque `varredura-seguranca` mora la e aparece. Este script copia os
`SKILL.md` de um lugar para o outro, sem apagar nada de terceiro.

Tres garantias, e as tres tem motivo:

1. **Idempotente.** Arquivo identico nao e reescrito. Reescrever mudaria mtime a
   cada execucao e faria toda passada parecer uma mudanca.
2. **Nunca sobrescreve skill de terceiro em silencio.** Skill com o mesmo nome de
   pasta mas de outra origem e conflito reportado, nao vitima. `--forcar` existe
   para o caso em que o humano decidiu; o default e recusar.
3. **Nao promete efeito imediato.** O harness descobre skills no inicio da
   sessao. Copiar arquivo agora nao faz `/aieos-status` aparecer agora.

Uso:
    python -m ferramentas.instalar_skills --dry-run
    python -m ferramentas.instalar_skills
    python -m ferramentas.instalar_skills --destino <caminho> [--forcar]

Codigos de saida: 0 tudo resolvido, 1 conflito nao resolvido, 2 erro de uso.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from .frontmatter import FrontMatterInvalido, extrair_bloco, parse_bloco

ARQUIVO_SKILL = "SKILL.md"
PREFIXO = "aieos-"
SUBDIR_SKILLS = Path(".claude") / "skills"

CRIAR = "criar"
ATUALIZAR = "atualizar"
IDENTICO = "identico"
CONFLITO = "conflito"


@dataclass(frozen=True, slots=True)
class Acao:
    """O que fazer com uma skill, e por que."""

    nome: str
    origem: Path
    destino: Path
    situacao: str
    motivo: str


def raiz_da_plataforma() -> Path:
    """A pasta `AI-ENGINEERING-OS/`, deduzida da localizacao deste modulo."""
    return Path(__file__).resolve().parents[1]


def raiz_do_repo(inicio: Path | None = None) -> Path:
    """Sobe procurando `.git`; sem repo, devolve o pai da plataforma.

    O alvo nao e "o diretorio acima" por coincidencia: e a raiz do repositorio,
    que e onde vive o `.claude/skills/` que o harness comprovadamente le.
    """
    atual = (inicio or raiz_da_plataforma()).resolve()
    for candidato in (atual, *atual.parents):
        if (candidato / ".git").exists():
            return candidato
    return raiz_da_plataforma().parent


def destino_padrao() -> Path:
    return raiz_do_repo() / SUBDIR_SKILLS


def origem_padrao() -> Path:
    return raiz_da_plataforma() / SUBDIR_SKILLS


def skills_de_origem(origem: Path) -> tuple[Path, ...]:
    """Os `aieos-*/SKILL.md` da origem, em ordem de nome.

    Pasta `aieos-*` sem `SKILL.md` e ignorada: nao ha o que instalar, e criar um
    arquivo vazio no destino seria registrar uma skill que nao existe.
    """
    if not origem.is_dir():
        return ()
    return tuple(sorted(origem.glob(f"{PREFIXO}*/{ARQUIVO_SKILL}")))


def nome_declarado(caminho: Path) -> str | None:
    """O campo `name` do front-matter, ou None se nao houver front-matter legivel."""
    try:
        bloco, _ = extrair_bloco(caminho.read_text(encoding="utf-8"))
        valor = parse_bloco(bloco).get("name")
    except (FrontMatterInvalido, OSError, UnicodeDecodeError):
        return None
    return str(valor) if valor else None


def _e_nossa(caminho: Path) -> bool:
    """Um `SKILL.md` do destino e nosso se declara `name: aieos-...`.

    A procedencia sai do conteudo, nao do nome da pasta. Pasta e apenas um
    caminho; o campo `name` e o que o harness usa como identidade da skill, e e
    ele que distingue uma versao antiga da nossa de uma skill alheia que por
    acaso ocupa o mesmo caminho.
    """
    nome = nome_declarado(caminho)
    return bool(nome and nome.startswith(PREFIXO))


def planejar(origem: Path, destino: Path) -> tuple[Acao, ...]:
    """Decide, sem escrever nada, o que fazer com cada skill da origem."""
    acoes: list[Acao] = []
    for arq in skills_de_origem(origem):
        nome = arq.parent.name
        alvo = destino / nome / ARQUIVO_SKILL
        if not alvo.exists():
            acoes.append(Acao(nome, arq, alvo, CRIAR, "nao existe no destino"))
            continue
        try:
            atual = alvo.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as erro:
            acoes.append(
                Acao(nome, arq, alvo, CONFLITO, f"destino ilegivel, nao vou sobrescrever: {erro}")
            )
            continue
        if atual == arq.read_text(encoding="utf-8"):
            acoes.append(Acao(nome, arq, alvo, IDENTICO, "destino ja identico a origem"))
        elif _e_nossa(alvo):
            acoes.append(Acao(nome, arq, alvo, ATUALIZAR, "versao antiga da mesma skill aieos-*"))
        else:
            declarado = nome_declarado(alvo) or "sem campo name legivel"
            acoes.append(
                Acao(
                    nome,
                    arq,
                    alvo,
                    CONFLITO,
                    f"destino e de outra origem (name={declarado!r}); use --forcar "
                    "se a intencao e substituir",
                )
            )
    return tuple(acoes)


def aplicar(acoes: tuple[Acao, ...], *, forcar: bool = False) -> tuple[Acao, ...]:
    """Escreve o que deve ser escrito. Devolve so as acoes efetivadas.

    `identico` nunca escreve. `conflito` so escreve com `forcar`, e nesse caso o
    humano ja foi avisado do que esta perdendo.
    """
    feitas: list[Acao] = []
    for a in acoes:
        if a.situacao == IDENTICO:
            continue
        if a.situacao == CONFLITO and not forcar:
            continue
        a.destino.parent.mkdir(parents=True, exist_ok=True)
        a.destino.write_text(a.origem.read_text(encoding="utf-8"), encoding="utf-8", newline="")
        feitas.append(a)
    return tuple(feitas)


def relatorio(acoes: tuple[Acao, ...], feitas: tuple[Acao, ...], *, dry_run: bool) -> str:
    """Relatorio linha a linha, dizendo o que foi feito e o que foi recusado."""
    aplicadas = {a.nome for a in feitas}
    linhas: list[str] = []
    for a in acoes:
        if dry_run:
            verbo = {CRIAR: "criaria", ATUALIZAR: "atualizaria", IDENTICO: "pularia",
                     CONFLITO: "abortaria"}[a.situacao]
        elif a.nome in aplicadas:
            verbo = {CRIAR: "criado", ATUALIZAR: "atualizado", CONFLITO: "sobrescrito"}[a.situacao]
        else:
            verbo = "pulado" if a.situacao == IDENTICO else "ABORTADO"
        linhas.append(f"  [{verbo}] {a.nome}: {a.motivo}")
    contagem: dict[str, int] = {}
    for a in acoes:
        contagem[a.situacao] = contagem.get(a.situacao, 0) + 1
    resumo = "  ".join(f"{k}={v}" for k, v in sorted(contagem.items())) or "nada a fazer"
    linhas.append("")
    linhas.append(f"Resumo: {resumo}")
    return "\n".join(linhas)


AVISO_SESSAO = """\
O harness descobre skills NO INICIO DA SESSAO. Copiar arquivo agora nao registra
skill na sessao atual: abra uma sessao nova para os comandos /aieos-novo-volume,
/aieos-auditar, /aieos-status, /aieos-cross-reference e /aieos-exportar
aparecerem na listagem."""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="instalar_skills",
        description="Copia as skills aieos-* para um diretorio que o harness descobre",
    )
    parser.add_argument(
        "--destino",
        default=None,
        help=f"diretorio de skills de destino (default: {destino_padrao()})",
    )
    parser.add_argument(
        "--origem", default=None, help=f"diretorio de origem (default: {origem_padrao()})"
    )
    parser.add_argument("--dry-run", action="store_true", help="so lista o que faria")
    parser.add_argument(
        "--forcar", action="store_true", help="sobrescreve destino de outra origem"
    )
    args = parser.parse_args(argv)

    origem = Path(args.origem).resolve() if args.origem else origem_padrao()
    destino = Path(args.destino).resolve() if args.destino else destino_padrao()

    if not origem.is_dir():
        print(f"erro: origem nao existe: {origem}", file=sys.stderr)
        return 2

    acoes = planejar(origem, destino)
    print(f"origem:  {origem}")
    print(f"destino: {destino}")
    try:
        destino.relative_to(raiz_da_plataforma())
    except ValueError:
        # Nao e erro - o destino descoberto pelo harness fica fora da plataforma
        # de proposito. Mas escrever fora desta pasta e decisao do humano, e ele
        # precisa ver isso escrito antes de acontecer.
        print(
            "aviso: o destino esta FORA de AI-ENGINEERING-OS/. Confira o caminho "
            "antes de rodar sem --dry-run."
        )
    print()

    if not acoes:
        print(f"nenhuma skill {PREFIXO}*/{ARQUIVO_SKILL} encontrada em {origem}")
        return 0

    feitas = () if args.dry_run else aplicar(acoes, forcar=args.forcar)
    print(relatorio(acoes, feitas, dry_run=args.dry_run))
    print()

    conflitos = [a for a in acoes if a.situacao == CONFLITO]
    if conflitos and not args.forcar:
        print(
            f"FALHA: {len(conflitos)} conflito(s) nao resolvido(s). Nada foi "
            "sobrescrito. Renomeie a skill alheia, aponte --destino para outro "
            "lugar, ou use --forcar se a intencao e substituir."
        )
        return 1
    if args.dry_run:
        print("dry-run: nada foi escrito em disco.")
    print()
    print(AVISO_SESSAO)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
