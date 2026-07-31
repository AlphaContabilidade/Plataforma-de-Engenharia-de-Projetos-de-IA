---
volume: "03"
volume_nome: DISCOVERY
tipo: PROCESSO
secao: 15-Checklist
status: PRONTO
atualizado_em: 2026-07-31
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
- **A prosa em volta dos blocos de `12-Exemplos.md` foi remedida?** Os *blocos de código* daquela
  seção agora são executados por `test_passo_a_passo.py`: mexer no catálogo e quebrar um `assert`
  deixa a suíte vermelha, e essa parte deixou de depender de disciplina. O que **continua
  descoberto** é o texto ao redor — "trinta e sete lacunas", "catorze perguntas", "seis
  universais". Nenhum teste lê número escrito por extenso. Acrescentar uma lacuna torna a frase
  falsa **sem que nada fique vermelho**, e remedir à mão segue sendo obrigação de quem mexe, não
  zelo opcional. Em relação à versão anterior deste item mudou o tamanho da obrigação, não a
  existência dela.

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
