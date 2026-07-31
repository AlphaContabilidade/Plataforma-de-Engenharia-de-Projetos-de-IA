"""Preparador de Deploy — pronto para qualquer plataforma.

Gera configs para:
- Vercel (Next.js, SPA)
- GitHub Pages (static)
- Heroku (dynos)
- Docker (container)
- Railway (moderna)
- Render (moderna)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ConfigDeploy:
    """Configuracao de deploy pronta."""

    plataforma: str  # "vercel", "github-pages", "heroku", "docker", etc
    arquivos_criados: list[Path]
    instrucoes: str
    status: str  # "pronto", "incompleto"


def criar_dockerfile(projeto_dir: Path) -> str:
    """Gera Dockerfile para containerizar."""
    return '''FROM node:18-alpine

WORKDIR /app

# Copia ambos os lados
COPY backend/package*.json ./backend/
COPY frontend/package*.json ./frontend/

# Instala dependencias
RUN cd backend && npm ci && cd ..
RUN cd frontend && npm ci && cd ..

COPY backend ./backend
COPY frontend ./frontend

# Build frontend
RUN cd frontend && npm run build && cd ..

EXPOSE 3000

CMD ["node", "backend/src/index.js"]
'''


def criar_vercelrc(projeto_dir: Path) -> str:
    """Gera vercel.json para deploy no Vercel."""
    return '''{
  "builds": [
    {
      "src": "frontend",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    },
    {
      "src": "backend/src/index.js",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "backend/src/index.js"
    },
    {
      "src": "/(.*)",
      "dest": "frontend/dist/index.html"
    }
  ]
}
'''


def criar_github_workflow(projeto_dir: Path) -> str:
    """Gera GitHub Actions para CI/CD."""
    return '''name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install frontend
        run: cd frontend && npm ci && cd ..

      - name: Build frontend
        run: cd frontend && npm run build && cd ..

      - name: Deploy to Vercel
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        run: npx vercel --prod --token $VERCEL_TOKEN
'''


def criar_procfile(projeto_dir: Path) -> str:
    """Gera Procfile para Heroku."""
    return '''web: node backend/src/index.js
'''


def criar_env_prod(projeto_dir: Path) -> str:
    """Gera .env para producao."""
    return '''# Production environment
NODE_ENV=production
PORT=3000

# Backend
DATABASE_URL=
API_URL=https://seu-dominio.com/api

# Frontend (build-time)
VITE_API_URL=https://seu-dominio.com/api
'''


def preparar_deploy(
    projeto_dir: Path,
    plataforma: str = "vercel",
) -> ConfigDeploy:
    """Prepara projeto para deploy em uma plataforma.

    Args:
        projeto_dir: Raiz do projeto gerado
        plataforma: "vercel", "github-pages", "heroku", "docker", etc

    Returns:
        ConfigDeploy com arquivos e instrucoes
    """
    arquivos = []

    if plataforma == "docker":
        dockerfile = projeto_dir / "Dockerfile"
        dockerfile.write_text(criar_dockerfile(projeto_dir))
        arquivos.append(dockerfile)

        instrucoes = """
DOCKER:
1. Build image:
   docker build -t meu-app .

2. Run container:
   docker run -p 3000:3000 meu-app

3. Push para Docker Hub:
   docker tag meu-app seu-usuario/meu-app:latest
   docker push seu-usuario/meu-app:latest
"""

    elif plataforma == "vercel":
        vercelrc = projeto_dir / "vercel.json"
        vercelrc.write_text(criar_vercelrc(projeto_dir))
        arquivos.append(vercelrc)

        instrucoes = """
VERCEL:
1. Instale Vercel CLI:
   npm install -g vercel

2. Deploy:
   vercel --prod

3. Configure no dashboard:
   - Conecte GitHub repo
   - Defina env vars em Settings
   - Deploy automatico a cada push
"""

    elif plataforma == "heroku":
        procfile = projeto_dir / "Procfile"
        procfile.write_text(criar_procfile(projeto_dir))
        arquivos.append(procfile)

        instrucoes = """
HEROKU:
1. Instale Heroku CLI:
   npm install -g heroku

2. Login:
   heroku login

3. Crie app:
   heroku create seu-app-name

4. Deploy:
   git push heroku main

5. Logs:
   heroku logs --tail
"""

    elif plataforma == "github-pages":
        # Frontend static
        instrucoes = """
GITHUB PAGES:
1. Vai para frontend/
2. Edite vite.config.js:
   export default {
     base: '/seu-repo/',
     ...
   }

3. Build:
   npm run build

4. Commit e push dist/ (ou use gh-pages branch)

5. GitHub Settings → Pages → deploy from gh-pages
"""

    else:
        instrucoes = f"Plataforma '{plataforma}' nao implementada."

    env_prod = projeto_dir / ".env.production"
    env_prod.write_text(criar_env_prod(projeto_dir))
    arquivos.append(env_prod)

    return ConfigDeploy(
        plataforma=plataforma,
        arquivos_criados=arquivos,
        instrucoes=instrucoes.strip(),
        status="pronto",
    )


def listar_opcoes_deploy() -> dict[str, str]:
    """Lista todas as opcoes de deploy disponíveis."""
    return {
        "vercel": "Vercel (React SPA) - gratis, mais rapido",
        "heroku": "Heroku (Node.js + React) - $7/mes",
        "docker": "Docker + seu servidor - controle total",
        "github-pages": "GitHub Pages (static frontend) - gratis",
        "railway": "Railway (moderno, node-ready) - $5/mes",
        "render": "Render (substituiu Heroku) - $7/mes",
    }
