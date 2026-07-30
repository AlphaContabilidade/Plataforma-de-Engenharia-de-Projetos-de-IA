---
volume: "03"
volume_nome: DISCOVERY
tipo: PROCESSO
secao: 07-Regras
status: PRONTO
atualizado_em: 2026-07-30
---

# Regras

Sete regras invioláveis, e cada uma tem um teste que a reprova quando violada. Regra sem teste é
recomendação, e recomendação cede no dia do prazo — por isso a coluna da verificação não é
decorativa: ela é o que faz da regra uma regra.

| # | Regra | Onde ela é verificada |
|---|---|---|
| R1 | Inferência nunca entra sem confirmação | `test_entrevista.py::test_palpite_nao_confirmado_nao_entra_em_respostas` |
| R2 | Palpite sem evidência não é produzido | `test_deteccao.py::test_frase_vazia_nao_gera_palpite` e `test_todo_palpite_tem_evidencia_nao_vazia` |
| R3 | Pergunta sem sentido no contexto não é feita | `test_catalogo.py::test_mobile_traz_offline_e_loja_e_nao_traz_as_de_desktop` |
| R4 | Especificação com lacuna universal aberta não se declara completa | `test_especificacao.py::test_completa_e_falsa_com_lacuna_universal_aberta` |
| R5 | Empate de peso é determinístico | `test_entrevista.py::test_empate_de_peso_resolve_pela_ordem_do_catalogo_e_nao_por_sorteio` |
| R6 | Lacuna sem resposta sai como decisão aberta, nunca como valor assumido | `test_especificacao.py::test_markdown_mostra_a_pergunta_e_nunca_um_valor_assumido` |
| R7 | Identificador desconhecido levanta em vez de ser aceito em silêncio | `test_entrevista.py::test_lacuna_desconhecida_ao_responder_id_inexistente` |

## R1 — Inferência nunca entra sem confirmação

Um palpite fica em `palpites_pendentes` até alguém chamar `confirmar` ou `recusar`. Enquanto está
lá, ele não aparece em `respostas`, não altera o conjunto de plataformas e não destrava lacuna
nenhuma. A regra tem uma segunda metade, que é a que costuma faltar: enquanto o palpite está
pendente, a especificação **não se declara completa**. Sem essa metade, ignorar o palpite seria
indistinguível de tê-lo resolvido, e ignorar é o que acontece por padrão quando ninguém obriga.

Confiança alta não dispensa a confirmação. No caso medido, a inferência de confiança **baixa** era
a errada e as duas de confiança alta e média estavam certas — mas isso é resultado, não critério.
Um motor que confirmasse sozinho o que tem confiança alta estaria apostando na distribuição do
próximo caso.

## R2 — Palpite sem evidência não é produzido

Se o componente não consegue apontar o trecho que o levou à conclusão, ele não conclui. A regra é
mais forte do que "registre a evidência quando houver": ela proíbe a conclusão na ausência dela.
Frase vazia devolve tupla vazia; frase sem termo conhecido devolve tupla vazia; não existe valor de
reserva. A consequência aceita é que uma frase realmente vaga produz uma entrevista que começa do
zero — o que é a descrição correta da situação.

A regra tem um corolário que a medição impôs. Evidência que não distingue um palpite do outro não
explica nenhum dos dois: a primeira versão devolvia a frase inteira, e numa ideia escrita em uma
frase só os três palpites saíam com a mesma evidência. A janela de palavras corrigiu isso, e
`test_palpites_da_mesma_frase_tem_evidencias_distintas` impede a volta.

## R3 — Pergunta sem sentido no contexto não é feita

Pergunta irrelevante não entra desabilitada, não entra marcada, não entra no fim da lista:
simplesmente não existe para aquela entrevista. Um formulário que mostra trinta e sete campos e
desabilita vinte e dois ensina a pessoa que o instrumento não entende o caso dela, e a partir dali
as respostas pioram — inclusive as das perguntas que faziam sentido.

A recíproca também é regra: lacuna não universal **precisa** declarar gatilho. Sem plataforma e sem
contexto ela seria relevante sempre, ou seja, universal com a marca errada, e o erro sumiria no meio
de um catálogo grande. `validar_catalogo` levanta `CatalogoInvalido` nesse caso.

## R4 — Especificação com lacuna universal aberta não se declara completa

É a proibição número um da plataforma aplicada localmente: status que mente destrói o valor de
todos os outros. Não há caso em que "que problema isso resolve" seja dispensável, e por isso a
condição não tem parâmetro de relaxamento. A assimetria com a lacuna condicional é deliberada:
condicional aberta **não** impede a completude, porque se impedisse a única saída seria perguntar
tudo — e perguntar tudo é o anti-padrão que o limiar existe para evitar.

## R5 — Empate de peso é determinístico

Duas lacunas de peso dez existem no catálogo, e `proxima()` devolve sempre a mesma. O desempate é a
ordem de declaração, nunca sorteio. Determinismo aqui não é preferência estética: entrevista que
muda de ordem entre execuções não se reproduz, e a primeira reclamação de "ele me perguntou outra
coisa" não tem como ser investigada. A mesma exigência vale para a detecção — a saída depende da
ordem da tabela de termos, e não da ordem em que os termos aparecem no texto.

## R6 e R7 — o que sai, e o que levanta

Lacuna sem resposta sai na especificação com a **pergunta inteira e o motivo dela**, e nunca com um
valor plausível no lugar. `Origem.PADRAO_ASSUMIDO` existe nomeado apenas para poder ser proibido: um
teste verifica que a palavra não aparece no markdown do caso incompleto. E identificador
desconhecido levanta `LacunaDesconhecida` em vez de ser aceito, porque aceitar em silêncio guardaria
a resposta num balde que ninguém lê, deixaria a lacuna verdadeira pendente, e a pessoa lembraria de
ter respondido. Erro de programa levanta; ausência de informação do domínio é registrada.
