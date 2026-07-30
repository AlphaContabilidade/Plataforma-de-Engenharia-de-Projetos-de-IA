# RISE — Role, Input, Steps, Expectation

> Técnica pública de estruturação de prompt · atualizado em 2026-07-29
> **Estado de atribuição:** `DOMINIO-PUBLICO-SEM-ATRIBUICAO-SEGURA`
> Técnica de domínio público, origem não atribuída com segurança.

## O que a sigla expande

| Letra | Campo | O que o campo responde |
|---|---|---|
| **R** | *Role* (papel) | De que ponto de vista responder |
| **I** | *Input* (insumo) | Que material entra, e o que ele contém |
| **S** | *Steps* (etapas) | Em que ordem executar |
| **E** | *Expectation* (expectativa) | Que saída, com que critério de aceitação |

**Variantes conhecidas:** o `I` aparece também como *Instructions* e o `E` como *End
goal*. Este acervo adota *Input* e *Expectation*, porque é a leitura em que os quatro
campos não se sobrepõem: com *Instructions* no `I`, o campo passa a competir com `Steps`
e a estrutura perde a distinção entre **o que entra** e **o que se faz**. Se a sua fonte
usa outra expansão, o essencial é preservar essa separação.

## Por que funciona

O campo que justifica a existência do RISE é `Steps`. Uma tarefa com etapas dependentes
tem um problema que RTF e CARE não endereçam: **a ordem é parte do resultado.** Se a etapa
3 depende do produto da etapa 2, executar 3 antes produz uma resposta errada que parece
certa — porque o modelo, sem o insumo da etapa 2, preenche com estimativa e segue em
frente com a mesma fluência.

Tornar as etapas explícitas tem dois efeitos mensuráveis. O primeiro é o raciocínio
intermediário, cujo ganho em tarefas de múltiplos passos está documentado em
*Chain-of-Thought Prompting Elicits Reasoning in Large Language Models* (Jason Wei et al.,
2022) e, na forma mínima "vamos pensar passo a passo", em *Large Language Models are
Zero-Shot Reasoners* (Takeshi Kojima et al., 2022) — ambos em
[`referencias/papers.md`](../../referencias/papers.md). O segundo é operacional e menos
citado: **etapas nomeadas dão ao revisor humano um lugar para apontar o defeito.** "A
etapa 3 usou o valor do título em vez do valor pago" é um diagnóstico; "a resposta está
errada" não é.

O campo `Input`, por sua vez, faz um trabalho silencioso: descrever o que o material
contém permite ao modelo detectar quando ele *não* contém. Um `Input` declarado como
"extrato OFX com data, valor e histórico; o histórico pode vir truncado pelo banco" cria a
possibilidade de o modelo dizer "o histórico desta linha está truncado" em vez de adivinhar
o que vinha depois do corte.

## Quando serve

- **Procedimentos com ordem de precedência**, em que aplicar a regra 2 antes da 1 muda o
  resultado. Toda classificação que depende de precedência entre fontes é assim.
- Tarefas em que você quer poder **auditar a etapa que falhou**, e não só o resultado.
- Quando o insumo é **heterogêneo ou incompleto** e o modelo precisa saber o que esperar
  dele.
- Como esqueleto de skill ou de agente: `Steps` mapeia quase um a um para o fluxo de um
  agente, e é por isso que o [`_template-agente.md`](../../agentes/_template-agente.md)
  tem a rubrica *Fluxos*.

## Quando NÃO serve

- **Quando você não sabe as etapas.** Este é o erro mais frequente. Inventar uma sequência
  plausível para preencher o campo é pior que não ter campo: o modelo seguirá a sequência
  errada com disciplina, e o erro fica sistemático em vez de aleatório — portanto mais
  difícil de notar. Se você não conhece o procedimento, RISE não é a estrutura; a estrutura
  é pesquisar o procedimento.
- **Tarefas exploratórias.** Se o objetivo é gerar alternativas, brainstorming ou
  hipóteses, `Steps` estreita o espaço de busca exatamente onde você queria amplitude.
- **Pedido de uma linha.** Quatro campos para "traduza esta frase" é cerimônia.
- **Quando o valor está no exemplo, não na ordem.** Convenção sutil se transmite por
  demonstração; use CARE.
- **Quando as etapas são tantas que o prompt vira manual.** Acima de sete ou oito etapas,
  o material do meio perde atenção (*Lost in the Middle*, Nelson F. Liu et al., 2023) e a
  aderência cai. Nesse ponto o problema não é de prompt: é de decomposição. Quebre em
  chamadas encadeadas, cada uma com seu RISE curto e sua saída verificável.

## Exemplo concreto

Tarefa real: decidir se um boleto liquidado no banco pode ser baixado automaticamente
contra um título em aberto, ou se precisa de decisão humana. É uma tarefa em que a ordem
das checagens é o núcleo da correção — inverter duas delas produz dinheiro lançado em
duplicidade.

```text
# Role
Você é um analista de triagem. Você decide apenas o que a evidência
fornecida decide. Quando a evidência não decide, a resposta correta é encaminhar para
decisão humana — nunca escolher a alternativa mais provável.

# Input
Você recebe:
1. UMA liquidação de boleto: data, valor liquidado, nome do pagador (como o banco
   registrou, podendo estar truncado ou abreviado), conta bancária.
2. A LISTA de títulos em aberto daquela conta: identificador, sacado, valor, vencimento.
3. A TRILHA de baixas já realizadas por esta automação: identificador do título, data,
   valor.
Nem toda liquidação tem título correspondente na lista. O nome do pagador NÃO é
identificador confiável: dois clientes podem ter nomes parecidos.

# Steps
1. Consulte a TRILHA. Se esta liquidação (mesma conta, mesma data, mesmo valor) já
   consta, PARE e devolva decisao="ja-processado". Não prossiga.
2. Filtre os títulos em aberto do mesmo sacado. Compare por identificador quando houver;
   por nome apenas como reforço, nunca como prova isolada.
3. Se sobrar exatamente 1 candidato e o valor liquidado for igual ao valor do título,
   devolva decisao="baixar", com o identificador.
4. Se sobrar exatamente 1 candidato e o valor liquidado for MENOR, devolva
   decisao="baixar-parcial" — pagamento parcial é normal neste domínio.
5. Se sobrarem 2 ou mais candidatos, devolva decisao="humano", motivo="ambiguo", e liste
   os candidatos. Não escolhe por vencimento, não escolhe por proximidade de nome.
6. Se não sobrar nenhum candidato, devolva decisao="humano",
   motivo="sem-titulo-correspondente". NÃO conclua que o título não existe: a hipótese
   mais provável é que ele já foi baixado, e lançar avulso aqui duplicaria o valor.

# Expectation
Um objeto JSON com as chaves: decisao (um de: "ja-processado", "baixar",
"baixar-parcial", "humano"), titulo_id (string, vazia quando não se aplica), motivo
(string, vazia quando decisao é "baixar"), candidatos (lista, vazia quando não se
aplica), etapa_que_decidiu (inteiro de 1 a 6).
Critério de aceitação: um revisor humano tem de conseguir refazer a decisão lendo apenas
o campo etapa_que_decidiu e o insumo. Se ele não conseguir, a saída está incompleta.
```

Três coisas nesse prompt só existem porque a estrutura tem um campo para elas.

A primeira é a **etapa 1 antes de tudo**: a checagem de idempotência precede a decisão de
negócio. Numa estrutura sem `Steps`, essa checagem entra como "e não esqueça de verificar
se já foi processado" no fim do parágrafo — posição em que a aderência é notoriamente
pior. A segunda é a **etapa 6**, que não é uma etapa de ação e sim uma proibição de
inferência: ela nomeia a conclusão errada mais tentadora e a bloqueia. A terceira é
`etapa_que_decidiu` na `Expectation`, que transforma o rastro de raciocínio em campo
estruturado — o revisor não lê a justificativa em prosa, lê um inteiro.

## Limitações

**1. Etapas inventadas produzem erro sistemático.** Vale repetir porque é o modo de falha
característico: RISE dá disciplina à sequência que você escreveu, esteja ela certa ou
errada. A estrutura amplifica a qualidade do procedimento; ela não a cria.

**2. `Steps` é instrução, não execução.** O modelo não é obrigado a executar as etapas na
ordem, e em geral não há como verificar internamente que executou. Se a ordem é
crítica — como no exemplo acima, onde inverter 1 e 3 custa dinheiro — a ordem precisa ser
imposta **fora** do prompt: uma chamada por etapa, com o resultado de cada uma validado por
código antes de alimentar a seguinte. Prompt não é mecanismo de controle de fluxo.

**3. Etapas longas comprometem as do meio.** Sequências extensas sofrem degradação de
atenção. Prefira decompor a alongar.

**4. `Expectation` costuma ser escrita como desejo.** "Espero uma análise completa e
precisa" não é critério de aceitação. Critério é uma condição que outra pessoa pode
verificar sem consultar o autor do prompt.

**5. O campo `Role` tem as mesmas limitações do RTF** — declarar senioridade não confere
conhecimento. Ver [`RTF.md`](RTF.md), limitação 1.

**6. Não há atribuição, e há variantes de expansão.** Registradas acima; nenhuma autoria
é afirmada.

## Relacionados

- [`RTF.md`](RTF.md) — quando não há etapas.
- [`CARE.md`](CARE.md) — quando o valor está no exemplo.
- [`TAG.md`](TAG.md) — quando o que falta é só o objetivo.
- [`agentes/_template-agente.md`](../../agentes/_template-agente.md) — `Steps` amadurece
  para a rubrica *Fluxos* quando a tarefa vira agente.
- [`referencias/papers.md`](../../referencias/papers.md) — cadeia de pensamento e
  degradação de contexto longo.
