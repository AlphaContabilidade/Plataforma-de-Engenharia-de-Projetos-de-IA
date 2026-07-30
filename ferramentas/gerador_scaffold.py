"""Gerador determinístico de scaffold React + Node.js a partir de Blueprint.

Este módulo transforma um Blueprint (Plano de Solução) em estrutura de projeto
executável: diretórios, arquivos-base e package.json pré-preenchidos.

Usa apenas a biblioteca padrão (json, pathlib, tempfile). Sem dependências externas.
Output é reproduzível: mesmo Blueprint → mesmo scaffold.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Scaffold:
    """Scaffold gerado — estrutura do projeto pronto para preencher."""

    nome_projeto: str
    diretorio_raiz: Path
    arquivos_criados: list[Path]
    pacote_json_frontend: dict[str, Any]
    pacote_json_backend: dict[str, Any]
    status: str  # "criado", "erro", etc.


def normalizar_nome(nome: str) -> str:
    """Converte nome em slug válido para npm/fs."""
    return nome.lower().replace(" ", "-").replace("_", "-")[:50]


def gerar_scaffold(
    blueprint: dict[str, Any],
    destino: Path,
) -> Scaffold:
    """Cria scaffold React + Node.js a partir de Blueprint.

    Args:
        blueprint: dict com keys: nome, mvp, objetivo_transformacao, etc.
        destino: raiz onde criar o projeto

    Returns:
        Scaffold com resultado e lista de arquivos criados.
    """
    nome = blueprint.get("nome", "projeto-novo")
    slug = normalizar_nome(nome)
    raiz = destino / slug

    try:
        raiz.mkdir(parents=True, exist_ok=True)
        arquivos = []

        # Frontend (React + Vite)
        frontend = raiz / "frontend"
        frontend.mkdir(exist_ok=True)
        arquivos.extend(_criar_frontend(frontend, slug, blueprint))

        # Backend (Node.js + Express)
        backend = raiz / "backend"
        backend.mkdir(exist_ok=True)
        arquivos.extend(_criar_backend(backend, slug, blueprint))

        # Raiz do projeto
        arquivos.extend(_criar_raiz(raiz, slug, blueprint))

        pkg_frontend = _pacote_json_frontend(slug, blueprint)
        pkg_backend = _pacote_json_backend(slug, blueprint)

        return Scaffold(
            nome_projeto=slug,
            diretorio_raiz=raiz,
            arquivos_criados=arquivos,
            pacote_json_frontend=pkg_frontend,
            pacote_json_backend=pkg_backend,
            status="criado",
        )

    except Exception as e:
        return Scaffold(
            nome_projeto=slug,
            diretorio_raiz=raiz,
            arquivos_criados=[],
            pacote_json_frontend={},
            pacote_json_backend={},
            status=f"erro: {e}",
        )


def _criar_frontend(
    raiz_frontend: Path,
    slug: str,
    blueprint: dict[str, Any],
) -> list[Path]:
    """Estrutura do frontend React."""
    arquivos = []

    # Diretórios
    (raiz_frontend / "src" / "components").mkdir(parents=True, exist_ok=True)
    (raiz_frontend / "src" / "pages").mkdir(parents=True, exist_ok=True)
    (raiz_frontend / "public").mkdir(parents=True, exist_ok=True)

    # index.html
    index_html = raiz_frontend / "index.html"
    index_html.write_text(
        f"""<!DOCTYPE html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{blueprint.get('nome', 'Projeto')}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""
    )
    arquivos.append(index_html)

    # main.jsx
    main_jsx = raiz_frontend / "src" / "main.jsx"
    main_jsx.write_text(
        """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""
    )
    arquivos.append(main_jsx)

    # App.jsx (placeholder)
    app_jsx = raiz_frontend / "src" / "App.jsx"
    objetivo = blueprint.get("objetivo_transformacao", "Projeto")
    app_jsx.write_text(
        f"""export default function App() {{
  return (
    <div style={{{{ padding: '2rem' }}}}>
      <h1>{objetivo}</h1>
      <p>Frontend gerado automaticamente. Customize este arquivo.</p>
    </div>
  )
}}
"""
    )
    arquivos.append(app_jsx)

    # index.css (vazio)
    css = raiz_frontend / "src" / "index.css"
    css.write_text("/* Adicione estilos aqui */\n")
    arquivos.append(css)

    # .gitignore
    gitignore = raiz_frontend / ".gitignore"
    gitignore.write_text("node_modules/\ndist/\n.env\n")
    arquivos.append(gitignore)

    return arquivos


def _criar_backend(
    raiz_backend: Path,
    slug: str,
    blueprint: dict[str, Any],
) -> list[Path]:
    """Estrutura do backend Node.js/Express."""
    arquivos = []

    # Diretórios
    (raiz_backend / "src" / "routes").mkdir(parents=True, exist_ok=True)
    (raiz_backend / "src" / "middleware").mkdir(parents=True, exist_ok=True)
    (raiz_backend / "src" / "models").mkdir(parents=True, exist_ok=True)

    # index.js
    index_js = raiz_backend / "src" / "index.js"
    index_js.write_text(
        """const express = require('express')
const cors = require('cors')

const app = express()
const PORT = process.env.PORT || 3000

app.use(cors())
app.use(express.json())

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() })
})

app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`)
})
"""
    )
    arquivos.append(index_js)

    # .env.example
    env_example = raiz_backend / ".env.example"
    env_example.write_text("PORT=3000\nNODE_ENV=development\n")
    arquivos.append(env_example)

    # .gitignore
    gitignore = raiz_backend / ".gitignore"
    gitignore.write_text("node_modules/\n.env\n*.log\n")
    arquivos.append(gitignore)

    return arquivos


def _criar_raiz(
    raiz: Path,
    slug: str,
    blueprint: dict[str, Any],
) -> list[Path]:
    """Arquivos na raiz do projeto."""
    arquivos = []

    # README.md
    readme = raiz / "README.md"
    readme.write_text(
        f"""# {blueprint.get('nome', 'Projeto')}

{blueprint.get('resumo', 'Descrição do projeto.')}

## Estrutura

- `frontend/` — React + Vite
- `backend/` — Node.js + Express

## Setup

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
npm install
npm start
```

## Gerado por

Plataforma de Engenharia de Projetos de IA
Motor: {blueprint.get('motor_elaboracao', 'desconhecido')}
"""
    )
    arquivos.append(readme)

    # .gitignore raiz
    gitignore = raiz / ".gitignore"
    gitignore.write_text("node_modules/\n.env\n*.log\n.DS_Store\n")
    arquivos.append(gitignore)

    return arquivos


def _pacote_json_frontend(
    slug: str,
    blueprint: dict[str, Any],
) -> dict[str, Any]:
    """Gera package.json do frontend."""
    return {
        "name": f"{slug}-frontend",
        "version": "0.0.1",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview",
            "test": "echo 'Adicione testes aqui'",
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


def _pacote_json_backend(
    slug: str,
    blueprint: dict[str, Any],
) -> dict[str, Any]:
    """Gera package.json do backend."""
    return {
        "name": f"{slug}-backend",
        "version": "0.0.1",
        "type": "commonjs",
        "main": "src/index.js",
        "scripts": {
            "start": "node src/index.js",
            "dev": "node --watch src/index.js",
            "test": "echo 'Adicione testes aqui'",
        },
        "dependencies": {
            "express": "^4.18.0",
            "cors": "^2.8.0",
        },
        "devDependencies": {},
    }
