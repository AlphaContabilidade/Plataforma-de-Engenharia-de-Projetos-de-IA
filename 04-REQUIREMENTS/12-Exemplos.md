---
volume: "04"
volume_nome: REQUIREMENTS
tipo: PROCESSO
secao: 12-Exemplos
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Exemplos

Uma conversão real, do formato que a descoberta entrega ao requisito com os dois rastros, e dois
casos de fronteira.

## De especificação a requisito

A descoberta do volume `03` produz entradas assim, para uma agenda de clínica:

```
lacuna: problema
resposta: "paciente so consegue marcar por telefone no horario comercial"
origem: RESPONDIDO
```

O enunciado direto — "o paciente deve poder marcar fora do horário comercial" — é falsificável, mas o
critério ainda não existe. A pergunta que o produz é onde se olha, com que entrada e qual o limite:

```
REQ-014
Enunciado: o paciente marca consulta sem falar com a recepcao, em qualquer hora do dia.
Criterio:  as 22h de um sabado, um paciente cadastrado conclui uma marcacao e recebe a
           confirmacao, sem nenhuma acao de funcionario.
Rastro tras:   lacuna "problema", origem RESPONDIDO
Rastro frente: teste de ponta a ponta "marcacao fora do expediente"
```

O critério menciona **sábado às 22h** de propósito. "Fora do horário comercial" é a categoria; o
critério precisa de um instante em que se possa olhar. E menciona "sem nenhuma ação de funcionário"
porque essa é a parte falsificável do enunciado — um sistema que aceita o pedido e espera alguém
confirmar na segunda-feira cumpre a letra e descumpre o requisito.

## Caso de fronteira 1 — o que parecia requisito e era restrição

"O sistema precisa aceitar o certificado digital da clínica." O projeto não escolhe isto: é imposição
externa. Vai para a lista de restrições. A diferença prática aparece na negociação — requisito se
discute, restrição se cumpre —, e uma lista que mistura os dois faz a equipe negociar o inegociável e
aceitar o negociável sem discutir.

## Caso de fronteira 2 — a lacuna que não virou requisito

A descoberta perguntou quantas pessoas usariam o sistema ao mesmo tempo e ninguém sabia. O resultado
correto **não** é "suportar 50 usuários simultâneos", que é o número que sairia de uma estimativa
razoável. É uma pendência:

```
PEND-003  Volume de uso simultaneo desconhecido.
          Impacto: decide se a arquitetura precisa de fila. Decidir antes da construcao.
```

Escrever "50" ali produziria um requisito com aparência de combinado que ninguém combinou — e, pior,
um número que a equipe otimizaria e o cliente nunca pediu.
