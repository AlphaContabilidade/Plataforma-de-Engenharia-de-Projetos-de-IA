"""As lacunas de uma especificacao, e o que destrava cada uma.

Uma especificacao nao e um documento com secoes: e um **conjunto de lacunas**, e
cada lacuna e uma coisa que precisa estar decidida antes de alguem construir. Este
modulo declara esse conjunto e a condicao que torna cada lacuna relevante.

A distincao que sustenta o resto do motor esta em dois campos. `universal` marca a
lacuna que vale para qualquer software -- que problema resolve, quem usa, como se
sabe que funcionou. `plataformas` e `contextos` marcam a lacuna **condicional**:
ela so existe quando o contexto a torna relevante. Perguntar sobre loja de
aplicativos para algo que roda em navegador nao e rigor, e ruido, e ruido gasta a
paciencia que a proxima pergunta boa vai precisar.

O campo `porque` existe porque a pergunta sem motivo declarado nao se defende. Uma
pessoa entrevistada pergunta "por que isso importa?" e a resposta honesta nao pode
ser inventada na hora -- ela e parte do catalogo, escrita antes, e revisavel.

O que este modulo deliberadamente NAO faz: nao ordena, nao decide o que perguntar
e nao guarda resposta. Ordenar por valor informativo e parar quando nao vale mais
e assunto de `entrevista.py`; inferir plataforma e contexto do texto e assunto de
`deteccao.py`. A separacao e o que permite trocar a heuristica de ordenacao sem
mexer no conteudo das perguntas, e revisar o conteudo das perguntas sem risco de
mudar o comportamento do controle.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

PESO_MINIMO_VALIDO = 1
PESO_MAXIMO_VALIDO = 10


class Plataforma(StrEnum):
    """Onde o software roda. Destrava um bloco de lacunas e cala os outros.

    Quatro valores, e a escolha de quais quatro nao e arbitraria: cada um traz um
    conjunto de perguntas que os outros tres nao fazem sentido responder.

    - `WEB`: chega por navegador, hospedado por alguem.
    - `MOBILE`: instalado em aparelho pessoal, com rede intermitente e loja no meio.
    - `DESKTOP`: instalado na maquina da pessoa, com acesso a arquivo local.
    - `AUTOMACAO`: roda sem ninguem olhando, disparado por tempo ou evento.

    Um mesmo software pode ter mais de uma plataforma, e nesse caso os dois blocos
    de lacunas ficam ativos. O conjunto e uniao, nunca escolha exclusiva.
    """

    WEB = "WEB"
    MOBILE = "MOBILE"
    DESKTOP = "DESKTOP"
    AUTOMACAO = "AUTOMACAO"


class Contexto(StrEnum):
    """Caracteristica do dominio que torna um grupo de perguntas obrigatorio.

    Contexto nao e categoria de mercado: e gatilho de risco. `LOJA_PAGAMENTOS` nao
    significa "e uma loja", significa "dinheiro troca de maos, entao existe a
    pergunta do que acontece quando cobra duas vezes". `SAUDE` nao significa "e da
    area medica", significa "existe dado que nao pode vazar e alguem tem de dizer
    quem pode ver".

    Diferente de `Plataforma`, contexto nenhum e obrigatorio: um contador de
    visitas nao tem pagamento, nem dado de saude, nem multiusuario. Especificacao
    sem contexto e legitima; especificacao sem plataforma nao e, porque todo
    software roda em algum lugar.
    """

    LOJA_PAGAMENTOS = "LOJA_PAGAMENTOS"
    SAUDE = "SAUDE"
    DADO_PESSOAL = "DADO_PESSOAL"
    MULTIUSUARIO = "MULTIUSUARIO"
    TEMPO_REAL = "TEMPO_REAL"
    INTEGRACAO_EXTERNA = "INTEGRACAO_EXTERNA"


class CatalogoInvalido(ValueError):
    """Catalogo com id repetido, peso fora da faixa ou lacuna sem gatilho.

    Levanta em vez de reportar porque isso e erro de programa, nao ausencia de
    informacao do dominio. Id repetido faz duas perguntas diferentes compartilharem
    o mesmo balde de resposta: responder uma marcaria a outra como respondida, e a
    especificacao sairia afirmando ter decidido algo que ninguem decidiu.

    Peso fora de 1..10 quebra a comparacao com `peso_minimo` sem sinal nenhum: peso
    zero significa "nunca perguntar", que e diferente de "vale pouco", e peso vinte
    faria uma pergunta ultrapassar o topo da escala e mascarar as de peso 10.
    """


@dataclass(frozen=True, slots=True)
class Lacuna:
    """Uma coisa que precisa estar decidida, e a condicao que a torna relevante.

    Congelada porque o catalogo e conteudo revisado, nao estado mutavel: mudar uma
    pergunta e editar este arquivo e reexecutar os testes, nunca alterar o objeto
    em tempo de execucao a partir de uma resposta.

    Campos, e o que cada um decide:

    - `id`: identidade estavel usada em `responder` e na especificacao final. Muda
      de nome nunca, porque especificacao antiga guarda o id.
    - `pergunta`: o texto que a pessoa le. Uma pergunta, nao um grupo delas.
    - `porque`: por que essa pergunta importa. E o que o motor mostra quando a
      pessoa pergunta "por que isso?" -- e o que impede a pergunta inutil de
      sobreviver a uma revisao, porque justificativa vazia nao se escreve.
    - `peso`: valor informativo de 1 a 10. Nao e prioridade de projeto nem esforco
      de implementacao: e quanta incerteza a resposta remove.
    - `universal`: vale para qualquer software, sem gatilho.
    - `plataformas`: conjunto vazio significa toda plataforma. Nao-vazio significa
      que a lacuna so entra quando ao menos uma dessas plataformas esta confirmada.
    - `contextos`: conjunto vazio significa que nenhum contexto e exigido.
      Nao-vazio significa que a lacuna so entra quando ao menos um deles esta
      confirmado.
    - `opcoes`: vazio significa resposta livre. Nao-vazio nao restringe a resposta
      -- oferece caminho. Restringir a resposta as opcoes conhecidas produziria
      especificacao que descreve o catalogo em vez do software.
    """

    id: str
    pergunta: str
    porque: str
    peso: int
    universal: bool
    plataformas: frozenset[Plataforma] = frozenset()
    contextos: frozenset[Contexto] = frozenset()
    opcoes: tuple[str, ...] = ()

    def relevante_para(
        self, plataformas: frozenset[Plataforma], contextos: frozenset[Contexto]
    ) -> bool:
        """A lacuna faz sentido para esta plataforma e este contexto?

        Universal e sempre relevante. Condicional exige as duas portas abertas: a
        de plataforma e a de contexto. Conjunto vazio e porta aberta -- ausencia de
        exigencia, e nao exigencia impossivel de satisfazer.

        A conjuncao entre as duas portas e deliberada. Uma lacuna que exige
        `MOBILE` e `LOJA_PAGAMENTOS` juntos e a pergunta de pagamento dentro do
        aplicativo, e ela nao faz sentido em nenhum dos dois casos isolados.
        """
        if self.universal:
            return True
        porta_plataforma = not self.plataformas or bool(self.plataformas & plataformas)
        porta_contexto = not self.contextos or bool(self.contextos & contextos)
        return porta_plataforma and porta_contexto


CATALOGO: tuple[Lacuna, ...] = (
    # --- Universais: valem para qualquer software, e a sua ausencia nunca e aceitavel.
    Lacuna(
        id="problema",
        pergunta="Que problema isso resolve hoje, e para quem ele doi o suficiente?",
        porque=(
            "Sem o problema declarado nao existe criterio para escolher entre duas "
            "solucoes, nem para saber se alguma serviu. Toda decisao seguinte se "
            "apoia nesta, e uma especificacao que a deixa aberta nao e vaga: e "
            "impossivel de avaliar."
        ),
        peso=10,
        universal=True,
    ),
    Lacuna(
        id="onde_roda",
        pergunta="Onde isso roda: navegador, aparelho de mao, maquina da pessoa, ou sozinho?",
        porque=(
            "A plataforma destrava um bloco inteiro de perguntas e cala os outros "
            "tres. Ela e a unica lacuna universal cuja resposta muda quais outras "
            "lacunas existem, e por isso ficar sem ela custa mais do que uma "
            "resposta faltando."
        ),
        peso=10,
        universal=True,
        opcoes=("WEB", "MOBILE", "DESKTOP", "AUTOMACAO"),
    ),
    Lacuna(
        id="usuario",
        pergunta="Quem usa isso no dia a dia, e quantas vezes por semana?",
        porque=(
            "Publico e frequencia mudam a construcao mais do que qualquer escolha "
            "tecnica. Algo usado tres vezes por dia por uma pessoa treinada e algo "
            "usado uma vez por mes por quem nunca viu a tela sao dois softwares "
            "diferentes com a mesma descricao."
        ),
        peso=9,
        universal=True,
    ),
    Lacuna(
        id="capacidade_nova",
        pergunta="O que a pessoa consegue fazer no dia seguinte a entrega que hoje nao consegue?",
        porque=(
            "Esta e a pergunta que separa software de reorganizacao de tela. Se a "
            "resposta descreve o que ja e feito, so mais bonito, o valor esperado "
            "e estetico e o orcamento devia saber disso antes de comecar."
        ),
        peso=9,
        universal=True,
    ),
    Lacuna(
        id="sucesso",
        pergunta="Como se sabe, com um numero, que funcionou?",
        porque=(
            "Sucesso sem numero e sucesso decidido depois, por quem tiver mais "
            "vontade de declarar vitoria. O numero nao precisa ser sofisticado -- "
            "precisa existir antes de a construcao comecar, porque depois ele vira "
            "descricao do que saiu."
        ),
        peso=8,
        universal=True,
    ),
    Lacuna(
        id="fora_de_escopo",
        pergunta="O que fica de fora desta primeira versao, mesmo sendo desejavel?",
        porque=(
            "Escopo declarado por exclusao e a unica forma de escopo que se defende "
            "sob pressao. Sem a lista do que fica fora, tudo o que alguem lembrar "
            "no meio do caminho parece ter estado dentro desde o inicio."
        ),
        peso=7,
        universal=True,
    ),
    # --- WEB
    Lacuna(
        id="web_autenticacao",
        pergunta="Como a pessoa entra: senha propria, conta de terceiro, ou sem login nenhum?",
        porque=(
            "Autenticacao decide o modelo de dados, a tela inicial e a superficie de "
            "ataque. Adiciona-la depois e reescrever o caminho de entrada de todas "
            "as telas ja construidas."
        ),
        peso=7,
        universal=False,
        plataformas=frozenset({Plataforma.WEB}),
        opcoes=("senha propria", "conta de terceiro", "sem login"),
    ),
    Lacuna(
        id="web_hospedagem",
        pergunta="Quem hospeda, e quem paga a conta da hospedagem todo mes?",
        porque=(
            "Hospedagem e a unica parte de um software web que continua custando "
            "depois de pronta. Projeto entregue sem dono da conta fica no ar ate o "
            "cartao de alguem recusar, e ninguem sabe de quem era."
        ),
        peso=6,
        universal=False,
        plataformas=frozenset({Plataforma.WEB}),
    ),
    Lacuna(
        id="web_navegador",
        pergunta="Qual navegador precisa funcionar, e qual versao minima?",
        porque=(
            "A resposta define o que se pode usar e o que precisa de alternativa. "
            "Descobrir na entrega que a maquina do balcao roda uma versao antiga "
            "transforma um detalhe em retrabalho de interface."
        ),
        peso=5,
        universal=False,
        plataformas=frozenset({Plataforma.WEB}),
    ),
    Lacuna(
        id="web_idioma",
        pergunta="A primeira versao precisa de mais de um idioma?",
        porque=(
            "Quase sempre a resposta e nao, e quando e sim isso aparece sem ser "
            "perguntado. Peso baixo de proposito: e uma pergunta cuja resposta "
            "provavel nao muda nada, e ela existe no catalogo para sair na "
            "especificacao como decisao aberta em vez de gastar um turno."
        ),
        peso=3,
        universal=False,
        plataformas=frozenset({Plataforma.WEB}),
    ),
    # --- MOBILE
    Lacuna(
        id="mobile_offline",
        pergunta="O que precisa continuar funcionando quando o aparelho esta sem rede?",
        porque=(
            "Funcionar sem rede nao e melhoria incremental: e decisao de arquitetura "
            "sobre onde o dado mora e como os dois lados voltam a concordar quando a "
            "rede retorna. Descoberta tardia, ela reescreve a camada de dados inteira."
        ),
        peso=8,
        universal=False,
        plataformas=frozenset({Plataforma.MOBILE}),
    ),
    Lacuna(
        id="mobile_loja",
        pergunta="Vai para a loja de aplicativos, ou fica instalado so nos aparelhos da equipe?",
        porque=(
            "Loja significa revisao por terceiro, prazo que nao se controla e regras "
            "que mudam sem aviso. Distribuicao interna nao tem nada disso e tem "
            "outro problema: alguem precisa instalar em cada aparelho."
        ),
        peso=7,
        universal=False,
        plataformas=frozenset({Plataforma.MOBILE}),
        opcoes=("loja publica", "distribuicao interna"),
    ),
    Lacuna(
        id="mobile_permissao",
        pergunta="Que recurso do aparelho isso usa: camera, localizacao, contatos, arquivos?",
        porque=(
            "Cada permissao e uma caixa de dialogo que a pessoa pode negar, e o "
            "software tem de continuar util depois do nao. Permissao pedida sem "
            "motivo visivel e o motivo mais comum de desinstalacao no primeiro uso."
        ),
        peso=6,
        universal=False,
        plataformas=frozenset({Plataforma.MOBILE}),
    ),
    Lacuna(
        id="mobile_notificacao",
        pergunta="O aplicativo precisa avisar a pessoa quando ela nao esta com ele aberto?",
        porque=(
            "Notificacao traz infraestrutura propria e uma decisao de produto sobre "
            "o que merece interromper alguem. Decidir isso depois costuma virar "
            "aviso para tudo, que e o mesmo que aviso para nada."
        ),
        peso=5,
        universal=False,
        plataformas=frozenset({Plataforma.MOBILE}),
    ),
    Lacuna(
        id="mobile_tablet",
        pergunta="Precisa ficar bom em tela de tablet, ou so em telefone?",
        porque=(
            "Peso baixo porque a resposta raramente muda a primeira versao: layout "
            "que funciona em telefone quase sempre e aceitavel em tablet. Fica no "
            "catalogo para constar como decisao aberta, nao para ocupar um turno."
        ),
        peso=3,
        universal=False,
        plataformas=frozenset({Plataforma.MOBILE}),
    ),
    # --- DESKTOP
    Lacuna(
        id="desktop_sistema",
        pergunta="Em qual sistema operacional, e em quais versoes dele?",
        porque=(
            "Sistema operacional decide empacotamento, assinatura de codigo e metade "
            "das bibliotecas disponiveis. Suportar tres em vez de um nao e tres "
            "vezes o trabalho de interface, e sim tres canais de instalacao."
        ),
        peso=7,
        universal=False,
        plataformas=frozenset({Plataforma.DESKTOP}),
    ),
    Lacuna(
        id="desktop_instalacao",
        pergunta="Como o programa chega na maquina, e como ele se atualiza depois?",
        porque=(
            "Atualizacao e o problema real do software instalado. Sem caminho de "
            "atualizacao definido, cada correcao depende de alguem visitar cada "
            "maquina, e a frota se separa em versoes que ninguem consegue mapear."
        ),
        peso=6,
        universal=False,
        plataformas=frozenset({Plataforma.DESKTOP}),
    ),
    Lacuna(
        id="desktop_arquivo_local",
        pergunta="Ele le ou escreve arquivo na maquina da pessoa? Em qual pasta?",
        porque=(
            "Acesso a arquivo local muda permissao, teste e o que acontece quando a "
            "pasta nao existe ou esta em uso. E a fonte mais comum de erro que so "
            "aparece na maquina de quem usa, nunca na de quem constroi."
        ),
        peso=5,
        universal=False,
        plataformas=frozenset({Plataforma.DESKTOP}),
    ),
    Lacuna(
        id="desktop_aparencia",
        pergunta="Precisa acompanhar o tema claro e escuro do sistema?",
        porque=(
            "Peso dois: agradavel, praticamente nunca decisivo, e barato de adicionar "
            "depois. Existe no catalogo para nao se perder e para nunca competir com "
            "uma pergunta que muda o que sera construido."
        ),
        peso=2,
        universal=False,
        plataformas=frozenset({Plataforma.DESKTOP}),
    ),
    # --- AUTOMACAO
    Lacuna(
        id="auto_disparo",
        pergunta="O que dispara a execucao: horario, chegada de arquivo, ou alguem apertando um botao?",
        porque=(
            "O gatilho e a especificacao de uma automacao. Horario fixo, evento e "
            "acionamento manual produzem tres desenhos diferentes, e o unico erro "
            "que nao tem conserto barato e descobrir o gatilho errado no fim."
        ),
        peso=9,
        universal=False,
        plataformas=frozenset({Plataforma.AUTOMACAO}),
        opcoes=("horario fixo", "chegada de arquivo", "acionamento manual"),
    ),
    Lacuna(
        id="auto_falha_no_meio",
        pergunta="Se falhar na metade, o que fica pela metade e o que precisa ser desfeito?",
        porque=(
            "Automacao que roda sem ninguem olhando falha sem ninguem olhando. Sem "
            "resposta aqui, a primeira falha parcial deixa estado inconsistente que "
            "alguem descobre dias depois, ja sem saber o que foi feito."
        ),
        peso=8,
        universal=False,
        plataformas=frozenset({Plataforma.AUTOMACAO}),
    ),
    Lacuna(
        id="auto_frequencia",
        pergunta="Com que frequencia roda, e quanto tempo pode levar sem incomodar ninguem?",
        porque=(
            "Frequencia e duracao aceitavel juntas definem se duas execucoes podem "
            "se sobrepor. Duas execucoes simultaneas de uma rotina escrita para uma "
            "e a forma mais silenciosa de duplicar trabalho."
        ),
        peso=6,
        universal=False,
        plataformas=frozenset({Plataforma.AUTOMACAO}),
    ),
    Lacuna(
        id="auto_saida_formato",
        pergunta="O resultado sai em planilha, em texto, ou fica so no banco?",
        porque=(
            "Peso baixo porque converter formato de saida e trabalho pequeno e "
            "isolado. A pergunta existe para ficar registrada como decisao aberta e "
            "nao para disputar turno com o gatilho ou com a falha parcial."
        ),
        peso=3,
        universal=False,
        plataformas=frozenset({Plataforma.AUTOMACAO}),
    ),
    # --- LOJA_PAGAMENTOS
    Lacuna(
        id="pag_cobranca_dupla",
        pergunta="Se a mesma compra for cobrada duas vezes, o que o sistema faz e como alguem descobre?",
        porque=(
            "Cobranca em duplicidade e o defeito que custa dinheiro e confianca ao "
            "mesmo tempo, e ele acontece por repeticao de pedido, nao por bug "
            "exotico. Quem nao responde isso no inicio descobre em reclamacao."
        ),
        peso=9,
        universal=False,
        contextos=frozenset({Contexto.LOJA_PAGAMENTOS}),
    ),
    Lacuna(
        id="pag_provedor",
        pergunta="Qual provedor de pagamento, e ele ja esta contratado e aprovado?",
        porque=(
            "O provedor decide o fluxo de tela, os dados que se pode guardar e o "
            "prazo de aprovacao cadastral, que costuma ser maior que o prazo de "
            "construcao. Escolher depois joga esse prazo para dentro da entrega."
        ),
        peso=8,
        universal=False,
        contextos=frozenset({Contexto.LOJA_PAGAMENTOS}),
    ),
    Lacuna(
        id="pag_estorno",
        pergunta="Quem pode desfazer uma cobranca, e ate quantos dias depois?",
        porque=(
            "Desfazer cobranca e a operacao mais sensivel de um sistema de "
            "pagamento, e ela precisa de autorizacao e registro. Sem regra "
            "declarada, ou ninguem consegue desfazer, ou qualquer um consegue."
        ),
        peso=7,
        universal=False,
        contextos=frozenset({Contexto.LOJA_PAGAMENTOS}),
    ),
    # --- SAUDE
    Lacuna(
        id="saude_dado_sensivel",
        pergunta="Qual dado de saude fica guardado, e qual deles daria para nao guardar?",
        porque=(
            "Dado sensivel que nao existe nao vaza. A pergunta e primeiro sobre o "
            "que se pode deixar de guardar e so depois sobre como proteger o que "
            "sobrou -- a ordem inversa produz cofre cheio de coisa desnecessaria."
        ),
        peso=9,
        universal=False,
        contextos=frozenset({Contexto.SAUDE}),
    ),
    Lacuna(
        id="saude_quem_ve",
        pergunta="Quem pode ver o registro de uma pessoa atendida, e como isso se comprova depois?",
        porque=(
            "Em dado de saude nao basta restringir o acesso: precisa ser possivel "
            "mostrar quem acessou o que e quando. Registro de acesso adicionado "
            "depois nao cobre o periodo anterior, que e justamente o auditado."
        ),
        peso=8,
        universal=False,
        contextos=frozenset({Contexto.SAUDE}),
    ),
    Lacuna(
        id="saude_retencao",
        pergunta="Quanto tempo o registro fica guardado, e o que acontece quando esse prazo vence?",
        porque=(
            "Prazo de guarda em saude vem de norma, nao de preferencia, e costuma "
            "ser longo. Ele decide custo de armazenamento, formato de arquivamento "
            "e o que se pode apagar quando alguem pede."
        ),
        peso=7,
        universal=False,
        contextos=frozenset({Contexto.SAUDE}),
    ),
    # --- DADO_PESSOAL
    Lacuna(
        id="pessoal_base_legal",
        pergunta="Com que justificativa cada dado pessoal e coletado, e onde a pessoa le isso?",
        porque=(
            "Coletar dado pessoal exige motivo declarado e visivel para quem "
            "entrega o dado. Sem isso, o cadastro cresce por conveniencia de tela e "
            "ninguem sabe dizer por que um campo existe."
        ),
        peso=8,
        universal=False,
        contextos=frozenset({Contexto.DADO_PESSOAL}),
    ),
    Lacuna(
        id="pessoal_exclusao",
        pergunta="Quando a pessoa pedir para ser apagada, o que exatamente e apagado?",
        porque=(
            "Apagar de verdade encosta em copia de seguranca, registro de acesso e "
            "historico agregado. Responder isso no inicio e desenho; responder "
            "depois do primeiro pedido e arqueologia sob prazo."
        ),
        peso=7,
        universal=False,
        contextos=frozenset({Contexto.DADO_PESSOAL}),
    ),
    # --- MULTIUSUARIO
    Lacuna(
        id="multi_papeis",
        pergunta="Que papeis existem, e quem cria o primeiro deles?",
        porque=(
            "Papel e a estrutura que todo o resto do controle de acesso assume. E a "
            "pergunta do primeiro papel nao e detalhe: sistema sem resposta para "
            "ela nasce precisando de alguem editando o banco na mao."
        ),
        peso=8,
        universal=False,
        contextos=frozenset({Contexto.MULTIUSUARIO}),
    ),
    Lacuna(
        id="multi_visibilidade",
        pergunta="O que cada papel ve, e o que ele nao pode ver de jeito nenhum?",
        porque=(
            "A metade proibida da resposta e a que importa. Visibilidade descrita "
            "so pelo que se pode ver deixa o resto por conta da implementacao, e a "
            "implementacao decide por omissao -- costuma mostrar."
        ),
        peso=7,
        universal=False,
        contextos=frozenset({Contexto.MULTIUSUARIO}),
    ),
    # --- TEMPO_REAL
    Lacuna(
        id="real_latencia",
        pergunta="Em quantos segundos a informacao precisa aparecer do outro lado?",
        porque=(
            "Tempo real sem numero e adjetivo. Dois segundos e trezentos "
            "milissegundos levam a arquiteturas diferentes, e a diferenca de custo "
            "entre elas nao e pequena."
        ),
        peso=7,
        universal=False,
        contextos=frozenset({Contexto.TEMPO_REAL}),
    ),
    Lacuna(
        id="real_atraso",
        pergunta="Quando atrasar mais que isso, a pessoa ve dado velho marcado como velho, ou nao ve nada?",
        porque=(
            "O comportamento sob atraso e o que define se o sistema e confiavel na "
            "hora ruim. Dado velho apresentado como atual e pior que ausencia de "
            "dado, porque a pessoa age sobre ele sem desconfiar."
        ),
        peso=6,
        universal=False,
        contextos=frozenset({Contexto.TEMPO_REAL}),
    ),
    # --- INTEGRACAO_EXTERNA
    Lacuna(
        id="externo_qual_sistema",
        pergunta="Com qual sistema de fora isso conversa, e quem controla esse sistema?",
        porque=(
            "Integracao com sistema de terceiro herda o calendario e os limites "
            "dele. Saber quem controla e o que decide se uma mudanca de contrato e "
            "negociavel ou apenas comunicada."
        ),
        peso=8,
        universal=False,
        contextos=frozenset({Contexto.INTEGRACAO_EXTERNA}),
    ),
    Lacuna(
        id="externo_queda",
        pergunta="Quando esse sistema estiver fora do ar, o que acontece com quem esta usando?",
        porque=(
            "O sistema de fora vai cair, e a pergunta e apenas o que se faz "
            "enquanto isso: fila, aviso, ou bloqueio. Sem resposta, o padrao e o "
            "erro cru na tela e a pessoa tentando de novo sem saber se funcionou."
        ),
        peso=7,
        universal=False,
        contextos=frozenset({Contexto.INTEGRACAO_EXTERNA}),
    ),
)


def validar_catalogo(catalogo: Iterable[Lacuna] = CATALOGO) -> tuple[Lacuna, ...]:
    """Reprova catalogo malformado e devolve a tupla validada, na ordem recebida.

    Devolve o proprio catalogo para que o chamador possa escrever
    `self._catalogo = validar_catalogo(catalogo)` e ficar com a garantia junto do
    dado, sem uma segunda linha que alguem possa esquecer de escrever.

    Quatro verificacoes, cada uma correspondendo a um defeito que ja se paga na
    primeira execucao:

    1. **Id vazio ou repetido.** Id e a chave da resposta; repetido, duas perguntas
       dividem um balde e uma delas se declara respondida sem ter sido feita.
    2. **Peso fora de 1..10.** Fora da faixa, a comparacao com `peso_minimo` deixa
       de significar o que a documentacao diz que significa.
    3. **Pergunta ou motivo em branco.** Pergunta vazia chega a pessoa como turno
       gasto sem conteudo; motivo vazio deixa o motor sem resposta para "por que
       isso importa?", que e a unica defesa da pergunta.
    4. **Lacuna nao universal sem gatilho nenhum.** Sem plataforma e sem contexto,
       ela e relevante sempre -- ou seja, e universal com a marca errada. O erro e
       silencioso e some no meio de um catalogo grande, entao ele levanta aqui.
    """
    lacunas = tuple(catalogo)
    vistos: set[str] = set()
    for lacuna in lacunas:
        identificador = lacuna.id.strip()
        if not identificador:
            raise CatalogoInvalido(
                "lacuna com id vazio: o id e a chave da resposta, e resposta sem "
                "chave nao volta para a especificacao"
            )
        if identificador in vistos:
            raise CatalogoInvalido(
                f"id duplicado {identificador!r}: duas lacunas dividiriam o mesmo "
                "balde de resposta, e responder uma marcaria a outra como respondida"
            )
        vistos.add(identificador)
        if not PESO_MINIMO_VALIDO <= lacuna.peso <= PESO_MAXIMO_VALIDO:
            raise CatalogoInvalido(
                f"peso {lacuna.peso} de {identificador!r} fora de "
                f"{PESO_MINIMO_VALIDO}..{PESO_MAXIMO_VALIDO}: fora da faixa a "
                "comparacao com o peso minimo deixa de significar valor informativo"
            )
        if not lacuna.pergunta.strip():
            raise CatalogoInvalido(f"lacuna {identificador!r} sem pergunta")
        if not lacuna.porque.strip():
            raise CatalogoInvalido(
                f"lacuna {identificador!r} sem motivo declarado: pergunta que nao "
                "se justifica por escrito nao sobrevive a uma revisao honesta"
            )
        if not lacuna.universal and not lacuna.plataformas and not lacuna.contextos:
            raise CatalogoInvalido(
                f"lacuna {identificador!r} nao e universal e nao tem gatilho: sem "
                "plataforma e sem contexto ela e relevante sempre, o que e ser "
                "universal com a marca errada"
            )
    return lacunas


def lacunas_ativas(
    plataformas: Iterable[Plataforma],
    contextos: Iterable[Contexto],
    *,
    catalogo: Iterable[Lacuna] = CATALOGO,
) -> tuple[Lacuna, ...]:
    """As universais mais as que esta plataforma e este contexto destravam.

    Ordem estavel: a do catalogo, sem reordenacao por peso. Ordenar por valor
    informativo e decisao do controle, e faze-la aqui esconderia a politica de
    priorizacao dentro de uma funcao cujo nome promete apenas filtrar.

    Pergunta que nao faz sentido **nao entra**. Nao entra desabilitada, nao entra
    marcada, nao entra no fim da lista: simplesmente nao existe para esta
    entrevista. Um formulario que mostra quarenta campos e desabilita trinta e
    dois ensina a pessoa que o instrumento nao entende o caso dela, e a partir
    dali as respostas pioram.
    """
    p = frozenset(plataformas)
    c = frozenset(contextos)
    return tuple(lacuna for lacuna in catalogo if lacuna.relevante_para(p, c))
