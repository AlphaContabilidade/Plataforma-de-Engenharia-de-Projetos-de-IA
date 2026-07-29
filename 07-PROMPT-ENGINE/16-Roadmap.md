---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 16-Roadmap
status: RASCUNHO
atualizado_em: 2026-07-29
---

# Roadmap

O motor entregue neste volume é completo para o que declarou fazer, e as evoluções abaixo são
extensões conhecidas, não lacunas. Cada uma está descrita com o que ela acrescenta e com a razão
de não ter entrado agora — item de roadmap sem essa razão é apenas uma lista de desejos.

| Evolução | O que acrescenta | Por que não entrou agora |
|---|---|---|
| Persistência do registro | Guardar versões e estados fora da memória do processo, para que o histórico sobreviva a reinício | Exige decisão de formato e de local que pertence ao volume de banco de dados; a interface pública do registro não muda quando a persistência entrar |
| Metadados de avaliação no registro | Guardar taxa de acerto e data ao lado da versão, em vez de manter o resultado fora | Aproximaria registro e avaliador, e a separação entre os dois é uma decisão de arquitetura registrada em [`04-Arquitetura.md`](04-Arquitetura.md) |
| Limiar de promoção declarado | Expressar o limiar como dado em lugar de convenção do operador | O limiar depende do domínio de cada prompt; declará-lo cedo produziria um número arbitrário aplicado a todos |
| Envelope de instrumentação do executor | Medir custo e latência sem que quem opera precise escrever o envelope | É código de dez linhas com dependência zero, mas altera o contrato do executor e merece decisão explícita |

## Ligação com os volumes 28 e 29

O volume 28, `PROMPT-COMPILER`, consome o contrato deste motor e produz, a partir de um mesmo
`PromptTemplate`, as formas concretas exigidas por dialetos de provedores diferentes. A direção
da dependência é essa e não a inversa: o compilador precisa do contrato para saber o que
compilar, enquanto o motor funciona sem compilador algum. O volume 29, `PROMPT-OPTIMIZER`,
consome o avaliador como função objetivo de um laço de busca sobre variações do corpo. Também
aqui a direção é de fora para dentro, e é ela que impede ciclo — se o motor chamasse o
otimizador, registrar uma versão passaria a depender de uma busca, e nenhum dos dois volumes
poderia ser lido primeiro.

A consequência prática para quem for escrever esses dois volumes é que nada neste motor precisa
mudar para acomodá-los. O ponto de extensão do 28 é o par corpo e assinatura; o ponto de extensão
do 29 é `avaliar`, que já recebe template e casos de fora. Se algum dos dois exigir alteração na
interface pública descrita em [`08-Modelos.md`](08-Modelos.md), a fronteira declarada em
[`03-Escopo.md`](03-Escopo.md) foi desenhada errado e a revisão precisa acontecer aqui, no volume
07, antes de ser contornada lá.
