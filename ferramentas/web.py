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
import json
import re
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

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

# Limite do corpo de POST que o handler aceita ler antes de descartar. Os POSTs
# desta interface nao tem corpo; o limite existe so para nao ficar lendo um corpo
# arbitrario de um cliente qualquer.
_LIMITE_DE_CORPO = 64 * 1024


class IdRecusado(ValueError):
    """Id de volume que nao passa na validacao contra o contrato."""


def raiz_padrao() -> Path:
    """A pasta da plataforma, deduzida de `__file__` - nunca do diretorio atual.

    O servidor nao pode depender de onde foi lancado. Quem sobe esta interface
    pelo mecanismo de preview do harness lanca o processo da raiz do repositorio
    (`CLAUDE/`), nao de dentro de `AI-ENGINEERING-OS/`; com raiz igual a `.` o
    arranque morreria com "contrato ausente" por um detalhe de cwd, e a mensagem
    culparia o contrato em vez do lancamento.

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
    "/api/acervo": ("GET",),
}
_ROTAS_COM_ID: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("/api/volume/", ("GET",)),
    ("/api/briefing/", ("GET",)),
    ("/api/gates/", ("POST",)),
)


def responder(
    metodo: str,
    caminho: str,
    raiz: Path,
    ct: Contrato,
    *,
    rodar_testes: bool = True,
) -> tuple[int, str, bytes]:
    """Resolve uma requisicao e devolve `(status, content_type, corpo)`.

    Toda a decisao da interface esta aqui, e nada aqui depende de socket. E o que
    permite testar a interface inteira sem porta livre e sem navegador: o handler
    de `http.server` so converte esta tripla em resposta HTTP.
    """
    metodo = (metodo or "").upper()
    caminho = normalizar_caminho(caminho)

    if caminho in _ROTAS_EXATAS:
        if metodo not in _ROTAS_EXATAS[caminho]:
            return _erro(
                405,
                f"metodo {metodo} nao vale em {caminho}. Use "
                f"{' ou '.join(_ROTAS_EXATAS[caminho])}.",
            )
        if caminho == "/":
            return 200, HTML_UTF8, PAGINA.encode("utf-8")
        return _json(200, dados_do_acervo(raiz, ct))

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
        "GET /api/volume/NN, GET /api/briefing/NN, POST /api/gates/NN.",
    )


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
        self._descartar_corpo()
        servidor = self.server
        try:
            status, tipo, corpo = responder(
                metodo, self.path, servidor.raiz, servidor.contrato  # type: ignore[attr-defined]
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

    def _descartar_corpo(self) -> None:
        """Le e joga fora o corpo, para nao dessincronizar a conexao.

        Nenhum endpoint desta interface le corpo de requisicao - o id do volume
        vem no caminho e nada mais e aceito. Mas deixar bytes nao lidos no socket
        com keep-alive faz a requisicao seguinte ser interpretada como corpo da
        anterior, e ai a pagina quebra sem motivo aparente.
        """
        try:
            tamanho = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            tamanho = 0
        if tamanho <= 0:
            return
        if tamanho > _LIMITE_DE_CORPO:
            self.close_connection = True
            return
        self.rfile.read(tamanho)

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
# A pagina. CSS e JS embutidos: sem CDN, sem framework, sem build.
# --------------------------------------------------------------------------

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
:root {
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

/* --- cabecalho ------------------------------------------------------- */
header.topo {
  border-bottom: 1px solid var(--linha);
  background: var(--papel);
}
.topo-linha { display: flex; flex-wrap: wrap; gap: 12px; align-items: baseline; justify-content: space-between; }
.selo {
  font-family: var(--mono); font-size: 0.72rem; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--acento);
  border: 1px solid var(--acento); border-radius: 2px; padding: 2px 8px;
}
.subtitulo { color: var(--texto-fraco); margin: 6px 0 0; max-width: 70ch; }
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
button.tema {
  font-family: var(--mono); font-size: 0.75rem; background: transparent;
  color: var(--texto-fraco); border: 1px solid var(--linha); border-radius: 2px;
  padding: 4px 10px; cursor: pointer;
}
button.tema:hover { border-color: var(--acento); color: var(--acento); }

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
.caixa { background: var(--papel); border: 1px solid var(--linha); border-radius: 3px; padding: 16px 18px; }

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
.dica { color: var(--texto-fraco); font-size: 0.8rem; margin-top: 10px; }

/* --- detalhe --------------------------------------------------------- */
.ficha dl { display: grid; grid-template-columns: max-content 1fr; gap: 4px 14px; margin: 12px 0 0; }
.ficha dt { font-family: var(--mono); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--texto-fraco); }
.ficha dd { margin: 0; }
.lista-secoes { display: flex; flex-wrap: wrap; gap: 5px; margin: 6px 0 0; padding: 0; list-style: none; }
.lista-secoes li { font-family: var(--mono); font-size: 0.72rem; border: 1px solid var(--linha); border-radius: 2px; padding: 1px 6px; }
.lista-secoes li.ausente { color: var(--reprovado); border-color: var(--reprovado); border-style: dashed; }
.lista-secoes li.presente { color: var(--aprovado); border-color: var(--aprovado); }
.bloco { margin-top: 18px; padding-top: 14px; border-top: 1px solid var(--linha); }
.acoes { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px; }
button.acao {
  font-family: var(--mono); font-size: 0.82rem; cursor: pointer;
  background: var(--acento); color: var(--papel); border: 1px solid var(--acento);
  border-radius: 3px; padding: 8px 14px;
}
button.acao--secundaria { background: transparent; color: var(--acento); }
button.acao:hover:not([disabled]) { filter: brightness(1.12); }
button.acao[disabled] { opacity: 0.55; cursor: progress; }
button.acao:focus-visible { outline: 2px solid var(--acento); outline-offset: 2px; }
.veredicto { border: 1px solid var(--linha); border-left: 4px solid var(--linha); border-radius: 3px; padding: 10px 12px; margin-top: 8px; }
.veredicto--ok { border-left-color: var(--aprovado); }
.veredicto--nao { border-left-color: var(--reprovado); }
.veredicto h4 { margin: 0; font-family: var(--titulo); font-size: 0.95rem; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.veredicto p { margin: 6px 0 0; font-family: var(--mono); font-size: 0.8rem; color: var(--texto-fraco); }
.grupo-regra { margin: 8px 0 0; }
.grupo-regra > span { font-family: var(--mono); font-size: 0.78rem; color: var(--reprovado); }
.grupo-regra ul { margin: 4px 0 0; padding-left: 20px; }
.grupo-regra li { font-family: var(--mono); font-size: 0.74rem; color: var(--texto-fraco); }
pre.saida {
  font-family: var(--mono); font-size: 0.76rem; background: var(--fundo);
  border: 1px solid var(--linha); border-radius: 3px; padding: 12px;
  max-height: 460px; overflow: auto; white-space: pre-wrap; word-break: break-word; margin: 8px 0 0;
}
.aviso { color: var(--reprovado); font-family: var(--mono); font-size: 0.8rem; margin-top: 8px; }
.trabalhando { color: var(--acento); font-family: var(--mono); font-size: 0.8rem; margin-top: 8px; }
.vazio { color: var(--texto-fraco); }
.escondido { position: absolute; left: -9999px; top: 0; }
footer.pe { margin-top: 30px; color: var(--texto-fraco); font-size: 0.78rem; font-family: var(--mono); }
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
      <button class="tema" id="btn-tema" type="button">Tema: sistema</button>
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


if __name__ == "__main__":
    raise SystemExit(main())
