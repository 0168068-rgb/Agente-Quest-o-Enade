# -*- coding: utf-8 -*-
"""
Batch 5: Disciplinas 15 a 18 (Versão ENADE Expandida - Caso Prático Robusto > 7 linhas)
"""
from generate_full_batch import create_exam

# 15. Redes de Alta Disponibilidade
create_exam(
    "Redes de Alta disponibilidade (4º Per redes)", "Redes de Alta Disponibilidade", "AI Redes de Alta Disponibilidade", "3; 6; 8; 10",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Agregação de Links com LACP (IEEE 802.3ad)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em uma arquitetura de Data Center de alta disponibilidade, a equipe de engenharia de redes precisa interligar dois switches de distribuição centrais através de múltiplos links de fibra óptica de 1 Gbps. O objetivo é evitar que a falha física de um único cabo ou porta interrompa o tráfego da rede, além de multiplicar a largura de banda agregada disponível entre os switches.\n\nPara evitar a criação de loops de camada 2 sem bloquear portas ativas e permitir a negociação dinâmica do canal lógico de comunicação (EtherChannel) entre equipamentos de múltiplos fabricantes de acordo com normas abertas da IEEE, os engenheiros precisam selecionar o protocolo de controle adequado.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o protocolo aberto padronizado pela IEEE responsável pela negociação dinâmica de agregação de links:",
            "opt_a": "LACP (Link Aggregation Control Protocol - IEEE 802.3ad).", "opt_b": "PAgP (Port Aggregation Protocol).", "opt_c": "STP (Spanning Tree Protocol).", "opt_d": "VRRP (Virtual Router Redundancy Protocol).",
            "feedback": "A resposta certa é LACP (Link Aggregation Control Protocol - IEEE 802.3ad).\nComentário: O LACP é o padrão aberto internacional IEEE para negociação dinâmica de EtherChannel, enquanto o PAgP é proprietário da Cisco.\nFonte: Redes de Alta Disponibilidade, UA 3."
        },
        {
            "ua": "06", "obj": 2, "grau": "MÉDIA", "kw": "Balanceamento de Carga com HAProxy e Algoritmo Round-Robin",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Uma plataforma de comércio eletrônico de grande acesso implanta um cluster web de alta disponibilidade composto por 4 servidores idênticos (nós de processamento) posicionados atrás de um balanceador de carga de camada 7 (HAProxy). Em horários normais de operação, o balanceador de carga recebe as requisições HTTP dos clientes e as distribui eficientemente entre os nós ativamente disponíveis.\n\nO arquiteto de infraestrutura necessita definir o algoritmo de balanceamento básico que distribua as novas conexões sequencialmente e de forma circular uniforme entre todos os servidores membros do pool, sem considerar o estado de carga pontual ou o histórico prévio de acessos de cada IP.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica o algoritmo de balanceamento de carga básico que distribui as requisições recebidas sequencialmente de forma circular entre os servidores ativos do pool:",
            "opt_a": "Round-Robin.", "opt_b": "Least Connections.", "opt_c": "Source IP Hash.", "opt_d": "Weighted Random.",
            "feedback": "A resposta certa é Round-Robin.\nComentário: O algoritmo Round-Robin distribui o tráfego em rodízio circular sequencial simples entre os nós membros do cluster.\nFonte: Redes de Alta Disponibilidade, UA 6."
        },
        {
            "ua": "08", "obj": 3, "grau": "DIFÍCIL", "kw": "Clusters Ativo/Passivo e Heartbeat/Corosync/Pacemaker",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Para garantir a continuidade dos serviços de banco de dados relacional PostgreSQL de uma instituição bancária, a equipe de TI implantou um cluster de alta disponibilidade no modelo Ativo/Passivo (Failover) utilizando os softwares de gerenciamento de cluster Corosync e Pacemaker sobre o sistema operacional Linux.\n\nDurante a simulação de desastre, a equipe avalia o mecanismo de comunicação de batimento cardíaco (Heartbeat) mantido entre os nós para detectar falhas de hardware, o controle de quórum do cluster e a atuação do mecanismo de isolamento físico STONITH (Shoot The Other Node In The Head) para impedir o cenário crítico de Split-Brain.",
            "afirmativas": "Com base nas tecnologias de gerenciamento de cluster e recursos de fencing, analise as afirmativas:\nI. O Corosync é responsável por manter a comunicação Heartbeat de estado e o quórum entre os nós do cluster.\nII. O mecanismo de STONITH (Shoot The Other Node In The Head) é utilizado para isolar/desligar forçadamente um nó com falha para evitar a corrupção de dados divididos (Split-Brain).\nIII. Em um cluster Ativo/Passivo, ambos os nós processam e gravam transações simultaneamente na mesma partição de disco sem controle de concorrência.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem corretamente o gerenciamento de quórum do Corosync e o fencing via STONITH para prevenir Split-Brain. A afirmativa III é falsa pois no modelo Ativo/Passivo apenas o nó ativo processa dados.\nFonte: Redes de Alta Disponibilidade, UA 8."
        },
        {
            "ua": "10", "obj": 1, "grau": "DIFÍCIL", "kw": "Replicação de Dados Síncrona vs Assíncrona e DRBD",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Um administrador de sistemas projeta a solução de alta disponibilidade e recuperação de desastres para o armazenamento de blocos de um cluster Linux sem dependência de um storage SAN proprietário centralizado. Ele utiliza o módulo de kernel DRBD (Distributed Replicated Block Device) para espelhar partições de disco via rede entre dois nós de servidores.\n\nAo definir a política de replicação, o administrador analisa as características operacionais do Protocolo A (Assíncrono) e do Protocolo C (Síncrono), avaliando o impacto da latência da rede no tempo de confirmação das operações de escrita em disco pela aplicação principal.",
            "afirmativas": "Com base nos modos de replicação de dados no DRBD (Protocolos A, B e C), analise as afirmativas:\nI. A replicação síncrona (Protocolo C) confirma a escrita no nó local somente após receber a confirmação de que os dados foram gravados no disco do nó remoto.\nII. A replicação assíncrona (Protocolo A) confirma a escrita assim que os dados entram no buffer de envio da rede local, priorizando o desempenho em links WAN de maior latência.\nIII. A replicação síncrona zera o tempo de latência de escrita no disco principal independentemente da distância física do nó secundário.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II diferenciam com precisão a replicação síncrona (Protocolo C) e assíncrona (Protocolo A). A afirmativa III é falsa pois a replicação síncrona adiciona a latência da rede à gravação.\nFonte: Redes de Alta Disponibilidade, UA 10."
        },
        {
            "ua": "10", "obj": 2, "grau": "DIFÍCIL", "kw": "Teorema CAP em Sistemas Distribuídos e Alta Disponibilidade",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "No projeto de arquitetura de um banco de dados distribuído geograficamente para suporte a uma aplicação financeira global, os arquitetos de software analisam as garantias teóricas formuladas por Eric Brewer no Teorema CAP (Consistência, Disponibilidade e Tolerância a Particionamento).\n\nDurante o planejamento da resiliência contra falhas de comunicação entre Data Centers regionais, a equipe avalia os trade-offs inevitáveis impostos pelo teorema quando ocorre um rombo físico de fibra óptica que isola temporariamente réplicas do banco de dados localizadas em continentes distintos.",
            "afirmativas": "Com base no Teorema CAP formulado por Eric Brewer, analise as afirmativas:\n\nI. De acordo com o Teorema CAP, em um sistema distribuído sujeito a partições de rede (Partition Tolerance - P), é impossível garantir simultaneamente a Consistência Forte (C) e a Disponibilidade Total (A) em todas as réplicas.\n\nPORQUE\n\nII. Na ocorrência de um corte de fibra óptica que isole nós da rede, o sistema deve obrigatoriamente optar entre recusar requisições para preservar dados consistentes (Sistemas CP) ou aceitar requisições podendo entregar dados desatualizados (Sistemas AP).",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A premissa central do Teorema CAP é que o particionamento obriga o trade-off direto entre Consistência e Disponibilidade.\nFonte: Redes de Alta Disponibilidade, UA 10."
        }
    ]
)

# 16. Redes de Computadores
create_exam(
    "Redes de Computadores(seg)", "Redes de Computadores", "AI Redes de Computadores", "3; 4; 8; 12",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Endereçamento IPv4 e Sub-redes CIDR",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Um analista de suporte e infraestrutura de TI foi incumbido de reestruturar a topologia de endereçamento IPv4 da rede local de uma empresa corporativa. Ele recebeu a faixa de endereços privada de classe C 192.168.10.0/24 e precisa dividi-la em sub-redes menores para isolar 4 departamentos em VLANs distintas.\n\nPara atender à demanda de alocação de hosts por departamento com eficiência de endereços, o analista adotou a máscara de sub-rede /26 (255.255.255.192), precisando determinar a quantidade exata de endereços IP válidos e atribuíveis a computadores clientes fornecidos em cada sub-rede gerada.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica a quantidade de endereços IP utilizáveis para computadores clientes fornecida por uma máscara /26 (255.255.255.192) em cada sub-rede:",
            "opt_a": "62 endereços.", "opt_b": "64 endereços.", "opt_c": "126 endereços.", "opt_d": "30 endereços.",
            "feedback": "A resposta certa é 62 endereços.\nComentário: Uma máscara /26 possui 6 bits de host (2^6 = 64 endereços totais). Descontando o endereço de Rede e o de Broadcast, restam 62 IPs válidos para hosts.\nFonte: Redes de Computadores, UA 3."
        },
        {
            "ua": "04", "obj": 2, "grau": "MÉDIA", "kw": "Protocolo TCP vs UDP na Camada de Transporte",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Na arquitetura do modelo de referência TCP/IP, a camada de transporte é responsável por prover a comunicação lógica fim a fim entre processos de aplicação rodando em hosts distintos. Os dois principais protocolos atuantes nessa camada, TCP (Transmission Control Protocol) e UDP (User Datagram Protocol), fornecem modelos de serviço fundamentalmente distintos para atender a diferentes requisitos de mercado.\n\nUm desenvolvedor de um sistema de transmissão de áudio e vídeo ao vivo (Streaming) necessita escolher o protocolo de transporte que priorize o envio contínuo com a menor latência possível, abrindo mão do estabelecimento de conexões formais e das retransmissões de pacotes perdidos.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o protocolo focado em baixa latência e sem orientação a conexão que não realiza Three-Way Handshake nem confirmação de recebimento (ACK):",
            "opt_a": "UDP (User Datagram Protocol).", "opt_b": "TCP (Transmission Control Protocol).", "opt_c": "BGP (Border Gateway Protocol).", "opt_d": "SCTP (Stream Control Transmission Protocol).",
            "feedback": "A resposta certa é UDP (User Datagram Protocol).\nComentário: O UDP é um protocolo não orientado a conexão, sem overhead de estabelecimento de sessão ou controle de fluxo, ideal para aplicações em tempo real.\nFonte: Redes de Computadores, UA 4."
        },
        {
            "ua": "08", "obj": 3, "grau": "DIFÍCIL", "kw": "Resolução de Nomes com Sistema DNS (Domain Name System)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Ao digitar um endereço web como 'www.exemplo.com.br' na barra de navegação de um cliente na rede local, o sistema operacional inicia um processo de resolução de nomes através da hierarquia global do serviço DNS (Domain Name System) para traduzir a URL textual em um endereço IP numérico de 32 bits ou 128 bits.\n\nDurante o acompanhamento do tráfego através de um analisador de pacotes (Wireshark), o analista de redes inspeciona a sequência de consultas recursivas e iterativas trocadas entre o servidor DNS local, os Servidores Raiz (Root Servers), os servidores TLD (.br) e os servidores autoritativos, analisando os tipos de registros de recursos (A, AAAA, MX, CNAME).",
            "afirmativas": "Com base no funcionamento do serviço DNS e seus registros de recursos, analise as afirmativas:\nI. O servidor DNS Raiz (Root Server) direciona a consulta do cliente para os servidores TLD (Top-Level Domain) responsáveis pelo domínio '.br'.\nII. O registro DNS do tipo 'AAAA' mapeia um nome de domínio para um endereço IPv6 de 128 bits.\nIII. O protocolo DNS utiliza exclusivamente a porta TCP 80 para responder a consultas comuns de resolução de nomes.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II descrevem corretamente a hierarquia DNS e o registro AAAA. A afirmativa III é falsa pois consultas DNS operam sobre UDP porta 53.\nFonte: Redes de Computadores, UA 8."
        },
        {
            "ua": "12", "obj": 1, "grau": "DIFÍCIL", "kw": "Endereçamento e Transição para IPv6",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Diante do esgotamento global do pool de endereços IPv4 públicos gerenciado pela IANA e pelo LACNIC, uma organização de tecnologia iniciou a transição da sua infraestrutura corporativa para o protocolo IPv6. O novo protocolo adota um espaço de endereçamento expandido de 128 bits expresso formalmente em notação hexadecimal.\n\nDurante o planejamento da arquitetura IPv6, os engenheiros analisam as inovações introduzidas na nova versão do protocolo, como o suporte nativo à autoconfiguração de endereços stateless (SLAAC), o suporte expandido à segurança com IPsec e as mudanças estruturais nas transmissões em grupo de rede.",
            "afirmativas": "Com base na arquitetura de endereçamento do protocolo IPv6, analise as afirmativas:\nI. Endereços IPv6 são compostos por 8 grupos de 4 dígitos hexadecimais separados por dois-pontos (ex: 2001:db8::1).\nII. O IPv6 aboliu o uso de pacotes de Broadcast tradicional, substituindo-o por transmissões Multicast eficientes.\nIII. O mecanismo de autoconfiguração de endereço stateless (SLAAC) exige obrigatoriamente a presença de um servidor DHCPv6 em todas as redes.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II apresentam com precisão o formato IPv6 e o fim do broadcast. A afirmativa III é falsa pois o SLAAC permite que o host gere seu próprio IP via mensagens Router Advertisement sem DHCP.\nFonte: Redes de Computadores, UA 12."
        },
        {
            "ua": "12", "obj": 2, "grau": "DIFÍCIL", "kw": "Protocolo ICMP e Utilitários de Diagnóstico (Ping e Traceroute)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Um analista de suporte técnico utiliza os utilitários de linha de comando 'ping' e 'traceroute' ('tracert') para diagnosticar problemas de perda de conectividade e identificar em qual roteador intermediário da internet os pacotes destinados a um servidor remoto estão sendo descartados.\n\nO funcionamento do utilitário 'traceroute' baseia-se no envio de uma sequência de pacotes de sonda com valores incrementais no campo Time-To-Live (TTL) do cabeçalho IP, explorando as mensagens de erro de controle retornadas pelo protocolo ICMP (Internet Control Message Protocol).",
            "afirmativas": "Com base nas mensagens de controle do protocolo ICMP (Internet Control Message Protocol), analise as afirmativas:\n\nI. O utilitário 'traceroute' descobre o caminho percorrido enviando pacotes com valores de TTL (Time-To-Live) crescentes (TTL=1, TTL=2, ...), forçando cada roteador intermediário a descartar o pacote e retornar uma mensagem ICMP 'Time Exceeded'.\n\nPORQUE\n\nII. Quando o campo TTL do cabeçalho IP atinge o valor zero em um roteador, o protocolo IP especifica que o pacote deve ser destruído e um aviso de erro ICMP Tipo 11 deve ser transmitido de volta à fonte.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A manipulação controlada do campo TTL do IP explorando a resposta ICMP Time Exceeded é a mecânica exata do traceroute.\nFonte: Redes de Computadores, UA 12."
        }
    ]
)

# 17. Redes de Longa Distância
create_exam(
    "Redes de Longa Distância", "Redes de Longa Distância", "AI Redes de Longa Distância", "2; 4; 6; 9",
    [
        {
            "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Arquitetura MPLS (Multiprotocol Label Switching)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Uma operadora de telecomunicações utiliza o protocolo MPLS (Multiprotocol Label Switching) no núcleo da sua rede WAN para acelerar o encaminhamento de pacotes de dados e oferecer serviços de VPN de camada 2 e camada 3 para seus clientes corporativos.\n\nAo ingressar no domínio MPLS, os pacotes IP convencionais recebem um rótulo (label) de 32 bits inserido entre os cabeçalhos de camada 2 e camada 3. A equipe técnica precisa identificar qual elemento da topologia de rede é responsável por inspecionar o pacote IP original e realizar a operação de inserção do rótulo inicial (Label Push).",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica o elemento do roteador MPLS responsável por inserir o rótulo (Label Push) na entrada do domínio MPLS:",
            "opt_a": "LER (Label Edge Router - Ingress).", "opt_b": "LSR (Label Switching Router - Core).", "opt_c": "CE (Customer Edge).", "opt_d": "DSLAM (Digital Subscriber Line Access Multiplexer).",
            "feedback": "A resposta certa é LER (Label Edge Router - Ingress).\nComentário: O LER de entrada (Ingress LER) insere o rótulo MPLS no pacote IP ao entrar no domínio de comutação por rótulos.\nFonte: Redes de Longa Distância, UA 2."
        },
        {
            "ua": "04", "obj": 2, "grau": "MÉDIA", "kw": "Tecnologia SD-WAN (Software-Defined WAN)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Uma empresa corporativa multinacional decidiu modernizar a infraestrutura de rede de suas 50 filiais remotas substituindo os caros links dedicados MPLS legados por uma solução de Redes de Longa Distância Definidas por Software (SD-WAN).\n\nA nova arquitetura combina dinamicamente múltiplos links comerciais de internet (Banda Larga, 5G, Satélite LEO) em cada filial, utilizando tunelamento seguro de dados e um controlador centralizado baseado em software para gerenciar o tráfego corporativo.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta a principal vantagem da arquitetura SD-WAN em relação às redes WAN tradicionais baseadas em roteamento estático:",
            "opt_a": "Seleção dinâmica do caminho de dados em tempo real com base no desempenho do link (latência, perda de pacotes) e controle centralizado por software.", "opt_b": "Fim da necessidade de criptografia em túneis VPN sobre a internet pública.", "opt_c": "Eliminação do uso de roteadores nas filiais remotas.", "opt_d": "Limitação do tráfego a uma única rota física sem redundância.",
            "feedback": "A resposta certa é Seleção dinâmica do caminho de dados em tempo real com base no desempenho do link (latência, perda de pacotes) e controle centralizado por software.\nComentário: SD-WAN separa o plano de controle do plano de dados, roteando tráfego dinamicamente pelo melhor caminho disponível segundo SLA.\nFonte: Redes de Longa Distância, UA 4."
        },
        {
            "ua": "06", "obj": 3, "grau": "DIFÍCIL", "kw": "Tecnologias Ópticas DWDM e SDH/SONET",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Para multiplicar expressivamente a capacidade de transmissão de dados de um backbone óptico subfluvial de 1.000 km sem a necessidade de lançar novos cabos de fibra óptica, uma concessionária de telecomunicações implantou equipamentos de Multiplexação por Divisão de Comprimento de Onda Densa (DWDM).\n\nA equipe de engenharia analisa os aspectos técnicos da tecnologia DWDM, incluindo a transmissão simultânea de múltiplas frequências de luz laser em fibra monomodo e a utilização de amplificadores ópticos EDFA (Erbium-Doped Fiber Amplifier) ao longo do trajeto.",
            "afirmativas": "Com base na multiplexação por divisão de comprimento de onda (DWDM), analise as afirmativas:\nI. O DWDM transmite múltiplos comprimentos de onda (cores de luz laser) simultaneamente pela mesma fibra óptica monomodo.\nII. O uso de amplificadores ópticos EDFA (Erbium-Doped Fiber Amplifier) permite amplificar o sinal óptico diretamente sem conversão eletro-óptica intermediária.\nIII. A tecnologia DWDM restringe a velocidade total da fibra ao limite de 100 Mbps por cabo.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com precisão a multiplexação DWDM e a amplificação óptica EDFA. A afirmativa III é falsa pois o DWDM atinge terabits por segundo (Tbps) por par de fibra.\nFonte: Redes de Longa Distância, UA 6."
        },
        {
            "ua": "09", "obj": 1, "grau": "DIFÍCIL", "kw": "Conexões de Satélite GEO/LEO e Redes Móveis 4G/5G",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Uma empresa de mineração opera jazidas em regiões geograficamente isoladas onde não há disponibilidade de infraestrutura terrestre de cabeamento ou fibra óptica. Para interligar os sistemas de automação e telemetria dessas instalações à matriz, a empresa utiliza soluções de conectividade via constelações de satélites de órbita baixa (LEO) e redes privadas 5G.\n\nOs engenheiros de telecomunicações comparam as características operacionais da comunicação por satélites LEO em relação aos satélites geoestacionários (GEO) tradicionais, avaliando latência, velocidade de propagação e a dinâmica de rastreamento de órbita.",
            "afirmativas": "Com base nas características de comunicação WAN via satélites LEO e GEO, analise as afirmativas:\nI. Satélites em órbita baixa (LEO, ex: Starlink) oferecem latência consideravelmente menor (20-40ms) em relação a satélites geoestacionários (GEO, ~600ms).\nII. Constelações LEO exigem o rastreamento dinâmico e handover contínuo entre satélites devido ao seu rápido movimento em relação à superfície da Terra.\nIII. Satélites GEO orbitam a uma altitude de aproximadamente 500 km da superfície terrestre.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II destacam a vantagem de baixa latência e a necessidade de handover dos satélites LEO. A afirmativa III é falsa pois satélites geoestacionários (GEO) orbitam a ~35.786 km de altitude.\nFonte: Redes de Longa Distância, UA 9."
        },
        {
            "ua": "09", "obj": 2, "grau": "DIFÍCIL", "kw": "VPNs IPsec (IKEv2, ESP) sobre a Internet",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Para conectar com segurança a matriz e 30 filiais remotas através da internet pública, o engenheiro de segurança projetou túneis VPN baseados na suíte de protocolos IPsec configurados em modo Túnel.\n\nO projeto especifica o uso do protocolo ESP (Encapsulating Security Payload) integrado à negociação de chaves via IKEv2 para garantir confidencialidade, integridade dos dados e autenticação de origem de todo o tráfego corporativo que transita na internet pública.",
            "afirmativas": "Com base nos protocolos do suite IPsec (AH, ESP e IKEv2), analise as afirmativas:\n\nI. O protocolo ESP (Encapsulating Security Payload) em modo Túnel fornece confidencialidade (criptografia), integridade de dados e autenticação da origem para todo o pacote IP original encapsulado.\n\nPORQUE\n\nII. Diferente do modo Transporte que criptografa apenas a carga útil (payload), o modo Túnel do ESP insere um novo cabeçalho IP externo, ocultando os endereços IP reais de origem e destino da rede interna.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. O modo Túnel do ESP encapsula o pacote IP inteiro em um novo pacote IP público, oferecendo sigilo dos IPs internos.\nFonte: Redes de Longa Distância, UA 9."
        }
    ]
)

# 18. Redes Sem Fio
create_exam(
    "Redes sem Fio (4º Per Redes)", "Redes Sem Fio", "AI Redes Sem Fio", "2; 6; 9; 11",
    [
        {
            "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Padrões Wi-Fi (IEEE 802.11a/b/g/n/ac/ax - Wi-Fi 6)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Durante a fase de planejamento de um projeto de modernização da rede sem fio de um centro de convenções corporativo com capacidade para mil participantes simultâneos, a equipe de engenharia de rede selecionou Access Points compatíveis com o padrão Wi-Fi 6 (IEEE 802.11ax).\n\nPara suportar a altíssima densidade de conexões mantendo elevadas taxas de transferência de dados e menor latência, o Wi-Fi 6 introduziu uma técnica avançada de modulação multiusuário herdada das redes móveis de telefonia celular.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica a tecnologia de modulação que permite ao Wi-Fi 6 subdividir um canal de radiofrequência em subportadoras menores (RU - Resource Units) para atender múltiplos clientes simultaneamente:",
            "opt_a": "OFDMA (Orthogonal Frequency-Division Multiple Access).", "opt_b": "CSMA/CD (Carrier Sense Multiple Access with Collision Detection).", "opt_c": "FHSS (Frequency-Hopping Spread Spectrum).", "opt_d": "DSSS (Direct-Sequence Spread Spectrum).",
            "feedback": "A resposta certa é OFDMA (Orthogonal Frequency-Division Multiple Access).\nComentário: O OFDMA é uma das principais inovações do Wi-Fi 6 (802.11ax), dividindo canais em subportadoras alocadas simultaneamente para múltiplos clientes.\nFonte: Redes Sem Fio, UA 2."
        },
        {
            "ua": "06", "obj": 2, "grau": "MÉDIA", "kw": "Mecanismo de Acesso ao Meio CSMA/CA e RTS/CTS",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Em redes locais sem fio padronizadas pelo IEEE 802.11, os dispositivos compartilham um meio físico de comunicação não guiado (o ar) e são incapazes de escutar e transmitir na mesma frequência simultaneamente, inviabilizando a detecção de colisões tradicional de redes cabeadas (CSMA/CD).\n\nPara solucionar essa restrição e mitigar o problema do nó escondido em cenários onde clientes sem fio estão fora do alcance de escuta mútuo mas conectados ao mesmo Access Point, o protocolo utiliza a reserva prévia do canal de rádio através da troca de mensagens curtas de controle.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta o protocolo utilizado em redes Wi-Fi para evitar o problema do nó escondido através da reserva explícita do canal de rádio:",
            "opt_a": "Mecanismo RTS/CTS (Request to Send / Clear to Send).", "opt_b": "Mecanismo CSMA/CD (Collision Detection).", "opt_c": "Token Ring Passing.", "opt_d": "ALOHA puro.",
            "feedback": "A resposta certa é Mecanismo RTS/CTS (Request to Send / Clear to Send).\nComentário: As mensagens RTS/CTS reservam o meio sem fio antes da transmissão de dados, prevenindo colisões causadas por nós fora do alcance mútuo.\nFonte: Redes Sem Fio, UA 6."
        },
        {
            "ua": "09", "obj": 3, "grau": "DIFÍCIL", "kw": "Segurança Wi-Fi (WPA2, WPA3, 802.1X/EAP)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Uma instituição de ensino superior reestruturou a segurança das suas redes sem fio corporativas para impedir acessos não autorizados e proteger as comunicações de dados de alunos e professores.\n\nA equipe de TI implementou o padrão WPA3 Enterprise com autenticação individualizada baseada na norma IEEE 802.1X integrada a um servidor RADIUS central, utilizando o protocolo SAE (Simultaneous Authentication of Equals) para mitigar ataques de dicionário e captura de handshake.",
            "afirmativas": "Com base nos padrões de segurança Wi-Fi WPA2/WPA3 Enterprise e 802.1X, analise as afirmativas:\nI. O WPA3 substitui a negociação PSK pelo protocolo SAE (Simultaneous Authentication of Equals), oferecendo proteção contra ataques de dicionário offline.\nII. O modo WPA Enterprise (802.1X) exige um servidor de autenticação RADIUS e credenciais individuais (como usuário/senha ou certificados EAP-TLS).\nIII. A criptografia WEP de 64 bits permanece recomendada pelas normas atuais por ser imune a ataques de quebra de chave.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II descrevem com precisão o avanço do WPA3 (SAE) e o funcionamento do 802.1X. A afirmativa III é falsa pois o WEP é obsoleto e vulnerável a quebra em minutos.\nFonte: Redes Sem Fio, UA 9."
        },
        {
            "ua": "11", "obj": 1, "grau": "DIFÍCIL", "kw": "Redes IoT Sem Fio de Longo Alcance (LoRaWAN, Zigbee, NB-IoT)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Um projeto de cidade inteligente (Smart City) prevê a instalação de 10.000 sensores alimentados por bateria para monitoramento de vaga de estacionamento, medição de água e controle de iluminação pública espalhados por todo o município.\n\nOs dispositivos precisam transmitir pequenas mensagens de dados a distâncias de até 15 km com consumo energético tão reduzido que permita a duração das baterias por mais de 5 anos sem manutenção física. Os engenheiros analisam as tecnologias da família LPWAN (Low-Power Wide-Area Network), como LoRaWAN e NB-IoT.",
            "afirmativas": "Com base nas tecnologias de redes LPWAN (Low-Power Wide-Area Network), analise as afirmativas:\nI. A tecnologia LoRaWAN utiliza frequências sub-GHz isentas de licença (como 915 MHz no Brasil) fornecendo longo alcance (até 15 km) com baixíssimo consumo de energia.\nII. O protocolo Zigbee (IEEE 802.15.4) é uma tecnologia WPAN voltada para redes de malha (Mesh) de curto alcance em ambientes internos.\nIII. Redes LoRaWAN foram projetadas para transmissão de streaming de vídeo 4K em tempo real.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem corretamente LoRaWAN e Zigbee. A afirmativa III é falsa pois LPWANs possuem baixíssima taxa de transmissão (kbps), inadequadas para vídeos.\nFonte: Redes Sem Fio, UA 11."
        },
        {
            "ua": "11", "obj": 2, "grau": "DIFÍCIL", "kw": "Atenuação de Sinal, Zonas de Fresnel e Orçamento de Link (Link Budget)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "No projeto de um enlace de rádio ponto-a-ponto de alta velocidade em 5.8 GHz cobrindo uma distância de 5 km entre a matriz de uma empresa e seu centro de distribuição, o engenheiro de telecomunicações realiza o cálculo do orçamento do enlace (Link Budget) e o estudo topográfico da visada direta.\n\nPara garantir a estabilidade do enlace e evitar a perda de sinal por atenuação de fase decorrente de reflexões e difração, o engenheiro exige a desobstrução de uma zona elipsoidal no espaço livre entre as antenas.",
            "afirmativas": "Com base nos conceitos de propagação de rádio e Zonas de Fresnel, analise as afirmativas:\n\nI. A Primeira Zona de Fresnel deve ser mantida desobstruída em pelo menos 60% do seu raio ao longo de todo o enlace de rádio de ponto-a-ponto.\n\nPORQUE\n\nII. Obstruções físicas (como árvores ou construções) dentro da Zona de Fresnel causam difração e desfasamento das ondas de rádio refletidas, provocando atenuação por cancelamento de fase (fading) no receptor.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A zona de Fresnel limpa garante que ondas refletidas não cancelem o sinal direto por interferência destrutiva.\nFonte: Redes Sem Fio, UA 11."
        }
    ]
)

print("Batch 5 atualizado com contextualização ENADE expandida.")
