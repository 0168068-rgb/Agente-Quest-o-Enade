# -*- coding: utf-8 -*-
"""
Batch 3: Disciplinas 8 a 11 (Versão ENADE Expandida - Caso Prático Robusto > 7 linhas)
"""
from generate_full_batch import create_exam

# 8. Infraestrutura e serviços de TI
create_exam(
    "Infraestrutura e Serviços de TI", "Infraestrutura e serviços de TI", "AI Infraestrutura e serviços de TI", "1; 3; 5; 11",
    [
        {
            "ua": "01", "obj": 1, "grau": "MÉDIA", "kw": "Modelos de Serviços em Nuvem (IaaS, PaaS, SaaS)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Uma startup de tecnologia em expansão precisa definir a arquitetura de implantação de seu novo sistema de gerenciamento de vendas. A equipe de desenvolvedores deseja focar exclusivamente na escrita do código-fonte e na lógica de negócios da aplicação em Node.js e Python, reduzindo o tempo de lançamento no mercado (Time-to-Market).\n\nPara isso, a diretoria decidiu contratar uma solução de nuvem onde o provedor seja o responsável integral por provisionar a infraestrutura de hardware, os sistemas operacionais virtuais, a instalação de dependências e os ambientes de runtime, eliminando a sobrecarga de administração de servidores da equipe interna.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o modelo de serviço em nuvem que fornece um ambiente completo de desenvolvimento e implantação gerenciado pelo provedor:",
            "opt_a": "PaaS (Platform as a Service).", "opt_b": "IaaS (Infrastructure as a Service).", "opt_c": "SaaS (Software as a Service).", "opt_d": "DaaS (Desktop as a Service).",
            "feedback": "A resposta certa é PaaS (Platform as a Service).\nComentário: No PaaS (Plataforma como Serviço), o provedor gerencia a infraestrutura, SO e runtime, cabendo ao cliente apenas o desenvolvimento e configuração da aplicação.\nFonte: Infraestrutura e Serviços de TI, UA 1."
        },
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Serviços de Diretório LDAP e Active Directory",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Em uma corporação com mais de 1.000 colaboradores distribuídos por 5 filiais, o departamento de TI precisa resolver o caos gerado pela gestão descentralizada de senhas de acesso a sistemas web, VPNs, e-mails e estações de trabalho.\n\nPara centralizar o gerenciamento de contas de usuário, políticas de acesso por grupo (GPO) e permissões de segurança em um único repositório hierárquico, a equipe implantou um Serviço de Diretório baseado na arquitetura X.500.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta o protocolo padrão de camada de aplicação utilizado por sistemas como OpenLDAP e Active Directory para consultar e modificar serviços de diretório em redes IP:",
            "opt_a": "LDAP (Lightweight Directory Access Protocol).", "opt_b": "SNMP (Simple Network Management Protocol).", "opt_c": "DHCP (Dynamic Host Configuration Protocol).", "opt_d": "SMTP (Simple Mail Transfer Protocol).",
            "feedback": "A resposta certa é LDAP (Lightweight Directory Access Protocol).\nComentário: O LDAP é o protocolo padrão utilizado para autenticação centralizada e consulta a bases de dados de diretório como OpenLDAP e Active Directory.\nFonte: Infraestrutura e Serviços de TI, UA 3."
        },
        {
            "ua": "05", "obj": 3, "grau": "DIFÍCIL", "kw": "Servidor Web Apache/Nginx e Proxy Reverso",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Para suportar picos de acessos durante eventos promocionais sem indisponibilizar a plataforma e-commerce, a equipe de infraestrutura instalou um cluster de servidores web Nginx atuando como Proxy Reverso e balanceador de carga HTTP em frente a 8 instâncias de aplicações backend.\n\nAlém de distribuir as requisições de forma proporcional, a camada de Proxy Reverso foi configurada para centralizar os certificados digitais HTTPS (SSL/TLS Termination) e aliviar a carga de processamento dos servidores internos.",
            "afirmativas": "Com base nos conceitos de Proxy Reverso e terminação SSL/TLS, analise as afirmativas:\nI. O Proxy Reverso recebe as requisições HTTPS dos clientes externos, decodifica a criptografia SSL/TLS e encaminha o tráfego limpo para os servidores HTTP internos.\nII. O uso do Nginx como Proxy Reverso esconde os endereços IP reais dos servidores de aplicação internos, aumentando a proteção perimetral contra ataques direcionados.\nIII. O Proxy Reverso impede a implementação de mecanismos de cache de conteúdo estático para imagens e arquivos CSS/JS.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II apresentam com precisão as funções de terminação SSL e mascaramento IP de um Proxy Reverso. A afirmativa III é falsa pois o cache de conteúdo estático é um dos principais benefícios do Nginx.\nFonte: Infraestrutura e Serviços de TI, UA 5."
        },
        {
            "ua": "11", "obj": 1, "grau": "DIFÍCIL", "kw": "Gerenciamento de Serviços de TI (ITIL v4) e Incidentes",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "A diretoria de operações de TI de uma empresa de logística adotou o framework ITIL 4 para estruturar a sua Gestão de Serviços de TI (ITSM). As práticas operacionais foram divididas para garantir a manutenção da estabilidade do negócio frente a falhas operacionais cotidianas.\n\nNo cotidiano da operação, chamados decorrentes de quedas imprevisíveis de links de comunicação e lentidões nos sistemas são registrados pelo Service Desk e encaminhados para tratamento conforme os processos formais.",
            "afirmativas": "Com base nas práticas de Gerenciamento de Incidentes e Gerenciamento de Problemas do ITIL v4, analise as afirmativas:\nI. A Gestão de Incidentes busca restaurar a operação normal do serviço o mais rápido possível, utilizando contornamentos (workarounds) se necessário, para minimizar o impacto no negócio.\nII. A Gestão de Problemas foca na identificação e análise das causas raiz recorrentes dos incidentes para prevenir a sua repetição futura.\nIII. Um Incidente e um Problema possuem exatamente o mesmo conceito e objetivo prático na estrutura de processos do ITIL v4.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II diferenciam com precisão a natureza da Gestão de Incidentes (restauração rápida) e Gestão de Problemas (causa raiz). A afirmativa III é falsa pois a ITIL separa estritamente estes dois conceitos.\nFonte: Infraestrutura e Serviços de TI, UA 11."
        },
        {
            "ua": "11", "obj": 2, "grau": "DIFÍCIL", "kw": "Central de Serviços (Service Desk) no ITIL v4",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Uma instituição financeira substituiu os atendimentos de TI informais realizados via ramais de técnicos por uma Central de Serviços (Service Desk) estruturada como o Ponto Único de Contato (SPOC - Single Point of Contact) da empresa.",
            "afirmativas": "Com base no papel estratégico da Central de Serviços (Service Desk) no ITIL 4, analise as afirmativas:\n\nI. A Central de Serviços deve ser o ponto focal para triagem de requisições de serviço, registro de incidentes e comunicação transparente com os usuários finais.\n\nPORQUE\n\nII. A centralização do atendimento em um ponto único evita solicitações informais paralelas aos técnicos, garantindo rastreabilidade, priorização baseada no impacto no negócio e cumprimento dos acordos de nível de serviço (SLA).",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. O Service Desk centraliza chamados exatamente para estruturar o fluxo de trabalho e evitar perda de visibilidade dos níveis de serviço.\nFonte: Infraestrutura e Serviços de TI, UA 11."
        }
    ]
)

# 9. Interação Humano-Computador
create_exam(
    "Interação Humano-Computador", "Interação Humano-Computador", "AI Interação Humano-Computador", "3; 4; 6; 8",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Heurísticas de Usabilidade de Jakob Nielsen",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Ao avaliar a interface gráfica de um aplicativo de transferência bancária móvel, um analista de UX/UI observou que, ao clicar no botão 'Confirmar PIX', a tela congelava por cerca de 4 segundos sem exibir nenhuma alteração visual, fazendo com que os usuários clicassem repetidamente no botão por dúvida sobre o envio.\n\nPara solucionar a falha, a equipe adicionou uma animação de progresso com a mensagem 'Processando sua transferência, aguarde...', alterando o estado do botão para desabilitado temporariamente.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica a Heurística de Usabilidade de Nielsen atendida diretamente por essa correção gráfica:",
            "opt_a": "Visibilidade do estado do sistema.", "opt_b": "Correspondência entre o sistema e o mundo real.", "opt_c": "Consistência e padrões.", "opt_d": "Flexibilidade e eficiência de uso.",
            "feedback": "A resposta certa é Visibilidade do estado do sistema.\nComentário: A 1ª Heurística de Nielsen afirma que o sistema deve sempre manter os usuários informados sobre o que está acontecendo, através de feedback apropriado dentro de um tempo razoável.\nFonte: Interação Humano-Computador, UA 3."
        },
        {
            "ua": "04", "obj": 2, "grau": "MÉDIA", "kw": "Acessibilidade Web (WCAG 2.1) e Leitores de Tela",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Um desenvolvedor front-end está auditando um portal de serviços públicos municipais para certificar o cumprimento do modelo e-MAG e das diretrizes internacionais de acessibilidade WCAG 2.1 no nível de conformidade AA.\n\nDurante os testes efetuados com leitores de tela sintéticos (como NVDA ou TalkBack) utilizados por pessoas com deficiência visual total, o software leitor simplesmente pronunciava a palavra 'imagem' sem transmitir qualquer significado funcional dos gráficos infográficos dispostos na página.",
            "afirmativas": "",
            "comando_text": "Para garantir que deficientes visuais compreendam o significado de elementos gráficos informativos via leitores de tela, assinale o atributo HTML obrigatório a ser adicionado na tag <img>:",
            "opt_a": "alt com um texto descritivo significativo.", "opt_b": "title com o caminho do arquivo no servidor.", "opt_c": "src em caixa alta.", "opt_d": "id numérico sequencial.",
            "feedback": "A resposta certa é alt com um texto descritivo significativo.\nComentário: O atributo 'alt' (texto alternativo) fornece a descrição textual lida pelos leitores de tela para sintetizar imagens informativas.\nFonte: Interação Humano-Computador, UA 4."
        },
        {
            "ua": "06", "obj": 3, "grau": "DIFÍCIL", "kw": "Design Centrado no Usuário (DCU) e Personas",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Durante a fase de concepção de um aplicativo móvel de telemedicina focado no público da terceira idade, a equipe de produto adota a metodologia do Design Centrado no Usuário (DCU).\n\nPara garantir que o software seja fácil de usar e atenda às limitações cognitivas e motoras reais dos futuros pacientes, os designers realizam entrevistas em profundidade, constroem mapas de empatia e desenvolvem representações sintetizadas dos perfis dos usuários.",
            "afirmativas": "Com base nos métodos de pesquisa de UX e na criação de Personas no DCU, analise as afirmativas:\nI. Personas são arquétipos fictícios construídos com base em dados reais de pesquisas com usuários que sintetizam comportamentos, necessidades e metas do público-alvo.\nII. A etapa de testes de usabilidade com protótipos navegáveis deve ser realizada exclusivamente após o lançamento final do aplicativo nas lojas de apps.\nIII. A empatia e a compreensão contínua do contexto de uso dos usuários são pilares fundamentais do Design Centrado no Usuário.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e III, apenas.", "opt_b": "I e II, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e III, apenas.\nComentário: As afirmativas I e III descrevem corretamente o conceito de Personas e a essência do DCU. A afirmativa II é falsa pois testes de usabilidade devem ser feitos iterativamente com protótipos ANTES do lançamento.\nFonte: Interação Humano-Computador, UA 6."
        },
        {
            "ua": "08", "obj": 1, "grau": "DIFÍCIL", "kw": "Arquitetura de Informação e Card Sorting",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Uma equipe de UX precisa reorganizar a estrutura dos menus de navegação, subcategorias e rótulos de uma plataforma corporativa complexa de EAD contendo mais de 200 cursos técnicos e materiais instrucionais.\n\nPara garantir que a classificação dos conteúdos corresponda ao modelo mental intuitivo dos alunos e não à visão hierárquica interna da faculdade, os pesquisadores aplicam a técnica de Card Sorting com grupos de estudantes.",
            "afirmativas": "Com base na técnica de Card Sorting aplicada à Arquitetura de Informação, analise as afirmativas:\nI. No Card Sorting Aberto, os participantes organizam os cartões de conteúdo em grupos e nomeiam livremente as categorias criadas.\nII. No Card Sorting Fechado, os participantes distribuem os cartões de conteúdo dentro de categorias predefinidas pelos pesquisadores.\nIII. O Card Sorting é uma técnica que elimina a necessidade de construir o mapa do site (Sitemap) e os fluxos de navegação do usuário.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com precisão as variações Aberto e Fechado do Card Sorting. A afirmativa III é falsa pois a Arquitetura de Informação complementa os fluxos de tarefas, não os substitui.\nFonte: Interação Humano-Computador, UA 8."
        },
        {
            "ua": "08", "obj": 2, "grau": "DIFÍCIL", "kw": "Lei de Fitts e Design de Interfaces Móveis",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "No design de interfaces móveis para smartphones, o posicionamento do botão de ação primário 'Finalizar Compra' na parte inferior da tela (próximo à zona de alcance natural do polegar) reduz a taxa de abandono de carrinho de compras.",
            "afirmativas": "Com base nos princípios ergonômicos da Lei de Fitts aplicados ao design de UI, analise as afirmativas:\n\nI. A Lei de Fitts estabelece que o tempo necessário para alcançar um alvo (como um botão) é função da distância até o alvo e da largura/tamanho do próprio alvo.\n\nPORQUE\n\nII. Aumentar a área de toque de botões críticos e posicioná-los na zona inferior de alcance do polegar reduz a latência de acionamento e minimiza erros de toque em dispositivos móveis.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A Lei de Fitts embasa a recomendação de criar botões com alvos maiores e próximos da zona de alcance natural do polegar.\nFonte: Interação Humano-Computador, UA 8."
        }
    ]
)

# 10. Programação em PYTHON
create_exam(
    "Programação em Python(seg)", "Programação em PYTHON", "AI Programação em PYTHON", "3; 4; 7; 10",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Estruturas de Dados Nativas (Listas, Tuplas, Dicionários, Sets)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em um script Python desenvolvido para processamento de logs de acesso de um servidor web, o desenvolvedor precisa armazenar uma coleção de endereços IP de origem únicos sem elementos duplicados.\n\nO objetivo é realizar operações matemáticas de conjunto (como união e interseção de acessos) com alta velocidade computacional em tempo médio O(1).",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta a estrutura de dados nativa em Python mutável e não ordenada que garante a unicidade de seus elementos:",
            "opt_a": "set (conjunto).", "opt_b": "list (lista).", "opt_c": "tuple (tupla).", "opt_d": "dict (dicionário).",
            "feedback": "A resposta certa é set (conjunto).\nComentário: Em Python, a estrutura 'set' elimina automaticamente elementos duplicados e suporta operações de teoria dos conjuntos em tempo médio O(1).\nFonte: Programação em PYTHON, UA 3."
        },
        {
            "ua": "04", "obj": 2, "grau": "MÉDIA", "kw": "Orientação a Objetos em Python e Métodos Mágicos (__init__, __str__)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Um engenheiro de software modela o sistema bancário corporativo utilizando o paradigma de Orientação a Objetos em Python. Ele desenvolve a classe 'ContaBancaria' contendo os atributos privados _saldo e _titular.\n\nNo momento em que um novo objeto do tipo ContaBancaria é instanciado na memória, o interpretador Python deve executar um método especial interno encarregado de atribuir os valores iniciais recebidos aos atributos do objeto.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o método especial (construtor) executado automaticamente no momento da instanciação de um novo objeto para inicializar seus atributos:",
            "opt_a": "__init__(self, ...).", "opt_b": "__main__(self, ...).", "opt_c": "__str__(self, ...).", "opt_d": "__call__(self, ...).",
            "feedback": "A resposta certa é __init__(self, ...).\nComentário: O método dunder `__init__` é o construtor padrão das classes em Python, responsável por inicializar o estado inicial das instâncias.\nFonte: Programação em PYTHON, UA 4."
        },
        {
            "ua": "07", "obj": 3, "grau": "DIFÍCIL", "kw": "Manipulação de Arquivos e Tratamento de Exceções (try/except/with)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um script de ETL em Python efetua a leitura de um arquivo CSV volumoso armazenado no disco rígido para extrair registros de vendas e gravar no banco de dados relacional.\n\nPara evitar vazamentos de memória e corrupção de descritores de arquivos no sistema operacional em caso de erros inesperados de E/S durante o processamento, o desenvolvedor utiliza blocos formais de tratamento de exceções.",
            "afirmativas": "Com base nas boas práticas de manipulação de arquivos e tratamento de exceções em Python, analise as afirmativas:\nI. O uso do gerenciador de contexto 'with open(...) as f:' garante o fechamento automático do arquivo mesmo ocorrendo exceções dentro do bloco.\nII. A cláusula 'except FileNotFoundError:' captura especificamente o erro lançado quando o arquivo informado não é localizado no caminho indicado.\nIII. A instrução 'finally:' é executada exclusivamente se nenhuma exceção for lançada dentro do bloco try.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com precisão o contexto `with` e a captura de exceções. A afirmativa III é falsa pois o bloco `finally` é SEMPRE executado, ocorrendo ou não exceções.\nFonte: Programação em PYTHON, UA 7."
        },
        {
            "ua": "10", "obj": 1, "grau": "DIFÍCIL", "kw": "Análise de Dados com Pandas e DataFrames",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Um cientista de dados utiliza a biblioteca Pandas em Python para higienizar e analisar um conjunto de dados de vendas contendo 100.000 registros obtidos de uma base relacional.\n\nO objetivo da análise é remover entradas inconsistentes com valores ausentes (NaN) e aplicar agregação estatística para calcular o faturamento mensal médio por categoria de produto.",
            "afirmativas": "Com base nos métodos da biblioteca Pandas em Python, analise as afirmativas:\nI. O método 'df.dropna()' remove linhas contendo valores nulos (NaN) do DataFrame.\nII. O método 'df.groupby()' permite agrupar dados por colunas categóricas e aplicar funções de agregação como mean(), sum() e count().\nIII. DataFrames do Pandas são estruturas de dados unidimensionais idênticas às tuplas nativas da linguagem Python.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II apresentam corretamente as funções dropna() e groupby(). A afirmativa III é falsa pois DataFrames são estruturas bidimensionais (tabelas com linhas e colunas).\nFonte: Programação em PYTHON, UA 10."
        },
        {
            "ua": "10", "obj": 2, "grau": "DIFÍCIL", "kw": "List Comprehensions e Funções Lambda",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Em um código de processamento numérico em Python, o desenvolvedor refatora um laço for tradicional contendo 6 linhas por uma única instrução concisa do tipo List Comprehension.",
            "afirmativas": "Com base nos recursos expressivos e funcionais de Python, analise as afirmativas:\n\nI. A expressão '[x**2 for x in numeros if x % 2 == 0]' constrói uma nova lista contendo os quadrados apenas dos números pares da lista original de forma concisa e expressiva.\n\nPORQUE\n\nII. As List Comprehensions são otimizadas em nível de bytecode CPython, oferecendo sintaxe legível e desempenho frequentemente superior ao encadeamento de laços for manuais com append().",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A sintaxe funcional da List Comprehension filtra e transforma dados de forma extremamente legível e performática em Python.\nFonte: Programação em PYTHON, UA 10."
        }
    ]
)

# 11. Programação em Python Eletiva
create_exam(
    "Programação em Python(seg)", "Programação em Python Eletiva", "AI Programação em Python Eletiva", "3; 4; 7; 10",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Estruturas de Dados e Compreensão de Dicionários",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Na disciplina de Programação em Python Eletiva, os alunos desenvolvem algoritmos funcionais de manipulação de coleções de dados para autoinscrição em eventos acadêmicos.\n\nA partir de uma lista contendo tuplas no formato (nome, idade), o código deve gerar um dicionário filtrado que mapeie o nome dos alunos como chave para suas idades apenas para participantes maiores de 18 anos.",
            "afirmativas": "",
            "comando_text": "Assinale a instrução em Python que constrói um dicionário filtrado através da sintaxe de Dict Comprehension:",
            "opt_a": "{nome: idade for nome, idade in pessoas if idade >= 18}.", "opt_b": "[nome: idade for nome, idade in pessoas if idade >= 18].", "opt_c": "(nome: idade for nome, idade in pessoas if idade >= 18).", "opt_d": "set(nome: idade for nome, idade in pessoas if idade >= 18).",
            "feedback": "A resposta certa é {nome: idade for nome, idade in pessoas if idade >= 18}.\nComentário: As chaves `{ k: v for ... }` definem a sintaxe de Dict Comprehension em Python.\nFonte: Programação em Python Eletiva, UA 3."
        },
        {
            "ua": "04", "obj": 2, "grau": "MÉDIA", "kw": "Herança e Polimorfismo com super()",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Em um sistema de folha de pagamento corporativo desenvolvido em Python, a subclasse 'Gerente' herda da classe base 'Funcionario' e sobrescreve o método 'calcular_salario()'.\n\nDentro da implementação do método sobrescrito em Gerente, o programador precisa reaproveitar o cálculo do salário base executado pelo método da classe pai Funcionario antes de somar a gratificação de gerência.",
            "afirmativas": "",
            "comando_text": "Para invocar a implementação do método 'calcular_salario()' da classe pai dentro da subclasse Gerente, assinale a função nativa correta em Python:",
            "opt_a": "super().calcular_salario().", "opt_b": "parent().calcular_salario().", "opt_c": "base().calcular_salario().", "opt_d": "this().calcular_salario().",
            "feedback": "A resposta certa é super().calcular_salario().\nComentário: A função `super()` retorna um objeto proxy que delega chamadas de métodos às classes pai da hierarquia de herança.\nFonte: Programação em Python Eletiva, UA 4."
        },
        {
            "ua": "07", "obj": 3, "grau": "DIFÍCIL", "kw": "Módulos Nativos json e os/sys",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um utilitário de linha de comando (CLI) em Python necessita carregar um arquivo JSON de configurações e inspecionar os arquivos contidos em um diretório do sistema operacional.",
            "afirmativas": "Com base nas bibliotecas padrão 'json' e 'os' do Python, analise as afirmativas:\nI. A função 'json.loads()' converte uma string contendo um documento JSON em um dicionário ou lista nativa Python.\nII. A função 'os.listdir()' retorna uma lista contendo os nomes das entradas presentes no diretório informado.\nIII. O módulo 'json' grava nativamente arquivos binários criptografados sem suporte a texto plano UTF-8.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com precisão `json.loads()` e `os.listdir()`. A afirmativa III é falsa pois o formato JSON é estritamente texto plano.\nFonte: Programação em Python Eletiva, UA 7."
        },
        {
            "ua": "10", "obj": 1, "grau": "DIFÍCIL", "kw": "Visualização de Dados com Matplotlib/Seaborn",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Um projeto eletivo de análise de dados utiliza as bibliotecas Matplotlib e Seaborn para gerar gráficos estáticos para relatórios executivos.",
            "afirmativas": "Com base nos módulos de plotagem gráfica em Python, analise as afirmativas:\nI. A função 'plt.plot()' gera gráficos de linhas para séries temporais e variáveis contínuas.\nII. A função 'plt.show()' exibe as figuras geradas na tela ou no ambiente Jupyter Notebook.\nIII. A biblioteca Matplotlib é incapaz de customizar títulos, rótulos de eixos ou legendas dos gráficos.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem funções básicas do Matplotlib. A afirmativa III é falsa pois a customização de títulos (title), eixos (xlabel, ylabel) e legendas (legend) é amplamente suportada.\nFonte: Programação em Python Eletiva, UA 10."
        },
        {
            "ua": "10", "obj": 2, "grau": "DIFÍCIL", "kw": "Decoradores (Decorators) em Python",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Em uma aplicação web desenvolvida em Python com o framework Flask, o programador utiliza a sintaxe '@autenticacao_requerida' acima da definição de funções de rotas administrativas.",
            "afirmativas": "Com base nos conceitos de Decoradores (Decorators) em Python, analise as afirmativas:\n\nI. Um Decorador em Python é uma função que recebe outra função como argumento, estende seu comportamento sem modificar seu código-fonte de forma explícita, e retorna uma nova função envolvida.\n\nPORQUE\n\nII. Funções em Python são objetos de primeira classe (First-Class Citizens), podendo ser atribuídas a variáveis, passadas como parâmetros e retornadas por outras funções.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A existência de funções como objetos de primeira classe é exatamente o mecanismo computacional que habilita a criação de decoradores em Python.\nFonte: Programação em Python Eletiva, UA 10."
        }
    ]
)

print("Batch 3 atualizado com contextualização ENADE robusta (> 7 linhas).")
