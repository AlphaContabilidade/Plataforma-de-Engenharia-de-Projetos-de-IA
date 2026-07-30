---
volume: "12"
volume_nome: MEMORY
tipo: ENGINE
secao: 09-Boas-Praticas
status: PRONTO
atualizado_em: 2026-07-30
---

# Boas práticas

As práticas abaixo são pares: cada uma tem o anti-padrão correspondente em
[`10-Anti-Patterns.md`](10-Anti-Patterns.md), com o mesmo identificador. O pareamento é
deliberado — recomendação isolada é fácil de concordar e difícil de aplicar, enquanto o par
mostra qual comportamento concreto está sendo trocado por qual.

## P1. Classifique a origem no ato do registro, e não depois

A procedência é conhecida no instante em que a entrada nasce, e nunca mais. Quem escreve o
adaptador da fonte sabe se aquele registro veio de terceiro, da base curada, de uma pessoa
ou da própria escrita do agente; quem lê a memória três semanas depois não sabe e não tem
como descobrir. Se a integração de uma fonte nova não deixa claro qual origem usar, isso é
uma pergunta a fazer antes de gravar, e não um detalhe a resolver com o valor mais provável.

## P2. Marque a escrita do agente na hora de escrever, não na hora de ler

O eco é criado quando o agente age, e é ali que ele é identificável sem ambiguidade. Se a
sua rotina escreve num sistema externo e depois relê aquele sistema, registre a própria
escrita como `ESCRITO_PELO_AGENTE` no mesmo passo em que a ação acontece — de preferência
com a mesma chave e a mesma data. Tentar identificar o eco depois, comparando texto ou
data, é adivinhação, e o erro dessa adivinhação é assimétrico: um eco não reconhecido se
autoconfirma para sempre.

## P3. Trate a contradição como item de trabalho, com prazo

A `Contradicao` é um relatório, e relatório sem dono acumula. A prática é ler
`n_observacoes` e `congelada_em`, decidir por qual dos dois lados investigar, e encaminhar:
base envelhecida vai para recuratoria da fonte, observação suspeita vai para conferência de
procedência. O fluxo está em [`06-Fluxogramas.md`](06-Fluxogramas.md). Contradição aberta há
muito tempo não é sinal de tolerância a ambiguidade — é sinal de que ninguém está olhando.

## P4. Prefira pendência a decisão fraca quando o erro custa

O veredicto indeciso existe para ser usado. Quando o custo de errar é maior que o custo de
esperar, o valor correto de `dominancia_minima` é alto e a taxa de indecisão sobe de
propósito. A conversa útil não é "como reduzir a indecisão" e sim "quanto custa cada erro
comparado a cada pendência", e essa conta é do domínio, não do componente. Ajustar o limiar
para baixo até a fila de pendências caber no dia é decidir por conveniência.

## P5. Escreva o texto de evidência pensando em quem vai triar

`evidencia` não entra em contagem alguma, então a tentação é deixá-la vazia. Ela é o que
permite que a triagem de uma contradição termine sem reexecutar nada. O conteúdo útil é o
que sustentou aquela decisão naquele momento — qual sinal foi visto, quem confirmou, qual
documento foi consultado. O conteúdo inútil é repetir a decisão em outras palavras.

## P6. Fixe a janela pelo prazo em que o domínio muda, e depois não mexa

`janela_dias` expressa uma hipótese sobre a velocidade com que o mundo muda para aquela
chave. Escolha o valor uma vez, com a razão escrita, e trate mudanças como mudança de
método: registre por que mudou e reprocesse. Ampliar a janela depois de ver um veredicto
que não agradou revive evidência antiga até a resposta virar, e o número resultante não
mede nada além da preferência de quem ampliou.

## P7. Registre a decisão humana na memória, não só no sistema de destino

Quando uma pessoa resolve uma pendência, essa decisão é a evidência mais forte que existe, e
perdê-la é caro duas vezes: a mesma chave volta como pendência na próxima rodada, e o
trabalho humano não acumula. Registrar como `DECIDIDO_POR_HUMANO` faz a precedência
funcionar e transforma cada intervenção em capital.

## P8. Consulte pelo resolvedor, não pelo armazém

`MemoriaObservada.dominancia` devolve número cru, com eco dentro. Ele existe para
diagnóstico e para o painel, não para decidir. Todo caminho de decisão passa por `resolver`,
que aplica descarte, janela, contradição e precedência na ordem correta. Um atalho que leia
o armazém direto reintroduz o defeito com aparência de otimização.
