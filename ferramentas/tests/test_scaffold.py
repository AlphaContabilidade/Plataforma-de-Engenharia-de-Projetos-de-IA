"""Testa a materializacao dos volumes declarados no contrato.

O scaffold e a unica ferramenta que escreve estrutura. Por isso o teste central
nao e "criou", e "criou uma vez": rodar de novo nao pode reescrever nada.
"""
from ferramentas import contrato as C
from ferramentas import scaffold as SC
from ferramentas import validar as V
from ferramentas.frontmatter import ler_volume_yml


def test_scaffold_cria_os_42(acervo):
    ct = C.carregar(acervo)
    criados = SC.criar_volumes(acervo, ct)
    assert criados == sorted(ct.volumes)
    assert len(criados) == 42
    assert (acervo / "07-PROMPT-ENGINE" / "_VOLUME.yml").exists()
    assert (acervo / "26-AI-MODELS" / "_VOLUME.yml").exists()
    # O prefixo 00 e reservado: 00-INTRODUCAO nao e volume e nao entra na lista.
    assert "00" not in criados
    assert V.volumes_existentes(acervo) == criados


def test_scaffold_e_idempotente(acervo):
    ct = C.carregar(acervo)
    SC.criar_volumes(acervo, ct)
    yml = acervo / "07-PROMPT-ENGINE" / "_VOLUME.yml"
    antes = yml.read_bytes()
    # Segunda passada: nada novo, e o byte a byte do yml permanece.
    # Comparar conteudo, nao mtime: a granularidade de mtime no Windows
    # esconderia uma reescrita imediata.
    assert SC.criar_volumes(acervo, ct) == []
    assert yml.read_bytes() == antes


def test_scaffold_nao_sobrescreve_yml_editado(acervo):
    ct = C.carregar(acervo)
    SC.criar_volumes(acervo, ct)
    yml = acervo / "07-PROMPT-ENGINE" / "_VOLUME.yml"
    editado = (
        'volume: "07"\nnome: PROMPT-ENGINE\ntipo: ENGINE\n'
        'status: REQUER_REVISAO\nperecivel: false\ndepende_de: [01, 28]\n'
    )
    yml.write_text(editado, encoding="utf-8")
    assert SC.criar_volumes(acervo, ct) == []
    assert yml.read_text(encoding="utf-8") == editado


def test_scaffold_completa_pasta_sem_yml(acervo):
    """Pasta criada a mao sem _VOLUME.yml e uma lacuna: o scaffold a fecha."""
    ct = C.carregar(acervo)
    (acervo / "07-PROMPT-ENGINE").mkdir()
    criados = SC.criar_volumes(acervo, ct)
    assert "07" in criados
    assert (acervo / "07-PROMPT-ENGINE" / "_VOLUME.yml").exists()


def test_volume_yml_gerado_e_valido_para_o_parser(acervo):
    ct = C.carregar(acervo)
    SC.criar_volumes(acervo, ct)
    vol = ler_volume_yml(acervo / "07-PROMPT-ENGINE" / "_VOLUME.yml")
    assert vol["volume"] == "07"
    assert vol["nome"] == "PROMPT-ENGINE"
    assert vol["tipo"] == "ENGINE"
    assert vol["status"] == "RASCUNHO"
    assert vol["perecivel"] is False
    assert vol["depende_de"] == []
    assert vol["escopo"] == ""
    assert ler_volume_yml(acervo / "26-AI-MODELS" / "_VOLUME.yml")["perecivel"] is True


def test_volume_yml_gerado_passa_o_gate_de_volume(acervo):
    """O gate nao pode reprovar a estrutura que a propria maquina gerou."""
    ct = C.carregar(acervo)
    SC.criar_volumes(acervo, ct)
    violacoes = V.validar_volume(acervo, "07", ct)
    assert [v for v in violacoes if v.regra in ("volume-yml", "volume-tipo")] == []
    # As 18 secoes e os diagramas obrigatorios do ENGINE ainda faltam: essas
    # violacoes sao esperadas num volume recem-criado, e so essas.
    assert {v.regra for v in violacoes} == {"secao-ausente", "diagrama-obrigatorio"}
    assert len([v for v in violacoes if v.regra == "secao-ausente"]) == 18


def test_cli_cria_e_reporta(acervo, capsys):
    assert SC.main(["--raiz", str(acervo)]) == 0
    assert "42" in capsys.readouterr().out
    assert SC.main(["--raiz", str(acervo)]) == 0
    assert "nada" in capsys.readouterr().out.lower()


def test_cli_sem_contrato_devolve_2(tmp_path, capsys):
    assert SC.main(["--raiz", str(tmp_path)]) == 2
