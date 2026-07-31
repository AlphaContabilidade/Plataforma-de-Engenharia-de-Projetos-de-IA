---
volume: "01"
volume_nome: FUNDACAO
tipo: GOVERNANCA
secao: 12-Exemplos
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Exemplos

Quatro casos reais deste acervo. Nenhum é hipotético, os quatro foram corrigidos, e três passariam
por revisão humana atenta — que é o argumento inteiro a favor de verificação executável.

## Caso 1 — o marcador proibido que reprovava o vocabulário da plataforma

A regra que impede marcador de trabalho inacabado em prosa publicada casava por substring. A palavra
**INDEPENDENTE** contém um dos marcadores da lista, e "auditoria independente" é o termo central do
controle C6. O resultado é que o arquivo de instruções da própria plataforma não passava no gate da
própria plataforma.

O defeito foi encontrado por um agente sendo recusado pelo diagrama que ele mesmo tinha escrito.
Correção: fronteira de palavra nos dois lados, mais três testes de regressão. **Nenhuma revisão de
código teria pegado isso** — a regra estava certa em intenção e a lista de marcadores estava certa;
o encontro entre as duas é que produzia o falso positivo.

## Caso 2 — a ordenação alfabética que esconderia a nota

A função que escolhe o relatório de auditoria mais recente ordenava por nome de arquivo. Os nomes
seguem uma gramática com data e sufixo opcional de revisão, e o sufixo com hífen ordena **antes** da
extensão sem sufixo, porque o hífen (0x2D) precede o ponto (0x2E). Uma reauditoria feita no mesmo dia
teria reportado a nota da primeira rodada, em silêncio, com aparência de funcionamento normal.

Descoberto ao preparar exatamente essa situação. Corrigido parseando data e revisão da gramática do
nome, com seis testes novos. É o caso mais desconfortável dos quatro: a ferramenta de controle
produzindo A1.

## Caso 3 — a contagem que apodreceu sozinha

Uma seção do volume 07 afirmava um número que o comando `pytest exemplos -q` imprimia. Era verdade no
dia em que foi escrita. Quando o volume 12 entrou no acervo, o mesmo comando passou a imprimir outro
número, e a afirmação virou falsa **sem que ninguém tocasse naquele arquivo**.

A correção não foi atualizar o número — o novo apodreceria igual. Foi passar a citar o comando com
escopo, restrito à pasta daquele volume, cujo resultado só muda quando aquele volume muda.

## Caso 4 — a suíte verde que não cobria o caso mais comum do país

A tabela de termos de um motor de detecção conhecia `checkout` e `carrinho`, e não conhecia `pix`,
`boleto` nem `loja`. A frase "loja online que vende tênis e aceita pix" saía sem contexto nenhum, e
**a suíte inteira continuava verde**, porque nenhum teste usava uma frase brasileira de pagamento.

Encontrado rodando a interface, não testando. É a demonstração mais direta de que suíte verde não é
cobertura: os testes provavam que o mecanismo funcionava, e o que faltava era o dado.
