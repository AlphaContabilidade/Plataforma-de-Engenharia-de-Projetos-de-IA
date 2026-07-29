---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 01-Introducao
status: RASCUNHO
atualizado_em: 2026-07-29
---

# Introdução

Um motor de prompts é o componente que trata prompt como artefato de produção, e não
como literal de string. Ele responde três perguntas que todo sistema baseado em modelo
de linguagem passa a precisar responder no dia em que entra em produção: qual era
exatamente o prompt em uso quando o comportamento mudou, quais variáveis ele exige para
funcionar, e com que evidência alguém decidiu trocá-lo. Onde não existe motor, essas
respostas ficam distribuídas entre o histórico do versionador, a memória de quem
escreveu e a sorte. Este volume documenta o motor: o contrato tipado do prompt, o
registro versionado por conteúdo e o avaliador que mede antes de promover.

## Por que prompt solto no código é dívida

Um prompt em f-string dentro de uma função tem quatro defeitos que só aparecem depois.
O primeiro é que o contrato dele é implícito: nada declara que ele exige `texto` e
`idioma`, então apagar um placeholder por descuido produz uma saída degradada em vez de
um erro. O segundo é que ele não tem identidade — duas cópias divergentes do mesmo
prompt coexistem em módulos diferentes e ninguém detecta. O terceiro é que ele não tem
histórico útil: o diff do versionador mostra que a string mudou, não mostra que a taxa
de acerto caiu quatro pontos por causa disso. O quarto é o mais caro: sem identidade e
sem histórico, avaliar fica impossível, e quando avaliar é impossível a decisão de
trocar o prompt volta a ser opinião.

O custo dessa dívida é assimétrico. Escrever o prompt solto leva um minuto; descobrir,
seis meses depois, qual das variantes espalhadas pelo código era a que rodava no incidente
consome uma investigação inteira e frequentemente termina sem conclusão, porque a evidência
necessária nunca foi gravada. O motor troca esse minuto economizado por uma estrutura pequena e
verificável.

## O que este volume entrega

O volume entrega três contratos com implementação executável e teste, descritos nas
seções [`08-Modelos.md`](08-Modelos.md) e [`11-Implementacao.md`](11-Implementacao.md):
um template que falha na construção quando corpo e variáveis discordam, um registro em
que a versão é derivada do hash do contrato, e um avaliador que recebe o executor por
injeção e por isso roda offline no processo de integração contínua. Entrega também as
fronteiras: o que este motor deliberadamente não faz está declarado em
[`03-Escopo.md`](03-Escopo.md), porque motor sem fronteira declarada invade o vizinho.

## Para quem é

Para quem escreve prompt que outra pessoa vai manter, e para quem precisa auditar
depois. Um autor sozinho, em um experimento descartável, não tem o problema que este
volume resolve — e forçar o motor sobre um experimento é fricção sem retorno. O motor
começa a pagar quando existe um segundo autor, um segundo ambiente ou um segundo
requisito de auditoria.
