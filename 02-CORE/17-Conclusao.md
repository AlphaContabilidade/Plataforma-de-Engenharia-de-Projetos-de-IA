---
volume: "02"
volume_nome: CORE
tipo: ARQUITETURA
secao: 17-Conclusao
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Conclusão

A tese do volume cabe numa frase: **a decisão de arquitetura que governa todas as outras num sistema
de IA é onde fica a fronteira entre o determinístico e o probabilístico** — e, quando ninguém a
desenha, ela se forma em toda parte, que é o pior lugar.

As seis partes, as oito regras e os sete anti-padrões são consequências dessa frase. A regra que
carrega o volume é a N2: nada além da fronteira de saída recebe texto livre do modelo. Ela é fácil de
enunciar, barata de obedecer no começo e quase impossível de recuperar depois, porque cada chamador
novo que decide sobre texto cru torna a reversão mais cara. É por isso que é regra de arquitetura e
não de estilo.

O que ficou demonstrado por código, e não por argumento, está em [`12-Exemplos.md`](12-Exemplos.md):
uma função de decisão pura torna uma interface HTTP inteira testável sem socket; uma fronteira com
razão escrita recusa entrada incompleta em vez de assumir valor; e uma alternativa determinística com
procedência entrega o trecho que produziu cada inferência, de graça e instantaneamente.

O terceiro exemplo carrega a lição mais desconfortável do volume, e ela contraria a intuição de um
projeto de IA: **menos chamadas ao modelo costuma ser melhor arquitetura, não menos ambição.** A
alternativa determinística falha por falta de dado, e falta de dado se corrige acrescentando dado. A
variação de um modelo não se corrige — administra-se. Trocar uma coisa administrável por uma coisa
corrigível é quase sempre o negócio certo.
