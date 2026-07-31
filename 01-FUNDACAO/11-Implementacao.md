---
volume: "01"
volume_nome: FUNDACAO
tipo: GOVERNANCA
secao: 11-Implementacao
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Implementação

A matriz de controles não é um documento sobre o acervo: sete das oito linhas são código que roda
neste repositório. Esta seção diz onde cada uma vive.

## A fonte única

`00-INTRODUCAO/contrato.json` é o único lugar onde as seções, os cinco tipos de volume, os status
válidos, os limiares de tamanho, os marcadores proibidos e os quarenta e dois volumes existem de
forma legível por máquina. `Convencoes.md` é a mesma informação para gente, e um teste reprova a
suíte se as duas divergirem — duas fontes de verdade sem verificação de igualdade é como o acervo
adquiriria duas regras contraditórias, ambas documentadas.

## Os controles executáveis

`ferramentas/regras.py` implementa C1, C2 e C3: contagem de palavras que **ignora blocos de código**,
marcadores proibidos com fronteira de palavra, validade e obrigatoriedade de diagramas mermaid,
resolução dos exemplos citados em disco e dos links relativos.

A contagem ignorar código não é detalhe de conveniência. Sem isso, uma seção composta só de listagem
passa o mínimo de duzentas palavras sem uma linha de prosa, e o controle vira A4 — existe, roda,
sempre passa.

A fronteira de palavra nos marcadores tem origem num defeito concreto: um marcador proibido casava
por substring dentro da palavra **INDEPENDENTE**, e "auditoria independente" é vocabulário central da
plataforma. O próprio arquivo de instruções reprovava no gate. A correção usa asserções de largura
zero em volta do termo, com três testes de regressão.

`ferramentas/validar.py` compõe as regras e implementa C4, a detecção de ciclo em `depende_de`. O
prefixo `00` é reservado: aceitá-lo como volume fazia a varredura devolver `00-INTRODUCAO` e derrubar
os modos `--tudo` e `--cross-refs` inteiros.

C5 é `pytest` sobre `exemplos/`, sem ferramenta própria — controle que reimplementa um executor de
testes é superfície nova sem benefício.

`ferramentas/status.py` alimenta C6 e C7. A escolha do relatório de auditoria mais recente parseia
`(data, revisão)` do nome do arquivo e **nunca ordena alfabeticamente**: um sufixo de revisão com
hífen perde para a extensão sem sufixo, porque o hífen precede o ponto na tabela de caracteres, e a
revisão dez perderia para a dois por comparação de texto. Sem esse conserto, uma reauditoria no mesmo
dia reportaria a nota antiga em silêncio — A1 produzido pela própria ferramenta de controle.

## O controle que não roda

C8 não tem implementação, e a ausência é declarada em [`04-Arquitetura.md`](04-Arquitetura.md) e em
[`16-Roadmap.md`](16-Roadmap.md). Nenhum gate lê número escrito por extenso em prosa.
