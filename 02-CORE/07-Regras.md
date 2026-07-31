---
volume: "02"
volume_nome: CORE
tipo: ARQUITETURA
secao: 07-Regras
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Regras

Regras estruturais deste volume. São poucas de propósito: arquitetura com vinte regras não é seguida.

**N1 — Existe exatamente uma fronteira de saída por tipo de resposta.** Nomeável, num arquivo. Duas
fronteiras para a mesma resposta divergem, e a segunda sempre é escrita com pressa.

**N2 — Nada além da fronteira de saída recebe texto livre do modelo.** O que atravessa é dado com
tipo. *Consequência:* um `if` sobre o conteúdo da resposta, fora da fronteira, é defeito de
arquitetura, mesmo funcionando.

**N3 — A resposta do modelo é entrada não confiável.** Recebe validação de forma, de domínio e de
autorização, nessa ordem, e as três são diferentes. *Consequência:* a ausência de teste com resposta
malformada é considerada ausência da fronteira.

**N4 — Falha de validação não produz efeito.** Nenhuma gravação, cobrança, envio ou publicação
acontece a partir de resposta que não passou. *Consequência:* é a regra que separa erro de estrago.

**N5 — Repetir só faz sentido em falha de forma.** Falha de domínio se corrige no contexto; falha de
autorização não se corrige, se recusa. *Consequência:* repetição cega multiplica custo e latência
sem mudar o resultado, e esconde a causa.

**N6 — A montagem de contexto é determinística.** Sem relógio, sem aleatório, sem leitura de estado
global. *Consequência:* dado o mesmo estado de entrada, o contexto é byte a byte igual, e por isso
uma resposta ruim é investigável — imprime-se o contexto e olha-se.

**N7 — O número de chamadas ao modelo por caminho é decisão declarada.** *Consequência:* acrescentar
uma chamada é mudança de arquitetura e vai com justificativa, não é detalhe de implementação.

**N8 — Quando existe alternativa determinística com qualidade suficiente, ela vence.** Uma tabela de
termos com procedência explícita é preferível a uma classificação por modelo quando as duas
resolvem: a tabela é auditável, reproduzível, instantânea e de graça. O motor de descoberta do
volume `03` é construído assim de propósito.
