---
volume: "31"
volume_nome: TESTING
tipo: PROCESSO
secao: 16-Roadmap
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Roadmap

**1. Registro de mutação por teste crítico.** Hoje a mutação é manual e o resultado vive na memória de
quem a fez. Um campo no próprio teste — uma linha dizendo o que foi mutado e que ficou vermelho —
transformaria a regra T2 em algo conferível por revisão, sem exigir ferramenta de mutação automática.
É a frente de maior valor por esforço.

**2. Contagem de intermitências.** Exige guardar o resultado de cada execução por teste, o que hoje
não é feito. Sem isso, a métrica de intermitência é impressão, e impressão sobre intermitência é
notoriamente ruim — o teste que falha uma vez em vinte parece confiável.

**3. Convenção que ligue teste a requisito.** O volume `04-REQUIREMENTS` exige rastro para frente e
não tem como conferi-lo. A forma mais simples é o identificador do requisito no nome ou num marcador
do teste, o que permitiria listar requisitos sem verificação automaticamente. É trabalho conjunto
dos dois volumes, e por isso está no roadmap dos dois.
