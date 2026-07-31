---
volume: "01"
volume_nome: FUNDACAO
tipo: GOVERNANCA
secao: 08-Modelos
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Modelos

Três modelos de dado sustentam a matriz de controles. Estão descritos como estrutura, não como
implementação de uma linguagem, porque volumes diferentes os realizam de formas diferentes.

## `Origem` — procedência de uma evidência

Enumeração fechada. Fechada é a característica que importa: origem livre vira campo de texto, e campo
de texto vira "várias pessoas escreveram a mesma coisa de seis jeitos".

| Valor | Significa | Confiável para decidir sozinho |
|---|---|---|
| `RESPONDIDO` | uma pessoa respondeu diretamente | sim |
| `DECIDIDO_POR_HUMANO` | alguém escolheu, sabendo que escolhia | sim, e vence as outras |
| `MEDIDO` | saiu de execução, com comando registrado | sim |
| `BASE_CONGELADA` | veio de base externa numa data | sim, com a data junto |
| `INFERIDO` | um agente deduziu, com o trecho que produziu a dedução | **não**, até confirmação |
| `PADRAO_ASSUMIDO` | ninguém decidiu; adotou-se o mais provável | **não**, e numa entrega é defeito |

A precedência entre origens é `DECIDIDO_POR_HUMANO` > `MEDIDO` > `BASE_CONGELADA`. O que uma pessoa
decidiu conscientemente vence a medição porque a medição responde "o que é" e a decisão responde "o
que queremos" — e é comum querer diferente do que é.

## `Controle` — uma linha da matriz

Registro com seis campos: identificador estável (`C1`, `C2`…), princípio que ele protege, descrição
da verificação, se é executável, comando quando é, e o que acontece ao reprovar. O identificador
**nunca muda de significado**: relatório de auditoria antigo cita `C6`, e renumerar controle
transforma histórico em ficção.

O campo `executavel` é booleano e não admite "parcialmente". Um controle meio automático é dois
controles: a parte que roda e a parte que não roda, e separá-los é o que impede a segunda de sumir
atrás da primeira.

## `Veredicto` — resultado de uma auditoria

Nota por seção, média, lista de achados com gravidade, e um dos três resultados: aprovado,
aprovado com ressalvas, reprovado. **"Indeciso" é resultado de primeira classe** e não uma forma
educada de reprovar: quando a evidência disponível não decide, forçar um veredicto produz um número
inventado com aparência de medição, que é o pior desfecho possível para um instrumento cuja função é
justamente detectar números inventados.
