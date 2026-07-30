"""Interface web local da AI-ENGINEERING-OS: a mesma maquina, com botao.

Por que existe: `ferramentas/painel.py` ja e a interface de uso da plataforma, mas
ela e de console e exige que a pessoa saiba que existe um comando, digite o
comando e leia a saida em texto. Quem chega perguntando "cade a interface e como
se usa" quer uma tela para clicar. Este modulo serve exatamente essa tela - e
nada mais.

Tres decisoes de fundo:

1. **Nenhuma regra e reimplementada aqui.** Resumo, briefing, veredicto dos
   gates, secoes ausentes e fronteira de escopo saem de `painel.py`, que por sua
   vez le `contrato.json`. Esta camada so traduz dataclass em JSON e JSON em HTML.
   Regra duplicada em camada de apresentacao e como a interface passa a mentir
   sobre o motor.
2. **O roteamento e uma funcao pura.** `responder()` recebe metodo, caminho, raiz
   e contrato e devolve `(status, content_type, corpo)`. O handler de
   `http.server` e um adaptador fino em cima dela, e os testes chamam `responder`
   direto - sem abrir socket, sem depender de porta livre, sem navegador.
3. **Este servidor executa processo, e por isso ele e tratado como executor.**
   O gate 2 roda `pytest` em subprocesso. Um endpoint que dispara processo nao
   pode ser exposto na rede: o bind e estritamente `127.0.0.1` (ver `HOST`), o id
   de volume e validado contra o contrato antes de qualquer toque em disco, e
   nenhum caminho de arquivo vem da requisicao.
4. **A tela de descoberta guarda estado, e estado guardado tem teto.** `/descoberta`
   mantem entrevistas em memoria do processo, com id de `secrets.token_urlsafe` e
   um teto de sessoes simultaneas (ver `TETO_DE_SESSOES`). Id sequencial deixaria
   outra aba adivinhar a entrevista alheia; dicionario sem teto deixaria um cliente
   em laco consumir memoria sem limite. O motor da entrevista continua vivendo em
   `exemplos/03-discovery/` - aqui nao ha nenhuma pergunta, nenhum peso e nenhuma
   regra de completude reimplementada.

Uso:
    python -m ferramentas.web                      # sobe e abre o navegador
    python -m ferramentas.web --porta 8765
    python -m ferramentas.web --sem-navegador
    python -m ferramentas.web --raiz <outro acervo>

A raiz da plataforma sai de `__file__`, nao do diretorio atual (ver `raiz_padrao`):
o servidor sobe igual lancado de dentro de `AI-ENGINEERING-OS/` ou da raiz do
repositorio.
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import secrets
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, NamedTuple

from . import painel as P
from .contrato import Contrato, ContratoInvalido, carregar
from .instalar_skills import raiz_da_plataforma
from .status import levantar, nota_da_ultima_auditoria, relatorio_mais_recente

# Bind estritamente em loopback, NUNCA em "0.0.0.0" nem no IP da maquina.
# Motivo: `POST /api/gates/NN` roda `pytest` em subprocesso. Um servidor que
# dispara processo local e, para qualquer host que o alcance, um executor remoto
# sem autenticacao. Em `127.0.0.1` o unico alcance possivel e esta maquina, e a
# plataforma nao tem nenhum caso de uso que exija outra maquina - a interface e
# para quem esta sentado no computador que tem o acervo em disco.
HOST = "127.0.0.1"
PORTA_PADRAO = 8765
TENTATIVAS_DE_PORTA = 20

JSON_UTF8 = "application/json; charset=utf-8"
HTML_UTF8 = "text/html; charset=utf-8"
TEXTO_UTF8 = "text/plain; charset=utf-8"

# Id de volume tem exatamente dois digitos. `7` nao e aceito de proposito nesta
# borda: o painel normaliza para quem digita no terminal, mas a URL e endereco de
# maquina, e endereco com duas formas para o mesmo recurso e ambiguidade que
# depois vira cache errado e log confuso.
_ID_DE_VOLUME = re.compile(r"^\d{2}$")

COMANDO_DA_SUITE = "python -m pytest ferramentas/tests exemplos -q"

# Limite do corpo de POST que o handler aceita ler do socket. Acima disso ele
# responde 413 e fecha a conexao em vez de continuar lendo: corpo sem teto e
# memoria do servidor entregue a quem souber o endereco.
_LIMITE_DE_CORPO = 64 * 1024


class IdRecusado(ValueError):
    """Id de volume que nao passa na validacao contra o contrato."""


def raiz_padrao() -> Path:
    """A pasta da plataforma, deduzida de `__file__` - nunca do diretorio atual.

    O servidor nao pode depender de onde foi lancado. Quem sobe esta interface
    pelo mecanismo de preview do harness lanca o processo da raiz do repositorio
    (`CLAUDE/`), nao de dentro de `AI-ENGINEERING-OS/`; com raiz igual a `.` o
    arranque morreria com "contrato ausente" por um detalhe de cwd, e a mensagem
    culparia o contrato em vez do diretorio de onde o processo subiu.

    `--raiz` continua existindo para apontar para outro acervo de proposito.
    """
    return raiz_da_plataforma()


# --------------------------------------------------------------------------
# Validacao de entrada. E o unico lugar por onde dado de requisicao entra.
# --------------------------------------------------------------------------


def validar_id(bruto: str, ct: Contrato) -> str:
    """Devolve o id se ele existir no contrato; levanta `IdRecusado` se nao.

    Duas checagens, nesta ordem, e as duas importam:

    - forma (`^\\d{2}$`): recusa `..`, `07/../..`, `%2e%2e`, id vazio e id com
      letra sem nunca tocar o disco;
    - existencia em `ct.volumes`: recusa `99`, que tem forma valida e nao e
      volume. Sem esta segunda checagem, `ct.volume("99")` levantaria
      `ContratoInvalido` la dentro e a resposta viraria erro 500 - erro de
      servidor para o que e erro de quem pediu.
    """
    bruto = str(bruto)
    if not _ID_DE_VOLUME.match(bruto):
        raise IdRecusado(
            f"id de volume invalido: {bruto!r}. Use exatamente dois digitos, "
            "como 07 ou 36."
        )
    if bruto not in ct.volumes:
        primeiro, ultimo = min(ct.volumes), max(ct.volumes)
        raise IdRecusado(
            f"nao existe volume {bruto} no contrato. Os ids declarados vao de "
            f"{primeiro} a {ultimo} - abra a grade da pagina para ver a lista."
        )
    return bruto


# --------------------------------------------------------------------------
# Dados. Cada funcao devolve dict pronto para `json.dumps`.
# --------------------------------------------------------------------------


def contagem_de_testes(raiz: Path) -> dict[str, object]:
    """Quantas funcoes de teste existem em disco - e o aviso de que isso nao e verde.

    A contagem e estatica (`def test_` em `test_*.py`). Ela NAO afirma que a
    suite passa: `parametrize` gera mais casos do que funcoes, e arquivo em disco
    nao e execucao. A proibicao 3 da plataforma - nunca afirmar sucesso sem ter
    olhado - vale para a propria interface, entao o campo `verificado` sai
    sempre `False` e a pagina mostra o comando que produz o veredicto de verdade.
    """
    total = 0
    arquivos = 0
    for base in ("ferramentas/tests", "exemplos"):
        pasta = raiz / base
        if not pasta.is_dir():
            continue
        for arq in sorted(pasta.rglob("test_*.py")):
            arquivos += 1
            texto = arq.read_text(encoding="utf-8", errors="replace")
            total += len(re.findall(r"^\s*def test_", texto, re.MULTILINE))
    return {
        "funcoes_de_teste": total,
        "arquivos": arquivos,
        "verificado": False,
        "comando": COMANDO_DA_SUITE,
        "observacao": (
            "contagem estatica de funcoes `def test_` em disco. Nao e afirmacao de "
            "que a suite passa: rode o comando para ter o veredicto."
        ),
    }


def _estado_para_dict(e) -> dict[str, object]:
    return {
        "id": e.vol_id,
        "nome": e.nome,
        "tipo": e.tipo,
        "status": e.status,
        "secoes_presentes": e.secoes_presentes,
        "secoes_esperadas": e.secoes_esperadas,
        "nota": e.nota_auditoria,
        "perecivel": e.perecivel,
    }


def dados_do_acervo(raiz: Path, ct: Contrato) -> dict[str, object]:
    """Os 42 volumes, a contagem por status e a proxima acao recomendada."""
    resumo = P.resumo_do_acervo(raiz, ct)
    return {
        "total": resumo.total,
        "contagem": resumo.contagem,
        "proxima_acao": resumo.proxima_acao,
        "mais_avancado": (
            _estado_para_dict(resumo.mais_avancado)
            if resumo.mais_avancado is not None
            else None
        ),
        "testes": contagem_de_testes(raiz),
        "volumes": [_estado_para_dict(e) for e in levantar(raiz, ct)],
    }


def dados_do_volume(raiz: Path, vol_id: str, ct: Contrato) -> dict[str, object]:
    """Ficha do volume: o que tem, o que FALTA, auditoria, deps e fronteira."""
    b = P.briefing_de(raiz, vol_id, ct)
    ausentes = list(b.secoes_ausentes)
    presentes = [s for s in b.secoes_obrigatorias if s not in b.secoes_ausentes]
    relatorio = relatorio_mais_recente(raiz, vol_id)
    return {
        "id": b.vol_id,
        "nome": b.nome,
        "tipo": b.tipo,
        "status": b.status,
        "perecivel": b.perecivel,
        "secoes_esperadas": len(b.secoes_obrigatorias),
        "secoes_presentes": presentes,
        "secoes_ausentes": ausentes,
        "minimos": dict(b.minimos),
        "diagramas_obrigatorios": list(b.diagramas_obrigatorios),
        "escopo": b.escopo,
        "depende_de": list(b.depende_de),
        "pre_requisitos": [
            {"id": dep_id, "nome": dep_nome, "status": dep_status}
            for dep_id, dep_nome, dep_status in b.pre_requisitos
        ],
        "auditoria": {
            "relatorio": relatorio.name if relatorio is not None else None,
            "nota": nota_da_ultima_auditoria(raiz, vol_id),
        },
        "fronteira": (
            None
            if b.fronteira is None
            else {
                "titulo": b.fronteira.titulo,
                "volumes": list(b.fronteira.volumes),
                "texto": b.fronteira.texto,
            }
        ),
        "pasta_exemplos": b.pasta_exemplos,
    }


def dados_do_briefing(raiz: Path, vol_id: str, ct: Contrato) -> dict[str, object]:
    """O briefing completo em Markdown, do jeito que ele vai para um agente."""
    b = P.briefing_de(raiz, vol_id, ct)
    return {"volume": b.vol_id, "nome": b.nome, "markdown": P.texto_do_briefing(b)}


_ANSI = re.compile(r"\[[0-9;]*[A-Za-z]")


def _sem_ansi(texto: str) -> str:
    """Remove sequencias de escape ANSI de saida capturada de subprocesso.

    O pytest colore quando acha que escreve num terminal. A pagina mostra
    esse texto como conteudo, e ali um \x1b[32m aparece literal. Limpar na
    apresentacao, e nao no motor, preserva a cor no painel de console.
    """
    return _ANSI.sub('', texto)


def _veredicto_para_dict(v) -> dict[str, object]:
    grupos = P.agrupar_por_regra(v.violacoes)
    return {
        "gate": v.gate,
        "nome": v.nome,
        "aprovado": v.aprovado,
        "detalhe": _sem_ansi(v.detalhe),
        "violacoes": len(v.violacoes),
        "violacoes_por_regra": [
            {
                "regra": regra,
                "quantidade": len(itens),
                "itens": [
                    {"arquivo": i.arquivo, "linha": i.linha, "mensagem": i.mensagem}
                    for i in itens[:5]
                ],
                "omitidas": max(0, len(itens) - 5),
            }
            for regra, itens in grupos.items()
        ],
    }


def dados_dos_gates(
    raiz: Path, vol_id: str, ct: Contrato, *, rodar_testes: bool = True
) -> dict[str, object]:
    """Os tres veredictos, com as violacoes agrupadas por regra."""
    vereditos = P.veredicto_dos_gates(raiz, vol_id, ct, rodar_testes=rodar_testes)
    return {
        "volume": vol_id,
        "aprovado": all(v.aprovado for v in vereditos),
        "gates": [_veredicto_para_dict(v) for v in vereditos],
    }


# --------------------------------------------------------------------------
# Descoberta. O motor e o do volume 03; aqui so ha estado de sessao e traducao.
# --------------------------------------------------------------------------

# Teto de entrevistas simultaneas em memoria. Ao estourar, a mais antiga e
# descartada. Sem teto, um cliente em laco chamando `iniciar` acumula uma
# `Entrevista` por chamada e o processo cresce ate o sistema reclamar - e este
# servidor nao tem quem o reinicie, ele e uma janela de terminal que a pessoa
# deixa aberta. Trinta e duas e generoso para uso humano (uma pessoa, algumas
# abas) e barato de manter.
TETO_DE_SESSOES = 32

# Teto da ideia em caracteres. O texto entra no motor de deteccao, que percorre
# cinquenta termos sobre o texto dobrado - custo linear, mas linear sobre um
# megabyte colado de qualquer lugar ja e CPU do servidor gasta por conta de um
# clique. Quatro mil caracteres e mais do que qualquer ideia inicial honesta.
LIMITE_DA_IDEIA = 4000
LIMITE_DA_RESPOSTA = 2000
LIMITE_DO_ID_DE_SESSAO = 128

# Teto do corpo JSON que as rotas de descoberta aceitam interpretar. Menor que
# `_LIMITE_DE_CORPO` de proposito: o handler para de ler em 64 KiB, e a regra
# recusa antes de `json.loads` qualquer coisa acima de 16 KiB.
LIMITE_DE_CORPO_JSON = 16 * 1024


class DescobertaRecusada(ValueError):
    """Entrada de requisicao que a tela de descoberta recusa, com o que fazer.

    Vira `400` em `responder`. Toda mensagem termina dizendo a acao seguinte:
    erro que so descreve o problema deixa a pessoa olhando a tela sem saber se o
    proximo passo e corrigir o texto, escolher outra opcao ou recarregar.
    """


class MotorAusente(RuntimeError):
    """`exemplos/03-discovery/` nao esta em disco, e sem ela nao existe entrevista."""


class Motor(NamedTuple):
    """Os quatro modulos do volume 03, carregados uma vez.

    Tupla nomeada em vez de quatro globais: o carregamento e um passo so, e ou os
    quatro estao disponiveis ou nenhum esta. Estado parcial aqui daria erro de
    atributo no meio de uma entrevista em vez de erro de arranque.
    """

    catalogo: Any
    deteccao: Any
    entrevista: Any
    especificacao: Any


_MOTOR: Motor | None = None


def motor_de_descoberta() -> Motor:
    """Carrega (uma vez) os quatro modulos de `exemplos/03-discovery/`.

    Tres decisoes que valem registro:

    - **A pasta sai de `raiz_da_plataforma()`, nunca da requisicao nem de `--raiz`.**
      O motor e codigo, e codigo que este servidor importa nao pode ser escolhido
      por quem faz a chamada. `--raiz` aponta para outro *acervo* - outro conjunto
      de volumes em Markdown - e deixar `--raiz` decidir o que se importa seria
      transformar um parametro de leitura em carregamento de codigo arbitrario.
    - **`sys.path.append`, e no fim da lista.** Os quatro modulos se importam pelo
      nome-base (`from catalogo import ...`), como o `conftest.py` do exemplo
      documenta, e por isso a pasta precisa estar no caminho de import. Anexar no
      fim em vez de inserir no comeco evita que `catalogo` daqui passe a sombrear
      um modulo homonimo de qualquer outra origem.
    - **Uma vez.** A tabela de termos e o catalogo sao imutaveis; recarregar a cada
      requisicao pagaria parse de novo para obter o mesmo objeto.
    """
    global _MOTOR
    if _MOTOR is not None:
        return _MOTOR
    pasta = raiz_da_plataforma() / "exemplos" / "03-discovery"
    if not (pasta / "catalogo.py").is_file():
        raise MotorAusente(
            f"nao encontrei o motor de descoberta em {pasta}. A tela /descoberta "
            "depende de exemplos/03-discovery/ estar em disco - confirme que o "
            "acervo desta plataforma esta completo e suba o servidor de novo."
        )
    caminho = str(pasta)
    if caminho not in sys.path:
        sys.path.append(caminho)
    _MOTOR = Motor(
        catalogo=importlib.import_module("catalogo"),
        deteccao=importlib.import_module("deteccao"),
        entrevista=importlib.import_module("entrevista"),
        especificacao=importlib.import_module("especificacao"),
    )
    return _MOTOR


def plataformas_do_catalogo() -> tuple[str, ...]:
    """Os nomes das plataformas, na ordem em que o catalogo as declara.

    Lidos da enumeracao do motor e nao escritos aqui: o seletor da tela oferece
    exatamente o que o catalogo conhece, e uma quinta plataforma no volume 03
    aparece na tela sem ninguem editar esta camada.
    """
    return tuple(str(p) for p in motor_de_descoberta().catalogo.Plataforma)


class RegistroDeSessoes:
    """As entrevistas vivas, com id imprevisivel e teto de quantidade.

    Nao ha persistencia, e a ausencia dela e desenho: entrevista e conversa em
    andamento, e gravar conversa em disco criaria um arquivo com texto de terceiro
    que ninguem pediu para guardar. Fechar o servidor descarta tudo, e a tela diz
    isso antes de a pessoa comecar.
    """

    def __init__(self, teto: int = TETO_DE_SESSOES) -> None:
        self._teto = max(1, int(teto))
        # `dict` preserva ordem de insercao, e e ela que define quem e "a mais
        # antiga" quando o teto estoura. Nao ha relogio envolvido de proposito:
        # ordem de chegada nao depende do fuso nem de ajuste de hora.
        self._sessoes: dict[str, Any] = {}

    @property
    def teto(self) -> int:
        return self._teto

    def __len__(self) -> int:
        return len(self._sessoes)

    def ids(self) -> tuple[str, ...]:
        """Os ids vivos, do mais antigo para o mais novo."""
        return tuple(self._sessoes)

    def criar(self, entrevista: Any) -> str:
        """Guarda a entrevista sob um id novo e devolve o id.

        O id vem de `secrets.token_urlsafe`, nunca de um contador. Id sequencial
        e adivinhavel: qualquer pagina aberta no navegador que alcance
        `127.0.0.1` poderia pedir a especificacao da sessao 1 e ler a entrevista
        de outra pessoa nesta mesma maquina. Aqui o id **e** a credencial, e por
        isso ele tem de ser imprevisivel.
        """
        while len(self._sessoes) >= self._teto:
            self._sessoes.pop(next(iter(self._sessoes)))
        chave = secrets.token_urlsafe(24)
        self._sessoes[chave] = entrevista
        return chave

    def obter(self, bruto: object) -> Any:
        """A entrevista desse id, ou `DescobertaRecusada` dizendo o que fazer.

        O id nao volta na mensagem de erro. Mensagem que ecoa a entrada devolve
        texto de terceiro para dentro da pagina, e nao ha nada a ganhar com isso:
        quem digitou o id nao precisa de confirmacao de que digitou.
        """
        if not isinstance(bruto, str) or not bruto or len(bruto) > LIMITE_DO_ID_DE_SESSAO:
            raise DescobertaRecusada(
                "id de entrevista ausente ou fora do formato. Recarregue /descoberta "
                "e comece uma entrevista nova."
            )
        entrevista = self._sessoes.get(bruto)
        if entrevista is None:
            raise DescobertaRecusada(
                "esta entrevista nao esta mais na memoria do servidor. Ou ela caiu "
                f"pelo teto de {self._teto} entrevistas simultaneas, ou o servidor "
                "foi reiniciado. Recarregue /descoberta e comece de novo."
            )
        return entrevista

    def limpar(self) -> None:
        """Descarta tudo. Usado pelos testes para nao herdar estado de outro teste."""
        self._sessoes.clear()


# Registro do processo. `responder` aceita outro por parametro para que o teste do
# teto possa usar um registro pequeno sem mexer no do servidor.
SESSOES = RegistroDeSessoes()


# --- Leitura do corpo da requisicao. Unica porta de entrada de dado de POST.


def _corpo_json(corpo: bytes | None) -> dict[str, Any]:
    """Interpreta o corpo como objeto JSON, ou recusa dizendo o que fazer."""
    dados = corpo or b""
    if len(dados) > LIMITE_DE_CORPO_JSON:
        raise DescobertaRecusada(
            f"corpo de {len(dados)} bytes acima do limite de {LIMITE_DE_CORPO_JSON}. "
            "Encurte a ideia e envie de novo."
        )
    if not dados.strip():
        raise DescobertaRecusada(
            "a requisicao chegou sem corpo. Recarregue /descoberta e use os botoes "
            "da propria tela."
        )
    try:
        dado = json.loads(dados.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise DescobertaRecusada(
            "corpo da requisicao nao e JSON valido em UTF-8. Recarregue /descoberta "
            "e tente de novo pela propria tela."
        ) from None
    if not isinstance(dado, dict):
        raise DescobertaRecusada(
            "corpo da requisicao precisa ser um objeto JSON. Recarregue /descoberta "
            "e use os botoes da propria tela."
        )
    return dado


def _texto(dado: dict[str, Any], chave: str, limite: int, como_resolver: str) -> str:
    """Le um campo de texto do corpo, com teto de tamanho e mensagem de conserto."""
    valor = dado.get(chave)
    if not isinstance(valor, str):
        raise DescobertaRecusada(f"campo {chave!r} ausente ou nao textual. {como_resolver}")
    if len(valor) > limite:
        raise DescobertaRecusada(
            f"campo {chave!r} tem {len(valor)} caracteres, acima do limite de "
            f"{limite}. {como_resolver}"
        )
    return valor


# --- Traducao para JSON. Nenhuma regra do motor e recalculada aqui.


def _lacuna_para_dict(lacuna: Any) -> dict[str, Any]:
    return {
        "id": lacuna.id,
        "pergunta": lacuna.pergunta,
        "porque": lacuna.porque,
        "peso": lacuna.peso,
        "universal": lacuna.universal,
        "opcoes": list(lacuna.opcoes),
    }


def _palpite_para_dict(palpite: Any) -> dict[str, Any]:
    return {
        "valor": str(palpite.valor),
        "origem": str(palpite.origem),
        "evidencia": palpite.evidencia,
        "confianca": str(palpite.confianca),
    }


def _progresso_para_dict(entrevista: Any) -> dict[str, Any]:
    """`progresso()` do motor, com o aviso de que o denominador pode subir.

    O motor devolve `(respondidas, alvo)` e o `alvo` **cresce** quando uma
    confirmacao destrava um bloco novo de lacunas. A tela nao pode esconder isso
    atras de uma barra que so avanca: barra que so avanca precisa de um total
    conhecido desde o inicio, e num grafo de decisao ele nao e conhecido. Por isso
    o total viaja com o aviso, e nao sozinho.
    """
    respondidas, total = entrevista.progresso()
    pendentes_de_palpite = len(entrevista.palpites_pendentes())
    return {
        "respondidas": respondidas,
        "total": total,
        "total_pode_crescer": pendentes_de_palpite > 0,
        "observacao": (
            "o total nao e fixo: cada confirmacao de contexto pode destravar "
            "perguntas novas e aumentar o denominador. Total que so cai seria total "
            "inventado no inicio."
        ),
    }


def estado_da_entrevista(chave: str, entrevista: Any) -> dict[str, Any]:
    """O retrato que as tres rotas de POST devolvem: pergunta, palpites, progresso."""
    proxima = entrevista.proxima()
    return {
        "sessao": chave,
        "ideia": entrevista.ideia,
        "plataformas": [str(p) for p in entrevista.plataformas()],
        "contextos": [str(c) for c in entrevista.contextos()],
        "pergunta": None if proxima is None else _lacuna_para_dict(proxima),
        "pendentes": [lacuna.id for lacuna in entrevista.pendentes()],
        "palpites": [_palpite_para_dict(p) for p in entrevista.palpites_pendentes()],
        "respostas": [
            {"lacuna_id": chave_da_lacuna, "valor": valor, "origem": str(origem)}
            for chave_da_lacuna, valor, origem in entrevista.respostas()
        ],
        "progresso": _progresso_para_dict(entrevista),
    }


# --- As quatro operacoes da tela.


def iniciar_descoberta(dado: dict[str, Any], sessoes: RegistroDeSessoes) -> dict[str, Any]:
    """Abre uma entrevista com a ideia escrita e a plataforma **escolhida**.

    Por que a plataforma vem de um seletor e nao da inferencia. A inferencia de
    plataforma e a mais consequente do motor: a plataforma e a unica lacuna
    universal cuja resposta muda *quais outras lacunas existem*, e o volume 03
    mede o custo de aceitar um palpite errado - um palpite de aparelho de mao
    aceito por engano produz sete perguntas inuteis em quinze. Um seletor visivel
    com as quatro opcoes do catalogo resolve essa lacuna com custo zero para quem
    usa (um clique, antes de escrever) e sem risco nenhum: nao ha palpite para
    errar quando a pessoa aponta.

    Consequencia no motor, e ela e deliberada: a plataforma entra por
    `Entrevista.responder("onde_roda", ...)`, com origem `RESPONDIDO`, e nao como
    `Palpite` a confirmar. E os palpites de plataforma que a deteccao tiver
    produzido do texto sao removidos com `recusar`. Isso **nao** e rejeitar a
    inferencia por engano: `recusar` e o unico metodo que tira o palpite da
    pendencia sem aplicar nada, e aplicar e exatamente o que `responder` faz na
    linha seguinte - com a origem mais forte. O que sobra e o estado correto: a
    plataforma consta como dita por uma pessoa, e nao como suposicao pendente.

    Palpite de **contexto** nao e tocado. Loja, saude, dado pessoal e companhia
    continuam pendentes e exigindo confirmacao explicita, com a evidencia a vista
    (regra R1 do volume 03: confianca alta nao dispensa confirmacao).
    """
    motor = motor_de_descoberta()
    ideia = _texto(
        dado,
        "ideia",
        LIMITE_DA_IDEIA,
        f"Escreva a ideia em no maximo {LIMITE_DA_IDEIA} caracteres e envie de novo.",
    )
    if not ideia.strip():
        raise DescobertaRecusada(
            "a ideia esta em branco. Escreva uma ou duas frases sobre o que precisa "
            "existir, ou clique num dos exemplos da tela para preencher o campo."
        )
    nomes = tuple(str(p) for p in motor.catalogo.Plataforma)
    bruto = _texto(dado, "plataforma", 32, "Escolha uma das opcoes do seletor da tela.")
    plataforma = bruto.strip().upper()
    if plataforma not in nomes:
        raise DescobertaRecusada(
            f"plataforma nao reconhecida. Escolha uma destas no seletor acima do "
            f"campo de ideia: {', '.join(nomes)}."
        )

    entrevista = motor.entrevista.Entrevista(ideia)
    descartados = [
        _palpite_para_dict(palpite)
        for palpite in entrevista.palpites_pendentes()
        if str(palpite.valor) in nomes
    ]
    for palpite in entrevista.palpites_pendentes():
        if str(palpite.valor) in nomes:
            entrevista.recusar(palpite)
    entrevista.responder("onde_roda", plataforma)

    chave = sessoes.criar(entrevista)
    retrato = estado_da_entrevista(chave, entrevista)
    retrato["plataforma_escolhida"] = plataforma
    # Palpite de plataforma que o texto produzia e o seletor substituiu. Vai para a
    # tela porque a pessoa merece ver o desencontro: "li 'celular' aqui, mas voce
    # escolheu navegador" e informacao, e esconder isso faria a escolha parecer
    # ignorada em vez de respeitada.
    retrato["plataforma_inferida_descartada"] = descartados
    return retrato


def responder_lacuna(dado: dict[str, Any], sessoes: RegistroDeSessoes) -> dict[str, Any]:
    """Grava a resposta de uma lacuna e devolve a proxima pergunta e o progresso."""
    motor = motor_de_descoberta()
    chave = _texto(
        dado, "sessao", LIMITE_DO_ID_DE_SESSAO, "Recarregue /descoberta e comece de novo."
    )
    entrevista = sessoes.obter(chave)
    lacuna_id = _texto(
        dado, "lacuna_id", 64, "Recarregue /descoberta para pegar a pergunta atual."
    ).strip()
    # Validacao contra o catalogo ANTES de qualquer uso, no mesmo espirito do
    # `validar_id` dos volumes: id desconhecido levanta `LacunaDesconhecida` la
    # dentro, e excecao de motor virando 500 seria erro de servidor para o que e
    # erro de quem pediu.
    conhecidos = {lacuna.id for lacuna in motor.catalogo.CATALOGO}
    if lacuna_id not in conhecidos:
        raise DescobertaRecusada(
            "essa pergunta nao existe no catalogo de lacunas. Recarregue /descoberta "
            "e responda a pergunta que a tela mostrar."
        )
    valor = _texto(
        dado,
        "valor",
        LIMITE_DA_RESPOSTA,
        f"Responda em no maximo {LIMITE_DA_RESPOSTA} caracteres.",
    )
    if not valor.strip():
        raise DescobertaRecusada(
            "a resposta esta em branco. Escreva a resposta no campo, ou clique numa "
            "das opcoes oferecidas."
        )
    try:
        entrevista.responder(lacuna_id, valor)
    except motor.entrevista.LacunaDesconhecida:
        raise DescobertaRecusada(
            "essa pergunta nao existe no catalogo de lacunas. Recarregue /descoberta "
            "e responda a pergunta que a tela mostrar."
        ) from None
    return estado_da_entrevista(chave, entrevista)


def resolver_palpite(dado: dict[str, Any], sessoes: RegistroDeSessoes) -> dict[str, Any]:
    """Confirma ou recusa um palpite de contexto - e recusar e um clique.

    `aceitar` e booleano obrigatorio, sem padrao. Padrao aqui seria decidir por
    omissao justamente na operacao cuja razao de existir e nao decidir por
    omissao: a regra R1 do volume 03 diz que inferencia nao entra sem alguem
    dizer que sim, e um `aceitar` ausente interpretado como `True` seria a
    violacao com cara de conveniencia.
    """
    chave = _texto(
        dado, "sessao", LIMITE_DO_ID_DE_SESSAO, "Recarregue /descoberta e comece de novo."
    )
    entrevista = sessoes.obter(chave)
    valor = _texto(
        dado, "valor", 64, "Use os botoes de confirmar ou recusar da propria tela."
    ).strip().upper()
    aceitar = dado.get("aceitar")
    if not isinstance(aceitar, bool):
        raise DescobertaRecusada(
            "campo 'aceitar' precisa ser true (o palpite esta certo) ou false (nao e "
            "o caso). Use os dois botoes da tela em vez de montar a chamada a mao."
        )
    alvo = next(
        (p for p in entrevista.palpites_pendentes() if str(p.valor) == valor), None
    )
    if alvo is None:
        raise DescobertaRecusada(
            "esse palpite nao esta mais pendente nesta entrevista - ele ja foi "
            "confirmado ou recusado. Recarregue /descoberta para ver o estado atual."
        )
    if aceitar:
        entrevista.confirmar(alvo)
    else:
        entrevista.recusar(alvo)
    return estado_da_entrevista(chave, entrevista)


def especificacao_da_sessao(chave: str, sessoes: RegistroDeSessoes) -> dict[str, Any]:
    """A especificacao atual em markdown, com `completa` e as duas listas.

    `por_que_nao_completa` nao e recalculo da regra: as duas condicoes de
    `Especificacao.completa` sao lidas do proprio objeto (`inferencias_pendentes` e
    lacuna universal em `decisoes_abertas`), e a lista existe para a tela poder
    dizer o motivo em vez de mostrar um rotulo vermelho sem explicacao. Se o motor
    mudar a regra, `completa` muda com ele e esta lista pode ficar vazia num caso
    incompleto - por isso a tela obedece a `completa` e usa a lista apenas como
    texto de apoio.
    """
    motor = motor_de_descoberta()
    entrevista = sessoes.obter(chave)
    spec = motor.especificacao.gerar(entrevista)
    universais_abertas = [lacuna for lacuna in spec.decisoes_abertas if lacuna.universal]
    motivos: list[str] = []
    if spec.inferencias_pendentes:
        quais = ", ".join(str(p.valor) for p in spec.inferencias_pendentes)
        motivos.append(
            f"{len(spec.inferencias_pendentes)} palpite(s) de contexto sem resposta "
            f"({quais}). Enquanto ninguem confirmar nem recusar, isso e coisa que o "
            "programa supos e nenhuma pessoa afirmou."
        )
    if universais_abertas:
        quais = ", ".join(lacuna.id for lacuna in universais_abertas)
        motivos.append(
            f"{len(universais_abertas)} pergunta(s) que valem para qualquer software "
            f"seguem sem resposta ({quais}). Nao existe caso em que elas sejam "
            "dispensaveis."
        )
    return {
        "sessao": chave,
        "ideia": entrevista.ideia,
        "completa": spec.completa,
        "por_que_nao_completa": motivos,
        "markdown": spec.markdown(),
        "plataformas": [str(p) for p in spec.plataformas],
        "contextos": [str(c) for c in spec.contextos],
        "respostas": [
            {"lacuna_id": chave_da_lacuna, "valor": valor, "origem": str(origem)}
            for chave_da_lacuna, valor, origem in spec.respostas
        ],
        "decisoes_abertas": [_lacuna_para_dict(lacuna) for lacuna in spec.decisoes_abertas],
        "inferencias_pendentes": [
            _palpite_para_dict(p) for p in spec.inferencias_pendentes
        ],
    }


# --------------------------------------------------------------------------
# Roteamento. Funcao pura: e ela que os testes exercitam.
# --------------------------------------------------------------------------


def _json(status: int, dado: object) -> tuple[int, str, bytes]:
    corpo = json.dumps(dado, ensure_ascii=False, indent=2).encode("utf-8")
    return status, JSON_UTF8, corpo


def _erro(status: int, mensagem: str) -> tuple[int, str, bytes]:
    return _json(status, {"erro": mensagem})


def normalizar_caminho(caminho: str) -> str:
    """Descarta query e fragmento e normaliza a barra final.

    Nao ha nada de util em query string nesta interface, e aceitar parametro que
    ninguem le e superficie a mais. `/api/volume/07?x=1` e `/api/volume/07/` sao
    o mesmo recurso que `/api/volume/07`.
    """
    caminho = (caminho or "").split("?", 1)[0].split("#", 1)[0]
    if not caminho.startswith("/"):
        caminho = "/" + caminho
    if len(caminho) > 1:
        caminho = caminho.rstrip("/") or "/"
    return caminho


# Rotas declaradas. Qualquer coisa fora desta tabela e 404; metodo fora do que a
# rota declara e 405. Nao existe rota que receba caminho de arquivo: os caminhos
# saem todos do contrato, dentro de `painel.py`.
_ROTAS_EXATAS: dict[str, tuple[str, ...]] = {
    "/": ("GET",),
    "/descoberta": ("GET",),
    "/api/acervo": ("GET",),
    "/api/descoberta/iniciar": ("POST",),
    "/api/descoberta/responder": ("POST",),
    "/api/descoberta/palpite": ("POST",),
}
_ROTAS_COM_ID: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("/api/volume/", ("GET",)),
    ("/api/briefing/", ("GET",)),
    ("/api/gates/", ("POST",)),
)

# A especificacao e de UMA entrevista, e o id dela viaja no caminho - no mesmo
# formato de `/api/volume/NN`, e nao em query string. Duas razoes: `normalizar_caminho`
# descarta query de proposito (parametro que ninguem le e superficie a mais), e id de
# sessao e credencial - credencial em query string acaba em log de servidor, em
# historico do navegador e no cabecalho `Referer` da requisicao seguinte.
_PREFIXO_DA_ESPECIFICACAO = "/api/descoberta/especificacao/"


def responder(
    metodo: str,
    caminho: str,
    raiz: Path,
    ct: Contrato,
    *,
    rodar_testes: bool = True,
    corpo: bytes | None = None,
    sessoes: RegistroDeSessoes | None = None,
) -> tuple[int, str, bytes]:
    """Resolve uma requisicao e devolve `(status, content_type, corpo)`.

    Toda a decisao da interface esta aqui, e nada aqui depende de socket. E o que
    permite testar a interface inteira sem porta livre e sem navegador: o handler
    de `http.server` so converte esta tripla em resposta HTTP.

    `corpo` sao os bytes do POST, ja limitados pelo handler. `sessoes` e o registro
    de entrevistas: o padrao e o do processo, e o parametro existe para o teste do
    teto poder usar um registro pequeno sem tocar no estado do servidor.
    """
    metodo = (metodo or "").upper()
    caminho = normalizar_caminho(caminho)
    sessoes = SESSOES if sessoes is None else sessoes

    if caminho in _ROTAS_EXATAS:
        if metodo not in _ROTAS_EXATAS[caminho]:
            return _erro(
                405,
                f"metodo {metodo} nao vale em {caminho}. Use "
                f"{' ou '.join(_ROTAS_EXATAS[caminho])}.",
            )
        if caminho == "/":
            return 200, HTML_UTF8, PAGINA.encode("utf-8")
        if caminho == "/api/acervo":
            return _json(200, dados_do_acervo(raiz, ct))
        return _responder_descoberta(caminho, corpo, sessoes)

    if caminho.startswith(_PREFIXO_DA_ESPECIFICACAO) or caminho == _PREFIXO_DA_ESPECIFICACAO.rstrip("/"):
        if metodo != "GET":
            return _erro(
                405,
                f"metodo {metodo} nao vale em {_PREFIXO_DA_ESPECIFICACAO}<sessao>. Use GET.",
            )
        chave = caminho[len(_PREFIXO_DA_ESPECIFICACAO) :]
        try:
            return _json(200, especificacao_da_sessao(chave, sessoes))
        except DescobertaRecusada as erro:
            return _erro(400, str(erro))
        except MotorAusente as erro:
            return _erro(500, str(erro))

    for prefixo, metodos in _ROTAS_COM_ID:
        if not caminho.startswith(prefixo):
            continue
        if metodo not in metodos:
            return _erro(
                405,
                f"metodo {metodo} nao vale em {prefixo}NN. Use "
                f"{' ou '.join(metodos)}.",
            )
        try:
            vol_id = validar_id(caminho[len(prefixo) :], ct)
        except IdRecusado as erro:
            return _erro(400, str(erro))
        try:
            if prefixo == "/api/volume/":
                return _json(200, dados_do_volume(raiz, vol_id, ct))
            if prefixo == "/api/briefing/":
                return _json(200, dados_do_briefing(raiz, vol_id, ct))
            return _json(
                200, dados_dos_gates(raiz, vol_id, ct, rodar_testes=rodar_testes)
            )
        except ContratoInvalido as erro:
            return _erro(500, f"contrato invalido: {erro}")
        except OSError as erro:
            return _erro(
                500,
                f"erro de disco ao ler o acervo: {erro}. Confirme que a pasta do acervo "
                "continua acessivel e recarregue a pagina.",
            )

    if metodo not in ("GET", "POST"):
        return _erro(405, f"metodo {metodo} nao e aceito. Esta interface usa GET e POST.")

    return _erro(
        404,
        f"nao existe {caminho} nesta interface. As rotas sao: GET /, GET /api/acervo, "
        "GET /api/volume/NN, GET /api/briefing/NN, POST /api/gates/NN, GET /descoberta, "
        "POST /api/descoberta/iniciar, POST /api/descoberta/responder, "
        "POST /api/descoberta/palpite, GET /api/descoberta/especificacao/<sessao>.",
    )


def _responder_descoberta(
    caminho: str, corpo: bytes | None, sessoes: RegistroDeSessoes
) -> tuple[int, str, bytes]:
    """As tres rotas de POST da descoberta, mais a pagina.

    Um unico bloco de tratamento de erro para as tres: `DescobertaRecusada` e
    sempre `400` com a mensagem que diz o que fazer, e `MotorAusente` e `500`
    porque a falta da pasta do motor e problema desta instalacao, nao de quem
    pediu. Nada aqui abre arquivo a partir do que veio na requisicao.
    """
    try:
        if caminho == "/descoberta":
            return 200, HTML_UTF8, pagina_de_descoberta().encode("utf-8")
        dado = _corpo_json(corpo)
        if caminho == "/api/descoberta/iniciar":
            return _json(200, iniciar_descoberta(dado, sessoes))
        if caminho == "/api/descoberta/responder":
            return _json(200, responder_lacuna(dado, sessoes))
        return _json(200, resolver_palpite(dado, sessoes))
    except DescobertaRecusada as erro:
        return _erro(400, str(erro))
    except MotorAusente as erro:
        return _erro(500, str(erro))


# --------------------------------------------------------------------------
# Adaptador HTTP. Fino de proposito: se ele crescer, a regra vazou para ca.
# --------------------------------------------------------------------------


class _Manipulador(BaseHTTPRequestHandler):
    server_version = "AI-ENGINEERING-OS/painel-web"
    sys_version = ""
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:  # noqa: N802 - nome exigido por http.server
        self._atender("GET")

    def do_POST(self) -> None:  # noqa: N802 - nome exigido por http.server
        self._atender("POST")

    # Nenhum outro `do_*`: `http.server` responde 501 sozinho para PUT, DELETE e
    # companhia, e isso e o comportamento desejado - o servidor nao aceita nada
    # que possa alterar o acervo.

    def _atender(self, metodo: str) -> None:
        if not self._cabecalhos_confiaveis():
            return
        entrada = self._ler_corpo()
        if entrada is None:
            return  # corpo acima do teto: `_ler_corpo` ja respondeu 413
        servidor = self.server
        try:
            status, tipo, corpo = responder(
                metodo,
                self.path,
                servidor.raiz,  # type: ignore[attr-defined]
                servidor.contrato,  # type: ignore[attr-defined]
                corpo=entrada,
            )
        except Exception as erro:  # noqa: BLE001 - o servidor local nao pode cair
            status, tipo, corpo = _erro(
                500, f"falha inesperada ao responder {self.path}: {erro!r}"
            )
        self._enviar(status, tipo, corpo)

    def _cabecalhos_confiaveis(self) -> bool:
        """Recusa Host estranho e Origin de outra pagina.

        Duas defesas, ambas contra o mesmo risco: uma pagina qualquer aberta no
        navegador consegue mandar requisicao para `localhost`.

        - **Host**: recusar Host que nao seja loopback bloqueia DNS rebinding, em
          que um dominio do atacante resolve para 127.0.0.1 e passa a falar com
          este servidor como se fosse origem propria.
        - **Origin**: `POST` de formulario nao dispara preflight, entao um site
          hostil poderia disparar o gate 2 (que roda pytest) sem que o navegador
          pedisse permissao. Requisicao com `Origin` de outra origem e recusada;
          a propria pagina nao manda `Origin` em GET e manda a origem correta em
          `fetch`.
        """
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]")
        if host and host not in ("127.0.0.1", "localhost", "::1"):
            self._enviar(
                *_erro(
                    403,
                    "Host nao reconhecido. Esta interface responde apenas em "
                    f"http://{HOST}:<porta>/ - abra o endereco impresso no terminal.",
                )
            )
            return False
        origem = self.headers.get("Origin")
        if origem:
            porta = self.server.server_address[1]
            permitidas = {
                f"http://127.0.0.1:{porta}",
                f"http://localhost:{porta}",
                f"http://[::1]:{porta}",
            }
            if origem not in permitidas:
                self._enviar(
                    *_erro(
                        403,
                        "requisicao de outra origem recusada. Esta interface so "
                        "aceita chamada feita pela propria pagina.",
                    )
                )
                return False
        return True

    def _ler_corpo(self) -> bytes | None:
        """Le o corpo inteiro, ou responde 413 e devolve `None`.

        O corpo tem de ser lido sempre, mesmo quando a rota nao o usa: bytes nao
        lidos no socket com keep-alive fazem a requisicao seguinte ser interpretada
        como corpo da anterior, e ai a pagina quebra sem motivo aparente.

        `Content-Length` e uma alegacao do cliente, e por isso o teto e checado
        **antes** de ler: alocar o que o cabecalho pediu confiaria a memoria do
        servidor ao numero que a requisicao mandou. Acima do teto, a resposta e 413
        e a conexao fecha - nao ha por que consumir megabytes para depois recusa-los.
        """
        try:
            tamanho = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            tamanho = 0
        if tamanho <= 0:
            return b""
        if tamanho > _LIMITE_DE_CORPO:
            self.close_connection = True
            self._enviar(
                *_erro(
                    413,
                    f"corpo de {tamanho} bytes acima do limite de {_LIMITE_DE_CORPO}. "
                    "Encurte o texto e envie de novo.",
                )
            )
            return None
        return self.rfile.read(tamanho)

    def _enviar(self, status: int, tipo: str, corpo: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        # Sem sniffing e sem cache: a pagina reflete o disco, e disco muda entre
        # dois cliques.
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(corpo)

    def log_message(self, formato: str, *args) -> None:
        # Uma linha por requisicao, sem data repetida: o console e a janela que a
        # pessoa deixa aberta, nao um arquivo de log.
        sys.stdout.write("  %s\n" % (formato % args))


class ServidorDoPainel(ThreadingHTTPServer):
    """`ThreadingHTTPServer` porque rodar os gates leva segundos.

    Com servidor de uma thread, um `POST /api/gates/NN` (que chama pytest) faria
    o navegador travar em qualquer outra requisicao ate o subprocesso terminar -
    a pagina inteira pareceria congelada por causa de um botao.
    """

    daemon_threads = True
    allow_reuse_address = False  # porta ocupada tem de falhar, nao ser roubada

    def __init__(self, endereco: tuple[str, int], raiz: Path, ct: Contrato) -> None:
        super().__init__(endereco, _Manipulador)
        self.raiz = raiz
        self.contrato = ct


def subir(
    raiz: Path, ct: Contrato, porta: int, *, fixa: bool = False
) -> ServidorDoPainel:
    """Abre o servidor em `porta`; se estiver ocupada e `fixa` for False, tenta as seguintes."""
    ultima: OSError | None = None
    limite = 1 if fixa else TENTATIVAS_DE_PORTA
    for tentativa in range(limite):
        try:
            return ServidorDoPainel((HOST, porta + tentativa), raiz, ct)
        except OSError as erro:
            ultima = erro
    if fixa:
        raise OSError(
            f"a porta {porta} esta ocupada. Feche quem esta usando ela ou rode sem "
            f"--porta para o servidor escolher uma livre. Detalhe: {ultima}"
        )
    raise OSError(
        f"nenhuma porta livre entre {porta} e {porta + TENTATIVAS_DE_PORTA - 1}. "
        f"Detalhe: {ultima}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="web",
        description="Interface web local da AI-ENGINEERING-OS (so em 127.0.0.1)",
    )
    parser.add_argument(
        "--raiz",
        default=None,
        help=(
            "raiz de outro acervo; por padrao usa a pasta desta plataforma, deduzida "
            "da localizacao do modulo"
        ),
    )
    parser.add_argument(
        "--porta",
        type=int,
        default=None,
        help=f"porta fixa; sem isso tenta {PORTA_PADRAO} e as seguintes",
    )
    parser.add_argument(
        "--sem-navegador",
        action="store_true",
        help="nao abre o navegador; so imprime a URL",
    )
    args = parser.parse_args(argv)

    # O caminho do acervo tem acento no Windows deste projeto ("Usuario" com til
    # nao, mas a pasta do perfil tem). Console em codepage 1252 morre com
    # UnicodeEncodeError ao imprimir isso, e o servidor nao sobe por causa de uma
    # linha de log. `painel` ja resolve exatamente esse caso - reusado, nao copiado.
    P._ajustar_stdout()

    raiz = raiz_padrao() if args.raiz is None else Path(args.raiz).resolve()
    try:
        ct = carregar(raiz)
    except ContratoInvalido as erro:
        print(f"erro: {erro}", file=sys.stderr)
        print(
            f"nao ha 00-INTRODUCAO/contrato.json em {raiz}. Sem --raiz o servidor usa a "
            "propria pasta da plataforma; com --raiz, o caminho que voce passou.",
            file=sys.stderr,
        )
        return 2

    try:
        servidor = subir(
            raiz, ct, args.porta or PORTA_PADRAO, fixa=args.porta is not None
        )
    except OSError as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 2

    porta = servidor.server_address[1]
    url = f"http://{HOST}:{porta}/"
    print("AI-ENGINEERING-OS - interface web local")
    print(f"  endereco: {url}")
    if args.porta is None and porta != PORTA_PADRAO:
        print(f"  (a porta {PORTA_PADRAO} estava ocupada; subiu na {porta})")
    print(f"  acervo:   {raiz}")
    print("  Ctrl+C encerra o servidor. Enquanto esta janela estiver aberta, a pagina funciona.")
    if not args.sem_navegador:
        webbrowser.open(url)

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando.")
    finally:
        servidor.shutdown()
        servidor.server_close()
    return 0


# --------------------------------------------------------------------------
# As paginas. CSS e JS embutidos: sem CDN, sem framework, sem build.
# --------------------------------------------------------------------------

# Os tokens de cor e de tipografia moram aqui uma vez e as duas telas os incluem.
# Duas copias dos mesmos valores hexadecimais divergem na primeira vez que alguem
# ajusta uma cor, e ai as duas telas do mesmo servidor deixam de parecer o mesmo
# programa. Tema claro e escuro pelos tokens: `prefers-color-scheme` para o padrao
# do sistema e `:root[data-theme=...]` para a escolha explicita do botao.
_ESTILO_COMUM = """:root {
  color-scheme: light dark;
  --fundo: #F4F5F8;
  --papel: #FFFFFF;
  --linha: #D7DAE4;
  --acento: #2E3A8C;
  --acento-fraco: #E8EAF6;
  --aprovado: #1B7F6B;
  --rascunho: #A8641B;
  --reprovado: #8C2F2F;
  --texto: #171B2C;
  --texto-fraco: #4C5470;
  --mono: "Cascadia Mono", Consolas, ui-monospace, "Courier New", monospace;
  --titulo: "Segoe UI Variable Display", "Segoe UI", system-ui, sans-serif;
  --corpo: "Segoe UI", system-ui, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root {
    --fundo: #0D0F15;
    --papel: #141822;
    --linha: #262B39;
    --acento: #93A0F0;
    --acento-fraco: #1B2136;
    --aprovado: #4FBFA3;
    --rascunho: #D69A4C;
    --reprovado: #E0736E;
    --texto: #E6E9F4;
    --texto-fraco: #99A1BE;
  }
}
:root[data-theme="dark"] {
  --fundo: #0D0F15;
  --papel: #141822;
  --linha: #262B39;
  --acento: #93A0F0;
  --acento-fraco: #1B2136;
  --aprovado: #4FBFA3;
  --rascunho: #D69A4C;
  --reprovado: #E0736E;
  --texto: #E6E9F4;
  --texto-fraco: #99A1BE;
}
:root[data-theme="light"] {
  --fundo: #F4F5F8;
  --papel: #FFFFFF;
  --linha: #D7DAE4;
  --acento: #2E3A8C;
  --acento-fraco: #E8EAF6;
  --aprovado: #1B7F6B;
  --rascunho: #A8641B;
  --reprovado: #8C2F2F;
  --texto: #171B2C;
  --texto-fraco: #4C5470;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--fundo);
  color: var(--texto);
  font-family: var(--corpo);
  font-size: 15px;
  line-height: 1.55;
}
h1, h2, h3 { font-family: var(--titulo); font-weight: 700; letter-spacing: -0.01em; margin: 0; }
h1 { font-size: 1.5rem; }
h2 { font-size: 1.05rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--texto-fraco); }
h3 { font-size: 1rem; }
code, kbd, pre, .mono { font-family: var(--mono); }
a { color: var(--acento); }
.envelope { max-width: 1180px; margin: 0 auto; padding: 24px 20px 56px; }
header.topo { border-bottom: 1px solid var(--linha); background: var(--papel); }
.topo-linha { display: flex; flex-wrap: wrap; gap: 12px; align-items: baseline; justify-content: space-between; }
.topo-acoes { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
.selo {
  font-family: var(--mono); font-size: 0.72rem; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--acento);
  border: 1px solid var(--acento); border-radius: 2px; padding: 2px 8px;
}
.subtitulo { color: var(--texto-fraco); margin: 6px 0 0; max-width: 70ch; }
.caixa { background: var(--papel); border: 1px solid var(--linha); border-radius: 3px; padding: 16px 18px; }
.dica { color: var(--texto-fraco); font-size: 0.8rem; margin-top: 10px; }
.vazio { color: var(--texto-fraco); }
.aviso { color: var(--reprovado); font-family: var(--mono); font-size: 0.8rem; margin-top: 8px; }
.trabalhando { color: var(--acento); font-family: var(--mono); font-size: 0.8rem; margin-top: 8px; }
.escondido { position: absolute; left: -9999px; top: 0; }
button.tema, a.ir {
  font-family: var(--mono); font-size: 0.75rem; background: transparent;
  color: var(--texto-fraco); border: 1px solid var(--linha); border-radius: 2px;
  padding: 4px 10px; cursor: pointer; text-decoration: none;
}
button.tema:hover, a.ir:hover { border-color: var(--acento); color: var(--acento); }
button.acao {
  font-family: var(--mono); font-size: 0.82rem; cursor: pointer;
  background: var(--acento); color: var(--papel); border: 1px solid var(--acento);
  border-radius: 3px; padding: 8px 14px;
}
button.acao--secundaria { background: transparent; color: var(--acento); }
button.acao:hover:not([disabled]) { filter: brightness(1.12); }
button.acao[disabled] { opacity: 0.55; cursor: progress; }
button.acao:focus-visible { outline: 2px solid var(--acento); outline-offset: 2px; }
.acoes { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px; }
pre.saida {
  font-family: var(--mono); font-size: 0.76rem; background: var(--fundo);
  border: 1px solid var(--linha); border-radius: 3px; padding: 12px;
  max-height: 460px; overflow: auto; white-space: pre-wrap; word-break: break-word; margin: 8px 0 0;
}
footer.pe { margin-top: 30px; color: var(--texto-fraco); font-size: 0.78rem; font-family: var(--mono); }
"""

PAGINA = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<!-- Icone vazio embutido: sem isto o navegador pede /favicon.ico e o console do
     servidor registra um 404 a cada abertura, o que parece defeito e nao e. -->
<link rel="icon" href="data:,">
<title>AI-ENGINEERING-OS - painel do acervo</title>
<style>
""" + _ESTILO_COMUM + """
/* --- cabecalho ------------------------------------------------------- */
.placas { display: flex; flex-wrap: wrap; gap: 10px; margin: 18px 0 0; padding: 0; list-style: none; }
.placa {
  flex: 1 1 150px; background: var(--fundo); border: 1px solid var(--linha);
  border-left: 4px solid var(--linha); border-radius: 3px; padding: 10px 12px;
}
.placa .n { font-family: var(--mono); font-size: 1.7rem; font-weight: 600; display: block; line-height: 1.1; }
.placa .r { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.07em; color: var(--texto-fraco); }
.placa .obs { display: block; font-size: 0.72rem; color: var(--texto-fraco); margin-top: 4px; }
.placa--pronto { border-left-color: var(--aprovado); }
.placa--pronto .n { color: var(--aprovado); }
.placa--rascunho { border-left-color: var(--rascunho); }
.placa--rascunho .n { color: var(--rascunho); }
.placa--revisao { border-left-color: var(--reprovado); }
.placa--revisao .n { color: var(--reprovado); }
.placa--testes { border-left-color: var(--acento); }
.placa--testes .n { color: var(--acento); font-size: 1.3rem; }
.destaque {
  margin: 16px 0 0; padding: 12px 14px; background: var(--acento-fraco);
  border: 1px solid var(--acento); border-radius: 3px;
}
.destaque .r { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--acento); font-family: var(--mono); }
.destaque p { margin: 4px 0 0; }

/* --- como funciona --------------------------------------------------- */
.como {
  margin: 22px 0 0; background: var(--papel); border: 1px solid var(--linha);
  border-radius: 3px; padding: 16px 18px;
}
.como ol { margin: 10px 0 0; padding-left: 22px; }
.como li { margin-bottom: 8px; }
.como code { background: var(--fundo); border: 1px solid var(--linha); padding: 1px 5px; border-radius: 2px; font-size: 0.85em; }
.como .pronto-def { margin: 12px 0 0; padding-left: 14px; border-left: 3px solid var(--acento); color: var(--texto-fraco); }

/* --- layout principal ------------------------------------------------ */
.colunas { display: grid; grid-template-columns: minmax(320px, 420px) 1fr; gap: 20px; margin-top: 22px; align-items: start; }
@media (max-width: 900px) { .colunas { grid-template-columns: 1fr; } }

/* --- grade dos 42 ---------------------------------------------------- */
.grade { display: grid; grid-template-columns: repeat(auto-fill, minmax(86px, 1fr)); gap: 8px; margin-top: 12px; }
.cartao {
  font: inherit; text-align: left; cursor: pointer; padding: 7px 8px;
  background: var(--fundo); color: var(--texto);
  border: 1px solid var(--linha); border-left: 4px solid var(--texto-fraco);
  border-radius: 3px;
}
.cartao:hover { border-color: var(--acento); }
.cartao:focus-visible { outline: 2px solid var(--acento); outline-offset: 2px; }
.cartao[aria-pressed="true"] { background: var(--acento-fraco); border-color: var(--acento); }
.cartao .id { font-family: var(--mono); font-weight: 600; font-size: 0.95rem; display: block; }
.cartao .nm { display: block; font-size: 0.68rem; color: var(--texto-fraco); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cartao .sec { font-family: var(--mono); font-size: 0.66rem; color: var(--texto-fraco); }
.cartao--pronto { border-left-color: var(--aprovado); }
.cartao--rascunho { border-left-color: var(--rascunho); }
.cartao--revisao { border-left-color: var(--reprovado); }
.cartao--pendente { border-left-style: dashed; border-left-color: var(--texto-fraco); }

/* Estado por cor E por forma: circulo=pronto, quadrado=rascunho,
   losango=requer revisao, anel vazado=pendente. Quem nao distingue as cores
   ainda distingue os estados. */
.pilula {
  display: inline-flex; align-items: center; gap: 6px;
  font-family: var(--mono); font-size: 0.72rem; text-transform: uppercase;
  letter-spacing: 0.06em; border: 1px solid currentColor; border-radius: 2px;
  padding: 1px 7px;
}
.pilula::before { content: ""; width: 8px; height: 8px; background: currentColor; }
.pilula--pronto { color: var(--aprovado); }
.pilula--pronto::before { border-radius: 50%; }
.pilula--rascunho { color: var(--rascunho); }
.pilula--rascunho::before { border-radius: 0; }
.pilula--revisao { color: var(--reprovado); }
.pilula--revisao::before { transform: rotate(45deg); }
.pilula--pendente { color: var(--texto-fraco); }
.pilula--pendente::before { background: transparent; border: 2px solid currentColor; border-radius: 50%; }

.legenda { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }

/* --- detalhe --------------------------------------------------------- */
.ficha dl { display: grid; grid-template-columns: max-content 1fr; gap: 4px 14px; margin: 12px 0 0; }
.ficha dt { font-family: var(--mono); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--texto-fraco); }
.ficha dd { margin: 0; }
.lista-secoes { display: flex; flex-wrap: wrap; gap: 5px; margin: 6px 0 0; padding: 0; list-style: none; }
.lista-secoes li { font-family: var(--mono); font-size: 0.72rem; border: 1px solid var(--linha); border-radius: 2px; padding: 1px 6px; }
.lista-secoes li.ausente { color: var(--reprovado); border-color: var(--reprovado); border-style: dashed; }
.lista-secoes li.presente { color: var(--aprovado); border-color: var(--aprovado); }
.bloco { margin-top: 18px; padding-top: 14px; border-top: 1px solid var(--linha); }
.veredicto { border: 1px solid var(--linha); border-left: 4px solid var(--linha); border-radius: 3px; padding: 10px 12px; margin-top: 8px; }
.veredicto--ok { border-left-color: var(--aprovado); }
.veredicto--nao { border-left-color: var(--reprovado); }
.veredicto h4 { margin: 0; font-family: var(--titulo); font-size: 0.95rem; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.veredicto p { margin: 6px 0 0; font-family: var(--mono); font-size: 0.8rem; color: var(--texto-fraco); }
.grupo-regra { margin: 8px 0 0; }
.grupo-regra > span { font-family: var(--mono); font-size: 0.78rem; color: var(--reprovado); }
.grupo-regra ul { margin: 4px 0 0; padding-left: 20px; }
.grupo-regra li { font-family: var(--mono); font-size: 0.74rem; color: var(--texto-fraco); }
</style>
</head>
<body>
<header class="topo">
  <div class="envelope" style="padding-bottom:20px">
    <div class="topo-linha">
      <div>
        <span class="selo">painel local</span>
        <h1 style="margin-top:8px">AI-ENGINEERING-OS</h1>
      </div>
      <div class="topo-acoes">
        <a class="ir" href="/descoberta">Descobrir o que construir</a>
        <button class="tema" id="btn-tema" type="button">Tema: sistema</button>
      </div>
    </div>
    <p class="subtitulo">
      Acervo tecnico de engenharia de IA em 42 volumes. O ativo da plataforma e a
      maquina de producao: nada entra no acervo sem passar por porta de qualidade
      executavel. Esta tela le o contrato e o disco, roda os gates e monta briefing -
      ela nao escreve volume e nao grava status.
    </p>
    <ul class="placas" id="placas"></ul>
    <div class="destaque">
      <span class="r">Proxima acao recomendada</span>
      <p id="proxima-acao">Carregando o estado do acervo...</p>
      <p class="dica" style="margin-top:6px">
        A recomendacao vem do mesmo motor do painel de console
        (<code>python -m ferramentas.painel</code>), e por isso ela cita "opcoes" numeradas:
        aqui, a opcao de inspecionar e clicar no volume na grade, e a de rodar os gates e
        o botao dentro da ficha.
      </p>
    </div>
  </div>
</header>

<div class="envelope">
  <section class="como">
    <h2>Como funciona</h2>
    <ol>
      <li><strong>Gate 1 - estrutural.</strong> <code>python -m ferramentas.validar NN</code>.
        Reprova front-matter errado, secao ausente, prosa abaixo do minimo, marcador
        proibido, Mermaid sem descricao, exemplo sem teste e link morto.</li>
      <li><strong>Gate 2 - executavel.</strong> <code>python -m pytest exemplos/&lt;vol&gt; -q</code>.
        Reprova codigo citado pelo volume que nao roda ou nao passa nos proprios testes.</li>
      <li><strong>Gate 3 - referencias cruzadas.</strong> <code>python -m ferramentas.validar --cross-refs</code>.
        Reprova <code>depende_de</code> apontando para volume inexistente e ciclo no grafo
        de pre-requisitos. Vale para o acervo inteiro, nao para um volume.</li>
    </ol>
    <p class="pronto-def">
      <strong>Definicao de PRONTO:</strong> gate 1 verde, gate 2 verde, auditoria com
      media maior ou igual a 8,0 e nenhuma secao abaixo de 6, e registro datado no
      <code>CHANGELOG.md</code>. Falta um dos quatro, o volume nao e PRONTO. Auditoria
      abaixo de 8,0 grava REQUER_REVISAO; gate vermelho mantem RASCUNHO. Quem escreve
      nao se aprova: o auditor e outro modelo, em outra sessao.
    </p>
  </section>

  <div class="colunas">
    <section class="caixa" aria-labelledby="tit-grade">
      <h2 id="tit-grade">Os 42 volumes</h2>
      <p class="dica">Clique num volume para abrir a ficha dele ao lado.</p>
      <div class="grade" id="grade"></div>
      <div class="legenda" id="legenda"></div>
      <p class="dica">
        O numero embaixo do nome e secoes presentes/esperadas, e "esperadas" varia por
        tipo. Presente significa que o arquivo existe - nao que ele e bom.
      </p>
    </section>

    <section class="caixa ficha" id="detalhe" aria-live="polite">
      <h2>Ficha do volume</h2>
      <p class="vazio">Nenhum volume selecionado. Escolha um na grade a esquerda.</p>
    </section>
  </div>

  <footer class="pe">
    Servidor local em 127.0.0.1, sem acesso pela rede. Ctrl+C na janela do terminal encerra.
  </footer>
</div>

<textarea id="area-copia" class="escondido" aria-hidden="true" tabindex="-1"></textarea>

<script>
var estado = { acervo: null, selecionado: null };

function q(sel) { return document.querySelector(sel); }

function criar(tag, classe, texto) {
  var el = document.createElement(tag);
  if (classe) { el.className = classe; }
  if (texto !== undefined && texto !== null) { el.textContent = String(texto); }
  return el;
}

var SUFIXO = {
  PRONTO: "pronto",
  RASCUNHO: "rascunho",
  REQUER_REVISAO: "revisao",
  PENDENTE: "pendente"
};

function sufixo(status) { return SUFIXO[status] || "pendente"; }

function pilula(status) {
  return criar("span", "pilula pilula--" + sufixo(status), status);
}

async function pedir(url, metodo) {
  var resposta;
  try {
    resposta = await fetch(url, {
      method: metodo || "GET",
      headers: { "Accept": "application/json" }
    });
  } catch (erro) {
    throw new Error(
      "Nao consegui falar com o servidor local. Confirme que a janela do terminal " +
      "que rodou 'python -m ferramentas.web' continua aberta e recarregue esta pagina."
    );
  }
  var texto = await resposta.text();
  var dado;
  try { dado = JSON.parse(texto); } catch (erro) { dado = { erro: texto }; }
  if (!resposta.ok) {
    throw new Error(dado.erro || ("o servidor respondeu " + resposta.status + "."));
  }
  return dado;
}

/* --- cabecalho ------------------------------------------------------- */

function placa(classe, numero, rotulo, obs) {
  var li = criar("li", "placa " + classe);
  li.appendChild(criar("span", "n", numero));
  li.appendChild(criar("span", "r", rotulo));
  if (obs) { li.appendChild(criar("span", "obs", obs)); }
  return li;
}

function desenharPlacas(dado) {
  var alvo = q("#placas");
  alvo.textContent = "";
  var c = dado.contagem || {};
  alvo.appendChild(placa("placa--pronto", c.PRONTO || 0, "Pronto", "os quatro criterios cumpridos"));
  alvo.appendChild(placa("placa--revisao", c.REQUER_REVISAO || 0, "Requer revisao", "auditoria abaixo de 8,0"));
  alvo.appendChild(placa("placa--rascunho", c.RASCUNHO || 0, "Rascunho", "escrito, ainda nao aprovado"));
  alvo.appendChild(placa("placa", c.PENDENTE || 0, "Pendente", "sem pasta em disco"));
  var t = dado.testes || {};
  alvo.appendChild(placa(
    "placa--testes",
    t.funcoes_de_teste || 0,
    "testes em disco",
    "verde so depois de rodar: " + (t.comando || "")
  ));
  q("#proxima-acao").textContent = dado.proxima_acao || "";
}

function desenharLegenda() {
  var alvo = q("#legenda");
  alvo.textContent = "";
  ["PRONTO", "REQUER_REVISAO", "RASCUNHO", "PENDENTE"].forEach(function (s) {
    alvo.appendChild(pilula(s));
  });
}

/* --- grade ----------------------------------------------------------- */

function desenharGrade(volumes) {
  var alvo = q("#grade");
  alvo.textContent = "";
  volumes.forEach(function (v) {
    var b = criar("button", "cartao cartao--" + sufixo(v.status));
    b.type = "button";
    b.setAttribute("aria-pressed", "false");
    b.dataset.id = v.id;
    b.title = v.id + "-" + v.nome + " - " + v.tipo + " - " + v.status;
    b.appendChild(criar("span", "id", v.id));
    b.appendChild(criar("span", "nm", v.nome));
    b.appendChild(criar("span", "sec", v.secoes_presentes + "/" + v.secoes_esperadas));
    b.addEventListener("click", function () { abrirVolume(v.id); });
    alvo.appendChild(b);
  });
}

function marcarSelecionado(id) {
  var cartoes = document.querySelectorAll(".cartao");
  for (var i = 0; i < cartoes.length; i++) {
    cartoes[i].setAttribute("aria-pressed", cartoes[i].dataset.id === id ? "true" : "false");
  }
}

/* --- ficha do volume ------------------------------------------------- */

function linha(dl, rotulo, valor) {
  dl.appendChild(criar("dt", null, rotulo));
  var dd = criar("dd");
  if (typeof valor === "string" || typeof valor === "number") {
    dd.textContent = String(valor);
  } else {
    dd.appendChild(valor);
  }
  dl.appendChild(dd);
  return dd;
}

function listaDeSecoes(nomes, classe) {
  var ul = criar("ul", "lista-secoes");
  if (!nomes.length) {
    ul.appendChild(criar("li", "vazio", "(nenhuma)"));
    return ul;
  }
  nomes.forEach(function (n) { ul.appendChild(criar("li", classe, n)); });
  return ul;
}

function desenharFicha(v) {
  var alvo = q("#detalhe");
  alvo.textContent = "";
  var cabeca = criar("div", "topo-linha");
  cabeca.appendChild(criar("h2", null, "Volume " + v.id + "-" + v.nome));
  cabeca.appendChild(pilula(v.status));
  alvo.appendChild(cabeca);

  var dl = criar("dl");
  linha(dl, "Tipo", v.tipo);
  linha(dl, "Secoes", v.secoes_presentes.length + " de " + v.secoes_esperadas + " em disco");
  linha(dl, "Perecivel", v.perecivel ? "sim - nao fixe numero que expira" : "nao");
  var aud = v.auditoria || {};
  linha(
    dl,
    "Auditoria",
    aud.relatorio
      ? aud.relatorio + (aud.nota === null || aud.nota === undefined ? " (sem linha media:)" : " - media " + aud.nota)
      : "nenhum relatorio em auditorias/ para este volume"
  );
  if (v.pre_requisitos.length) {
    var texto = v.pre_requisitos.map(function (p) {
      return p.id + "-" + p.nome + " [" + p.status + "]";
    }).join(", ");
    linha(dl, "depende_de", texto);
  } else {
    linha(dl, "depende_de", "vazio - nenhum pre-requisito de leitura declarado");
  }
  linha(dl, "Exemplos", v.pasta_exemplos + "/");
  alvo.appendChild(dl);

  var bl = criar("div", "bloco");
  bl.appendChild(criar("h3", null, "Secoes presentes"));
  bl.appendChild(listaDeSecoes(v.secoes_presentes, "presente"));
  bl.appendChild(criar("h3", null, "Secoes ausentes"));
  bl.appendChild(listaDeSecoes(v.secoes_ausentes, "ausente"));
  alvo.appendChild(bl);

  var fr = criar("div", "bloco");
  fr.appendChild(criar("h3", null, "Fronteira de escopo"));
  if (v.fronteira) {
    fr.appendChild(criar("p", null,
      v.fronteira.titulo + " - declare no 03-Escopo o que pertence ao vizinho. " +
      "Fronteira ausente e lacuna de conteudo."));
    fr.appendChild(criar("pre", "saida", v.fronteira.texto));
  } else {
    fr.appendChild(criar("p", "vazio",
      "Este volume nao esta em nenhum grupo sobreposto do ROADMAP.md."));
  }
  alvo.appendChild(fr);

  var acoes = criar("div", "bloco");
  acoes.appendChild(criar("h3", null, "Verificar e preparar"));
  var caixaBotoes = criar("div", "acoes");
  var btnGates = criar("button", "acao", "Rodar os tres gates");
  btnGates.type = "button";
  btnGates.addEventListener("click", function () { rodarGates(v.id, btnGates); });
  var btnBriefing = criar("button", "acao acao--secundaria", "Gerar briefing");
  btnBriefing.type = "button";
  btnBriefing.addEventListener("click", function () { gerarBriefing(v.id, btnBriefing); });
  caixaBotoes.appendChild(btnGates);
  caixaBotoes.appendChild(btnBriefing);
  acoes.appendChild(caixaBotoes);
  acoes.appendChild(criar("p", "dica",
    "O gate 2 chama pytest de verdade e pode levar alguns segundos. O briefing sai " +
    "do contrato, do disco e do ROADMAP - nada nele e inventado."));
  var saida = criar("div");
  saida.id = "saida-acao";
  acoes.appendChild(saida);
  alvo.appendChild(acoes);
}

async function abrirVolume(id) {
  marcarSelecionado(id);
  estado.selecionado = id;
  var alvo = q("#detalhe");
  alvo.textContent = "";
  alvo.appendChild(criar("h2", null, "Volume " + id));
  alvo.appendChild(criar("p", "trabalhando", "Lendo o volume no disco..."));
  try {
    desenharFicha(await pedir("/api/volume/" + id));
  } catch (erro) {
    alvo.textContent = "";
    alvo.appendChild(criar("h2", null, "Volume " + id));
    alvo.appendChild(criar("p", "aviso", erro.message));
  }
}

/* --- gates ----------------------------------------------------------- */

function desenharGates(dado) {
  var saida = q("#saida-acao");
  saida.textContent = "";
  var titulo = criar("h3", null, dado.aprovado
    ? "Os tres gates passaram"
    : "Algum gate reprovou - gate vermelho grava RASCUNHO, nunca PRONTO");
  saida.appendChild(titulo);
  dado.gates.forEach(function (g) {
    var caixa = criar("div", "veredicto veredicto--" + (g.aprovado ? "ok" : "nao"));
    var h = criar("h4");
    h.appendChild(criar("span", null, "Gate " + g.gate + " - " + g.nome));
    h.appendChild(criar("span", "pilula pilula--" + (g.aprovado ? "pronto" : "revisao"),
      g.aprovado ? "aprovado" : "reprovado"));
    caixa.appendChild(h);
    caixa.appendChild(criar("p", null, g.detalhe));
    (g.violacoes_por_regra || []).forEach(function (grupo) {
      var bloco = criar("div", "grupo-regra");
      bloco.appendChild(criar("span", null, "[" + grupo.regra + "] x" + grupo.quantidade));
      var ul = criar("ul");
      grupo.itens.forEach(function (item) {
        ul.appendChild(criar("li", null, item.arquivo + ":" + item.linha + ": " + item.mensagem));
      });
      if (grupo.omitidas > 0) {
        ul.appendChild(criar("li", null, "... e " + grupo.omitidas + " outra(s) da mesma regra"));
      }
      bloco.appendChild(ul);
      caixa.appendChild(bloco);
    });
    saida.appendChild(caixa);
  });
}

async function rodarGates(id, botao) {
  var saida = q("#saida-acao");
  saida.textContent = "";
  saida.appendChild(criar("p", "trabalhando",
    "Rodando os tres gates do volume " + id + ". O gate 2 chama pytest e pode levar " +
    "alguns segundos - a pagina continua respondendo."));
  botao.disabled = true;
  botao.textContent = "Rodando os gates...";
  try {
    desenharGates(await pedir("/api/gates/" + id, "POST"));
  } catch (erro) {
    saida.textContent = "";
    saida.appendChild(criar("p", "aviso", erro.message));
  } finally {
    botao.disabled = false;
    botao.textContent = "Rodar os tres gates";
  }
}

/* --- briefing -------------------------------------------------------- */

function copiar(texto, botao) {
  function ok() {
    botao.textContent = "Copiado";
    setTimeout(function () { botao.textContent = "Copiar"; }, 1800);
  }
  function pelaArea() {
    // navigator.clipboard exige contexto seguro. http://127.0.0.1 costuma contar
    // como seguro, mas nao em todo navegador nem em toda configuracao - por isso
    // o textarea escondido fica como plano B em vez de a copia simplesmente falhar.
    var area = q("#area-copia");
    area.value = texto;
    area.focus();
    area.select();
    var deu = false;
    try { deu = document.execCommand("copy"); } catch (erro) { deu = false; }
    area.blur();
    if (deu) { ok(); return; }
    botao.textContent = "Copie com Ctrl+C";
    window.getSelection().selectAllChildren(q("#markdown-briefing"));
  }
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(texto).then(ok, pelaArea);
  } else {
    pelaArea();
  }
}

async function gerarBriefing(id, botao) {
  var saida = q("#saida-acao");
  saida.textContent = "";
  saida.appendChild(criar("p", "trabalhando", "Montando o briefing do volume " + id + "..."));
  botao.disabled = true;
  try {
    var dado = await pedir("/api/briefing/" + id);
    saida.textContent = "";
    var cabeca = criar("div", "topo-linha");
    cabeca.appendChild(criar("h3", null, "Briefing do volume " + dado.volume + "-" + dado.nome));
    var btnCopiar = criar("button", "acao acao--secundaria", "Copiar");
    btnCopiar.type = "button";
    btnCopiar.addEventListener("click", function () { copiar(dado.markdown, btnCopiar); });
    cabeca.appendChild(btnCopiar);
    saida.appendChild(cabeca);
    saida.appendChild(criar("p", "dica",
      "Cole isto num agente. Quem escreve o volume e um modelo; esta tela so prepara e verifica."));
    var pre = criar("pre", "saida", dado.markdown);
    pre.id = "markdown-briefing";
    saida.appendChild(pre);
  } catch (erro) {
    saida.textContent = "";
    saida.appendChild(criar("p", "aviso", erro.message));
  } finally {
    botao.disabled = false;
  }
}

/* --- tema ------------------------------------------------------------ */

var TEMAS = ["sistema", "claro", "escuro"];
var temaAtual = 0;

function aplicarTema() {
  var nome = TEMAS[temaAtual];
  if (nome === "sistema") {
    document.documentElement.removeAttribute("data-theme");
  } else {
    document.documentElement.setAttribute("data-theme", nome === "escuro" ? "dark" : "light");
  }
  q("#btn-tema").textContent = "Tema: " + nome;
}

/* --- arranque -------------------------------------------------------- */

async function carregar() {
  try {
    var dado = await pedir("/api/acervo");
    estado.acervo = dado;
    desenharPlacas(dado);
    desenharLegenda();
    desenharGrade(dado.volumes);
  } catch (erro) {
    q("#proxima-acao").textContent = erro.message;
    q("#grade").appendChild(criar("p", "aviso", erro.message));
  }
}

q("#btn-tema").addEventListener("click", function () {
  temaAtual = (temaAtual + 1) % TEMAS.length;
  aplicarTema();
});

aplicarTema();
carregar();
</script>
</body>
</html>
"""


def pagina_de_descoberta() -> str:
    """A tela de descoberta, com o seletor preenchido pelo catalogo do volume 03.

    A lista de plataformas e injetada num `<script type="application/json">` e lida
    com `JSON.parse` do `textContent`. Nao e interpolacao dentro de codigo: um bloco
    de dados nao executa, e por isso o valor injetado nunca pode virar instrucao,
    mesmo que alguem acrescente uma plataforma com nome estranho no catalogo.
    """
    return PAGINA_DESCOBERTA.replace(
        "__PLATAFORMAS__", json.dumps(list(plataformas_do_catalogo()))
    )


PAGINA_DESCOBERTA = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<link rel="icon" href="data:,">
<title>AI-ENGINEERING-OS - descoberta do que construir</title>
<style>
""" + _ESTILO_COMUM + """
/* --- passos ---------------------------------------------------------- */
.passo { margin-top: 20px; }
.oculto { display: none; }
.rotulo-campo { display: block; font-family: var(--mono); font-size: 0.78rem;
  text-transform: uppercase; letter-spacing: 0.06em; color: var(--texto-fraco); margin: 16px 0 6px; }
textarea.ideia, textarea.livre, input.livre {
  width: 100%; font-family: var(--corpo); font-size: 0.95rem; color: var(--texto);
  background: var(--fundo); border: 1px solid var(--linha); border-radius: 3px; padding: 10px 12px;
}
textarea.ideia:focus, textarea.livre:focus, input.livre:focus { outline: 2px solid var(--acento); outline-offset: 1px; }
.contador { font-family: var(--mono); font-size: 0.72rem; color: var(--texto-fraco); margin: 4px 0 0; }
.contador--cheio { color: var(--rascunho); }

/* --- seletor de plataforma ------------------------------------------- */
fieldset.seletor { border: 1px solid var(--linha); border-radius: 3px; padding: 10px 14px 14px; margin: 0; }
fieldset.seletor legend { font-family: var(--mono); font-size: 0.78rem; text-transform: uppercase;
  letter-spacing: 0.06em; color: var(--texto-fraco); padding: 0 6px; }
.plataformas { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 8px; margin-top: 6px; }
.plataformas label {
  display: block; cursor: pointer; background: var(--fundo);
  border: 1px solid var(--linha); border-left: 4px solid var(--texto-fraco);
  border-radius: 3px; padding: 8px 10px;
}
.plataformas label:hover { border-color: var(--acento); }
.plataformas input { position: absolute; opacity: 0; width: 0; height: 0; }
.plataformas input:checked + .marca { color: var(--acento); }
.plataformas label:has(input:checked) { background: var(--acento-fraco); border-color: var(--acento); border-left-color: var(--acento); }
.plataformas label:has(input:focus-visible) { outline: 2px solid var(--acento); outline-offset: 2px; }
.plataformas .marca { display: block; font-size: 0.92rem; }
.plataformas .cod { display: block; font-family: var(--mono); font-size: 0.7rem; color: var(--texto-fraco); }

/* --- exemplos clicaveis ---------------------------------------------- */
.exemplos { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 8px; margin-top: 6px; }
button.exemplo {
  font: inherit; font-size: 0.86rem; text-align: left; cursor: pointer;
  background: var(--fundo); color: var(--texto);
  border: 1px dashed var(--linha); border-radius: 3px; padding: 8px 10px;
}
button.exemplo:hover { border-color: var(--acento); border-style: solid; }
button.exemplo:focus-visible { outline: 2px solid var(--acento); outline-offset: 2px; }

/* --- progresso ------------------------------------------------------- */
.progresso { border: 1px solid var(--linha); border-radius: 3px; padding: 10px 12px; background: var(--fundo); }
.progresso .conta { font-family: var(--mono); font-size: 0.86rem; }
.trilho { height: 6px; background: var(--linha); border-radius: 3px; margin: 8px 0 0; overflow: hidden; }
.trilho span { display: block; height: 100%; background: var(--acento); }
.progresso .obs { font-size: 0.76rem; color: var(--texto-fraco); margin: 6px 0 0; }

/* --- palpites de contexto -------------------------------------------- */
.palpite {
  border: 1px solid var(--linha); border-left: 4px solid var(--rascunho);
  border-radius: 3px; padding: 10px 12px; margin-top: 8px;
}
.palpite h4 { font-family: var(--titulo); font-size: 0.95rem; margin: 0; }
.palpite .conf { font-family: var(--mono); font-size: 0.72rem; color: var(--rascunho);
  text-transform: uppercase; letter-spacing: 0.06em; }
.palpite .prova { font-family: var(--mono); font-size: 0.78rem; background: var(--fundo);
  border-left: 3px solid var(--linha); padding: 6px 8px; margin: 8px 0 0; }

/* --- pergunta -------------------------------------------------------- */
.pergunta { border: 1px solid var(--acento); border-radius: 3px; padding: 14px 16px; background: var(--papel); }
.pergunta .id { font-family: var(--mono); font-size: 0.72rem; color: var(--texto-fraco); }
.pergunta h3 { margin: 4px 0 0; font-size: 1.12rem; line-height: 1.4; }
.porque { margin: 10px 0 0; padding: 8px 10px; background: var(--acento-fraco);
  border-left: 3px solid var(--acento); font-size: 0.88rem; }
.opcoes { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0 0; }
button.opcao {
  font-family: var(--mono); font-size: 0.82rem; cursor: pointer;
  background: transparent; color: var(--texto); border: 1px solid var(--linha);
  border-radius: 3px; padding: 7px 12px;
}
button.opcao:hover { border-color: var(--acento); color: var(--acento); }
button.opcao:focus-visible { outline: 2px solid var(--acento); outline-offset: 2px; }

/* --- especificacao --------------------------------------------------- */
.selo-estado { display: inline-flex; align-items: center; gap: 6px; font-family: var(--mono);
  font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.06em;
  border: 1px solid currentColor; border-radius: 2px; padding: 1px 8px; }
.selo-estado::before { content: ""; width: 8px; height: 8px; background: currentColor; }
.selo-estado--completa { color: var(--aprovado); }
.selo-estado--completa::before { border-radius: 50%; }
.selo-estado--incompleta { color: var(--rascunho); }
.selo-estado--incompleta::before { border-radius: 0; }
.motivos { margin: 10px 0 0; padding-left: 20px; }
.motivos li { margin-bottom: 6px; }
.lista-lacunas { list-style: none; margin: 8px 0 0; padding: 0; }
.lista-lacunas li { border-left: 3px solid var(--linha); padding: 4px 0 4px 10px; margin-bottom: 8px; }
.lista-lacunas .p { display: block; }
.lista-lacunas .m { display: block; font-size: 0.8rem; color: var(--texto-fraco); }
</style>
</head>
<body>
<header class="topo">
  <div class="envelope" style="padding-bottom:20px">
    <div class="topo-linha">
      <div>
        <span class="selo">descoberta</span>
        <h1 style="margin-top:8px">Descobrir o que construir</h1>
      </div>
      <div class="topo-acoes">
        <a class="ir" href="/">Voltar ao painel dos 42 volumes</a>
        <button class="tema" id="btn-tema" type="button">Tema: sistema</button>
      </div>
    </div>
    <p class="subtitulo">
      Uma pergunta por vez, escolhida por quanta incerteza ela remove - e nunca uma
      pergunta que nao faz sentido para o seu caso. No fim sai uma especificacao com
      tres listas: o que ficou decidido, o que ficou aberto, e o que o programa supos
      sem ninguem ter confirmado.
    </p>
  </div>
</header>

<div class="envelope">
  <section class="caixa passo" id="passo-ideia">
    <h2>1. A ideia, e onde ela vai rodar</h2>
    <fieldset class="seletor">
      <legend>Onde isso vai rodar</legend>
      <p class="dica" style="margin-top:0">
        Escolher aqui e a diferenca entre uma entrevista curta e uma entrevista errada.
        Esta e a unica resposta que muda <em>quais</em> outras perguntas existem: cada
        opcao destrava um bloco de perguntas e cala os outros tres. Com a escolha feita
        no clique, o motor recebe a plataforma como resposta sua - nao como palpite
        dele a confirmar depois.
      </p>
      <div class="plataformas" id="plataformas"></div>
    </fieldset>

    <label class="rotulo-campo" for="ideia">O que precisa existir, em uma ou duas frases</label>
    <textarea class="ideia" id="ideia" rows="4" maxlength="4000"
      placeholder="Escreva com as suas palavras. Nao precisa de termo tecnico."></textarea>
    <p class="contador" id="contador"></p>

    <h3 style="margin-top:18px">Ou comece de um exemplo</h3>
    <p class="dica" style="margin-top:4px">Clicar preenche o campo acima; depois edite o texto do jeito que precisar.</p>
    <div class="exemplos" id="exemplos"></div>

    <div class="acoes" style="margin-top:16px">
      <button class="acao" id="btn-iniciar" type="button">Comecar a entrevista</button>
    </div>
    <div id="erro-inicio"></div>
  </section>

  <section class="caixa passo oculto" id="passo-entrevista" aria-live="polite">
    <h2>2. Uma pergunta por vez</h2>
    <div id="progresso"></div>
    <div id="palpites"></div>
    <div id="pergunta"></div>
    <div class="acoes" style="margin-top:16px">
      <button class="acao acao--secundaria" id="btn-spec" type="button">Ver a especificacao como esta agora</button>
    </div>
    <p class="dica">
      A especificacao pode ser gerada a qualquer momento, inclusive no meio da conversa:
      um documento com decisoes abertas declaradas e util, e o que ele nao faz e se
      declarar completo antes de ser.
    </p>
  </section>

  <section class="caixa passo oculto" id="passo-spec" aria-live="polite">
    <h2>3. A especificacao</h2>
    <div id="spec"></div>
  </section>

  <footer class="pe">
    Servidor local em 127.0.0.1, sem acesso pela rede. A entrevista fica na memoria
    deste processo e nada dela e gravado em disco: fechar a janela do terminal descarta
    tudo. Copie a especificacao antes de fechar.
  </footer>
</div>

<textarea id="area-copia" class="escondido" aria-hidden="true" tabindex="-1"></textarea>
<script id="dados-de-plataforma" type="application/json">__PLATAFORMAS__</script>
<script>
var estado = { sessao: null, plataforma: null, ultimo: null };

var LIMITE_DA_IDEIA = 4000;

function q(sel) { return document.querySelector(sel); }

function criar(tag, classe, texto) {
  var el = document.createElement(tag);
  if (classe) { el.className = classe; }
  if (texto !== undefined && texto !== null) { el.textContent = String(texto); }
  return el;
}

/* Todo texto que veio do servidor entra por textContent, e nunca como marcacao
   crua: evidencia e resposta sao texto de quem usa, e texto de quem usa
   interpretado como marcacao e o caminho mais curto para a pagina executar o que
   alguem digitou. Por isso a pagina inteira e montada por createElement. */

var ROTULO_DE_PLATAFORMA = {
  WEB: "Chega por navegador",
  MOBILE: "Instalado em aparelho de mao",
  DESKTOP: "Instalado na maquina da pessoa",
  AUTOMACAO: "Roda sozinho, sem ninguem olhando"
};

var EXEMPLOS = [
  "Controle de estoque de uma padaria: quanto sobrou de cada massa no fim do dia.",
  "Agenda de uma clinica de fisioterapia, com remarcacao sem precisar ligar para a recepcao.",
  "Catalogo de pecas de uma oficina mecanica, com foto e a prateleira onde cada peca esta.",
  "Registro de manutencao de uma frota de vans: o que foi trocado em cada veiculo e quando.",
  "Painel de chamados de um provedor de internet de bairro, com prazo por chamado aberto."
];

async function pedir(url, metodo, corpo) {
  var resposta;
  var opcoes = { method: metodo || "GET", headers: { "Accept": "application/json" } };
  if (corpo !== undefined && corpo !== null) {
    opcoes.headers["Content-Type"] = "application/json";
    opcoes.body = JSON.stringify(corpo);
  }
  try {
    resposta = await fetch(url, opcoes);
  } catch (erro) {
    throw new Error(
      "Nao consegui falar com o servidor local. Confirme que a janela do terminal " +
      "que rodou 'python -m ferramentas.web' continua aberta e recarregue esta pagina."
    );
  }
  var texto = await resposta.text();
  var dado;
  try { dado = JSON.parse(texto); } catch (erro) { dado = { erro: texto }; }
  if (!resposta.ok) {
    throw new Error(dado.erro || ("o servidor respondeu " + resposta.status + "."));
  }
  return dado;
}

function mostrarErro(alvoId, mensagem) {
  var alvo = q(alvoId);
  alvo.textContent = "";
  alvo.appendChild(criar("p", "aviso", mensagem));
}

/* --- passo 1: plataforma, ideia, exemplos ---------------------------- */

function desenharPlataformas() {
  var nomes = JSON.parse(q("#dados-de-plataforma").textContent);
  var alvo = q("#plataformas");
  alvo.textContent = "";
  nomes.forEach(function (nome, indice) {
    var label = criar("label");
    var radio = document.createElement("input");
    radio.type = "radio";
    radio.name = "plataforma";
    radio.value = nome;
    if (indice === 0) { radio.checked = true; estado.plataforma = nome; }
    radio.addEventListener("change", function () { estado.plataforma = nome; });
    label.appendChild(radio);
    label.appendChild(criar("span", "marca", ROTULO_DE_PLATAFORMA[nome] || nome));
    label.appendChild(criar("span", "cod", nome));
    alvo.appendChild(label);
  });
}

function atualizarContador() {
  var usados = q("#ideia").value.length;
  var alvo = q("#contador");
  alvo.textContent = usados + " de " + LIMITE_DA_IDEIA + " caracteres";
  alvo.className = usados >= LIMITE_DA_IDEIA ? "contador contador--cheio" : "contador";
}

function desenharExemplos() {
  var alvo = q("#exemplos");
  alvo.textContent = "";
  EXEMPLOS.forEach(function (texto) {
    var b = criar("button", "exemplo", texto);
    b.type = "button";
    b.addEventListener("click", function () {
      q("#ideia").value = texto;
      atualizarContador();
      q("#ideia").focus();
    });
    alvo.appendChild(b);
  });
}

async function iniciar(botao) {
  var ideia = q("#ideia").value;
  q("#erro-inicio").textContent = "";
  if (!ideia.trim()) {
    mostrarErro("#erro-inicio",
      "Escreva a ideia no campo acima, ou clique num dos exemplos para preencher.");
    return;
  }
  botao.disabled = true;
  botao.textContent = "Lendo a ideia...";
  try {
    var dado = await pedir("/api/descoberta/iniciar", "POST", {
      ideia: ideia,
      plataforma: estado.plataforma
    });
    estado.sessao = dado.sessao;
    q("#passo-entrevista").classList.remove("oculto");
    desenharEstado(dado);
    q("#passo-entrevista").scrollIntoView({ block: "start" });
  } catch (erro) {
    mostrarErro("#erro-inicio", erro.message);
  } finally {
    botao.disabled = false;
    botao.textContent = "Comecar a entrevista";
  }
}

/* --- passo 2: progresso, palpites, pergunta -------------------------- */

function desenharProgresso(p) {
  var alvo = q("#progresso");
  alvo.textContent = "";
  var caixa = criar("div", "progresso");
  caixa.appendChild(criar("span", "conta",
    p.respondidas + " de " + p.total + " perguntas respondidas"));
  var trilho = criar("div", "trilho");
  var barra = criar("span");
  var fracao = p.total > 0 ? Math.round((p.respondidas / p.total) * 100) : 0;
  barra.style.width = fracao + "%";
  trilho.appendChild(barra);
  caixa.appendChild(trilho);
  caixa.appendChild(criar("p", "obs", p.observacao));
  if (p.total_pode_crescer) {
    caixa.appendChild(criar("p", "obs",
      "Agora mesmo: ha palpite de contexto sem resposta. Confirmar um deles acrescenta " +
      "perguntas, e o total abaixo vai subir - isso e o numero ficando honesto, nao " +
      "um erro de conta."));
  }
  alvo.appendChild(caixa);
}

function desenharPalpites(dado) {
  var alvo = q("#palpites");
  alvo.textContent = "";
  var descartados = dado.plataforma_inferida_descartada || [];
  if (descartados.length) {
    var nota = criar("div", "palpite");
    nota.appendChild(criar("h4", null, "O texto sugeria outra plataforma, e a sua escolha valeu"));
    descartados.forEach(function (p) {
      nota.appendChild(criar("p", "conf", "li " + p.valor + " neste trecho"));
      nota.appendChild(criar("p", "prova", p.evidencia));
    });
    nota.appendChild(criar("p", "dica",
      "Voce escolheu " + (dado.plataforma_escolhida || "") + " no seletor, e e isso que " +
      "vale. O palpite foi descartado, nao guardado como suposicao."));
    alvo.appendChild(nota);
  }
  var palpites = dado.palpites || [];
  if (!palpites.length) { return; }
  alvo.appendChild(criar("h3", null, "Antes de continuar: confirme ou recuse"));
  alvo.appendChild(criar("p", "dica",
    "Isto o programa concluiu do seu texto, e ninguem confirmou. Enquanto estiver aqui " +
    "nao vale como decisao, nao destrava pergunta nenhuma e impede a especificacao de " +
    "se declarar completa. Confianca alta nao dispensa a confirmacao."));
  palpites.forEach(function (p) {
    var caixa = criar("div", "palpite");
    caixa.appendChild(criar("h4", null, "Isto envolve " + p.valor + "?"));
    caixa.appendChild(criar("span", "conf", "confianca " + p.confianca));
    caixa.appendChild(criar("p", "prova", p.evidencia));
    caixa.appendChild(criar("p", "dica", "O trecho acima e o que produziu esta conclusao."));
    var acoes = criar("div", "acoes");
    var sim = criar("button", "acao", "Sim, e o caso");
    sim.type = "button";
    sim.addEventListener("click", function () { resolverPalpite(p.valor, true, acoes); });
    var nao = criar("button", "acao acao--secundaria", "Nao e o caso");
    nao.type = "button";
    nao.addEventListener("click", function () { resolverPalpite(p.valor, false, acoes); });
    acoes.appendChild(sim);
    acoes.appendChild(nao);
    caixa.appendChild(acoes);
    alvo.appendChild(caixa);
  });
}

function desenharPergunta(dado) {
  var alvo = q("#pergunta");
  alvo.textContent = "";
  var p = dado.pergunta;
  if (!p) {
    var fim = criar("div", "pergunta");
    fim.appendChild(criar("h3", null, "Nao ha mais pergunta que valha o seu tempo"));
    fim.appendChild(criar("p", null,
      "O que sobrou tem valor informativo abaixo do limiar do motor, e por isso nao " +
      "sera perguntado. Nada disso foi preenchido com valor assumido: tudo sai na " +
      "especificacao como decisao aberta, com a pergunta inteira."));
    alvo.appendChild(fim);
    return;
  }
  var caixa = criar("div", "pergunta");
  caixa.appendChild(criar("span", "id", p.id + " - peso " + p.peso +
    (p.universal ? " - vale para qualquer software" : " - vale para o seu caso")));
  caixa.appendChild(criar("h3", null, p.pergunta));

  var motivo = criar("p", "porque", p.porque);
  motivo.classList.add("oculto");
  var btnPorque = criar("button", "acao acao--secundaria", "Por que essa pergunta?");
  btnPorque.type = "button";
  btnPorque.addEventListener("click", function () {
    var escondido = motivo.classList.toggle("oculto");
    btnPorque.textContent = escondido ? "Por que essa pergunta?" : "Esconder o motivo";
  });
  var linhaPorque = criar("div", "acoes");
  linhaPorque.style.marginTop = "10px";
  linhaPorque.appendChild(btnPorque);
  caixa.appendChild(linhaPorque);
  caixa.appendChild(motivo);

  if (p.opcoes && p.opcoes.length) {
    caixa.appendChild(criar("p", "dica", "Caminhos mais comuns - clicar responde na hora:"));
    var linha = criar("div", "opcoes");
    p.opcoes.forEach(function (opcao) {
      var b = criar("button", "opcao", opcao);
      b.type = "button";
      b.addEventListener("click", function () { responder(p.id, opcao); });
      linha.appendChild(b);
    });
    caixa.appendChild(linha);
    caixa.appendChild(criar("p", "dica",
      "As opcoes nao restringem a resposta: se o seu caso e outro, escreva abaixo."));
  }

  var rotulo = criar("label", "rotulo-campo",
    p.opcoes && p.opcoes.length ? "Ou responda com as suas palavras" : "Responda com as suas palavras");
  rotulo.setAttribute("for", "resposta-livre");
  caixa.appendChild(rotulo);
  var campo = document.createElement("textarea");
  campo.className = "livre";
  campo.id = "resposta-livre";
  campo.rows = 3;
  campo.maxLength = 2000;
  caixa.appendChild(campo);
  var acoes = criar("div", "acoes");
  acoes.style.marginTop = "10px";
  var enviar = criar("button", "acao", "Gravar e ver a proxima pergunta");
  enviar.type = "button";
  enviar.addEventListener("click", function () { responder(p.id, campo.value); });
  acoes.appendChild(enviar);
  caixa.appendChild(acoes);
  var erro = criar("div");
  erro.id = "erro-pergunta";
  caixa.appendChild(erro);
  alvo.appendChild(caixa);
}

function desenharEstado(dado) {
  estado.ultimo = dado;
  desenharProgresso(dado.progresso);
  desenharPalpites(dado);
  desenharPergunta(dado);
}

async function responder(lacunaId, valor) {
  if (!valor || !valor.trim()) {
    mostrarErro("#erro-pergunta",
      "Escreva a resposta no campo, ou clique numa das opcoes oferecidas.");
    return;
  }
  try {
    desenharEstado(await pedir("/api/descoberta/responder", "POST", {
      sessao: estado.sessao, lacuna_id: lacunaId, valor: valor
    }));
  } catch (erro) {
    mostrarErro("#erro-pergunta", erro.message);
  }
}

async function resolverPalpite(valor, aceitar, acoes) {
  Array.prototype.forEach.call(acoes.children, function (b) { b.disabled = true; });
  try {
    desenharEstado(await pedir("/api/descoberta/palpite", "POST", {
      sessao: estado.sessao, valor: valor, aceitar: aceitar
    }));
  } catch (erro) {
    Array.prototype.forEach.call(acoes.children, function (b) { b.disabled = false; });
    mostrarErro("#palpites", erro.message);
  }
}

/* --- passo 3: especificacao ------------------------------------------ */

function copiar(texto, botao) {
  function ok() {
    botao.textContent = "Copiado";
    setTimeout(function () { botao.textContent = "Copiar"; }, 1800);
  }
  function pelaArea() {
    var area = q("#area-copia");
    area.value = texto;
    area.focus();
    area.select();
    var deu = false;
    try { deu = document.execCommand("copy"); } catch (erro) { deu = false; }
    area.blur();
    if (deu) { ok(); return; }
    botao.textContent = "Copie com Ctrl+C";
    window.getSelection().selectAllChildren(q("#markdown-spec"));
  }
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(texto).then(ok, pelaArea);
  } else {
    pelaArea();
  }
}

function listaDeLacunas(itens) {
  var ul = criar("ul", "lista-lacunas");
  if (!itens.length) {
    ul.appendChild(criar("li", "vazio", "Nenhuma."));
    return ul;
  }
  itens.forEach(function (l) {
    var li = criar("li");
    li.appendChild(criar("span", "p", l.pergunta));
    li.appendChild(criar("span", "m", l.id + " - peso " + l.peso + " - " + l.porque));
    ul.appendChild(li);
  });
  return ul;
}

function listaDePalpites(itens) {
  var ul = criar("ul", "lista-lacunas");
  if (!itens.length) {
    ul.appendChild(criar("li", "vazio", "Nenhuma. Toda inferencia foi confirmada ou recusada."));
    return ul;
  }
  itens.forEach(function (p) {
    var li = criar("li");
    li.appendChild(criar("span", "p", p.valor + " - confianca " + p.confianca));
    li.appendChild(criar("span", "m", "evidencia: " + p.evidencia));
    ul.appendChild(li);
  });
  return ul;
}

function desenharSpec(dado) {
  var alvo = q("#spec");
  alvo.textContent = "";

  var cabeca = criar("div", "topo-linha");
  cabeca.appendChild(criar("h3", null, "Estado da especificacao"));
  cabeca.appendChild(criar("span",
    "selo-estado selo-estado--" + (dado.completa ? "completa" : "incompleta"),
    dado.completa ? "completa" : "incompleta"));
  alvo.appendChild(cabeca);

  if (dado.completa) {
    alvo.appendChild(criar("p", null,
      "Nenhuma pergunta que vale para qualquer software ficou sem resposta e nenhuma " +
      "inferencia ficou pendente. Decisao aberta de peso baixo pode existir, e ela " +
      "esta listada abaixo com a pergunta inteira."));
  } else {
    alvo.appendChild(criar("p", null,
      "Esta especificacao NAO esta completa, e nao deve ser tratada como pronta. " +
      "O motivo:"));
    var ul = criar("ul", "motivos");
    (dado.por_que_nao_completa || []).forEach(function (m) {
      ul.appendChild(criar("li", null, m));
    });
    if (!(dado.por_que_nao_completa || []).length) {
      ul.appendChild(criar("li", null,
        "o motor devolveu incompleta sem detalhar o motivo - volte ao passo 2 e " +
        "resolva o que ainda estiver aberto."));
    }
    alvo.appendChild(ul);
  }

  var mdCabeca = criar("div", "topo-linha");
  mdCabeca.style.marginTop = "18px";
  mdCabeca.appendChild(criar("h3", null, "Markdown"));
  var btnCopiar = criar("button", "acao acao--secundaria", "Copiar");
  btnCopiar.type = "button";
  btnCopiar.addEventListener("click", function () { copiar(dado.markdown, btnCopiar); });
  mdCabeca.appendChild(btnCopiar);
  alvo.appendChild(mdCabeca);
  var pre = criar("pre", "saida", dado.markdown);
  pre.id = "markdown-spec";
  alvo.appendChild(pre);

  var abertas = criar("div");
  abertas.style.marginTop = "18px";
  abertas.appendChild(criar("h3", null, "Decisoes abertas"));
  abertas.appendChild(criar("p", "dica",
    "Cada linha e uma pergunta sem resposta, com o motivo dela. Nenhuma foi " +
    "preenchida com valor plausivel no lugar."));
  abertas.appendChild(listaDeLacunas(dado.decisoes_abertas || []));
  alvo.appendChild(abertas);

  var inferidas = criar("div");
  inferidas.style.marginTop = "18px";
  inferidas.appendChild(criar("h3", null, "Inferencias nao confirmadas"));
  inferidas.appendChild(criar("p", "dica",
    "O programa concluiu isto do texto inicial e ninguem confirmou."));
  inferidas.appendChild(listaDePalpites(dado.inferencias_pendentes || []));
  alvo.appendChild(inferidas);
}

async function verSpec(botao) {
  var alvo = q("#passo-spec");
  alvo.classList.remove("oculto");
  q("#spec").textContent = "";
  q("#spec").appendChild(criar("p", "trabalhando", "Montando a especificacao..."));
  botao.disabled = true;
  try {
    desenharSpec(await pedir("/api/descoberta/especificacao/" + encodeURIComponent(estado.sessao)));
    alvo.scrollIntoView({ block: "start" });
  } catch (erro) {
    mostrarErro("#spec", erro.message);
  } finally {
    botao.disabled = false;
  }
}

/* --- tema ------------------------------------------------------------ */

var TEMAS = ["sistema", "claro", "escuro"];
var temaAtual = 0;

function aplicarTema() {
  var nome = TEMAS[temaAtual];
  if (nome === "sistema") {
    document.documentElement.removeAttribute("data-theme");
  } else {
    document.documentElement.setAttribute("data-theme", nome === "escuro" ? "dark" : "light");
  }
  q("#btn-tema").textContent = "Tema: " + nome;
}

/* --- arranque -------------------------------------------------------- */

q("#btn-tema").addEventListener("click", function () {
  temaAtual = (temaAtual + 1) % TEMAS.length;
  aplicarTema();
});
q("#btn-iniciar").addEventListener("click", function () { iniciar(q("#btn-iniciar")); });
q("#btn-spec").addEventListener("click", function () { verSpec(q("#btn-spec")); });
q("#ideia").addEventListener("input", atualizarContador);

aplicarTema();
desenharPlataformas();
desenharExemplos();
atualizarContador();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
