---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 10-Anti-Patterns
status: PRONTO
atualizado_em: 2026-07-29
---

# Anti-padrões

Os anti-padrões de `A1` a `A8` correspondem, pelo identificador, à prática de mesmo número em
[`09-Boas-Praticas.md`](09-Boas-Praticas.md). `A9` e `A10` **não têm par**, de propósito: eles
descrevem falhas de processo em torno do motor, não o uso errado de uma prática dele, e
inventar uma prática só para completar a simetria seria norma criada para caber na tabela. A
descrição diz o que o comportamento produz, e não apenas que ele é ruim: um anti-padrão sem
consequência observável é gosto pessoal disfarçado de norma.

## A1. Declarar tudo como texto

`Variavel("quantidade", str)` aceita qualquer coisa que já seja texto e desliga a
verificação sem avisar. O defeito aparece longe da causa: o modelo recebe `"12,5"` onde
esperava um inteiro, responde algo plausível, e a falha vira uma discussão sobre a
qualidade do prompt quando era um problema de tipo na chamada.

## A2. Escrever o caso de ouro depois de ver a saída

Formular a expectativa a partir da resposta obtida produz uma bateria que aprova o presente
por construção. Ela nunca reprova nada, dá a sensação de cobertura e falha exatamente no
momento em que seria útil, porque foi calibrada para o comportamento atual e não para o
comportamento correto.

## A3. Comparar por igualdade literal

Exigir a resposta exata faz o teste quebrar quando o modelo troca uma vírgula. O custo real
não é o alarme falso: é que baterias que dão alarme falso são desligadas, e a partir daí o
motor tem gate no papel e nenhum gate na prática.

## A4. Promover porque "ficou melhor"

Promover sem comparar sobre a mesma amostra é substituir medição por memória. O caso mais
caro é a troca que melhora dois casos e piora cinco, imperceptível para quem só conferiu o
exemplo que motivou a mudança.

## A5. Corrigir o prompt sem reproduzir o incidente

Reescrever o corpo depois de uma falha que não reproduz na bateria gasta uma versão do
histórico, muda o comportamento em direção desconhecida e deixa a causa real — quase sempre
no executor, no provedor ou nos dados — intacta para reaparecer.

## A6. Numerar a versão à mão

Manter um contador manual reintroduz o erro que o hash elimina. Duas pessoas incrementam
para o mesmo número, ou ninguém incrementa, e o histórico deixa de identificar o que rodava.

## A7. Renomear o prompt para "reorganizar"

O nome é a chave do agrupamento. Renomear zera a numeração, deixa a trilha anterior órfã e
faz `promovida` devolver vazio para o nome novo, o que muda o comportamento de `obter` sem
versão em produção.

## A8. Acoplar o motor a um provedor específico

Importar um cliente de modelo dentro do avaliador torna a bateria dependente de rede e de
crédito. O efeito prático conhecido é o gate ser marcado como opcional para não travar a
esteira, e a partir daí prompt sem evidência chega à produção.

## A9. Deixar marcador de trabalho inacabado no volume

Um volume que carrega `TODO`, `TBD` ou `FIXME` no corpo afirma estar documentado e não está.
O leitor descobre isso depois de tomar uma decisão com base no texto, o que é pior do que
não ter encontrado seção alguma.

Este parágrafo é o exemplo do escape, e ele é deliberado. A regra `marcador-proibido` do
validador reprova esses marcadores em prosa, mas remove os trechos entre acentos graves
antes de procurar. Escrever o marcador dentro de um trecho de código é, portanto, a forma
legítima de falar sobre ele — e é exatamente o que os parágrafos acima fazem. O escape
existe porque esta seção precisa nomear o que proíbe: uma regra que impedisse a própria
documentação de citar o termo forçaria a descrição por paráfrase, e paráfrase não permite ao
leitor reconhecer o marcador quando o encontrar. A contrapartida é que o escape não pode ser
usado para contrabandear pendência: um trecho de código com o marcador dentro de uma frase
que promete conteúdo futuro continua sendo conteúdo faltante, ainda que o validador não o
detecte. Essa é uma checagem que só a auditoria humana faz.

## A10. Tratar bateria vazia como aprovação

Um avaliador que devolvesse taxa de acerto igual a um para uma lista vazia de casos
promoveria todo prompt que ninguém testou, e o faria justamente nos prompts novos, que são
os mais arriscados. O motor devolve zero nesse caso, e a decisão está registrada como a
regra R8 em [`07-Regras.md`](07-Regras.md).
