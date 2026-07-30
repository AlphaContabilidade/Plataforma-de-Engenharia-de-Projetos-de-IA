---
volume: "12"
volume_nome: MEMORY
tipo: ENGINE
secao: 08-Modelos
status: RASCUNHO
atualizado_em: 2026-07-30
---

# Modelos

Esta seção é a referência de contrato do componente. As assinaturas abaixo são as do código
executável em `exemplos/12-memory/`, e não uma paráfrase: quem lê aqui e escreve código
contra o que leu compila. Divergência entre esta seção e o código é defeito do volume, não
liberdade de redação.

## O armazém

```python
class ChaveInvalida(ValueError): ...

class Origem(StrEnum):
    OBSERVADO = "OBSERVADO"
    ESCRITO_PELO_AGENTE = "ESCRITO_PELO_AGENTE"
    BASE_CONGELADA = "BASE_CONGELADA"
    DECIDIDO_POR_HUMANO = "DECIDIDO_POR_HUMANO"

@dataclass(frozen=True, slots=True)
class Entrada:
    chave: str
    decisao: str
    origem: Origem
    em: date
    evidencia: str = ""

def contagem_de(entradas: Iterable[Entrada]) -> dict[str, int]: ...
def dominancia_de(entradas: Iterable[Entrada]) -> tuple[str, float] | None: ...

class MemoriaObservada:
    def registrar(self, entrada: Entrada) -> None: ...
    def entradas(self, chave: str) -> tuple[Entrada, ...]: ...
    def contagem(self, chave: str) -> dict[str, int]: ...
    def dominancia(self, chave: str) -> tuple[str, float] | None: ...
    def chaves(self) -> tuple[str, ...]: ...
```

`Entrada` é congelada com `slots`, o que a torna comparável por valor e barata de guardar em
tupla. Os quatro primeiros campos são obrigatórios: não há valor padrão para `origem`, e a
ausência de padrão é a decisão de projeto — um padrão qualquer permitiria adiar a
classificação da fonte, e a fonte mais fácil de esquecer de classificar é a escrita do
próprio agente. `chave` é normalizada na borda pelo construtor: espaço à esquerda ou à
direita é removido, e branco levanta `ChaveInvalida`. Normalizar nos dois lados — registro e
consulta — é o que garante que gravar com espaço e consultar sem espaço alcancem o mesmo
balde; sem isso existiriam dois baldes para a mesma identidade, cada um com metade das
observações e nenhum com dominância. `evidencia` é texto livre, fica fora de qualquer
contagem, e existe para o diagnóstico humano, que sem ele depende de reexecutar.

`contagem_de` e `dominancia_de` são funções puras sobre qualquer iterável de entrada, e é
por isso que os outros dois módulos as reusam em lugar de recontar. A ordem de saída de
`contagem_de` é estável — contagem decrescente, desempate alfabético — e não a ordem de
registro: ordem instável faria a dominante de um empate depender de qual observação chegou
primeiro, o que é sorte disfarçada de critério. A fração de `dominancia_de` **não** é
arredondada, porque arredondar antes de comparar com um limiar move o limiar.

As consultas do armazém são cruas de propósito: `contagem` e `dominancia` incluem o eco do
agente. `entradas` devolve tupla vazia para chave desconhecida e levanta apenas para chave
em branco — ausência de evidência é estado normal do domínio, chave vazia é erro de
programa, e misturar os dois faria o chamador tratar defeito como pendência.

## A guarda

```python
@dataclass(frozen=True, slots=True)
class Contradicao:
    chave: str
    decisao_congelada: str
    decisao_observada: str
    n_observacoes: int
    congelada_em: date

def filtrar_contaminacao(
    entradas: Iterable[Entrada],
) -> tuple[tuple[Entrada, ...], tuple[Entrada, ...]]: ...

def contradicoes(entradas: Iterable[Entrada]) -> tuple[Contradicao, ...]: ...
```

`filtrar_contaminacao` devolve o par `(evidencia_valida, descartadas)` preservando a ordem
de entrada. As descartadas são devolvidas em vez de sumirem porque a quantidade é um número
operacional: memória cujo volume é majoritariamente eco está medindo a própria atividade, e
isso precisa aparecer no painel descrito em [`14-Metricas.md`](14-Metricas.md).

`contradicoes` agrupa por chave, calcula a dominante considerando **apenas** origem
`OBSERVADO`, e emite uma `Contradicao` por entrada `BASE_CONGELADA` que discorde. O recorte
por origem é o que impede o eco de silenciar o relatório. O limiar de reporte é zero: uma
única observação discordante já produz `Contradicao`, e a força do sinal vai em
`n_observacoes` para que quem lê julgue. Suprimir contradição fraca seria decidir em
silêncio que a base congelada está certa, o que é a regra R3 de
[`07-Regras.md`](07-Regras.md) violada por omissão. A ordenação da saída é por chave, data
de congelamento e decisão congelada, de modo que o relatório é reproduzível.

## A regra de precedência

```python
class Confianca(StrEnum):
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAIXA = "BAIXA"

PRECEDENCIA: tuple[Origem, ...] = (
    Origem.DECIDIDO_POR_HUMANO,
    Origem.OBSERVADO,
    Origem.BASE_CONGELADA,
)

@dataclass(frozen=True, slots=True)
class Veredicto:
    decisao: str | None
    confianca: Confianca | None
    justificativa: str
    descartadas: int
    contradicoes: tuple[Contradicao, ...]

def resolver(
    memoria: MemoriaObservada,
    chave: str,
    *,
    hoje: date,
    janela_dias: int = 365,
    dominancia_minima: float = 0.7,
) -> Veredicto: ...
```

`PRECEDENCIA` tem três valores, e a origem ausente é a informação: `ESCRITO_PELO_AGENTE`
não aparece, e por isso não decide nem quando é a única coisa registrada. Os três níveis de
`Confianca` mapeiam para situações distintas e disjuntas: `ALTA` é dominância no mínimo ou
acima dele, sem contradição aberta; `MEDIA` é o rebaixamento por contradição, que alcança
inclusive a decisão humana; `BAIXA` é a base congelada decidindo sozinha, sem confirmação
observada. `Veredicto` com `decisao is None` é pendência humana, e nesse caso `confianca` é
`None` também — não existe palpite rotulado como confiança baixa.

Os parâmetros de `resolver` são todos por palavra-chave depois da chave. `hoje` é
obrigatório, sem padrão, porque um padrão para a data de hoje faria a suíte depender do dia
em que roda; passá-lo é injeção de dependência, e é o que torna a expiração determinística.
`janela_dias` é comparado por diferença em dias, e entrada com data futura não está expirada
— o componente não policia relógio. `dominancia_minima` é **piso inclusivo**: sete de dez
observações com mínimo de zero vírgula sete decide, e esse limite está fixado por teste
justamente porque a redação "acima do mínimo" admitiria a leitura oposta.
