"""Executa o passo a passo escrito em `03-DISCOVERY/12-Exemplos.md`.

Este arquivo fecha uma lacuna que o volume declarava em `15-Checklist.md`: os blocos
de codigo daquela secao sao cheios de `assert`, mas nada os executava. Prosa com
`assert` que ninguem roda e prosa, nao verificacao — e envelhece exatamente como
qualquer outro numero escrito a mao.

A lacuna nao era teorica. Acrescentar o termo "loja" a tabela de contexto de
`deteccao.py` mexeu na deteccao da frase do proprio passo a passo, que fala em
"minha loja de bairro". Nada quebrou (o palpite de "pagamento", de confianca ALTA,
absorve o de "loja", de confianca MEDIA), mas *saber* que nada quebrou dependia de
alguem lembrar de rodar aquilo a mao.

O que este teste NAO cobre continua valendo: os numeros escritos por extenso na
prosa em volta dos blocos — "trinta e sete lacunas", "catorze perguntas" — nao sao
lidos por ninguem. Se um bloco mudar de resultado, este teste fica vermelho; se a
frase ao lado dele mentir, continua verde.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

CERCA = chr(96) * 3
_BLOCO = re.compile(CERCA + r"python\n(.*?)" + CERCA, re.S)

_AQUI = Path(__file__).resolve()
_EXEMPLO = _AQUI.parents[1]
_SECAO = _AQUI.parents[3] / "03-DISCOVERY" / "12-Exemplos.md"


def _blocos() -> list[str]:
    return _BLOCO.findall(_SECAO.read_text(encoding="utf-8"))


def test_a_secao_de_exemplos_existe_e_tem_codigo():
    """Guarda contra o modo de falha silencioso: secao renomeada, zero blocos, tudo verde."""
    assert _SECAO.is_file(), f"nao achei {_SECAO}"
    assert len(_blocos()) >= 8


def test_o_passo_a_passo_documentado_roda_sem_quebrar_nenhum_assert():
    """Os blocos rodam em sequencia, no mesmo escopo, como quem le de cima para baixo.

    Escopo compartilhado e proposital: o passo 5 depende da entrevista construida no
    passo 3. Rodar cada bloco isolado passaria a testar outra coisa que nao o texto.
    """
    if str(_EXEMPLO) not in sys.path:
        sys.path.insert(0, str(_EXEMPLO))

    escopo: dict[str, object] = {}
    for numero, corpo in enumerate(_blocos(), 1):
        try:
            exec(compile(corpo, f"12-Exemplos.md bloco {numero}", "exec"), escopo)
        except AssertionError as erro:  # pragma: no cover - so roda quando o texto mente
            pytest.fail(
                f"o bloco {numero} de 12-Exemplos.md afirma algo que o motor nao faz mais: {erro}"
            )
