---
volume: "12"
volume_nome: MEMORY
tipo: ENGINE
secao: 03-Escopo
status: RASCUNHO
atualizado_em: 2026-07-30
---

# Escopo

Este volume trata de **duas coisas, e só duas**: o armazém de decisões observadas — com a
procedência de cada uma — e a regra de precedência entre origens que discordam. A
fronteira é declarada aqui de forma explícita porque a plataforma tomou a decisão,
registrada em [`../ROADMAP.md`](../ROADMAP.md), de manter os quarenta e dois volumes e
resolver sobreposição por fronteira em vez de fusão. Fronteira ausente é lacuna de
conteúdo, não economia de texto: no grupo de conhecimento e contexto há quatro volumes com
assunto adjacente, e sobreposição não declarada produz duas implementações do mesmo
comportamento que divergem em silêncio.

## Dentro do escopo

Está dentro do escopo o registro de uma decisão com chave, decisão, origem, data e texto
de evidência, e a garantia de que chave em branco não entra. Está dentro do escopo a
contagem crua por decisão e a dominância sobre essa contagem. Está dentro do escopo a
separação entre evidência e eco: descartar o que o próprio agente escreveu e devolver a
quantidade descartada. Está dentro do escopo detectar e **reportar** a contradição entre
uma base congelada e a decisão dominante observada, sem escolher lado. Está dentro do
escopo a regra de precedência, a expiração por janela de dias, o limiar de dominância, a
detecção de empate e o veredicto indeciso com justificativa numérica.

## Fora do escopo, e de quem é

| Assunto | Volume responsável | Por que não é aqui |
|---|---|---|
| Curadoria da base congelada: de onde ela vem, quem tem autoridade para escrevê-la, quando ela expira como documento e como é reingerida | 11, `KNOWLEDGE` | Este volume trata a base congelada como uma origem entre outras e sabe apenas a data do congelamento. Decidir se o documento continua válido é julgamento de autoridade sobre a fonte, e trazê-lo para cá faria a memória opinar sobre a legitimidade do que ela apenas registra |
| Recuperação de entrada por similaridade: encontrar a decisão parecida quando a chave exata não existe | 13, `RAG` | Aqui a chave é identidade exata e a consulta é determinística. Casar por proximidade introduz ranqueamento, e ranqueamento tem métrica de qualidade própria que não é dominância |
| Orçamento da janela de contexto: o que entra no prompt, em que ordem e o que é descartado por falta de espaço | 15, `CONTEXT` | O que este volume produz é um veredicto pequeno. Decidir quanto do histórico cabe na janela do modelo é problema de orçamento, e vale mesmo em sistema que não tenha memória de decisões |
| Índice vetorial, embedding e métrica de similaridade | 14, `VECTOR` | Nenhuma estrutura daqui é vetorial; a busca é por igualdade de chave |
| O laço de agente que consome o veredicto e age sobre ele | 08, `AGENT-ENGINE` | O agente é consumidor: ele pergunta e recebe decisão ou pendência. A memória não conhece o laço nem executa a ação |
| Contrato, versionamento e avaliação de prompt | 07, `PROMPT-ENGINE` | Assunto disjunto; a fronteira daquele volume está em [`../07-PROMPT-ENGINE/03-Escopo.md`](../07-PROMPT-ENGINE/03-Escopo.md) e serve de implementação de referência para esta seção |

A tabela é a fronteira operacional e também declara a direção da dependência. O volume 11
é a **fonte** da origem `BASE_CONGELADA`, e este volume a consome sem conhecer a curadoria;
o volume 13 consome chaves para recuperar por proximidade quando a igualdade falha; o
volume 15 consome o veredicto como um item candidato a entrar na janela. Nenhum deles é
pré-requisito de leitura hoje, e por isso `depende_de` está vazio — a razão está em
[`18-Referencias-Cruzadas.md`](18-Referencias-Cruzadas.md).

## Fronteira interna do próprio volume

Dentro do volume, o armazém não filtra e não decide, a guarda não decide, e quem decide
não conhece o formato de armazenamento. `MemoriaObservada.dominancia` devolve número cru,
incluindo o eco; limpar é `filtrar_contaminacao`; decidir é `resolver`. A separação é
deliberada e tem um custo aceito: quem chamar `dominancia` diretamente, esperando um
número limpo, lê um número contaminado. O ganho é que a filtragem fica visível como um
passo com nome, testável isoladamente, em vez de embutida na contagem — e foi justamente
uma filtragem embutida e não declarada que produziu a contradição resolvida por acidente
no sistema de onde este componente saiu.
