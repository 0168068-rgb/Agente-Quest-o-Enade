# -*- coding: utf-8 -*-
"""
Batch TG 6: Disciplinas 19 a 23 (Provas TG 2026-4 - UAs Específicas do Tema Gerador e Contextualização ENADE > 7 linhas)
"""
from generate_full_batch import create_exam

# 19. Segurança da informação (UAs 2, 4)
create_exam(
    "Segurança da Informação", "Segurança da informação", "AD Segurança da informação", "2; 4",
    [
        {
            "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Princípio do Menor Privilégio (Principle of Least Privilege)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em uma reestruturação da política de controle de acesso de um banco de dados corporativo contendo informações financeiras sigilosas, a equipe de segurança revoga as contas de administradores com permissões irrestritas (`root`/`DBA`) utilizadas no dia a dia pelos funcionários.\n\nA equipe passa a conceder a cada usuário e aplicação apenas o nível estrito de permissões necessário para a execução de suas tarefas funcionais diárias.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica o princípio fundamental de segurança da informação aplicado nessa reestruturação:",
            "opt_a": "Princípio do Menor Privilégio (Least Privilege).", "opt_b": "Criptografia de Chave Pública Assimétrica.", "opt_c": "Segurança por Obscuridade.", "opt_d": "Não-Repúdio Obrigatório.",
            "feedback": "A resposta certa é Princípio do Menor Privilégio (Least Privilege).\nComentário: O princípio do menor privilégio estabelece que cada entidade deve ter acesso apenas às informações e recursos estritamente necessários para sua função legítima.\nFonte: Segurança da informação, UA 2."
        },
        {
            "ua": "02", "obj": 2, "grau": "MÉDIA", "kw": "Controles de Acesso Discricionário (DAC) vs Mandatório (MAC) vs Baseado em Papéis (RBAC)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Em um sistema de gestão de recursos humanos (RH), os funcionários da empresa são agrupados em papéis funcionais (ex: 'Analista de RH', 'Gerente de RH', 'Estagiário').\n\nAs permissões de leitura, escrita e exclusão de arquivos de prontuários são atribuídas aos papéis e não diretamente aos usuários individuais, facilitando a atribuição automática de privilégios quando um novo colaborador é contratado.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta a modelo de controle de acesso utilizado nesse sistema:",
            "opt_a": "RBAC (Role-Based Access Control - Controle de Acesso Baseado em Papéis).", "opt_b": "DAC (Discretionary Access Control).", "opt_c": "MAC (Mandatory Access Control).", "opt_d": "ABAC sem regras de contexto.",
            "feedback": "A resposta certa é RBAC (Role-Based Access Control - Controle de Acesso Baseado em Papéis).\nComentário: No RBAC, as permissões são associadas a papéis/funções da organização e os usuários são atribuídos a esses papéis, simplificando a gestão de acessos.\nFonte: Segurança da informação, UA 2."
        },
        {
            "ua": "04", "obj": 1, "grau": "DIFÍCIL", "kw": "Funções Hash Criptográficas (SHA-256 / SHA-3) e Propriedade de Resistência a Colisões",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Para garantir a integridade de um arquivo de atualização de software de 2 GB distribuído via internet, a equipe de segurança gera e publica o resumo criptográfico do arquivo calculado pelo algoritmo **SHA-256**.\n\nO cliente que baixa o arquivo calcula o hash localmente e compara a string hexadecimal resultante com o valor oficial publicado no site do fabricante.",
            "afirmativas": "Com base nas funções hash criptográficas (SHA-256), analise as afirmativas:\nI. Uma função hash criptográfica é unidirecional (One-Way), sendo computacionalmente inviável reverter o resumo hash para obter a mensagem original.\nII. A propriedade de resistência a colisões garante que é extremamente difícil encontrar duas mensagens distintas que produzam exatamente o mesmo resumo hash.\nIII. A alteração de um único bit no arquivo original modifica completamente o resumo hash gerado (Efeito Avalanche).",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I, II e III.", "opt_b": "I e II, apenas.", "opt_c": "I e III, apenas.", "opt_d": "II e III, apenas.",
            "feedback": "A resposta certa é I, II e III.\nComentário: Todas as afirmativas são verdadeiras. Elas definem com exatidão a unidirecionalidade, a resistência a colisões e o efeito avalanche das funções hash criptográficas como o SHA-256.\nFonte: Segurança da informação, UA 4."
        },
        {
            "ua": "04", "obj": 2, "grau": "DIFÍCIL", "kw": "Ataques de Análise de Frequência e Quebra de Senhas por Força Bruta / Dicionário",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Um perito forense computacional analisa uma lista de hashes de senhas vazadas de um sistema corporativo para identificar contas vulneráveis à quebra por ferramentas especializadas (como John the Ripper ou Hashcat).\n\nEle compara o desempenho de ataques de **Dicionário** (uso de listas de senhas populares), **Força Bruta** (testes exaustivos de combinações) e **Rainbow Tables** (tabelas pré-computadas de hash).",
            "afirmativas": "Com base nas técnicas de quebra e proteção de senhas, analise as afirmativas:\nI. Ataques de Dicionário testam sequencialmente milhares de palavras comuns e combinações frequentes de senhas previamente compiladas.\nII. Ataques de Força Bruta testam exaustivamente todas as combinações possíveis de caracteres até encontrar a senha correta.\nIII. Senhas compostas por 8 caracteres numéricos são mais seguras e difíceis de quebrar por força bruta do que senhas com 16 caracteres alfanuméricos e símbolos.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II diferenciam com exatidão ataques de dicionário e força bruta. A afirmativa III é falsa pois senhas numéricas curtas possuem espaço de busca minúsculo ($10^8$ combinações), quebradas em milissegundos.\nFonte: Segurança da informação, UA 4."
        },
        {
            "ua": "04", "obj": 3, "grau": "DIFÍCIL", "kw": "Armazenamento Seguro de Senhas com Salting e Algoritmos com Custo Iterativo (Bcrypt / Argon2)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Durante o desenvolvimento de um novo sistema de login para um portal bancário, o arquiteto de segurança exige que as senhas dos usuários nunca sejam armazenadas em texto claro e nem mesmo em hashes simples sem sal (como `MD5(senha)` ou `SHA256(senha)`).\n\nO sistema adota algoritmos de hash de senha projetados com custo computacional iterativo e adição de um valor aleatório único por usuário (**Salt**), como o **Bcrypt** ou **Argon2**.",
            "afirmativas": "Com base no armazenamento seguro de senhas com Salting e Bcrypt, analise as afirmativas:\n\nI. A inclusão de um Salt aleatório e único para cada senha antes de gerar o hash previne que atacantes utilizem tabelas pré-computadas (Rainbow Tables) e impede a identificação de senhas iguais de usuários diferentes.\n\nPORQUE\n\nII. Algoritmos como o Bcrypt possuem um fator de custo ajustável que torna a geração do hash intencionalmente lenta para a CPU/GPU, dificultando ataques de força bruta em massa.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. O Salt inutiliza Rainbow Tables (afirmativa I) e o fator de custo desacelera força bruta (afirmativa II); embora complementares, o Salt atua na unicidade do hash e o custo na desaceleração do cálculo.\nFonte: Segurança da informação, UA 4."
        }
    ],
    subfolder='AD'
)

# 20. Segurança da Informação e Legislação (UAs 2, 4)
create_exam(
    "Segurança da Informação e Legislação", "Segurança da Informação e Legislação", "AD Segurança da Informação e Legislação", "2; 4",
    [
        {
            "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Conceito de Dado Pessoal e Dado Anonimizado na LGPD",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Uma empresa de análise de mercado recebe um banco de dados de clientes para realizar um estudo estatístico sobre hábitos de consumo.\n\nAntes de iniciar o processamento, a empresa submete o banco de dados a um processo de **Anonimização** utilizando meios técnicos razoáveis, de forma que o dado não possa mais ser associado, direta ou indiretamente, a nenhum indivíduo específico.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta o status legal de um Dado Anonimizado sob a regência da LGPD (Lei 13.709/2018):",
            "opt_a": "O dado anonimizado não é considerado dado pessoal para os fins da LGPD, salvo se o processo for revertido com meios próprios.", "opt_b": "O dado anonimizado continua sendo classificado como dado pessoal sensível de alto risco.", "opt_c": "O dado anonimizado exige obrigatoriamente a aprovação diária do DPO para ser lido.", "opt_d": "A LGPD proíbe a utilização de dados anonimizados no Brasil.",
            "feedback": "A resposta certa é O dado anonimizado não é considerado dado pessoal para os fins da LGPD, salvo se o processo for revertido com meios próprios.\nComentário: O Artigo 12 da LGPD estabelece que dados anonimizados não são considerados dados pessoais para os fins da lei, pois perdem o vínculo de identificação com o titular.\nFonte: Segurança da Informação e Legislação, UA 2."
        },
        {
            "ua": "02", "obj": 2, "grau": "MÉDIA", "kw": "Papéis e Agentes de Tratamento de Dados (Controlador, Operador e Titular)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Uma loja de comércio eletrônico (Empresa X) contrata uma empresa terceirizada de computação em nuvem (Empresa Y) para armazenar o banco de dados de seus clientes cadastrados.\n\nA Empresa X define quais dados serão coletados e com quais finalidades, enquanto a Empresa Y apenas realiza o armazenamento e processamento conforme as instruções contratuais dadas pela Empresa X.",
            "afirmativas": "",
            "comando_text": "De acordo com as definições da LGPD, assinale a opção que classifica corretamente a Empresa X e a Empresa Y:",
            "opt_a": "Empresa X é a Controladora e Empresa Y é a Operadora.", "opt_b": "Empresa X é a Operadora e Empresa Y é o Titular.", "opt_c": "Empresa X é o DPO e Empresa Y é a ANPD.", "opt_d": "Ambas as empresas são classificadas exclusivamente como Titulares.",
            "feedback": "A resposta certa é Empresa X é a Controladora e Empresa Y é a Operadora.\nComentário: O Controlador (Empresa X) toma as decisões referentes ao tratamento de dados, enquanto o Operador (Empresa Y) realiza o tratamento em nome do controlador.\nFonte: Segurança da Informação e Legislação, UA 2."
        },
        {
            "ua": "04", "obj": 1, "grau": "DIFÍCIL", "kw": "Notificação Obrigatória de Incidentes de Segurança à ANPD e aos Titulares",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um servidor de banco de dados de um hospital privado sofreu uma invasão hacker que resultou no vazamento de exames e dados cadastrais de 50 mil pacientes.\n\nO Encarregado (DPO) e a equipe jurídica do hospital convocam uma reunião de emergência para cumprir os requisitos de **Notificação de Incidentes de Segurança** previstos no Artigo 48 da LGPD.",
            "afirmativas": "Com base no Artigo 48 da LGPD sobre comunicação de incidentes, analise as afirmativas:\nI. O controlador deve comunicar à Autoridade Nacional (ANPD) e aos titulares a ocorrência de incidente de segurança que possa acarretar risco ou dano relevante aos titulares.\nII. A comunicação deve ser feita em prazo razoável, mencionando a descrição da natureza dos dados afetados, as medidas de segurança adotadas e os riscos envolvidos.\nIII. O hospital pode manter o vazamento em sigilo total sem notificar ninguém para preservar a reputação da marca.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II refletem a obrigação legal do Artigo 48 da LGPD sobre notificação de incidentes relevantes. A afirmativa III é falsa pois a omissão na comunicação sujeita a empresa a sanções administrativas graves da ANPD.\nFonte: Segurança da Informação e Legislação, UA 4."
        },
        {
            "ua": "04", "obj": 2, "grau": "DIFÍCIL", "kw": "Avaliação de Legítimo Interesse (LIA - Legitimate Interest Assessment)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Uma empresa de software deseja tratar dados pessoais de potenciais clientes corporativos para envio de e-mails de prospecção de vendas (Marketing B2B) baseando-se na hipótese legal do **Legítimo Interesse do Controlador** (Artigo 7º, IX da LGPD).\n\nPara validar a legalidade dessa operação, o DPO realiza a **Avaliação de Impacto de Legítimo Interesse** (LIA - Legitimate Interest Assessment).",
            "afirmativas": "Com base na hipótese do Legítimo Interesse e no LIA, analise as afirmativas:\nI. O Legítimo Interesse só pode fundamentar o tratamento para finalidades legítimas e alinhadas às expectativas razoáveis do titular.\nII. O teste de proporcionalidade do LIA pondera o interesse legítimo da empresa contra os direitos e liberdades fundamentais do titular.\nIII. O Legítimo Interesse pode ser utilizado livremente para o tratamento de Dados Pessoais Sensíveis sem qualquer restrição.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão o teste de proporcionalidade do LIA. A afirmativa III é falsa pois o Artigo 11 da LGPD NÃO inclui o Legítimo Interesse como hipótese legal para tratamento de Dados Pessoais Sensíveis.\nFonte: Segurança da Informação e Legislação, UA 4."
        },
        {
            "ua": "04", "obj": 3, "grau": "DIFÍCIL", "kw": "Responsabilidade Solidária e Reparação de Danos Patrimoniais na LGPD",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Um vazamento de dados de cartão de crédito causado por negligência na segurança de uma empresa operadora terceirizada causou fraudes financeiras e prejuízos materiais a centenas de clientes de um portal de e-commerce (controlador).\n\nOs clientes lesados ajuizaram ação judicial de reparação de danos contra ambas as empresas com base nos Artigos 42 a 45 da LGPD.",
            "afirmativas": "Com base na responsabilidade civil e reparação de danos na LGPD, analise as afirmativas:\n\nI. O controlador ou o operador que, em razão do exercício de atividade de tratamento de dados pessoais, causar a outrem dano patrimonial, moral, individual ou coletivo, é obrigado a repará-lo.\n\nPORQUE\n\nII. A LGPD prevê a responsabilidade solidária entre controlador e operador em casos de violação da segurança que causem danos, para assegurar a efetiva indenização aos titulares lesados.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. O dever geral de indenizar os danos causados e a responsabilidade solidária dos agentes de tratamento fundamentam o ressarcimento aos titulares.\nFonte: Segurança da Informação e Legislação, UA 4."
        }
    ],
    subfolder='AD'
)

# 21. Segurança de redes de computadores (UAs 2, 6)
create_exam(
    "Segurança de Redes de Computadores", "Segurança de redes de computadores", "AD Segurança de redes de computadores", "2; 6",
    [
        {
            "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Filtragem de Pacotes por Regras de Tabela de Firewall (ACLs de Entrada e Saída)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em um roteador ou firewall perimetral, o administrador de redes configura uma Listas de Controle de Acesso (ACL - Access Control List) para bloquear o tráfego não autorizado vindo da internet pública.\n\nA tabela de regras do firewall inspeciona os cabeçalhos IP/TCP/UDP de cada pacote e aplica a política de segurança de cima para baixo de forma sequencial.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica a regra padrão implícita que existe no final de qualquer tabela de firewall ou ACL sem exceção:",
            "opt_a": "Deny All (Negação Implícita de todo o tráfego não explicitamente permitido).", "opt_b": "Permit All (Permissão irrestrita de todo o tráfego).", "opt_c": "Encrypt All (Criptografia de todos os pacotes).", "opt_d": "Redirect All (Redirecionamento para o Google).",
            "feedback": "A resposta certa é Deny All (Negação Implícita de todo o tráfego não explicitamente permitido).\nComentário: Toda ACL/Firewall possui uma regra implícita final 'deny any any' (Deny All), bloqueando tudo o que não foi explicitamente autorizado nas regras anteriores.\nFonte: Segurança de redes de computadores, UA 2."
        },
        {
            "ua": "02", "obj": 2, "grau": "MÉDIA", "kw": "Zonas de Segurança de Firewall (Inside, Outside e DMZ)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Um engenheiro de segurança configura um firewall corporativo dividindo a infraestrutura física de rede em três zonas lógicas de segurança com níveis de confiança distintos: Zona Interna (Inside), Zona Externa (Outside) e Zona Desmilitarizada (DMZ).\n\nEle necessita criar a política de controle de fluxo de tráfego permitindo conexões originadas da rede interna em direção a qualquer zona, mas restringindo severamente conexões originadas da internet.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o nível de confiança padrão das zonas de segurança em firewalls corporativos:",
            "opt_a": "Inside (Maior Confiança - 100), DMZ (Média Confiança - 50) e Outside (Nenhuma Confiança - 0).", "opt_b": "Outside possui maior confiança que a zona Inside.", "opt_c": "Todas as zonas possuem obrigatoriamente a mesma confiança nula.", "opt_d": "A DMZ é a única zona conectada à rede elétrica.",
            "feedback": "A resposta certa é Inside (Maior Confiança - 100), DMZ (Média Confiança - 50) e Outside (Nenhuma Confiança - 0).\nComentário: Zonas de firewall utilizam níveis de confiança para liberar por padrão tráfego de maior confiança para menor confiança e bloquear o fluxo inverso sem regras explícitas.\nFonte: Segurança de redes de computadores, UA 2."
        },
        {
            "ua": "06", "obj": 1, "grau": "DIFÍCIL", "kw": "Posicionamento de Sensores IDS Baseados em Host (HIDS) vs Rede (NIDS)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Para implementar a detecção de intrusão em camadas (Defesa em Profundidade), a equipe de segurança instala sensores de **NIDS** (Network-based IDS) em portas de espelhamento (SPAN) de switches e agentes de **HIDS** (Host-based IDS) em servidores de banco de dados críticos.\n\nEles comparam a capacidade de visibilidade de ataques fornecida por ambas as abordagens.",
            "afirmativas": "Com base em NIDS e HIDS, analise as afirmativas:\nI. O NIDS inspeciona cópias do tráfego de rede capturado em pontos estratégicos da topologia, detectando varreduras de portas e exploits de rede.\nII. O HIDS roda dentro do sistema operacional do servidor hospedeiro, inspecionando chamadas de sistema, logs locais e alterações em arquivos de sistema.\nIII. O NIDS é capaz de decodificar e ler todo o conteúdo de payloads criptografados por TLS que passam pela rede sem possuir as chaves privadas.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II caracterizam corretamente o escopo de rede do NIDS e o escopo local de host do HIDS. A afirmativa III é falsa pois o NIDS na rede não consegue inspecionar o payload criptografado por TLS sem decodificação.\nFonte: Segurança de redes de computadores, UA 6."
        },
        {
            "ua": "06", "obj": 2, "grau": "DIFÍCIL", "kw": "Falsos Positivos vs Falsos Negativos em Sistemas de Detecção de Intrusão",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Durante a calibração das regras de detecção de um sistema IDS/IPS corporativo, a equipe de SOC (Security Operations Center) analisa a taxa de ocorrência de **Falsos Positivos** e **Falsos Negativos** nos relatórios de alertas diários.\n\nUm excesso de alertas irrelevantes causa a fadiga de alertas (Alert Fatigue) na equipe, enquanto falhas de detecção omitem ataques reais.",
            "afirmativas": "Com base nas métricas de acurácia de um IDS/IPS, analise as afirmativas:\nI. Um Falso Positivo ocorre quando o IDS gera um alerta de segurança para uma atividade de rede legítima e inofensiva.\nII. Um Falso Negativo ocorre quando um ataque malicioso real transita pela rede sem ser detectado ou alertado pelo IDS.\nIII. Falsos Negativos são inofensivos e não trazem qualquer risco de comprometimento aos servidores.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão Falso Positivo (alarme falso) e Falso Negativo (ataque não detectado). A afirmativa III é falsa pois Falsos Negativos são as falhas de segurança mais perigosas de um IDS.\nFonte: Segurança de redes de computadores, UA 6."
        },
        {
            "ua": "06", "obj": 3, "grau": "DIFÍCIL", "kw": "Arquiteturas de Honeypots e Honeynets para Coleta de Inteligência sobre Atacantes",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Uma equipe de pesquisa em cibersegurança instala um servidor propositalmente vulnerável e desprovido de qualquer valor produtivo (**Honeypot**) em um segmento isolado da internet.\n\nO objetivo é atrair cibercriminosos e malwares automatizados para analisar suas táticas, técnicas e procedimentos (TTPs) e capturar amostras inéditas de exploit.",
            "afirmativas": "Com base no uso de Honeypots e Honeynets em segurança, analise as afirmativas:\n\nI. Qualquer tentativa de conexão ou acesso a um Honeypot é considerada suspeita por definição, pois o ambiente não executa nenhum serviço produtivo e não possui usuários legítimos.\n\nPORQUE\n\nII. Honeypots atuam como armadilhas de monitoramento que registram detalhadamente os comandos e ferramentas utilizadas por atacantes sem colocar os sistemas de produção reais em risco.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A ausência de tráfego legítimo no Honeypot garante que qualquer interação seja tratada como atividade maliciosa/suspeita, justificando a coleta de inteligência.\nFonte: Segurança de redes de computadores, UA 6."
        }
    ],
    subfolder='AD'
)

# 22. Servidores e Computação na Nuvem (UAs 3, 4)
create_exam(
    "Servidores e computação na Nuvem", "Servidores e Computação na Nuvem", "AD Servidores e Computação na Nuvem", "3; 4",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Isolamento de Processos em Containers Linux via Namespaces e CGroups",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "No nível do sistema operacional Linux hospedeiro, o mecanismo do Docker utiliza dois recursos nativos do Kernel do Linux para garantir que os contêineres rodem de forma isolada e segura.\n\nEle utiliza **Namespaces** para criar o isolamento de visão dos processos, rede e sistemas de arquivos, e **Control Groups (cgroups)** para limitar o consumo de recursos computacionais.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica a função primária dos Control Groups (cgroups) no isolamento de contêineres Linux:",
            "opt_a": "Limitar e alocar a quantidade máxima de CPU, memória RAM e I/O de disco que cada contêiner pode consumir.", "opt_b": "Criptografar as senhas de banco de dados salvas em disco.", "opt_c": "Gerar endereços IPv4 públicos para o Docker Hub.", "opt_d": "Substituir a necessidade do Kernel do sistema operacional.",
            "feedback": "A resposta certa é Limitar e alocar a quantidade máxima de CPU, memória RAM e I/O de disco que cada contêiner pode consumir.\nComentário: Os cgroups do kernel Linux gerenciam a alocação e limites de recursos físicos (CPU, RAM, I/O) consumidos pelos grupos de processos dos contêineres.\nFonte: Servidores e Computação na Nuvem, UA 3."
        },
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Registros de Imagens de Containers (Docker Hub / Quay / ECR) e Imagens Privadas",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Após a equipe de desenvolvimento construir e testar a imagem Docker de uma nova versão da API corporativa (`empresa/api:v2.0`), ela precisa disponibilizar esse artefato para que os servidores de produção em nuvem consigam baixá-lo via comando `docker pull`.\n\nA imagem é enviada para um servidor centralizado de armazenagem e distribuição de imagens de contêiner chamado **Container Registry**.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o comando da CLI do Docker utilizado para enviar uma imagem local para um Container Registry público ou privado:",
            "opt_a": "docker push empress/api:v2.0", "opt_b": "docker commit empress/api:v2.0", "opt_c": "docker build empress/api:v2.0", "opt_d": "docker run empress/api:v2.0",
            "feedback": "A resposta certa é docker push empress/api:v2.0.\nComentário: O comando `docker push` faz o upload do artefato da imagem compilada localmente para o Container Registry remoto.\nFonte: Servidores e Computação na Nuvem, UA 3."
        },
        {
            "ua": "04", "obj": 1, "grau": "DIFÍCIL", "kw": "Componentes do Control Plane do Kubernetes (API Server, etcd, Scheduler, Controller Manager)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Em um cluster Kubernetes de produção de alta disponibilidade, o plano de controle (**Control Plane** / Master Nodes) gerencia o estado e as decisões de implantação de toda a infraestrutura de contêineres.\n\nO Control Plane é composto pelos módulos **kube-apiserver**, **etcd**, **kube-scheduler** e **kube-controller-manager**.",
            "afirmativas": "Com base nos componentes do Control Plane do Kubernetes, analise as afirmativas:\nI. O `kube-apiserver` é o ponto de entrada central que expõe a API do Kubernetes e valida todas as requisições de controle.\nII. O `etcd` é um banco de dados chave-valor distribuído altamente disponível que armazena o estado persistente de todo o cluster.\nIII. O `kube-scheduler` é o módulo responsável por selecionar em qual nó de trabalho (Worker Node) cada novo Pod deve ser executado.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I, II e III.", "opt_b": "I e II, apenas.", "opt_c": "I e III, apenas.", "opt_d": "II e III, apenas.",
            "feedback": "A resposta certa é I, II e III.\nComentário: Todas as afirmativas são verdadeiras. Elas descrevem com exatidão os papeis essenciais do API Server, do banco etcd e do Scheduler no Control Plane do Kubernetes.\nFonte: Servidores e Computação na Nuvem, UA 4."
        },
        {
            "ua": "04", "obj": 2, "grau": "DIFÍCIL", "kw": "Serviços de Exposição de Rede no Kubernetes (ClusterIP, NodePort e LoadBalancer)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Para permitir a comunicação de rede entre conjuntos de Pods e expor aplicações para a internet pública, o Kubernetes utiliza a abstração de objetos do tipo **Service**.\n\nO desenvolvedor configura o arquivo manifesto selecionando o tipo de serviço apropriado: **ClusterIP**, **NodePort** ou **LoadBalancer**.",
            "afirmativas": "Com base nos tipos de Service no Kubernetes, analise as afirmativas:\nI. O tipo `ClusterIP` (padrão) expõe o serviço apenas em um IP interno privado do cluster, acessível somente por outros Pods internos.\nII. O tipo `NodePort` expõe o serviço em uma porta estática aberta na interface IP de cada Nó do cluster.\nIII. O tipo `LoadBalancer` provisiona automaticamente um balanceador de carga de nuvem pública (ex: AWS ELB) para rotear o tráfego externo para o serviço.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I, II e III.", "opt_b": "I e II, apenas.", "opt_c": "I e III, apenas.", "opt_d": "II e III, apenas.",
            "feedback": "A resposta certa é I, II e III.\nComentário: Todas as afirmativas são verdadeiras. Elas definem adequadamente a exposição interna do ClusterIP, a porta de nó do NodePort e a integração em nuvem do LoadBalancer.\nFonte: Servidores e Computação na Nuvem, UA 4."
        },
        {
            "ua": "04", "obj": 3, "grau": "DIFÍCIL", "kw": "Armazenamento Persistente no Kubernetes (PersistentVolumes e PVCs)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Como contêineres Docker são efêmeros por natureza (dados gravados dentro do contêiner são perdidos quando o contêiner é destruído ou reiniciado), a implantação de um banco de dados em Kubernetes exige armazenamento persistente desacoplado.\n\nO Kubernetes gerencia a alocação de armazenamento através dos objetos **PersistentVolume** (PV) e **PersistentVolumeClaim** (PVC).",
            "afirmativas": "Com base em armazenamento persistente em Kubernetes, analise as afirmativas:\n\nI. O `PersistentVolumeClaim` (PVC) é uma solicitação de armazenamento enviada pelo desenvolvedor que especifica o tamanho em gigabytes e o modo de acesso desejado, desvinculando a aplicação dos detalhes físicos da infraestrutura de armazenamento.\n\nPORQUE\n\nII. O subsistema de armazenamento do Kubernetes realiza o provisionamento dinâmico vinculando automaticamente um `PersistentVolume` (PV) correspondente ao PVC solicitado.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. O PVC abstrai o pedido de disco e o provisionador dinâmico aloca o PV físico correspondente, garantindo persistência desacoplada.\nFonte: Servidores e Computação na Nuvem, UA 4."
        }
    ],
    subfolder='AD'
)

# 23. Sistemas Operacionais de Redes Abertas (UAs 2, 5)
create_exam(
    "Sistemas Operacionais de Redes Abertas", "Sistemas Operacionais de Redes Abertas", "AD Sistemas Operacionais de Redes Abertas", "2; 5",
    [
        {
            "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Estrutura do Sistema de Arquivos em Linux (FHS - Filesystem Hierarchy Standard)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em um servidor Linux de redes abertas (como Ubuntu Server ou Debian), a organização dos diretórios do sistema segue a norma padrão **FHS** (Filesystem Hierarchy Standard).\n\nUm analista de suporte precisa localizar os arquivos de configuração dos serviços de rede (como o arquivo de interfaces ou configurações do SSH) no sistema de arquivos raiz (`/`).",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica o diretório padrão do Linux reservado para armazenar os arquivos de configuração do sistema e dos serviços instalados:",
            "opt_a": "/etc", "opt_b": "/var", "opt_c": "/bin", "opt_d": "/home",
            "feedback": "A resposta certa é /etc.\nComentário: Segundo o padrão FHS em sistemas Linux, o diretório `/etc` contém todos os arquivos de configuração do sistema e programas.\nFonte: Sistemas Operacionais de Redes Abertas, UA 2."
        },
        {
            "ua": "02", "obj": 2, "grau": "MÉDIA", "kw": "Gerenciamento de Permissões de Arquivos em Linux (chmod, chown e Octal 755/644)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Um administrador de sistemas Linux altera as permissões de acesso de um script de inicialização de rede (`/etc/init.d/rede.sh`) utilizando o comando `chmod 755 rede.sh` em notação octal.\n\nEle precisa compreender os privilégios atribuídos ao Dono (Owner), ao Grupo (Group) e aos Outros usuários (Others).",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica os direitos de acesso concedidos pela permissão octal `755` (`rwxr-xr-x`) em um arquivo no Linux:",
            "opt_a": "Dono: Leitura, Escrita e Execução (7); Grupo e Outros: Leitura e Execução (5).", "opt_b": "Dono, Grupo e Outros possuem acesso total irrestrito (777).", "opt_c": "Apenas o dono pode ler o arquivo.", "opt_d": "O arquivo é bloqueado contra qualquer tipo de leitura.",
            "feedback": "A resposta certa é Dono: Leitura, Escrita e Execução (7); Grupo e Outros: Leitura e Execução (5).\nComentário: Na notação octal do Linux, r(4)+w(2)+x(1) = 7 para o Dono, e r(4)+x(1) = 5 para Grupo e Outros.\nFonte: Sistemas Operacionais de Redes Abertas, UA 2."
        },
        {
            "ua": "05", "obj": 1, "grau": "DIFÍCIL", "kw": "Gerenciamento de Processos Linux (ps, top, kill, systemctl) e Sinalizadores",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um servidor Linux de redes travou o serviço do servidor web Apache que parou de responder na porta 80. O administrador acessa o servidor por SSH para interromper o processo travado e reiniciar o serviço.\n\nEle utiliza comandos de gerenciamento de processos como `ps aux`, `kill` e `systemctl`.",
            "afirmativas": "Com base no gerenciamento de processos e serviços em Linux, analise as afirmativas:\nI. O comando `systemctl restart apache2` instrui o gerenciador de sistema e serviços Systemd a reiniciar o serviço do Apache.\nII. O comando `kill -9 <PID>` envia o sinal `SIGKILL` ao processo, forçando sua interrupção imediata pelo kernel do Linux.\nIII. O comando `ps aux` apaga todos os processos em execução no sistema operacional.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com exatidão o gerenciamento via systemctl e o envio do sinal SIGKILL pelo comando `kill -9`. A afirmativa III é falsa pois o `ps aux` apenas lista os processos ativos na tela sem alterá-los.\nFonte: Sistemas Operacionais de Redes Abertas, UA 5."
        },
        {
            "ua": "05", "obj": 2, "grau": "DIFÍCIL", "kw": "Configuração de Redes Abertas em Linux (iproute2, Netplan e arquivos /etc/network/interfaces)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Em uma distribuição Linux moderna como o Ubuntu Server 22.04 LTS, a configuração de interfaces de rede físicas e virtuais é gerenciada pelo utilitário **Netplan** utilizando arquivos de especificação YAML posicionados em `/etc/netplan/`.\n\nO administrador configura o IP estático, máscara, gateway e DNS da interface `eth0` e aplica as alterações com o comando `netplan apply`.",
            "afirmativas": "Com base na configuração de rede em sistemas Linux modernos com Netplan e iproute2, analise as afirmativas:\nI. O comando `ip addr show` do pacote `iproute2` substitui o utilitário legado `ifconfig` para exibir os endereços IP das interfaces de rede.\nII. O utilitário Netplan utiliza sintaxe YAML com controle rigoroso de indentação de espaços para definir as configurações de rede.\nIII. O comando `netplan apply` exige a reinicialização física completa do servidor para aplicar as alterações de IP.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com precisão a suíte iproute2 e a sintaxe do Netplan. A afirmativa III é falsa pois o Netplan aplica as alterações em tempo de execução sem necessitar de reboot do servidor.\nFonte: Sistemas Operacionais de Redes Abertas, UA 5."
        },
        {
            "ua": "05", "obj": 3, "grau": "DIFÍCIL", "kw": "Servidores de Arquivo de Código Aberto (Samba / NFS) em Redes Heterogêneas",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Em um ambiente corporativo com rede heterogênea contendo servidores Linux e clientes Windows de estações de trabalho, o administrador instala e configura o serviço **Samba** (`smbd`/`nmbd`).\n\nO serviço Samba permite que o servidor Linux compartilhe pastas e impressoras na rede local utilizando o protocolo padrão SMB/CIFS nativo do Windows.",
            "afirmativas": "Com base no uso de servidores Samba e NFS em redes abertas, analise as afirmativas:\n\nI. O servidor Samba implementa os protocolos SMB/CIFS em Linux, permitindo que clientes Windows acessem compartilhamentos de arquivos de forma transparente com controle de permissões de usuário.\n\nPORQUE\n\nII. O protocolo NFS (Network File System) é a solução padrão recomendada para compartilhamento nativo de alto desempenho de arquivos entre sistemas operacionais estritamente Linux/Unix.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. O Samba é a solução para redes heterogêneas Windows/Linux (afirmativa I) e o NFS é a solução para redes homogêneas Linux/Unix (afirmativa II); são duas soluções complementares para cenários distintos.\nFonte: Sistemas Operacionais de Redes Abertas, UA 5."
        }
    ],
    subfolder='AD'
)

print("Batch TG 6 concluído.")
