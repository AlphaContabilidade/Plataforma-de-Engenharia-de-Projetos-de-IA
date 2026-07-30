# Gerador de Scaffold — React + Node.js

> **Status:** Funcional, testes passando  
> **Adicionado em:** 2026-07-30  
> **Tipo:** Camada de adaptador (opcional, usa stdlib)

## O que é

Módulo `ferramentas/gerador_scaffold.py` que transforma um **Blueprint** (Plano de Solução) em estrutura de projeto executável:

- **Frontend:** React + Vite (src/App.jsx, index.html, package.json)
- **Backend:** Node.js + Express (src/index.js, .env.example, package.json)
- **Raiz:** README.md, .gitignore, estrutura pronta para git

**Determinístico:** Mesmo Blueprint → Mesmo scaffold (sem aleatoriedade).

## Como usar

### Via CLI (em desenvolvimento)

```bash
python -m ferramentas.gerador_scaffold \
  --blueprint plano_solucao.json \
  --destino ~/meus_projetos
```

### Via código Python

```python
from pathlib import Path
from ferramentas.projetos import gerar_blueprint
from ferramentas.gerador_scaffold import gerar_scaffold

# Fase 1: Descubra requisitos
entrada = {
    "ideia": "App de controlar hábitos",
    "tipo": "web",
    # ... outras respostas
}

# Fase 2: Gere Blueprint
blueprint = gerar_blueprint(entrada)

# Fase 3: Gere scaffold
scaffold = gerar_scaffold(
    blueprint.para_dict(),
    destino=Path.cwd() / "projetos"
)

print(f"✓ Criado em: {scaffold.diretorio_raiz}")
print(f"✓ Arquivos: {len(scaffold.arquivos_criados)}")
```

### Via API HTTP (construtor web)

**Endpoint:** `POST /api/gerar-codigo`

```bash
curl -X POST http://127.0.0.1:8765/api/gerar-codigo \
  -H "Content-Type: application/json" \
  -d '{
    "blueprint": {
      "nome": "Meu App",
      "objetivo_transformacao": "...",
      "resumo": "..."
    },
    "destino": "/home/user/projetos"
  }'
```

**Resposta:**

```json
{
  "modo": "scaffold",
  "nome_projeto": "meu-app",
  "diretorio": "/home/user/projetos/meu-app",
  "arquivos": [
    "/home/user/projetos/meu-app/frontend/index.html",
    "/home/user/projetos/meu-app/backend/src/index.js",
    ...
  ],
  "status": "criado",
  "package_json_frontend": { ... },
  "package_json_backend": { ... }
}
```

## Fluxo completo: Descoberta → Scaffold → Código

```
1. Interface web: formulário de descoberta (4 etapas)
   ↓
2. Blueprint: Plano de Solução em JSON (aprovado)
   ↓
3. Scaffold: Estrutura React + Node vazia
   ↓
4. [LLM - próxima fase] Preenche código dentro de cada arquivo
   ↓
5. Projeto executável: npm install → npm run dev
```

## Estrutura gerada

```
meu-app/
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   └── index.css
│   ├── public/
│   ├── index.html
│   ├── package.json
│   └── .gitignore
├── backend/
│   ├── src/
│   │   └── index.js
│   ├── .env.example
│   ├── package.json
│   └── .gitignore
├── README.md
└── .gitignore
```

## Próximos passos

### Fase 2: Preenchimento com LLM (adaptador)

Novo módulo `codigo_generators/llm_filler.py`:
- Recebe scaffold + Blueprint
- Chama Claude/GPT para preencher cada arquivo
- Usa volume 28 (PROMPT-COMPILER) para adaptar prompts

### Fase 3: Refinamento interativo

Como LOVABLE: Select & Edit
- Usuário clica em elemento
- Descreve mudança em linguagem natural
- Sistema regenera apenas aquela parte

### Fase 4: Templates extraídos

Quando houver 2+ projetos passando pelos gates:
- Extrair padrões reais em `templates/react-node/`
- Documentar em volume `40-TEMPLATES`
- Reutilizar para scaffold mais rico

## Testes

**Unitários:** 13 testes (normalizar_nome, criar estrutura, reproduzibilidade)

```bash
python -m pytest ferramentas/tests/test_gerador_scaffold.py -v
```

**Integração:** 2 testes (Blueprint → Scaffold com dados reais)

```bash
python -m pytest ferramentas/tests/test_integracao_blueprint_scaffold.py -v
```

**Todos:** 229 testes da plataforma

```bash
python -m pytest ferramentas/tests -q
```

## Restrições atuais

- ✅ React + Node.js fixos (próx: templates plugáveis)
- ✅ Sem dependências externas (só stdlib)
- ✅ Sem chamar LLM (determinístico)
- ✅ Sem npm install automático (deixa pra usuário)
- ✅ Sem git init automático (respeita contratos locais)

## Relação com os volumes

- **07-PROMPT-ENGINE:** define contrato de prompts (será usado em compilador)
- **28-PROMPT-COMPILER:** transforma prompts para cada provedor (préx implementar)
- **37-CODE-GENERATION:** escopo futuro (volume está em rascunho)
- **40-TEMPLATES:** onde templates extraídos viverão

## Arquivos

| Arquivo | Linhas | Tipo |
|---------|--------|------|
| `ferramentas/gerador_scaffold.py` | 285 | Módulo principal |
| `ferramentas/tests/test_gerador_scaffold.py` | 110 | Unitários |
| `ferramentas/tests/test_integracao_blueprint_scaffold.py` | 110 | Integração |
| `ferramentas/construtor_web.py` | +30 | Endpoint HTTP |

**Total novo:** ~535 linhas, tudo testado, determinístico.
