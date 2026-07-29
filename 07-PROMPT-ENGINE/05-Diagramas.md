---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 05-Diagramas
status: RASCUNHO
atualizado_em: 2026-07-29
---

# Diagramas

Esta seção reúne os quatro diagramas de comportamento e de dados do motor. Eles não
ilustram o código: eles são a leitura humana de estruturas que existem em um único lugar
no código. A máquina de estados abaixo, em particular, tem os mesmos cinco nomes e as
mesmas transições do dicionário `TRANSICOES` em `prompt_registry.py`; se um dos dois
mudar sem o outro, o volume passa a mentir e a auditoria detecta a divergência.

## Sequência de uma versão, do contrato à promoção

```mermaid
sequenceDiagram
    autonumber
    actor A as Autor
    participant T as PromptTemplate
    participant R as PromptRegistry
    participant E as PromptEvaluator
    participant X as Executor injetado
    A->>T: PromptTemplate(nome, corpo, variaveis)
    T-->>A: ContratoViolado se corpo e contrato divergem
    A->>R: registrar(template)
    R->>T: le template.hash
    R-->>A: "v1", estado VERSIONADO
    A->>R: transicionar(nome, "v1", EM_AVALIACAO)
    A->>E: avaliar(template, casos)
    loop para cada CasoDeOuro
        E->>T: render(**caso.entradas)
        T-->>E: prompt concreto ou ContratoViolado
        E->>X: executor(prompt)
        X-->>E: saida em texto
        E->>E: re.search(caso.esperado, saida)
    end
    E-->>A: Resultado(total, falhas)
    A->>R: transicionar(nome, "v1", PROMOVIDO)
    R->>R: versao promovida anterior cai para DEPRECIADO
```

A sequência deixa visíveis dois detalhes que costumam ser esquecidos na descrição verbal
do fluxo. O primeiro é que o avaliador chama `render` uma vez por caso de ouro, dentro do
laço, e trata a falha de renderização como falha do caso — um caso malformado não derruba
a bateria inteira. O segundo é que o rebaixamento da versão promovida anterior acontece
dentro do mesmo `transicionar`, e não em uma segunda chamada: não existe instante em que
duas versões do mesmo nome se declarem a de produção.

## Ciclo de vida de uma versão

```mermaid
stateDiagram-v2
    [*] --> RASCUNHO
    RASCUNHO --> VERSIONADO: registrar(template)
    VERSIONADO --> EM_AVALIACAO: entra na bateria de casos de ouro
    VERSIONADO --> DEPRECIADO: abandonada antes de qualquer avaliacao
    EM_AVALIACAO --> PROMOVIDO: taxa de acerto atinge o limiar
    EM_AVALIACAO --> VERSIONADO: reprovada, volta para ajuste do corpo
    EM_AVALIACAO --> DEPRECIADO: descartada durante a avaliacao
    PROMOVIDO --> DEPRECIADO: outra versao assume a producao
    DEPRECIADO --> [*]
```

São cinco estados e sete transições — uma saindo de `RASCUNHO`, duas de `VERSIONADO`, três de
`EM_AVALIACAO`, uma de `PROMOVIDO` e nenhuma de `DEPRECIADO`, exatamente a contagem das chaves de
`TRANSICOES`. As duas setas restantes do diagrama, ligadas a `[*]`, marcam entrada e saída do
ciclo e não são transições do dicionário. A ausência mais importante do diagrama é a aresta
que não existe: não há caminho de `VERSIONADO` para `PROMOVIDO`. Prompt sem avaliação não
promove, e essa regra não depende de disciplina de quem opera — ela é uma chave ausente
no dicionário de transições. `RASCUNHO` é o estado de quem ainda não entrou no registro:
toda versão registrada nasce em `VERSIONADO`, e o estado inicial existe no enumerado
porque a transição rascunho para versionado é parte do fluxo documentado mesmo
acontecendo fora do registro. `DEPRECIADO` é terminal; ressuscitar uma versão antiga é
registrá-la de novo, o que preserva a trilha em vez de reescrevê-la.

## Modelo de dados do registro

```mermaid
erDiagram
    PROMPT ||--|{ VERSAO : "agrupa por nome"
    VERSAO ||--|| CONTRATO : "congela"
    VERSAO ||--o{ AVALIACAO : "acumula"
    AVALIACAO ||--o{ FALHA : "detalha"
    CONTRATO ||--|{ VARIAVEL : "declara"
    PROMPT {
        string nome PK
    }
    VERSAO {
        string versao PK
        string hash
        string estado
    }
    CONTRATO {
        string corpo
        string assinatura
    }
    VARIAVEL {
        string nome PK
        string tipo
        bool obrigatoria
    }
    AVALIACAO {
        int total
        float taxa_acerto
    }
    FALHA {
        string caso
        string saida
        string motivo
    }
```

O modelo mostra que a chave de identidade não é o nome do prompt, e sim o par nome mais
versão, e que o hash é atributo da versão porque é dele que a versão nasce. A relação
entre versão e avaliação é de zero ou muitas: uma versão pode nunca ter sido avaliada, e
é exatamente esse caso que a máquina de estados impede de chegar à produção. A relação
entre contrato e variável é de uma ou muitas, o que registra uma restrição real do
código: um corpo sem placeholder algum e com variáveis declaradas é reprovado na
construção.

## Domínio do volume em um olhar

```mermaid
mindmap
  root((Motor de prompts))
    Contrato
      Corpo com placeholders
      Variaveis tipadas
      Assinatura em ordem alfabetica
      Hash de 12 hexdigitos
    Registro
      Versao derivada do hash
      Idempotencia por conteudo
      Cinco estados e sete transicoes
      Historico como trilha
    Avaliacao
      Casos de ouro
      Executor injetado
      Taxa de acerto
      Deriva entre versoes
    Fora do escopo
      Compilacao multi-modelo no volume 28
      Otimizacao automatica no volume 29
      Roteamento por custo no volume 27
```

O mapa mental serve como índice de leitura, e não como especificação. Ele existe porque os
três ramos internos correspondem exatamente aos três módulos do volume, e o quarto ramo
repete as fronteiras de [`03-Escopo.md`](03-Escopo.md) no mesmo lugar em que o leitor
forma sua primeira impressão do domínio — declarar a fronteira só no meio do documento
chega tarde para quem está decidindo se este é o volume que procura.
