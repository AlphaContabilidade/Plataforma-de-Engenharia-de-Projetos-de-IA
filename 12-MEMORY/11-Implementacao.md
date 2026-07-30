---
volume: "12"
volume_nome: MEMORY
tipo: ENGINE
secao: 11-Implementacao
status: PRONTO
atualizado_em: 2026-07-30
---

# Implementação

Os três módulos existem como código executável com teste, e é esse código que esta seção
descreve. As citações abaixo são verificadas pelo gate estrutural: o validador confere que o
arquivo citado existe e que existe o teste correspondente em `tests/test_<arquivo>.py`.
Documentação que cita código inexistente reprova.

<!-- exemplo: exemplos/12-memory/memoria_observada.py -->
<!-- exemplo: exemplos/12-memory/contaminacao.py -->
<!-- exemplo: exemplos/12-memory/precedencia.py -->

## Passo 1: o armazém

O módulo do armazém tem uma decisão estrutural na primeira função útil: a validação da chave
é uma função só, `_chave_valida`, chamada **nos dois lados** — no construtor de `Entrada` e
em `MemoriaObservada.entradas`. Centralizar não é elegância, é correção: se o registro
normalizasse a borda e a consulta não, gravar com espaço e consultar sem espaço alcançariam
baldes diferentes, cada um com metade das observações e nenhum com dominância. O erro
resultante seria silencioso e teria a forma mais enganosa possível — pendência humana em uma
chave que tem evidência de sobra.

A validação da entrada acontece em `__post_init__`, ou seja, na construção. A normalização
usa `object.__setattr__`, que é o caminho previsto para ajustar campo de dataclass congelada
dentro do próprio construtor, e a mensagem de `ChaveInvalida` explica por que a chave importa
em vez de apenas dizer que está inválida — o diagnóstico cabe na exceção.

O campo `decisao` passa pela função irmã `_decisao_valida`, que compartilha com a da chave o
mesmo núcleo de borda, `_sem_borda`, e levanta a própria exceção, `DecisaoInvalida`. Duas
funções e duas exceções em vez de uma genérica com nome de campo: o `except` de quem chama
consegue distinguir os dois defeitos sem inspecionar mensagem, e mensagem de erro não é
interface. `evidencia` deliberadamente não recebe esse tratamento — ela não entra em contagem
nenhuma, e evidência vazia é ausência de diagnóstico, não erro de programa.

As duas funções puras, `contagem_de` e `dominancia_de`, existem para serem reusadas pelos
outros dois módulos em vez de recontadas. `contagem_de` devolve um dicionário ordenado por
contagem decrescente com desempate alfabético, e essa ordem é o que torna a dominante de um
empate determinística. `dominancia_de` lê o primeiro item do dicionário já ordenado, o que
elimina uma segunda passada, e devolve a fração sem arredondar.

## Passo 2: a guarda

`filtrar_contaminacao` é a função mais curta do componente e a mais difícil de escrever
corretamente, porque a tentação é adicionar um parâmetro. Ela percorre uma vez, escolhe o
destino de cada entrada por identidade de origem e devolve duas tuplas. Não há limiar, não há
exceção e não há modo permissivo. A ausência de parâmetro é a implementação da regra R1 de
[`07-Regras.md`](07-Regras.md): um botão de tolerância ao eco seria acionado no primeiro dia
em que a fila de pendências incomodasse.

`contradicoes` agrupa por chave em um dicionário, e o recorte por origem acontece **antes** de
calcular a dominante — só entradas `OBSERVADO` entram na contagem. Essa ordem é a diferença
entre detectar e não detectar: no defeito real, **cinco** escritas do próprio agente concordando
com a base congelada apontariam a dominância para o lado da base, e a contradição desapareceria.
Cinco é o número do cenário reproduzido em `test_eco_nao_silencia_a_contradicao` e citado em
[`13-Testes.md`](13-Testes.md); não confundir com o exemplo sintético do passo 2 de
[`12-Exemplos.md`](12-Exemplos.md), que usa nove escritas para inverter uma amostra maior.
A saída é ordenada por chave, data de congelamento e decisão congelada, de modo que dois
relatórios da mesma memória são idênticos byte a byte — relatório instável perde credibilidade
antes de perder correção.

## Passo 3: a regra de precedência

`resolver` tem quatro etapas em ordem fixa, e a ordem é a parte que não se pode trocar:
descartar o eco, expirar o que passou da janela, procurar contradição, aplicar a precedência.
Procurar contradição antes de descartar o eco deixaria o agente silenciar a própria
contradição. Expirar depois de procurar contradição faria o relatório citar documento que a
resolução já não usa.

Duas funções internas concentram o que seria repetição. `descarte` monta o sufixo que informa
o que ficou fora da deliberação, e ele é anexado a **toda** justificativa — inclusive às que
decidem, porque um veredicto alto sobre dez observações vigentes ao lado de nove entradas
descartadas por contaminação, que é exatamente o passo 2 de
[`12-Exemplos.md`](12-Exemplos.md), é uma informação que quem lê precisa ter. `veredicto` é o único ponto de construção do resultado, e
é ali que o rebaixamento por contradição acontece uma vez, para os três caminhos que decidem.
Ter um construtor único é o que garante que nenhum retorno esqueça de anexar as contradições.

O laço sobre `PRECEDENCIA` tem a propriedade que dá nome à regra R5: cada iteração começa
filtrando as candidatas daquela origem, e **se houver candidatas, a iteração retorna** — com
decisão ou sem. O `continue` só é alcançado quando a origem está ausente. É essa forma que
impede a cascata: a base congelada nunca é consultada quando existe observação vigente, nem
que a observação não tenha decidido.

`_mais_recente` resolve empate de data pela última registrada, usando o índice como segundo
critério, porque `max` devolve o primeiro máximo e a semântica desejada é a oposta: entre duas
decisões humanas do mesmo dia, a que vale é a mais nova.

## Ordem de construção e dependências

A ordem correta é armazém, guarda, precedência, porque o grafo é uma cadeia com raiz no
armazém. Os módulos usam apenas a biblioteca padrão: `dataclasses`, `datetime`, `enum` e
`collections.abc`. Não há dependência externa, não há estado em disco e não há configuração —
um projeto que precise apenas do registro com procedência copia um arquivo. O
[`conftest.py`](../exemplos/12-memory/conftest.py) do diretório de exemplos existe por um
motivo de coleta de teste, explicado no próprio arquivo, e não faz parte do componente.
