---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 12-Exemplos
status: PRONTO
atualizado_em: 2026-07-30
---

# Exemplos

O exemplo desta seção é um caminho ponta a ponta: declarar um prompt de triagem de
solicitações, registrá-lo, avaliá-lo contra quatro casos de ouro, comparar duas versões e promover
a que mediu melhor. O executor usado é um substituto determinístico, o que faz o exemplo
inteiro rodar sem rede — a mesma propriedade que permite ao gate de teste rodar em cada
mudança.

<!-- exemplo: exemplos/07-prompt-engine/prompt_template.py -->
<!-- exemplo: exemplos/07-prompt-engine/prompt_registry.py -->
<!-- exemplo: exemplos/07-prompt-engine/prompt_evaluator.py -->

## Declarar o contrato

```python
from prompt_template import PromptTemplate, Variavel

classificar_v1 = PromptTemplate(
    nome="classificar-solicitacao",
    corpo=(
        "Classifique a solicitacao abaixo em uma categoria do catalogo.\n"
        "Descricao: {descricao}\n"
        "Horas estimadas: {horas}\n"
        "Responda apenas com o codigo da categoria."
    ),
    variaveis=(
        Variavel("descricao", str, descricao="Texto da solicitacao, como o solicitante escreveu"),
        Variavel("horas", float, descricao="Horas estimadas para atender; fracao e permitida"),
    ),
)
```

A declaração já é uma verificação. Se o corpo citasse `{prazo}` sem declarar a variável, ou se
`horas` estivesse declarado e não aparecesse no corpo, a construção levantaria
`ContratoViolado` no carregamento do módulo — antes de qualquer chamada paga. O tipo `float`
em `horas` não é decorativo: passar `"6"` como texto é reprovado por `render`.

## Registrar e verificar a idempotência

```python
from prompt_registry import Estado, PromptRegistry

reg = PromptRegistry()
assert reg.registrar(classificar_v1) == "v1"
assert reg.registrar(classificar_v1) == "v1"          # idempotente por hash
assert reg.estado("classificar-solicitacao", "v1") is Estado.VERSIONADO
assert reg.promovida("classificar-solicitacao") is None
```

Registrar duas vezes o mesmo conteúdo devolve o mesmo rótulo e não cria entrada nova, então
chamar `registrar` na carga do módulo é seguro. A versão nasce em `VERSIONADO` e
`promovida` devolve vazio: nada foi para produção ainda, e `obter` sem versão nesse momento
devolveria a última registrada.

## Avaliar contra casos de ouro

```python
from prompt_evaluator import CasoDeOuro, PromptEvaluator

CASOS = (
    CasoDeOuro("acesso", {"descricao": "SOLICITACAO DE ACESSO AO SISTEMA", "horas": 0.5},
               esperado=r"\bINF-104\b"),
    CasoDeOuro("equipamento", {"descricao": "TROCA DE EQUIPAMENTO DEFEITUOSO", "horas": 3.0},
               esperado=r"\bSUP-210\b"),
    CasoDeOuro("relatorio", {"descricao": "RELATORIO MENSAL DE ATENDIMENTOS", "horas": 6.0},
               esperado=r"\bDAD-330\b"),
    CasoDeOuro("ambiguo", {"descricao": "AJUSTE NO PAINEL", "horas": 2.0},
               esperado=r"\bREVISAR\b",
               descricao="Descricao sem sistema nem area identificavel; nao deve ser chutada"),
)

def executor_fake(prompt: str) -> str:
    """Substituto deterministico: decide pelo trecho da descricao presente no prompt."""
    if "ACESSO AO SISTEMA" in prompt:
        return "INF-104"
    if "TROCA DE EQUIPAMENTO" in prompt:
        return "SUP-210"
    if "RELATORIO MENSAL" in prompt:
        return "DAD-330"
    if "REVISAR" in prompt:      # so o corpo da v2 carrega essa instrucao
        return "REVISAR"
    return "INF-104"

aval = PromptEvaluator(executor_fake)
resultado = aval.avaliar(classificar_v1, CASOS)
assert resultado.total == 4 and resultado.acertos == 3
assert resultado.taxa_acerto == 0.75
assert [f.caso for f in resultado.falhas] == ["ambiguo"]
```

O padrão esperado de cada caso ancora no código da categoria e ignora o resto da redação, o
que é a prática P3 de [`09-Boas-Praticas.md`](09-Boas-Praticas.md) aplicada. O executor
substituto não simula o modelo: ele fixa um comportamento conhecido para que o teste meça o
motor, e não o provedor. Trocá-lo por um cliente real não exige mudar uma linha do avaliador.
O quarto caso reprova de propósito: a v1 não tem instrução para recusar descrição ambígua, e
`Falha` guarda a saída observada para que o diagnóstico não dependa de reexecutar.

## Comparar duas versões e promover

```python
# A v1 e a incumbente: foi avaliada e promovida quando a bateria tinha apenas os
# tres primeiros casos. O caso "ambiguo" entrou depois, vindo de um incidente
# real -- e e por isso que a versao em producao hoje mede 0,75 e nao 1,0.
reg.transicionar("classificar-solicitacao", "v1", Estado.EM_AVALIACAO)
reg.transicionar("classificar-solicitacao", "v1", Estado.PROMOVIDO)
assert reg.promovida("classificar-solicitacao") == "v1"

classificar_v2 = PromptTemplate(
    nome="classificar-solicitacao",
    corpo=classificar_v1.corpo + "\nSe a descricao for ambigua, responda REVISAR.",
    variaveis=classificar_v1.variaveis,
)
assert reg.registrar(classificar_v2) == "v2"          # corpo mudou, hash mudou

comp = aval.comparar(classificar_v1, classificar_v2, CASOS)
assert comp.taxa_a == 0.75 and comp.taxa_b == 1.0
assert comp.deriva == 0.25 and comp.vencedor == "b"

if comp.deriva > 0.0:                                 # empate nao promove
    reg.transicionar("classificar-solicitacao", "v2", Estado.EM_AVALIACAO)
    reg.transicionar("classificar-solicitacao", "v2", Estado.PROMOVIDO)

assert reg.promovida("classificar-solicitacao") == "v2"
assert reg.obter("classificar-solicitacao") is classificar_v2
```

A condição de promoção é deriva estritamente positiva, e não maior ou igual a zero: empate troca
o risco conhecido pelo desconhecido sem ganho medido, o que é o anti-padrão A4 de
[`10-Anti-Patterns.md`](10-Anti-Patterns.md). Vale registrar a limitação deste exemplo em vez de
disfarçá-la: quatro casos dão granularidade de 0,25, então a deriva observada é exatamente a
menor variação detectável da amostra. O exemplo demonstra o mecanismo; a decisão real pediria
ampliar a bateria antes de promover, pela regra de granularidade de
[`14-Metricas.md`](14-Metricas.md). A promoção também passa obrigatoriamente por `EM_AVALIACAO`:
tentar ir de `VERSIONADO` direto para `PROMOVIDO` levanta `TransicaoInvalida` com a lista de
destinos válidos. Depois da promoção, `obter` sem versão devolve a v2 em qualquer ponto do
sistema, o que faz da transição o único ato que muda o comportamento em produção.

## A trilha que sobra

```python
for versao, hash_, estado in reg.historico("classificar-solicitacao"):
    print(versao, hash_, estado)
# v1 <12 hexdigitos> DEPRECIADO
# v2 <12 hexdigitos> PROMOVIDO
```

A v1 aparece como `DEPRECIADO` sem que ninguém a tenha depreciado explicitamente: o
rebaixamento aconteceu dentro da promoção da v2, o que preserva o invariante de uma promovida
por nome. Vale notar o limite desse mecanismo, porque ele é fonte de engano: o rebaixamento
automático só alcança a versão que estava em `PROMOVIDO`. Uma versão que nunca foi promovida
permanece em `VERSIONADO` para sempre, e abandoná-la exige uma transição explícita para
`DEPRECIADO` — é o ramo direto que aparece no diagrama de
[`05-Diagramas.md`](05-Diagramas.md). Essa saída de duas linhas é a resposta para a pergunta
que abriu o volume: qual prompt estava em produção e quando deixou de estar. Os dois hashes
ficam escritos como marcador de forma, e não com o valor literal, porque o hash é derivado do
corpo e da assinatura: fixá-lo na prosa criaria um número que envelhece na primeira edição do
corpo sem que nenhum gate perceba.
