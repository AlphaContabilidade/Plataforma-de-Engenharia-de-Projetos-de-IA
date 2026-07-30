# TAG — Task, Action, Goal

> Técnica pública de estruturação de prompt · atualizado em 2026-07-30
> **Estado de atribuição:** `DOMINIO-PUBLICO-SEM-ATRIBUICAO-SEGURA`
> Técnica de domínio público, origem não atribuída com segurança.

## O que a sigla expande

| Letra | Campo | O que o campo responde |
|---|---|---|
| **T** | *Task* (tarefa) | Qual é o trabalho, em uma frase |
| **A** | *Action* (ação) | O que concretamente fazer para realizá-lo |
| **G** | *Goal* (objetivo) | Para que serve o resultado, e o que caracteriza sucesso |

A distinção entre `Task` e `Action` é a parte que costuma confundir e é o que dá utilidade
à sigla: `Task` é o **escopo** ("revisar a categoria atribuída a estas solicitações"),
`Action` é a **operação** ("compare a categoria atribuída com a que o catálogo prevê para o
sistema citado na descrição e liste as divergências"). Escopo sem operação produz resposta
vaga; operação sem escopo produz resposta fora de propósito.

## Por que funciona

TAG existe por causa do terceiro campo. `Goal` responde a uma pergunta que quase nenhum
prompt informal responde: **para que este resultado vai ser usado?** A mesma tarefa muda
completamente de forma segundo o destino da saída.

"Liste as divergências de categoria" produz coisas diferentes se o objetivo é (a) decidir
se vale abrir conversa com a área solicitante, (b) instruir uma recategorização retroativa
da fila, ou (c) alimentar um painel de acompanhamento. Em (a) o que importa é a
materialidade — dois casos de meia hora não valem a conversa. Em (b) o que importa é a
fundamentação, porque alguém vai contestar. Em (c) o que importa é a estrutura de colunas,
e prosa é ruído.

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
Analise estas 40 solicitações da fila de infraestrutura e me diga quais estão mal
categorizadas.
```

O que "mal categorizada" significa é decidido pelo modelo. A resposta vem provavelmente
como uma lista longa misturando código fora do catálogo, código válido mas de outra fila,
categoria genérica onde havia uma específica e solicitação sem categoria nenhuma — cada
uma delas um critério diferente, nenhum deles o que se queria.

Com TAG:

```text
# Task
Revisar 40 solicitações da fila de infraestrutura quanto à categoria atribuída na
triagem (código do catálogo na coluna "categoria"; solicitações antigas podem trazer
código de uma versão anterior do catálogo).

# Action
Para cada solicitação: localize o sistema citado na descrição; extraia a categoria que o
catálogo vigente prevê para aquele sistema; compare com a categoria efetivamente
atribuída e com a fila em que a solicitação foi atendida (fornecidas na planilha anexa).
Registre divergência quando a categoria prevista e a atribuída forem diferentes, OU
quando a categoria atribuída pertencer a outra fila. Quando a descrição não citar sistema
algum, registre como "sem sistema" — não é divergência, é lacuna da solicitação.

# Goal
A saída vai ser usada para decidir, área por área, se vale abrir a conversa de
recategorização retroativa. Duas consequências: (1) ordene por horas acumuladas na
categoria errada, decrescente, porque a decisão é sobre onde gastar a conversa; (2) para
cada divergência, cite o trecho literal da descrição, porque a área vai contestar e quem
for conversar precisa ter o texto em mãos. Itens abaixo de 2 horas acumuladas podem ser
agrupados em uma linha "materialidade baixa" com a contagem — não detalhe cada um.
```

O `Goal` fez três coisas que a `Action` não faria: definiu a **ordenação** (por horas, não
por nome nem por data), exigiu **citação literal** (porque haverá contestação), e autorizou
**agregar o irrelevante** (materialidade). Nenhuma dessas três decisões é dedutível da
tarefa; todas as três são dedutíveis do uso.

Note ainda que a `Action` cria uma terceira categoria — "sem sistema" — em vez de forçar
tudo em divergente/não divergente. Categoria de escape explícita é o que impede o modelo
de encaixar à força o caso que não encaixa.

## Limitações

**1. Só três campos, e nenhum deles guarda dado.** TAG é a estrutura mais leve depois do
RTF. Se a resposta depende de regra interna, catálogo ou histórico, esse material não tem
lugar aqui e vai acabar empurrado para dentro de `Action`, que então deixa de ser uma
operação e vira um parágrafo.

**2. `Goal` pode induzir viés de conveniência.** Declarar "o objetivo é embasar a
recategorização" inclina o modelo a encontrar divergências. O contrapeso é escrever o
objetivo em termos da **decisão** ("decidir se vale abrir a conversa" — que admite a
resposta "não vale") e não em termos do **resultado desejado** ("embasar a
recategorização" — que já pressupõe que há o que recategorizar). A diferença entre essas
duas formulações é a diferença entre análise e advocacia.

**3. Não substitui verificação.** `Goal` melhora a utilidade da saída, não a sua exatidão.
O trecho citado literalmente pode ter sido citado errado.

**4. Confusão entre `Task` e `Action`.** Quando os dois campos dizem a mesma coisa com
palavras diferentes, a estrutura degenerou para um RTF sem formato. O teste rápido: se
apagar `Task` e a `Action` continuar compreensível, o `Task` estava redundante.

**5. Não há atribuição.** Não se sabe com segurança quem cunhou a sigla; nenhum autor,
ano ou artigo é afirmado aqui.

## Relacionados

- [`RTF.md`](RTF.md) — quando o que falta é formato.
- [`CARE.md`](CARE.md) — quando o que falta é contexto e exemplo.
- [`RISE.md`](RISE.md) — quando o que falta é ordem.
