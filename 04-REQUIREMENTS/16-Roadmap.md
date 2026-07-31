---
volume: "04"
volume_nome: REQUIREMENTS
tipo: PROCESSO
secao: 16-Roadmap
status: RASCUNHO
atualizado_em: 2026-07-31
---

# Roadmap

**1. Consumir a saída do volume 03 sem transcrição manual.** Hoje a especificação da descoberta é
lida por uma pessoa, que escreve os requisitos à mão. Todos os campos de que este volume precisa já
existem lá — resposta, origem, trecho de evidência, decisões abertas com peso —, e a transcrição
manual é justamente onde a origem se perde. Um conversor que gerasse o esqueleto de cada requisito,
com rastro para trás preenchido e critério de aceite em branco, eliminaria a perda sem fingir que a
parte de julgamento pode ser automatizada.

**2. Verificação de rastro para frente como gate.** Hoje a métrica de requisitos sem verificação é
contada à mão. Automatizá-la exige uma convenção de nomeação que ligue requisito e teste — a forma
mais simples é o identificador do requisito no nome ou no marcador do teste. É barato e transforma a
métrica mais útil do volume em algo que reprova sozinho.

**3. Aposentadoria explícita de identificador.** A regra Q4 proíbe reciclar identificador, e hoje
isso depende de disciplina. Uma lista de identificadores aposentados, versionada junto, torna a
violação visível — e é o mesmo remédio que o volume `01` aplica aos identificadores de controle.
