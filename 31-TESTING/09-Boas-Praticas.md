---
volume: "31"
volume_nome: TESTING
tipo: PROCESSO
secao: 09-Boas-Praticas
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Boas Práticas

**Escreva primeiro o teste que falha pelo motivo certo.** Ver o vermelho antes do verde é a versão
barata da mutação: se o teste passa antes de o código existir, ele não testa o que se pensava.

**Comece pelo caso de erro.** O caminho feliz se escreve sozinho; o caminho de erro é o que decide se
o sistema estraga alguma coisa de madrugada. Este acervo aplica: a interface local recusa corpo acima
do teto **antes de alocar**, e o teste que verifica isso vale mais que o que verifica o corpo normal.

**Teste o dado, não só o mecanismo.** Se existe tabela, lista de termos ou catálogo, escreva casos
com entradas reais do domínio em que o sistema vai rodar. O defeito do `pix` estava com o mecanismo
perfeitamente testado.

**Nomeie o teste pelo comportamento, não pela função.** Um nome como
`test_recusar_remove_da_pendencia_sem_aplicar_nada` diz o que se espera; `test_recusar` diz onde se
mexeu. O primeiro sobrevive a refatoração.

**Injete o relógio como parâmetro.** Uma função que recebe a data em vez de consultá-la é testável
sem truque, e a mudança é de uma linha quando feita no começo.

**Repita a asserção de determinismo algumas vezes no mesmo teste.** Ordenação instável passa uma vez
em cada duas execuções; repetir cinco vezes na mesma asserção faz uma implementação com conjunto não
ordenado falhar de forma consistente, em vez de intermitente.

**Meça o tempo dos corpos separado do tempo de partida.** São grandezas diferentes. Num destes
volumes, os corpos somam dois centésimos de segundo e o terminal imprime dezessete — quase tudo é
partida do interpretador e coleta. Confundir as duas leva a otimizar o que não custa e a se acomodar
com o que custa.
