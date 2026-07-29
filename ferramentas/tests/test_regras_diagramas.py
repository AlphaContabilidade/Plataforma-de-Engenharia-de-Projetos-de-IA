"""Regras de diagrama, exemplo executavel e link interno."""
from ferramentas import contrato as C
from ferramentas import regras as R
from ferramentas.tests.conftest import FRONT_OK, PROSA

CABECA = FRONT_OK.format(vol="07", nome="PROMPT-ENGINE", tipo="ENGINE", secao="05-Diagramas")


def _regras(violacoes):
    return {v.regra for v in violacoes}


def _escrever(pasta, nome, miolo):
    arq = pasta / nome
    arq.write_text(CABECA + "\n" + miolo, encoding="utf-8")
    return arq


def test_mermaid_valido_com_descricao_passa(volume_engine):
    _, pasta = volume_engine
    arq = _escrever(
        pasta, "05-Diagramas.md",
        "# Diagramas\n\n```mermaid\nflowchart TD\n  A --> B\n```\n\n"
        "O diagrama mostra o fluxo de A para B.\n\n" + PROSA + "\n",
    )
    linhas, inicio = R.corpo_de(arq)
    assert R.checar_mermaid("05-Diagramas.md", linhas, inicio) == []


def test_mermaid_sem_paragrafo_descritivo_e_detectado(volume_engine):
    _, pasta = volume_engine
    arq = _escrever(
        pasta, "05-Diagramas.md",
        "# Diagramas\n\n```mermaid\nflowchart TD\n  A --> B\n```\n\n## Outra secao\n\n" + PROSA + "\n",
    )
    linhas, inicio = R.corpo_de(arq)
    assert "mermaid-sem-descricao" in _regras(R.checar_mermaid("05-Diagramas.md", linhas, inicio))


def test_mermaid_com_tipo_desconhecido_e_detectado(volume_engine):
    _, pasta = volume_engine
    arq = _escrever(
        pasta, "05-Diagramas.md",
        "# Diagramas\n\n```mermaid\ndiagramaInventado XY\n  A --> B\n```\n\nDescricao.\n\n" + PROSA,
    )
    linhas, inicio = R.corpo_de(arq)
    assert "mermaid-tipo" in _regras(R.checar_mermaid("05-Diagramas.md", linhas, inicio))


def test_mermaid_vazio_e_detectado(volume_engine):
    _, pasta = volume_engine
    arq = _escrever(pasta, "05-Diagramas.md", "# Diagramas\n\n```mermaid\n```\n\nDescricao.\n\n" + PROSA)
    linhas, inicio = R.corpo_de(arq)
    assert "mermaid-vazio" in _regras(R.checar_mermaid("05-Diagramas.md", linhas, inicio))


def test_mermaid_nao_fechado_e_detectado(volume_engine):
    _, pasta = volume_engine
    arq = _escrever(pasta, "05-Diagramas.md", "# Diagramas\n\n```mermaid\nflowchart TD\n  A --> B\n")
    linhas, inicio = R.corpo_de(arq)
    assert "mermaid-nao-fechado" in _regras(R.checar_mermaid("05-Diagramas.md", linhas, inicio))


def test_engine_sem_state_machine_e_detectado(volume_engine):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    texto = "```mermaid\nC4Context\n```\n```mermaid\nsequenceDiagram\n```\n"
    saida = R.checar_diagramas_obrigatorios("07-PROMPT-ENGINE", texto, "ENGINE", ct)
    assert "diagrama-obrigatorio" in _regras(saida)
    assert "stateDiagram-v2" in str(saida[0])


def test_engine_com_os_tres_diagramas_passa(volume_engine):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    texto = (
        "```mermaid\nC4Context\n```\n```mermaid\nsequenceDiagram\n```\n"
        "```mermaid\nstateDiagram-v2\n```\n"
    )
    assert R.checar_diagramas_obrigatorios("07-PROMPT-ENGINE", texto, "ENGINE", ct) == []


def test_biblioteca_nao_exige_diagrama(volume_engine):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    assert R.checar_diagramas_obrigatorios("40-TEMPLATES", "", "BIBLIOTECA", ct) == []


def test_exemplo_inexistente_e_detectado(volume_engine):
    raiz, pasta = volume_engine
    arq = _escrever(
        pasta, "12-Exemplos.md",
        "# Exemplos\n\n<!-- exemplo: exemplos/07-prompt-engine/fantasma.py -->\n\n" + PROSA,
    )
    linhas, inicio = R.corpo_de(arq)
    assert "exemplo-inexistente" in _regras(R.checar_exemplos(raiz, "12-Exemplos.md", linhas, inicio))


def test_exemplo_sem_teste_e_detectado(volume_engine):
    raiz, pasta = volume_engine
    alvo = raiz / "exemplos" / "07-prompt-engine"
    alvo.mkdir(parents=True)
    (alvo / "prompt_template.py").write_text("VALOR = 1\n", encoding="utf-8")
    arq = _escrever(
        pasta, "12-Exemplos.md",
        "# Exemplos\n\n<!-- exemplo: exemplos/07-prompt-engine/prompt_template.py -->\n\n" + PROSA,
    )
    linhas, inicio = R.corpo_de(arq)
    assert "exemplo-sem-teste" in _regras(R.checar_exemplos(raiz, "12-Exemplos.md", linhas, inicio))


def test_exemplo_com_teste_passa(volume_engine):
    raiz, pasta = volume_engine
    alvo = raiz / "exemplos" / "07-prompt-engine"
    (alvo / "tests").mkdir(parents=True)
    (alvo / "prompt_template.py").write_text("VALOR = 1\n", encoding="utf-8")
    (alvo / "tests" / "test_prompt_template.py").write_text("def test_x():\n    pass\n", encoding="utf-8")
    arq = _escrever(
        pasta, "12-Exemplos.md",
        "# Exemplos\n\n<!-- exemplo: exemplos/07-prompt-engine/prompt_template.py -->\n\n" + PROSA,
    )
    linhas, inicio = R.corpo_de(arq)
    assert R.checar_exemplos(raiz, "12-Exemplos.md", linhas, inicio) == []


def test_link_morto_e_detectado(volume_engine):
    raiz, pasta = volume_engine
    arq = _escrever(
        pasta, "18-Referencias-Cruzadas.md",
        "# Referencias\n\nVeja [Volume 99](../99-INEXISTENTE/01-Introducao.md).\n\n" + PROSA,
    )
    linhas, inicio = R.corpo_de(arq)
    assert "link-morto" in _regras(
        R.checar_links(raiz, arq, "18-Referencias-Cruzadas.md", linhas, inicio)
    )


def test_link_vivo_e_externo_passam(volume_engine):
    raiz, pasta = volume_engine
    arq = _escrever(
        pasta, "18-Referencias-Cruzadas.md",
        "# Referencias\n\nVeja [Arquitetura](04-Arquitetura.md) e "
        "[Mermaid](https://mermaid.js.org/) e [ancora](#secao).\n\n" + PROSA,
    )
    linhas, inicio = R.corpo_de(arq)
    assert R.checar_links(raiz, arq, "18-Referencias-Cruzadas.md", linhas, inicio) == []
