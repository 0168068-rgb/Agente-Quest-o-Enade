# -*- coding: utf-8 -*-
"""
Batch PS 4: Disciplinas 12 a 14 (Provas PS 2026-4 - Novos Objetivos e Contextualização ENADE > 7 linhas)
"""
from generate_full_batch import create_exam

# 12. Programação WEB II-Desenvolvimento back-end
create_exam(
    "Programação WEB II- Desenvolvimento Back-end", "Programação WEB II-Desenvolvimento back-end", "PS Programação WEB II-Desenvolvimento back-end", "2; 5; 8; 10",
    [
        {
            "ua": "02", "obj": 2, "grau": "MÉDIA", "kw": "Códigos de Status HTTP (200, 201, 400, 401, 404, 500)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Durante o desenvolvimento e testes de integração da API RESTful de um sistema bancário, os desenvolvedores tratam as respostas HTTP emitidas pelos endpoints para garantir que os clientes da API interpretem o resultado do processamento de forma padronizada.\n\nAo efetuar uma requisição HTTP `POST /api/v1/contas` para criar com sucesso um novo cadastro de conta no banco de dados, o servidor deve retornar a representação do novo recurso criado acompanhada do código de status HTTP adequado.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta o código de status HTTP padronizado (RFC 7231) que indica que a requisição foi bem-sucedida e resultou na criação de um novo recurso:",
            "opt_a": "201 Created.", "opt_b": "200 OK.", "opt_c": "400 Bad Request.", "opt_d": "204 No Content.",
            "feedback": "A resposta certa é 201 Created.\nComentário: O código 201 Created é a resposta padrão REST para requisições POST bem-sucedidas que resultam na criação efetiva de um novo recurso.\nFonte: Programação WEB II-Desenvolvimento back-end, UA 2."
        },
        {
            "ua": "05", "obj": 3, "grau": "MÉDIA", "kw": "Padrão DTO (Data Transfer Object) e Validação de Payload",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Para evitar que dados sensíveis da camada de persistência (como hash de senha ou chaves internas) sejam expostos nas respostas JSON da API web, a equipe de arquitetura adota o padrão DTO (Data Transfer Object).\n\nAlém de moldar o formato dos dados retornados ao cliente, os DTOs de entrada são combinados com bibliotecas de validação de esquemas (como class-validator ou Zod) para barrar payloads malformados antes do processamento do controller.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta a principal função do padrão DTO em uma arquitetura de API RESTful:",
            "opt_a": "Desacoplar os modelos de dados internos da entidade de banco de dados da representação externa trafegada nas requisições HTTP.", "opt_b": "Executar o balanceamento de carga entre servidores backend.", "opt_c": "Criptografar as tabelas de banco de dados em disco.", "opt_d": "Substituir a necessidade de roteamento de URLs na aplicação.",
            "feedback": "A resposta certa é Desacoplar os modelos de dados internos da entidade de banco de dados da representação externa trafegada nas requisições HTTP.\nComentário: O DTO atua como uma camada de transporte de dados sob medida, isolando a estrutura do banco de dados das interfaces expostas na API.\nFonte: Programação WEB II-Desenvolvimento back-end, UA 5."
        },
        {
            "ua": "08", "obj": 1, "grau": "DIFÍCIL", "kw": "Estratégias de Caching de API com Redis",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Para suportar o acesso simultâneo de milhões de usuários à página principal de um portal de notícias sem sobrecarregar o banco de dados relacional principal, os engenheiros implantaram uma camada de Caching em memória com Redis.\n\nAo receber um pedido de consulta, o backend verifica primeiramente se o dado está presente no Redis (Cache Hit); caso não esteja (Cache Miss), consulta o banco de dados, grava o resultado no Redis com um tempo de expiração (TTL) e retorna a resposta.",
            "afirmativas": "Com base nas estratégias de caching com Redis em APIs web, analise as afirmativas:\nI. O armazenamento de dados em memória RAM no Redis fornece tempos de resposta em sub-milissegundos para consultas repetitivas.\nII. A definição adequada do TTL (Time To Live) é indispensável para evitar que dados desatualizados (stale data) permaneçam infinitamente no cache.\nIII. O Redis substitui obrigatoriamente todos os bancos de dados relacionais e sistemas de arquivos de uma aplicação web.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II refletem a alta velocidade do Redis e a importância do TTL na invalidação de cache. A afirmativa III é falsa pois o Redis atua como cache temporário/secundário e chave-valor, não substituindo o banco relacional primário.\nFonte: Programação WEB II-Desenvolvimento back-end, UA 8."
        },
        {
            "ua": "10", "obj": 2, "grau": "DIFÍCIL", "kw": "Arquitetura de API Gateway e Rate Limiting",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Uma corporação migrou seus sistemas para uma arquitetura de microsserviços e posicionou um **API Gateway** na entrada da infraestrutura para centralizar roteamento, autenticação, encerramento TLS e controle de tráfego.\n\nPara proteger os microsserviços contra ataques de negação de serviço e abuso de consumo por scripts não autorizados, o API Gateway aplica algoritmos de **Rate Limiting** (como Token Bucket ou Leaky Bucket).",
            "afirmativas": "Com base na arquitetura de API Gateway e Rate Limiting, analise as afirmativas:\nI. O Rate Limiting restringe a quantidade máxima de requisições HTTP que um determinado cliente (identificado por IP ou chave de API) pode realizar em um intervalo de tempo.\nII. Quando o limite de requisições do cliente é excedido, o API Gateway retorna o código de status `HTTP 429 Too Many Requests`.\nIII. O API Gateway exige que cada microsserviço downstream implemente seu próprio certificado TLS e mecanismo de roteamento de borda.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem corretamente a função do Rate Limiting e o retorno do código HTTP 429. A afirmativa III é falsa pois o API Gateway centraliza e desonera os microsserviços do gerenciamento de TLS e roteamento de borda.\nFonte: Programação WEB II-Desenvolvimento back-end, UA 10."
        },
        {
            "ua": "10", "obj": 3, "grau": "DIFÍCIL", "kw": "Arquiteturas Event-Driven e Padrão Saga",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Em um sistema de e-commerce baseado em microsserviços (Serviço de Pedidos, Serviço de Pagamento e Serviço de Estoque), a realização de uma compra exige uma transação distribuída que abrange múltiplos bancos de dados independentes.\n\nComo transações ACID tradicionais com bloqueio de duas fases (2PC) prejudicam o desempenho e a disponibilidade em nuvem, os arquitetos implementaram o **Padrão Saga** (Saga Pattern) baseado em eventos coordenados com ações de compensação.",
            "afirmativas": "Com base no Padrão Saga em arquiteturas de microsserviços, analise as afirmativas:\n\nI. O Padrão Saga gerencia transações distribuídas como uma sequência de transações locais em cada microsserviço, onde a falha de uma etapa dispara eventos com transações compensatórias para desfazer as alterações anteriores.\n\nPORQUE\n\nII. Transações compensatórias garantem a consistência eventual (Eventual Consistency) do sistema sem a necessidade de manter bloqueios (locks) síncronos de longa duração em bancos de dados distintos.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A substituição do bloqueio síncrono 2PC por transações compensatórias assíncronas é a essência do Padrão Saga para consistência eventual.\nFonte: Programação WEB II-Desenvolvimento back-end, UA 10."
        }
    ],
    subfolder='PS'
)

# 13. Projeto de Redes de Computadores
create_exam(
    "Projetos de Redes de Computadores (seg)", "Projeto de Redes de Computadores", "PS Projeto de Redes de Computadores", "4; 5; 8; 12",
    [
        {
            "ua": "04", "obj": 2, "grau": "MÉDIA", "kw": "Mapeamento de Requisitos Técnicos e Matriz de Tráfego",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Na fase de análise de requisitos de um projeto de redes para um novo hospital de alta complexidade, a equipe de engenharia realiza o levantamento do perfil de tráfego de dados gerado pelos equipamentos de tomografia, sistemas de prontuário eletrônico e câmeras de monitoramento IP.\n\nPara dimensionar a capacidade dos links e switches, os engenheiros constroem a **Matriz de Tráfego**, mapeando as fontes de dados, os destinos, os volumes de dados em megabits por segundo e os requisitos de latência de cada aplicação.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica o objetivo principal da construção de uma Matriz de Tráfego no planejamento de redes:",
            "opt_a": "Identificar os fluxos de dados predominantes na rede para dimensionar corretamente a largura de banda dos links de distribuição e núcleo.", "opt_b": "Definir as senhas de administração dos roteadores corporativos.", "opt_c": "Substituir a necessidade de testes de certificação de cabos de cobre.", "opt_d": "Calcular o imposto sobre aquisição de equipamentos importados.",
            "feedback": "A resposta certa é Identificar os fluxos de dados predominantes na rede para dimensionar corretamente a largura de banda dos links de distribuição e núcleo.\nComentário: A Matriz de Tráfego mapeia quem fala com quem e qual o volume de tráfego trocado, fornecendo a base quantitativa para o dimensionamento dos links.\nFonte: Projeto de Redes de Computadores, UA 4."
        },
        {
            "ua": "05", "obj": 3, "grau": "MÉDIA", "kw": "Projeto de Redundância e Alta Disponibilidade com HSRP/VRRP",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "No projeto de camada 3 da rede local de uma empresa financeira, duas interfaces de roteadores de borda atuarão como gateway padrão (Default Gateway) para os computadores dos usuários.\n\nPara evitar que a falha física de um único roteador de borda interrompa o acesso à internet de toda a empresa, a equipe de projeto configura um protocolo de redundância de primeiro salto (First Hop Redundancy Protocol - FHRP), como VRRP ou HSRP.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta o mecanismo operacional de protocolos FHRP como o VRRP/HSRP:",
            "opt_a": "Compartilhar um endereço IP virtual e um endereço MAC virtual entre dois ou mais roteadores, assumindo o controle em caso de falha do nó ativo.", "opt_b": "Mesclar as tabelas de roteamento BGP de provedores concorrentes em uma única sessão.", "opt_c": "Executar a criptografia dos arquivos salvos nas estações de trabalho.", "opt_d": "Converter pacotes IPv4 em IPv6 sem o uso de cabeçalhos virtuais.",
            "feedback": "A resposta certa é Compartilhar um endereço IP virtual e um endereço MAC virtual entre dois ou mais roteadores, assumindo o controle em caso de falha do nó ativo.\nComentário: O IP/MAC virtual é o gateway configurado nos clientes; caso o roteador primário falhe, o secundário assume o IP virtual de forma transparente.\nFonte: Projeto de Redes de Computadores, UA 5."
        },
        {
            "ua": "08", "obj": 1, "grau": "DIFÍCIL", "kw": "Dimensionamento de Links WAN e Acordos de SLA",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Ao contratar links de comunicação WAN para interligar as filiais de uma corporação, o projetista de redes estabelece os Acordos de Nível de Serviço (SLA - Service Level Agreement) que devem ser cumpridos contratualmente pelas operadoras de telecomunicações.\n\nO documento de SLA define parâmetros técnicos estritos de disponibilidade percentual, latência máxima bidirecional (RTT), limite aceitável de variação do atraso (Jitter) e taxa de perda de pacotes (Packet Loss).",
            "afirmativas": "Com base nas métricas de SLA em projetos de WAN, analise as afirmativas:\nI. A métrica de RTT (Round Trip Time) mede o tempo total que um pacote leva para ir da origem ao destino e retornar à origem.\nII. Uma disponibilidade contratual de 'Quatro Novedades' (99.99%) admite um tempo de indisponibilidade máximo de aproximadamente 52 minutos por ano.\nIII. A taxa de perda de pacotes em links corporativos SLA de alta qualidade pode atingir até 25% sem comprometer as aplicações.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com precisão o RTT e a janela de indisponibilidade de 99.99%. A afirmativa III é falsa pois a perda de pacotes aceitável em SLAs corporativos é inferior a 0.1% a 0.5%.\nFonte: Projeto de Redes de Computadores, UA 8."
        },
        {
            "ua": "12", "obj": 2, "grau": "DIFÍCIL", "kw": "Plano de Testes, Homologação e Comissionamento de Rede",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Após a conclusão da instalação física e lógica da nova rede de um Data Center, a equipe de projeto inicia a fase de **Comissionamento e Homologação** antes de autorizar a entrada em produção dos serviços críticos.\n\nO Plano de Testes de Aceitação (ATP - Acceptance Test Plan) inclui simulações de failover de links, testes de carga sob estresse de tráfego, verificação de rotas de failover e auditagem de rotulagem e documentação da rede.",
            "afirmativas": "Com base no processo de comissionamento de projetos de rede, analise as afirmativas:\nI. Os testes de estresse (Burn-in) submetem os ativos de rede à carga máxima contínua por um período determinado para identificar falhas infantis de componentes.\nII. O relatório de comissionamento devidamente assinado pelas partes valida a conformidade do projeto com o termo de referência (RFP).\nIII. A fase de comissionamento deve ser realizada apenas 6 meses após a entrada oficial em produção.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão os testes Burn-in e a homologação formal do projeto. A afirmativa III é falsa pois o comissionamento é realizado ANTES da entrega e aceite da rede em produção.\nFonte: Projeto de Redes de Computadores, UA 12."
        },
        {
            "ua": "12", "obj": 3, "grau": "DIFÍCIL", "kw": "Gestão de Riscos e Matriz de Impacto em Projetos de Rede",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Durante o gerenciamento do projeto de migração da infraestrutura de rede de uma empresa, o gerente de projetos constrói a Matriz de Riscos (Probabilidade x Impacto) para identificar ameaças potenciais ao prazo e orçamento da implantação.\n\nUm dos riscos mapeados é o atraso na entrega dos switches importados pelo fornecedor, o que paralisaria a fase de configuração dos ambientes de produção.",
            "afirmativas": "Com base no gerenciamento de riscos em projetos de infraestrutura de rede, analise as afirmativas:\n\nI. O plano de resposta aos riscos deve priorizar eventos que combinem alta probabilidade de ocorrência e alto impacto negativo no projeto, definindo ações preventivas e planos de contingência prévios.\n\nPORQUE\n\nII. A identificação antecipada de gargalos de suprimentos (Procurement) permite contratar fornecedores secundários ou readequar o cronograma sem estourar o orçamento do projeto.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A matriz de severidade orienta onde alocar recursos de mitigação para proteger as restrições do projeto.\nFonte: Projeto de Redes de Computadores, UA 12."
        }
    ],
    subfolder='PS'
)

# 14. Redes Convergentes
create_exam(
    "Redes Convergentes", "Redes Convergentes", "PS Redes Convergentes", "3; 7; 8; 10",
    [
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Arquitetura SIP Proxy Server vs Registrador",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em uma rede de telefonia IP corporativa com múltiplos domínios SIP, os telefones IP precisam localizar os endereços IP reais dos destinatários das chamadas a partir de URLs SIP (ex: `sip:usuario@empresa.com`).\n\nPara gerenciar o registro das localizações atuais das extensões na rede e rotear as mensagens de sinalização `INVITE` para o destino correto, a infraestrutura depende de servidores de sinalização SIP (Proxy Server e Registrar).",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta a função do servidor SIP Registrar:",
            "opt_a": "Receber as mensagens `REGISTER` dos clientes VoIP e atualizar o banco de dados de localização com o mapeamento IP/Porta atual do ramal.", "opt_b": "Comprimir o sinal analógico de áudio em pacotes digitais.", "opt_c": "Converter sinalização SIP em tráfego de vídeo HDMI.", "opt_d": "Fornecer energia elétrica aos telefones IP via cabo de par trançado.",
            "feedback": "A resposta certa é Receber as mensagens REGISTER dos clientes VoIP e atualizar o banco de dados de localização com o mapeamento IP/Porta atual do ramal.\nComentário: O SIP Registrar autêntica o ramal e grava no Location Server a associação entre o URI SIP e o IP físico atual do dispositivo.\nFonte: Redes Convergentes, UA 3."
        },
        {
            "ua": "07", "obj": 3, "grau": "MÉDIA", "kw": "Controle de Qualidade com Protocolo RTCP (Real-time Control Protocol)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Enquanto o protocolo RTP é encarregado da transmissão dos pacotes de mídia em tempo real de uma chamada de videoconferência, seu protocolo irmão **RTCP** (Real-time Transport Control Protocol) roda em paralelo sobre portas UDP contíguas.\n\nO RTCP envia periodicamente pacotes de controle entre os participantes da sessão multimídia para fornecer estatísticas de qualidade de serviço e telemetria da transmissão de rede.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica as estatísticas de desempenho monitoradas e relatadas pelas mensagens RTCP Sender/Receiver Reports:",
            "opt_a": "Contagem de pacotes perdidos, variação do atraso (jitter) e tempo de ida e volta (RTT).", "opt_b": "Resolução da tela em pixels e taxa de quadros por segundo (FPS).", "opt_c": "Contas de e-mail cadastradas na lista de contatos do usuário.", "opt_d": "Senhas de criptografia WPA3 das redes sem fio locais.",
            "feedback": "A resposta certa é Contagem de pacotes perdidos, variação do atraso (jitter) e tempo de ida e volta (RTT).\nComentário: O RTCP monitora o desempenho do canal multimídia, fornecendo feedback de telemetria sobre perda, jitter e RTT aos endpoints.\nFonte: Redes Convergentes, UA 7."
        },
        {
            "ua": "08", "obj": 1, "grau": "DIFÍCIL", "kw": "Mecanismos de Supressão de Silêncio (VAD/CNG) em Telefonia IP",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Durante uma conversa telefônica normal via VoIP, estima-se que em cerca de 50% do tempo do canal um dos interlocutores está apenas escutando em silêncio. Transmitir pacotes contendo amostras de silêncio desperdiça largura de banda valiosa da rede.\n\nPara otimizar o consumo de dados do link WAN, os gateways de telefonia utilizam o Detector de Atividade de Voz (VAD - Voice Activity Detection) e o Gerador de Ruído de Conforto (CNG - Comfort Noise Generator).",
            "afirmativas": "Com base nos mecanismos VAD e CNG em voz sobre IP, analise as afirmativas:\nI. O VAD interrompe a geração e o envio de pacotes RTP quando detecta períodos de silêncio na fala do usuário.\nII. O CNG sintetiza um ruído de fundo suave na recepção durante os momentos de silêncio para evitar que o ouvinte pense que a chamada caiu devido ao silêncio absoluto.\nIII. O VAD aumenta o consumo de banda da rede ao duplicar a amostragem de dados durante o silêncio.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com exatidão o papel do VAD (cessar pacotes no silêncio) e do CNG (gerar ruído de conforto na ponta remota). A afirmativa III é falsa pois o objetivo do VAD é justamente economizar banda.\nFonte: Redes Convergentes, UA 8."
        },
        {
            "ua": "10", "obj": 2, "grau": "DIFÍCIL", "kw": "Engenharia de Tráfego em Redes HFC (DOCSIS 3.1/4.0)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Uma operadora de TV a cabo e banda larga entrega telefonia, internet gigabit e canais de vídeo para milhares de clientes utilizando uma infraestrutura híbrida de fibra óptica e cabo coaxial (HFC - Hybrid Fiber-Coaxial).\n\nPara suportar a transmissão de dados de alta velocidade sobre o cabo coaxial residencial de forma convergente, a rede adota o padrão de transmissão DOCSIS (Data Over Cable Service Interface Specification).",
            "afirmativas": "Com base nas especificações da tecnologia DOCSIS em redes HFC, analise as afirmativas:\nI. O padrão DOCSIS 3.1/4.0 utiliza modulação de amplitude em quadratura (OFDM/OFDMA) para alcançar velocidades multgigabit sobre a rede de cabo coaxial.\nII. O equipamento CMTS (Cable Modem Termination System) atua como a central de terminação de dados localizada no Headend da operadora.\nIII. A tecnologia HFC substitui obrigatoriamente todas as fibras ópticas por cabos de par trançado de cobre Categoria 5e.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II refletem a modulação avançada do DOCSIS e a função do CMTS no Headend. A afirmativa III é falsa pois redes HFC utilizam backbone de fibra óptica até os nós de distribuição (Nodes).\nFonte: Redes Convergentes, UA 10."
        },
        {
            "ua": "10", "obj": 3, "grau": "DIFÍCIL", "kw": "Desafios de Sincronismo e Latência em Videoconferências 4K",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Durante a transmissão de uma teleconferência cirúrgica em tempo real em resolução 4K entre dois hospitais universitários, a equipe de engenharia médica monitora o sincronismo de lábios (Lip Sync) entre o áudio falado e o vídeo do cirurgião.\n\nComo o fluxo de vídeo exige maior tempo de decodificação e processamento em relação ao fluxo de áudio, descompassos de tempo na entrega geram desincronia perceptível e desconfortável aos espectadores.",
            "afirmativas": "Com base no sincronismo multimídia em tempo real, analise as afirmativas:\n\nI. O receptor de mídia utiliza os timestamps sincronizados dos cabeçalhos RTP/RTCP para realizar o alinhamento temporal (Lip Sync) entre as faixas independentes de áudio e vídeo antes do envio à tela e alto-falantes.\n\nPORQUE\n\nII. Variações diferenciadas de latência e tempo de decodificação entre os codecs de vídeo pesados (ex: H.265/HEVC) e os codecs de áudio leves exigem ajuste de compensação de buffer no receptor.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. Os timestamps do RTP alinhados pelo RTCP são o mecanismo padrão para compensar as assimetrias de processamento de áudio/vídeo.\nFonte: Redes Convergentes, UA 10."
        }
    ],
    subfolder='PS'
)

print("Batch PS 4 concluído.")
