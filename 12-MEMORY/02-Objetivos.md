---
volume: "12"
volume_nome: MEMORY
tipo: ENGINE
secao: 02-Objetivos
status: PRONTO
atualizado_em: 2026-07-30
---

# Objetivos

Os objetivos deste volume são afirmações verificáveis. Cada um tem um critério que uma
pessoa confere sem confiar na palavra de quem escreveu, e o lugar exato onde essa
conferência acontece. Objetivo sem critério é intenção, e intenção não sustenta gate.

| Objetivo | Critério verificável | Onde se confere |
|---|---|---|
| Toda evidência carrega procedência | `Entrada` exige `origem` no construtor; não há caminho para registrar decisão sem declarar de onde veio | `tests/test_memoria_observada.py` |
| O sistema não se ouve | Entrada com origem `ESCRITO_PELO_AGENTE` nunca entra na evidência válida, e a quantidade descartada aparece no veredicto | `tests/test_contaminacao.py`, `tests/test_precedencia.py` |
| Contradição é visível | Base congelada que discorda da dominante observada produz uma `Contradicao`, inclusive quando o veredicto é indeciso | `tests/test_contaminacao.py` |
| Eco não silencia contradição | Cinco escritas do próprio agente concordando com a base congelada não removem a contradição | `test_eco_nao_silencia_a_contradicao` |
| Indeciso é resultado, não ausência | `decisao is None` vem sempre com `confianca is None` e justificativa não vazia dizendo o número que faltou | `tests/test_precedencia.py` |
| Precedência é declarada em um lugar | A ordem vive em `PRECEDENCIA`, e `ESCRITO_PELO_AGENTE` está fora da tupla | `test_precedencia_exclui_o_eco_do_agente` |
| Precedência não é cascata | Observação presente que não alcança dominância encerra a resolução; a base congelada não assume | `test_observacao_indecisa_nao_cai_para_a_base_congelada` |
| Evidência velha não decide | Entrada fora da janela não conta, e o veredicto informa quantas expiraram | `test_entrada_fora_da_janela_expira` |
| Decisão humana vence | Uma decisão humana vence nove observações contrárias | `test_decisao_humana_vence_dominancia_contraria` |
| Falta de evidência nunca levanta | Memória vazia devolve veredicto indeciso; só chave em branco levanta | `test_memoria_vazia_devolve_indeciso_sem_excecao` |

## Objetivo primário

O objetivo primário é fazer com que **duas fontes que discordam produzam um relatório, e
não um vencedor por acidente**. Todo o resto do volume existe para tornar isso possível: a
procedência existe para que as fontes sejam distinguíveis, o descarte do eco existe para
que a contagem meça observação e não atividade própria, e o veredicto indeciso existe
para que a ausência de resposta seja uma resposta legível em vez de um vazio ambíguo.

## Objetivos secundários

O segundo objetivo é tornar o custo de auditar uma decisão proporcional ao tamanho da
trilha, e não ao tamanho do código. Com o armazém, explicar por que o agente decidiu algo
é ler entradas com data e origem; sem ele, é reconstruir a ordem das consultas por
leitura de código. O terceiro é manter o componente sem dependência: os três módulos usam
apenas a biblioteca padrão, e a data de referência entra por parâmetro, o que faz a
expiração testável offline e de forma determinística.

## O que não é objetivo

Não é objetivo curar a base congelada — decidir de onde ela vem, quem tem autoridade
sobre ela e quando ela expira como documento. Não é objetivo recuperar entrada por
similaridade, nem orçar janela de contexto. As três coisas têm volume próprio, e a
fronteira está declarada em [`03-Escopo.md`](03-Escopo.md). Também não é objetivo escolher
o limiar de dominância: ele é parâmetro porque o valor correto depende do custo do erro
no domínio de quem usa, e fixá-lo aqui seria impor um número arbitrário como se fosse
resultado de medição.
