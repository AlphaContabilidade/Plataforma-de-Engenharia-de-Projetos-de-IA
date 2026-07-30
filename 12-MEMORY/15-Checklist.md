---
volume: "12"
volume_nome: MEMORY
tipo: ENGINE
secao: 15-Checklist
status: PRONTO
atualizado_em: 2026-07-30
---

# Checklist

Este checklist responde a uma pergunta única: **a memória deste agente pode ser usada para
decidir?** Cada item se marca com evidência à mão — uma chamada que devolve o valor esperado, um
número anotado, uma linha de código apontada — e nenhum depende de julgamento subjetivo. Dois
itens dependem de coisa que o componente não produz sozinho, e cada um diz de onde vem a
evidência em vez de supor que ela existe. Se algum item não puder ser marcado, a memória ainda
não é confiável para decidir, e o item que falhou aponta o que fazer.

## Procedência

- [ ] Toda fonte que alimenta o armazém tem uma origem declarada, e a lista de fontes foi
  percorrida uma a uma em vez de presumida.
- [ ] A escrita do próprio agente é registrada como `ESCRITO_PELO_AGENTE` **no mesmo passo** em
  que a ação acontece, e não identificada depois por comparação de texto ou data.
- [ ] Nenhum adaptador de fonte usa um valor de origem por conveniência quando a classificação
  correta não estava clara; a dúvida foi resolvida antes de gravar.
- [ ] A fração de eco de uma chave em que o agente escreve é maior que zero; valor exatamente
  zero é motivo de suspeita de marcação errada, conforme [`14-Metricas.md`](14-Metricas.md).

## Consulta

- [ ] Todo caminho de decisão passa por `resolver`; nenhum lê `dominancia` do armazém e compara
  com limiar à mão.
- [ ] O valor de `dominancia_minima` foi escolhido a partir do custo relativo entre errar e
  esperar no domínio, e a razão está escrita em algum lugar que sobrevive à pessoa que escolheu.
- [ ] O valor de `janela_dias` corresponde ao prazo em que o assunto daquela chave muda, e não
  foi ajustado depois de ver um veredicto indesejado.
- [ ] O chamador trata `decisao is None` como pendência humana e **para**, em vez de aplicar a
  alternativa que liderava a contagem.

## Contradição

- [ ] As contradições abertas têm dono e prazo; a contagem e a idade de cada uma são
  acompanhadas, não apenas a contagem.
- [ ] Nenhuma contradição foi encerrada registrando decisão humana como tapa-buraco sem
  encaminhar a fonte discordante para revisão.
- [ ] Antes de concluir que a base congelada envelheceu, a procedência das entradas que a
  contradizem foi conferida item a item.

## Evidência para auditoria

- [ ] O campo `evidencia` das entradas registradas diz o que sustentou a decisão, e não repete a
  decisão em outras palavras.
- [ ] Uma decisão tomada há semanas pode ser explicada lendo apenas o armazém, sem reexecutar o
  agente — a conferência foi feita em pelo menos uma chave real.
- [ ] A idade média da evidência das chaves que decidem foi medida com o envelope de
  instrumentação descrito em [`14-Metricas.md`](14-Metricas.md); o componente não produz esse
  número por conta própria, e quem decide sem ele não sabe se está apoiado em observação recente
  ou em memória que apenas não expirou.
