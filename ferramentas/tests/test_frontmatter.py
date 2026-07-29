"""Testa o parser do subconjunto YAML do front-matter."""
import pytest

from ferramentas.frontmatter import (
    FrontMatterInvalido, extrair_bloco, ler, ler_volume_yml, parse_bloco,
)

BLOCO_OK = """---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 04-Arquitetura
status: RASCUNHO
atualizado_em: 2026-07-29
perecivel: false
depende_de: [08-AGENT-ENGINE, 28-PROMPT-COMPILER]
---

# Arquitetura

Conteudo.
"""


def test_extrair_bloco_devolve_corpo_e_linha_do_conteudo():
    corpo, linha = extrair_bloco(BLOCO_OK)
    assert "tipo: ENGINE" in corpo
    assert linha == 11  # fechamento na linha 10; conteudo comeca na 11


def test_volume_permanece_string():
    campos = parse_bloco(extrair_bloco(BLOCO_OK)[0])
    assert campos["volume"] == "07" and isinstance(campos["volume"], str)


def test_le_lista_em_linha():
    campos = parse_bloco(extrair_bloco(BLOCO_OK)[0])
    assert campos["depende_de"] == ["08-AGENT-ENGINE", "28-PROMPT-COMPILER"]


def test_le_booleano():
    assert parse_bloco(extrair_bloco(BLOCO_OK)[0])["perecivel"] is False


def test_lista_vazia():
    assert parse_bloco("depende_de: []")["depende_de"] == []


def test_inteiro_sem_zero_a_esquerda():
    assert parse_bloco("minimo: 200")["minimo"] == 200


def test_ignora_comentario_e_linha_vazia():
    assert parse_bloco("# comentario\n\ntipo: ENGINE\n") == {"tipo": "ENGINE"}


def test_sem_abertura_falha():
    with pytest.raises(FrontMatterInvalido, match="ausente"):
        extrair_bloco("# Titulo\n\nsem front-matter\n")


def test_sem_fechamento_falha():
    with pytest.raises(FrontMatterInvalido, match="fechamento"):
        extrair_bloco("---\ntipo: ENGINE\n\n# Titulo\n")


def test_linha_sem_dois_pontos_falha():
    with pytest.raises(FrontMatterInvalido, match="linha 1"):
        parse_bloco("tipo ENGINE\n")


def test_chave_duplicada_falha():
    with pytest.raises(FrontMatterInvalido, match="duplicada"):
        parse_bloco("tipo: ENGINE\ntipo: PROCESSO\n")


def test_chave_vazia_falha():
    with pytest.raises(FrontMatterInvalido, match="vazia"):
        parse_bloco(": ENGINE\n")


def test_ler_arquivo(tmp_path):
    arq = tmp_path / "04-Arquitetura.md"
    arq.write_text(BLOCO_OK, encoding="utf-8")
    campos, linha = ler(arq)
    assert campos["secao"] == "04-Arquitetura" and linha == 11


def test_ler_volume_yml(tmp_path):
    arq = tmp_path / "_VOLUME.yml"
    arq.write_text('volume: "07"\nnome: PROMPT-ENGINE\ntipo: ENGINE\n', encoding="utf-8")
    assert ler_volume_yml(arq)["nome"] == "PROMPT-ENGINE"
