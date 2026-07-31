---
volume: "02"
volume_nome: CORE
tipo: ARQUITETURA
secao: 13-Testes
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Testes

Este volume descreve uma camada arquitetural e não publica exemplo de código próprio: o código que o
realiza são as ferramentas e os exemplos dos volumes vizinhos. O comando com escopo é este.

```
python -m pytest ferramentas/tests -q
```

## O que se testa numa arquitetura com fronteira

**A fronteira de entrada** se testa com entrada inválida antes de entrada válida. Campo faltando,
tipo errado, tamanho acima do teto. A asserção que importa é que a recusa acontece **antes** de
qualquer alocação ou efeito — um teste que só verifica o código de status não distingue recusar cedo
de recusar depois de já ter feito o trabalho.

**A montagem de contexto** se testa por igualdade: mesmo estado de entrada, mesmo contexto, byte a
byte. É o teste que fixa a regra N6, e ele falha imediatamente quando alguém acrescenta uma leitura
de relógio — que é justamente o defeito que se quer pegar cedo.

**A fronteira de saída** exige três famílias de teste, uma por camada: resposta malformada, resposta
bem formada com valor fora do domínio, e resposta bem formada e válida pedindo algo não autorizado. A
terceira é a que quase nunca existe, e é a única que separa "o modelo errou" de "o modelo fez o que
não podia".

**A parte probabilística** se testa substituindo. Como a chamada está atrás de uma interface pequena,
o teste injeta uma função que devolve o texto que se quer — inclusive texto ruim. Testar contra o
provedor real é teste de integração, roda em outro lugar e em outra frequência.

## O que não se testa aqui

Não se testa a qualidade da resposta do modelo. Isso é avaliação, tem instrumento próprio e não cabe
numa suíte que precisa rodar em segundos e sem rede. Um sistema que mistura as duas coisas acaba com
uma suíte lenta, cara e intermitente, e a reação previsível a suíte intermitente é desligá-la.
