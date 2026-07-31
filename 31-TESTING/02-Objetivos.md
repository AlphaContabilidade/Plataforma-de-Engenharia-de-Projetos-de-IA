---
volume: "31"
volume_nome: TESTING
tipo: PROCESSO
secao: 02-Objetivos
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Objetivos

**1. Que todo teste tenha um defeito nomeável que ele pega.** Quem escreve consegue dizer, em uma
frase, o que quebraria se aquele teste não existisse. *Verificação:* a pergunta é feita na revisão, e
"garante que a função funciona" não é resposta — é a forma educada de dizer que ninguém sabe.

**2. Que a suíte rode sem rede, sem disco e sem relógio.** *Verificação:* rodar com a rede desligada.
Este acervo obedece: os exemplos dos volumes `03`, `07` e `12` não tocam nenhum dos três, e a
ausência de relógio é a mais esquecida — comportamento que depende do dia em que roda não se
reproduz, e o defeito aparece meses depois, sem ninguém ter mexido em nada.

**3. Que a asserção seja sobre o comportamento, não sobre o estado conveniente.** *Verificação:* a
asserção sobrevive ao crescimento do sistema. "A lista fica vazia" passa por acidente enquanto o
conjunto tiver um elemento só; "o item recusado não está mais na lista" continua verdadeiro depois.

**4. Que a suíte seja rápida o bastante para rodar sempre.** *Verificação:* o tempo dos corpos de
teste, medido separado do tempo de partida do interpretador. As duas grandezas são diferentes e
confundi-las produz tanto otimização desnecessária quanto acomodação com suíte lenta.

**5. Que o teste não seja ajustado para o código passar.** É a regra R2 do volume `01`, e aqui ela
tem a forma operacional: quando um teste cai depois de uma mudança, ou a mudança está errada, ou o
teste estava frouxo. *Verificação:* toda asserção enfraquecida carrega a razão escrita, no código.

O que **não** é objetivo: perseguir percentual de cobertura. A razão está em
[`14-Metricas.md`](14-Metricas.md), e ela é específica — cobertura mede linhas alcançadas, e o
defeito do `pix` estava em cem por cento de linhas alcançadas.
