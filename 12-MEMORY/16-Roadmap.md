---
volume: "12"
volume_nome: MEMORY
tipo: ENGINE
secao: 16-Roadmap
status: RASCUNHO
atualizado_em: 2026-07-30
---

# Roadmap

O componente entregue neste volume é completo para o que declarou fazer, e as evoluções abaixo
são extensões conhecidas, não lacunas. Cada uma está descrita com o que acrescenta e com a razão
de não ter entrado agora — item de roadmap sem essa razão é apenas uma lista de desejos.

| Evolução | O que acrescenta | Por que não entrou agora |
|---|---|---|
| Persistência do armazém | Guardar entradas fora da memória do processo, para que a trilha sobreviva a reinício | Exige decisão de formato e de local que pertence ao volume de banco de dados; a interface pública não muda quando a persistência entrar, porque `MemoriaObservada` já expõe apenas verbos |
| Rejeição de decisão em branco | Impedir que uma decisão vazia entre como se fosse uma alternativa legítima | O conjunto de valores que funcionam como marcador de ausência é conhecimento do domínio de quem usa — na operação de origem havia uma categoria genérica que não ensinava nada — e fixar essa lista aqui seria decidir por todos os domínios |
| Janela por origem | Permitir que a base congelada expire em prazo diferente do da observação | Hoje a janela é uniforme e a uniformidade é uma regra só, testável; prazo por origem é a decisão de validade do documento, que pertence ao volume vizinho de conhecimento |
| Peso por evidência | Deixar uma observação valer mais que outra segundo a qualidade do sinal | Ponderar transforma dominância em escore, e escore precisa de calibração própria; sem essa calibração, o peso seria opinião com aparência de número |
| Trilha de veredictos | Guardar cada veredicto emitido, com data e parâmetros, para medir deriva da própria memória | As métricas de [`14-Metricas.md`](14-Metricas.md) hoje se calculam por instrumentação de quem chama; gravar veredicto dentro do componente o tornaria escritor, e escritor tem de decidir onde escreve |
| Fechamento de contradição por revisão | Marcar uma contradição como examinada, sem apagá-la | Depende de existir a curadoria da fonte no volume 11; um estado de examinada criado aqui viraria, na prática, o botão de silenciar que a regra R3 proíbe |

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
