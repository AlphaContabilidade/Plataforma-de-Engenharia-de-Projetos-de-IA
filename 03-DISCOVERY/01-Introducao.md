---
volume: "03"
volume_nome: DISCOVERY
tipo: PROCESSO
secao: 01-Introducao
status: PRONTO
atualizado_em: 2026-07-31
---

# Introdução

Toda construção de software começa com uma frase curta e insuficiente. "Quero um app para a
minha loja." "Preciso organizar o estoque." "Dá para automatizar aquele relatório?" A frase
não é preguiça de quem pede: ela é honesta sobre o que a pessoa sabe. Ela sabe o que dói. Ela
não sabe — e não tem por que saber — que a resposta dela sobre onde o programa roda decide se
existe pergunta de loja de aplicativos ou de navegador, nem que a palavra "pagamento" abre uma
pergunta sobre o que acontece quando a mesma compra é cobrada duas vezes.

Este volume trata do trecho entre essa frase e uma especificação precisa o suficiente para
construir. O trecho tem dois modos de dar errado, e os dois são comuns. No primeiro, alguém
constrói direto da frase, preenchendo as lacunas com o que parecia razoável, e a divergência
aparece na entrega, quando o custo de corrigir é o de refazer. No segundo, alguém manda um
formulário de quarenta perguntas, e ele é abandonado no décimo quinto item — sobra uma conversa
interrompida, sem registro de onde parou, com a pessoa mais impaciente do que começou.

O motor deste volume existe porque os dois erros têm a mesma raiz: **tratar a especificação
como um documento a preencher, em vez de um conjunto de lacunas a fechar por ordem de valor.**
Fechar por ordem de valor muda três coisas de lugar. A pergunta seguinte passa a ser a que
resolve mais incerteza, e não a próxima da lista. A pergunta que o contexto tornou irrelevante
deixa de existir, em vez de aparecer desabilitada. E a pergunta que vale pouco não é feita: ela
sai na especificação como decisão aberta, com o texto original, para quem for construir decidir
com o olho aberto.

## Por que ele merece volume separado

Há um segundo motivo, e ele é o que separa este volume do `04-REQUIREMENTS`. Descobrir e
registrar são atividades diferentes. Registrar requisito pressupõe que já se sabe o que
registrar; descobrir é decidir o que perguntar quando ainda não se sabe. O instrumento de
descoberta é um grafo de decisão sobre incerteza, e ele tem uma métrica própria — número de
perguntas até a especificação fechar — que não é métrica de rastreabilidade nem de cobertura de
requisito.

O terceiro motivo é o princípio que o volume `12-MEMORY` já paga em código: **procedência.**
Aqui ela reaparece com outro nome e a mesma função. Uma inferência razoável tirada da frase
inicial — "app" provavelmente significa aparelho de mão — precisa viajar marcada como
inferência, com o trecho que a produziu, e precisa ser confirmada antes de valer. Sem a marca,
ela chega ao fim indistinguível de uma resposta, e quem for construir trata suposição como
requisito. No passo a passo medido em [`12-Exemplos.md`](12-Exemplos.md), essa inferência
específica estava **errada**, e aceitá-la em silêncio teria produzido quatro perguntas de
aparelho de mão que não se aplicavam e deixado de fazer três de navegador: sete das quinze
perguntas erradas, sem que nada no processo apitasse.

O que este volume entrega não é um roteiro de entrevista. É um motor executável em quatro
módulos, com setenta e três testes, e a defesa de cinco princípios que o código obedece de
forma verificável — porque princípio que o código não obedece é preferência declarada, e
preferência declarada não sobrevive ao primeiro prazo apertado.
