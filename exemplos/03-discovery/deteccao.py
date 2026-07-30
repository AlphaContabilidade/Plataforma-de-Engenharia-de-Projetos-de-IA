"""O que se pode inferir da frase inicial -- e sempre com o trecho que provou.

Nao perguntar o que se pode inferir e metade do principio. A outra metade e nunca
usar inferencia em silencio, e as duas juntas produzem uma regra so: **palpite sem
evidencia nao e produzido.** Se este modulo nao consegue dizer que trecho o levou a
concluir `MOBILE`, ele nao conclui `MOBILE`.

A ideia de `Origem` vem do mesmo lugar que a de `12-MEMORY`: guardar de onde cada
informacao veio e o que permite distinguir o que a pessoa disse do que o programa
supos. Sem esse campo, uma inferencia razoavel entra na especificacao com a mesma
autoridade de uma resposta, e ninguem consegue mais separar as duas -- nem quem
escreveu, uma semana depois.

O casamento e por termo, sobre o texto dobrado para minusculas e sem acento, com
fronteira de palavra exigida nos dois lados. Termo e nao modelo estatistico por uma
razao de projeto: aqui o custo de um falso positivo e uma pergunta de confirmacao,
e o custo de um falso negativo e uma pergunta a mais na entrevista. Nenhum dos dois
justifica um componente que nao se explica -- e explicar-se e literalmente o
requisito, porque `Palpite.evidencia` tem de conter um trecho real do que a pessoa
escreveu.

O que este modulo deliberadamente NAO faz: nao confirma, nao recusa e nao decide
nada. Ele produz candidatos com procedencia; quem os aceita e `entrevista.py`, e
apenas quando uma pessoa disser que sim.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import StrEnum

from catalogo import Contexto, Plataforma

CONFIANCA_ALTA = "ALTA"
CONFIANCA_MEDIA = "MEDIA"
CONFIANCA_BAIXA = "BAIXA"


class Origem(StrEnum):
    """De onde a informacao veio. Nunca e metadado decorativo.

    - `RESPONDIDO`: a pessoa disse. Unica origem que dispensa confirmacao.
    - `INFERIDO`: o programa concluiu de um trecho do texto. Vale como candidato e
      nada mais; entra na especificacao so depois de confirmado, e enquanto nao for
      aparece na secao de inferencias nao confirmadas.
    - `PADRAO_ASSUMIDO`: valor que o programa adotaria por falta de resposta. Existe
      nomeado justamente para que se possa proibi-lo de circular como decisao: a
      especificacao trata lacuna sem resposta como decisao aberta, e nao como
      padrao silencioso.

    A ordem de declaracao nao e ordem de autoridade. Autoridade e assunto de
    `entrevista.py` e de `especificacao.py`, cada um em um lugar so.
    """

    RESPONDIDO = "RESPONDIDO"
    INFERIDO = "INFERIDO"
    PADRAO_ASSUMIDO = "PADRAO_ASSUMIDO"


@dataclass(frozen=True, slots=True)
class Palpite:
    """Uma conclusao candidata, com o trecho que a produziu.

    Congelado porque evidencia nao se edita: se a conclusao mudar, o palpite e
    outro. `valor` e o nome de um membro de `Plataforma` ou de `Contexto`, em
    texto, para que o palpite viaje entre camadas sem que cada uma precise conhecer
    as duas enumeracoes.

    `evidencia` e o trecho do texto original -- com acento e caixa preservados,
    como a pessoa escreveu. E o campo que torna o palpite discutivel: quem le "por
    que voce achou que era um aplicativo de celular?" recebe a frase de volta, e
    nao uma alegacao de que o modelo achou.

    `confianca` e texto de tres valores conhecidos (`ALTA`, `MEDIA`, `BAIXA`) e
    serve para ordenar a conversa de confirmacao, nunca para dispensa-la. Palpite de
    confianca alta continua sendo palpite.
    """

    valor: str
    origem: Origem
    evidencia: str
    confianca: str


# Termo, alvo e confianca. A ordem importa duas vezes: define qual termo produz a
# evidencia quando dois casam o mesmo alvo (o primeiro ganha) e define a ordem de
# leitura para quem for revisar a tabela. Nenhum termo aparece em dois alvos.
_TERMOS_PLATAFORMA: tuple[tuple[str, Plataforma, str], ...] = (
    ("navegador", Plataforma.WEB, CONFIANCA_ALTA),
    ("no browser", Plataforma.WEB, CONFIANCA_ALTA),
    ("pagina web", Plataforma.WEB, CONFIANCA_ALTA),
    ("site", Plataforma.WEB, CONFIANCA_MEDIA),
    ("portal", Plataforma.WEB, CONFIANCA_MEDIA),
    ("celular", Plataforma.MOBILE, CONFIANCA_ALTA),
    ("telefone", Plataforma.MOBILE, CONFIANCA_MEDIA),
    ("android", Plataforma.MOBILE, CONFIANCA_ALTA),
    ("iphone", Plataforma.MOBILE, CONFIANCA_ALTA),
    ("aplicativo", Plataforma.MOBILE, CONFIANCA_MEDIA),
    # "app" e usado com a mesma naturalidade para coisa que roda em navegador. Fica
    # como BAIXA de proposito: e o palpite que existe para ser recusado sem
    # cerimonia, e a taxa de recusa dele e o termometro da tabela.
    ("app", Plataforma.MOBILE, CONFIANCA_BAIXA),
    ("windows", Plataforma.DESKTOP, CONFIANCA_MEDIA),
    ("macos", Plataforma.DESKTOP, CONFIANCA_MEDIA),
    ("instalado na maquina", Plataforma.DESKTOP, CONFIANCA_ALTA),
    ("programa de computador", Plataforma.DESKTOP, CONFIANCA_MEDIA),
    ("automatizar", Plataforma.AUTOMACAO, CONFIANCA_ALTA),
    ("automacao", Plataforma.AUTOMACAO, CONFIANCA_ALTA),
    ("sem intervencao", Plataforma.AUTOMACAO, CONFIANCA_ALTA),
    ("toda noite", Plataforma.AUTOMACAO, CONFIANCA_MEDIA),
    ("todo dia as", Plataforma.AUTOMACAO, CONFIANCA_MEDIA),
    ("rotina", Plataforma.AUTOMACAO, CONFIANCA_BAIXA),
)

_TERMOS_CONTEXTO: tuple[tuple[str, Contexto, str], ...] = (
    ("pagamento", Contexto.LOJA_PAGAMENTOS, CONFIANCA_ALTA),
    ("cartao de credito", Contexto.LOJA_PAGAMENTOS, CONFIANCA_ALTA),
    ("checkout", Contexto.LOJA_PAGAMENTOS, CONFIANCA_ALTA),
    ("carrinho", Contexto.LOJA_PAGAMENTOS, CONFIANCA_MEDIA),
    ("cobrar", Contexto.LOJA_PAGAMENTOS, CONFIANCA_MEDIA),
    ("vender online", Contexto.LOJA_PAGAMENTOS, CONFIANCA_MEDIA),
    ("paciente", Contexto.SAUDE, CONFIANCA_ALTA),
    ("prontuario", Contexto.SAUDE, CONFIANCA_ALTA),
    ("clinica", Contexto.SAUDE, CONFIANCA_MEDIA),
    ("consultorio", Contexto.SAUDE, CONFIANCA_MEDIA),
    ("vacina", Contexto.SAUDE, CONFIANCA_MEDIA),
    ("cpf", Contexto.DADO_PESSOAL, CONFIANCA_ALTA),
    ("dado pessoal", Contexto.DADO_PESSOAL, CONFIANCA_ALTA),
    ("dados pessoais", Contexto.DADO_PESSOAL, CONFIANCA_ALTA),
    ("cadastro de cliente", Contexto.DADO_PESSOAL, CONFIANCA_MEDIA),
    ("cadastro de clientes", Contexto.DADO_PESSOAL, CONFIANCA_MEDIA),
    ("equipe", Contexto.MULTIUSUARIO, CONFIANCA_MEDIA),
    ("funcionarios", Contexto.MULTIUSUARIO, CONFIANCA_MEDIA),
    ("varios usuarios", Contexto.MULTIUSUARIO, CONFIANCA_ALTA),
    ("cada vendedor", Contexto.MULTIUSUARIO, CONFIANCA_ALTA),
    ("permissao", Contexto.MULTIUSUARIO, CONFIANCA_BAIXA),
    ("tempo real", Contexto.TEMPO_REAL, CONFIANCA_ALTA),
    ("ao vivo", Contexto.TEMPO_REAL, CONFIANCA_ALTA),
    ("na hora", Contexto.TEMPO_REAL, CONFIANCA_BAIXA),
    ("instantaneo", Contexto.TEMPO_REAL, CONFIANCA_MEDIA),
    ("integrar com", Contexto.INTEGRACAO_EXTERNA, CONFIANCA_ALTA),
    ("integracao com", Contexto.INTEGRACAO_EXTERNA, CONFIANCA_ALTA),
    ("sincronizar com", Contexto.INTEGRACAO_EXTERNA, CONFIANCA_ALTA),
    ("puxar do", Contexto.INTEGRACAO_EXTERNA, CONFIANCA_MEDIA),
    ("importar de", Contexto.INTEGRACAO_EXTERNA, CONFIANCA_MEDIA),
)

_FIM_DE_FRASE = re.compile(r"[.!?;\n]")


def _dobrar(texto: str) -> tuple[str, list[int]]:
    """Devolve (texto sem acento e em minusculas, posicao original de cada caractere).

    A lista de posicoes existe porque a evidencia tem de sair do texto **original**:
    devolver o texto dobrado como evidencia entregaria a pessoa uma versao sem
    acento da propria frase, o que parece defeito e destroi a confianca no que o
    motor mostra. A normalizacao roda caractere a caractere para que cada caractere
    produzido saiba de qual caractere original ele veio.
    """
    saida: list[str] = []
    mapa: list[int] = []
    for posicao, caractere in enumerate(texto):
        for parte in unicodedata.normalize("NFD", caractere):
            if unicodedata.combining(parte):
                continue
            saida.append(parte.lower())
            mapa.append(posicao)
    return "".join(saida), mapa


def _fronteira(dobrado: str, inicio: int, fim: int) -> bool:
    """O casamento comeca e termina em fronteira de palavra?

    Sem esta verificacao, `app` casaria dentro de `aplicativo` e produziria dois
    palpites da mesma plataforma com evidencias diferentes; `site` casaria dentro de
    `deposite`. Fronteira de palavra e a diferenca entre uma tabela de termos e uma
    tabela de substrings.
    """
    antes_ok = inicio == 0 or not (dobrado[inicio - 1].isalnum() or dobrado[inicio - 1] == "_")
    depois_ok = fim >= len(dobrado) or not (dobrado[fim].isalnum() or dobrado[fim] == "_")
    return antes_ok and depois_ok


PALAVRAS_DE_MARGEM = 3


def _limites_da_frase(texto: str, posicao: int) -> tuple[int, int]:
    """Inicio e fim da frase do texto original que contem a posicao dada."""
    inicio = 0
    for casado in _FIM_DE_FRASE.finditer(texto, 0, posicao):
        inicio = casado.end()
    seguinte = _FIM_DE_FRASE.search(texto, posicao)
    fim = seguinte.start() if seguinte else len(texto)
    return inicio, fim


def _trecho_em(texto: str, posicao: int, margem: int = PALAVRAS_DE_MARGEM) -> str:
    """A palavra casada mais algumas de cada lado, sem sair da frase.

    A primeira versao deste modulo devolvia a **frase inteira** como evidencia, com
    o argumento de que a frase e a unidade que a pessoa reconhece como sua. Rodar o
    passo a passo de `12-Exemplos.md` desmontou o argumento: numa ideia escrita em
    uma frase so, os tres palpites saiam com evidencia **identica** -- o texto todo,
    tres vezes. Evidencia que nao distingue um palpite do outro nao explica nenhum
    dos dois, e a pergunta "por que voce achou que era um aplicativo?" recebia de
    volta a frase que tambem falava de pagamento e de cadastro.

    A janela de palavras corrige isso e mantem contexto suficiente para reconhecer o
    proprio texto. Ela e limitada pela frase de proposito: atravessar o ponto final
    juntaria duas ideias diferentes numa evidencia so, que e o defeito anterior em
    escala menor.
    """
    inicio_frase, fim_frase = _limites_da_frase(texto, posicao)
    palavras = [(m.start(), m.end()) for m in re.finditer(r"\S+", texto[inicio_frase:fim_frase])]
    if not palavras:
        return texto[inicio_frase:fim_frase].strip()
    relativa = posicao - inicio_frase
    alvo = next(
        (n for n, (comeca, termina) in enumerate(palavras) if comeca <= relativa < termina),
        0,
    )
    primeira = max(0, alvo - margem)
    ultima = min(len(palavras) - 1, alvo + margem)
    return texto[inicio_frase + palavras[primeira][0] : inicio_frase + palavras[ultima][1]].strip()


def _detectar(
    ideia: str, termos: tuple[tuple[str, object, str], ...]
) -> tuple[Palpite, ...]:
    """Um palpite por alvo, do primeiro termo que casou, na ordem da tabela.

    Um alvo, um palpite. Dois termos da mesma plataforma nao produzem dois palpites,
    porque a pessoa nao tem duas confirmacoes para dar -- ela tem uma, e receber a
    mesma pergunta duas vezes com evidencias diferentes soa a interrogatorio.

    Texto vazio, ou texto sem nenhum termo, devolve tupla vazia. **Nao existe
    palpite generico de fallback.** Um valor adotado por falta de sinal seria
    exatamente o padrao silencioso que a especificacao proibe, com a agravante de
    vir rotulado como inferencia e com evidencia inventada.
    """
    dobrado, mapa = _dobrar(ideia or "")
    if not dobrado.strip():
        return ()

    encontrados: dict[object, Palpite] = {}
    for termo, alvo, confianca in termos:
        if alvo in encontrados:
            continue
        posicao = 0
        while True:
            achou = dobrado.find(termo, posicao)
            if achou < 0:
                break
            if _fronteira(dobrado, achou, achou + len(termo)):
                encontrados[alvo] = Palpite(
                    valor=str(alvo),
                    origem=Origem.INFERIDO,
                    evidencia=_trecho_em(ideia, mapa[achou]),
                    confianca=confianca,
                )
                break
            posicao = achou + 1
    # A ordem de insercao do dicionario e a ordem da tabela: o alvo entra na
    # primeira vez que um termo dele casa, e os termos sao percorridos na ordem
    # declarada. Nada aqui depende da ordem em que os termos aparecem no texto, e e
    # por isso que a saida e a mesma para a mesma frase, sempre.
    return tuple(encontrados.values())


def detectar_plataformas(ideia: str) -> tuple[Palpite, ...]:
    """Plataformas inferidas do texto, uma por plataforma, na ordem da tabela.

    Pode devolver mais de uma: "um app e um site para a loja" e web e mobile, e
    reduzir isso a uma escolha unica seria o motor decidindo o que a pessoa nao
    disse. Cada palpite viaja separado e e confirmado separado.
    """
    return _detectar(ideia, _TERMOS_PLATAFORMA)


def detectar_contextos(ideia: str) -> tuple[Palpite, ...]:
    """Contextos inferidos do texto, um por contexto, na ordem da tabela.

    Sobreposicao e esperada e correta: uma clinica que cobra consulta aciona saude,
    dado pessoal e pagamento ao mesmo tempo, e cada um destrava perguntas que os
    outros nao fazem.
    """
    return _detectar(ideia, _TERMOS_CONTEXTO)
