---
volume: "04"
volume_nome: REQUIREMENTS
tipo: PROCESSO
secao: 04-Arquitetura
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Arquitetura

Um requisito tem cinco partes. Faltando qualquer uma, ele deixa de servir para a função que justifica
existir — decidir, mais tarde, se foi cumprido.

## As cinco partes

**1. Identificador estável.** Nunca muda de significado. Reaproveitar o identificador de um requisito
retirado transforma todo registro que o cita em ficção — é a mesma regra dos controles do volume `01`
e pelo mesmo motivo.

**2. Enunciado falsificável.** Descreve um comportamento observável, não uma qualidade. "O relatório
mensal fica pronto em menos de dez minutos para a maior loja da base" é falsificável; "o relatório é
rápido" não.

**3. Critério de aceite.** O fato específico que se observa para decidir. É a diferença entre o
enunciado e a medição: o enunciado diz o que vale, o critério diz onde se olha, com que entrada e
qual é o limite.

**4. Rastro para trás.** Qual lacuna da especificação originou este requisito, e com que origem a
resposta foi obtida. É a parte que responde "por que isto está aqui?" três meses depois.

**5. Rastro para frente.** Qual verificação confere este requisito. Sem ela, o requisito é uma
promessa que ninguém cobra.

## O que não é requisito

Três coisas são frequentemente anotadas como requisito e não são, e separá-las é o trabalho mais útil
desta etapa.

**Restrição** é algo que o projeto não escolhe: a lei, o sistema legado, o orçamento, a plataforma que
a empresa já usa. Não é falsificável por observação do produto, e tratá-la como requisito produz uma
lista onde itens negociáveis e inegociáveis parecem iguais.

**Decisão de projeto** é uma escolha da equipe — a linguagem, o banco, o formato do arquivo. Ela
serve a requisitos, mas não é um. Confundi-las congela implementação dentro do combinado com o
cliente, e depois qualquer refatoração parece quebra de contrato.

**Desejo** é o enunciado não falsificável. A ação correta não é apagar: é **transformar ou declarar**.
Perguntar "o que você veria acontecer que te faria dizer que isto não está bom?" costuma converter um
desejo em requisito em uma frase. Quando não converte, ele fica registrado como desejo, num lugar
separado, e ninguém o conta como escopo.
