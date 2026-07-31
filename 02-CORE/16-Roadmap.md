---
volume: "02"
volume_nome: CORE
tipo: ARQUITETURA
secao: 16-Roadmap
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Roadmap

**1. Exemplo executável próprio deste volume.** Hoje ele aponta para código dos volumes vizinhos, o
que é honesto mas indireto. Um exemplo mínimo — as seis partes num arquivo, com a parte 3 substituída
no teste e as três camadas de validação cobertas — tornaria a arquitetura conferível sem precisar ler
outro volume. É a frente de maior valor e deve vir antes de qualquer outra.

**2. Contrato de saída como estrutura verificável.** O volume `07` já tem assinatura tipada para a
entrada do prompt; falta a contraparte para a saída, com as três camadas separadas e a ação de cada
uma declarada. Fechar isso permitiria que a fronteira fosse gerada a partir do contrato, em vez de
escrita à mão em cada rota — e fronteira escrita à mão em cada rota é como se produz a segunda
fronteira divergente que a regra N1 proíbe.

**3. Medição da proporção testável sem rede.** Hoje é afirmação qualitativa. Torná-la número exige
marcar os testes que dependem do provedor e rodar a suíte nos dois modos. Enquanto não existir, o
que [`14-Metricas.md`](14-Metricas.md) descreve é um procedimento de diagnóstico, e não uma medição
já feita deste acervo — a distinção está escrita lá.
