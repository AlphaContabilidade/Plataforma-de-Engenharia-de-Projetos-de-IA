---
volume: "01"
volume_nome: FUNDACAO
tipo: GOVERNANCA
secao: 02-Objetivos
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Objetivos

Cinco objetivos, cada um com a forma pela qual se sabe que foi atingido. Objetivo sem critério de
verificação é intenção, e este volume trata precisamente da diferença entre as duas coisas.

**1. Tornar a procedência de cada afirmação recuperável.** Toda informação no acervo carrega de onde
veio: respondida por uma pessoa, inferida por um agente, medida por execução, congelada de uma base
externa ou assumida como padrão. *Verificação:* o modelo de `Origem` em [`08-Modelos.md`](08-Modelos.md)
é usado pelos volumes que produzem dados, e `PADRAO_ASSUMIDO` aparecendo numa entrega é defeito, não
detalhe.

**2. Impedir que status minta.** Um volume marcado `PRONTO` com gate vermelho é pior que um volume
`RASCUNHO`, porque desliga a atenção de quem lê. *Verificação:* a Definição de PRONTO em
[`07-Regras.md`](07-Regras.md) tem quatro critérios, três deles com código de saída, e nenhum é
dispensável por urgência.

**3. Separar quem escreve de quem aprova.** *Verificação:* a auditoria de cada volume é feita por um
modelo diferente do que escreveu, em sessão separada, e a nota entra no acervo mesmo quando é baixa —
o relatório da primeira rodada do volume 07, nota 8,5, continua publicado ao lado da segunda.

**4. Tornar cada princípio executável ou declaradamente não executável.** Não há terceira opção. Um
princípio que ninguém consegue verificar entra na matriz de controles com a coluna de verificação
marcada como manual, e essa marca é uma dívida visível, não uma omissão. *Verificação:* a matriz em
[`04-Arquitetura.md`](04-Arquitetura.md) não admite linha com verificação vazia.

**5. Fazer o custo de mentir ser maior que o de admitir.** Este é o objetivo que sustenta os outros
quatro, e o único que não se resolve com ferramenta. *Verificação:* os anti-padrões de
[`10-Anti-Patterns.md`](10-Anti-Patterns.md) descrevem o que a plataforma faz quando a evidência não
decide, e a resposta é sempre a mesma — a lacuna é declarada, e declarar não custa nada além de
disciplina.
