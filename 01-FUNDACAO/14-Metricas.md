---
volume: "01"
volume_nome: FUNDACAO
tipo: GOVERNANCA
secao: 14-Metricas
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Métricas

Quatro métricas. Cada uma tem a forma de obtenção junto, porque métrica sem procedência é o
anti-padrão A2 aplicado à própria medição de qualidade.

**Cobertura da matriz.** Quantos controles são executáveis, sobre o total. Hoje: **sete de oito**.
*Obtenção:* contagem direta da tabela em [`04-Arquitetura.md`](04-Arquitetura.md). O valor útil desta
métrica não é o número alto; é a lista dos que faltam. Uma matriz com oito de oito onde o oitavo foi
apagado por conveniência mede pior que esta.

**Achados por auditoria, por gravidade.** Quantos defeitos a auditoria independente encontra em cada
volume. *Obtenção:* relatórios em `auditorias/`. O volume 03 teve quatro achados; o volume 07 teve um
achado de código na primeira rodada que os gates não pegariam. A leitura correta é contraintuitiva:
**zero achados é sinal de alarme**, não de excelência — significa auditoria superficial ou auditor
alinhado demais com o autor.

**Defeitos encontrados rodando, e não testando.** Quantos problemas apareceram no uso e não na suíte.
*Obtenção:* contagem no `CHANGELOG`. É a métrica mais honesta sobre a qualidade dos testes, e a que
se prefere não olhar. O Caso 4 de [`12-Exemplos.md`](12-Exemplos.md) é um deles.

**Idade da afirmação mais antiga não reconferida.** Quanto tempo faz que o número mais velho da prosa
foi medido. *Obtenção:* manual hoje, pelo campo `atualizado_em` do front-matter cruzado com a data da
última execução registrada. É a métrica que o controle C8 mediria se existisse, e enquanto não
existir ela é uma estimativa — o que a coloca, com alguma ironia, sob suspeita de A2.

## O que não se mede aqui

Não se mede quantidade de páginas, de prompts ou de exemplos. Contagem de artefato mede esforço, e
esforço não é a variável que este volume governa. Um acervo de oito mil páginas cujos números
ninguém conferiu é pior que um de quatrocentas cujos números são todos rastreáveis.
