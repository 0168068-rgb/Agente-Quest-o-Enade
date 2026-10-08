# -*- coding: utf-8 -*-
"""
Batch TG 5: Disciplinas 15 a 18 (Provas TG 2026-4 - UAs Específicas do Tema Gerador e Contextualização ENADE > 7 linhas)
"""
from generate_full_batch import create_exam

# 15. Redes de Alta Disponibilidade (UAs 3, 6)
create_exam(
    "Redes de Alta disponibilidade (4º Per redes)", "Redes de Alta Disponibilidade", "AD Redes de Alta Disponibilidade", "3; 6",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Protocolos de Agregação de Links (EtherChannel: LACP vs PAgP)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em um projeto de rede local de alta disponibilidade para um centro financeiro, o engenheiro de redes precisa interligar um switch de distribuição a um switch de núcleo utilizando quatro cabos de par trançado agregados em um único canal lógico (EtherChannel).\n\nEle compara o protocolo padrão aberto internacional da IEEE (LACP - 802.3ad) com o protocolo proprietário desenvolvido pela Cisco (PAgP - Port Aggregation Protocol).",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica os dois modos de negociação suportados pelo protocolo PAgP proprietário da Cisco:",
            "opt_a": "Auto e Desirable.", "opt_b": "Active e Passive.", "opt_c": "On e Off.", "opt_d": "Trunk e Access.",
            "feedback": "A resposta certa é Auto e Desirable.\nComentário: O protocolo PAgP (Cisco) utiliza os modos Auto e Desirable, enquanto o LACP (IEEE) utiliza os modos Passive e Active.\nFonte: Redes de Alta Disponibilidade, UA 3."
        },
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Balanceamento de Carga de Tráfego em EtherChannel (Hash Algorithm)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Durante o monitoramento de um canal EtherChannel de 4 Gbps (formado por 4 portas de 1 Gbps), o administrador de redes observa que 90% de todo o tráfego do canal está passando por apenas uma das portas físicas, deixando as outras três ociosas.\n\nEle descobre que a causa da distribuição desigual de tráfego é a configuração inadequada do algoritmo de Hash de Balanceamento de Carga do EtherChannel (Load-Balance Hash Algorithm).",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta o funcionamento da distribuição de tráfego em um canal EtherChannel:",
            "opt_a": "O switch aplica uma função hash sobre os endereços de origem e/ou destino (MAC ou IP) para determinar por qual porta física do canal cada fluxo de dados trafega.", "opt_b": "O switch alterna a transmissão pacote por pacote sequencialmente entre as 4 portas de forma circular.", "opt_c": "Todo o tráfego de broadcast é obrigatoriamente transmitido pelas 4 portas simultaneamente sem controle.", "opt_d": "O EtherChannel exige que o tráfego seja limitado a no máximo 10 Mbps por porta física.",
            "feedback": "A resposta certa é O switch aplica uma função hash sobre os endereços de origem e/ou destino (MAC ou IP) para determinar por qual porta física do canal cada fluxo de dados trafega.\nComentário: O EtherChannel distribui o tráfego por fluxos (baseado em hash de MAC/IP/Porta), garantindo que os pacotes de uma mesma sessão mantenham a ordem de entrega.\nFonte: Redes de Alta Disponibilidade, UA 3."
        },
        {
            "ua": "06", "obj": 1, "grau": "DIFÍCIL", "kw": "Checagem de Saúde de Servidores (Health Checks HTTP/TCP) no HAProxy",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um cluster de balanceamento de carga HAProxy gerencia o tráfego de acesso para um pool de 5 servidores web de aplicação backend.\n\nPara evitar que requisições de clientes reais sejam enviadas para um servidor do pool que travou ou está respondendo com erro interno de servidor (`HTTP 500`), o HAProxy executa sondagens periódicas de **Checagem de Saúde** (Health Checks).",
            "afirmativas": "Com base nas checagens de saúde (Health Checks) no HAProxy, analise as afirmativas:\nI. O HAProxy pode realizar checagens de saúde de camada 4 (verificação de abertura de porta TCP) ou de camada 7 (requisição `GET /health` esperando retorno `HTTP 200`).\nII. Quando um servidor do pool falha consecutivamente nas checagens de saúde, o HAProxy o marca como 'DOWN' e remove temporariamente a distribuição de tráfego para ele.\nIII. Servidores marcados como 'DOWN' precisam ser reiniciados manualmente pelo administrador para voltar ao pool do HAProxy.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão os tipos de Health Check e a remoção automática do servidor com falha. A afirmativa III é falsa pois o HAProxy re-insere o servidor no pool automaticamente assim que ele volta a passar nas checagens de saúde.\nFonte: Redes de Alta Disponibilidade, UA 6."
        },
        {
            "ua": "06", "obj": 2, "grau": "DIFÍCIL", "kw": "Terminação SSL/TLS (Offloading) em Balanceadores de Carga",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Em um portal de e-commerce com dezenas de milhares de acessos HTTPS simultâneos, o processamento de criptografia e decodificação do aperto de mão TLS consome mais de 60% do processamento de CPU dos servidores web de aplicação backend.\n\nPara desonerar os servidores de aplicação, o arquiteto configura o recurso de **Terminação SSL/TLS** (SSL Offloading) no balanceador de carga de borda (HAProxy / Nginx).",
            "afirmativas": "Com base na Terminação SSL/TLS (SSL Offloading), analise as afirmativas:\nI. O balanceador de carga decodifica o tráfego HTTPS criptografado do cliente e repassa o tráfego HTTP em texto claro pela rede interna para os servidores backend.\nII. A terminação SSL desonera o uso de CPU dos servidores de aplicação, centralizando a gestão dos certificados digitais X.509 no balanceador de carga.\nIII. A terminação SSL exige que os servidores de aplicação backend possuam certificados digitais registrados na internet pública.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com exatidão o desoneração de CPU e a centralização de certificados no SSL Offloading. A afirmativa III é falsa pois o tráfego interno backend flui em HTTP/rede privada, sem necessidade de certificados públicos nos servidores internos.\nFonte: Redes de Alta Disponibilidade, UA 6."
        },
        {
            "ua": "06", "obj": 3, "grau": "DIFÍCIL", "kw": "Arquiteturas de Balanceadores de Carga em Camada 4 (TCP/UDP) vs Camada 7 (HTTP)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Durante o planejamento de arquitetura de alta disponibilidade de uma infraestrutura em nuvem, o engenheiro de sistemas precisa escolher entre implementar um balanceador de carga de **Camada 4** (L4 - Transporte) ou um balanceador de carga de **Camada 7** (L7 - Aplicação).\n\nEle avalia o desempenho de taxa de pacotes por segundo (PPS) e a capacidade de roteamento baseado no conteúdo dos cabeçalhos das requisições.",
            "afirmativas": "Com base no balanceamento de carga em Camada 4 vs Camada 7, analise as afirmativas:\n\nI. Balanceadores de carga de Camada 7 (L7) conseguem tomar decisões de roteamento avançadas com base na URL da requisição, nos cabeçalhos HTTP, cookies e parâmetros do payload JSON.\n\nPORQUE\n\nII. Balanceadores de Camada 7 inspecionam a carga útil do protocolo de aplicação, enquanto balanceadores de Camada 4 (L4) encaminham pacotes em nível de transporte (IP/Porta) com maior velocidade e menor consumo de CPU por não lerem o conteúdo da aplicação.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A inspeção do payload na L7 fornece roteamento inteligente baseado em conteúdo, enquanto a L4 atua com foco em velocidade bruta no nível de transporte.\nFonte: Redes de Alta Disponibilidade, UA 6."
        }
    ],
    subfolder='AD'
)

# 16. Redes de Computadores (UAs 3, 4)
create_exam(
    "Redes de Computadores(seg)", "Redes de Computadores", "AD Redes de Computadores", "3; 4",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Campos do Cabeçalho IPv4 (TTL, Protocol, Checksum, IP Origem/Destino)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Na camada de rede do modelo TCP/IP, cada pacote de dados é encapsulado em um datagrama IPv4 contendo um cabeçalho padronizado de 20 bytes com diversos campos de controle de transmissão.\n\nUm analista de rede inspeciona um pacote capturado no Wireshark e analisa o campo **Protocol** (Protocolo de Camada Superior) e o campo **TTL** (Time-To-Live).",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica o número de protocolo armazenado no campo Protocol do cabeçalho IPv4 para identificar que o pacote transporta um segmento TCP:",
            "opt_a": "6 (TCP).", "opt_b": "17 (UDP).", "opt_c": "1 (ICMP).", "opt_d": "89 (OSPF).",
            "feedback": "A resposta certa é 6 (TCP).\nComentário: O campo Protocol no IPv4 utiliza números padronizados pela IANA: 6 para TCP, 17 para UDP e 1 para ICMP.\nFonte: Redes de Computadores, UA 3."
        },
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Endereçamento IP de Classe Pública vs Privada (RFC 1918)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Para conter o esgotamento dos endereços IPv4 globais, a IETF padronizou a especificação **RFC 1918**, reservando faixas específicas de endereços IP para uso exclusivo em redes privadas internas (LANs).\n\nEndereços IP privados são não-roteáveis na internet pública e exigem tradução por NAT para acessar servidores externos.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta uma faixa de endereços IPv4 privada reservada pela RFC 1918:",
            "opt_a": "192.168.0.0 até 192.168.255.255 (/16).", "opt_b": "200.100.0.0 até 200.100.255.255.", "opt_c": "8.8.8.0 até 8.8.8.255.", "opt_d": "1.1.1.0 até 1.1.1.255.",
            "feedback": "A resposta certa é 192.168.0.0 até 192.168.255.255 (/16).\nComentário: A RFC 1918 reserva 10.0.0.0/8, 172.16.0.0/12 e 192.168.0.0/16 para redes privadas.\nFonte: Redes de Computadores, UA 3."
        },
        {
            "ua": "04", "obj": 1, "grau": "DIFÍCIL", "kw": "O Apertar de Mão de Três Vias (Three-Way Handshake TCP: SYN, SYN-ACK, ACK)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Antes que um cliente web consiga solicitar uma página HTML a um servidor via protocolo TCP, o protocolo estabelece uma conexão orientada e confiável de transporte fim a fim.\n\nO estabelecimento de sessão ocorre através do aperto de mão de três vias (**Three-Way Handshake**), trocando sinalizadores (flags) de sincronização de números de sequência (ISN).",
            "afirmativas": "Com base nas etapas do Three-Way Handshake TCP, analise as afirmativas:\nI. O cliente inicia o aperto de mão enviando um segmento com a flag `SYN=1` e um número de sequência inicial aleatório.\nII. O servidor responde com um segmento contendo as flags `SYN=1` e `ACK=1`, confirmando o recebimento e enviando seu próprio número de sequência.\nIII. O cliente finaliza o aperto de mão enviando um segmento com a flag `ACK=1`, estabelecendo o estado `ESTABLISHED` na conexão.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I, II e III.", "opt_b": "I e II, apenas.", "opt_c": "I e III, apenas.", "opt_d": "II e III, apenas.",
            "feedback": "A resposta certa é I, II e III.\nComentário: Todas as afirmativas são verdadeiras. Elas detalham perfeitamente a sequência SYN -> SYN-ACK -> ACK do Three-Way Handshake do TCP.\nFonte: Redes de Computadores, UA 4."
        },
        {
            "ua": "04", "obj": 2, "grau": "DIFÍCIL", "kw": "Sinalizadores TCP (Flags: SYN, ACK, FIN, RST, PSH, URG) e Encerramento de Conexão",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Um analisador de tráfego de rede (Wireshark) registra o encerramento gracioso de uma sessão de transferência de arquivos FTP entre um cliente e um servidor.\n\nO encerramento regular de uma conexão TCP utiliza os sinalizadores **FIN** (Finish) e **ACK** em quatro etapas de troca de pacotes (Four-Way Wavehand).",
            "afirmativas": "Com base nas flags do cabeçalho TCP e encerramento de conexão, analise as afirmativas:\nI. A flag `FIN` é enviada por uma das pontas para indicar que não possui mais dados para transmitir e deseja encerrar a conexão.\nII. A flag `RST` (Reset) é enviada para abortar imediatamente uma conexão anormal ou recusar uma tentativa de conexão a uma porta fechada.\nIII. O envio de um pacote com a flag `FIN=1` apaga imediatamente todo o buffer de recepção sem aguardar a confirmação da outra ponta.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão a função graciosa da flag FIN e o encerramento abrupto da flag RST. A afirmativa III é falsa pois o encerramento por FIN exige confirmações ACK bilaterais sem perda de dados represados.\nFonte: Redes de Computadores, UA 4."
        },
        {
            "ua": "04", "obj": 3, "grau": "DIFÍCIL", "kw": "Controle de Congestionamento TCP (Slow Start, Congestion Avoidance, Fast Retransmit)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Quando um servidor TCP inicia o envio de uma grande quantidade de dados pela internet, ele precisa ajustar a velocidade de transmissão ao nível de congestão dinâmico dos roteadores intermediários na rede.\n\nO TCP gerencia a Janela de Congestionamento (**cwnd**) utilizando a fase de Partida Lenta (**Slow Start**) e a fase de Prevenção de Congestionamento (**Congestion Avoidance**).",
            "afirmativas": "Com base nos algoritmos de controle de congestionamento do TCP, analise as afirmativas:\n\nI. Na fase de Slow Start, o tamanho da janela de congestionamento (cwnd) cresce exponencialmente (dobrando a cada RTT) a partir de 1 MSS até atingir o limite de threshold (ssthresh).\n\nPORQUE\n\nII. Iniciar a conexão enviando a capacidade máxima do link de uma só vez poderia colapsar a memória dos roteadores intermediários por estouro de buffer de filas (Bufferbloat).",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A exploração gradual e exponencial de banda no Slow Start previne o colapso por congestão da rede.\nFonte: Redes de Computadores, UA 4."
        }
    ],
    subfolder='AD'
)

# 17. Redes de Longa Distância (UAs 2, 4)
create_exam(
    "Redes de Longa Distância", "Redes de Longa Distância", "AD Redes de Longa Distância", "2; 4",
    [
        {
            "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Conceito de Comutação de Rótulos (Label Switching) e Pilha de Rótulos MPLS",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em um backbone WAN operado com tecnologia MPLS, o roteamento de pacotes no núcleo da rede não depende de consultas complexas à tabela de roteamento IP completa (Longest Prefix Match).\n\nEm vez disso, os roteadores do núcleo (LSRs - Label Switching Routers) encaminham os pacotes examinando apenas um número inteiro simples contido no campo de rótulo (Label) do cabeçalho MPLS.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica o nome do processo executado por um roteador LSR do núcleo MPLS que substitui o rótulo de entrada por um novo rótulo de saída:",
            "opt_a": "Label Swap (Troca de Rótulo).", "opt_b": "Label Push (Inserção de Rótulo).", "opt_c": "Label Pop (Remoção de Rótulo).", "opt_d": "Label Drop (Descarte de Rótulo).",
            "feedback": "A resposta certa é Label Swap (Troca de Rótulo).\nComentário: No núcleo MPLS (LSR), a operação padrão é o `Label Swap`: o roteador consulta a tabela LFIB, substitui o rótulo antigo pelo novo e despacha o pacote.\nFonte: Redes de Longa Distância, UA 2."
        },
        {
            "ua": "02", "obj": 2, "grau": "MÉDIA", "kw": "VPNs MPLS de Camada 3 (L3VPN) e Tabelas de Roteamento VRF",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Uma operadora de telecomunicações fornece serviços de VPN MPLS de Camada 3 para dois clientes corporativos concorrentes (Cliente A e Cliente B). Ambos os clientes utilizam a mesma faixa de endereçamento IP privado `192.168.1.0/24` em suas redes internas.\n\nPara permitir que a operadora transporte o tráfego de ambos os clientes na mesma infraestrutura sem misturar os pacotes ou gerar conflito de endereços IP, o roteador PE (Provider Edge) utiliza tabelas virtuais de roteamento isoladas.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica a tecnologia do roteador PE responsável por criar instâncias isoladas de tabelas de roteamento e encaminhamento para cada cliente em VPNs MPLS:",
            "opt_a": "VRF (Virtual Routing and Forwarding).", "opt_b": "VLAN 802.1Q Tagging.", "opt_c": "NAT Estático.", "opt_d": "DMZ Perimetral.",
            "feedback": "A resposta certa é VRF (Virtual Routing and Forwarding).\nComentário: A VRF cria instâncias virtuais independentes de tabelas de roteamento em um mesmo roteador físico, permitindo a coincidência de IPs privados entre clientes VPN distintos.\nFonte: Redes de Longa Distância, UA 2."
        },
        {
            "ua": "04", "obj": 1, "grau": "DIFÍCIL", "kw": "Arquitetura de Túneis de Transporte SD-WAN (IPsec sobre Internet / MPLS)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Uma empresa multinacional conecta suas 100 filiais à sede utilizando uma solução SD-WAN. Cada filial possui dois links físicos de transporte: um link de internet comercial de banda larga e um link dedicado MPLS.\n\nPara formar a malha de conectividade segura de overlay (Overlay Network), o roteador SD-WAN estabelece túneis criptografados automáticos sobre ambas as conexões WAN.",
            "afirmativas": "Com base na arquitetura de transporte overlay em SD-WAN, analise as afirmativas:\nI. A malha de overlay SD-WAN utiliza túneis criptografados IPsec (ex: com protocolo DTLS/TLS) para proteger o tráfego que transita sobre links de internet pública.\nII. A abstração de overlay separa a rede de transporte subjacente (Underlay - MPLS/4G/Banda Larga) da rede lógica de conectividade entre filiais.\nIII. A arquitetura SD-WAN exige a contratação de links MPLS dedicados em 100% das filiais, sendo incompatível com conexões comerciais de internet.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com exatidão o tunelamento seguro IPsec e o desacoplamento entre Overlay e Underlay. A afirmativa III é falsa pois a maior vantagem do SD-WAN é justamente permitir a substituição ou combinação de MPLS por links de internet comercial.\nFonte: Redes de Longa Distância, UA 4."
        },
        {
            "ua": "04", "obj": 2, "grau": "DIFÍCIL", "kw": "Qualidade de Experiência (Application-Aware Routing) no SD-WAN",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Em uma filial corporativa conectada por um link MPLS de baixa latência e um link de internet de alta velocidade, uma chamada de videoconferência executiva está em andamento.\n\nO controlador SD-WAN monitora continuamente a latência, o jitter e a perda de pacotes de ambos os links através de sondas BFD (Bidirectional Forwarding Detection). Ao detectar que a latência do link MPLS subiu de 20ms para 300ms, o algoritmo de **Roteamento Sensível à Aplicação** (Application-Aware Routing - AAR) altera o tráfego da videoconferência em tempo real.",
            "afirmativas": "Com base no Roteamento Sensível à Aplicação (AAR) no SD-WAN, analise as afirmativas:\nI. O AAR direciona o tráfego das aplicações dinamicamente para o melhor caminho disponível com base nos requisitos de SLA (latência, jitter e packet loss) daquela classe de aplicação.\nII. O chaveamento de caminho realizado pelo AAR para fluxos de mídia ocorre em tempo real sem derrubar a chamada em andamento.\nIII. O SD-WAN força todo o tráfego de vídeo a utilizar obrigatoriamente o link com a maior perda de pacotes.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão o AAR e a comutação dinâmica sem queda de sessão. A afirmativa III é falsa pois o AAR busca exatamente os caminhos com MENOR perda de pacotes e melhor SLA.\nFonte: Redes de Longa Distância, UA 4."
        },
        {
            "ua": "04", "obj": 3, "grau": "DIFÍCIL", "kw": "Provisionamento de Borda sem Intervenção (Zero-Touch Provisioning - ZTP) no SD-WAN",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Uma empresa de varejo precisa instalar roteadores SD-WAN em 50 novas lojas recém-inauguradas espalhadas por diferentes estados sem enviar engenheiros de rede a cada local.\n\nA equipe utiliza a tecnologia de **Provisionamento sem Intervenção** (Zero-Touch Provisioning - ZTP / Plug-and-Play).",
            "afirmativas": "Com base no ZTP em projetos de SD-WAN, analise as afirmativas:\n\nI. O recurso de ZTP permite que um técnico não especializado na loja apenas conecte o roteador à energia e ao cabo de internet, fazendo com que o equipamento consulte automaticamente o servidor de autenticação na nuvem e baixe todas as suas configurações corporativas sem necessidade de CLI local.\n\nPORQUE\n\nII. O número de série e o certificado de hardware do roteador são previamente cadastrados no portal de orquestração do SD-WAN, permitindo autenticar a identidade do equipamento de forma segura na primeira conexão.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A verificação do número de série e certificado no portal de orquestração é a mecânica de segurança exata que viabiliza o provisionamento Zero-Touch (ZTP).\nFonte: Redes de Longa Distância, UA 4."
        }
    ],
    subfolder='AD'
)

# 18. Redes sem Fio (UAs 2, 6)
create_exam(
    "Redes sem Fio (4º Per Redes)", "Redes Sem Fio", "AD Redes Sem Fio", "2; 6",
    [
        {
            "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Frequências e Canais Wi-Fi (Faixas de 2.4 GHz, 5 GHz e 6 GHz / Wi-Fi 6E)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Durante o planejamento de radiofrequência (RF) para a rede sem fio de uma empresa em um edifício comercial denso, o analista compara as faixas de frequência de 2.4 GHz e 5 GHz.\n\nEle necessita selecionar a faixa de frequência que ofereça maior quantidade de canais não sobrepostos e menor nível de interferência de redes vizinhas para suportar aplicações de alta velocidade.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta a principal vantagem da faixa de frequência de 5 GHz em relação à faixa de 2.4 GHz:",
            "opt_a": "Maior número de canais não sobrepostos disponíveis e menor interferência de eletrodomésticos.", "opt_b": "Maior capacidade de atravessar paredes de concreto armado.", "opt_c": "Alcance físico de cobertura 10 vezes maior em campo aberto.", "opt_d": "Incompatibilidade total com dispositivos móveis modernos.",
            "feedback": "A resposta certa é Maior número de canais não sobrepostos disponíveis e menor interferência de eletrodomésticos.\nComentário: A faixa de 5 GHz oferece mais de 20 canais não sobrepostos de 20 MHz, contra apenas 3 canais em 2.4 GHz, além de ser livre de interferências de fornos micro-ondas e Bluetooth.\nFonte: Redes Sem Fio, UA 2."
        },
        {
            "ua": "02", "obj": 2, "grau": "MÉDIA", "kw": "Largura de Canal e Sobreposição de Canais (Canais 1, 6 e 11 em 2.4 GHz)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Ao configurar três Access Points (APs) vizinhos posicionados no mesmo andar de um escritório operando na frequência de 2.4 GHz, o técnico precisa atribuir os canais de rádio de modo a evitar a interferência co-canal (Co-Channel Interference).\n\nCada canal na faixa de 2.4 GHz possui uma largura de banda de 22 MHz, mas os canais estão espaçados por apenas 5 MHz.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica os três únicos canais de rádio totalmente independentes e não sobrepostos na faixa de 2.4 GHz no Brasil:",
            "opt_a": "Canais 1, 6 e 11.", "opt_b": "Canais 1, 2 e 3.", "opt_c": "Canais 5, 10 e 15.", "opt_d": "Canais 2, 4 e 8.",
            "feedback": "A resposta certa é Canais 1, 6 e 11.\nComentário: Na faixa de 2.4 GHz, os canais 1, 6 e 11 são os únicos três canais com separação de frequência suficiente (25 MHz) para não apresentarem sobreposição de espectro.\nFonte: Redes Sem Fio, UA 2."
        },
        {
            "ua": "06", "obj": 1, "grau": "DIFÍCIL", "kw": "Espaçamento Inter-Quadros (SIFS, DIFS, EIFS) no Mecanismo CSMA/CA",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "O protocolo de acesso ao meio em redes sem fio IEEE 802.11 (CSMA/CA) coordena a transmissão de quadros de rádio utilizando intervalos de tempo fixos chamados Espaçamento Inter-Quadros (IFS - Inter-Frame Space).\n\nOs diferentes valores de IFS (SIFS, PIFS e DIFS) determinam a prioridade de acesso ao canal de rádio para mensagens de confirmação (ACK) e quadros de dados comuns.",
            "afirmativas": "Com base nos intervalos de tempo IFS no protocolo 802.11, analise as afirmativas:\nI. O SIFS (Short Inter-Frame Space) é o menor intervalo de tempo de espera, concedendo maior prioridade para o envio de mensagens imediatas de resposta como ACKs e CTS.\nII. O DIFS (DCF Inter-Frame Space) é o tempo que uma estação deve escutar o meio de rádio ocioso antes de tentar transmitir um quadro de dados comum.\nIII. O SIFS possui um tempo de espera maior que o DIFS para forçar a desconexão de quadros de confirmação.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com exatidão o menor tempo do SIFS para dar prioridade aos ACKs/CTS e o tempo do DIFS para tráfego normal. A afirmativa III é falsa pois o SIFS é mais curto (menor tempo) exatamente para ter prioridade sobre o DIFS.\nFonte: Redes Sem Fio, UA 6."
        },
        {
            "ua": "06", "obj": 2, "grau": "DIFÍCIL", "kw": "Problema do Nó Escondido e Nó Exposto em Redes sem Fio",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Em uma rede sem fio Wi-Fi, dois notebooks clientes (Estação A e Estação B) estão conectados ao mesmo Access Point central (AP), mas estão situados em extremidades opostas da sala separados por uma divisória espessa.\n\nA Estação A consegue escutar o AP, mas não consegue escutar o sinal de rádio da Estação B, configurando o clássico **Problema do Nó Escondido** (Hidden Node Problem).",
            "afirmativas": "Com base no Problema do Nó Escondido em redes 802.11, analise as afirmativas:\nI. No nó escondido, ambas as estações escutam o meio ocioso ao mesmo tempo e transmitem para o AP simultaneamente, causando colisões irrecuperáveis no receptor do AP.\nII. A troca de mensagens de reserva de canal RTS/CTS (Request to Send / Clear to Send) resolve o problema do nó escondido alertando a estação escondida através do aviso do AP.\nIII. O problema do nó escondido ocorre exclusivamente em conexões por cabo de fibra óptica.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II descrevem a causa da colisão no AP no nó escondido e a solução via RTS/CTS. A afirmativa III é falsa pois o nó escondido é um fenômeno exclusivo de redes sem fio não guiadas.\nFonte: Redes Sem Fio, UA 6."
        },
        {
            "ua": "06", "obj": 3, "grau": "DIFÍCIL", "kw": "Eficiência de Transmissão e Overhead de Cabeçalhos no Meio sem Fio",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Ao medir a velocidade útil de download de arquivos (Throughput efetivo na camada de aplicação) em uma rede sem fio Wi-Fi com velocidade nominal de link de 100 Mbps, o usuário obtém uma taxa real de transferência de apenas cerca de 50 a 60 Mbps.\n\nA diferença entre a taxa nominal bruta e o throughput útil decorre da pesada sobrecarga de protocolo (Overhead) exigida pelo meio sem fio.",
            "afirmativas": "Com base no overhead de transmissão em redes Wi-Fi, analise as afirmativas:\n\nI. A taxa útil de transferência de dados em redes Wi-Fi é significativamente menor que a velocidade nominal de enlace devido ao overhead de cabeçalhos 802.11, preâmbulos de rádio, tempos de guarda IFS e confirmações ACK obrigatórias para cada quadro.\n\nPORQUE\n\nII. Redes sem fio operam em modo Half-Duplex sobre um meio compartilhado sujeito a colisões e retransmissões, exigindo mecanismos de checagem e controle de meio inexistentes no Ethernet Full-Duplex.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A operação Half-Duplex e os controles exigidos para a comunicação de rádio justificam o elevado overhead e a diferença entre velocidade nominal e real.\nFonte: Redes Sem Fio, UA 6."
        }
    ],
    subfolder='AD'
)

print("Batch TG 5 concluído.")
