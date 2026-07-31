---
volume: "04"
volume_nome: REQUIREMENTS
tipo: PROCESSO
secao: 14-Metricas
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Métricas

**Requisitos sem verificação associada.** *Obtenção:* contagem direta do campo de rastro para frente.
O valor esperado é zero, e qualquer outro número é literalmente o tamanho da diferença entre o que se
prometeu e o que se confere. É a métrica mais útil do volume porque é barata e não tem interpretação.

**Pendências abertas na entrega.** *Obtenção:* contagem da lista de decisões pendentes. A leitura é
contraintuitiva: **zero é suspeito**. Um projeto de tamanho real cuja descoberta não deixou nenhuma
decisão em aberto quase sempre teve as lacunas preenchidas em silêncio — o anti-padrão D2 —, e a
ausência da lista é o sintoma, não a prova de completude.

**Requisitos alterados sem razão registrada.** *Obtenção:* histórico do arquivo versionado, filtrando
mudanças cuja razão é vazia, "ajuste" ou "alinhamento". Mede a saúde do processo, não do produto.

**Falhas de verificação resolvidas mudando o requisito.** *Obtenção:* cruzamento entre falhas e
histórico. Uma proporção alta indica o anti-padrão D7 — o conjunto virando espelho da implementação.
Zero também é sinal, do lado oposto: significa que nenhum requisito jamais estava errado, o que não
acontece em projeto real.

**Proporção de requisitos com origem `INFERIDO` não confirmada.** *Obtenção:* campo de origem. Cada
um destes é uma afirmação que ninguém fez sobrevivendo dentro de um combinado.

## O que não se mede

Não se mede quantidade de requisitos. Conjunto grande não é conjunto bom, e a única coisa que o
número diz com segurança é quanto tempo levará para revisar — o que é custo, não valor.
