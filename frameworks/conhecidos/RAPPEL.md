# RAPPEL — sigla sem expansão padronizada

> Técnica pública de estruturação de prompt · atualizado em 2026-07-30
> **Estado de atribuição:** `DOMINIO-PUBLICO-SEM-ATRIBUICAO-SEGURA`
> Técnica de domínio público, origem não atribuída com segurança.

## Aviso que precede tudo neste arquivo

Das seis técnicas documentadas nesta pasta, RAPPEL é a única cuja **expansão letra a letra
não pôde ser confirmada**. As demais (RTF, CARE, RISE, TAG, BAB) têm expansão estável — ou,
no caso de CARE e RISE, duas variantes conhecidas e nomeadas. RAPPEL não tem isso.

O que este acervo sabe com segurança:

- a sigla circula em material de engenharia de prompt, com seis letras;
- `rappel` é palavra francesa e significa "lembrete" / "recordação", o que sugere que a
  sigla foi construída em francês e escolhida para ser mnemônica na própria língua;
- não foi possível estabelecer, com fonte primária, qual palavra corresponde a cada letra.

O que este acervo **não** vai fazer: escrever uma expansão inventada com aparência de fato.
Seria fácil — seis letras acomodam várias combinações plausíveis, e um leitor não teria como
distinguir a combinação apurada da combinação construída. É exatamente por isso que não se
escreve. A regra vale aqui como vale em [`_backlog.md`](../_backlog.md): a lacuna declarada
é informação; a lacuna preenchida é ruído indistinguível de conhecimento.

## Leitura de trabalho (convenção interna, não afirmação de fato)

Para que a sigla não fique inutilizável no acervo, esta plataforma registra uma **leitura de
trabalho**, marcada como tal. Ela é uma convenção desta casa, adotada por conveniência; não
é uma reconstituição da técnica original e não deve ser citada como se fosse.

| Letra | Leitura de trabalho | O que o campo cobriria |
|---|---|---|
| **R** | Rôle / Papel | ponto de vista da resposta |
| **A** | Action / Ação | operação a executar |
| **P** | Précision / Precisão | grau de detalhe e rigor exigido |
| **P** | Public / Público | para quem a saída é escrita |
| **E** | Exemple / Exemplo | demonstração do par entrada→saída |
| **L** | Limites | o que a resposta não deve fazer |

Duas observações sobre essa leitura. Primeira: se ela estiver certa, RAPPEL é essencialmente
um CARE acrescido de **público** e de **limites** — e esses dois campos são, de fato, os que
mais frequentemente faltam nas outras cinco estruturas. Segunda: se ela estiver errada, o
acervo não perde nada, porque nenhum volume depende dela; a informação que os volumes usam é
a de que a sigla não tem expansão confirmada.

**Não há garantia de que esta leitura corresponda à intenção de quem cunhou a sigla.**

## Quando serve

Enquanto a expansão não for confirmada, a recomendação operacional desta plataforma é:
**não use RAPPEL como estrutura canônica de um prompt de produção.** Um prompt versionado e
auditado não deve depender de uma sigla cujo significado o próprio acervo declara incerto —
quem revisar o prompt daqui a um ano não terá como saber se os campos foram preenchidos
segundo a técnica ou segundo a convenção local.

Os dois campos que a leitura de trabalho acrescenta, porém, **valem por si**, independentemente
da sigla:

- **Público.** Declarar para quem a saída é escrita muda mais a resposta do que declarar o
  papel de quem escreve. Um parecer para o solicitante e o mesmo parecer para o analista
  responsável têm vocabulário, extensão e nível de ressalva diferentes.
- **Limites.** Uma lista explícita de "não faça" é a forma mais direta de bloquear os modos
  de falha conhecidos daquele prompt. É também a parte mais fácil de manter: cada incidente
  vira uma linha nova.

A recomendação prática é acrescentar esses dois campos ao RTF, ao CARE ou ao RISE — que têm
expansão estável — em vez de adotar a sigla incerta.

## Quando NÃO serve

- **Em prompt de produção versionado**, pelo motivo acima.
- **Em documentação voltada a terceiros**, onde citar uma sigla com expansão não confirmada
  transfere a incerteza sem o aviso.
- **Quando você não tem exemplo real** — vale a mesma limitação do CARE: exemplo fabricado
  ensina a fabricar.
- **Quando seis campos são excesso.** Se o pedido cabe em três, use RTF.

## Exemplo concreto

Um prompt escrito com os seis campos da leitura de trabalho, explicitamente marcado como
convenção interna. Tarefa: redigir a nota que acompanha o encaminhamento de uma solicitação
triada de volta ao solicitante.

```text
# Rôle / Papel
Analista responsável pela triagem, escrevendo em nome da equipe.

# Action / Ação
Redija a nota de encaminhamento da solicitação, a partir dos números que eu fornecer
e das três observações de triagem que eu listar.

# Précision / Precisão
Cite cada número com duas casas decimais, exatamente como fornecido — não arredonde e não
recalcule nada. Se um número que a nota precisa citar não estiver na minha lista, escreva
"[não fornecido]" no lugar; não estime.

# Public / Público
O solicitante, que não é da equipe técnica. Ele lê no celular, tem dois minutos, e vai
encaminhar a nota para a área dele. Evite sigla sem expansão na primeira ocorrência. Não
use "conforme a política vigente" sem dizer qual.

# Exemple / Exemplo
[cole aqui uma nota real de uma solicitação anterior, aprovada, com os dados do
solicitante removidos]

# Limites
- Não afirme que a categoria está "correta": diga que a triagem foi feita com o catálogo
  vigente até a data X, e nomeie a data.
- Não prometa prazo que não esteja na minha lista de observações.
- Não recomende mudança de escopo nesta nota; se houver oportunidade, escreva apenas
  que há um ponto a discutir e qual é o assunto.
- Não passe de 15 linhas.
```

Os campos `Public` e `Limites` são os que carregam o peso. O primeiro determinou vocabulário,
extensão e formato (celular, dois minutos, encaminhável). O segundo bloqueou os três modos de
falha reais desse tipo de nota: afirmar correção que não se pode afirmar, prometer prazo, e
dar recomendação de escopo num documento que não é o lugar dela. Note que `Précision`
também criou a saída honesta `[não fornecido]`, em vez de deixar o modelo estimar.

Note, por fim, que o campo `Exemple` está aqui como marcador de onde o exemplo entra — e
está vazio de propósito. Preenchê-lo com uma nota inventada, no meio de um arquivo cujo
assunto é justamente não inventar, seria a contradição perfeita.

## Limitações

**1. A expansão não é confirmada.** É a limitação principal e não é contornável por escrita
mais cuidadosa. Ela só se resolve com fonte.

**2. Seis campos convidam ao excesso.** Quanto mais campos, maior a chance de um deles ser
preenchido por obrigação e não por necessidade. Campo preenchido sem conteúdo real dilui os
que têm.

**3. `Précision` é o campo mais mal-entendido da leitura de trabalho.** Pedir "alta precisão"
não aumenta precisão; o que aumenta é dizer o que fazer quando o dado não está disponível.
Precisão, em prompt, é sobretudo uma regra de abstenção.

**4. Não há atribuição.** Nenhum autor, ano, empresa ou artigo é afirmado neste arquivo — nem
para a sigla, nem para a leitura de trabalho, que é convenção local declarada.

## O que desbloqueia este arquivo

Uma fonte primária que expanda as seis letras. Com ela, o arquivo é reescrito: a leitura de
trabalho sai, a expansão confirmada entra, o estado de atribuição pode subir para
`VERIFICADO`, e o aviso do topo é substituído pela citação da fonte com data de consulta. Até
então, o aviso do topo **é** o conteúdo mais importante deste arquivo.

## Relacionados

- [`CARE.md`](CARE.md) — estrutura de expansão estável com campo de exemplo.
- [`RTF.md`](RTF.md) — a estrutura mínima, quando seis campos são excesso.
- [`_backlog.md`](../_backlog.md) — a mesma política aplicada a treze nomes sem definição.
