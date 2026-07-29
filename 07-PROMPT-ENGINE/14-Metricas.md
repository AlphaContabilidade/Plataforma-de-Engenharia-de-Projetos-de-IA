---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 14-Metricas
status: PRONTO
atualizado_em: 2026-07-29
---

# Métricas

Cada métrica abaixo tem definição operacional, unidade e origem do dado. Métrica sem unidade
não compara e métrica sem origem não audita — as duas colunas existem para que ninguém precise
adivinhar o que "melhorou" significa. Quatro delas o motor calcula; duas exigem instrumentação
do executor, e isso está dito onde é o caso.

| Métrica | Definição operacional | Unidade | Origem |
|---|---|---|---|
| Taxa de acerto | `acertos / total` sobre a bateria de casos de ouro de uma versão; `acertos` é `total` menos o número de falhas | fração de 0 a 1 | `Resultado.taxa_acerto` |
| Deriva entre versões | `taxa_b - taxa_a`, medido sobre a mesma amostra materializada de casos | pontos de fração, de −1 a +1 | `Comparacao.deriva` |
| Cobertura de casos de ouro | número de casos de ouro da bateria de um prompt | casos, contagem absoluta | `Resultado.total` |
| Falhas por classe de origem | contagem de `Falha` particionada em duas classes pelo prefixo do campo `motivo`: `render falhou` quando o contrato reprovou antes de chamar o executor, `saida nao casa` quando o executor respondeu e o padrão não casou | falhas por classe, contagem absoluta | `Resultado.falhas` |
| Custo por execução | custo cobrado pelo provedor dividido pelo número de chamadas do executor na rodada | unidade monetária por execução | instrumentação do executor injetado |
| Latência por execução | tempo entre a chamada do executor e o retorno, medido por caso | milissegundos | instrumentação do executor injetado |

## Como ler taxa de acerto sem se enganar

A taxa de acerto é uma fração sobre a bateria, e não uma estimativa da qualidade do prompt no
mundo. Uma bateria de três casos só produz quatro valores possíveis — 0, 0,333, 0,667 e 1,0 — e
portanto a menor variação detectável é de 0,333, ou 33,3 pontos. Isso significa que ganho
inferior a essa granularidade é invisível com três casos, e que uma diferença de um caso parece
enorme. A regra operacional que decorre disso é simples: antes de decidir por deriva pequena,
amplie a amostra. Com dez casos, a granularidade cai para 0,1; com trinta, para 0,033.

Bateria vazia devolve 0,0 e não 1,0, o que é a regra R8 de [`07-Regras.md`](07-Regras.md). O
efeito prático em qualquer painel é que prompt sem caso de ouro aparece no fundo da lista, junto
dos que medem mal, e não no topo com os que medem bem.

## Deriva e o sinal que ela carrega

A deriva é a única métrica de comparação do motor e tem sinal. Positiva significa que a
candidata acertou mais que a referência sobre os mesmos casos; negativa, o contrário; zero
significa empate, e empate não é motivo para promover — promover uma versão empatada troca o
risco conhecido pelo desconhecido sem ganho medido. A propriedade `vencedor` devolve `"a"`,
`"b"` ou `"empate"` para leitura direta.

Duas armadilhas de leitura merecem registro. A primeira é comparar versões sobre amostras
diferentes: `comparar` materializa os casos em tupla exatamente para impedi-lo dentro do motor,
mas nada impede alguém de rodar duas chamadas de `avaliar` com listas distintas e subtrair os
números à mão. A segunda é interpretar deriva positiva com bateria pequena como melhoria
consolidada, conforme o parágrafo anterior sobre granularidade.

## Por que as falhas se partem em duas classes, e não em muitas

A definição da quarta métrica é deliberadamente grosseira, e a razão é que ela precisa ser
mensurável com o que o código produz hoje. O campo `motivo` de `Falha` é texto livre e embute
conteúdo específico do caso — o padrão que não casou aparece dentro da mensagem —, então
agrupar pelo campo inteiro produziria um grupo por expressão regular distinta, o que não é
uma categorização: é a lista de falhas com outro nome. O que o campo permite de fato é uma
partição em duas classes, porque `avaliar` só tem dois pontos de saída por falha, e cada um
escreve um prefixo fixo. A leitura útil dessa partição é diagnóstica e imediata: falha da
classe `render falhou` acusa caso de ouro malformado ou contrato mudado sem que a bateria
acompanhasse, e não diz nada sobre a qualidade do prompt, porque o executor nem foi chamado;
falha da classe `saida nao casa` acusa o prompt, o modelo ou um padrão esperado escrito
estreito demais. Confundir as duas leva a reescrever prompt para consertar bateria. Um
recorte mais fino exigiria um campo enumerado em `Falha`, e essa evolução está em
[`16-Roadmap.md`](16-Roadmap.md) com a razão de não ter entrado agora.

## As duas métricas que o motor não calcula

Custo e latência por execução dependem do provedor e do transporte, e o motor não conhece
nenhum dos dois — a única superfície de contato é o `Callable[[str], str]` recebido pelo
avaliador. A instrumentação correta é envolver o executor em uma função que meça e acumule, e
injetar o envelope em lugar do executor original. Essa é a forma que preserva a fronteira
declarada em [`03-Escopo.md`](03-Escopo.md): otimizar custo é assunto do volume 34 e escolher
modelo por custo é do volume 27, mas medir o custo do que este motor executou é responsabilidade
de quem opera o motor. Sem essa medição, a decisão de promover ignora metade da conta: um prompt
que ganha 0,05 de taxa de acerto e dobra o custo por execução pode ser um retrocesso, e sem o
número essa conclusão não é alcançável.
