---
volume: "01"
volume_nome: FUNDACAO
tipo: GOVERNANCA
secao: 04-Arquitetura
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Arquitetura

A disciplina tem quatro camadas, e a ordem entre elas é o que impede o modo de falha mais comum —
publicar um artefato cuja evidência ninguém consegue reconstituir.

## As quatro camadas

**Evidência.** O que se observou, com procedência. Não é "o sistema é rápido"; é "a suíte de 73 testes
soma 0,02 s de corpo, medido com `--durations=0`". Evidência sem procedência é boato com formatação.

**Decisão.** O que se escolheu, com a razão junto. A razão não é enfeite: decisão sem razão registrada
é revertida por engano pelo próximo que passar, e revertida de novo quando o problema original voltar.

**Artefato.** O que se entregou — código, prosa, configuração. É a única camada que o usuário final
enxerga, e a única que sobrevive sozinha.

**Verificação.** O que confere que o artefato ainda corresponde à decisão e a decisão ainda
corresponde à evidência. É a camada que envelhece pior quando falta, porque a corrosão é silenciosa.

A regra estrutural é que **cada camada só pode apontar para a de baixo**. Artefato aponta para
decisão, decisão aponta para evidência. Artefato que aponta direto para evidência é ferramenta sem
justificativa; decisão que aponta para artefato é racionalização.

## A matriz de controles

O produto executável deste volume é uma matriz. Cada linha liga um princípio a uma verificação
concreta, e nenhuma linha pode ter a coluna de verificação vazia.

| # | Princípio | Verificação | Executável | O que acontece ao reprovar |
|---|---|---|---|---|
| C1 | Status não mente | `validar NN` confere seções, tamanho e marcadores | sim | `exit 1`; o volume não pode ser `PRONTO` |
| C2 | Exemplo citado existe | regra `exemplo-inexistente` resolve o caminho em disco | sim | `exit 1` |
| C3 | Referência resolve | regra `link-morto` e `--cross-refs` | sim | `exit 1` |
| C4 | Pré-requisito é acíclico | `--cross-refs` detecta ciclo em `depende_de` | sim | `exit 1` |
| C5 | Código publicado roda | `pytest` sobre `exemplos/` | sim | suíte vermelha |
| C6 | Quem escreve não se aprova | auditoria por modelo distinto, em sessão separada | não | promoção bloqueada |
| C7 | Promoção deixa rastro | entrada datada no `CHANGELOG.md` | não | critério 4 da Definição de PRONTO falha |
| C8 | Número da prosa é medido | **manual** — nenhum gate lê número por extenso | **não** | dívida declarada, ver `16-Roadmap` |

A linha C8 é a mais importante da tabela, e é a única com "não" em negrito. Ela existe porque a
alternativa — omiti-la — faria a matriz parecer completa. Controle que não roda tem de aparecer como
controle que não roda; matriz que só lista o que já é automático mede a ferramenta, não a disciplina.
