# Template de exemplo executável

> Biblioteca transversal · atualizado em 2026-07-29
> Use ao criar qualquer exemplo em `exemplos/<volume>/`. O que este arquivo descreve **não é
> estilo**: é o que o gate de teste da plataforma exige.

## A regra que governa esta pasta

**Volume não cita código que não roda.**

Todo trecho de código citado por um volume existe como arquivo executável em
`exemplos/<vol>/`, e todo arquivo executável tem teste em `exemplos/<vol>/tests/`. O gate
estrutural (`ferramentas/validar.py`) reprova referência a exemplo cujo arquivo não existe, e
reprova exemplo que existe sem teste correspondente. O gate seguinte é uma execução de `pytest`
sobre a pasta.

A razão é que o leitor confia no código mais do que na prosa — e com motivo, porque código é
específico e verificável. Só que essa confiança é justificada **apenas** se o código foi
executado. Trecho ilustrativo que nunca rodou é a maior fonte de erro silencioso em acervo
técnico: ele está lá exatamente para ser copiado, e é copiado.

## Estrutura de arquivos

```
exemplos/
  <NN-nome-do-volume>/           ex.: 07-prompt-engine/
    <conceito>.py                ex.: prompt_template.py
    tests/
      __init__.py
      test_<conceito>.py         ex.: test_prompt_template.py
```

Um conceito por arquivo. Nome de arquivo em `snake_case`, correspondendo ao conceito que o volume
nomeia — se o volume fala de `PromptTemplate`, o arquivo é `prompt_template.py`. O teste tem o
nome do módulo prefixado por `test_`.

## O arquivo de código

Cinco exigências, todas com razão prática:

**1. Executável de verdade, sem dependência externa.** Só biblioteca padrão, salvo quando o
próprio assunto do volume é uma biblioteca de terceiro. Exemplo que exige instalação é exemplo que
o leitor não roda — e exemplo não rodado volta a ser ilustração.

**2. Docstring de módulo que diga a decisão, não a função.** O que o código faz está no código. O
que **não** está no código é por que ele foi escrito assim, e essa é a informação que se perde.
Escreva a alternativa rejeitada:

```python
"""Template de prompt com variaveis tipadas.

Decisao deliberada: o construtor levanta quando os placeholders do corpo divergem
das variaveis declaradas, em qualquer direcao. A alternativa - avisar so no render -
foi rejeitada porque adia a deteccao para a execucao, e um template so e valido se
o contrato fecha no momento em que ele e definido.
"""
```

**3. Tipos nas assinaturas públicas.** Anotação é documentação que o interpretador ajuda a manter
honesta.

**4. Erro explícito no lugar de retorno silencioso.** Exemplo que devolve `None` em caso ruim
ensina a engolir falha. Levante exceção nomeada — `ContratoViolado`, não `ValueError` genérica — e
ponha na mensagem **a diferença encontrada**, não só a constatação de que houve diferença.

**5. Nenhum dado real de cliente, nenhum segredo, em nenhuma circunstância.** Nem CNPJ, nem nome
de empresa, nem chave, nem trecho de extrato bancário. Quando o exemplo precisa de dado com forma
realista, use dado claramente fictício e diga que é fictício.

## O arquivo de teste

O teste não está aí para inflar cobertura. Ele está aí para **provar que o exemplo faz o que o
volume afirma**. Se o volume diz "o hash muda quando o tipo de uma variável muda", existe um teste
com exatamente esse nome.

Exija os quatro grupos:

- **caminho felizmente bem sucedido** — o uso que o volume mostra;
- **cada erro declarado** — um teste por exceção que o código pode levantar, verificando também a
  mensagem quando ela carrega informação;
- **os casos de borda que o volume menciona** — vazio, ausente, duplicado, limite;
- **a propriedade que o volume promete** — estabilidade de hash, idempotência, ordem, o que for.

Nomes de teste em português, descrevendo o comportamento e não a função chamada:

```python
def test_hash_muda_quando_o_tipo_de_uma_variavel_muda():
    ...
```

O nome do teste é a documentação que nunca dessincroniza: quando ele fica falso, ele quebra.

Sem rede, sem sistema de arquivos fora de `tmp_path`, sem relógio real, sem ordem de execução
entre testes. Teste que depende de qualquer uma dessas quatro coisas falha um dia por razão que
não é a razão que ele investigava — e um teste que falha por motivo alheio é um teste que a equipe
aprende a ignorar.

## A referência no volume

Do lado do volume, cada citação de código aponta para o arquivo:

```markdown
<!-- exemplo: exemplos/07-prompt-engine/prompt_template.py -->
```

O gate resolve esse caminho. Caminho que não existe é violação com arquivo e linha.

Cite **recorte**, não o arquivo inteiro. O volume explica a decisão; o arquivo tem a
implementação completa. Colar 200 linhas no volume garante duas coisas: que ninguém lê, e que a
cópia divergirá do original.

## Checklist antes de considerar o exemplo pronto

- [ ] `python -m pytest exemplos/<vol> -q` passa, rodado da raiz da plataforma.
- [ ] Existe teste para cada exceção que o módulo levanta.
- [ ] Existe teste para cada propriedade que o volume promete.
- [ ] A docstring de módulo registra ao menos uma alternativa rejeitada.
- [ ] Nenhum dado de cliente, nome de empresa real ou segredo.
- [ ] O volume aponta para o arquivo com `<!-- exemplo: ... -->`, e o caminho resolve.
- [ ] O recorte citado no volume corresponde ao que está no arquivo.
- [ ] O exemplo roda sem instalar nada além da biblioteca padrão.

## Anti-padrões

| Anti-padrão | Por que é ruim |
|---|---|
| Trecho no volume que não existe como arquivo | O gate reprova — e, sem gate, seria código nunca executado sendo copiado por quem confia nele. |
| Exemplo sem teste | O gate reprova. Exemplo não testado é afirmação, não demonstração. |
| Teste que só verifica o caminho bem sucedido | Não prova nada sobre o comportamento em falha, que é onde o leitor vai se machucar. |
| Exemplo com dado real "porque fica mais concreto" | Vazamento. E concretude não exige realidade: exige forma realista. |
| Exemplo que precisa de chave de API | Ninguém executa; volta a ser ilustração. |
| `print` no lugar de `assert` | Demonstra sem verificar. Saída em tela não reprova nada. |
| Arquivo com três conceitos | Impossível citar um sem arrastar os outros dois. |

## Relacionados

- [`agentes/_template-agente.md`](../agentes/_template-agente.md) — mesma política de rubrica
  vazia declarada em vez de preenchida.
- [`frameworks/proprietarios/AI-ENGINEERING-FRAMEWORK.md`](../frameworks/proprietarios/AI-ENGINEERING-FRAMEWORK.md)
  — a fase 4 do ciclo é a execução destes testes.
- [`referencias/links.md`](../referencias/links.md) — documentação do pytest.
