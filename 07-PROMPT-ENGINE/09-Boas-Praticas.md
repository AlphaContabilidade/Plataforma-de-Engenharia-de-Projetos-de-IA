---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 09-Boas-Praticas
status: RASCUNHO
atualizado_em: 2026-07-29
---

# Boas práticas

As práticas abaixo são pares: cada uma tem o anti-padrão correspondente em
[`10-Anti-Patterns.md`](10-Anti-Patterns.md), na mesma ordem e com o mesmo identificador.
Isso é deliberado — recomendação isolada é fácil de concordar e difícil de aplicar,
enquanto o par mostra qual comportamento concreto está sendo trocado por qual.

## P1. Declare a variável com o tipo que o modelo vai receber

Declarar `Variavel("quantidade", int)` em vez de `Variavel("quantidade", str)` transfere
para o construtor uma verificação que de outro modo aconteceria no provedor, cobrada por
token. O tipo declarado é o tipo que `isinstance` verifica, então declarar o tipo largo
equivale a desligar a verificação. Quando o valor legítimo pode ser de mais de um tipo, o
caminho correto é normalizar antes de chamar `render`, e não alargar a declaração.

## P2. Escreva o caso de ouro antes de mexer no corpo

O caso de ouro é o que transforma "melhorou" em número. Escrevê-lo antes evita o viés de
formular a expectativa depois de ver a saída que se conseguiu, que é a forma mais comum de
produzir uma bateria que nunca reprova nada. Um caso de ouro tem nome, entradas e um padrão
verificável; três casos bem escolhidos valem mais que trinta variações do mesmo caso.

## P3. Ancore o padrão esperado no que importa, não no formato

Um padrão como `r"\b2\.500,00\b"` verifica o número que a resposta tinha de conter. Um
padrão que exige o parágrafo inteiro verifica a redação, que varia legitimamente. A regra
prática é ancorar no fato, na estrutura obrigatória ou no rótulo exigido, e deixar o resto
livre; padrão frouxo demais não detecta regressão, padrão apertado demais gera falso alarme
e a bateria perde credibilidade.

## P4. Promova por deriva medida, não por impressão

Comparar a candidata contra a versão promovida sobre a mesma amostra é uma chamada de
`comparar`, e devolve um sinal. Deriva zero com custo maior é motivo para não promover.
Deriva positiva pequena em amostra pequena é motivo para ampliar a amostra antes de decidir,
porque um acerto a mais em dez casos é uma variação de dez pontos que pode não significar
nada.

## P5. Trate cada incidente como um caso de ouro novo

Quando uma falha real de produção reproduz na bateria, ela vira um caso permanente e a
regressão fica impossível de repetir em silêncio. Quando não reproduz, o achado tem de ser
registrado: a causa está no executor, no provedor ou nos dados, e reescrever o prompt nesse
cenário produz mudança sem efeito e gasta uma versão do histórico.

## P6. Deixe o registro decidir a versão

Registrar o mesmo conteúdo é idempotente, então o caminho seguro é chamar `registrar` sem
medo em cada carga do módulo e usar o rótulo devolvido. Numerar versão à mão reintroduz
exatamente o problema que o hash resolve, porque o número passa a depender de alguém lembrar
de incrementá-lo.

## P7. Mantenha o nome do prompt estável

O nome é a chave de agrupamento do histórico. Renomear cria um espaço de versões novo, com
numeração recomeçando em `v1`, e a trilha anterior fica órfã. Quando o propósito do prompt
muda de verdade, o nome novo é a decisão certa — mas ela precisa ser consciente, e o volume
que consome o prompt precisa ser atualizado no mesmo passo.

## P8. Documente o executor, não o provedor

O motor registra que existe um `Callable[[str], str]`. Qual modelo está atrás dele, com que
parâmetros e a que custo é informação que envelhece rápido e pertence a outros volumes. O
que o volume 07 precisa registrar é o contrato da função e o fato de que a bateria de teste
usa um substituto determinístico.
