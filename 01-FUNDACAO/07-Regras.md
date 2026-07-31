---
volume: "01"
volume_nome: FUNDACAO
tipo: GOVERNANCA
secao: 07-Regras
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Regras

As regras estão numeradas para poderem ser citadas em revisão e em relatório de auditoria. Cada uma
traz a consequência, porque regra sem consequência é sugestão.

**R1 — Nunca afirmar sucesso sem ter olhado.** Rodou, cola a saída; não rodou, diz que não rodou.
*Consequência:* afirmação de sucesso sem evidência anexa é tratada como defeito de mesma gravidade
que o defeito que ela esconderia.

**R2 — Nunca ajustar a verificação para o artefato passar.** Se um teste cai depois de uma mudança,
ou a mudança está errada, ou o teste estava frouxo. As duas hipóteses exigem investigação; nenhuma
autoriza afrouxar a asserção. *Consequência:* teste enfraquecido sem justificativa escrita é
reversão obrigatória.

**R3 — Nunca inventar arquivo, API, número ou regra de negócio.** Sem evidência, é lacuna declarada.
*Consequência:* é a única regra sem exceção nenhuma nesta plataforma.

**R4 — Toda decisão técnica sai com a justificativa junto.** *Consequência:* decisão sem razão é
tratada como não tomada, e volta para a fila.

**R5 — Quem escreve não se aprova.** *Consequência:* volume sem auditoria por modelo distinto não
pode receber `PRONTO`, por melhor que esteja.

**R6 — Marcador de trabalho inacabado não entra em prosa publicada.** A lista está em
`contrato.json` e a checagem usa fronteira de palavra. *Consequência:* `exit 1` no gate estrutural.

**R7 — Lacuna declarada é resultado, não fracasso.** Dizer que a evidência não decide é entrega
válida; preencher a lacuna com o valor mais provável não é. *Consequência:* uma entrega com lacuna
declarada é aceita; uma com lacuna preenchida por suposição é rejeitada inteira.

## A Definição de PRONTO

Um volume é `PRONTO` quando os quatro critérios valem ao mesmo tempo. Não há ordem de importância e
nenhum é dispensável por urgência.

1. Gate estrutural com `exit 0` — seções presentes, tamanho mínimo, marcadores ausentes, diagramas
   exigidos pelo tipo, exemplos citados existentes, links resolvendo.
2. Gate executável verde — a suíte dos exemplos do volume passa.
3. Auditoria independente com média **8,0 ou mais** e **nenhuma seção abaixo de 6**. A segunda
   condição existe porque média esconde buraco: 9 em dezessete seções e 3 numa não é um volume bom.
4. Entrada datada no `CHANGELOG.md` descrevendo o que mudou de estado.
