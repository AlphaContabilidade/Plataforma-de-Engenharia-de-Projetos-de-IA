---
volume: "02"
volume_nome: CORE
tipo: ARQUITETURA
secao: 09-Boas-Praticas
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Boas Práticas

**Imprima o contexto antes de trocar de modelo.** A maior parte das respostas ruins vem de contexto
montado errado — dado que não entrou, instrução duplicada, histórico truncado no meio de uma frase.
Trocar de modelo custa caro e muda o sintoma sem tocar na causa. Como a montagem é determinística
(regra N6), imprimir e olhar é barato.

**Escreva o contrato de saída antes do prompt.** Saber o que se quer de volta muda o que se escreve
no pedido, e a ordem inversa produz prompt que pede uma coisa e parser que espera outra.

**Teste a fronteira com resposta malformada antes de testar com resposta boa.** O caminho feliz é o
que se escreve sozinho; o caminho de erro é o que decide se o sistema estraga alguma coisa às três da
manhã. Este acervo tem o hábito: a interface web recusa corpo acima do teto **antes de alocar**,
porque o cabeçalho de tamanho é alegação do cliente.

**Isole a chamada atrás de uma interface pequena.** Uma função que recebe contexto e devolve texto,
ou levanta. Interface pequena é fácil de substituir no teste; interface grande arrasta o cliente do
fornecedor para dentro do domínio.

**Prefira a alternativa determinística quando ela resolve.** É a regra N8, e vale repetir porque é
contraintuitiva num projeto de IA. Menos chamadas ao modelo é melhor arquitetura, não menos ambição.

**Faça a função de decisão ser pura.** Neste repositório, `responder()` da interface web recebe
método, caminho e corpo e devolve uma tripla, sem tocar em socket — o manipulador HTTP só converte. É
o que permite testar a interface inteira sem porta livre e sem navegador.

**Trate indisponibilidade como caso normal.** O provedor cai. Um sistema cuja única resposta a isso é
uma exceção com o nome do fornecedor na tela não tem a parte 3 isolada.
