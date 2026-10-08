# -*- coding: utf-8 -*-
"""
Batch 2: Disciplinas 5 a 7 (Versão ENADE Expandida - Caso Prático Robusto > 7 linhas)
"""
from generate_full_batch import create_exam

# 5. Gerenciamento de redes de computadores
create_exam(
    "Gerenciamento de Redes", "Gerenciamento de redes de computadores", "AI Gerenciamento de redes de computadores", "3; 4; 8; 11",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Arquitetura e Protocolos SNMP (v1, v2c, v3)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em um Centro de Operações de Rede (NOC) de um provedor de serviços de internet (ISP), a equipe de suporte utiliza o protocolo SNMP (Simple Network Management Protocol) para monitorar continuamente a disponibilidade, o uso de CPU, o consumo de memória e a vazão das interfaces dos roteadores de borda.\n\nDurante uma auditoria de segurança da informação, constatou-se que a versão legado SNMPv2c utilizada na rede transmitia as strings de comunidade (Community Strings) em texto claro sem qualquer criptografia. Para proteger a infraestrutura contra ataques de interceptação de pacotes (Eavesdropping) e alteração remota de configurações por cibercriminosos na rede WAN, a gerência exigiu a migração imediata para uma versão do protocolo que forneça autenticação forte de usuários e criptografia simétrica de pacotes.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica a versão do protocolo SNMP que atende aos requisitos de segurança ao oferecer o modelo de segurança USM (User-based Security Model) com autenticação e criptografia de dados:",
            "opt_a": "SNMPv3.", "opt_b": "SNMPv1.", "opt_c": "SNMPv2c.", "opt_d": "SNMPv2u.",
            "feedback": "A resposta certa é SNMPv3.\nComentário: O SNMPv3 introduziu o modelo USM (User-based Security Model) e VACM, fornecendo autenticação HMAC-SHA/MD5 e privacidade por criptografia AES/DES.\nFonte: Gerenciamento de Redes, UA 3."
        },
        {
            "ua": "04", "obj": 2, "grau": "MÉDIA", "kw": "Estrutura da MIB II e SMI",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Durante o processo de implantação de uma plataforma de monitoramento Zabbix/Nagios em uma rede corporativa, o administrador de sistemas precisa cadastrar Identificadores de Objetos (OIDs - Object Identifiers) pertencentes à MIB II (Management Information Base) padronizada pela IETF.\n\nO objetivo é construir dashboards de desempenho para registrar o volume de octetos trafegados, contadores de pacotes unicast/multicast descartados e o status operacional (Up/Down) de cada uma das interfaces físicas de rede dos switches principais do Data Center.",
            "afirmativas": "",
            "comando_text": "Na estrutura hierárquica da árvore MIB-II (SMI), assinale o grupo de objetos padronizado responsável por armazenar estatísticas de tráfego, contadores de erro e o estado operacional das interfaces de rede:",
            "opt_a": "interfaces (iso.org.dod.internet.mgmt.mib-2.interfaces).", "opt_b": "system (iso.org.dod.internet.mgmt.mib-2.system).", "opt_c": "icmp (iso.org.dod.internet.mgmt.mib-2.icmp).", "opt_d": "snmp (iso.org.dod.internet.mgmt.mib-2.snmp).",
            "feedback": "A resposta certa é interfaces (iso.org.dod.internet.mgmt.mib-2.interfaces).\nComentário: O grupo 'interfaces' (ifTable) da MIB-II define contadores de octetos, erros, descartes e estado operacional de cada interface de rede do dispositivo gerenciado.\nFonte: Gerenciamento de Redes, UA 4."
        },
        {
            "ua": "08", "obj": 3, "grau": "DIFÍCIL", "kw": "NetFlow, IPFIX e Análise de Tráfego",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Uma grande empresa de varejo e-commerce enfrenta lentidões periódicas não explicadas em seu link de longa distância (WAN) que interliga a sede administrativa aos centros de distribuição. O gerenciamento por amostragem SNMP tradicional revela apenas a média de consumo de banda por interface, sendo incapaz de identificar quais aplicações específicas ou endereços IP estão consumindo a largura de banda.\n\nPara solucionar esse gargalo de visibilidade, a equipe de engenharia ativou a exportação de estatísticas de fluxos de dados NetFlow/IPFIX nos roteadores de borda enviando relatórios para um coletor centralizado.",
            "afirmativas": "Com base nos conceitos do protocolo NetFlow/IPFIX e análise de tráfego de fluxos, analise as afirmativas:\nI. Um fluxo de rede no NetFlow é unidirecional e definido pelo conjunto único de 5 tuplas: IP de Origem, IP de Destino, Porta de Origem, Porta de Destino e Protocolo IP.\nII. Diferente do monitoramento SNMP por polling repetitivo, o NetFlow exporta relatórios estatísticos proativos contendo metadados dos fluxos assim que são encerrados.\nIII. A tecnologia NetFlow analisa e transporta o conteúdo integral (payload) dos arquivos transferidos pelos usuários para inspeção de conteúdo DLP.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com precisão a 5-tupla de identificação de fluxo e o envio proativo de estatísticas. A afirmativa III é falsa pois o NetFlow exporta apenas metadados de cabeçalho, não a carga útil (payload).\nFonte: Gerenciamento de Redes, UA 8."
        },
        {
            "ua": "11", "obj": 1, "grau": "DIFÍCIL", "kw": "Frameworks FCAPS e Gerenciamento de Desempenho",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "A ISO padronizou o modelo de referência FCAPS para categorizar as atividades de gerenciamento de redes em 5 áreas funcionais interligadas: Gestão de Falhas (Fault), Gestão de Configuração (Configuration), Gestão de Contabilidade (Accounting), Gestão de Desempenho (Performance) e Gestão de Segurança (Security).\n\nUma consultoria de TI foi contratada para reestruturar as operações do NOC de uma multinacional adaptando suas ferramentas aos pilares da arquitetura FCAPS.",
            "afirmativas": "Com base nas 5 áreas funcionais do modelo FCAPS, analise as afirmativas:\nI. A Gestão de Falhas engloba a detecção, isolamento, notificação (via SNMP Traps/Syslog) e correção de anomalias operacionais na rede.\nII. A Gestão de Contabilidade registra a utilização de recursos de rede pelos usuários ou departamentos para fins de cobrança ou rateio de custos de TI.\nIII. A Gestão de Segurança restringe-se exclusivamente à aplicação pontual de atualizações de firmware nos roteadores de borda.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II cobrem adequadamente Falhas e Contabilidade do FCAPS. A afirmativa III é falsa pois a Gestão de Segurança engloba controle de acesso, criptografia, auditoria, políticas e firewalls.\nFonte: Gerenciamento de Redes, UA 11."
        },
        {
            "ua": "11", "obj": 2, "grau": "DIFÍCIL", "kw": "SLA, Acordos de Nível de Serviço e Indicadores MTBF/MTTR",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Um contrato de prestação de serviços de conectividade corporativa de dados (SLA - Service Level Agreement) entre uma operadora e um banco estabelece uma cláusula de disponibilidade mínima de 99,9% ao ano. Para mensurar a eficiência da operação de suporte e a qualidade dos equipamentos, o gerenciamento de redes monitora continuamente os indicadores chave MTBF (Mean Time Between Failures) e MTTR (Mean Time To Repair).",
            "afirmativas": "Com base nos indicadores operacionais de disponibilidade de redes MTBF e MTTR, analise as afirmativas:\n\nI. A redução do tempo médio de reparo (MTTR) combinada ao aumento do tempo médio entre falhas (MTBF) eleva diretamente a porcentagem de disponibilidade total do serviço de rede acordado no SLA.\n\nPORQUE\n\nII. A disponibilidade percentual de um sistema de rede é calculada formalmente pela relação matemática Availability = MTBF / (MTBF + MTTR).",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A fórmula clássica de disponibilidade demonstra que aumentar o tempo sem falhas (MTBF) e diminuir o tempo de reparo (MTTR) maximiza a disponibilidade do SLA.\nFonte: Gerenciamento de Redes, UA 11."
        }
    ]
)

# 6. Infraestrutura de redes
create_exam(
    "Infraestrutura de rede (seg)", "Infraestrutura de redes", "AI Infraestrutura de redes", "2; 3; 5; 8",
    [
        {
            "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Modelo de Referência OSI e Modelo TCP/IP",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Na análise do tráfego de rede de uma empresa utilizando um sniffer de pacotes (Wireshark), um engenheiro de redes examina o processo de encapsulamento de dados. Ao trafegar da origem ao destino, os dados da aplicação são envolvidos sequencialmente por cabeçalhos de transporte, rede e enlace.\n\nPara que um pacote consiga ser roteado através de múltiplas redes intermediárias heterogêneas até atingir o seu destino final, um conjunto de informações de endereçamento lógico global deve ser lido pelos roteadores ao longo do caminho.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica a camada do modelo OSI responsável pelo endereçamento lógico fim-a-fim, roteamento de pacotes e controle de fragmentação:",
            "opt_a": "Camada de Rede (Camada 3).", "opt_b": "Camada de Enlace (Camada 2).", "opt_c": "Camada de Transporte (Camada 4).", "opt_d": "Camada de Aplicação (Camada 7).",
            "feedback": "A resposta certa é Camada de Rede (Camada 3).\nComentário: A Camada de Rede (Network Layer) gerencia o endereçamento IP, decisão de rotas e encaminhamento de pacotes entre diferentes sub-redes.\nFonte: Infraestrutura de redes, UA 2."
        },
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Comutação em Camada 2 e Protocolo Spanning Tree (STP)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Em uma topologia de rede local de camada 2 composta por múltiplos switches Ethernet interligados por links de fibra óptica, a equipe de infraestrutura manteve conexões físicas redundantes em anel para garantir alta disponibilidade em caso de rompimento de cabos.\n\nEntretanto, se todas as portas dos switches permanecerem ativas sem um controle lógico, quadros de broadcast (como requisições ARP) circularão infinitamente em anel, provocando tempestades de broadcast (Broadcast Storms) que travam completamente a rede.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta o protocolo de camada de enlace projetado para construir uma topologia lógica em árvore sem loops, bloqueando portas redundantes:",
            "opt_a": "STP (Spanning Tree Protocol - IEEE 802.1D).", "opt_b": "BGP (Border Gateway Protocol).", "opt_c": "OSPF (Open Shortest Path First).", "opt_d": "LACP (Link Aggregation Control Protocol).",
            "feedback": "A resposta certa é STP (Spanning Tree Protocol - IEEE 802.1D).\nComentário: O STP constrói uma árvore lógica sem loops em redes Ethernet de camada 2, colocando portas redundantes em estado de bloqueio (blocking).\nFonte: Infraestrutura de redes, UA 3."
        },
        {
            "ua": "05", "obj": 3, "grau": "DIFÍCIL", "kw": "Roteamento Dinâmico OSPF e Vetor de Distância BGP",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Uma corporação expandiu sua infraestrutura de TI interligando 5 campi universitários. Para gerenciar o roteamento interno de pacotes entre os diversos edifícios, a equipe adota o protocolo dinâmico OSPF (Open Shortest Path First). Ao mesmo tempo, para trocar rotas externas com o seu provedor de internet (ISP) através de um Sistema Autônomo (AS), a empresa configura o protocolo BGP (Border Gateway Protocol).",
            "afirmativas": "Com base nos protocolos de roteamento dinâmico OSPF e BGP, analise as afirmativas:\nI. O OSPF é um protocolo IGP de Estado de Enlace (Link-State) que utiliza o algoritmo de Dijkstra para calcular a árvore de rotas de menor custo dentro da rede interna.\nII. O OSPF exige que todas as áreas não-zero estejam fisicamente ou logicamente (via Virtual Link) conectadas à Área de Backbone (Área 0).\nIII. O protocolo BGP é um protocolo IGP interno que utiliza exclusivamente a métrica de contagem de saltos (Hop Count) limitada ao máximo de 15 saltos.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem perfeitamente o OSPF. A afirmativa III é falsa pois o BGP é um protocolo EGP de Vetor de Caminho (Path Vector), enquanto o limite de 15 saltos é do RIP.\nFonte: Infraestrutura de redes, UA 5."
        },
        {
            "ua": "08", "obj": 1, "grau": "DIFÍCIL", "kw": "VLANs (IEEE 802.1Q) e Troncos Trunking",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Para segregar o tráfego dos departamentos de Engenharia, Financeiro e Visitantes sobre uma mesma infraestrutura física de switches de rede, a equipe de TI estabeleceu redes locais virtuais (VLANs).\n\nAs conexões que interligam os switches principais precisam transportar os quadros pertencentes a todas as VLANs configuradas de forma isolada e identificada.",
            "afirmativas": "Com base no padrão IEEE 802.1Q e no roteamento inter-VLAN, analise as afirmativas:\nI. O padrão IEEE 802.1Q insere uma tag de 4 bytes no cabeçalho do quadro Ethernet contendo o identificador numérico da VLAN (VLAN ID).\nII. Conexões configuradas como Trunk (Tronco) transportam tráfego etiquetado (tagged) de múltiplas VLANs entre switches de rede.\nIII. A comunicação em camada 2 entre estações pertencentes a VLANs distintas ocorre de forma direta no mesmo switch sem a necessidade de roteamento L3.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II estão corretas. A afirmativa III é falsa pois a comunicação entre VLANs distintas exige obrigatoriamente roteamento de camada 3 (Router-on-a-stick ou Switch L3).\nFonte: Infraestrutura de redes, UA 8."
        },
        {
            "ua": "08", "obj": 2, "grau": "DIFÍCIL", "kw": "Redundância de Gateway com VRRP/HSRP",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Para garantir alta disponibilidade e evitar que a falha de hardware em um roteador de borda interrompa o acesso dos servidores à internet, a equipe de redes implementa o protocolo de redundância de primeiro salto VRRP (Virtual Router Redundancy Protocol).",
            "afirmativas": "Com base no funcionamento dos protocolos de redundância de gateway (FHRP), analise as afirmativas:\n\nI. O VRRP agrupa dois ou mais roteadores físicos sob um único endereço IP virtual e endereço MAC virtual compartilhado pelos clientes da sub-rede local.\n\nPORQUE\n\nII. Em caso de falha do roteador Master, o roteador Backup assume instantaneamente o encaminhamento dos pacotes destinados ao IP virtual sem necessidade de alterar o gateway padrão nas estações de trabalho.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A virtualização do endereço IP/MAC no VRRP permite alta disponibilidade do gateway transparente aos clientes da sub-rede.\nFonte: Infraestrutura de redes, UA 8."
        }
    ]
)

# 7. Infraestrutura de TI
create_exam(
    "Infraestrutura de TI (4º per Redes)", "Infraestrutura de TI", "AI Infraestrutura de TI", "1; 3; 10; 12",
    [
        {
            "ua": "01", "obj": 1, "grau": "MÉDIA", "kw": "Componentes de Infraestrutura de TI e Data Center",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "O planejamento e construção de um Data Center corporativo de alta densidade exige o dimensionamento integrado de ativos de hardware de processamento, storages de armazenamento, conectividade de rede, sistemas operacionais e infraestrutura predial de apoio.\n\nPara garantir a operação contínua de 24x7 dos servidores mesmo em cenários de blecaute ou oscilações severas na rede elétrica da concessionária pública, o projeto especifica subsistemas elétricos dedicados.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica o componente de infraestrutura predial responsável por fornecer energia ininterrupta via baterias e cobrir a transição até o acionamento do gerador:",
            "opt_a": "Sistema de No-Break (UPS) combinado com Grupo Gerador a Diesel.", "opt_b": "Chiller de condensação a ar comprimido.", "opt_c": "Switch Core de fibra óptico redundante.", "opt_d": "Servidor de diretórios LDAP/Active Directory.",
            "feedback": "A resposta certa é Sistema de No-Break (UPS) combinado com Grupo Gerador a Diesel.\nComentário: O UPS fornece energia instantânea via baterias para cobrir o intervalo até a partida automatizada do grupo gerador a diesel.\nFonte: Infraestrutura de TI, UA 1."
        },
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Virtualização de Servidores e Hypervisors (Tipo 1 e Tipo 2)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Para reduzir os custos operacionais de energia e espaço físico, o gerente de TI de uma instituição de ensino orienta a consolidação de 30 servidores físicos legados em um cluster de dois servidores físicos de alta capacidade utilizando virtualização.\n\nA arquitetura exige a instalação de uma camada de software de virtualização que rode diretamente sobre o hardware limpo (Bare-Metal) para maximizar o desempenho de I/O.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que classifica corretamente o tipo de hypervisor (como VMware ESXi ou Proxmox VE) que é instalado diretamente sobre o hardware físico (Bare-Metal) sem um SO hospedeiro prévio:",
            "opt_a": "Hypervisor Tipo 1 (Bare-Metal).", "opt_b": "Hypervisor Tipo 2 (Hosted).", "opt_c": "Contêiner Docker nativo.", "opt_d": "Emulador de firmware QEMU em modo usuário.",
            "feedback": "A resposta certa é Hypervisor Tipo 1 (Bare-Metal).\nComentário: Hypervisors Tipo 1 rodam diretamente no hardware limpo, oferecendo maior eficiência, menor latência e maior isolamento de recursos para as VMs.\nFonte: Infraestrutura de TI, UA 3."
        },
        {
            "ua": "10", "obj": 3, "grau": "DIFÍCIL", "kw": "Armazenamento SAN, NAS e Protocolos (iSCSI, FC, NFS)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um arquiteto de TI projeta a infraestrutura de armazenamento corporativo de uma empresa de logística. O projeto precisa atender a dois cenários distintos: o banco de dados relacional de transações (exigindo acesso em nível de bloco com ultra-baixa latência) e o repositório de documentos dos funcionários (exigindo compartilhamento de arquivos em nível de sistema de arquivos via rede local).",
            "afirmativas": "Com base nas arquiteturas de armazenamento SAN (Storage Area Network) e NAS (Network Attached Storage), analise as afirmativas:\nI. A arquitetura SAN disponibiliza armazenamento em nível de bloco (Block-Level) através de protocolos como Fibre Channel (FC) e iSCSI.\nII. A arquitetura NAS disponibiliza compartilhamento de arquivos em nível de arquivo (File-Level) via protocolos como NFS e SMB/CIFS.\nIII. O protocolo iSCSI exige obrigatoriamente a construção de um cabeamento óptico dedicado exclusivo incompatível com redes Ethernet.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com precisão SAN (bloco) e NAS (arquivo). A afirmativa III é falsa pois o iSCSI encapsula comandos SCSI em quadros TCP/IP padrão sobre redes Ethernet comuns.\nFonte: Infraestrutura de TI, UA 10."
        },
        {
            "ua": "12", "obj": 1, "grau": "DIFÍCIL", "kw": "Planos de Continuidade de Negócios (PCN), RPO e RTO",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Durante a elaboração da política de continuidade de negócios (PCN) e recuperação de desastres (Disaster Recovery) de uma operadora de plano de saúde, a diretoria executiva define os requisitos de tolerância a falhas para o sistema de agendamento de consultas.",
            "afirmativas": "Com base nas métricas RPO (Recovery Point Objective) e RTO (Recovery Time Objective), analise as afirmativas:\nI. O RPO estabelece a quantidade máxima de perda de dados aceitável (medida em tempo, ex: 15 minutos de transações perdidas desde o último backup).\nII. O RTO estabelece o tempo máximo permitido para restabelecer o funcionamento operacional do serviço após a ocorrência de um desastre.\nIII. Reduzir o RPO e o RTO a zero não causa qualquer impacto financeiro no investimento em infraestrutura e replicação de dados síncrona.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem os conceitos basilares de RPO e RTO. A afirmativa III é falsa pois atingir RPO=0 e RTO=0 exige replicação síncrona redundante de altíssimo custo.\nFonte: Infraestrutura de TI, UA 12."
        },
        {
            "ua": "12", "obj": 2, "grau": "DIFÍCIL", "kw": "Níveis de Redundância de Data Center (Tier I a Tier IV - Uptime Institute)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Uma empresa de serviços financeiros precisa contratar um Data Center fornecedor de colocation que garanta disponibilidade mínima de 99,995% ao ano com tolerância total a falhas (Fault Tolerant).",
            "afirmativas": "Com base no sistema de classificação por Tiers do Uptime Institute, analise as afirmativas:\n\nI. Um Data Center certificado como Tier IV exige caminhos de distribuição de energia e refrigeração múltiplos e ativos simultaneamente (redundância 2N+1), permitindo manutenções e suportando qualquer falha individual sem causar paralisações.\n\nPORQUE\n\nII. A certificação Tier I admite componentes de capacidade não redundantes e caminho único de distribuição sem piso elevado, resultando em paralisações programadas e não programadas ao longo do ano.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.\nComentário: Ambas as afirmativas são descrições verdadeiras dos níveis Tier IV e Tier I da Uptime Institute. Porém, a infraestrutura simples do Tier I não é a justificativa da alta redundância do Tier IV, tratando-se de constatações independentes.\nFonte: Infraestrutura de TI, UA 12."
        }
    ]
)

print("Batch 2 atualizado com contextualização ENADE robusta (> 7 linhas).")
