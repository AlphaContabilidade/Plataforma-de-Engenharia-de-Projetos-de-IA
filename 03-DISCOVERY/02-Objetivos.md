---
volume: "03"
volume_nome: DISCOVERY
tipo: PROCESSO
secao: 02-Objetivos
status: PRONTO
atualizado_em: 2026-07-30
---

# Objetivos

Cada objetivo abaixo é um verbo que se verifica, e ao lado dele está onde a verificação acontece.
Objetivo que não aponta para um teste ou para um número medido é intenção, e intenção não se
audita.

| Depois de ler, o leitor consegue | Onde isso se verifica |
|---|---|
| Declarar uma especificação como conjunto de lacunas, separando universais de condicionais | `catalogo.CATALOGO`, com `validar_catalogo` reprovando lacuna condicional sem gatilho |
| Escrever a condição que torna uma pergunta relevante, e provar que a irrelevante não aparece | `test_catalogo.py::test_mobile_traz_offline_e_loja_e_nao_traz_as_de_desktop` |
| Produzir inferência com a evidência que a sustenta, e recusar-se a inferir sem evidência | `test_deteccao.py::test_frase_vazia_nao_gera_palpite` e `test_palpites_da_mesma_frase_tem_evidencias_distintas` |
| Ordenar perguntas por valor informativo com desempate determinístico | `test_entrevista.py::test_empate_de_peso_resolve_pela_ordem_do_catalogo_e_nao_por_sorteio` |
| Definir e defender um critério de parada explícito e parametrizável | `test_entrevista.py::test_peso_minimo_e_parametrizavel_e_muda_o_que_se_pergunta` |
| Emitir especificação que se recusa a se declarar completa quando não está | `test_especificacao.py::test_completa_e_falsa_com_lacuna_universal_aberta` |
| Medir a qualidade da própria detecção pela fração de inferências recusadas | [`14-Metricas.md`](14-Metricas.md), com o valor medido de 1/3 no passo a passo |

## O que "conseguir fazer" significa em cada caso

**Declarar lacunas em vez de seções.** A diferença prática é que o conjunto de perguntas passa a
ser dado, e não estrutura de código. Acrescentar um contexto novo é acrescentar linhas a uma
tupla e nada mais; nenhuma condicional em `entrevista.py` conhece nome de contexto. É o que
permite revisar o conteúdo das perguntas sem risco de mudar o comportamento do controle, e
mudar a heurística de ordenação sem tocar no conteúdo das perguntas.

**Inferir com evidência.** O objetivo não é acertar mais: é nunca concluir sem poder mostrar de
onde veio a conclusão. A consequência de projeto é dura e vale escrever por extenso — se o
componente não consegue apontar o trecho, ele não conclui, mesmo quando a conclusão pareceria
certa. Frase vazia devolve tupla vazia; frase sem termo conhecido devolve tupla vazia. Não
existe palpite genérico de reserva.

**Parar quando não vale.** Este é o objetivo mais fácil de trair, porque perguntar tudo tem a
aparência de rigor. O leitor sai daqui capaz de defender o contrário: que o limiar existe, que
ele é parâmetro porque o ponto certo depende de quanto custa errar no domínio, e que a lacuna
não perguntada continua constando na saída. No caso medido, o limiar padrão trocou uma pergunta
por uma decisão aberta registrada — quinze perguntas viraram catorze, e a décima quinta apareceu
por escrito em vez de desaparecer.

**Recusar-se a fechar mentindo.** A propriedade `completa` é a versão local da proibição número
um da plataforma. Ela é `False` com inferência não confirmada e `False` com lacuna universal
aberta, e não existe parâmetro para relaxar isso. A ausência do parâmetro é o desenho: limiar
afrouxável é limiar que será afrouxado no dia do prazo.
