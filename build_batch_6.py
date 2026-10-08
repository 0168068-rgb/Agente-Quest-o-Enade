# -*- coding: utf-8 -*-
"""
Batch 6: Disciplinas 19 a 22 (Versão ENADE Expandida - Caso Prático Robusto > 7 linhas)
"""
from generate_full_batch import create_exam

# 19. Segurança da informação
create_exam(
    "Segurança da Informação", "Segurança da informação", "AI Segurança da informação", "2; 4; 7; 10",
    [
        {
            "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Tríade CIA (Confidencialidade, Integridade e Disponibilidade)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Ao estruturar a política de segurança da informação (PSI) de uma instituição hospitalar de grande porte, a equipe de TI estabelece controles de acesso e auditoria para impedir que prontuários médicos e históricos de pacientes sejam modificados de forma não autorizada ou acidental por usuários ou softwares maliciosos.\n\nA equipe busca assegurar a exatidão, a completude e a garantia de que as informações armazenadas no banco de dados reflitam fielmente o estado real dos diagnósticos médicos sem qualquer tipo de alteração indevida ou corrupção.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o pilar fundamental da segurança da informação focado em garantir a exatidão, completude e salvaguarda dos dados contra modificações indevidas:",
            "opt_a": "Integridade.", "opt_b": "Confidencialidade.", "opt_c": "Disponibilidade.", "opt_d": "Não-repúdio.",
            "feedback": "A resposta certa é Integridade.\nComentário: A Integridade assegura que a informação seja mantida em seu estado original, sem alterações, adulterações ou exclusões não autorizadas.\nFonte: Segurança da informação, UA 2."
        },
        {
            "ua": "04", "obj": 2, "grau": "MÉDIA", "kw": "Criptografia Simétrica vs Criptografia Assimétrica",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Um sistema de comunicação corporativa segura implementa um protocolo híbrido de criptografia (como TLS/SSL) para proteger os dados em trânsito na internet. O protocolo utiliza algoritmos de chave pública assimétrica (como RSA ou ECC) exclusivamente na fase inicial de estabelecimento de sessão (Handshake) para autenticar as partes e negociar com segurança uma chave secreta compartilhada.\n\nNas etapas subsequentes de transferência de grandes arquivos de dados e streams de vídeo, o sistema chaveia automaticamente para a criptografia simétrica (como AES-256), aproveitando sua alta eficiência computacional.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta a principal razão computacional para utilizar algoritmos de chave simétrica (AES) no encriptamento de grandes arquivos de dados:",
            "opt_a": "A criptografia simétrica é ordens de grandeza mais rápida e computacionalmente menos onerosa que a assimétrica.", "opt_b": "A chave simétrica pode ser publicada abertamente na internet sem comprometer o sigilo.", "opt_c": "A criptografia simétrica dispensa o uso de qualquer chave matemática.", "opt_d": "A criptografia assimétrica não suporta chaves maiores que 64 bits.",
            "feedback": "A resposta certa é A criptografia simétrica é ordens de grandeza mais rápida e computacionalmente menos onerosa que a assimétrica.\nComentário: Algoritmos simétricos utilizam operações de deslocamento/substituição de blocos altamente eficientes em hardware, ideais para dados extensos.\nFonte: Segurança da informação, UA 4."
        },
        {
            "ua": "07", "obj": 3, "grau": "DIFÍCIL", "kw": "Engenharia Social e Ataques de Phishing/Ransomware",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um funcionário do departamento financeiro de uma empresa recebe um e-mail com aparência legítima simulando uma notificação urgente da instituição bancária corporativa. A mensagem alerta sobre uma suposta pendência cadastral e induz o usuário a clicar em um link malicioso que o direciona para uma página falsa de captura de credenciais, além de executar em segundo plano um arquivo anexo contendo um programa malicioso.\n\nO malware inicia imediatamente a criptografia não autorizada de todos os arquivos armazenados no disco local e nos mapeamentos de rede corporativa, exibindo uma tela de resgate que exige pagamento em criptomoedas para o fornecimento da chave de decodificação.",
            "afirmativas": "Com base nas ameaças de Engenharia Social e Malware, analise as afirmativas:\nI. O ataque de Phishing explora a vulnerabilidade humana e a persuasão psicológica para capturar credenciais de acesso sigilosas.\nII. O Ransomware é um tipo de malware que criptografa os arquivos da vítima e exige o pagamento de resgate para fornecer a chave de decodificação.\nIII. A instalação de um antivírus corporativo elimina completamente o risco de funcionários caírem em ataques de engenharia social por e-mail.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com precisão Phishing e Ransomware. A afirmativa III é falsa pois o fator humano exige treinamento contínuo de conscientização em segurança, que nenhum software previne 100%.\nFonte: Segurança da informação, UA 7."
        },
        {
            "ua": "10", "obj": 1, "grau": "DIFÍCIL", "kw": "Gestão de Riscos (ISO 27005) e Avaliação de Impacto",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Durante o processo de análise e avaliação de riscos de segurança da informação conduzido segundo as diretrizes da norma internacional ISO/IEC 27005, o gestor de TI identifica os ativos críticos, avalia as ameaças existentes e mapeia as vulnerabilidades presentes na infraestrutura corporativa.\n\nApós o levantamento inicial, a equipe projeta o plano de tratamento de riscos selecionando controles de segurança para mitigar as ameaças identificadas, analisando os conceitos de Risco Inerente, Risco Residual e as estratégias de tratamento (Mitigar, Transferir, Evitar, Aceitar).",
            "afirmativas": "Com base nos conceitos de Gestão de Riscos em Segurança da Informação, analise as afirmativas:\nI. O Risco Residual é o nível de risco que permanece após a implementação dos controles de segurança e mitigações planejadas.\nII. As opções de tratamento de risco incluem: Mudar/Mitigar, Transferir (ex: seguro), Evitar e Aceitar o risco.\nIII. O Risco Inerente considera o impacto da ameaça somente após a aplicação de todos os controles de segurança de última geração.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem corretamente Risco Residual e as 4 estratégias de tratamento de risco. A afirmativa III é falsa pois Risco Inerente é o risco bruto ANTES da aplicação de qualquer controle.\nFonte: Segurança da informação, UA 10."
        },
        {
            "ua": "10", "obj": 2, "grau": "DIFÍCIL", "kw": "Infraestrutura de Chaves Públicas (ICP-Brasil e Certificados X.509)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Uma empresa de contabilidade e auditoria assina digitalmente contratos comerciais e emite notas fiscais eletrônicas com validade jurídica no Brasil utilizando certificados digitais ICP-Brasil padronizados pela norma X.509.\n\nO processo de assinatura digital utiliza a chave privada do titular para gerar o hash assinado do documento, permitindo que qualquer destinatário valide publicamente a autenticidade, a integridade do arquivo e a irretratabilidade da autoria com base na confiança da Autoridade Certificadora (AC).",
            "afirmativas": "Com base no funcionamento da Infraestrutura de Chaves Públicas (PKI / X.509), analise as afirmativas:\n\nI. A assinatura digital baseada em chave privada de um certificado digital X.509 válido garante autenticidade, integridade do documento e a propriedade do Não-Repúdio (irrefutabilidade).\n\nPORQUE\n\nII. Uma Autoridade Certificadora (AC) confiável valida a identidade do titular e assina digitalmente o certificado contendo a chave pública correspondente à chave privada mantida em sigilo exclusivo pelo titular.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. O vínculo de confiança estabelecido pela Autoridade Certificadora na chave pública é o pilar que confere o valor legal de Não-Repúdio à assinatura digital.\nFonte: Segurança da informação, UA 10."
        }
    ]
)

# 20. Segurança da Informação e Legislação
create_exam(
    "Segurança da Informação e Legislação", "Segurança da Informação e Legislação", "AI Segurança da Informação e Legislação", "2; 4; 7; 8",
    [
        {
            "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Lei Geral de Proteção de Dados (LGPD - Lei 13.709/2018)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Uma fintech de serviços financeiros coleta dados pessoais de seus clientes (nome, CPF, endereço, histórico de transações e biometria facial) para efetuar o cadastro e processamento de operações de crédito.\n\nPara garantir a conformidade legal com a Lei Geral de Proteção de Dados (LGPD - Lei 13.709/2018), a diretoria da empresa precisa designar formalmente o profissional responsável por atuar como canal de comunicação entre a organização controladora, os titulares dos dados pessoais e a Autoridade Nacional de Proteção de Dados (ANPD).",
            "afirmativas": "",
            "comando_text": "De acordo com a LGPD, assinale a opção que indica o profissional indicado pelo controlador e operador para atuar como canal de comunicação entre a empresa, os titulares dos dados e a Autoridade Nacional de Proteção de Dados (ANPD):",
            "opt_a": "DPO (Data Protection Officer - Encarregado pelo Tratamento de Dados Pessoais).", "opt_b": "CISO (Chief Information Security Officer).", "opt_c": "DBA (Database Administrator).", "opt_d": "Auditor Externo ISO 27001.",
            "feedback": "A resposta certa é DPO (Data Protection Officer - Encarregado pelo Tratamento de Dados Pessoais).\nComentário: O Encarregado (DPO) é a figura legal exigida pelo Artigo 41 da LGPD para intermediar o diálogo com titulares e com a ANPD.\nFonte: Segurança da Informação e Legislação, UA 2."
        },
        {
            "ua": "04", "obj": 2, "grau": "MÉDIA", "kw": "Bases Legais e Dados Pessoais Sensíveis na LGPD",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Uma plataforma de saúde digital desenvolve um aplicativo móvel para gerenciamento de prontuários, agendamento de consultas e armazenamento de resultados de exames de laboratório. O sistema armazena informações relativas ao histórico clínico, diagnósticos médicos, dados genéticos e biometria de acesso dos usuários.\n\nDe acordo com os preceitos e definições formais estabelecidos no Artigo 5º da LGPD, a legislação confere uma camada reforçada de proteção a determinadas categorias de dados pessoais devido ao seu elevado potencial discriminatório ou de impacto à intimidade do titular.",
            "afirmativas": "",
            "comando_text": "Segundo a LGPD, dados sobre origem racial ou étnica, convicção religiosa, dados referentes à saúde ou à vida sexual e dados genéticos ou biométricos são classificados como:",
            "opt_a": "Dados Pessoais Sensíveis.", "opt_b": "Dados Anonimizados Comerciais.", "opt_c": "Dados de Domínio Público Irrestrito.", "opt_d": "Dados Financeiros Abertos (Open Finance).",
            "feedback": "A resposta certa é Dados Pessoais Sensíveis.\nComentário: O Artigo 5º da LGPD define Dados Pessoais Sensíveis devido ao potencial discriminatório de seu uso indevido, exigindo hipóteses de tratamento mais rígidas.\nFonte: Segurança da Informação e Legislação, UA 4."
        },
        {
            "ua": "07", "obj": 3, "grau": "DIFÍCIL", "kw": "Marco Civil da Internet (Lei 12.965/2014) e Guarda de Logs",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um provedor de acesso à internet (ISP) e uma empresa desenvolvedora de aplicações web reestruturam seus procedimentos operacionais de segurança e retenção de dados para atender aos mandamentos da Lei nº 12.965/2014 (Marco Civil da Internet) no Brasil.\n\nA equipe jurídica e de TI define os prazos legais mínimos obrigatórios para a guarda de registros de conexão à internet sob sigilo em ambiente seguro, bem como os prazos aplicáveis aos registros de acesso a aplicações de internet.",
            "afirmativas": "Com base nas exigências de guarda de logs do Marco Civil da Internet, analise as afirmativas:\nI. Os provedores de acesso à internet (ISPs) devem manter os registros de conexão sob sigilo, em ambiente seguro, pelo prazo mínimo de 1 ano.\nII. Os provedores de aplicações de internet (websites/apps) devem manter os registros de acesso a aplicações pelo prazo de 6 meses.\nIII. O Marco Civil da Internet permite que os provedores de acesso guardem e vendam o histórico detalhado dos sites navegados pelos usuários a empresas de publicidade.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II apresentam com precisão os prazos legais de guarda de logs (1 ano para conexão e 6 meses para aplicações). A afirmativa III é falsa pois a lei proíbe expressamente a comercialização de registros sem consentimento.\nFonte: Segurança da Informação e Legislação, UA 7."
        },
        {
            "ua": "08", "obj": 1, "grau": "DIFÍCIL", "kw": "Sanções Administrativas da ANPD e Relatório RIPD",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Após sofrer um incidente de segurança que resultou no vazamento inadvertido de dados de cartões de crédito e cadastros de milhares de usuários, uma grande rede varejista foi notificada pela Autoridade Nacional de Proteção de Dados (ANPD) para prestação de esclarecimentos e abertura de processo administrativo sancionatório.\n\nA ANPD exige a apresentação do Relatório de Impacto à Proteção de Dados Pessoais (RIPD/DPIA) referente aos processos afetados e avalia a aplicação das sanções administrativas cabíveis previstas no Artigo 52 da LGPD.",
            "afirmativas": "Com base nas sanções administrativas previstas no Artigo 52 da LGPD e no Relatório de Impacto à Proteção de Dados Pessoais (RIPD), analise as afirmativas:\nI. A ANPD pode aplicar multas simples de até 2% do faturamento do grupo econômico no Brasil, limitada a R$ 50 milhões por infração.\nII. O Relatório de Impacto à Proteção de Dados Pessoais (RIPD/DPIA) documenta os processos de tratamento que podem gerar riscos às liberdades civis e descreve os mecanismos de mitigação adotados.\nIII. Empresas públicas brasileiras estão totalmente isentas de cumprir as determinações e sanções da LGPD.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II refletem os limites de multa da LGPD e o propósito do RIPD. A afirmativa III é falsa pois o poder público também se submete estritamente aos regramentos da LGPD.\nFonte: Segurança da Informação e Legislação, UA 8."
        },
        {
            "ua": "08", "obj": 2, "grau": "DIFÍCIL", "kw": "Princípios da LGPD (Finalidade, Adequação, Necessidade e Transparência)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Um aplicativo móvel de utilidade simples (como uma ferramenta de lanterna ou calculadora) exige obrigatoriamente durante a instalação que o usuário forneça seu CPF, endereço residencial completo e autorize o acesso irrestrito à sua lista telefônica de contatos para permitir o funcionamento do software.\n\nDurante uma auditoria de privacidade, os especialistas em compliance constataram que a coleta excessiva de dados pessoais desproporcionais à função precípua do aplicativo viola diretamente os princípios da minimização de dados e da adequação estipulados no Artigo 6º da LGPD.",
            "afirmativas": "Com base nos Princípios da LGPD (Artigo 6º), analise as afirmativas:\n\nI. A exigência de dados desproporcionais e irrelevantes para a execução do serviço contratado viola frontalmente os Princípios da Necessidade (minimização de dados) e da Adequação definidos pela LGPD.\n\nPORQUE\n\nII. O Princípio da Necessidade determina que o tratamento de dados pessoais deve limitar-se ao mínimo estritamente indispensável para a realização de suas finalidades específicas com abrangência dos dados pertinentes.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. Coletar dados excessivos sem relevância funcional descumpre o princípio legal da minimização/necessidade da LGPD.\nFonte: Segurança da Informação e Legislação, UA 8."
        }
    ]
)

# 21. Segurança de redes de computadores
create_exam(
    "Segurança de Redes de Computadores", "Segurança de redes de computadores", "AI Segurança de redes de computadores", "2; 6; 7; 9",
    [
        {
            "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Arquitetura de Firewalls Stateful vs Stateless",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Na borda de conexão de uma rede corporativa com a internet pública, a equipe de segurança configura um firewall para filtrar o tráfego de entrada e saída. A equipe necessita que o firewall acompanhe dinamicamente a tabela de estados das conexões TCP (State Table), permitindo automaticamente os pacotes de resposta legítimos sem a necessidade de criar regras de entrada estáticas abertas.\n\nO firewall deve inspecionar a validade dos números de sequência TCP, os sinalizadores (flags) e o contexto de sessão de cada pacote que transita entre a rede interna confiável e a rede externa não confiável.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o tipo de firewall que inspeciona dinamicamente o estado das conexões de transporte e contexto dos pacotes:",
            "opt_a": "Firewall Stateful Inspection (Inspeção de Estado).", "opt_b": "Firewall Stateless (Packet Filter estático).", "opt_c": "Roteador de borda sem ACLs.", "opt_d": "Filtro de endereço MAC de camada 1.",
            "feedback": "A resposta certa é Firewall Stateful Inspection (Inspeção de Estado).\nComentário: Firewalls Stateful mantêm uma tabela de estado de conexões ativas, liberando conexões de retorno de pacotes de forma contextualizada.\nFonte: Segurança de redes de computadores, UA 2."
        },
        {
            "ua": "06", "obj": 2, "grau": "MÉDIA", "kw": "Sistemas IDS (Intrusion Detection) vs IPS (Intrusion Prevention)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Para proteger os servidores web e de banco de dados posicionados na DMZ contra ataques de exploração de vulnerabilidades (exploits), varreduras de portas e injeções maliciosas, a empresa implementou uma ferramenta de segurança da informação baseada na análise de assinaturas de tráfego (como Snort ou Suricata).\n\nA equipe de segurança precisa decidir entre posicionar a ferramenta no modo passivo fora de banda (Out-of-band) como um IDS ou no modo ativo em linha (In-line) no fluxo direto de pacotes como um IPS.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta a diferença fundamental entre um Sistema IPS (Intrusion Prevention System) e um IDS (Intrusion Detection System):",
            "opt_a": "O IPS é posicionado In-line (em linha) no fluxo de tráfego, podendo bloquear e descartar pacotes maliciosos em tempo real.", "opt_b": "O IPS é posicionado Fora-de-banda (Out-of-band) apenas escutando cópias de tráfego sem poder bloquear pacotes.", "opt_c": "O IPS roda exclusivamente dentro da BIOS de cada computador da rede.", "opt_d": "O IPS substitui os servidores DNS para responder com IPs falsos.",
            "feedback": "A resposta certa é O IPS é posicionado In-line (em linha) no fluxo de tráfego, podendo bloquear e descartar pacotes maliciosos em tempo real.\nComentário: O IPS fica in-line e dropa pacotes maliciosos ativamente, enquanto o IDS analisa réplicas de tráfego e gera alertas passivos.\nFonte: Segurança de redes de computadores, UA 6."
        },
        {
            "ua": "07", "obj": 3, "grau": "DIFÍCIL", "kw": "Segurança de Camada 2 (DHCP Snooping, DAI, Port Security)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Para proteger a infraestrutura de switches de camada 2 da rede local contra ataques de envenenamento de tabela ARP (ARP Poisoning), esgotamento de DHCP (DHCP Starvation) e instalação de servidores DHCP não autorizados (Rogue DHCP), a equipe de redes ativou um pacote de recursos de segurança L2.\n\nA solução combina o DHCP Snooping para construir a tabela de vinculação confiável (Binding Table), o Dynamic ARP Inspection (DAI) para interceptar requisições ARP inválidas e o recurso de Port Security para limitar o número de endereços MAC por porta física.",
            "afirmativas": "Com base nos recursos de segurança de switches L2, analise as afirmativas:\nI. O DHCP Snooping cria uma tabela de vinculação (Binding Table) associando MAC, IP, VLAN e Porta, bloqueando respostas de servidores DHCP não confiáveis.\nII. O Dynamic ARP Inspection (DAI) valida os pacotes ARP interceptados consultando a tabela do DHCP Snooping para mitigar ARP Poisoning.\nIII. O recurso de Port Security bloqueia a porta do switch caso identifique pacotes com endereços IP de classes reservadas.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com precisão DHCP Snooping e DAI. A afirmativa III é falsa pois o Port Security restringe endereços MAC de camada 2 por porta, e não endereços IP.\nFonte: Segurança de redes de computadores, UA 7."
        },
        {
            "ua": "09", "obj": 1, "grau": "DIFÍCIL", "kw": "Ataques de Negação de Serviço (DoS/DDoS - SYN Flood, NTP Amplification)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "O servidor web principal de uma plataforma de serviços online tornou-se inacessível devido a um ataque cibernético de Negação de Serviço Distribuída (DDoS) que inundou a interface de rede com milhares de pacotes de solicitação de abertura de conexão TCP (SYN) por segundo com endereços IP de origem forjados (Spoofed IPs).\n\nO ataque satura a tabela de conexões pendentes (Half-Open Connections) do servidor antes que o aperto de mão de três vias (Three-Way Handshake) possa ser concluído, impedindo que requisições de clientes legítimos sejam processadas.",
            "afirmativas": "Com base na taxonomia e mitigação de ataques DoS/DDoS, analise as afirmativas:\nI. O ataque SYN Flood satura os recursos da vitima enviando solicitações de abertura de conexão TCP com IPs falsificados sem responder com o ACK final.\nII. O uso de SYN Cookies nos servidores permite responder a requisições SYN sem alocar memória de estado até receber o ACK legítimo.\nIII. Ataques de amplificação DNS/NTP utilizam pacotes TCP com confirmação de entrega para multiplicar o tráfego refletido.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão o SYN Flood e a contra-medida SYN Cookies. A afirmativa III é falsa pois ataques de amplificação utilizam requisições UDP com IP de origem forjado (IP Spoofing).\nFonte: Segurança de redes de computadores, UA 9."
        },
        {
            "ua": "09", "obj": 2, "grau": "DIFÍCIL", "kw": "Arquitetura Zero Trust (ZTNA - Zero Trust Network Access)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Frente ao crescimento do trabalho remoto, da adoção de ambientes multi-nuvem e da perda de eficácia da segurança de perímetro tradicional baseada em redes confiáveis internas versus externas, a equipe de segurança da informação projeta a migração da empresa para o modelo de arquitetura Zero Trust (Confiança Zero).\n\nO paradigma Zero Trust estabelece que nenhuma tentativa de acesso a recursos corporativos deve ser aceita implicitamente, exigindo autenticação contínua, autorização dinâmica baseada em contexto e criptografia ponta a ponta independentemente da localização física da origem.",
            "afirmativas": "Com base nos princípios do modelo Zero Trust ('Never Trust, Always Verify'), analise as afirmativas:\n\nI. O modelo Zero Trust exige autenticação contínua, autorização baseada em contexto e criptografia ponta a ponta para toda tentativa de acesso a recursos, mesmo que originada de dentro da rede corporativa interna.\n\nPORQUE\n\nII. O conceito tradicional de perímetro de rede confiável é insuficiente frente à mobilidade de usuários, adoção de nuvem e movimentação lateral de invasores previamente infiltrados na rede local.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A dissolução do perímetro clássico justifica a necessidade do Zero Trust para tratar todo o tráfego como potencialmente hostil.\nFonte: Segurança de redes de computadores, UA 9."
        }
    ]
)

# 22. Servidores e Computação na Nuvem
create_exam(
    "Servidores e computação na Nuvem", "Servidores e Computação na Nuvem", "AI Servidores e Computação na Nuvem", "3; 4; 7; 11",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Containers Docker vs Virtualização Tradicional",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Uma equipe de desenvolvimento e operações (DevOps) migrou a arquitetura de microsserviços da empresa, anteriormente implantada em Máquinas Virtuais (VMs) tradicionais sob um Hypervisor de tipo 1, para contêineres Docker leves rodando sobre o Linux.\n\nA equipe observou uma redução expressiva no tempo de inicialização das instâncias e um aproveitamento muito superior da memória RAM e CPU do servidor hospedeiro, necessitando identificar a diferença arquitetural fundamental que torna os contêineres mais eficientes.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica a diferença arquitetural fundamental que torna os contêineres Docker mais leves e de inicialização mais rápida que as Máquinas Virtuais:",
            "opt_a": "Os contêineres compartilham o mesmo Kernel do sistema operacional hospedeiro sem necessitar de um SO completo em cada instância.", "opt_b": "Os contêineres não utilizam nenhuma forma de isolamento de processos ou memória.", "opt_c": "Os contêineres exigem um hardware de processador quântico dedicado.", "opt_d": "Os contêineres rodam obrigatoriamente dentro de um arquivo de imagem ISO emulação BIOS.",
            "feedback": "A resposta certa é Os contêineres compartilham o mesmo Kernel do sistema operacional hospedeiro sem necessitar de um SO completo em cada instância.\nComentário: Contêineres utilizam namespaces e cgroups do kernel Linux hospedeiro para isolar processos, descartando a sobrecarga de rodar múltiplos SOs virtuais.\nFonte: Servidores e Computação na Nuvem, UA 3."
        },
        {
            "ua": "04", "obj": 2, "grau": "MÉDIA", "kw": "Orquestração de Containers com Kubernetes (K8s)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Para gerenciar centenas de contêineres Docker distribuídos em um ambiente de produção em nuvem com suporte a auto-scaling, auto-healing (recuperação automática de contêineres com falha) e balanceamento de carga, a equipe de infraestrutura adotou a plataforma de orquestração Kubernetes (K8s).\n\nAo criar os manifestos de implantação em formato YAML, os desenvolvedores definem a menor unidade executável e implantável do modelo de objetos do Kubernetes, a qual envolve um ou mais contêineres estreitamente acoplados compartilhando a mesma pilha de rede e volumes.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica a menor unidade implantável no Kubernetes que agrupa um ou mais contêineres compartilhando armazenamento e rede:",
            "opt_a": "Pod.", "opt_b": "Node.", "opt_c": "Namespace.", "opt_d": "Ingress Controller.",
            "feedback": "A resposta certa é Pod.\nComentário: O Pod é a menor unidade de execução gerenciada pelo Kubernetes, contendo um ou mais contêineres estreitamente acoplados.\nFonte: Servidores e Computação na Nuvem, UA 4."
        },
        {
            "ua": "07", "obj": 3, "grau": "DIFÍCIL", "kw": "Infraestrutura como Código (IaC) com Terraform/Ansible",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Para automatizar a criação, alteração e provisionamento de instâncias virtuais, redes privadas, conjuntos de regras de firewall e balanceadores de carga em nuvens públicas (como AWS e Microsoft Azure), a equipe de engenharia adota o conceito de Infraestrutura como Código (IaC).\n\nA solução combina o uso do Terraform para a definição declarativa dos recursos de infraestrutura e o uso do Ansible para a gestão de configuração e automação de softwares dentro dos servidores provisionados sem a necessidade de intervenção manual em consoles gráficos.",
            "afirmativas": "Com base nos conceitos de IaC com Terraform e Ansible, analise as afirmativas:\nI. O Terraform utiliza linguagem declarativa (HCL) para gerenciar o ciclo de vida e estado (tfstate) dos recursos de infraestrutura em múltiplos provedores.\nII. O Ansible é uma ferramenta baseada em playbooks YAML agentless (sem necessidade de agente instalado nos alvos) que utiliza SSH para automação de configurações.\nIII. A abordagem de Infraestrutura como Código exige que modificações no ambiente de produção sejam realizadas manualmente via interface gráfica da nuvem.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com precisão o papel do Terraform e do Ansible. A afirmativa III é falsa pois a IaC substitui cliques manuais por automação versionada via código.\nFonte: Servidores e Computação na Nuvem, UA 7."
        },
        {
            "ua": "11", "obj": 1, "grau": "DIFÍCIL", "kw": "Computação Serverless (AWS Lambda, Azure Functions)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Uma plataforma de e-learning adota a arquitetura de computação Serverless (FaaS - Function as a Service) para processar a conversão e geração de miniaturas (thumbnails) de vídeos enviadas por professores apenas quando um novo arquivo é carregado no bucket de armazenamento.\n\nNo modelo Serverless, a infraestrutura é totalmente abstraída pelo provedor de nuvem, que executa o código sob demanda e cobra exclusivamente pelo tempo de processamento por milissegundo e memória consumida durante a execução da função.",
            "afirmativas": "Com base nas características da computação Serverless, analise as afirmativas:\nI. No modelo Serverless, a cobrança é baseada estritamente no tempo exato de execução do código e consumo de memória por milissegundo.\nII. As funções Serverless escalam automaticamente de zero a milhares de execuções simultaneamente em resposta a eventos acionadores (Triggers).\nIII. O modelo Serverless exige que o desenvolvedor mantenha um servidor Linux virtual rodando continuamente 24h por dia para aguardar requisições.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II destacam a tarifação por execução e a auto-escalabilidade orientada a eventos do Serverless. A afirmativa III é falsa pois a gestão e provisionamento de servidores são 100% abstraídos pelo provedor.\nFonte: Servidores e Computação na Nuvem, UA 11."
        },
        {
            "ua": "11", "obj": 2, "grau": "DIFÍCIL", "kw": "Modelo de Responsabilidade Compartilhada na Nuvem",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Durante o projeto de migração de um banco de dados relacional crítico para uma instância de IaaS (Infraestrutura como Serviço) em um provedor de nuvem pública, o CISO da empresa analisa as obrigações de segurança do provedor e do cliente estabelecidas no Modelo de Responsabilidade Compartilhada.\n\nO parecer técnico delimita expressamente que a contratação da nuvem não exime a organização cliente da responsabilidade pela segurança dos dados armazenados, atualizações do sistema operacional virtual e configuração dos controles de acesso.",
            "afirmativas": "Com base no Modelo de Responsabilidade Compartilhada da Computação em Nuvem, analise as afirmativas:\n\nI. Em um modelo IaaS (Infraestrutura como Serviço), o provedor de nuvem é responsável pela segurança DA nuvem (hardware físico, instalações do Data Center, hypervisores), enquanto o cliente é integralmente responsável pela segurança NA nuvem (sistema operacional virtual, atualizações de patches, dados, configurações de firewall e controle de acessos).\n\nPORQUE\n\nII. A contratação de um serviço de nuvem pública transfere automaticamente a responsabilidade legal pelo sigilo dos dados do cliente para o provedor em caso de vazamento por senha fraca do usuário.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_b": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_c": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é A afirmativa I é verdadeira, e a II é falsa.\nComentário: A afirmativa I descreve perfeitamente a divisão de responsabilidades em IaaS. A afirmativa II é falsa pois a responsabilidade pela governança dos dados e senhas permanece sob controle do cliente.\nFonte: Servidores e Computação na Nuvem, UA 11."
        }
    ]
)

print("Batch 6 atualizado com contextualização ENADE expandida.")
