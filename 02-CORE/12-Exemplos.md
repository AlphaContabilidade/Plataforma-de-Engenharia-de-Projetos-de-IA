---
volume: "02"
volume_nome: CORE
tipo: ARQUITETURA
secao: 12-Exemplos
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Exemplos

Três recortes de código real deste repositório. São exemplos de arquitetura, e por isso o que
importa em cada um é a fronteira, não a funcionalidade.

## Recorte 1 — a fronteira que devolve tripla, não resposta

A interface local do acervo separa decisão de transporte. A decisão é uma função pura; o transporte é
um manipulador que converte.

```
responder(metodo, caminho, raiz, contrato, corpo, sessoes) -> (status, tipo, corpo)
```

O que essa assinatura compra: um teste que verifica que um método errado numa rota devolve `405` não
precisa de rede, e um que verifica que corpo acima do teto devolve `413` não precisa alocar o corpo.
A verificação do teto acontece **antes** de ler do socket, porque o tamanho declarado no cabeçalho é
alegação do cliente — confiar nele seria entregar a memória do servidor a quem souber o endereço.

## Recorte 2 — as três camadas de validação numa só rota

A rota que planeja um projeto exige `ideia`, `publico` e `problema`. Um pedido sem `publico` recebe
`400` com a razão escrita — "preencha o campo publico" —, e não um valor assumido.

Este é o modelo `Resultado` de [`08-Modelos.md`](08-Modelos.md) na prática: dois estados, e nunca o
terceiro. A alternativa tentadora seria preencher `publico` com "a confirmar" e seguir. O sistema
funcionaria, ninguém veria erro, e o plano gerado conteria uma decisão que ninguém tomou — que é
exatamente o anti-padrão A6 do volume `01`.

Uma validação de tamanho mínimo da ideia mora na mesma fronteira, e produziu um caso instrutivo: uma
verificação feita com a frase "loja online", de onze caracteres, voltou `400`. Por um instante aquilo
pareceu regressão de uma integração recém-feita; era a fronteira funcionando e recusando entrada
curta demais para gerar pergunta útil. **Fronteira boa produz falso alarme em quem a testa
distraído** — é o preço de recusar cedo, e é barato.

## Recorte 3 — a alternativa determinística com procedência

O motor de descoberta devolve, para cada inferência, o trecho do texto original que a produziu:

```
palpite = (LOJA_PAGAMENTOS, evidencia="tenis e aceita pix", confianca=ALTA)
```

Nenhuma chamada a modelo. A evidência sai do texto **original**, com acento preservado, por uma
função que normaliza para comparar mas guarda a posição de cada caractere. Devolver a versão
normalizada entregaria à pessoa a própria frase sem acento — parece defeito e destrói a confiança no
que o motor mostra.
