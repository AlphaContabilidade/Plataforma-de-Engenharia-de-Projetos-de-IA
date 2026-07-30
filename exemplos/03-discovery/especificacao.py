"""A saida: o que foi decidido, o que ficou aberto, e o que nunca foi confirmado.

Uma especificacao honesta tem tres listas, nao uma. A primeira e o que foi
respondido, com a procedencia de cada resposta. A segunda e o que ficou aberto --
lacuna ativa sem resposta, apresentada com a pergunta inteira e nunca com um valor
adotado no lugar. A terceira e o que o programa inferiu e ninguem confirmou.

A terceira lista e a que costuma nao existir, e a ausencia dela e o defeito. Sem
ela, a inferencia razoavel do inicio da conversa chega ao fim indistinguivel de uma
resposta, e quem for construir trata suposicao como requisito. Palpite pendente e
motivo suficiente para a especificacao **nao** se declarar completa, porque ela
depende de uma coisa que ninguem afirmou.

`completa` e a implementacao local da proibicao de status que mente: assim como a
plataforma proibe gravar `PRONTO` com gate vermelho, uma especificacao com lacuna
universal aberta ou com inferencia pendente nao se declara completa. Nao existe
parametro para relaxar isso, e a ausencia do parametro e o desenho -- limiar
afrouxavel e limiar que sera afrouxado no dia do prazo.

O que este modulo deliberadamente NAO faz: nao pergunta, nao infere e nao decide o
que perguntar. Ele le uma `Entrevista` e a escreve. Ele tambem nao completa lacuna
faltante com padrao: `Origem.PADRAO_ASSUMIDO` existe nomeado em `deteccao.py` para
que se possa proibi-lo de aparecer aqui sem que alguem o tenha escrito de proposito.
"""

from __future__ import annotations

from dataclasses import dataclass

from catalogo import Contexto, Lacuna, Plataforma
from deteccao import Origem, Palpite
from entrevista import Entrevista


@dataclass(frozen=True, slots=True)
class Especificacao:
    """O resultado de uma entrevista, congelado no momento em que foi gerado.

    Congelada porque especificacao e um retrato: continuar a conversa produz outra
    especificacao, e ter as duas permite comparar. Objeto mutavel aqui deixaria a
    versao que foi para a construcao indistinguivel da versao de agora.

    `respostas` e uma tupla de `(id, valor, origem)`. A origem viaja junto e nao ao
    lado: uma resposta e o rotulo de como ela foi obtida sao a mesma informacao, e
    separa-los e o comeco de perder o rotulo.

    `decisoes_abertas` guarda a `Lacuna` inteira, e nao apenas o id. Quem le a
    especificacao precisa da pergunta e do motivo dela sem ter de abrir o catalogo,
    porque a decisao aberta e justamente a parte que alguem vai ter de resolver.
    """

    ideia: str
    plataformas: tuple[Plataforma, ...]
    contextos: tuple[Contexto, ...]
    respostas: tuple[tuple[str, str, Origem], ...]
    inferencias_pendentes: tuple[Palpite, ...]
    decisoes_abertas: tuple[Lacuna, ...]

    @property
    def completa(self) -> bool:
        """`True` somente sem inferencia pendente e sem lacuna universal aberta.

        As duas condicoes sao independentes e nenhuma delas e negociavel.

        Inferencia pendente e uma afirmacao que ninguem fez. Ela pode estar certa --
        e provavelmente esta, senao nao teria sido inferida -- e isso e irrelevante:
        o que a torna inutilizavel e nao se saber. Declarar-se completa com palpite
        pendente e transformar acerto provavel em requisito.

        Lacuna universal aberta e ausencia de algo que vale para qualquer software.
        Nao ha caso em que "que problema isso resolve" seja dispensavel. Lacuna
        **condicional** aberta nao impede a completude, e a assimetria e deliberada:
        pergunta de peso baixo que o motor escolheu nao fazer continua listada como
        aberta, e listar e o suficiente. Se ela impedisse a completude, a unica saida
        seria perguntar tudo -- e perguntar tudo e o anti-padrao que o limiar existe
        para evitar.
        """
        if self.inferencias_pendentes:
            return False
        return not any(lacuna.universal for lacuna in self.decisoes_abertas)

    def markdown(self) -> str:
        """A especificacao em markdown, com as duas secoes que costumam faltar.

        As secoes de decisoes abertas e de inferencias nao confirmadas sao escritas
        **sempre**, mesmo vazias, e a razao e de leitura: secao ausente e lida como
        "nao havia nada disso", que e o mesmo texto que sai quando ninguem olhou.
        Escrever "Nenhuma" e uma afirmacao; omitir a secao nao e nada.

        Nenhum valor assumido aparece como decidido em ponto nenhum. Onde nao houve
        resposta sai a pergunta, e nao um valor plausivel: a linha de uma decisao
        aberta e a pergunta original mais o motivo dela, exatamente o que alguem
        precisa para decidir.
        """
        linhas: list[str] = [
            "# Especificacao",
            "",
            f"**Ideia inicial:** {self.ideia.strip() or '(nao informada)'}",
            "",
            f"**Estado:** {'completa' if self.completa else 'incompleta'}",
            "",
            "## Plataformas confirmadas",
            "",
        ]
        linhas.append(
            ", ".join(self.plataformas)
            if self.plataformas
            else "Nenhuma confirmada. Sem plataforma nao se sabe onde isso roda."
        )
        linhas += ["", "## Contextos confirmados", ""]
        linhas.append(
            ", ".join(self.contextos)
            if self.contextos
            else "Nenhum. Ausencia de contexto e resultado legitimo."
        )

        linhas += ["", "## Decidido", ""]
        if self.respostas:
            linhas += ["| Lacuna | Resposta | Origem |", "|---|---|---|"]
            linhas += [
                f"| {chave} | {valor} | {origem} |" for chave, valor, origem in self.respostas
            ]
        else:
            linhas.append("Nada decidido.")

        linhas += ["", "## Decisoes abertas", ""]
        if self.decisoes_abertas:
            linhas.append(
                "Cada linha e uma pergunta sem resposta. Nenhuma delas foi preenchida "
                "com valor assumido."
            )
            linhas.append("")
            linhas += ["| Lacuna | Pergunta | Peso | Universal | Por que importa |", "|---|---|---|---|---|"]
            linhas += [
                f"| {lacuna.id} | {lacuna.pergunta} | {lacuna.peso} | "
                f"{'sim' if lacuna.universal else 'nao'} | {lacuna.porque} |"
                for lacuna in self.decisoes_abertas
            ]
        else:
            linhas.append("Nenhuma. Toda lacuna ativa recebeu resposta.")

        linhas += ["", "## Inferencias nao confirmadas", ""]
        if self.inferencias_pendentes:
            linhas.append(
                "O motor concluiu isto do texto inicial e ninguem confirmou. Enquanto "
                "constar aqui, nao vale como decisao."
            )
            linhas.append("")
            linhas += ["| Valor | Confianca | Evidencia |", "|---|---|---|"]
            linhas += [
                f"| {p.valor} | {p.confianca} | {p.evidencia} |"
                for p in self.inferencias_pendentes
            ]
        else:
            linhas.append("Nenhuma. Toda inferencia foi confirmada ou recusada.")

        return "\n".join(linhas) + "\n"


def gerar(entrevista: Entrevista) -> Especificacao:
    """Congela o estado atual da entrevista numa especificacao.

    Pode ser chamada em qualquer momento, inclusive no meio da conversa, e o
    resultado e valido: uma especificacao incompleta com tres decisoes abertas e um
    documento util, e negar a geracao antes do fim faria a unica saida do motor
    depender de a conversa ter terminado bem. O que a funcao nao faz e mentir sobre
    o estado -- `completa` responde por isso.
    """
    return Especificacao(
        ideia=entrevista.ideia,
        plataformas=entrevista.plataformas(),
        contextos=entrevista.contextos(),
        respostas=entrevista.respostas(),
        inferencias_pendentes=entrevista.palpites_pendentes(),
        decisoes_abertas=entrevista.decisoes_abertas(),
    )
