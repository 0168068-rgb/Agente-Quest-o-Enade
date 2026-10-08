# -*- coding: utf-8 -*-
"""
Batch PS 2: Disciplinas 5 a 7 (Provas PS 2026-4 - Novos Objetivos e Contextualização ENADE > 7 linhas)
"""
from generate_full_batch import create_exam

# 5. Gerenciamento de redes de computadores
create_exam(
    "Gerenciamento de Redes", "Gerenciamento de redes de computadores", "PS Gerenciamento de redes de computadores", "3; 4; 8; 11",
    [
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Armadilha SNMP (SNMP Traps / InformRequest)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em um sistema de monitoramento de redes corporativo baseado em SNMPv3, o servidor NMS (Network Management System) realiza polling periódico para consultar métricas de tráfego das interfaces dos roteadores de borda.\n\nPara evitar que falhas críticas de hardware (como a queda abrupta de uma interface de fibra ou superaquecimento da CPU) sejam identificadas apenas na consulta seguinte do polling, os roteadores são configurados para enviar notificações assíncronas não solicitadas imediatamente ao NMS quando o evento ocorre.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o tipo de mensagem assíncrona gerada espontaneamente por um agente SNMP para alertar o gerenciador sobre um evento crítico:",
            "opt_a": "SNMP Trap.", "opt_b": "SNMP GetNextRequest.", "opt_c": "SNMP SetRequest.", "opt_d": "SNMP GetResponse.",
            "feedback": "A resposta certa é SNMP Trap.\nComentário: As mensagens SNMP Trap (ou InformRequest) são alertas assíncronos enviados pelo agente para o NMS assim que uma alteração de estado ou falha é detectada.\nFonte: Gerenciamento de redes de computadores, UA 3."
        },
        {
            "ua": "04", "obj": 3, "grau": "MÉDIA", "kw": "Arquitetura de Protocolo NetFlow/IPFIX",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Para obter visibilidade sobre o perfil de consumo de dados e aplicações que trafegam na rede corporativa, o engenheiro de redes habilita o protocolo NetFlow v9 nos roteadores de borda.\n\nDiferente do espelhamento de portas (SPAN) que analisa todo o conteúdo dos pacotes, o NetFlow agrupa os pacotes em fluxos lógicos baseados na tupla de 5 elementos (IP Origem, IP Destino, Porta Origem, Porta Destino e Protocolo de Transporte), exportando as estatísticas para um coletor central.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta o principal benefício da tecnologia NetFlow/IPFIX para a gerência de redes:",
            "opt_a": "Análise estatística de volume e perfil de tráfego por aplicação com baixo consumo de processamento nos coletores.", "opt_b": "Criptografia automática dos pacotes em trânsito no backbone.", "opt_c": "Substituição completa do protocolo de roteamento OSPF.", "opt_d": "Eliminação do uso de firewalls na borda da rede.",
            "feedback": "A resposta certa é Análise estatística de volume e perfil de tráfego por aplicação com baixo consumo de processamento nos coletores.\nComentário: O NetFlow fornece contabilidade de fluxos de tráfego detalhada, identificando quem consome banda e quais aplicações geram tráfego sem a sobrecarga de inspecionar payloads completos.\nFonte: Gerenciamento de redes de computadores, UA 4."
        },
        {
            "ua": "08", "obj": 1, "grau": "DIFÍCIL", "kw": "Protocolo Syslog (RFC 5424) e Servidores SIEM",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Uma equipe de resposta a incidentes de segurança (CSIRT) centraliza os registros de eventos (logs) gerados por 200 ativos de rede (firewalls, switches, servidores Linux e Windows) em um servidor SIEM (Security Information and Event Management).\n\nOs dispositivos enviam seus eventos em tempo real utilizando o protocolo padrão Syslog (UDP/TCP porta 514), o qual categoriza cada mensagem com base na sua Instalação (Facility) e Nível de Severidade (Severity Level, variando de 0-Emergency a 7-Debug).",
            "afirmativas": "Com base no protocolo Syslog e gestão de registros, analise as afirmativas:\nI. O protocolo Syslog padronizado pela RFC 5424 classifica os eventos por níveis de severidade, permitindo filtrar mensagens críticas de erro em relação a avisos informativos.\nII. Servidores SIEM correlacionam múltiplos logs Syslog recebidos de diferentes ativos para identificar ataques distribuídos complexos.\nIII. O protocolo Syslog em modo UDP padrão garante a entrega de 100% das mensagens de log sem possibilidade de perda de pacotes.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão os níveis do Syslog e a função do SIEM. A afirmativa III é falsa pois o transporte sobre UDP não fornece garantia de entrega ou retransmissão.\nFonte: Gerenciamento de redes de computadores, UA 8."
        },
        {
            "ua": "11", "obj": 2, "grau": "DIFÍCIL", "kw": "Gerenciamento de Falhas e Acordos de SLA (MTBF e MTTR)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Durante a reunião trimestral de revisão dos Acordos de Nível de Serviço (SLA) de infraestrutura de TI de um provedor de internet (ISP), o gestor de redes analisa os indicadores operacionais chave de desempenho (KPIs) da rede de fibra óptica.\n\nOs dois principais indicadores avaliados são o Tempo Médio Entre Falhas (MTBF - Mean Time Between Failures) e o Tempo Médio Para Reparo (MTTR - Mean Time To Repair), utilizados para calcular a disponibilidade percentual total do serviço.",
            "afirmativas": "Com base nos indicadores de disponibilidade e métricas MTBF/MTTR, analise as afirmativas:\nI. O MTBF mede a confiabilidade do sistema, representando o tempo médio operacional em que o equipamento funciona sem apresentar interrupções.\nII. O MTTR mede a eficiência da equipe de suporte e manutenção na resolução de incidentes, representando o tempo médio desde a ocorrência da falha até a restauração completa do serviço.\nIII. Reduzir o MTTR para zero diminui a disponibilidade percentual do sistema segundo a fórmula matemática padrão.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II apresentam com precisão os conceitos de MTBF e MTTR. A afirmativa III é falsa pois quanto menor o MTTR (tempo de reparo), maior será a disponibilidade final do sistema (`Disponibilidade = MTBF / (MTBF + MTTR)`).\nFonte: Gerenciamento de redes de computadores, UA 11."
        },
        {
            "ua": "11", "obj": 3, "grau": "DIFÍCIL", "kw": "Gerenciamento de Mudanças e Configuração com Rancid/Git",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Após uma alteração não autorizada na regra de um roteador de borda causar a queda do serviço de internet de uma filial por 3 horas, a empresa implementou uma ferramenta de gestão automatizada de configuração de ativos de rede (como RANCID ou Oxidized) integrada a um repositório Git.\n\nA ferramenta realiza backup diário do arquivo de configuração de todos os switches e roteadores e envia alertas de diff sempre que uma linha do arquivo de configuração é modificada.",
            "afirmativas": "Com base nas boas práticas de gerência de configuração em redes de computadores, analise as afirmativas:\n\nI. A automação do versionamento de configurações de ativos de rede permite rastrear quem alterou, quando alterou e qual linha de comando foi modificada, viabilizando o rollback imediato para uma versão estável em caso de falha.\n\nPORQUE\n\nII. O gerenciamento de mudanças previne que alterações acidentais ou maliciosas em equipamentos de rede passem despercebidas, garantindo a governança e o alinhamento com auditorias de compliance.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A rastreabilidade e a capacidade de rollback rápido são os pilares da governança de gerência de configuração de redes.\nFonte: Gerenciamento de redes de computadores, UA 11."
        }
    ],
    subfolder='PS'
)

# 6. Infraestrutura de redes
create_exam(
    "Infraestrutura de rede (seg)", "Infraestrutura de redes", "PS Infraestrutura de redes", "2; 3; 5; 8",
    [
        {
            "ua": "02", "obj": 2, "grau": "MÉDIA", "kw": "Protocolo Spanning Tree (STP - IEEE 802.1D / RSTP 802.1w)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Para fornecer alta disponibilidade e tolerância a falhas na camada 2 de uma rede local corporativa, a equipe de infraestrutura interligou 3 switches em uma topologia em anel redundante.\n\nSem um protocolo de controle ativo, o envio de um único pacote de broadcast (como um ARP Request) provocaria uma tempestade de broadcast (Broadcast Storm) e a corrupção da tabela MAC dos switches. O protocolo Spanning Tree (STP - IEEE 802.1D) é ativado para bloquear logicamente uma das portas do anel.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica a mensagem de controle trocada periodicamente entre os switches para eleger o Root Bridge e calcular a árvore livre de loops no STP:",
            "opt_a": "BPDU (Bridge Protocol Data Unit).", "opt_b": "LCP (Link Control Protocol).", "opt_c": "ICMP Echo Request.", "opt_d": "ARP Reply.",
            "feedback": "A resposta certa é BPDU (Bridge Protocol Data Unit).\nComentário: BPDUs são os quadros de controle utilizados pelos switches STP/RSTP para trocar informações de ID de ponte, custo de caminho e estado de portas.\nFonte: Infraestrutura de redes, UA 2."
        },
        {
            "ua": "03", "obj": 3, "grau": "MÉDIA", "kw": "Roteamento Inter-VLAN com Roteador em um Palito (Router-on-a-Stick)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Uma empresa segmentou sua rede local em duas VLANs distintas: VLAN 10 (Financeiro) e VLAN 20 (Engenharia). Um switch L2 conecta os computadores de ambas as redes, mas os usuários da VLAN 10 precisam se comunicar com os servidores da VLAN 20.\n\nPara realizar o roteamento entre as VLANs utilizando um único roteador conectado ao switch por um cabo de par trançado (arquitetura Router-on-a-Stick), a interface física do roteador é dividida em sub-interfaces lógicas com encapsulamento IEEE 802.1Q.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o tipo de link configurado na porta do switch que conecta o roteador na arquitetura Router-on-a-Stick:",
            "opt_a": "Trunk (Tronco IEEE 802.1Q).", "opt_b": "Access (Acesso de porta única).", "opt_c": "Console RS-232.", "opt_d": "Loopback virtual.",
            "feedback": "A resposta certa é Trunk (Tronco IEEE 802.1Q).\nComentário: A porta do switch deve ser configurada como Trunk para multiplexar o tráfego de múltiplas VLANs etiquetadas (802.1Q) através de um único link físico até o roteador.\nFonte: Infraestrutura de redes, UA 3."
        },
        {
            "ua": "05", "obj": 1, "grau": "DIFÍCIL", "kw": "Protocolos de Roteamento Dinâmico Interior (OSPF vs EIGRP)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "No projeto de roteamento interno da rede corporativa de um grupo empresarial composta por 15 roteadores, o engenheiro de redes avalia a implantação do protocolo OSPF (Open Shortest Path First).\n\nO OSPF é um protocolo de Roteamento por Estado de Enlace (Link-State) baseado no algoritmo de Dijkstra, que divide a rede em Áreas (com a Área 0 / Backbone como centro obrigatório) para otimizar o consumo de memória e convergência.",
            "afirmativas": "Com base no funcionamento do protocolo de roteamento OSPF, analise as afirmativas:\nI. Todos os roteadores pertencentes à mesma área OSPF mantêm um banco de dados de estado de enlace (LSDB) idêntico.\nII. O OSPF utiliza a métrica de Custo (baseada na largura de banda do link) para determinar o caminho mais curto.\nIII. O OSPF limita a quantidade máxima de saltos (Hop Count) na rede a no máximo 15 roteadores.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II descrevem perfeitamente o LSDB e a métrica de custo do OSPF. A afirmativa III é falsa pois o limite de 15 saltos é uma limitação do protocolo RIP, não do OSPF.\nFonte: Infraestrutura de redes, UA 5."
        },
        {
            "ua": "08", "obj": 2, "grau": "DIFÍCIL", "kw": "Protocolo BGP (Border Gateway Protocol) e Sistema Autônomo (AS)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Um provedor de internet (ISP) obteve o registro de seu próprio Sistema Autônomo (ASN) junto ao Registro.br e precisa estabelecer conexões de troca de tráfego com duas operadoras de telecomunicações distintas (Multihoming).\n\nPara gerenciar o roteamento externo entre Sistemas Autônomos na internet global, a equipe de redes configura sessões eBGP (External BGP) nos seus roteadores de borda.",
            "afirmativas": "Com base na arquitetura do protocolo BGP, analise as afirmativas:\nI. O BGP é classificado como um protocolo de vetor de caminhos (Path Vector) que utiliza atributos (como AS-Path e Local Preference) para seleção de rotas.\nII. As conexões de vizinhança (Peering) BGP são estabelecidas através de sessões TCP diretas na porta 179.\nIII. O protocolo eBGP utiliza transmissões de Broadcast UDP em rede local para descobrir roteadores vizinhos automaticamente.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão o BGP como Path Vector e o uso de TCP 179 para vizinhança. A afirmativa III é falsa pois vizinhos BGP devem ser configurados manualmente por IP sem discovery por broadcast.\nFonte: Infraestrutura de redes, UA 8."
        },
        {
            "ua": "08", "obj": 3, "grau": "DIFÍCIL", "kw": "Tradução de Endereços de Rede (NAT/PAT - Port Address Translation)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Em uma rede local de escritório com 250 computadores configurados com endereços IP privados (faixa 192.168.1.0/24), todos os usuários navegam simultaneamente na internet utilizando um único endereço IPv4 público atribuído ao roteador pelo provedor.\n\nO roteador executa a Tradução de Endereços de Rede com Sobreposição de Portas (PAT / NAPT - Network Address Port Translation).",
            "afirmativas": "Com base na mecânica do PAT (Port Address Translation), analise as afirmativas:\n\nI. O PAT permite que centenas de hosts com IPs privados compartilhem um único IP público na internet mapeando cada conexão interna para uma porta de transporte de origem dinâmica única no roteador.\n\nPORQUE\n\nII. Quando os pacotes de resposta retornam da internet, a tabela de tradução do PAT utiliza o número da porta de destino para identificar univocamente a qual IP privado interno a resposta pertence.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A multiplexação por portas L4 é o mecanismo exato que permite o reuso de um único IP público para centenas de estações privadas.\nFonte: Infraestrutura de redes, UA 8."
        }
    ],
    subfolder='PS'
)

# 7. Infraestrutura de TI
create_exam(
    "Infraestrutura de TI (4º per Redes)", "Infraestrutura de TI", "PS Infraestrutura de TI", "1; 3; 10; 12",
    [
        {
            "ua": "01", "obj": 2, "grau": "MÉDIA", "kw": "Modelos de Governança de TI (ITIL 4 e COBIT 2019)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "A diretoria de TI de um grupo multinacional decide reestruturar os processos de gestão de serviços e alinhamento estratégico da tecnologia aos objetivos de negócios da corporação.\n\nPara orientar a criação de valor, gerenciamento de incidentes e entrega contínua de serviços de TI aos clientes internos, a equipe adota o framework de boas práticas ITIL 4 (Information Technology Infrastructure Library).",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o componente central do ITIL 4 responsável por descrever como todos os componentes e atividades da organização trabalham juntos para criar valor:",
            "opt_a": "Sistema de Valor do Serviço (SVS - Service Value System).", "opt_b": "Matriz RACI de Projetos.", "opt_c": "Diagrama de Causa e Efeito de Ishikawa.", "opt_d": "Banco de Dados de Conhecimento SQL.",
            "feedback": "A resposta certa é Sistema de Valor do Serviço (SVS - Service Value System).\nComentário: O SVS é o modelo central do ITIL 4, representando como a oportunidade/demanda é convertida em valor real através dos princípios orientadores, governança e cadeia de valor.\nFonte: Infraestrutura de TI, UA 1."
        },
        {
            "ua": "03", "obj": 3, "grau": "MÉDIA", "kw": "Servidores de Armazenamento NAS vs SAN (iSCSI / Fiber Channel)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Durante o dimensionamento do sistema de armazenamento de dados para um ambiente de virtualização de servidores com alta demanda de IOPS em banco de dados, o arquiteto de TI compara as arquiteturas NAS (Network Attached Storage) e SAN (Storage Area Network).\n\nA solução escolhida deve fornecer acesso em nível de bloco de disco (Block-level storage) via rede dedicada de altíssima velocidade utilizando o protocolo Fiber Channel ou iSCSI.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta a principal característica de uma rede de armazenamento SAN em comparação a um servidor NAS:",
            "opt_a": "A SAN disponibiliza volumes de armazenamento em nível de bloco, permitindo que os servidores formate os discos com seu próprio sistema de arquivos.", "opt_b": "A SAN compartilha arquivos exclusivamente via protocolos de arquivos NFS e SMB/CIFS.", "opt_c": "O NAS exige cabeamento óptico proprietário incompatível com redes Ethernet.", "opt_d": "A SAN opera exclusivamente dentro da nuvem pública sem suporte a equipamentos físicos.",
            "feedback": "A resposta certa é A SAN disponibiliza volumes de armazenamento em nível de bloco, permitindo que os servidores formate os discos com seu próprio sistema de arquivos.\nComentário: Redes SAN fornecem armazenamento em nível de bloco (como se fosse um HD local), enquanto NAS fornece armazenamento em nível de arquivos (File-level).\nFonte: Infraestrutura de TI, UA 3."
        },
        {
            "ua": "10", "obj": 1, "grau": "DIFÍCIL", "kw": "Virtualização de Servidores e Gerenciamento de Hypervisores (Type 1 vs Type 2)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Uma empresa de desenvolvimento de sistemas precisa implantar uma infraestrutura de virtualização no seu Data Center para consolidar 40 servidores físicos em 3 servidores de alta densidade.\n\nO arquiteto de TI analisa a arquitetura de Hypervisores Tipo 1 (Bare-Metal, como VMware ESXi ou Proxmox VE) e Hypervisores Tipo 2 (Hosted, como VirtualBox ou VMware Workstation).",
            "afirmativas": "Com base na tecnologia de virtualização de servidores, analise as afirmativas:\nI. Hypervisores Tipo 1 (Bare-Metal) rodam diretamente sobre o hardware físico sem a necessidade de um sistema operacional hospedeiro intermediário.\nII. Hypervisores Tipo 1 oferecem maior desempenho e eficiência computacional para ambientes de produção corporativos.\nIII. Hypervisores Tipo 2 rodam dentro de um sistema operacional hospedeiro tradicional, sendo indicados para ambientes de testes de desenvolvimento.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I, II e III.", "opt_b": "I e II, apenas.", "opt_c": "I e III, apenas.", "opt_d": "II e III, apenas.",
            "feedback": "A resposta certa é I, II e III.\nComentário: Todas as afirmativas são verdadeiras. Hypervisores Bare-Metal (Tipo 1) interagem direto com o hardware garantindo máximo desempenho em produção, enquanto Tipo 2 roda sobre um SO hospedeiro para testes.\nFonte: Infraestrutura de TI, UA 10."
        },
        {
            "ua": "12", "obj": 2, "grau": "DIFÍCIL", "kw": "Plano de Continuidade de Negócios (PCN) e RPO/RTO",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Durante a elaboração do Plano de Continuidade de Negócios (PCN) e de Recuperação de Desastres (DRP) de uma instituição financeira, a equipe de governança de TI estabelece os parâmetros de RPO (Recovery Point Objective) e RTO (Recovery Time Objective).\n\nEm um cenário hipotético de ataque de Ransomware que paralise o banco de dados principal às 14:00h, os gestores analisam quanto tempo o sistema pode ficar fora do ar e qual a tolerância máxima de perda de transações recentes.",
            "afirmativas": "Com base nas métricas RPO e RTO de continuidade de negócios, analise as afirmativas:\nI. O RPO (Objetivo de Ponto de Recuperação) define a quantidade máxima tolerável de perda de dados medida em tempo (ex: perder no máximo 15 minutos de transações).\nII. O RTO (Objetivo de Tempo de Recuperação) define o tempo máximo aceitável para restaurar os serviços de TI após a ocorrência do desastre.\nIII. Um RPO igual a zero exige que a empresa realize backups manuais semanais em fita magnética.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão RPO (perda de dados) e RTO (tempo de indisponibilidade). A afirmativa III é falsa pois RPO zero exige replicação de dados síncrona em tempo real.\nFonte: Infraestrutura de TI, UA 12."
        },
        {
            "ua": "12", "obj": 3, "grau": "DIFÍCIL", "kw": "Estratégias de Backup (Completo, Incremental e Diferencial)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "O administrador de sistemas de um portal de e-commerce planeja a rotina de cópias de segurança (backup) dos servidores de aplicação e bancos de dados.\n\nPara otimizar o tempo de janela de backup noturno e a capacidade de armazenamento de disco nos repositórios, ele combina um Backup Completo (Full) executado aos domingos com backups diários de segunda a sábado.",
            "afirmativas": "Com base no funcionamento dos tipos de backup (Incremental vs Diferencial), analise as afirmativas:\n\nI. O Backup Incremental copia apenas os dados que foram alterados desde o último backup realizado (seja ele Full ou Incremental), resultando em janelas de backup diárias mais rápidas.\n\nPORQUE\n\nII. Durante o processo de restauração total após um desastre, o Backup Incremental exige a restauração do último Backup Completo seguido da aplicação sequencial de TODOS os backups incrementais diários em ordem cronológica.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A velocidade do backup incremental durante a gravação compensa o processo de restauração mais complexo e encadeado.\nFonte: Infraestrutura de TI, UA 12."
        }
    ],
    subfolder='PS'
)

print("Batch PS 2 concluído.")
