---
volume: "12"
volume_nome: MEMORY
tipo: ENGINE
secao: 06-Fluxogramas
status: RASCUNHO
atualizado_em: 2026-07-30
---

# Fluxogramas

Os diagramas de [`05-Diagramas.md`](05-Diagramas.md) descrevem o que o componente é. Os
fluxogramas desta seção descrevem o que o código percorre e onde uma pessoa tem de olhar um
número e agir. A diferença importa: a máquina de estados diz quais estados existem, o
fluxograma diz em que ponto a resolução para e quem fica com a conta.

## Resolução de uma chave, do armazém ao veredicto

```mermaid
flowchart TD
    A[resolver chave com hoje, janela_dias e dominancia_minima] --> B[entradas da chave em ordem de registro]
    B --> C{Chave em branco?}
    C -- sim --> D[ChaveInvalida: erro de programa, nao pendencia]
    C -- nao --> E[Descartar origem ESCRITO_PELO_AGENTE]
    E --> F[Expirar o que passou da janela]
    F --> G[Procurar contradicao entre base congelada e dominante observada]
    G --> H{Existe entrada DECIDIDO_POR_HUMANO vigente?}
    H -- sim --> I[Decisao humana mais recente vence; confianca ALTA]
    H -- nao --> J{Existe entrada OBSERVADO vigente?}
    J -- sim --> K{Empate no topo da contagem?}
    K -- sim --> L[Indeciso: empate nao decide]
    K -- nao --> M{Dominancia atinge o minimo?}
    M -- nao --> N[Indeciso: dominancia abaixo do minimo]
    M -- sim --> O[Decide pela dominante; confianca ALTA]
    J -- nao --> P{Existe entrada BASE_CONGELADA vigente?}
    P -- sim --> Q[Base congelada decide sozinha; confianca BAIXA]
    P -- nao --> R[Indeciso: nenhuma evidencia vigente]
    I --> S{Ha contradicao aberta?}
    O --> S
    Q --> S
    S -- sim --> T[Rebaixa a confianca para MEDIA e anexa a contradicao]
    S -- nao --> U[Veredicto com a confianca original]
    L --> V[Veredicto indeciso com justificativa numerica]
    N --> V
    R --> V
```

O fluxograma tem sete pontos de decisão e nenhum depende de julgamento. Três merecem
comentário. O primeiro é que a chave em branco sai por um ramo próprio, que **levanta** em
vez de devolver veredicto: falta de evidência é estado normal do domínio, chave vazia é
defeito de quem chamou, e misturar os dois faria o chamador tratar bug como pendência. O
segundo é o desenho dos ramos `J` e `P`: o ramo negativo de `J` é a única entrada para a
base congelada. Se a observação existe e não decide, o caminho segue para `L` ou `N`, e não
para `P` — a base congelada não é rede de segurança da observação que falhou. O terceiro é
que o nó `S` alcança os três caminhos que decidem, inclusive o da decisão humana: chave com
contradição aberta é chave conhecidamente inconsistente, e nenhum veredicto sobre chave
inconsistente sai como confiança alta, nem quando quem decidiu foi uma pessoa.

## Triagem de uma contradição aberta

```mermaid
flowchart LR
    A[Contradicao no veredicto] --> B[Ler n_observacoes e congelada_em]
    B --> C{n_observacoes suficiente para o custo do erro no dominio?}
    C -- nao --> D[Manter em observacao e coletar mais evidencia independente]
    C -- sim --> E{A base congelada esta desatualizada ou a observacao esta contaminada?}
    E -- base desatualizada --> F[Encaminhar a fonte para recuratoria no volume 11]
    E -- observacao suspeita --> G[Conferir a procedencia das entradas OBSERVADO uma a uma]
    G --> H{Alguma veio da escrita do proprio agente sem estar marcada?}
    H -- sim --> I[Corrigir a marcacao na origem e reprocessar]
    H -- nao --> J[Registrar decisao humana; ela vence e encerra a contradicao operacionalmente]
    F --> K[A contradicao permanece aberta ate a fonte mudar]
    D --> K
```

O segundo fluxograma existe porque a contradição é reportada e não resolvida, e portanto
alguém precisa saber o que fazer com ela. A pergunta que abre a triagem não é "quem está
certo" e sim "quantas observações independentes sustentam o lado observado" — é para isso
que `n_observacoes` existe no relatório. O ramo mais importante é o de `H`: antes de
concluir que a base congelada envelheceu, vale conferir se a observação que a contradiz é
de fato independente, porque uma entrada mal marcada é o mesmo defeito de sempre com outra
roupa. O ramo de `J` merece um alerta explícito: registrar decisão humana encerra a
contradição **na prática**, porque a precedência a torna irrelevante para o veredicto, mas
não encerra na origem — a base congelada continua discordando, e a `Contradicao` continua
sendo emitida enquanto as duas entradas existirem na janela. Isso é intencional: silenciar
o relatório com uma decisão humana transformaria a decisão em tapa-buraco e deixaria a
fonte errada intacta para reaparecer na próxima chave.
