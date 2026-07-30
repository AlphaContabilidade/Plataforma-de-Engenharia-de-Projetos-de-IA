# Semantic Kernel

> Framework de software (terceiro) · atualizado em 2026-07-29
> **Estado de atribuição:** `VERIFICADO` — documentação oficial consultada em 2026-07-29:
> <https://learn.microsoft.com/en-us/semantic-kernel/overview/>
> **Perecível: sim.** Sem número de versão nem assinatura de API neste arquivo.

## O que é

SDK de código aberto da Microsoft para construir agentes de IA e integrar modelos a bases de
código existentes em **C#, Python e Java**. A documentação o descreve como um *middleware*
leve, voltado a entrega de soluções de nível corporativo, e destaca três compromissos:
modularidade, observabilidade (telemetria, ganchos e filtros) e estabilidade — a documentação
consultada afirma compromisso com mudanças não disruptivas a partir da versão 1.0 nas três
linguagens.

## O recorte que o distingue

Os outros três frameworks desta pasta partem do modelo e constroem a aplicação em volta dele. O
Semantic Kernel parte do **código que já existe** e o expõe ao modelo. A documentação é explícita
sobre o mecanismo: descreve-se o código existente para o modelo; quando o modelo decide que
precisa daquela capacidade, ele solicita a chamada de função; o kernel traduz a solicitação em
chamada real e devolve o resultado ao modelo.

Duas consequências práticas dessa inversão de ponto de partida:

**1. O código de negócio permanece o dono da regra.** A função que calcula, valida ou grava
continua sendo código testado. O modelo escolhe *quando* chamá-la; ele não reimplementa a regra
em prosa. Para domínios em que a regra é normativa — regulatório, contratual, tarifário — essa é a
diferença entre um sistema auditável e um sistema opinativo.

**2. A integração usa especificação de API como contrato.** A documentação menciona o uso de
especificações OpenAPI para que extensões possam ser compartilhadas com outros
desenvolvedores, inclusive de baixo código. Contrato declarado é contrato verificável.

## Conceitos centrais

| Conceito | Papel |
|---|---|
| **Kernel** | o *middleware* que recebe a solicitação do modelo, resolve a função e devolve o resultado |
| **Plugins** | unidades que empacotam capacidades — código nativo existente e funções baseadas em prompt |
| **Connectors** | integrações prontas com serviços de IA e de dados, para trocar de serviço sem reescrever a aplicação |
| **Filters / hooks** | pontos de interceptação para telemetria, política e controle — a base do argumento de observabilidade |
| **Chamada de função** | o mecanismo pelo qual o modelo solicita a execução de uma capacidade descrita |

Os **filtros** são a peça mais subestimada. Eles são o lugar arquiteturalmente correto para
colocar o que não se deve confiar ao prompt: limite de gasto, registro de auditoria, bloqueio
de operação irreversível, mascaramento de dado sensível. Instrução em prompt é pedido; filtro é
mecanismo. A diferença aparece no dia em que o modelo decide diferente.

## Quando serve

- **Aplicação corporativa existente** em C#, Java ou Python que precisa ganhar capacidade de
  IA sem virar um projeto de IA.
- Quando **estabilidade de API** e ciclo de suporte pesam na decisão — é o argumento central da
  documentação, e é um argumento raro neste ecossistema.
- Quando a organização já está em plataforma Microsoft e a integração com o restante do
  ambiente vale mais que a amplitude de conectores de terceiros.
- Quando é preciso **política aplicada por mecanismo** (filtros), e não por instrução.

## Quando NÃO serve

- **Prototipagem exploratória rápida** — a cerimônia de kernel, plugins e registro cobra
  adiantado o que um script de vinte linhas não precisa pagar.
- **Quando a aplicação é essencialmente um grafo de agentes** — o desenho de orquestração é
  mais explícito em frameworks que nasceram para isso.
- **Quando não se tem código para expor.** O valor do SDK está na integração com o que existe;
  sem esse código, sobra a parte menos diferenciada.
- **Quando alguém espera que "chamada de função" signifique determinismo.** A função é
  determinística; a **decisão** de chamá-la não é. Se o efeito é irreversível, o gate fica no
  código — antes da execução — não na esperança de que o modelo chame a função certa. Esta é a
  mesma regra que esta plataforma aprendeu construindo classificadores apoiados em
  evidência: escrita irreversível passa por verificação de programa, sempre.

## Relação com esta plataforma

Não há dependência. O que o acervo toma emprestado é o princípio: **a regra vive no código; o
modelo escolhe quando invocá-la.** É o mesmo princípio pelo qual os três gates desta plataforma
são programas Python (`ferramentas/validar.py`, `pytest`, `validar.py --cross-refs`) e não
instruções em prompt — um gate que é prompt pode ser argumentado; um gate que é `exit code` não
pode.

Referência externa dos volumes `16-INTEGRATION`, `08-AGENT-ENGINE` e `41-SDK`.

## Fonte consultada

- <https://learn.microsoft.com/en-us/semantic-kernel/overview/> — consultada em 2026-07-29.
