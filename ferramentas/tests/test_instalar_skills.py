"""Testa o instalador de skills.

A origem e a real (`AI-ENGINEERING-OS/.claude/skills/`), porque o que se quer
provar e que as cinco skills DE VERDADE chegam ao destino. O destino e sempre
`tmp_path`: nenhum teste escreve no `.claude/` do usuario.
"""
from pathlib import Path

from ferramentas import instalar_skills as I

ESPERADAS = {
    "aieos-auditar",
    "aieos-cross-reference",
    "aieos-exportar",
    "aieos-novo-volume",
    "aieos-status",
}


def _origem() -> Path:
    return I.origem_padrao()


def test_origem_tem_as_cinco_skills():
    nomes = {arq.parent.name for arq in I.skills_de_origem(_origem())}
    assert nomes == ESPERADAS


def test_instala_os_cinco_arquivos(tmp_path, capsys):
    destino = tmp_path / "skills"
    assert I.main(["--destino", str(destino)]) == 0
    for nome in ESPERADAS:
        alvo = destino / nome / I.ARQUIVO_SKILL
        assert alvo.is_file()
        assert alvo.read_text(encoding="utf-8").strip()
        assert I.nome_declarado(alvo) == nome
    assert "criado" in capsys.readouterr().out


def test_avisa_que_o_harness_descobre_no_inicio_da_sessao(tmp_path, capsys):
    I.main(["--destino", str(tmp_path / "skills")])
    saida = capsys.readouterr().out
    assert "INICIO DA SESSAO" in saida
    assert "sessao nova" in saida


def test_idempotente_segunda_passada_nao_reescreve(tmp_path):
    destino = tmp_path / "skills"
    I.main(["--destino", str(destino)])
    acoes = I.planejar(_origem(), destino)
    assert {a.situacao for a in acoes} == {I.IDENTICO}
    # `aplicar` nao toca em nada quando tudo esta identico.
    assert I.aplicar(acoes) == ()


def test_atualiza_versao_antiga_da_propria_skill(tmp_path):
    destino = tmp_path / "skills"
    I.main(["--destino", str(destino)])
    alvo = destino / "aieos-status" / I.ARQUIVO_SKILL
    alvo.write_text(
        "---\nname: aieos-status\ndescription: versao antiga\n---\n\nconteudo velho\n",
        encoding="utf-8",
    )
    acoes = {a.nome: a for a in I.planejar(_origem(), destino)}
    assert acoes["aieos-status"].situacao == I.ATUALIZAR
    assert acoes["aieos-auditar"].situacao == I.IDENTICO
    feitas = I.aplicar(tuple(acoes.values()))
    assert [a.nome for a in feitas] == ["aieos-status"]
    assert "conteudo velho" not in alvo.read_text(encoding="utf-8")


def test_aborta_em_conflito_com_skill_de_terceiro(tmp_path, capsys):
    destino = tmp_path / "skills"
    alheia = destino / "aieos-status" / I.ARQUIVO_SKILL
    alheia.parent.mkdir(parents=True)
    original = "---\nname: outra-coisa\ndescription: skill de terceiro\n---\n\nnao me apague\n"
    alheia.write_text(original, encoding="utf-8")

    assert I.main(["--destino", str(destino)]) == 1
    saida = capsys.readouterr().out
    assert "ABORTADO" in saida
    assert "conflito=1" in saida
    # O arquivo alheio continua intacto, e as outras quatro foram instaladas.
    assert alheia.read_text(encoding="utf-8") == original
    assert sum(1 for _ in destino.glob(f"*/{I.ARQUIVO_SKILL}")) == 5


def test_forcar_sobrescreve_o_conflito(tmp_path, capsys):
    destino = tmp_path / "skills"
    alheia = destino / "aieos-status" / I.ARQUIVO_SKILL
    alheia.parent.mkdir(parents=True)
    alheia.write_text("---\nname: outra-coisa\n---\n\nnao me apague\n", encoding="utf-8")

    assert I.main(["--destino", str(destino), "--forcar"]) == 0
    assert I.nome_declarado(alheia) == "aieos-status"
    assert "sobrescrito" in capsys.readouterr().out


def test_destino_sem_front_matter_legivel_e_conflito(tmp_path):
    """Procedencia desconhecida e recusa, nao chute."""
    destino = tmp_path / "skills"
    alvo = destino / "aieos-exportar" / I.ARQUIVO_SKILL
    alvo.parent.mkdir(parents=True)
    alvo.write_text("texto solto sem front-matter\n", encoding="utf-8")
    acoes = {a.nome: a for a in I.planejar(_origem(), destino)}
    assert acoes["aieos-exportar"].situacao == I.CONFLITO


def test_dry_run_nao_escreve_nada(tmp_path, capsys):
    destino = tmp_path / "skills"
    assert I.main(["--destino", str(destino), "--dry-run"]) == 0
    assert not destino.exists()
    saida = capsys.readouterr().out
    assert "criaria" in saida
    assert "nada foi escrito" in saida


def test_dry_run_tambem_reporta_conflito_sem_escrever(tmp_path, capsys):
    destino = tmp_path / "skills"
    alheia = destino / "aieos-status" / I.ARQUIVO_SKILL
    alheia.parent.mkdir(parents=True)
    original = "---\nname: outra-coisa\n---\n\nnao me apague\n"
    alheia.write_text(original, encoding="utf-8")
    assert I.main(["--destino", str(destino), "--dry-run"]) == 1
    assert alheia.read_text(encoding="utf-8") == original
    assert "abortaria" in capsys.readouterr().out


def test_origem_inexistente_sai_dois(tmp_path, capsys):
    assert I.main(["--origem", str(tmp_path / "nada"), "--destino", str(tmp_path / "d")]) == 2
    assert "origem nao existe" in capsys.readouterr().err


def test_origem_sem_skill_nao_e_erro(tmp_path, capsys):
    vazia = tmp_path / "vazia"
    (vazia / "aieos-fantasma").mkdir(parents=True)  # pasta sem SKILL.md
    assert I.main(["--origem", str(vazia), "--destino", str(tmp_path / "d")]) == 0
    assert "nenhuma skill" in capsys.readouterr().out


def test_destino_padrao_e_o_claude_skills_da_raiz_do_repo():
    """O default acompanha a raiz Git tanto no clone quanto no uso aninhado."""
    destino = I.destino_padrao()
    assert destino.parts[-2:] == (".claude", "skills")
    assert destino.parent.parent == I.raiz_do_repo()
    if I.raiz_do_repo() == I.raiz_da_plataforma():
        assert destino == I.origem_padrao()


def test_clone_independente_trata_origem_igual_ao_destino_como_noop():
    """A instalacao no clone standalone nao reescreve nem perde as skills."""
    origem = _origem()
    acoes = I.planejar(origem, origem)
    assert len(acoes) == len(ESPERADAS)
    assert {acao.situacao for acao in acoes} == {I.IDENTICO}
    assert I.aplicar(acoes) == ()
