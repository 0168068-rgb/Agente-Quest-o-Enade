# -*- coding: utf-8 -*-
"""
Batch TG 3: Disciplinas 8 a 11 (Provas TG 2026-4 - UAs Específicas do Tema Gerador e Contextualização ENADE > 7 linhas)
"""
from generate_full_batch import create_exam

# 8. Infraestrutura e Serviços de TI (UAs 1, 3)
create_exam(
    "Infraestrutura e Serviços de TI", "Infraestrutura e Serviços de TI", "AD Infraestrutura e serviços de TI", "1; 3",
    [
        {
            "ua": "01", "obj": 1, "grau": "MÉDIA", "kw": "Resolução de Nomes com Servidores DNS Recursivos e Autoritativos",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em uma rede corporativa com 500 computadores conectados, a resolução de nomes de domínio da internet (como `www.google.com` ou `portal.empresa.com.br`) é realizada através de servidores DNS internos configurados nas propriedades de rede dos clientes.\n\nO servidor DNS local consulta a árvore hierárquica global do DNS para traduzir a URL amigável em um endereço IP numérico de 32 bits ou 128 bits.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta a função de um Servidor DNS Autoritativo na hierarquia do serviço DNS:",
            "opt_a": "Manter o banco de dados original contendo os registros de recursos oficiais de uma zona de domínio específica.", "opt_b": "Gerar endereços IP dinâmicos para computadores recém-conectados na rede local.", "opt_c": "Bloquear a execução de vírus no sistema operacional dos computadores.", "opt_d": "Executar o roteamento de pacotes entre VLANs distintas.",
            "feedback": "A resposta certa é Manter o banco de dados original contendo os registros de recursos oficiais de uma zona de domínio específica.\nComentário: Servidores autoritativos possuem a palavra final sobre o mapa de registros de um domínio sob sua responsabilidade (sua zona DNS).\nFonte: Infraestrutura e Serviços de TI, UA 1."
        },
        {
            "ua": "01", "obj": 2, "grau": "MÉDIA", "kw": "Consultas DNS Iterativas e Zonas Foward/Reverse (PTR)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Durante o diagnóstico de um problema de segurança no servidor de e-mail corporativo, o administrador de sistemas precisa identificar qual nome de domínio está associado ao endereço IP `200.180.40.10` registrado nos logs de tentativa de acesso.\n\nPara traduzir um endereço IP numérico de volta para o nome de domínio textual correspondente, o serviço DNS consulta a **Zona de Pesquisa Reversa** (Reverse Lookup Zone).",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o tipo de registro de recurso DNS utilizado exclusivamente em Zonas de Pesquisa Reversa para mapear um IP a um nome de domínio:",
            "opt_a": "Registro PTR (Pointer Record).", "opt_b": "Registro A (Address Record).", "opt_c": "Registro CNAME (Canonical Name).", "opt_d": "Registro MX (Mail Exchanger).",
            "feedback": "A resposta certa é Registro PTR (Pointer Record).\nComentário: O registro PTR realiza a resolução de nome reversa (IP -> Nome de Domínio), essencial para validação de servidores de e-mail e auditorias.\nFonte: Infraestrutura e Serviços de TI, UA 1."
        },
        {
            "ua": "03", "obj": 1, "grau": "DIFÍCIL", "kw": "Protocolo DHCP e o Processo DORA (Discover, Offer, Request, Acknowledge)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Quando um notebook corporativo é ligado na tomada de rede da sala de reuniões da empresa, sua placa de rede emite mensagens para obter automaticamente um endereço IP válido, máscara de sub-rede, gateway padrão e IPs dos servidores DNS.\n\nEsse processo de negociação de concessão de IP (Lease) entre o cliente e o servidor DHCP ocorre em quatro etapas sequenciais conhecidas pela sigla **DORA**.",
            "afirmativas": "Com base nas quatro etapas do processo DORA do protocolo DHCP, analise as afirmativas:\nI. A etapa `Discover` é emitida pelo cliente via pacote Broadcast em busca de qualquer servidor DHCP disponível na rede local.\nII. A etapa `Offer` é enviada pelo servidor DHCP oferecendo um endereço IP disponível e as opções de rede ao cliente.\nIII. A etapa `Acknowledge (ACK)` confirma a concessão final do IP e grava o tempo de lease no cliente e no servidor.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I, II e III.", "opt_b": "I e II, apenas.", "opt_c": "I e III, apenas.", "opt_d": "II e III, apenas.",
            "feedback": "A resposta certa é I, II e III.\nComentário: Todas as afirmativas são verdadeiras. Elas descrevem com precisão a sequência DORA do DHCP: Discover, Offer, Request e Acknowledge.\nFonte: Infraestrutura e Serviços de TI, UA 3."
        },
        {
            "ua": "03", "obj": 2, "grau": "DIFÍCIL", "kw": "Agente de Relay DHCP (DHCP Relay / ip helper-address) em Múltiplas VLANs",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Uma empresa possui um único servidor DHCP centralizado na VLAN 100 de Gerenciamento, mas deseja fornecer endereços IP dinâmicos para computadores localizados em outras 10 VLANs distintas distribuídas nos switches de camada 3 da rede.\n\nComo requisições DHCP Discover de broadcast não atravessam interfaces de roteadores de camada 3 por padrão, o engenheiro de redes configura o recurso de **Agente de Relay DHCP** (`ip helper-address`) nas interfaces SVI dos switches.",
            "afirmativas": "Com base no funcionamento do Agente de Relay DHCP, analise as afirmativas:\nI. O Agente de Relay intercepta a mensagem DHCP Discover de broadcast da VLAN local e a converte em um pacote Unicast endereçado ao IP do servidor DHCP central.\nII. O servidor DHCP identifica de qual sub-rede a requisição se origina consultando o campo `giaddr` (Gateway IP Address) inserido no pacote pelo Agente de Relay.\nIII. O Agente de Relay exige a instalação de um servidor DHCP físico em cada sala de trabalho da empresa.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com exatidão a conversão de broadcast em unicast e a identificação do escopo correto pelo campo `giaddr`. A afirmativa III é falsa pois o objetivo do DHCP Relay é justamente evitar a presença de um servidor DHCP em cada VLAN.\nFonte: Infraestrutura e Serviços de TI, UA 3."
        },
        {
            "ua": "03", "obj": 3, "grau": "DIFÍCIL", "kw": "Reservas Estáticas de IP por Endereço MAC no DHCP",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Na sala de impressão corporativa da empresa, 5 impressoras multifuncionais de grande porte precisam manter obrigatoriamente os mesmos endereços IP fixos para que os funcionários consigam imprimir sem reconfigurar drivers constantemente.\n\nEm vez de configurar os IPs manualmente nas telas das impressoras (o que dificulta a gerência centralizada), o administrador opta por criar **Reservas de IP por Endereço MAC** no escopo do servidor DHCP.",
            "afirmativas": "Com base na reserva de endereços IP no servidor DHCP, analise as afirmativas:\n\nI. A reserva de IP por MAC vincula um endereço IP específico do escopo DHCP ao endereço físico de camada 2 (MAC Address) do adaptador de rede da impressora.\n\nPORQUE\n\nII. Quando a impressora envia a requisição DHCP Discover na rede, o servidor reconhece o seu endereço MAC e entrega sempre o mesmo endereço IP reservado acompanhado das opções de rede centralizadas.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A vinculação IP-MAC no DHCP garante entrega determinística do mesmo IP fixo via gerenciamento centralizado por DHCP.\nFonte: Infraestrutura e Serviços de TI, UA 3."
        }
    ],
    subfolder='AD'
)

# 9. Interação Humano-Computador (UAs 3, 4)
create_exam(
    "Interação Humano-Computador", "Interação Humano-Computador", "AD Interação Humano-Computador", "3; 4",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Conceitos de Affordance, Mapeamento e Signifiers em IHC (Don Norman)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Ao projetar uma nova interface gráfica para o aplicativo de caixa eletrônico de um banco, o designer de IHC aplica os princípios fundamentais de design de Donald Norman estabelecidos em sua obra *The Design of Everyday Things*.\n\nEle necessita garantir que a forma e o aspecto visual dos botões na tela sugiram imediatamente a ação correta que o usuário pode realizar (por exemplo, um botão com relevo visual 3D sugerindo que ele pode ser pressionado).",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica o conceito de IHC que define as propriedades perceptíveis de um objeto que determinam como ele pode ser utilizado:",
            "opt_a": "Affordance (e Signifiers).", "opt_b": "Heurística de Nielsen.", "opt_c": "Algoritmo de Dijkstra.", "opt_d": "Card Sorting.",
            "feedback": "A resposta certa é Affordance (e Signifiers).\nComentário: Affordance refere-se às propriedades físicas/perceptíveis do objeto que indicam quais ações são possíveis, enquanto os Signifiers comunicam onde e como a ação deve ocorrer.\nFonte: Interação Humano-Computador, UA 3."
        },
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Modelos Mentais de Usuários vs Modelo do Designer em Interfaces",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Durante os testes iniciais de um novo aplicativo de transporte público, os usuários relataram enorme dificuldade para encontrar o botão de confirmação da corrida, pois o designer posicionou a opção em um menu secundário oculto.\n\nO problema ocorreu devido ao descompasso entre o **Modelo do Designer** (como o sistema realmente funciona internamente) e o **Modelo Mental do Usuário** (o conhecimento prévio e a expectativa que o usuário possui sobre como aplicativos de transporte funcionam).",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta a melhor diretriz de design para alinhar a interface ao Modelo Mental do Usuário:",
            "opt_a": "Projetar a interface utilizando metáforas familiares e convenções de mercado já consagradas pelo público-alvo.", "opt_b": "Criar novos ícones abstratos nunca vistos no mercado para forçar o aprendizado.", "opt_c": "Ocultar todas as opções de navegação em telas em branco.", "opt_d": "Exigir que o usuário leia um manual de 50 páginas antes de abrir o aplicativo.",
            "feedback": "A resposta certa é Projetar a interface utilizando metáforas familiares e convenções de mercado já consagradas pelo público-alvo.\nComentário: Interfaces bem-sucedidas respeitam o modelo mental dos usuários adotando convenções e metáforas do mundo real (ex: ícone de lixeira, carrinho de compras).\nFonte: Interação Humano-Computador, UA 3."
        },
        {
            "ua": "04", "obj": 1, "grau": "DIFÍCIL", "kw": "Métodos de Pesquisa de Usuário: Entrevistas, Questionários e Personas",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Na fase inicial de levantamento de requisitos de UX para o desenvolvimento de um aplicativo de saúde voltado para idosos, a equipe de design de interação realiza a etapa de **Pesquisa com Usuários** (User Research).\n\nPara sintetizar os dados qualitativos e quantitativos coletados nas entrevistas e observações de campo, a equipe cria **Personas** arquétipas representando perfis de usuários reais da aplicação.",
            "afirmativas": "Com base nas técnicas de pesquisa de usuário e criação de Personas em IHC, analise as afirmativas:\nI. Personas são personagens fictícios baseados em dados empíricos reais que sintetizam as necessidades, objetivos, limitações e comportamentos do público-alvo.\nII. Entrevistas qualitativas semiestruturadas permitem aprofundar a compreensão das motivações e dores dos usuários durante a interação.\nIII. Personas devem ser criadas com base no achismo pessoal dos desenvolvedores, dispensando pesquisas de campo.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem corretamente a utilidade das Personas e das entrevistas de campo. A afirmativa III é falsa pois Personas válidas obrigatoriamente exigem fundamentação em dados reais da pesquisa.\nFonte: Interação Humano-Computador, UA 4."
        },
        {
            "ua": "04", "obj": 2, "grau": "DIFÍCIL", "kw": "Prototipação de Interfaces de Baixa Fidelidade vs Alta Fidelidade",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Antes de escrever qualquer linha de código front-end para um novo portal de e-learning, a equipe de UI constrói protótipos de interface para testar os fluxos de navegação com as partes interessadas (Stakeholders).\n\nEles alternam entre **Protótipos de Baixa Fidelidade** (desenhos em papel / Wireframes rascunhados) e **Protótipos de Alta Fidelidade** (telas interativas clicáveis criadas em ferramentas como Figma ou Adobe XD).",
            "afirmativas": "Com base nos níveis de fidelidade de prototipação em IHC, analise as afirmativas:\nI. Protótipos de baixa fidelidade são rápidos e baratos de produzir, sendo ideais para explorar conceitos iniciais e validar fluxos sem apego visual.\nII. Protótipos de alta fidelidade representam com precisão visual, tipografia e interatividade o produto final, sendo indicados para testes de usabilidade detalhados.\nIII. Protótipos de baixa fidelidade exigem obrigatoriamente a escrita de código em JavaScript e React.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II diferenciam com exatidão a agilidade do papel/wireframe e o realismo do Figma. A afirmativa III é falsa pois protótipos de baixa fidelidade são feitos sem código (ex: esboços em papel).\nFonte: Interação Humano-Computador, UA 4."
        },
        {
            "ua": "04", "obj": 3, "grau": "DIFÍCIL", "kw": "Arquitetura de Informação: Navegação Hierárquica, Sequencial e por Busca",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Ao projetar a estrutura de navegação de um grande portal de notícias com milhares de artigos categorizados por editorias (Esportes, Política, Economia), o arquiteto de informação define a organização dos menus e mecanismos de busca.\n\nPara garantir que o leitor não se sinta perdido e consiga alternar facilmente entre tópicos de interesse, ele combina a estrutura de **Navegação Hierárquica** com links de atalho (Breadcrumbs / Migalhas de Pão).",
            "afirmativas": "Com base na Arquitetura de Informação e estruturas de navegação, analise as afirmativas:\n\nI. O componente de navegação Breadcrumb (Migalha de Pão) exibe a localização hierárquica atual do usuário dentro da estrutura do site (ex: `Home > Esportes > Futebol`), permitindo o retorno rápido aos níveis superiores.\n\nPORQUE\n\nII. Reduzir o esforço cognitivo de orientação do usuário melhora a usabilidade e previne o sentimento de desorientação espacial em sites com arquiteturas profundas.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. O Breadcrumb apoia a orientação espacial na hierarquia do site, reduzindo a carga cognitiva de navegação.\nFonte: Interação Humano-Computador, UA 4."
        }
    ],
    subfolder='AD'
)

# 10. Programação em PYTHON (UAs 3, 4)
create_exam(
    "Programação em Python(seg)", "Programação em PYTHON", "AD Programação em PYTHON", "3; 4",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Tipos de Dados Primitivos e Operações Matemáticas/Lógicas em Python",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "No desenvolvimento de um script em Python para cálculo de médias ponderadas de notas escolares, o desenvolvedor lida com a coerção dinâmica de tipos (Dynamic Typing).\n\nEle executa a divisão de dois números inteiros (`resultado = 10 / 4`) e precisa verificar o tipo de dado do objeto resultante atribuído à variável `resultado` pelo interpretador.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta o tipo de dado retornado pela operação de divisão simples `/` em Python 3:",
            "opt_a": "float (ponto flutuante).", "opt_b": "int (inteiro).", "opt_c": "str (string).", "opt_d": "bool (booleano).",
            "feedback": "A resposta certa é float (ponto flutuante).\nComentário: Em Python 3, a divisão simples `/` sempre retorna um valor do tipo `float` (ex: `10 / 4 = 2.5`), enquanto a divisão inteira é realizada pelo operador `//`.\nFonte: Programação em PYTHON, UA 3."
        },
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Fatiamento de Sequências (Slicing de Strings e Listas)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Um analista de dados processa uma string contendo um código de identificação de produto (`codigo = 'PROD-9842-BR'`) em um script Python.\n\nPara extrair apenas os quatro dígitos numéricos centrais da string (`'9842'`), ele utiliza a funcionalidade de **Fatiamento de Sequências** (Slicing) informando os índices inicial e final (`string[start:stop]`).",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta a expressão de slicing correta em Python para extrair o trecho `'9842'` da string `codigo = 'PROD-9842-BR'`:",
            "opt_a": "codigo[5:9]", "opt_b": "codigo[4:8]", "opt_c": "codigo[5:10]", "opt_d": "codigo[0:4]",
            "feedback": "A resposta certa é codigo[5:9].\nComentário: Os caracteres '9', '8', '4', '2' estão nos índices 5, 6, 7 e 8. Como o limite superior do slice é exclusivo, o limite 9 extrai até o índice 8.\nFonte: Programação em PYTHON, UA 3."
        },
        {
            "ua": "04", "obj": 1, "grau": "DIFÍCIL", "kw": "Estruturas de Controle de Fluxo Condicional (if-elif-else) e Laços",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um programador escreve um algoritmo em Python para percorrer uma lista de números inteiros de 1 a 20 e classificar cada número segundo regras de divisibilidade.\n\nO algoritmo utiliza o laço `for`, a função `range()` e estruturas condicionais `if-elif-else` com operadores de resto da divisão (`%`).",
            "afirmativas": "Com base no controle de fluxo e laços em Python, analise as afirmativas:\nI. A função `range(1, 21)` gera uma sequência iterável de números inteiros de 1 a 20 (o limite superior 21 é exclusivo).\nII. As instruções `break` e `continue` dentro de um laço servem, respectivamente, para interromper o laço imediatamente e para saltar para a próxima iteração.\nIII. A indentação do código (espaçamento por blocos) em Python é apenas estética e não afeta a execução lógica das condicionais.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com exatidão a função `range()` e o comportamento do `break`/`continue`. A afirmativa III é falsa pois a indentação em Python é sintática e define os blocos de código.\nFonte: Programação em PYTHON, UA 4."
        },
        {
            "ua": "04", "obj": 2, "grau": "DIFÍCIL", "kw": "Definição de Funções, Parâmetros Padrão e *args / **kwargs em Python",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Para construir uma biblioteca utilitária flexível em Python, o desenvolvedor projeta funções que aceitam uma quantidade variável de argumentos posicionais e argumentos nomeados (Key-Word Arguments).\n\nEle utiliza a sintaxe especial de desempacotamento de parâmetros `*args` e `**kwargs` na assinatura da função `def processar_dados(*args, **kwargs):`.",
            "afirmativas": "Com base em parâmetros de funções em Python, analise as afirmativas:\nI. O parâmetro `*args` captura uma quantidade arbitrária de argumentos posicionais extras como uma Tupla.\nII. O parâmetro `**kwargs` captura uma quantidade arbitrária de argumentos nomeados extras como um Dicionário.\nIII. Parâmetros com valores padrão (default parameters) devem ser colocados ANTES dos parâmetros posicionais obrigatórios na assinatura da função.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão a captura de argumentos via `*args` (tupla) e `**kwargs` (dicionário). A afirmativa III é falsa pois parâmetros com valor default devem obrigatoriamente vir DEPOIS dos parâmetros posicionais sem default.\nFonte: Programação em PYTHON, UA 4."
        },
        {
            "ua": "04", "obj": 3, "grau": "DIFÍCIL", "kw": "Funções de Alta Ordem em Python (map(), filter() e reduce())",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Um engenheiro de software aplica os princípios da Programação Funcional em Python para transformar um vetor de valores numéricos `valores = [1, 2, 3, 4, 5, 6]`.\n\nEle utiliza a função de alta ordem `filter()` combinada com uma função anônima `lambda x: x % 2 == 0` para isolar apenas os números pares.",
            "afirmativas": "Com base em funções de alta ordem em Python, analise as afirmativas:\n\nI. A função `filter(funcao_teste, iteravel)` aplica a função de teste booleana a cada elemento do iterável, retornando um iterador contendo apenas os elementos para os quais a função retornou `True`.\n\nPORQUE\n\nII. Em Python, funções são objetos de primeira classe (First-Class Objects), podendo ser atribuídas a variáveis, passadas como argumentos para outras funções e retornadas como resultado de chamadas.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A natureza de First-Class Objects das funções em Python é a premissa fundamental que permite a existência e o funcionamento de funções de alta ordem como `filter()`, `map()` e `reduce()`.\nFonte: Programação em PYTHON, UA 4."
        }
    ],
    subfolder='AD'
)

# 11. Programação em Python Eletiva (UAs 3, 4)
create_exam(
    "Programação em Python(seg)", "Programação em Python Eletiva", "AD Programação em Python Eletiva", "3; 4",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Mutabilidade de Objetos e Copias Rasas (copy()) vs Profundas (deepcopy())",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Ao manipular uma lista aninhada contendo sublistas de dados (`dados = [[1, 2], [3, 4]]`) em Python, o programador realiza a cópia do objeto para um novo identificador `dados_copia = copy.copy(dados)` utilizando o módulo `copy`.\n\nAo alterar um valor dentro de uma sublista em `dados_copia`, ele percebe que a alteração refletiu-se involuntariamente na lista original `dados` devido ao comportamento de Cópia Rasa (Shallow Copy).",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta a função do módulo `copy` necessária para criar uma cópia totalmente independente e profunda (Deep Copy), duplicando recursivamente todos os objetos aninhados:",
            "opt_a": "copy.deepcopy()", "opt_b": "copy.shallowcopy()", "opt_c": "copy.clone()", "opt_d": "copy.duplicate()",
            "feedback": "A resposta certa é copy.deepcopy().\nComentário: A função `copy.deepcopy()` duplica recursivamente o objeto e todos os seus contêineres aninhados, garantindo independência total na memória.\nFonte: Programação em Python Eletiva, UA 3."
        },
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Manipulação de Conjuntos (set) e Operações de União/Interseção",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Um analista de dados precisa identificar os alunos que estão matriculados simultaneamente nas disciplinas de Python (`python_aluno = {'Ana', 'Bruno', 'Carlos'}`) e Banco de Dados (`bd_aluno = {'Bruno', 'Daniela', 'Ana'}`).\n\nEle utiliza a estrutura de dados nativa de **Conjuntos** (`set`) em Python para realizar a operação matemática de interseção de conjuntos (`&`).",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta o resultado da operação de interseção `python_aluno & bd_aluno`:",
            "opt_a": "{'Ana', 'Bruno'}", "opt_b": "{'Ana', 'Bruno', 'Carlos', 'Daniela'}", "opt_c": "{'Carlos'}", "opt_d": "{'Daniela'}",
            "feedback": "A resposta certa é {'Ana', 'Bruno'}.\nComentário: A operação de interseção (`&`) em conjuntos Python retorna os elementos presentes em ambos os conjuntos ('Ana' e 'Bruno').\nFonte: Programação em Python Eletiva, UA 3."
        },
        {
            "ua": "04", "obj": 1, "grau": "DIFÍCIL", "kw": "Compreensão de Dicionários (Dictionary Comprehensions) em Python",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um cientista de dados possui uma lista de tuplas contendo nomes de cidades e suas temperaturas em Celsius (`dados = [('SP', 25), ('RJ', 30), ('PR', 18)]`).\n\nEle deseja construir um Dicionário em Python onde as chaves sejam as cidades e os valores sejam as temperaturas convertidas para a escala Kelvin ($K = C + 273$), utilizando a sintaxe expressiva de **Dictionary Comprehension**.",
            "afirmativas": "Com base em Dictionary Comprehensions em Python, analise as afirmativas:\nI. A sintaxe de Dictionary Comprehension é dada por `{chave: valor for item in iterável}`.\nII. A expressão `{cidade: temp + 273 for cidade, temp in dados}` constrói corretamente o dicionário com as temperaturas em Kelvin.\nIII. Dictionary Comprehensions convertem automaticamente todas as chaves de string em inteiros.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com exatidão a estrutura de geração de dicionários por compreenção em Python. A afirmativa III é falsa pois o tipo da chave é preservado conforme definido.\nFonte: Programação em Python Eletiva, UA 4."
        },
        {
            "ua": "04", "obj": 2, "grau": "DIFÍCIL", "kw": "Funções Geradoras (yield) e Iteradores Personalizados",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Para processar um arquivo de log gigantesco de 100 GB contendo bilhões de linhas sem carregar todo o arquivo para a memória RAM do servidor, um desenvolvedor Python cria uma **Função Geradora** (Generator Function).\n\nA função utiliza a palavra-chave **`yield`** para produzir uma linha por vez à medida que é solicitada pelo laço de repetição.",
            "afirmativas": "Com base em Geradores (Generators) em Python, analise as afirmativas:\nI. Funções geradoras utilizam a instrução `yield` em vez de `return`, suspendendo o estado da função e retornando um valor por vez de forma preguiçosa (Lazy Evaluation).\nII. Geradores mantêm o estado local de suas variáveis entre chamadas sucessivas do método `next()`.\nIII. Geradores consomem a mesma quantidade de memória RAM do que carregar uma lista contendo todos os bilhões de elementos pré-computados.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão a avaliação preguiçosa (lazy) e a preservação de estado dos geradores `yield`. A afirmativa III é falsa pois a maior vantagem dos geradores é justamente o consumo de memória O(1) quase nulo.\nFonte: Programação em Python Eletiva, UA 4."
        },
        {
            "ua": "04", "obj": 3, "grau": "DIFÍCIL", "kw": "Programação Funcional com Módulos Nativos functools e itertools",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Um desenvolvedor Python otimiza o desempenho de uma função matemática recursiva pesada (como o cálculo de números de Fibonacci ou combinações estatísticas) utilizando o decorador `@functools.lru_cache(maxsize=None)` do módulo nativo `functools`.\n\nO decorador armazena automaticamente em cache de memória (Memoização) os resultados de chamadas de função com os mesmos argumentos de entrada.",
            "afirmativas": "Com base na memoização com `functools.lru_cache`, analise as afirmativas:\n\nI. O uso do decorador `@functools.lru_cache` reduz a complexidade de tempo de funções recursivas de custo exponencial para custo linear ao reutilizar resultados previamente calculados em chamadas anteriores.\n\nPORQUE\n\nII. A técnica de Memoização armazena o mapeamento de argumentos e resultados em uma tabela hash interna em memória, evitando a reavaliação de sub-problemas já resolvidos.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A memoização em memória evita recálculos recursivos, reduzindo drasticamente o tempo de execução de funções com subproblemas sobrepostos.\nFonte: Programação em Python Eletiva, UA 4."
        }
    ],
    subfolder='AD'
)

print("Batch TG 3 concluído.")
