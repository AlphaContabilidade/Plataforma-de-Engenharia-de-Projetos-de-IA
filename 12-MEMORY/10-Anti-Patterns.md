---
volume: "12"
volume_nome: MEMORY
tipo: ENGINE
secao: 10-Anti-Patterns
status: PRONTO
atualizado_em: 2026-07-30
---

# Anti-padrões

Cada anti-padrão abaixo corresponde, pelo identificador, a uma prática de
[`09-Boas-Praticas.md`](09-Boas-Praticas.md). A descrição diz o que o comportamento produz,
e não apenas que ele é ruim: anti-padrão sem consequência observável é gosto pessoal
disfarçado de norma. Os três primeiros são os defeitos reais que motivaram o componente,
descritos como padrão — o custo é conhecido porque foi pago.

## A1. Guardar decisão sem guardar de onde ela veio

Uma memória com chave, decisão e data, sem procedência, parece completa e não é. No momento
em que duas fontes discordam, nada distingue uma da outra, e a resposta passa a ser a da
fonte consultada primeiro. O padrão observado em produção foi exatamente esse: uma base
curada e congelada numa data passada contradizia o histórico do que havia sido observado em
quatro de quatro itens conferidos, e o sistema não emitia sinal algum. A precedência
existia — estava na ordem das linhas de código, onde ninguém a lê como decisão. A
contradição foi descoberta por conferência manual, semanas depois de começar.

## A2. O sistema lê a própria escrita como evidência independente

Este é o anti-padrão mais caro do volume, porque ele **melhora os números** enquanto piora
o resultado. A automação decide, escreve no sistema de registro, e a base de histórico é
regenerada depois lendo aquele mesmo sistema — inclusive as linhas que a automação acabou de
gravar. Na rodada seguinte, ela encontra várias ocorrências concordantes, calcula
dominância alta e se autoconfirma. Nenhum limiar protege: o número sobe porque a amostra é o
próprio eco. Uma decisão errada fica mais confiante a cada rodada, e o sinal de erro
desaparece exatamente quando o erro se consolida. O agravante é que o eco também **silencia
contradição** — bastam algumas escritas concordando com a base congelada para que a
discordância com a observação real deixe de aparecer.

## A3. Tratar evidência que não decide como se decidisse

O padrão tem duas formas e as duas custam. A primeira é devolver um valor vazio ambíguo para
dois estados diferentes — "não há evidência" e "há evidência que não basta" — deixando o
chamador sem como distinguir e sem como saber por quê. A segunda é devolver a alternativa
mais frequente com um rótulo de confiança baixa, o que soa prudente e não é: quem recebe uma
decisão não confere de novo, e o rótulo não sobrevive à primeira planilha. A formulação mais
dura desse anti-padrão vem da operação de origem, e vale citar: fechar a conta escolhendo
uma categoria genérica para o saldo bater é inventar. O componente responde com um resultado
indeciso de primeira classe, e a justificativa carrega o número que faltou.

## A4. Baixar o limiar até a fila de pendências caber no dia

O limiar de dominância é uma afirmação sobre o custo relativo entre errar e esperar.
Ajustá-lo para baixo porque a fila cresceu troca uma conta de domínio por uma conta de
agenda, e o efeito é invisível no painel: a taxa de indecisão melhora, a taxa de erro piora,
e a segunda não é medida porque medir erro exige conferência que ninguém faz quando a
decisão veio pronta.

## A5. Deixar `evidencia` vazio porque não entra em contagem

O campo não afeta número nenhum, então parece supérfluo. O custo aparece na triagem: sem o
texto do que sustentou a decisão, resolver uma contradição exige reconstruir o contexto de
uma decisão tomada semanas antes, e a reconstrução ou custa horas ou termina em palpite.

## A6. Ampliar a janela até a resposta virar

A expiração é calculada por consulta, então mudar `janela_dias` muda veredictos sem mudar o
armazém. Ampliar depois de ver um resultado indesejado revive evidência antiga até a
dominância inverter. O número resultante é reproduzível, defensável em revisão e mede apenas
a preferência de quem ampliou — o pior tipo de defeito, porque não parece defeito.

## A7. Resolver a pendência só no sistema de destino

Quando a pessoa decide fora da memória, o trabalho humano não acumula: a mesma chave volta
como pendência na rodada seguinte, e a decisão anterior não tem como vencer, porque não está
registrada. Pior, se o sistema de destino é relido como fonte de observação, a decisão
humana volta disfarçada de observação e perde a precedência que merecia.

## A8. Ler o armazém direto porque `resolver` parece pesado

Chamar `dominancia` e comparar com um limiar à mão salta o descarte do eco, a expiração e a
detecção de contradição. É o anti-padrão A1 e A2 reintroduzidos com aparência de otimização,
e o caminho é atraente justamente porque devolve um número imediatamente.

## A9. Deixar marcador de trabalho inacabado no volume

Um volume que carrega `TODO`, `TBD` ou `FIXME` no corpo afirma estar documentado e não está.
O leitor descobre depois de ter tomado uma decisão com base no texto. O escape legítimo é
citar o marcador dentro de fonte de código, como estes parágrafos fazem — a regra
`marcador-proibido` remove trechos entre acentos graves antes de procurar. O escape existe
porque esta seção precisa nomear o que proíbe, e a contrapartida é que ele não serve para
contrabandear pendência: uma frase que promete conteúdo futuro continua sendo conteúdo
faltante, e essa é uma checagem que só a auditoria humana faz.

## A10. Silenciar o relatório de contradição com uma decisão humana

Registrar decisão humana faz a precedência ignorar a contradição, e é tentador tratar isso
como resolução. Não é: a base congelada continua discordando, a `Contradicao` continua sendo
emitida, e a fonte errada continua alimentando outras chaves. Usar a decisão humana como
tapa-buraco troca um problema de fonte por um trabalho manual recorrente, que cresce com o
número de chaves afetadas.
