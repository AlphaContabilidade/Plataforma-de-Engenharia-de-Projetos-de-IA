"""Teste de integração: Blueprint → Scaffold."""

from pathlib import Path
from tempfile import TemporaryDirectory

from ferramentas.gerador_scaffold import gerar_scaffold
from ferramentas.projetos import gerar_blueprint


class TestBlueprintParaScaffold:
    """Fluxo completo: descobre requisitos → gera scaffold."""

    def test_blueprint_real_gera_scaffold_valido(self):
        """Um Blueprint completo deve gerar scaffold executável."""
        with TemporaryDirectory() as tmpdir:
            # Entrada: descoberta de um projeto real
            entrada_descoberta = {
                "ideia": "App para controlar hábitos diários",
                "tipo": "web",
                "modo": "novo",
                "publico": "Pessoas que querem rastrear hábitos",
                "problema": "Falta de ferramenta simples para rastrear hábitos",
                "formato": "Web responsiva",
                "quantidade_usuarios": "1-100",
                "prioridade": "velocidade",
                "integracao": "Nenhuma no MVP",
                "dados_sensiveis": "Não",
                "prazo_estimado": "2-4 semanas",
            }

            # Fase 1: Gera Blueprint (Plano de Solução)
            blueprint = gerar_blueprint(entrada_descoberta)
            assert blueprint.nome != ""
            assert blueprint.mvp
            assert blueprint.arquitetura

            # Fase 2: Transforma Blueprint em scaffold
            destino = Path(tmpdir)
            scaffold = gerar_scaffold(blueprint.para_dict(), destino)

            assert scaffold.status == "criado"
            assert scaffold.diretorio_raiz.exists()
            assert len(scaffold.arquivos_criados) > 0

            # Verifica estrutura esperada
            raiz = scaffold.diretorio_raiz
            assert (raiz / "frontend" / "src" / "App.jsx").exists()
            assert (raiz / "backend" / "src" / "index.js").exists()
            assert (raiz / "README.md").exists()

            # Verifica que package.json tem dependências
            assert "react" in scaffold.pacote_json_frontend["dependencies"]
            assert "express" in scaffold.pacote_json_backend["dependencies"]

    def test_blueprint_com_dados_variados(self):
        """Diferentes Blueprints produzem scaffolds diferentes."""
        with TemporaryDirectory() as tmpdir1:
            with TemporaryDirectory() as tmpdir2:
                # Blueprint 1: API
                entrada1 = {
                    "ideia": "API de previsão do tempo",
                    "tipo": "web",
                    "modo": "novo",
                    "publico": "Desenvolvedores",
                    "problema": "Dados de tempo não padronizados",
                    "formato": "API REST",
                    "quantidade_usuarios": "100-1000",
                    "prioridade": "qualidade",
                    "integracao": "OpenWeatherMap",
                    "dados_sensiveis": "Não",
                    "prazo_estimado": "1-2 semanas",
                }

                # Blueprint 2: App de tarefas
                entrada2 = {
                    "ideia": "App de gerenciar tarefas do dia",
                    "tipo": "web",
                    "modo": "novo",
                    "publico": "Profissionais ocupados",
                    "problema": "Perda de produtividade",
                    "formato": "Web responsiva",
                    "quantidade_usuarios": "10-100",
                    "prioridade": "velocidade",
                    "integracao": "Nenhuma no MVP",
                    "dados_sensiveis": "Não",
                    "prazo_estimado": "2-4 semanas",
                }

                bp1 = gerar_blueprint(entrada1)
                bp2 = gerar_blueprint(entrada2)

                # Ambos geram scaffold válido
                s1 = gerar_scaffold(bp1.para_dict(), Path(tmpdir1))
                s2 = gerar_scaffold(bp2.para_dict(), Path(tmpdir2))

                assert s1.status == "criado"
                assert s2.status == "criado"

                # Ambos têm estrutura
                assert (s1.diretorio_raiz / "frontend").exists()
                assert (s2.diretorio_raiz / "frontend").exists()

                # Conteúdo dos READMEs preservam dados do Blueprint
                readme1 = (s1.diretorio_raiz / "README.md").read_text()
                readme2 = (s2.diretorio_raiz / "README.md").read_text()
                assert "AI-ENGINEERING-OS v1" in readme1
                assert "AI-ENGINEERING-OS v1" in readme2
                assert "React" in readme1
                assert "Express" in readme2
