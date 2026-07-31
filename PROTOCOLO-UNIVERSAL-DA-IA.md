# Protocolo universal da IA

## Objetivo

Permitir que qualquer inteligência artificial clone este repositório, compreenda a
plataforma e conduza a pessoa desde uma ideia até um software verificável. A IA é o
operador inteligente; o repositório fornece método, memória técnica, interface e gates.

## Contrato de independência

A plataforma não depende de um modelo específico. Existem três camadas:

1. **Núcleo determinístico:** perguntas, Plano de Solução, acervo e validações em Python.
2. **Interface universal:** navegador local iniciado por `python iniciar.py interface`.
3. **Adaptadores opcionais:** MCP/ChatGPT ou recursos nativos de Claude, Codex e outras IAs.

Uma integração pode melhorar a experiência, mas nunca pode se tornar condição para abrir,
planejar, exportar ou validar um projeto.

## Roteiro que a IA deve seguir

### 1. Reconhecer o ambiente

Rode:

```bash
python iniciar.py verificar --json
```

Se o Python for anterior ao 3.11 ou faltar arquivo essencial, pare e explique exatamente
o que precisa ser corrigido. Não tente compensar um clone incompleto inventando arquivos.

### 2. Entender a solicitação

Classifique o trabalho sem limitar as possibilidades:

- criar projeto novo;
- analisar e melhorar projeto existente;
- transformar dados ou planilhas em BI;
- criar sistema, aplicativo, página ou portal;
- automatizar ou integrar processos;
- modernizar, migrar ou auditar uma solução.

### 3. Conduzir a descoberta

Faça uma pergunta simples por vez. Explique termos técnicos em linguagem cotidiana.
Indique claramente campos obrigatórios e opcionais. Quando a pessoa não souber, ofereça
opções e registre a incerteza como pergunta aberta.

### 4. Tratar documentos

Leia apenas formatos que a ferramenta atual consegue extrair com segurança. Para arquivos
binários sem extração disponível, registre nome, tipo e tamanho; não alegue ter analisado
o conteúdo. Nunca envie anexos para serviços externos sem autorização específica.

### 5. Firmar o Plano de Solução

O plano deve conter problema, público, MVP, arquitetura, riscos, decisões, perguntas
abertas, anexos considerados e conhecimento recomendado. Apresente-o para revisão antes
de implementar. Mudanças posteriores devem atualizar o contrato ou ser registradas.

### 6. Construir

Depois da aprovação:

1. inspecione o repositório e as instruções locais;
2. escolha a menor alteração capaz de entregar valor verificável;
3. implemente preservando o que já existe;
4. teste comportamento, integração e interface quando aplicável;
5. mostre o resultado e a evidência;
6. repita até cumprir os critérios de aceite.

### 7. Finalizar com honestidade

Use estes significados:

- **Plano pronto:** descoberta organizada; código pode ainda não existir.
- **Prévia pronta:** representação visual validável; não equivale a produto publicado.
- **Versão executável:** software inicia e os testes definidos passam.
- **Publicado:** uma implantação real foi concluída e inspecionada.

Nunca avance o status por expectativa.

## Adaptação por capacidade

| Capacidade da IA | Como proceder |
|---|---|
| Lê e edita arquivos | Trabalhar diretamente no clone e preservar o Git |
| Executa terminal | Rodar inicializador, testes e gates |
| Controla navegador | Validar a jornada local e o comportamento visual |
| Usa MCP | Conectar o adaptador opcional em `chatgpt_app/` |
| Apenas conversa | Orientar a pessoa com comandos exatos e interpretar as saídas |

## Handoff entre IAs

Ao transferir o projeto para outra IA, deixe:

- objetivo atual;
- decisões confirmadas;
- perguntas ainda abertas;
- arquivos alterados;
- comandos executados e resultados;
- riscos ou bloqueios;
- próximo passo concreto.

O handoff deve ser compreensível sem acesso ao histórico da conversa anterior.
