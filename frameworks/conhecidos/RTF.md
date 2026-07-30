# RTF — Role, Task, Format

> Técnica pública de estruturação de prompt · atualizado em 2026-07-30
> **Estado de atribuição:** `DOMINIO-PUBLICO-SEM-ATRIBUICAO-SEGURA`
> Técnica de domínio público, origem não atribuída com segurança.

## O que a sigla expande

| Letra | Campo | O que o campo responde |
|---|---|---|
| **R** | *Role* (papel) | De que ponto de vista o modelo deve responder |
| **T** | *Task* (tarefa) | Que operação exatamente ele deve executar |
| **F** | *Format* (formato) | Em que forma a saída deve chegar |

Três campos, nessa ordem. Não há quarto campo: RTF é deliberadamente a estrutura mais
enxuta do conjunto, e essa é a sua vantagem.

## Por que funciona

RTF não é mágica de prompt — é o preenchimento de três lacunas que o pedido informal
costuma deixar abertas, e cada lacuna aberta é uma decisão que o modelo toma sozinho.

- **Sem papel**, o modelo escolhe um registro por conta própria. Um pedido de triagem
  técnica respondido com o vocabulário de um blog de produtividade não está errado:
  está sem papel definido.
- **Sem tarefa explícita**, o modelo escolhe o verbo. "Fale sobre a categoria INF-104"
  pode virar definição, comparação, histórico ou parecer. Cada um é uma resposta diferente
  para o mesmo pedido.
- **Sem formato**, a saída vem em prosa. Prosa é o formato mais difícil de consumir por
  programa e o mais difícil de comparar entre execuções.

O terceiro campo é o que faz RTF valer num pipeline. Um formato declarado é um formato
verificável: se você pede `JSON com as chaves categoria, fila, confianca`, o consumidor
pode falhar de forma explícita quando a chave não vem — o que é infinitamente melhor que
um parser tolerante que engole a divergência.

## Quando serve

- Pedido **único e autocontido**, sem etapas com dependência entre si.
- Casos em que a **saída é consumida por código** e o formato precisa ser estável.
- Como camada de base num template versionado: `Role` e `Format` ficam fixos no
  template, `Task` entra por variável.
- Quando você quer o menor prompt que ainda é reprodutível — RTF é o piso, não o teto.

## Quando NÃO serve

- **Tarefa com etapas ordenadas.** RTF não tem campo para sequência. Colar as etapas
  dentro de `Task` transforma o campo num parágrafo longo e a estrutura deixa de ajudar.
  Use RISE.
- **Tarefa em que o contexto de negócio é o que decide a resposta.** RTF não tem campo
  de contexto. Empurrar as regras da operação para dentro de `Role` ("você é um analista
  que sabe que nesta operação pedido de acesso vai sempre para a fila de infraestrutura")
  mistura identidade com fato, e o modelo trata fato como característica de personagem —
  que ele pode reinterpretar. Use CARE.
- **Tarefa cujo critério de sucesso não é óbvio.** RTF diz o que fazer, não como saber
  se ficou bom. Use TAG.
- **Saída longa e argumentativa** em que o formato rígido atrapalha o raciocínio.
- **Quando o campo `Role` é usado para transferir competência que o modelo não tem.**
  Escrever "você é um analista de triagem sênior" não faz o modelo conhecer o catálogo
  desta operação; faz ele adotar o tom de quem conhece. Esse é o modo de falha mais caro
  do RTF, e está descrito na seção de limitações.

## Exemplo concreto

Um pedido informal, do tipo que se digita sem pensar:

```text
me ajuda a classificar essas solicitações que chegaram
```

O mesmo pedido em RTF, com os três campos preenchidos:

```text
# Role
Você é um analista de triagem que classifica solicitações recebidas contra um
catálogo fechado de categorias. Você não tem acesso a nenhuma informação sobre estas
solicitações além do que está neste prompt.

# Task
Para cada solicitação abaixo, proponha uma categoria do catálogo fornecido.
Regras de decisão, em ordem de precedência:
1. Se a descrição da solicitação nomear um sistema presente na lista de sistemas
   conhecidos, use a categoria daquele sistema.
2. Se não nomear, e o solicitante pertencer a uma área que tem fila dedicada na
   lista de filas, use a categoria padrão daquela fila.
3. Se nenhuma das duas se aplicar, devolva a categoria vazia e confiança "baixa".
Nunca escolha uma categoria apenas porque ela é a mais frequente. Categoria sem
evidência na descrição é categoria vazia.

# Format
JSON, uma lista de objetos, sem texto antes ou depois. Chaves exatamente:
  "id" (string, o identificador da solicitação como recebido),
  "horas" (número, horas estimadas; 0 quando não informado),
  "descricao" (string, copiada literalmente da solicitação),
  "categoria" (string, vazia se não houver evidência),
  "regra_aplicada" (um de: "sistema", "fila-da-area", "sem-evidencia"),
  "confianca" (um de: "alta", "media", "baixa").
```

O que mudou de fato: o `Role` fechou o escopo de conhecimento ("você não tem acesso a
nenhuma informação além do que está neste prompt" é a parte que mais reduz invenção); a
`Task` transformou o julgamento em ordem de precedência auditável e criou uma saída
legítima para o caso "não sei"; e o `Format` deu ao consumidor um contrato — `confianca`
e `regra_aplicada` permitem que o código a jusante roteie automaticamente só o que veio
com `alta`, e mande o resto para revisão humana.

Note que a estrutura não melhorou o modelo. Ela melhorou o *pedido*, e por consequência
tornou o resultado verificável.

## Limitações

**1. O papel não confere competência.** Este é o mal-entendido central do RTF. `Role` é
um seletor de registro e vocabulário; ele não injeta conhecimento que não está nos pesos
nem no contexto. "Você é um especialista nas políticas desta operação" produz um texto com
a segurança de um especialista, o que é precisamente o pior resultado possível quando o
conhecimento não está lá: aumenta a fluência sem aumentar a exatidão, e portanto reduz a
chance de o leitor perceber o erro. Se a resposta depende do catálogo, o catálogo vai no
contexto.

**2. Não há campo para incerteza.** RTF não pede ao modelo que declare o que não sabe.
Ou você abre esse espaço dentro de `Format` (como no exemplo acima, com `confianca`), ou
não existe. Um RTF sem saída para "não sei" empurra o modelo a preencher.

**3. `Format` restringe a forma, não a veracidade.** JSON válido com valores inventados é
um resultado comum e especialmente perigoso, porque passa em qualquer validação de
esquema. O formato é um gate sintático; ele não substitui verificação de conteúdo.

**4. É estrutura, não avaliação.** Nenhuma das seis técnicas desta pasta mede qualidade.
Adotar RTF sem casos de ouro e sem comparação entre versões apenas organiza o prompt —
não diz se ele está melhorando. Essa medição é assunto do volume `07-PROMPT-ENGINE`
(seções `13-Testes` e `14-Metricas`) e do avaliador em
`exemplos/07-prompt-engine/`.

**5. Não há atribuição.** Não se sabe com segurança quem cunhou a sigla. Este arquivo não
cita autor, ano, empresa ou artigo, e não deve passar a citar sem fonte primária lida.

## Relacionados

- [`TAG.md`](TAG.md) — quando falta o critério de sucesso.
- [`RISE.md`](RISE.md) — quando faltam etapas ordenadas.
- [`CARE.md`](CARE.md) — quando falta contexto de negócio.
- [`_catalogo.md`](../_catalogo.md) — estados de atribuição desta biblioteca.
