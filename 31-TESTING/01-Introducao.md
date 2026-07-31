---
volume: "31"
volume_nome: TESTING
tipo: PROCESSO
secao: 01-Introducao
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Introdução

**Um teste que nunca ficou vermelho é uma hipótese, não um teste.**

A frase parece exagero até a primeira vez que se encontra o caso. Um laço que percorre uma lista que
ficou vazia. Uma asserção sobre um conjunto que sempre contém o que se procura. Um `assert` dentro de
um bloco que nenhuma execução alcança. Todos passam, todos aparecem verdes no relatório, e todos
contam para a métrica de cobertura. A suíte inteira dá a sensação de que o sistema está protegido, e
a proteção é uma ilusão que ninguém tem motivo para questionar — porque questionar exige suspeitar do
que está funcionando.

Este acervo tem o caso documentado. Uma seção de um volume era composta de blocos de código cheios de
`assert`, escritos para o leitor conferir o raciocínio. Nada os executava. Eram prosa com aparência
de verificação, e envelheciam como qualquer outro número escrito à mão. Quando um teste passou a
executá-los, a prova de que ele não era decoração veio por **mutação**: trocar um `37` por `99` no
Markdown deixou a suíte vermelha, e o texto foi restaurado em seguida. Aquele minuto de trabalho é a
diferença entre um controle e um enfeite convincente.

O segundo tema do volume é mais desconfortável, porque contraria o instrumento em que mais se confia:
**suíte verde não é cobertura**. Também há caso registrado aqui. Um motor de detecção tinha dezesseis
testes, todos verdes, provando que o mecanismo funcionava — fronteira de palavra, acento preservado,
evidência distinta. E a frase comercial mais comum do país saía sem resultado nenhum, porque a tabela
de dados não conhecia `pix`. Os testes cobriam o **mecanismo** e ninguém tinha testado o **dado**. A
distinção não aparece em nenhuma métrica de linhas cobertas.

O que este volume defende, então, não é escrever mais testes. É escrever testes que possam falhar, e
saber dizer o que cada um pegaria se estivesse errado.
