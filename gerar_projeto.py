"""Script principal: gera projeto completo em um comando.

Uso:
  python gerar_projeto.py --nome "Meu App" --tipo web

Ou interativo:
  python gerar_projeto.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ferramentas.projetos import gerar_blueprint
from codigo_generators import gerar_projeto_completo, exibir_resultado
from codigo_generators.deploy_prep import (
    preparar_deploy,
    listar_opcoes_deploy,
)


def main():
    parser = argparse.ArgumentParser(
        description="Gera projeto React + Node.js completo e executavel"
    )
    parser.add_argument(
        "--nome",
        help="Nome do projeto (ex: 'App de Tarefas')",
    )
    parser.add_argument(
        "--tipo",
        default="web",
        help="Tipo de projeto (web, mobile, api, etc)",
    )
    parser.add_argument(
        "--destino",
        default=".",
        help="Onde criar o projeto (default: diretorio atual)",
    )
    parser.add_argument(
        "--deploy",
        help="Preparar para deploy em (vercel, heroku, docker, etc)",
    )

    args = parser.parse_args()

    # Se nao passou nome, pede no chat
    if not args.nome:
        print("\nGERADOR DE PROJETO - Plataforma de IA Engineering")
        print("=" * 60)
        print("\nResponda as perguntas abaixo:\n")

        ideia = input("Qual eh a sua ideia? (ex: App para controlar habitos) > ")
        publico = input("Quem eh o publico? (ex: Profissionais ocupados) > ")
        problema = input("Qual problema resolve? > ")

        entrada = {
            "ideia": ideia,
            "tipo": args.tipo,
            "modo": "novo",
            "publico": publico,
            "problema": problema,
            "formato": "Web responsiva",
            "quantidade_usuarios": "1-100",
            "prioridade": "velocidade",
            "integracao": "Nenhuma no MVP",
            "dados_sensiveis": "Nao",
            "prazo_estimado": "2-4 semanas",
        }
    else:
        entrada = {
            "ideia": args.nome,
            "tipo": args.tipo,
            "modo": "novo",
            "publico": "Usuarios",
            "problema": "Resolver um problema",
            "formato": "Web responsiva",
            "quantidade_usuarios": "1-100",
            "prioridade": "velocidade",
            "integracao": "Nenhuma no MVP",
            "dados_sensiveis": "Nao",
            "prazo_estimado": "2-4 semanas",
        }

    print("\n" + "=" * 60)
    print("Gerando projeto...")
    print("=" * 60 + "\n")

    # Gera blueprint
    blueprint = gerar_blueprint(entrada)

    # Gera projeto completo
    resultado = gerar_projeto_completo(
        blueprint.para_dict(),
        Path(args.destino),
    )

    exibir_resultado(resultado)

    if resultado.status == "sucesso":
        print(f"\nProjeto criado em: {resultado.diretorio}\n")

        # Deploy prep opcional
        if args.deploy:
            print(f"Preparando para deploy em {args.deploy}...")
            config = preparar_deploy(resultado.diretorio, args.deploy)
            print(config.instrucoes)

        elif resultado.status == "sucesso":
            print("\nOpcoes de deploy disponíveis:")
            for plat, desc in listar_opcoes_deploy().items():
                print(f"  {plat:20} - {desc}")
            print("\nUse: python gerar_projeto.py --deploy <plataforma>")

        print("\n" + "=" * 60)
        print("PROXIMO PASSO")
        print("=" * 60)
        print(f"cd {resultado.diretorio.name}")
        print("cd backend && npm install && npm start")
        print("\n[Em outro terminal]")
        print("cd ../frontend && npm install && npm run dev")


if __name__ == "__main__":
    main()
