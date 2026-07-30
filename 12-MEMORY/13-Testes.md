---
volume: "12"
volume_nome: MEMORY
tipo: ENGINE
secao: 13-Testes
status: PRONTO
atualizado_em: 2026-07-30
---

# Testes

O componente tem **cinquenta funções de teste** distribuídas em três arquivos — dezoito
para o armazém, treze para a guarda e dezenove para a precedência. Nenhuma é parametrizada, de
modo que cinquenta é ao mesmo tempo a contagem de funções e a contagem de casos que
`python -m pytest exemplos/12-memory -q` imprime. A distinção importa porque contagem de funções
e contagem de casos divergem sempre que há parametrização, e citar uma como se fosse a outra faz
quem roda o comando duvidar do resto da seção.

A suíte roda sem rede, sem credencial, sem estado em disco e sem depender do dia em que é
executada — a data de referência entra por parâmetro em toda chamada. Essa propriedade não é
conveniência: é o que faz do segundo gate da plataforma um gate que ninguém tem motivo para
desligar.

## O que cada arquivo cobre

| Arquivo de teste | Alvo | Casos que só existem por causa de um risco concreto |
|---|---|---|
| `tests/test_memoria_observada.py` | Identidade da chave, branco na decisão, ordem de registro, contagem e dominância | Chave em branco levanta na construção e na consulta; decisão em branco levanta `DecisaoInvalida`, que não é `ChaveInvalida`; borda é normalizada nos dois campos; a dominância é crua e inclui o eco; empate é determinístico e vale exatamente meio |
| `tests/test_contaminacao.py` | Descarte do eco e relatório de contradição | Eco não silencia contradição; base congelada sozinha não contradiz nada; uma observação isolada já contradiz; duas bases discordantes geram duas contradições |
| `tests/test_precedencia.py` | Janela, limiar, empate, precedência e forma do veredicto | Sete de dez decide no limite inclusivo; seis de dez não decide; observação indecisa não cai para a base congelada; contradição rebaixa até a decisão humana; janela maior muda o veredicto |

Três dos dezoito casos do armazém entraram na incorporação da auditoria, e o motivo de estarem
aqui é o mesmo que justifica os outros: cada um fecha um caminho pelo qual um valor sem sentido
chegaria a um veredicto. `test_decisao_em_branco_levanta_decisao_invalida` cobre a string vazia,
o espaço e a tabulação; `test_decisao_em_branco_nao_e_chave_invalida` fixa que as duas exceções
são irmãs distintas, para que um `except` de chamador não trate um defeito como o outro; e
`test_decisao_e_normalizada_na_borda` fixa que `"alfa"` e `" alfa "` contam como a mesma decisão,
porque contá-las separado partiria a dominância em duas metades sem que nada aparecesse errado.

## Os quatro testes que carregam o volume

O primeiro é `test_eco_nao_silencia_a_contradicao`. Ele monta o cenário exato do defeito de
produção: a base congelada diz uma coisa, três observações independentes dizem outra, e o agente
escreveu cinco vezes concordando com a base. Se o eco contasse, a dominante seria a decisão da
base congelada e a contradição desapareceria — que é precisamente como uma decisão errada se
consolida sem deixar sinal. O teste afirma que a contradição existe, que o lado observado é o
das três observações e que `n_observacoes` vale três.

O segundo é `test_observacao_indecisa_nao_cai_para_a_base_congelada`. Ele existe porque a
implementação mais natural de precedência é uma cascata de reserva, e a cascata é errada aqui:
com seis observações contra quatro e uma base congelada presente, a cascata devolveria a decisão
da base, que é o defeito original com outro nome. O teste fixa `decisao is None`, `confianca is
None` e a presença da contradição no veredicto indeciso.

O terceiro é `test_eco_do_agente_e_descartado_e_contado`. Ele afirma duas coisas na mesma
função, e as duas são necessárias: que a dominância crua do armazém aponta para o eco — cinco
sétimos — e que o veredicto aponta para a observação. Sem a primeira asserção, o teste passaria
mesmo se o armazém tivesse começado a filtrar por conta própria, e a separação entre armazém e
guarda deixaria de ser verificada.

O quarto é `test_dominancia_7_em_10_decide`, junto com o irmão de seis em dez. Eles fixam o
limite inclusivo do limiar, que é ambíguo em prosa: "acima do mínimo" admite as duas leituras, e
sem teste o comportamento no limite seria descoberto por acidente em produção. O par também
ancora o formato da justificativa, verificando que a fração aparece nela.

## Estratégia, e o que ela deliberadamente não faz

A estratégia é testar o componente com entradas sintéticas construídas por auxiliares de três
linhas, e não com dados de nenhum sistema real. A suíte prova que o armazém guarda procedência,
que o eco é descartado, que a contradição é reportada e que a precedência decide ou se recusa a
decidir pelos motivos declarados. A consequência aceita é explícita: ela **não** prova que a
classificação da origem foi feita corretamente por quem alimenta o armazém. Eco marcado por
engano como observação atravessa todas as garantias, porque nenhuma verificação interna pode
distinguir uma marcação errada de um fato. Essa é a fronteira honesta do componente, está
registrada como limite de R1 em [`07-Regras.md`](07-Regras.md), e a defesa contra ela é o ramo de
conferência de procedência em [`06-Fluxogramas.md`](06-Fluxogramas.md).

## Como este volume se encaixa nos gates da plataforma

O primeiro gate é estrutural, `python -m ferramentas.validar 12`: front-matter, substância,
marcadores, diagramas tipados com parágrafo descritivo, exemplos citados que existem e têm
teste, e links relativos que resolvem. O segundo é a suíte descrita aqui,
`python -m pytest exemplos/12-memory -q`. O terceiro é a verificação cruzada,
`python -m ferramentas.validar --cross-refs`, que confere que toda dependência declarada aponta
para volume existente e que o grafo de pré-requisitos é acíclico. A ordem é essa porque o mais
barato reprova primeiro, e nenhum volume recebe o estado de pronto com qualquer um dos três
vermelho. As regras completas estão em
[`../00-INTRODUCAO/Convencoes.md`](../00-INTRODUCAO/Convencoes.md).
