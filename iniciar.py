"""Ponto de entrada universal da AI-ENGINEERING-OS.

Funciona após o clone apenas com Python 3.11+. Nenhuma API de IA é obrigatória.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parent
PYTHON_MINIMO = (3, 11)


def diagnostico() -> dict[str, object]:
    arquivos = [
        "AGENTS.md",
        "GUIA-DE-USO.md",
        "PROTOCOLO-UNIVERSAL-DA-IA.md",
        "chatgpt_app/widget.html",
        "00-INTRODUCAO/contrato.json",
    ]
    return {
        "plataforma": "AI-ENGINEERING-OS",
        "sistema": platform.system(),
        "python": platform.python_version(),
        "python_compativel": sys.version_info >= PYTHON_MINIMO,
        "arquivos_essenciais": {
            caminho: (RAIZ / caminho).is_file() for caminho in arquivos
        },
        "interface_sem_dependencias": True,
        "adaptador_mcp_disponivel": importlib.util.find_spec("mcp") is not None,
        "ia_obrigatoria": False,
    }


def mostrar_guia(nome_ia: str) -> None:
    ia = nome_ia.strip() or "IA escolhida"
    print(f"Adaptação para: {ia}")
    print("1. Leia AGENTS.md e PROTOCOLO-UNIVERSAL-DA-IA.md.")
    print("2. Rode: python iniciar.py verificar")
    print("3. Rode: python iniciar.py interface")
    print("4. Ajude a pessoa a responder uma pergunta simples por vez.")
    print("5. Use o Plano de Solução gerado como contrato inicial.")
    print("6. Antes de editar código, confirme perguntas abertas e escopo.")
    print("7. Implemente em etapas pequenas, rode testes e relate evidências.")
    print("8. Nunca afirme publicação ou funcionamento sem verificar.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inicializador universal da AI-ENGINEERING-OS"
    )
    sub = parser.add_subparsers(dest="comando")

    verificar = sub.add_parser("verificar", help="verifica o clone e o ambiente")
    verificar.add_argument("--json", action="store_true")

    interface = sub.add_parser(
        "interface",
        help="abre o construtor local sem exigir API de IA",
    )
    interface.add_argument("--porta", type=int, default=None)
    interface.add_argument("--sem-navegador", action="store_true")

    adaptar = sub.add_parser(
        "adaptar",
        help="mostra o protocolo para a IA que trabalhará no repositório",
    )
    adaptar.add_argument("--ia", default="IA escolhida")

    args = parser.parse_args(argv)
    comando = args.comando or "ajuda"

    if comando == "verificar":
        dado = diagnostico()
        if args.json:
            print(json.dumps(dado, ensure_ascii=False, indent=2))
        else:
            print("AI-ENGINEERING-OS - verificação do ambiente")
            print(f"  Python: {dado['python']}")
            print(
                "  Compatível: "
                + ("sim" if dado["python_compativel"] else "não; use Python 3.11+")
            )
            faltantes = [
                caminho
                for caminho, existe in dado["arquivos_essenciais"].items()
                if not existe
            ]
            print(
                "  Arquivos essenciais: "
                + ("ok" if not faltantes else "faltando " + ", ".join(faltantes))
            )
            print("  Interface local: pronta, sem chave de API")
            print("  Próximo passo: python iniciar.py interface")
        return 0 if dado["python_compativel"] and all(
            dado["arquivos_essenciais"].values()
        ) else 2

    if comando == "interface":
        from ferramentas.construtor_web import main as iniciar_interface

        argumentos: list[str] = []
        if args.porta is not None:
            argumentos.extend(["--porta", str(args.porta)])
        if args.sem_navegador:
            argumentos.append("--sem-navegador")
        return iniciar_interface(argumentos)

    if comando == "adaptar":
        mostrar_guia(args.ia)
        return 0

    parser.print_help()
    print("\nComece com: python iniciar.py verificar")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
