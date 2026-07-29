"""Registro de prompts versionado por conteudo, com ciclo de vida explicito.

Sem registro, "qual prompt estava em producao quando a taxa de acerto caiu" e
uma pergunta sem resposta. Aqui a versao e derivada do hash do contrato, nao de
um numero que alguem incrementa a mao -- registrar o mesmo conteudo duas vezes
devolve a versao existente, entao reimportar no deploy nao poluiu o historico.

A maquina de estados e a mesma do `stateDiagram-v2` do volume 07: os cinco nomes
de `Estado` existem em um unico lugar, e o diagrama do documento e a leitura
humana deste dicionario.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from prompt_template import PromptTemplate


class Estado(StrEnum):
    """Ciclo de vida de uma versao de prompt.

    `RASCUNHO` e o estado de quem ainda nao entrou no registro; toda versao
    registrada nasce em `VERSIONADO`. Ele existe no enum porque a transicao
    rascunho -> versionado e parte do fluxo documentado, mesmo acontecendo fora.
    """

    RASCUNHO = "RASCUNHO"
    VERSIONADO = "VERSIONADO"
    EM_AVALIACAO = "EM_AVALIACAO"
    PROMOVIDO = "PROMOVIDO"
    DEPRECIADO = "DEPRECIADO"


# Nenhum caminho leva direto de VERSIONADO a PROMOVIDO: prompt sem avaliacao nao
# promove. E DEPRECIADO e terminal -- ressuscitar versao antiga e registrar de
# novo, o que preserva a trilha em vez de reescreve-la.
TRANSICOES: dict[Estado, frozenset[Estado]] = {
    Estado.RASCUNHO: frozenset({Estado.VERSIONADO}),
    Estado.VERSIONADO: frozenset({Estado.EM_AVALIACAO, Estado.DEPRECIADO}),
    Estado.EM_AVALIACAO: frozenset({Estado.PROMOVIDO, Estado.VERSIONADO, Estado.DEPRECIADO}),
    Estado.PROMOVIDO: frozenset({Estado.DEPRECIADO}),
    Estado.DEPRECIADO: frozenset(),
}


class TransicaoInvalida(ValueError):
    """Transicao de estado nao prevista em `TRANSICOES`."""


class NaoRegistrado(KeyError):
    """Nome ou versao de prompt inexistente no registro."""


@dataclass(slots=True)
class _Entrada:
    """Uma versao registrada. Mutavel porque o estado dela e o que evolui."""

    versao: str
    template: PromptTemplate
    estado: Estado


class PromptRegistry:
    """Guarda versoes de prompt por nome e governa as transicoes de estado."""

    def __init__(self) -> None:
        self._por_nome: dict[str, list[_Entrada]] = {}

    def registrar(self, template: PromptTemplate) -> str:
        """Registra o template e devolve a versao (`"v1"`, `"v2"`, ...).

        Idempotente por hash: conteudo identico devolve a versao existente. E a
        identidade do conteudo que define a versao, e o hash cobre corpo, nome,
        tipo e obrigatoriedade das variaveis -- mudar so o tipo, ou so a
        obrigatoriedade, ja gera versao nova. O unico campo do contrato fora do
        hash e `descricao`, que nao altera o que `render` produz: editar so a
        descricao devolve a versao existente, de proposito.
        """
        entradas = self._por_nome.setdefault(template.nome, [])
        for entrada in entradas:
            if entrada.template.hash == template.hash:
                return entrada.versao
        versao = f"v{len(entradas) + 1}"
        entradas.append(_Entrada(versao, template, Estado.VERSIONADO))
        return versao

    def obter(self, nome: str, versao: str | None = None) -> PromptTemplate:
        """Devolve a versao pedida; sem versao, a promovida, e senao a ultima.

        O fallback para a ultima registrada e deliberado: em desenvolvimento nada
        foi promovido ainda, e exigir promocao para poder ler travaria o ciclo.
        """
        entradas = self._entradas(nome)
        if versao is None:
            versao = self.promovida(nome) or entradas[-1].versao
        return self._entrada(nome, versao).template

    def transicionar(self, nome: str, versao: str, destino: Estado) -> None:
        """Move a versao para `destino`, se `TRANSICOES` permitir.

        Promover mantem o invariante de uma promovida por nome: a versao que
        estava em `PROMOVIDO` cai para `DEPRECIADO` no mesmo passo, para que nunca
        exista instante em que duas versoes se declarem a de producao.
        """
        entrada = self._entrada(nome, versao)
        permitidos = TRANSICOES[entrada.estado]
        if destino not in permitidos:
            validos = ", ".join(sorted(permitidos)) or "nenhum (estado terminal)"
            raise TransicaoInvalida(
                f"{nome} {versao}: transicao {entrada.estado} -> {destino} invalida; "
                f"destinos validos a partir de {entrada.estado}: {validos}"
            )
        if destino is Estado.PROMOVIDO:
            for outra in self._por_nome[nome]:
                if outra.versao != versao and outra.estado is Estado.PROMOVIDO:
                    outra.estado = Estado.DEPRECIADO
        entrada.estado = destino

    def estado(self, nome: str, versao: str) -> Estado:
        return self._entrada(nome, versao).estado

    def historico(self, nome: str) -> tuple[tuple[str, str, Estado], ...]:
        """`(versao, hash, estado)` em ordem de registro -- a trilha de auditoria."""
        return tuple((e.versao, e.template.hash, e.estado) for e in self._entradas(nome))

    def promovida(self, nome: str) -> str | None:
        """Versao em `PROMOVIDO`, ou `None`. Por invariante, no maximo uma."""
        for entrada in self._entradas(nome):
            if entrada.estado is Estado.PROMOVIDO:
                return entrada.versao
        return None

    def _entradas(self, nome: str) -> list[_Entrada]:
        if nome not in self._por_nome:
            conhecidos = ", ".join(sorted(self._por_nome)) or "nenhum"
            raise NaoRegistrado(f"prompt {nome!r} nao registrado; conhecidos: {conhecidos}")
        return self._por_nome[nome]

    def _entrada(self, nome: str, versao: str) -> _Entrada:
        for entrada in self._entradas(nome):
            if entrada.versao == versao:
                return entrada
        disponiveis = ", ".join(e.versao for e in self._por_nome[nome])
        raise NaoRegistrado(
            f"prompt {nome!r} nao tem versao {versao!r}; disponiveis: {disponiveis}"
        )
