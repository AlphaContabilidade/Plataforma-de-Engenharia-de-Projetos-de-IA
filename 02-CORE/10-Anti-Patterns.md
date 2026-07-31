---
volume: "02"
volume_nome: CORE
tipo: ARQUITETURA
secao: 10-Anti-Patterns
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Anti-Patterns

**B1 — Texto livre vazado.** A resposta do modelo atravessa a fronteira como texto e o chamador
decide sobre o conteúdo. É o anti-padrão raiz: os outros quase todos derivam dele. *Sintoma:* alguém
diz que aquele trecho "não dá para testar". *Custo:* cresce com o número de chamadores, e por isso
quase nunca é revertido.

**B2 — Repetição cega.** Qualquer falha dispara nova chamada, às vezes três, às vezes em laço.
Multiplica custo e latência, esconde a causa, e não corrige nada quando a falha é de domínio.
*Contramedida:* N5 e a tabela de três camadas de [`08-Modelos.md`](08-Modelos.md).

**B3 — Efeito antes da validação.** Grava primeiro "para não perder", valida depois. Transforma o
caminho de erro no mais perigoso do sistema. *Contramedida:* N4.

**B4 — Contexto montado com relógio.** A montagem lê a hora, ou um contador global, ou um valor
aleatório. O sistema deixa de ser reproduzível e a investigação de uma resposta ruim vira arqueologia.
*Contramedida:* N6 — e a forma prática é receber o instante como parâmetro em vez de consultá-lo.

**B5 — Validação só de forma.** O JSON está perfeito e a data está no ano que vem, ou a operação é
"apagar" quando o chamador só autorizou "arquivar". Passa em todo teste de parser. *Contramedida:* as
camadas de domínio e autorização, que são as duas que ninguém escreve.

**B6 — Modelo no meio do domínio.** Uma função de regra de negócio chama o modelo lá dentro. A partir
daí a regra não é mais testável nem legível, e ninguém consegue responder o que ela faz sem rede.
*Contramedida:* as seis partes; a chamada é a parte 3, e regra de negócio é parte 5.

**B7 — Chamada acrescentada sem decisão.** Alguém precisou de um resumo e pôs mais uma chamada no
caminho quente. Ninguém percebeu que a latência dobrou e o custo por requisição também.
*Contramedida:* N7 — número de chamadas é arquitetura declarada, e aparece no diagrama de sequência.
