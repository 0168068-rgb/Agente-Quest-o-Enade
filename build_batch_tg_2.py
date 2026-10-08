# -*- coding: utf-8 -*-
"""
Batch TG 2: Disciplinas 5 a 7 (Provas TG 2026-4 - UAs Específicas do Tema Gerador e Contextualização ENADE > 7 linhas)
"""
from generate_full_batch import create_exam

# 5. Gerenciamento de redes de computadores (UAs 3, 4)
create_exam(
    "Gerenciamento de Redes", "Gerenciamento de redes de computadores", "AD Gerenciamento de redes de computadores", "3; 4",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Arquitetura de Gerenciamento SNMP (SMI, MIB e Agente/NMS)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em uma arquitetura de gerência de redes corporativa baseada no modelo cliente-servidor do protocolo SNMP (Simple Network Management Protocol), o software gerenciador NMS (Network Management System) consulta periodicamente os ativos de rede (roteadores, switches e firewalls).\n\nCada ativo de rede executa um processo interno chamado Agente SNMP, que consulta e atualiza o banco de dados hierárquico de objetos de gerenciamento chamado MIB (Management Information Base).",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica o banco de dados estruturado em árvore de identificadores de objetos (OIDs) mantido no ativo de rede para consulta pelo NMS:",
            "opt_a": "MIB (Management Information Base).", "opt_b": "SMI (Structure of Management Information).", "opt_c": "DNS (Domain Name System).", "opt_d": "ARP (Address Resolution Protocol).",
            "feedback": "A resposta certa é MIB (Management Information Base).\nComentário: A MIB é a base de dados estruturada que armazena todas as variáveis de gerenciamento (OIDs) consultadas pelo NMS através do agente SNMP.\nFonte: Gerenciamento de redes de computadores, UA 3."
        },
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Comandos PDU do SNMP (Get, GetNext, Set e Response)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Um administrador de redes utiliza uma ferramenta de gerência via linha de comando para alterar o nome de contato do administrador (`sysContact`) de um roteador de borda via protocolo SNMPv2c/SNMPv3.\n\nEle precisa enviar uma Unidade de Dados de Protocolo (PDU) que altere remotamente o valor da variável de gerenciamento contida na MIB do roteador.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o comando PDU do SNMP utilizado pelo NMS para modificar o valor de uma variável na MIB de um agente:",
            "opt_a": "SetRequest.", "opt_b": "GetRequest.", "opt_c": "GetNextRequest.", "opt_d": "TrapRequest.",
            "feedback": "A resposta certa é SetRequest.\nComentário: A PDU `SetRequest` é enviada pelo gerenciador NMS para alterar/gravar o valor de um objeto específico na MIB do agente SNMP.\nFonte: Gerenciamento de redes de computadores, UA 3."
        },
        {
            "ua": "04", "obj": 1, "grau": "DIFÍCIL", "kw": "Protocolos de Coleta de Fluxos (NetFlow / sFlow / IPFIX)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Para identificar quais usuários ou aplicações estão consumindo toda a largura de banda do link de internet de 1 Gbps da empresa durante horários de pico, a equipe de redes habilita a exportação de fluxos de tráfego nos roteadores de borda.\n\nEles analisam as diferenças operacionais entre a amostragem de pacotes estatística do **sFlow** e a contabilidade de fluxos baseada em estado do **NetFlow** / **IPFIX** (RFC 7011).",
            "afirmativas": "Com base nos protocolos de monitoramento de fluxo de tráfego, analise as afirmativas:\nI. O NetFlow agrupa pacotes com as mesmas características de 5 tuplas em fluxos na memória do roteador antes de exportar as estatísticas.\nII. O sFlow utiliza amostragem estatística de pacotes em hardware (ex: 1 a cada 1000 pacotes), enviando a cópia diretamente para o coletor sem manter tabelas de fluxo no switch.\nIII. O NetFlow e o sFlow dependem da leitura do protocolo SNMP para capturar o conteúdo completo de arquivos baixados pelos usuários.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II diferenciam corretamente o empacotamento em fluxos do NetFlow e a amostragem pura do sFlow. A afirmativa III é falsa pois NetFlow/sFlow são protocolos independentes do SNMP e não inspecionam o conteúdo completo dos arquivos.\nFonte: Gerenciamento de redes de computadores, UA 4."
        },
        {
            "ua": "04", "obj": 2, "grau": "DIFÍCIL", "kw": "Monitoramento de Largura de Banda e Alertas com MRTG/Zabbix",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Uma equipe de operações de TI (NOC) utiliza o sistema **Zabbix** para monitorar continuamente o uso de CPU, memória RAM e tráfego de rede (bits/s de entrada e saída) de 100 servidores e ativos de rede.\n\nO sistema utiliza Triggers para disparar alertas visuais e notificações via Telegram/E-mail sempre que o uso de banda de um link ultrapassa 90% por mais de 5 minutos consecutivos.",
            "afirmativas": "Com base no monitoramento de desempenho de redes com Zabbix, analise as afirmativas:\nI. O Zabbix armazena as métricas coletadas em um banco de dados relacional e gera gráficos de tendência de consumo de tráfego ao longo do tempo.\nII. Triggers no Zabbix definem expressões lógicas sobre os dados coletados que determinam o estado de um problema (Ok ou Problem).\nIII. O Zabbix exige obrigatoriamente a reinicialização física dos roteadores de borda para registrar a ocorrência de um alerta de tráfego elevado.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com exatidão o armazenamento histórico e a lógica de Triggers no Zabbix. A afirmativa III é falsa pois o Zabbix apenas monitora passivamente os dados sem reiniciar equipamentos.\nFonte: Gerenciamento de redes de computadores, UA 4."
        },
        {
            "ua": "04", "obj": 3, "grau": "DIFÍCIL", "kw": "Sondagem RMON (Remote Monitoring) em Switches L2",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Para monitorar as estatísticas de colisão, quadros com erro de CRC e padrões de tráfego diretamente nos segmentos de rede local de switches sem sobrecarregar o link de gerência com polling SNMP frequente, o arquiteto habilita o recurso **RMON** (Remote Monitoring - RFC 2819).\n\nSondas RMON embutidas nos switches coletam estatísticas das portas e mantêm tabelas locais de históricos e alarmes.",
            "afirmativas": "Com base na tecnologia de monitoramento remoto RMON, analise as afirmativas:\n\nI. A especificação RMON define grupos MIB específicos (como Estatísticas, Histórico, Alarmes e Eventos) que permitem ao próprio switch analisar o tráfego local e disparar eventos apenas quando limites pré-configurados forem violados.\n\nPORQUE\n\nII. O processamento descentralizado do RMON reduz significativamente o tráfego de gerência transmitido pela rede, desonerando o servidor NMS central do polling contínuo de contadores brutos.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A descentralização da análise de métricas no próprio ativo através dos grupos RMON é a razão direta para a redução de tráfego de gerência na rede.\nFonte: Gerenciamento de redes de computadores, UA 4."
        }
    ],
    subfolder='AD'
)

# 6. Infraestrutura de redes (UAs 2, 3)
create_exam(
    "Infraestrutura de rede (seg)", "Infraestrutura de redes", "AD Infraestrutura de redes", "2; 3",
    [
        {
            "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Conceito e Vantagens de Redes Locais Virtuais (VLANs - IEEE 802.1Q)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em uma empresa corporativa com 200 computadores conectados ao mesmo conjunto de switches físicos de camada 2, o tráfego de broadcast gerado por protocolos como ARP e DHCP satura o desempenho da rede local.\n\nPara solucionar esse gargalo e isolar o tráfego do departamento Financeiro do departamento de Visitantes sem adquirir novos switches físicos, a equipe de infraestrutura implementa **VLANs** (Virtual Local Area Networks) baseadas na norma IEEE 802.1Q.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica a principal vantagem técnica da criação de VLANs em switches de camada 2:",
            "opt_a": "Subdividir um domínio de broadcast físico em múltiplos domínios de broadcast lógicos menores e isolados.", "opt_b": "Aumentar a velocidade física dos cabos de par trançado de 100 Mbps para 10 Gbps.", "opt_c": "Criptografar as senhas salvas nos navegadores das estações de trabalho.", "opt_d": "Eliminar a necessidade de endereços IP nas placas de rede dos computadores.",
            "feedback": "A resposta certa é Subdividir um domínio de broadcast físico em múltiplos domínios de broadcast lógicos menores e isolados.\nComentário: A função primária das VLANs é segmentar domínios de broadcast, aumentando a segurança e reduzindo o impacto de tempestades de broadcast na rede.\nFonte: Infraestrutura de redes, UA 2."
        },
        {
            "ua": "02", "obj": 2, "grau": "MÉDIA", "kw": "Tipos de Portas em Switches (Acesso vs Tronco / Native VLAN)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Na configuração de um switch gerenciável de camada 2, o analista de redes precisa configurar duas portas físicas com funções distintas: uma porta conectada diretamente ao computador de um usuário final e outra porta conectada a um segundo switch para interligar todas as VLANs.\n\nDe acordo com os padrões da norma IEEE 802.1Q, as portas são classificadas nos modos de **Acesso** (Access) e **Tronco** (Trunk).",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o comportamento de uma porta configurada no modo de Acesso (Access):",
            "opt_a": "Pertence a uma única VLAN e transmite quadros Ethernet sem etiqueta de cabeçalho 802.1Q (Untagged) para o dispositivo do usuário.", "opt_b": "Transporta quadros etiquetados de múltiplas VLANs simultaneamente entre switches.", "opt_c": "Conecta exclusivamente roteadores BGP de borda pública.", "opt_d": "Desativa automaticamente o protocolo Spanning Tree na porta.",
            "feedback": "A resposta certa é Pertence a uma única VLAN e transmite quadros Ethernet sem etiqueta de cabeçalho 802.1Q (Untagged) para o dispositivo do usuário.\nComentário: Portas de Acesso conectam computadores finais, pertencem a apenas uma VLAN e removem a etiqueta 802.1Q antes de entregar o quadro ao host.\nFonte: Infraestrutura de redes, UA 2."
        },
        {
            "ua": "03", "obj": 1, "grau": "DIFÍCIL", "kw": "Roteamento Estático em Roteadores IP (Rotas Default e Distância Administrativa)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um administrador de redes configura a tabela de roteamento IP de um roteador de filial contendo duas saídas: um link principal de fibra óptica e um link de backup via rádio de menor velocidade.\n\nEle cria uma Rota Estática Padrão (Default Route `0.0.0.0/0`) direcionada ao link principal e uma Rota Estática Flutuante (Floating Static Route) direcionada ao link de backup ajustando a **Distância Administrativa** (AD).",
            "afirmativas": "Com base no Roteamento Estático e Distância Administrativa, analise as afirmativas:\nI. A Rota Padrão (`0.0.0.0/0` ou `::/0`) é utilizada quando a tabela de roteamento não encontra uma rota mais específica para o IP de destino.\nII. A Distância Administrativa (AD) estabelece a confiabilidade da fonte de rota; quanto MENOR o valor da AD, maior a prioridade de inserção da rota na tabela de roteamento.\nIII. Uma rota estática flutuante de backup deve ser configurada com uma Distância Administrativa MENOR do que a rota estática principal.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com exatidão a rota padrão e o critério de prioridade da AD (menor AD = maior prioridade). A afirmativa III é falsa pois a rota de backup deve ter uma AD MAIOR para ficar inativa enquanto o link principal (menor AD) estiver operacional.\nFonte: Infraestrutura de redes, UA 3."
        },
        {
            "ua": "03", "obj": 2, "grau": "DIFÍCIL", "kw": "Roteamento Inter-VLAN com Switches Camada 3 (SVI - Switched Virtual Interface)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Para realizar o roteamento de altíssimo desempenho em velocidade de barramento de comutação (Wire-Speed) entre 10 VLANs corporativas em um Data Center, a equipe substituiu a arquitetura Router-on-a-Stick por um **Switch de Camada 3** (Multilayer Switch).\n\nNo switch L3, o engenheiro ativa o comando `ip routing` e configura Interfaces Virtuais de Switch (**SVI** - Switched Virtual Interface) para cada VLAN (`interface vlan 10`, `ip address 192.168.10.1 ...`).",
            "afirmativas": "Com base no Roteamento Inter-VLAN por SVIs em switches L3, analise as afirmativas:\nI. Uma SVI é uma interface lógica de camada 3 associada a uma VLAN específica no switch L3, atuando como gateway padrão para os hosts daquela VLAN.\nII. O roteamento inter-VLAN realizado em switches L3 utiliza hardware ASIC especializado de comutação, oferecendo desempenho muito superior ao roteamento em roteadores externos.\nIII. Para ativar a SVI de uma VLAN, basta criá-la no switch, sem necessidade de atribuir um endereço IP válido.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II descrevem perfeitamente a função e a velocidade baseada em ASICs das SVIs em switches L3. A afirmativa III é falsa pois a SVI exige obrigatoriamente a atribuição de um IP/máscara L3 para funcionar como gateway.\nFonte: Infraestrutura de redes, UA 3."
        },
        {
            "ua": "03", "obj": 3, "grau": "DIFÍCIL", "kw": "Resolução de Problemas em Tabelas de Roteamento IP (Longest Prefix Match)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Ao analisar uma tabela de roteamento de um roteador de borda contendo quatro rotas ativas (`10.0.0.0/8`, `10.1.0.0/16`, `10.1.5.0/24` e `0.0.0.0/0`), o analista dispara um teste de envio de pacotes destinados ao IP `10.1.5.42`.\n\nO roteador consulta a tabela de roteamento e precisa decidir por qual interface e próximo salto (Next-Hop) o pacote deve ser encaminhado.",
            "afirmativas": "Com base na regra de decisão de roteamento IP por Maior Casamento de Prefixo (Longest Prefix Match), analise as afirmativas:\n\nI. O pacote destinado ao IP `10.1.5.42` será encaminhado pela rota correspondente ao prefixo `10.1.5.0/24`.\n\nPORQUE\n\nII. Em tabelas de roteamento IP, quando múltiplos prefixos de rede cobrem o mesmo IP de destino, o roteador seleciona a rota que possui a máscara de sub-rede mais específica (maior quantidade de bits de rede correspondentes ao destino).",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A regra fundamental do roteamento IP é o Longest Prefix Match (/24 é mais específico que /16, /8 e /0), justificando a escolha da rota `10.1.5.0/24`.\nFonte: Infraestrutura de redes, UA 3."
        }
    ],
    subfolder='AD'
)

# 7. Infraestrutura de TI (UAs 1, 3)
create_exam(
    "Infraestrutura de TI (4º per Redes)", "Infraestrutura de TI", "AD Infraestrutura de TI", "1; 3",
    [
        {
            "ua": "01", "obj": 1, "grau": "MÉDIA", "kw": "Componentes de Hardware do Data Center (Servidores Blade, Racks, PDU e No-breaks/UPS)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Durante o projeto de montagem da sala de servidores de uma empresa de grande porte, o arquiteto de infraestrutura especifica a aquisição de gabinetes metálicos padronizados de 19 polegadas (Racks 42U).\n\nPara otimizar o espaço físico nos racks, a distribuição de energia elétrica monitorada e a densidade de processamento por metro quadrado, o projeto adota **Servidores Blade** montados em um chassis compartilhado e réguas de distribuição de energia inteligentes (**PDU** - Power Distribution Unit).",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta a principal vantagem dos servidores Blade em comparação a servidores tradicionais de montagem em rack (1U/2U):",
            "opt_a": "Compartilhamento centralizado de fontes de alimentação, refrigeração e switches no mesmo chassis, otimizando o espaço e o cabeamento.", "opt_b": "Eliminação da necessidade de energia elétrica na sala de servidores.", "opt_c": "Uso exclusivo de unidades de armazenamento em disquetes magnéticos de 3.5 polegadas.", "opt_d": "Incompatibilidade proposital com qualquer sistema de virtualização.",
            "feedback": "A resposta certa é Compartilhamento centralizado de fontes de alimentação, refrigeração e switches no mesmo chassis, otimizando o espaço e o cabeamento.\nComentário: Servidores Blade utilizam um chassis consolidado que fornece energia, ventilação e conectividade comuns para múltiplas lâminas de processamento.\nFonte: Infraestrutura de TI, UA 1."
        },
        {
            "ua": "01", "obj": 2, "grau": "MÉDIA", "kw": "Redundância de Alimentação Elétrica (Geradores e UPS Dupla Conversão Online)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Um Data Center corporativo de missão crítica não pode sofrer nenhuma micro-interrupção na alimentação elétrica, sob pena de reiniciar servidores e corromper bancos de dados ativamente em uso.\n\nPara proteger os equipamentos contra surtos, ruídos, variações de frequência e quedas da concessionária de energia, a infraestrutura utiliza um sistema de **No-break (UPS) do tipo Dupla Conversão Online** integrado a um grupo gerador a diesel de partida automática.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica a característica operacional de um no-break (UPS) Dupla Conversão Online:",
            "opt_a": "Os equipamentos de TI são alimentados continuamente pelo inversor do no-break sem tempo de transferência (0 milissegundos) em caso de falha da rede pública.", "opt_b": "O no-break liga o inversor apenas 5 minutos após a queda de energia da concessionária.", "opt_c": "O no-break converte a energia elétrica em sinal de rádio FM para transmissão sem fios.", "opt_d": "O equipamento opera sem o uso de baterias recarregáveis internas ou externas.",
            "feedback": "A resposta certa é Os equipamentos de TI são alimentados continuamente pelo inversor do no-break sem tempo de transferência (0 milissegundos) em caso de falha da rede pública.\nComentário: No-breaks Dupla Conversão Online convertem AC->DC->AC continuamente; na queda da concessionária, as baterias alimentam o inversor sem qualquer tempo de comutação (0 ms).\nFonte: Infraestrutura de TI, UA 1."
        },
        {
            "ua": "03", "obj": 1, "grau": "DIFÍCIL", "kw": "Níveis de Arranjo RAID de Discos (RAID 0, RAID 1, RAID 5 e RAID 10)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "O administrador de sistemas de um servidor de arquivos corporativo precisa configurar o controlador de disco físico (Controladora RAID HWD) para formar um volume lógico seguro e rápido utilizando 4 discos rígidos SAS de 2 TB cada.\n\nEle compara as características operacionais dos níveis de arranjo **RAID 0** (Striping), **RAID 1** (Mirroring), **RAID 5** (Paridade Distribuída) e **RAID 10** (Striping de Espelhos).",
            "afirmativas": "Com base nos níveis de arranjo RAID de discos, analise as afirmativas:\nI. O RAID 0 divide os dados entre os discos sem redundância, oferecendo alto desempenho mas sem tolerância a falhas (a perda de 1 disco destrói todo o volume).\nII. O RAID 5 utiliza paridade distribuída entre pelo menos 3 discos, suportando a falha de no máximo 1 disco do arranjo sem perda de dados.\nIII. O RAID 10 exige no mínimo 4 discos e combina o espelhamento (RAID 1) com o particionamento (RAID 0), oferecendo alta performance e alta redundância.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I, II e III.", "opt_b": "I e II, apenas.", "opt_c": "I e III, apenas.", "opt_d": "II e III, apenas.",
            "feedback": "A resposta certa é I, II e III.\nComentário: Todas as afirmativas são verdadeiras. Elas definem com exatidão a ausência de redundância do RAID 0, a paridade do RAID 5 e o arranjo híbrido do RAID 10.\nFonte: Infraestrutura de TI, UA 3."
        },
        {
            "ua": "03", "obj": 2, "grau": "DIFÍCIL", "kw": "Tecnologias de Discos de Armazenamento (NVMe, SSD SAS/SATA e HDD Enterprise)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Durante o planejamento de upgrade dos servidores de banco de dados transacionais de altíssimo volume de IOPS de uma instituição financeira, a equipe de infraestrutura substituiu os discos mecânicos rígidos legados (HDDs SAS 15k RPM) por unidades de estado sólido de tecnologia **NVMe** (Non-Volatile Memory Express).\n\nO NVMe utiliza o barramento de comunicação PCI Express (PCIe) direto com o processador da máquina em vez da interface tradicional SATA/AHCI.",
            "afirmativas": "Com base nas tecnologias de armazenamento SSD NVMe e HDDs, analise as afirmativas:\nI. Unidades SSD NVMe conectam-se diretamente às vias PCIe do processador, eliminando o gargalo de velocidade dos controladores SATA (limitados a 600 MB/s).\nII. O protocolo NVMe suporta mais de 64.000 filas de comandos paralelas com 64.000 comandos por fila, contra apenas 1 fila de 32 comandos do protocolo AHCI/SATA.\nIII. Discos rígidos mecânicos HDDs oferecem menor tempo de busca aleatória (Seek Time) do que SSDs de memória Flash NAND.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com exatidão o barramento PCIe e o paralelismo massivo de filas do protocolo NVMe. A afirmativa III é falsa pois SSDs não possuem partes mecânicas e têm tempo de busca quase nulo em comparação ao braço leitor dos HDDs.\nFonte: Infraestrutura de TI, UA 3."
        },
        {
            "ua": "03", "obj": 3, "grau": "DIFÍCIL", "kw": "Replicação de Armazenamento em Storage Arrays (LUN Masking e Zoning)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Em uma rede SAN (Storage Area Network) baseada em Fiber Channel conectando múltiplos servidores de virtualização a um Storage Array corporativo, o administrador precisa garantir que cada servidor acesse apenas o seu volume de disco lógico (**LUN** - Logical Unit Number) exclusivo.\n\nPara garantir o isolamento de segurança e impedir que um servidor sobrescreva acidentalmente os dados da LUN de outro servidor, a equipe configura os recursos de **Zoning** nos switches Fiber Channel e **LUN Masking** no Storage.",
            "afirmativas": "Com base nas técnicas de segurança em redes de armazenamento SAN, analise as afirmativas:\n\nI. O LUN Masking é uma configuração no Storage Array que restringe quais endereços de identificadores de porta (WWNN/WWPN) de adaptadores HBA podem visualizar e acessar uma determinada LUN.\n\nPORQUE\n\nII. O Zoning nos switches SAN limita o tráfego de fibra óptica isolando portas específicas em zonas lógicas virtuais, prevenindo acessos não autorizados entre servidores no barramento SAN.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. O LUN Masking atua no Storage Array (controle por WWPN/LUN) e o Zoning atua no switch SAN (controle por portas/WWPN); ambos compõem a segurança da SAN em camadas distintas.\nFonte: Infraestrutura de TI, UA 3."
        }
    ],
    subfolder='AD'
)

print("Batch TG 2 concluído.")
