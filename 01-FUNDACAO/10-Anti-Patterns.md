---
volume: "01"
volume_nome: FUNDACAO
tipo: GOVERNANCA
secao: 10-Anti-Patterns
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Anti-Patterns

Seis modos de falha. Todos foram observados — quatro deles neste acervo — e nenhum decorre de
descuido: são o que acontece quando a pressa encontra um processo sem controle executável.

**A1 — Status que mente.** Marcar `PRONTO` com gate vermelho, ou `concluído` com ressalva não
escrita. É o mais grave porque desliga a atenção de quem lê: um volume `RASCUNHO` é lido com
desconfiança saudável, e um `PRONTO` falso é lido como base para a próxima decisão. *Contramedida:*
critério 1 da Definição de PRONTO, com código de saída.

**A2 — Número que ninguém mediu.** "Reduz o custo em 40%", "cerca de 200 testes". Número redondo
sem comando ao lado é quase sempre estimativa promovida a fato pela repetição. *Contramedida:* R3,
e o hábito de escrever o comando junto.

**A3 — Autoaprovação.** Quem escreveu avalia o que escreveu e conclui que está bom. Não é
desonestidade: é que o autor lê o que quis dizer, não o que escreveu. *Contramedida:* R5.

**A4 — Controle decorativo.** O gate existe, roda, sempre passa, e ninguém percebeu que ele não
testa nada — um laço sobre uma lista que ficou vazia, uma asserção sobre um conjunto que sempre
contém o que se procura. *Contramedida:* mutação deliberada; um controle que nunca ficou vermelho
não foi verificado.

**A5 — Afirmação verdadeira que lê como falsa.** Discutida em [`06-Fluxogramas.md`](06-Fluxogramas.md).
O autor mediu certo, escreveu certo, e o leitor confere e vê outra coisa. O efeito na confiança é
idêntico ao de uma mentira, e é pior de corrigir porque o autor tem razão e resiste. *Contramedida:*
o ponto `Q4` do fluxo — não basta ser verdade, precisa ser confirmável pelo leitor.

**A6 — Lacuna preenchida em silêncio.** A evidência não decidia, alguém adotou o valor mais provável,
e ninguém marcou. Três passos adiante isso é um requisito que o cliente nunca pediu. *Contramedida:*
R7 e a origem `PADRAO_ASSUMIDO`, cuja função é justamente ter um nome — o que não tem nome não é
procurado.

O padrão comum aos seis é que **nenhum deles produz sintoma no momento em que acontece**. Todos
produzem sintoma semanas depois, longe da causa, e é por isso que dependem de controle e não de
atenção.
