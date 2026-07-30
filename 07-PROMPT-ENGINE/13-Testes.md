---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 13-Testes
status: PRONTO
atualizado_em: 2026-07-29
---

# Testes

O motor tem trinta e sete funções de teste distribuídas em três arquivos — treze para o
contrato, treze para o registro e onze para o avaliador — que o pytest coleta como **trinta e
nove casos**, porque o teste de valores de fronteira da taxa de acerto é parametrizado em
três. Trinta e nove é o número que `python -m pytest exemplos/07-prompt-engine -q` imprime, e
é ele que vale: contagem de funções e contagem de casos divergem sempre que há parametrização,
e citar a primeira como se fosse a segunda faz o leitor que roda o comando duvidar do resto da
seção. Repare que o comando citado tem **escopo**, e isso é deliberado: `pytest exemplos -q`,
sem escopo, soma os exemplos de todos os volumes do acervo, então o número que ele imprime
cresce a cada volume novo. Uma afirmação verdadeira hoje apodreceria sozinha, sem que ninguém
editasse esta seção e sem que gate nenhum percebesse — foi o que aconteceu com a primeira
versão deste parágrafo, e a auditoria de 2026-07-30 pegou.
A suíte roda a partir da raiz da plataforma, sem rede, sem credencial e sem estado em disco.
Essa propriedade não é conveniência: é o que faz do segundo gate da plataforma um gate que
ninguém tem motivo para desligar.

## O que cada arquivo cobre

| Arquivo de teste | Alvo | Casos que só existem por causa de um risco concreto |
|---|---|---|
| `tests/test_prompt_template.py` | Construção, renderização, assinatura e hash | Hash muda quando o tipo de uma variável muda; hash muda quando a obrigatoriedade muda; hash ignora `descricao`; variável declarada e não usada reprova no construtor |
| `tests/test_prompt_registry.py` | Versionamento, máquina de estados e histórico | Idempotência por hash; mudança só de obrigatoriedade gera `v2`; promover a segunda versão deprecia a anterior; o enumerado tem exatamente os cinco nomes do diagrama |
| `tests/test_prompt_evaluator.py` | Taxa de acerto, deriva e injeção do executor | Bateria vazia não divide por zero; erro de renderização conta como falha e não sobe; o executor é chamado uma vez por caso |

## Os três testes que carregam o volume

O primeiro é `test_hash_muda_quando_o_tipo_de_uma_variavel_muda`. Ele é o guardião da regra R2:
se alguém simplificar o cálculo do hash para cobrir apenas o corpo, esse teste falha, e sem ele
a simplificação passaria como refatoração inofensiva enquanto tornaria invisível toda mudança de
contrato que não mexesse no texto. Ele tem um irmão que existe por um defeito real, encontrado
por auditoria e não por intuição: `test_hash_muda_quando_a_obrigatoriedade_de_uma_variavel_muda`.
A primeira versão do motor deixava `obrigatoria` fora da assinatura, e dois contratos que
diferiam só nesse campo colidiam no hash — `registrar` devolvia `v1` para o segundo e o
histórico não guardava a mudança, embora ela alterasse o que `render` faz. O par de testes
cobre agora os dois campos da assinatura que decidem comportamento, e um terceiro,
`test_hash_ignora_descricao`, fixa o limite do outro lado, para que a cobertura do hash seja
uma escolha verificada e não um acidente da implementação.

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
