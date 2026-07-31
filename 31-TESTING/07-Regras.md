---
volume: "31"
volume_nome: TESTING
tipo: PROCESSO
secao: 07-Regras
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Regras

**T1 — Todo teste tem um defeito nomeável.** Escrito, em uma frase. *Consequência:* teste sem essa
frase não pode ser aposentado com segurança, e por isso a suíte só cresce até ficar lenta demais para
ser rodada.

**T2 — Teste crítico passa por mutação uma vez.** Quebra-se de propósito o que ele deveria pegar,
confere-se o vermelho, desfaz-se. *Consequência:* sem isso, ele é hipótese.

**T3 — A suíte não toca rede, disco nem relógio.** *Consequência:* comportamento que depende do dia
em que roda não se reproduz, e a falha aparece meses depois sem ninguém ter mexido em nada.

**T4 — A asserção negativa é obrigatória quando existe filtro ou seleção.** *Consequência:* sem ela,
uma implementação que devolvesse tudo passaria.

**T5 — Asserção que só vale para o tamanho atual do conjunto é frouxa.** "Fica vazio", "tem
exatamente um", "é o primeiro". *Consequência:* passa por acidente e cai quando o sistema cresce — e
o momento em que cai é justamente quando se está mexendo em outra coisa.

**T6 — Nunca ajustar o teste para o código passar.** Precisar é permitido e vai com razão escrita;
afrouxar não é. *Consequência:* é a regra R2 do volume `01`, e a diferença entre as duas ações é o
que o revisor confere.

**T7 — Um comportamento por teste.** *Consequência:* teste que exercita três coisas falha sem dizer
qual das três, e o tempo de diagnóstico é o que decide se a suíte é usada ou ignorada.

**T8 — Comando citado em documentação leva escopo.** *Consequência:* um comando que roda a pasta
inteira de exemplos produz um número que cresce a cada volume novo do acervo; o mesmo comando
restrito a uma pasta produz um número que só muda quando aquele volume muda. Documentação que cita o
primeiro envelhece sozinha.

**T9 — Cobertura de mecanismo não é cobertura de dado.** *Consequência:* uma tabela, uma lista de
termos ou um catálogo precisa de teste próprio com casos reais do domínio — e a ausência deles não
aparece em nenhuma métrica de linhas alcançadas.
