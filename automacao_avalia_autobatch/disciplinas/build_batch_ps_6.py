# -*- coding: utf-8 -*-
"""
Batch PS 6: Disciplinas 19 a 22 (Provas PS 2026-4 - Novos Objetivos e Contextualização ENADE > 7 linhas)
"""
from generate_full_batch import create_exam

# 19. Segurança da informação
create_exam(
    "Segurança da Informação", "Segurança da informação", "PS Segurança da informação", "2; 4; 7; 10",
    [
        {
            "ua": "02", "obj": 2, "grau": "MÉDIA", "kw": "Autenticação por Múltiplos Fatores (MFA / 2FA)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Para conter a onda de acessos indevidos causados por vazamento ou roubo de credenciais (usuário e senha) em sistemas corporativos, a equipe de segurança da informação implementou a obrigatoriedade da **Autenticação por Múltiplos Fatores** (MFA / 2FA).\n\nO modelo exige que o usuário combine obrigatoriamente dois ou mais fatores de autenticação de categorias distintas (Algo que você sabe, Algo que você tem e Algo que você é) durante o processo de login.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta uma combinação válida de dois fatores de autenticação de categorias distintas:",
            "opt_a": "Senha textual (Algo que você sabe) + Token OTP por aplicativo no smartphone (Algo que você tem).", "opt_b": "Senha de 8 dígitos + Segunda senha de 4 dígitos.", "opt_c": "Nome de usuário público + Endereço de e-mail corporativo.", "opt_d": "Pergunta de segurança + Nome da mãe do usuário.",
            "feedback": "A resposta certa é Senha textual (Algo que você sabe) + Token OTP por aplicativo no smartphone (Algo que você tem).\nComentário: O MFA exige combinar fatores de categorias diferentes (conhecimento, posse ou biometria). Senha + Token OTP combina conhecimento com posse.\nFonte: Segurança da informação, UA 2."
        },
        {
            "ua": "04", "obj": 3, "grau": "MÉDIA", "kw": "Criptografia Assimétrica e Troca de Chaves Diffie-Hellman",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Dois servidores situados em redes geograficamente distantes precisam negociar com segurança uma chave simétrica secreta através de um canal de comunicação não confiável (a internet) sem transmitirem a chave diretamente pela rede.\n\nPara resolver esse desafio de distribuição de chaves, os servidores utilizam o algoritmo matemático de troca de chaves **Diffie-Hellman** (DH).",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o objetivo principal do algoritmo de troca de chaves Diffie-Hellman:",
            "opt_a": "Permitir que duas partes estabeleçam uma chave secreta compartilhada sobre um meio inseguro sem que a chave seja transmitida pelo canal.", "opt_b": "Executar a compactação de dados para envio por e-mail.", "opt_c": "Criptografar arquivos locais em disco rígido sem usar senhas.", "opt_d": "Substituir o uso de certificados digitais X.509 em servidores web.",
            "feedback": "A resposta certa é Permitir que duas partes estabeleçam uma chave secreta compartilhada sobre um meio inseguro sem que a chave seja transmitida pelo canal.\nComentário: O algoritmo Diffie-Hellman utiliza propriedades de aritmética modular para calcular uma chave simétrica comum entre as pontas sem trafegá-la na rede.\nFonte: Segurança da informação, UA 4."
        },
        {
            "ua": "07", "obj": 1, "grau": "DIFÍCIL", "kw": "Análise de Malware em Sandbox e Indicadores de Comprometimento (IoC)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Após um servidor da empresa apresentar comportamento anômalo e alto uso de CPU, o analista de resposta a incidentes extrai o arquivo executável suspeito e o submete a uma análise dinâmica dentro de um ambiente isolado de **Sandbox**.\n\nA análise registra a criação de chaves no Registro do Windows, conexões de rede para IPs de Comando e Controle (C2) e hashes de arquivos maliciosos, gerando o relatório de Indicadores de Comprometimento (IoC).",
            "afirmativas": "Com base na análise de malware e Indicadores de Comprometimento (IoC), analise as afirmativas:\nI. Ambientes de Sandbox isolam a execução do arquivo malicioso para observar seu comportamento sem colocar a rede corporativa em risco.\nII. Indicadores de Comprometimento (IoCs) incluem hashes de arquivos (MD5/SHA256), IPs maliciosos, domínios C2 e chaves de registro alteradas.\nIII. A análise estática de um executável exige a execução direta do código malicioso no servidor principal de produção.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com precisão o propósito da Sandbox e a definição de IoCs. A afirmativa III é falsa pois a análise estática inspeciona o código e strings sem executar a amostra, e jamais em produção.\nFonte: Segurança da informação, UA 7."
        },
        {
            "ua": "10", "obj": 2, "grau": "DIFÍCIL", "kw": "Gestão de Continuidade de Negócios segundo a ISO 22301",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Uma corporação financeira implementa um Sistema de Gestão de Continuidade de Negócios (SGCN) certificado pela norma internacional **ISO 22301** para garantir que a empresa sobreviva a desastres graves (como incêndios, ataques cibernéticos ou pandemias).\n\nComo parte do processo, a equipe realiza a Análise de Impacto no Negócio (BIA - Business Impact Analysis) para identificar os processos críticos da organização e seus tempos máximos de parada aceitáveis.",
            "afirmativas": "Com base na norma ISO 22301 e Análise de Impacto no Negócio (BIA), analise as afirmativas:\nI. A BIA (Análise de Impacto no Negócio) quantifica os impactos financeiros e operacionais resultantes da interrupção dos processos de negócio ao longo do tempo.\nII. O MTPD (Maximum Tolerable Period of Disruption) estabelece o tempo limite que um processo pode ficar paralisado antes de causar danos irreparáveis à viabilidade da empresa.\nIII. A norma ISO 22301 aplica-se exclusivamente a infraestruturas de hardware e desconsidera os processos humanos do negócio.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão a função da BIA e a métrica MTPD na ISO 22301. A afirmativa III é falsa pois a gestão de continuidade aborda pessoas, processos, fornecedores e tecnologia de forma holística.\nFonte: Segurança da informação, UA 10."
        },
        {
            "ua": "10", "obj": 3, "grau": "DIFÍCIL", "kw": "Políticas de Segurança da Informação (PSI) e Conscientização de Usuários",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Uma empresa investiu milhões de reais em firewalls NGFW de última geração, criptografia de dados e sistemas IPS de ponta, mas sofreu um vazamento crítico de dados após um estagiário fornecer sua senha por telefone a um falso técnico de suporte.\n\nO Comitê de Segurança aprovou a obrigatoriedade de programas contínuos de conscientização em segurança para todos os colaboradores, além da aplicação rigorosa da Política de Segurança da Informação (PSI).",
            "afirmativas": "Com base nas Políticas de Segurança e fator humano em segurança da informação, analise as afirmativas:\n\nI. O treinamento contínuo de conscientização em segurança é um controle indispensável da PSI, pois o ser humano é considerado o elo mais fraco da corrente de segurança contra ataques de engenharia social.\n\nPORQUE\n\nII. Controles tecnológicos (como firewalls e antivírus) são incapazes de impedir que um usuário legítimo revele voluntariamente suas credenciais de acesso ao cair em uma fraude de engenharia social por telefone ou e-mail.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A vulnerabilidade do fator humano a truques psicológicos justifica a necessidade crítica dos programas de conscientização.\nFonte: Segurança da informação, UA 10."
        }
    ],
    subfolder='PS'
)

# 20. Segurança da Informação e Legislação
create_exam(
    "Segurança da Informação e Legislação", "Segurança da Informação e Legislação", "PS Segurança da Informação e Legislação", "2; 4; 7; 8",
    [
        {
            "ua": "02", "obj": 2, "grau": "MÉDIA", "kw": "Direitos dos Titulares de Dados Pessoais na LGPD (Artigo 18)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Um cliente de um aplicativo de entregas solicita ao suporte da empresa a exclusão definitiva do seu cadastro e de todo o seu histórico de dados pessoais da base do sistema.\n\nDe acordo com o **Artigo 18 da Lei Geral de Proteção de Dados (LGPD)**, o titular dos dados pessoais tem o direito de obter do controlador, em relação aos dados por ele tratados, a qualquer momento e mediante requisição expressa, a confirmação, o acesso, a correção e a eliminação dos dados.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta o direito do titular que permite solicitar a transferência dos seus dados pessoais a outro fornecedor de serviço ou produto:",
            "opt_a": "Portabilidade dos dados.", "opt_b": "Anonimização irreversível.", "opt_c": "Revogação da licença de software.", "opt_d": "Bloqueio do endereço IP do provedor.",
            "feedback": "A resposta certa é Portabilidade dos dados.\nComentário: O Artigo 18, V da LGPD garante expressamente o direito à portabilidade dos dados a outro fornecedor de serviço ou produto, mediante requisição expressa.\nFonte: Segurança da Informação e Legislação, UA 2."
        },
        {
            "ua": "04", "obj": 3, "grau": "MÉDIA", "kw": "Hipóteses de Tratamento de Dados Pessoais (Consentimento vs Legítimo Interesse)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Uma instituição financeira precisa consultar a pontuação de crédito (Score) de um cliente em um banco de dados de proteção ao crédito antes de conceder um financiamento imobiliário solicitado pelo próprio cliente.\n\nO departamento jurídico analisa as 10 hipóteses legais que autorizam o tratamento de dados pessoais previstas no Artigo 7º da LGPD para enquadrar a operação sem depender exclusivamente do consentimento do titular.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica a hipótese legal de tratamento da LGPD aplicável à consulta de crédito descrita:",
            "opt_a": "Proteção do crédito.", "opt_b": "Execução de pesquisas por órgão de estudo público exclusivamente.", "opt_c": "Tutela da saúde em procedimento realizado por farmacêuticos exclusivamente.", "opt_d": "Consentimento sob coação verbal.",
            "feedback": "A resposta certa é Proteção do crédito.\nComentário: O Artigo 7º, X da LGPD autoriza expressamente o tratamento de dados pessoais para a proteção do crédito, inclusive quanto ao disposto na legislação pertinente.\nFonte: Segurança da Informação e Legislação, UA 4."
        },
        {
            "ua": "07", "obj": 1, "grau": "DIFÍCIL", "kw": "Responsabilidade Civil dos Provedores no Marco Civil da Internet",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um usuário de uma rede social publica um comentário contendo conteúdo ofensivo e difamatório contra uma empresa comercial. A empresa vítima notifica a plataforma de rede social exigindo a remoção imediata do post sob pena de responsabilização judicial.\n\nA equipe jurídica analisa as regras de responsabilidade civil por danos decorrentes de conteúdos gerados por terceiros estabelecidas no **Artigo 19 do Marco Civil da Internet** (Lei 12.965/2014).",
            "afirmativas": "Com base na responsabilidade civil dos provedores no Marco Civil da Internet, analise as afirmativas:\nI. Com o intuito de assegurar a liberdade de expressão e impedir a censura, o provedor de aplicações só responde civilmente por danos de terceiros se, após ordem judicial específica, não tomar as providências para tornar o conteúdo indisponível.\nII. A exceção à regra da ordem judicial aplica-se aos casos de divulgação não autorizada de imagens de nudez ou atos sexuais de caráter privado (Artigo 21), onde a notificação da vítima basta para obrigar a remoção.\nIII. Provedores de aplicação respondem objetivamente por todo e qualquer texto publicado por seus usuários independentemente de ordem judicial ou notificação.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II apresentam com exatidão a regra geral da ordem judicial (Art. 19) e a exceção de vingança pornográfica (Art. 21) do Marco Civil. A afirmativa III é falsa pois o Marco Civil afastou a responsabilidade objetiva genérica dos provedores.\nFonte: Segurança da Informação e Legislação, UA 7."
        },
        {
            "ua": "08", "obj": 2, "grau": "DIFÍCIL", "kw": "Transferência Internacional de Dados Pessoais na LGPD",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Uma startup brasileira de tecnologia contrata um provedor de nuvem cuja infraestrutura de banco de dados está localizada fisicamente em um Data Center nos Estados Unidos, realizando a **Transferência Internacional de Dados Pessoais** de seus clientes brasileiros.\n\nO DPO da startup verifica as condições e salvaguardas legais exigidas no Capítulo V (Artigos 33 a 36) da LGPD para validar a transferência dos dados para fora do território nacional.",
            "afirmativas": "Com base nas regras de Transferência Internacional de Dados da LGPD, analise as afirmativas:\nI. A transferência internacional é permitida quando o país de destino proporcionar grau de proteção de dados pessoais adequado ao previsto na LGPD, reconhecido pela ANPD.\nII. A transferência internacional é permitida quando o controlador comprovar oferecer garantias de cumprimento dos princípios da LGPD através de cláusulas contratuais padrão ou normas corporativas globais.\nIII. A LGPD proíbe sumariamente qualquer envio ou armazenamento de dados pessoais brasileiros fora das fronteiras físicas do Brasil.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II refletem os mecanismos válidos de transferência internacional da LGPD (Artigo 33). A afirmativa III é falsa pois o envio internacional é plenamente legal desde que observadas as salvaguardas da lei.\nFonte: Segurança da Informação e Legislação, UA 8."
        },
        {
            "ua": "08", "obj": 3, "grau": "DIFÍCIL", "kw": "Princípios de Privacy by Design e Privacy by Default",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Ao projetar uma nova versão de um aplicativo móvel de transporte de passageiros, a equipe de engenharia de software adota a metodologia de **Privacy by Design** (Privacidade desde a Concepção) e **Privacy by Default** (Privacidade por Padrão).\n\nDesde as primeiras reuniões de arquitetura, as configurações de compartilhamento de dados com terceiros vêm desativadas por padrão, e a coleta de dados de localização é restrita ao momento do uso da corrida.",
            "afirmativas": "Com base nos princípios de Privacy by Design e Privacy by Default, analise as afirmativas:\n\nI. A abordagem Privacy by Design exige que a privacidade e a proteção de dados sejam incorporadas em todo o ciclo de vida do desenvolvimento do software, desde a concepção arquitetural até a implantação final.\n\nPORQUE\n\nII. O Privacy by Default garante que, sem a intervenção explícita do usuário para alterar as configurações, o sistema aplique automaticamente a opção de maior privacidade possível com a menor coleta de dados.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A integração da privacidade desde o design e as configurações restritivas por padrão são a essência do modelo de conformidade moderno.\nFonte: Segurança da Informação e Legislação, UA 8."
        }
    ],
    subfolder='PS'
)

# 21. Segurança de redes de computadores
create_exam(
    "Segurança de Redes de Computadores", "Segurança de redes de computadores", "PS Segurança de redes de computadores", "2; 6; 7; 9",
    [
        {
            "ua": "02", "obj": 2, "grau": "MÉDIA", "kw": "Next-Generation Firewalls (NGFW) e Filtro de Aplicação L7",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Para conter a fuga de informações confidenciais e o uso não autorizado de aplicativos de mensagens instantâneas e compartilhamento de arquivos P2P que operam sob a porta padrão HTTP/HTTPS 443, a equipe de segurança substituiu o firewall de pacotes tradicional por um **Next-Generation Firewall (NGFW)**.\n\nO NGFW executa a Inspeção Profunda de Pacotes (DPI - Deep Packet Inspection) para identificar a assinatura da aplicação na camada 7, independentemente da porta de transporte utilizada.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta a principal capacidade diferenciadora de um Next-Generation Firewall (NGFW) em relação a um firewall de estado tradicional:",
            "opt_a": "Identificação e controle granular de aplicações na camada 7 (App-ID) e integração nativa com prevenção de intrusão (IPS).", "opt_b": "Filtragem estática baseada exclusivamente em endereços MAC de camada 2.", "opt_c": "Criação de cópias de segurança em fita magnética.", "opt_d": "Aumento do consumo elétrico da rede local.",
            "feedback": "A resposta certa é Identificação e controle granular de aplicações na camada 7 (App-ID) e integração nativa com prevenção de intrusão (IPS).\nComentário: NGFWs vão além de portas e IPs, inspecionando a camada 7 para identificar a aplicação real (ex: diferenciar tráfego SSL legítimo de BitTorrent tunelado no port 443).\nFonte: Segurança de redes de computadores, UA 2."
        },
        {
            "ua": "06", "obj": 3, "grau": "MÉDIA", "kw": "Análise de Tráfego por Comportamento (NBA / Anomaly Detection)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Para detectar ataques cibernéticos de Dia Zero (Zero-Day) que não possuem assinaturas previamente conhecidas nos bancos de dados dos antivírus e IPSs, a empresa implementou uma ferramenta de **Análise de Comportamento de Rede** (NBA - Network Behavior Analysis).\n\nA ferramenta estabelece a linha de base de tráfego normal (Baseline) da rede corporativa durante semanas e emite alertas automatizados sempre que ocorrem desvios estatísticos anômalos no volume ou padrão de conexões.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o mecanismo de detecção utilizado por ferramentas de análise comportamental de rede:",
            "opt_a": "Detecção baseada em anomalias (Anomaly-based Detection).", "opt_b": "Detecção estritamente baseada em assinaturas de código fixas.", "opt_c": "Varredura manual de discos com antivírus legado.", "opt_d": "Bloqueio permanente de todas as conexões de saída da rede.",
            "feedback": "A resposta certa é Detecção baseada em anomalias (Anomaly-based Detection).\nComentário: A detecção por anomalia compara o tráfego em tempo real com a linha de base normal, sendo capaz de identificar comportamentos atípicos e ameaças Zero-Day sem assinatura prévia.\nFonte: Segurança de redes de computadores, UA 6."
        },
        {
            "ua": "07", "obj": 1, "grau": "DIFÍCIL", "kw": "Mitigação de Ataques de VLAN Hopping (IEEE 802.1Q Tagging)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Em um teste de invasão (PenTest) realizado na rede local da empresa, o auditor de segurança conseguiu invadir a VLAN restrita de servidores a partir de uma porta de acesso comum na recepção utilizando a técnica de **VLAN Hopping** (via Double Tagging 802.1Q ou spoofing de DTP).\n\nA equipe de redes é encarregada de aplicar as diretrizes de endurecimento de segurança (Hardening) em todos os switches da infraestrutura.",
            "afirmativas": "Com base na mitigação de ataques de VLAN Hopping em switches L2, analise as afirmativas:\nI. Desativar a negociação automática de troncos (DTP - Dynamic Trunking Protocol) nas portas de acesso de usuários previne o spoofing de trunking.\nII. Alterar a Native VLAN padrão (VLAN 1) em todas as portas Trunk para uma VLAN não utilizada mitiga o ataque de Double Tagging.\nIII. Manter todas as portas de acesso dos usuários configuradas no modo 'Trunk Auto' é a recomendação oficial de segurança.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II apresentam com precisão as duas principais contra-medidas contra VLAN Hopping. A afirmativa III é falsa pois portas de acesso devem ser travadas explicitamente no modo `switchport mode access`.\nFonte: Segurança de redes de computadores, UA 7."
        },
        {
            "ua": "09", "obj": 2, "grau": "DIFÍCIL", "kw": "Ataques de Amplificação DNS/NTP Amplification DDoS",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Um servidor web corporativo tornou-se indisponível após ser atingido por um ataque de Negação de Serviço Distribuída (DDoS) do tipo **DNS Amplification** com taxa de tráfego recebido de 50 Gbps.\n\nO atacante utilizou uma Botnet para enviar pequenas consultas DNS em protocolo UDP com o endereço IP de origem forjado (IP Spoofing) com o IP da vítima para milhares de servidores DNS recursivos abertos na internet.",
            "afirmativas": "Com base nos ataques de amplificação DNS/NTP, analise as afirmativas:\nI. Ataques de amplificação exploram o protocolo UDP sem conexão para forjar o IP da vítima no cabeçalho de origem (IP Spoofing).\nII. O fator de amplificação ocorre quando a resposta emitida pelo servidor aberto é dezenas de vezes maior em bytes do que a pequena requisição enviada.\nIII. A implementação do filtro BCP 38 (Source Address Validation) pelos provedores de internet impede que pacotes com IPs forjados saiam das redes de origem.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I, II e III.", "opt_b": "I e II, apenas.", "opt_c": "I e III, apenas.", "opt_d": "II e III, apenas.",
            "feedback": "A resposta certa é I, II e III.\nComentário: Todas as afirmativas são verdadeiras. Elas explicam o mecanismo de IP Spoofing em UDP, o fator de multiplicação de tráfego e a contra-medida global BCP 38.\nFonte: Segurança de redes de computadores, UA 9."
        },
        {
            "ua": "09", "obj": 3, "grau": "DIFÍCIL", "kw": "Arquitetura de Microsegmentação de Rede e Segurança em Nuvem",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Em uma infraestrutura de nuvem privada para microsserviços, o invasor conseguiu comprometer um contêiner web secundário e tentou movimentar-se lateralmente (Lateral Movement) na rede para acessar o banco de dados de produção armazenado no mesmo servidor físico.\n\nA tentativa de invasão lateral foi bloqueada imediatamente devido à implementação de **Microsegmentação de Rede** via SDN (Software-Defined Networking).",
            "afirmativas": "Com base no conceito de Microsegmentação em segurança de redes, analise as afirmativas:\n\nI. A Microsegmentação isola cargas de trabalho individuais (workloads) no nível do hipervisor ou contêiner, aplicando regras de firewall granulares de camada 7 entre workloads que residem na mesma sub-rede IP local.\n\nPORQUE\n\nII. O controle de tráfego Leste-Oeste (tráfego entre servidores internos) impede a movimentação lateral de atacantes previamente infiltrados dentro do perímetro de rede tradicional.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. O bloqueio do tráfego Leste-Oeste em nível de workload é o princípio central da microsegmentação para conter a movimentação lateral.\nFonte: Segurança de redes de computadores, UA 9."
        }
    ],
    subfolder='PS'
)

# 22. Servidores e Computação na Nuvem
create_exam(
    "Servidores e computação na Nuvem", "Servidores e Computação na Nuvem", "PS Servidores e Computação na Nuvem", "3; 4; 7; 11",
    [
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Imagens de Containers Docker e Arquivo Dockerfile",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Um desenvolvedor precisa empacotar uma aplicação Python/Flask com todas as suas dependências em um contêiner portátil para implantação em produção.\n\nEle cria um arquivo de texto declarativo chamado **Dockerfile** contendo as instruções de montagem da imagem Docker em camadas imutáveis (como `FROM`, `WORKDIR`, `COPY`, `RUN` e `CMD`).",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica a instrução do Dockerfile utilizada para definir o comando padrão que será executado quando o contêiner for iniciado:",
            "opt_a": "CMD.", "opt_b": "FROM.", "opt_c": "ENV.", "opt_d": "EXPOSE.",
            "feedback": "A resposta certa é CMD.\nComentário: A instrução `CMD` (ou `ENTRYPOINT`) especifica o comando e argumentos padrão que serão executados na inicialização do contêiner.\nFonte: Servidores e Computação na Nuvem, UA 3."
        },
        {
            "ua": "04", "obj": 3, "grau": "MÉDIA", "kw": "Controladores de Replicação no Kubernetes (Deployments e StatefulSets)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Ao implantar um banco de dados relacional PostgreSQL em um cluster Kubernetes, a equipe de DevOps necessita que cada réplica de Pod possua uma identidade de rede estável e persistente (ex: `postgres-0`, `postgres-1`) e volumes de disco dedicados vinculados a cada nó específico.\n\nA equipe compara os controladores de carga de trabalho do Kubernetes: `Deployment` (para aplicações stateless) e `StatefulSet` (para aplicações stateful).",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o recurso adequado do Kubernetes para gerenciar aplicações que exigem persistência de dados de estado e identificadores de rede únicos ordenados:",
            "opt_a": "StatefulSet.", "opt_b": "Deployment.", "opt_c": "DaemonSet.", "opt_d": "CronJob.",
            "feedback": "A resposta certa é StatefulSet.\nComentário: O `StatefulSet` é o recurso do Kubernetes projetado para gerenciar aplicações stateful, fornecendo garantia de ordem de inicialização, nomes de rede estáveis e volumes persistentes únicos por Pod.\nFonte: Servidores e Computação na Nuvem, UA 4."
        },
        {
            "ua": "07", "obj": 1, "grau": "DIFÍCIL", "kw": "Automação de Infraestrutura com Ansible Playbooks e Módulos",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um analista de infraestrutura precisa atualizar os pacotes de segurança e instalar o servidor web Nginx em 50 servidores Linux virtuais rodando em nuvem privada.\n\nPara automatizar a execução das tarefas de forma idempotente sem necessidade de instalar agentes nos servidores remotos, ele escreve um **Ansible Playbook** em formato YAML e executa a automação via SSH.",
            "afirmativas": "Com base na ferramenta de automação Ansible, analise as afirmativas:\nI. O Ansible é uma ferramenta 'agentless', utilizando conexões SSH nativas no Linux e WinRM no Windows para gerenciar os nós remotos.\nII. Playbooks do Ansible são escritos na sintaxe humanamente legível YAML e organizados por tarefas (tasks) e módulos (ex: `apt`, `yum`, `service`).\nIII. A idempotência dos módulos Ansible garante que reexecutar o mesmo Playbook em um servidor que já possui a configuração desejada não causará alterações indevidas.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I, II e III.", "opt_b": "I e II, apenas.", "opt_c": "I e III, apenas.", "opt_d": "II e III, apenas.",
            "feedback": "A resposta certa é I, II e III.\nComentário: Todas as afirmativas são verdadeiras. Elas definem com exatidão o funcionamento agentless, a sintaxe em YAML e a idempotência do Ansible.\nFonte: Servidores e Computação na Nuvem, UA 7."
        },
        {
            "ua": "11", "obj": 2, "grau": "DIFÍCIL", "kw": "Armazenamento de Objetos (Object Storage - AWS S3 / Azure Blob)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Uma plataforma de streaming de fotos e vídeos armazena petabytes de arquivos de mídia em nuvem pública utilizando um serviço de **Armazenamento de Objetos** (Object Storage, como AWS S3 ou Azure Blob Storage).\n\nO arquiteto de nuvem seleciona as classes de armazenamento (Standard, Infrequent Access e Archive/Glacier) para otimizar os custos de armazenamento com base na frequência de acesso aos arquivos antigos.",
            "afirmativas": "Com base no Armazenamento de Objetos em nuvem (Object Storage), analise as afirmativas:\nI. O armazenamento de objetos organiza os dados em uma estrutura plana (flat) em repositórios (Buckets), associando cada arquivo a uma chave única e metadados extensíveis.\nII. A classe de armazenamento de Arquivo (Archive / Glacier) oferece custos por gigabyte extremamente baixos, mas exige tempos de recuperação de horas para disponibilizar os dados para download.\nIII. Armazenamento de objetos é formatado como um sistema de arquivos de blocos POSIX montável diretamente como disco de sistema operacional (`/dev/sda1`).",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II refletem a estrutura sem hierarquia do Object Storage e o custo/tempo da classe Archive. A afirmativa III é falsa pois o Object Storage é acessado via API HTTP (REST/S3 API) e não como sistema de arquivos POSIX local.\nFonte: Servidores e Computação na Nuvem, UA 11."
        },
        {
            "ua": "11", "obj": 3, "grau": "DIFÍCIL", "kw": "Estratégias de Migração para Nuvem (Os 6 Rs: Rehost, Replatform, Refactor, etc.)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Uma empresa de médio porte planeja a migração de seus 30 sistemas corporativos legados do seu Data Center on-premises para uma nuvem pública.\n\nA consultoria de nuvem mapeia as aplicações segundo o modelo de estratégias de migração conhecido como **Os 6 Rs da Migração** (Rehost/Lift-and-Shift, Replatform, Refactor/Re-architect, Repurchase, Retire e Retain).",
            "afirmativas": "Com base nas estratégias dos 6 Rs de migração para a nuvem, analise as afirmativas:\n\nI. A estratégia de Rehost (Lift-and-Shift) move aplicações e servidores virtuais para a nuvem exatamente como estão sem realizar alterações na arquitetura do código, sendo a forma mais rápida de migração inicial.\n\nPORQUE\n\nII. A estratégia de Refactor (Re-architect) reescreve a aplicação para aproveitar recursos nativos da nuvem (como Serverless e microsserviços), exigindo maior investimento e tempo de desenvolvimento mas entregando maior otimização de custos e escalabilidade a longo prazo.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A afirmativa I descreve perfeitamente o Lift-and-Shift e a afirmativa II detalha a re-arquitetura nativa de nuvem (Refactor); contudo, a II descreve uma estratégia alternativa e não a justificativa da velocidade do Rehost.\nFonte: Servidores e Computação na Nuvem, UA 11."
        }
    ],
    subfolder='PS'
)

print("Batch PS 6 concluído.")
