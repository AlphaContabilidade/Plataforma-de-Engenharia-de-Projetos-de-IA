"""Preenchedor de scaffold nativo — Claude Code integrado.

Sem API externa. Claude Code gera código diretamente nos arquivos.
Usado via Edit/Write tools durante a sessão.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class ArquivoGerado:
    """Arquivo preenchido."""

    caminho: Path
    conteudo: str
    tipo: str  # "react", "nodejs", "config"
    status: str  # "gerado", "pendente"


def gerar_app_jsx(blueprint: dict[str, Any]) -> str:
    """Gera App.jsx (React component principal)."""
    nome_projeto = blueprint.get("nome", "App")
    objetivo = blueprint.get("objetivo_transformacao", "Aplicação")
    mvp = blueprint.get("mvp", [])

    features = "\n      ".join(f"<li>{f}</li>" for f in mvp) if mvp else "<li>MVP</li>"

    return f'''import {{ useState }} from 'react'
import './App.css'

export default function App() {{
  const [count, setCount] = useState(0)

  return (
    <div className="app">
      <header className="app-header">
        <h1>{nome_projeto}</h1>
        <p className="subtitle">{objetivo}</p>
      </header>

      <main className="app-main">
        <section className="features">
          <h2>MVP</h2>
          <ul>
            {features}
          </ul>
        </section>

        <section className="demo">
          <h2>Demo</h2>
          <button onClick={{() => setCount(count + 1)}}>
            Clicado {{count}} vezes
          </button>
          <p>API: <code>GET /api/health</code></p>
        </section>
      </main>

      <footer className="app-footer">
        <p>Gerado por AI-ENGINEERING-OS</p>
      </footer>
    </div>
  )
}}
'''


def gerar_app_css() -> str:
    """Gera App.css (estilos)."""
    return '''/* App Styles */

* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  color: #333;
}}

.app {{
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: white;
  margin: 20px;
  border-radius: 8px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}}

.app-header {{
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  text-align: center;
}}

.app-header h1 {{
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}}

.subtitle {{
  font-size: 1.1rem;
  opacity: 0.9;
}}

.app-main {{
  flex: 1;
  padding: 2rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}}

.features, .demo {{
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}}

.features h2, .demo h2 {{
  color: #667eea;
  margin-bottom: 1rem;
}}

.features ul {{
  list-style: none;
}}

.features li {{
  padding: 0.5rem 0;
  padding-left: 1.5rem;
  position: relative;
}}

.features li:before {{
  content: ">>";
  position: absolute;
  left: 0;
  color: #667eea;
  font-weight: bold;
}}

button {{
  background: #667eea;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}}

button:hover {{
  background: #764ba2;
}}

code {{
  background: #e9ecef;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}}

.app-footer {{
  background: #f8f9fa;
  padding: 1.5rem;
  text-align: center;
  border-top: 1px solid #e9ecef;
  color: #6c757d;
}}

@media (max-width: 768px) {{
  .app-main {{
    grid-template-columns: 1fr;
  }}

  .app-header h1 {{
    font-size: 1.8rem;
  }}
}}
'''


def gerar_index_js(blueprint: dict[str, Any]) -> str:
    """Gera backend index.js (Express server)."""
    nome_projeto = blueprint.get("nome", "API")

    return '''const express = require('express')
const cors = require('cors')

const app = express()
const PORT = process.env.PORT || 3000

// Middleware
app.use(cors())
app.use(express.json())

// Health check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  })
})

// Info endpoint
app.get('/api/info', (req, res) => {
  res.json({
    name: 'API',
    version: '0.0.1',
    environment: process.env.NODE_ENV || 'development',
  })
})

// Simple in-memory database
let items = [
  { id: 1, name: 'Item 1', done: false },
  { id: 2, name: 'Item 2', done: true },
]

let nextId = 3

// GET /api/items - Lista todos
app.get('/api/items', (req, res) => {
  res.json(items)
})

// GET /api/items/:id - Busca por ID
app.get('/api/items/:id', (req, res) => {
  const item = items.find(i => i.id === parseInt(req.params.id))
  if (!item) {
    return res.status(404).json({ error: 'Item não encontrado' })
  }
  res.json(item)
})

// POST /api/items - Cria novo
app.post('/api/items', (req, res) => {
  const { name } = req.body
  if (!name) {
    return res.status(400).json({ error: 'Nome é obrigatório' })
  }
  const newItem = { id: nextId++, name, done: false }
  items.push(newItem)
  res.status(201).json(newItem)
})

// PUT /api/items/:id - Atualiza
app.put('/api/items/:id', (req, res) => {
  const item = items.find(i => i.id === parseInt(req.params.id))
  if (!item) {
    return res.status(404).json({ error: 'Item não encontrado' })
  }
  if (req.body.name) item.name = req.body.name
  if (req.body.done !== undefined) item.done = req.body.done
  res.json(item)
})

// DELETE /api/items/:id - Deleta
app.delete('/api/items/:id', (req, res) => {
  const index = items.findIndex(i => i.id === parseInt(req.params.id))
  if (index === -1) {
    return res.status(404).json({ error: 'Item não encontrado' })
  }
  items.splice(index, 1)
  res.json({ message: 'Item deletado' })
})

// Error handling
app.use((err, req, res, next) => {
  console.error(err)
  res.status(500).json({ error: 'Erro interno do servidor' })
})

// Start server
app.listen(PORT, () => {
  console.log(`API rodando em http://localhost:${PORT}`)
  console.log(`Health check: http://localhost:${PORT}/api/health`)
})

module.exports = app
'''


def gerar_env_example() -> str:
    """Gera .env.example."""
    return '''# Backend environment variables
PORT=3000
NODE_ENV=development

# Database (futuro)
# DATABASE_URL=

# API Keys (futuro)
# API_KEY=
'''


def gerar_package_json_frontend(nome_projeto: str) -> str:
    """Gera package.json atualizado com scripts."""
    import json
    pkg = {
        "name": f"{nome_projeto}-frontend",
        "version": "0.0.1",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview",
            "test": "echo 'Add tests here'",
        },
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
        },
        "devDependencies": {
            "@vitejs/plugin-react": "^4.0.0",
            "vite": "^4.3.0",
        },
    }
    return json.dumps(pkg, indent=2, ensure_ascii=True)


def gerar_package_json_backend(nome_projeto: str) -> str:
    """Gera package.json backend atualizado."""
    import json
    pkg = {
        "name": f"{nome_projeto}-backend",
        "version": "0.0.1",
        "type": "commonjs",
        "main": "src/index.js",
        "scripts": {
            "start": "node src/index.js",
            "dev": "node --watch src/index.js",
            "test": "echo 'Add tests here'",
        },
        "dependencies": {
            "express": "^4.18.0",
            "cors": "^2.8.0",
        },
        "devDependencies": {},
    }
    return json.dumps(pkg, indent=2, ensure_ascii=True)


def listar_arquivos_para_preencher(scaffold_dir: Path) -> dict[str, Path]:
    """Lista arquivos que precisam preenchimento."""
    arquivos = {}

    if (scaffold_dir / "frontend" / "src" / "App.jsx").exists():
        arquivos["frontend/src/App.jsx"] = scaffold_dir / "frontend" / "src" / "App.jsx"
    if (scaffold_dir / "frontend" / "src" / "index.css").exists():
        arquivos["frontend/src/index.css"] = scaffold_dir / "frontend" / "src" / "index.css"
    if (scaffold_dir / "backend" / "src" / "index.js").exists():
        arquivos["backend/src/index.js"] = scaffold_dir / "backend" / "src" / "index.js"
    if (scaffold_dir / "backend" / ".env.example").exists():
        arquivos["backend/.env.example"] = scaffold_dir / "backend" / ".env.example"

    return arquivos


def gerar_readme(blueprint: dict[str, Any], scaffold_dir: Path) -> str:
    """Gera README completo."""
    nome_projeto = blueprint.get("nome", "Projeto")
    resumo = blueprint.get("resumo", "Descrição do projeto")
    objetivo = blueprint.get("objetivo_transformacao", "")

    return f'''# {nome_projeto}

{resumo}

## Objetivo

{objetivo}

## Estrutura

```
{scaffold_dir.name}/
├── frontend/          # React + Vite
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   └── index.css
│   ├── public/
│   ├── index.html
│   └── package.json
├── backend/           # Node.js + Express
│   ├── src/
│   │   └── index.js
│   ├── .env.example
│   └── package.json
└── README.md
```

## Quick Start

### Frontend

```bash
cd frontend
npm install
npm run dev
# Abre em http://localhost:5173
```

### Backend

```bash
cd backend
npm install
npm start
# Abre em http://localhost:3000
# Health: http://localhost:3000/api/health
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/info` - Info da API
- `GET /api/items` - Lista todos os itens
- `GET /api/items/:id` - Busca por ID
- `POST /api/items` - Cria novo
- `PUT /api/items/:id` - Atualiza
- `DELETE /api/items/:id` - Deleta

## Deploy

Gerado por **AI-ENGINEERING-OS v1** - Plataforma de Engenharia de Projetos de IA
'''
