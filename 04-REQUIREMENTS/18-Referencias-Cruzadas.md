---
volume: "04"
volume_nome: REQUIREMENTS
tipo: PROCESSO
secao: 18-Referencias-Cruzadas
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Referências Cruzadas

`depende_de` aponta para `01` e `03`. Para `01` porque este volume usa o vocabulário de procedência da
fundação — as seis origens, o anti-padrão da lacuna preenchida em silêncio — em vez de redefini-lo.
Para `03` porque a entrada deste processo é literalmente a saída daquele motor, e ler os requisitos
sem saber como a especificação foi produzida esconde a informação mais importante de cada item: como
a resposta foi obtida.

**Dentro deste volume**, quem vai escrever requisitos lê [`04-Arquitetura.md`](04-Arquitetura.md),
pelas cinco partes e pelas três coisas que não são requisito, e
[`06-Fluxogramas.md`](06-Fluxogramas.md), pelo funil de conversão. Quem vai revisar um conjunto
existente começa por [`10-Anti-Patterns.md`](10-Anti-Patterns.md).

**Vizinhança com seção escrita:** o [`03-DISCOVERY`](../03-DISCOVERY/01-Introducao.md) entrega a
especificação que este volume consome, com origem e evidência já anexadas a cada resposta. O
[`02-CORE`](../02-CORE/01-Introducao.md) recebe daqui os requisitos que definem o contrato de saída de
um sistema de IA, e a exigência de critério de aceite observável casa com a exigência de contrato
declarado antes da chamada.

**Vizinhança em prosa e sem link**, porque os volumes existem como pasta sem seção escrita:
`05-BUSINESS` julga se um requisito merece existir, o que este volume não faz; `31-TESTING` trata da
técnica de escrever a verificação que o rastro para frente exige; `17-SECURITY` trata dos requisitos
cuja falsificação exige construir o ataque; e `38-PROJECT-PLANNER` e `39-ROADMAP` recebem o conjunto
e decidem ordem e prazo, que a regra Q5 mantém fora daqui.
