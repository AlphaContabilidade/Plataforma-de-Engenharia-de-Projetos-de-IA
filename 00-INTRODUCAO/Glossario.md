# Glossário

Os termos abaixo são usados **sempre no mesmo sentido** em todo o acervo. Estão aqui porque
cada um deles tem um significado técnico específico nesta plataforma que não coincide
necessariamente com o uso corrente.

## Termos da plataforma

**Volume.** Uma unidade de domínio do acervo, materializada como pasta `NN-NOME/` na raiz da
plataforma — por exemplo `07-PROMPT-ENGINE`. Toda pasta de volume contém um `_VOLUME.yml`
com os metadados e um arquivo Markdown por seção aplicável. Os 42 volumes estão declarados
em `contrato.json`; declarado e materializado são coisas diferentes, e `status.py` distingue
as duas. `NN` é sempre string de dois dígitos, com zero à esquerda quando necessário.

**Seção.** Um dos 18 arquivos padronizados dentro de um volume, com nome fixo
(`04-Arquitetura.md`, `13-Testes.md`). O nome do arquivo é contrato: o validador procura por
ele, `status.py` conta quantos existem, e o campo `secao` do front-matter tem de repetir o
nome exatamente. As seções aplicáveis a um volume dependem do seu tipo.

**Tipo.** A classificação de um volume que determina quais seções são obrigatórias e quais
diagramas são exigidos. Há cinco: `ENGINE`, `ARQUITETURA`, `PROCESSO`, `BIBLIOTECA` e
`GOVERNANCA`. O tipo existe para evitar seção-enchimento: exigir máquina de estados de um
volume de templates produziria texto vazio, e texto vazio contradiz a regra de qualidade.
A atribuição vive em `contrato.json` e é projetada para humanos em
[Convencoes.md](Convencoes.md).

**Contrato.** O arquivo `00-INTRODUCAO/contrato.json`: única fonte de verdade legível por
máquina sobre seções, tipos, status válidos, limiares de palavras, marcadores proibidos,
diagramas obrigatórios e os 42 volumes. Nenhuma ferramenta tem regra hardcoded que
contradiga o contrato. Quando este glossário diz "o contrato exige", é literalmente esse
arquivo JSON.

**Gate.** Uma porta de qualidade executável: um programa que reprova conteúdo e devolve
código de saída diferente de zero. São três, na ordem em que rodam — gate 1 estrutural
(`ferramentas.validar`), gate 2 executável (`pytest` nos exemplos) e gate 3 de referências
cruzadas (`ferramentas.validar --cross-refs`). "Gate verde" significa exit 0; "gate
vermelho" significa violação reportada. Gate não é revisão humana nem opinião de modelo: é
código determinístico.

**Regra.** Uma verificação individual de um gate, identificada por nome estável e
implementada como função pura em `ferramentas/regras.py`. Exemplos de nomes:
`substancia-curta`, `marcador-proibido`, `mermaid-sem-descricao`, `exemplo-sem-teste`,
`link-morto`. Toda violação sai com o nome da regra entre colchetes, para que a discussão
sobre um problema fique ancorada no que a máquina verifica.

**Violação.** O registro de uma quebra de contrato: arquivo, linha, nome da regra e
mensagem. Linha igual a zero significa "o arquivo como um todo" — usada quando o problema é
a ausência de algo, não um trecho específico. Violação nunca é exceção: as regras devolvem
lista de violações e reservam exceção para erro de programa.

**Status.** O estado gravável de um volume, no `_VOLUME.yml` e no front-matter das seções.
Só três valores existem: `RASCUNHO`, `REQUER_REVISAO` e `PRONTO`. `PENDENTE` aparece em
`/status` mas **não é gravável** — é estado derivado, calculado quando a pasta do volume
ainda não existe em disco.

**Definição de PRONTO.** O critério de aceite que substitui contagem de páginas. Quatro
condições simultâneas: gate 1 verde para o volume, gate 2 verde nos exemplos, auditoria com
média maior ou igual a 8,0 e nenhuma seção abaixo de 6, e registro no `CHANGELOG.md` com
data. Falta uma, o volume não é `PRONTO`.

**Perecível.** Marca `perecivel: true` no `_VOLUME.yml` de volume cujo assunto muda em
semanas — modelos, roteamento entre modelos e custo. Volume perecível é deliberadamente fino
e não fixa preço, limite ou nome de modelo como valor de referência: descreve o método de
decidir e aponta para a fonte viva. Número concreto só entra com data e fonte na mesma
frase, como ilustração de método.

**Padrão-ouro.** O volume de referência contra o qual os demais se comparam:
`07-PROMPT-ENGINE`. Ele existe para provar que o contrato é satisfazível com conteúdo
substantivo, e para servir de teste de estresse das próprias convenções. Quando uma dúvida
de forma não estiver resolvida por [Convencoes.md](Convencoes.md), a resposta é olhar o
padrão-ouro.

**Auditoria.** O relatório do subagente `auditor-fable` sobre um volume, gravado em
`auditorias/VOL-NN-auditoria-YYYY-MM-DD.md`, com nota de 0 a 10 por seção, problemas,
sugestões e veredicto, mais uma linha `media:` que `status.py` lê. O auditor é outro modelo,
em outra sessão: quem escreve não se aprova, porque revisar o próprio texto no mesmo
contexto tende a confirmar o que já está lá.

## Termos do domínio de prompt engineering

Nestes termos o identificador fica em inglês, porque é assim que aparecem no código e na
literatura da área. A prosa em volta permanece em português.

**Prompt template.** Um prompt parametrizado com variáveis **tipadas** e contrato validado:
os marcadores presentes no corpo têm de coincidir exatamente com as variáveis declaradas,
nas duas direções. Variável obrigatória ausente, tipo errado ou chave extra na renderização
é erro de contrato, não aviso. É o que separa um template de uma string com chaves.

**Registry.** O repositório versionado de templates, com versão derivada do **hash do
conteúdo mais da assinatura das variáveis**. Registrar conteúdo idêntico devolve a versão
existente em vez de criar outra; cada versão tem estado próprio no seu ciclo de vida
(rascunho, versionado, em avaliação, promovido, depreciado) e no máximo uma versão por nome
está promovida ao mesmo tempo. O hash cobrir a assinatura, e não só o texto, é o que impede
duas versões incompatíveis de colidirem como se fossem a mesma.

**Avaliador.** O componente que julga uma versão de prompt contra **casos de ouro** —
entradas com saída esperada conhecida — e compara versões entre si para detectar deriva.
Serve para responder "a versão nova é melhor?" com número em vez de impressão. Avaliador é o
que torna a promoção de uma versão uma decisão medida, e não uma preferência.
