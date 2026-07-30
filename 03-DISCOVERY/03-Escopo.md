---
volume: "03"
volume_nome: DISCOVERY
tipo: PROCESSO
secao: 03-Escopo
status: PRONTO
atualizado_em: 2026-07-30
---

# Escopo

Este volume conduz **da ideia à especificação**, e não um passo além. A fronteira é declarada
aqui de forma explícita porque a plataforma tomou a decisão, registrada em
[`../ROADMAP.md`](../ROADMAP.md), de manter os quarenta e dois volumes e resolver sobreposição
por fronteira em vez de fusão. Este é um dos casos em que a decisão custa mais caro: quatro
volumes tratam do que acontece antes de a primeira linha ser escrita, e sem fronteira declarada
os quatro produzem a mesma lista de perguntas com nomes diferentes, divergindo em silêncio.

## Dentro do escopo

Está dentro do escopo o catálogo de lacunas — universais e condicionais — com a condição que
torna cada uma relevante e o motivo declarado de cada pergunta. Está dentro do escopo a
inferência de plataforma e de contexto a partir do texto inicial, sempre acompanhada do trecho
que a produziu. Está dentro do escopo o controle da conversa: qual pergunta vem agora, por que
ela vem agora, o que uma resposta destrava, e quando a próxima pergunta deixa de valer o turno.
Está dentro do escopo a especificação de saída com três listas separadas — decidido, aberto,
inferido e não confirmado — e a propriedade que se recusa a declará-la completa quando não está.

## Fora do escopo, e de quem é

| Assunto | Volume responsável | Por que não é aqui |
|---|---|---|
| Elicitação formal e rastreabilidade de requisito: transformar cada decisão em requisito numerado, ligá-lo a critério de aceite e a teste, e manter a matriz de rastreabilidade quando o requisito muda | 04, `REQUIREMENTS` | Aqui a saída é uma decisão tomada com procedência, e nada mais. Requisito rastreável pressupõe que já se sabe o que registrar; descobrir é decidir o que perguntar quando ainda não se sabe. Trazer a matriz para cá faria o motor de descoberta responder por consistência entre requisitos que ele não escreveu |
| Modelo de negócio e viabilidade: quanto custa construir, quanto se espera receber, se compensa fazer, e qual alternativa de compra existe | 05, `BUSINESS` | Este volume não tem opinião sobre a ideia valer a pena. Ele pergunta "como se sabe que funcionou" e registra a resposta; julgar se a resposta justifica o investimento é decisão de negócio, e um instrumento de entrevista que a emitisse estaria opinando disfarçado de coletar |
| Planejamento de entrega: sequência, dependência entre tarefas, estimativa, alocação e data | 38, `PROJECT-PLANNER` | O peso de uma lacuna é valor informativo, e **não** prioridade de execução nem esforço. Confundir os dois é o erro que transforma o catálogo em plano de projeto: a pergunta mais informativa costuma ser a mais barata de responder, e a mais cara de implementar raramente é a mais incerta |
| Contrato, versionamento e avaliação de prompt do modelo que conduz a conversa | 07, `PROMPT-ENGINE` | Assunto disjunto. Este motor é determinístico e não chama modelo nenhum; quando alguém colocar um modelo na frente dele, o contrato desse prompt é lá. A fronteira daquele volume está em [`../07-PROMPT-ENGINE/03-Escopo.md`](../07-PROMPT-ENGINE/03-Escopo.md) e serve de implementação de referência para esta seção |
| Memória entre sessões: lembrar o que uma entrevista anterior decidiu e resolver discordância entre duas fontes | 12, `MEMORY` | A entrevista deste volume vive numa sessão. O conceito de origem vem de lá, e o veredicto indeciso de primeira classe também; persistir e decidir precedência entre origens que discordam é o assunto daquele volume, e sua fronteira está em [`../12-MEMORY/03-Escopo.md`](../12-MEMORY/03-Escopo.md) |
| Desenho de tela, texto de interface e acessibilidade do instrumento de entrevista | 22, `FRONTEND-ARCHITECT` | O motor devolve a pergunta, o motivo e as opções. Como isso aparece é outra camada, e ela pode ser conversa de texto, formulário de uma pergunta por vez ou voz sem que nada aqui mude |

A tabela é a fronteira operacional e também declara a direção do fluxo. O volume 04 é o
**consumidor** natural da especificação: ele recebe as decisões e as decisões abertas e as
converte em requisito. O volume 05 consome a mesma saída para julgar viabilidade. O 38 consome a
lista de decisões abertas como risco de planejamento — decisão aberta é exatamente a coisa que
pode mudar uma estimativa depois de ela ter sido dada. Nenhum dos três é pré-requisito de
leitura hoje, e por isso `depende_de` está vazio; a razão completa está em
[`18-Referencias-Cruzadas.md`](18-Referencias-Cruzadas.md).

## Fronteira interna do próprio volume

Dentro do volume a separação também é declarada, e ela tem um custo aceito. O catálogo não
ordena e não decide; a detecção não confirma nada; o controle não formata saída; a especificação
não pergunta. Quem chamar `lacunas_ativas` esperando a lista já priorizada recebe a ordem do
catálogo, que não é ordem de entrevista. O ganho é que a política de priorização fica num lugar
com nome — `Entrevista._ordenar` — em vez de embutida numa função cujo nome promete apenas
filtrar. Foi filtragem embutida e não declarada que produziu o defeito descrito no volume 12, e
a lição atravessa o assunto.
