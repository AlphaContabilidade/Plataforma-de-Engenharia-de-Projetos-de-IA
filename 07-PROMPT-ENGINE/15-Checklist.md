---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 15-Checklist
status: PRONTO
atualizado_em: 2026-07-29
---

# Checklist

Este checklist responde a uma pergunta única: meu prompt está pronto para promoção? Cada item se
marca com evidência à mão — uma chamada que devolve o valor esperado, uma leitura de `historico`,
um número anotado — e nenhum depende de julgamento subjetivo. Dois itens dependem de coisa que o
motor não produz sozinho, e cada um deles diz de onde vem a evidência em vez de supor que ela
existe: a passagem por `EM_AVALIACAO` se confere no script de promoção, porque o registro guarda
o estado atual e não a trilha de estados, e o custo por execução se confere na instrumentação do
executor. Se algum item não puder ser marcado, o prompt não está pronto — e o item que falhou
aponta o que fazer.

## Contrato

- [ ] O prompt existe como `PromptTemplate`, com nome estável, e não como literal de string no meio do código.
- [ ] Toda variável está declarada com o tipo que o modelo vai receber, e não com o tipo mais largo que aceitaria qualquer coisa.
- [ ] A construção do template roda no carregamento do módulo, de forma que uma divergência entre corpo e contrato falhe antes de qualquer chamada paga.
- [ ] O campo `descricao` de cada variável diz o que ela contém, e não repete o nome dela.
- [ ] Cada variável marcada como opcional é opcional porque a ausência dela tem significado no corpo, e não porque preenchê-la dá trabalho; alternar `obrigatoria` muda o contrato e gera versão nova, conforme a regra R2 de [`07-Regras.md`](07-Regras.md).

## Registro

- [ ] `registrar` foi chamado e devolveu um rótulo de versão; chamá-lo de novo devolve o mesmo rótulo.
- [ ] `historico` do nome mostra apenas versões que existiram de fato, sem entradas duplicadas geradas por reimportação.
- [ ] Nenhuma versão foi renomeada para reorganizar; o nome é o mesmo desde a primeira versão.

## Evidência

- [ ] A bateria tem pelo menos três casos de ouro, e cada padrão esperado ancora no fato exigido em vez de na redação inteira.
- [ ] A bateria roda com executor determinístico no gate de teste e com o provedor real antes da promoção.
- [ ] A taxa de acerto da candidata foi medida e registrada com o número, não com um adjetivo.
- [ ] A deriva contra a versão promovida foi medida sobre a mesma amostra e é positiva; empate não promove.
- [ ] O custo por execução da candidata foi medido e comparado com o envelope de instrumentação descrito em [`14-Metricas.md`](14-Metricas.md), para que ganho de acerto pago com dobro de custo apareça na decisão; o motor não produz esse número por conta própria, e quem promove sem o envelope está decidindo sem metade da conta.

## Promoção

- [ ] A sequência de chamadas de `transicionar` do script de promoção passa por `EM_AVALIACAO` antes de `PROMOVIDO` — a evidência é o script, e não o histórico, porque o registro guarda o estado atual e não a trilha de estados por que a versão passou.
- [ ] Depois de promover, `promovida` devolve a versão nova e `historico` mostra a anterior em `DEPRECIADO`.
- [ ] Cada incidente que motivou a mudança virou um caso de ouro permanente na bateria.
