---
volume: "12"
volume_nome: MEMORY
tipo: ENGINE
secao: 14-Metricas
status: RASCUNHO
atualizado_em: 2026-07-30
---

# Métricas

Cada métrica abaixo tem definição operacional, unidade e origem do dado. Métrica sem unidade
não compara e métrica sem origem não audita. Três delas saem direto do veredicto; três exigem
instrumentação de quem chama, e isso está dito onde é o caso. Os números citados nesta seção
vêm da execução do exemplo de [`12-Exemplos.md`](12-Exemplos.md) — são ilustração de método
medida, e não referência de mercado.

| Métrica | Definição operacional | Unidade | Origem |
|---|---|---|---|
| Taxa de indecisão | número de chamadas de `resolver` com `decisao is None` dividido pelo total de chamadas na janela de medição | fração de 0 a 1 | `Veredicto.decisao` |
| Fração de eco | `Veredicto.descartadas` dividido pelo total de entradas da chave no armazém, no momento da consulta | fração de 0 a 1 | `Veredicto.descartadas` e `len(memoria.entradas(chave))` |
| Contradições abertas | número de `Contradicao` distintas produzidas por `contradicoes` sobre as entradas vigentes de todas as chaves | contagem absoluta | `contradicoes(...)` |
| Idade média da evidência | média de `(hoje - entrada.em).days` sobre as entradas válidas e vigentes que sustentaram o veredicto | dias | instrumentação de quem chama |
| Distribuição de confiança | contagem de veredictos decididos por nível, nas três categorias de `Confianca` | contagem absoluta por nível | `Veredicto.confianca` |
| Taxa de sobreposição humana | número de chaves com ao menos uma entrada `DECIDIDO_POR_HUMANO` vigente, dividido pelo número de chaves consultadas | fração de 0 a 1 | instrumentação de quem chama |

## Taxa de indecisão: por que ela não deve ser minimizada

A taxa de indecisão é a métrica mais fácil de melhorar pelo motivo errado. Baixar
`dominancia_minima` a reduz imediatamente e sem esforço, e o efeito colateral — mais decisões
com evidência fraca — não aparece em nenhum painel, porque medir erro exige conferência que
ninguém faz quando a decisão chegou pronta. É o anti-padrão A4 de
[`10-Anti-Patterns.md`](10-Anti-Patterns.md).

A leitura correta é conjunta: taxa de indecisão só significa algo ao lado do custo médio de uma
pendência e do custo médio de um erro no domínio. Se a pendência custa dez minutos de uma pessoa
e o erro custa um lançamento financeiro incorreto, a taxa de indecisão **aceitável** é alta. O
componente não escolhe esse ponto e não tem opinião sobre ele: por isso o limiar é parâmetro, e
não constante.

## Fração de eco: o número que diz se a memória está medindo a si mesma

Esta é a métrica que o defeito de produção pede. No passo 2 do exemplo executável, a fração de
eco é de dez em vinte entradas, ou zero vírgula cinco, e a dominância crua já havia invertido: o
lado escrito pelo agente liderava por onze contra nove, fração de zero vírgula cinquenta e
cinco. Os dois números juntos descrevem o estado exato em que um sistema sem a guarda troca a
decisão com base na própria escrita.

A leitura operacional é simples e tem um limite honesto. Fração de eco crescente em uma chave
significa que o agente está agindo mais do que observando ali, e a partir de certo ponto a
memória daquela chave é quase toda atividade própria. O que a métrica **não** diz é se a
marcação está correta: uma memória com fração de eco igual a zero pode estar limpa ou pode estar
com todo o eco marcado como observação, e os dois casos são indistinguíveis por dentro. Fração
de eco exatamente zero em uma chave onde o agente escreve é, portanto, motivo de suspeita, e não
de tranquilidade.

## Contradições abertas: contagem e tempo, nunca só contagem

A contagem sozinha engana, porque uma contradição nova e uma de três meses contam igual. O par
útil é contagem mais idade, e a idade sai de `congelada_em`: a diferença entre `hoje` e essa data
é o tempo mínimo em que a base envelheceu sem revisão. No exemplo executável há exatamente uma
contradição aberta ao final de todos os sete passos, e ela sobreviveu inclusive ao passo da
decisão humana — o que é o comportamento correto e a razão de a métrica existir. Contradição que
some ao ser contornada não é métrica, é alívio.

O sinal complementar é `n_observacoes` dentro de cada contradição, que dá a força do lado
observado. Uma contradição com uma observação é um alerta; com nove, como no exemplo, é um
veredicto sobre a base congelada, e o encaminhamento correto é recuratoria da fonte no volume
vizinho de conhecimento em vez de tolerância continuada.

## Idade média da evidência e as duas métricas instrumentadas

Idade média da evidência responde se as decisões estão apoiadas em observação recente ou em
memória antiga que apenas não expirou. Ela precisa de instrumentação porque `resolver` não
devolve as entradas que usou — devolve o veredicto. Envolver a chamada em uma função que também
calcule a média sobre as entradas vigentes é a forma que preserva a fronteira do componente, do
mesmo jeito que a taxa de sobreposição humana, que exige varrer as chaves consultadas em busca
de decisão humana vigente. Essa última é a métrica de custo de operação: sobreposição humana
crescente significa que a memória está decidindo mal ou que o limiar está alto demais para o
domínio, e distinguir os dois casos exige olhar a taxa de indecisão junto — pendência alta com
sobreposição alta indica limiar apertado, enquanto pendência baixa com sobreposição alta indica
decisão automática que as pessoas estão corrigindo.
