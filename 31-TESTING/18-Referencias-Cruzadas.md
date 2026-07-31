---
volume: "31"
volume_nome: TESTING
tipo: PROCESSO
secao: 18-Referencias-Cruzadas
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Referências Cruzadas

`depende_de` aponta para `01` e `04`. Para `01` porque a regra T6 é a forma operacional da regra R2 da
fundação, e o anti-padrão do controle decorativo é o mesmo E1 visto de outro ângulo. Para `04` porque
este volume trata da técnica de escrever a verificação que aquele exige como rastro para frente —
lê-lo sem saber por que a verificação precisa existir inverte a ordem natural.

**Dentro deste volume**, quem vai escrever teste lê [`04-Arquitetura.md`](04-Arquitetura.md), pelas
quatro partes e pela asserção negativa, e [`05-Diagramas.md`](05-Diagramas.md), pelo ciclo de
mutação. Quem recebeu um teste vermelho vai direto a [`06-Fluxogramas.md`](06-Fluxogramas.md), que é
a única seção escrita para ser lida com pressa.

**Vizinhança com seção escrita:** o [`04-REQUIREMENTS`](../04-REQUIREMENTS/01-Introducao.md) exige a
verificação que este volume ensina a escrever; o [`02-CORE`](../02-CORE/04-Arquitetura.md) define a
fronteira que torna a parte probabilística substituível no teste; e o
[`01-FUNDACAO`](../01-FUNDACAO/07-Regras.md) traz a regra de nunca ajustar a verificação para o
artefato passar.

**Vizinhança em prosa e sem link**, porque os volumes existem como pasta sem seção escrita:
`32-QUALITY` decide o que acontece depois que o teste falha e quem revisa o quê; `17-SECURITY` trata
do teste cuja construção exige montar o ataque; `33-PERFORMANCE` mede o tempo do produto, e não o da
suíte; e `26-AI-MODELS` cuida da avaliação de resposta de modelo, que este volume mantém
deliberadamente fora da suíte rápida.
