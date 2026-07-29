# TAG — Task, Action, Goal

> Técnica pública de estruturação de prompt · atualizado em 2026-07-29
> **Estado de atribuição:** `DOMINIO-PUBLICO-SEM-ATRIBUICAO-SEGURA`
> Técnica de domínio público, origem não atribuída com segurança.

## O que a sigla expande

| Letra | Campo | O que o campo responde |
|---|---|---|
| **T** | *Task* (tarefa) | Qual é o trabalho, em uma frase |
| **A** | *Action* (ação) | O que concretamente fazer para realizá-lo |
| **G** | *Goal* (objetivo) | Para que serve o resultado, e o que caracteriza sucesso |

A distinção entre `Task` e `Action` é a parte que costuma confundir e é o que dá utilidade
à sigla: `Task` é o **escopo** ("revisar a cláusula de reajuste destes contratos"),
`Action` é a **operação** ("compare o índice previsto na cláusula com o índice aplicado na
última fatura e liste as divergências"). Escopo sem operação produz resposta vaga;
operação sem escopo produz resposta fora de propósito.

## Por que funciona

TAG existe por causa do terceiro campo. `Goal` responde a uma pergunta que quase nenhum
prompt informal responde: **para que este resultado vai ser usado?** A mesma tarefa muda
completamente de forma segundo o destino da saída.

"Liste as divergências de reajuste" produz coisas diferentes se o objetivo é (a) decidir se
vale abrir conversa com o cliente, (b) instruir uma cobrança retroativa, ou (c) alimentar
uma planilha de acompanhamento. Em (a) o que importa é a materialidade — dois casos de R$
30 não valem a conversa. Em (b) o que importa é a fundamentação, porque alguém vai
contestar. Em (c) o que importa é a estrutura de colunas, e prosa é ruído.

O `Goal` é também o campo que permite ao modelo **omitir**. Sem objetivo declarado, o
comportamento seguro é incluir tudo, e a saída vem inflada com material que o consumidor
descarta. Com objetivo declarado, "não relevante para este objetivo" torna-se uma decisão
legítima.

## Quando serve

- Pedido em que a **tarefa é clara mas o critério de sucesso não é** — o caso mais comum
  de resposta tecnicamente correta e praticamente inútil.
- Quando a mesma tarefa serve a **destinos diferentes** e você precisa dizer qual é o desta
  vez.
- Como **complemento** de outra estrutura: `Goal` pode ser acrescentado a um RTF sem
  reescrevê-lo, e frequentemente é a melhoria de maior retorno por palavra escrita.
- Prompts curtos que precisam ficar curtos: TAG tem três campos e nenhum deles pede
  material de apoio.

## Quando NÃO serve

- **Quando falta contexto de negócio.** TAG não tem campo para dados nem para regra
  interna. Use CARE.
- **Quando a ordem das operações é crítica.** `Action` é um campo, não uma sequência
  numerada. Use RISE.
- **Quando o formato da saída precisa ser estável para consumo por programa.** TAG não
  tem campo de formato; `Goal` descreve finalidade, não esquema. Use RTF, ou combine os
  dois.
- **Quando o objetivo real é político ou não declarável.** Se o `Goal` verdadeiro é
  "justificar uma decisão já tomada", escrevê-lo faz o modelo produzir justificação
  enviesada com competência. O problema aqui não é da técnica.
- **Quando o objetivo é vago por natureza** — "quero entender melhor o assunto". Aí o
  campo `Goal` vira eco da `Task` e a estrutura não paga o custo.

## Exemplo concreto

Um pedido sem `Goal`, e o mesmo pedido com ele.

Sem:

```text
Analise estes 40 contratos de prestação de serviço contábil e me diga quais estão
desatualizados.
```

O que "desatualizado" significa é decidido pelo modelo. A resposta vem provavelmente como
uma lista longa misturando data de assinatura antiga, cláusula de índice extinto, valor
abaixo da tabela atual e ausência de cláusula de LGPD — cada uma delas um critério
diferente, nenhum deles o que se queria.

Com TAG:

```text
# Task
Revisar 40 contratos de prestação de serviço contábil quanto à cláusula de reajuste
anual (cláusula 4.4 no modelo padrão; pode ter outra numeração nos contratos antigos).

# Action
Para cada contrato: localize a cláusula de reajuste; extraia o índice previsto e o mês
de aniversário; compare com o índice e o mês efetivamente aplicados na última fatura
emitida (fornecidos na planilha anexa). Registre divergência quando o índice previsto e
o aplicado forem diferentes, OU quando o reajuste previsto não tiver sido aplicado em
nenhuma fatura desde o aniversário. Quando o contrato não tiver cláusula de reajuste,
registre como "sem cláusula" — não é divergência, é lacuna contratual.

# Goal
A saída vai ser usada para decidir, cliente por cliente, se vale abrir a conversa de
cobrança retroativa. Duas consequências: (1) ordene por valor não faturado acumulado,
decrescente, porque a decisão é sobre onde gastar a conversa; (2) para cada divergência,
cite o trecho literal da cláusula, porque o cliente vai contestar e quem for conversar
precisa ter o texto em mãos. Itens abaixo de R$ 500 acumulados podem ser agrupados em
uma linha "materialidade baixa" com a contagem — não detalhe cada um.
```

O `Goal` fez três coisas que a `Action` não faria: definiu a **ordenação** (por valor, não
por nome nem por data), exigiu **citação literal** (porque haverá contestação), e autorizou
**agregar o irrelevante** (materialidade). Nenhuma dessas três decisões é dedutível da
tarefa; todas as três são dedutíveis do uso.

Note ainda que a `Action` cria uma terceira categoria — "sem cláusula" — em vez de forçar
tudo em divergente/não divergente. Categoria de escape explícita é o que impede o modelo
de encaixar à força o caso que não encaixa.

## Limitações

**1. Só três campos, e nenhum deles guarda dado.** TAG é a estrutura mais leve depois do
RTF. Se a resposta depende de regra interna, norma ou histórico, esse material não tem
lugar aqui e vai acabar empurrado para dentro de `Action`, que então deixa de ser uma
operação e vira um parágrafo.

**2. `Goal` pode induzir viés de conveniência.** Declarar "o objetivo é embasar a cobrança"
inclina o modelo a encontrar divergências. O contrapeso é escrever o objetivo em termos da
**decisão** ("decidir se vale abrir a conversa" — que admite a resposta "não vale") e não
em termos do **resultado desejado** ("embasar a cobrança" — que já pressupõe que há o que
cobrar). A diferença entre essas duas formulações é a diferença entre análise e advocacia.

**3. Não substitui verificação.** `Goal` melhora a utilidade da saída, não a sua exatidão.
O contrato citado literalmente pode ter sido citado errado.

**4. Confusão entre `Task` e `Action`.** Quando os dois campos dizem a mesma coisa com
palavras diferentes, a estrutura degenerou para um RTF sem formato. O teste rápido: se
apagar `Task` e a `Action` continuar compreensível, o `Task` estava redundante.

**5. Não há atribuição.** Não se sabe com segurança quem cunhou a sigla; nenhum autor,
ano ou artigo é afirmado aqui.

## Relacionados

- [`RTF.md`](RTF.md) — quando o que falta é formato.
- [`CARE.md`](CARE.md) — quando o que falta é contexto e exemplo.
- [`RISE.md`](RISE.md) — quando o que falta é ordem.
