# Prefácio

## Por que esta plataforma existe

Documentação técnica de engenharia de IA envelhece mal e mente cedo. Ela mente de três
maneiras previsíveis: afirma que um componente funciona de um jeito que o código já
abandonou; cita um framework, um paper ou um número que ninguém verificou; e declara-se
completa porque tem muitas páginas. As três formas de mentira têm a mesma origem — nada
verifica o texto além da boa vontade de quem o leu por último.

A AI-ENGINEERING-OS nasceu de uma especificação ambiciosa: 42 volumes, 18 seções por
volume, mais de oito mil páginas, dois mil prompts, trezentos agentes, quinhentos exemplos
de código. Ao revisar a especificação, ficou claro que a meta de volume e a regra de
qualidade ("nunca gere conteúdo superficial") se contradiziam: preencher 756 seções obriga
o conteúdo a ficar genérico. A escolha foi então inverter a prioridade. Em vez de construir
os 756 arquivos e esperar que fossem bons, construir a **máquina que só aceita arquivo
bom** — e depois produzir volumes, um por vez, atravessando a máquina.

O ativo desta plataforma é a linha de produção: um contrato legível por máquina, um
validador que reprova conteúdo vazio, um modelo de auditoria por outro modelo, e uma
definição de "pronto" que é executável em vez de opinável. O acervo é a consequência. Se
alguém copiasse todos os volumes e deixasse a máquina para trás, teria levado a parte
menos valiosa.

## Para quem é

Para **quem constrói sistemas de IA e precisa de decisões defensáveis**, não de inspiração.
Três perfis, concretamente:

- **O engenheiro que vai implementar.** Encontra contrato de dados, invariantes, exemplos
  que rodam e testes que provam o que os exemplos afirmam. Cada bloco de código citado por
  um volume existe como arquivo e tem teste ao lado — não é ilustração, é código.
- **O arquiteto que vai decidir.** Encontra o escopo de cada domínio, o que está fora dele,
  os anti-patterns com o custo concreto de errar, e as métricas com unidade e fonte. As
  fronteiras entre volumes são explícitas porque a sobreposição entre domínios foi tratada
  como problema, não ignorada.
- **O agente de IA que vai produzir o próximo volume.** Encontra em `CLAUDE.md` e em
  [Convencoes.md](Convencoes.md) tudo que precisa para gerar conteúdo que passa nos gates,
  e encontra nos gates a recusa quando não passa. O acervo é escrito para ser lido por
  máquina tanto quanto por pessoa.

Também serve a quem herda o projeto meses depois. É a razão de cada diagrama ter parágrafo
descritivo obrigatório, de cada regra citar o nome da função que a implementa, e de cada
pendência ter lugar próprio em vez de virar um marcador solto no meio do texto.

## O que esta plataforma deliberadamente não é

Dizer o que uma coisa não é economiza mais tempo do que dizer o que ela é.

- **Não é um curso.** Não há progressão didática, exercício, nem preocupação com nivelar o
  leitor. Cada volume assume o contexto que declara em `03-Escopo` e aponta os
  pré-requisitos em `depende_de`.
- **Não é uma coleção de receitas para copiar.** Prática sem razão explícita é superstição:
  a seção `09-Boas-Praticas` sempre diz por que, e a `10-Anti-Patterns` sempre diz quanto
  custa errar. Receita descontextualizada é o que produz sistema que funciona por acidente.
- **Não é um catálogo de ferramentas nem um comparativo de fornecedores.** Preço, limite de
  requisição e nome de modelo mudam em semanas. Os três volumes que tocam esse terreno são
  marcados como perecíveis, ficam finos de propósito e apontam para fonte viva em vez de
  fixar número.
- **Não é uma coleção de frameworks proprietários.** Técnicas públicas de prompt são
  descritas como públicas. Nomes que apareceram na especificação original sem definição
  ficam registrados em `frameworks/_backlog.md` como pendência do autor, com a declaração
  explícita de que não foram inventados. Inventar definição para um nome bonito seria a
  falha mais grave que este acervo pode cometer.
- **Não é uma medida de produtividade por página.** As metas numéricas da especificação
  original estão registradas no `ROADMAP.md` como estimativa, e explicitamente não são
  critério de aceite. O critério é a Definição de PRONTO.
- **Não é neutra sobre o próprio estado.** Um volume que não passou nos gates aparece como
  `RASCUNHO`, e isso é visível em `/status` para quem quiser olhar. O acervo prefere admitir
  que dezenas de volumes estão pendentes a fingir que estão prontos.

## Como ler

Comece por [Como-Utilizar.md](Como-Utilizar.md) se a intenção é produzir. Comece por
[Convencoes.md](Convencoes.md) se a intenção é entender as regras. Comece por
[Arquitetura-Geral.md](Arquitetura-Geral.md) se a intenção é entender a máquina. Se algum
termo parecer usado de forma técnica e específica, ele está no
[Glossario.md](Glossario.md) — e está lá justamente porque é usado sempre no mesmo sentido.
