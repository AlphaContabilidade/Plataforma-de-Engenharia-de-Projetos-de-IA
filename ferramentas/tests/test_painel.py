"""Testa as funcoes puras do painel.

Nenhum teste digita no menu. O laco interativo depende de `input()`, e teste que
simula digitacao verifica o roteamento de teclas em vez da regra - entao a regra
foi extraida para funcao pura e e ela que esta sob teste. O que o menu faz e
chamar essas funcoes.
"""
from pathlib import Path

import pytest

from ferramentas import contrato as C
from ferramentas import painel as P
from ferramentas.contrato import ContratoInvalido


# --- resumo ---------------------------------------------------------------


def test_resumo_conta_os_status_corretamente(volume_engine):
    raiz, _ = volume_engine
    r = P.resumo_do_acervo(raiz, C.carregar(raiz))
    assert r.total == 42
    assert r.contagem["RASCUNHO"] == 1
    assert r.contagem[P.PENDENTE] == 41
    assert sum(r.contagem.values()) == 42


def test_resumo_aponta_o_volume_mais_avancado(volume_engine):
    raiz, pasta = volume_engine
    (pasta / "_VOLUME.yml").write_text(
        'volume: "07"\nnome: PROMPT-ENGINE\ntipo: ENGINE\n'
        "status: PRONTO\nperecivel: false\ndepende_de: []\n",
        encoding="utf-8",
    )
    r = P.resumo_do_acervo(raiz, C.carregar(raiz))
    assert r.mais_avancado is not None
    assert r.mais_avancado.vol_id == "07"
    assert r.mais_avancado.status == "PRONTO"


def test_resumo_manda_rodar_os_gates_de_rascunho_completo(volume_engine):
    """RASCUNHO com todas as secoes em disco vira 'rode os gates'.

    Vem antes de scaffold de proposito: volume escrito e nao verificado e o que
    esta mais perto de virar PRONTO, e tambem o que mais arrisca virar PRONTO
    sem gate se ninguem rodar.
    """
    raiz, _ = volume_engine
    r = P.resumo_do_acervo(raiz, C.carregar(raiz))
    assert "rode os gates" in r.proxima_acao.lower()


def test_resumo_recomenda_scaffold_quando_falta_pasta(volume_engine):
    raiz, pasta = volume_engine
    (pasta / "_VOLUME.yml").write_text(
        'volume: "07"\nnome: PROMPT-ENGINE\ntipo: ENGINE\n'
        "status: PRONTO\nperecivel: false\ndepende_de: []\n",
        encoding="utf-8",
    )
    r = P.resumo_do_acervo(raiz, C.carregar(raiz))
    # 41 volumes sem pasta e nada pendente antes deles: materializar.
    assert "materializar" in r.proxima_acao.lower()
    assert "41" in r.proxima_acao


def test_resumo_prioriza_volume_reprovado_pela_auditoria(volume_engine):
    raiz, pasta = volume_engine
    (pasta / "_VOLUME.yml").write_text(
        'volume: "07"\nnome: PROMPT-ENGINE\ntipo: ENGINE\n'
        "status: REQUER_REVISAO\nperecivel: false\ndepende_de: []\n",
        encoding="utf-8",
    )
    r = P.resumo_do_acervo(raiz, C.carregar(raiz))
    assert "07-PROMPT-ENGINE" in r.proxima_acao
    assert "auditoria" in r.proxima_acao.lower()


def test_resumo_manda_terminar_volume_pela_metade(volume_engine):
    raiz, pasta = volume_engine
    (pasta / "14-Metricas.md").unlink()
    r = P.resumo_do_acervo(raiz, C.carregar(raiz))
    # Volume parcial vence volume inexistente: divida antes de cobertura nova.
    assert "Termine o volume 07-PROMPT-ENGINE" in r.proxima_acao


# --- secoes ausentes ------------------------------------------------------


def test_secoes_ausentes_de_engine_completo_e_vazio(volume_engine):
    raiz, _ = volume_engine
    assert P.secoes_ausentes(raiz, "07", C.carregar(raiz)) == ()


def test_secoes_ausentes_de_engine_acerta_o_que_falta(volume_engine):
    raiz, pasta = volume_engine
    (pasta / "05-Diagramas.md").unlink()
    (pasta / "08-Modelos.md").unlink()
    ausentes = P.secoes_ausentes(raiz, "07", C.carregar(raiz))
    assert ausentes == ("05-Diagramas", "08-Modelos")


def test_secoes_ausentes_de_processo_nao_cobra_08_modelos(acervo):
    """PROCESSO dispensa `08-Modelos`: 17 secoes, nao 18."""
    ct = C.carregar(acervo)
    pasta = acervo / "03-DISCOVERY"
    pasta.mkdir()
    ausentes = P.secoes_ausentes(acervo, "03", ct)
    assert "08-Modelos" not in ausentes
    assert len(ausentes) == 17
    assert len(P.secoes_ausentes(acervo, "01", ct)) == 18  # GOVERNANCA: as 18 da base


def test_secoes_ausentes_de_biblioteca_troca_arquitetura_por_catalogo(acervo):
    ausentes = P.secoes_ausentes(acervo, "36", C.carregar(acervo))
    assert "04-Catalogo" in ausentes
    assert "04-Arquitetura" not in ausentes
    assert "05-Diagramas" not in ausentes


# --- briefing -------------------------------------------------------------


def test_briefing_de_biblioteca_lista_catalogo_e_nao_arquitetura(acervo):
    b = P.briefing_de(acervo, "36", C.carregar(acervo))
    assert b.tipo == "BIBLIOTECA"
    assert "04-Catalogo" in b.secoes_obrigatorias
    assert "04-Arquitetura" not in b.secoes_obrigatorias
    assert "05-Diagramas" not in b.secoes_obrigatorias
    texto = P.texto_do_briefing(b)
    assert "`04-Catalogo`" in texto
    assert "`04-Arquitetura`" not in texto


def test_briefing_traz_os_diagramas_obrigatorios_do_tipo(acervo):
    ct = C.carregar(acervo)
    engine = P.briefing_de(acervo, "08", ct)
    assert engine.diagramas_obrigatorios == ("C4Context", "sequenceDiagram", "stateDiagram-v2")
    for exigido in engine.diagramas_obrigatorios:
        assert exigido in P.texto_do_briefing(engine)

    processo = P.briefing_de(acervo, "03", ct)
    assert processo.diagramas_obrigatorios == ("flowchart",)

    biblioteca = P.briefing_de(acervo, "36", ct)
    assert biblioteca.diagramas_obrigatorios == ()
    assert "nao exige diagrama obrigatorio" in P.texto_do_briefing(biblioteca)


def test_briefing_traz_os_limiares_de_palavras_por_secao(acervo):
    b = P.briefing_de(acervo, "08", C.carregar(acervo))
    assert b.minimos["01-Introducao"] == 200
    assert b.minimos["15-Checklist"] == 120
    assert b.minimos["18-Referencias-Cruzadas"] == 80


def test_briefing_normaliza_id_de_um_digito(acervo):
    assert P.briefing_de(acervo, "8", C.carregar(acervo)).vol_id == "08"


def test_briefing_resolve_pre_requisitos_com_status(volume_engine):
    raiz, pasta = volume_engine
    (pasta / "_VOLUME.yml").write_text(
        'volume: "07"\nnome: PROMPT-ENGINE\ntipo: ENGINE\n'
        'status: RASCUNHO\nperecivel: false\ndepende_de: ["01", "02"]\n',
        encoding="utf-8",
    )
    b = P.briefing_de(raiz, "07", C.carregar(raiz))
    assert b.depende_de == ("01", "02")
    assert b.pre_requisitos == (
        ("01", "FUNDACAO", P.PENDENTE),
        ("02", "CORE", P.PENDENTE),
    )
    assert "01-FUNDACAO" in P.texto_do_briefing(b)


def test_briefing_avisa_que_o_painel_nao_inventa_conteudo(acervo):
    texto = P.texto_do_briefing(P.briefing_de(acervo, "08", C.carregar(acervo)))
    assert "nao escreve o volume e nao inventa conteudo" in texto


def test_briefing_de_volume_inexistente_levanta_contrato_invalido(acervo):
    with pytest.raises(ContratoInvalido):
        P.briefing_de(acervo, "99", C.carregar(acervo))


def test_regras_citadas_existem_no_motor():
    """O briefing nao pode ensinar regra fantasma.

    Se `regras.py` renomear uma regra, este teste reprova antes de o briefing
    comecar a citar nome que a maquina nunca emite.
    """
    raiz = Path(__file__).resolve().parents[2]
    fonte = (raiz / "ferramentas" / "regras.py").read_text(encoding="utf-8")
    fonte += (raiz / "ferramentas" / "validar.py").read_text(encoding="utf-8")
    for regra, _ in P.REGRAS_QUE_MAIS_REPROVAM:
        assert f'"{regra}"' in fonte, f"regra citada no briefing nao existe: {regra}"


# --- fronteira de escopo --------------------------------------------------


def test_fronteira_sai_do_roadmap_real():
    """A fronteira e lida do ROADMAP.md, nao duplicada em Python."""
    raiz = Path(__file__).resolve().parents[2]
    grupos = P.fronteiras_do_roadmap(raiz)
    assert len(grupos) == 4
    por_volume = {v: g for g in grupos for v in g.volumes}
    assert por_volume["07"].volumes == ("07", "28", "29")
    assert "11" in por_volume and "15" in por_volume["11"].volumes
    # A faixa `22`-`25` tem de ser expandida: sem isso 23 e 24 ficariam sem
    # fronteira mesmo estando declarados.
    assert {"22", "23", "24", "25", "16"} <= set(por_volume["23"].volumes)


def test_fronteira_ausente_nao_e_inventada(acervo):
    """Sem ROADMAP.md em disco, o painel devolve None em vez de chutar."""
    assert P.fronteiras_do_roadmap(acervo) == ()
    assert P.fronteira_de(acervo, "07") is None
    assert "nao aparece em nenhum grupo" in P.texto_do_briefing(
        P.briefing_de(acervo, "07", C.carregar(acervo))
    )


# --- gates ----------------------------------------------------------------


def test_veredicto_aprova_o_volume_completo(volume_engine):
    raiz, _ = volume_engine
    vereditos = P.veredicto_dos_gates(raiz, "07", C.carregar(raiz))
    assert [v.gate for v in vereditos] == [1, 2, 3]
    assert all(v.aprovado for v in vereditos), [v.detalhe for v in vereditos]


def test_veredicto_reprova_volume_com_secao_faltando(volume_engine):
    raiz, pasta = volume_engine
    (pasta / "09-Boas-Praticas.md").unlink()
    gate1, _, _ = P.veredicto_dos_gates(raiz, "07", C.carregar(raiz))
    assert gate1.aprovado is False
    assert any(v.regra == "secao-ausente" for v in gate1.violacoes)


def test_gate_2_sem_pasta_de_exemplos_nao_reprova(volume_engine):
    """Volume que nao cita exemplo executavel nao tem o que rodar.

    Reprovar por ausencia de pasta transformaria 'nada a executar' em falha, e
    o gate 2 existe para pegar codigo que nao roda, nao codigo que nao existe.
    """
    raiz, _ = volume_engine
    _, gate2, _ = P.veredicto_dos_gates(raiz, "07", C.carregar(raiz))
    assert gate2.aprovado is True
    assert "nada a rodar" in gate2.detalhe


def test_gate_3_pega_depende_de_inexistente(volume_engine):
    raiz, pasta = volume_engine
    (pasta / "_VOLUME.yml").write_text(
        'volume: "07"\nnome: PROMPT-ENGINE\ntipo: ENGINE\n'
        'status: RASCUNHO\nperecivel: false\ndepende_de: ["99"]\n',
        encoding="utf-8",
    )
    _, _, gate3 = P.veredicto_dos_gates(raiz, "07", C.carregar(raiz))
    assert gate3.aprovado is False
    assert any(v.regra == "depende-de-inexistente" for v in gate3.violacoes)


def test_agrupar_por_regra_conta_e_ordena_pela_frequencia(volume_engine):
    raiz, pasta = volume_engine
    for secao in ("09-Boas-Praticas", "10-Anti-Patterns", "13-Testes"):
        (pasta / f"{secao}.md").unlink()
    escrever_curto = pasta / "14-Metricas.md"
    escrever_curto.write_text(
        escrever_curto.read_text(encoding="utf-8").split("# 14-Metricas")[0]
        + "# 14-Metricas\n\nduas palavras\n",
        encoding="utf-8",
    )
    gate1, _, _ = P.veredicto_dos_gates(raiz, "07", C.carregar(raiz))
    grupos = P.agrupar_por_regra(gate1.violacoes)
    assert list(grupos)[0] == "secao-ausente"
    assert len(grupos["secao-ausente"]) == 3
    assert len(grupos["substancia-curta"]) == 1
    texto = P.texto_dos_gates((gate1,))
    assert "[secao-ausente] x3" in texto
    assert "REPROVADO" in texto


# --- modo nao interativo --------------------------------------------------


def test_resumo_na_linha_de_comando_sai_zero(volume_engine, capsys):
    raiz, _ = volume_engine
    assert P.main(["--raiz", str(raiz), "--resumo"]) == 0
    saida = capsys.readouterr().out
    assert "AI-ENGINEERING-OS" in saida
    assert "Proxima acao recomendada" in saida


def test_briefing_na_linha_de_comando_sai_zero(volume_engine, capsys):
    raiz, _ = volume_engine
    assert P.main(["--raiz", str(raiz), "--briefing", "36"]) == 0
    assert "04-Catalogo" in capsys.readouterr().out


def test_gates_na_linha_de_comando_sai_zero_quando_passa(volume_engine, capsys):
    raiz, _ = volume_engine
    assert P.main(["--raiz", str(raiz), "--gates", "07"]) == 0
    assert "os tres gates passaram" in capsys.readouterr().out


def test_gates_na_linha_de_comando_sai_um_quando_ha_violacao(volume_engine, capsys):
    raiz, pasta = volume_engine
    (pasta / "07-Regras.md").unlink()
    assert P.main(["--raiz", str(raiz), "--gates", "07"]) == 1
    assert "REPROVADO" in capsys.readouterr().out


def test_volume_inexistente_e_erro_tratado_nao_traceback(volume_engine, capsys):
    raiz, _ = volume_engine
    assert P.main(["--raiz", str(raiz), "--briefing", "99"]) == 2
    assert P.main(["--raiz", str(raiz), "--gates", "99"]) == 2
    assert "nao declarado no contrato" in capsys.readouterr().err


def test_contrato_ausente_sai_dois(tmp_path, capsys):
    assert P.main(["--raiz", str(tmp_path), "--resumo"]) == 2
    assert "contrato ausente" in capsys.readouterr().err
