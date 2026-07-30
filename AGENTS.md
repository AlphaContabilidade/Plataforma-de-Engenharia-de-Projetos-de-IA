# Instruções universais para agentes de IA

Este arquivo é a entrada oficial para qualquer agente que trabalhe neste repositório:
Codex, Claude Code, Gemini CLI, GitHub Copilot, agentes locais ou outros modelos.
Recursos específicos de um fornecedor são opcionais; nunca são requisito do núcleo.

## Comece sempre assim

1. Trabalhe somente dentro da raiz deste repositório.
2. Leia `PROTOCOLO-UNIVERSAL-DA-IA.md`.
3. Rode `python iniciar.py verificar`.
4. Consulte `README.md`, `ROADMAP.md` e os arquivos diretamente ligados à tarefa.
5. Antes de alterar código, confirme o objetivo e preserve mudanças existentes.

Para abrir a experiência principal sem instalar dependências:

```bash
python iniciar.py interface
```

O construtor roda em `127.0.0.1`, usa apenas a biblioteca padrão e não exige chave de API.
Ele produz um Plano de Solução que deve ser tratado como contrato inicial, não como prova
de que o software já foi implementado.

## Como adaptar o trabalho à IA atual

- Use as ferramentas nativas disponíveis para ler, editar e testar arquivos.
- Não altere o domínio ou o contrato para imitar recursos exclusivos do modelo atual.
- Se houver MCP ou integração com chat, trate-a como adaptador opcional.
- Se a IA não controlar navegador, informe a URL local para a pessoa abrir.
- Se a IA não executar comandos, entregue os comandos exatos e aguarde os resultados.
- Nunca exija Claude, Codex, ChatGPT ou outro provedor para usar o motor determinístico.

O comando abaixo imprime o mesmo protocolo com o nome da IA atual:

```bash
python iniciar.py adaptar --ia "nome da IA"
```

## Fluxo obrigatório para projetos de software

1. Descobrir: ideia, público, problema e resultado esperado.
2. Perguntar: uma pergunta simples por vez, distinguindo obrigatório de opcional.
3. Analisar anexos sem inventar conteúdo de arquivos não extraídos.
4. Gerar e revisar o Plano de Solução.
5. Confirmar perguntas abertas e escopo antes de escrever código.
6. Implementar em incrementos pequenos e reversíveis.
7. Rodar testes proporcionais ao risco e registrar a evidência.
8. Só declarar “funciona”, “pronto” ou “publicado” após verificação real.

O projeto pode ser novo ou existente e pode resultar em sistema web, mobile, desktop,
BI/dashboard, site, portal, API, integração, automação, suplemento ou extensão.

## Contratos técnicos

- `00-INTRODUCAO/contrato.json` é a fonte única das regras do acervo.
- Prosa e mensagens para a pessoa usuária são em português do Brasil.
- Python mínimo: 3.11.
- O núcleo em `ferramentas/` usa somente biblioteca padrão.
- O adaptador MCP em `chatgpt_app/` possui dependências próprias e é opcional.
- Datas usam ISO `YYYY-MM-DD`.
- Não ajuste testes para esconder uma falha do conteúdo.
- Não grave status `PRONTO` com gate vermelho.

## Verificação

```bash
python -m pytest ferramentas/tests -q
python -m ferramentas.validar 07
python -m pytest exemplos/07-prompt-engine -q
python -m ferramentas.validar --cross-refs
```

No Windows com diretório temporário restrito, use um destino dentro do repositório:

```powershell
python -m pytest ferramentas/tests -q --basetemp=.pytest_tmp
```

## Segurança e Git

- Não exponha chaves, tokens, dados pessoais ou conteúdo privado de anexos.
- Não execute ações destrutivas ou publique externamente sem autorização.
- Preserve alterações não relacionadas.
- Antes de commit: rode testes, `git diff --check` e revise `git status`.
- Só faça push quando a pessoa pedir explicitamente e apenas para remotos confirmados.
