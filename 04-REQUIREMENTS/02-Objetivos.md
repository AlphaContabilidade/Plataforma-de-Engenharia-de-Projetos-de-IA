---
volume: "04"
volume_nome: REQUIREMENTS
tipo: PROCESSO
secao: 02-Objetivos
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Objetivos

Quatro objetivos, cada um com a verificação junto.

**1. Que todo requisito seja falsificável.** Existe um fato observável que o torna falso, e esse fato
está escrito. *Verificação:* o teste do contraexemplo, descrito em [`07-Regras.md`](07-Regras.md) —
quem escreve o requisito escreve também o que veria se ele estivesse sendo descumprido. Se não
consegue, não é requisito.

**2. Que todo requisito tenha rastro para trás.** Aponta para a lacuna da descoberta que o originou, e
para a origem da resposta daquela lacuna. *Verificação:* seguir o rastro de um requisito qualquer até
a evidência leva a uma das seis origens do volume `01` — e chegar em `PADRAO_ASSUMIDO` é achado, não
detalhe.

**3. Que todo requisito tenha rastro para frente.** Existe pelo menos uma verificação que o confere.
*Verificação:* a lista de requisitos sem verificação associada é uma métrica, e ela deveria ser
vazia. Quando não é, o número é o tamanho da diferença entre o que se prometeu e o que se confere.

**4. Que a mudança de um requisito seja visível.** Requisito alterado sem registro é a origem do
desentendimento mais caro em projeto longo — duas pessoas lembrando de versões diferentes do mesmo
combinado. *Verificação:* existe histórico por requisito, com data e razão, e a razão não é "ajuste".

O que **não** é objetivo: descobrir o que a pessoa quer. Isso é o volume `03-DISCOVERY`, que entrega
uma especificação; este volume começa onde aquele termina. Nem estimar, planejar ou priorizar entrega
— assunto do `38-PROJECT-PLANNER` e do `39-ROADMAP`.
