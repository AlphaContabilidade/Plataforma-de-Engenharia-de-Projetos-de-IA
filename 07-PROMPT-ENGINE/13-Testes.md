---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 13-Testes
status: RASCUNHO
atualizado_em: 2026-07-29
---

# Testes

O motor tem trinta e quatro testes distribuídos em três arquivos: onze para o contrato, doze
para o registro e onze para o avaliador. Eles rodam com `python -m pytest exemplos -q` a
partir da raiz da plataforma, sem rede, sem credencial e sem estado em disco. Essa
propriedade não é conveniência: é o que faz do segundo gate da plataforma um gate que ninguém
tem motivo para desligar.

## O que cada arquivo cobre

| Arquivo de teste | Alvo | Casos que só existem por causa de um risco concreto |
|---|---|---|
| `tests/test_prompt_template.py` | Construção, renderização, assinatura e hash | Hash muda quando o tipo de uma variável muda; variável declarada e não usada reprova no construtor |
| `tests/test_prompt_registry.py` | Versionamento, máquina de estados e histórico | Idempotência por hash; promover a segunda versão deprecia a anterior; o enumerado tem exatamente os cinco nomes do diagrama |
| `tests/test_prompt_evaluator.py` | Taxa de acerto, deriva e injeção do executor | Bateria vazia não divide por zero; erro de renderização conta como falha e não sobe; o executor é chamado uma vez por caso |

## Os três testes que carregam o volume

O primeiro é `test_hash_muda_quando_o_tipo_de_uma_variavel_muda`. Ele é o guardião da regra R2:
se alguém simplificar o cálculo do hash para cobrir apenas o corpo, esse teste falha, e sem ele
a simplificação passaria como refatoração inofensiva enquanto tornaria invisível toda mudança de
contrato que não mexesse no texto.

O segundo é `test_mesmo_conteudo_e_idempotente`. Ele afirma que registrar duas vezes devolve `v1`
e que o histórico tem uma única entrada. Sem essa garantia, cada implantação que reimporta o
módulo criaria uma versão nova, e o histórico — que é a base da auditoria — viraria ruído em
poucas semanas.

O terceiro é `test_estado_tem_exatamente_os_cinco_nomes_do_diagrama`. Ele existe porque a máquina
de estados vive em dois lugares: no código e no `stateDiagram-v2` de
[`05-Diagramas.md`](05-Diagramas.md). O teste ancora o lado do código para que a divergência
tenha um sinal automático; o lado do documento continua sendo responsabilidade da auditoria.

## Estratégia, e o que ela deliberadamente não faz

A estratégia é testar o motor com um substituto determinístico do executor e não testar o
provedor. Um teste que chamasse modelo real mediria três coisas ao mesmo tempo — o motor, o
provedor e a rede — e falharia por qualquer uma delas, o que o tornaria inútil como diagnóstico e
caro como rotina. A consequência aceita é explícita: a suíte prova que o motor renderiza,
versiona, transiciona e mede corretamente; ela não prova que um prompt específico funciona bem
com um modelo específico. Essa segunda pergunta é respondida pela bateria de casos de ouro do
próprio prompt, executada contra o provedor real, fora do gate de integração contínua.

## Como este volume se encaixa nos gates da plataforma

O primeiro gate é estrutural e roda `python -m ferramentas.validar 07`: front-matter, substância,
marcadores, diagramas tipados com parágrafo descritivo, exemplos citados que existem e têm teste,
e links relativos que resolvem. O segundo gate é a suíte descrita nesta seção. O terceiro é a
verificação cruzada, `python -m ferramentas.validar --cross-refs`, que confere que toda dependência
declarada aponta para volume existente e que o grafo de pré-requisitos é acíclico. Nenhum volume
recebe o estado de pronto com qualquer um dos três vermelho, e a ordem em que eles rodam é essa
porque o mais barato reprova primeiro.
