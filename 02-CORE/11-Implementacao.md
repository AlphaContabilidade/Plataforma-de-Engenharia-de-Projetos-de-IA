---
volume: "02"
volume_nome: CORE
tipo: ARQUITETURA
secao: 11-Implementacao
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Implementação

As seis partes não exigem framework. Exigem que cada uma esteja num lugar nomeável e que a fronteira
entre elas seja uma assinatura de função. Esta seção mostra como isso aparece em código real deste
repositório, porque exemplo de terceiro não se confere.

## A função de decisão pura

`ferramentas/web.py` implementa a regra N6 e a boa prática da função pura de uma forma que vale
copiar. A função `responder(metodo, caminho, raiz, contrato, corpo, sessoes)` devolve uma tripla
`(status, tipo, corpo)` e **não toca em socket**. O manipulador de `http.server` apenas converte essa
tripla numa resposta HTTP.

O ganho é direto: a interface inteira é testável sem porta livre, sem navegador e sem espera. As
asserções sobre roteamento, erro e limite rodam em memória, e o único teste que precisa de socket é o
que verifica que o socket funciona.

## O contrato de saída declarado antes

O volume `07-PROMPT-ENGINE` traz a forma que este volume recomenda: um modelo de prompt com
**assinatura tipada** — nome, parâmetros com tipo, marca de opcional — e um identificador de versão
derivado do corpo mais a assinatura. Declarar a assinatura junto do prompt é o que permite validar a
resposta contra algo escrito antes da chamada, em vez de deduzir o contrato do que voltou.

O detalhe que aquele volume aprendeu por auditoria é instrutivo aqui: o identificador de versão não
cobria a marca de obrigatoriedade, e por isso dois modelos que renderizavam diferente recebiam a
mesma versão. Contrato que ignora parte de si mesmo é contrato que não distingue o que deveria.

## A alternativa determinística

O motor do volume `03-DISCOVERY` é o exemplo da regra N8. A detecção de plataforma e de contexto
poderia ser uma chamada ao modelo; é uma tabela de termos com fronteira de palavra, que devolve o
**trecho** que produziu cada palpite. É auditável, reproduzível, instantânea e de graça.

O preço dessa escolha também é real e está registrado lá: a tabela não conhecia `pix`, e a frase
comercial mais comum do país saía sem contexto — com a suíte inteira verde. Alternativa
determinística falha por **falta de dado**, não por variação; a diferença é que falta de dado se
corrige acrescentando dado, e variação não se corrige.

## Onde a parte 3 é isolada

A forma mínima é uma função que recebe o contexto montado e devolve texto ou levanta. Tudo o que o
resto do sistema sabe do provedor cabe nessa assinatura. Quando o cliente do fornecedor aparece
importado em três módulos de domínio, a parte 3 não está isolada — está espalhada.
