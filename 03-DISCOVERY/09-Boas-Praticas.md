---
volume: "03"
volume_nome: DISCOVERY
tipo: PROCESSO
secao: 09-Boas-Praticas
status: PRONTO
atualizado_em: 2026-07-30
---

# Boas práticas

Cada prática abaixo vem com a razão. Prática sem razão é superstição, e superstição em processo de
descoberta é caro porque ela se propaga: quem aprendeu a fazer sem saber por que faz ensina a
próxima pessoa a fazer sem saber por que.

## Escreva o motivo da pergunta antes de escrever a pergunta

O campo `porque` não é documentação: é o teste de existência da lacuna. Uma pergunta cujo motivo
não se consegue escrever em duas frases não sobrevive a uma revisão honesta, e é melhor descobrir
isso no arquivo do que na frente de quem está sendo entrevistado. A prática tem efeito colateral
útil: o motivo escrito antes tende a ser sobre o que muda na construção, enquanto o motivo escrito
depois tende a justificar a pergunta que já existe.

## Faça o peso significar valor informativo, e nada mais

Peso não é prioridade de projeto, não é esforço de implementação e não é importância do assunto
para o negócio. É quanta incerteza a resposta remove. A confusão mais comum é com esforço, e ela
inverte a ordem: a pergunta mais informativa costuma ser a mais barata de responder, e a mais cara
de implementar raramente é a mais incerta. Quando alguém propuser subir o peso de uma lacuna
porque "isso é muito importante", a pergunta de volta é quantas outras decisões mudam de acordo com
a resposta.

## Prefira destravamento genérico a caso especial por identificador

`Entrevista.responder` destrava plataforma e contexto testando se o valor da resposta corresponde a
um membro das enumerações. Não existe `if lacuna_id == "onde_roda"` em lugar nenhum. A razão é que
caso especial por identificador transforma o catálogo em código: a partir do primeiro, acrescentar
uma lacuna deixa de ser editar dados e passa a exigir leitura do controle para saber se aquele
identificador é especial.

## Deixe o denominador do progresso crescer

`progresso()` devolve um par em que o total **sobe** quando uma confirmação destrava um bloco novo.
No caso medido, ele foi de seis para onze quando dois contextos foram confirmados, e de onze para
catorze quando a plataforma entrou. A tentação é fixar o denominador no total do catálogo para a
barra andar sempre para frente; o preço seria uma barra que começa em zero de trinta e sete e nunca
chega perto do fim, medindo o catálogo em vez da conversa. Barra honesta que recua é melhor que
barra bonita que mente.

## Mostre a evidência junto com o palpite, sempre

Confirmar uma inferência sem ver o trecho que a produziu é confirmar por educação. A pessoa que lê
"o motor concluiu que é para aparelho de mão" tende a concordar; a que lê o trecho `Quero um app
para a minha` costuma corrigir — porque reconhece que disse "app" no sentido genérico. A recusa
medida no passo a passo aconteceu exatamente assim, e ela evitou quatro perguntas erradas.

## Trate "não se aplica" como resposta, não como lacuna aberta

Quando a pessoa diz que a pergunta não vale para o caso dela, isso é uma decisão e deve ser gravada
com `responder`. Deixar a lacuna aberta guardaria a mesma informação com o sinal errado: decisão
aberta é o que ninguém decidiu, e alguém decidiu. A distinção importa para quem lê a especificação
depois, porque decisão aberta é trabalho pendurado e "não se aplica" é trabalho encerrado.

## Revise o catálogo a partir da taxa de recusa, não da opinião

A fração de inferências recusadas mede a qualidade da tabela de termos, e é a única métrica do
motor que aponta para um arquivo específico. Termo com recusa alta ou é ambíguo — e o lugar dele é
confiança baixa — ou está errado, e o lugar dele é fora da tabela. Opinião sobre qual termo
"deveria" funcionar não tem como competir com esse número, e é bom que não tenha.
