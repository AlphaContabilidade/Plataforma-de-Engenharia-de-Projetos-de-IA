"""As regras de qualidade da plataforma, uma funcao pura por regra.

Cada funcao recebe o que precisa e devolve `list[Violacao]` - nunca imprime,
nunca levanta por conteudo ruim. Levantar e para erro de programa; conteudo
ruim e violacao reportada.
"""

from __future__ import annotations

import re
from pathlib import Path

from .contrato import Contrato
from .frontmatter import FrontMatterInvalido, extrair_bloco, parse_bloco
from .modelo import Violacao

REGRAS_ESTRUTURA = (
    "frontmatter",
    "frontmatter-campo",
    "frontmatter-status",
    "frontmatter-coerencia",
    "substancia-curta",
    "marcador-proibido",
)

_FENCE = re.compile(r"^\s*```")
_CODE_SPAN = re.compile(r"`[^`]*`")


def corpo_de(caminho: Path) -> tuple[list[str], int]:
    """Devolve (linhas do arquivo, linha 1-indexed onde o conteudo comeca).

    Se o front-matter esta ausente, `inicio` e 1: o arquivo todo e conteudo.
    """
    texto = caminho.read_text(encoding="utf-8")
    linhas = texto.splitlines()
    try:
        _, inicio = extrair_bloco(texto)
    except FrontMatterInvalido:
        inicio = 1
    return linhas, inicio


def _fora_de_codigo(linhas: list[str], inicio: int):
    """Itera (numero_da_linha, texto) apenas fora de blocos cercados."""
    dentro = False
    for n in range(inicio, len(linhas) + 1):
        linha = linhas[n - 1]
        if _FENCE.match(linha):
            dentro = not dentro
            continue
        if not dentro:
            yield n, linha


def palavras_de_prosa(linhas: list[str], inicio: int) -> int:
    """Conta palavras de prosa, ignorando blocos de codigo e cabecalhos."""
    total = 0
    for _, linha in _fora_de_codigo(linhas, inicio):
        limpa = linha.strip()
        if not limpa or limpa.startswith("#"):
            continue
        total += len(limpa.split())
    return total


def checar_frontmatter(
    rel: str, caminho: Path, secao: str, vol: dict, ct: Contrato
) -> list[Violacao]:
    """Front-matter presente, completo, com status valido e coerente com o volume."""
    texto = caminho.read_text(encoding="utf-8")
    try:
        bloco, _ = extrair_bloco(texto)
        campos = parse_bloco(bloco)
    except FrontMatterInvalido as erro:
        return [Violacao(rel, 1, "frontmatter", str(erro))]

    saida: list[Violacao] = []
    for campo in ct.campos_frontmatter:
        if campo not in campos or campos[campo] in ("", None):
            saida.append(
                Violacao(rel, 1, "frontmatter-campo", f"campo obrigatorio ausente: {campo}")
            )
    if campos.get("status") not in ct.status_validos and "status" in campos:
        aceitos = ", ".join(ct.status_validos)
        saida.append(
            Violacao(
                rel, 1, "frontmatter-status",
                f"status {campos['status']!r} invalido; aceitos: {aceitos}",
            )
        )
    esperado = {"volume": vol["volume"], "volume_nome": vol["nome"], "tipo": vol["tipo"]}
    for campo, valor in esperado.items():
        if campo in campos and campos[campo] != valor:
            saida.append(
                Violacao(
                    rel, 1, "frontmatter-coerencia",
                    f"{campo}={campos[campo]!r} divergente do _VOLUME.yml ({valor!r})",
                )
            )
    if campos.get("secao") != secao:
        saida.append(
            Violacao(
                rel, 1, "frontmatter-coerencia",
                f"secao={campos.get('secao')!r} nao corresponde ao arquivo ({secao!r})",
            )
        )
    return saida


def checar_substancia(
    rel: str, linhas: list[str], inicio: int, secao: str, ct: Contrato
) -> list[Violacao]:
    """Prosa suficiente para a secao. Codigo nao conta."""
    minimo = ct.minimo_de(secao)
    total = palavras_de_prosa(linhas, inicio)
    if total < minimo:
        return [
            Violacao(
                rel, inicio, "substancia-curta",
                f"{total} palavras de prosa; minimo para {secao} e {minimo}",
            )
        ]
    return []


def sem_marcadores(rel: str, linhas: list[str], inicio: int, ct: Contrato) -> list[Violacao]:
    """Nenhum marcador de trabalho inacabado fora de codigo.

    Mencionar o marcador em fonte de codigo (`TODO`) e permitido de proposito:
    o volume 10-Anti-Patterns precisa poder falar sobre ele.
    """
    saida: list[Violacao] = []
    for n, linha in _fora_de_codigo(linhas, inicio):
        limpa = _CODE_SPAN.sub("", linha)
        for marcador in ct.marcadores_proibidos:
            if marcador in limpa:
                saida.append(
                    Violacao(rel, n, "marcador-proibido", f"marcador {marcador!r} no conteudo")
                )
    return saida


TIPOS_MERMAID = frozenset(
    {
        "flowchart", "graph", "sequenceDiagram", "stateDiagram", "stateDiagram-v2",
        "erDiagram", "classDiagram", "journey", "gantt", "gitGraph", "mindmap",
        "timeline", "quadrantChart", "block-beta", "requirementDiagram",
        "C4Context", "C4Container", "C4Component", "C4Dynamic", "C4Deployment",
    }
)

_ABRE_MERMAID = re.compile(r"^\s*```mermaid\s*$")
_CITA_EXEMPLO = re.compile(r"<!--\s*exemplo:\s*([^\s>]+?)\s*-->")
_LINK = re.compile(r"\[[^\]]*\]\(\s*([^)\s#]+)(?:#[^)]*)?\s*\)")


def _blocos_mermaid(linhas: list[str], inicio: int) -> list[tuple[int, int | None, list[str]]]:
    """Devolve [(linha_da_abertura, linha_do_fechamento_ou_None, linhas_internas)]."""
    blocos: list[tuple[int, int | None, list[str]]] = []
    n = inicio
    while n <= len(linhas):
        if _ABRE_MERMAID.match(linhas[n - 1]):
            interno: list[str] = []
            fecha = None
            m = n + 1
            while m <= len(linhas):
                if _FENCE.match(linhas[m - 1]):
                    fecha = m
                    break
                interno.append(linhas[m - 1])
                m += 1
            blocos.append((n, fecha, interno))
            n = (fecha or len(linhas)) + 1
            continue
        n += 1
    return blocos


def checar_mermaid(rel: str, linhas: list[str], inicio: int) -> list[Violacao]:
    """Todo bloco mermaid e tipado, nao vazio, fechado e seguido de descricao.

    A exigencia de descricao vem do CLAUDE.md: 'diagramas sempre em Mermaid e
    seguidos de descricao textual'. Aqui ela deixa de ser recomendacao.
    """
    saida: list[Violacao] = []
    for abre, fecha, interno in _blocos_mermaid(linhas, inicio):
        if fecha is None:
            saida.append(Violacao(rel, abre, "mermaid-nao-fechado", "bloco mermaid sem '```'"))
            continue
        uteis = [ln.strip() for ln in interno if ln.strip()]
        if not uteis:
            saida.append(Violacao(rel, abre, "mermaid-vazio", "bloco mermaid sem conteudo"))
            continue
        token = uteis[0].split()[0].rstrip(":")
        if token not in TIPOS_MERMAID:
            aceitos = ", ".join(sorted(TIPOS_MERMAID))
            saida.append(
                Violacao(
                    rel, abre + 1, "mermaid-tipo",
                    f"tipo de diagrama {token!r} desconhecido; aceitos: {aceitos}",
                )
            )
        seguinte = next(
            (ln.strip() for ln in linhas[fecha:] if ln.strip()), ""
        )
        if not seguinte or seguinte.startswith(("#", "```", "|", "-", "*", "<!--")):
            saida.append(
                Violacao(
                    rel, fecha, "mermaid-sem-descricao",
                    "diagrama sem paragrafo descritivo imediatamente apos o bloco",
                )
            )
    return saida


def checar_diagramas_obrigatorios(
    rel: str, texto_do_volume: str, tipo: str, ct: Contrato
) -> list[Violacao]:
    """O volume inteiro precisa conter os diagramas exigidos pelo seu tipo."""
    saida: list[Violacao] = []
    for exigido in ct.diagramas_de(tipo):
        if exigido not in texto_do_volume:
            saida.append(
                Violacao(
                    rel, 0, "diagrama-obrigatorio",
                    f"tipo {tipo} exige um diagrama {exigido} em algum lugar do volume",
                )
            )
    return saida


def checar_exemplos(raiz: Path, rel: str, linhas: list[str], inicio: int) -> list[Violacao]:
    """Exemplo citado existe como arquivo e tem teste correspondente.

    Sintaxe da citacao: <!-- exemplo: exemplos/<pasta>/<arquivo>.py -->
    Teste esperado:     exemplos/<pasta>/tests/test_<arquivo>.py
    """
    saida: list[Violacao] = []
    for n, linha in _fora_de_codigo(linhas, inicio):
        for citado in _CITA_EXEMPLO.findall(linha):
            alvo = raiz / citado
            if not alvo.exists():
                saida.append(
                    Violacao(rel, n, "exemplo-inexistente", f"exemplo citado nao existe: {citado}")
                )
                continue
            teste = alvo.parent / "tests" / f"test_{alvo.stem}.py"
            if not teste.exists():
                saida.append(
                    Violacao(
                        rel, n, "exemplo-sem-teste",
                        f"exemplo {citado} nao tem teste em {teste.relative_to(raiz).as_posix()}",
                    )
                )
    return saida


def checar_links(
    raiz: Path, caminho: Path, rel: str, linhas: list[str], inicio: int
) -> list[Violacao]:
    """Todo link relativo resolve. Links http(s)/mailto e ancoras sao ignorados."""
    saida: list[Violacao] = []
    for n, linha in _fora_de_codigo(linhas, inicio):
        for destino in _LINK.findall(linha):
            if destino.startswith(("http://", "https://", "mailto:", "#")):
                continue
            alvo = (caminho.parent / destino).resolve()
            if not alvo.exists():
                saida.append(Violacao(rel, n, "link-morto", f"link nao resolve: {destino}"))
    return saida
