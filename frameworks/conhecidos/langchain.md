# LangChain

> Framework de software (terceiro) · atualizado em 2026-07-29
> **Estado de atribuição:** `VERIFICADO` — documentação oficial consultada em 2026-07-29:
> <https://docs.langchain.com/oss/python/langchain/overview>
> **Perecível: sim.** Este arquivo evita de propósito fixar versão, assinatura de função e
> nome de módulo. Trate-o como orientação de arquitetura, não como referência de API.

## O que é

Framework de código aberto para construir aplicações e agentes sobre modelos de linguagem,
com implementações em Python e JavaScript/TypeScript. A tese da documentação oficial é
resumida por ela mesma numa equação: **agente = modelo + *harness***, onde *harness* é o
conjunto de prompt, ferramentas e *middleware* que molda o comportamento do agente. O que o
framework vende, portanto, não é o modelo — é o arnês.

## Peças que importam para arquitetura

Quatro ideias sobrevivem às reorganizações de API e são as que valem estudar.

**1. Interface única de modelo.** O framework padroniza a chamada a modelos de chat,
*embeddings* e afins atrás de uma interface comum, para que trocar de provedor (OpenAI,
Anthropic, Google e outros) não obrigue a reescrever a aplicação. É a promessa mais valiosa e
a mais parcialmente cumprida: a interface unifica a chamada, mas não unifica o comportamento —
o mesmo prompt em dois provedores produz saídas diferentes, e a suíte de avaliação é o que
diz se a troca foi neutra.

**2. Arnês configurável.** A construção do agente se dá por composição de peças opcionais —
guarda-corpos, novas tentativas, roteamento, políticas de uso de ferramenta. A ideia
arquitetural é que o laço do agente seja *montado*, não herdado.

**3. Ferramentas como funções.** Funções comuns são declaradas como ferramentas e entregues ao
agente, que decide quando chamá-las. O padrão conceitual por trás disso é o de raciocínio
intercalado com ação, formalizado em *ReAct* (Shunyu Yao et al., 2022 — ver
[`referencias/papers.md`](../../referencias/papers.md)).

**4. Orquestração separada do agente.** O ecossistema separa a montagem do agente da
orquestração do fluxo: **LangGraph** é a camada de orquestração — grafos, execução durável,
persistência de estado e ponto de intervenção humana; **LangSmith** é a camada de
observabilidade — rastreamento, depuração e avaliação; e há também uma configuração
"baterias incluídas" (*Deep Agents*) com compressão automática de contexto e subagentes.

Essa separação é a lição transferível, e vale mesmo para quem nunca vai usar o framework: o
laço de decisão do agente e o controle de fluxo do processo são preocupações distintas.
Quando estão no mesmo lugar, não se consegue retomar um processo interrompido sem re-executar
a decisão — e re-executar decisão é o que produz efeito colateral duplicado.

## Quando serve

- Aplicação que precisa **trocar de provedor de modelo** ou manter mais de um em produção.
- Fluxo agêntico com **estado durável** e retomada — território do LangGraph.
- Quando você quer **rastreamento e avaliação prontos** em vez de construir a instrumentação.
- Prototipagem rápida com muitos conectores já escritos (bancos vetoriais, carregadores de
  documento, ferramentas).

## Quando NÃO serve

- **Uma única chamada de LLM.** Se a aplicação faz um prompt e lê a resposta, o SDK do
  provedor resolve com menos indireção e menos superfície para quebrar.
- **Quando a estabilidade de API é requisito.** Este ecossistema reorganiza-se com frequência
  — a própria URL da documentação consultada por este arquivo é resultado de um redirecionamento
  permanente do endereço anterior. Em código de longa vida sem manutenção regular, isso é
  dívida.
- **Quando a abstração esconde o prompt.** O maior custo oculto: se você não vê o texto final
  que foi enviado ao modelo, não pode versioná-lo, medi-lo, nem explicar uma regressão. Antes
  de adotar, verifique como se inspeciona o prompt efetivo.
- **Quando a equipe não tem suíte de avaliação.** Um framework de composição facilita mudar
  muita coisa depressa. Sem casos de ouro, "mudou" e "melhorou" ficam indistinguíveis.

## Relação com esta plataforma

Esta plataforma **não depende** de LangChain. As ferramentas em `ferramentas/` usam apenas a
biblioteca padrão do Python, por decisão registrada nas restrições globais do plano, e os
exemplos do volume-piloto (`exemplos/07-prompt-engine/`) implementam template, registry e
avaliador de prompt sem dependência externa — justamente para que o conceito fique legível sem
o acoplamento.

O que interessa ao acervo é o **padrão**: separação entre interface de modelo, arnês,
orquestração e observabilidade. Os volumes `08-AGENT-ENGINE`, `09-ORCHESTRATOR` e
`10-WORKFLOW` tratam desse recorte, e este arquivo é a referência externa deles.

## Como manter este arquivo

Volume e biblioteca perecíveis seguem a mesma regra: **aponte para a fonte viva, não a
transcreva.** Se você se pegar copiando para cá o nome de uma função, a assinatura de um
construtor ou um número de versão, pare — esse é o conteúdo que envelhece em semanas e
transforma o acervo em armadilha. Atualize a data e a URL de consulta no topo quando revisar.

## Fonte consultada

- <https://docs.langchain.com/oss/python/langchain/overview> — consultada em 2026-07-29.
  (O endereço anterior, `https://python.langchain.com/docs/introduction`, responde com
  redirecionamento permanente para o domínio atual.)
