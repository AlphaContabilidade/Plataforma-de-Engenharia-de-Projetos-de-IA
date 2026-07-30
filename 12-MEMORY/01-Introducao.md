---
volume: "12"
volume_nome: MEMORY
tipo: ENGINE
secao: 01-Introducao
status: PRONTO
atualizado_em: 2026-07-30
---

# Introdução

Memória, num sistema com agentes, é o componente que responde a uma pergunta só: **o
que já foi decidido para este caso, por quem, e com que evidência?** Onde não existe
memória com essa forma, a resposta é montada na hora a partir do que estiver mais perto
— um arquivo de base curada, uma consulta ao sistema de registro, o resultado de uma
busca textual — e a primeira fonte que responde ganha. Ganhar por ordem de consulta não
é uma regra de decisão; é o efeito colateral da ordem em que as linhas de código foram
escritas.

Este volume documenta o armazém de decisões observadas, a guarda que separa evidência de
eco e a regra de precedência entre origens. Ele foi extraído de um sistema em produção que roda
diariamente e escreve em sistema de terceiros, onde classificar errado custa dinheiro. Os
três módulos generalizam o que aquele sistema aprendeu à força, e cada
um existe para tornar impossível um defeito que já aconteceu.

## Os três defeitos que motivaram o componente

O primeiro é a **contradição silenciosa**. Uma base de classificação curada e congelada
numa data passada contradizia o histórico do que havia sido de fato observado em quatro
de quatro itens conferidos. Nada no sistema sinalizava a discordância. Quem consultasse a
base primeiro obtinha uma resposta, quem consultasse o histórico primeiro obtinha outra,
e as duas se apresentavam com a mesma cara — sem marca de procedência, sem data, sem
contagem. A contradição existia havia semanas e foi encontrada por conferência manual,
não por sinal automático.

O segundo é o **eco da própria escrita**. A automação classificava, escrevia no sistema,
e a base de histórico era regenerada depois lendo o próprio sistema — inclusive as linhas
que a automação acabara de gravar. Na rodada seguinte, ela lia a própria escrita como se
fosse observação independente, encontrava concordância alta e se autoconfirmava. Não
existe limiar de dominância que proteja contra isso: o número sobe porque a amostra é o
próprio eco. Uma decisão errada fica mais confiante a cada rodada, e o sinal de erro
desaparece exatamente no momento em que o erro se consolida.

O terceiro é a **evidência que não decide sendo tratada como se decidisse**. A regra do
operador é explícita: se a evidência não decide, é pendência humana, e classificar só
para o saldo fechar é inventar. No código, porém, o classificador devolvia o mesmo valor
vazio para dois estados que são diferentes — "não há evidência alguma" e "há evidência
que não basta" — e o chamador não tinha como distinguir um do outro nem como saber por
quê. Entre esse valor ambíguo e um palpite rotulado como confiança baixa havia um passo.

## O que este volume entrega

Entrega três contratos com implementação executável e teste, descritos em
[`08-Modelos.md`](08-Modelos.md) e [`11-Implementacao.md`](11-Implementacao.md): um
armazém que grava a procedência de cada decisão, uma guarda que descarta o eco e
**reporta** a contradição em vez de resolvê-la, e uma regra de precedência cujo resultado
indeciso é de primeira classe, com justificativa numérica. Entrega também a fronteira: o
que pertence ao volume vizinho está declarado em [`03-Escopo.md`](03-Escopo.md).

## Para quem é

Para quem escreve agente que decide repetidamente sobre casos recorrentes e cujo erro
tem custo — dinheiro, retrabalho ou confiança. Um agente que responde uma pergunta e
esquece não tem o problema que este volume resolve. O componente começa a pagar no dia em
que o agente passa a consultar o que ele mesmo produziu.
