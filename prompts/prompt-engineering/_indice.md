# Prompts de engenharia de prompt

> Biblioteca transversal · atualizado em 2026-07-29
> Esta pasta **não é um volume**: não tem front-matter de seção e não passa pelos gates de
> volume. Os três prompts abaixo foram extraídos do volume
> [`07-PROMPT-ENGINE`](../../07-PROMPT-ENGINE/01-Introducao.md) e operam o motor descrito lá.

## Regra desta pasta

Todo prompt aqui é **executável como está**: as variáveis estão declaradas com tipo, o formato
de saída é explícito, e nenhum deles pede ao modelo que invente informação ausente. Um prompt
que dependesse de contexto não declarado seria irreprodutível, e prompt irreprodutível não tem
como ser avaliado — o que contraria a razão de existir do volume 07.

## Catálogo

| Arquivo | O que faz | Variáveis | Seção de origem |
|---|---|---|---|
| [`declarar-contrato.md`](declarar-contrato.md) | Converte um prompt solto em `PromptTemplate` com variáveis tipadas | `prompt_bruto:str`, `linguagem:str` | [`08-Modelos.md`](../../07-PROMPT-ENGINE/08-Modelos.md), [`11-Implementacao.md`](../../07-PROMPT-ENGINE/11-Implementacao.md) |
| [`derivar-casos-de-ouro.md`](derivar-casos-de-ouro.md) | Produz casos de ouro com padrão esperado ancorado no fato | `contrato:str`, `dominio:str`, `quantidade:int` | [`09-Boas-Praticas.md`](../../07-PROMPT-ENGINE/09-Boas-Praticas.md), [`14-Metricas.md`](../../07-PROMPT-ENGINE/14-Metricas.md) |
| [`decidir-promocao.md`](decidir-promocao.md) | Emite parecer de promoção a partir dos números medidos | `taxa_a:float`, `taxa_b:float`, `total_casos:int`, `custo_a:float`, `custo_b:float` | [`07-Regras.md`](../../07-PROMPT-ENGINE/07-Regras.md), [`15-Checklist.md`](../../07-PROMPT-ENGINE/15-Checklist.md) |

## Como usar

Cada arquivo traz o corpo do prompt em um bloco de código, a declaração de variáveis na forma
que `PromptTemplate` aceita, e a lista de casos de ouro que a bateria dele deveria conter. O
caminho recomendado é copiar o corpo e a declaração para código, construir o template — o que já
verifica se corpo e variáveis concordam — e registrar. O terceiro prompt é o único que não deve
ser promovido sem revisão humana do parecer, porque a saída dele influencia uma decisão de
produção.
