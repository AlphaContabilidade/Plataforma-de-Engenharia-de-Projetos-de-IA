"""Armazem de decisoes observadas, com a procedencia de cada evidencia gravada.

Extraido de uma rotina de conciliacao financeira em producao, onde classificar
errado custa dinheiro de verdade. La o classificador consultava duas fontes --
uma base curada e congelada numa data passada, e o historico do que foi
realmente observado -- e a que respondia primeiro ganhava. Quando as duas
discordavam, nada sinalizava: a precedencia era um acidente da ordem das linhas
de codigo, e a contradicao ficava semanas sem ser vista.

Este modulo troca isso por um armazem que grava **de onde cada decisao veio**.
`Origem` nao e metadado decorativo: e o que permite a `contaminacao.py`
descartar o que o proprio agente escreveu e a `precedencia.py` decidir quem
ganha, com a regra declarada em um lugar so. Memoria que guarda decisoes sem
guardar procedencia nao consegue distinguir evidencia de eco da propria escrita,
e uma decisao errada que se le de volta fica mais confiante a cada rodada.

O que o armazem deliberadamente NAO faz: nao filtra, nao pondera e nao decide.
`contagem` e `dominancia` sao numeros crus sobre tudo o que foi registrado --
inclusive o eco do agente. Limpar mora em `contaminacao.py` e decidir mora em
`precedencia.py`. A separacao e o que torna a filtragem visivel: se o armazem
filtrasse por conta propria, a escolha ficaria embutida e ninguem a auditaria.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class ChaveInvalida(ValueError):
    """Chave vazia ou so com espaco.

    Levanta em vez de reportar porque isso e erro de programa, nao ausencia de
    evidencia: a chave e a identidade da decisao, e um balde de identidade vazia
    soma observacoes sem relacao alguma. A dominancia desse balde seria um numero
    inventado com aparencia de evidencia -- pior que numero nenhum.
    """


class Origem(StrEnum):
    """De onde a decisao veio. A ordem de declaracao NAO e a precedencia.

    A precedencia mora em `precedencia.PRECEDENCIA`, em um lugar so, porque
    escrever a ordem duas vezes e como as duas fontes do sistema original
    passaram a divergir. Aqui os quatro valores apenas nomeiam procedencias:

    - `OBSERVADO`: registro que existia independentemente deste agente.
    - `ESCRITO_PELO_AGENTE`: registro que este agente produziu. Nunca e
      evidencia -- ler a propria escrita e o sistema se ouvindo.
    - `BASE_CONGELADA`: base curada, valida na data em que foi congelada. Pode
      ter envelhecido; discordancia com o observado e reportada, nao resolvida.
    - `DECIDIDO_POR_HUMANO`: decisao tomada por pessoa com autoridade. Vence.
    """

    OBSERVADO = "OBSERVADO"
    ESCRITO_PELO_AGENTE = "ESCRITO_PELO_AGENTE"
    BASE_CONGELADA = "BASE_CONGELADA"
    DECIDIDO_POR_HUMANO = "DECIDIDO_POR_HUMANO"


class DecisaoInvalida(ValueError):
    """Decisao vazia ou so com espaco. Irma de `ChaveInvalida`, e pelo mesmo motivo.

    Branco na decisao e erro de programa, nao ausencia de evidencia: uma decisao
    em branco entra como alternativa legitima, soma contagem, pode empatar com
    uma decisao real e chegar ao chamador dentro de um veredicto de confianca
    alta. Rejeitar aqui nao exige conhecimento de dominio nenhum -- e a mesma
    verificacao que a chave ja fazia, na simetria que faltava.

    O que esta excecao **nao** cobre e o valor-marcador de ausencia especifico de
    cada dominio, do tipo categoria generica que nao ensina nada. Essa lista e
    conhecimento de quem opera, fixa-la aqui seria decidir por todos os dominios,
    e por isso ela segue em `16-Roadmap.md`.
    """


def _sem_borda(valor: str) -> str:
    """Texto sem espaco de borda, tratando ausencia como vazio."""
    return (valor or "").strip()


def _chave_valida(chave: str) -> str:
    """Normaliza a borda e reprova o branco. Usado no registro e na consulta.

    O mesmo tratamento nos dois lados e o que garante que gravar `" k "` e
    consultar `"k"` alcancem o mesmo balde. Espaco de borda nao e identidade, e
    sem normalizar existiriam dois baldes para a mesma coisa -- cada um com
    metade das observacoes e nenhum com dominancia.
    """
    limpa = _sem_borda(chave)
    if not limpa:
        raise ChaveInvalida(
            f"chave {chave!r} vazia ou so com espaco: a chave e a identidade da "
            "decisao, e um balde sem identidade soma observacoes sem relacao"
        )
    return limpa


def _decisao_valida(decisao: str) -> str:
    """Normaliza a borda e reprova o branco, simetrico a `_chave_valida`.

    A normalizacao vem pelo mesmo argumento da chave: `"alfa"` e `" alfa "` sao a
    mesma decisao, e conta-las separado partiria a dominancia em duas metades sem
    que nada aparecesse errado. O branco levanta `DecisaoInvalida` porque decisao
    e o conteudo do veredicto, e veredicto com decisao vazia e resposta com cara
    de resposta.
    """
    limpa = _sem_borda(decisao)
    if not limpa:
        raise DecisaoInvalida(
            f"decisao {decisao!r} vazia ou so com espaco: decisao em branco nao e "
            "alternativa, e ela empataria ou venceria a contagem como se fosse"
        )
    return limpa


@dataclass(frozen=True, slots=True)
class Entrada:
    """Uma decisao observada, com procedencia e data.

    Congelada porque evidencia registrada nao se edita: corrigir e registrar uma
    entrada nova, o que preserva a trilha em vez de reescreve-la. `evidencia` e
    texto livre com o que sustentou a decisao -- fica fora de qualquer contagem
    e existe para o diagnostico humano, que sem ele depende de reexecutar.

    `chave` e `decisao` recebem o mesmo tratamento de borda e a mesma recusa ao
    branco, com uma excecao propria cada. `evidencia` nao recebe: ela nao entra em
    contagem nenhuma, e evidencia vazia e ausencia de diagnostico, nao erro.
    """

    chave: str
    decisao: str
    origem: Origem
    em: date
    evidencia: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "chave", _chave_valida(self.chave))
        object.__setattr__(self, "decisao", _decisao_valida(self.decisao))


def contagem_de(entradas: Iterable[Entrada]) -> dict[str, int]:
    """Quantas vezes cada decisao aparece, da mais frequente para a menos.

    A ordem e estavel -- contagem decrescente, desempate alfabetico -- e nao a
    ordem de registro. Ordem instavel faria a dominancia de um empate depender
    de qual observacao chegou primeiro, o que e sorte disfarcada de criterio.
    """
    bruto: dict[str, int] = {}
    for entrada in entradas:
        bruto[entrada.decisao] = bruto.get(entrada.decisao, 0) + 1
    return dict(sorted(bruto.items(), key=lambda par: (-par[1], par[0])))


def dominancia_de(entradas: Iterable[Entrada]) -> tuple[str, float] | None:
    """Decisao mais frequente e sua fracao do total, ou `None` se nao ha entrada.

    A fracao nao e arredondada de proposito: arredondar antes de comparar com um
    limiar move o limiar. Quem for exibir o numero arredonda na exibicao.
    """
    contagem = contagem_de(entradas)
    if not contagem:
        return None
    total = sum(contagem.values())
    decisao, n = next(iter(contagem.items()))
    return decisao, n / total


class MemoriaObservada:
    """Guarda entradas por chave, em ordem de registro, sem julgar nenhuma."""

    def __init__(self) -> None:
        self._por_chave: dict[str, list[Entrada]] = {}

    def registrar(self, entrada: Entrada) -> None:
        """Anexa a entrada ao balde da chave dela. Nunca substitui, nunca deduplica.

        Nao deduplicar e deliberado: duas observacoes iguais em datas diferentes
        sao duas observacoes, e e a repeticao que constroi dominancia. Deduplicar
        aqui apagaria justamente o sinal que a dominancia mede.
        """
        self._por_chave.setdefault(entrada.chave, []).append(entrada)

    def entradas(self, chave: str) -> tuple[Entrada, ...]:
        """Tudo o que foi registrado para a chave, em ordem de registro.

        Chave desconhecida devolve tupla vazia em vez de levantar: ausencia de
        evidencia e estado normal do dominio -- e o estado que produz pendencia
        humana -- e nao erro de programa. Chave em branco continua levantando.
        """
        return tuple(self._por_chave.get(_chave_valida(chave), ()))

    def contagem(self, chave: str) -> dict[str, int]:
        """Contagem crua por decisao, incluindo o eco do agente.

        Crua de proposito. Quem precisa de evidencia limpa passa as entradas por
        `contaminacao.filtrar_contaminacao` antes de contar; o armazem nao decide
        por ninguem qual origem vale.
        """
        return contagem_de(self.entradas(chave))

    def dominancia(self, chave: str) -> tuple[str, float] | None:
        """Decisao dominante e fracao, sobre a contagem crua. `None` se nao ha entrada."""
        return dominancia_de(self.entradas(chave))

    def chaves(self) -> tuple[str, ...]:
        """As chaves conhecidas, na ordem em que apareceram pela primeira vez."""
        return tuple(self._por_chave)
