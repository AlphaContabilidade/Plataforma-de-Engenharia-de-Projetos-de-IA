"""Testa a orquestracao dos gates e a CLI."""
from ferramentas import contrato as C
from ferramentas import validar as V


def _regras(violacoes):
    return {v.regra for v in violacoes}


def _dep(pasta, valor):
    yml = pasta / "_VOLUME.yml"
    texto = yml.read_text(encoding="utf-8").replace("depende_de: []", f"depende_de: {valor}")
    yml.write_text(texto, encoding="utf-8")


def test_volume_completo_e_valido(volume_engine):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    assert V.validar_volume(raiz, "07", ct) == []


def test_secao_obrigatoria_ausente_e_detectada(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    (pasta / "14-Metricas.md").unlink()
    saida = V.validar_volume(raiz, "07", ct)
    assert "secao-ausente" in _regras(saida)
    assert "14-Metricas" in str(saida[0])


def test_volume_yml_ausente_e_detectado(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    (pasta / "_VOLUME.yml").unlink()
    assert "volume-yml" in _regras(V.validar_volume(raiz, "07", ct))


def test_tipo_invalido_no_volume_yml_lista_os_aceitos(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    yml = pasta / "_VOLUME.yml"
    yml.write_text(
        'volume: "07"\nnome: PROMPT-ENGINE\ntipo: INVENTADO\nstatus: RASCUNHO\ndepende_de: []\n',
        encoding="utf-8",
    )
    saida = V.validar_volume(raiz, "07", ct)
    assert "volume-tipo" in _regras(saida)
    assert "ENGINE" in str(saida[0])


def test_volumes_existentes_ignora_pasta_nao_volume(volume_engine):
    raiz, _ = volume_engine
    (raiz / "ferramentas").mkdir(exist_ok=True)
    assert V.volumes_existentes(raiz) == ["07"]


def test_validar_tudo_nao_cobra_volume_nao_materializado(volume_engine):
    raiz, _ = volume_engine
    ct = C.carregar(raiz)
    assert V.validar_tudo(raiz, ct) == []


def test_depende_de_inexistente_e_detectado(volume_engine):
    raiz, pasta = volume_engine
    ct = C.carregar(raiz)
    _dep(pasta, '["99"]')
    assert "depende-de-inexistente" in _regras(V.validar_cross_refs(raiz, ct))


def test_ciclo_em_depende_de_e_detectado(volume_engine):
    raiz, pasta7 = volume_engine
    ct = C.carregar(raiz)
    pasta28 = raiz / "28-PROMPT-COMPILER"
    pasta28.mkdir()
    (pasta28 / "_VOLUME.yml").write_text(
        'volume: "28"\nnome: PROMPT-COMPILER\ntipo: ENGINE\n'
        'status: RASCUNHO\ndepende_de: ["07"]\n',
        encoding="utf-8",
    )
    _dep(pasta7, '["28"]')
    saida = V.validar_cross_refs(raiz, ct)
    assert "depende-de-ciclo" in _regras(saida)


def test_dependencia_acicilica_passa(volume_engine):
    raiz, pasta7 = volume_engine
    ct = C.carregar(raiz)
    pasta1 = raiz / "01-FUNDACAO"
    pasta1.mkdir()
    (pasta1 / "_VOLUME.yml").write_text(
        'volume: "01"\nnome: FUNDACAO\ntipo: GOVERNANCA\nstatus: RASCUNHO\ndepende_de: []\n',
        encoding="utf-8",
    )
    _dep(pasta7, '["01"]')
    assert V.validar_cross_refs(raiz, ct) == []


def test_cli_volume_valido_retorna_zero(volume_engine, capsys, monkeypatch):
    raiz, _ = volume_engine
    monkeypatch.chdir(raiz)
    assert V.main(["07"]) == 0
    assert "ok" in capsys.readouterr().out.lower()


def test_cli_volume_invalido_retorna_um(volume_engine, capsys, monkeypatch):
    raiz, pasta = volume_engine
    (pasta / "14-Metricas.md").unlink()
    monkeypatch.chdir(raiz)
    assert V.main(["07"]) == 1
    assert "secao-ausente" in capsys.readouterr().out


def test_cli_volume_desconhecido_retorna_dois(volume_engine, monkeypatch):
    raiz, _ = volume_engine
    monkeypatch.chdir(raiz)
    assert V.main(["99"]) == 2
