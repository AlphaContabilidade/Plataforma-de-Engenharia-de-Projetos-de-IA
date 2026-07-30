---
volume: "03"
volume_nome: DISCOVERY
tipo: PROCESSO
secao: 15-Checklist
status: PRONTO
atualizado_em: 2026-07-30
---

# Checklist

Duas listas: a de quem acrescenta conteúdo ao catálogo e a de quem entrega uma especificação para
alguém construir. Elas são separadas porque erram por motivos diferentes — a primeira erra por
entusiasmo, a segunda por prazo.

## Antes de acrescentar uma lacuna ao catálogo

- O motivo declarado nomeia **o que muda na construção** se a resposta for diferente? Se não nomeia,
  a lacuna é o anti-padrão A4 e não entra.
- O peso é valor informativo, e não esforço de implementação nem importância do assunto para o
  negócio? A pergunta de controle é quantas outras decisões mudam conforme a resposta.
- Se a lacuna não é universal, ela declara plataforma, contexto, ou os dois? `validar_catalogo`
  levanta quando não declara, e a falha imediata é o comportamento desejado.
- O identificador é novo, estável e descritivo? Identificador muda de nome nunca, porque
  especificação antiga guarda o identificador.
- As opções, quando existem, oferecem caminho sem restringir a resposta livre?
- A suíte continua verde depois de acrescentar? `validar_catalogo` reprova id duplicado e peso
  fora da faixa, então erro de forma cai no gate.
- **As contagens escritas em `12-Exemplos.md` foram remedidas?** Aqui há uma lacuna real de
  cobertura, e vale declará-la em vez de fingir que o gate cobre: nenhum teste da suíte confere
  os números que a prosa daquela seção afirma — quantas lacunas o catálogo tem, quantas ficam
  ativas em cada passo, quantas perguntas o caminho correto exige. Acrescentar uma lacuna ao
  catálogo torna esses números falsos **sem que nada fique vermelho**. Enquanto essa verificação
  não existir, remedir à mão é obrigação de quem mexe no catálogo, não zelo opcional.

## Antes de entregar uma especificação

- `Especificacao.completa` é `True`? Se é `False`, a entrega vai acompanhada da razão, e a razão é
  uma das duas: inferência pendente ou lacuna universal aberta.
- A lista de inferências não confirmadas está vazia? Palpite pendente é afirmação que ninguém fez.
- As decisões abertas foram **lidas** por quem vai construir, e não apenas anexadas? Cada uma é uma
  escolha que alguém fará — a diferença é se será uma escolha consciente ou uma consequência.
- Nenhum valor aparece decidido sem estar? A verificação rápida é procurar por origem
  `PADRAO_ASSUMIDO` na saída: ela não deveria existir.
- A origem de cada resposta está correta? Resposta obtida por dedução de quem conduziu a conversa é
  `INFERIDO`, não `RESPONDIDO`, e a diferença aparece na tabela.
- O número de perguntas feitas e o número de decisões abertas foram anotados? São as duas métricas
  que se leem juntas, e nenhuma delas se recupera depois.
