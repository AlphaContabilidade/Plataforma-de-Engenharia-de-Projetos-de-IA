---
volume: "03"
volume_nome: DISCOVERY
tipo: PROCESSO
secao: 12-Exemplos
status: PRONTO
atualizado_em: 2026-07-30
---

# Exemplos

O exemplo desta seção é um caminho ponta a ponta em nove passos, a partir de uma frase que uma
pessoa real escreveria: uma loja de bairro que quer vender pela internet. Detectar da frase, recusar
a inferência errada, confirmar as certas, destravar um bloco respondendo uma pergunta, percorrer as
perguntas por ordem de valor, parar, gerar a especificação, e medir o que teria acontecido se a
inferência errada tivesse sido aceita em silêncio.

Todos os números e todas as frases citadas abaixo foram **medidos executando este código** contra os
módulos reais, com asserções em cada passo. Onde a medição contrariou a expectativa, o texto foi
corrigido, e não a medição — e uma dessas correções mudou o código, não o texto.

<!-- exemplo: exemplos/03-discovery/catalogo.py -->
<!-- exemplo: exemplos/03-discovery/deteccao.py -->
<!-- exemplo: exemplos/03-discovery/entrevista.py -->
<!-- exemplo: exemplos/03-discovery/especificacao.py -->

## Preparação

```python
from catalogo import CATALOGO, Contexto, Plataforma, lacunas_ativas
from deteccao import detectar_contextos, detectar_plataformas
from entrevista import Entrevista
from especificacao import gerar

IDEIA = (
    "Quero um app para a minha loja de bairro, com pagamento no cartão de crédito "
    "e um cadastro de clientes para avisar das promoções."
)

assert len(CATALOGO) == 37
assert sum(1 for l in CATALOGO if l.universal) == 6
assert len(lacunas_ativas((), ())) == 6
assert len(lacunas_ativas(tuple(Plataforma), tuple(Contexto))) == 37
```

Trinta e sete lacunas no catálogo, seis universais. Sem plataforma e sem contexto confirmados, seis
estão ativas — as universais e nada mais. Com as quatro plataformas e os seis contextos todos
confirmados, as trinta e sete estão ativas, o que é a prova de que nenhuma lacuna está inalcançável
por gatilho impossível.

## Passo 1: três inferências, cada uma com o seu trecho

```python
palpites = (*detectar_plataformas(IDEIA), *detectar_contextos(IDEIA))
assert [(p.valor, p.confianca) for p in palpites] == [
    ("MOBILE", "BAIXA"),
    ("LOJA_PAGAMENTOS", "ALTA"),
    ("DADO_PESSOAL", "MEDIA"),
]
assert [p.evidencia for p in palpites] == [
    "Quero um app para a minha",
    "de bairro, com pagamento no cartão de",
    "crédito e um cadastro de clientes para",
]
assert len({p.evidencia for p in palpites}) == 3
```

Cada palpite carrega o trecho que o produziu, e os três trechos são **diferentes**. A confiança do
primeiro é baixa de propósito: "app" é usado com a mesma naturalidade para coisa que roda em
navegador, e a tabela de termos declara isso. Repare que o acento sobreviveu — a evidência sai do
texto original, e não da versão normalizada usada para casar os termos.

Este parágrafo é o lugar de registrar a correção que a medição impôs, porque ela é o assunto da
seção. A primeira versão de `deteccao.py` devolvia a **frase inteira** como evidência, com o
argumento de que a frase é a unidade que a pessoa reconhece como sua. Ao executar, os três palpites
saíram com evidência idêntica: a ideia é escrita em uma frase só, e a frase inteira aparecia três
vezes. Evidência que não distingue um palpite do outro não explica nenhum dos dois — a pergunta "por
que você achou que era um aplicativo de celular?" recebia de volta o texto que também falava de
pagamento e de cadastro. A janela de três palavras de cada lado corrigiu o problema, e a última
asserção acima existe para impedir a volta. Nenhum gate teria pegado isso: o código rodava, os
testes passavam, e a prosa estava plausível.

## Passo 2: sem sinal, nenhum palpite

```python
for vaga in ("", "   ", "Quero uma coisa melhor do que a que eu tenho hoje."):
    assert detectar_plataformas(vaga) == ()
    assert detectar_contextos(vaga) == ()
```

Frase vazia e frase sem termo conhecido devolvem tupla vazia. Não existe palpite genérico de reserva,
e a ausência dele é o desenho: um valor adotado por falta de sinal seria o padrão silencioso que a
especificação proíbe, com a agravante de vir rotulado como inferência e com evidência inventada.

## Passo 3: a entrevista antes de qualquer confirmação

```python
e = Entrevista(IDEIA)
assert e.peso_minimo == 4
assert [p.valor for p in e.palpites_pendentes()] == ["MOBILE", "LOJA_PAGAMENTOS", "DADO_PESSOAL"]
assert e.plataformas() == () and e.contextos() == ()
assert e.respostas() == ()

assert [(l.id, l.peso) for l in e.pendentes()] == [
    ("problema", 10), ("onde_roda", 10), ("usuario", 9),
    ("capacidade_nova", 9), ("sucesso", 8), ("fora_de_escopo", 7),
]
assert e.progresso() == (0, 6)
assert e.proxima().id == "problema"        # empate de peso 10 resolvido pelo catalogo
```

Nada foi aplicado. Os três palpites estão pendentes, os conjuntos de plataforma e de contexto estão
vazios, e por isso só as seis universais aparecem — nenhuma pergunta de pagamento, nenhuma de
aparelho de mão. A fila está ordenada por peso decrescente, e o empate entre as duas de peso dez
resolve pela ordem do catálogo: `problema` vem antes de `onde_roda`, sempre, em qualquer execução.

## Passo 4: recusar a inferência errada, confirmar as duas certas

```python
app = next(p for p in e.palpites_pendentes() if p.valor == "MOBILE")
e.recusar(app)
for p in list(e.palpites_pendentes()):
    e.confirmar(p)

assert e.palpites_pendentes() == ()
assert e.plataformas() == ()                                  # recusar nao aplica nada
assert e.contextos() == (Contexto.LOJA_PAGAMENTOS, Contexto.DADO_PESSOAL)
assert len(e.pendentes()) == 11
assert e.progresso() == (0, 11)
assert [l.id for l in e.pendentes()][:5] == [
    "problema", "onde_roda", "usuario", "capacidade_nova", "pag_cobranca_dupla",
]
```

A recusa não deixou rastro: o conjunto de plataformas continua vazio, nada foi gravado em `respostas`
e nenhuma lacuna de aparelho de mão apareceu. As duas confirmações destravaram cinco lacunas — três
de pagamento e duas de dado pessoal —, e a fila foi de seis para onze. Repare onde
`pag_cobranca_dupla` entrou: em quinto lugar, com peso nove, à frente de `sucesso` e de
`fora_de_escopo`. A pergunta sobre cobrar duas vezes vale mais que a pergunta sobre o número de
sucesso neste caso, e é o peso que diz isso, não a ordem em que os assuntos foram mencionados.

## Passo 5: uma resposta que destrava um bloco

```python
antes = {l.id for l in e.pendentes()}
alvo_antes = e.progresso()[1]

e.responder("problema", "quem passa na frente da loja nao sabe o que tem dentro")
e.responder("onde_roda", "WEB")

assert e.plataformas() == (Plataforma.WEB,)
assert {l.id for l in e.pendentes()} - antes == {
    "web_autenticacao", "web_hospedagem", "web_navegador",
}
assert (alvo_antes, e.progresso()[1]) == (11, 14)
assert e.progresso() == (2, 14)
```

Responder `onde_roda` com `"WEB"` destravou três lacunas de navegador, e o **denominador** do
progresso subiu de onze para catorze. Nenhum caso especial por identificador está envolvido: o valor
da resposta corresponde ao nome de um membro de `Plataforma`, e a regra genérica de destravamento fez
o resto. A barra de progresso recuou em termos relativos — duas de catorze é menos que duas de onze —
e isso é o comportamento correto. Progresso que só anda para frente exigiria fingir que o total era
conhecido desde o início, e num grafo de decisão ele não é.

## Passo 6: as perguntas, por ordem de valor, até não valer mais

```python
ordem = []
while (lacuna := e.proxima()) is not None:
    ordem.append((lacuna.id, lacuna.peso))
    e.responder(lacuna.id, f"resposta de {lacuna.id}")

assert ordem == [
    ("usuario", 9), ("capacidade_nova", 9), ("pag_cobranca_dupla", 9),
    ("sucesso", 8), ("pag_provedor", 8), ("pessoal_base_legal", 8),
    ("fora_de_escopo", 7), ("web_autenticacao", 7), ("pag_estorno", 7),
    ("pessoal_exclusao", 7), ("web_hospedagem", 6), ("web_navegador", 5),
]
assert len(ordem) == 12                     # mais as duas do passo 5 = 14 perguntas
assert e.progresso() == (14, 14)
assert e.proxima() is None
```

Doze perguntas neste laço, catorze somando as duas do passo anterior. A ordem é estritamente
decrescente em peso, e dentro de cada peso é a do catálogo — os três pesos nove vêm antes dos três
pesos oito, e assim por diante. `proxima()` devolveu `None` ao chegar em `web_navegador`, de peso
cinco: a lacuna seguinte na fila teria peso três, abaixo do mínimo de quatro, e por isso não foi
perguntada.

## Passo 7: a especificação, com a decisão que não foi perguntada

```python
spec = gerar(e)
assert spec.completa is True
assert spec.plataformas == (Plataforma.WEB,)
assert spec.contextos == (Contexto.LOJA_PAGAMENTOS, Contexto.DADO_PESSOAL)
assert len(spec.respostas) == 14
assert spec.inferencias_pendentes == ()
assert [(l.id, l.peso, l.universal) for l in spec.decisoes_abertas] == [("web_idioma", 3, False)]

md = spec.markdown()
assert len(md.splitlines()) == 44
assert "## Decisoes abertas" in md and "## Inferencias nao confirmadas" in md
assert "Nenhuma. Toda inferencia foi confirmada ou recusada." in md
assert "A primeira versao precisa de mais de um idioma?" in md
```

A especificação se declara completa, e tem o direito: não há inferência pendente e não há lacuna
universal aberta. Ela **não** está vazia de pendências, e é aí que está o ponto — `web_idioma`, de
peso três, ficou aberta e aparece no markdown com a pergunta inteira e o motivo. O motor escolheu não
gastar um turno com ela e registrou a escolha por escrito. Um instrumento que a omitisse produziria a
mesma especificação com uma informação a menos, e ninguém notaria a diferença até alguém precisar de
dois idiomas.

## Passo 8: o custo de aceitar a inferência de confiança baixa

```python
errada = Entrevista(IDEIA)
for p in list(errada.palpites_pendentes()):
    errada.confirmar(p)                     # inclusive o MOBILE de confianca BAIXA
errada.responder("onde_roda", "MOBILE")

perguntas_erradas = [l.id for l in errada.pendentes()]
while (l := errada.proxima()) is not None:
    errada.responder(l.id, "x")

assert errada.plataformas() == (Plataforma.MOBILE,)
assert len(perguntas_erradas) + 1 == 15     # uma pergunta a mais que o caminho correto
assert sorted(i for i in perguntas_erradas if i.startswith("mobile_")) == [
    "mobile_loja", "mobile_notificacao", "mobile_offline", "mobile_permissao",
]
assert not [i for i in perguntas_erradas if i.startswith("web_")]
assert [l.id for l in gerar(errada).decisoes_abertas] == ["mobile_tablet"]
```

Este é o anti-padrão A2 de [`10-Anti-Patterns.md`](10-Anti-Patterns.md) em números. Aceitar o palpite
de confiança baixa produz quinze perguntas em vez de catorze, e a contagem é a parte menos grave:
quatro delas são de aparelho de mão — rede ausente, loja de aplicativos, permissão de dispositivo,
notificação — e não se aplicam a uma página que os clientes abrem no navegador, enquanto as três de
navegador nunca são feitas. Sete das quinze perguntas erradas, sem que nada no processo apite, porque
o caminho é internamente coerente: as perguntas de aparelho de mão são exatamente as certas **para a
plataforma errada**.

A diferença entre este passo e o passo 4 é uma pessoa tendo visto o trecho `Quero um app para a
minha` e dito que não. É por isso que a evidência viaja junto e é por isso que confiança alta não
dispensa confirmação.

## Passo 9: o mesmo caminho com o limiar em um

```python
tudo = Entrevista(IDEIA, peso_minimo=1)
for p in list(tudo.palpites_pendentes()):
    if p.valor == "MOBILE":
        tudo.recusar(p)
    else:
        tudo.confirmar(p)
tudo.responder("onde_roda", "WEB")

perguntas = 1
while (lacuna := tudo.proxima()) is not None:
    tudo.responder(lacuna.id, "x")
    perguntas += 1

spec_tudo = gerar(tudo)
assert perguntas == 15                      # contra 14 com o limiar padrao
assert spec_tudo.decisoes_abertas == ()
assert spec_tudo.completa is True
assert len(tudo.ativas()) == 15
```

Com o limiar em um, o motor pergunta as quinze lacunas ativas e não sobra decisão aberta. A diferença
é de uma pergunta — modesta neste caso, porque só `web_idioma` está abaixo do mínimo nesta combinação
de plataforma e contextos. A comparação que importa não é catorze contra quinze: é quinze contra
**trinta e sete**, que é o que um formulário fixo perguntaria. O limiar economiza no detalhe; o grafo
de decisão economiza na ordem de grandeza. As duas economias são independentes, e é por isso que o
limiar ser parâmetro não afrouxa nada — a economia grande vem da relevância, e relevância não tem
parâmetro.
