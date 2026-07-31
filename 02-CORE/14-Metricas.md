---
volume: "02"
volume_nome: CORE
tipo: ARQUITETURA
secao: 14-Metricas
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Métricas

Quatro métricas, cada uma com a obtenção junto.

**Proporção do código testável sem rede.** Quanto do sistema roda com o provedor desligado.
*Obtenção:* rodar a suíte sem rede e ver o que quebra. A resposta útil não é o número em si; é se
alguém sabe respondê-lo. Quando a resposta é "não sei", o diagnóstico já está feito, e quase sempre é
o anti-padrão B1.

**Chamadas ao modelo por caminho.** Quantas vezes um pedido aciona o provedor. *Obtenção:* contagem
no diagrama de sequência, conferida por registro em execução. É a métrica que governa latência e
custo ao mesmo tempo, e a que mais cresce sem ninguém decidir — cada acréscimo parece pequeno.

**Distribuição das falhas de fronteira por camada.** Quantas são de forma, quantas de domínio,
quantas de autorização. *Obtenção:* o campo de razão do `Resultado`, agregado. A leitura é
diagnóstica e direta: muita falha de forma indica prompt ou contrato mal escrito; muita de domínio
indica contexto sem as restrições; **qualquer** falha de autorização merece investigação individual.

**Efeitos produzidos a partir de resposta não validada.** *Obtenção:* deveria ser sempre zero, e o
modo de obter é auditoria do caminho de erro, não contagem. É a métrica que só tem valor quando é
zero — qualquer outro número é incidente, não medida.

## O que não se mede aqui

Não se mede acurácia do modelo. É assunto de avaliação, com instrumento e vocabulário próprios.
Misturar acurácia com métrica de arquitetura produz a conclusão errada mais comum da área: atribuir
ao modelo um problema de montagem de contexto, e gastar a troca de fornecedor para descobrir que o
sintoma continua igual.
