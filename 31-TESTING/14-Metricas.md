---
volume: "31"
volume_nome: TESTING
tipo: PROCESSO
secao: 14-Metricas
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Métricas

**Tempo dos corpos de teste, separado do tempo total.** *Obtenção:* medir as durações de chamada com
as opções de duração do executor, e somá-las. Num dos volumes deste acervo os corpos somam **0,02 s**
e o terminal imprime cerca de dezessete segundos — quase tudo é partida do interpretador e coleta.
Medir só o total leva a otimizar o que não custa; medir só os corpos leva a se acomodar com uma suíte
que demora a dar resposta.

**Testes que já ficaram vermelhos alguma vez.** *Obtenção:* histórico de execução, ou registro manual
da mutação. É a métrica mais próxima de "quantos dos meus testes verificam alguma coisa", e a mais
incômoda de olhar.

**Intermitências por semana.** *Obtenção:* contagem de execuções em que o mesmo teste falhou e
passou sem mudança de código. Deveria ser zero. Qualquer valor acima disso corrói a autoridade de
toda a suíte, porque um vermelho que pode ser ruído faz todos os vermelhos serem discutidos antes de
investigados.

**Defeitos encontrados rodando, e não testando.** *Obtenção:* contagem no registro de mudanças. É a
métrica mais honesta sobre a qualidade da suíte, e a mais desconfortável. O caso do `pix` é um.

## Sobre cobertura de linhas

Cobertura mede **linhas alcançadas**, e alcançar não é verificar. Uma linha executada por um teste
sem asserção conta igual a uma linha protegida por três. O defeito do `pix` aconteceu com o motor em
cobertura completa de linhas: o caminho de detecção era percorrido por dezesseis testes, e faltava
uma entrada na tabela de dados.

O uso legítimo da métrica é o inverso do usual: não como meta a atingir, mas como **detector de
região não visitada**. Um trecho com zero por cento é informação útil — ninguém passou ali. Um
trecho com noventa por cento não é informação nenhuma sobre se o que passa ali está correto.
