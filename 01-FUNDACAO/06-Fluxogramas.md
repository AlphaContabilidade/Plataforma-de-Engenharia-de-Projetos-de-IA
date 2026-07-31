---
volume: "01"
volume_nome: FUNDACAO
tipo: GOVERNANCA
secao: 06-Fluxogramas
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Fluxogramas

O fluxo que este volume governa não é o de escrever um volume — esse está em
[`05-Diagramas.md`](05-Diagramas.md). É o fluxo menor e mais frequente: alguém afirma alguma coisa, e
essa afirmação precisa virar fato do acervo ou pendência declarada. Acontece dezenas de vezes por
volume, e é onde a disciplina se ganha ou se perde.

```mermaid
flowchart TD
    START([alguem afirma algo]) --> Q1{tem procedencia?}
    Q1 -->|nao| PEND[lacuna declarada com a pergunta em aberto]
    Q1 -->|sim| Q2{a procedencia e execucao?}
    Q2 -->|sim| Q3{o comando esta escrito junto da afirmacao?}
    Q3 -->|nao| FIX[escrever o comando e o escopo dele]
    FIX --> Q3
    Q3 -->|sim| Q4{quem le consegue rodar e ver o mesmo?}
    Q4 -->|nao| RISK[afirmacao verdadeira que le como falsa]
    RISK --> REW[reescrever separando o medido do que aparece]
    REW --> Q4
    Q4 -->|sim| FATO([fato do acervo])
    Q2 -->|nao| Q5{e inferencia?}
    Q5 -->|sim| Q6{a evidencia que a produziu esta junto?}
    Q6 -->|nao| PEND
    Q6 -->|sim| CONF{alguem confirmou?}
    CONF -->|nao| PEND
    CONF -->|sim| FATO
    Q5 -->|nao| Q7{foi decidido por humano?}
    Q7 -->|sim| FATO
    Q7 -->|nao| PEND
```

Sete pontos de decisão, e vale ler dois deles com atenção porque são os que custaram correção real.

O ponto `Q4` — "quem lê consegue rodar e ver o mesmo?" — não é redundante com `Q3`. Uma seção deste
acervo afirmava que a suíte roda em menos de dois décimos de segundo. Era **verdade** sobre os corpos
de teste, medida com ferramenta adequada, e mesmo assim quem rodava o comando via dezessete segundos
na tela e concluía que o texto mentia. Afirmação verdadeira que o leitor não consegue confirmar tem o
mesmo efeito prático de uma falsa, e por isso o fluxo tem um estado chamado exatamente assim.

O ponto `CONF` é o que impede o modo de falha mais caro da inferência: um palpite plausível que
ninguém recusou vira, três passos depois, um requisito que ninguém pediu. A saída dele para a lacuna
declarada não é punição — lacuna declarada é um resultado legítimo e barato.
