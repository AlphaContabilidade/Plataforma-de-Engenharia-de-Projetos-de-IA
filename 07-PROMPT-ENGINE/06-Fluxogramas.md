---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 06-Fluxogramas
status: RASCUNHO
atualizado_em: 2026-07-29
---

# Fluxogramas

Os diagramas de [`05-Diagramas.md`](05-Diagramas.md) descrevem o que o motor é. Os
fluxogramas desta seção descrevem o que o operador faz, e onde ele decide. A diferença
importa: a máquina de estados diz quais transições são possíveis, o fluxograma diz em que
ponto alguém tem de olhar um número e escolher.

## Ciclo completo, do rascunho à produção

```mermaid
flowchart TD
    A[Necessidade de um prompt novo ou alterado] --> B[Declarar corpo e variaveis tipadas]
    B --> C{Placeholders do corpo e variaveis declaradas concordam?}
    C -- nao --> D[ContratoViolado na construcao]
    D --> B
    C -- sim --> E[registrar no PromptRegistry]
    E --> F{Hash ja existe para este nome?}
    F -- sim --> G[Devolve a versao existente, historico intacto]
    G --> Z[Prompt disponivel via obter]
    F -- nao --> H[Cria vN no estado VERSIONADO]
    H --> I{Existe caso de ouro para este prompt?}
    I -- nao --> J[Escrever casos de ouro com entradas e padrao esperado]
    J --> I
    I -- sim --> K[transicionar para EM_AVALIACAO]
    K --> L[avaliar com o executor injetado]
    L --> M{taxa_acerto atinge o limiar acordado?}
    M -- nao --> N[transicionar de volta para VERSIONADO]
    N --> B
    M -- sim --> O{comparar contra a versao promovida da deriva positiva?}
    O -- nao --> P[transicionar para DEPRECIADO e registrar o motivo]
    O -- sim --> Q[transicionar para PROMOVIDO]
    Q --> R[A versao promovida anterior cai para DEPRECIADO no mesmo passo]
    R --> Z
```

O fluxograma tem quatro pontos de decisão e nenhum deles é uma questão de gosto. O
primeiro é verificado pelo construtor. O segundo é verificado pelo hash e é o que impede
que reimplantar o mesmo prompt polua o histórico. O terceiro exige que exista caso de
ouro antes da avaliação, porque uma bateria vazia devolve taxa de acerto zero e nunca
atinge limiar algum — a ausência de evidência não é tratada como evidência de acerto. O
quarto compara a candidata contra a versão que está em produção sobre a mesma amostra, e
é aqui que a decisão deixa de ser "o prompt novo parece melhor" e passa a ser um número
com sinal.

## Queda de qualidade em produção

```mermaid
flowchart LR
    A[Sinal de degradacao: taxa de acerto cai ou incidente reportado] --> B[historico do nome afetado]
    B --> C{A versao promovida hoje e a mesma de quando o sinal comecou?}
    C -- nao --> D[Reavaliar a versao promovida atual contra os casos de ouro]
    C -- sim --> E[Reavaliar com casos de ouro ampliados pelo incidente]
    D --> F{A queda reproduz na bateria?}
    E --> F
    F -- sim --> G[Registrar versao corrigida e seguir o ciclo normal]
    F -- nao --> H[A causa esta fora do prompt: executor, provedor ou dados de entrada]
    H --> I[Encaminhar para o volume responsavel e registrar o achado]
    G --> J[Promover so depois de deriva positiva medida]
```

O segundo fluxograma existe porque a pergunta mais frequente em um incidente não é "qual
prompt usar" e sim "o prompt mudou?". Sem registro, essa pergunta consome horas; com
registro, ela é uma leitura de `historico`. O ramo que termina fora do prompt é
deliberadamente explícito: quando a queda não reproduz na bateria de casos de ouro, a
causa provável está no executor, no provedor ou nos dados de entrada, e insistir em
reescrever o prompt nesse cenário produz mudança sem efeito e ainda gasta uma versão do
histórico. Cada incidente que reproduz na bateria deve terminar com um caso de ouro novo,
porque é assim que a bateria cresce na direção dos erros que realmente aconteceram em vez
de crescer na direção do que era fácil imaginar.
