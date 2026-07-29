"""Testa o registro versionado e a maquina de estados do prompt.

O teste da idempotencia por hash e o mais importante do arquivo: sem ele, cada
deploy que reimporta o mesmo prompt criaria uma versao nova, e o historico -- que
e a base da auditoria -- viraria ruido.
"""

import pytest

from prompt_registry import Estado, NaoRegistrado, PromptRegistry, TransicaoInvalida
from prompt_template import PromptTemplate, Variavel


def _tpl(corpo: str = "Resuma {texto}", nome: str = "resumo") -> PromptTemplate:
    return PromptTemplate(nome=nome, corpo=corpo, variaveis=(Variavel("texto", str),))


def _promover(reg: PromptRegistry, nome: str, versao: str) -> None:
    """Caminho legitimo ate PROMOVIDO: nenhuma versao promove sem passar por avaliacao."""
    reg.transicionar(nome, versao, Estado.EM_AVALIACAO)
    reg.transicionar(nome, versao, Estado.PROMOVIDO)


def test_estado_tem_exatamente_os_cinco_nomes_do_diagrama():
    assert [e.name for e in Estado] == [
        "RASCUNHO",
        "VERSIONADO",
        "EM_AVALIACAO",
        "PROMOVIDO",
        "DEPRECIADO",
    ]


def test_primeira_versao_e_v1_e_nasce_versionado():
    reg = PromptRegistry()
    assert reg.registrar(_tpl()) == "v1"
    assert reg.estado("resumo", "v1") is Estado.VERSIONADO


def test_corpo_diferente_gera_v2():
    reg = PromptRegistry()
    reg.registrar(_tpl())
    assert reg.registrar(_tpl(corpo="Resuma {texto} em tres linhas")) == "v2"


def test_mesmo_conteudo_e_idempotente():
    reg = PromptRegistry()
    reg.registrar(_tpl())
    assert reg.registrar(_tpl()) == "v1"
    assert len(reg.historico("resumo")) == 1


def test_obter_sem_versao_devolve_a_promovida():
    reg = PromptRegistry()
    reg.registrar(_tpl())
    reg.registrar(_tpl(corpo="Resuma {texto} em tres linhas"))
    _promover(reg, "resumo", "v1")
    assert reg.obter("resumo").corpo == "Resuma {texto}"


def test_obter_sem_promovida_devolve_a_ultima():
    reg = PromptRegistry()
    reg.registrar(_tpl())
    reg.registrar(_tpl(corpo="Resuma {texto} em tres linhas"))
    assert reg.obter("resumo").corpo == "Resuma {texto} em tres linhas"
    assert reg.promovida("resumo") is None


def test_obter_versao_explicita():
    reg = PromptRegistry()
    reg.registrar(_tpl())
    reg.registrar(_tpl(corpo="Resuma {texto} em tres linhas"))
    _promover(reg, "resumo", "v2")
    assert reg.obter("resumo", "v1").corpo == "Resuma {texto}"


def test_nome_inexistente_levanta_nao_registrado():
    reg = PromptRegistry()
    with pytest.raises(NaoRegistrado, match="inexistente"):
        reg.obter("inexistente")


def test_transicao_valida_muda_o_estado():
    reg = PromptRegistry()
    reg.registrar(_tpl())
    reg.transicionar("resumo", "v1", Estado.EM_AVALIACAO)
    assert reg.estado("resumo", "v1") is Estado.EM_AVALIACAO


def test_transicao_invalida_lista_os_destinos_validos():
    reg = PromptRegistry()
    reg.registrar(_tpl())

    with pytest.raises(TransicaoInvalida) as erro:
        reg.transicionar("resumo", "v1", Estado.PROMOVIDO)
    assert "EM_AVALIACAO" in str(erro.value) and "DEPRECIADO" in str(erro.value)

    reg.transicionar("resumo", "v1", Estado.DEPRECIADO)
    with pytest.raises(TransicaoInvalida) as erro:
        reg.transicionar("resumo", "v1", Estado.PROMOVIDO)
    assert "DEPRECIADO" in str(erro.value) and "nenhum" in str(erro.value)


def test_promover_uma_segunda_versao_deprecia_a_anterior():
    """Invariante: no maximo uma versao PROMOVIDO por nome."""
    reg = PromptRegistry()
    reg.registrar(_tpl())
    reg.registrar(_tpl(corpo="Resuma {texto} em tres linhas"))
    _promover(reg, "resumo", "v1")
    _promover(reg, "resumo", "v2")
    assert reg.estado("resumo", "v1") is Estado.DEPRECIADO
    assert reg.promovida("resumo") == "v2"
    promovidas = [v for v, _, e in reg.historico("resumo") if e is Estado.PROMOVIDO]
    assert promovidas == ["v2"]


def test_historico_preserva_a_ordem_de_registro():
    reg = PromptRegistry()
    reg.registrar(_tpl())
    reg.registrar(_tpl(corpo="Resuma {texto} em tres linhas"))
    reg.registrar(_tpl(corpo="Resuma {texto} sem adjetivos"))
    historico = reg.historico("resumo")
    assert [v for v, _, _ in historico] == ["v1", "v2", "v3"]
    assert historico[0][1] == _tpl().hash
    assert len({h for _, h, _ in historico}) == 3
