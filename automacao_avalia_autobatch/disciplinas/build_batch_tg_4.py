# -*- coding: utf-8 -*-
"""
Batch TG 4: Disciplinas 12 a 14 (Provas TG 2026-4 - UAs Específicas do Tema Gerador e Contextualização ENADE > 7 linhas)
"""
from generate_full_batch import create_exam

# 12. Programação WEB II-Desenvolvimento back-end (UAs 2, 5)
create_exam(
    "Programação WEB II- Desenvolvimento Back-end", "Programação WEB II-Desenvolvimento back-end", "AD Programação WEB II-Desenvolvimento back-end", "2; 5",
    [
        {
            "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Protocolo HTTP/1.1 vs HTTP/2 (Multiplexação e Cabeçalhos HPACK)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Para acelerar a velocidade de carregamento de uma aplicação web backend e reduzir o tempo de latência de rede, a equipe de engenharia atualizou o protocolo de transferência dos servidores web para o **HTTP/2** (RFC 7540).\n\nDiferente do protocolo HTTP/1.1 legado que abria múltiplas conexões TCP paralelas sujeitas a bloqueio de início da fila (Head-of-Line Blocking), o HTTP/2 utiliza uma única conexão TCP persistente em formato binário.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta a tecnologia do HTTP/2 responsável por enviar múltiplos pedidos e respostas assíncronas intercaladas sobre uma mesma conexão TCP:",
            "opt_a": "Multiplexação de Streams (Streams Multiplexing).", "opt_b": "Criação de novos sockets UDP sem criptografia.", "opt_c": "Desativação de cabeçalhos HTTP de resposta.", "opt_d": "Execução de consultas SQL diretamente no navegador.",
            "feedback": "A resposta certa é Multiplexação de Streams (Streams Multiplexing).\nComentário: A multiplexação permite enviar e receber múltiplos quadros de requisição e resposta simultaneamente em uma única conexão TCP.\nFonte: Programação WEB II-Desenvolvimento back-end, UA 2."
        },
        {
            "ua": "02", "obj": 2, "grau": "MÉDIA", "kw": "Modelos de Maturidade REST de Leonard Richardson (Níveis 0 a 3 - HATEOAS)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Durante a revisão da arquitetura de uma API corporativa, o arquiteto de software avalia o grau de aderência do sistema aos princípios REST utilizando o **Modelo de Maturidade de Richardson** (Níveis 0, 1, 2 e 3).\n\nA API atinge o nível máximo de maturidade (Nível 3) quando incorpora o conceito de HATEOAS (Hypermedia As The Engine Of Application State), inserindo hiperlinks navegáveis dentro das respostas JSON.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica a principal característica de uma API REST que atinge o Nível 3 de Maturidade de Richardson (HATEOAS):",
            "opt_a": "As respostas da API incluem hiperlinks de navegação dinâmicos que informam ao cliente quais ações e rotas podem ser executadas a partir do estado atual do recurso.", "opt_b": "A API utiliza apenas o método HTTP POST para todas as requisições em uma única URL.", "opt_c": "A API exige que todas as respostas sejam formatadas em XML desformatado.", "opt_d": "A API desativa o uso de códigos de status HTTP de erro.",
            "feedback": "A resposta certa é As respostas da API incluem hiperlinks de navegação dinâmicos que informam ao cliente quais ações e rotas podem ser executadas a partir do estado atual do recurso.\nComentário: O HATEOAS (Nível 3) insere hipermídia no payload de resposta, orientando o cliente sobre como navegar entre os recursos disponíveis sem acoplamento estático de URLs.\nFonte: Programação WEB II-Desenvolvimento back-end, UA 2."
        },
        {
            "ua": "05", "obj": 1, "grau": "DIFÍCIL", "kw": "Padrão Repository e Camada de Acesso a Dados (DAO / Active Record)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Para evitar que regras de acesso a banco de dados e consultas SQL fiquem espalhadas dentro dos controllers e serviços de negócio de um sistema web em Node.js/Java, a arquitetura implementa o padrão **Repository**.\n\nO repositório abstrai a camada de persistência em memória, fornecendo uma coleção emulada de objetos de domínio para a camada de serviços da aplicação.",
            "afirmativas": "Com base nos padrões de persistência de dados (Repository vs Active Record vs DAO), analise as afirmativas:\nI. O padrão Repository encapsula a lógica de acesso a dados e consultas, fornecendo uma interface orientada a objetos para o domínio.\nII. O padrão Active Record mistura regras de negócio e métodos de persistência diretamente dentro da própria classe da entidade de domínio.\nIII. O padrão Repository força os controllers HTTP a executarem instruções SQL brutas diretamente nas rotas da API.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II diferenciam com exatidão o desacoplamento do Repository e a abordagem acoplada do Active Record. A afirmativa III é falsa pois o objetivo do Repository é justamente evitar que os controllers conheçam SQL.\nFonte: Programação WEB II-Desenvolvimento back-end, UA 5."
        },
        {
            "ua": "05", "obj": 2, "grau": "DIFÍCIL", "kw": "Migrações de Banco de Dados (Database Migrations) e Versionamento de Schema",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Em uma equipe de desenvolvimento ágil composta por 10 programadores trabalhando em ambiente de Integração Contínua (CI/CD), alterações no esquema do banco de dados relacional (como criação de tabelas e adição de colunas) precisam ser propagadas com segurança.\n\nA equipe utiliza ferramentas de **Database Migrations** (como Flyway, Liquibase ou Prisma Migrations) para versionar o banco de dados via código.",
            "afirmativas": "Com base no uso de Database Migrations em desenvolvimento web, analise as afirmativas:\nI. Arquivos de migration contêm scripts ordenados por timestamp que aplicam alterações (`up`) ou revertem alterações (`down`) no esquema do banco de dados.\nII. Migrations garantem que todos os ambientes (Desenvolvimento, Staging e Produção) mantenham exatamente a mesma versão de esquema do banco de dados.\nIII. Ferramentas de migration exigem que o banco de dados seja completamente deletado e recriado a cada nova alteração de tabela.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com precisão o controle de versão incremental por scripts up/down e a sincronia entre ambientes. A afirmativa III é falsa pois migrations aplicam alterações incrementais mantendo os dados existentes.\nFonte: Programação WEB II-Desenvolvimento back-end, UA 5."
        },
        {
            "ua": "05", "obj": 3, "grau": "DIFÍCIL", "kw": "Padrão de Injeção de Dependência (Inversion of Control - IoC) em Frameworks Backend",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "No desenvolvimento de um backend modular em Java (Spring Boot) ou TypeScript (NestJS), os serviços de negócio recebem suas dependências (como instâncias de repositórios e serviços de envio de e-mail) através do construtor da classe.\n\nA aplicação adota os princípios de **Inversão de Controle** (IoC) e **Injeção de Dependência** (DI).",
            "afirmativas": "Com base nos conceitos de Injeção de Dependência e IoC, analise as afirmativas:\n\nI. A Injeção de Dependência passa a responsabilidade de instanciar e gerenciar o ciclo de vida dos objetos de serviço para o contêiner do framework, em vez de permitir que as classes criem suas próprias dependências com o operador `new`.\n\nPORQUE\n\nII. O desacoplamento fornecido pela Injeção de Dependência facilita a escrita de testes unitários automatizados, permitindo substituir dependências reais por objetos de teste (Mocks / Stubs) com facilidade.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A transferência da instanciação para o contêiner de IoC desonera a classe e facilita a substituição por Mocks em suítes de testes unitários.\nFonte: Programação WEB II-Desenvolvimento back-end, UA 5."
        }
    ],
    subfolder='AD'
)

# 13. Projeto de Redes de Computadores (UAs 4, 5)
create_exam(
    "Projetos de Redes de Computadores (seg)", "Projeto de Redes de Computadores", "AD Projeto de Redes de Computadores", "4; 5",
    [
        {
            "ua": "04", "obj": 1, "grau": "MÉDIA", "kw": "Identificação de Restrições Financeiras, Técnicas e Políticas em Projetos de Rede",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Na fase inicial de planejamento de um projeto de redes para uma instituição bancária pública, o projetista realiza o levantamento das restrições do projeto divididas em restrições financeiras, restrições tecnológicas e restrições políticas/regulatórias.\n\nEle identifica que a Lei de Licitações Públicas exige o uso de especificações abertas (não proprietárias) e que o orçamento limite de CAPEX para equipamentos é de R$ 2 milhões.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que classifica a exigência de cumprimento de normas de segurança bancária do Banco Central do Brasil em um projeto de redes:",
            "opt_a": "Restrição Política / Regulatória de Compliance.", "opt_b": "Restrição Física de Cabeamento.", "opt_c": "Restrição de Frequência de Rádio.", "opt_d": "Restrição de Marca de Switch.",
            "feedback": "A resposta certa é Restrição Política / Regulatória de Compliance.\nComentário: Normas legais, regulatórias do BACEN e leis de licitação constituem restrições políticas e de compliance do projeto de TI.\nFonte: Projeto de Redes de Computadores, UA 4."
        },
        {
            "ua": "04", "obj": 2, "grau": "MÉDIA", "kw": "Análise de Escalabilidade e Crescimento Futuro da Infraestrutura",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Um engenheiro projeta a rede local de um novo edifício corporativo que abrigará inicialmente 300 funcionários, mas com previsão de expansão para 800 colaboradores nos próximos 3 anos.\n\nPara garantir que a infraestrutura seja escalável sem exigir a substituição prematura dos equipamentos de núcleo e distribuição, ele aplica o princípio de **Design Modular e Escalabilidade**.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta uma decisão de projeto orientada à escalabilidade técnica da rede:",
            "opt_a": "Adotar switches de núcleo modulares com slots de expansão para novas placas de portas e fontes de alimentação redundantes.", "opt_b": "Utilizar cabos de par trançado Categoria 3 exclusivos para dados.", "opt_c": "Atribuir IPs estáticos manualmente para todos os 800 computadores.", "opt_d": "Eliminar o uso de VLANs na rede interna.",
            "feedback": "A resposta certa é Adotar switches de núcleo modulares com slots de expansão para novas placas de portas e fontes de alimentação redundantes.\nComentário: Equipamentos modulares permitem expandir a capacidade de portas e processamento apenas adicionando lâminas/módulos extras sem trocar o chassi.\nFonte: Projeto de Redes de Computadores, UA 4."
        },
        {
            "ua": "05", "obj": 1, "grau": "DIFÍCIL", "kw": "Projeto de Topologia de Rede de Borda (DMZ e Firewalls Perimetrais)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "No projeto da arquitetura de borda de internet de uma corporação, o projetista de segurança desenha uma Zona Desmilitarizada (**DMZ** - Demilitarized Zone) isolada por firewalls perimetrais.\n\nA DMZ abrigará os servidores públicos da empresa (servidor web, servidor DNS externo e gateway de e-mail), impedindo o acesso direto da internet à rede interna corporativa (Intranet).",
            "afirmativas": "Com base na arquitetura de rede com DMZ, analise as afirmativas:\nI. Servidores posicionados na DMZ são acessíveis publicamente pela internet, mas possuem acesso estritamente restrito e controlado à rede interna.\nII. A comprometimento de um servidor web posicionado na DMZ não garante ao atacante acesso direto e irrestrito aos bancos de dados da Intranet.\nIII. A DMZ é configurada colocando os servidores públicos dentro da mesma VLAN privada dos computadores dos diretores.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão a função de contensão de danos da DMZ. A afirmativa III é falsa pois a DMZ deve ficar em uma rede/VLAN isolada das estações internas.\nFonte: Projeto de Redes de Computadores, UA 5."
        },
        {
            "ua": "05", "obj": 2, "grau": "DIFÍCIL", "kw": "Redundância de Cabeamento de Backbone em Anel/Malha (Mesh Topology)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Para evitar um ponto único de falha (SPOF) na infraestrutura de cabeamento de backbone de fibra óptica que conecta 4 switches de distribuição em um Data Center, a equipe projeta uma topologia em **Malha Completa** (Full Mesh).\n\nCada switch de distribuição é conectado diretamente a todos os outros switches por links ópticos independentes.",
            "afirmativas": "Com base em topologias de cabeamento de backbone redundantes, analise as afirmativas:\nI. A topologia em Malha Completa com N nós exige um total de $N \\times (N - 1) / 2$ links físicos de conexão.\nII. Topologias em malha garantem que a ruptura acidental de um cabo óptico não interrompa a comunicação entre os nós remanescentes.\nIII. Uma topologia em Malha Completa exige a desativação permanente de todos os protocolos de proteção Spanning Tree.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com exatidão a fórmula de conexões da malha e a tolerância a falhas. A afirmativa III é falsa pois enlaces redundantes em malha exigem estritamente o STP/RSTP ativado para prevenir loops de camada 2.\nFonte: Projeto de Redes de Computadores, UA 5."
        },
        {
            "ua": "05", "obj": 3, "grau": "DIFÍCIL", "kw": "Dimensionamento da Camada de Acesso (Power over Ethernet - PoE / PoE+)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "No projeto da camada de acesso para um novo edifício de escritórios, o engenheiro de redes seleciona switches de acesso com suporte a tecnologia **Power over Ethernet** (**PoE** - IEEE 802.3af / **PoE+** - IEEE 802.3at).\n\nOs switches alimentarão 48 pontos de telefones IP, Access Points Wi-Fi 6 e câmeras de segurança IP sem necessidade de fontes de alimentação na tomada elétrica dos ambientes.",
            "afirmativas": "Com base no dimensionamento de switches PoE em projetos de rede, analise as afirmativas:\n\nI. O engenheiro deve calcular o Orçamento de Potência PoE Total (Power Budget em Watts) do switch para garantir que a soma das potências consumidas pelos dispositivos conectados não ultrapasse a capacidade máxima da fonte do switch.\n\nPORQUE\n\nII. O padrão PoE+ (802.3at) fornece até 30 Watts de potência por porta, sendo necessário para alimentar dispositivos de maior consumo como câmeras PTZ com aquecedor e Access Points Wi-Fi 6 de rádios múltiplos.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A maior demanda de potência dos dispositivos modernos (PoE+ 30W) obriga o correto dimensionamento do Power Budget total da fonte do switch.\nFonte: Projeto de Redes de Computadores, UA 5."
        }
    ],
    subfolder='AD'
)

# 14. Redes Convergentes (UAs 3, 7)
create_exam(
    "Redes Convergentes", "Redes Convergentes", "AD Redes Convergentes", "3; 7",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Códigos de Resposta SIP (1xx, 2xx, 4xx, 5xx)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em uma chamada de voz VoIP sinalizada pelo protocolo SIP, após a emissão da mensagem `INVITE` pelo telefone chamador, o servidor IP-PBX retorna respostas numéricas de status padronizadas baseadas na estrutura de códigos do protocolo HTTP.\n\nQuando o telefone chamado começa a tocar fisicamente na mesa do destinatário, o servidor envia uma resposta provisória da classe `1xx Informacional` para o chamador.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica o código de resposta SIP que informa que o telefone de destino está chamando (Ringing):",
            "opt_a": "180 Ringing.", "opt_b": "200 OK.", "opt_c": "404 Not Found.", "opt_d": "486 Busy Here.",
            "feedback": "A resposta certa é 180 Ringing.\nComentário: A mensagem SIP `180 Ringing` é a resposta informacional que avisa o chamador que o destino está chamando e gerando o tom de chamada.\nFonte: Redes Convergentes, UA 3."
        },
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Arquitetura de Gateways PSTN / E1 / FXS / FXO em Telefonia IP",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Para integrar uma nova central IP-PBX baseada em SIP às linhas analógicas e troncos digitais legados fornecidos pela operadora pública de telefonia (PSTN), o engenheiro de telecomunicações instala **Gateways de Voz** na infraestrutura.\n\nEle precisa selecionar os cartões de interface adequados para conectar aparelhos telefônicos analógicos comuns (porta FXS) e linhas telefônicas analógicas da operadora (porta FXO).",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta a função de uma porta de interface FXS (Foreign Exchange Station):",
            "opt_a": "Fornecer tom de discagem, tensão de bateria e sinal de campainha para conectar telefones analógicos comuns ou aparelhos de Fax.", "opt_b": "Conectar diretamente um tronco E1 de 30 canais digitais.", "opt_c": "Receber a linha telefônica vinda da tomada de parede da operadora pública.", "opt_d": "Converter tráfego de vídeo 4K em pacotes de rádio Wi-Fi.",
            "feedback": "A resposta certa é Fornecer tom de discagem, tensão de bateria e sinal de campainha para conectar telefones analógicos comuns ou aparelhos de Fax.\nComentário: Portas FXS emulam a tomada da central telefônica, fornecendo bateria (48V) e tom para aparelhos analógicos finais.\nFonte: Redes Convergentes, UA 3."
        },
        {
            "ua": "07", "obj": 1, "grau": "DIFÍCIL", "kw": "Avaliação da Qualidade do Som por Métricas Perceptivas (PESQ e POLQA)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Para automatizar a medição da qualidade de áudio em testes de bancada de codecs de voz VoIP sem depender de pesquisas de opinião humana (MOS subjetivo), o laboratório de engenharia utiliza algoritmos de avaliação perceptiva padronizados pela ITU-T.\n\nEles utilizam o algoritmo **PESQ** (Perceptual Evaluation of Speech Quality - ITU-T P.862) e seu sucessor **POLQA** (ITU-T P.863).",
            "afirmativas": "Com base nos algoritmos de avaliação de qualidade de voz PESQ e POLQA, analise as afirmativas:\nI. O PESQ compara o sinal de áudio original enviado com o sinal degradado recebido após o trânsito na rede de pacotes.\nII. O algoritmo calcula uma pontuação quantitativa correlacionada com a escala MOS (1 a 5).\nIII. O PESQ exige a avaliação manual de ouvintes humanos em uma sala acusticamente isolada.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com exatidão a comparação matemática de sinais do PESQ/POLQA para estimar o MOS. A afirmativa III é falsa pois o objetivo desses algoritmos é justamente automatizar o cálculo sem ouvintes humanos.\nFonte: Redes Convergentes, UA 7."
        },
        {
            "ua": "07", "obj": 2, "grau": "DIFÍCIL", "kw": "Perda de Pacotes (Packet Loss) e Técnicas de Compensação FEC (Forward Error Correction)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Em uma conexão de videoconferência via internet pública sujeira a 5% de perda aleatória de pacotes (Packet Loss), o áudio fica entrecortado devido ao descarte de quadros de voz.\n\nComo a retransmissão de pacotes perdidos via TCP introduziria latência inaceitável para a conversação em tempo real, os codecs avançados (como Opus ou G.729) utilizam técnicas de **Compensação por Ocultamento de Perda de Pacotes** (PLC) e **FEC** (Forward Error Correction).",
            "afirmativas": "Com base na mitigação de perda de pacotes em mídia tempo real, analise as afirmativas:\nI. A técnica de FEC (Forward Error Correction) envia informações redundantes de correção de erro juntas com o pacote primário, permitindo reconstruir pacotes perdidos sem retransmissão.\nII. A técnica de PLC (Packet Loss Concealment) sintetiza um trecho de áudio estimado para preencher a lacuna do pacote perdido baseado nas amostras imediatamente anteriores.\nIII. Retransmitir pacotes de áudio perdidos via TCP é a solução recomendada para chamadas de voz interativas de alta velocidade.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem corretamente as técnicas de FEC e PLC em codecs VoIP. A afirmativa III é falsa pois a retransmissão por TCP introduz latência incompatível com a conversação em tempo real.\nFonte: Redes Convergentes, UA 7."
        },
        {
            "ua": "07", "obj": 3, "grau": "DIFÍCIL", "kw": "Qualidade de Serviço para Vídeo Interativo (DSCP AF41/AF42 em DiffServ)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "No projeto de QoS da rede corporativa convergente, o tráfego de sessões de videoconferência telepresença é classificado no modelo DiffServ com valores de cabeçalho **DSCP AF41** (Assured Forwarding Class 4, Low Drop Probability).\n\nOs roteadores utilizam filas de enfileiramento com garantia de banda reservada (CBWFQ - Class-Based Weighted Fair Queueing) para proteger o tráfego de vídeo.",
            "afirmativas": "Com base nas classes de QoS para vídeo interativo em redes convergentes, analise as afirmativas:\n\nI. O tráfego de vídeo interativo exige alta largura de banda e baixa latência, sendo classificado na classe Assured Forwarding (AF4) para receber reserva de banda preferencial em relação ao tráfego de dados comum (Best-Effort).\n\nPORQUE\n\nII. Diferente do tráfego de voz (que é sensível primariamente ao jitter e usa a classe EF), o tráfego de vídeo consiste em rajadas de pacotes de grande tamanho que se beneficiam de filas de largura de banda garantida com descarte controlado.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. As características de rajada de dados do vídeo justificam o uso das classes Assured Forwarding (AF) com CBWFQ em vez de Expedited Forwarding (EF).\nFonte: Redes Convergentes, UA 7."
        }
    ],
    subfolder='AD'
)

print("Batch TG 4 concluído.")
