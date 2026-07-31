---
volume: "02"
volume_nome: CORE
tipo: ARQUITETURA
secao: 15-Checklist
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Checklist

## Antes de acrescentar uma chamada ao modelo

- A alternativa determinística foi considerada e descartada **com razão escrita**? Regra N8.
- O contrato de saída está declarado antes do prompt, e não deduzido da resposta?
- As três camadas de validação existem — forma, domínio e **autorização**? A terceira é a que falta.
- O caminho de falha não produz efeito nenhum? Regra N4.
- A repetição, se existe, só dispara em falha de forma, e no máximo uma vez? Regra N5.
- O número de chamadas do caminho mudou? Se sim, isso é decisão de arquitetura e vai com
  justificativa no diagrama de sequência, não só no código.

## Antes de dizer que um trecho não é testável

- O que exatamente não é testável: a chamada, ou o que está em volta dela? Quase sempre é o que está
  em volta, e isso é vazamento (B1), não limitação.
- A chamada está atrás de uma interface pequena que o teste substitua?
- A montagem de contexto lê relógio, aleatório ou estado global? Se lê, o problema é N6, e a correção
  é receber o valor por parâmetro.
- Existe teste alimentando a fronteira de saída com resposta malformada? Sem ele, a fronteira é uma
  intenção, não um controle.
