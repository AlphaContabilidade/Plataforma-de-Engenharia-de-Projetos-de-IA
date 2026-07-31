---
volume: "31"
volume_nome: TESTING
tipo: PROCESSO
secao: 15-Checklist
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Checklist

## Antes de dizer que um teste está pronto

- Consegue escrever, em uma frase, qual defeito ele pega? "Garante que a função funciona" não é
  resposta — é o modo educado de dizer que ninguém sabe.
- Ele já ficou vermelho? Se nunca ficou, quebre de propósito o que ele deveria pegar, confira o
  vermelho e desfaça. Leva menos de um minuto.
- A asserção sobrevive ao conjunto crescer? "Fica vazio", "tem exatamente um" e "é o primeiro" são
  frouxas por natureza.
- Se há filtro ou seleção, existe a asserção **negativa** — o que não deveria estar ali?
- Ele toca rede, disco ou relógio? Se toca no relógio, receba a data como parâmetro.
- Ele exercita mais de um comportamento? Se sim, a falha não vai dizer qual quebrou.

## Antes de mexer num teste que estava passando

- O que mudou: o código ou o teste?
- Se o comportamento novo é o desejado, a asserção antiga estava **frouxa** ou estava **certa**?
- Se estava frouxa, a correção é torná-la **precisa**, com a razão escrita no código — não
  afrouxá-la mais.
- Se estava certa e ainda assim o comportamento novo é desejado, isso é mudança de contrato e vai
  registrada, não silenciosa.

## Antes de citar um número de testes em documentação

- O comando tem **escopo**? Sem escopo, o número cresce a cada volume novo e a frase apodrece
  sozinha.
- O número foi medido agora, ou copiado de outra seção?
