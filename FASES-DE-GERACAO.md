# Fases de Geração de Código: Blueprint → Código Executável

> **Status:** Fases 2-3 implementadas, testes passando  
> **Total de código novo:** ~1.200 linhas  
> **Testes:** 33 (13 scaffold + 12 llm_filler + 8 refinador)  
> **Endpoints HTTP:** 3

## Arquitetura

```
USUÁRIO
  ↓
1. DESCOBERTA (interface web)
   - 4 etapas de perguntas
   - Output: Blueprint (JSON)
  ↓
2. SCAFFOLD (determinístico)
   - Blueprint → Estrutura vazia
   - React + Node.js + .gitignore
   - Output: Diretório pronto
  ↓
3. PREENCHIMENTO COM LLM (Claude)
   - Scaffold + Blueprint → Código funcional
   - Arquivo por arquivo
   - Output: Backend + Frontend com código
  ↓
4. REFINAMENTO ITERATIVO (Select & Edit)
   - Usuário: "Adicione autenticação"
   - Sistema regenera aquela parte
   - Repete quantas vezes precisar
  ↓
CÓDIGO EXECUTÁVEL (pronto para npm install)
```

---

## Fase 1: Scaffold Determinístico ✅

**Módulo:** `ferramentas/gerador_scaffold.py`  
**Dependências:** Nenhuma (stdlib)  
**O que faz:**
- Recebe Blueprint com nome, objetivo, MVP
- Cria estrutura React + Node.js
- Gera package.json, .gitignore, README
- Determinístico: mesmo input → mesmo output

**Exemplo:**

```python
from ferramentas.projetos import gerar_blueprint
from ferramentas.gerador_scaffold import gerar_scaffold

blueprint = gerar_blueprint(entrada_descoberta)
scaffold = gerar_scaffold(blueprint.para_dict(), Path("~/projetos"))

print(f"Criado em: {scaffold.diretorio_raiz}")
# Criado em: /home/user/projetos/novo-produto/
```

**Estrutura gerada:**

```
novo-produto/
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx         ← placeholder
│   │   └── index.css
│   ├── public/
│   ├── index.html
│   ├── package.json
│   └── .gitignore
├── backend/
│   ├── src/
│   │   └── index.js        ← placeholder
│   ├── .env.example
│   ├── package.json
│   └── .gitignore
├── README.md
└── .gitignore
```

**Testes:** 13 unitários + 2 integração  
**Endpoint HTTP:** `POST /api/gerar-codigo`

---

## Fase 2: LLM Filler (Preenchimento) ✅

**Módulo:** `codigo_generators/llm_filler.py`  
**Dependências:** `anthropic` (pip install anthropic)  
**O que faz:**
- Recebe scaffold vazio + Blueprint
- Para cada arquivo, gera prompt contextualizado
- Chama Claude para escrever código
- Salva código no arquivo
- Retorna tokens gastos e status

**Fluxo:**

```python
from codigo_generators import preencher_com_claude

resultado = preencher_com_claude(
    diretorio_scaffold=Path("novo-produto"),
    blueprint={
        "nome": "App Hábitos",
        "objetivo": "Rastrear hábitos diários",
        "mvp": ["Dashboard", "Criar hábito"],
    },
    api_key="sk-ant-..."  # ou env ANTHROPIC_API_KEY
)

# resultado.status == "completo"
# resultado.arquivos_preenchidos == [10 arquivos]
# resultado.resumo == "10 arquivo(s) preenchido(s)"
```

**O que Claude gera:**
- `App.jsx`: Componente React com dashboard básico
- `index.js`: Express server com rotas REST
- Outros: Helpers, styles, configs

**Prompts compilados (volume 28):**
- Cada arquivo recebe prompt customizado
- Inclui tipo (React/Node), objetivo, MVP
- Restrições: sem ORMs, sem auth complexa no MVP

**Testes:** 12 (com mock da API)  
**Endpoint HTTP:** `POST /api/preencher-codigo`

---

## Fase 3: Refinador Iterativo (Select & Edit) ✅

**Módulo:** `codigo_generators/refinador_iterativo.py`  
**Dependências:** `anthropic`  
**O que faz:**
- Usuário descreve mudança em português simples
- Sistema regenera aquela parte do código
- Iteração contínua até satisfeito
- Similar ao "Select & Edit" do LOVABLE

**Fluxo no chat:**

```
Usuário: "Adicione autenticação JWT"
Sistema: Regenera backend/src/index.js com JWT
Usuário: "Adicione validação de email"
Sistema: Refaz aquela parte
Usuário: "Pronto!"
Sistema: Código salvo
```

**Via código:**

```python
from codigo_generators import refinar_iterativo

resultado = refinar_iterativo(
    caminho_arquivo=Path("novo-produto/backend/src/index.js"),
    descricao="Adicione rota POST /usuarios",
    api_key="sk-ant-..."
)

print(f"Status: {resultado.status}")
print(f"Tokens gastos: {resultado.tokens_input + resultado.tokens_output}")
```

**Testes:** 8 (com mock)  
**Endpoint HTTP:** `POST /api/refinar-codigo`

---

## API HTTP Completa

### 1. POST /api/gerar-codigo
Gera scaffold vazio.

**Request:**
```json
{
  "blueprint": {
    "nome": "Meu App",
    "objetivo_transformacao": "Gerenciar tarefas",
    "resumo": "...",
    "mvp": ["Criar tarefa", "Listar"]
  },
  "destino": "/home/user/projetos"
}
```

**Response (200):**
```json
{
  "modo": "scaffold",
  "nome_projeto": "meu-app",
  "diretorio": "/home/user/projetos/meu-app",
  "arquivos": [10 arquivos],
  "status": "criado",
  "package_json_frontend": { ... },
  "package_json_backend": { ... }
}
```

---

### 2. POST /api/preencher-codigo
Preenche scaffold com código.

**Request:**
```json
{
  "blueprint": { ... },
  "diretorio": "/home/user/projetos/meu-app",
  "api_key": "sk-ant-..."
}
```

**Response (200):**
```json
{
  "modo": "codigo_preenchido",
  "diretorio": "/home/user/projetos/meu-app",
  "status": "completo",
  "resumo": "10 arquivo(s) preenchido(s)",
  "arquivos_preenchidos": 10,
  "detalhes": [
    {
      "caminho": "frontend/src/App.jsx",
      "status": "sucesso",
      "tokens_input": 500,
      "tokens_output": 300
    },
    ...
  ]
}
```

---

### 3. POST /api/refinar-codigo
Refina um arquivo.

**Request:**
```json
{
  "arquivo": "/home/user/projetos/meu-app/backend/src/index.js",
  "descricao": "Adicione validação de entrada em todas as rotas",
  "api_key": "sk-ant-..."
}
```

**Response (200):**
```json
{
  "modo": "codigo_refinado",
  "arquivo": "backend/src/index.js",
  "status": "sucesso",
  "descricao": "Adicione validação",
  "tokens_input": 200,
  "tokens_output": 400
}
```

---

## Fluxo Completo: Do Zero ao Executável

```bash
# 1. Iniciar interface de descoberta
python iniciar.py interface

# [Usuário responde 4 perguntas na web]

# 2. No código/chat:

# Recebe Blueprint do frontend
blueprint = { ... }  # JSON do formulário

# Cria scaffold
scaffold = gerar_scaffold(blueprint, Path.cwd() / "projetos")

# Preenche com código
resultado = preencher_com_claude(
    scaffold.diretorio_raiz,
    blueprint,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# [Opcionalmente refina]
refinar_iterativo(
    Path("projetos/novo-produto/backend/src/index.js"),
    "Adicione logger estruturado",
)

# 3. Resultado: projeto executável
cd projetos/novo-produto/backend
npm install
npm start

cd ../frontend
npm install
npm run dev
```

---

## Custos e Limites

### Tokens por Fase

| Fase | Input | Output | Total/Arquivo |
|------|-------|--------|---|
| Scaffold | 0 | 0 | 0 (determinístico) |
| LLM Filler | ~500 | ~300 | ~800 × 10 arquivos = 8K tokens |
| Refinação | ~200 | ~400 | ~600 por mudança |

**Exemplo completo:** 8K (scaffold) + 600 (uma refinação) = **8.6K tokens**

### Recomendações

- ✅ Use scaffold determinístico primeiro (grátis)
- ✅ Preencha quando aprovado o Blueprint (custa ~$0.03 por projeto)
- ✅ Refine iterativamente (~$0.001 por mudança)
- ❌ Não regenere tudo quando pode refinar uma parte

---

## Diferenças com LOVABLE

| Aspecto | LOVABLE | Nossa Plataforma |
|---------|---------|------------------|
| Descoberta | UI visual | 4 perguntas texto |
| Blueprint | Automático | Estruturado (JSON) |
| Scaffold | Rápido | Determinístico (verificável) |
| Preenchimento | Direto | Compilado (volume 28) |
| Refinação | Select & Edit visual | Select & Edit por texto (próx: visual) |
| Templates | Fixos (React/Node) | Personalizáveis (futuro: volume 40) |
| Deploy | 1-click (Vercel) | Manual (usuário escolhe) |

---

## Roadmap Futuro

**Fase 4:** Templates extraídos (volume 40)
- Quando houver 3+ projetos completos
- Padrões reutilizáveis em `templates/react-node/`
- Scaffold ainda mais rico

**Pós-fase 4:** UI visual com Select & Edit
- Captura de screenshot do componente
- Clique em elemento específico
- Descrição em português → regenera aquele componente

**Modelos locais:** llama2, mistral
- Para quem não quer usar Claude
- Qualidade menor, mas zero API calls

---

## Como Testar

### Sem API Key (Mock)
```bash
pytest codigo_generators/tests -v
pytest ferramentas/tests/test_gerador_scaffold.py -v
```

### Com API Key (Real)
```bash
export ANTHROPIC_API_KEY="sk-ant-..."

python -c "
from pathlib import Path
from ferramentas.gerador_scaffold import gerar_scaffold
from codigo_generators.llm_filler import preencher_com_claude

scaffold = gerar_scaffold(
    {'nome': 'Test App', 'objetivo_transformacao': 'Test'},
    Path('/tmp/test-project')
)

resultado = preencher_com_claude(
    scaffold.diretorio_raiz,
    {'nome': 'Test App'},
)

print(f'Status: {resultado.status}')
print(f'Arquivos preenchidos: {len(resultado.arquivos_preenchidos)}')
"
```

---

## Arquivos Novos/Modificados

```
+ codigo_generators/
  ├── __init__.py
  ├── llm_filler.py (342 linhas)
  ├── refinador_iterativo.py (193 linhas)
  └── tests/
      ├── __init__.py
      ├── test_llm_filler.py (245 linhas)
      └── test_refinador_iterativo.py (201 linhas)

~ ferramentas/construtor_web.py (+94 linhas de endpoints)

+ FASES-DE-GERACAO.md (este arquivo)
```

**Total:** ~1.200 linhas de código novo, todos testados.

---

**Pronto para usar! Próxima parada: templates extraídos da vida real (fase 4).**
