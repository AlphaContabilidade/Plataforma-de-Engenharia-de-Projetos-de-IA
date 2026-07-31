---
volume: "31"
volume_nome: TESTING
tipo: PROCESSO
secao: 10-Anti-Patterns
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Anti-Patterns

**E1 — Teste vazio.** Passa sempre, inclusive com o código quebrado. Laço sobre lista que ficou
vazia, asserção sobre conjunto que sempre contém o esperado, bloco inalcançável. *Contramedida:* T2,
a mutação. É o anti-padrão que este volume existe para combater.

**E2 — Asserção frouxa que passa por acidente.** "A lista fica vazia" enquanto o conjunto tem um
elemento. Cai quando o sistema cresce, e quem estiver mexendo em outra coisa vai achar que quebrou
algo. *Contramedida:* T5, e a correção é **precisar**, não afrouxar.

**E3 — Teste intermitente tolerado.** Falha uma vez em cada dez e alguém roda de novo. A suíte perde
autoridade: quando o vermelho pode ser ruído, nenhum vermelho é levado a sério. *Contramedida:* T3, e
tratar intermitência como prioridade acima de qualquer teste novo.

**E4 — Suíte que só cresce.** Ninguém aposenta teste porque ninguém sabe o que cada um pega. Fica
lenta, deixa de ser rodada a cada mudança, e vira ritual de fim de semana. *Contramedida:* T1 — a
frase do defeito nomeável é o que torna a aposentadoria segura.

**E5 — Cobertura como meta.** Percentual alto obtido com testes que exercitam sem afirmar. Mede
linhas alcançadas, e linha alcançada por um teste sem asserção conta igual. *Contramedida:* a leitura
de [`14-Metricas.md`](14-Metricas.md).

**E6 — Teste de mecanismo apresentado como cobertura de domínio.** O motor está perfeito e a tabela
não tem os dados do país onde o sistema roda. *Contramedida:* T9.

**E7 — Ajuste na falha.** O teste caiu, alguém "atualizou a expectativa" e ele voltou a passar. Se a
expectativa nova descreve o que o código faz, o teste virou espelho — e espelho não verifica nada.
*Contramedida:* T6, e o fluxo de decisão de [`06-Fluxogramas.md`](06-Fluxogramas.md).

**E8 — Número sem escopo na documentação.** "A suíte tem trinta e nove testes." Verdade no dia em que
foi escrita, falsa na semana seguinte, sem ninguém ter tocado no arquivo. *Contramedida:* T8.
