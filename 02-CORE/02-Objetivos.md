---
volume: "02"
volume_nome: CORE
tipo: ARQUITETURA
secao: 02-Objetivos
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Objetivos

Quatro objetivos. Cada um com a verificação junto, porque objetivo de arquitetura sem forma de
conferir vira preferência estética na primeira discussão de prazo.

**1. Tornar a fronteira de saída explícita e única.** Existe um ponto no código, nomeável, onde texto
livre vira dado com tipo. *Verificação:* é possível apontar o arquivo e a função. Se a resposta for
"em vários lugares", o objetivo falhou, e falhou de um jeito que só piora — cada lugar novo é mais
barato de acrescentar que o primeiro.

**2. Manter o núcleo testável sem rede, sem chave e sem relógio.** Toda a lógica que decide alguma
coisa roda em memória, com entrada sintética. *Verificação:* a suíte passa com a rede desligada. Este
acervo obedece: os exemplos dos volumes `03`, `07` e `12` não tocam rede, disco nem relógio, e a
ausência de relógio é o item que mais se esquece — comportamento que muda conforme o dia em que roda
não se reproduz.

**3. Dar à saída do modelo o mesmo tratamento de qualquer entrada não confiável.** Validação de forma,
caso de erro escrito, e comportamento definido para quando a resposta não serve. *Verificação:* existe
teste que alimenta o parser com resposta malformada e verifica o que acontece. A ausência desse teste
é o defeito mais comum desta categoria.

**4. Fazer o custo do não-determinismo aparecer no desenho.** Cada chamada ao modelo é uma aposta com
latência, preço e chance de resposta inútil. *Verificação:* o diagrama de sequência em
[`05-Diagramas.md`](05-Diagramas.md) mostra quantas chamadas um caminho faz, e o número é uma decisão
de arquitetura, não um acidente de implementação.

O que **não** é objetivo deste volume: escolher modelo, escrever prompt, orquestrar agentes. São três
assuntos de vizinhos, e a fronteira está em [`03-Escopo.md`](03-Escopo.md).
