---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 12-Exemplos
status: PRONTO
atualizado_em: 2026-07-29
---

# Exemplos

O exemplo desta seção é um caminho ponta a ponta: declarar um prompt de classificação
contábil, registrá-lo, avaliá-lo contra quatro casos de ouro, comparar duas versões e promover
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
    nome="classificar-lancamento",
    corpo=(
        "Classifique o lancamento bancario abaixo em uma categoria contabil.\n"
        "Historico: {historico}\n"
        "Valor: {valor}\n"
        "Responda apenas com o codigo da categoria."
    ),
    variaveis=(
        Variavel("historico", str, descricao="Texto do extrato, como veio do banco"),
        Variavel("valor", float, descricao="Valor com sinal; negativo e saida"),
    ),
)
```

A declaração já é uma verificação. Se o corpo citasse `{data}` sem declarar a variável, ou se
`valor` estivesse declarado e não aparecesse no corpo, a construção levantaria
`ContratoViolado` no carregamento do módulo — antes de qualquer chamada paga. O tipo `float`
em `valor` não é decorativo: passar `"1200"` como texto é reprovado por `render`.

## Registrar e verificar a idempotência

```python
from prompt_registry import Estado, PromptRegistry

reg = PromptRegistry()
assert reg.registrar(classificar_v1) == "v1"
assert reg.registrar(classificar_v1) == "v1"          # idempotente por hash
assert reg.estado("classificar-lancamento", "v1") is Estado.VERSIONADO
assert reg.promovida("classificar-lancamento") is None
```

Registrar duas vezes o mesmo conteúdo devolve o mesmo rótulo e não cria entrada nova, então
chamar `registrar` na carga do módulo é seguro. A versão nasce em `VERSIONADO` e
`promovida` devolve vazio: nada foi para produção ainda, e `obter` sem versão nesse momento
devolveria a última registrada.

## Avaliar contra casos de ouro

```python
from prompt_evaluator import CasoDeOuro, PromptEvaluator

CASOS = (
    CasoDeOuro("tarifa-bancaria", {"historico": "TARIFA PACOTE SERVICOS", "valor": -89.0},
               esperado=r"\b4\.01\.02\b"),
    CasoDeOuro("energia", {"historico": "CPFL PAULISTA CONTA", "valor": -1320.55},
               esperado=r"\b2\.04\.07\b"),
    CasoDeOuro("recebimento", {"historico": "LIQUIDACAO BOLETO 000123", "valor": 2500.0},
               esperado=r"\b1\.01\.01\b"),
    CasoDeOuro("ambiguo", {"historico": "TED CREDITO 000999", "valor": 500.0},
               esperado=r"\bREVISAR\b",
               descricao="Historico sem identidade do pagador; nao deve ser chutado"),
)

def executor_fake(prompt: str) -> str:
    """Substituto deterministico: decide pelo trecho do historico presente no prompt."""
    if "TARIFA" in prompt:
        return "4.01.02"
    if "CPFL" in prompt:
        return "2.04.07"
    if "LIQUIDACAO BOLETO" in prompt:
        return "1.01.01"
    if "REVISAR" in prompt:      # so o corpo da v2 carrega essa instrucao
        return "REVISAR"
    return "1.01.01"

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
O quarto caso reprova de propósito: a v1 não tem instrução para recusar histórico ambíguo, e
`Falha` guarda a saída observada para que o diagnóstico não dependa de reexecutar.

## Comparar duas versões e promover

```python
# A v1 e a incumbente: foi avaliada e promovida quando a bateria tinha apenas os
# tres primeiros casos. O caso "ambiguo" entrou depois, vindo de um incidente
# real -- e e por isso que a versao em producao hoje mede 0,75 e nao 1,0.
reg.transicionar("classificar-lancamento", "v1", Estado.EM_AVALIACAO)
reg.transicionar("classificar-lancamento", "v1", Estado.PROMOVIDO)
assert reg.promovida("classificar-lancamento") == "v1"

classificar_v2 = PromptTemplate(
    nome="classificar-lancamento",
    corpo=classificar_v1.corpo + "\nSe o historico for ambiguo, responda REVISAR.",
    variaveis=classificar_v1.variaveis,
)
assert reg.registrar(classificar_v2) == "v2"          # corpo mudou, hash mudou

comp = aval.comparar(classificar_v1, classificar_v2, CASOS)
assert comp.taxa_a == 0.75 and comp.taxa_b == 1.0
assert comp.deriva == 0.25 and comp.vencedor == "b"

if comp.deriva > 0.0:                                 # empate nao promove
    reg.transicionar("classificar-lancamento", "v2", Estado.EM_AVALIACAO)
    reg.transicionar("classificar-lancamento", "v2", Estado.PROMOVIDO)

assert reg.promovida("classificar-lancamento") == "v2"
assert reg.obter("classificar-lancamento") is classificar_v2
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
for versao, hash_, estado in reg.historico("classificar-lancamento"):
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
que abriu o volume: qual prompt estava em produção e quando deixou de estar.
