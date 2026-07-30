---
volume: "03"
volume_nome: DISCOVERY
tipo: PROCESSO
secao: 13-Testes
status: PRONTO
atualizado_em: 2026-07-30
---

# Testes

Sessenta e nove testes, distribuídos assim: dezenove em `test_catalogo.py`, dezesseis em
`test_deteccao.py`, vinte e dois em `test_entrevista.py` e doze em `test_especificacao.py`. A
distribuição não é acidental — o controle tem mais testes que os outros porque é onde vive a
política, e política é o que muda por conveniência.

```
python -m pytest exemplos/03-discovery -q
```

Nenhum teste toca rede, disco ou relógio. A ausência de relógio é herdada do volume 12 pelo mesmo
argumento: comportamento que depende do dia em que se roda não se reproduz. Aqui não há nem data — o
motor não tem noção de tempo, e é por isso que a suíte roda em menos de dois décimos de segundo.

## Não existe `__init__.py` em `tests/`

O caminho de import é resolvido por `exemplos/03-discovery/conftest.py`, que insere a pasta do
exemplo em `sys.path`. A escolha é deliberada e a razão está registrada como dívida técnica em
[`../ROADMAP.md`](../ROADMAP.md): duas pastas `exemplos/<vol>/tests/` com `__init__.py` reivindicam o
mesmo nome de pacote `tests`, e rodar a suíte dos exemplos inteira falha com erro de módulo na
segunda pasta coletada — a primeira ganha o nome e a segunda procura seus módulos dentro dela. Sem
`__init__.py`, cada arquivo é importado pelo nome-base, único no acervo, e a colisão desaparece.

## O que cada arquivo cobre

`test_catalogo.py` prova duas coisas separadas. A primeira é que o catálogo publicado passa na
própria validação — identificadores únicos, pesos entre um e dez, pergunta e motivo não vazios,
lacuna condicional com gatilho. Um catálogo que impõe regras e as viola seria a versão mais
embaraçosa possível de status que mente. A segunda é o comportamento do filtro, e o teste central
aqui é o que verifica que aparelho de mão traz rede ausente e loja de aplicativos e **não** traz
nenhuma de programa instalado nem de navegador — a asserção negativa é a que importa, porque a
positiva passaria também num filtro que devolvesse tudo.

`test_deteccao.py` cobre o contrato de evidência. Frase vazia e frase sem sinal não geram palpite;
todo palpite produzido tem evidência não vazia e contida no texto original; o acento sobrevive; a
janela não atravessa o ponto final; e palpites da mesma frase têm evidências **distintas** — este
último é o teste de regressão do defeito descrito em [`12-Exemplos.md`](12-Exemplos.md). Há também
um teste de fronteira de palavra que cobre os dois casos, `app` dentro de `aplicativo` e `site`
dentro de `deposite`,
porque falso positivo por substring é silencioso e produz o palpite certo com a evidência errada.

`test_entrevista.py` cobre a política. Ordem por peso, determinismo no empate — repetido cinco vezes
na mesma asserção, para que uma implementação com conjunto não ordenado falhe de forma consistente —,
destravamento por confirmação e por resposta, recusa que não deixa rastro, limiar parametrizável nos
dois sentidos, e as duas exceções. Dois testes merecem menção especial: o que verifica que responder
o mesmo identificador de novo **substitui** o valor e preserva a posição na ordem da conversa, e o que
verifica que o denominador do progresso cresce quando o contexto destrava.

`test_especificacao.py` cobre a completude e a saída. Os três casos exigidos estão lá — falsa com
inferência pendente, falsa com universal aberta, verdadeira no caminho feliz — e há um quarto que é o
mais fácil de errar: decisão aberta de peso baixo **não** impede a completude, mas consta. O markdown
é verificado nas duas seções críticas e num detalhe que parece cosmético e não é: no caso vazio ele
escreve `Nenhuma` em vez de omitir a seção, porque seção ausente é lida como "não havia nada disso".

## O que os testes não cobrem, e por quê

Não há teste de qualidade do texto das perguntas. Perguntar se `problema` está bem redigida é
julgamento, e julgamento é assunto da auditoria — o gate executável reprova pergunta vazia, não
pergunta ruim. Também não há teste de cobertura da tabela de termos contra um corpo de frases reais:
isso exigiria um conjunto de frases anotadas que não existe, e inventá-lo produziria uma métrica que
mede a própria escrita. A consequência prática está registrada em [`16-Roadmap.md`](16-Roadmap.md).
