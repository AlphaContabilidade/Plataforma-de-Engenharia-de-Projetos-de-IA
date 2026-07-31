---
volume: "01"
volume_nome: FUNDACAO
tipo: GOVERNANCA
secao: 13-Testes
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Testes

Este volume não tem exemplo de código próprio: ele governa o acervo, e o código que o realiza mora em
`ferramentas/`, verificado pela suíte da plataforma. O comando com escopo é este, e o escopo é
deliberado — sem ele o número somaria os exemplos de todos os volumes e cresceria a cada volume novo.

```
python -m pytest ferramentas/tests -q
```

## O que prova que os controles funcionam

**C1** é coberto por testes que constroem volumes sintéticos violando cada regra isoladamente: seção
faltando, seção curta demais, marcador proibido, diagrama exigido ausente. A asserção que importa em
cada um é **negativa** — que o validador reprova —, porque a positiva passaria também num validador
que aprovasse tudo.

Os três testes de fronteira de palavra do marcador merecem menção: eles fixam que o termo isolado é
recusado, que a palavra que o contém é aceita, e que a distinção sobrevive a maiúsculas e acento. Sem
o terceiro, a correção do Caso 1 valeria só para a grafia exata que apareceu no defeito.

**C2 e C3** são cobertos com arquivos que existem e arquivos que não existem, nos dois sentidos. O
caso interessante é o link relativo que sobe de diretório: resolver errado aqui produziria links
mortos aprovados, que é a forma mais silenciosa de A4.

**C4** tem teste de ciclo direto e de ciclo indireto de três volumes. O indireto é o que importa —
ciclo de dois é visível a olho nu numa revisão, e o de três não é.

**C6 e C7** são cobertos pelo lado da leitura: a escolha do relatório mais recente tem seis testes,
incluindo os dois casos do Caso 2, e a exigência de entrada no `CHANGELOG` é verificada contra um
arquivo sem a data esperada.

## O que os testes não cobrem, e por quê

**C8 não tem teste**, e não é omissão: um teste que lesse número por extenso em prosa portuguesa
precisaria de um analisador de linguagem natural cuja correção seria menos verificável que o problema
que ele resolve. A dívida está declarada na matriz e em [`16-Roadmap.md`](16-Roadmap.md).

Também não há teste de **qualidade** de prosa. Se uma seção está bem escrita é julgamento, e
julgamento é assunto de C6, feito por outro modelo, em sessão separada.
