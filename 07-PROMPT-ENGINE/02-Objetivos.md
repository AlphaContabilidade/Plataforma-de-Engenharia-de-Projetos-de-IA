---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 02-Objetivos
status: RASCUNHO
atualizado_em: 2026-07-29
---

# Objetivos

Os objetivos deste volume são escritos como afirmações verificáveis. Cada um tem um
critério que uma pessoa consegue conferir sem confiar na palavra de quem escreveu, e o
lugar onde essa conferência acontece. Objetivo sem critério é intenção, e intenção não
sustenta gate.

| Objetivo | Critério verificável | Onde se confere |
|---|---|---|
| Prompt tem contrato explícito | O construtor levanta `ContratoViolado` quando o corpo e as variáveis declaradas divergem em qualquer direção | `tests/test_prompt_template.py` |
| Prompt tem identidade estável | O mesmo corpo e a mesma assinatura produzem o mesmo hash de 12 hexdígitos; mudar o tipo de uma variável muda o hash | `tests/test_prompt_template.py` |
| Prompt é versionado sem intervenção manual | `registrar` deriva a versão do hash e é idempotente por conteúdo | `tests/test_prompt_registry.py` |
| Prompt é avaliável offline | O avaliador recebe o executor por injeção e roda com um substituto determinístico | `tests/test_prompt_evaluator.py` |
| Promoção exige evidência | Nenhuma transição leva de `VERSIONADO` direto a `PROMOVIDO` | `TRANSICOES` em `prompt_registry.py` |
| Só uma versão em produção por nome | Promover uma versão rebaixa a anterior para `DEPRECIADO` no mesmo passo | `tests/test_prompt_registry.py` |
| O histórico é auditável | `historico` devolve `(versao, hash, estado)` em ordem de registro | `tests/test_prompt_registry.py` |

## Objetivo primário

O objetivo primário é reduzir a decisão "trocar o prompt" a uma comparação numérica
entre duas versões sobre a mesma amostra de casos de ouro. Tudo o mais no volume existe
para tornar essa comparação possível: o contrato tipado existe para que renderizar seja
determinístico, o hash existe para que as duas versões sejam distinguíveis, o registro
existe para que a versão anterior continue recuperável, e o avaliador existe para que a
comparação produza um número em vez de uma impressão.

## Objetivos secundários

O segundo objetivo é tornar o custo de auditoria proporcional ao tamanho do histórico, e
não ao tamanho do código. Com o registro, auditar significa ler uma trilha de tuplas;
sem ele, significa varrer o repositório. O terceiro objetivo é manter o motor
independente de provedor: nenhuma linha dos três módulos importa cliente de modelo, o
que faz do executor injetado a única superfície de acoplamento.

## O que não é objetivo

Não é objetivo deste volume melhorar prompt automaticamente, escolher modelo por custo
ou traduzir um prompt entre dialetos de provedores diferentes. Essas três coisas têm
volume próprio e a fronteira está declarada em [`03-Escopo.md`](03-Escopo.md). Também
não é objetivo esconder o custo de execução: medir custo é objetivo, otimizá-lo não.
