# templates/

> Biblioteca transversal · atualizado em 2026-07-29
> **Estado: vazia.** Nenhum template publicado até agora. A razão está abaixo.

## O que esta pasta é

O lugar dos artefatos **reutilizáveis e prontos para copiar** que a plataforma oferece: esqueleto
de seção, esqueleto de volume, estrutura de relatório de auditoria, formulário de decisão de
arquitetura, cabeçalho de exemplo executável.

É a contraparte concreta do volume `40-TEMPLATES`, do tipo `BIBLIOTECA` — o tipo que, no
contrato, dispensa `04-Arquitetura` e `05-Diagramas` e ganha `04-Catalogo.md`. Acervo catalogado
não tem arquitetura própria: tem itens e um índice.

## Por que está vazia

Porque template só é útil quando é **extraído** de algo que funcionou, e não **projetado** antes
de existir uso.

Um template projetado no vácuo carrega as suposições de quem o escreveu sobre um trabalho que
ainda não foi feito. Ele fica bonito, é preenchido uma vez, e na segunda vez descobre-se que
faltavam três campos e que dois dos que existem nunca são usados. A partir daí ninguém confia
nele — mas ele continua na pasta, e quem chega copia.

O caminho oposto é mais lento e produz template que aguenta: primeiro se faz o volume-piloto
(`07-PROMPT-ENGINE`) com as 18 seções passando nos três gates; depois se olha o que se repetiu,
o que variou por tipo de volume, e o que teve de ser corrigido em todas as seções pelo mesmo
motivo. **É esse resíduo que é template.**

Há dois templates que **já existem** neste acervo, e não por acaso: eles nasceram de uso real,
não de projeto antecipado.

- [`agentes/_template-agente.md`](../agentes/_template-agente.md) — as 13 rubricas, que vinham
  da especificação e foram testadas contra um agente concreto (`auditor-fable`).
- [`exemplos/_template-exemplo.md`](../exemplos/_template-exemplo.md) — o contrato de exemplo
  executável, derivado do que o gate de teste efetivamente exige.

Nenhum dos dois está nesta pasta, e isso é deliberado: template vive perto do que ele serve.
`templates/` é para o que serve ao acervo **todo**.

## Como um template entra aqui

1. **Duas ocorrências reais antes da abstração.** Um único caso não revela o que é essencial e o
   que era daquele caso. Duas revelam o que é comum; três confirmam.
2. **Todo campo tem de ter sido preenchido com conteúdo diferente ao menos uma vez.** Campo que
   nas duas ocorrências recebeu o mesmo texto não é campo — é conteúdo fixo, e deve estar no
   corpo do template, não como lacuna a preencher.
3. **Nenhum campo de exemplo com dado fabricado.** Se o template traz exemplo, ele é recorte de
   caso real. Exemplo inventado dentro de template é a forma mais eficiente de propagar
   invenção: ele é copiado literalmente, muitas vezes, por quem confia no template.
4. **Instrução de preenchimento junto do campo**, não num guia separado. Guia separado
   dessincroniza.
5. **Registro no `04-Catalogo.md` do volume `40-TEMPLATES`** quando aquele volume existir. Até
   então, no índice deste arquivo.

## Índice

Vazio. Quando o primeiro template for extraído, ele é listado aqui com uma linha dizendo **de
qual uso ele foi extraído** — a procedência é parte do template, porque é o que permite julgar se
ele se aplica ao seu caso.

## Relacionados

- [`frameworks/proprietarios/AI-ENGINEERING-FRAMEWORK.md`](../frameworks/proprietarios/AI-ENGINEERING-FRAMEWORK.md)
  — o ciclo do qual os templates serão extraídos.
- [`diagramas/README.md`](../diagramas/README.md) — mesma política, aplicada a diagramas.
