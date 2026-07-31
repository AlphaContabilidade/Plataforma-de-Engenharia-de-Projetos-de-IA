import json
import threading
from pathlib import Path
from urllib.request import Request, urlopen

import iniciar
from ferramentas.construtor_web import subir


RAIZ = Path(__file__).resolve().parents[2]


def requisitar(url: str, entrada: dict[str, object] | None = None) -> dict[str, object]:
    dados = None
    headers = {}
    if entrada is not None:
        dados = json.dumps(entrada, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    with urlopen(Request(url, data=dados, headers=headers), timeout=5) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


def test_diagnostico_confirma_clone_portatil():
    dado = iniciar.diagnostico()
    assert dado["python_compativel"] is True
    assert dado["interface_sem_dependencias"] is True
    assert dado["ia_obrigatoria"] is False
    assert all(dado["arquivos_essenciais"].values())


def test_instrucoes_de_fornecedores_apontam_para_contrato_universal():
    for caminho in (
        "CLAUDE.md",
        "CODEX.md",
        "GEMINI.md",
        ".github/copilot-instructions.md",
    ):
        texto = (RAIZ / caminho).read_text(encoding="utf-8")
        assert "AGENTS.md" in texto
        assert "PROTOCOLO-UNIVERSAL-DA-IA.md" in texto

    claude = (RAIZ / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Opus 5" not in claude
    assert "Fable 5" not in claude


def test_widget_se_apresenta_como_independente_de_fornecedor():
    html = (RAIZ / "chatgpt_app" / "widget.html").read_text(encoding="utf-8")
    assert "compatível com qualquer IA" in html
    assert "Claude, Codex, ChatGPT, Gemini ou outra IA" in html
    assert "dentro do ChatGPT" not in html


def test_servidor_universal_entrega_descoberta_e_plano():
    servidor = subir(0, fixa=True)
    thread = threading.Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    porta = servidor.server_address[1]
    base = f"http://127.0.0.1:{porta}"
    try:
        saude = requisitar(base + "/saude")
        assert saude["status"] == "ok"
        assert saude["dependencia_de_ia"] is False

        descoberta = requisitar(
            base + "/api/perguntas",
            {
                "ideia": "Sistema web para organizar estoque e vendas de pequenas empresas.",
                "tipo": "auto",
                "modo": "novo",
            },
        )
        assert descoberta["modo"] == "descoberta"
        assert descoberta["tipo_inferido"] == "web"

        plano = requisitar(
            base + "/api/planejar",
            {
                "ideia": "Sistema web para organizar estoque e vendas de pequenas empresas.",
                "publico": "gestores de pequenas empresas",
                "problema": "planilhas divergentes geram retrabalho e decisões atrasadas",
                "tipo": "web",
            },
        )
        assert plano["modo"] == "blueprint"
        assert "Plano de Solução" in plano["blueprint"]["markdown"]
    finally:
        servidor.shutdown()
        servidor.server_close()
        thread.join(timeout=5)
