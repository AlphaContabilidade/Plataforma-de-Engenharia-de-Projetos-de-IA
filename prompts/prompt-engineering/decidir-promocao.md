# decidir-promocao

**Origem:** volume 07, seções `07-Regras` e `15-Checklist`.
**Serve para:** transformar os números medidos em um parecer de promoção com justificativa.
**Não serve para:** decidir sozinho. A saída é um parecer para revisão humana, porque ela influencia
uma mudança de comportamento em produção.

## Corpo

```text
Voce vai emitir um parecer sobre promover ou nao uma versao de prompt.

Numeros medidos sobre a MESMA amostra de casos de ouro:
- taxa de acerto da versao de referencia (A): {taxa_a}
- taxa de acerto da versao candidata (B): {taxa_b}
- total de casos na amostra: {total_casos}
- custo por execucao de A, em unidade monetaria: {custo_a}
- custo por execucao de B, em unidade monetaria: {custo_b}

Calcule e reporte:
1. A deriva, que e a taxa de B menos a taxa de A. Diga o sinal.
2. A menor variacao detectavel na amostra, que e 1 dividido pelo total de casos.
3. Se a deriva em modulo e maior que a menor variacao detectavel. Se nao for, o
   resultado esta dentro da granularidade da amostra e nao sustenta decisao.
4. A variacao percentual de custo de B em relacao a A.

Aplique as regras, nesta ordem, e pare na primeira que decidir:
- Se o total de casos e zero, o parecer e NAO PROMOVER: sem evidencia nao se promove.
- Se a deriva e negativa, o parecer e NAO PROMOVER.
- Se a deriva e zero, o parecer e NAO PROMOVER: empate troca risco conhecido por
  desconhecido sem ganho medido.
- Se a deriva e positiva mas menor ou igual a menor variacao detectavel, o parecer
  e AMPLIAR AMOSTRA.
- Se a deriva e positiva e o custo de B subiu mais de 50 por cento, o parecer e
  DECISAO HUMANA, com o compromisso explicitado.
- Caso contrario, o parecer e PROMOVER.

Nao arredonde para favorecer uma conclusao. Nao acrescente criterio que nao esta
nesta lista. Se algum numero de entrada for incoerente, por exemplo taxa fora do
intervalo de zero a um, o parecer e ENTRADA INVALIDA e voce diz qual numero.

Formato de saida, sem texto adicional:
## Numeros
As quatro linhas calculadas.
## Parecer
Uma das palavras: PROMOVER, NAO PROMOVER, AMPLIAR AMOSTRA, DECISAO HUMANA,
ENTRADA INVALIDA.
## Justificativa
Uma frase citando qual regra decidiu.
```

## Declaração

```python
decidir_promocao = PromptTemplate(
    nome="decidir-promocao",
    corpo=CORPO_DECIDIR_PROMOCAO,
    variaveis=(
        Variavel("taxa_a", float, descricao="Resultado.taxa_acerto da versao de referencia"),
        Variavel("taxa_b", float, descricao="Resultado.taxa_acerto da versao candidata"),
        Variavel("total_casos", int, descricao="Resultado.total; zero significa bateria vazia"),
        Variavel("custo_a", float, descricao="Custo por execucao de A, medido no envelope do executor"),
        Variavel("custo_b", float, descricao="Custo por execucao de B, medido no envelope do executor"),
    ),
)
```

## Casos de ouro sugeridos

| Nome | Entradas | Padrão esperado | Por que este caso |
|---|---|---|---|
| `bateria-vazia` | `total_casos` igual a 0 | `r"NAO PROMOVER"` | Verifica a regra R8: ausência de evidência não é evidência de acerto |
| `empate` | taxas iguais, 30 casos | `r"NAO PROMOVER"` | Verifica que empate não promove |
| `dentro-da-granularidade` | 0,60 contra 0,70 com 3 casos | `r"AMPLIAR AMOSTRA"` | Verifica que ganho abaixo da menor variação detectável não decide |
| `ganho-com-custo-dobrado` | 0,70 contra 0,90 com 30 casos, custo de 0,01 para 0,02 | `r"DECISAO HUMANA"` | Verifica que o compromisso entre acerto e custo sobe para decisão humana |
| `promover-limpo` | 0,70 contra 0,90 com 30 casos, custo igual | `r"PROMOVER"` | Verifica o caminho de aprovação |
| `taxa-invalida` | `taxa_b` igual a 1,4 | `r"ENTRADA INVALIDA"` | Verifica que número incoerente não é acomodado |
