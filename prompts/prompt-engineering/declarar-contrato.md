# declarar-contrato

**Origem:** volume 07, seções `08-Modelos` e `11-Implementacao`.
**Serve para:** converter um prompt escrito solto em código no contrato tipado que o motor exige.
**Não serve para:** melhorar a redação do prompt — isso é otimização, e é assunto do volume 29.

## Corpo

```text
Voce vai converter um prompt solto em um contrato tipado.

Prompt bruto, exatamente como esta hoje no codigo:
{prompt_bruto}

Linguagem de destino: {linguagem}

Faca, nesta ordem:
1. Liste cada informacao que o prompt precisa receber de fora. Para cada uma, diga
   o nome em snake_case, o tipo concreto que o chamador deve passar, se e
   obrigatoria, e uma descricao de uma linha do que ela contem.
2. Reescreva o corpo do prompt trocando cada informacao externa por um placeholder
   entre chaves com exatamente o nome que voce declarou. Nao altere o sentido do
   texto e nao acrescente instrucao nova.
3. Emita a declaracao do template na linguagem de destino.

Regras:
- Todo placeholder do corpo tem de estar declarado, e toda variavel declarada tem
  de aparecer no corpo. Divergencia nas duas direcoes e erro.
- Escolha o tipo mais estreito que aceita os valores legitimos. Se o valor
  legitimo pode ser de mais de um tipo, declare o tipo estreito e diga na
  descricao que o chamador precisa normalizar antes.
- Nao invente informacao que o prompt bruto nao pede. Se algo estiver ambiguo,
  liste em "Ambiguidades" no fim e nao resolva por conta propria.

Formato de saida, nesta ordem e sem texto adicional:
## Variaveis
Uma linha por variavel: nome | tipo | obrigatoria | descricao
## Corpo com placeholders
O texto reescrito, em bloco de codigo.
## Declaracao
O codigo do template, em bloco de codigo.
## Ambiguidades
Lista, ou a palavra NENHUMA.
```

## Declaração

```python
declarar_contrato = PromptTemplate(
    nome="declarar-contrato",
    corpo=CORPO_DECLARAR_CONTRATO,
    variaveis=(
        Variavel("prompt_bruto", str, descricao="Prompt como esta hoje no codigo, sem edicao"),
        Variavel("linguagem", str, descricao="Linguagem da declaracao de saida, ex.: Python"),
    ),
)
```

## Casos de ouro sugeridos

| Nome | Entradas | Padrão esperado | Por que este caso |
|---|---|---|---|
| `uma-variavel` | prompt com um único trecho variável | `r"## Variaveis"` e `r"\|\s*str\s*\|"` | Verifica o caminho mais simples e a presença das quatro seções de saída |
| `tipo-numerico` | prompt que cita uma quantidade de horas | `r"\bfloat\b"` | Verifica se o tipo estreito é escolhido em vez de texto |
| `ambiguo` | prompt que menciona "o cliente" sem dizer se é nome ou identificador | `r"## Ambiguidades"` seguido de conteúdo | Verifica que a ambiguidade é reportada e não resolvida por conta própria |
