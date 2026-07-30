---
volume: "12"
volume_nome: MEMORY
tipo: ENGINE
secao: 07-Regras
status: PRONTO
atualizado_em: 2026-07-30
---

# Regras

As regras abaixo são invioláveis no sentido preciso de que **não dependem de disciplina de
quem opera**: cada uma está implementada no código e verificada por teste. Regra que
existisse apenas como recomendação escrita seria convenção, e convenção se erode no
primeiro dia em que atrasa uma entrega. A coluna "onde vive" aponta o mecanismo que a torna
impossível de violar por descuido, e em três casos o mecanismo é uma **ausência** — o
caminho errado não existe, em vez de existir e ser verificado.

| Id | Regra | Onde vive |
|---|---|---|
| R1 | Evidência escrita pelo agente nunca conta como evidência | `filtrar_contaminacao` separa `ESCRITO_PELO_AGENTE` sem oferecer parâmetro de tolerância; um limiar configurável seria o caminho de volta ao defeito |
| R2 | `ESCRITO_PELO_AGENTE` não decide nem quando é a única origem presente | Ausência do valor na tupla `PRECEDENCIA`; ausência é mais forte que última posição, porque última posição decide no caso novo |
| R3 | Contradição é reportada, nunca resolvida em silêncio | `contradicoes` devolve `Contradicao` e não escolhe lado; nenhuma função do volume remove uma das duas entradas |
| R4 | Contradição viaja no veredicto inclusive quando ele é indeciso | `Veredicto.contradicoes` é preenchido antes da precedência, no mesmo lugar para os dois caminhos |
| R5 | Precedência não é cascata de reserva | A fonte de maior precedência presente encerra a resolução; o ramo de `BASE_CONGELADA` só é alcançado quando não há entrada `OBSERVADO` vigente |
| R6 | Empate nunca decide, qualquer que seja o limiar | Verificação explícita do topo da contagem antes de comparar a fração, e não confiança em o limiar ser maior que a metade |
| R7 | Dominância abaixo do mínimo devolve indeciso, não palpite | `resolver` retorna `decisao=None`; não existe caminho que devolva a dominante com confiança rebaixada |
| R8 | Veredicto indeciso tem confiança nula e justificativa não vazia | Os **três** retornos indecisos de `resolver` — empate no topo da contagem, dominância abaixo do mínimo e nenhuma evidência vigente — passam `None` nos dois primeiros campos e uma justificativa com os números |
| R9 | Entrada fora da janela não conta para nada, inclusive para contradição | A janela é aplicada antes de `contradicoes`, e não depois |
| R10 | Falta de evidência nunca levanta; campo em branco sempre levanta | `entradas` devolve tupla vazia para chave desconhecida; `_chave_valida` levanta `ChaveInvalida` e `_decisao_valida` levanta `DecisaoInvalida`, a irmã que fecha a assimetria — decisão vazia não é alternativa |

## Por que R1 é a regra que sustenta as outras

Sem R1, todas as demais medem o eco. A dominância sobe, o limiar é atingido, a confiança
sai alta e a contradição desaparece — e cada um desses passos parece correto isoladamente.
O componente inteiro produziria números impecáveis sobre a própria atividade. É por isso
que a regra é implementada por separação de origem no ato do registro, e não por
verificação posterior: depois que a entrada está gravada sem procedência, nenhuma
heurística a recupera. Vale registrar o limite honesto de R1: ela garante que o eco
**marcado** não conta. Entrada de eco marcada por engano como observação passa, e nenhuma
verificação interna a detecta. A defesa contra esse caso é externa e está descrita no ramo
de triagem de [`06-Fluxogramas.md`](06-Fluxogramas.md) — conferir a procedência item a item
quando a contradição não fecha.

## Por que R3 e R7 são a mesma disciplina em dois lugares

R3 proíbe resolver contradição em silêncio; R7 proíbe transformar evidência insuficiente em
resposta. As duas são a mesma recusa: **não produzir certeza que não existe**. A tentação é
simétrica e prática — nos dois casos há uma resposta plausível à mão, e devolvê-la faz o
sistema parecer mais completo. O custo de devolvê-la é assimétrico: quem recebe uma decisão
não confere de novo, e uma decisão errada com aparência de decisão certa custa mais que
pendência nenhuma. No sistema de origem, a formulação dessa disciplina é anterior ao código
e mais dura: classificar um valor numa categoria genérica só para o saldo fechar é
inventar, e inventar é a única coisa proibida sem exceção.

## Regras de operação derivadas

Três consequências práticas seguem das dez e valem ser ditas. A primeira é que **corrigir
uma entrada é registrar outra**: `Entrada` é congelada, e a correção entra como decisão
humana com data nova, o que preserva a trilha em vez de reescrevê-la. A segunda é que
**mudar o valor de `janela_dias` muda veredictos sem mudar o armazém** — a expiração é
calculada por consulta, então uma janela ampliada revive evidência antiga, e ampliar a
janela para obter a resposta desejada é adulteração de método, não ajuste de parâmetro. A
terceira é que **uma chave com contradição aberta nunca produz confiança alta**, nem sob
decisão humana: a decisão humana vence o veredicto, e não encerra a contradição na fonte.

Uma palavra sobre a extensão de R10, porque ela foi acrescentada depois da auditoria e a razão
importa mais que a linha de código. `ChaveInvalida` já recusava chave em branco, mas `decisao`
aceitava a string vazia, e a assimetria não tinha defesa: uma entrada com decisão vazia somava
contagem, podia empatar com uma decisão real e chegar ao chamador dentro de um veredicto de
confiança alta. Recusar o branco não exige conhecimento de domínio nenhum — é a mesma
verificação, no campo vizinho. O que **continua** fora do código é a lista de valores-marcador
de ausência de cada operação, do tipo categoria genérica que não ensina nada: essa lista é
conhecimento de quem usa, fixá-la aqui decidiria por todos os domínios, e ela segue registrada
em [`16-Roadmap.md`](16-Roadmap.md).
