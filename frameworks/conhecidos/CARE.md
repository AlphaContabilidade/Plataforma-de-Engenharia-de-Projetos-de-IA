# CARE — Context, Action, Result, Example

> Técnica pública de estruturação de prompt · atualizado em 2026-07-29
> **Estado de atribuição:** `DOMINIO-PUBLICO-SEM-ATRIBUICAO-SEGURA`
> Técnica de domínio público, origem não atribuída com segurança.

## O que a sigla expande

| Letra | Campo | O que o campo responde |
|---|---|---|
| **C** | *Context* (contexto) | Que situação, dados e restrições cercam o pedido |
| **A** | *Action* (ação) | Que operação executar sobre esse contexto |
| **R** | *Result* (resultado) | Que resultado caracteriza sucesso |
| **E** | *Example* (exemplo) | Uma demonstração do par entrada→saída desejado |

**Variante conhecida:** o `E` final aparece também como *Expectation* (expectativa), o
que aproxima CARE do RISE e faz o quarto campo repetir o terceiro. A leitura com
*Example* é a que este acervo adota, porque é a que acrescenta algo que nenhuma das
outras cinco técnicas desta pasta acrescenta: **uma demonstração**. Se a sua fonte usa
*Expectation*, o conteúdo dos campos muda, mas a técnica não deixa de ser a mesma —
apenas perde o único campo que a distingue.

## Por que funciona

CARE é a única das seis estruturas que reserva espaço para **exemplo**. Isso importa mais
do que parece: um exemplo carrega, de forma compacta, informação que a instrução em prosa
transmite mal — nível de detalhe, granularidade, tom, o que fazer com casos de borda,
quanto arredondar, quando abreviar. Um único par entrada→saída bem escolhido substitui
meia página de instrução, e substitui melhor.

O campo `Context` é o segundo diferencial. RTF não tem onde colocar regra de negócio; TAG
não tem onde colocar dado. CARE tem. E o lugar certo para a regra da empresa é o contexto,
não o papel — porque no contexto ela é um fato dado ao modelo, e no papel ela é uma
característica de personagem que o modelo pode reinterpretar quando o caso não encaixa.

## Quando serve

- **Domínio com regra própria**, em que a resposta genericamente correta é a resposta
  errada para esta empresa. Contabilidade, fiscal, jurídico e compliance vivem disso.
- Quando existe **um exemplo real e representativo** para mostrar. Este é o gatilho
  principal: se você tem o caso resolvido em mãos, CARE aproveita-o.
- Quando a saída tem **convenção sutil** que é mais fácil demonstrar que descrever
  (nomenclatura interna, casas decimais, formato de identificador, como escrever
  observações de lançamento).
- Como estrutura de *few-shot*: o campo `Example` é o encaixe natural para uma ou mais
  demonstrações.

## Quando NÃO serve

- **Quando você não tem exemplo.** Um exemplo inventado para preencher o campo é a pior
  coisa que se pode colocar num prompt CARE: ele será tratado como padrão a imitar. Um
  exemplo fabricado com valores, nomes ou categorias plausíveis mas falsos ensina o
  modelo a produzir exatamente aquele tipo de falsidade. Sem exemplo real, use RTF.
- **Quando um exemplo enviesa.** Um só exemplo faz o modelo generalizar da amostra: se o
  seu exemplo é um caso simples, os casos difíceis vêm respondidos como se fossem
  simples. Ou mostre dois exemplos contrastantes (um trivial, um de borda), ou nenhum.
- **Tarefa procedimental com muitas etapas** — CARE não tem campo de sequência. Use RISE.
- **Contexto muito longo.** CARE convida a despejar tudo no primeiro campo, e contexto
  inflado degrada a atenção do modelo ao material do meio do prompt (efeito documentado
  em *Lost in the Middle*, Nelson F. Liu et al., 2023 — ver
  [`referencias/papers.md`](../../referencias/papers.md)). Contexto é curadoria, não
  despejo.
- **Pedido trivial**: quatro campos para "resuma este parágrafo" é cerimônia sem retorno.

## Exemplo concreto

Tarefa real do domínio: escrever a observação de um lançamento a pagar que será lido por
outro contador seis meses depois.

```text
# Context
Contabilidade brasileira, cliente do regime Lucro Presumido. Os lançamentos a pagar são
criados por automação e revisados por humanos. A observação do lançamento é o único
lugar onde fica registrado *por que* aquele valor foi classificado daquela forma — o
histórico do extrato bancário é truncado pelo banco e frequentemente ilegível.
Convenções internas em vigor:
- a observação começa pelo nome do fornecedor em maiúsculas, como aparece no cadastro;
- valor divergente do contratado é sempre explicitado, com os dois valores;
- quando a decisão veio de regra e não de documento, a regra é nomeada;
- nunca se escreve "conforme conversado" nem "ajuste" sem dizer qual.

# Action
Escreva a observação do lançamento a partir dos dados brutos que eu fornecer.
Se algum dado necessário para cumprir as convenções não estiver presente, escreva a
observação com o que há e acrescente, na última linha, "FALTA: <o que falta>".

# Result
Uma observação de 1 a 3 linhas, sem abreviação nova, legível por quem não participou da
decisão, e suficiente para que essa pessoa reconstitua o raciocínio sem abrir o extrato.

# Example
Entrada:
  fornecedor_cadastro: "SABESP - CIA SANEAMENTO BASICO SP"
  valor_titulo: 400.00
  valor_pago: 322.42
  origem_da_decisao: "fatura recebida por e-mail em 27/07/2026"
Saída:
  SABESP - CIA SANEAMENTO BASICO SP. Título aberto de 400,00 alterado para 322,42,
  valor da fatura recebida em 27/07/2026. Diferença de 77,58 é consumo menor no mês,
  não desconto.
```

O que cada campo entregou: `Context` colocou as quatro convenções internas como fatos, e
explicou *por que* elas existem — o modelo que entende que a observação substitui um
extrato ilegível escreve diferente do modelo que só recebeu a regra. `Action` criou uma
saída honesta para dado ausente (`FALTA:`), em vez de deixar o modelo preencher. `Result`
definiu o teste de aceitação em termos de outra pessoa, não de adjetivos. E `Example`
transmitiu em cinco linhas o que a prosa transmitiria mal: que "77,58" é escrito com
vírgula, que a diferença é explicada e não só mencionada, e que a última frase mata a
interpretação errada mais provável ("não desconto").

Esse último detalhe é o argumento inteiro a favor do campo `Example`. Nenhuma instrução
em prosa produziria, com a mesma economia, a percepção de que a observação deve fechar a
porta para a leitura equivocada.

## Limitações

**1. O exemplo é a maior alavanca e o maior risco.** O modelo imita o exemplo com muito
mais força do que obedece à instrução. Um exemplo com erro propaga o erro; um exemplo
inventado ensina a inventar. Trate o campo `Example` como código em produção: ele precisa
estar correto, precisa ser revisado, e precisa ser atualizado quando a convenção muda.

**2. Um exemplo define implicitamente a distribuição.** O modelo assume que os casos
futuros parecem com o que ele viu. Se o único exemplo é um caso limpo, casos sujos vêm
respondidos como limpos — inclusive com a mesma segurança de tom.

**3. `Context` incha.** É o campo que mais cresce entre versões de um prompt, porque cada
incidente adiciona uma regra. Sem poda periódica, o contexto vira um sedimento de
exceções em que nem o autor sabe mais o que é regra viva. Versione o prompt (ver
`exemplos/07-prompt-engine/prompt_registry.py`) e revise o contexto como se fosse código.

**4. `Result` tende a virar adjetivo.** "Resultado: uma observação clara e profissional"
não é critério — é elogio antecipado. Critério é: quem lê consegue reconstituir a decisão
sem abrir o extrato. A diferença é que o segundo pode ser testado.

**5. Não há atribuição, e a expansão do `E` diverge entre fontes.** Este arquivo registra
as duas leituras e não atribui autoria.

## Relacionados

- [`RTF.md`](RTF.md) — quando não há exemplo real para mostrar.
- [`RISE.md`](RISE.md) — quando a tarefa é uma sequência.
- [`BAB.md`](BAB.md) — quando o pedido é mudança de estado, não produção de artefato.
- [`referencias/papers.md`](../../referencias/papers.md) — *Lost in the Middle*, sobre o
  custo do contexto inflado.
