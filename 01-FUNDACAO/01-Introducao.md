---
volume: "01"
volume_nome: FUNDACAO
tipo: GOVERNANCA
secao: 01-Introducao
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Introdução

Uma equipe entrega uma funcionalidade de IA. Seis semanas depois ninguém sabe dizer por que o prompt
tem aquela frase no meio, se o número que está no README foi medido alguma vez, nem o que precisaria
ser verdade para a coisa estar errada. Ninguém mentiu. Ninguém foi negligente. O que faltou não foi
esforço nem talento: faltou que alguma afirmação pudesse ser conferida por quem não estava lá.

Esse é o problema que este volume trata, e ele não é sobre modelos. Trocar de modelo não resolve, e
nem sequer melhora — modelo melhor produz afirmação plausível mais rápido, e afirmação plausível não
conferível é exatamente o insumo do problema. O que separa engenharia de IA de experimentação com IA
não é a qualidade do modelo. É se existe um caminho, escrito e executável, entre o que se afirma e o
que se pode verificar.

A distinção tem consequência prática imediata. Experimentação é legítima e necessária: alguém tenta,
observa, aprende. O que a experimentação **não** produz é um artefato que outra pessoa possa herdar.
Um caderno de experimentos entregue como sistema é um sistema cuja manutenção exige adivinhar a
intenção de quem saiu da empresa. Engenharia é o que se faz depois: transformar o que funcionou em
algo que continua funcionando quando quem fez não está mais na sala.

Este volume estabelece a constituição do acervo — os princípios que todos os outros quarenta e um
volumes obedecem — e, mais importante, a **matriz de controles** que liga cada princípio a uma
verificação que roda. Princípio sem controle é preferência declarada, e preferência declarada não
sobrevive ao primeiro prazo apertado. A diferença entre esta plataforma e um manual de boas intenções
está inteira nessa ligação: cada linha da matriz nomeia o princípio, a verificação, quem a executa e
o que acontece quando ela reprova.

Nada aqui é aspiracional. Os defeitos discutidos em [`12-Exemplos.md`](12-Exemplos.md) aconteceram
neste acervo, foram corrigidos, e três deles passariam por qualquer revisão humana atenta — o que é
justamente o argumento a favor de verificação executável.
