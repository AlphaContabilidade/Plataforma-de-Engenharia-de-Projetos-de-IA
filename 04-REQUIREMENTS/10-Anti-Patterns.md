---
volume: "04"
volume_nome: REQUIREMENTS
tipo: PROCESSO
secao: 10-Anti-Patterns
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Anti-Patterns

**D1 — Requisito-desejo.** "Rápido", "intuitivo", "confiável", "escalável". Não falsificável, logo
não testável, logo não cobrado — mas contado no escopo. *Sintoma:* na entrega, cliente e equipe
discordam sobre se está pronto e nenhum dos dois consegue provar. *Contramedida:* Q1 e o teste do
contraexemplo.

**D2 — Lacuna preenchida com o provável.** A descoberta não obteve resposta e alguém escreveu o valor
mais razoável. É o A6 do volume `01` aplicado a requisitos, e é pior aqui, porque um requisito tem
autoridade de combinado. *Contramedida:* Q2 e a porta de origem no fluxo.

**D3 — Requisito que descreve a solução.** "O sistema deve usar uma fila de mensagens." Isso é
decisão de projeto disfarçada, e congela implementação dentro do contrato com o cliente — depois
qualquer refatoração parece quebra de acordo. *Contramedida:* a pergunta do fluxo, comportamento ou
construção.

**D4 — Rastro só para trás.** O requisito diz de onde veio e ninguém sabe quem o confere. É o modo de
falha mais comum, porque a metade de trás dá a sensação de rastreabilidade completa.
*Contramedida:* Q3, e a métrica de requisitos sem verificação.

**D5 — Identificador reciclado.** Um requisito é retirado e o número volta para outro. Todo registro
antigo passa a apontar para a coisa errada, silenciosamente. *Contramedida:* Q4.

**D6 — Requisito com prazo dentro.** "Até março, o relatório deve...". Quando o plano muda, o
requisito parece descumprido sem que nada de comportamento tenha mudado, e a lista perde
credibilidade. *Contramedida:* Q5.

**D7 — Ajuste silencioso na falha.** A verificação falhou, alguém "esclareceu" o enunciado e ele
passou a descrever o que o sistema faz. O conjunto vira espelho da implementação, e um espelho não
verifica nada. *Contramedida:* Q7 e Q8 — mudar é permitido, mudar sem registro e sem razão não é.
