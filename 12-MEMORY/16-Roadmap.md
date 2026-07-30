---
volume: "12"
volume_nome: MEMORY
tipo: ENGINE
secao: 16-Roadmap
status: PRONTO
atualizado_em: 2026-07-30
---

# Roadmap

O componente entregue neste volume é completo para o que declarou fazer, e as evoluções abaixo
são extensões conhecidas, não lacunas. Cada uma está descrita com o que acrescenta e com a razão
de não ter entrado agora — item de roadmap sem essa razão é apenas uma lista de desejos.

| Evolução | O que acrescenta | Por que não entrou agora |
|---|---|---|
| Persistência do armazém | Guardar entradas fora da memória do processo, para que a trilha sobreviva a reinício | Exige decisão de formato e de local que pertence ao volume de banco de dados; a interface pública não muda quando a persistência entrar, porque `MemoriaObservada` já expõe apenas verbos |
| Lista de valores-marcador de ausência | Recusar também os valores que, num domínio específico, significam "não sei" sem dizer — na operação de origem havia uma categoria genérica que não ensinava nada | O conjunto desses valores é conhecimento do domínio de quem usa, e fixar a lista aqui seria decidir por todos os domínios; a metade que **não** depende de domínio — a decisão em branco literal — já saiu do roadmap e está implementada, ver abaixo |
| Janela por origem | Permitir que a base congelada expire em prazo diferente do da observação | Hoje a janela é uniforme e a uniformidade é uma regra só, testável; prazo por origem é a decisão de validade do documento, que pertence ao volume vizinho de conhecimento |
| Peso por evidência | Deixar uma observação valer mais que outra segundo a qualidade do sinal | Ponderar transforma dominância em escore, e escore precisa de calibração própria; sem essa calibração, o peso seria opinião com aparência de número |
| Trilha de veredictos | Guardar cada veredicto emitido, com data e parâmetros, para medir deriva da própria memória | As métricas de [`14-Metricas.md`](14-Metricas.md) hoje se calculam por instrumentação de quem chama; gravar veredicto dentro do componente o tornaria escritor, e escritor tem de decidir onde escreve |
| Fechamento de contradição por revisão | Marcar uma contradição como examinada, sem apagá-la | Depende de existir a curadoria da fonte no volume 11; um estado de examinada criado aqui viraria, na prática, o botão de silenciar que a regra R3 proíbe |

## O item que era um e virou dois: decisão em branco

A auditoria independente do volume desmontou este item, e com razão. Ele tratava como uma coisa
só duas que não são: a **string vazia ou só espaço**, que não é marcador de domínio nenhum, e a
**lista de valores que significam ausência** em cada operação. A justificativa de conhecimento
do domínio vale para a segunda e não vale para a primeira — recusar branco é a mesma verificação
que `ChaveInvalida` já fazia na chave, e a assimetria era indefensável: `Entrada(chave="k",
decisao="")` entrava como alternativa legítima, somava contagem, podia empatar com uma decisão
real e chegar ao chamador dentro de um veredicto de confiança alta.

A metade sem dependência de domínio saiu do roadmap na incorporação desta auditoria.
`_decisao_valida` normaliza a borda e levanta `DecisaoInvalida`, irmã de `ChaveInvalida` e não
subclasse dela, com três casos de teste em
[`13-Testes.md`](13-Testes.md) e a regra registrada como extensão de R10 em
[`07-Regras.md`](07-Regras.md). A metade restante — a lista de valores-marcador — continua na
tabela acima com a justificativa original intacta, porque ali a razão de não entrar é real:
qualquer lista que este volume fixasse seria a lista de um domínio imposta a todos os outros.

## Ligação com os volumes 11, 13 e 15

O volume 11, `KNOWLEDGE`, é a fonte da origem `BASE_CONGELADA`. Este componente sabe apenas a
data do congelamento e nunca julga se o documento continua válido; quem decide autoridade,
validade e recuratoria é aquele volume. A direção da dependência é de fora para dentro — a
memória consome entradas e devolve contradições — e é ela que impede ciclo: se a memória
decidisse quando a base expira, registrar uma entrada passaria a exigir uma decisão de
curadoria, e nenhum dos dois volumes poderia ser lido primeiro.

O volume 13, `RAG`, entra onde a igualdade de chave falha. Aqui a chave é identidade exata, e
uma chave nova simplesmente não tem evidência; recuperar por proximidade é o que permite
aproveitar decisões de chaves parecidas, e aquele volume traz consigo o ranqueamento e a métrica
de fidelidade que este não tem. O volume 15, `CONTEXT`, consome o veredicto como um item
candidato a entrar na janela do modelo: um veredicto é pequeno de propósito, e a trilha completa
de uma chave não é — decidir quanto da trilha cabe no prompt é problema de orçamento, não de
memória.

A consequência prática para quem for escrever esses três volumes é que nada aqui precisa mudar
para acomodá-los. O ponto de extensão do 11 é a origem `BASE_CONGELADA` e o relatório de
contradição; o do 13 é a chave; o do 15 é o `Veredicto`. Se algum deles exigir alteração na
interface pública descrita em [`08-Modelos.md`](08-Modelos.md), a fronteira declarada em
[`03-Escopo.md`](03-Escopo.md) foi desenhada errado, e a revisão precisa acontecer aqui antes de
ser contornada lá.
