---
volume: "03"
volume_nome: DISCOVERY
tipo: PROCESSO
secao: 14-Metricas
status: PRONTO
atualizado_em: 2026-07-30
---

# Métricas

Cada métrica abaixo tem definição operacional, unidade e origem do dado. Métrica sem unidade não
compara e métrica sem origem não audita. Os números citados nesta seção vêm da execução do passo a
passo de [`12-Exemplos.md`](12-Exemplos.md) — são ilustração de método medida, e não referência de
mercado.

| Métrica | Definição operacional | Unidade | Origem |
|---|---|---|---|
| Perguntas até fechar | número de chamadas de `responder` desde o início da entrevista até `Especificacao.completa` devolver `True` | contagem absoluta | instrumentação de quem chama, contando as chamadas |
| Fração de lacunas resolvidas por inferência confirmada | número de palpites confirmados dividido pela soma de palpites confirmados e perguntas feitas | fração de 0 a 1 | contagem de `confirmar` e de `responder` |
| Fração de inferências recusadas | número de chamadas de `recusar` dividido pelo total de palpites produzidos na entrevista | fração de 0 a 1 | contagem de `recusar` e `len` da detecção inicial |
| Decisões abertas por especificação | `len(Especificacao.decisoes_abertas)` no momento em que a especificação é entregue | contagem absoluta | `Especificacao.decisoes_abertas` |
| Decisões abertas universais | quantas das decisões abertas têm `universal` verdadeiro | contagem absoluta | `Especificacao.decisoes_abertas` |
| Economia de relevância | uma menos o número de lacunas ativas dividido pelo tamanho do catálogo | fração de 0 a 1 | `len(entrevista.ativas())` e `len(CATALOGO)` |
| Palpites pendentes na entrega | `len(Especificacao.inferencias_pendentes)` no momento da entrega | contagem absoluta | `Especificacao.inferencias_pendentes` |

## Os valores medidos no caso do passo a passo

No caminho principal: catorze perguntas até fechar; dois palpites confirmados contra catorze
perguntas, o que dá fração de 2/16, ou 0,125; uma recusa em três palpites produzidos, ou seja 1/3
igual a 0,333; uma decisão aberta, nenhuma universal; quinze lacunas ativas de trinta e sete, o que
dá economia de relevância de 1 menos 15/37, ou 0,595; zero palpites pendentes na entrega.

O número que carrega o argumento do volume é a economia de relevância. Quase seis décimos do catálogo
nunca foi cogitado neste caso — não por escolha de economia, mas porque as perguntas não faziam
sentido. É uma métrica de relevância e não de eficiência, e ela **não** deve ser maximizada: economia
alta com decisões abertas universais significa que o motor não conseguiu destravar nada, e não que ele
foi eficiente. As duas se leem juntas.

## Fração de inferências recusadas: a única métrica que aponta para um arquivo

Esta é a métrica de qualidade da detecção, e ela é a mais útil das sete porque a ação que ela sugere é
específica. Recusa alta em um termo significa uma de duas coisas: ou o termo é ambíguo, e o lugar dele
é confiança baixa; ou está errado, e o lugar dele é fora da tabela. Nos dois casos a correção é uma
linha em `_TERMOS_PLATAFORMA` ou `_TERMOS_CONTEXTO`, com o teste acompanhando.

A leitura tem um limite honesto que vale escrever. Recusa igual a zero **não** significa detecção
perfeita: pode significar que ninguém está olhando os palpites antes de confirmar. Uma taxa de recusa
exatamente zero ao longo de muitas entrevistas é motivo de suspeita, não de tranquilidade, e a
verificação é olhar se a evidência está sendo mostrada junto do palpite. No caso medido a recusa foi de
um terço, e ela evitou quatro perguntas erradas — o valor da métrica não é a fração em si, é que ela
existe para que essa recusa seja contada em vez de esquecida.

## Perguntas até fechar: por que ela não deve ser minimizada

Baixar o número de perguntas é trivial: sobe-se `peso_minimo` e pronto. O efeito colateral — mais
decisões abertas chegando a quem constrói — não aparece em painel nenhum, porque medir decisão ruim
exige conferência que ninguém faz quando a especificação chegou fechada. É o anti-padrão A6 de
[`10-Anti-Patterns.md`](10-Anti-Patterns.md).

A leitura correta é o par com decisões abertas. No caso medido, catorze perguntas e uma decisão aberta
de peso três; com o limiar em um, quinze perguntas e zero decisões abertas. A pergunta operacional não
é qual dos dois é melhor, é quanto vale a décima quinta pergunta naquele domínio — e a resposta muda
com o custo de errar. Um motor que escolhesse esse ponto por conta própria estaria decidindo por todos
os domínios, e é por isso que o limiar é parâmetro e não constante.

## Fração resolvida por inferência: o teto realista

Um oitavo das decisões vindo de inferência confirmada parece pouco, e é — mas é o número correto para
o desenho atual, e vale dizer por quê. A detecção só infere plataforma e contexto, que são dois tipos
de informação entre trinta e sete lacunas. Ela nunca vai inferir "que problema isso resolve", porque
isso não está na frase inicial de ninguém. O que essa métrica mede, na prática, é quanto do
**destravamento** veio de graça: dois palpites confirmados destravaram cinco lacunas de contexto que
alguém teria de descobrir de outra forma. Quem quiser subi-la tem de aumentar o que a detecção cobre,
e aumentar o que a detecção cobre sem aumentar a taxa de recusa é o trabalho registrado em
[`16-Roadmap.md`](16-Roadmap.md).
