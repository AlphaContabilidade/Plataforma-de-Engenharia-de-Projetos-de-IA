"""Testa o carregamento do contrato e a resolucao de secoes por tipo."""
import re
from pathlib import Path

import pytest

from ferramentas import contrato as C

RAIZ = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def ct():
    return C.carregar(RAIZ)


def test_dezoito_secoes_base(ct):
    assert len(ct.secoes_base) == 18
    assert ct.secoes_base[0] == "01-Introducao"
    assert ct.secoes_base[-1] == "18-Referencias-Cruzadas"


def test_status_validos_sao_exatamente_tres(ct):
    assert ct.status_validos == ("RASCUNHO", "REQUER_REVISAO", "PRONTO")


def test_engine_usa_todas_as_dezoito(ct):
    assert ct.secoes_de("ENGINE") == ct.secoes_base


def test_biblioteca_troca_arquitetura_por_catalogo(ct):
    secoes = ct.secoes_de("BIBLIOTECA")
    assert "04-Arquitetura" not in secoes
    assert "05-Diagramas" not in secoes
    assert "04-Catalogo" in secoes


def test_processo_dispensa_modelos(ct):
    assert "08-Modelos" not in ct.secoes_de("PROCESSO")


def test_secoes_saem_em_ordem_numerica(ct):
    for tipo in ct.tipos:
        prefixos = [int(s[:2]) for s in ct.secoes_de(tipo)]
        assert prefixos == sorted(prefixos), tipo


def test_tipo_desconhecido_lista_os_aceitos(ct):
    with pytest.raises(C.ContratoInvalido) as erro:
        ct.secoes_de("INVENTADO")
    assert "ENGINE" in str(erro.value)


def test_os_42_volumes_estao_declarados(ct):
    assert set(ct.volumes) == {f"{n:02d}" for n in range(1, 43)}


def test_todo_volume_tem_tipo_conhecido(ct):
    for vol_id, meta in ct.volumes.items():
        assert meta["tipo"] in ct.tipos, f"{vol_id} tem tipo invalido"


def test_volume_07_e_prompt_engine_do_tipo_engine(ct):
    assert ct.volume("07") == {"nome": "PROMPT-ENGINE", "tipo": "ENGINE", "perecivel": False}


def test_pereciveis_sao_os_tres_previstos(ct):
    assert {v for v, m in ct.volumes.items() if m["perecivel"]} == {"26", "27", "34"}


def test_volume_inexistente_falha(ct):
    with pytest.raises(C.ContratoInvalido, match="99"):
        ct.volume("99")


def test_minimo_por_secao_tem_fallback(ct):
    assert ct.minimo_de("04-Arquitetura") == ct.min_palavras
    assert ct.minimo_de("15-Checklist") == 120


def test_convencoes_nao_derivou(ct):
    """A tabela de tipos em Convencoes.md tem de refletir contrato.json."""
    texto = (RAIZ / "00-INTRODUCAO" / "Convencoes.md").read_text(encoding="utf-8")
    for tipo in ct.tipos:
        linha = next(
            (ln for ln in texto.splitlines() if ln.strip().startswith(f"| `{tipo}`")), None
        )
        assert linha, f"tipo {tipo} ausente da tabela de Convencoes.md"
        declarados = set(re.findall(r"\b(\d{2})\b", linha.split("|")[2]))
        esperados = {v for v, m in ct.volumes.items() if m["tipo"] == tipo}
        assert declarados == esperados, f"{tipo}: Convencoes.md diverge de contrato.json"
