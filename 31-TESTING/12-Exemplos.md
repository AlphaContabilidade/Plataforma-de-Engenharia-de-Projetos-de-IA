---
volume: "31"
volume_nome: TESTING
tipo: PROCESSO
secao: 12-Exemplos
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Exemplos

Quatro casos reais deste acervo. Os quatro foram vividos, não construídos para ilustrar.

## Caso 1 — a prova por mutação

Um teste passou a executar os blocos de código de uma seção de documentação. Ele ficou verde na
primeira execução, o que não prova nada. A prova foi trocar, no Markdown, uma asserção sobre o
tamanho de um catálogo — de `37` para `99`:

```
1 failed, 1 passed
```

E, depois de restaurar o texto, conferir que voltou ao verde. Menos de um minuto de trabalho, e é a
única coisa que distingue aquele teste de um enfeite. Repare que o resultado da mutação mostra
`1 failed, 1 passed` — o segundo teste do arquivo, o que exige que os blocos existam, continuou
passando, e é o guarda contra o modo de falha do próprio teste.

## Caso 2 — a asserção que passava por acidente

Um teste verificava que, depois de recusar um palpite, a lista de palpites ficava **vazia**. Passava
há semanas. Ao acrescentar o termo `loja` a uma tabela de detecção, a frase-fixture — "aplicativo de
celular para os pedidos da loja" — passou a gerar dois palpites, e o teste caiu.

O teste estava certo em cair, e o nome dele dizia o que ele queria provar: recusar remove da
pendência sem aplicar nada. A asserção correta é sobre **o palpite recusado**, não sobre a lista
ficar vazia. A correção foi essa, com a razão registrada no código, e não afrouxar a exigência.

## Caso 3 — a suíte verde que não cobria o dado

Dezesseis testes cobriam um motor de detecção: fronteira de palavra nos dois lados, acento
preservado, evidência contida no texto original, palpites da mesma frase com evidências distintas.
Todos verdes. E "loja online que vende tênis e aceita pix" saía **sem contexto nenhum**, porque a
tabela conhecia `checkout` e `carrinho` e não conhecia `pix`, `boleto` nem `loja`.

O mecanismo estava impecavelmente testado. O dado, não. É a regra T9, e o defeito foi encontrado
rodando a interface — não pela suíte.

## Caso 4 — o teste de fronteira que precisa dos dois lados

Ao acrescentar `pix`, um risco novo entrou junto: termo de três letras casa dentro de outras
palavras. Um editor de imagem que fala em `pixel` não é uma loja. O teste que cobre isso é a asserção
**negativa**:

```
assert detectar_contextos("editor que ajusta cada pixel da imagem") == ()
```

Sem ele, a proteção de fronteira de palavra seria intenção, não controle. E é o tipo de falso
positivo que passaria despercebido, porque produz um resultado plausível a partir da evidência
errada.
