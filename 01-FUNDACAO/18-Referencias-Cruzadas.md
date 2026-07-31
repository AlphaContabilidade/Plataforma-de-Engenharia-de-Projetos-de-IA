---
volume: "01"
volume_nome: FUNDACAO
tipo: GOVERNANCA
secao: 18-Referencias-Cruzadas
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Referências Cruzadas

Este volume é pré-requisito de leitura de todo o acervo, e por isso `depende_de` está **vazio**: uma
fundação que dependesse de outro volume criaria a pergunta de qual dos dois se lê primeiro.

**Dentro deste volume**, a leitura mínima para quem vai aplicar os controles é
[`04-Arquitetura.md`](04-Arquitetura.md), pela matriz, e [`07-Regras.md`](07-Regras.md), pela
Definição de PRONTO. Quem vai escrever um volume novo deve ler antes
[`10-Anti-Patterns.md`](10-Anti-Patterns.md), porque os seis modos de falha são mais úteis como
prevenção que como diagnóstico.

**Vizinhança, em prosa e sem link**, porque os volumes citados existem como pasta e ainda não têm
seção escrita — apontar link para arquivo inexistente produziria pré-requisito que não pode ser lido.

`17-SECURITY` trata do adversário deliberado; aqui o adversário é o engano involuntário.
`30-AI-GOVERNANCE` diz o que é permitido fazer com uma afirmação verdadeira; aqui se estabelece como
se sabe que ela é verdadeira. `31-TESTING` e `32-QUALITY` recebem a exigência de verificação
executável e tratam da técnica e do processo. `35-DOCUMENTATION` herda o problema do apodrecimento de
prosa, descrito no Caso 3.

Os volumes `03-DISCOVERY`, `07-PROMPT-ENGINE` e `12-MEMORY` são as três realizações concretas destes
princípios hoje, e servem de referência de forma para quem for escrever o próximo.
