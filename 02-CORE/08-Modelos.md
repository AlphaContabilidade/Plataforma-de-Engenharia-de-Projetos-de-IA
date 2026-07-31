---
volume: "02"
volume_nome: CORE
tipo: ARQUITETURA
secao: 08-Modelos
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Modelos

Três estruturas. Estão descritas por forma e invariante, não por linguagem.

## `Pedido` — o que atravessa a fronteira de entrada

Estrutura fechada, validada, sem campo de texto livre que o resto do sistema vá interpretar. Pode
conter texto livre como **dado** — a descrição que a pessoa escreveu —, e a distinção é essencial:
texto que será mostrado, armazenado ou enviado ao modelo é dado; texto sobre o qual o código vai
tomar decisão é fronteira que faltou.

## `ContratoDeSaida` — o que a fronteira de saída exige

Declarado **antes** da chamada, junto do prompt. Tem três camadas, na ordem em que são verificadas:

| Camada | Pergunta | Repetir adianta | Falha significa |
|---|---|---|---|
| Forma | tem os campos e os tipos? | sim, uma vez, descrevendo a falha | o modelo não seguiu o formato |
| Domínio | os valores cabem no mundo? | não | faltou restrição no contexto |
| Autorização | isto era permitido? | não | recusa, e registro |

Separar as três não é purismo. Elas têm ações diferentes, e um sistema que as trata como uma só ou
repete quando não devia — gastando o dobro para chegar no mesmo lugar — ou desiste quando bastava
repetir.

## `Resultado` — o que sai da fronteira

Um de dois estados, e nunca os dois nem nenhum: **valor com tipo** ou **falha com razão**. A razão é
uma das três camadas acima, e não um texto de erro genérico: quem chamou precisa saber se vale
tentar de novo, e essa informação está justamente na camada que falhou.

O que este modelo proíbe é o terceiro estado que aparece sozinho nos sistemas reais: valor
"parcial", com alguns campos preenchidos e outros no padrão. Ele é a origem do anti-padrão A6 do
volume `01` — a lacuna preenchida em silêncio — e a defesa é estrutural: o tipo não permite
representá-lo.
