# -*- coding: utf-8 -*-
"""
Batch 1: Disciplinas 1 a 4 (Versão ENADE Expandida - Caso Prático Robusto > 7 linhas)
"""
from generate_full_batch import create_exam

# 1. Cabeamento estruturado II
create_exam(
    "Cabeamento estruturado II (seg)", "Cabeamento estruturado II", "AI Cabeamento estruturado II", "5; 6; 9; 10",
    [
        {
            "ua": "05", "obj": 1, "grau": "MÉDIA", "kw": "Norma ANSI/TIA-568 e Categorias de Cabos",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em um projeto de modernização da infraestrutura de rede de uma instituição financeira de grande porte, a equipe de engenharia de redes foi encarregada de projetar a nova Sala de Equipamentos (ER) e o cabeamento de backbone para interligar os servidores de missão crítica instalados no Data Center corporativo aos switches do núcleo da rede.\n\nO projeto estabelece a exigência rigorosa de suporte a taxas de transmissão de 10 Gbps (10GBASE-T) em links de até 100 metros de extensão total, operando em frequências de amostragem de até 500 MHz para mitigar os efeitos severos de diafonia alienígena (Alien Crosstalk - ANEXT) causados pela alta densidade de cabos dispostos em calhas suspensas. Além disso, o sistema precisa atender estritamente aos requisitos das normas internacionais ANSI/TIA-568.2-D e ISO/IEC 11801 para subsistemas de cabeamento estruturado de par trançado blindado.",
            "afirmativas": "",
            "comando_text": "Considerando a classificação das normas internacionais de cabeamento estruturado e o desempenho de transmissão exigido para redes de alta velocidade, assinale a alternativa que indica a categoria de cabo de par trançado de cobre que atende de forma exata às especificações para 10GBASE-T a 500 MHz:",
            "opt_a": "Categoria 6A (Cat6A / Classe EA).", "opt_b": "Categoria 5e (Cat5e / Classe D).", "opt_c": "Categoria 3 (Cat3 / Classe C).", "opt_d": "Categoria 5 (Cat5 / Classe D).",
            "feedback": "A resposta certa é Categoria 6A (Cat6A / Classe EA).\nComentário: A norma ANSI/TIA-568.2-D especifica que a Categoria 6A opera em frequências de até 500 MHz e suporta a aplicação 10GBASE-T na distância máxima do canal de 100 metros, eliminando os problemas de Alien Crosstalk (ANEXT).\nFonte: Cabeamento Estruturado II, UA 5."
        },
        {
            "ua": "06", "obj": 2, "grau": "MÉDIA", "kw": "Certificação de Redes de Cobre e Parâmetros NEXT/FEXT",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Durante o processo de auditagem e comissionamento final do cabeamento estruturado de um edifício comercial recém-construído de 12 andares, um analista técnico utilizou um certificador de rede de campo para auditar todos os links permanentes de cobre da Categoria 6A entre a Sala de Telecomunicações (TR) e as tomadas de telecomunicações (TO) das estações de trabalho.\n\nDurante a execução dos auto-testes de certificação, o equipamento acusou repetidas falhas por rejeição no parâmetro de Diafonia no Endereço Próximo (NEXT - Near-End Crosstalk) especificamente nas extremidades onde os conectores fêmea RJ-45 (Keystones) foram montados pelos instaladores. Ao inspecionar fisicamente a conectorização dos pares nos blocos de engate rápido IDC das tomadas, o auditor observou que a capa externa de PVC dos cabos havia sido removida em cerca de 5 cm e os pares trançados de cobre foram totalmente desenrolados e alinhados para facilitar a fixação dos fios.",
            "afirmativas": "",
            "comando_text": "Com base nas normas ANSI/TIA-568 e nas boas práticas de engenharia de montagem de conectores de cabeamento estruturado, assinale a alternativa que apresenta a causa primária responsável pelo alto nível de ruído por NEXT identificado nas tomadas:",
            "opt_a": "O destrançamento excessivo dos pares de fios no momento da montagem no conector, violando o limite máximo de 13 mm recomendado pelas normas.", "opt_b": "O uso de patch cords de manobra de cobre com comprimento inferior a 0,5 metros na conexão das estações.", "opt_c": "A instalação dos cabos de dados de par trançado em canaletas exclusivas sem a presença de cabos de energia elétrica.", "opt_d": "A utilização de tomadas de telecomunicações RJ-45 de engate rápido com contatos banhados a ouro no bloco IDC.",
            "feedback": "A resposta certa é O destrançamento excessivo dos pares de fios no momento da montagem no conector, violando o limite máximo de 13 mm recomendado pelas normas.\nComentário: O destrançamento dos pares acima do limite normativo (máximo 13 mm para Cat6/6A) expõe os condutores paralelos ao acoplamento eletromagnético mútuo de alta frequência, elevando drasticamente a diafonia (NEXT).\nFonte: Cabeamento Estruturado II, UA 6."
        },
        {
            "ua": "09", "obj": 3, "grau": "DIFÍCIL", "kw": "Redes de Fibras Ópticas e Emendas por Fusão",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Uma concessionária de telecomunicações está implantando um tronco de backbone óptico subterrâneo com extensão de 15 km para conectar o ponto de presença (PoP) central à central telefônica do distrito industrial. O projeto especifica a utilização de um cabo óptico autossustentado contendo fibras ópticas monomodo (SMF G.652.D) conectorizadas em distribuidores internos ópticos (DIO) nas duas pontas.\n\nDurante a fase de instalação, a equipe de campo precisou realizar diversas emendas ópticas por fusão em caixas de emenda herméticas ao longo do trajeto. Para validar a qualidade das fusões e certificar a atenução total do enlace, os engenheiros utilizaram um máquina de fusão por alinhamento do núcleo a laser e um Refletômetro Óptico no Domínio do Tempo (OTDR) operando nos comprimentos de onda de 1310 nm e 1550 nm.",
            "afirmativas": "Com base nas técnicas de preparação de fibras, emendas por fusão e interpretação dos traçados de refletometria (OTDR), analise as afirmativas:\nI. A realização de uma fusão de alta qualidade em fibras monomodo exige o decapamento térmico da acrilato e a clivagem da face da fibra em ângulo reto (90°) para minimizar a perda por inserção e a reflexão de retorno (ORL).\nII. A substituição das fibras monomodo por fibras multimodo (OM4) nesse enlace de 15 km é recomendada para eliminar a dispersão modal e reduzir a atenuação óptica total do canal.\nIII. No gráfico do traçado do OTDR, um evento de fusão bem executado é representado visualmente por um degrau atenuativo localizado sem a presença de pico reflexivo.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e III, apenas.", "opt_b": "I e II, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e III, apenas.\nComentário: As afirmativas I e III são corretas. A clivagem de precisão a 90° é indispensável para fusões de baixa perda e a curva do OTDR exibe fusões como degraus não reflexivos. A afirmativa II é falsa pois fibras multimodo sofrem com altíssima dispersão modal em distâncias acima de 2 km.\nFonte: Cabeamento Estruturado II, UA 9."
        },
        {
            "ua": "10", "obj": 1, "grau": "DIFÍCIL", "kw": "Gerenciamento de Infraestrutura e Data Center (TIA-942)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "O diretor de infraestrutura de TI de um provedor de serviços em nuvem supervisiona a construção de uma nova sala de servidores projetada segundo as diretrizes de arquitetura física da norma ANSI/TIA-942.\n\nO ambiente conta com piso elevado perfurado para insuflamento de ar frio, gabinetes fechados de alta densidade e leitos suspensos aramados para separação física entre cabos de sinal e cabos de energia elétrica. Para otimizar a eficiência de refrigeração (PUE) e evitar pontos quentes (Hot Spots), o projeto adotou a organização arquitetural baseada no confinamento de corredores quentes e frios (Hot/Cold Aisle Containment).",
            "afirmativas": "Com base nos conceitos da norma ANSI/TIA-942 de infraestrutura de Data Centers, analise as afirmativas:\nI. No arranjo de corredores quentes e frios, as frentes dos racks ficam voltadas umas para as outras no corredor frio (recebendo o ar gelado do piso) e as traseiras voltam-se para o corredor quente (expelindo o ar aquecido para o retorno de ar).\nII. A mistura de cabos de energia elétrica de alta voltagem de corrente alternada e cabos UTP de dados de cobre no mesmo leito suspenso é recomendada para otimizar a distribuição do peso nos racks.\nIII. O sistema de identificação e etiquetagem dos cabos, tomadas, patch panels e racks do Data Center deve seguir os padrões de administração da norma ANSI/TIA-606-C para garantir rastreabilidade.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e III, apenas.", "opt_b": "I e II, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e III, apenas.\nComentário: As afirmativas I e III descrevem perfeitamente o confinamento térmico Hot/Cold Aisle da TIA-942 e a norma de identificação TIA-606-C. A afirmativa II é falsa pois a convivência de cabos de potência e dados no mesmo leito gera ruído por indução eletromagnética.\nFonte: Cabeamento Estruturado II, UA 10."
        },
        {
            "ua": "10", "obj": 2, "grau": "DIFÍCIL", "kw": "Sistema de Aterramento de Telecomunicações (ANSI/TIA-607)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Um Data Center corporativo construído em uma estrutura predial de 5 andares exige um sistema de aterramento e equipotencialização de telecomunicações projetado estritamente sob as especificações da norma ANSI/TIA-607-D. Todos os Racks de servidores, organizadores metálicos, calhas e painéis de patch panel blindados (FTP/STP) foram conectados à Barra de Aterramento de Telecomunicações do Andar (TGB), a qual se interliga à Barra de Aterramento Principal (TMGB) pelo condutor de backbone de aterramento de cobre nu.",
            "afirmativas": "Com base nos princípios de aterramento de infraestruturas de TI da norma ANSI/TIA-607-D, analise as afirmativas:\n\nI. A ligação equipotencial e o aterramento efetivo de todas as estruturas metálicas dos Racks e da malha de blindagem dos cabos ao sistema de aterramento são obrigatórios para drenar correntes induzidas, surtos elétricos e descargas eletrostáticas para a terra.\n\nPORQUE\n\nII. O acúmulo de cargas eletrostáticas e a presença de diferenças de potencial elétrico de terra entre edifícios conectados por cabos de cobre causam surtos de tensão que danificam permanentemente as interfaces das placas de rede dos switches e geram riscos de choques aos operadores.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A ligação equipotencial TIA-607 drena ruídos e surtos de tensão, prevenindo queimaduras em interfaces de switches provocadas por diferenças de potencial de terra.\nFonte: Cabeamento Estruturado II, UA 10."
        }
    ]
)

# 2. Compiladores
create_exam(
    "Compiladores", "Compiladores", "AI Compiladores", "2; 3; 5; 8",
    [
        {
            "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Análise Léxica e Autômatos Finitos",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Durante o desenvolvimento da primeira fase de um compilador para uma linguagem de programação orientada a objetos, a equipe de engenharia de linguagens constrói o analisador léxico (Scanner). O papel primário desse módulo é varrer sequencialmente a cadeia de caracteres do código-fonte armazenado no arquivo de texto, agrupar esses caracteres em sequências com significado lógico chamadas lexemas e mapear cada lexema para sua representação simbólica (Token), eliminando espaços em branco e comentários.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta a estrutura matemática formal utilizada na ciência da computação para modelar e implementar o mecanismo de reconhecimento de padrões de lexemas em um analisador léxico:",
            "opt_a": "Autômato Finito Determinístico (AFD).", "opt_b": "Árvore Sintática Abstrata (AST).", "opt_c": "Tabela de Símbolos de Precedência LR(1).", "opt_d": "Máquina de Turing Não-Determinística de Fita Dupla.",
            "feedback": "A resposta certa é Autômato Finito Determinístico (AFD).\nComentário: Analisadores léxicos são fundamentados na teoria de linguagens regulares e utilizam Autômatos Finitos Determinísticos para transitar entre estados e reconhecer tokens.\nFonte: Compiladores, UA 2."
        },
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Análise Sintática Preditiva LL(1)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Um projetista de compiladores está desenvolvendo um analisador sintático descendente preditivo (Top-Down Parser) do tipo LL(1) utilizando a técnica de recursão descendente para processar construções de controle de fluxo de uma linguagem imperativa.\n\nDurante o processo de formalização da Gramática Livre de Contexto (GLC), o desenvolvedor constatou que algumas regras de produção apresentavam a estrutura E -> E + T, onde a variável não terminal no lado esquerdo aparece como o primeiro símbolo da produção no lado direito.",
            "afirmativas": "",
            "comando_text": "Considerando os requisitos de funcionamento dos algoritmos de análise sintática preditiva LL(1), assinale a alternativa que indica o procedimento gramatical obrigatório a ser aplicado para corrigir o problema da recursão e permitir a análise sem retrocesso (backtracking):",
            "opt_a": "Eliminação da recursão à esquerda e fatoração à esquerda da gramática.", "opt_b": "Inversão da ordem dos tokens na tabela de símbolos durante o parsing.", "opt_c": "Conversão direta da gramática em um autômato de pilha não determinístico sem tabela.", "opt_d": "Substituição de todas as variáveis não terminais por constantes numéricas inteiras.",
            "feedback": "A resposta certa é Eliminação da recursão à esquerda e fatoração à esquerda da gramática.\nComentário: Parsers LL(1) entram em loop infinito na presença de recursão à esquerda direta ou indireta; portanto, a eliminação da recursão à esquerda é pré-requisito obrigatório.\nFonte: Compiladores, UA 3."
        },
        {
            "ua": "05", "obj": 3, "grau": "DIFÍCIL", "kw": "Análise Semântica e Esquemas de Tradução",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Após a verificação sintática e a geração da Árvore Sintática Abstrata (AST), o compilador executa a etapa de análise semântica. O objetivo desta fase é checar a conformidade das regras de tipo da linguagem, validar o escopo das variáveis declaradas na Tabela de Símbolos e assegurar que operandos em expressões aritméticas possuam tipos compatíveis (como evitar a adição de uma string a um ponteiro de memória).\n\nPara associar regras semânticas à gramática livre de contexto, os projetistas utilizam uma Definição Dirigida pela Sintaxe (DDS), na qual atributos computados são anexados aos nós da árvore sintática.",
            "afirmativas": "Com base nos conceitos de tradução dirigida pela sintaxe, atributos sintetizados e herdados, analise as afirmativas:\nI. Atributos sintetizados em um nó pai da árvore sintática dependem exclusivamente dos valores dos atributos dos seus nós filhos.\nII. Atributos herdados em um nó filho podem depender dos valores dos atributos do seu nó pai e dos seus nós irmãos na árvore sintática.\nIII. A checagem de tipos e a validação do escopo das variáveis em tempo de compilação são tarefas executadas exclusivamente pela fase de análise léxica.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II diferenciam com precisão atributos sintetizados e herdados. A afirmativa III é falsa pois a checagem de tipos e validação de escopo ocorrem na análise semântica.\nFonte: Compiladores, UA 5."
        },
        {
            "ua": "08", "obj": 1, "grau": "DIFÍCIL", "kw": "Geração de Código Intermediário e Otimização",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "No fluxo de compilação de linguagens de alto desempenho como C e Rust, a etapa de otimização de código atua sobre uma representação intermediária (IR) independente de máquina, tal como o Código de Três Endereços (TAC - Three-Address Code) ou o grafo de controle de fluxo (CFG).\n\nO objetivo do otimizador de código é aplicar transformações que reduzam o tempo de execução do programa gerado e diminuam a pegada de memória, sem alterar o comportamento funcional nem a semântica original do algoritmo.",
            "afirmativas": "Com base nas técnicas de otimização de código intermediário e análise de fluxo de dados, analise as afirmativas:\nI. A eliminação de subexpressões comuns identifica cálculos idênticos repetidos em um mesmo bloco básico e reaproveita o resultado previamente armazenado.\nII. O desdobramento de laços (loop unrolling) reduz a sobrecarga (overhead) causada pelo incremento do contador e pelas instruções de salto condicional em loops repetitivos.\nIII. A representação intermediária (IR) deve ser projetada para depender estritamente dos registradores físicos de um processador específico para garantir eficiência.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II apresentam técnicas consagradas de otimização de código. A afirmativa III é falsa pois a representação intermediária (IR) deve ser independente de máquina para dar portabilidade.\nFonte: Compiladores, UA 8."
        },
        {
            "ua": "08", "obj": 2, "grau": "DIFÍCIL", "kw": "Alocação de Registradores por Coloração de Grafos",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Na fase final de geração de código de máquina para arquiteturas de hardware modernas (como x86_64 ou ARM64), o gerador de código do compilador deve mapear centenas de variáveis temporárias virtuais em um número limitado de registradores de uso geral da CPU (ex: 16 registradores físicos disponíveis na arquitetura). Para resolver esse problema de alocação de recursos, utilizam-se heurísticas baseadas em Teoria dos Grafos.",
            "afirmativas": "Com base no algoritmo de alocação de registradores por coloração de grafos de interferência, analise as afirmativas:\n\nI. A construção do Grafo de Interferência de Variáveis conecta dois registradores virtuais por uma aresta sempre que ambas as variáveis estiverem 'vivas' (live) simultaneamente no mesmo ponto do programa.\n\nPORQUE\n\nII. Caso o número cromático K necessário para colorir o grafo de interferência seja maior que a quantidade de registradores físicos da CPU, o compilador deve executar a operação de 'spill', transferindo o valor de variáveis temporárias para a memória Stack.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A interferência de variáveis vivas impede o compartilhamento do registrador físico; se faltarem registradores físicos (coloração K), o spill para a pilha é obrigatório.\nFonte: Compiladores, UA 8."
        }
    ]
)

# 3. Desenvolvimento de Dispositivos Móveis
create_exam(
    "Desenvolvimento de Dispositivos Móveis", "Desenvolvimento de Dispositivos Móveis", "AI Desenvolvimento de Dispositivos Móveis", "3; 4; 8; 10",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Ciclo de Vida de Activities e State Management no Android",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Durante o desenvolvimento de um aplicativo Android corporativo em Kotlin para gestão de vendas em campo, a equipe técnica enfrenta problemas de perda de dados digitados pelos usuários. Quando o usuário rotaciona a tela do smartphone da posição vertical (Portrait) para horizontal (Landscape), o sistema operacional Android destrói a instância corrente da Activity e cria uma nova instância do zero.\n\nPara evitar que o usuário precise preencher novamente os formulários e para não reexecutar chamadas assíncronas custosas ao servidor backend, os desenvolvedores precisam adotar um componente de arquitetura que preserve os dados da interface gráfica sobrevivendo a essas destruições e recriações provocadas por mudanças de configuração de hardware.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o componente da arquitetura Android Jetpack recomendado para armazenar e gerenciar dados de interface gráfica de forma consciente do ciclo de vida:",
            "opt_a": "ViewModel.", "opt_b": "IntentService.", "opt_c": "BroadcastReceiver.", "opt_d": "ContentProvider.",
            "feedback": "A resposta certa é ViewModel.\nComentário: O ViewModel foi projetado para reter e gerenciar dados de interface gráfica sobrevivendo a mudanças de configuração como rotações de tela.\nFonte: Desenvolvimento de Dispositivos Móveis, UA 3."
        },
        {
            "ua": "04", "obj": 2, "grau": "MÉDIA", "kw": "Layouts Declarativos com Jetpack Compose e Flexbox",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "No desenvolvimento moderno de aplicativos móveis utilizando a biblioteca gráfica Jetpack Compose em Kotlin, os desenvolvedores constroem interfaces dinâmicas através de um paradigma de UI declarativa, substituindo os antigos arquivos de layout XML por funções compostas (Composables) reativas.\n\nEm uma tela de detalhes de produtos, a equipe precisa dispor sequencialmente a imagem do produto, o título, a descrição e o botão de compra de cima para baixo, garantindo o empilhamento vertical ordenado dos elementos visuais.",
            "afirmativas": "",
            "comando_text": "No Jetpack Compose, assinale o componente composable nativo de layout utilizado para organizar e empilhar seus elementos filhos em uma sequência estritamente vertical:",
            "opt_a": "Column.", "opt_b": "Row.", "opt_c": "Box.", "opt_d": "Scaffold.",
            "feedback": "A resposta certa é Column.\nComentário: No Jetpack Compose, o layout 'Column' organiza seus elementos filhos de maneira vertical sequencial, equivalente a um LinearLayout com orientação vertical.\nFonte: Desenvolvimento de Dispositivos Móveis, UA 4."
        },
        {
            "ua": "08", "obj": 3, "grau": "DIFÍCIL", "kw": "Persistência de Dados Local com Room Database e SQLite",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um aplicativo móvel de entregas de encomendas necessita operar em modo offline-first (funcionamento garantido mesmo sem conectividade com a internet). Todos os dados de pedidos, clientes e rotas devem ser armazenados localmente no dispositivo móvel em um banco de dados relacional SQLite protegido por uma camada de abstração segura.\n\nPara implementar essa persistência de dados local de forma estruturada, a equipe adota a biblioteca Room do Android Jetpack.",
            "afirmativas": "Com base nos 3 componentes arquiteturais principais da biblioteca Room, analise as afirmativas:\nI. A anotação '@Entity' é utilizada para definir as classes de modelo que representam as tabelas e colunas do banco de dados SQLite local.\nII. As interfaces anotadas com '@Dao' (Data Access Object) contêm as assinaturas dos métodos anotados com @Query, @Insert, @Update e @Delete para manipulação dos dados.\nIII. Operações de leitura e escrita executadas na biblioteca Room são liberadas para rodar na Main Thread (UI Thread) sem qualquer bloqueio da interface gráfica.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com precisão Entity e DAO. A afirmativa III é falsa pois o Room proíbe acessos na Main Thread por padrão para evitar congelamento de tela (ANR).\nFonte: Desenvolvimento de Dispositivos Móveis, UA 8."
        },
        {
            "ua": "10", "obj": 1, "grau": "DIFÍCIL", "kw": "Consumo de APIs REST com Retrofit e Coroutines",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Para sincronizar o catálogo de produtos e autenticar usuários com o servidor backend em nuvem, um aplicativo móvel utiliza a biblioteca HTTP Retrofit combinada com Coroutines em Kotlin.\n\nA arquitetura do app foi desenhada para efetuar chamadas de rede assíncronas sem causar congelamento da interface (ANR - Application Not Responding) e para converter as respostas JSON em objetos de dados DTO automaticamente.",
            "afirmativas": "Com base na integração entre Retrofit, Coroutines e parsing de dados em aplicativos móveis, analise as afirmativas:\nI. A declaração de funções de rede anotadas com o modificador 'suspend' no Retrofit permite que as chamadas HTTP sejam executadas em threads secundárias de forma não bloqueante.\nII. Os conversores de dados (como Moshi ou Gson) serializam e deserializam automaticamente strings JSON em objetos Kotlin de forma transparente.\nIII. Requisições HTTP em ambiente mobile dispensam a necessidade de tratamento de exceções de falha de conectividade (como queda de sinal de rede móvel).",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão a assincronia das Coroutines e o conversor JSON. A afirmativa III é falsa pois redes móveis sofrem com quedas frequentes, exigindo tratamento de erro.\nFonte: Desenvolvimento de Dispositivos Móveis, UA 10."
        },
        {
            "ua": "10", "obj": 2, "grau": "DIFÍCIL", "kw": "Gerenciamento de Tarefas em Segundo Plano com WorkManager",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Um aplicativo de rastreamento de entregas urbanas precisa enviar em lotes as coordenadas geográficas (GPS) coletadas ao longo do dia para os servidores da empresa, mesmo se o aplicativo for encerrado pelo usuário ou se o smartphone for reiniciado durante o percurso.",
            "afirmativas": "Com base nos recursos de agendamento de tarefas diferíveis e persistentes da API WorkManager do Android Jetpack, analise as afirmativas:\n\nI. O WorkManager é a biblioteca recomendada para agendar tarefas em segundo plano que necessitam de execução garantida, mesmo que o aplicativo seja encerrado ou o sistema operacional reinicie.\n\nPORQUE\n\nII. O WorkManager seleciona automaticamente a API de agendamento do sistema operacional mais adequada (como JobScheduler ou AlarmManager) e respeita critérios de execução e modos de economia de bateria (Doze Mode).",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. O WorkManager abstrai a complexidade do agendamento background e garante a execução persistente respeitando as políticas de economia de energia do Android.\nFonte: Desenvolvimento de Dispositivos Móveis, UA 10."
        }
    ]
)

# 4. Estrutura de dados(seg)
create_exam(
    "Estrutura de dados(seg)", "Estrutura de Dados", "AI Estrutura de Dados", "3; 4; 6; 10",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Listas Encadeadas e Alocação Dinâmica",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em linguagens de programação de baixo e médio nível como C e C++, o gerenciamento eficiente de memória é crucial para o desempenho de sistemas embarcados e motores de banco de dados. Ao implementar uma lista encadeada simples, o programador aloca nós dinamicamente na memória Heap através da função malloc/new. Cada nó armazena o valor do elemento e um ponteiro de memória apontando diretamente para o nó seguinte da sequência.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que apresenta a principal vantagem operacional de uma lista encadeada simples em relação a um vetor (array) estático de tamanho fixo em memória:",
            "opt_a": "Capacidade de realizar inserções e remoções de elementos no início da estrutura em tempo constante O(1) sem a necessidade de deslocar os demais elementos.", "opt_b": "Acesso direto e aleatório a qualquer elemento da estrutura através do seu índice numérico em tempo constante O(1).", "opt_c": "Menor ocupação de espaço em memória física por elemento por descartar o uso de ponteiros de memória.", "opt_d": "Garantia de alocação de todos os elementos em um mesmo bloco contíguo de memória física RAM.",
            "feedback": "A resposta certa é Capacidade de realizar inserções e remoções de elementos no início da estrutura em tempo constante O(1) sem a necessidade de deslocar os demais elementos.\nComentário: Diferente dos arrays que exigem deslocamento de N elementos O(n) na inserção/remoção no início, listas encadeadas apenas ajustam os ponteiros em tempo O(1).\nFonte: Estrutura de Dados, UA 3."
        },
        {
            "ua": "04", "obj": 2, "grau": "MÉDIA", "kw": "Pilhas (Stack) e Filas (Queue) - LIFO e FIFO",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Um arquiteto de sistemas está projetando os módulos fundamentais de um ambiente operacional de escritório. Ele precisa definir as estruturas de dados adequadas para duas funcionalidades específicas: a função de histórico de navegação 'Voltar' de um navegador web (que deve retornar à página mais recentemente acessada) e o gerenciador de spool de impressão corporativo (que deve imprimir os documentos estritamente na ordem cronológica de chegada).",
            "afirmativas": "",
            "comando_text": "Assinale a opção que identifica corretamente as estruturas de dados abstratas adequadas para implementar a função de histórico 'Voltar' do navegador e a fila de impressão do servidor, respectivamente:",
            "opt_a": "Pilha (LIFO) e Fila (FIFO).", "opt_b": "Fila (FIFO) e Pilha (LIFO).", "opt_c": "Árvore Binária de Busca e Grafo Direcionado.", "opt_d": "Tabela Hash e Matriz Esparsa.",
            "feedback": "A resposta certa é Pilha (LIFO) e Fila (FIFO).\nComentário: O histórico de navegação funciona como Pilha (Last-In, First-Out: a última página visitada é a primeira a voltar). A fila de impressão é FIFO (First-In, First-Out: o primeiro documento enviado é o primeiro impresso).\nFonte: Estrutura de Dados, UA 4."
        },
        {
            "ua": "06", "obj": 3, "grau": "DIFÍCIL", "kw": "Árvores Binárias de Busca (BST) e Caminhamento",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Uma Árvore Binária de Busca (BST - Binary Search Tree) é uma estrutura de dados hierárquica não linear amplamente utilizada em algoritmos de indexação rápida. A propriedade fundamental de uma BST estabelece que, para qualquer nó N, todas as chaves armazenadas na subárvore esquerda possuem valores estritamente menores que a chave de N, enquanto todas as chaves na subárvore direita possuem valores estritamente maiores.",
            "afirmativas": "Com base nos algoritmos de travessia em árvores e na complexidade computacional de busca, analise as afirmativas:\nI. O caminhamento Em-Ordem (In-Order) em uma BST visita todos os nós em ordem numérica estritamente crescente de suas chaves.\nII. A busca por um elemento em uma BST perfeitamente balanceada possui complexidade de tempo de pior caso O(log n).\nIII. No pior caso de uma BST totalmente desbalanceada (degenerada no formato de lista encadeada), a busca possui complexidade de tempo O(n).",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I, II e III.", "opt_b": "I e II, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I e III, apenas.",
            "feedback": "A resposta certa é I, II e III.\nComentário: As três afirmativas são verdadeiras. O caminhamento Em-Ordem produz chaves ordenadas. O tempo de busca é proporcional à altura da árvore: O(log n) quando balanceada e O(n) quando degenerada.\nFonte: Estrutura de Dados, UA 6."
        },
        {
            "ua": "10", "obj": 1, "grau": "DIFÍCIL", "kw": "Tabelas Hash e Resolução de Colisões",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Para garantir acesso em tempo constante O(1) aos dados de dicionários, tabelas de rotas e índices de bancos de dados relacionais, utilizam-se Tabelas Hash (Tabelas de Espalhamento).\n\nA função hash h(k) mapeia chaves de entrada em posições de um vetor. Contudo, quando duas chaves distintas geram o mesmo índice de vetor, ocorre uma colisão que deve ser tratada por uma estratégia formal de resolução.",
            "afirmativas": "Com base nos métodos de resolução de colisões em Tabelas Hash, analise as afirmativas:\nI. O encadeamento separado (Separate Chaining) resolve colisões armazenando os elementos colidentes em uma lista encadeada vinculada àquela posição do vetor.\nII. O endereçamento aberto com sondagem linear (Linear Probing) procura sequencialmente a próxima posição livre no vetor quando ocorre uma colisão.\nIII. Uma função hash ideal deve mapear todas as chaves de entrada no mesmo índice inicial para otimizar o uso da memória cache L1 do processador.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II descrevem com precisão encadeamento separado e sondagem linear. A afirmativa III é falsa pois mapear todas as chaves no mesmo índice provocaria colisões catastróficas O(n).\nFonte: Estrutura de Dados, UA 10."
        },
        {
            "ua": "10", "obj": 2, "grau": "DIFÍCIL", "kw": "Árvores Balanceadas AVL e Rotações",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Em aplicações de alta performance que realizam frequentes operações de busca, inserção e remoção em grandes volumes de dados, utilizam-se Árvores Binárias Autobalanceadas do tipo AVL (Adelson-Velsky e Landis). O balanceamento da árvore é garantido através do cálculo contínuo do Fator de Balanceamento (FB) em cada nó.",
            "afirmativas": "Com base na propriedade de balanceamento e rotações em Árvores AVL, analise as afirmativas:\n\nI. Uma Árvore AVL executa rotações simples ou duplas à esquerda e à direita sempre que o Fator de Balanceamento de algum nó (diferença entre as alturas da subárvore esquerda e direita) assumir valores fora do intervalo [-1, 0, 1].\n\nPORQUE\n\nII. A manutenção estrita do Fator de Balanceamento em todos os nós da árvore garante que a sua altura total permaneça O(log n), prevenindo a degradação do desempenho das operações de busca para O(n).",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A regra de balanceamento AVL (|FB| <= 1) via rotações é justamente o mecanismo que limita a altura a O(log n).\nFonte: Estrutura de Dados, UA 10."
        }
    ]
)

print("Batch 1 atualizado com contextualização ENADE robusta (> 7 linhas).")
