# -*- coding: utf-8 -*-
"""
Batch PS 3: Disciplinas 8 a 11 (Provas PS 2026-4 - Novos Objetivos e Contextualização ENADE > 7 linhas)
"""
from generate_full_batch import create_exam

# 8. Infraestrutura e Serviços de TI
create_exam(
    "Infraestrutura e Serviços de TI", "Infraestrutura e Serviços de TI", "PS Infraestrutura e serviços de TI", "1; 3; 5; 11",
    [
        {
            "ua": "01", "obj": 2, "grau": "MÉDIA", "kw": "Serviços de Diretório com Active Directory (AD DS e LDAP)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em uma corporação com 2.000 funcionários e múltiplos departamentos, o administrador de sistemas precisa centralizar a gestão de identidades, autenticação de usuários, contas de computadores e políticas de segurança da informação em um único repositório hierárquico.\n\nA equipe instala o serviço Active Directory Domain Services (AD DS) em controladores de domínio rodando Windows Server, permitindo o acesso aos dados de diretório através do protocolo padrão LDAP.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica o recurso do Active Directory utilizado para aplicar configurações de segurança, restrições de sistema e instalação de softwares em massa para grupos de usuários e computadores:",
            "opt_a": "Diretivas de Grupo (GPO - Group Policy Objects).", "opt_b": "Servidor DHCP Scope.", "opt_c": "Registro de Recursos DNS AAAA.", "opt_d": "Filtro de Conteúdo HTTP.",
            "feedback": "A resposta certa é Diretivas de Grupo (GPO - Group Policy Objects).\nComentário: As GPOs permitem centralizar e automatizar a aplicação de políticas de configuração e segurança sobre objetos organizacionais no AD DS.\nFonte: Infraestrutura e Serviços de TI, UA 1."
        },
        {
            "ua": "03", "obj": 3, "grau": "MÉDIA", "kw": "Atribuição Dinâmica de IPs com DHCP e Opções Scope",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Na rede local corporativa de uma empresa, um servidor DHCP fornece automaticamente endereços IP, máscara de sub-rede e gateway padrão para mais de 300 notebooks de funcionários.\n\nAlém das configurações básicas de rede IP, a equipe de telefonia precisa que o servidor DHCP informe automaticamente aos telefones IP (VoIP) recém-conectados à rede o endereço IP do servidor TFTP de provisionamento do firmware.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o mecanismo do protocolo DHCP utilizado para transmitir parâmetros de configuração adicionais (como IP do servidor TFTP ou nome do domínio) aos clientes:",
            "opt_a": "Opções DHCP (DHCP Options - ex: Opção 15, 66, 150).", "opt_b": "Tabela de Roteamento Estático.", "opt_c": "Registro de Chave Pública RSA.", "opt_d": "Cabeçalho HTTP User-Agent.",
            "feedback": "A resposta certa é Opções DHCP (DHCP Options - ex: Opção 15, 66, 150).\nComentário: As opções DHCP transmitem dados suplementares de configuração de rede para os clientes durante o processo de lease (DHCPACK).\nFonte: Infraestrutura e Serviços de TI, UA 3."
        },
        {
            "ua": "05", "obj": 1, "grau": "DIFÍCIL", "kw": "Protocolos de Correio Eletrônico (SMTP vs IMAP/POP3)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Uma empresa de serviços corporativos estrutura seu servidor de e-mail corporativo utilizando a pilha de protocolos padrão de correio eletrônico na internet (SMTP, IMAP e POP3).\n\nOs funcionários utilizam clientes de e-mail (como Microsoft Outlook ou Mozilla Thunderbird) instalados em seus notebooks e smartphones para enviar e receber mensagens eletrônicas.",
            "afirmativas": "Com base nos protocolos de correio eletrônico, analise as afirmativas:\nI. O protocolo SMTP (Simple Mail Transfer Protocol) é utilizado para a transferência e envio de e-mails entre o cliente e o servidor ou entre servidores MTA.\nII. O protocolo IMAP permite sincronizar mensagens diretamente na caixa de correio do servidor em múltiplos dispositivos simultaneamente.\nIII. O protocolo POP3 mantém todas as mensagens armazenadas permanentemente no servidor remoto sem baixá-las para o disco local.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem corretamente o SMTP (envio) e IMAP (sincronização no servidor). A afirmativa III é falsa pois o POP3 por padrão baixa as mensagens para o cliente e as apaga do servidor.\nFonte: Infraestrutura e Serviços de TI, UA 5."
        },
        {
            "ua": "11", "obj": 2, "grau": "DIFÍCIL", "kw": "Servidores Web HTTP (Apache HTTPd / Nginx e Hosts Virtuais)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Um servidor web Linux rodando Nginx ou Apache precisa hospedar 3 sites institucionais distintos (`site1.empresa.com`, `site2.empresa.com` e `site3.empresa.com`) utilizando uma única interface de rede e um único endereço IP público.\n\nO administrador de sistemas configura o recurso de Hosts Virtuais baseados em nomes (Name-Based Virtual Hosts) no servidor web para direcionar as requisições HTTP recebidas aos diretórios corretos.",
            "afirmativas": "Com base em servidores web e Hosts Virtuais, analise as afirmativas:\nI. Hosts Virtuais baseados em nomes utilizam o cabeçalho HTTP 'Host' enviado pelo navegador para identificar qual site deve responder à requisição.\nII. O servidor Nginx utiliza uma arquitetura assíncrona orientada a eventos, sendo altamente eficiente na manipulação de conexões concorrentes.\nIII. Hosts Virtuais exigem obrigatoriamente a atribuição de uma placa de rede física dedicada para cada domínio hospedado.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com precisão o cabeçalho Host do HTTP/1.1 e a arquitetura orientada a eventos do Nginx. A afirmativa III é falsa pois múltiplos Hosts Virtuais compartilham o mesmo IP e interface.\nFonte: Infraestrutura e Serviços de TI, UA 11."
        },
        {
            "ua": "11", "obj": 3, "grau": "DIFÍCIL", "kw": "Criptografia de Camada de Aplicação com HTTPS/TLS",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Para proteger dados financeiros e senhas de usuários em um portal de compras online, a empresa instala um certificado digital SSL/TLS e força o redirecionamento de todas as conexões HTTP comuns para o protocolo seguro HTTPS (porta TCP 443).\n\nO protocolo TLS estabelece um túnel criptografado entre o navegador do usuário e o servidor web antes da troca de qualquer dado de aplicação.",
            "afirmativas": "Com base na segurança de servidores web com HTTPS/TLS, analise as afirmativas:\n\nI. O protocolo HTTPS previne ataques de interceptação de dados (Eavesdropping) e adulteração em trânsito (Man-in-the-Middle) ao criptografar todo o tráfego HTTP com chaves simétricas negociadas no aperto de mão TLS.\n\nPORQUE\n\nII. O certificado digital TLS X.509 instalado no servidor web garante a autenticidade do domínio para o navegador do cliente através da assinatura digital de uma Autoridade Certificadora (AC) confiável.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A autenticação do servidor pela AC e a criptografia dos dados formam os dois pilares do HTTPS.\nFonte: Infraestrutura e Serviços de TI, UA 11."
        }
    ],
    subfolder='PS'
)

# 9. Interação Humano-Computador
create_exam(
    "Interação Humano-Computador", "Interação Humano-Computador", "PS Interação Humano-Computador", "3; 4; 6; 8",
    [
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Leis de UX (Lei de Fitts e Lei de Hick)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Durante o redesign da interface móvel de um aplicativo de compras, a equipe de UX/UI projeta a posição e o tamanho do botão principal de finalização do pedido (Call to Action - CTA).\n\nPara facilitar a interação rápida e reduzir erros de toque do usuário em telas sensíveis ao toque, a equipe aplica a **Lei de Fitts**, que relaciona o tempo necessário para alcançar um alvo com a distância até ele e o seu tamanho físico.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta a recomendação de design derivada da Lei de Fitts para botões de ação críticos em interfaces móveis:",
            "opt_a": "Tornar os botões de ação primária grandes e posicioná-los em áreas de fácil alcance do polegar do usuário.", "opt_b": "Esconder os botões principais em menus suspensos de segundo nível.", "opt_c": "Reduzir o tamanho do botão para o menor valor possível para economizar espaço de tela.", "opt_d": "Alterar a cor do botão aleatoriamente a cada clique do usuário.",
            "feedback": "A resposta certa é Tornar os botões de ação primária grandes e posicioná-los em áreas de fácil alcance do polegar do usuário.\nComentário: A Lei de Fitts estabelece que alvos maiores e mais próximos da área de interação rápida reduzem o tempo de movimento e aumentam a precisão do toque.\nFonte: Interação Humano-Computador, UA 3."
        },
        {
            "ua": "04", "obj": 3, "grau": "MÉDIA", "kw": "Arquitetura de Informação e Testes de Card Sorting",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Uma equipe de Arquitetura de Informação precisa organizar as dezenas de categorias e subcategorias de um novo portal de e-commerce de departamento para garantir uma navegação intuitiva.\n\nPara compreender o modelo mental dos usuários e decidir como agrupar e nomear os menus do site de acordo com suas expectativas reais, a equipe organiza uma sessão de teste de **Card Sorting** (Ordenação de Cartões) com usuários representativos do público-alvo.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o funcionamento de um teste de Card Sorting Aberto:",
            "opt_a": "Os participantes organizam os cartões com os tópicos de conteúdo em grupos que façam sentido para eles e criam os próprios nomes para cada categoria.", "opt_b": "Os participantes devem inserir os cartões em categorias rígidas previamente definidas pelos desenvolvedores.", "opt_c": "O sistema sorteia aleatoriamente a posição de cada elemento sem intervenção humana.", "opt_d": "O teste avalia a velocidade de digitação do usuário em um formulário em branco.",
            "feedback": "A resposta certa é Os participantes organizam os cartões com os tópicos de conteúdo em grupos que façam sentido para eles e criam os próprios nomes para cada categoria.\nComentário: No Card Sorting Aberto, os usuários agrupam livremente os conceitos e dão nomes às categorias, revelando a estrutura mental do público.\nFonte: Interação Humano-Computador, UA 4."
        },
        {
            "ua": "06", "obj": 1, "grau": "DIFÍCIL", "kw": "Avaliação de Usabilidade por Avaliação Heurística de Nielsen",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um especialista em usabilidade realiza uma avaliação de IHC em um sistema de gestão acadêmica utilizando o método de inspeção da **Avaliação Heurística de Jakob Nielsen**.\n\nDurante a inspeção das telas de lançamento de notas pelos professores, o avaliador identifica que o sistema não exibe nenhuma indicação visual de que um salvamento está em andamento, deixando a tela travada sem feedback visual.",
            "afirmativas": "Com base nas 10 Heurísticas de Usabilidade de Nielsen, analise as afirmativas:\nI. A ausência de indicação visual sobre o processamento de salvar viola a heurística de 'Visibilidade do Estado do Sistema'.\nII. A heurística de 'Prevenção de Erros' recomenda criar interfaces que impeçam a ocorrência de erros graves antes mesmo que eles aconteçam.\nIII. A Avaliação Heurística é um método de teste com usuários reais que exige laboratório de ocularização (Eye Tracking).",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II aplicam corretamente as heurísticas de Nielsen de Visibilidade do Estado e Prevenção de Erros. A afirmativa III é falsa pois a Avaliação Heurística é um método de inspeção por especialistas, sem testes com usuários de laboratório.\nFonte: Interação Humano-Computador, UA 6."
        },
        {
            "ua": "08", "obj": 2, "grau": "DIFÍCIL", "kw": "Acessibilidade Web (WCAG 2.1) e Leitores de Tela",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Para atender às exigências legais de acessibilidade digital e às diretrizes internacionais do WCAG 2.1 (Web Content Accessibility Guidelines) no nível AA, um portal de serviços públicos passa por uma auditoria de acessibilidade.\n\nA equipe avalia a compatibilidade do código HTML5 do portal com tecnologias assistivas, como leitores de tela (ex: NVDA, JAWS ou TalkBack) utilizados por pessoas com deficiência visual.",
            "afirmativas": "Com base nas recomendações do WCAG 2.1 e acessibilidade digital, analise as afirmativas:\nI. Imagens informativas no HTML devem conter obrigatoriamente o atributo `alt` com texto alternativo descritivo para que leitores de tela possam narrar o conteúdo.\nII. Todos os elementos interativos do portal (botões, links, formulários) devem ser totalmente navegáveis utilizando exclusivamente o teclado (tecla Tab/Enter).\nIII. O contraste de cor entre o texto e o fundo da página não possui relevância para a acessibilidade visual de pessoas com baixa visão.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem requisitos fundamentais da WCAG para leitores de tela e navegação por teclado. A afirmativa III é falsa pois a WCAG 2.1 exige razão de contraste mínimo de 4.5:1 para texto normal.\nFonte: Interação Humano-Computador, UA 8."
        },
        {
            "ua": "08", "obj": 3, "grau": "DIFÍCIL", "kw": "Design Responsivo e Princípios de Mobile First",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Ao iniciar o projeto de uma nova aplicação web corporativa, a equipe de front-end adota a abordagem metodológica de desenvolvimento **Mobile First** (O Mobile Primeiro).\n\nEm vez de projetar primeiro a versão desktop para telas grandes e posteriormente tentar encolher os componentes para telas pequenas, a equipe projeta a experiência inicial para dispositivos móveis com recursos limitados.",
            "afirmativas": "Com base nos conceitos de Design Responsivo e abordagem Mobile First, analise as afirmativas:\n\nI. A abordagem Mobile First força a equipe de UI/UX a priorizar o conteúdo e as funcionalidades essenciais da aplicação, resultando em um código CSS/HTML mais limpo e otimizado via Media Queries progressivas (min-width).\n\nPORQUE\n\nII. Projetar para telas menores primeiro elimina o carregamento desnecessário de recursos pesados em dispositivos móveis, garantindo melhor desempenho e tempos de carregamento mais rápidos em redes celulares.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A priorização do conteúdo em telas pequenas e a otimização de performance justificam a adoção do Mobile First.\nFonte: Interação Humano-Computador, UA 8."
        }
    ],
    subfolder='PS'
)

# 10. Programação em PYTHON
create_exam(
    "Programação em Python(seg)", "Programação em PYTHON", "PS Programação em PYTHON", "3; 4; 7; 10",
    [
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Manipulação de Listas, Tuplas e Dicionários em Python",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em um script Python desenvolvido para processar o inventário de um almoxarifado, o programador utiliza diferentes estruturas de dados nativas para armazenar os produtos.\n\nEle precisa armazenar as coordenadas geográficas fixas do depósito (Latitude, Longitude) em uma estrutura de dados que garanta imutabilidade, impedindo alterações acidentais durante a execução do programa.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica a estrutura de dados nativa do Python que é imutável e representada por parênteses `()`:",
            "opt_a": "Tupla (tuple).", "opt_b": "Lista (list).", "opt_c": "Dicionário (dict).", "opt_d": "Conjunto (set).",
            "feedback": "A resposta certa é Tupla (tuple).\nComentário: Em Python, tuplas são sequências imutáveis; uma vez criadas, seus elementos não podem ser adicionados, removidos ou modificados.\nFonte: Programação em PYTHON, UA 3."
        },
        {
            "ua": "04", "obj": 3, "grau": "MÉDIA", "kw": "Compreensão de Listas (List Comprehensions) e Funções Lambda",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Um cientista de dados escreve um código Python para filtrar e transformar uma lista de números inteiros representando leituras de sensores de temperatura (`temperaturas = [18, 25, 31, 12, 40, 22]`).\n\nEle necessita criar uma nova lista contendo apenas os valores de temperatura superiores a 20 graus, multiplicados por 1.8 (conversão para escala Fahrenheit), utilizando a sintaxe pythônica expressiva e concisa em uma única linha de código.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta a expressão de Compreensão de Lista (List Comprehension) correta para essa transformação:",
            "opt_a": "[t * 1.8 for t in temperaturas if t > 20]", "opt_b": "[for t in temperaturas if t > 20 : t * 1.8]", "opt_c": "{t * 1.8 : t in temperaturas > 20}", "opt_d": "filter(lambda t: t > 20 * 1.8, temperaturas)",
            "feedback": "A resposta certa é [t * 1.8 for t in temperaturas if t > 20].\nComentário: A sintaxe padronizada de List Comprehension em Python é `[expressão for item in iterável if condição]`.\nFonte: Programação em PYTHON, UA 4."
        },
        {
            "ua": "07", "obj": 1, "grau": "DIFÍCIL", "kw": "Programação Orientada a Objetos em Python (Classes, Herança e @classmethod)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Em um sistema bancário desenvolvido em Python, o desenvolvedor estrutura a hierarquia de classes da aplicação utilizando Programação Orientada a Objetos (POO).\n\nA classe base `ContaBancaria` possui atributos de instância como `titular` e `_saldo`, e métodos decorados com `@classmethod` e `@staticmethod` para rotinas de fábrica de objetos e utilitários gerais.",
            "afirmativas": "Com base na POO em Python, analise as afirmativas:\nI. O parâmetro `self` no método de instância representa a própria referência do objeto concreto que está invocando o método.\nII. Métodos decorados com `@classmethod` recebem implicitamente a referência da própria classe (`cls`) como primeiro parâmetro.\nIII. Atributos iniciados com dois sublinhados (ex: `__saldo`) ativam a modificação de nome (Name Mangling) para impedir acesso direto de fora da classe.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I, II e III.", "opt_b": "I e II, apenas.", "opt_c": "I e III, apenas.", "opt_d": "II e III, apenas.",
            "feedback": "A resposta certa é I, II e III.\nComentário: Todas as afirmativas são verdadeiras. Elas descrevem com exatidão o papel do self, do decorador @classmethod e do Name Mangling para atributos privados em Python.\nFonte: Programação em PYTHON, UA 7."
        },
        {
            "ua": "10", "obj": 2, "grau": "DIFÍCIL", "kw": "Tratamento de Exceções (try-except-finally) e Criadores de Contexto (with)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Um programa Python abre um arquivo de dados texto no disco (`dados.txt`), lê seu conteúdo linha a linha e realiza operações de conversão de tipos de dados numéricos.\n\nPara evitar vazamento de recursos e garantir que o arquivo seja fechado corretamente mesmo se ocorrer um erro de conversão (`ValueError`) ou ausência de arquivo (`FileNotFoundError`), o desenvolvedor adota o bloco `with open(...)` e tratamento de exceções.",
            "afirmativas": "Com base no tratamento de exceções e instrução `with` em Python, analise as afirmativas:\nI. A instrução `with` utiliza o protocolo de Gerenciador de Contexto (`__enter__` e `__exit__`), garantindo que o arquivo seja fechado automaticamente ao sair do bloco.\nII. O bloco `finally` em uma estrutura `try-except-finally` é executado obrigatoriamente, independentemente de ter ocorrido uma exceção ou não.\nIII. O bloco `except` é ignorado se ocorrer um erro de divisão por zero durante a execução do `try`.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II estão corretas. O gerenciador de contexto e o bloco `finally` garantem a liberação segura de recursos. A afirmativa III é falsa pois o `except` correspondente (ex: `ZeroDivisionError`) é justamente acionado na ocorrência do erro.\nFonte: Programação em PYTHON, UA 10."
        },
        {
            "ua": "10", "obj": 3, "grau": "DIFÍCIL", "kw": "Manipulação de Dados em Arquivos JSON/CSV e Módulo pandas",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Um analista de dados precisa carregar um arquivo CSV contendo 500 mil linhas de dados de vendas diárias em uma estrutura de dados bidimensional em memória chamada `DataFrame` utilizando a biblioteca `pandas` em Python.\n\nEle executa o comando `df = pd.read_csv('vendas.csv')` e realiza operações de agrupamento (`groupby`) e cálculo de média de faturamento por região.",
            "afirmativas": "Com base no uso do Pandas para análise de dados em Python, analise as afirmativas:\n\nI. O DataFrame do Pandas armazena dados estruturados em linhas e colunas rotuladas, fornecendo métodos otimizados em linguagem C para filtragem, agregação e manipulação de grandes volumes de dados.\n\nPORQUE\n\nII. A biblioteca Pandas substitui a necessidade de utilizar qualquer banco de dados relacional SQL na infraestrutura da empresa.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "A afirmativa I é verdadeira, e a II é falsa.", "opt_b": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.", "opt_c": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.", "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é A afirmativa I é verdadeira, e a II é falsa.\nComentário: A afirmativa I descreve com exatidão a estrutura e performance do DataFrame do Pandas. A afirmativa II é falsa pois o Pandas é uma biblioteca de análise em memória, não um sistema gerenciador de banco de dados (SGBD) de persistência.\nFonte: Programação em PYTHON, UA 10."
        }
    ],
    subfolder='PS'
)

# 11. Programação em Python Eletiva
create_exam(
    "Programação em Python(seg)", "Programação em Python Eletiva", "PS Programação em Python Eletiva", "3; 4; 7; 10",
    [
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Estruturas de Dados Mutáveis e Imutáveis em Python",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Durante o desenvolvimento de um módulo de cache em memória para uma aplicação web Python, o desenvolvedor precisa escolher a estrutura de dados correta para armazenar pares de chave-valor onde as chaves devem ser obrigatoriamente objetos imutáveis e hasháveis.\n\nEle avalia o comportamento de tipos primitivos e compostos em relação à mutabilidade em memória no interpretador CPython.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica uma estrutura de dados mutável em Python que NÃO pode ser utilizada como chave de um dicionário:",
            "opt_a": "Lista (list).", "opt_b": "Tupla contendo apenas inteiros (tuple).", "opt_c": "String (str).", "opt_d": "Número inteiro (int).",
            "feedback": "A resposta certa é Lista (list).\nComentário: Listas são mutáveis e portanto não-hasháveis (unhashable type), o que impede seu uso como chaves de dicionários em Python.\nFonte: Programação em Python Eletiva, UA 3."
        },
        {
            "ua": "04", "obj": 3, "grau": "MÉDIA", "kw": "Decoradores (@decorator) e Funções de Primeira Classe em Python",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Em um framework web em Python (como Flask ou FastAPI), as rotas de requisição HTTP utilizam sintaxe de decorador `@app.route('/api')` sobre as funções manipuladoras.\n\nO desenvolvedor decide criar seu próprio decorador personalizado `@medir_tempo` para registrar o tempo de execução de funções de processamento pesado no log da aplicação.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta o conceito fundamental em Python que permite a criação e uso de decoradores:",
            "opt_a": "Funções são objetos de primeira classe (First-Class Functions), podendo ser passadas como argumentos e retornadas por outras funções.", "opt_b": "Python exige que todas as funções sejam compiladas em linguagem C antes da execução.", "opt_c": "Decoradores modificam diretamente o código-fonte do interpretador Python em tempo de execução.", "opt_d": "Decoradores funcionam exclusivamente dentro de classes herdadas de `type`.",
            "feedback": "A resposta certa é Funções são objetos de primeira classe (First-Class Functions), podendo ser passadas como argumentos e retornadas por outras funções.\nComentário: Em Python, funções são objetos comuns que podem ser envolvidos por funções de ordem superior (decoradores) para estender seu comportamento sem alterar seu código.\nFonte: Programação em Python Eletiva, UA 4."
        },
        {
            "ua": "07", "obj": 1, "grau": "DIFÍCIL", "kw": "Métodos Mágicos (__init__, __str__, __repr__) em Python",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Em uma biblioteca de matemática vetorial desenvolvida em Python, o engenheiro cria a classe `Vetor2D` e implementa os Métodos Mágicos (Dunder Methods) para permitir a sobrecarga de operadores aritméticos nativos (`v1 + v2`).\n\nEle sobrescreve os métodos `__add__`, `__eq__` e `__str__` para customizar a adição, comparação de igualdade e representação amigável em texto do objeto.",
            "afirmativas": "Com base nos Métodos Mágicos (Dunder Methods) em Python, analise as afirmativas:\nI. O método `__add__(self, outro)` é invocado automaticamente pelo interpretador quando o operador de adição `+` é aplicado entre dois objetos.\nII. O método `__str__(self)` define a representação em string informal do objeto exibida ao utilizar `print(objeto)`.\nIII. Sobrescrever métodos mágicos é proibido pela especificação da linguagem Python.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com precisão os métodos dunder `__add__` e `__str__`. A afirmativa III é falsa pois a sobrecarga de operadores via métodos dunder é um dos pilares do modelo de objetos do Python.\nFonte: Programação em Python Eletiva, UA 7."
        },
        {
            "ua": "10", "obj": 2, "grau": "DIFÍCIL", "kw": "Gerenciadores de Contexto Personalizados e Instrução with",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Para garantir que conexões a um banco de dados SQLite sejam abertas, comitadas e fechadas com segurança mesmo se ocorrerem exceções durante a transação, um desenvolvedor cria uma classe Gerenciadora de Contexto personalizada em Python.\n\nA classe implementa os dois métodos especiais do protocolo de contexto: `__enter__` e `__exit__`.",
            "afirmativas": "Com base nos Gerenciadores de Contexto em Python, analise as afirmativas:\nI. O método `__enter__` é executado ao iniciar o bloco `with`, retornando o recurso que será atribuído à variável do `as`.\nII. O método `__exit__` é executado automaticamente ao finalizar o bloco `with`, recebendo detalhes de eventuais exceções ocorridas para tratamento.\nIII. Se o método `__exit__` retornar `True`, o interpretador suprime a exceção e impede sua propagação.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I, II e III.", "opt_b": "I e II, apenas.", "opt_c": "I e III, apenas.", "opt_d": "II e III, apenas.",
            "feedback": "A resposta certa é I, II e III.\nComentário: Todas as afirmativas são verdadeiras. Elas detalham a mecânica exata dos métodos `__enter__` e `__exit__` do protocolo de contexto `with` em Python.\nFonte: Programação em Python Eletiva, UA 10."
        },
        {
            "ua": "10", "obj": 3, "grau": "DIFÍCIL", "kw": "Processamento Assíncrono com asyncio e Geradores (yield)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Em um serviço de web scraping de alta performance construído em Python para coletar cotações de ações de mil páginas web simultaneamente, o desenvolvedor utiliza o módulo `asyncio` e funções corrotinas definidas com `async def` e `await`.\n\nA arquitetura orientada a eventos do `asyncio` utiliza um Event Loop único para alternar a execução entre tarefas durante os tempos de espera de I/O de rede.",
            "afirmativas": "Com base na programação assíncrona com `asyncio` em Python, analise as afirmativas:\n\nI. A programação assíncrona com `asyncio` permite tratar milhares de conexões de I/O concorrentes na mesma thread sem a sobrecarga de criar threads do sistema operacional para cada tarefa.\n\nPORQUE\n\nII. A palavra-chave `await` cede voluntariamente o controle da execução de volta ao Event Loop enquanto aguarda a conclusão da operação de E/S pendente.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A cooperação voluntária via `await` é a mecânica exata que permite ao Event Loop do asyncio atingir altíssima concorrência em I/O Bound.\nFonte: Programação em Python Eletiva, UA 10."
        }
    ],
    subfolder='PS'
)

print("Batch PS 3 concluído.")
