# sdk/

> Biblioteca transversal · atualizado em 2026-07-29
> **Estado: vazia, e vazia por decisão** — não por falta de tempo.

## O que esta pasta seria

O lugar de um SDK que exponha as capacidades da plataforma como biblioteca instalável: contrato,
validação, estado do acervo e exportação, consumíveis de fora desta pasta. É a contraparte
concreta do volume `41-SDK`, do tipo `ENGINE`.

## Por que está vazia

Porque **ainda não existe consumidor externo**, e SDK sem consumidor externo é a forma mais cara
de errar uma interface.

O argumento é específico, não uma preferência por minimalismo. Um SDK é, antes de tudo, uma
**promessa de estabilidade**: publicar `validar(volume)` como função pública significa que a
assinatura, o tipo de retorno e o significado do retorno passam a ser compromisso. Quem chama de
fora não vê a implementação e não pode ser corrigido por quem a muda. A partir daí, cada
refatoração interna precisa negociar com a interface publicada.

Enquanto o único consumidor das ferramentas é a própria plataforma — as cinco skills e a suíte de
testes —, esse compromisso é puro custo. As funções em `ferramentas/` podem mudar de assinatura
numa tarde, porque todos os chamadores estão no mesmo repositório e os testes apontam o que
quebrou. Publicar um SDK agora congelaria interfaces que ainda vão mudar, e o resultado previsível
é um SDK que fica desatualizado em relação ao código que ele deveria expor: mesmo problema do
template projetado no vácuo, com consequência maior, porque agora há gente de fora dependendo.

Há ainda a razão do momento. As ferramentas nasceram nas primeiras tasks do plano de
implementação e foram exercitadas por **um** volume-piloto. Uma interface desenhada a partir de um
caso de uso é uma interface desenhada a partir daquele caso — e é justamente ao aplicar a máquina
ao segundo e ao terceiro volume, de **tipos diferentes** (`PROCESSO`, `BIBLIOTECA`,
`GOVERNANCA`), que se descobre o que na interface era geral e o que era acidente do `ENGINE`.

## O que existe hoje, e como usar

As capacidades **existem** — só não estão empacotadas como SDK. Elas são consumidas como módulos
Python de dentro de `AI-ENGINEERING-OS/`:

| Módulo | Responsabilidade |
|---|---|
| `ferramentas/contrato.py` | carrega `00-INTRODUCAO/contrato.json`; resolve seções e diagramas por tipo |
| `ferramentas/frontmatter.py` | parser do subconjunto YAML do front-matter e dos `_VOLUME.yml` |
| `ferramentas/regras.py` | as regras de qualidade, uma função pura por regra |
| `ferramentas/validar.py` | orquestra as regras; é o gate estrutural e a CLI dele |
| `ferramentas/status.py` | leitura do estado do acervo |
| `ferramentas/exportar.py` | geração do `mkdocs.yml` |
| `ferramentas/scaffold.py` | criação idempotente de pastas de volume e `_VOLUME.yml` |
| `ferramentas/modelo.py` | `Violacao` — o tipo que atravessa todas as ferramentas |

Duas restrições valem para todo esse código e valeriam para o SDK: **apenas biblioteca padrão**
(sem PyYAML — a gramática restrita do front-matter é o que permite validá-la sem dependência e com
erro preciso) e **execução a partir da raiz da plataforma**, porque os imports `ferramentas.*`
dependem disso.

O contrato de fato estável hoje não é uma assinatura de função: é o **código de saída** da CLI.
`validar.py` devolve `exit ≠ 0` com uma lista `arquivo:linha` por violação. Qualquer integração
externa que precise do gate agora deve depender disso, e não de API Python — código de saída é a
interface mais barata de manter e a mais difícil de quebrar por acidente.

## Condições para o SDK existir

1. **Um consumidor externo real, nomeado.** Não "outros projetos poderão usar" — um projeto
   concreto, com necessidade concreta.
2. **A máquina exercitada em ao menos três tipos de volume diferentes.** Antes disso, a
   generalidade da interface é suposição.
3. **Decisão explícita sobre versionamento**, com política de mudança incompatível registrada.
4. **O próprio SDK sob os gates da plataforma:** volume `41-SDK` com as 18 seções, exemplos
   executáveis com teste, e a Definição de PRONTO satisfeita. SDK que não passa no gate que ele
   próprio expõe seria a contradição mais visível possível.

Até que as quatro condições estejam satisfeitas, esta pasta permanece vazia — e este arquivo é o
registro da decisão, não um aviso de obra em andamento.

## Relacionados

- [`frameworks/proprietarios/AI-ENGINEERING-FRAMEWORK.md`](../frameworks/proprietarios/AI-ENGINEERING-FRAMEWORK.md)
  — as seis fases que as ferramentas implementam.
- [`frameworks/conhecidos/semantic-kernel.md`](../frameworks/conhecidos/semantic-kernel.md) —
  compromisso de estabilidade de API como argumento de produto, e o que ele custa.
- [`templates/README.md`](../templates/README.md) — mesma política de extrair em vez de projetar.
