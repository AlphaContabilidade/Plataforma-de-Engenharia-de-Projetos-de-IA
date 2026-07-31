---
volume: "01"
volume_nome: FUNDACAO
tipo: GOVERNANCA
secao: 16-Roadmap
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Roadmap

Três frentes, em ordem de valor por esforço. Nenhuma é promessa de data — este volume não tem dono
exclusivo e a fila muda conforme os volumes vizinhos entram.

**1. Fechar o controle C8, ou declará-lo definitivamente manual.** É a única linha não executável da
matriz. O caminho mais promissor não é interpretar português: é obrigar que todo número afirmado em
prosa apareça também num bloco verificável — o padrão já usado no volume 03, onde os blocos de código
da seção de exemplos são executados por um teste que os extrai do Markdown. Isso não cobre número
escrito por extenso, e por isso a alternativa honesta é declarar C8 manual para sempre e mover o
esforço para reduzir a quantidade de número solto na prosa.

**2. Métrica de idade de afirmação.** Hoje é estimativa, o que a coloca sob suspeita do anti-padrão
que ela deveria ajudar a detectar. Exige registrar a data de cada medição junto do número, e não
apenas no front-matter da seção.

**3. Matriz de controles legível por máquina.** Hoje a matriz é uma tabela em Markdown, escrita à
mão. Movê-la para `contrato.json` permitiria que o gate conferisse que todo controle declarado tem
teste correspondente — o controle dos controles. O risco é conhecido e precisa ser desenhado antes:
uma matriz que só aceita controle executável empurra os manuais para fora do registro, e é
exatamente o que este volume proíbe.
