# ChatGPT App — AI-ENGINEERING-OS

Este adaptador leva o construtor de software para uma conversa do ChatGPT por meio de MCP.
O ChatGPT faz a entrevista em linguagem simples; o servidor usa o mesmo motor Python da
plataforma para gerar o Plano de Solução; o widget mostra e edita o resultado dentro do chat.

## Fronteira de segurança da versão 0.1

As quatro ferramentas são somente leitura:

- `abrir_construtor` — abre o widget;
- `planejar_software` — transforma respostas e documentos em um Plano de Solução;
- `consultar_acervo` — lista os 42 volumes e seus estados;
- `consultar_volume` — consulta escopo e dependências de um volume.

Nenhuma ferramenta grava arquivo, executa comando ou afirma que o software foi construído.
Uma futura ferramenta de construção deve ser separada, exigir confirmação e operar num
workspace confinado.

## Executar localmente

Na raiz do repositório:

```powershell
python -m pip install -r chatgpt_app/requirements.txt
python -m chatgpt_app.server
```

Verificação de saúde:

```text
http://127.0.0.1:8000/
```

Endpoint MCP:

```text
http://127.0.0.1:8000/mcp
```

## Conectar ao ChatGPT

O ChatGPT precisa alcançar o servidor por HTTPS. Durante desenvolvimento, exponha a porta
8000 com um túnel HTTPS. Ao usar um domínio de túnel, declare antes de iniciar:

```powershell
$env:MCP_ALLOWED_HOSTS="seu-dominio-do-tunel.example"
$env:MCP_ALLOWED_ORIGINS="https://seu-dominio-do-tunel.example"
python -m chatgpt_app.server
```

Depois:

1. habilite o modo de desenvolvedor nas configurações do ChatGPT;
2. adicione um app MCP;
3. informe `https://seu-dominio-do-tunel.example/mcp`;
4. atualize o app sempre que ferramentas ou metadados mudarem;
5. em uma conversa, selecione o app e peça: “Quero transformar minha ideia em software”.

Para produção, substitua o túnel por hospedagem HTTPS estável, logs, autenticação e
persistência adequadas.
