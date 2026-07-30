"""O controle: qual pergunta vem agora, e quando vale a pena parar.

Duas decisoes moram aqui, e sao as duas que separam um motor de descoberta de um
formulario. A primeira e **qual pergunta**: a proxima e a que resolve mais
incerteza entre as que fazem sentido, e nao a proxima de uma lista. A segunda e
**quando parar**: abaixo de um limiar de valor informativo, a pergunta nao e feita
-- ela sai na especificacao como decisao aberta.

Por que parar e obrigatorio. Interrogatorio de quarenta itens e abandonado no
decimo quinto, e o que fica nao e uma especificacao com vinte e cinco lacunas
declaradas: e uma conversa interrompida, com a pessoa mais impaciente do que
comecou e sem registro de onde parou. Perguntar tudo tem a aparencia de rigor e o
efeito de nao priorizar. O limiar e parametro (`peso_minimo`) porque o ponto certo
depende de quanto custa errar no dominio, e este componente nao tem opiniao sobre
isso -- ele tem opiniao sobre o limiar existir.

Terceira decisao, esta negativa: **inferencia nao entra sozinha.** Um palpite de
`deteccao.py` fica em `palpites_pendentes` ate alguem confirmar ou recusar. Recusar
nao e ignorar -- e remover da pendencia sem aplicar, o que faz a inferencia deixar
de constar como pendente e nunca constar como resposta.

O que este modulo deliberadamente NAO faz: nao formata saida e nao julga se a
especificacao esta completa. Isso e `especificacao.py`, que le este objeto e nao
escreve nele.
"""

from __future__ import annotations

from collections.abc import Iterable

from catalogo import CATALOGO, Contexto, Lacuna, Plataforma, lacunas_ativas, validar_catalogo
from deteccao import Origem, Palpite, detectar_contextos, detectar_plataformas

PESO_MINIMO_PADRAO = 4


class LacunaDesconhecida(KeyError):
    """Id respondido que nao existe no catalogo.

    Levanta em vez de ignorar porque isso e erro de programa com consequencia
    silenciosa: um id digitado errado guardaria a resposta em um balde que ninguem
    le, a lacuna verdadeira continuaria pendente, e a especificacao sairia sem a
    resposta que a pessoa deu -- com a agravante de que a pessoa lembra de ter
    respondido. Herda de `KeyError` porque e exatamente isso: chave ausente.
    """


class PalpiteDesconhecido(ValueError):
    """Palpite cujo valor nao e nome de plataforma nem de contexto.

    Confirmar um palpite aplica o valor dele ao conjunto de plataformas ou de
    contextos. Valor que nao corresponde a nenhum dos dois nao teria onde ser
    aplicado, e aceitar em silencio faria a confirmacao parecer ter funcionado sem
    destravar nada -- o pior dos dois mundos, porque a pessoa acha que respondeu.
    """


def _como_plataforma_ou_contexto(valor: str) -> Plataforma | Contexto:
    """Traduz o texto do palpite para o membro correspondente das enumeracoes."""
    limpo = (valor or "").strip().upper()
    for enumeracao in (Plataforma, Contexto):
        try:
            return enumeracao(limpo)
        except ValueError:
            continue
    raise PalpiteDesconhecido(
        f"valor {valor!r} nao e plataforma nem contexto conhecido; aceitos: "
        f"{', '.join([*Plataforma, *Contexto])}"
    )


class Entrevista:
    """O estado de uma conversa: o que foi inferido, o que foi respondido, o que falta.

    Mutavel de proposito -- e o unico objeto mutavel do exemplo, e a mutacao e o
    proprio assunto. Tudo o que ele devolve, no entanto, e imutavel: tuplas e
    objetos congelados, para que o chamador nao consiga alterar o estado por dentro
    de um resultado de consulta.
    """

    def __init__(
        self,
        ideia: str,
        *,
        peso_minimo: int = PESO_MINIMO_PADRAO,
        catalogo: Iterable[Lacuna] = CATALOGO,
    ) -> None:
        """Guarda a ideia e roda a deteccao uma vez, sem aplicar nada.

        A deteccao roda no construtor porque a frase inicial nao muda depois: rodar
        de novo a cada consulta daria a mesma resposta com mais trabalho, e rodar
        sob demanda tornaria `palpites_pendentes` uma consulta com efeito colateral.

        `peso_minimo` e `catalogo` sao injecao de dependencia pelo mesmo motivo que
        `hoje` e parametro no volume 12: com o limiar por fora, o comportamento de
        parada e testavel sem depender do conteudo real do catalogo, e o catalogo
        real e testavel sem depender do limiar padrao.
        """
        self._ideia = ideia
        self._peso_minimo = peso_minimo
        self._catalogo = validar_catalogo(catalogo)
        self._por_id: dict[str, Lacuna] = {lacuna.id: lacuna for lacuna in self._catalogo}
        self._plataformas: set[Plataforma] = set()
        self._contextos: set[Contexto] = set()
        self._palpites: list[Palpite] = [
            *detectar_plataformas(ideia),
            *detectar_contextos(ideia),
        ]
        self._respostas: dict[str, tuple[str, Origem]] = {}

    # --- Leitura do estado

    @property
    def ideia(self) -> str:
        """A frase inicial, como a pessoa escreveu."""
        return self._ideia

    @property
    def peso_minimo(self) -> int:
        """O limiar abaixo do qual a pergunta nao e feita."""
        return self._peso_minimo

    def plataformas(self) -> tuple[Plataforma, ...]:
        """Plataformas confirmadas, em ordem de declaracao da enumeracao."""
        return tuple(p for p in Plataforma if p in self._plataformas)

    def contextos(self) -> tuple[Contexto, ...]:
        """Contextos confirmados, em ordem de declaracao da enumeracao."""
        return tuple(c for c in Contexto if c in self._contextos)

    def palpites_pendentes(self) -> tuple[Palpite, ...]:
        """Inferencias que ainda nao foram confirmadas nem recusadas.

        Enquanto esta tupla nao esta vazia, o conjunto de lacunas ativas pode
        mudar, e por isso o laco de entrevista resolve palpite antes de perguntar.
        Fazer o contrario e gastar turno numa pergunta de navegador enquanto um
        palpite de aparelho de mao espera confirmacao.
        """
        return tuple(self._palpites)

    def respostas(self) -> tuple[tuple[str, str, Origem], ...]:
        """(id, valor, origem) na ordem em que foram respondidas.

        Ordem de resposta e nao ordem de catalogo: a sequencia real da conversa e
        informacao, e ela some se a saida for reordenada para ficar arrumada.
        """
        return tuple((chave, valor, origem) for chave, (valor, origem) in self._respostas.items())

    def ativas(self) -> tuple[Lacuna, ...]:
        """Todas as lacunas que fazem sentido agora, respondidas ou nao."""
        return lacunas_ativas(self._plataformas, self._contextos, catalogo=self._catalogo)

    def pendentes(self) -> tuple[Lacuna, ...]:
        """Ativas, sem resposta e com peso suficiente -- as que ainda serao feitas.

        Ordenadas por peso decrescente e, no empate, pela ordem do catalogo. E a
        mesma ordem que `proxima` percorre, exposta inteira para que a interface
        possa mostrar o que vem adiante sem reimplementar o criterio de ordenacao.
        """
        return self._ordenar(
            lacuna
            for lacuna in self.ativas()
            if lacuna.id not in self._respostas and lacuna.peso >= self._peso_minimo
        )

    def decisoes_abertas(self) -> tuple[Lacuna, ...]:
        """Ativas e sem resposta, **inclusive** as de peso abaixo do minimo.

        E a lista que vai para a especificacao. Ela inclui deliberadamente o que
        nunca sera perguntado: nao perguntar e uma escolha de economia de turno, e
        nao uma licenca para adotar valor por conta propria. A lacuna aparece na
        saida como aberta, com a pergunta inteira, para quem for construir decidir
        com o olho aberto.
        """
        return self._ordenar(
            lacuna for lacuna in self.ativas() if lacuna.id not in self._respostas
        )

    def progresso(self) -> tuple[int, int]:
        """(respondidas, alvo) sobre as lacunas ativas que valem perguntar.

        `alvo` conta as ativas com peso suficiente **somadas as ja respondidas**, e
        por isso ele **cresce** quando uma confirmacao destrava um bloco novo:
        confirmar aparelho de mao acrescenta quatro lacunas, e o denominador sobe.
        Progresso que so anda para frente exigiria fingir que o total era conhecido
        desde o inicio, e num grafo de decisao ele nao e. Barra honesta que recua e
        melhor que barra bonita que mente.
        """
        ativas = self.ativas()
        respondidas = sum(1 for lacuna in ativas if lacuna.id in self._respostas)
        a_fazer = sum(
            1
            for lacuna in ativas
            if lacuna.id not in self._respostas and lacuna.peso >= self._peso_minimo
        )
        return respondidas, respondidas + a_fazer

    def proxima(self) -> Lacuna | None:
        """A lacuna ativa, sem resposta, de maior peso. `None` quando nao vale mais.

        `None` significa uma coisa so: nao existe lacuna ativa acima do limiar. Nao
        significa que a especificacao esta completa -- palpite pendente e decisao
        aberta continuam podendo existir, e sao `especificacao.py` que os julga.

        Empate resolve pela ordem do catalogo, nunca por sorteio. Determinismo aqui
        nao e preferencia estetica: entrevista que muda de ordem entre execucoes nao
        se reproduz, e a primeira reclamacao de "ele me perguntou outra coisa" nao
        tem como ser investigada.
        """
        candidatas = self.pendentes()
        return candidatas[0] if candidatas else None

    def porque(self, lacuna_id: str) -> str:
        """O motivo declarado da pergunta -- a resposta a "por que isso importa?".

        Existe como metodo, e nao como algo que a interface monta, porque a
        justificativa e conteudo revisado do catalogo. Texto gerado na hora seria
        plausivel e nao seria revisavel.
        """
        return self._exigir(lacuna_id).porque

    # --- Mutacao do estado

    def confirmar(self, palpite: Palpite) -> None:
        """Aceita a inferencia: remove da pendencia e aplica plataforma ou contexto.

        Aplicar pode destravar um bloco inteiro de lacunas, e e por isso que a
        confirmacao vem antes das perguntas no laco. Confirmar duas vezes o mesmo
        palpite e inofensivo -- conjunto nao duplica, e a segunda remocao nao acha
        nada para remover.
        """
        alvo = _como_plataforma_ou_contexto(palpite.valor)
        self._esquecer(palpite)
        if isinstance(alvo, Plataforma):
            self._plataformas.add(alvo)
        else:
            self._contextos.add(alvo)

    def recusar(self, palpite: Palpite) -> None:
        """Rejeita a inferencia: remove da pendencia e **nao** aplica nada.

        Recusar e diferente de ignorar. Ignorado, o palpite continua pendente e
        impede a especificacao de se declarar completa -- corretamente, porque
        ninguem olhou. Recusado, ele sai da pendencia e nao deixa rastro de valor
        assumido em lugar nenhum: nem em `respostas`, nem no conjunto de
        plataformas, nem nas decisoes abertas.
        """
        _como_plataforma_ou_contexto(palpite.valor)
        self._esquecer(palpite)

    def responder(
        self, lacuna_id: str, valor: str, origem: Origem = Origem.RESPONDIDO
    ) -> None:
        """Grava a resposta de uma lacuna, com a origem dela.

        `origem` e parametro com padrao `RESPONDIDO` para que o caso comum seja
        curto e o caso incomum seja explicito: gravar algo como `INFERIDO` ou
        `PADRAO_ASSUMIDO` exige escrever a palavra, e a palavra viaja ate a
        especificacao, onde a secao de origem a mostra.

        Responder tambem pode destravar. Se o valor corresponder a uma plataforma ou
        a um contexto -- o caso da lacuna `onde_roda`, cujas opcoes sao exatamente os
        nomes das plataformas -- o conjunto e atualizado e o bloco correspondente
        entra. A regra e generica e nao trata nenhum id de forma especial, porque
        caso especial por id transforma o catalogo em codigo.

        Responder de novo o mesmo id **substitui** o valor e preserva a posicao na
        ordem da conversa. Correcao e normal em entrevista; virar entrada nova no
        fim faria a ordem mentir sobre quando o assunto foi tratado.
        """
        self._exigir(lacuna_id)
        self._respostas[lacuna_id] = (valor, origem)
        try:
            alvo = _como_plataforma_ou_contexto(valor)
        except PalpiteDesconhecido:
            return
        if isinstance(alvo, Plataforma):
            self._plataformas.add(alvo)
        else:
            self._contextos.add(alvo)

    # --- Internos

    def _exigir(self, lacuna_id: str) -> Lacuna:
        if lacuna_id not in self._por_id:
            raise LacunaDesconhecida(
                f"lacuna {lacuna_id!r} nao existe no catalogo; a resposta iria para um "
                "balde que ninguem le e a lacuna verdadeira continuaria pendente"
            )
        return self._por_id[lacuna_id]

    def _esquecer(self, palpite: Palpite) -> None:
        self._palpites = [outro for outro in self._palpites if outro != palpite]

    def _ordenar(self, lacunas: Iterable[Lacuna]) -> tuple[Lacuna, ...]:
        """Peso decrescente, empate pela ordem do catalogo. Sem sorteio em ponto nenhum."""
        posicao = {lacuna.id: n for n, lacuna in enumerate(self._catalogo)}
        return tuple(sorted(lacunas, key=lambda lacuna: (-lacuna.peso, posicao[lacuna.id])))
