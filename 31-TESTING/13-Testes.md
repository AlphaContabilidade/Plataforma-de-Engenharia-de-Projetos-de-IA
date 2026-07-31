---
volume: "31"
volume_nome: TESTING
tipo: PROCESSO
secao: 13-Testes
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Testes

Um volume sobre testes precisa dizer como as próprias regras são verificadas, sob pena de ser o
anti-padrão que descreve. Este volume não publica exemplo de código próprio: as regras são exercidas
pela suíte da plataforma, e o comando com escopo é este.

```
python -m pytest ferramentas/tests -q
```

## Onde cada regra é exercida no acervo

**T3, determinismo**, é verificável por inspeção e por execução: nenhum exemplo dos volumes escritos
importa módulo de rede, e o relógio é parâmetro nos motores que precisariam dele. Uma suíte que
depende de relógio falha um dia por ano e ninguém liga o defeito à causa.

**T4, asserção negativa**, aparece nos testes de filtro: verificar que aparelho de mão traz certas
lacunas e **não** traz nenhuma de navegador. A negativa é a que reprova a implementação que devolve
tudo.

**T5, asserção precisa**, tem o caso do palpite recusado, com a razão escrita no próprio teste. Um
teste que explica por que a asserção anterior passava por acidente é documentação que não apodrece,
porque vive ao lado do código que a tornou necessária.

**T9, cobertura de dado**, tem os testes de termos brasileiros de pagamento, escritos depois do
defeito e nomeados como regressão.

## O que não é verificado por gate

A regra **T1** — todo teste tem um defeito nomeável — não tem gate. Nenhuma ferramenta lê a frase e
julga se ela diz alguma coisa. Fica no checklist de revisão, e é dívida declarada, não omissão: um
verificador de qualidade de frase em português seria menos confiável que o problema que resolve.

A regra **T2** — mutação — também não tem gate, e a razão é mais interessante. Mutação automática
existe como técnica, mas gerar mutantes de um acervo inteiro custa tempo de máquina desproporcional
ao benefício quando a suíte é pequena. O que este volume defende é a versão manual, aplicada aos
testes críticos, que custa um minuto e pega o caso E1.
