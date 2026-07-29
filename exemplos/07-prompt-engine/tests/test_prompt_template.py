"""Testa o contrato tipado de PromptTemplate.

Os testes de hash existem porque o hash e o que o registry usa para decidir
idempotencia. Se o hash cobrisse apenas o texto, trocar o tipo -- ou a
obrigatoriedade -- de uma variavel produziria o mesmo hash e o registry devolveria
a versao antiga como se nada tivesse mudado; o contrato mudou, a versao tem de
mudar. O reverso tambem e testado: `descricao` nao entra no hash, e isso e
deliberado, porque descricao nenhuma altera a saida de `render`.
"""

import pytest

from prompt_template import ContratoViolado, PromptTemplate, Variavel

CORPO = "Resuma {texto} em {n} linhas. Tom: {tom}"


def _template(corpo: str = CORPO, variaveis: tuple[Variavel, ...] | None = None) -> PromptTemplate:
    if variaveis is None:
        variaveis = (
            Variavel("texto", str, descricao="texto de entrada"),
            Variavel("n", int),
            Variavel("tom", str, obrigatoria=False),
        )
    return PromptTemplate(nome="resumo", corpo=corpo, variaveis=variaveis)


def test_render_preenche_todas_as_variaveis():
    saida = _template().render(texto="um relatorio", n=3, tom="formal")
    assert saida == "Resuma um relatorio em 3 linhas. Tom: formal"


def test_obrigatoria_ausente_levanta():
    with pytest.raises(ContratoViolado, match="texto"):
        _template().render(n=3, tom="formal")


def test_tipo_errado_levanta():
    with pytest.raises(ContratoViolado, match="int"):
        _template().render(texto="x", n="tres", tom="formal")


def test_chave_extra_levanta():
    with pytest.raises(ContratoViolado, match="idioma"):
        _template().render(texto="x", n=3, tom="formal", idioma="pt")


def test_opcional_ausente_vira_string_vazia():
    assert _template().render(texto="x", n=1) == "Resuma x em 1 linhas. Tom: "


def test_placeholder_nao_declarado_levanta_no_construtor():
    with pytest.raises(ContratoViolado, match="idioma"):
        PromptTemplate(
            nome="resumo",
            corpo="Resuma {texto} em {idioma}",
            variaveis=(Variavel("texto", str),),
        )


def test_variavel_declarada_e_nao_usada_levanta_no_construtor():
    with pytest.raises(ContratoViolado, match="sobrando"):
        PromptTemplate(
            nome="resumo",
            corpo="Resuma {texto}",
            variaveis=(Variavel("texto", str), Variavel("n", int)),
        )


def test_assinatura_em_ordem_alfabetica_e_marca_a_opcional():
    """`tom` e opcional no contrato do fixture, e a assinatura registra isso com `?`."""
    assert _template().assinatura == "resumo(n:int, texto:str, tom?:str)"


def test_hash_estavel_entre_instancias_iguais():
    assert _template().hash == _template().hash
    assert len(_template().hash) == 12


def test_hash_muda_quando_o_corpo_muda():
    outro = _template(corpo=CORPO + " Seja objetivo.")
    assert outro.hash != _template().hash


def test_hash_muda_quando_o_tipo_de_uma_variavel_muda():
    """O hash cobre a assinatura, nao apenas o texto do prompt."""
    mesmo_texto_outro_contrato = _template(
        variaveis=(
            Variavel("texto", str),
            Variavel("n", float),
            Variavel("tom", str, obrigatoria=False),
        )
    )
    assert mesmo_texto_outro_contrato.corpo == _template().corpo
    assert mesmo_texto_outro_contrato.hash != _template().hash


def test_hash_muda_quando_a_obrigatoriedade_de_uma_variavel_muda():
    """Obrigatoriedade muda o comportamento de `render`, logo muda a identidade.

    Com `tom` obrigatoria, `render(texto=..., n=...)` levanta; com `tom` opcional,
    devolve texto com o placeholder vazio. Sao saidas diferentes para a mesma
    chamada -- se o hash fosse igual, o registry devolveria a versao antiga para
    um contrato que mudou de comportamento.
    """
    tom_obrigatorio = _template(
        variaveis=(
            Variavel("texto", str),
            Variavel("n", int),
            Variavel("tom", str, obrigatoria=True),
        )
    )
    tom_opcional = _template(
        variaveis=(
            Variavel("texto", str),
            Variavel("n", int),
            Variavel("tom", str, obrigatoria=False),
        )
    )
    assert tom_obrigatorio.corpo == tom_opcional.corpo
    assert tom_obrigatorio.assinatura != tom_opcional.assinatura
    assert tom_obrigatorio.hash != tom_opcional.hash


def test_hash_ignora_descricao():
    """Limite declarado: `descricao` e documentacao e nao altera saida de `render`."""
    com_descricao = _template(
        variaveis=(
            Variavel("texto", str, descricao="texto de entrada"),
            Variavel("n", int, descricao="numero de linhas"),
            Variavel("tom", str, obrigatoria=False, descricao="formal ou informal"),
        )
    )
    sem_descricao = _template(
        variaveis=(
            Variavel("texto", str),
            Variavel("n", int),
            Variavel("tom", str, obrigatoria=False),
        )
    )
    assert com_descricao.hash == sem_descricao.hash
