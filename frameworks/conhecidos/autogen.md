# AutoGen

> Framework de software (terceiro) · atualizado em 2026-07-29
> **Estado de atribuição:** `VERIFICADO` — documentação oficial consultada em 2026-07-29:
> <https://microsoft.github.io/autogen/stable/>
> **Perecível: sim, e mais que os outros** — houve reescrita de arquitetura, e material
> anterior a ela descreve um framework que não é mais o mesmo.

## O que é

Framework da Microsoft para construir agentes e aplicações de IA, com suporte a sistemas de
agente único e multiagente conversacional. A documentação consultada organiza o projeto em
quatro pacotes com propósitos distintos:

| Pacote | Para que serve |
|---|---|
| **Core** | framework de programação **orientado a eventos**, base para sistemas multiagente escaláveis e distribuídos |
| **AgentChat** | camada de programação conversacional (Python 3.10+), construída sobre o Core |
| **Studio** | interface web para prototipar aplicações de agente sem escrever código, construída sobre o AgentChat |
| **Extensions** | integrações com serviços externos — servidores de Model Context Protocol, API de assistentes da OpenAI, Docker para execução de código, gRPC para agentes distribuídos |

A recomendação implícita nessa organização é útil: **Studio** para prototipar sem código,
**AgentChat** para aplicação conversacional, **Core** quando o sistema é para valer.

## A ideia que vale estudar: eventos em vez de chamadas

O ponto arquitetural relevante do AutoGen é que o núcleo é **orientado a eventos e assíncrono**,
no espírito de um modelo de atores, em vez de uma cadeia de chamadas síncronas.

A consequência prática é maior do que parece. Num desenho por chamadas, o agente A chama o
agente B e espera; o estado do sistema vive na pilha de execução, e uma interrupção no meio
perde tudo. Num desenho por eventos, cada agente reage a mensagens que chegam e publica
mensagens que outros consomem; o estado vive nas mensagens e no armazenamento, não na pilha.
Isso é o que torna viável distribuir os agentes por processos ou máquinas — e, mais importante
no dia a dia, é o que torna possível **observar** o sistema: a fila de eventos é o log.

Quem constrói sistema de agente sem nunca usar AutoGen ainda ganha em conhecer esse recorte,
porque ele é o divisor entre um protótipo que roda numa sessão e um sistema que sobrevive a
reinício.

## Quando serve

- Sistema multiagente que precisa **escalar ou distribuir** (processos separados, máquinas
  separadas, comunicação por gRPC).
- Quando a **execução de código gerado** faz parte do fluxo e precisa de isolamento — a
  integração com Docker existe para isso, e executar código gerado por modelo fora de
  contêiner é um risco que não se justifica.
- Quando se quer **prototipar sem código** e depois descer para o framework — o caminho
  Studio → AgentChat → Core é explícito na documentação.
- Quando o sistema já consome servidores MCP.

## Quando NÃO serve

- **Tarefa de agente único e simples.** O modelo de eventos cobra complexidade adiantada:
  registro de agentes, tipos de mensagem, assinatura de tópicos. Para um laço de ferramenta
  simples, é máquina grande demais.
- **Quando a equipe não domina programação assíncrona.** Depuração de sistema orientado a
  eventos é qualitativamente mais difícil que depuração de pilha de chamadas — o rastro está
  espalhado no tempo, não empilhado.
- **Quando o material de referência disponível é antigo.** Este é um risco concreto e
  específico deste framework: a reescrita de arquitetura significa que tutoriais, respostas de
  fórum e trechos de código anteriores a ela podem não se aplicar. Confirme a data de tudo o que
  você copiar.
- **Quando o determinismo é requisito no caminho crítico.** Vale aqui o mesmo que em
  [`crewai.md`](crewai.md): efeito irreversível pede código, não agente.

## O risco específico de conversa entre agentes

O padrão conversacional multiagente tem um modo de falha próprio, e ele não é técnico: dois
agentes conversando **convergem**. Eles chegam a um acordo articulado, com aparência de
deliberação, que não é evidência de correção — é evidência de que ambos partiram do mesmo
modelo, com o mesmo viés, e se reforçaram.

A mitigação não está no framework. Está em (a) usar **modelos diferentes** para papéis que
precisam discordar, (b) manter um **gate determinístico** fora da conversa, e (c) limitar o
número de turnos, porque conversas longas entre agentes gastam muito e convergem mais, não
menos. Esta plataforma aplica as três coisas: o gerador é um modelo, o auditor é outro
(`auditor-fable`), e os três gates são programas Python cujo veredicto não é negociável por
conversa. Ver
[`proprietarios/AI-ENGINEERING-FRAMEWORK.md`](../proprietarios/AI-ENGINEERING-FRAMEWORK.md).

## Relação com esta plataforma

Não há dependência. A plataforma toma emprestada uma só ideia — **auditoria por outro
participante, com veredicto fora da conversa** — e a implementa com subagente do Claude Code.
O framework é referência externa dos volumes `08-AGENT-ENGINE`, `09-ORCHESTRATOR` e
`16-INTEGRATION`.

## Fonte consultada

- <https://microsoft.github.io/autogen/stable/> — consultada em 2026-07-29.
