# BAB — Before, After, Bridge

> Técnica pública de estruturação de prompt · atualizado em 2026-07-29
> **Estado de atribuição:** `DOMINIO-PUBLICO-SEM-ATRIBUICAO-SEGURA`
> Técnica de domínio público, origem não atribuída com segurança. A estrutura circula há
> muito tempo como fórmula de redação persuasiva e foi adotada em prompting; este arquivo
> **não** afirma quem a formulou nem quando.

## O que a sigla expande

| Letra | Campo | O que o campo responde |
|---|---|---|
| **B** | *Before* (antes) | Qual é o estado atual, com evidência |
| **A** | *After* (depois) | Qual é o estado desejado, de forma verificável |
| **B** | *Bridge* (ponte) | O que leva de um ao outro |

É a única das seis estruturas desta pasta que **não descreve uma tarefa** — descreve uma
**transição**. Essa diferença determina tudo sobre quando usá-la.

## Por que funciona

Prompts de melhoria costumam falhar por uma razão específica: pedem o destino sem
descrever a origem. "Melhore este código", "otimize este processo", "deixe este texto mais
claro" — em todos os três, o modelo tem de inferir o que está ruim, e a inferência dele
sobre o que está ruim é a parte que você não controla. O resultado típico é uma reescrita
que resolve um problema que você não tinha e preserva o que você queria mudar.

BAB obriga a nomear o estado atual **e** o estado desejado antes de pedir o caminho. Com os
dois pontos fixos, o `Bridge` passa a ser uma pergunta bem-posta: existe uma diferença
concreta a fechar, e as propostas podem ser avaliadas contra ela.

O segundo efeito é sobre honestidade. Descrever o `Before` com evidência — números,
sintomas, ocorrências — frequentemente revela que o problema declarado não é o problema
real. Prompts BAB bem escritos costumam morrer na redação do primeiro campo, e isso é um
resultado útil: economizou-se a construção da ponte errada.

## Quando serve

- **Diagnóstico e proposta de mudança**: processo, arquitetura, texto, código, rotina
  operacional.
- **Justificação de decisão técnica**, quando é preciso registrar por que se saiu de A e
  chegou a B — é a forma natural de um registro de decisão de arquitetura (ver
  [`referencias/links.md`](../../referencias/links.md), ADR).
- **Escrita persuasiva e comunicação executiva**, que é o terreno de origem da fórmula:
  situação, benefício, meio.
- **Retrospectiva e pós-incidente**: `Before` é o que aconteceu, `After` é o que deveria
  acontecer na próxima vez, `Bridge` é a mudança de controle.

## Quando NÃO serve

- **Produção de artefato**, e não mudança de estado. "Escreva o memorial de cálculo" não
  tem um `Before`. Use RTF ou RISE.
- **Quando o `Before` não é conhecido com evidência.** Se você não tem o estado atual
  medido, o campo será preenchido com a suspeita, e a ponte será construída para o problema
  suspeito. Esse é o modo de falha mais caro do BAB: ele produz um plano coerente para um
  diagnóstico não verificado, e a coerência do plano é lida como confirmação do
  diagnóstico. Meça primeiro.
- **Quando o `After` é um adjetivo.** "Depois: um código limpo e escalável" não é estado
  desejado, é aspiração. Se não é verificável, não é `After`.
- **Quando o problema tem múltiplas causas independentes.** BAB tem uma ponte. Três causas
  distintas exigem três análises, e forçá-las numa ponte única produz um plano que não
  fecha nenhuma delas por completo.
- **Tarefas classificatórias e extrativas.** Não há transição envolvida.

## Exemplo concreto

Caso real de operação: uma rotina automatizada que trava por sobrecarga de varredura de
diretórios. O pedido informal seria "otimize a varredura", que convida o modelo a propor
paralelismo, cache e reescrita ao mesmo tempo, sem saber qual dos três resolve.

```text
# Before
Uma rotina Python varre um diretório de rede (T:\...) para localizar a pasta de cada
cliente e cruzar com uma lista de 40 contratos. Estado medido, não estimado:
- a varredura usa rglob sem limite de profundidade;
- a execução completa não terminou em 3 horas nas duas tentativas registradas;
- o log mostra que a varredura desce em subpastas de anos anteriores e em pastas de
  backup, que não contêm o que se procura;
- 100% do tempo está em I/O de rede; a CPU fica ociosa.

# After
A execução completa termina em menos de 10 minutos, com o MESMO conjunto de pastas
localizadas que a varredura exaustiva encontraria. Verificação de aceitação: rodar a
versão nova e a exaustiva sobre 5 clientes conhecidos e comparar os caminhos
encontrados, um a um. Divergência é reprovação, mesmo que a versão nova seja mais
rápida.

# Bridge
Proponha o caminho mais curto entre os dois estados, respeitando estas restrições:
- não é permitido mudar a estrutura do diretório de rede (é compartilhado e alheio);
- não é permitido paralelizar a ponto de saturar o compartilhamento SMB;
- a solução tem de degradar de forma visível: se uma pasta não for encontrada, isso
  precisa aparecer no relatório, não desaparecer silenciosamente.
Para cada alternativa proposta, diga o que ela custa e em que caso ela falha. Se duas
alternativas resolvem, prefira a que é mais fácil de reverter, não a mais rápida.
```

O que a estrutura entregou: o `Before` mostrou, com medição, que o gargalo era **profundidade
de varredura**, não falta de paralelismo — e portanto que a proposta óbvia (paralelizar)
atacaria o sintoma errado e ainda arriscaria saturar a rede. O `After` amarrou desempenho a
**equivalência de resultado**, fechando a porta para a otimização que fica rápida porque
deixou de olhar onde precisava. E o `Bridge` pediu custo e modo de falha de cada
alternativa, além de estabelecer o critério de desempate (reversibilidade sobre
velocidade), que é o critério que um operador quer e que um gerador de código raramente
adota por conta própria.

## Limitações

**1. O `Before` é onde mora a mentira.** Não a mentira deliberada: a estimativa escrita com
a confiança de medição. "A varredura está lenta" é impressão; "não terminou em 3 horas em
duas tentativas registradas" é dado. A ponte construída sobre impressão é indistinguível,
na forma, da ponte construída sobre dado — e é isso que a torna perigosa.

**2. `After` mal definido produz plano bonito e inverificável.** Se o estado desejado não
tem teste de aceitação, não há como reprovar a ponte, e qualquer proposta "atende".

**3. A estrutura pressupõe uma causa.** Com causas múltiplas e independentes, o `Bridge`
tende a virar uma lista de tudo, que é o oposto do que a técnica promete.

**4. Herança persuasiva.** A fórmula vem da redação de venda, e carrega o hábito de fazer o
`After` parecer melhor do que se pode entregar. Num contexto técnico esse hábito é um
defeito: o `After` deve ser o mínimo verificável, não o máximo desejável.

**5. Não há atribuição.** A fórmula é de domínio público e sua origem não é atribuída com
segurança neste arquivo. Nenhum autor, ano, empresa ou artigo é afirmado.

## Relacionados

- [`RISE.md`](RISE.md) — quando a ponte já é conhecida e o que falta é executá-la em ordem.
- [`TAG.md`](TAG.md) — quando o que falta é o critério de sucesso e não há estado anterior.
- [`proprietarios/AI-ENGINEERING-FRAMEWORK.md`](../proprietarios/AI-ENGINEERING-FRAMEWORK.md)
  — o ciclo da plataforma usa a mesma lógica em escala de volume: estado, estado desejado
  (Definição de PRONTO) e gates como ponte.
