# Backlog de frameworks sem definição

> Biblioteca transversal · atualizado em 2026-07-29
> Estado de atribuição de todos os itens abaixo: **indefinido**. Nenhum foi escrito.

## Por que estes arquivos não existem

A especificação original desta plataforma listava, entre os frameworks a documentar,
treze nomes que não vinham acompanhados de definição alguma: nenhuma expansão de sigla,
nenhum escopo, nenhuma entrada, nenhuma saída, nenhuma fonte. Eram nomes.

Havia duas maneiras de "cumprir" essa parte da especificação:

1. **Preencher.** Inventar para cada sigla uma expansão plausível, um propósito
   plausível, um conjunto de fases plausível — e entregar treze arquivos que passariam
   em qualquer contagem de páginas.
2. **Registrar a lacuna.** Entregar um arquivo que diz exatamente o que se sabe: que os
   nomes existem na especificação e que a definição não existe.

A primeira opção viola a regra mais dura desta plataforma — *nunca inventar framework,
número ou fonte*. E viola de um modo particularmente difícil de reverter: conteúdo
inventado que soa competente não é distinguível, seis meses depois, de conteúdo apurado.
Quem ler `ORBIT.md` daqui a um ano não vai saber se aquelas fases saíram de uma fonte ou
de uma sessão de geração. O acervo inteiro perde credibilidade por causa de treze
arquivos que ninguém pediu para serem verdadeiros — só para existirem.

Um acervo com treze lacunas declaradas é auditável. Um acervo com treze invenções bem
escritas não é. Por isso esta task escolheu a segunda opção, e por isso a pasta
`proprietarios/` tem **um** arquivo em vez de catorze.

Uma consequência prática: a **Definição de PRONTO** desta plataforma (`validar.py`
verde, `pytest` verde, auditoria com média ≥ 8,0 e nenhuma seção < 6, registro datado no
`CHANGELOG.md`) não pode ser satisfeita por nenhum destes treze itens, porque não há
como auditar a fidelidade de um texto a uma fonte que não existe. A auditoria não teria
contra o que comparar. O gate, aqui, não é uma formalidade que se contorna: ele
simplesmente não tem entrada.

## O que desbloqueia cada item

Um item sai deste backlog quando o autor da especificação fornecer, no mínimo:

- a **expansão** da sigla, letra por letra;
- o **escopo**: que problema o framework resolve e qual ele deliberadamente não resolve;
- as **entradas**: o que o praticante precisa ter em mãos para aplicá-lo;
- as **saídas**: que artefato concreto sai da aplicação;
- a **origem**: se é técnica pública (e então em que estado de atribuição), material
  interno do autor, ou formulação nova — caso em que passa a ser proprietário e vai para
  `proprietarios/` com o mesmo rigor exigido do `AI-ENGINEERING-FRAMEWORK`.

Com esses cinco campos, o item vira um arquivo em `conhecidos/` ou `proprietarios/`, é
acrescentado ao [`_catalogo.md`](_catalogo.md) e passa a ser citável pelos volumes.
Sem eles, permanece aqui.

## Os treze nomes

### ORBIT

nome presente na especificação original sem definição; aguardando o autor definir escopo, entradas e saídas. Não foi inventado.

### FLOW

nome presente na especificação original sem definição; aguardando o autor definir escopo, entradas e saídas. Não foi inventado.

### NEXUS

nome presente na especificação original sem definição; aguardando o autor definir escopo, entradas e saídas. Não foi inventado.

### FUSION

nome presente na especificação original sem definição; aguardando o autor definir escopo, entradas e saídas. Não foi inventado.

### GENESIS

nome presente na especificação original sem definição; aguardando o autor definir escopo, entradas e saídas. Não foi inventado.

### ATLAS

nome presente na especificação original sem definição; aguardando o autor definir escopo, entradas e saídas. Não foi inventado.

### EVEREST

nome presente na especificação original sem definição; aguardando o autor definir escopo, entradas e saídas. Não foi inventado.

### QUANTUM

nome presente na especificação original sem definição; aguardando o autor definir escopo, entradas e saídas. Não foi inventado.

### IDEA+

nome presente na especificação original sem definição; aguardando o autor definir escopo, entradas e saídas. Não foi inventado.

### PACE

nome presente na especificação original sem definição; aguardando o autor definir escopo, entradas e saídas. Não foi inventado.

### BUILD

nome presente na especificação original sem definição; aguardando o autor definir escopo, entradas e saídas. Não foi inventado.

### SMART-AI

nome presente na especificação original sem definição; aguardando o autor definir escopo, entradas e saídas. Não foi inventado.

### ENTERPRISE-AI

nome presente na especificação original sem definição; aguardando o autor definir escopo, entradas e saídas. Não foi inventado.

## Nota sobre colisão de nomes

Vários destes nomes coincidem com termos de uso corrente em engenharia de software e em
gestão — a palavra `FLOW` aparece em orquestração de agentes (inclusive como primitiva do
CrewAI, documentada em [`conhecidos/crewai.md`](conhecidos/crewai.md)); `ATLAS`, `NEXUS`
e `QUANTUM` nomeiam produtos comerciais de várias empresas; `BUILD` e `PACE` são palavras
comuns. **Essa coincidência não é evidência de nada.** Encontrar na internet um framework
chamado `NEXUS` não autoriza supor que era esse o que a especificação tinha em mente, e
documentar o homônimo como se fosse o item pedido seria a mesma invenção por outro
caminho. Se um destes nomes for desbloqueado, a definição tem de vir do autor, não de
busca por sigla.

## Anti-padrão que este arquivo previne

O anti-padrão tem nome e é comum em acervos gerados com apoio de IA: **completar a
estrutura em vez de completar o conhecimento.** Ele se reconhece por três sinais:

1. o número de arquivos bate exatamente com a lista pedida, sem sobra nem falta;
2. os arquivos têm a mesma extensão de texto e a mesma forma interna;
3. nenhum deles cita fonte, e nenhum deles admite não saber alguma coisa.

Quando os três sinais aparecem juntos, a probabilidade de que a estrutura tenha sido
preenchida em vez de apurada é alta. Este arquivo é a contraprova deliberada: a lista
pedida tinha catorze frameworks proprietários e a plataforma entregou um, mais treze
lacunas nomeadas. A falta é a informação.
