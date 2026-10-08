# -*- coding: utf-8 -*-
"""
Batch PS 1: Disciplinas 1 a 4 (Provas PS 2026-4 - Novos Objetivos e Contextualização ENADE > 7 linhas)
"""
from generate_full_batch import create_exam

# 1. Cabeamento estruturado II
create_exam(
    "Cabeamento estruturado II (seg)", "Cabeamento estruturado II", "PS Cabeamento estruturado II", "5; 6; 9; 10",
    [
        {
            "ua": "05", "obj": 2, "grau": "MÉDIA", "kw": "Cabeamento de Backbone e Fibras Ópticas OM3/OM4",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em um projeto de modernização do cabeamento de backbone de um campus universitário composto por 5 edifícios acadêmicos distantes 400 metros entre si, a equipe de engenharia precisa selecionar o meio físico de transmissão óptico para interligar as salas de telecomunicações dos prédios ao Data Center principal.\n\nO projeto especifica o suporte imediato a conexões de 10 Gbps (10GBASE-SR) com suporte a migração futura para 40 Gbps e 100 Gbps utilizando lasers VCSEL de 850 nm. De acordo com as normas ANSI/TIA-568.3-D e ISO/IEC 11801, a escolha do tipo de fibra óptica multimodo otimizada por laser é determinante para mitigar a dispersão modal e garantir a largura de banda passante em comprimentos de onda de 850 nm.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica a categoria de fibra óptica multimodo com núcleo de 50 µm otimizada para laser que atende às especificações do projeto para 10 Gbps em 400 metros:",
            "opt_a": "OM4.", "opt_b": "OM1.", "opt_c": "OM2.", "opt_d": "OS1.",
            "feedback": "A resposta certa é OM4.\nComentário: A fibra multimodo OM4 possui largura de banda modal de 4700 MHz·km a 850 nm, suportando conexões 10GBASE-SR até 550 metros, enquanto a OM3 limita-se a 300 metros.\nFonte: Cabeamento Estruturado II, UA 5."
        },
        {
            "ua": "06", "obj": 3, "grau": "MÉDIA", "kw": "Certificação de Redes com OTDR e Margem de Headroom",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Durante o processo de auditagem de comissionamento do cabeamento de par trançado Categoria 6A em um Data Center corporativo, a equipe técnica realiza testes de certificação de campo utilizando um certificador de redes calibrado.\n\nAlém de verificar parâmetros como comprimento, atraso de propagação e atenuação por inserção, o relatório do equipamento exibe o valor de Headroom em decibéis (dB) para cada parâmetro testado. O analista precisa interpretar o significado prático desse indicador de margem de desempenho para a homologação da garantia de 25 anos do fabricante.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta o significado correto do indicador Headroom nos relatórios de certificação de cabeamento estruturado:",
            "opt_a": "A diferença positiva em decibéis (dB) entre a medida real obtida no link de teste e o limite mínimo exigido pela norma técnica.", "opt_b": "A quantidade de metros excedentes de cabo instalados acima do limite de 90 metros.", "opt_c": "O percentual de perda de pacotes aceitável durante a transmissão de dados.", "opt_d": "A taxa máxima de consumo elétrico das interfaces dos switches de acesso.",
            "feedback": "A resposta certa é A diferença positiva em decibéis (dB) entre a medida real obtida no link de teste e o limite mínimo exigido pela norma técnica.\nComentário: O Headroom representa a margem de segurança do link; quanto maior o valor em dB em relação ao limite normativo, maior a qualidade e resiliência da instalação.\nFonte: Cabeamento Estruturado II, UA 6."
        },
        {
            "ua": "09", "obj": 1, "grau": "DIFÍCIL", "kw": "Fusão de Precisão e Conectores Ópticos Multifibra MPO/MTP",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Para suportar a alta densidade de conexões de 40 Gbps e 100 Gbps nos gabinetes de distribuição principal (MDA) de um Data Center bancário, os projetistas adotaram troncos de cabos ópticos pré-conectorizados baseados na tecnologia de conectores multifibra MPO/MTP (Multi-fiber Push-On).\n\nA equipe de instalação realiza a conectorização nos cassetes de distribuição e executa testes de polaridade (Tipos A, B e C) e inspeção por microscópio óptico para garantir que as superfícies das ponteiras cerâmicas estejam isentas de sujeira e riscos.",
            "afirmativas": "Com base na tecnologia de conectores ópticos MPO/MTP e polaridade, analise as afirmativas:\nI. Conectores MPO/MTP agregam 12 ou 24 fibras ópticas em uma única ponteira retangular de alta densidade.\nII. A verificação de polaridade garante que a fibra de transmissão (Tx) de um transceptor na ponta A conecte-se corretamente à fibra de recepção (Rx) na ponta B.\nIII. O conector MPO elimina a necessidade de alinhamento físico por pinos guia em conexões macho-fêmea.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão a densidade e a função da polaridade em conectores MPO/MTP. A afirmativa III é falsa pois conectores MPO exigem pinos guia para o alinhamento de alta precisão entre os conectores macho e fêmea.\nFonte: Cabeamento Estruturado II, UA 9."
        },
        {
            "ua": "10", "obj": 2, "grau": "DIFÍCIL", "kw": "Redundância de Caminhos em Data Centers (TIA-942 Tier III/IV)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Um Data Center governamental de alta segurança foi projetado para atender aos requisitos de resiliência da norma ANSI/TIA-942 no nível Tier III (Manutenível Simultaneamente), exigindo que qualquer manutenção preventiva em equipamentos ou caminhos de cabos possa ser realizada sem interromper os serviços de TI.\n\nO projeto físico de cabeamento estruturado exige a criação de duas salas de entrada de telecomunicações (Entrance Rooms - ER1 e ER2) geograficamente opostas no terreno e caminhos de leitos de cabos totalmente redundantes e isolados.",
            "afirmativas": "Com base nas diretrizes de redundância de cabeamento da norma ANSI/TIA-942, analise as afirmativas:\nI. A redundância de infraestrutura exige duas rotas físicas de leitos de cabos totalmente separadas para evitar que um único incêndio ou colisão física corte ambos os backbones.\nII. Um Data Center Tier III admite paralisações planejadas da rede de cabeamento de até 48 horas anuais para manutenção de rotina.\nIII. As salas de entrada de telecomunicações redundantes devem conectar-se aos operadores de serviços por acessos físicos independentes.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e III, apenas.", "opt_b": "I e II, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e III, apenas.\nComentário: As afirmativas I e III refletem os requisitos da TIA-942 Tier III para caminhos e entradas redundantes. A afirmativa II é falsa pois a classificação Tier III exige disponibilidade de 99.982%, permitindo no máximo 1.6 horas de indisponibilidade não planejada por ano, sem paralisações para manutenção.\nFonte: Cabeamento Estruturado II, UA 10."
        },
        {
            "ua": "10", "obj": 3, "grau": "DIFÍCIL", "kw": "Sistema de Proteção contra Surtos e Equipotencialização (ANSI/TIA-607)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Durante uma tempestade com intensa incidência de descargas elétricas atmosféricas (rayos), um Data Center corporativo teve várias portas de switches de borda queimadas nas tomadas de comunicação de estações de trabalho de um andar específico.\n\nAo inspecionar a instalação de aterramento segundo a norma ANSI/TIA-607-D, o perito identificou que a Barra de Aterramento de Telecomunicações (TGB) daquele andar estava desconectada da malha principal de aterramento elétrico do edifício, criando uma diferença de potencial elétrico (DDP) induzida durante a descarga.",
            "afirmativas": "Com base nos conceitos da norma ANSI/TIA-607-D de aterramento em telecomunicações, analise as afirmativas:\n\nI. Todos os elementos metálicos não energizados do sistema de cabeamento (como racks, calhas e malhas de blindagem de cabos FTP) devem ser equipotencializados à mesma malha de aterramento elétrico da edificação.\n\nPORQUE\n\nII. A equipotencialização elimina diferenças de potencial transitórias causadas por surtos elétricos, evitando o surgimento de correntes de laço de terra (Ground Loops) que destroem equipamentos e geram ruído nas transmissões de dados.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A integração de todos os elementos metálicos à mesma barra de aterramento impede a formação de potenciais destrutivos induzidos por descargas.\nFonte: Cabeamento Estruturado II, UA 10."
        }
    ],
    subfolder='PS'
)

# 2. Compiladores
create_exam(
    "Compiladores", "Compiladores", "PS Compiladores", "2; 3; 5; 8",
    [
        {
            "ua": "02", "obj": 2, "grau": "MÉDIA", "kw": "Autômatos Finitos Determinísticos (AFD) e Expressões Regulares",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "No desenvolvimento do analisador léxico (Scanner) de um compilador para uma linguagem de programação orientada a objetos, a equipe precisa construir o gerador de tokens para identificar identificadores válidos de variáveis e métodos.\n\nA especificação da linguagem estabelece que um identificador deve começar obrigatoriamente por uma letra (maiúscula ou minúscula) ou sublinhado (`_`), seguido por qualquer sequência de letras, dígitos numéricos ou sublinhados. O analisador léxico converte a expressão regular correspondente em um Autômato Finito Determinístico (AFD) para processar o fluxo de caracteres de entrada.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta a propriedade fundamental de um Autômato Finito Determinístico (AFD) utilizado na análise léxica:",
            "opt_a": "Para cada estado e cada caractere de entrada, existe no máximo uma transição de estado definida, sem transições vazias (transições ε).", "opt_b": "Múltiplas transições de estado podem ser executadas simultaneamente para o mesmo caractere de entrada.", "opt_c": "O automato necessita de uma pilha de memória infinita para contar os caracteres lidos.", "opt_d": "A análise léxica com AFD é executada exclusivamente durante o tempo de execução (Runtime) da aplicação.",
            "feedback": "A resposta certa é Para cada estado e cada caractere de entrada, existe no máximo uma transição de estado definida, sem transições vazias (transições ε).\nComentário: AFDs garantem determinismo computacional (tempo linear O(n)), onde cada símbolo direciona a exatamente um estado seguinte sem ambiguidade.\nFonte: Compiladores, UA 2."
        },
        {
            "ua": "03", "obj": 3, "grau": "MÉDIA", "kw": "Análise Sintática Preditiva LL(1) e Tabelas de Parsing",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Um engenheiro de software constrói um analisador sintático preditivo descendente do tipo LL(1) para verificar a correção estrutural dos programas em relação à gramática livre de contexto da linguagem.\n\nPara que a gramática seja classificada como LL(1) e possa ser analisada sem retrocesso (backtracking) utilizando apenas 1 token de consulta futura (lookahead), o engenheiro deve eliminar previamente a recursão à esquerda das regras de produção e aplicar o fatoramento à esquerda.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o problema sintático gerado pela presença de recursão à esquerda direta (ex: `A -> A α | β`) em um analisador sintático preditivo descendente:",
            "opt_a": "Entrada em um loop infinito de chamadas recursivas antes de consumir qualquer token da entrada.", "opt_b": "Impossibilidade de gerar código objeto binário executável.", "opt_c": "Erro de estouro de memória no banco de dados do compilador.", "opt_d": "Fusão indevida de tokens numéricos com operadores lógicos.",
            "feedback": "A resposta certa é Entrada em um loop infinito de chamadas recursivas antes de consumir qualquer token da entrada.\nComentário: Analisadores descendentes tentam expandir o não-terminal mais à esquerda; se houver recursão à esquerda, a função chama a si mesma indefinidamente.\nFonte: Compiladores, UA 3."
        },
        {
            "ua": "05", "obj": 1, "grau": "DIFÍCIL", "kw": "Gramáticas de Atributos e Análise Semântica",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Durante a fase de análise semântica de um compilador C-like, o analisador utiliza Gramáticas de Atributos para verificar a compatibilidade de tipos em expressões aritméticas e atribuições (ex: verificar se um valor do tipo `float` está sendo atribuído a um ponteiro `int*`).\n\nOs atributos associados aos nós da árvore de sintaxe abstrata (AST) são divididos em Atributos Sintetizados e Atributos Herdados, governando o fluxo de avaliação das regras semânticas durante a travessia da árvore.",
            "afirmativas": "Com base nas Gramáticas de Atributos e Análise Semântica, analise as afirmativas:\nI. Atributos Sintetizados são calculados para um nó pai a partir dos valores dos atributos dos seus nós filhos na AST.\nII. Atributos Herdados passam informações do nó pai ou de nós irmãos para os nós filhos na AST (fluxo top-down ou horizontal).\nIII. A verificação semântica ocorre antes da fase de análise léxica para descartar palavras reservadas.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão os fluxos de atributos sintetizados e herdados. A afirmativa III é falsa pois a análise semântica ocorre APÓS a análise sintática.\nFonte: Compiladores, UA 5."
        },
        {
            "ua": "08", "obj": 2, "grau": "DIFÍCIL", "kw": "Geração de Código Intermediário em Notação de Três Endereços",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Um compilador otimizador traduz a árvore sintática de expressões matemáticas complexas para Código de Três Endereços (TAC - Three-Address Code), uma representação intermediária independente de máquina.\n\nNa notação TAC, cada instrução possui no máximo três operandos e um único operador (ex: `t1 = a * b`; `t2 = t1 + c`), simplificando a posterior alocação de registradores e otimização de instruções pela arquitetura de destino.",
            "afirmativas": "Com base na representação de código em Notação de Três Endereços (TAC), analise as afirmativas:\nI. Instruções TAC abstraem os registradores reais da CPU, utilizando um número ilimitado de variáveis temporárias (`t1, t2, ...`).\nII. Estruturas de controle como `if-else` e `while` são traduzidas em TAC utilizando saltos condicionais (`ifFalse t1 goto L1`) e rótulos (labels).\nIII. O Código de Três Endereços vincula o código intermediário estritamente aos registradores da arquitetura x86-64.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II apresentam com precisão a estrutura e o desvio condicional em TAC. A afirmativa III é falsa pois o TAC é uma representação independente de arquitetura física.\nFonte: Compiladores, UA 8."
        },
        {
            "ua": "08", "obj": 3, "grau": "DIFÍCIL", "kw": "Otimização de Código e Eliminação de Subexpressões Comuns",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Durante a fase de otimização de código intermediário de um compilador para alto desempenho em laços de repetição (loops), o módulo otimizador identifica a presença de cálculos idênticos repetidos dentro do corpo do laço (ex: `x = a + b; ... y = a + b;`).\n\nO otimizador aplica a técnica de Eliminação de Subexpressões Comuns (Common Subexpression Elimination - CSE) para reaproveitar o resultado previamente computado em uma variável temporária.",
            "afirmativas": "Com base nas técnicas de Otimização de Código em compiladores, analise as afirmativas:\n\nI. A Eliminação de Subexpressões Comuns substitui a reavaliação de uma expressão já calculada pelo valor armazenado em uma temporária, desde que os operandos não tenham sido modificados no intervalo.\n\nPORQUE\n\nII. Reduzir o número de instruções aritméticas redundantes diminui a quantidade de ciclos de clock da CPU necessários para executar o bloco de código otimizado.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. Evitar recálculos desnecessários economiza instruções da CPU e melhora o tempo de execução do programa.\nFonte: Compiladores, UA 8."
        }
    ],
    subfolder='PS'
)

# 3. Desenvolvimento de Dispositivos Móveis
create_exam(
    "Desenvolvimento de Dispositivos Móveis", "Desenvolvimento de Dispositivos Móveis", "PS Desenvolvimento de Dispositivos Móveis", "3; 4; 8; 10",
    [
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Ciclo de Vida de Activities e Fragments em Android",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Um desenvolvedor Android cria um aplicativo móvel de reprodução de vídeo. Durante o uso, o usuário recebe uma ligação telefônica, fazendo com que o aplicativo seja colocado em segundo plano (background) e a tela de atendimento ocupe a interface do dispositivo.\n\nPara evitar o vazamento de memória e pausar a execução do vídeo e a liberação da câmera/reprodução de áudio de forma adequada, o desenvolvedor implementa os métodos de retorno do ciclo de vida da `Activity`.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica o método do ciclo de vida chamado imediatamente quando a Activity perde o foco visível parcial ou total para outra aplicação:",
            "opt_a": "onPause().", "opt_b": "onDestroy().", "opt_c": "onCreate().", "opt_d": "onRestart().",
            "feedback": "A resposta certa é onPause().\nComentário: O método `onPause()` é o primeiro indicador de que o usuário está deixando a Activity (embora ela ainda possa estar parcialmente visível), sendo o local correto para pausar vídeos e liberar recursos pesados.\nFonte: Desenvolvimento de Dispositivos Móveis, UA 3."
        },
        {
            "ua": "04", "obj": 3, "grau": "MÉDIA", "kw": "Gerenciamento de Estado com Redux/Provider no Flutter/React Native",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Em um aplicativo de e-commerce desenvolvido com React Native ou Flutter, múltiplos componentes visuais em telas distintas (como o ícone do carrinho no cabeçalho, a tela de checkout e a lista de produtos) precisam acessar e modificar o estado global do carrinho de compras.\n\nPara evitar a passagem excessiva e frágil de dados via propriedades entre componentes pais e filhos (Prop Drilling), a arquitetura adotou um padrão de Gerenciamento de Estado Centralizado (como Redux ou Provider/Bloc).",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica a principal vantagem da arquitetura de fluxo de dados unidirecional (Unidirectional Data Flow) no gerenciamento de estado global móvel:",
            "opt_a": "Previsibilidade do estado da aplicação, facilitando a depuração e o rastreamento de mutações através de ações e reducers puros.", "opt_b": "Eliminação da necessidade de compilação de código nativo para iOS e Android.", "opt_c": "Criptografia automática de todos os dados salvos na memória RAM.", "opt_d": "Aumento da velocidade de download do aplicativo nas lojas de apps.",
            "feedback": "A resposta certa é Previsibilidade do estado da aplicação, facilitando a depuração e o rastreamento de mutações através de ações e reducers puros.\nComentário: O fluxo de dados unidirecional garante que o estado seja imutável e atualizado apenas por dispatch de ações explícitas, prevenindo efeitos colaterais imprevistos.\nFonte: Desenvolvimento de Dispositivos Móveis, UA 4."
        },
        {
            "ua": "08", "obj": 1, "grau": "DIFÍCIL", "kw": "Persistência de Dados Local com SQLite/Room",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um aplicativo de anotações offline para smartphones precisa salvar notas, categorias e datas no armazenamento interno do dispositivo móvel sem depender de conexão contínua à internet.\n\nA equipe de desenvolvimento utiliza a biblioteca de abstração Room (ORM oficial do Android sobre SQLite), definindo Entidades (`@Entity`), Objetos de Acesso a Dados (`@Dao`) e o banco de dados (`@Database`).",
            "afirmativas": "Com base na persistência de dados local com Room/SQLite em aplicativos móveis, analise as afirmativas:\nI. A anotação `@Dao` define a interface contendo os métodos de consulta SQL (`@Query`, `@Insert`, `@Delete`) para manipular as entidades do banco de dados.\nII. A execução de consultas síncronas pesadas ao banco de dados Room diretamente na Thread Principal de UI (Main Thread) é permitida por padrão em produção.\nIII. A biblioteca Room realiza a verificação de erros de sintaxe das consultas SQL em tempo de compilação.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e III, apenas.", "opt_b": "I e II, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e III, apenas.\nComentário: As afirmativas I e III são corretas. DAOs contêm as rotinas de banco e o Room valida SQL em tempo de compilação. A afirmativa II é falsa pois o Android lança exceção se consultas Room forem executadas na Main Thread para evitar congelamento da tela (ANR).\nFonte: Desenvolvimento de Dispositivos Móveis, UA 8."
        },
        {
            "ua": "10", "obj": 2, "grau": "DIFÍCIL", "kw": "Consumo de APIs REST Assíncronas com Retrofit/Axios e Promises",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Para exibir a previsão do tempo e índices de qualidade do ar atualizados em tempo real, um aplicativo móvel efetua chamadas assíncronas HTTP JSON para uma API REST externa utilizando bibliotecas como Retrofit em Kotlin ou Axios/Fetch em JavaScript.\n\nPara evitar o bloqueio da interface gráfica (UI Freeze) durante a aguardada resposta do servidor web em redes móveis de alta latência (3G/4G), a aplicação adota programação assíncrona baseada em Corrotinas (`async/await`) ou `Promises`.",
            "afirmativas": "Com base no consumo assíncrono de APIs em dispositivos móveis, analise as afirmativas:\nI. Chamadas HTTP assíncronas executam a requisição em threads secundárias de I/O, retornando a resposta para a thread principal atualizar a interface de usuário.\nII. O uso do padrão `async/await` simplifica o código assíncrono, permitindo tratar respostas e erros com estruturas `try/catch` convencionais.\nIII. Requisições assíncronas garantem que a resposta da API HTTP chegue instantaneamente em 0 milissegundos independente do estado da rede.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II descrevem perfeitamente o funcionamento do I/O assíncrono e da sintaxe async/await. A afirmativa III é falsa pois latências físicas de rede continuarão existindo.\nFonte: Desenvolvimento de Dispositivos Móveis, UA 10."
        },
        {
            "ua": "10", "obj": 3, "grau": "DIFÍCIL", "kw": "Publicação e Permissões em Tempo de Execução (Runtime Permissions)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Um aplicativo móvel de entrega de comida solicita acesso à localização exata por GPS e à câmera do smartphone do usuário durante o primeiro uso da funcionalidade de rastreamento do entregador.\n\nA partir das versões modernas dos sistemas operacionais móveis (Android 6.0+ e iOS), a solicitação de permissões perigosas migrou da mera declaração estática na instalação para a exigência de solicitação dinâmica de Permissões em Tempo de Execução (Runtime Permissions).",
            "afirmativas": "Com base no modelo de segurança de permissões móveis, analise as afirmativas:\n\nI. O aplicativo deve solicitar explicitamente o consentimento do usuário em tempo de execução antes de acessar recursos sensíveis do hardware (como GPS, Câmera e Microfone), tratando graciosamente a eventual negação do acesso.\n\nPORQUE\n\nII. A permissão em tempo de execução garante ao usuário maior controle sobre sua privacidade, impedindo que aplicativos leiam dados de localização em segundo plano sem transparência ou justificativa funcional.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A exigência de permissões dinâmicas fundamenta-se na proteção da privacidade do usuário contra monitoramento indevido.\nFonte: Desenvolvimento de Dispositivos Móveis, UA 10."
        }
    ],
    subfolder='PS'
)

# 4. Estrutura de dados
create_exam(
    "Estrutura de dados(seg)", "Estrutura de Dados", "PS Estrutura de dados", "3; 4; 6; 10",
    [
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Filas de Prioridade e Heaps Binários (Min-Heap / Max-Heap)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "No desenvolvimento do módulo de triagem do sistema de emergência de um hospital pronto-socorro, os pacientes recebem senhas de atendimento classificadas por gravidade médica (Vermelho, Amarelo, Verde). O sistema deve atender sempre o paciente de maior prioridade disponível no momento da chamada.\n\nPara implementar essa estrutura de dados com eficiência de inserção e remoção em tempo logarítmico O(log n), o engenheiro de software utiliza uma Fila de Prioridade estruturada como um Max-Heap Binário armazenado em um vetor (array).",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta a propriedade estrutural fundamental que caracteriza um Max-Heap Binário:",
            "opt_a": "O valor de cada nó pai é sempre maior ou igual aos valores contidos em seus nós filhos.", "opt_b": "O valor do nó raiz é sempre o menor elemento contido na árvore.", "opt_c": "Todos os nós da árvore possuem obrigatoriamente três nós filhos.", "opt_d": "Elementos são removidos estritamente na ordem LIFO (Last-In, First-Out).",
            "feedback": "A resposta certa é O valor de cada nó pai é sempre maior ou igual aos valores contidos em seus nós filhos.\nComentário: A propriedade do Max-Heap garante que a raiz contenha sempre o maior valor (maior prioridade), permitindo acesso O(1) ao topo e remoção/reorganização em O(log n).\nFonte: Estrutura de Dados, UA 3."
        },
        {
            "ua": "04", "obj": 3, "grau": "MÉDIA", "kw": "Algoritmos de Ordenação Eficientes (QuickSort vs MergeSort)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Uma plataforma de análise de grandes volumes de dados (Big Data) precisa ordenar um vetor contendo 10 milhões de registros de transações de cartão de crédito. O arquiteto de software analisa a complexidade assintótica de tempo e espaço dos algoritmos de ordenação por Divisão e Conquista: MergeSort e QuickSort.\n\nO requisito do sistema exige estabilidade de ordenação (preservação da ordem relativa de elementos com chaves iguais) e garantia de tempo de execução O(n log n) mesmo no pior caso de entrada de dados.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o algoritmo de ordenação que garante complexidade O(n log n) no pior caso e estabilidade de chave:",
            "opt_a": "MergeSort.", "opt_b": "QuickSort.", "opt_c": "BubbleSort.", "opt_d": "SelectionSort.",
            "feedback": "A resposta certa é MergeSort.\nComentário: O MergeSort divide o vetor sucessivamente ao meio e combina as partes ordenadamente, garantindo O(n log n) no pior caso e preservando a estabilidade dos registros.\nFonte: Estrutura de Dados, UA 4."
        },
        {
            "ua": "06", "obj": 1, "grau": "DIFÍCIL", "kw": "Árvores de Busca Balanceadas (Árvores AVL)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Para evitar a degradação do tempo de busca para O(n) que ocorre em Árvores Binárias de Busca (BST) comuns quando dados são inseridos em ordem sequencial crescente, um desenvolvedor utiliza uma Árvore AVL de busca auto-balanceada.\n\nA Árvore AVL calcula o Fator de Balanceamento (FB = altura_esquerda - altura_direita) de cada nó a cada inserção ou remoção, aplicando rotações simples ou duplas (à esquerda ou à direita) sempre que |FB| > 1.",
            "afirmativas": "Com base no funcionamento de Árvores AVL, analise as afirmativas:\nI. O Fator de Balanceamento de qualquer nó em uma Árvore AVL válida deve pertencer estritamente ao conjunto {-1, 0, +1}.\nII. Rotações em Árvores AVL reajustam a altura da árvore mantendo a propriedade de ordenação binária de busca em tempo O(1).\nIII. Árvores AVL possuem tempo de busca de pior caso O(n²) para chaves previamente ordenadas.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão o fator de balanceamento e a eficiência das rotações locais. A afirmativa III é falsa pois o balanceamento estrito garante busca O(log n) no pior caso.\nFonte: Estrutura de Dados, UA 6."
        },
        {
            "ua": "10", "obj": 2, "grau": "DIFÍCIL", "kw": "Tabelas Hash e Tratamento de Colisões por Encadeamento",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Um mecanismo de busca em memória utiliza uma Tabela Hash (Hash Table) com 1.000 posições (buckets) para armazenar palavras e seus significados. A função hash mapeia uma chave textual em um índice inteiro através da operação de resto da divisão (`hash(chave) % 1000`).\n\nQuando duas chaves distintas produzem exatamente o mesmo índice calculado (colisão hash), o sistema utiliza a técnica de Tratamento de Colisões por Encadeamento Separado (Separate Chaining), mantendo uma Lista Encadeada em cada bucket.",
            "afirmativas": "Com base em Tabelas Hash e tratamento de colisões, analise as afirmativas:\nI. O tratamento por encadeamento armazena elementos colididos em uma lista encadeada alocada no nó correspondente da tabela.\nII. Se a função hash for ruim e mapear todas as n chaves para o mesmo bucket, a complexidade de busca degrada para O(n).\nIII. O Fator de Carga (Load Factor) de uma tabela hash com encadeamento nunca pode superar o valor 1.0.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II descrevem perfeitamente o encadeamento e a degradação em pior caso. A afirmativa III é falsa pois no encadeamento o número de elementos pode ser muito maior que o número de buckets (fator de carga > 1.0).\nFonte: Estrutura de Dados, UA 10."
        },
        {
            "ua": "10", "obj": 3, "grau": "DIFÍCIL", "kw": "Grafos: Algoritmo de Dijkstra para Caminho Mínimo",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Um aplicativo de navegação GPS calcula a rota mais rápida entre a posição atual do motorista e o destino desejado em uma malha viária urbana representada como um Grafo Ponderado Direcionado, onde os vértices representam cruzamentos e as arestas representam ruas com pesos baseados na distância e tempo de tráfego.\n\nPara determinar o caminho de custo mínimo originado de um nó fonte, o sistema utiliza o Algoritmo de Dijkstra com fila de prioridades.",
            "afirmativas": "Com base no Algoritmo de Dijkstra em estruturas de dados de grafos, analise as afirmativas:\n\nI. O Algoritmo de Dijkstra calcula iterativamente o menor caminho de um nó de origem a todos os demais vértices do grafo, desde que todas as arestas possuam pesos não negativos (pesos ≥ 0).\n\nPORQUE\n\nII. A presença de arestas com pesos negativos pode fazer com que o algoritmo de Dijkstra finalize antecipadamente a distância de um vértice antes de avaliar um caminho indireto com custo total menor, exigindo o uso do algoritmo de Bellman-Ford.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A premissa de gulosidade (greedy) de Dijkstra falha em arcos negativos, justificando a restrição de pesos não negativos.\nFonte: Estrutura de Dados, UA 10."
        }
    ],
    subfolder='PS'
)

print("Batch PS 1 concluído.")
