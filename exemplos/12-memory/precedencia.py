"""Quem ganha entre origens que discordam -- e o que responder quando ninguem ganha.

A regra-mestra que este modulo implementa vem da operacao real de onde ele foi
extraido: **se a evidencia nao decide, e pendencia humana.** No sistema original
essa regra existia no documento e nao no codigo. O classificador devolvia `None`
para dois estados que sao diferentes -- "nao ha evidencia" e "ha evidencia que
nao basta" -- e o chamador nao tinha como distinguir um do outro nem como saber
por que. Fechar a conta com um chute era, na pratica, um passo de distancia.

`Veredicto` corrige isso tornando o indeciso um resultado de primeira classe:
`decisao is None` significa pendencia humana, e `justificativa` diz exatamente
por que, com os numeros. Nenhum chute e emitido com confianca baixa para dar a
aparencia de resposta.

A segunda correcao esta na forma da precedencia. `PRECEDENCIA` **nao e cascata de
fallback**: a fonte de maior precedencia que estiver presente e a que responde, e
se ela nao decide, o veredicto e indeciso. Cair para a fonte seguinte quando a
observacao nao alcanca dominancia reintroduziria exatamente o defeito original --
uma base congelada decidindo o que a observacao independente nao sustentou.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from contaminacao import Contradicao, contradicoes, filtrar_contaminacao
from memoria_observada import Entrada, MemoriaObservada, Origem, contagem_de


class Confianca(StrEnum):
    """Quanto o veredicto se sustenta. Sempre `None` quando `decisao` e `None`.

    `ALTA` exige dominancia no minimo ou acima dele **e** nenhuma contradicao
    aberta. `MEDIA` e o rebaixamento por contradicao: a chave e conhecidamente
    inconsistente, e nenhum veredicto sobre chave inconsistente merece ser alto.
    `BAIXA` e a base congelada decidindo sozinha, sem confirmacao observada.
    """

    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAIXA = "BAIXA"


# `ESCRITO_PELO_AGENTE` esta fora da lista, e a ausencia e a regra: origem que nao
# aparece aqui nao decide nada. Deixa-la fora e mais forte que dar-lhe a ultima
# posicao, porque ultima posicao ainda decide quando as outras faltam -- e foi
# assim que o eco da propria escrita passou a se confirmar no sistema original.
PRECEDENCIA: tuple[Origem, ...] = (
    Origem.DECIDIDO_POR_HUMANO,
    Origem.OBSERVADO,
    Origem.BASE_CONGELADA,
)


@dataclass(frozen=True, slots=True)
class Veredicto:
    """O resultado de uma consulta. `decisao is None` e pendencia humana.

    `justificativa` nunca e vazia e carrega os numeros que sustentam ou negam a
    decisao -- e ela que transforma "nao deu" em algo acionavel. `descartadas`
    conta as entradas removidas por contaminacao, e `contradicoes` viaja no
    veredicto para que uma contradicao aberta nunca seja perdida no caminho,
    inclusive quando o veredicto e indeciso.
    """

    decisao: str | None
    confianca: Confianca | None
    justificativa: str
    descartadas: int
    contradicoes: tuple[Contradicao, ...]


def _mais_recente(candidatas: tuple[Entrada, ...]) -> Entrada:
    """A mais recente por data; empate de data resolve pela ultima registrada."""
    return max(enumerate(candidatas), key=lambda par: (par[1].em, par[0]))[1]


def resolver(
    memoria: MemoriaObservada,
    chave: str,
    *,
    hoje: date,
    janela_dias: int = 365,
    dominancia_minima: float = 0.7,
) -> Veredicto:
    """Resolve a chave contra a memoria e devolve um veredicto, sempre.

    Nunca levanta por falta de evidencia: memoria vazia, tudo contaminado ou tudo
    expirado devolvem veredicto indeciso com a justificativa dizendo qual dos tres
    casos ocorreu. Levantar e reservado a erro de programa -- chave em branco, que
    vem de `memoria.entradas`.

    A ordem das etapas importa e nao e negociavel. Primeiro descarta o eco,
    depois expira o que esta fora da janela, depois procura contradicao, e so
    entao aplica a precedencia. Procurar contradicao antes de descartar o eco
    deixaria o proprio agente silenciar a contradicao que ele mesmo criou.

    `hoje` e parametro em vez de `date.today()` por injecao de dependencia: com a
    data por fora, expiracao e testavel offline e de forma deterministica. Uma
    entrada com data futura nao esta expirada e conta; este componente nao
    policia relogio, e transformar isso em erro silencioso seria pior.

    `dominancia_minima` e piso inclusivo: 0,7 com minimo 0,7 decide. Empate entre
    duas decisoes nunca decide, independentemente do minimo -- a verificacao de
    empate e explicita para que a garantia nao dependa de o minimo ser maior que
    a metade.
    """
    todas = memoria.entradas(chave)
    validas, eco = filtrar_contaminacao(todas)
    vigentes = tuple(e for e in validas if (hoje - e.em).days <= janela_dias)
    expiradas = len(validas) - len(vigentes)
    abertas = contradicoes(vigentes)

    def descarte() -> str:
        """O que ficou fora da deliberacao, anexado a toda justificativa."""
        partes = []
        if eco:
            partes.append(f"{len(eco)} descartada(s) por contaminacao")
        if expiradas:
            partes.append(f"{expiradas} expirada(s) fora da janela de {janela_dias} dias")
        return f" [{'; '.join(partes)}]" if partes else ""

    def veredicto(
        decisao: str | None, confianca: Confianca | None, justificativa: str
    ) -> Veredicto:
        if decisao is not None and abertas:
            confianca = Confianca.MEDIA
            justificativa = (
                f"{justificativa}; {len(abertas)} contradicao(oes) aberta(s) entre base "
                f"congelada e observacao rebaixam a confianca"
            )
        return Veredicto(decisao, confianca, justificativa + descarte(), len(eco), abertas)

    for origem in PRECEDENCIA:
        candidatas = tuple(e for e in vigentes if e.origem is origem)
        if not candidatas:
            continue

        if origem is Origem.DECIDIDO_POR_HUMANO:
            escolhida = _mais_recente(candidatas)
            return veredicto(
                escolhida.decisao,
                Confianca.ALTA,
                f"decisao humana de {escolhida.em.isoformat()} para {chave!r}: "
                f"{Origem.DECIDIDO_POR_HUMANO} tem precedencia sobre qualquer "
                f"dominancia observada, inclusive contraria",
            )

        if origem is Origem.OBSERVADO:
            contagem = contagem_de(candidatas)
            itens = list(contagem.items())
            total = sum(contagem.values())
            decisao, n = itens[0]
            empatadas = [d for d, k in itens if k == n]
            if len(empatadas) > 1:
                return veredicto(
                    None,
                    None,
                    f"pendencia humana: empate entre {len(empatadas)} decisoes com {n} "
                    f"observacao(oes) cada ({', '.join(empatadas)}); empate nao decide",
                )
            fracao = n / total
            if fracao < dominancia_minima:
                return veredicto(
                    None,
                    None,
                    f"pendencia humana: dominancia observada {n}/{total} = {fracao:.3f} "
                    f"abaixo do minimo {dominancia_minima:.3f}; evidencia que nao decide "
                    f"nao passa a decidir por maioria simples",
                )
            return veredicto(
                decisao,
                Confianca.ALTA,
                f"dominancia observada {n}/{total} = {fracao:.3f}, minimo "
                f"{dominancia_minima:.3f}, em {total} observacao(oes) vigente(s) na "
                f"janela de {janela_dias} dias",
            )

        escolhida = _mais_recente(candidatas)
        return veredicto(
            escolhida.decisao,
            Confianca.BAIXA,
            f"nenhuma observacao vigente para {chave!r}: base congelada de "
            f"{escolhida.em.isoformat()} decide sozinha, sem confirmacao observada",
        )

    return veredicto(
        None,
        None,
        f"pendencia humana: nenhuma evidencia vigente para {chave!r}; "
        f"{len(todas)} entrada(s) no armazem",
    )
