---
volume: "01"
volume_nome: FUNDACAO
tipo: GOVERNANCA
secao: 09-Boas-Praticas
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Boas Práticas

Práticas que passaram no teste de terem evitado defeito real, e não por soarem sensatas.

**Escreva o comando com escopo.** `pytest exemplos/03-discovery -q` e `pytest exemplos -q` produzem
números diferentes, e o segundo cresce a cada volume novo. Prosa que cita o comando sem escopo
envelhece na semana seguinte, e envelhece de um jeito que parece mentira em vez de defasagem.

**Separe o que foi medido do que aparece na tela.** Corpo de teste e relógio de parede são grandezas
diferentes. Afirmar a primeira e deixar o leitor conferir a segunda tem o mesmo efeito de escrever
algo falso, com o agravante de ter sido escrito de boa-fé e por isso ninguém procurar o erro.

**Prefira a asserção sobre o objeto à asserção sobre o conjunto.** "A lista fica vazia" passa por
acidente enquanto o conjunto tiver um elemento só; "o item recusado não está mais na lista" continua
verdadeiro quando o conjunto cresce. Um teste deste acervo caiu ao acrescentar um termo à detecção, e
a asserção foi tornada precisa em vez de afrouxada — a diferença entre as duas reações é o que
`R2` protege.

**Declare a falta no lugar onde ela morde.** A verificação que não existe pertence ao checklist de
quem vai mexer, não a um documento de dívida técnica que ninguém abre na hora de mexer.

**Faça o controle falhar de propósito, uma vez.** Um teste que nunca ficou vermelho é uma hipótese.
Neste acervo, o teste que executa os blocos de código da prosa foi validado por mutação: trocar `37`
por `99` no Markdown deixa a suíte vermelha, e o texto foi restaurado em seguida. Sem esse minuto de
trabalho, o teste seria decoração convincente.

**Registre o veredicto baixo.** O relatório da primeira auditoria do volume 07, nota 8,5, continua no
acervo ao lado da segunda, 8,9. Apagar a nota baixa depois de corrigir transforma o histórico num
argumento de que nada deu errado, e histórico assim não ensina ninguém.

**Prefira falha imediata a erro silencioso.** Validação que levanta no carregamento troca um defeito
que aparece em produção por um que aparece no primeiro `import`.
