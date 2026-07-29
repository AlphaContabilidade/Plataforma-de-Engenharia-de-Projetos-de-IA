"""Prompt como contrato tipado, nao como string solta no meio do codigo.

Prompt em f-string espalhado pelo codigo e divida: ninguem sabe quais variaveis
ele exige, ninguem detecta quando alguem apaga um placeholder, e nao existe
identidade estavel para versionar ou avaliar. Este modulo troca isso por um
contrato: o corpo e as variaveis declaradas tem de concordar, e a concordancia
e verificada na construcao -- falha cedo, no import, nao em producao.

O hash cobre corpo E assinatura de proposito. Duas versoes com o mesmo texto e
tipos diferentes sao contratos diferentes; se o hash ignorasse a assinatura, o
registry trataria a segunda como identica a primeira e nunca criaria a versao.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

# Somente identificadores Python: e o que `render` sabe substituir, e restringir
# a gramatica evita que chave literal de JSON no corpo pareca placeholder.
_PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


class ContratoViolado(ValueError):
    """O corpo e as variaveis declaradas discordam, ou `render` recebeu valor invalido."""


@dataclass(frozen=True, slots=True)
class Variavel:
    """Uma variavel do prompt: nome, tipo esperado e obrigatoriedade.

    `tipo` e uma classe e nao uma anotacao de texto porque `render` valida com
    `isinstance` -- validacao que roda, em vez de documentacao que envelhece.
    """

    nome: str
    tipo: type
    obrigatoria: bool = True
    descricao: str = ""


@dataclass(frozen=True)
class PromptTemplate:
    """Um prompt versionavel: corpo, contrato de variaveis e identidade estavel."""

    nome: str
    corpo: str
    variaveis: tuple[Variavel, ...]

    def __post_init__(self) -> None:
        """Reprova divergencia nas duas direcoes.

        Placeholder sem declaracao quebraria em `render`; variavel declarada e
        nao usada e contrato mentiroso -- quem le a assinatura acredita que ela
        influencia a saida. As duas sao erro de programacao, logo levantam.
        """
        usados = set(_PLACEHOLDER.findall(self.corpo))
        declarados = {v.nome for v in self.variaveis}
        faltando = sorted(usados - declarados)
        sobrando = sorted(declarados - usados)
        if faltando or sobrando:
            raise ContratoViolado(
                f"{self.nome}: corpo e contrato divergem - "
                f"placeholders sem declaracao: {faltando}; "
                f"variaveis declaradas e nao usadas (sobrando): {sobrando}"
            )

    def render(self, **valores: object) -> str:
        """Substitui os placeholders, validando o contrato antes.

        A substituicao e por regex, e nao por `str.format`, porque prompt que
        pede saida em JSON carrega chaves literais que fariam `format` quebrar.
        """
        declaradas = {v.nome: v for v in self.variaveis}
        extras = sorted(set(valores) - set(declaradas))
        if extras:
            raise ContratoViolado(
                f"{self.nome}: variaveis nao declaradas no contrato: {extras}"
            )

        concretos: dict[str, str] = {}
        for nome, variavel in declaradas.items():
            if nome not in valores:
                if variavel.obrigatoria:
                    raise ContratoViolado(
                        f"{self.nome}: variavel obrigatoria ausente: {nome}"
                    )
                concretos[nome] = ""
                continue
            valor = valores[nome]
            if not isinstance(valor, variavel.tipo):
                raise ContratoViolado(
                    f"{self.nome}: variavel {nome} esperava {variavel.tipo.__name__}, "
                    f"recebeu {type(valor).__name__}"
                )
            concretos[nome] = str(valor)
        return _PLACEHOLDER.sub(lambda m: concretos[m.group(1)], self.corpo)

    @property
    def assinatura(self) -> str:
        """`"nome(v1:int, v2:str)"`, em ordem alfabetica.

        A ordem e alfabetica, e nao a de declaracao, para que reordenar a tupla
        de variaveis nao mude o hash: reordenar nao muda o contrato.
        """
        ordenadas = sorted(self.variaveis, key=lambda v: v.nome)
        campos = ", ".join(f"{v.nome}:{v.tipo.__name__}" for v in ordenadas)
        return f"{self.nome}({campos})"

    @property
    def hash(self) -> str:
        """Identidade do conteudo: 12 hexdigitos de sha256 sobre corpo + assinatura.

        O `\\x00` separa os dois campos para que nenhuma concatenacao de corpo e
        assinatura possa colidir com outra combinacao.
        """
        semente = f"{self.corpo}\x00{self.assinatura}".encode("utf-8")
        return hashlib.sha256(semente).hexdigest()[:12]
