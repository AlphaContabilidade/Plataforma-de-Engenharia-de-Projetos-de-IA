# derivar-casos-de-ouro

**Origem:** volume 07, seções `09-Boas-Praticas` e `14-Metricas`.
**Serve para:** produzir a bateria inicial de casos de ouro a partir do contrato de um prompt.
**Não serve para:** substituir os casos vindos de incidentes reais, que são os mais valiosos e só
existem depois de a falha ter acontecido.

## Corpo

```text
Voce vai escrever casos de ouro para avaliar um prompt.

Contrato do prompt, com nome, corpo e variaveis declaradas:
{contrato}

Dominio de aplicacao: {dominio}
Quantidade de casos pedida: {quantidade}

Um caso de ouro tem quatro campos: nome curto em kebab-case, entradas com um valor
por variavel obrigatoria, um padrao de expressao regular que a saida correta deve
casar, e uma descricao de uma linha dizendo qual risco o caso cobre.

Regras de construcao:
- Ancore o padrao no fato exigido, na estrutura obrigatoria ou no rotulo esperado.
  Nao escreva padrao que exija a redacao inteira: a redacao varia legitimamente e
  o caso passaria a dar alarme falso.
- Nao escreva dois casos que cubram o mesmo risco com dados diferentes. Prefira
  cobrir riscos distintos: caminho normal, valor de fronteira, entrada ambigua,
  entrada que deveria ser recusada.
- Todo valor de entrada tem de respeitar o tipo declarado no contrato.
- Nao invente dado que pareca real quando ele nao e. Use valores claramente
  ficticios e diga na descricao que sao ficticios.
- Se a quantidade pedida for maior que o numero de riscos distintos que voce
  consegue justificar, entregue menos casos e explique a diferenca.

Formato de saida, sem texto adicional:
## Casos
Um bloco por caso, com as quatro linhas: nome, entradas, esperado, descricao.
## Riscos nao cobertos
Lista dos riscos que voce identificou e nao conseguiu transformar em caso
verificavel, ou a palavra NENHUM.
```

## Declaração

```python
derivar_casos = PromptTemplate(
    nome="derivar-casos-de-ouro",
    corpo=CORPO_DERIVAR_CASOS,
    variaveis=(
        Variavel("contrato", str, descricao="Nome, corpo e variaveis do prompt a avaliar"),
        Variavel("dominio", str, descricao="Dominio de aplicacao, ex.: classificacao contabil"),
        Variavel("quantidade", int, descricao="Numero de casos pedido; a saida pode entregar menos"),
    ),
)
```

## Casos de ouro sugeridos

| Nome | Entradas | Padrão esperado | Por que este caso |
|---|---|---|---|
| `tres-casos-distintos` | contrato simples, `quantidade` igual a 3 | `r"## Casos"` e três ocorrências de `r"nome:"` | Verifica a contagem pedida e o formato de saída |
| `pede-mais-do-que-cabe` | contrato trivial, `quantidade` igual a 20 | `r"## Riscos nao cobertos"` com conteúdo | Verifica que a quantidade excessiva é recusada com explicação em vez de preenchida com variações redundantes |
| `tipo-respeitado` | contrato com variável `int` | ausência de valor entre aspas para essa variável | Verifica que o tipo declarado é respeitado nas entradas geradas |
