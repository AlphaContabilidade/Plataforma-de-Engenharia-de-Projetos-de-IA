---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 03-Escopo
status: PRONTO
atualizado_em: 2026-07-29
---

# Escopo

Este volume trata do ciclo de vida de um prompt dentro de um único dialeto de provedor:
declarar o contrato, renderizar, registrar, avaliar, promover e depreciar. A fronteira é
declarada aqui de forma explícita porque a especificação original desta plataforma
descrevia quatro volumes com responsabilidade sobreposta sobre prompt, e sobreposição
não declarada produz duas implementações do mesmo comportamento que divergem em silêncio.

## Dentro do escopo

Está dentro do escopo o contrato tipado do prompt — corpo com placeholders, variáveis
com tipo e obrigatoriedade, assinatura canônica e hash de conteúdo. Está dentro do
escopo o registro versionado por nome, com versão derivada do hash, idempotência por
conteúdo, máquina de estados de cinco posições e trilha de auditoria. Está dentro do
escopo a avaliação contra casos de ouro: renderização de cada caso, execução via
executor injetado, casamento da saída por expressão regular, taxa de acerto e deriva
entre duas versões sobre a mesma amostra. Está dentro do escopo a política de promoção,
que é a regra de que nenhuma versão chega a `PROMOVIDO` sem passar por `EM_AVALIACAO`.

## Fora do escopo, e de quem é

| Assunto | Volume responsável | Por que não é aqui |
|---|---|---|
| Compilação de um mesmo prompt para dialetos de provedores diferentes | 28, `PROMPT-COMPILER` | Compilar exige conhecer as particularidades de cada provedor; trazer isso para cá acoplaria o motor a fornecedores e quebraria o objetivo de independência |
| Otimização automática do texto do prompt | 29, `PROMPT-OPTIMIZER` | Otimizar é um laço de busca que consome o avaliador deste volume como função objetivo; misturar o laço com a medição tornaria a medição não auditável |
| Roteamento de execução entre modelos por custo ou latência | 27, `LLM-ROUTER` | Roteamento é decisão sobre onde executar, não sobre o que executar; ela mora atrás do executor injetado |
| Catálogo e características dos modelos disponíveis | 26, `AI-MODELS` | É informação perecível de fornecedor; o motor não pode depender dela para funcionar |
| Estratégia geral de teste da plataforma | 31, `TESTING` | Aqui fica apenas a estratégia de teste do motor, descrita em [`13-Testes.md`](13-Testes.md) |
| Uso de prompt dentro de um laço de agente com ferramentas | 08, `AGENT-ENGINE` | O agente é consumidor do motor; o motor não conhece o laço do agente |

A tabela acima é a fronteira operacional. Ela também define a direção da dependência: os
volumes 28 e 29 consomem os contratos deste volume, e não o contrário. Essa direção é o
que impede ciclo — se o motor precisasse do compilador para registrar uma versão,
nenhum dos dois poderia ser lido primeiro.

## Fronteira interna do próprio volume

Dentro do volume, o avaliador não conhece o registro e o registro não conhece o
avaliador. Quem os amarra é o autor, ou a esteira de integração contínua, chamando
`avaliar` e depois `transicionar`. Essa separação é deliberada: se o registro chamasse o
avaliador, registrar passaria a custar execução de modelo, e registrar precisa ser
barato para ser idempotente sem penalidade. A consequência aceita é que a regra "não
promove sem avaliar" é garantida pela máquina de estados, e não por uma verificação de
resultado dentro de `transicionar`.
