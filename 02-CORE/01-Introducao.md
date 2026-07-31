---
volume: "02"
volume_nome: CORE
tipo: ARQUITETURA
secao: 01-Introducao
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Introdução

Todo sistema que usa um modelo de linguagem tem uma decisão de arquitetura que determina todas as
outras, e quase nunca ela é tomada de propósito: **onde fica a fronteira entre a parte determinística
e a parte probabilística.**

Quando ninguém desenha essa fronteira, ela se forma sozinha — e se forma no pior lugar possível, que
é em toda parte. O texto livre que o modelo devolveu vira uma variável, essa variável entra num `if`,
o `if` decide se um pedido é aprovado, e três meses depois ninguém consegue escrever um teste para
aquela função, porque a entrada dela é "o que o modelo costuma responder". O sistema não está errado;
ele está **inverificável**, que é uma condição pior, porque errado se conserta.

O sintoma clássico aparece na conversa sobre testes. Alguém pergunta como testar aquele trecho e a
resposta é "não dá, depende do modelo". Essa frase quase sempre está errada. O que não dá para testar
de forma determinística é a chamada ao modelo — uma linha. Tudo o que vem antes, o preparo do
contexto, e tudo o que vem depois, a interpretação da resposta, é código comum e é testável. Quando
"não dá para testar" se espalha por um módulo inteiro, o que aconteceu foi vazamento: o
não-determinismo escapou da linha onde deveria estar confinado.

Este volume trata da anatomia mínima de um sistema de IA — seis partes — e da regra estrutural que as
organiza: **o não-determinismo não passa da fronteira de saída**. Antes dela, texto. Depois dela,
dado com tipo, que o resto do sistema trata como trataria qualquer outro dado de origem externa: com
validação, com caso de erro e com teste.

A consequência prática é agradável e conferível. Num sistema com a fronteira desenhada, quase todo o
código roda com o provedor desligado. Num sistema sem ela, a resposta honesta à pergunta "quanto do
seu código você consegue testar sem rede?" é "não sei", e não saber já é o diagnóstico.
