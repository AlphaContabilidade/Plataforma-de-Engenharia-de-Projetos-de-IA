# Guia de uso — do download à construção

Este guia serve para pessoas e para qualquer IA assistente. O funcionamento básico não
exige ChatGPT, Claude, Codex, chave de API ou assinatura de um modelo.

## 1. Baixar

Com Git instalado:

```bash
git clone https://github.com/AlphaContabilidade/Plataforma-de-Engenharia-de-Projetos-de-IA.git
cd Plataforma-de-Engenharia-de-Projetos-de-IA
```

Também é possível usar **Code > Download ZIP** no GitHub e extrair a pasta.

## 2. Requisito

Instale Python 3.11 ou superior. Depois confirme:

```bash
python --version
python iniciar.py verificar
```

O verificador informa se o clone possui todos os arquivos essenciais.

## 3. Abrir a ferramenta

```bash
python iniciar.py interface
```

O navegador abrirá a interface local. Se isso não acontecer, copie a URL exibida no
terminal. Para iniciar sem abrir automaticamente:

```bash
python iniciar.py interface --sem-navegador
```

Nenhum dado é enviado para uma IA por esse comando. O servidor aceita conexões apenas no
próprio computador (`127.0.0.1`).

## 4. Descrever o projeto

Escolha entre:

- **Criar projeto novo**
- **Analisar projeto existente**

Descreva a ideia em linguagem simples. A ferramenta fará perguntas personalizadas sobre
público, problema, plataforma, prioridade e decisões específicas. Campos obrigatórios e
opcionais aparecem identificados.

Você pode anexar requisitos, planilhas, propostas, código e outros documentos. Arquivos
textuais podem entrar na análise; formatos que não forem extraídos serão registrados como
referência, sem falsa alegação de leitura.

## 5. Trabalhar com o resultado

Na área final:

- **Plano:** escopo inicial, arquitetura, riscos e perguntas abertas;
- **Prévia:** direção visual que pode receber ajustes simples;
- **Gerenciar:** download do plano e instruções para continuar a construção.

Publicação permanece bloqueada enquanto não existir uma versão executável testada.

## 6. Continuar com qualquer IA

Abra sua IA preferida dentro da pasta clonada e diga:

> Leia `AGENTS.md` e `PROTOCOLO-UNIVERSAL-DA-IA.md`. Rode o verificador, use o Plano de
> Solução como contrato inicial e me conduza com uma pergunta simples por vez.

Você também pode gerar um lembrete adaptado:

```bash
python iniciar.py adaptar --ia "Claude"
python iniciar.py adaptar --ia "Codex"
python iniciar.py adaptar --ia "Gemini"
```

A IA deve confirmar perguntas abertas antes de escrever código e deve testar antes de
afirmar que o resultado funciona.

## 7. Integração MCP opcional

O diretório `chatgpt_app/` oferece um adaptador MCP para ambientes compatíveis. Ele não é
necessário para usar a interface universal.

```bash
python -m pip install -r chatgpt_app/requirements.txt
python -m chatgpt_app.server
```

Consulte `chatgpt_app/README.md` para configuração detalhada.

## 8. Atualizar depois

Se o repositório foi clonado com Git:

```bash
git pull
python iniciar.py verificar
```

Se houver alterações locais, peça à sua IA para revisar `git status` antes do `git pull`.

## Problemas comuns

### `python` não é reconhecido

Instale Python 3.11+ e marque a opção para adicioná-lo ao PATH. No Windows, tente também
`py iniciar.py verificar`.

### A porta está ocupada

Escolha outra:

```bash
python iniciar.py interface --porta 8877
```

### A página não abre

Mantenha o terminal aberto e acesse a URL informada. Encerrar o terminal encerra o servidor.

### A IA não conhece os comandos

Peça que ela leia `AGENTS.md`. As integrações específicas são opcionais; o comando
`python iniciar.py interface` funciona independentemente delas.
