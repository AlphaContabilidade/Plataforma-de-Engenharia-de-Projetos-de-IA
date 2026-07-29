---
name: exportar
description: Gera o `mkdocs.yml` do acervo AI-ENGINEERING-OS a partir do que existe em disco rodando `python -m ferramentas.exportar`, e valida o build com `mkdocs build --strict` apenas quando o `mkdocs` está instalado. Use quando o pedido for `/exportar`, "gerar o site", "exportar para MkDocs" ou "publicar o acervo".
---

# `/exportar`

Procedimento. A navegação é derivada **do disco, não do contrato**: volume declarado e não
materializado fica fora do site, porque item de menu sem página é promessa de conteúdo que
não existe.

**Rode de dentro de `AI-ENGINEERING-OS/`.**

## 1. Rodar

```bash
python -m ferramentas.exportar
```

O que acontece, na ordem:

1. Grava `mkdocs.yml` na raiz — cabeçalho fixo (tema `material`, `pymdownx.superfences` com
   a *custom fence* de Mermaid) mais a `nav` montada do disco: `00-INTRODUCAO` primeiro, em
   seguida os volumes materializados em ordem de id, e dentro de cada volume só as seções que
   **existem como arquivo**.
2. Imprime `ok: <caminho>/mkdocs.yml gerado com N pagina(s)`.
3. Procura o executável `mkdocs` no PATH.

## 2. Interpretar a saída — os três desfechos possíveis

| Saída | Exit | O que de fato aconteceu |
|---|---|---|
| `ok: ... gerado com N pagina(s)` + `ok: mkdocs build --strict validado com sucesso` | 0 | `mkdocs.yml` gerado **e** build validado |
| `ok: ... gerado com N pagina(s)` + `aviso: mkdocs nao encontrado, build nao validado` | 0 | **só o `mkdocs.yml` foi gerado.** O site **não** foi construído nem verificado |
| `ok: ... gerado ...` + `FALHA: mkdocs build --strict reprovou` | 1 | YAML gerado, build **reprovou** — o site não sai |

## 3. Sem `mkdocs` instalado, reporte a limitação — não afirme sucesso

O exit code é **0** no caso do `aviso:`. Isso é deliberado: gerar o `mkdocs.yml` é o trabalho
da ferramenta, e a ausência de uma dependência opcional não é falha dela. Mas **exit 0 aqui
não significa "site validado"**, e é exatamente aí que um relatório desonesto nasce.

Com o aviso na saída, escreva na resposta, com estas palavras ou equivalentes diretos:

> `mkdocs.yml` gerado com N páginas. **O build não foi validado**: `mkdocs` não está
> instalado neste ambiente. Não sei se o site constrói.

Proibido: "exportado com sucesso", "site gerado", "pronto para publicar", "deve construir
sem problemas". Você não olhou. Erro de digitação em tipo de Mermaid, link relativo que o
MkDocs resolve diferente do validador e seção fora da `nav` só aparecem **no build** — o
gate 1 não pega nada disso.

Se o usuário quiser a validação de verdade, ofereça `pip install mkdocs mkdocs-material` e
diga que é a única dependência externa do projeto (as `ferramentas/` usam apenas a biblioteca
padrão). **Não instale sem o usuário pedir.**

## 4. Build reprovado (exit 1)

O build roda `mkdocs build --strict` com um *config-file* temporário fora da raiz apontando
`docs_dir` para a raiz absoluta — o MkDocs recusa `docs_dir` igual à pasta do próprio config,
e aqui o acervo **é** a pasta de conteúdo. Se o build reprovar, a causa está no conteúdo ou
na `nav`, não nesse desvio de layout.

Cole a saída do `mkdocs`, identifique o arquivo apontado e corrija o **conteúdo**. Nunca
edite `mkdocs.yml` à mão: o cabeçalho do arquivo diz "gerado por `ferramentas/exportar.py` —
não edite a mão", e a próxima execução sobrescreve qualquer ajuste manual.

## 5. Reportar

Sempre: o comando, **a saída colada**, o número de páginas, e a frase explícita sobre o build
— validado, não validado por ausência de `mkdocs`, ou reprovado. Se um volume que você
esperava não apareceu, a causa é disco: confirme com `python -m ferramentas.status` que ele
tem seções (`presentes/esperadas`) e não só `_VOLUME.yml`.
