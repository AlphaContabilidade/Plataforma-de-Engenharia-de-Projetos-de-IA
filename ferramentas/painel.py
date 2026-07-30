"""Painel de console da AI-ENGINEERING-OS: a interface de uso da plataforma.

Por que existe: a maquina de producao (contrato, gates, scaffold, exportacao) e
completa mas nao tem porta de entrada. Quem chega precisa saber *quais* comandos
existem, em que ordem, e o que cada saida significa - e isso hoje mora em prosa
espalhada por `CLAUDE.md`, `Convencoes.md` e `ROADMAP.md`. O painel junta essa
informacao num menu numerado: ninguem precisa decorar comando nem ler documento
para descobrir o que existe, o que falta e qual e o proximo passo.

Duas decisoes de fundo, ambas deliberadas:

1. **O painel nao escreve volume.** Ele prepara briefing e roda gate. Conteudo e
   escrito por um modelo, com o criador/auditor descrito no `CLAUDE.md`. Um
   painel que gerasse secao a partir de template produziria exatamente o
   enchimento que a plataforma proibe.
2. **Nenhuma regra e reimplementada aqui.** Tipo, secoes, limiares, diagramas e
   veredictos vem de `contrato`, `status`, `validar`, `scaffold` e `exportar`.
   Duplicar regra em camada de apresentacao e como a interface passa a mentir
   sobre o motor.

Uso:
    python -m ferramentas.painel              # interativo
    python -m ferramentas.painel --resumo     # resumo do acervo, exit 0
    python -m ferramentas.painel --briefing NN
    python -m ferramentas.painel --gates NN   # exit 1 se algum gate reprovar
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from . import exportar, scaffold
from .contrato import Contrato, ContratoInvalido, carregar
from .frontmatter import FrontMatterInvalido, ler_volume_yml
from .modelo import Violacao
from .status import (
    PENDENTE,
    EstadoVolume,
    levantar,
    relatorio_mais_recente,
    tabela,
)
from .validar import validar_cross_refs, validar_volume

PASTA_BRIEFINGS = "briefings"
ARQUIVO_ROADMAP = "ROADMAP.md"
LARGURA = 78

# Ordem de avanco dos status. `PENDENTE` e derivado (pasta ausente) e por isso
# fica abaixo de `RASCUNHO`, que ao menos tem `_VOLUME.yml` em disco.
_PESO_STATUS = {PENDENTE: 0, "RASCUNHO": 1, "REQUER_REVISAO": 2, "PRONTO": 3}

# As regras que mais reprovam volume novo, com o motivo em linguagem de quem vai
# escrever. Os nomes sao os que `regras.py` e `validar.py` emitem de verdade -
# `test_painel.py::test_regras_citadas_existem_no_motor` reprova a suite se
# algum nome deixar de existir, para o briefing nao ensinar regra fantasma.
REGRAS_QUE_MAIS_REPROVAM: tuple[tuple[str, str], ...] = (
    (
        "secao-ausente",
        "faltou um arquivo de secao obrigatorio do tipo; crie todos antes de rodar o gate",
    ),
    (
        "substancia-curta",
        "prosa abaixo do minimo da secao; codigo e cabecalho nao contam como prosa",
    ),
    (
        "frontmatter-coerencia",
        "campo `secao` diferente do nome do arquivo, ou `volume`/`tipo` diferentes do "
        "_VOLUME.yml; e o erro classico de copiar uma secao e esquecer de trocar o campo",
    ),
    (
        "mermaid-sem-descricao",
        "todo bloco mermaid exige um paragrafo de prosa imediatamente depois; tabela, "
        "lista, cabecalho ou nova cerca nao contam como descricao",
    ),
    (
        "diagrama-obrigatorio",
        "o tipo do volume exige diagramas especificos em algum lugar do volume",
    ),
    (
        "exemplo-sem-teste",
        "codigo citado com <!-- exemplo: ... --> precisa de tests/test_<arquivo>.py ao lado",
    ),
    (
        "marcador-proibido",
        "TBD, TODO, PENDENTE, FIXME, XXX e 'preencher aqui' na prosa; pendencia vai "
        "para 16-Roadmap, nunca para o corpo",
    ),
    (
        "link-morto",
        "link relativo que nao resolve em disco; links http(s) e ancoras sao ignorados",
    ),
)

_CABECA_GRUPO = re.compile(r"^\*\*(Grupo\s+\d+[^*]*?)\.?\*\*")
_ID_EM_CODE_SPAN = re.compile(r"`(\d{2})`")
# Faixa `22`-`25`, com hifen ou travessao. Sem expandir a faixa, 23 e 24 ficariam
# sem fronteira mesmo estando declarados no ROADMAP.
_FAIXA_DE_IDS = re.compile(r"`(\d{2})`\s*[–—-]\s*`(\d{2})`")


# --------------------------------------------------------------------------
# Funcoes puras: sao elas que os testes exercitam.
# --------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Resumo:
    """Retrato do acervo em uma tela."""

    total: int
    contagem: dict[str, int]
    mais_avancado: EstadoVolume | None
    proxima_acao: str


@dataclass(frozen=True, slots=True)
class Fronteira:
    """Fronteira de escopo de um grupo sobreposto, lida do `ROADMAP.md`."""

    titulo: str
    volumes: tuple[str, ...]
    texto: str


@dataclass(frozen=True, slots=True)
class Briefing:
    """Tudo que um modelo precisa saber para escrever um volume.

    Nenhum campo e inventado: cada um sai do contrato, do disco ou do
    `ROADMAP.md`. Onde a plataforma nao tem a informacao, o campo vem vazio e o
    texto do briefing diz que esta vazio - nunca preenche por conta.
    """

    vol_id: str
    nome: str
    tipo: str
    status: str
    perecivel: bool
    secoes_obrigatorias: tuple[str, ...]
    minimos: dict[str, int]
    diagramas_obrigatorios: tuple[str, ...]
    secoes_ausentes: tuple[str, ...]
    depende_de: tuple[str, ...]
    pre_requisitos: tuple[tuple[str, str, str], ...]
    escopo: str
    fronteira: Fronteira | None
    pasta_exemplos: str


@dataclass(frozen=True, slots=True)
class Veredicto:
    """Resultado de um dos tres gates, em forma legivel."""

    gate: int
    nome: str
    aprovado: bool
    detalhe: str
    violacoes: tuple[Violacao, ...]


def normalizar_id(bruto: str) -> str:
    """`7` e `07` sao o mesmo volume para quem digita, nunca para a maquina.

    O contrato indexa por string de dois digitos. Normalizar na borda evita que
    `--briefing 7` caia em `ContratoInvalido` por um zero.
    """
    return str(bruto).strip().zfill(2)


def secoes_ausentes(raiz: Path, vol_id: str, ct: Contrato) -> tuple[str, ...]:
    """Secoes que o tipo exige e que nao existem em disco, em ordem canonica.

    O tipo vem do contrato, nao do `_VOLUME.yml`: o contrato vence, e um yml com
    tipo divergente e violacao `volume-tipo` no gate 1 - nao base para calcular
    o que falta.
    """
    meta = ct.volume(vol_id)
    pasta = scaffold.pasta_de(raiz, vol_id, ct)
    return tuple(
        secao for secao in ct.secoes_de(meta["tipo"]) if not (pasta / f"{secao}.md").exists()
    )


def _chave_de_avanco(e: EstadoVolume) -> tuple[int, int, float]:
    return (_PESO_STATUS.get(e.status, 0), e.secoes_presentes, e.nota_auditoria or -1.0)


def _proxima_acao(estados: list[EstadoVolume]) -> str:
    """Uma frase, em linguagem simples, dizendo o que fazer agora.

    A ordem de prioridade e deliberada: primeiro consertar o que a auditoria
    reprovou, depois fechar o que esta pela metade, e so no fim comecar coisa
    nova. Acervo com volume reprovado e volume meio escrito acumula divida mais
    rapido do que ganha cobertura.
    """
    reprovados = [e for e in estados if e.status == "REQUER_REVISAO"]
    if reprovados:
        e = reprovados[0]
        nota = f"{e.nota_auditoria:.1f}" if e.nota_auditoria is not None else "sem nota"
        return (
            f"Incorpore o feedback da auditoria do volume {e.vol_id}-{e.nome} "
            f"(media {nota}) e rode os gates de novo: opcao 3 do menu."
        )

    cheios = [
        e
        for e in estados
        if e.status == "RASCUNHO" and e.secoes_presentes == e.secoes_esperadas
    ]
    if cheios:
        e = cheios[0]
        return (
            f"O volume {e.vol_id}-{e.nome} tem todas as secoes em disco mas ainda e "
            f"RASCUNHO: rode os gates (opcao 3) e, se passarem, mande auditar."
        )

    parciais = [
        e for e in estados if 0 < e.secoes_presentes < e.secoes_esperadas
    ]
    if parciais:
        e = parciais[0]
        faltam = e.secoes_esperadas - e.secoes_presentes
        return (
            f"Termine o volume {e.vol_id}-{e.nome} antes de comecar outro: faltam "
            f"{faltam} secao(oes). A opcao 2 lista quais."
        )

    fantasmas = [e for e in estados if e.status == PENDENTE]
    if fantasmas:
        return (
            f"{len(fantasmas)} volume(s) do contrato ainda nao existem como pasta em "
            f"disco. Rode a opcao 5 para materializar todos de uma vez."
        )

    vazios = [e for e in estados if e.secoes_presentes == 0]
    if vazios:
        e = vazios[0]
        return (
            f"Escreva o proximo volume: {e.vol_id}-{e.nome} e o de menor numero sem "
            f"nenhuma secao escrita. A opcao 4 monta o briefing dele."
        )

    return (
        "Todo volume declarado tem secao escrita e nenhum esta reprovado. Rode a "
        "opcao 6 para exportar o site e a opcao 3 para reconferir os gates."
    )


def resumo_do_acervo(raiz: Path, ct: Contrato) -> Resumo:
    """Contagem por status, volume mais avancado e a proxima acao recomendada."""
    estados = levantar(raiz, ct)
    contagem: dict[str, int] = {}
    for e in estados:
        contagem[e.status] = contagem.get(e.status, 0) + 1
    # max() devolve o primeiro maximo, e `levantar` ordena por id: empate entre
    # dois volumes igualmente avancados resolve pelo menor numero, sem sorteio.
    mais = max(estados, key=_chave_de_avanco) if estados else None
    return Resumo(len(estados), contagem, mais, _proxima_acao(estados))


def _ids_da_linha(linha: str) -> tuple[str, ...]:
    achados: list[str] = []
    for inicio, fim in _FAIXA_DE_IDS.findall(linha):
        achados.extend(f"{n:02d}" for n in range(int(inicio), int(fim) + 1))
    for solto in _ID_EM_CODE_SPAN.findall(linha):
        if solto not in achados:
            achados.append(solto)
    return tuple(sorted(set(achados)))


def fronteiras_do_roadmap(raiz: Path) -> tuple[Fronteira, ...]:
    """Le do `ROADMAP.md` as fronteiras por grupo, sem duplicar o texto aqui.

    A decisao de 2026-07-29 resolveu a sobreposicao de dominios por fronteira
    declarada no `03-Escopo` de cada volume, e o `ROADMAP.md` e onde essas
    fronteiras foram registradas. Copiar as tabelas para dentro do Python
    criaria uma segunda versao que envelhece sozinha; por isso o painel le o
    documento. Se o formato mudar e a leitura nao achar nada, o painel diz que
    nao achou - nao inventa fronteira.
    """
    arq = raiz / ARQUIVO_ROADMAP
    if not arq.is_file():
        return ()
    achados: list[tuple[str, tuple[str, ...], list[str]]] = []
    atual: tuple[str, tuple[str, ...], list[str]] | None = None
    for linha in arq.read_text(encoding="utf-8").splitlines():
        casado = _CABECA_GRUPO.match(linha.strip())
        if casado:
            if atual is not None:
                achados.append(atual)
            atual = (casado.group(1).strip(), _ids_da_linha(linha), [linha.strip()])
            continue
        if atual is None:
            continue
        if linha.startswith("#"):
            achados.append(atual)
            atual = None
            continue
        atual[2].append(linha.rstrip())
    if atual is not None:
        achados.append(atual)
    return tuple(
        Fronteira(titulo, ids, "\n".join(bloco).strip())
        for titulo, ids, bloco in achados
        if ids
    )


def fronteira_de(raiz: Path, vol_id: str) -> Fronteira | None:
    """A fronteira do grupo a que o volume pertence, ou None se ele nao tem grupo."""
    for f in fronteiras_do_roadmap(raiz):
        if vol_id in f.volumes:
            return f
    return None


def _yml_do_volume(raiz: Path, vol_id: str, ct: Contrato) -> dict[str, object]:
    yml = scaffold.pasta_de(raiz, vol_id, ct) / scaffold.ARQUIVO_VOLUME
    if not yml.exists():
        return {}
    try:
        return ler_volume_yml(yml)
    except FrontMatterInvalido:
        return {}


def pasta_de_exemplos(vol_id: str, nome: str) -> str:
    """Caminho relativo dos exemplos do volume: `exemplos/NN-nome-minusculo`."""
    return f"exemplos/{vol_id}-{nome.lower()}"


def briefing_de(raiz: Path, vol_id: str, ct: Contrato) -> Briefing:
    """Monta o briefing completo de um volume a partir do contrato e do disco."""
    vol_id = normalizar_id(vol_id)
    meta = ct.volume(vol_id)
    tipo = meta["tipo"]
    yml = _yml_do_volume(raiz, vol_id, ct)

    deps = yml.get("depende_de", []) or []
    if isinstance(deps, str):
        deps = [deps]
    deps = tuple(str(d) for d in deps)

    estados = {e.vol_id: e for e in levantar(raiz, ct)}
    pre = tuple(
        (d, estados[d].nome, estados[d].status) if d in estados else (d, "?", "NAO DECLARADO")
        for d in deps
    )

    secoes = ct.secoes_de(tipo)
    return Briefing(
        vol_id=vol_id,
        nome=meta["nome"],
        tipo=tipo,
        status=str(yml.get("status", PENDENTE)),
        perecivel=bool(meta.get("perecivel")),
        secoes_obrigatorias=secoes,
        minimos={s: ct.minimo_de(s) for s in secoes},
        diagramas_obrigatorios=ct.diagramas_de(tipo),
        secoes_ausentes=secoes_ausentes(raiz, vol_id, ct),
        depende_de=deps,
        pre_requisitos=pre,
        escopo=str(yml.get("escopo", "") or ""),
        fronteira=fronteira_de(raiz, vol_id),
        pasta_exemplos=pasta_de_exemplos(vol_id, meta["nome"]),
    )


def agrupar_por_regra(violacoes: tuple[Violacao, ...] | list[Violacao]) -> dict[str, tuple[Violacao, ...]]:
    """Agrupa violacoes por nome de regra, da mais frequente para a menos.

    Uma lista plana de setenta violacoes nao ensina nada; 'substancia-curta x18'
    diz na primeira linha que o volume esta raso, e nao que tem setenta defeitos
    diferentes.
    """
    grupos: dict[str, list[Violacao]] = {}
    for v in violacoes:
        grupos.setdefault(v.regra, []).append(v)
    ordenado = sorted(grupos.items(), key=lambda par: (-len(par[1]), par[0]))
    return {regra: tuple(itens) for regra, itens in ordenado}


def _rodar_pytest(raiz: Path, alvo: Path) -> tuple[bool, str]:
    """Roda pytest no alvo e devolve (passou, ultima linha util da saida)."""
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(alvo), "-q"],
            cwd=str(raiz),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as erro:  # interprete ausente ou sem permissao de execucao
        return False, f"nao foi possivel rodar pytest: {erro}"
    linhas = [ln.strip() for ln in (proc.stdout or "").splitlines() if ln.strip()]
    resumo = linhas[-1] if linhas else (proc.stderr or "").strip()[:200]
    return proc.returncode == 0, resumo or "pytest nao produziu saida"


def veredicto_dos_gates(
    raiz: Path, vol_id: str, ct: Contrato, *, rodar_testes: bool = True
) -> tuple[Veredicto, ...]:
    """Roda os tres gates do volume, na ordem em que a plataforma os define.

    Gate 3 e do acervo inteiro por natureza: o grafo de `depende_de` e global, e
    um ciclo em qualquer par de volumes invalida o grafo todo. Reportar 'gate 3
    verde' olhando so um volume seria falso, entao o veredicto carrega as
    violacoes de todo o acervo e diz isso no nome.
    """
    vol_id = normalizar_id(vol_id)
    meta = ct.volume(vol_id)

    v1 = tuple(validar_volume(raiz, vol_id, ct))
    gate1 = Veredicto(
        1,
        "estrutural (ferramentas.validar)",
        not v1,
        "sem violacoes" if not v1 else f"{len(v1)} violacao(oes)",
        v1,
    )

    alvo = raiz / pasta_de_exemplos(vol_id, meta["nome"])
    if not alvo.is_dir():
        gate2 = Veredicto(
            2,
            "executavel (pytest dos exemplos)",
            True,
            f"{alvo.name} nao existe: o volume nao cita exemplo executavel, "
            "nada a rodar",
            (),
        )
    elif not rodar_testes:
        gate2 = Veredicto(2, "executavel (pytest dos exemplos)", True, "execucao desligada", ())
    else:
        passou, detalhe = _rodar_pytest(raiz, alvo)
        gate2 = Veredicto(2, "executavel (pytest dos exemplos)", passou, detalhe, ())

    v3 = tuple(validar_cross_refs(raiz, ct))
    gate3 = Veredicto(
        3,
        "referencias cruzadas (acervo inteiro)",
        not v3,
        "sem violacoes" if not v3 else f"{len(v3)} violacao(oes) no acervo",
        v3,
    )
    return (gate1, gate2, gate3)


# --------------------------------------------------------------------------
# Renderizacao. Texto puro e ASCII: o terminal alvo e o Windows.
# --------------------------------------------------------------------------


def _regua(caractere: str = "-") -> str:
    return caractere * LARGURA


def _caixa(titulo: str) -> str:
    return f"{_regua('=')}\n  {titulo}\n{_regua('=')}"


def texto_do_resumo(raiz: Path, ct: Contrato) -> str:
    """A tela inicial: o que existe, o que falta e o que fazer agora."""
    r = resumo_do_acervo(raiz, ct)
    linhas = [_caixa("AI-ENGINEERING-OS - painel do acervo")]
    linhas.append("")
    linhas.append(
        "Acervo tecnico de engenharia de IA em 42 volumes. Nada entra sem passar"
    )
    linhas.append("por porta de qualidade executavel: sao tres gates, e eles reprovam.")
    linhas.append("")
    linhas.append(f"Volumes declarados no contrato: {r.total}")
    for status in ("PRONTO", "REQUER_REVISAO", "RASCUNHO", PENDENTE):
        linhas.append(f"  {status:<16} {r.contagem.get(status, 0):>3}")
    outros = {k: v for k, v in r.contagem.items() if k not in _PESO_STATUS}
    for status, quanto in sorted(outros.items()):
        linhas.append(f"  {status:<16} {quanto:>3}   (status fora do contrato)")
    linhas.append("")
    if r.mais_avancado is not None:
        e = r.mais_avancado
        nota = f"{e.nota_auditoria:.1f}" if e.nota_auditoria is not None else "sem auditoria"
        linhas.append(
            f"Volume mais avancado: {e.vol_id}-{e.nome} ({e.tipo}) - {e.status}, "
            f"{e.secoes_presentes}/{e.secoes_esperadas} secoes, auditoria {nota}"
        )
    linhas.append("")
    linhas.append("Proxima acao recomendada:")
    for pedaco in _quebrar(r.proxima_acao, LARGURA - 2):
        linhas.append(f"  {pedaco}")
    return "\n".join(linhas)


def _quebrar(texto: str, largura: int) -> list[str]:
    """Quebra em linhas de largura maxima sem cortar palavra."""
    saida: list[str] = []
    atual = ""
    for palavra in texto.split():
        if atual and len(atual) + 1 + len(palavra) > largura:
            saida.append(atual)
            atual = palavra
        else:
            atual = f"{atual} {palavra}".strip()
    if atual:
        saida.append(atual)
    return saida or [""]


def texto_da_inspecao(raiz: Path, vol_id: str, ct: Contrato) -> str:
    """Ficha completa de um volume: o que tem, o que falta, e o que julgou."""
    vol_id = normalizar_id(vol_id)
    meta = ct.volume(vol_id)
    b = briefing_de(raiz, vol_id, ct)
    ausentes = b.secoes_ausentes
    presentes = [s for s in b.secoes_obrigatorias if s not in ausentes]

    linhas = [_caixa(f"Volume {vol_id}-{meta['nome']}")]
    linhas.append(f"Tipo:      {b.tipo}")
    linhas.append(f"Status:    {b.status}")
    linhas.append(f"Perecivel: {'sim - fino, sem numero que expira' if b.perecivel else 'nao'}")
    linhas.append(
        f"Secoes:    {len(presentes)}/{len(b.secoes_obrigatorias)} presentes em disco"
    )
    linhas.append("")
    linhas.append("Secoes presentes:")
    linhas.append("  " + (", ".join(presentes) if presentes else "(nenhuma)"))
    linhas.append("")
    linhas.append("Secoes AUSENTES:")
    linhas.append("  " + (", ".join(ausentes) if ausentes else "(nenhuma - volume completo)"))
    linhas.append("")

    relatorio = relatorio_mais_recente(raiz, vol_id)
    estado = {e.vol_id: e for e in levantar(raiz, ct)}[vol_id]
    if relatorio is None:
        linhas.append("Auditoria: nenhum relatorio em auditorias/ para este volume.")
    else:
        nota = (
            f"{estado.nota_auditoria:.1f}"
            if estado.nota_auditoria is not None
            else "sem linha 'media:' reconhecida"
        )
        linhas.append(f"Auditoria vigente: {relatorio.name}")
        linhas.append(f"  media: {nota}   (PRONTO exige media >= 8,0 e nenhuma secao < 6)")
    linhas.append("")

    if b.pre_requisitos:
        linhas.append("depende_de (pre-requisito de leitura):")
        for dep_id, dep_nome, dep_status in b.pre_requisitos:
            linhas.append(f"  {dep_id}-{dep_nome}  [{dep_status}]")
    else:
        linhas.append("depende_de: vazio (nenhum pre-requisito de leitura declarado).")
    linhas.append("")

    if b.fronteira is None:
        linhas.append(
            "Fronteira de escopo: este volume nao esta em nenhum grupo sobreposto "
            "do ROADMAP.md."
        )
    else:
        linhas.append(f"Fronteira de escopo - {b.fronteira.titulo}")
        linhas.append(
            "  Declare no 03-Escopo o que pertence ao vizinho. Fronteira ausente e "
            "lacuna de conteudo."
        )
        linhas.append(_regua())
        linhas.append(b.fronteira.texto)
        linhas.append(_regua())
    return "\n".join(linhas)


def texto_dos_gates(vereditos: tuple[Veredicto, ...]) -> str:
    """Os tres gates com veredicto legivel e violacoes agrupadas por regra."""
    linhas = [_caixa("Gates")]
    for v in vereditos:
        marca = "APROVADO" if v.aprovado else "REPROVADO"
        linhas.append("")
        linhas.append(f"Gate {v.gate} - {v.nome}: {marca}")
        linhas.append(f"  {v.detalhe}")
        if not v.violacoes:
            continue
        for regra, itens in agrupar_por_regra(v.violacoes).items():
            linhas.append(f"  [{regra}] x{len(itens)}")
            for item in itens[:5]:
                linhas.append(f"      {item.arquivo}:{item.linha}: {item.mensagem}")
            if len(itens) > 5:
                linhas.append(f"      ... e {len(itens) - 5} outra(s) da mesma regra")
    linhas.append("")
    todos = all(v.aprovado for v in vereditos)
    linhas.append(
        "Resultado: os tres gates passaram."
        if todos
        else "Resultado: algum gate reprovou. Gate vermelho grava RASCUNHO, nunca PRONTO."
    )
    return "\n".join(linhas)


def texto_do_briefing(b: Briefing) -> str:
    """O briefing como prompt pronto para colar num agente.

    Sai em Markdown porque o destino e um modelo, e porque gravado em
    `briefings/` ele continua legivel por humano.
    """
    linhas = [
        f"# Briefing de producao - volume {b.vol_id}-{b.nome}",
        "",
        "Gerado por `python -m ferramentas.painel --briefing "
        f"{b.vol_id}` a partir de `00-INTRODUCAO/contrato.json`, do disco e do "
        "`ROADMAP.md`.",
        "",
        "> O painel **prepara e verifica**; ele nao escreve o volume e nao inventa "
        "conteudo. Tudo abaixo e o que a plataforma ja sabe. O que a plataforma nao "
        "sabe aparece como lacuna explicita, nunca preenchido por conta.",
        "",
        "## 1. Identidade",
        "",
        f"- **Volume:** `{b.vol_id}` - {b.nome}",
        f"- **Tipo:** `{b.tipo}` (o tipo e que decide quais secoes sao obrigatorias)",
        f"- **Status atual:** `{b.status}`",
        f"- **Perecivel:** {'sim' if b.perecivel else 'nao'}",
        f"- **Pasta do volume:** `{b.vol_id}-{b.nome}/`",
        f"- **Pasta dos exemplos:** `{b.pasta_exemplos}/` "
        f"(teste ao lado, em `{b.pasta_exemplos}/tests/test_<arquivo>.py`)",
    ]
    if b.perecivel:
        linhas += [
            "",
            "Volume perecivel: **nao fixe numero que expira** - preco por milhao de "
            "tokens, janela de contexto, limite por minuto, nome de modelo. Descreva o "
            "**metodo** de decidir e aponte a fonte viva. Perecivel longo e divida.",
        ]

    linhas += [
        "",
        "## 2. Escopo declarado no `_VOLUME.yml`",
        "",
        f"{b.escopo}" if b.escopo.strip() else
        "_Vazio._ O `_VOLUME.yml` nao declara escopo. Escrever o `03-Escopo` implica "
        "decidir esse escopo; se a decisao nao for obvia a partir dos volumes "
        "vizinhos, ela e do autor, nao sua.",
        "",
        f"## 3. Secoes obrigatorias do tipo `{b.tipo}` ({len(b.secoes_obrigatorias)})",
        "",
        "Minimo de palavras **de prosa** por secao. Codigo entre cercas e linha de "
        "cabecalho nao contam. O minimo e piso, nao meta.",
        "",
        "| Secao | Minimo de prosa | Em disco |",
        "|---|---|---|",
    ]
    for secao in b.secoes_obrigatorias:
        marca = "ausente" if secao in b.secoes_ausentes else "presente"
        linhas.append(f"| `{secao}` | {b.minimos[secao]} | {marca} |")

    linhas += [
        "",
        f"Faltam **{len(b.secoes_ausentes)}** secao(oes): "
        + (", ".join(f"`{s}`" for s in b.secoes_ausentes) if b.secoes_ausentes else "nenhuma."),
        "",
        "## 4. Diagramas obrigatorios",
        "",
    ]
    if b.diagramas_obrigatorios:
        for d in b.diagramas_obrigatorios:
            # A cerca vai como code span: escrever tres acentos graves literais
            # aqui abriria um bloco de codigo no meio do briefing renderizado.
            linhas.append(f"- `{d}` - em algum lugar do volume, em bloco cercado `mermaid`")
        linhas += [
            "",
            "Todo bloco Mermaid e seguido **imediatamente** por um paragrafo de prosa "
            "descrevendo o que o diagrama mostra. Cabecalho, tabela, lista ou nova "
            "cerca no lugar da prosa reprova em `mermaid-sem-descricao`.",
        ]
    else:
        linhas.append(
            f"Nenhum. O tipo `{b.tipo}` nao exige diagrama obrigatorio - e nao invente "
            "um so para parecer completo."
        )

    linhas += ["", "## 5. Pre-requisitos de leitura (`depende_de`)", ""]
    if b.pre_requisitos:
        linhas.append("Leia estes volumes **antes** de escrever, porque o novo cita o contrato deles:")
        linhas.append("")
        for dep_id, dep_nome, dep_status in b.pre_requisitos:
            linhas.append(f"- `{dep_id}-{dep_nome}` - status `{dep_status}`")
        linhas += [
            "",
            "Pre-requisito em `PENDENTE` ou `RASCUNHO` vazio e sinal de ordem errada de "
            "producao: escrever agora produz secao que cita contrato inexistente.",
        ]
    else:
        linhas.append(
            "`depende_de` esta vazio. Vizinhanca bidirecional (assunto proximo) vai em "
            "`18-Referencias-Cruzadas.md`, **fora** do grafo - senao dois volumes "
            "vizinhos formam ciclo falso e o gate 3 reprova."
        )

    linhas += ["", "## 6. Fronteira de escopo do grupo", ""]
    if b.fronteira is None:
        linhas.append(
            "Este volume nao aparece em nenhum grupo sobreposto do `ROADMAP.md`. Ainda "
            "assim o `03-Escopo` declara o que fica fora e qual volume cobre o que ficou fora."
        )
    else:
        linhas += [
            f"Do `ROADMAP.md`, secao \"Decisao tomada: sobreposicao de dominios\" - "
            f"**{b.fronteira.titulo}**. Regra que vale: todo volume de um grupo sobreposto "
            "declara a fronteira no seu `03-Escopo`, nomeando o volume vizinho e o que "
            "pertence a ele. Fronteira ausente e lacuna de conteudo, e a auditoria cobra "
            "isso na secao 03.",
            "",
            b.fronteira.texto,
        ]

    linhas += [
        "",
        "## 7. As regras que mais reprovam",
        "",
        "Nomes reais das regras emitidas por `ferramentas/regras.py` e "
        "`ferramentas/validar.py`. Cite a regra pelo nome quando quiser discutir o "
        "veredicto - e assim que a conversa fica ancorada no que a maquina verifica.",
        "",
    ]
    for regra, porque in REGRAS_QUE_MAIS_REPROVAM:
        linhas.append(f"- **`{regra}`** - {porque}")

    linhas += [
        "",
        "## 8. Front-matter de cada arquivo de secao",
        "",
        "```yaml",
        "---",
        f'volume: "{b.vol_id}"',
        f"volume_nome: {b.nome}",
        f"tipo: {b.tipo}",
        "secao: 01-Introducao",
        "status: RASCUNHO",
        "atualizado_em: AAAA-MM-DD",
        "---",
        "```",
        "",
        "`secao` tem de ser identico ao nome do arquivo sem `.md`; `volume`, "
        "`volume_nome` e `tipo` tem de coincidir com o `_VOLUME.yml`. `status` aceita "
        "so `RASCUNHO`, `REQUER_REVISAO` e `PRONTO`.",
        "",
        "## 9. O que nao fazer, em nenhuma hipotese",
        "",
        "1. Nao gravar `PRONTO` com gate vermelho. Gate vermelho grava `RASCUNHO` e "
        "reporta as violacoes.",
        "2. Nao inventar framework, numero ou fonte. Nome sem definicao vai para "
        "`frameworks/_backlog.md`; numero sem fonte nao entra; autor que voce nao pode "
        "verificar nao e citado.",
        "3. Nao afirmar sucesso sem ter olhado. Rodou o gate? Cole a saida.",
        "4. Nao ajustar o teste para o conteudo passar. O teste e o contrato.",
        "5. Nao marcar pendencia com marcador proibido na prosa - use `16-Roadmap`.",
        "",
        "## 10. Como fechar",
        "",
        "```bash",
        f"python -m ferramentas.validar {b.vol_id}",
        f"python -m pytest {b.pasta_exemplos} -q",
        "python -m ferramentas.validar --cross-refs",
        "```",
        "",
        "`PRONTO` exige os quatro ao mesmo tempo: gate 1 verde, gate 2 verde, auditoria "
        "com media >= 8,0 e nenhuma secao abaixo de 6, e registro datado no "
        "`CHANGELOG.md`. Falta um dos quatro, o volume nao e `PRONTO`.",
        "",
    ]
    return "\n".join(linhas)


TEXTO_EXPLICACAO = """\
O que e a AI-ENGINEERING-OS
---------------------------
Um acervo tecnico de engenharia de IA em 42 volumes, cada um com 18 secoes fixas.
O ativo desta plataforma NAO e a contagem de arquivos: e a maquina de producao.
O diferencial nao e escrever muito - e que nada entra no acervo sem passar por
porta de qualidade executavel. Um volume so se declara pronto quando um programa
confirma que ele e.

A fonte unica de verdade
------------------------
`00-INTRODUCAO/contrato.json` define secoes, tipos de volume, status validos,
limiares de palavras, marcadores proibidos, diagramas obrigatorios e os 42
volumes. Toda ferramenta le esse arquivo; nenhuma tem regra duplicada em codigo.
`00-INTRODUCAO/Convencoes.md` e a mesma informacao em forma humana, e um teste
reprova a suite se as duas versoes divergirem.

Cinco tipos de volume, e o tipo decide as secoes
------------------------------------------------
ENGINE, ARQUITETURA e GOVERNANCA exigem as 18 secoes da base. PROCESSO dispensa
08-Modelos (o fluxo importa mais que o modelo de dados). BIBLIOTECA troca
04-Arquitetura e 05-Diagramas por 04-Catalogo. Isso existe porque exigir "maquina
de estados" de um volume de templates forca enchimento - e em vez de relaxar a
regra de qualidade, relaxamos a lista de secoes, de forma explicita e auditavel.

Os tres gates, na ordem em que rodam
------------------------------------
  Gate 1  Estrutural       python -m ferramentas.validar NN
          Reprova: front-matter, secao ausente, prosa curta, marcador proibido,
          Mermaid sem descricao, exemplo sem teste, link morto.

  Gate 2  Executavel       python -m pytest exemplos/<vol> -q
          Reprova: codigo citado pelo volume que nao roda ou nao passa.

  Gate 3  Referencias      python -m ferramentas.validar --cross-refs
          Reprova: depende_de para volume inexistente, ciclo no grafo.

A auditoria entra ENTRE o gate 2 e o gate 3: audita-se o que ja e estruturalmente
valido e executavel, porque julgar o texto de um volume que nem compila e gastar
a auditoria no problema errado.

Quem escreve nao se aprova
--------------------------
O criador escreve o volume e roda os gates. O auditor e outro modelo, em outra
sessao, com outro contexto - ele julga secao por secao de 0 a 10 e NAO edita o
volume. Revisar o proprio texto no mesmo contexto tende a confirmar o que ja
esta la em vez de encontrar o que falta.

A Definicao de PRONTO
---------------------
Contagem de paginas nao mede qualidade - mede volume de texto, e otimizar por
volume de texto produz enchimento. Um volume e PRONTO quando, e somente quando,
os quatro criterios abaixo valem ao mesmo tempo:

  1. `python -m ferramentas.validar NN` retorna exit 0.
  2. `python -m pytest exemplos/<vol>` passa.
  3. A auditoria registra media >= 8,0 e nenhuma secao abaixo de 6.
  4. O resultado esta registrado no CHANGELOG.md com a data do dia.

Falta um dos quatro, o volume nao e PRONTO. Auditoria abaixo de 8,0 grava
REQUER_REVISAO; gate estrutural vermelho mantem RASCUNHO e reporta as violacoes.
PENDENTE nao e valor gravavel: e estado derivado, calculado quando a pasta do
volume nao existe.

As proibicoes, que e o que separa isto de um gerador de texto convincente
------------------------------------------------------------------------
  1. Nunca gravar PRONTO com gate vermelho. Status que mente destroi o valor de
     todos os outros status do acervo.
  2. Nunca inventar framework, numero ou fonte. Atribuicao errada e pior que
     ausencia de atribuicao.
  3. Nunca afirmar sucesso sem ter olhado. "Deve passar" nao e resultado.
  4. Nunca ajustar o teste para o conteudo passar. O teste e o contrato.
  5. Nunca marcar pendencia com marcador proibido na prosa de um volume.

O que este painel faz, e o que ele nao faz
------------------------------------------
Ele LE o contrato, LE o disco, roda os gates, monta briefing e materializa pasta
vazia. Ele NAO escreve secao, NAO inventa conteudo e NAO grava status. Escrever
e trabalho de um modelo com o briefing na mao; aprovar e trabalho do auditor.
"""


# --------------------------------------------------------------------------
# Laco interativo.
# --------------------------------------------------------------------------

_OPCOES = (
    ("1", "Ver o acervo (tabela dos 42, com filtro opcional)"),
    ("2", "Inspecionar um volume (secoes, auditoria, dependencias, fronteira)"),
    ("3", "Rodar os gates de um volume (1 estrutural, 2 executavel, 3 cross-refs)"),
    ("4", "Preparar a criacao de um volume (monta o briefing para um agente)"),
    ("5", "Materializar os volumes que faltam em disco (scaffold)"),
    ("6", "Exportar o site (gera mkdocs.yml)"),
    ("7", "Explicar a plataforma (o que e, os tres gates, a Definicao de PRONTO)"),
    ("0", "Sair"),
)


def texto_do_menu() -> str:
    linhas = [_regua(), "  O que voce quer fazer?", _regua()]
    for numero, rotulo in _OPCOES:
        linhas.append(f"  {numero}) {rotulo}")
    linhas.append(_regua())
    linhas.append("Digite o numero e Enter. Enter vazio reexibe o menu; 'q' ou 0 sai.")
    return "\n".join(linhas)


def _perguntar(pergunta: str) -> str:
    return input(f"{pergunta} ").strip()


def _pedir_volume(raiz: Path, ct: Contrato) -> str | None:
    """Pede um id de volume e valida contra o contrato. None = desistiu."""
    bruto = _perguntar("Numero do volume (2 digitos, ex.: 08; Enter cancela):")
    if not bruto:
        return None
    vol_id = normalizar_id(bruto)
    if vol_id not in ct.volumes:
        print(
            f"\nNao existe volume {vol_id} no contrato. Os ids validos vao de "
            f"{min(ct.volumes)} a {max(ct.volumes)}. Use a opcao 1 para ver a lista."
        )
        return None
    return vol_id


def _tela_acervo(raiz: Path, ct: Contrato) -> None:
    estados = levantar(raiz, ct)
    filtro = _perguntar(
        "Filtrar por status (PRONTO/RASCUNHO/REQUER_REVISAO/PENDENTE), por tipo\n"
        "(ENGINE/ARQUITETURA/PROCESSO/BIBLIOTECA/GOVERNANCA), ou Enter para tudo:"
    ).upper()
    if filtro:
        filtrados = [e for e in estados if filtro in (e.status, e.tipo)]
        if not filtrados:
            print(f"\nNenhum volume com status ou tipo {filtro!r}. Mostrando tudo.\n")
        else:
            estados = filtrados
    print()
    print(tabela(estados))
    print(
        "A coluna Secoes e presentes/esperadas, e 'esperadas' varia por tipo - "
        "comparar 12/18 com 12/17 e comparar coisas diferentes. Presente significa "
        "arquivo existe, nao arquivo bom."
    )


def _tela_briefing(raiz: Path, ct: Contrato) -> None:
    print(
        "\nO painel monta o briefing; QUEM ESCREVE O VOLUME E UM MODELO.\n"
        "Nada aqui e conteudo inventado: tudo sai do contrato, do disco e do ROADMAP.\n"
    )
    vol_id = _pedir_volume(raiz, ct)
    if vol_id is None:
        return
    b = briefing_de(raiz, vol_id, ct)
    texto = texto_do_briefing(b)
    print()
    print(texto)
    if b.pre_requisitos and any(st in (PENDENTE, "RASCUNHO") for _, _, st in b.pre_requisitos):
        print(
            "AVISO: ha pre-requisito de leitura que ainda nao esta pronto. Escrever "
            "agora tende a produzir secao citando contrato que nao existe."
        )
    resposta = _perguntar(
        f"\nGravar em {PASTA_BRIEFINGS}/VOL-{vol_id}-briefing.md? [s/N]"
    ).lower()
    if resposta not in ("s", "sim", "y"):
        print("Nao gravado. Copie o texto acima e cole no agente.")
        return
    destino = raiz / PASTA_BRIEFINGS / f"VOL-{vol_id}-briefing.md"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")
    print(f"Gravado: {destino}")
    print(
        "Briefing e artefato descartavel: e reproduzivel a qualquer momento pelo "
        f"contrato mais o ROADMAP, e por isso {PASTA_BRIEFINGS}/ esta no .gitignore."
    )


def _tela_gates(raiz: Path, ct: Contrato) -> None:
    vol_id = _pedir_volume(raiz, ct)
    if vol_id is None:
        return
    print(f"\nRodando os tres gates do volume {vol_id}. O gate 2 chama pytest e pode demorar.\n")
    print(texto_dos_gates(veredicto_dos_gates(raiz, vol_id, ct)))


def _tela_scaffold(raiz: Path, ct: Contrato) -> None:
    print(
        "\nscaffold cria NN-NOME/_VOLUME.yml para todo volume declarado que ainda nao "
        "tem. E idempotente: nunca reescreve yml existente, porque o yml acumula "
        "estado editado a mao (status, depende_de, escopo).\n"
    )
    criados = scaffold.criar_volumes(raiz, ct)
    if not criados:
        print("Nada a criar: todos os volumes do contrato ja estao materializados.")
        return
    print(f"Criados {len(criados)} volume(s): {', '.join(criados)}")
    print("Eles nascem em RASCUNHO com zero secao escrita - use a opcao 4 para o briefing.")


def _tela_exportar(raiz: Path, ct: Contrato) -> None:
    yaml = exportar.gerar_mkdocs(raiz, ct)
    paginas = yaml.count("      - ")
    print(f"\nGerado {raiz / exportar.ARQUIVO} com {paginas} pagina(s).")
    print(
        "A navegacao vem do DISCO, nao do contrato: volume declarado e nao "
        "materializado fica fora do site, porque item de menu sem pagina promete "
        "conteudo que nao existe."
    )
    print("Para validar o build tambem: python -m ferramentas.exportar")


def _laco_interativo(raiz: Path, ct: Contrato) -> int:
    """Menu numerado, tolerante a entrada invalida.

    Entrada invalida nunca encerra o painel nem levanta: reexibe o menu com uma
    mensagem dizendo o que era esperado. Quem esta descobrindo a plataforma erra
    a digitacao, e ser expulso do programa por isso ensina a nao usar o programa.
    """
    print(texto_do_resumo(raiz, ct))
    while True:
        print()
        print(texto_do_menu())
        escolha = _perguntar(">").lower()
        if escolha in ("0", "q", "sair", "quit", "exit"):
            print("Ate logo.")
            return 0
        if not escolha:
            continue
        acoes = {
            "1": _tela_acervo,
            "2": _inspecionar,
            "3": _tela_gates,
            "4": _tela_briefing,
            "5": _tela_scaffold,
            "6": _tela_exportar,
        }
        if escolha == "7":
            print()
            print(TEXTO_EXPLICACAO)
            continue
        acao = acoes.get(escolha)
        if acao is None:
            print(
                f"\nNao entendi {escolha!r}. Digite um numero de 0 a 7 do menu acima "
                "(ou 'q' para sair)."
            )
            continue
        try:
            acao(raiz, ct)
        except ContratoInvalido as erro:
            print(f"\nerro de contrato: {erro}")
        except OSError as erro:
            print(f"\nerro de disco: {erro}")


def _inspecionar(raiz: Path, ct: Contrato) -> None:
    vol_id = _pedir_volume(raiz, ct)
    if vol_id is None:
        return
    print()
    print(texto_da_inspecao(raiz, vol_id, ct))


def _ajustar_stdout() -> None:
    """Evita UnicodeEncodeError ao imprimir trecho acentuado do ROADMAP.

    O terminal alvo e o Windows, onde o console pode estar em codepage que nao
    cobre travessao ou aspa curva. O painel prefere imprimir com caractere de
    substituicao a morrer no meio de um relatorio.
    """
    for fluxo in (sys.stdout, sys.stderr):
        reconfigurar = getattr(fluxo, "reconfigure", None)
        if reconfigurar is None:
            continue
        try:
            reconfigurar(errors="replace")
        except (ValueError, OSError):
            pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="painel",
        description="Interface de uso da AI-ENGINEERING-OS (interativa por padrao)",
    )
    parser.add_argument("--raiz", default=".", help="raiz da plataforma (default: .)")
    parser.add_argument(
        "--resumo", action="store_true", help="imprime o resumo do acervo e sai"
    )
    parser.add_argument("--briefing", metavar="NN", help="imprime o briefing do volume e sai")
    parser.add_argument(
        "--gates", metavar="NN", help="roda os tres gates do volume; exit 1 se algum reprovar"
    )
    args = parser.parse_args(argv)

    _ajustar_stdout()
    raiz = Path(args.raiz).resolve()
    try:
        ct = carregar(raiz)
    except ContratoInvalido as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 2

    try:
        if args.resumo:
            print(texto_do_resumo(raiz, ct))
            return 0
        if args.briefing:
            print(texto_do_briefing(briefing_de(raiz, args.briefing, ct)))
            return 0
        if args.gates:
            vereditos = veredicto_dos_gates(raiz, normalizar_id(args.gates), ct)
            print(texto_dos_gates(vereditos))
            return 0 if all(v.aprovado for v in vereditos) else 1
    except ContratoInvalido as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 2

    try:
        return _laco_interativo(raiz, ct)
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C e fim de entrada saem limpos. Traceback de KeyboardInterrupt
        # parece defeito do programa para quem so queria fechar a tela.
        print("\nAte logo.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
