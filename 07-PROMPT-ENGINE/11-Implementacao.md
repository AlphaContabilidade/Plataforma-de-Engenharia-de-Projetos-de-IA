---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 11-Implementacao
status: RASCUNHO
atualizado_em: 2026-07-29
---

# Implementação

Os três módulos do motor existem como código executável com teste, e é esse código que
esta seção descreve. As citações abaixo são verificadas pelo gate: o validador confere que
o arquivo citado existe e que existe o teste correspondente em `tests/test_<arquivo>.py`.
Documentação que cita código inexistente reprova.

<!-- exemplo: exemplos/07-prompt-engine/prompt_template.py -->
<!-- exemplo: exemplos/07-prompt-engine/prompt_registry.py -->
<!-- exemplo: exemplos/07-prompt-engine/prompt_evaluator.py -->

## Passo 1: o contrato

O módulo do contrato tem uma decisão estrutural na primeira linha útil: a expressão regular
de placeholder aceita apenas identificadores, na forma `[A-Za-z_][A-Za-z0-9_]*` entre chaves.
Restringir a gramática resolve um problema real — prompt que pede saída em JSON carrega
chaves literais, e uma gramática permissiva as confundiria com variáveis. A mesma restrição é
o que permite substituir por expressão regular em vez de `str.format`, que quebraria diante
dessas chaves.

A validação acontece em `__post_init__`, ou seja, na construção. O método calcula o conjunto
de placeholders usados no corpo e o conjunto de nomes declarados, e reprova as duas
diferenças: placeholder sem declaração quebraria depois, em `render`, e variável declarada e
não usada é contrato mentiroso, porque quem lê a assinatura acredita que ela influencia a
saída. A mensagem de erro nomeia as duas listas, o que faz o diagnóstico caber na exceção.

`render` percorre as variáveis declaradas em vez de percorrer os valores recebidos. A ordem
importa: percorrer os declarados é o que permite descobrir a obrigatória ausente e preencher
a opcional com texto vazio. As chaves extras são detectadas antes, por diferença de
conjuntos, e levantam com a lista do que sobrou.

## Passo 2: o registro

O registro guarda um dicionário de nome para lista de entradas, e a entrada é a única
estrutura mutável do motor — mutável porque o estado dela é justamente o que evolui. A
função `registrar` varre as entradas comparando o hash antes de criar versão, e é essa varredura
que dá a idempotência: reimportar o módulo em cada implantação não polui o histórico. O
rótulo da versão é derivado do tamanho da lista, então a numeração é densa e sequencial por
construção.

`transicionar` é o ponto onde a regra R3 vive. Ele valida o destino contra `TRANSICOES`,
levanta com a lista de destinos válidos quando o destino não é permitido, e — no caso
específico de promoção — rebaixa a versão promovida anterior antes de gravar o estado novo.
Fazer as duas coisas na mesma chamada é o que impede o instante em que duas versões do mesmo
nome se declaram a de produção.

Os dois auxiliares privados centralizam a resolução de nome e de versão, o que faz com que
toda mensagem de `NaoRegistrado` traga a lista do que existe. Erro de consulta que informa as
opções disponíveis economiza uma ida ao código.

## Passo 3: o avaliador

O avaliador recebe o executor no construtor e o guarda em atributo privado. `avaliar` conta
os casos com um contador próprio em vez de medir o tamanho da coleção, porque a entrada é
declarada como iterável e um gerador não tem tamanho. Cada caso passa por `render` dentro de
um bloco de tratamento: falha de contrato vira `Falha` com o motivo, e não exceção, para que
um caso malformado não esconda o estado real dos outros. O casamento usa `re.search`, e não
`re.fullmatch`, o que torna o padrão do caso de ouro uma âncora e não uma descrição completa
da resposta.

`comparar` materializa os casos em tupla antes de avaliar os dois lados. Sem isso, um
iterador seria consumido na primeira avaliação e a segunda mediria zero caso, produzindo
deriva falsa com sinal negativo — um defeito que passaria por resultado plausível.

## Ordem de construção e dependências

A ordem correta é contrato, registro, avaliador, porque o grafo de dependência é uma árvore
com raiz no contrato. Os módulos usam apenas a biblioteca padrão: `hashlib`, `re`,
`dataclasses`, `enum` e `collections.abc`. Não há dependência externa e não há configuração;
um projeto que precise apenas do contrato tipado pode copiar um arquivo.
