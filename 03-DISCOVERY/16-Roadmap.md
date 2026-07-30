---
volume: "03"
volume_nome: DISCOVERY
tipo: PROCESSO
secao: 16-Roadmap
status: PRONTO
atualizado_em: 2026-07-30
---

# Roadmap

O que este volume ainda não cobre, na ordem em que pretende cobrir. Cada item diz o que falta e por
que ele não foi feito agora — porque "não foi feito" sem razão declarada é indistinguível de
esquecimento.

## 1. Conjunto de frases anotadas para medir a detecção

Hoje a qualidade da tabela de termos é medida em produção, pela fração de inferências recusadas. Falta
um conjunto de frases reais com a plataforma e os contextos corretos anotados, contra o qual se possa
medir acerto e erro antes de publicar uma mudança na tabela. Não foi feito porque escrever as frases
aqui produziria um conjunto que mede a própria escrita: quem escolhe os termos escolhendo as frases
tem acerto garantido e informação zero. O conjunto tem de vir de entrevistas reais, e por isso ele
depende de uso.

## 2. Lacuna que depende de outra resposta, e não só de plataforma e contexto

O gatilho atual tem dois eixos. Falta o terceiro: a lacuna que só existe porque outra lacuna foi
respondida de um jeito específico — se a autenticação é por conta de terceiro, aparece a pergunta de
qual provedor de identidade. Não foi feito agora porque o gatilho por resposta exige comparar valor de
texto livre, e comparar texto livre traz a mesma classe de ambiguidade que a detecção já tem. A
alternativa é permitir gatilho apenas sobre lacunas com opções fechadas, e essa restrição precisa ser
desenhada antes de ser implementada.

## 3. Custo estimado por lacuna, para ordenar por valor sobre custo

O peso mede quanta incerteza a resposta remove. Falta o outro lado: quanto custa obter a resposta.
Algumas lacunas são caras — "quanto tempo o registro fica guardado" pode exigir consulta a norma — e
uma pergunta de peso oito que leva três dias para ser respondida talvez deva vir depois de duas de
peso sete que se respondem na hora. Não foi feito porque custo de obtenção varia por organização, e
fixá-lo no catálogo seria decidir por todos os casos.

## 4. Persistência entre sessões

A entrevista vive numa sessão. Retomar uma conversa interrompida exige gravar o estado e lê-lo de
volta, com a data de cada resposta. Não foi feito aqui porque o assunto é do volume 12, e a
implementação correta consome aquele componente em vez de reimplementar procedência.

## 5. Verificação que reprove `__init__.py` em pasta de teste de exemplo

A dívida técnica está registrada em [`../ROADMAP.md`](../ROADMAP.md) e este volume adota a solução
correta — `conftest.py` que ajusta o caminho de import. Falta a regra no validador que reprove a
alternativa errada antes de ela custar uma suíte inteira. É trabalho na máquina, não no volume, e por
isso ele está aqui apenas como referência cruzada.
