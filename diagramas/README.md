# diagramas/

> Biblioteca transversal · atualizado em 2026-07-29
> **Estado: vazia.** Nenhum diagrama reaproveitável publicado até agora.

## O que esta pasta é

O acervo dos diagramas **reaproveitáveis entre volumes** — os que descrevem a plataforma como um
todo, e não um volume específico. Diagrama de um volume vive na seção `05-Diagramas` daquele
volume; aqui ficam os que dois ou mais volumes precisam citar.

É a contraparte concreta do volume `36-DIAGRAMS`, do tipo `BIBLIOTECA`.

## As duas regras de diagrama da plataforma

Valem para qualquer diagrama, aqui ou dentro de volume, e são verificadas pelo gate estrutural.

**1. Mermaid, sempre.** Diagrama é texto versionado, não imagem. Imagem não entra em *diff*, não
é pesquisável, e envelhece separada do texto que a explica — três meses depois ninguém sabe se o
PNG corresponde ao parágrafo. Ver [`referencias/links.md`](../referencias/links.md) para a
documentação do Mermaid.

**2. Todo bloco Mermaid é seguido de um parágrafo que o explica.** Não é estilo: é regra do
contrato, e `ferramentas/validar.py` reprova o volume quando falta.

A razão da segunda regra é a que costuma ser mal entendida. O parágrafo **não** existe para
descrever o desenho a quem não pode vê-lo — existe porque escrever em prosa o que o diagrama
mostra é o teste que revela quando o diagrama não mostra nada. Diagrama vago produz parágrafo
vago, e parágrafo vago é visível. Uma caixa chamada "Processamento" ligada a outra chamada
"Sistema" passa por diagrama até alguém tentar escrever a frase que diz o que acontece entre as
duas.

O parágrafo deve dizer o que o **grafo** afirma e a prosa em volta não afirmava: que não existe
caminho de A a D sem passar por C, que a aresta de falha volta duas etapas e não uma, que dois
nós que pareciam sequenciais são concorrentes. Se o parágrafo apenas repete a legenda das caixas,
ele não está cumprindo a regra — está cumprindo a contagem de palavras.

## Diagramas exigidos por tipo de volume

Do `contrato.json`, campo `diagramas_obrigatorios`:

| Tipo | Diagramas obrigatórios |
|---|---|
| `ENGINE` | `C4Context`, `sequenceDiagram`, `stateDiagram-v2` |
| `ARQUITETURA` | `C4Context`, `sequenceDiagram` |
| `PROCESSO` | `flowchart` |
| `GOVERNANCA` | `flowchart` |
| `BIBLIOTECA` | nenhum |

A lógica da tabela: motor tem **estado** (por isso máquina de estados) e **interação no tempo**
(por isso sequência); processo e governança têm **fluxo com decisão**; biblioteca é acervo
catalogado e não tem comportamento a diagramar — forçar um diagrama ali produziria exatamente o
desenho decorativo que a regra 2 existe para expor.

## Por que está vazia

Mesma razão de [`templates/README.md`](../templates/README.md): diagrama reaproveitável é
**extraído**, não projetado. Só se sabe que um diagrama serve a vários volumes depois que vários
volumes existem e alguém percebe que estão redesenhando a mesma coisa com nomes diferentes — e
essa divergência de nomes é, aliás, o sintoma mais útil, porque revela que os volumes discordam
sobre a arquitetura.

O único diagrama da plataforma que já existe hoje é o ciclo de seis fases, em
[`frameworks/proprietarios/AI-ENGINEERING-FRAMEWORK.md`](../frameworks/proprietarios/AI-ENGINEERING-FRAMEWORK.md).
Ele fica lá porque é parte do argumento daquele arquivo. Se um segundo volume precisar citá-lo,
ele migra para cá e os dois passam a apontar para uma fonte só — que é o critério de entrada
nesta pasta, e não "o diagrama ficou bom".

## Como um diagrama entra aqui

1. **Dois ou mais volumes precisam dele.** Um só volume: fica na seção `05-Diagramas` dele.
2. **Vem com o parágrafo.** Diagrama sem prosa explicativa não é publicável em nenhum lugar deste
   acervo.
3. **Tem uma única fonte.** Cópia de diagrama em dois arquivos é garantia de divergência: um dos
   dois será atualizado.
4. **Não descreve o que ainda não existe.** Diagrama de arquitetura futura é proposta, e proposta
   vai para `ROADMAP.md`. Aqui só entra o que descreve o sistema como ele é — do contrário o
   acervo passa a documentar a intenção como se fosse o estado.

## Índice

Vazio. Cada entrada futura registra: o arquivo, o tipo de diagrama Mermaid, e quais volumes o
citam.

## Relacionados

- `00-INTRODUCAO/Convencoes.md` — a regra de diagrama em forma normativa.
- `00-INTRODUCAO/contrato.json` — `diagramas_obrigatorios` por tipo, fonte da tabela acima.
- [`referencias/links.md`](../referencias/links.md) — Mermaid e modelo C4.
