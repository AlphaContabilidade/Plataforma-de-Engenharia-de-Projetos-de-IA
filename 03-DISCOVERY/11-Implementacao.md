---
volume: "03"
volume_nome: DISCOVERY
tipo: PROCESSO
secao: 11-Implementacao
status: PRONTO
atualizado_em: 2026-07-31
---

# Implementação

O motor são quatro arquivos de biblioteca padrão, sem dependência externa, com setenta e três
testes ao lado. A ordem de leitura é a ordem de dependência: catálogo, detecção, entrevista,
especificação. Ler na ordem inversa funciona e custa mais, porque cada módulo é escrito assumindo
que o anterior já é conhecido.

<!-- exemplo: exemplos/03-discovery/catalogo.py -->
<!-- exemplo: exemplos/03-discovery/deteccao.py -->
<!-- exemplo: exemplos/03-discovery/entrevista.py -->
<!-- exemplo: exemplos/03-discovery/especificacao.py -->

## `catalogo.py` — o dado

Duas enumerações (`Plataforma`, `Contexto`), um registro congelado (`Lacuna`), uma tupla de trinta e
sete lacunas (`CATALOGO`), uma função de filtro (`lacunas_ativas`) e um validador
(`validar_catalogo`). Nada mais.

A decisão de implementação que mais paga é `Lacuna.relevante_para`, que resolve a relevância com duas
portas em conjunção: a de plataforma e a de contexto. Conjunto vazio é porta **aberta** — ausência de
exigência, e não exigência impossível de satisfazer. É o que permite escrever uma lacuna que só
existe para pagamento dentro de aparelho de mão declarando os dois conjuntos, e o teste
`test_lacuna_de_contexto_nao_depende_de_plataforma` fixa o comportamento no caso de porta aberta.

A validação levanta em quatro situações, e a quarta é a menos óbvia: lacuna não universal sem
gatilho nenhum. Ela seria relevante sempre, o que é ser universal com a marca errada, e o defeito
sumiria no meio de um catálogo grande. Levantar no carregamento troca um erro silencioso por uma
falha imediata.

## `deteccao.py` — a inferência com procedência

`Origem`, `Palpite`, duas tabelas de termos e duas funções públicas. O trabalho fino está em três
funções privadas, e vale conhecê-las porque cada uma existe por um defeito concreto.

`_dobrar` normaliza o texto para minúsculas sem acento **preservando a posição original de cada
caractere**. A lista de posições existe porque a evidência tem de sair do texto original: devolver a
versão dobrada entregaria à pessoa a própria frase sem acento, o que parece defeito e destrói a
confiança no que o motor mostra.

`_fronteira` exige fronteira de palavra nos dois lados do casamento. Sem ela, `app` casaria dentro de
`aplicativo` e `site` casaria dentro de `deposite` — os dois casos estão no mesmo teste, porque é
o tipo de falso positivo que passaria despercebido.

`_trecho_em` recorta a palavra casada mais até três palavras de cada lado, sem atravessar a fronteira
da frase. Esta é a função que mudou depois da medição: a primeira versão devolvia a frase inteira, e
numa ideia escrita em uma frase só os três palpites saíam com evidência idêntica. O parágrafo de
[`12-Exemplos.md`](12-Exemplos.md) registra a correção com o antes e o depois.

## `entrevista.py` — o controle

Um objeto mutável, e é o único do motor. O construtor roda a detecção uma vez — a frase inicial não
muda depois, e rodar sob demanda faria de `palpites_pendentes` uma consulta com efeito colateral.

Três decisões de implementação sustentam as regras de [`07-Regras.md`](07-Regras.md). A primeira é
`_ordenar`, que ordena por peso decrescente e desempata pela posição no catálogo, calculada a partir
do catálogo injetado e não de uma constante — assim um catálogo de teste tem desempate próprio e
coerente. A segunda é o destravamento por resposta, que testa se o valor corresponde a um membro das
enumerações e não conhece identificador nenhum. A terceira é a separação entre `pendentes` — ativas,
sem resposta, com peso suficiente — e `decisoes_abertas`, que é a mesma lista **sem** o filtro de
peso: não perguntar é economia de turno, não licença para omitir.

`peso_minimo` e `catalogo` são injeção de dependência pelo mesmo argumento que faz `hoje` ser
parâmetro no volume 12: com o limiar por fora, o comportamento de parada é testável sem depender do
conteúdo real do catálogo, e o catálogo real é testável sem depender do limiar padrão.

## `especificacao.py` — a saída

Um registro congelado com seis campos, uma propriedade e dois métodos. `completa` é duas condições
independentes e nenhum parâmetro; `markdown` escreve as duas seções críticas **sempre**, mesmo
vazias, porque seção ausente é lida como "não havia nada disso" — que é o mesmo texto que sai quando
ninguém olhou.

`gerar` pode ser chamada em qualquer momento, inclusive no meio da conversa, e o resultado é válido:
uma especificação incompleta com três decisões abertas é um documento útil. Negar a geração antes do
fim faria a única saída do motor depender de a conversa ter terminado bem, e conversa interrompida é
justamente o caso em que se precisa saber onde parou.
