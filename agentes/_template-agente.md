# Template de especificação de agente

> Biblioteca transversal · atualizado em 2026-07-29
> Copie este arquivo para `agentes/<nome-do-agente>.md` e preencha as **13 rubricas**.
> Rubrica sem conteúdo real **não é preenchida com texto genérico** — é declarada vazia com
> a razão, como em [`frameworks/_backlog.md`](../frameworks/_backlog.md).

## Como usar este template

As 13 rubricas abaixo vêm da especificação original da plataforma e não são negociáveis em
número nem em nome — um catálogo de agentes só é comparável se todos os agentes forem
descritos pelas mesmas rubricas. O que varia é a profundidade.

Três regras de preenchimento:

1. **Rubrica é contrato, não descrição.** Se *Saídas* diz "JSON com as chaves x, y, z", esse
   é o contrato que o consumidor pode exigir. Escreva o que se pode cobrar, não o que se
   espera.
2. **`Limitações` é a rubrica mais importante e a mais deixada de lado.** Um agente sem
   limitações declaradas é um agente que será usado fora do escopo por quem não sabia que
   havia escopo. Se ela estiver curta, o agente não foi entendido.
3. **Rubrica vazia se declara.** "*Memória*: este agente não tem memória entre execuções, de
   propósito — cada auditoria precisa ser independente da anterior" é conteúdo. "*Memória*:
   utiliza memória de contexto para melhor desempenho" não é.

O teste rápido de qualidade da especificação: **outra pessoa consegue prever a saída do
agente lendo só o arquivo, sem executá-lo?** Se não, falta contrato em algum lugar.

---

## 1. Missão

Uma frase que diga **por que este agente existe** e o que ele produz que ninguém mais
produz. Se a missão pudesse ser cumprida por um agente já existente no
[`_catalogo.md`](_catalogo.md), o agente não deveria existir — e essa comparação é parte da
rubrica.

Evite missão que descreve atividade ("analisar código"); escreva missão que descreve
resultado ("dizer se a mudança pode ser promovida, e por quê").

## 2. Objetivos

De 2 a 5 objetivos **verificáveis**, em lista. Cada objetivo precisa admitir a pergunta
"como se sabe que foi cumprido?" com resposta concreta. Objetivo cuja verificação é opinião
não é objetivo, é intenção.

Ordene por prioridade e diga explicitamente o que cede quando dois entram em conflito — o
conflito ocorre em produção, e quem decide na hora é quem tiver essa linha.

## 3. Entradas

O que o agente recebe, item por item, com **tipo, obrigatoriedade e o que fazer quando
falta**. Essa terceira coluna é a que evita a falha silenciosa: agente que recebe entrada
incompleta e prossegue produz saída plausível e errada.

| Entrada | Tipo | Obrigatória | Se ausente |
|---|---|---|---|
| … | … | … | … |

Declare também o que o agente **não** recebe e não deve buscar por conta própria. Escopo de
leitura é parte do contrato.

## 4. Saídas

O artefato produzido, com formato e local. Se é arquivo, diga o caminho e a convenção de
nome (com data em ISO `YYYY-MM-DD` quando houver). Se é estrutura de dados, liste as chaves
e os valores admissíveis, chave por chave.

Inclua sempre **a saída para o caso "não foi possível decidir"**. Um agente sem saída
legítima para a incerteza é um agente que vai preencher.

## 5. Ferramentas

As ferramentas às quais o agente tem acesso, e — mais importante — **as que ele não tem**.
Justifique cada restrição pela consequência, não por preferência: "sem escrita em disco
porque o auditor não pode corrigir o que audita" é justificativa; "somente leitura por
segurança" não é.

Se alguma ferramenta tem efeito irreversível, marque-a e diga qual verificação precede o uso.

## 6. Prompts

Onde vive o prompt do agente e como ele é versionado. Se o prompt está embutido na definição
do agente, diga isso; se está em `prompts/`, aponte o caminho.

Registre **por que** o prompt é como é nos pontos não óbvios. Um prompt sem essa nota é
reescrito por quem não sabia que uma frase estranha estava lá para bloquear um modo de falha
concreto — e o modo de falha volta.

## 7. Fluxos

As etapas, em ordem, com a decisão que cada uma toma. É a rubrica que corresponde ao campo
`Steps` do [`RISE.md`](../frameworks/conhecidos/RISE.md), e vale aqui o mesmo alerta: etapa
inventada produz erro sistemático, não aleatório.

Diga o que acontece em cada ramo de falha. Fluxo que só descreve o caminho felizmente bem
sucedido não é especificação de agente — é demonstração.

## 8. Limitações

O que o agente **não** faz, não decide e não garante. Divida em três, porque são naturezas
diferentes:

- **De escopo**: está fora do que ele se propõe.
- **De capacidade**: está dentro do escopo, mas ele faz mal — e é melhor saber antes.
- **De confiança**: ele produz, mas o resultado precisa de verificação independente.

A terceira é a que evita o pior desfecho: saída de agente tratada como fato porque ninguém
disse que não era.

## 9. Memória

O que persiste entre execuções, onde persiste, e por quanto tempo. Se **nada** persiste,
diga e diga por quê — ausência deliberada de memória é uma decisão de projeto com
consequência (independência entre execuções) e não uma lacuna.

Se há memória, responda: quem a escreve, quem a lê, o que acontece quando ela contradiz a
entrada atual, e como ela é invalidada. Memória que nunca é invalidada é a origem de decisão
correta ontem e errada hoje.

## 10. Conhecimento

As fontes de conhecimento que o agente consulta: arquivos do acervo, contrato, volumes,
documentação externa. Diga se são lidas a cada execução ou congeladas no prompt.

**Conhecimento congelado tem data.** Registre-a. Base congelada que contradiz a fonte viva é
um modo de falha real e difícil de perceber, porque o agente responde com a mesma confiança
nos dois casos.

## 11. Eventos

O que dispara o agente (comando, gate, agendamento, outro agente) e o que a execução dele
dispara depois. Inclua o efeito no estado do acervo: que arquivo muda, que status é gravado,
o que passa a ser possível ou impossível depois.

Se o agente pode ser disparado em paralelo consigo mesmo, diga o que impede duas execuções
de colidirem sobre o mesmo arquivo.

## 12. Exemplos

Ao menos **uma** execução real, com entrada e saída verdadeiras — recortadas, se preciso, mas
não fabricadas. Exemplo inventado num arquivo de especificação é pior que exemplo ausente:
ele é lido como comportamento observado.

Se o agente ainda não rodou, escreva "sem execução registrada até <data>" e deixe a rubrica
assim até haver uma. Ver [`exemplos/_template-exemplo.md`](../exemplos/_template-exemplo.md).

## 13. Integrações

Com que outras partes do sistema o agente conversa: comandos, ferramentas Python, arquivos de
estado, outros agentes. Para cada uma, diga a direção (lê, escreve, dispara) e o que quebra
do outro lado se este agente mudar de contrato.

Esta rubrica é o que permite estimar o custo de alterar o agente. Sem ela, toda mudança é
uma aposta.

---

## Checklist antes de publicar a especificação

- [ ] As 13 rubricas estão presentes, com estes nomes e nesta ordem.
- [ ] Nenhuma rubrica foi preenchida com texto genérico; as vazias estão declaradas com razão.
- [ ] *Entradas* diz o que fazer quando cada entrada falta.
- [ ] *Saídas* inclui a saída para "não foi possível decidir".
- [ ] *Limitações* tem as três naturezas (escopo, capacidade, confiança).
- [ ] *Memória* diz como é invalidada — ou que não existe, e por quê.
- [ ] *Conhecimento* congelado tem data.
- [ ] *Exemplos* traz execução real, ou declara que não houve.
- [ ] O agente foi acrescentado ao [`_catalogo.md`](_catalogo.md). Agente fora do catálogo é
      agente que ninguém encontra.
