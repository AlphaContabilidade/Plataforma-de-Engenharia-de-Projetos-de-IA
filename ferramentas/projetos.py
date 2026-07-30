"""Descoberta guiada de software para a interface local.

Este modulo transforma respostas simples em um plano de solucao. Ele nao chama
modelo de IA e nao escreve codigo: a saida e deterministica, revisavel e pronta para
ser entregue a um agente construtor. Essa fronteira e deliberada. Perguntas e
recomendacoes precisam funcionar mesmo sem internet ou credencial configurada; a
geracao executavel entra numa etapa posterior, sempre com confirmacao humana.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class ProjetoInvalido(ValueError):
    """Entrada insuficiente ou fora do contrato do construtor."""


MOTOR_ELABORACAO = "Planejador determinístico AI-ENGINEERING-OS v1"


@dataclass(frozen=True)
class Blueprint:
    nome: str
    motor_elaboracao: str
    resumo: str
    mvp: tuple[str, ...]
    arquitetura: tuple[str, ...]
    fases: tuple[dict[str, object], ...]
    riscos: tuple[str, ...]
    perguntas_pendentes: tuple[str, ...]
    documentos_referencia: tuple[dict[str, object], ...]
    decisoes_descoberta: dict[str, str]
    volumes_recomendados: tuple[dict[str, str], ...]
    markdown: str

    def para_dict(self) -> dict[str, object]:
        return {
            "nome": self.nome,
            "motor_elaboracao": self.motor_elaboracao,
            "resumo": self.resumo,
            "mvp": list(self.mvp),
            "arquitetura": list(self.arquitetura),
            "fases": [dict(fase) for fase in self.fases],
            "riscos": list(self.riscos),
            "perguntas_pendentes": list(self.perguntas_pendentes),
            "documentos_referencia": [
                dict(documento) for documento in self.documentos_referencia
            ],
            "decisoes_descoberta": dict(self.decisoes_descoberta),
            "volumes_recomendados": [
                dict(volume) for volume in self.volumes_recomendados
            ],
            "markdown": self.markdown,
        }


_TIPOS = {
    "web": "aplicacao web responsiva",
    "mobile": "aplicativo movel",
    "automacao": "automacao de processo",
    "api": "API ou servico de integracao",
    "desktop": "aplicacao desktop",
}
_PRIORIDADES = {
    "velocidade": "colocar uma primeira versao utilizavel no ar rapidamente",
    "qualidade": "reduzir retrabalho e privilegiar qualidade desde a primeira entrega",
    "custo": "manter infraestrutura e operacao enxutas",
    "escala": "preparar crescimento de usuarios e volume de dados",
}


def gerar_perguntas_personalizadas(ideia: str, tipo: str = "auto") -> dict[str, object]:
    """Cria uma trilha curta de descoberta adaptada à ideia e à plataforma."""
    texto = str(ideia or "").strip()
    if len(texto) < 20:
        raise ProjetoInvalido("descreva a ideia com pelo menos 20 caracteres")
    normalizado = texto.casefold()
    if tipo == "auto":
        if any(p in normalizado for p in ("celular", "android", "iphone", "mobile", "aplicativo")):
            tipo = "mobile"
        elif any(p in normalizado for p in ("windows", "desktop", "computador", "pc", "offline")):
            tipo = "desktop"
        elif any(p in normalizado for p in ("automat", "robô", "robo", "processo repetitivo")):
            tipo = "automacao"
        else:
            tipo = "web"
    if tipo not in _TIPOS:
        raise ProjetoInvalido(f"tipo desconhecido: {tipo}")

    comercio = any(
        palavra in normalizado
        for palavra in ("loja", "venda", "e-commerce", "ecommerce", "pedido", "checkout", "marketplace")
    )
    saude = any(
        palavra in normalizado
        for palavra in ("saúde", "saude", "clínica", "clinica", "paciente", "médico", "medico")
    )
    financeiro = any(
        palavra in normalizado
        for palavra in ("finance", "pagamento", "banco", "contáb", "contab", "fatura")
    )

    perguntas: list[dict[str, object]] = [
        {
            "id": "publico",
            "titulo": "Quem usará este produto no dia a dia?",
            "ajuda": "Descreva o perfil principal, não apenas “todos”.",
            "tipo": "texto",
            "obrigatoria": True,
        },
        {
            "id": "problema",
            "titulo": "Qual dificuldade deve desaparecer primeiro?",
            "ajuda": "Conte como isso é resolvido hoje e onde ocorre perda de tempo, dinheiro ou qualidade.",
            "tipo": "texto",
            "obrigatoria": True,
        },
    ]
    if tipo == "mobile":
        perguntas.append(
            {
                "id": "recurso_plataforma",
                "titulo": "Qual recurso do celular é mais importante?",
                "ajuda": "Isso muda permissões, testes e arquitetura do aplicativo.",
                "tipo": "opcao",
                "obrigatoria": True,
                "opcoes": [
                    "Câmera ou leitura de código",
                    "Localização e mapas",
                    "Notificações",
                    "Uso offline",
                    "Nenhum recurso especial",
                ],
            }
        )
    elif tipo == "desktop":
        perguntas.append(
            {
                "id": "recurso_plataforma",
                "titulo": "Como o programa para PC deverá funcionar?",
                "ajuda": "Escolha o cenário mais próximo da operação real.",
                "tipo": "opcao",
                "obrigatoria": True,
                "opcoes": [
                    "Instalado e funcionando offline",
                    "Instalado, mas conectado à nuvem",
                    "Em rede dentro da empresa",
                    "Ainda não sei",
                ],
            }
        )
    elif tipo == "automacao":
        perguntas.append(
            {
                "id": "recurso_plataforma",
                "titulo": "Quando a automação encontrar uma exceção, o que deve acontecer?",
                "ajuda": "Automação profissional precisa de um caminho de decisão humana.",
                "tipo": "opcao",
                "obrigatoria": True,
                "opcoes": [
                    "Pausar e pedir aprovação",
                    "Registrar e continuar os demais casos",
                    "Tentar novamente automaticamente",
                    "Ainda precisa ser definido",
                ],
            }
        )
    else:
        perguntas.append(
            {
                "id": "recurso_plataforma",
                "titulo": "Como as pessoas acessarão o sistema?",
                "ajuda": "Isso orienta autenticação, permissões e distribuição.",
                "tipo": "opcao",
                "obrigatoria": True,
                "opcoes": [
                    "Conta individual com login",
                    "Acesso interno da empresa",
                    "Acesso público sem login",
                    "Ainda não sei",
                ],
            }
        )

    if comercio or financeiro:
        perguntas.append(
            {
                "id": "decisao_especifica",
                "titulo": "Como pagamentos ou cobranças deverão funcionar?",
                "ajuda": "Escolha uma direção inicial; provedores podem ser definidos depois.",
                "tipo": "opcao",
                "obrigatoria": True,
                "opcoes": [
                    "Pix e cartão",
                    "Assinatura recorrente",
                    "Pagamento fora do sistema",
                    "Sem pagamento nesta primeira versão",
                ],
            }
        )
    elif saude:
        perguntas.append(
            {
                "id": "decisao_especifica",
                "titulo": "Que tipo de informação de saúde será armazenada?",
                "ajuda": "Dados clínicos exigem controles diferentes de simples dados de contato.",
                "tipo": "opcao",
                "obrigatoria": True,
                "opcoes": [
                    "Prontuário ou informação clínica",
                    "Agenda e dados de contato",
                    "Somente indicadores sem identificação",
                    "Ainda precisa ser definido",
                ],
            }
        )

    perguntas.extend(
        [
            {
                "id": "estilo_visual",
                "titulo": "Qual direção visual combina com o produto?",
                "ajuda": "A escolha orienta o primeiro protótipo e pode ser alterada depois.",
                "tipo": "opcao",
                "obrigatoria": False,
                "opcoes": [
                    "Profissional e discreta",
                    "Moderna e tecnológica",
                    "Simples e acolhedora",
                    "Visual forte e marcante",
                    "Prefiro receber uma recomendação",
                ],
            },
            {
                "id": "prioridade",
                "titulo": "O que é mais importante na primeira entrega?",
                "ajuda": "Prazo, qualidade, custo e escala geram decisões diferentes.",
                "tipo": "opcao",
                "obrigatoria": True,
                "opcoes": [
                    "Qualidade e menos retrabalho",
                    "Primeira versão rapidamente",
                    "Custo inicial baixo",
                    "Preparar grande crescimento",
                ],
            },
        ]
    )
    return {
        "tipo_inferido": tipo,
        "categoria": "comercio" if comercio else "saude" if saude else "financeiro" if financeiro else "geral",
        "perguntas": perguntas,
    }

def _texto(dados: dict[str, Any], campo: str, *, obrigatorio: bool = False) -> str:
    valor = str(dados.get(campo) or "").strip()
    if len(valor) > 4_000:
        raise ProjetoInvalido(f"{campo} excede o limite de 4.000 caracteres")
    if obrigatorio and not valor:
        raise ProjetoInvalido(f"preencha o campo {campo}")
    return valor


def _lista(dados: dict[str, Any], campo: str) -> tuple[str, ...]:
    valor = dados.get(campo, ())
    if isinstance(valor, str):
        itens = valor.split(",")
    elif isinstance(valor, list):
        itens = valor
    else:
        raise ProjetoInvalido(f"{campo} deve ser texto ou lista")
    limpos = tuple(str(item).strip() for item in itens if str(item).strip())
    if len(limpos) > 20:
        raise ProjetoInvalido(f"{campo} aceita no maximo 20 itens")
    return limpos


def _sim_nao(dados: dict[str, Any], campo: str) -> bool:
    valor = dados.get(campo, False)
    if isinstance(valor, bool):
        return valor
    return str(valor).strip().lower() in {"sim", "true", "1", "yes"}


def _documentos(dados: dict[str, Any]) -> tuple[dict[str, object], ...]:
    """Valida referencias documentais e preserva texto seguro e limitado."""
    valor = dados.get("documentos", [])
    if valor in (None, ""):
        return ()
    if not isinstance(valor, list):
        raise ProjetoInvalido("documentos deve ser uma lista")
    if len(valor) > 10:
        raise ProjetoInvalido("anexe no maximo 10 documentos")

    resultado: list[dict[str, object]] = []
    total_texto = 0
    for indice, item in enumerate(valor, start=1):
        if not isinstance(item, dict):
            raise ProjetoInvalido(f"documento {indice} deve ser um objeto")
        nome = str(item.get("nome") or "").strip()
        if not nome or len(nome) > 240:
            raise ProjetoInvalido(f"documento {indice} precisa de um nome valido")
        tipo = str(item.get("tipo") or "application/octet-stream").strip()[:120]
        try:
            tamanho = max(0, int(item.get("tamanho") or 0))
        except (TypeError, ValueError) as erro:
            raise ProjetoInvalido(f"tamanho invalido no documento {nome}") from erro
        if tamanho > 5 * 1024 * 1024:
            raise ProjetoInvalido(f"{nome} excede o limite de 5 MB")
        conteudo = str(item.get("conteudo") or "").strip()
        if len(conteudo) > 20_000:
            conteudo = conteudo[:20_000]
        total_texto += len(conteudo)
        if total_texto > 60_000:
            raise ProjetoInvalido("o texto total dos documentos excede 60.000 caracteres")
        resultado.append(
            {
                "nome": nome,
                "tipo": tipo,
                "tamanho": tamanho,
                "conteudo": conteudo,
                "conteudo_disponivel": bool(conteudo),
            }
        )
    return tuple(resultado)


def _decisoes(dados: dict[str, Any]) -> dict[str, str]:
    valor = dados.get("respostas_descoberta") or {}
    if not isinstance(valor, dict):
        raise ProjetoInvalido("respostas_descoberta deve ser um objeto")
    if len(valor) > 20:
        raise ProjetoInvalido("respostas_descoberta aceita no maximo 20 itens")
    return {
        str(chave)[:80]: str(resposta).strip()[:1000]
        for chave, resposta in valor.items()
        if str(resposta).strip()
    }


def _volumes(
    tipo: str, dados_sensiveis: bool, integracoes: tuple[str, ...], prioridade: str
) -> tuple[dict[str, str], ...]:
    escolhidos: list[tuple[str, str, str]] = [
        ("03", "DISCOVERY", "transformar a ideia em problema e evidencia"),
        ("04", "REQUIREMENTS", "declarar escopo e criterios de aceite"),
        ("38", "PROJECT-PLANNER", "converter o plano de solucao em entregas verificaveis"),
        ("31", "TESTING", "proteger os fluxos essenciais com testes"),
    ]
    if tipo == "web":
        escolhidos.extend(
            [
                ("22", "FRONTEND-ARCHITECT", "desenhar a experiencia da interface"),
                ("23", "BACKEND-ARCHITECT", "organizar regras e servicos"),
            ]
        )
    elif tipo == "mobile":
        escolhidos.extend(
            [
                ("22", "FRONTEND-ARCHITECT", "desenhar a experiencia movel"),
                ("25", "API-ARCHITECT", "definir a comunicacao do aplicativo"),
            ]
        )
    elif tipo == "automacao":
        escolhidos.extend(
            [
                ("10", "WORKFLOW", "modelar etapas, estados e excecoes"),
                ("16", "INTEGRATION", "isolar sistemas externos"),
            ]
        )
    elif tipo == "api":
        escolhidos.extend(
            [
                ("25", "API-ARCHITECT", "versionar e proteger o contrato"),
                ("16", "INTEGRATION", "tratar falhas e idempotencia"),
            ]
        )
    else:
        escolhidos.append(
            ("23", "BACKEND-ARCHITECT", "separar interface, dominio e persistencia")
        )
    if integracoes:
        escolhidos.append(
            ("16", "INTEGRATION", "planejar contratos com as integracoes informadas")
        )
    if dados_sensiveis:
        escolhidos.extend(
            [
                ("17", "SECURITY", "definir controles para dados sensiveis"),
                ("30", "AI-GOVERNANCE", "registrar acesso, finalidade e retencao"),
            ]
        )
    if prioridade == "escala":
        escolhidos.extend(
            [
                ("33", "PERFORMANCE", "definir metas de carga e latencia"),
                ("21", "OBSERVABILITY", "medir comportamento em producao"),
            ]
        )

    unicos: dict[str, dict[str, str]] = {}
    for vol_id, nome, motivo in escolhidos:
        unicos.setdefault(vol_id, {"id": vol_id, "nome": nome, "motivo": motivo})
    return tuple(unicos.values())


def gerar_blueprint(dados: dict[str, Any]) -> Blueprint:
    """Valida respostas e gera um plano inicial honesto e acionavel."""
    if not isinstance(dados, dict):
        raise ProjetoInvalido("o corpo do projeto deve ser um objeto JSON")

    nome = _texto(dados, "nome") or "Novo produto"
    ideia = _texto(dados, "ideia", obrigatorio=True)
    publico = _texto(dados, "publico", obrigatorio=True)
    problema = _texto(dados, "problema", obrigatorio=True)
    tipo = _texto(dados, "tipo") or "web"
    prioridade = _texto(dados, "prioridade") or "qualidade"
    usuarios = _texto(dados, "usuarios") or "a confirmar"
    prazo = _texto(dados, "prazo")
    restricoes = _texto(dados, "restricoes")
    integracoes = _lista(dados, "integracoes")
    dados_sensiveis = _sim_nao(dados, "dados_sensiveis")
    documentos = _documentos(dados)
    decisoes = _decisoes(dados)

    if tipo not in _TIPOS:
        raise ProjetoInvalido(
            f"tipo desconhecido: {tipo}. Use: {', '.join(sorted(_TIPOS))}"
        )
    if prioridade not in _PRIORIDADES:
        raise ProjetoInvalido(
            "prioridade desconhecida. Use: " + ", ".join(sorted(_PRIORIDADES))
        )

    resumo = (
        f"{nome} sera uma {_TIPOS[tipo]} para {publico}. "
        f"O produto atacara o problema: {problema}. "
        f"A direcao de entrega e {_PRIORIDADES[prioridade]}."
    )

    mvp = [
        "Entrada guiada com linguagem simples e exemplos",
        "Fluxo principal que resolve o problema declarado de ponta a ponta",
        "Confirmacao clara do resultado e possibilidade de corrigir dados",
        "Historico minimo das operacoes importantes",
        "Metricas de uso, erro e conclusao do fluxo principal",
    ]
    if tipo in {"web", "mobile", "desktop"}:
        mvp.insert(1, "Acesso seguro e perfil basico quando houver dados por usuario")
    if integracoes:
        mvp.append("Integracao inicial com " + ", ".join(integracoes))
    if tipo == "automacao":
        mvp.append("Fila de excecoes para casos que exigem decisao humana")
    if decisoes.get("recurso_plataforma"):
        mvp.append("Suporte inicial à decisão de plataforma: " + decisoes["recurso_plataforma"])
    if decisoes.get("decisao_especifica"):
        mvp.append("Regra específica validada: " + decisoes["decisao_especifica"])

    arquitetura = [
        f"Canal principal: {_TIPOS[tipo]}.",
        "Regras de negocio separadas da interface para permitir testes e evolucao.",
        "Persistencia com migracoes, trilha de auditoria e copia de seguranca.",
        "Entrega incremental: cada fase termina com demonstracao e criterio de aceite.",
    ]
    if integracoes:
        arquitetura.append(
            "Adaptadores isolados para sistemas externos, com timeout, repeticao segura e log."
        )
    if dados_sensiveis:
        arquitetura.append(
            "Criptografia, menor privilegio, consentimento/finalidade e politica de retencao."
        )
    if prioridade == "escala":
        arquitetura.append(
            "Metas mensuraveis de latencia, capacidade e custo antes de otimizar."
        )

    fases = (
        {
            "nome": "1. Descoberta",
            "resultado": "problema validado, jornada principal e fora de escopo",
            "criterios": [
                "publico e dor descritos sem jargao",
                "sucesso mensuravel definido",
            ],
        },
        {
            "nome": "2. Prototipo",
            "resultado": "fluxo clicavel validado com usuarios representativos",
            "criterios": [
                "tarefas principais compreendidas",
                "duvidas e abandonos registrados",
            ],
        },
        {
            "nome": "3. MVP executavel",
            "resultado": "primeira versao funcional com testes do caminho critico",
            "criterios": [
                "criterios de aceite verdes",
                "erros observaveis e recuperaveis",
            ],
        },
        {
            "nome": "4. Piloto e evolucao",
            "resultado": "uso real medido e backlog repriorizado por evidencia",
            "criterios": [
                "metricas comparadas com a linha de base",
                "proxima entrega decidida com dados",
            ],
        },
    )

    riscos = [
        "A ideia ainda pode conter mais de um produto; manter um unico fluxo principal no MVP.",
        "Prazo, custo e escopo precisam ser negociados juntos; fixar os tres aumenta risco.",
        "Automacao sem caminho de excecao pode transformar erro raro em operacao bloqueada.",
    ]
    if integracoes:
        riscos.append(
            "Integracoes externas podem mudar ou ficar indisponiveis; contratos e simuladores sao obrigatorios."
        )
    if dados_sensiveis:
        riscos.append(
            "Dados sensiveis elevam impacto de acesso indevido; seguranca entra no desenho, nao no final."
        )
    if documentos:
        riscos.append(
            "Documentos de referencia podem estar desatualizados ou conter premissas "
            "conflitantes; validar versao, autoria e prioridade antes de convertê-los em requisito."
        )

    pendentes = []
    if not prazo:
        pendentes.append("Existe uma data real ou evento que limita a primeira entrega?")
    if not integracoes:
        pendentes.append("O produto precisa conversar com algum sistema que ja existe?")
    if usuarios == "a confirmar":
        pendentes.append("Quantas pessoas usarao o produto no inicio e em doze meses?")
    if not restricoes:
        pendentes.append("Ha limite de orcamento, tecnologia, hospedagem ou equipe?")
    pendentes.extend(
        [
            "Qual numero mostrara que o problema melhorou depois do lancamento?",
            "Qual decisao nunca deve ser automatizada sem confirmacao humana?",
        ]
    )
    sem_texto = [str(doc["nome"]) for doc in documentos if not doc["conteudo_disponivel"]]
    if sem_texto:
        pendentes.append(
            "Confirmar no chat os pontos relevantes dos arquivos sem extracao de texto: "
            + ", ".join(sem_texto)
            + "."
        )

    volumes = _volumes(tipo, dados_sensiveis, integracoes, prioridade)
    blueprint_sem_markdown = {
        "nome": nome,
        "resumo": resumo,
        "ideia": ideia,
        "publico": publico,
        "problema": problema,
        "usuarios": usuarios,
        "prazo": prazo or "a confirmar",
        "restricoes": restricoes or "a confirmar",
        "mvp": tuple(mvp),
        "arquitetura": tuple(arquitetura),
        "fases": fases,
        "riscos": tuple(riscos),
        "perguntas_pendentes": tuple(pendentes),
        "documentos_referencia": documentos,
        "decisoes_descoberta": decisoes,
        "volumes_recomendados": volumes,
    }
    markdown = _para_markdown(blueprint_sem_markdown)
    return Blueprint(
        nome=nome,
        motor_elaboracao=MOTOR_ELABORACAO,
        resumo=resumo,
        mvp=tuple(mvp),
        arquitetura=tuple(arquitetura),
        fases=fases,
        riscos=tuple(riscos),
        perguntas_pendentes=tuple(pendentes),
        documentos_referencia=documentos,
        decisoes_descoberta=decisoes,
        volumes_recomendados=volumes,
        markdown=markdown,
    )


def _para_markdown(dado: dict[str, Any]) -> str:
    linhas = [
        f"# Plano de Solução — {dado['nome']}",
        "",
        f"**Motor de elaboração:** {MOTOR_ELABORACAO}",
        "**Modelo de IA no servidor:** nenhum; este documento é gerado por regras verificáveis.",
        "",
        "## Entendimento",
        "",
        dado["resumo"],
        "",
        f"**Ideia original:** {dado['ideia']}",
        f"**Público:** {dado['publico']}",
        f"**Problema:** {dado['problema']}",
        f"**Usuários esperados:** {dado['usuarios']}",
        f"**Prazo:** {dado['prazo']}",
        f"**Restrições:** {dado['restricoes']}",
        "",
        "## Documentos de referência",
        "",
    ]
    if dado["documentos_referencia"]:
        linhas.extend(
            "- "
            + str(documento["nome"])
            + (
                " — texto disponível para análise"
                if documento["conteudo_disponivel"]
                else " — referência anexada, sem extração automática de texto"
            )
            for documento in dado["documentos_referencia"]
        )
    else:
        linhas.append("- Nenhum documento anexado.")
    linhas.extend(["", "## Decisões da descoberta personalizada", ""])
    if dado["decisoes_descoberta"]:
        linhas.extend(
            f"- **{chave.replace('_', ' ').title()}:** {resposta}"
            for chave, resposta in dado["decisoes_descoberta"].items()
        )
    else:
        linhas.append("- Nenhuma decisão adicional registrada.")
    linhas.extend(["", "## Escopo inicial do MVP", ""])
    linhas.extend(f"- {item}" for item in dado["mvp"])
    linhas.extend(["", "## Direção de arquitetura", ""])
    linhas.extend(f"- {item}" for item in dado["arquitetura"])
    linhas.extend(["", "## Fases", ""])
    for fase in dado["fases"]:
        linhas.append(f"### {fase['nome']}")
        linhas.append("")
        linhas.append(str(fase["resultado"]))
        linhas.append("")
        linhas.extend(f"- {item}" for item in fase["criterios"])
        linhas.append("")
    linhas.extend(["## Riscos que precisam de decisão", ""])
    linhas.extend(f"- {item}" for item in dado["riscos"])
    linhas.extend(["", "## Perguntas ainda abertas", ""])
    linhas.extend(f"- {item}" for item in dado["perguntas_pendentes"])
    linhas.extend(["", "## Volumes do acervo recomendados", ""])
    linhas.extend(
        f"- `{v['id']}-{v['nome']}` — {v['motivo']}"
        for v in dado["volumes_recomendados"]
    )
    linhas.extend(
        [
            "",
            "## Próximo comando para um agente construtor",
            "",
            "Use este plano de solução como contrato inicial. Antes de escrever código, confirme "
            "as perguntas abertas, converta o MVP em critérios de aceite verificáveis e "
            "proponha a menor primeira fatia executável. Não invente integrações, regras "
            "legais, números ou decisões que não estejam declaradas.",
            "",
        ]
    )
    return "\n".join(linhas)
