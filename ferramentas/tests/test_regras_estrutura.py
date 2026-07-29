"""Fixtures deliberadamente ruins: cada uma precisa ser detectada."""
from ferramentas import contrato as C
from ferramentas import regras as R
from ferramentas.tests.conftest import FRONT_OK, PROSA


def _regras(violacoes):
    return {v.regra for v in violacoes}


def test_secao_valida_nao_gera_violacao(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "04-Arquitetura.md"
    linhas, inicio = R.corpo_de(arq)
    vol = {"volume": "07", "nome": "PROMPT-ENGINE", "tipo": "ENGINE"}
    assert R.checar_frontmatter("04-Arquitetura.md", arq, "04-Arquitetura", vol, ct) == []
    assert R.checar_substancia("04-Arquitetura.md", linhas, inicio, "04-Arquitetura", ct) == []


def test_secao_sem_frontmatter_e_detectada(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "04-Arquitetura.md"
    arq.write_text("# Arquitetura\n\n" + PROSA + "\n", encoding="utf-8")
    vol = {"volume": "07", "nome": "PROMPT-ENGINE", "tipo": "ENGINE"}
    assert "frontmatter" in _regras(
        R.checar_frontmatter("04-Arquitetura.md", arq, "04-Arquitetura", vol, ct)
    )


def test_campo_obrigatorio_ausente_e_detectado(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "04-Arquitetura.md"
    arq.write_text(
        '---\nvolume: "07"\ntipo: ENGINE\nsecao: 04-Arquitetura\n'
        "status: RASCUNHO\natualizado_em: 2026-07-29\n---\n\n" + PROSA + "\n",
        encoding="utf-8",
    )
    vol = {"volume": "07", "nome": "PROMPT-ENGINE", "tipo": "ENGINE"}
    saida = R.checar_frontmatter("04-Arquitetura.md", arq, "04-Arquitetura", vol, ct)
    assert "frontmatter-campo" in _regras(saida)
    assert "volume_nome" in str(saida[0])


def test_status_invalido_e_detectado(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "04-Arquitetura.md"
    texto = arq.read_text(encoding="utf-8").replace("status: RASCUNHO", "status: QUASE")
    arq.write_text(texto, encoding="utf-8")
    vol = {"volume": "07", "nome": "PROMPT-ENGINE", "tipo": "ENGINE"}
    assert "frontmatter-status" in _regras(
        R.checar_frontmatter("04-Arquitetura.md", arq, "04-Arquitetura", vol, ct)
    )


def test_secao_do_frontmatter_diferente_do_nome_do_arquivo(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "04-Arquitetura.md"
    texto = arq.read_text(encoding="utf-8").replace("secao: 04-Arquitetura", "secao: 05-Diagramas")
    arq.write_text(texto, encoding="utf-8")
    vol = {"volume": "07", "nome": "PROMPT-ENGINE", "tipo": "ENGINE"}
    assert "frontmatter-coerencia" in _regras(
        R.checar_frontmatter("04-Arquitetura.md", arq, "04-Arquitetura", vol, ct)
    )


def test_tipo_divergente_do_volume_yml(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "04-Arquitetura.md"
    texto = arq.read_text(encoding="utf-8").replace("tipo: ENGINE", "tipo: PROCESSO")
    arq.write_text(texto, encoding="utf-8")
    vol = {"volume": "07", "nome": "PROMPT-ENGINE", "tipo": "ENGINE"}
    assert "frontmatter-coerencia" in _regras(
        R.checar_frontmatter("04-Arquitetura.md", arq, "04-Arquitetura", vol, ct)
    )


def test_secao_curta_e_detectada(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "04-Arquitetura.md"
    cabeca = FRONT_OK.format(vol="07", nome="PROMPT-ENGINE", tipo="ENGINE", secao="04-Arquitetura")
    arq.write_text(cabeca + "\n# Arquitetura\n\nCurto demais.\n", encoding="utf-8")
    linhas, inicio = R.corpo_de(arq)
    saida = R.checar_substancia("04-Arquitetura.md", linhas, inicio, "04-Arquitetura", ct)
    assert "substancia-curta" in _regras(saida)


def test_codigo_nao_conta_como_prosa(volume_engine):
    """Uma secao so de codigo tem de reprovar por curta."""
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "04-Arquitetura.md"
    cabeca = FRONT_OK.format(vol="07", nome="PROMPT-ENGINE", tipo="ENGINE", secao="04-Arquitetura")
    codigo = "```python\n" + ("x = 1  # palavra palavra palavra\n" * 120) + "```\n"
    arq.write_text(cabeca + "\n# Arquitetura\n\n" + codigo, encoding="utf-8")
    linhas, inicio = R.corpo_de(arq)
    assert "substancia-curta" in _regras(
        R.checar_substancia("04-Arquitetura.md", linhas, inicio, "04-Arquitetura", ct)
    )


def test_marcador_proibido_e_detectado(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "04-Arquitetura.md"
    cabeca = FRONT_OK.format(vol="07", nome="PROMPT-ENGINE", tipo="ENGINE", secao="04-Arquitetura")
    arq.write_text(cabeca + "\n# Arquitetura\n\nTODO: escrever isso.\n\n" + PROSA + "\n",
                   encoding="utf-8")
    linhas, inicio = R.corpo_de(arq)
    saida = R.sem_marcadores("04-Arquitetura.md", linhas, inicio, ct)
    assert "marcador-proibido" in _regras(saida)
    # 8 linhas de front-matter (1-8), linha 9 vazia, 10 o titulo, 11 vazia, 12 o TODO.
    assert saida[0].linha == 12
    assert linhas[saida[0].linha - 1].startswith("TODO")


def test_marcador_em_code_span_e_permitido(volume_engine):
    """Mencionar `TODO` em fonte de codigo e legitimo; a regra nao pode pegar."""
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = pasta / "10-Anti-Patterns.md"
    cabeca = FRONT_OK.format(vol="07", nome="PROMPT-ENGINE", tipo="ENGINE", secao="10-Anti-Patterns")
    arq.write_text(
        cabeca + "\n# Anti-Patterns\n\nDeixar `TODO` no volume e anti-pattern.\n\n" + PROSA + "\n",
        encoding="utf-8",
    )
    linhas, inicio = R.corpo_de(arq)
    assert R.sem_marcadores("10-Anti-Patterns.md", linhas, inicio, ct) == []


def _com_prosa(pasta, nome, secao, miolo):
    cabeca = FRONT_OK.format(vol="07", nome="PROMPT-ENGINE", tipo="ENGINE", secao=secao)
    arq = pasta / nome
    arq.write_text(cabeca + f"\n# {secao}\n\n{miolo}\n\n" + PROSA + "\n", encoding="utf-8")
    return arq


def test_independente_nao_dispara_o_marcador_pendente(volume_engine):
    """PENDENTE dentro de INDEPENDENTE nao e marcador.

    Regressao: a busca era por substring, entao "AUDITORIA INDEPENDENTE" - que e
    vocabulario central da plataforma - reprovava o volume.
    """
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = _com_prosa(pasta, "04-Arquitetura.md", "04-Arquitetura",
                     "A AUDITORIA INDEPENDENTE julga o volume ja verde no gate estrutural.")
    linhas, inicio = R.corpo_de(arq)
    assert R.sem_marcadores("04-Arquitetura.md", linhas, inicio, ct) == []


def test_pendente_como_palavra_inteira_ainda_dispara(volume_engine):
    """A fronteira de palavra nao pode ter desarmado a regra."""
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = _com_prosa(pasta, "04-Arquitetura.md", "04-Arquitetura",
                     "Esta secao esta PENDENTE de revisao.")
    linhas, inicio = R.corpo_de(arq)
    assert "marcador-proibido" in _regras(
        R.sem_marcadores("04-Arquitetura.md", linhas, inicio, ct)
    )


def test_marcador_multipalavra_ainda_dispara(volume_engine):
    """`preencher aqui` tem espaco no meio; a fronteira nao pode quebrar isso."""
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    arq = _com_prosa(pasta, "04-Arquitetura.md", "04-Arquitetura",
                     "Diagrama: preencher aqui depois.")
    linhas, inicio = R.corpo_de(arq)
    assert "marcador-proibido" in _regras(
        R.sem_marcadores("04-Arquitetura.md", linhas, inicio, ct)
    )
