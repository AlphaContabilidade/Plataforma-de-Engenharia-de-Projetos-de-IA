---
volume: "03"
volume_nome: DISCOVERY
tipo: PROCESSO
secao: 10-Anti-Patterns
status: PRONTO
atualizado_em: 2026-07-30
---

# Anti-patterns

Seis padrões, cada um com o custo concreto de praticá-lo. Os quatro primeiros são os que este
volume existe para impedir; os dois últimos são os que aparecem quando alguém tenta consertar os
quatro primeiros do jeito errado.

## A1 — O formulário fixo de quarenta perguntas

**O que é.** Uma lista única, igual para todo caso, apresentada de uma vez ou em páginas. Quem
recebe responde as primeiras com atenção, as do meio por obrigação e as últimas com o que der.

**O custo, em número medido.** O catálogo deste volume tem trinta e sete lacunas. No caso do passo a
passo em [`12-Exemplos.md`](12-Exemplos.md), apenas quinze estavam ativas, e o motor fez catorze
perguntas. As vinte e duas restantes não são perguntas mal colocadas: são perguntas sem sentido
naquele caso — loja de aplicativos para algo que roda em navegador, prazo de guarda de dado de saúde
para uma loja de bairro. O formulário fixo cobra vinte e duas respostas inventadas e, pior, gasta a
paciência de que a pergunta boa precisa.

**O sinal de que está acontecendo.** A pessoa começa a escrever "não se aplica" e depois só deixa em
branco. Ou o instrumento tem trinta campos e vinte desabilitados — que é a versão educada do mesmo
erro, com a agravante de ensinar que o instrumento não entende o caso.

## A2 — A inferência silenciosa

**O que é.** O programa conclui algo do texto inicial e passa a agir como se aquilo tivesse sido
dito. Não mente: simplesmente não distingue. A conclusão entra na especificação com a mesma
autoridade de uma resposta.

**O custo, em número medido.** Na frase do passo a passo, a palavra "app" produz uma inferência de
aparelho de mão com confiança **baixa**, e ela está errada — a pessoa quer uma página que os
clientes abram no navegador. Aceitá-la em silêncio produz catorze das quinze perguntas por um
caminho errado: quatro perguntas de aparelho de mão que não se aplicam — rede ausente, loja,
permissão de dispositivo, notificação — e três de navegador que nunca são feitas. Sete das quinze
perguntas erradas, e nada no processo apita.

**Por que é sedutor.** Porque a inferência costuma estar certa, e cada acerto reforça a prática. O
que a torna inutilizável não é errar: é não se saber. Uma conclusão provavelmente correta e não
verificada é uma aposta com a aparência de requisito.

## A3 — O valor assumido apresentado como decidido

**O que é.** A lacuna que ninguém respondeu sai na especificação preenchida com o valor mais
provável, sem marca. É o anti-pattern A2 na saída em vez da entrada, e é mais grave porque a
especificação é o documento que alguém vai construir.

**O custo.** Quem constrói não tem como distinguir o que foi decidido do que foi preenchido, e por
isso trata tudo como decidido. A divergência aparece na entrega. Pior: quando aparece, a discussão é
sobre quem errou, e não sobre a decisão — porque o documento afirma que a decisão existiu.

**Como o código impede.** `decisoes_abertas` carrega a `Lacuna` inteira e o markdown a imprime com a
pergunta original e o motivo. `Origem.PADRAO_ASSUMIDO` existe nomeado para poder ser proibido, e um
teste verifica que a palavra não aparece no markdown do caso incompleto. Escrever `Nenhuma` numa
seção vazia é uma afirmação; omitir a seção não é nada — e omitir é o que produz este anti-pattern
por descuido.

## A4 — A pergunta cuja resposta não muda nada

**O que é.** A pergunta que existe porque estava no roteiro, ou porque alguém achou interessante
saber. Nenhuma resposta dela altera o que será construído.

**O custo.** Ela é indistinguível de uma pergunta boa para quem responde, e por isso consome o mesmo
turno e a mesma paciência. O custo real não é o turno: é que ela ensina a pessoa que as perguntas do
instrumento podem ser respondidas de qualquer jeito — e essa lição se aplica retroativamente às
perguntas que importavam.

**Como se detecta.** Escrevendo o campo `porque`. Se o motivo escrito não consegue nomear o que muda
na construção, a lacuna é esta. O segundo detector é a pergunta em produção: quando a pessoa
pergunta "por que você quer saber isso?" e o motivo declarado não convence quem conhece o próprio
problema, o defeito é do catálogo, e a correção é rebaixar o peso ou remover a lacuna — no arquivo,
com o teste acompanhando.

## A5 — Marcar pendência com `TODO` em vez de declarar decisão aberta

**O que é.** A tentativa de resolver A3 escrevendo `TBD` ou `FIXME` no lugar do valor. Parece
honesto e não é: o marcador não diz qual era a pergunta, não diz por que ela importa e não diz quem
decide.

**O custo.** Ele passa por revisão porque parece um recado temporário, e recado temporário sobrevive
a entregas. A alternativa é a decisão aberta com a pergunta inteira e o motivo, que é acionável para
quem lê. É por isso que a plataforma proíbe esses marcadores na prosa dos volumes e dá lugar próprio
para pendência de verdade.

## A6 — Afrouxar o limiar para a especificação fechar

**O que é.** Baixar `peso_minimo` — ou pior, criar um parâmetro que dispensa a lacuna universal —
para que `completa` devolva `True` no dia do prazo.

**O custo.** A métrica melhora imediatamente e o efeito colateral não aparece em painel nenhum,
porque medir decisão ruim exige conferência que ninguém faz quando a especificação chegou fechada. É
o mesmo mecanismo do anti-pattern equivalente no volume 12: o limiar afrouxável é o limiar que será
afrouxado. Por isso `peso_minimo` é parâmetro e a condição de `completa` **não é** — perguntar menos
é uma escolha de economia, declarar-se completa sem estar é uma afirmação falsa.
