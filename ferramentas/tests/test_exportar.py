"""Testa a exportacao para MkDocs.

A navegacao e derivada do que existe em disco, nunca do que deveria existir:
volume pendente nao pode aparecer no site, senao o site promete pagina que nao
tem.
"""
from ferramentas import contrato as C
from ferramentas import exportar as E


def _chaves(nav):
    return [k for item in nav for k in item]


def _titulos(entrada):
    return [k for item in list(entrada.values())[0] for k in item]


def test_nav_comeca_por_introducao(volume_engine):
    raiz, _ = volume_engine
    (raiz / "00-INTRODUCAO" / "Prefacio.md").write_text("# Prefacio\n", encoding="utf-8")
    nav = E.montar_nav(raiz, C.carregar(raiz))
    assert _chaves(nav)[0] == "00-INTRODUCAO"
    assert nav[0]["00-INTRODUCAO"] == [{"Prefacio": "00-INTRODUCAO/Prefacio.md"}]


def test_nav_sem_introducao_nao_inventa_entrada(volume_engine):
    """A fixture tem 00-INTRODUCAO so com contrato.json: nada a publicar."""
    raiz, _ = volume_engine
    nav = E.montar_nav(raiz, C.carregar(raiz))
    assert "00-INTRODUCAO" not in _chaves(nav)


def test_nav_ignora_volume_nao_materializado(volume_engine):
    raiz, _ = volume_engine
    nav = E.montar_nav(raiz, C.carregar(raiz))
    assert _chaves(nav) == ["07-PROMPT-ENGINE"]
    assert "13-RAG" not in _chaves(nav)


def test_nav_lista_secoes_em_ordem(volume_engine):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    entrada = E.montar_nav(raiz, ct)[0]
    assert _titulos(entrada) == list(ct.secoes_de("ENGINE"))
    assert entrada["07-PROMPT-ENGINE"][0] == {
        "01-Introducao": "07-PROMPT-ENGINE/01-Introducao.md"
    }


def test_nav_ignora_secao_ausente(volume_engine):
    raiz, pasta = volume_engine
    (pasta / "14-Metricas.md").unlink()
    entrada = E.montar_nav(raiz, C.carregar(raiz))[0]
    assert "14-Metricas" not in _titulos(entrada)
    assert len(_titulos(entrada)) == 17


def test_mkdocs_yml_tem_superfences_mermaid(volume_engine):
    raiz, _ = volume_engine
    yaml = E.gerar_mkdocs(raiz, C.carregar(raiz))
    assert "pymdownx.superfences" in yaml
    assert "name: mermaid" in yaml
    assert "fence_code_format" in yaml
    assert "site_name: AI-ENGINEERING-OS" in yaml
    assert "name: material" in yaml


def test_gerar_grava_o_arquivo_na_raiz(volume_engine):
    raiz, _ = volume_engine
    yaml = E.gerar_mkdocs(raiz, C.carregar(raiz))
    assert (raiz / "mkdocs.yml").read_text(encoding="utf-8") == yaml
    assert "07-PROMPT-ENGINE/01-Introducao.md" in yaml


def test_cli_avisa_quando_mkdocs_ausente(volume_engine, capsys, monkeypatch):
    raiz, _ = volume_engine
    monkeypatch.setattr(E.shutil, "which", lambda _: None)
    assert E.main(["--raiz", str(raiz)]) == 0
    saida = capsys.readouterr().out
    assert "aviso: mkdocs nao encontrado, build nao validado" in saida
    assert "validado com sucesso" not in saida


def test_cli_devolve_1_quando_o_build_falha(volume_engine, monkeypatch):
    raiz, _ = volume_engine
    monkeypatch.setattr(E.shutil, "which", lambda _: "/usr/bin/mkdocs")
    monkeypatch.setattr(E, "_construir", lambda _raiz: 3)
    assert E.main(["--raiz", str(raiz)]) == 1


def test_cli_sem_contrato_devolve_2(tmp_path):
    assert E.main(["--raiz", str(tmp_path)]) == 2
