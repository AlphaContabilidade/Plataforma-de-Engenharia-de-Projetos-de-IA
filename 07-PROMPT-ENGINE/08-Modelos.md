---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 08-Modelos
status: PRONTO
atualizado_em: 2026-07-29
---

# Modelos

Esta seção é a referência de contrato do motor. As assinaturas abaixo são as do código
executável em `exemplos/07-prompt-engine/`, e não uma paráfrase: quem lê aqui e escreve
código contra o que leu compila. Divergência entre esta seção e o código é defeito do
volume, não liberdade de redação, e o gate de exemplo garante que o código citado existe
e tem teste.

## Contrato do prompt

```python
class ContratoViolado(ValueError): ...

@dataclass(frozen=True, slots=True)
class Variavel:
    nome: str
    tipo: type
    obrigatoria: bool = True
    descricao: str = ""

@dataclass(frozen=True)
class PromptTemplate:
    nome: str
    corpo: str
    variaveis: tuple[Variavel, ...]

    def __post_init__(self) -> None: ...
    def render(self, **valores: object) -> str: ...
    @property
    def assinatura(self) -> str: ...
    @property
    def hash(self) -> str: ...
```

`Variavel` é congelada e usa `slots`, o que a torna comparável por valor e barata de
guardar em tupla. O campo `tipo` recebe uma classe, não um texto de anotação, porque
`render` valida com `isinstance` — validação que roda em vez de documentação que
envelhece. `render` aceita apenas variáveis declaradas e levanta `ContratoViolado` em três
situações: chave extra, obrigatória ausente e tipo incompatível; opcional ausente é
substituída por texto vazio. `assinatura` devolve a forma `nome(v1:int, v2?:str)` com as
variáveis em ordem alfabética, e a ordem é alfabética justamente para que reordenar a tupla
não mude a identidade; a interrogação antes dos dois-pontos marca a variável opcional, de
modo que a assinatura carrega os três campos que mudam o comportamento de `render` — nome,
tipo e obrigatoriedade. `hash` devolve os doze primeiros hexdígitos do `sha256` sobre o
corpo, um byte nulo e a assinatura.

O limite desse alcance é declarado em vez de deixado por descobrir: `descricao` não entra na
assinatura e portanto não entra no hash. Editar apenas a descrição de uma variável faz
`registrar` devolver a versão existente, e isso é intencional, porque descrição nenhuma
altera o texto que o modelo recebe. Qualquer outra edição do contrato — corpo, nome de
variável, tipo ou obrigatoriedade — produz hash diferente e, por consequência, versão nova.
A distinção entre os dois casos está coberta por dois testes de `tests/test_prompt_template.py`
e por um de `tests/test_prompt_registry.py`, citados em [`13-Testes.md`](13-Testes.md).

## Registro e ciclo de vida

```python
class Estado(StrEnum):
    RASCUNHO = "RASCUNHO"
    VERSIONADO = "VERSIONADO"
    EM_AVALIACAO = "EM_AVALIACAO"
    PROMOVIDO = "PROMOVIDO"
    DEPRECIADO = "DEPRECIADO"

TRANSICOES: dict[Estado, frozenset[Estado]]

class TransicaoInvalida(ValueError): ...
class NaoRegistrado(KeyError): ...

class PromptRegistry:
    def __init__(self) -> None: ...
    def registrar(self, template: PromptTemplate) -> str: ...
    def obter(self, nome: str, versao: str | None = None) -> PromptTemplate: ...
    def transicionar(self, nome: str, versao: str, destino: Estado) -> None: ...
    def estado(self, nome: str, versao: str) -> Estado: ...
    def historico(self, nome: str) -> tuple[tuple[str, str, Estado], ...]: ...
    def promovida(self, nome: str) -> str | None: ...
```

`registrar` devolve o rótulo da versão como texto — `"v1"`, `"v2"` e assim por diante — e
devolve o rótulo já existente quando o hash coincide. `obter` sem versão devolve a
promovida e, na ausência de promovida, a última registrada; nome desconhecido levanta
`NaoRegistrado` com a lista de nomes conhecidos na mensagem. `transicionar` valida o
destino contra `TRANSICOES` e levanta `TransicaoInvalida` nomeando a origem e os destinos
válidos, o que faz da mensagem de erro a própria documentação da máquina de estados.
`historico` devolve tuplas de versão, hash e estado em ordem de registro. As duas exceções
herdam de tipos padrão de propósito: código que já trata `ValueError` e `KeyError` continua
correto sem conhecer o motor.

## Avaliação

```python
@dataclass(frozen=True, slots=True)
class CasoDeOuro:
    nome: str
    entradas: dict[str, object]
    esperado: str
    descricao: str = ""

@dataclass(frozen=True, slots=True)
class Falha:
    caso: str
    saida: str
    motivo: str

@dataclass(frozen=True, slots=True)
class Resultado:
    total: int
    falhas: tuple[Falha, ...]
    @property
    def acertos(self) -> int: ...
    @property
    def taxa_acerto(self) -> float: ...

@dataclass(frozen=True, slots=True)
class Comparacao:
    taxa_a: float
    taxa_b: float
    @property
    def deriva(self) -> float: ...
    @property
    def vencedor(self) -> str: ...

class PromptEvaluator:
    def __init__(self, executor: Callable[[str], str]) -> None: ...
    def avaliar(self, template: PromptTemplate, casos: Iterable[CasoDeOuro]) -> Resultado: ...
    def comparar(self, a: PromptTemplate, b: PromptTemplate,
                 casos: Iterable[CasoDeOuro]) -> Comparacao: ...
```

O campo `esperado` de `CasoDeOuro` é uma expressão regular, e não uma igualdade literal,
porque saída de modelo varia em detalhe irrelevante e exigir texto exato produziria teste
que quebra sem que nada tenha piorado. `Falha` guarda a saída porque diagnóstico sem a
saída observada é adivinhação. `Resultado.taxa_acerto` é a fração de acertos e devolve
`0.0` quando `total` é zero. `Comparacao.deriva` é `taxa_b - taxa_a`, de modo que sinal
positivo significa que a candidata melhorou sobre a versão de referência, e `vencedor`
devolve `"a"`, `"b"` ou `"empate"`. `PromptEvaluator` recebe o executor como
`Callable[[str], str]`: essa é a única superfície pela qual o motor toca um provedor, e é o
que permite que a bateria inteira rode offline no gate de teste.
