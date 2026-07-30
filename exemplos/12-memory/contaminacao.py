"""Separa evidencia de eco, e reporta contradicao em vez de resolve-la.

Dois defeitos reais de producao moram aqui. Os dois foram observados numa rotina
que escreve em sistema contabil, onde o erro custa dinheiro.

**O eco.** A automacao classifica, escreve no sistema, e a base de historico e
regenerada depois LENDO o proprio sistema -- inclusive as linhas que a automacao
acabou de gravar. Na rodada seguinte ela le a propria escrita como se fosse
observacao independente, encontra dominancia alta e se autoconfirma. Uma decisao
errada fica mais confiante a cada rodada, e o sinal de erro desaparece
exatamente quando o erro se consolida. Nao existe limiar de dominancia que
proteja contra isso: o numero cresce porque a amostra e o proprio eco.

**A contradicao silenciosa.** Uma base curada e congelada numa data passada
discordava do historico observado em quatro de quatro itens conferidos. Nada
sinalizava: quem consultasse a base primeiro obtinha uma resposta, quem
consultasse o historico primeiro obtinha outra, e as duas se apresentavam com a
mesma cara. A contradicao existia havia semanas.

A resposta deste modulo e assimetrica de proposito. O eco e **descartado**,
porque nao carrega informacao nova. A contradicao e **reportada**, porque carrega
informacao -- e escolher um lado em silencio e precisamente o defeito. Nenhuma
funcao daqui resolve contradicao; `precedencia.py` decide quem ganha, e leva a
contradicao junto no veredicto para que ela nunca desapareca do caminho.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from memoria_observada import Entrada, Origem, dominancia_de


@dataclass(frozen=True, slots=True)
class Contradicao:
    """Uma base congelada discordando da decisao dominante entre as observacoes.

    Carrega os cinco campos que permitem julgar sem reabrir o armazem: a chave,
    os dois lados do desacordo, quantas observacoes sustentam o lado observado e
    de quando e o congelamento. `n_observacoes` e a forca do lado observado --
    uma contradicao com uma observacao e um alerta, com trinta e um veredicto
    sobre a base. A estrutura nao pondera: quem le decide.
    """

    chave: str
    decisao_congelada: str
    decisao_observada: str
    n_observacoes: int
    congelada_em: date


def filtrar_contaminacao(
    entradas: Iterable[Entrada],
) -> tuple[tuple[Entrada, ...], tuple[Entrada, ...]]:
    """Devolve `(evidencia_valida, descartadas)`, preservando a ordem de entrada.

    A regra e uma linha e nao tem excecao: entrada com origem
    `ESCRITO_PELO_AGENTE` nunca conta como evidencia. Nao ha parametro para
    afrouxa-la, e a ausencia do parametro e a decisao de projeto -- um limiar
    configuravel viraria, no primeiro dia apertado, o caminho de volta ao defeito.

    As descartadas sao devolvidas em vez de sumirem porque a quantidade e um
    numero operacional: memoria cujo volume e majoritariamente eco esta medindo
    a propria atividade, e isso precisa aparecer no painel, nao no silencio.
    """
    validas: list[Entrada] = []
    descartadas: list[Entrada] = []
    for entrada in entradas:
        alvo = descartadas if entrada.origem is Origem.ESCRITO_PELO_AGENTE else validas
        alvo.append(entrada)
    return tuple(validas), tuple(descartadas)


def contradicoes(entradas: Iterable[Entrada]) -> tuple[Contradicao, ...]:
    """Toda base congelada que discorda da dominante entre as entradas `OBSERVADO`.

    Agrupa por chave, calcula a dominante considerando **apenas** origem
    `OBSERVADO` e compara com cada entrada `BASE_CONGELADA` da mesma chave. O
    recorte por origem e o que impede o eco de silenciar a contradicao: no
    defeito real, cinco escritas do proprio agente concordavam com a base
    congelada e a fariam parecer confirmada.

    O limiar de reporte e zero de proposito. Suprimir contradicao com poucas
    observacoes seria decidir em silencio que a base congelada esta certa -- o
    defeito que este modulo existe para tornar impossivel. A forca do sinal vai
    em `n_observacoes` e o julgamento fica com quem le.

    Sem entrada `OBSERVADO` nao ha contradicao: base congelada sozinha nao
    contradiz nada, ela apenas nao foi confirmada. Essa distincao aparece no
    veredicto como confianca baixa, e nao como contradicao.
    """
    por_chave: dict[str, list[Entrada]] = {}
    for entrada in entradas:
        por_chave.setdefault(entrada.chave, []).append(entrada)

    achadas: list[Contradicao] = []
    for chave, grupo in por_chave.items():
        observadas = [e for e in grupo if e.origem is Origem.OBSERVADO]
        dominante = dominancia_de(observadas)
        if dominante is None:
            continue
        decisao_observada, _ = dominante
        n = sum(1 for e in observadas if e.decisao == decisao_observada)
        for congelada in grupo:
            if congelada.origem is not Origem.BASE_CONGELADA:
                continue
            if congelada.decisao == decisao_observada:
                continue
            achadas.append(
                Contradicao(
                    chave=chave,
                    decisao_congelada=congelada.decisao,
                    decisao_observada=decisao_observada,
                    n_observacoes=n,
                    congelada_em=congelada.em,
                )
            )
    achadas.sort(key=lambda c: (c.chave, c.congelada_em, c.decisao_congelada))
    return tuple(achadas)
