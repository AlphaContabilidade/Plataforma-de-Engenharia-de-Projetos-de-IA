---
volume: "07"
volume_nome: PROMPT-ENGINE
tipo: ENGINE
secao: 17-Conclusao
status: RASCUNHO
atualizado_em: 2026-07-29
---

# Conclusão

Este volume entregou um motor de prompts com três módulos, dez regras invioláveis e trinta e
quatro testes que rodam sem rede. O que ele torna possível é uma frase que não era pronunciável
antes: a versão `v2` do prompt `classificar-lancamento` está em produção desde a data tal, acertou
uma fração medida da bateria de casos de ouro, e a versão anterior está preservada com o estado que
recebeu. Nenhuma parte dessa frase depende da memória de quem escreveu o prompt.

As três decisões que sustentam o resultado merecem ser repetidas no fechamento, porque são elas que
um leitor levará para outro contexto. A primeira é validar o contrato na construção: o erro aparece
no carregamento do módulo, antes de qualquer chamada paga, e o custo é apenas construir prompt
dinâmico dentro de tratamento de exceção. A segunda é derivar a versão do hash do conteúdo,
cobrindo corpo e assinatura, o que torna o registro idempotente sem penalidade e faz de qualquer
mudança de contrato uma versão nova mesmo quando o texto não muda. A terceira é injetar o executor,
o que mantém o motor sem conhecimento de provedor e permite que a bateria de teste rode em cada
mudança — a propriedade que decide se o gate de evidência será mantido ligado ou desligado no
primeiro dia em que atrasar uma entrega.

O volume também declarou o que não faz. Compilação para múltiplos dialetos é do volume 28,
otimização automática do corpo é do 29, e roteamento por custo ou latência é do 27. Essa
declaração não é formalidade: a especificação original desta plataforma descrevia essas
responsabilidades de forma sobreposta, e sobreposição não declarada produz duas implementações do
mesmo comportamento que divergem sem que ninguém perceba. A fronteira está em
[`03-Escopo.md`](03-Escopo.md) com a razão de cada corte.

Fica registrado um limite honesto. A máquina de estados garante que uma versão passou pelo estado
de avaliação; ela não garante que a avaliação teve resultado bom. O julgamento do número é do
operador, e o checklist de [`15-Checklist.md`](15-Checklist.md) é o instrumento desse julgamento.
Automatizar o limiar exigiria fixar um número aplicável a todo domínio, e um número arbitrário
aplicado uniformemente daria a aparência de rigor sem o rigor.
