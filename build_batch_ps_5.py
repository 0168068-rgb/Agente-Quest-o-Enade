# -*- coding: utf-8 -*-
"""
Batch PS 5: Disciplinas 15 a 18 (Provas PS 2026-4 - Novos Objetivos e Contextualização ENADE > 7 linhas)
"""
from generate_full_batch import create_exam

# 15. Redes de Alta Disponibilidade
create_exam(
    "Redes de Alta disponibilidade (4º Per redes)", "Redes de Alta Disponibilidade", "PS Redes de Alta Disponibilidade", "3; 6; 8; 10",
    [
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Protocolo LACP e Modos Ativo/Passivo",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Ao configurar a agregação de links de rede entre um servidor de banco de dados e um switch de distribuição via protocolo LACP (IEEE 802.3ad), o administrador de redes deve selecionar os modos de operação das portas no protocolo LACPDU.\n\nPara que o canal lógico EtherChannel seja negociado com sucesso, pelo menos uma das pontas do enlace deve estar configurada no modo Ativo (Active), pronta para enviar pacotes de controle LACPDU.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o comportamento de uma porta configurada no modo LACP Passivo (Passive):",
            "opt_a": "Responde às mensagens LACPDU recebidas da outra ponta, mas não inicia a negociação espontaneamente.", "opt_b": "Inicia a negociação ativamente enviando pacotes LACPDU a cada 1 segundo.", "opt_c": "Bloqueia permanentemente todo o tráfego de dados do servidor.", "opt_d": "Desativa a interface física de rede ao detectar outro switch.",
            "feedback": "A resposta certa é Responde às mensagens LACPDU recebidas da outra ponta, mas não inicia a negociação espontaneamente.\nComentário: No modo LACP Passivo, a porta aguarda o recebimento de pacotes LACPDU da ponta Ativa para responder e fechar o canal.\nFonte: Redes de Alta Disponibilidade, UA 3."
        },
        {
            "ua": "06", "obj": 3, "grau": "MÉDIA", "kw": "Persistência de Sessão (Sticky Sessions) no HAProxy",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Uma aplicação web de portal de serviços estaduais armazena a sessão dos usuários logados na memória RAM local do servidor de aplicação web que atendeu a requisição original.\n\nPara evitar que um usuário logado seja redirecionado aleatoriamente pelo balanceador de carga HAProxy para outro servidor do pool que não possui o estado de sua sessão (causando desconexão indevida), a equipe ativa a **Persistência de Sessão** (Sticky Sessions) baseada em Cookies de aplicação.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta o funcionamento da Persistência de Sessão por Cookie no balanceador de carga:",
            "opt_a": "Injetar um cookie HTTP na resposta do cliente para garantir que requisições subsequentes do mesmo navegador sejam direcionadas ao mesmo servidor do pool.", "opt_b": "Desativar o balanceamento de carga para todos os usuários em horários de pico.", "opt_c": "Criptografar todo o banco de dados do servidor web com algoritmo RSA.", "opt_d": "Redirecionar todo o tráfego de usuários móveis para uma página estática de erro.",
            "feedback": "A resposta certa é Injetar um cookie HTTP na resposta do cliente para garantir que requisições subsequentes do mesmo navegador sejam direcionadas ao mesmo servidor do pool.\nComentário: Sticky Sessions por Cookie identificam o nó do servidor responsável pela sessão e garantem que o HAProxy roteie o cliente para o mesmo servidor enquanto a sessão durar.\nFonte: Redes de Alta Disponibilidade, UA 6."
        },
        {
            "ua": "08", "obj": 1, "grau": "DIFÍCIL", "kw": "Quórum de Cluster e Prevenção de Split-Brain com Corosync/QNet",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um cluster de alta disponibilidade de virtualização de servidores é composto por apenas 2 nós físicos ativos situados no mesmo rack.\n\nPara evitar que uma falha temporária no cabo de rede de batimento cardíaco (Heartbeat) entre os dois nós faça com que ambos pensem que o outro nó morreu e tentem assumir os mesmos discos rígidos compartilhados simultaneamente (cenário catastrófico de Split-Brain), a equipe instala um nó desempatador de quórum externo (QNet Device).",
            "afirmativas": "Com base nos conceitos de Quórum e mitigação de Split-Brain em clusters, analise as afirmativas:\nI. O Quórum representa o número mínimo de votos necessários no cluster para tomar decisões de gerenciamento de recursos de forma segura.\nII. Em um cluster de 2 nós sem nó desempatador, a perda do link de heartbeat faz com que nenhum dos nós atinja a maioria estrita de votos (>50%), paralisando o cluster para proteger os dados.\nIII. O cenário de Split-Brain ocorre quando múltiplos nós assumem a gravação simultânea na mesma partição de armazenamento sem coordenação, promovendo a corrupção do sistema de arquivos.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I, II e III.", "opt_b": "I e II, apenas.", "opt_c": "I e III, apenas.", "opt_d": "II e III, apenas.",
            "feedback": "A resposta certa é I, II e III.\nComentário: Todas as afirmativas são verdadeiras. A exigência de maioria de votos (quórum) e o risco de corrupção em Split-Brain são os conceitos fundamentais da arquitetura de clusters.\nFonte: Redes de Alta Disponibilidade, UA 8."
        },
        {
            "ua": "10", "obj": 2, "grau": "DIFÍCIL", "kw": "Replicação de Armazenamento Ceph e Algoritmo CRUSH",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Para fornecer armazenamento de objetos e blocos altamente disponível e escalável em nuvem privada sem um ponto único de falha (SPOF), uma equipe de infraestrutura implanta um cluster **Ceph Storage** com 10 servidores de armazenamento (OSDs).\n\nO Ceph utiliza o algoritmo determinístico **CRUSH** (Controlled Replication Under Scalable Hashing) para calcular a localização física das réplicas de dados nos discos sem depender de um servidor de metadados centralizado.",
            "afirmativas": "Com base na arquitetura de armazenamento distribuído Ceph e algoritmo CRUSH, analise as afirmativas:\nI. O algoritmo CRUSH calcula dinamicamente onde gravar e ler os objetos com base no mapa do cluster, eliminando gargalos de servidores de tabelas de busca centralizadas.\nII. A regra de replicação no Ceph permite definir que as cópias de um mesmo dado sejam gravadas obrigatoriamente em racks físicos diferentes.\nIII. O Ceph exige que todo o tráfego de leitura de dados seja obrigatoriamente processado por uma única unidade de fita magnética.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II refletem a eficiência do algoritmo CRUSH e a tolerância a falhas por rack no Ceph. A afirmativa III é falsa pois o Ceph distribui a leitura paralelamente entre múltiplos OSDs de disco rígido/NVMe.\nFonte: Redes de Alta Disponibilidade, UA 10."
        },
        {
            "ua": "10", "obj": 3, "grau": "DIFÍCIL", "kw": "Arquitetura Multi-Region Active-Active com DNS Anycast",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Uma plataforma global de pagamentos em nuvem precisa garantir disponibilidade contínua de 99.999% (Cinco Novedades) mesmo em caso de destruição física completa de um Data Center inteiro por um desastre natural.\n\nA arquitetura adota a implantação Multi-Region Ativo-Ativo (Active-Active) com roteamento de borda baseado em **DNS Anycast** e BGP.",
            "afirmativas": "Com base na arquitetura Multi-Region Active-Active e DNS Anycast, analise as afirmativas:\n\nI. O DNS Anycast anuncia o mesmo endereço IP público a partir de múltiplos Data Centers ao redor do mundo via BGP, permitindo que a infraestrutura da internet roteie os clientes automaticamente para o Data Center geograficamente mais próximo e com menor latência.\n\nPORQUE\n\nII. Em caso de queda total de um dos Data Centers regionais, a retirada do anúncio BGP redireciona o tráfego de trânsito dos usuários para o Data Center remanescente de forma transparente em tempo de convergência da internet.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A combinação de Anycast e BGP é a solução padrão de alta disponibilidade global para failover automático de Data Centers.\nFonte: Redes de Alta Disponibilidade, UA 10."
        }
    ],
    subfolder='PS'
)

# 16. Redes de Computadores
create_exam(
    "Redes de Computadores(seg)", "Redes de Computadores", "PS Redes de Computadores", "3; 4; 8; 12",
    [
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Fragmentação e Reagrupamento de Pacotes IP",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Durante o trânsito de um datagrama IPv4 através de múltiplos roteadores na internet, o pacote de 4.000 bytes precisa atravessar um enlace de rede cujo limite máximo de unidade de transmissão (MTU - Maximum Transmission Unit) é de 1.500 bytes.\n\nO roteador intermediário executa o processo de **Fragmentação IP**, dividindo a carga em fragmentos menores e utilizando campos específicos do cabeçalho IPv4 (Identification, Flags e Fragment Offset) para permitir o reagrupamento correto no destino.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica o nó da rede responsável por realizar o reagrupamento final dos fragmentos IP recebidos:",
            "opt_a": "O host de destino final da transmissão.", "opt_b": "O primeiro roteador de borda da operadora.", "opt_c": "O switch de camada 2 da rede local de origem.", "opt_d": "O servidor DNS recursivo da rede.",
            "feedback": "A resposta certa é O host de destino final da transmissão.\nComentário: No IPv4, a fragmentação pode ocorrer nos roteadores intermediários, mas o reagrupamento dos fragmentos é executado exclusivamente pelo host de destino final.\nFonte: Redes de Computadores, UA 3."
        },
        {
            "ua": "04", "obj": 3, "grau": "MÉDIA", "kw": "Controle de Fluxo TCP por Janela Deslizante (Sliding Window)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Um servidor web de alta velocidade envia um grande arquivo de dados para um smartphone conectado a uma rede sem fio instável. Para evitar que o emissor inunde o receptor com uma quantidade de dados superior à sua capacidade de processamento e buffer de memória, o protocolo TCP utiliza o mecanismo de **Controle de Fluxo por Janela Deslizante** (Sliding Window).\n\nO receptor informa continuamente ao emissor o tamanho atual do seu buffer disponível através do campo **Window Size** no cabeçalho dos segmentos TCP de confirmação (ACK).",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta a ação do emissor TCP quando o receptor envia uma confirmação contendo o campo Window Size igual a 0 (zero):",
            "opt_a": "Pausar imediatamente o envio de novos dados até receber uma atualização com tamanho de janela positivo.", "opt_b": "Encerrar a conexão TCP emitindo um pacote RST.", "opt_c": "Duplicar a velocidade de envio de pacotes na interface de rede.", "opt_d": "Descartar todos os pacotes em trânsito e reconectar via UDP.",
            "feedback": "A resposta certa é Pausar imediatamente o envio de novos dados até receber uma atualização com tamanho de janela positivo.\nComentário: Uma janela de tamanho 0 avisa que o buffer do receptor está cheio, instruindo o emissor a parar de enviar dados até que a janela reabra.\nFonte: Redes de Computadores, UA 4."
        },
        {
            "ua": "08", "obj": 1, "grau": "DIFÍCIL", "kw": "Registros DNS CNAME, MX e TXT (SPF/DKIM/DMARC)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um administrador de sistemas configura a zona autoritativa do domínio corporativo `empresa.com.br` no servidor DNS principal para validar o envio de e-mails legítimos e direcionar os acessos web da empresa.\n\nEle cria registros dos tipos CNAME, MX e registros de texto (TXT) contendo as especificações de autenticação de e-mail SPF (Sender Policy Framework) e DKIM.",
            "afirmativas": "Com base nos tipos de registros de recursos do DNS, analise as afirmativas:\nI. O registro do tipo MX (Mail Exchanger) aponta para os servidores de e-mail responsáveis por receber mensagens do domínio.\nII. O registro do tipo CNAME cria um alias (apelido) que aponta um nome de domínio para outro nome de domínio canônico.\nIII. O registro do tipo TXT contendo regras SPF autoriza explicitamente quais endereços IP de servidores estão liberados para enviar e-mails em nome do domínio.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I, II e III.", "opt_b": "I e II, apenas.", "opt_c": "I e III, apenas.", "opt_d": "II e III, apenas.",
            "feedback": "A resposta certa é I, II e III.\nComentário: Todas as afirmativas são verdadeiras. Elas descrevem com exatidão as funções essenciais dos registros MX, CNAME e TXT (SPF) nas zonas DNS.\nFonte: Redes de Computadores, UA 8."
        },
        {
            "ua": "12", "obj": 2, "grau": "DIFÍCIL", "kw": "Mecanismo de Descoberta do MTU do Caminho (PMTUD) no IPv6",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Diferente do protocolo IPv4, a especificação da arquitetura do protocolo IPv6 **aboliu a realização de fragmentação de pacotes por roteadores intermediários** ao longo do caminho de rede.\n\nPara permitir que pacotes de grande tamanho alcancem o destino sem descarte indevido, os hosts de origem em redes IPv6 devem executar o procedimento de **Descoberta do MTU do Caminho** (Path MTU Discovery - PMTUD) baseado em mensagens ICMPv6.",
            "afirmativas": "Com base na fragmentação e PMTUD no protocolo IPv6, analise as afirmativas:\nI. No IPv6, caso um pacote exceda o MTU do link intermediário, o roteador descarta o pacote e retorna uma mensagem ICMPv6 'Packet Too Big' informando o MTU suportado.\nII. O host de origem IPv6 ajusta o tamanho dos pacotes enviados com base nas mensagens ICMPv6 recebidas, realizando a fragmentação na fonte se estritamente necessário.\nIII. O protocolo IPv6 permite que roteadores intermediários fragmentem pacotes de até 64.000 bytes livremente.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com exatidão a mecânica do PMTUD no IPv6. A afirmativa III é falsa pois roteadores IPv6 NUNCA fragmentam pacotes intermediários.\nFonte: Redes de Computadores, UA 12."
        },
        {
            "ua": "12", "obj": 3, "grau": "DIFÍCIL", "kw": "Autoconfiguração Stateless (SLAAC) e Solicitação de Roteador (RS/RA)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Um computador recém-conectado a uma rede local IPv6 obtém automaticamente um endereço global utilizável e a rota padrão de saída sem a necessidade de consultar um servidor DHCPv6.\n\nO processo de Autoconfiguração de Endereço Stateless (SLAAC) baseia-se na troca de mensagens do protocolo ICMPv6 Neighbor Discovery: Solicitação de Roteador (Router Solicitation - RS) e Anúncio de Roteador (Router Advertisement - RA).",
            "afirmativas": "Com base no protocolo SLAAC em redes IPv6, analise as afirmativas:\n\nI. No SLAAC, o host envia uma mensagem ICMPv6 Router Solicitation em multicast e recebe uma resposta Router Advertisement do roteador local contendo o prefixo de rede (ex: `2001:db8:1::/64`), combinando esse prefixo com seu identificador de interface para gerar seu IP único.\n\nPORQUE\n\nII. O mecanismo de Detecção de Endereço Duplicado (DAD - Duplicate Address Detection) é executado em seguida pelo host para garantir que nenhum outro dispositivo na rede local esteja utilizando o mesmo IP autogerado.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. O SLAAC combina o prefixo do RA com a DAD para garantir autoconfiguração sem conflitos de IP.\nFonte: Redes de Computadores, UA 12."
        }
    ],
    subfolder='PS'
)

# 17. Redes de Longa Distância
create_exam(
    "Redes de Longa Distância", "Redes de Longa Distância", "PS Redes de Longa Distância", "2; 4; 6; 9",
    [
        {
            "ua": "02", "obj": 2, "grau": "MÉDIA", "kw": "Engenharia de Tráfego MPLS-TE e Túneis RSVP-TE",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em um backbone WAN MPLS de uma grande operadora de telecomunicações, o link óptico principal entre São Paulo e Rio de Janeiro atinge 95% de ocupação, enquanto um link secundário via Brasília possui 70% de banda ociosa.\n\nPara evitar o gargalo no link principal sem alterar o roteamento padrão IGP (OSPF/IS-IS), a equipe de engenharia estabelece um túnel de Engenharia de Tráfego MPLS (MPLS-TE) utilizando o protocolo de sinalização RSVP-TE para reservar banda ao longo do caminho alternativo.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta o protocolo de sinalização utilizado para reservar largura de banda e estabelecer Caminhos de Rótulos Comutados (LSP) com garantia de SLA no MPLS-TE:",
            "opt_a": "RSVP-TE (Resource Reservation Protocol - Traffic Engineering).", "opt_b": "RIPv2.", "opt_c": "ICMPv6.", "opt_d": "FTP.",
            "feedback": "A resposta certa é RSVP-TE (Resource Reservation Protocol - Traffic Engineering).\nComentário: O RSVP-TE é o protocolo de sinalização responsável por solicitar e reservar a largura de banda necessária ao longo da rota calculada para o túnel MPLS-TE.\nFonte: Redes de Longa Distância, UA 2."
        },
        {
            "ua": "04", "obj": 3, "grau": "MÉDIA", "kw": "Arquitetura de Controlador Centralizado SD-WAN (vManage/vSmart)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Na arquitetura corporativa de uma solução de SD-WAN (Software-Defined WAN), a gestão da rede é dividida em três planos fundamentais: Plano de Orquestração, Plano de Controle e Plano de Gerenciamento/Dados.\n\nO controlador do **Plano de Controle** (ex: vSmart) é responsável por centralizar as decisões de roteamento, aplicar políticas de segurança e distribuir as chaves de criptografia e rotas para os roteadores de borda (vEdge) das filiais via protocolo OMP (Overlay Management Protocol).",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o benefício da separação do Plano de Controle centralizado na arquitetura SD-WAN:",
            "opt_a": "Centralização das políticas de roteamento e segurança em controladores de software, eliminando a necessidade de configurar cada roteador de filial individualmente via CLI.", "opt_b": "Eliminação do uso de cabos físicos nas conexões de fibra óptica.", "opt_c": "Criptografia dos discos rígidos de todos os computadores da empresa.", "opt_d": "Substituição do uso de endereços IP por nomes de domínio locais.",
            "feedback": "A resposta certa é Centralização das políticas de roteamento e segurança em controladores de software, eliminando a necessidade de configurar cada roteador de filial individualmente via CLI.\nComentário: O plano de controle centralizado desacopla a inteligência do hardware, permitindo aplicar políticas globais corporativas em tempo real.\nFonte: Redes de Longa Distância, UA 4."
        },
        {
            "ua": "06", "obj": 1, "grau": "DIFÍCIL", "kw": "Multiplexação por Divisão de Tempo Reconfigurável (ROADM) em DWDM",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Em um backbone de fibra óptica DWDM de longa distância operado por uma concessionária, os engenheiros precisam adicionar ou remover comprimentos de onda (λ - λ-channels) específicos em nós intermediários da rede sem a necessidade de converter todo o tráfego óptico em sinal elétrico.\n\nA equipe instala multiplexadores ópticos de inserção e extração reconfiguráveis (**ROADM** - Reconfigurable Optical Add-Drop Multiplexer).",
            "afirmativas": "Com base na tecnologia ROADM em redes ópticas DWDM, analise as afirmativas:\nI. ROADMs permitem redirecionar comprimentos de onda de luz remotamente via software sem necessidade de intervenção física de técnicos no local.\nII. A tecnologia ROADM realiza o roteamento em nível óptico (Wavelength Routing), reduzindo a latência e o consumo energético ao evitar conversões O-E-O (Óptico-Elétrico-Óptico).\nIII. ROADMs limitam a velocidade total da fibra a no máximo 10 Mbps por canal de luz.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com precisão a flexibilidade do ROADM e a comutação puramente óptica sem conversão O-E-O. A afirmativa III é falsa pois canais ROADM suportam 100G, 400G e 800Gbps por lambda.\nFonte: Redes de Longa Distância, UA 6."
        },
        {
            "ua": "09", "obj": 2, "grau": "DIFÍCIL", "kw": "Redes Móveis 5G Standalone (5G SA) e Network Slicing",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Uma operadora de telecomunicações implantou a arquitetura **5G Standalone (5G SA)** com núcleo de rede em nuvem (5GC - 5G Core Network) para fornecer serviços diferenciados para três públicos: carros autônomos, transmissão de vídeo 8K e sensores IoT de baixa potência.\n\nPara entregar requisitos de SLA totalmente distintos na mesma infraestrutura física de antenas, a operadora utiliza o recurso de **Fatiamento de Rede** (Network Slicing).",
            "afirmativas": "Com base no 5G Standalone e Network Slicing, analise as afirmativas:\nI. O Network Slicing cria redes virtuais ponta a ponta isoladas sobre a mesma infraestrutura física 5G, adaptadas para requisitos específicos de latência, banda e densidade.\nII. O perfil URLLC (Ultra-Reliable Low-Latency Communication) do 5G é projetado para aplicações críticas como cirurgia remota e veículos autônomos com latência < 1ms.\nIII. A arquitetura 5G SA exige a presença de uma central telefônica analógica de comutação por circuitos em cada antena rádio.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com precisão o Network Slicing e a categoria URLLC do 5G SA. A afirmativa III é falsa pois o 5G é uma arquitetura 100% nativa em nuvem baseada em pacotes IP.\nFonte: Redes de Longa Distância, UA 9."
        },
        {
            "ua": "09", "obj": 3, "grau": "DIFÍCIL", "kw": "Arquitetura IPsec com Criptografia AES-GCM e Troca IKEv2",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "No projeto de segurança de interconexão WAN por VPN IPsec entre os Data Centers da empresa, o engenheiro especifica o protocolo de gerenciamento de chaves **IKEv2** (Internet Key Exchange version 2) em conjunto com o algoritmo de criptografia **AES-GCM** (Galois/Counter Mode).\n\nA escolha visa otimizar a velocidade de criptografia do tráfego em gigabits mantendo proteção contra ataques de falsificação de pacotes.",
            "afirmativas": "Com base nas tecnologias IKEv2 e AES-GCM em VPNs IPsec, analise as afirmativas:\n\nI. O algoritmo de criptografia AES-GCM fornece Criptografia Autenticada com Dados Associados (AEAD), garantindo confidencialidade e autenticidade de integridade em uma única operação matemática de alto desempenho em hardware.\n\nPORQUE\n\nII. O protocolo IKEv2 oferece melhor resiliência para reconexão de túneis móveis e menor sobrecarga de trocas de mensagens na fase de estabelecimento em comparação com a versão legada IKEv1.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. O AES-GCM é um algoritmo de cifra simétrica AEAD e o IKEv2 é um protocolo de controle de chaves avançado; embora ambos componham o IPsec moderno, a afirmativa II descreve o IKEv2 e não a justificativa matemática da cifra AEAD.\nFonte: Redes de Longa Distância, UA 9."
        }
    ],
    subfolder='PS'
)

# 18. Redes Sem Fio
create_exam(
    "Redes sem Fio (4º Per Redes)", "Redes Sem Fio", "PS Redes Sem Fio", "2; 6; 9; 11",
    [
        {
            "ua": "02", "obj": 2, "grau": "MÉDIA", "kw": "Tecnologia MU-MIMO (Multi-User MIMO) e Formação de Feixe (Beamforming)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Durante o planejamento de RF de um ambiente corporativo com centenas de dispositivos sem fio conectados simultaneamente aos Access Points (APs), a equipe de redes utiliza a tecnologia **MU-MIMO** (Multi-User Multiple-Input Multiple-Output) do Wi-Fi 5/6.\n\nA tecnologia é combinada com o **Beamforming** explícito para direcionar a energia dos sinais de radiofrequência espacialmente para a localização exata dos dispositivos clientes ativos.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta o benefício direto da tecnologia Beamforming em redes Wi-Fi:",
            "opt_a": "Focar o sinal de radiofrequência na direção específica dos clientes conectados em vez de irradiar em todas as direções uniformemente, aumentando o SNR e alcance.", "opt_b": "Eliminar o uso de senhas de autenticação de segurança na rede sem fio.", "opt_c": "Converter frequências de 5 GHz em frequências de rádio FM comerciais.", "opt_d": "Permitir o uso de cabos UTP para transmitir RF pelo ar sem antenas.",
            "feedback": "A resposta certa é Focar o sinal de radiofrequência na direção específica dos clientes conectados em vez de irradiar em todas as direções uniformemente, aumentando o SNR e alcance.\nComentário: O Beamforming ajusta a fase dos sinais em múltiplas antenas para formar feixes direcionais focados nos clientes, melhorando a relação sinal-ruído (SNR).\nFonte: Redes Sem Fio, UA 2."
        },
        {
            "ua": "06", "obj": 3, "grau": "MÉDIA", "kw": "Roaming Sem Fio Rápido (IEEE 802.11r / 802.11k)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Em um hospital, médicos utilizam robôs de telemedicina e tablets móveis para chamadas de vídeo enquanto caminham entre os corredores do prédio, transitando entre a cobertura de diferentes Access Points (APs).\n\nPara evitar que a reconexão entre os APs cause quedas nas chamadas de voz e vídeo devido ao tempo de reautenticação 802.1X, a equipe ativa o padrão de **Fast BSS Transition** (**IEEE 802.11r**).",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o efeito da implementação do padrão IEEE 802.11r em uma rede Wi-Fi corporativa:",
            "opt_a": "Reduzir o tempo de chaveamento de roaming entre APs para menos de 50 milissegundos pré-autenticando a chave de criptografia.", "opt_b": "Aumentar a potência de transmissão do rádio acima dos limites da Anatel.", "opt_c": "Bloquear o acesso de smartphones não cadastrados no banco de dados.", "opt_d": "Obrigá o usuário a digitar a senha Wi-Fi a cada 10 metros caminhados.",
            "feedback": "A resposta certa é Reduzir o tempo de chaveamento de roaming entre APs para menos de 50 milissegundos pré-autenticando a chave de criptografia.\nComentário: O 802.11r (Fast Roaming) pré-calcula a negociação de chaves WPA2/WPA3 Enterprise antes da transição do cliente para o novo AP, eliminando congelamentos em VoIP.\nFonte: Redes Sem Fio, UA 6."
        },
        {
            "ua": "09", "obj": 1, "grau": "DIFÍCIL", "kw": "Autenticação 802.1X com Certificados EAP-TLS",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Para atingir o nível máximo de segurança da informação exigido pela auditoria em sua rede sem fio corporativa, uma empresa financeira substituiu a autenticação baseada em usuário/senha pelo protocolo **EAP-TLS** no padrão IEEE 802.1X.\n\nNessa arquitetura, a autenticação exige a presença de um Certificado Digital X.509 válido instalado tanto no servidor RADIUS quanto no dispositivo cliente (notebook/smartphone).",
            "afirmativas": "Com base na autenticação Wi-Fi 802.1X com EAP-TLS, analise as afirmativas:\nI. O EAP-TLS fornece autenticação mútua baseada em criptografia assimétrica de certificados digitais no cliente e no servidor RADIUS.\nII. A autenticação EAP-TLS é imune a ataques de Phishing de credenciais porque não utiliza senhas textuais transmitidas pelo usuário.\nIII. O EAP-TLS permite que qualquer dispositivo não identificado conecte-se livremente sem validação prévia de certificado.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão a autenticação mútua por certificados e a imunidade a phishing do EAP-TLS. A afirmativa III é falsa pois dispositivos sem certificado corporativo válido são sumariamente recusados.\nFonte: Redes Sem Fio, UA 9."
        },
        {
            "ua": "11", "obj": 2, "grau": "DIFÍCIL", "kw": "Redes Celulares IoT (NB-IoT vs LTE-M)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Uma empresa de rastreamento de frotas de caminhões e contêineres de transporte de carga seleciona a tecnologia de conectividade celular LPWAN ideal para equipar seus módulos rastreadores em todo o território nacional.\n\nA equipe compara os padrões de redes celulares IoT padronizados pelo 3GPP: **NB-IoT** (Narrowband IoT) e **LTE-M** (Cat-M1).",
            "afirmativas": "Com base nas tecnologias celulares IoT NB-IoT e LTE-M, analise as afirmativas:\nI. O NB-IoT é otimizado para sensores estáticos com transmissão de baixíssimos volumes de dados, fornecendo máxima penetração em ambientes internos (Deep Indoor).\nII. O LTE-M suporta maior taxa de transmissão de dados, mobilidade em tempo real e chamadas de voz (VoLTE), sendo ideal para rastreamento de ativos em movimento.\nIII. Redes NB-IoT e LTE-M operam exclusivamente na frequência não licenciada de 2.4 GHz compartilhada com o forno micro-ondas.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II caracterizam adequadamente os dois perfis de conectividade celular IoT do 3GPP. A afirmativa III é falsa pois NB-IoT e LTE-M operam em espectro licenciado da telefonia celular de operadoras.\nFonte: Redes Sem Fio, UA 11."
        },
        {
            "ua": "11", "obj": 3, "grau": "DIFÍCIL", "kw": "Atenuação de Sinal por Obstáculos e Perda no Espaço Livre (FSPL)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Ao realizar o planejamento de cobertura Wi-Fi em uma fábrica, o engenheiro calcula a Perda de Percurso no Espaço Livre (FSPL - Free Space Path Loss) e o fator de atenuação de paredes de concreto armado e estruturas metálicas.\n\nEle observa que o sinal de rádio transmitido na frequência de 5 GHz sofre maior atenuação física e possui menor alcance de cobertura através de obstáculos do que o sinal na frequência de 2.4 GHz.",
            "afirmativas": "Com base nos conceitos de propagação de RF e atenuação de frequência, analise as afirmativas:\n\nI. Ondas eletromagnéticas de frequências mais altas (como 5 GHz ou 6 GHz) possuem comprimentos de onda menores, resultando em maior atenuação ao atravessar obstáculos físicos sólidos em comparação a frequências menores (2.4 GHz ou sub-GHz).\n\nPORQUE\n\nII. De acordo com a equação de Friis para perda no espaço livre (FSPL), a atenuação do sinal é diretamente proporcional ao quadrado da frequência e ao quadrado da distância percorrida pela onda.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A fórmula matemática da perda no espaço livre (FSPL) demonstra por que frequências maiores atenuam mais rápido com a distância e obstáculos.\nFonte: Redes Sem Fio, UA 11."
        }
    ],
    subfolder='PS'
)

print("Batch PS 5 concluído.")
