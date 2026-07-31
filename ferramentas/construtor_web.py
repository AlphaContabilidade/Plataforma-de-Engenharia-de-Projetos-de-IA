"""Servidor local e portátil do construtor de software.

Este módulo usa somente a biblioteca padrão. Ele entrega o mesmo widget usado
pelo adaptador MCP, mas sem exigir ChatGPT, Claude, Codex, chave de API ou conta
em um provedor. A IA escolhida pelo usuário entra depois, ao receber o Plano de
Solução produzido pela interface.
"""

from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from ferramentas.projetos import (
    ProjetoInvalido,
    gerar_blueprint,
    gerar_perguntas_personalizadas,
)


HOST = "127.0.0.1"
PORTA_PADRAO = 8765
TENTATIVAS_DE_PORTA = 20
LIMITE_REQUISICAO = 12 * 1024 * 1024
RAIZ = Path(__file__).resolve().parents[1]
WIDGET = RAIZ / "chatgpt_app" / "widget.html"


class ConstrutorHandler(BaseHTTPRequestHandler):
    """Rotas mínimas necessárias para a jornada guiada."""

    server_version = "AIEngineeringOS/1.0"

    def log_message(self, formato: str, *args: object) -> None:
        print(f"[construtor] {self.address_string()} - {formato % args}")

    def _responder(
        self,
        status: int,
        corpo: bytes,
        content_type: str,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.end_headers()
        self.wfile.write(corpo)

    def _json(self, status: int, dado: dict[str, Any]) -> None:
        corpo = json.dumps(dado, ensure_ascii=False).encode("utf-8")
        self._responder(status, corpo, "application/json; charset=utf-8")

    def _entrada_json(self) -> dict[str, Any]:
        tamanho_texto = self.headers.get("Content-Length", "")
        try:
            tamanho = int(tamanho_texto)
        except ValueError as erro:
            raise ProjetoInvalido("tamanho da requisição inválido") from erro
        if tamanho <= 0 or tamanho > LIMITE_REQUISICAO:
            raise ProjetoInvalido("requisição vazia ou maior que 12 MB")
        try:
            entrada = json.loads(self.rfile.read(tamanho).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as erro:
            raise ProjetoInvalido("JSON inválido") from erro
        if not isinstance(entrada, dict):
            raise ProjetoInvalido("a entrada deve ser um objeto JSON")
        return entrada

    def do_GET(self) -> None:  # noqa: N802 - contrato de BaseHTTPRequestHandler
        caminho = self.path.split("?", 1)[0]
        if caminho in ("/", "/widget.html"):
            self._responder(
                200,
                WIDGET.read_bytes(),
                "text/html; charset=utf-8",
            )
            return
        if caminho == "/saude":
            self._json(
                200,
                {
                    "status": "ok",
                    "motor": "Planejador determinístico AI-ENGINEERING-OS v1",
                    "dependencia_de_ia": False,
                },
            )
            return
        self._json(404, {"modo": "erro", "erro": "rota não encontrada"})

    def do_POST(self) -> None:  # noqa: N802 - contrato de BaseHTTPRequestHandler
        caminho = self.path.split("?", 1)[0]
        try:
            entrada = self._entrada_json()
            if caminho == "/api/perguntas":
                descoberta = gerar_perguntas_personalizadas(
                    entrada.get("ideia", ""),
                    entrada.get("tipo", "auto"),
                    entrada.get("modo", "novo"),
                )
                self._json(200, {"modo": "descoberta", **descoberta})
                return
            if caminho == "/api/planejar":
                blueprint = gerar_blueprint(entrada).para_dict()
                self._json(
                    200,
                    {"modo": "blueprint", "blueprint": blueprint, "stateVersion": 1},
                )
                return
            self._json(404, {"modo": "erro", "erro": "rota não encontrada"})
        except (AttributeError, TypeError, ValueError, ProjetoInvalido) as erro:
            self._json(400, {"modo": "erro", "erro": str(erro)})


class ServidorDoConstrutor(ThreadingHTTPServer):
    daemon_threads = True


def subir(porta: int = PORTA_PADRAO, *, fixa: bool = False) -> ServidorDoConstrutor:
    """Sobe em loopback e procura outra porta quando a preferida está ocupada."""

    tentativas = 1 if fixa or porta == 0 else TENTATIVAS_DE_PORTA
    ultima: OSError | None = None
    for deslocamento in range(tentativas):
        try:
            return ServidorDoConstrutor(
                (HOST, porta + deslocamento),
                ConstrutorHandler,
            )
        except OSError as erro:
            ultima = erro
    raise OSError(
        f"nenhuma porta disponível entre {porta} e "
        f"{porta + tentativas - 1}: {ultima}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Construtor local de software, independente de fornecedor de IA."
        )
    )
    parser.add_argument("--porta", type=int, default=None)
    parser.add_argument(
        "--sem-navegador",
        action="store_true",
        help="somente imprime o endereço, sem abrir o navegador",
    )
    args = parser.parse_args(argv)

    try:
        servidor = subir(
            args.porta if args.porta is not None else PORTA_PADRAO,
            fixa=args.porta is not None,
        )
    except OSError as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 2

    porta = servidor.server_address[1]
    url = f"http://{HOST}:{porta}/widget.html"
    print("AI-ENGINEERING-OS - construtor universal")
    print(f"  interface: {url}")
    print("  IA obrigatória: não")
    print("  integração: copie o Plano de Solução para a IA de sua escolha")
    print("  Ctrl+C encerra o servidor")
    if not args.sem_navegador:
        webbrowser.open(url)

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando.")
    finally:
        servidor.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
