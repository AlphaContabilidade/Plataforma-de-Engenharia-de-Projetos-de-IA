---
volume: "04"
volume_nome: REQUIREMENTS
tipo: PROCESSO
secao: 15-Checklist
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Checklist

## Antes de escrever um requisito

- A origem da resposta é uma das válidas, e **não** é `PADRAO_ASSUMIDO`? Se for, isto é pendência.
- Existe fato observável que tornaria o enunciado falso? Se não consegue descrevê-lo, aplique a
  pergunta de conversão antes de escrever.
- O projeto pode escolher diferente? Se não pode, é restrição e vai para outra lista.
- Isto descreve comportamento ou modo de construir? Modo de construir é decisão de projeto.
- O critério de aceite diz **onde se olha, com que entrada e qual é o limite**? "Rápido para a maior
  loja" ainda não é critério; "menos de dez minutos para a loja com 40 mil lançamentos no mês" é.
- O enunciado tem "e" no meio? Provavelmente são dois requisitos que falham separado.

## Antes de entregar o conjunto

- Todo requisito tem verificação nomeada? A lista dos que não têm vai junto, visível.
- A lista de decisões abertas está no corpo da entrega, e não em anexo? Anexo não é lido.
- A lista de decisões abertas está vazia? Se está, desconfie: em projeto real isso quase sempre
  significa lacuna preenchida em silêncio.
- Alguém que não escreveu tentou o teste do contraexemplo por amostragem?
- Nenhum requisito carrega prazo ou prioridade dentro do enunciado?
