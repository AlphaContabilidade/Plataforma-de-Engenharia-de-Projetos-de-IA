---
volume: "31"
volume_nome: TESTING
tipo: PROCESSO
secao: 17-Conclusao
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Conclusão

A tese cabe numa frase: **um teste que nunca ficou vermelho é uma hipótese.** Todo o resto do volume
— as nove regras, os oito anti-padrões, o ciclo de mutação — existe para tornar essa frase aplicável
por alguém com pressa, que é a única condição em que ela é testada.

O instrumento é o mais barato do acervo. Quebrar de propósito o que o teste deveria pegar, conferir o
vermelho, desfazer. Menos de um minuto por teste crítico, sem ferramenta, sem configuração. Foi o que
separou, neste repositório, um teste real de um enfeite convincente — e o enfeite teria contado
igual em qualquer métrica de cobertura.

A segunda ideia é a que mais contraria o instrumento em que se confia: **suíte verde não é
cobertura**. O caso está registrado e é preciso: dezesseis testes cobrindo um mecanismo de detecção,
todos verdes, e a frase comercial mais comum do país saindo sem resultado porque a tabela de dados
não conhecia uma palavra. Cobertura de linhas não distingue mecanismo de dado, e o defeito morava
inteiramente no segundo.

A terceira é operacional e decide se as duas primeiras servem para alguma coisa: **quando um teste
cai, precisar não é afrouxar.** Um teste que exigia lista vazia caiu ao acrescentar um termo ao
sistema. A asserção passava por acidente — só valia enquanto o conjunto tivesse um elemento. Torná-la
precisa a fez sobreviver ao sistema crescer; afrouxá-la a teria transformado em mais um teste que
aceita qualquer coisa, e ninguém teria notado a diferença no relatório verde da manhã seguinte.
