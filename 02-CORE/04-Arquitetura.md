---
volume: "02"
volume_nome: CORE
tipo: ARQUITETURA
secao: 04-Arquitetura
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Arquitetura

Seis partes. A ordem é a do fluxo de uma requisição, e a divisão não é arbitrária: cada fronteira
entre duas partes é um lugar onde se pode escrever um teste.

## As seis partes

**1. Fronteira de entrada.** Onde o que veio de fora — formulário, arquivo, mensagem — vira estrutura
com tipo. Nada probabilístico acontece aqui. Se for preciso interpretar linguagem natural para
preencher a estrutura, isso já é chamada ao modelo e pertence à parte 3.

**2. Montagem de contexto.** O que o modelo vai ver, montado por código comum: instrução, dados
recuperados, histórico, exemplos. É **determinística e testável**, e é a parte que mais se subestima
— a maioria das respostas ruins que se atribuem ao modelo vem de contexto montado errado, e isso se
descobre imprimindo o contexto, não trocando de modelo.

**3. Chamada.** A única parte probabilística. Uma função, com tempo limite, política de repetição e
tratamento de indisponibilidade. Tudo o que se sabe dela é que devolve texto, ou falha.

**4. Fronteira de saída.** Onde o texto vira dado com tipo, ou vira erro declarado. **É a parte mais
importante do volume.** Depois dela não existe mais "o que o modelo respondeu"; existe um valor
validado ou uma falha que o chamador precisa tratar.

**5. Efeito.** O que muda no mundo: gravar, cobrar, enviar, publicar. Código comum, com as mesmas
exigências de qualquer efeito colateral — idempotência, registro, reversibilidade quando possível.

**6. Verificação.** O que confere que o efeito corresponde à intenção. Fora do caminho da requisição,
e é a parte que sistemas apressados não têm.

## A regra estrutural

**O não-determinismo não passa da parte 4.** As partes 1, 2, 5 e 6 são código comum e testam-se como
código comum. A parte 3 é isolada atrás de uma interface que o teste substitui. A parte 4 é onde a
disciplina se aplica, e é onde ela costuma faltar.

A violação típica não parece violação: alguém devolve o texto cru da parte 3 para o chamador, "só por
enquanto", e o chamador faz um `if` sobre o conteúdo. A partir daí o não-determinismo está do lado de
fora, e recolhê-lo exige mexer em todos os chamadores — motivo pelo qual quase nunca é recolhido.

## Onde a fronteira de saída vive

A forma que funciona é um **contrato de saída** declarado junto do prompt, e não deduzido da resposta.
Declarar antes permite validar depois; deduzir depois é aceitar o que veio e chamar de contrato.
