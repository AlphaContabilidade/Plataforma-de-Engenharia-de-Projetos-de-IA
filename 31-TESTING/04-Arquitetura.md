---
volume: "31"
volume_nome: TESTING
tipo: PROCESSO
secao: 04-Arquitetura
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Arquitetura

Um teste tem quatro partes, e a segunda é a que quase nunca é escrita.

## As quatro partes

**1. O arranjo.** O estado de entrada, construído explicitamente. Estado que vem de fora — arquivo,
banco, variável de ambiente, hora atual — torna o teste dependente de algo que ninguém controla, e a
falha resultante aparece como intermitência, que é a forma mais cara de defeito de teste.

**2. O defeito que ele pega.** Uma frase, escrita, dizendo o que quebraria se este teste não
existisse. Não é comentário decorativo: é o que permite decidir, meses depois, se o teste ainda faz
sentido ou se virou peso morto. Um teste sem essa frase é impossível de aposentar com segurança, e
por isso as suítes só crescem.

**3. A ação.** O que se executa. Uma coisa por teste — teste que exercita três comportamentos falha
sem dizer qual dos três.

**4. A asserção.** O que se afirma. E é aqui que mora a distinção que carrega este volume.

## Asserção positiva e asserção negativa

A asserção positiva verifica que o resultado contém o que deveria. A negativa verifica que **não**
contém o que não deveria. A segunda é quase sempre a que importa, porque a primeira passaria também
numa implementação que devolvesse tudo.

Este acervo tem o exemplo. Um filtro que recebe "aparelho de mão" deve trazer as lacunas de rede
ausente e loja de aplicativos. Verificar isso é a parte fácil. O teste que decide é o que verifica
que ele **não** traz nenhuma lacuna de programa instalado nem de navegador — porque um filtro
quebrado que ignorasse o parâmetro e devolvesse o catálogo inteiro passaria na positiva.

## A camada probabilística

Quando existe chamada a modelo, ela fica atrás de uma interface pequena que o teste substitui,
conforme o volume [`02-CORE`](../02-CORE/04-Arquitetura.md). O que se testa é o que está em volta: a
montagem do contexto, por igualdade byte a byte, e a fronteira de saída, alimentada com resposta
malformada, com valor fora do domínio e com decisão não autorizada.

Testar contra o provedor real é teste de integração: roda em outro lugar, em outra frequência, e não
faz parte da suíte que precisa rodar a cada mudança.
