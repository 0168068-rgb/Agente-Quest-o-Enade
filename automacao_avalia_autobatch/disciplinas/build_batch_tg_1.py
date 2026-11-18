# -*- coding: utf-8 -*-
"""
Batch TG 1: Disciplinas 1 a 4 (Provas TG 2026-4 - UAs Específicas do Tema Gerador e Contextualização ENADE > 7 linhas)
"""
from generate_full_batch import create_exam

# 1. Cabeamento estruturado II (UAs 5, 6)
create_exam(
    "Cabeamento estruturado II (seg)", "Cabeamento estruturado II", "AD Cabeamento estruturado II", "5; 6",
    [
        {
            "ua": "05", "obj": 1, "grau": "MÉDIA", "kw": "Desempenho e Frequência de Cabos Cat6A (500 MHz / 10GBASE-T)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em um projeto de infraestrutura de rede para o centro de processamento de dados de um hospital universitário, a equipe de engenharia precisa selecionar os cabos de par trançado para os links de 10 Gbps entre os racks do Data Center.\n\nO projeto estabelece a exigência rigorosa de suporte a frequências de amostragem de até 500 MHz a uma distância de até 100 metros no canal completo, mitigando a diafonia alienígena (ANEXT) em calhas de alta densidade conforme a norma ANSI/TIA-568.2-D.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica a categoria de cabo de par trançado de cobre especificada pela norma para essa aplicação:",
            "opt_a": "Categoria 6A (Cat6A).", "opt_b": "Categoria 5e (Cat5e).", "opt_c": "Categoria 3 (Cat3).", "opt_d": "Categoria 5 (Cat5).",
            "feedback": "A resposta certa é Categoria 6A (Cat6A).\nComentário: A Categoria 6A opera até 500 MHz e suporta a aplicação 10GBASE-T na distância máxima de 100 metros no canal completo.\nFonte: Cabeamento Estruturado II, UA 5."
        },
        {
            "ua": "05", "obj": 2, "grau": "MÉDIA", "kw": "Atenuação, Impedância Característica e Perda de Retorno (Return Loss)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Durante a transmissão de sinais de alta frequência em um cabeamento estruturado de par trançado de 100 Ohms de impedância nominal, o sinal elétrico sofre degradação e reflexões de energia em pontos de descontinuidade do meio físico.\n\nA equipe técnica analisa o parâmetro de Perda de Retorno (Return Loss), que mede a quantidade de sinal refletido de volta para a fonte emissora devido a variações imprevistas na impedância ao longo do cabo e nos conectores.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta a principal causa física para o aumento desfavorável da reflexão de sinal (baixa Perda de Retorno) em um link de par trançado:",
            "opt_a": "Esmagamento físico, dobras com raio de curvatura inferior ao permitido ou conectores com impedância desalinhada.", "opt_b": "Uso de patch cords de manobra de fibra óptica monomodo.", "opt_c": "Instalação de cabos em canaletas exclusivas e blindadas.", "opt_d": "Utilização de switches com portas de 1 Gbps em vez de 100 Mbps.",
            "feedback": "A resposta certa é Esmagamento físico, dobras com raio de curvatura inferior ao permitido ou conectores com impedância desalinhada.\nComentário: Deformações mecânicas no cabo alteram o espaçamento interno dos condutores, modificando a impedância e provocando reflexões de sinal (Return Loss baixo).\nFonte: Cabeamento Estruturado II, UA 5."
        },
        {
            "ua": "06", "obj": 1, "grau": "DIFÍCIL", "kw": "Testes de Certificação de Campo e Medição de NEXT/PS-NEXT",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Durante a validação de um cabeamento estruturado Categoria 6 de 4 pares em um novo prédio corporativo, o auditor de rede utiliza um certificador de campo de alta precisão para realizar a homologação dos links permanentes.\n\nO equipamento realiza a varredura das métricas de Diafonia no Endereço Próximo (NEXT - Near-End Crosstalk) e de Soma Potencial da Diafonia no Endereço Próximo (PS-NEXT - Power Sum NEXT).",
            "afirmativas": "Com base nos parâmetros NEXT e PS-NEXT de certificação, analise as afirmativas:\nI. O NEXT mede a interferência eletromagnética induzida entre um par transmissor e um par receptor no mesmo cabo, medida na extremidade próxima do emissor.\nII. O PS-NEXT calcula a soma combinada da diafonia gerada por três pares transmissores sobre o quarto par receptor no mesmo cabo.\nIII. Valores elevados em decibéis (dB) no parâmetro NEXT indicam péssima qualidade de sinal e reprovação do link.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem corretamente NEXT e PS-NEXT. A afirmativa III é falsa pois no NEXT, quanto MAIOR a margem em dB acima do limite normativo, MELHOR e mais isolado é o link.\nFonte: Cabeamento Estruturado II, UA 6."
        },
        {
            "ua": "06", "obj": 2, "grau": "DIFÍCIL", "kw": "Diagnóstico de Falhas por Mapeamento de Fios (Wiremap) e TDR",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Um técnico de suporte analisa um ponto de rede em um escritório que apresenta falta total de conectividade. Ele conecta o certificador de cabo e executa o teste básico de Mapeamento de Fios (Wiremap) e Refletometria no Domínio do Tempo (TDR).\n\nO relatório exibe que os condutores do par 1-2 foram invertidos no conector RJ-45 da tomada fêmea (Par Invertido) e indica uma ruptura física no condutor do pino 3 a 45 metros da sala de telecomunicações.",
            "afirmativas": "Com base em diagnósticos com Wiremap e TDR, analise as afirmativas:\nI. O teste de Wiremap verifica a continuidade pino a pino, identificando curto-circuitos, pares abertos, pares invertidos e pares transpostos.\nII. A tecnologia TDR (Time-Domain Reflectometer) calcula a localização exata de falhas e interrupções no cabo medindo o tempo de retorno dos pulsos elétricos refletidos.\nIII. O Wiremap é capaz de diagnosticar a perda de pacote causada por atenuação de alta frequência no cabo.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II detalham perfeitamente o Wiremap pino a pino e a localização de rupturas por TDR. A afirmativa III é falsa pois atenuação por frequência exige varredura com gerador de RF, incapaz de ser medida pelo teste simples de Wiremap.\nFonte: Cabeamento Estruturado II, UA 6."
        },
        {
            "ua": "06", "obj": 3, "grau": "DIFÍCIL", "kw": "Certificação de Enlaces com OTDR e Testador de Certificação de Cobre",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Em um contrato de instalação de cabeamento de dados para um tribunal de justiça, a cláusula contratual exige a apresentação dos laudos técnicos digitais originais gerados por um certificador de rede homologado de Nível III para os cabos de cobre e OTDR para o backbone óptico.\n\nA equipe de instalação realizou testes de continuidade simples com um testador de bancada de LEDs e tentou emitir o laudo de aceitação final.",
            "afirmativas": "Com base na certificação de redes de comunicação, analise as afirmativas:\n\nI. Testadores simples de continuidade de LEDs são insuficientes para a certificação de instalações de cabeamento estruturado corporativas.\n\nPORQUE\n\nII. A certificação formal exige a validação parametrizada em frequências de trabalho reais com medições quantitativas de NEXT, Atenuação, Perda de Retorno e Delay Skew comparadas aos limites das normas ANSI/TIA.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. Testadores de LED apenas verificam continuidade elétrica DC, omitindo a análise de alta frequência exigida na certificação formal.\nFonte: Cabeamento Estruturado II, UA 6."
        }
    ],
    subfolder='AD'
)

# 2. Compiladores (UAs 2, 3)
create_exam(
    "Compiladores", "Compiladores", "AD Compiladores", "2; 3",
    [
        {
            "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Análise Léxica e Expressões Regulares em Geradores como Flex/Lex",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Na construção do compilador para uma nova linguagem de programação, a primeira fase do front-end consiste na **Análise Léxica** (Scanning). O analisador léxico lê o fluxo contínuo de caracteres do código-fonte e o agrupa em tokens válidos (como palavras reservadas, identificadores, números e operadores).\n\nPara automatizar a criação do analisador léxico a partir de padrões formais definidos por Expressões Regulares, o desenvolvedor utiliza ferramentas geradoras de código léxico como o Flex (Fast Lexical Analyzer Generator).",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica a estrutura de dados retornada pelo analisador léxico para o analisador sintático a cada caractere/palavra reconhecida:",
            "opt_a": "Tokens (pares contendo a classe do token e seu valor/lexema associado).", "opt_b": "Árvore de Sintaxe Abstrata (AST) completa.", "opt_c": "Código executável binário ELF de 64 bits.", "opt_d": "Matriz de alocação de registradores da CPU.",
            "feedback": "A resposta certa é Tokens (pares contendo a classe do token e seu valor/lexema associado).\nComentário: A saída do analisador léxico é um fluxo sequencial de tokens consumido diretamente pelo analisador sintático.\nFonte: Compiladores, UA 2."
        },
        {
            "ua": "02", "obj": 2, "grau": "MÉDIA", "kw": "Conversão de AFN para AFD (Algoritmo de Construção de Subconjuntos)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Durante o processamento das expressões regulares que descrevem os padrões de identificadores em um compilador, o gerador de analisador léxico constrói inicialmente um Autômato Finito Não-Determinístico (AFN) contendo transições vazias (ε-transições).\n\nComo AFNs não podem ser executados diretamente em tempo linear O(n) por máquinas computacionais convencionais, o algoritmo de **Construção de Subconjuntos** (Subset Construction) é aplicado para converter o AFN em um Autômato Finito Determinístico (AFD) equivalente.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta a principal razão para converter um AFN em um AFD na análise léxica:",
            "opt_a": "Garantir tempo de reconhecimento de tokens estritamente linear O(n) em relação ao tamanho da entrada, sem retrocesso.", "opt_b": "Reduzir o tamanho do arquivo binário executável em disco.", "opt_c": "Permitir a compilação de linguagens de programação dinâmicas sem tipos.", "opt_d": "Eliminar a necessidade de tabelas de símbolos no compilador.",
            "feedback": "A resposta certa é Garantir tempo de reconhecimento de tokens estritamente linear O(n) em relação ao tamanho da entrada, sem retrocesso.\nComentário: O determinismo do AFD garante que cada caractere de entrada avance para exatamente um estado, garantindo tempo de execução linear O(n).\nFonte: Compiladores, UA 2."
        },
        {
            "ua": "03", "obj": 1, "grau": "DIFÍCIL", "kw": "Gramáticas Livres de Contexto (GLC) e Ambiguidade Sintática",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um projetista de compiladores define a sintaxe das estruturas de controle e expressões aritméticas da linguagem através de uma Gramática Livre de Contexto (GLC) na notação BNF (Backus-Naur Form).\n\nDurante os testes da gramática para a expressão `if E then S else S`, ele descobre que a regra gera o problema clássico do **dangling-else** (else ambíguo), permitindo duas árvores de análise sintática distintas para a mesma cadeia de entrada.",
            "afirmativas": "Com base em Gramáticas Livres de Contexto e ambiguidade, analise as afirmativas:\nI. Uma gramática é ambígua se existir pelo menos uma cadeia de entrada para a qual se pode construir duas ou mais árvores de derivação sintática distintas.\nII. Ambiguidade sintática em expressões aritméticas (ex: `a + b * c`) é resolvida reestruturando a gramática com níveis de precedência e associatividade de operadores.\nIII. Compiladores industriais conseguem gerar código executável sem ambiguidades mesmo utilizando gramáticas 100% ambíguas sem regras de desambiguação.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com precisão a ambiguidade e sua resolução por precedência. A afirmativa III é falsa pois ambiguidades não resolvidas causam conflitos shift/reduce em geradores como Yacc/Bison.\nFonte: Compiladores, UA 3."
        },
        {
            "ua": "03", "obj": 2, "grau": "DIFÍCIL", "kw": "Parsing Ascendente LR(1) / LALR(1) e Tabelas de Parsing Yacc/Bison",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Na construção da etapa de análise sintática de um compilador C++, o desenvolvedor utiliza o gerador Bison para produzir um analisador sintático ascendente (Bottom-Up) da família LALR(1).\n\nO analisador sintático LALR(1) mantém uma pilha de estados e toma decisões de empilhar (Shift) ou reduzir (Reduce) consultando uma tabela de ação e desvio (ACTION e GOTO) com 1 token de consulta futura.",
            "afirmativas": "Com base nos analisadores sintáticos ascendentes LR/LALR, analise as afirmativas:\nI. A ação de Shift (Empilhar) consome o token atual de entrada e empilha o novo estado na pilha de parsing.\nII. A ação de Reduce (Reduzir) substitui uma sequência de símbolos do topo da pilha correspondente ao corpo de uma produção pelo seu não-terminal de cabeça.\nIII. Um conflito Shift/Reduce ocorre quando a tabela de parsing não consegue decidir se deve empilhar o token ou aplicar uma redução naquela posição.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I, II e III.", "opt_b": "I e II, apenas.", "opt_c": "I e III, apenas.", "opt_d": "II e III, apenas.",
            "feedback": "A resposta certa é I, II e III.\nComentário: Todas as afirmativas são verdadeiras. Elas explicam as operações fundamentais Shift e Reduce de analisadores ascendentes e a definição de conflito Shift/Reduce.\nFonte: Compiladores, UA 3."
        },
        {
            "ua": "03", "obj": 3, "grau": "DIFÍCIL", "kw": "Tratamento e Recuperação de Erros Sintáticos em Compiladores",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Durante a compilação de um arquivo de código-fonte contendo centenas de linhas de instruções, o analisador sintático encontra um erro de sintaxe (como a ausência de um ponto-e-vírgula `;` no final de uma instrução na linha 15).\n\nPara evitar que o compilador pare a execução imediatamente no primeiro erro encontrado, o analisador utiliza um modo de **Recuperação de Erros em Modo Pânico** (Panic-Mode Recovery).",
            "afirmativas": "Com base nos mecanismos de tratamento de erros em compiladores, analise as afirmativas:\n\nI. A recuperação de erros em modo pânico descarta tokens da entrada um a um até encontrar um símbolo de sincronização definido (como `;` ou `}`), permitindo continuar a análise sintática das instruções seguintes do programa.\n\nPORQUE\n\nII. Reportar múltiplos erros de compilação legítimos em uma única execução melhora a produtividade dos desenvolvedores ao evitar a necessidade de re-compilar o código a cada pequeno erro corrigido.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A recuperação por tokens de sincronização no modo pânico atende diretamente à necessidade de relatar múltiplos erros em uma única rodada de compilação.\nFonte: Compiladores, UA 3."
        }
    ],
    subfolder='AD'
)

# 3. Desenvolvimento de Dispositivos Móveis (UAs 3, 4)
create_exam(
    "Desenvolvimento de Dispositivos Móveis", "Desenvolvimento de Dispositivos Móveis", "AD Desenvolvimento de Dispositivos Móveis", "3; 4",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Gerenciamento de Layouts Responsivos em Android (ConstraintLayout)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "No desenvolvimento da interface de usuário (UI) de um aplicativo móvel Android para suporte a diferentes tamanhos e orientações de tela (smartphones e tablets), o desenvolvedor projeta a árvore de componentes visuais em XML.\n\nPara evitar o aninhamento profundo e ineficiente de múltiplos `LinearLayout` ou `RelativeLayout` que degrada a performance de renderização da tela, a documentação oficial do Android recomenda a utilização do gerenciador de layout plano `ConstraintLayout`.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica a principal vantagem arquitetural do `ConstraintLayout` na construção de telas complexas no Android:",
            "opt_a": "Permitir a criação de layouts planos (flat hierarchies) sem aninhamento de views, reduzindo o tempo de cálculo de medidas da tela.", "opt_b": "Eliminar a necessidade de código Java ou Kotlin na aplicação.", "opt_c": "Criptografar as imagens armazenadas na pasta res/drawable.", "opt_d": "Publicar automaticamente o aplicativo na Google Play Store.",
            "feedback": "A resposta certa é Permitir a criação de layouts planos (flat hierarchies) sem aninhamento de views, reduzindo o tempo de cálculo de medidas da tela.\nComentário: O ConstraintLayout permite posicionar e dimensionar widgets com base em restrições relativas entre elementos, mantendo a hierarquia plana e rápida para renderizar.\nFonte: Desenvolvimento de Dispositivos Móveis, UA 3."
        },
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Passagem de Dados entre Activities usando Intents e Bundles",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Em um aplicativo de compras para Android, após o usuário selecionar um produto na lista exibida na `ListaProdutosActivity`, o aplicativo deve abrir a tela `DetalheProdutoActivity` exibindo as informações do item selecionado.\n\nPara navegar entre as duas telas e transferir dados estruturados (como ID do produto e preço), o desenvolvedor utiliza uma `Intent` explícita associada a um objeto `Bundle` (`putExtra`).",
            "afirmativas": "",
            "comando_text": "Assinale a opção que apresenta o método utilizado no Android para enviar um valor do tipo String dentro de uma Intent de navegação:",
            "opt_a": "intent.putExtra(\"chave\", valorString)", "opt_b": "intent.sendSocket(valorString)", "opt_c": "intent.writeMemory(valorString)", "opt_d": "intent.setDatabase(valorString)",
            "feedback": "A resposta certa é intent.putExtra(\"chave\", valorString).\nComentário: O método `putExtra` insere pares de chave-valor nos extras da Intent, permitindo a recuperação na Activity de destino via `getIntent().getStringExtra(\"chave\")`.\nFonte: Desenvolvimento de Dispositivos Móveis, UA 3."
        },
        {
            "ua": "04", "obj": 1, "grau": "DIFÍCIL", "kw": "Arquitetura MVVM (Model-View-ViewModel) e LiveData/StateFlow",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Para garantir a separação de responsabilidades, testabilidade e sobrevivência de dados a mudanças de configuração de tela (como rotação de retrato para paisagem) no Android, a equipe adota a arquitetura **MVVM** (Model-View-ViewModel).\n\nO `ViewModel` armazena o estado e as regras de negócio da interface, utilizando contêineres de dados observáveis como `LiveData` ou `StateFlow` para notificar a `Activity`/`Fragment` (`View`) sobre atualizações.",
            "afirmativas": "Com base no padrão arquitetural MVVM no desenvolvimento Android, analise as afirmativas:\nI. O `ViewModel` não deve manter referências diretas ao contexto de `Activity` ou `View` para evitar vazamentos de memória (Memory Leaks).\nII. A `View` observa as alterações nos dados do `LiveData` mantido pelo `ViewModel` e atualiza os componentes de interface automaticamente.\nIII. A rotação da tela do smartphone destrói o `ViewModel` e apaga todo o estado da tela que estava em memória.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem corretamente o isolamento do ViewModel e o padrão Observer com LiveData. A afirmativa III é falsa pois a principal vantagem do ViewModel é justamente sobreviver às mudanças de configuração como rotação de tela.\nFonte: Desenvolvimento de Dispositivos Móveis, UA 4."
        },
        {
            "ua": "04", "obj": 2, "grau": "DIFÍCIL", "kw": "Gerenciamento de Estado Reativo em Flutter (StatefulWidget / Provider)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "No desenvolvimento de um aplicativo multiplataforma com o framework Flutter (Dart), o desenvolvedor precisa gerenciar o estado da tela de um formulário interativo de cadastro com múltiplos campos e validações.\n\nEle avalia o uso de gerenciamento de estado local com `StatefulWidget` e o método `setState()`, comparado a soluções de estado reativo global como `Provider`, `Riverpod` ou `Bloc`.",
            "afirmativas": "Com base no gerenciamento de estado em Flutter, analise as afirmativas:\nI. A chamada ao método `setState()` instrui o framework Flutter a agendar a reconstrução (rebuild) da árvore de widgets do `StatefulWidget`.\nII. Abordagens de estado reativo (como Provider ou Bloc) evitam a reconstrução desnecessária da árvore inteira de widgets ao atualizar apenas os componentes observadores específicos.\nIII. O Flutter não permite alterar o estado de qualquer componente visual após a inicialização da tela.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II explicam com precisão o disparo de rebuild via `setState()` e a eficiência do gerenciamento de estado reativo com Provider/Bloc. A afirmativa III é falsa pois o Flutter é um framework reativo dinâmico.\nFonte: Desenvolvimento de Dispositivos Móveis, UA 4."
        },
        {
            "ua": "04", "obj": 3, "grau": "DIFÍCIL", "kw": "Renderização de Listas de Alto Desempenho (RecyclerView / ListView.builder)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Um aplicativo de rede social exibe um feed contendo milhares de publicações com imagens e textos através da rolagem da tela do smartphone do usuário.\n\nPara evitar que a alocação de memória para milhares de componentes visuais esgote a memória RAM do dispositivo (causando travamento ANR), a aplicação utiliza o componente `RecyclerView` no Android ou `ListView.builder` no Flutter.",
            "afirmativas": "Com base na renderização de listas em aplicações móveis, analise as afirmativas:\n\nI. Componentes como `RecyclerView` e `ListView.builder` reciclam as visões (views) dos itens que rolaram para fora da tela visível, reequipando-as com os novos dados dos itens que estão entrando na tela.\n\nPORQUE\n\nII. A reciclagem de visões mantém um número fixo de objetos de visualização alocados em memória RAM suficiente apenas para preencher a tela física, garantindo rolagem fluida em listas de tamanho arbitrariamente grande.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. O reuso de ViewHolder/views visíveis é o mecanismo exato de reciclagem para garantir rolagem fluida a 60 FPS sem estouro de memória.\nFonte: Desenvolvimento de Dispositivos Móveis, UA 4."
        }
    ],
    subfolder='AD'
)

# 4. Estrutura de dados (UAs 3, 4)
create_exam(
    "Estrutura de dados(seg)", "Estrutura de Dados", "AD Estrutura de dados", "3; 4",
    [
        {
            "ua": "03", "obj": 1, "grau": "MÉDIA", "kw": "Alocação Sequencial vs Encadeada (Listas Encadeadas)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Ao projetar o módulo de gerenciamento de memória de um sistema operacional de tempo real, o programador analisa as vantagens e desvantagens de utilizar vetores estáticos (alocação sequencial contígua) versus Listas Encadeadas Dinâmicas.\n\nNa Lista Encadeada Simples, cada nó alocado na memória Heap contém a informação do dado armazenado e um ponteiro de referência para o endereço do próximo nó da lista.",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica a principal vantagem de uma Lista Encadeada Dinâmica em relação a um Vetor Estático:",
            "opt_a": "Inserção e remoção de elementos em qualquer posição sem a necessidade de deslocamento físico dos demais elementos.", "opt_b": "Acesso direto a qualquer elemento em tempo constante O(1) através de um índice numérico.", "opt_c": "Eliminação total do uso de ponteiros em memória RAM.", "opt_d": "Menor consumo de memória RAM total para armazenar dados pequenos.",
            "feedback": "A resposta certa é Inserção e remoção de elementos em qualquer posição sem a necessidade de deslocamento físico dos demais elementos.\nComentário: Em listas encadeadas, a inserção/remoção altera apenas os ponteiros dos nós vizinhos, sem necessitar da reordenação física em bloco típica dos vetores.\nFonte: Estrutura de Dados, UA 3."
        },
        {
            "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Pilhas (LIFO) e Aplicações em Avaliação de Expressões Pós-fixas (RPN)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Uma calculadora científica utiliza uma estrutura de dados de **Pilha** (Stack) operando segundo a disciplina LIFO (Last-In, First-Out) para avaliar expressões matemáticas escritas na Notação Polonesa Reversa (pós-fixa, ex: `5 3 + 2 *`).\n\nDurante o processamento da expressão, os operandos numéricos são empilhados (`push`); quando um operador aritmético é encontrado, os dois últimos operandos são desempilhados (`pop`), calculados e o resultado é empilhado novamente.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o valor final resultante do processamento da expressão pós-fixa `6 2 / 4 +` em uma pilha:",
            "opt_a": "7.", "opt_b": "8.", "opt_c": "12.", "opt_d": "3.",
            "feedback": "A resposta certa é 7.\nComentário: Empilha 6 e 2; operador `/` desempilha 6 e 2 (`6 / 2 = 3`) e empilha 3; empilha 4; operador `+` desempilha 3 e 4 (`3 + 4 = 7`). Resultado final = 7.\nFonte: Estrutura de Dados, UA 3."
        },
        {
            "ua": "04", "obj": 1, "grau": "DIFÍCIL", "kw": "Algoritmos de Ordenação O(n²) (BubbleSort, InsertionSort, SelectionSort)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um estudante de ciência da computação implementa e compara três algoritmos simples de ordenação quadrática O(n²): **BubbleSort**, **SelectionSort** e **InsertionSort** para ordenar vetores pequenos de inteiros em memória.\n\nEle analisa a quantidade de comparações de chaves e a quantidade de trocas físicas de posição realizadas por cada algoritmo.",
            "afirmativas": "Com base nos algoritmos de ordenação quadráticos O(n²), analise as afirmativas:\nI. O InsertionSort possui comportamento altamente eficiente O(n) para vetores que já se encontram previamente ordenados ou quase ordenados.\nII. O SelectionSort realiza sempre o mesmo número de comparações O(n²) independentemente da ordem inicial dos elementos do vetor.\nIII. O BubbleSort flutua o maior elemento do vetor para sua posição final a cada passagem através de trocas adjacentes sucessivas.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I, II e III.", "opt_b": "I e II, apenas.", "opt_c": "I e III, apenas.", "opt_d": "II e III, apenas.",
            "feedback": "A resposta certa é I, II e III.\nComentário: Todas as afirmativas são verdadeiras. Elas caracterizam com exatidão o melhor caso O(n) do InsertionSort, a rigidez do SelectionSort e a mecânica de trocas adjacentes do BubbleSort.\nFonte: Estrutura de Dados, UA 4."
        },
        {
            "ua": "04", "obj": 2, "grau": "DIFÍCIL", "kw": "Algoritmos de Busca (Busca Binária vs Busca Linear) e Pré-requisitos",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Um programador precisa localizar o registro de um cliente pelo número de CPF em uma tabela contendo 1 milhão de registros em memória.\n\nEle analisa o desempenho da **Busca Linear** (complexidade O(n)) versus a **Busca Binária** (complexidade O(log n)) e verifica os pré-requisitos necessários para a execução de cada algoritmo.",
            "afirmativas": "Com base nos algoritmos de busca em vetores, analise as afirmativas:\nI. A Busca Binária exige obrigatoriamente que o vetor de dados esteja previamente ordenado pela chave de busca.\nII. A Busca Binária reduz a área de busca pela metade a cada comparação, realizando no máximo cerca de 20 comparações em um vetor de 1 milhão de elementos.\nIII. A Busca Linear é mais rápida que a Busca Binária para vetores ordenados de grande porte.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem com exatidão a ordenação prévia e a eficiência O(log n) da busca binária (`log2(1.000.000) ≈ 20`). A afirmativa III é falsa pois a busca binária é exponencialmente mais rápida que a busca linear em dados grandes.\nFonte: Estrutura de Dados, UA 4."
        },
        {
            "ua": "04", "obj": 3, "grau": "DIFÍCIL", "kw": "Análise de Complexidade Assintótica de Espaço e Tempo (Notação Big-O)",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Durante a revisão de código de uma função de processamento de matrizes $N \\times N$, o líder técnico identifica dois laços de repetição `for` aninhados (`for i in range(N): for j in range(N): ...`).\n\nEle utiliza a notação assintótica **Big-O** para classificar o crescimento do tempo de execução do algoritmo à medida que o tamanho da entrada $N$ tende ao infinito.",
            "afirmativas": "Com base na análise assintótica de complexidade com Notação Big-O, analise as afirmativas:\n\nI. Um algoritmo com laços aninhados de tamanho N possui complexidade de tempo de pior caso classificada como $O(N^2)$ (complexidade quadrática).\n\nPORQUE\n\nII. A Notação Big-O descreve o limite superior assintótico da taxa de crescimento do algoritmo, desconsiderando constantes multiplicativas e termos de menor ordem para entradas grandes.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. O aninhamento $N \\times N$ gera a taxa de crescimento $N^2$, que é formalmente caracterizada pelo limite superior assintótico da Notação Big-O.\nFonte: Estrutura de Dados, UA 4."
        }
    ],
    subfolder='AD'
)

print("Batch TG 1 concluído.")
