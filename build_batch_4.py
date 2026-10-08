# -*- coding: utf-8 -*-
"""
Batch 4: Disciplinas 12 a 14 (Versão ENADE Expandida - Caso Prático Robusto > 7 linhas)
"""
from generate_full_batch import create_exam

# 12. Programação WEB II-Desenvolvimento back-end
create_exam(
    "Programação WEB II- Desenvolvimento Back-end", "Programação WEB II-Desenvolvimento back-end", "AI Programação WEB II-Desenvolvimento back-end", "2; 5; 8; 10",
    [
        {
            "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Arquitetura RESTful e Métodos HTTP (GET, POST, PUT, DELETE)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "No desenvolvimento de uma API RESTful em Node.js/Express para um sistema de gestão de e-commerce de grande porte, a equipe de engenharia de software precisa definir a especificação dos endpoints HTTP para manipulação do recurso 'clientes'. Durante a revisão técnica do código do backend, os desenvolvedores analisaram as rotas responsáveis pela atualização dos cadastros dos usuários.\n\nO requisito do sistema estabelece que o cliente envie uma requisição contendo a representação completa e atualizada de todos os campos do recurso identificado pelo seu ID de cadastro (ex: /api/v1/clientes/4829), de modo que requisições repetidas idênticas produzam exatamente o mesmo estado final no banco de dados, sem gerar registros duplicados nem alterações colaterais involuntárias. A equipe deve selecionar o verbo HTTP padronizado na especificação RFC 7231 que possua semântica idempotente e seja indicado para a substituição/atualização integral do estado do recurso.",
            "afirmativas": "",
            "comando_text": "Considerando os padrões da arquitetura RESTful e a semântica dos métodos HTTP, assinale a opção que indica o método idempotente que deve ser utilizado para atualizar completamente os dados de um recurso existente:",
            "opt_a": "PUT.", "opt_b": "POST.", "opt_c": "GET.", "opt_d": "CONNECT.",
            "feedback": "A resposta certa é PUT.\nComentário: O método HTTP PUT é recomendado pela especificação REST para substituição/atualização integral de um recurso, possuindo semântica idempotente.\nFonte: Programação WEB II-Desenvolvimento back-end, UA 2."
        },
        {
            "ua": "05", "obj": 2, "grau": "MÉDIA", "kw": "Mapeamento Objeto-Relacional (ORM) e Injeção de SQL",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Em uma auditoria de segurança de software realizada na API backend de uma instituição bancária, a equipe de DevSecOps identificou vulnerabilidades críticas decorrentes de rotas legadas que concatenavam diretamente strings de entrada do usuário dentro de instruções SQL puras (SELECT * FROM usuarios WHERE email = ' + input + '). Essa falha permitia a execução de comandos maliciosos arbitrariamente injetados pelos atacantes.\n\nPara remediar essa ameaça e padronizar o acesso à camada de persistência em PostgreSQL, a arquitetura determinou a adoção obrigatória de um framework de Mapeamento Objeto-Relacional (ORM, como Prisma ou Hibernate) integrado a consultas preparadas (Prepared Statements). O objetivo principal é garantir a sanitização dos dados antes de qualquer interação com o banco de dados.",
            "afirmativas": "",
            "comando_text": "Com base nas boas práticas de segurança em desenvolvimento web backend, assinale a alternativa que apresenta a principal defesa contra ataques de injeção de SQL (SQL Injection) fornecida nativamente pelas ferramentas de ORM e consultas preparadas:",
            "opt_a": "Parametrização automática de valores, tratando dados fornecidos pelo usuário estritamente como literais e não como instruções executáveis.", "opt_b": "Criptografia do banco de dados com algoritmo AES-256.", "opt_c": "Bloqueio do acesso de usuários anônimos à porta do servidor HTTP.", "opt_d": "Limitação do tamanho máximo do arquivo de upload no servidor.",
            "feedback": "A resposta certa é Parametrização automática de valores, tratando dados fornecidos pelo usuário estritamente como literais e não como instruções executáveis.\nComentário: Prepared Statements e ORMs separam o código SQL dos dados através de parâmetros delimitados, neutralizando tentativas de SQL Injection.\nFonte: Programação WEB II-Desenvolvimento back-end, UA 5."
        },
        {
            "ua": "08", "obj": 3, "grau": "DIFÍCIL", "kw": "Autenticação por Tokens JWT (JSON Web Token)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Uma arquitetura moderna de microsserviços distribuídos em nuvem adota autenticação stateless baseada em tokens JWT (JSON Web Tokens) transmitidos pelos clientes nos cabeçalhos HTTP sob o formato 'Authorization: Bearer <token>'. O gateway de API recebe as requisições, valida a autenticidade e expiração do token e repassa as informações de identidade do usuário para os serviços downstream sem a necessidade de consultar um servidor central de sessão em memória a cada chamada.\n\nDurante o planejamento da segurança do token JWT, o arquiteto de software analisa a estrutura interna dividida em três partes separadas por pontos (header.payload.signature) e as garantias de privacidade e integridade fornecidas por cada uma dessas seções no ecossistema web.",
            "afirmativas": "Com base na estrutura de um JWT (Header, Payload e Signature), analise as afirmativas:\nI. O Payload do JWT contém as declarações (claims) sobre o usuário (como ID, papéis e tempo de expiração exp).\nII. A Assinatura (Signature) é gerada aplicando um algoritmo hash (como HMAC-SHA256) sobre o Header e Payload codificados em Base64URL utilizando uma chave secreta do servidor.\nIII. O Payload do JWT é automaticamente criptografado por padrão e não pode ser decodificado em Base64 no navegador do cliente.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II detalham a estrutura padrão do JWT. A afirmativa III é falsa pois o Payload de um JWT comum é apenas codificado em Base64URL (visível), não criptografado (a menos que se use JWE).\nFonte: Programação WEB II-Desenvolvimento back-end, UA 8."
        },
        {
            "ua": "10", "obj": 1, "grau": "DIFÍCIL", "kw": "Arquitetura de Microsserviços e Mensageria (RabbitMQ/Kafka)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Para desacoplar a comunicação entre o microsserviço de processamento de vendas e o microsserviço de emissão de notas fiscais eletrônicas em uma plataforma de e-commerce, o arquiteto de software introduziu um broker de mensageria assíncrona (RabbitMQ). Em momentos de alta demanda (como na Black Friday), o volume de novos pedidos supera temporariamente a capacidade de processamento concorrente da SEFAZ, gerando gargalos na integração síncrona original por chamadas REST HTTP.\n\nCom a introdução da arquitetura orientada a eventos e filas de mensagens, a equipe busca garantir a resiliência do sistema, o amortecimento de picos de carga (Load Leveling) e o desacoplamento temporal entre o serviço produtor de eventos e os serviços consumidores.",
            "afirmativas": "Com base nas arquiteturas orientadas a eventos e mensageria, analise as afirmativas:\nI. O desacoplamento temporal permite que o serviço produtor publique mensagens na fila mesmo se o serviço consumidor estiver temporariamente indisponível.\nII. Filas de mensagens garantem alta resiliência e amortecimento de picos de carga (Load Leveling) em sistemas distribuídos.\nIII. A comunicação síncrona via REST HTTP é o único meio capaz de garantir desacoplamento entre microsserviços.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II destacam os benefícios fundamentais da mensageria assíncrona. A afirmativa III é falsa pois chamadas REST síncronas geram acoplamento forte temporal entre serviços.\nFonte: Programação WEB II-Desenvolvimento back-end, UA 10."
        },
        {
            "ua": "10", "obj": 2, "grau": "DIFÍCIL", "kw": "Mecanismo CORS (Cross-Origin Resource Sharing)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Uma aplicação web moderna desenvolvida como Single Page Application (SPA) em React é disponibilizada aos usuários através do domínio público 'https://app.empresa.com'. Durante a navegação, os scripts executados no navegador do cliente efetuam chamadas assíncronas AJAX (via API fetch ou Axios) para obter dados do servidor backend REST hospedado sob o domínio distinto 'https://api.empresa.com'.\n\nNas primeiras tentativas de integração no ambiente de homologação, os desenvolvedores observaram que todas as requisições HTTP eram bloqueadas imediatamente pelo navegador web antes de alcançarem a aplicação, exibindo alertas de violação de segurança no console de desenvolvedor devido às restrições da Política de Mesma Origem (Same-Origin Policy - SOP).",
            "afirmativas": "Com base no mecanismo de segurança CORS (Cross-Origin Resource Sharing), analise as afirmativas:\n\nI. O navegador bloqueia requisições HTTP realizadas entre origens diferentes se o servidor API backend não responder com o cabeçalho HTTP 'Access-Control-Allow-Origin' apropriado.\n\nPORQUE\n\nII. A Política de Mesma Origem (Same-Origin Policy - SOP) implementada pelos navegadores impede por padrão que scripts de uma origem leiam dados de outra origem não autorizada para prevenir ataques XSS e sequestro de sessão.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. O CORS é o mecanismo flexibilizador controlado da Same-Origin Policy dos navegadores.\nFonte: Programação WEB II-Desenvolvimento back-end, UA 10."
        }
    ]
)

# 13. Projeto de Redes de Computadores
create_exam(
    "Projetos de Redes de Computadores (seg)", "Projeto de Redes de Computadores", "AI Projeto de Redes de Computadores", "4; 5; 8; 12",
    [
        {
            "ua": "04", "obj": 1, "grau": "MÉDIA", "kw": "Metodologia PPDIOO da Cisco para Projetos de Redes",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Uma consultoria especializada em infraestrutura foi contratada por uma grande rede de varejo para reformular integralmente a topologia de conectividade de suas 150 filiais e centros de distribuição. Para estruturar o ciclo de vida do projeto de forma metodológica e alinhada às melhores práticas internacionais, a equipe adotou o modelo de referência PPDIOO (Prepare, Plan, Design, Implement, Operate, Optimize) proposto pela Cisco.\n\nNa primeira fase da iniciativa, os consultores reuniram-se com o conselho executivo para mapear as metas estratégicas do negócio, estimar restrições orçamentárias de CAPEX/OPEX, inventariar a infraestrutura física e lógica legada e definir os critérios de sucesso e retorno sobre o investimento (ROI) antes do detalhamento dos requisitos técnicos de rede.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica a fase inicial da PPDIOO na qual são levantados os requisitos de negócios, restrições financeiras e inventário da rede legada:",
            "opt_a": "Preparação (Prepare).", "opt_b": "Otimização (Optimize).", "opt_c": "Implementação (Implement).", "opt_d": "Operação (Operate).",
            "feedback": "A resposta certa é Preparação (Prepare).\nComentário: A fase Prepare estabelece os objetivos de negócios, estratégia e justificativa financeira antes do planejamento detalhado.\nFonte: Projeto de Redes de Computadores, UA 4."
        },
        {
            "ua": "05", "obj": 2, "grau": "MÉDIA", "kw": "Modelo de Design Hierárquico de Redes (Core, Distribution, Access)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "No projeto de reestruturação da rede local de computadores (LAN) de um campus universitário composto por 8 blocos acadêmicos, a equipe de engenharia projetou a topologia física e lógica seguindo rigorosamente a arquitetura hierárquica tradicional de três camadas (Core, Distribution, Access).\n\nCada camada possui atribuições e funções estritamente delimitadas para otimizar o desempenho, a escalabilidade, o isolamento de domínios de difusão (broadcast) e a tolerância a falhas. O projeto especifica que o tráfego originado das estações de trabalho e laboratórios nos blocos deve ser agregado e filtrado em um nível intermediário antes de alcançar o backbone central de altíssima velocidade.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica a camada responsável por agregar o tráfego vindo dos switches de acesso, aplicar políticas de roteamento, listas de controle de acesso (ACLs) e limites de VLAN:",
            "opt_a": "Distribuição (Distribution Layer).", "opt_b": "Acesso (Access Layer).", "opt_c": "Núcleo (Core Layer).", "opt_d": "Borda Externa (DMZ).",
            "feedback": "A resposta certa é Distribuição (Distribution Layer).\nComentário: A camada de distribuição atua como fronteira entre o acesso L2 e o core L3, aplicando políticas de segurança, qualidade de serviço e agrupamento de VLANs.\nFonte: Projeto de Redes de Computadores, UA 5."
        },
        {
            "ua": "08", "obj": 3, "grau": "DIFÍCIL", "kw": "Dimensionamento de Banda e Qualidade de Serviço (QoS)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "No projeto de redes WAN de uma corporação multinacional que conecta a sede aos seus escritórios regionais por links dedicados, a equipe de redes identificou severas degradações de desempenho durante horários de pico. Tráfegos de chamadas de telefonia IP (VoIP), sessões de videoconferência executiva, sistemas ERP críticos e navegação web recreativa disputam concorrentemente a largura de banda limitada do link.\n\nPara solucionar esse conflito de recursos e garantir os Acordos de Nível de Serviço (SLA) das aplicações de missão crítica em tempo real, os engenheiros desenharam uma arquitetura de Qualidade de Serviço (QoS) baseada no modelo DiffServ (Differentiated Services), utilizando marcação de cabeçalhos DSCP e algoritmos de enfileiramento por prioridade nos roteadores de borda.",
            "afirmativas": "Com base nos mecanismos de QoS (DiffServ), analise as afirmativas:\nI. O tráfego de voz (VoIP) exige baixa latência (<150ms), baixo jitter e deve ser classificado com o valor DSCP EF (Expedited Forwarding).\nII. Mecanismos de filas de prioridade (Priority Queuing) garantem tratamento preferencial aos pacotes de voz em momentos de congestão.\nIII. O tráfego HTTP de navegação recreativa deve receber a maior prioridade de largura de banda na fila de saída do roteador.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem corretamente o perfil de tráfego de voz e enfileiramento QoS. A afirmativa III é falsa pois tráfego de navegação web comum é classificado como Best-Effort (menor prioridade).\nFonte: Projeto de Redes de Computadores, UA 8."
        },
        {
            "ua": "12", "obj": 1, "grau": "DIFÍCIL", "kw": "Documentação de Projeto e RFP (Request for Proposal)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "A fase de especificação técnica de um grande projeto de reformulação da infraestrutura de TI de uma instituição pública resultou na elaboração de um conjunto completo de documentos executivos e no lançamento de um processo licitatório na modalidade Request for Proposal (RFP) para contratação de fornecedores de tecnologia.\n\nO documento de projeto técnico deve fornecer a todas as empresas licitantes os subsídios necessários para o correto dimensionamento das propostas comerciais e técnicas, incluindo detalhamento das topologias físicas e lógicas, matriz de endereçamento IP, especificações de equipamentos, além dos procedimentos exigidos para a validação e homologação dos serviços.",
            "afirmativas": "Com base nos componentes de um documento de projeto de redes, analise as afirmativas:\nI. O documento de projeto deve conter diagramas de topologia física, topologia lógica, esquema de endereçamento IP e matriz de requisitos.\nII. A RFP detalha as especificações técnicas exigidas para permitir que fornecedores apresentem propostas comerciais comparáveis.\nIII. O memorial descritivo de projeto pode omitir o plano de testes e comissionamento da rede.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II descrevem os itens essenciais da documentação técnica e da RFP. A afirmativa III é falsa pois o plano de testes e validação é indispensável para homologação do projeto.\nFonte: Projeto de Redes de Computadores, UA 12."
        },
        {
            "ua": "12", "obj": 2, "grau": "DIFÍCIL", "kw": "Estimativa de Custo Total de Propriedade (TCO) em Projetos de Rede",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Durante a apresentação da proposta final de arquitetura para a nova rede corporativa ao comitê executivo de investimentos (C-Level), a equipe de engenharia de redes apresentou uma análise detalhada do Custo Total de Propriedade (TCO - Total Cost of Ownership) projetada para um horizonte de utilização de 5 anos.\n\nO parecer financeiro enfatizou que a tomada de decisão baseada exclusivamente no valor inicial de compra dos switches, roteadores e licenças de software (CAPEX) pode levar a escolhas equivocadas, omitindo o impacto expressivo dos custos operacionais recorrentes (OPEX) ao longo da vida útil da infraestrutura.",
            "afirmativas": "Com base na análise do Custo Total de Propriedade (TCO - Total Cost of Ownership), analise as afirmativas:\n\nI. A avaliação do TCO de um projeto de redes deve contabilizar não apenas a aquisição inicial de hardware e licenças (CAPEX), mas também os custos recorrentes de consumo de energia, manutenção, treinamento e suporte técnico (OPEX) ao longo de todo o ciclo de vida da infraestrutura.\n\nPORQUE\n\nII. Em muitos projetos de TI, os custos operacionais (OPEX) acumulados ao longo de 5 anos superam o investimento inicial de aquisição dos ativos de hardware.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. O TCO pondera CAPEX e OPEX justamente porque a operação contínua frequentemente é a maior fatia de custo total da infraestrutura.\nFonte: Projeto de Redes de Computadores, UA 12."
        }
    ]
)

# 14. Redes Convergentes
create_exam(
    "Redes Convergentes", "Redes Convergentes", "AI Redes Convergentes", "3; 7; 8; 10",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Sinalização VoIP com Protocolo SIP (Session Initiation Protocol)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em uma central telefônica IP corporativa (IP-PBX) baseada na arquitetura aberta de protocolo SIP (Session Initiation Protocol), um usuário utiliza um telefone IP configurado na extensão 1001 para realizar uma chamada de voz para outro ramal na extensão 2005. O processo exige o estabelecimento prévio de uma sessão multimídia bidirecional através de mensagens de sinalização de texto sobre a camada de transporte UDP/TCP.\n\nA arquitetura SIP define um conjunto estrito de métodos (comandos) e respostas numéricas para gerenciar a sinalização de abertura, modificação e encerramento de chamadas de telefonia na rede corporativa.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica a mensagem SIP enviada pelo cliente chamador para estabelecer uma nova sessão de comunicação de voz:",
            "opt_a": "INVITE.", "opt_b": "REGISTER.", "opt_c": "BYE.", "opt_d": "ACK.",
            "feedback": "A resposta certa é INVITE.\nComentário: O método SIP INVITE é utilizado para iniciar um diálogo de estabelecimento de sessão multimídia entre dois endpoints.\nFonte: Redes Convergentes, UA 3."
        },
        {
            "ua": "07", "obj": 2, "grau": "MÉDIA", "kw": "Transporte de Mídia em Tempo Real com RTP/RTCP",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Após a conclusão bem-sucedida do aperto de mão de sinalização via protocolo SIP, a sessão de telefonia IP transita para a fase de transmissão direta dos pacotes de áudio digitalizados entre os dois endpoints VoIP. O fluxo de voz codificado exige transporte em tempo real com mecanismos capazes de compensar o atraso, a ordenação incorreta de pacotes e a variação no tempo de chegada (jitter).\n\nPara atender às restrições de tempo real sem introduzir a latência excessiva causada pelas retransmissões e controles de fluxo rígidos da camada de transporte tradicional, a arquitetura utiliza um protocolo específico de aplicação sobre UDP dotado de cabeçalhos com timestamps e números de sequência.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta o protocolo que transporta os dados de áudio em tempo real com carimbo de data/hora (timestamp) e número de sequência sobre UDP:",
            "opt_a": "RTP (Real-time Transport Protocol).", "opt_b": "TCP (Transmission Control Protocol).", "opt_c": "HTTP (Hypertext Transfer Protocol).", "opt_d": "FTP (File Transfer Protocol).",
            "feedback": "A resposta certa é RTP (Real-time Transport Protocol).\nComentário: O RTP roda sobre UDP para transmitir dados multimídia em tempo real, fornecendo timestamps para reconstrução de jitter e números de sequência para reordenação de pacotes.\nFonte: Redes Convergentes, UA 7."
        },
        {
            "ua": "08", "obj": 3, "grau": "DIFÍCIL", "kw": "Codecs de Voz (G.711, G.729) e Consumo de Bandwidth",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um engenheiro de redes e telecomunicações foi encarregado de dimensionar o link WAN dedicado necessário para interligar a central telefônica da sede de uma empresa à sua central de atendimento (Call Center) remota. A infraestrutura precisa suportar a ocorrência simultânea de 50 chamadas de voz com alta inteligibilidade e estabilidade operacional.\n\nPara otimizar o consumo de dados do link mantendo os padrões exigidos de qualidade da fala (avaliados na escala MOS - Mean Opinion Score), o especialista analisa os trade-offs entre a codificação sem compressão G.711 (PCM) e o codec de alta compressão G.729 (CS-ACELP), calculando a taxa de bits bruta e o impacto dos cabeçalhos dos pacotes.",
            "afirmativas": "Com base nos codecs de voz G.711 (PCM) e G.729 (CS-ACELP), analise as afirmativas:\nI. O codec G.711 produz uma taxa de amostragem sem compressão de 64 kbps por canal de voz com excelente qualidade sonora (MOS ~4.4).\nII. O codec G.729 utiliza compressão avançada reduzindo a taxa de amostragem para 8 kbps, economizando banda em links WAN restritos.\nIII. A inclusão dos cabeçalhos IP/UDP/RTP reduz a sobrecarga total do pacote VoIP para zero bytes.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II apresentam com precisão os dois codecs de voz mais populares e suas taxas de bit. A afirmativa III é falsa pois os cabeçalhos IP/UDP/RTP adicionam cerca de 40 bytes de overhead por pacote.\nFonte: Redes Convergentes, UA 8."
        },
        {
            "ua": "10", "obj": 1, "grau": "DIFÍCIL", "kw": "Engenharia de Tráfego IPTV e Multicast (IGMP/PIM)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Uma operadora de telecomunicações disponibiliza um serviço de televisão digital via protocolo IP (IPTV) transmitindo 150 canais em alta definição (HD/4K) para milhares de assinantes conectados à sua rede de acesso por fibra óptica (GPON). Para enviar a mesma transmissão de vídeo ao vivo de um canal para centenas de receptores simultâneos no mesmo bairro sem duplicar exaustivamente os fluxos de pacotes e colapsar os links de transmissão, o projeto adota arquitetura de roteamento Multicast.\n\nA infraestrutura exige a atuação coordenada de protocolos no nível dos dispositivos clientes (set-top boxes) para gerenciamento de grupos de escuta e protocolos entre os roteadores de borda para a construção de árvores de distribuição dinâmicas.",
            "afirmativas": "Com base nos protocolos de distribuição Multicast (IGMP e PIM-SM), analise as afirmativas:\nI. O protocolo IGMP (Internet Group Management Protocol) é utilizado pelos set-top boxes para solicitar entrada ou saída de um grupo multicast na rede local.\nII. O PIM-SM (Protocol Independent Multicast - Sparse Mode) constrói árvores de distribuição multicast entre roteadores utilizando um Ponto de Encontro (Rendezvous Point - RP).\nIII. A transmissão em Unicast é mais eficiente que o Multicast para enviar a mesma transmissão de vídeo ao vivo simultaneamente para 10.000 usuários.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com precisão as funções do IGMP e PIM-SM na distribuição multicast de vídeo. A afirmativa III é falsa pois o Unicast duplicaria a transmissão 10.000 vezes, colapsando a rede.\nFonte: Redes Convergentes, UA 10."
        },
        {
            "ua": "10", "obj": 2, "grau": "DIFÍCIL", "kw": "Métricas de Qualidade de Experiência (QoE) e MOS em Redes Convergentes",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "A equipe de operações de TI de uma empresa multinacional monitora a qualidade de transmissão das sessões de videoconferência corporativa e chamadas de voz via IP utilizando ferramentas de medição baseadas na métrica padronizada MOS (Mean Opinion Score), que qualifica a percepção subjetiva dos usuários em uma escala de 1 a 5.\n\nDurante o diagnóstico de incidentes recorrentes de voz picotada e robótica, os analistas constataram variações severas no tempo de atraso de chegada dos pacotes de áudio (Jitter) no receptor. Para conter essa oscilação, o sistema depende da atuação de um buffer de de-jitter na recepção.",
            "afirmativas": "Com base nos conceitos de MOS (Mean Opinion Score) e Jitter, analise as afirmativas:\n\nI. A variação no tempo de chegada dos pacotes de áudio/vídeo (Jitter) exige o uso de um Jitter Buffer na recepção para recompor a cadência contínua do sinal de mídia.\n\nPORQUE\n\nII. Jitter excessivo que supere a capacidade do buffer de de-jitter resulta no descarte de pacotes de voz pelo receptor, degradando severamente a pontuação de qualidade MOS percebida pelo usuário.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. O Jitter Buffer é essencial para mitigar o jitter, e quando estourado, o descarte de pacotes prejudica a inteligibilidade do áudio e derruba a nota MOS.\nFonte: Redes Convergentes, UA 10."
        }
    ]
)

print("Batch 4 atualizado com contextualização ENADE expandida.")
