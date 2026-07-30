---
volume: "12"
volume_nome: MEMORY
tipo: ENGINE
secao: 12-Exemplos
status: PRONTO
atualizado_em: 2026-07-30
---

# Exemplos

O exemplo desta seção é um caminho ponta a ponta em sete passos: registrar observação,
contaminar a memória com a escrita do próprio agente, introduzir uma base congelada que
discorda, encontrar uma chave que não decide, resolvê-la com decisão humana, mostrar a
expiração mudando o veredicto sem mudar o armazém, e consultar uma chave que nunca existiu.
Todos os números e todas as frases citadas abaixo foram **medidos executando este código**
contra os módulos reais, com asserções em cada passo. Onde a medição contrariou a expectativa,
o texto foi corrigido, e não a medição.

<!-- exemplo: exemplos/12-memory/memoria_observada.py -->
<!-- exemplo: exemplos/12-memory/contaminacao.py -->
<!-- exemplo: exemplos/12-memory/precedencia.py -->

## Preparação

```python
from datetime import date

from contaminacao import contradicoes, filtrar_contaminacao
from memoria_observada import Entrada, MemoriaObservada, Origem
from precedencia import Confianca, resolver

HOJE = date(2026, 7, 30)
CHAVE = "evento:renovacao-mensal-assinatura"
mem = MemoriaObservada()

def registrar(chave, decisao, origem, em, n=1, evidencia=""):
    for _ in range(n):
        mem.registrar(Entrada(chave=chave, decisao=decisao, origem=origem,
                              em=em, evidencia=evidencia))
```

A data de referência é uma constante do exemplo, e não `date.today()`, pela mesma razão que a
faz parâmetro em `resolver`: com a data por fora, o resultado é o mesmo em qualquer dia em que
alguém rode o código. As decisões são nomes de fila de atendimento, e a chave é um tipo de
evento recorrente — o domínio do componente é decisão observada, não nenhum assunto específico.

## Passo 1: dez observações, nove concordantes

```python
registrar(CHAVE, "fila-financeiro", Origem.OBSERVADO, date(2026, 5, 10), n=9,
          evidencia="rotulo conferido por pessoa na triagem de maio")
registrar(CHAVE, "fila-suporte", Origem.OBSERVADO, date(2026, 5, 12))

v = resolver(mem, CHAVE, hoje=HOJE)
assert v.decisao == "fila-financeiro"
assert v.confianca is Confianca.ALTA
assert v.descartadas == 0 and v.contradicoes == ()
# justificativa:
# 'dominancia observada 9/10 = 0.900, minimo 0.700, em 10 observacao(oes)
#  vigente(s) na janela de 365 dias'
```

A justificativa carrega os quatro números que sustentam a decisão: quantas concordaram, sobre
quantas, a fração e o mínimo exigido. Nenhum deles é opcional para quem vai auditar depois — é
a diferença entre "o agente decidiu com confiança alta" e "nove de dez observações
independentes dos últimos oitenta e um dias concordaram". Oitenta e um, e não oitenta: a
observação mais antiga é de 2026-05-10 e a data de referência é 2026-07-30, o que dá
`(HOJE - date(2026, 5, 10)).days == 81`. Aproximar para um número redondo não custaria nada
neste parágrafo e custaria a única coisa que a seção afirma sobre si mesma.

## Passo 2: o agente contamina a própria memória

```python
registrar(CHAVE, "fila-suporte", Origem.ESCRITO_PELO_AGENTE, date(2026, 6, 1), n=9,
          evidencia="lancamento gravado por esta automacao")

assert mem.contagem(CHAVE) == {"fila-suporte": 10, "fila-financeiro": 9}
assert mem.dominancia(CHAVE) == ("fila-suporte", 10 / 19)   # numero cru, com eco dentro

validas, descartadas = filtrar_contaminacao(mem.entradas(CHAVE))
assert (len(validas), len(descartadas)) == (10, 9)

v = resolver(mem, CHAVE, hoje=HOJE)
assert v.decisao == "fila-financeiro" and v.confianca is Confianca.ALTA
assert v.descartadas == 9
# justificativa: '... 9/10 = 0.900 ... [9 descartada(s) por contaminacao]'
```

Nove é o **menor** número de escritas que inverte a liderança, e a afirmação de mínimo tem as
suas próprias asserções em vez de ficar só na prosa:

```python
def dominancia_crua_com(n_escritas):
    """A amostra do passo 1 com n escritas do agente somadas, medida crua."""
    aux = MemoriaObservada()
    for _ in range(9):
        aux.registrar(Entrada(CHAVE, "fila-financeiro", Origem.OBSERVADO, date(2026, 5, 10)))
    aux.registrar(Entrada(CHAVE, "fila-suporte", Origem.OBSERVADO, date(2026, 5, 12)))
    for _ in range(n_escritas):
        aux.registrar(Entrada(CHAVE, "fila-suporte", Origem.ESCRITO_PELO_AGENTE,
                              date(2026, 6, 1)))
    return aux.dominancia(CHAVE)

assert dominancia_crua_com(8) == ("fila-financeiro", 0.5)     # 9 x 9, desempate alfabetico
assert dominancia_crua_com(9) == ("fila-suporte", 10 / 19)    # 10 x 9, a inversao
```

Este passo é o anti-padrão A2 de [`10-Anti-Patterns.md`](10-Anti-Patterns.md) em números. A
dominância crua **inverteu**: `fila-suporte` passou a liderar com dez contra nove em dezenove
entradas, fração de 0,5263, e um sistema que lesse o armazém direto teria trocado a decisão com
base exclusivamente na própria escrita. O veredicto não mudou, porque o eco foi descartado antes
da contagem, e a quantidade descartada aparece no resultado em vez de desaparecer.

Vale registrar as duas correções que a medição impôs a este parágrafo, porque elas são o assunto
da seção. A primeira versão do exemplo usava seis escritas do agente e afirmava que a dominância
crua se invertia. Ao executar, ela não se invertia: com seis, `fila-financeiro` ainda liderava
por nove contra sete em dezesseis entradas, fração de zero vírgula cinco seis dois cinco, e para
o lado certo. A segunda correção veio da auditoria independente do volume. O número havia sido
trocado por dez com a alegação de que dez era o menor valor que inverte a liderança — e essa
alegação também não tinha sido medida. Varrendo o valor de um até quinze contra os módulos reais,
o menor é **nove**: com nove escritas, `fila-suporte` lidera por dez contra nove, fração
0,5263157894736842. Com oito, a contagem empata em nove contra nove e o desempate alfabético de
`contagem_de` mantém `fila-financeiro` à frente — é exatamente por isso que oito não basta, e é
um detalhe que só aparece medindo.

Duas afirmações falsas conviveram com os três gates verdes no mesmo parágrafo, e nenhuma delas
seria pega por gate nenhum: gate confere que o código roda, não que a prosa mediu o que diz ter
medido. As duas asserções sobre `dominancia_crua_com` existem para fechar essa brecha no ponto
em que ela apareceu — daqui em diante, mexer no número quebra a execução em vez de produzir mais
uma frase plausível.

## Passo 3: a base congelada discorda

```python
registrar(CHAVE, "fila-juridico", Origem.BASE_CONGELADA, date(2026, 1, 20),
          evidencia="base curada, revisao de janeiro")

v = resolver(mem, CHAVE, hoje=HOJE)
assert v.decisao == "fila-financeiro"
assert v.confianca is Confianca.MEDIA            # rebaixada pela contradicao
assert len(v.contradicoes) == 1
# Contradicao(chave='evento:renovacao-mensal-assinatura',
#             decisao_congelada='fila-juridico',
#             decisao_observada='fila-financeiro',
#             n_observacoes=9,
#             congelada_em=datetime.date(2026, 1, 20))
```

A decisão continua sendo a da observação, mas a confiança cai para média e a contradição vem
anexada com os cinco campos que permitem triá-la sem reabrir o armazém. Repare em
`n_observacoes` igual a nove: é a força do lado observado, e é ela que decide se o próximo
passo é recuratoria da fonte ou conferência da observação. Repare também no que **não**
aconteceu: nada foi resolvido em silêncio, e a base congelada não venceu nem perdeu — ela
passou a constar.

## Passo 4: a chave que não decide

```python
AMBIGUA = "evento:transferencia-sem-identidade"
registrar(AMBIGUA, "fila-financeiro", Origem.OBSERVADO, date(2026, 6, 15), n=3)
registrar(AMBIGUA, "fila-suporte", Origem.OBSERVADO, date(2026, 6, 20), n=2)

v = resolver(mem, AMBIGUA, hoje=HOJE)
assert v.decisao is None and v.confianca is None
# justificativa:
# 'pendencia humana: dominancia observada 3/5 = 0.600 abaixo do minimo 0.700;
#  evidencia que nao decide nao passa a decidir por maioria simples'
```

Três contra dois é maioria e não é dominância. O veredicto é indeciso, a confiança é nula — não
existe palpite rotulado como baixa — e a justificativa diz exatamente qual número faltou. Um
operador que leia essa frase sabe duas coisas acionáveis: qual é a alternativa que lidera e
quantas observações a mais mudariam o resultado.

## Passo 5: a decisão humana vence

```python
registrar(AMBIGUA, "fila-suporte", Origem.DECIDIDO_POR_HUMANO, HOJE,
          evidencia="regra dada pelo responsavel da area")

v = resolver(mem, AMBIGUA, hoje=HOJE)
assert v.decisao == "fila-suporte" and v.confianca is Confianca.ALTA
# justificativa: "decisao humana de 2026-07-30 para 'evento:transferencia-sem-identidade':
#  DECIDIDO_POR_HUMANO tem precedencia sobre qualquer dominancia observada, inclusive contraria"
```

A pessoa decidiu contra a alternativa que liderava a contagem, e a precedência respeitou. O
ponto operacional é que a decisão foi registrada **na memória**, e não apenas no sistema de
destino: por isso a mesma chave não volta como pendência na próxima rodada, e o trabalho humano
acumulou em vez de evaporar.

## Passo 6: a mesma memória, duas janelas, dois veredictos

```python
ANUAL = "evento:renovacao-anual-contrato"
registrar(ANUAL, "fila-juridico", Origem.OBSERVADO, date(2025, 2, 1), n=8)
registrar(ANUAL, "fila-financeiro", Origem.OBSERVADO, date(2026, 7, 1), n=2)

curto = resolver(mem, ANUAL, hoje=HOJE, janela_dias=365)
longo = resolver(mem, ANUAL, hoje=HOJE, janela_dias=3650)
assert curto.decisao == "fila-financeiro"       # 2/2 = 1.000, 8 expiradas
assert longo.decisao == "fila-juridico"         # 8/10 = 0.800, nenhuma expirada
```

Os dois veredictos são corretos e nada no armazém mudou entre as duas chamadas: o que mudou foi
a pergunta. Isso é a máquina de estados de [`05-Diagramas.md`](05-Diagramas.md) em ação — o
estado de expirada é calculado por consulta, não gravado. É também o anti-padrão A6: quem
ampliasse a janela depois de ver o resultado curto obteria uma resposta reproduzível,
defensável em revisão, e que mede apenas a própria preferência.

## Passo 7: a chave que nunca existiu

```python
v = resolver(mem, "evento:nunca-visto", hoje=HOJE)
assert v.decisao is None and v.descartadas == 0 and v.contradicoes == ()
# justificativa: "pendencia humana: nenhuma evidencia vigente para
#  'evento:nunca-visto'; 0 entrada(s) no armazem"

assert mem.chaves() == ("evento:renovacao-mensal-assinatura",
                        "evento:transferencia-sem-identidade",
                        "evento:renovacao-anual-contrato")
assert len(contradicoes(mem.entradas(CHAVE))) == 1
```

Nenhuma exceção: chave desconhecida devolve veredicto indeciso, e a justificativa distingue
esse caso de todos os outros dizendo que o armazém tem zero entradas. Essa distinção é o que
separa "nunca vi isso" de "vi e não me convenceu" e de "vi somente o meu próprio eco" — três
situações que, no sistema de origem, chegavam ao chamador como o mesmo valor vazio. A última
linha mostra que a contradição do passo 3 continua aberta depois de tudo: ela não foi resolvida
por nenhum passo posterior, e é isso que se espera de um relatório.
