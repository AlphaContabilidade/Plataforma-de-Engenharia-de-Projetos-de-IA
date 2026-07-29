"""Testa o levantamento de estado do acervo."""
from ferramentas import contrato as C
from ferramentas import status as S


def _por_id(estados):
    return {e.vol_id: e for e in estados}


def test_volume_materializado_aparece_com_seu_status(volume_engine):
    raiz, _ = volume_engine
    estados = _por_id(S.levantar(raiz, C.carregar(raiz)))
    assert estados["07"].status == "RASCUNHO"
    assert estados["07"].secoes_presentes == 18
    assert estados["07"].secoes_esperadas == 18


def test_volume_sem_pasta_e_pendente(volume_engine):
    raiz, _ = volume_engine
    estados = _por_id(S.levantar(raiz, C.carregar(raiz)))
    assert estados["13"].status == "PENDENTE"
    assert estados["13"].secoes_presentes == 0


def test_todos_os_42_aparecem(volume_engine):
    raiz, _ = volume_engine
    assert len(S.levantar(raiz, C.carregar(raiz))) == 42


def test_secao_faltante_reduz_a_contagem(volume_engine):
    raiz, pasta = volume_engine
    (pasta / "14-Metricas.md").unlink()
    estados = _por_id(S.levantar(raiz, C.carregar(raiz)))
    assert estados["07"].secoes_presentes == 17


def test_perecivel_vem_do_contrato(volume_engine):
    raiz, _ = volume_engine
    estados = _por_id(S.levantar(raiz, C.carregar(raiz)))
    assert estados["26"].perecivel is True
    assert estados["07"].perecivel is False


def test_nota_da_auditoria_e_lida(volume_engine):
    raiz, _ = volume_engine
    pasta = raiz / "auditorias"
    pasta.mkdir()
    (pasta / "VOL-07-auditoria-2026-07-29.md").write_text(
        "# Auditoria\n\nmedia: 8.4\n", encoding="utf-8"
    )
    estados = _por_id(S.levantar(raiz, C.carregar(raiz)))
    assert estados["07"].nota_auditoria == 8.4


def test_sem_auditoria_a_nota_e_none(volume_engine):
    raiz, _ = volume_engine
    estados = _por_id(S.levantar(raiz, C.carregar(raiz)))
    assert estados["07"].nota_auditoria is None


def test_auditoria_mais_recente_vence(volume_engine):
    raiz, _ = volume_engine
    pasta = raiz / "auditorias"
    pasta.mkdir()
    (pasta / "VOL-07-auditoria-2026-07-28.md").write_text("media: 6.0\n", encoding="utf-8")
    (pasta / "VOL-07-auditoria-2026-07-29.md").write_text("media: 9.1\n", encoding="utf-8")
    assert S.nota_da_ultima_auditoria(raiz, "07") == 9.1


def test_tabela_tem_uma_linha_por_volume(volume_engine):
    raiz, _ = volume_engine
    saida = S.tabela(S.levantar(raiz, C.carregar(raiz)))
    assert saida.count("\n| ") >= 42
    assert "PROMPT-ENGINE" in saida


def test_cli_retorna_zero(volume_engine, capsys, monkeypatch):
    raiz, _ = volume_engine
    monkeypatch.chdir(raiz)
    assert S.main([]) == 0
    assert "PROMPT-ENGINE" in capsys.readouterr().out
