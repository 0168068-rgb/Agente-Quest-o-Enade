# -*- coding: utf-8 -*-
"""
Script de Construção e Geração Completa das 22 Provas AI 2026-4
"""
import os
from generate_all_22_exams import create_discipline_exam

all_disciplines_data = [
    # 1. Cabeamento estruturado II
    {
        "folder": "Cabeamento estruturado II (seg)",
        "name": "Cabeamento estruturado II",
        "title": "AI Cabeamento estruturado II",
        "uas": "5; 6; 9; 10",
        "questions": [
            {
                "ua": "05", "obj": 1, "grau": "MÉDIA", "kw": "Norma ANSI/TIA-568 e Categorias de Cabos",
                "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
                "context_text": "Em um projeto de infraestrutura de cabeamento estruturado para um centro de dados corporativo, a equipe de engenharia precisa selecionar os subsistemas de cabeamento e categorias de par trançado blindado (S/FTP) capazes de suportar taxas de transmissão de até 10 Gbps em frequências de até 500 MHz, respeitando os limites de distância da norma ANSI/TIA-568.2-D.",
                "afirmativas": "",
                "comando_text": "Considerando a classificação das normas internacionais de cabeamento estruturado, a categoria de cabo de par trançado que atende de forma exata às especificações para 10GBASE-T a 500 MHz é a [lacuna]",
                "opt_a": "Categoria 6A (Cat6A).", "opt_b": "Categoria 5e (Cat5e).", "opt_c": "Categoria 3 (Cat3).", "opt_d": "Categoria 5 (Cat5).",
                "feedback": "A resposta certa é Categoria 6A (Cat6A).\nComentário: A norma ANSI/TIA-568.2-D especifica que a Categoria 6A opera em frequências de até 500 MHz e suporta a aplicação 10GBASE-T em distâncias de até 100 metros.\nFonte: Cabeamento Estruturado II, UA 5."
            },
            {
                "ua": "06", "obj": 2, "grau": "MÉDIA", "kw": "Certificação de Redes de Cobre e Parâmetros NEXT/FEXT",
                "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
                "context_text": "Durante o processo de comissionamento de uma rede de cabeamento estruturado em um edifício comercial, um técnico utiliza um certificador de rede de campo para validar os links permanentes de cobre. O relatório acusou falhas de diafonia na extremidade próxima (NEXT - Near-End Crosstalk) em diversos pontos da sala de telecomunicações.",
                "afirmativas": "",
                "comando_text": "Com base nas boas práticas de conectorização e normas de certificação de cabeamento, a causa primária para o alto nível de ruído por NEXT em conectores RJ-45 é [lacuna]",
                "opt_a": "o destrançamento excessivo dos pares de fios no momento da crimpagem nos conectores fêmea.", "opt_b": "o uso de patch cords com comprimento inferior a 0,5 metros.", "opt_c": "a instalação dos cabos em canaletas plásticas exclusivas sem cabos elétricos.", "opt_d": "a utilização de tomadas de telecomunicações com contatos banhados a ouro.",
                "feedback": "A resposta certa é o destrançamento excessivo dos pares de fios no momento da crimpagem nos conectores fêmea.\nComentário: O destrançamento dos pares acima do limite especificado pelas normas (máximo 13 mm para Cat6/6A) expõe os condutores ao acoplamento eletromagnético mútuo, causando degradação do parâmetro NEXT.\nFonte: Cabeamento Estruturado II, UA 6."
            },
            {
                "ua": "09", "obj": 3, "grau": "DIFÍCIL", "kw": "Redes de Fibras Ópticas e Emendas por Fusão",
                "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
                "context_text": "Uma empresa de telecomunicações está implantando o cabeamento de backbone óptico entre dois edifícios separados por 3 km. O projeto prevê a utilização de fibras ópticas monomodo (SMF) conectorizadas em distribuidores internos ópticos (DIO). Durante a fusão de duas extensões de cabo óptico utilizando uma máquina de fusão por alinhamento pelo núcleo, a equipe precisa garantir a menor atenuação possível na emenda e validar o link com um refletômetro óptico no domínio do tempo (OTDR).",
                "afirmativas": "Com base nas técnicas de conectorização, emendas e testes em redes ópticas, analise as afirmativas:\nI. A fusão de fibras monomodo exige a clivagem precisa da face da fibra em ângulo reto (90°) para minimizar as perdas por inserção e o retorno óptico (ORL).\nII. O uso de fibras ópticas multimodo em substituição às monomodo reduziria a dispersão modal em links de longa distância acima de 2 km.\nIII. O evento de fusão na curva do OTDR é identificado como uma atenuação localizada (degrau de perda não reflexivo).",
                "comando_text": "É correto o que se afirma em:",
                "opt_a": "I e III, apenas.", "opt_b": "I e II, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
                "feedback": "A resposta certa é I e III, apenas.\nComentário: As afirmativas I e III são corretas. A clivagem perfeita é essencial para fusões ópticas de baixa perda. A curva do OTDR exibe fusões como eventos atenuativos não reflexivos. A afirmativa II é falsa porque fibras multimodo possuem alta dispersão modal em comparação com fibras monomodo em links longos.\nFonte: Cabeamento Estruturado II, UA 9."
            },
            {
                "ua": "10", "obj": 1, "grau": "DIFÍCIL", "kw": "Gerenciamento de Infraestrutura e Data Center (TIA-942)",
                "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
                "context_text": "O gerente de TI de uma instituição financeira supervisiona a modernização da Sala de Equipamentos (ER) e dos racks do Data Center. O projeto adota a norma ANSI/TIA-942 e estabelece a separação dos caminhos de cabeamento óptico e de cobre através de leitos de cabos suspensos, além da organização térmica por corredores quentes e frios (Hot/Cold Aisle).",
                "afirmativas": "Com base nas normas de gerenciamento e infraestrutura de Data Centers, analise as afirmativas:\nI. A organização em corredores quentes e frios exige que os racks fiquem dispostos de frente para frente (recebendo ar frio do piso elevado) e de costas para costas (expelindo ar quente para o exaustor).\nII. A mistura de cabos de energia elétrica de alta voltagem no mesmo leito de cabos de dados de cobre sem blindagem é recomendada para economizar espaço físico nos Racks.\nIII. A identificação e etiquetagem dos cabos e painéis de conexão deve seguir a norma ANSI/TIA-606-C para permitir rastreabilidade de ponta a ponta.",
                "comando_text": "É correto o que se afirma em:",
                "opt_a": "I e III, apenas.", "opt_b": "I e II, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
                "feedback": "A resposta certa é I e III, apenas.\nComentário: A afirmativa I descreve com precisão a disposição térmica Hot/Cold Aisle da TIA-942. A afirmativa III destaca a norma TIA-606-C de identificação. A afirmativa II é falsa pois a convivência de cabos de potência e dados no mesmo leito gera ruído por indução eletromagnética.\nFonte: Cabeamento Estruturado II, UA 10."
            },
            {
                "ua": "10", "obj": 2, "grau": "DIFÍCIL", "kw": "Sistema de Aterramento de Telecomunicações (ANSI/TIA-607)",
                "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
                "context_text": "Em um edifício comercial de múltiplos andares, a infraestrutura de telecomunicações requer um sistema dedicado de aterramento e equipotencialização segundo os parâmetros definidos na norma ANSI/TIA-607-D. Todos os racks de telecomunicações dos andares foram conectados à barra de aterramento principal (TMGB) através do condutor backbone de aterramento.",
                "afirmativas": "Com base nas normas de aterramento e proteção de sistemas de telecomunicações, analise as afirmativas:\n\nI. A equipotencialização de todos os racks e painéis de patch panel blindados ao sistema de aterramento de telecomunicações é indispensável para drenar correntes induzidas e descargas eletrostáticas para a terra.\n\nPORQUE\n\nII. O acúmulo de cargas estáticas ou diferenças de potencial terra entre edifícios conectados por cabos de cobre blindados pode causar danos permanentes às portas dos switches de rede e riscos de choque aos operadores.",
                "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
                "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
                "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
                "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
                "opt_d": "As afirmativas I e II são falsas.",
                "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A norma TIA-607 exige a ligação equipotencial para drenar ruídos e surtos elétricos, prevenindo surtos de tensão que danificam interfaces ativas de rede.\nFonte: Cabeamento Estruturado II, UA 10."
            }
        ]
    },

    # 2. Compiladores
    {
        "folder": "Compiladores",
        "name": "Compiladores",
        "title": "AI Compiladores",
        "uas": "2; 3; 5; 8",
        "questions": [
            {
                "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Análise Léxica e Autômatos Finitos",
                "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
                "context_text": "Durante a primeira fase de compilação de um código C++, o analisador léxico (Scanner) processa o fluxo de caracteres do código-fonte para reconhecer os lexemas e convertê-los em uma sequência de tokens válidos, descartando espaços em branco e comentários.",
                "afirmativas": "",
                "comando_text": "A estrutura formal utilizada teoricamente para implementar o reconhecimento de tokens em um analisador léxico é [lacuna]",
                "opt_a": "o Autômato Finito Determinístico (AFD).", "opt_b": "a Árvore Sintática Abstrata (AST).", "opt_c": "a Tabela de Símbolos LR(1).", "opt_d": "a Máquina de Turing de Fita Dupla.",
                "feedback": "A resposta certa é o Autômato Finito Determinístico (AFD).\nComentário: O analisador léxico baseia-se em expressões regulares e Autômatos Finitos Determinísticos para reconhecer padrões de lexemas e emitir os respectivos tokens.\nFonte: Compiladores, UA 2."
            },
            {
                "ua": "03", "obj": 2, "grau": "MÉDIA", "kw": "Análise Sintática Preditiva LL(1)",
                "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
                "context_text": "Um projetista de compiladores está construindo um analisador sintático descendente (Top-Down) do tipo LL(1) para uma linguagem de programação estruturada. Durante a elaboração da gramática livre de contexto, ele observa que a presença de recursão à esquerda impede a análise preditiva sem retrocesso.",
                "afirmativas": "",
                "comando_text": "Para tornar uma gramática recursiva à esquerda apta para ser analisada por um parser LL(1), o compilador deve aplicar o procedimento de [lacuna]",
                "opt_a": "eliminação da recursão à esquerda e fatoração à esquerda da gramática.", "opt_b": "inversão da ordem dos tokens na tabela de símbolos.", "opt_c": "conversão direta da gramática em um autômato de pilha não determinístico.", "opt_d": "substituição de todas as variáveis não terminais por constantes numéricas.",
                "feedback": "A resposta certa é eliminação da recursão à esquerda e fatoração à esquerda da gramática.\nComentário: Parsers LL(1) entram em loop infinito na presença de recursão à esquerda direta ou indireta; portanto, a eliminação da recursão à esquerda é pré-requisito obrigatório.\nFonte: Compiladores, UA 3."
            },
            {
                "ua": "05", "obj": 3, "grau": "DIFÍCIL", "kw": "Análise Semântica e Esquemas de Tradução",
                "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
                "context_text": "Na etapa de análise semântica, o compilador verifica a coerência dos tipos de dados nas atribuições e operações aritméticas. Para isso, utiliza uma Definição Dirigida pela Sintaxe (DDS) onde os atributos das variáveis não terminais são calculados ao longo dos nós da árvore sintática.",
                "afirmativas": "Com base nos conceitos de tradução dirigida pela sintaxe e verificação de tipos, analise as afirmativas:\nI. Atributos sintetizados em uma nó da árvore dependem apenas dos valores dos atributos dos seus nós filhos.\nII. Atributos herdados podem depender dos valores dos atributos do nó pai e dos seus nós irmãos na árvore sintática.\nIII. A verificação de coerência de tipos em tempo de compilação é uma tarefa exclusiva da fase de análise léxica.",
                "comando_text": "É correto o que se afirma em:",
                "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
                "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II definem corretamente atributos sintetizados e herdados. A afirmativa III é falsa pois a verificação de tipos é realizada na análise semântica, não na léxica.\nFonte: Compiladores, UA 5."
            },
            {
                "ua": "08", "obj": 1, "grau": "DIFÍCIL", "kw": "Geração de Código Intermediário e Otimização",
                "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
                "context_text": "A fase de otimização de código de um compilador busca transformar o código intermediário (como o código de três endereços - TAC) em uma versão equivalente mais rápida e que consome menos memória, antes da geração do código assembly final da arquitetura-alvo.",
                "afirmativas": "Com base nas técnicas de otimização de código e alocação de registradores, analise as afirmativas:\nI. A eliminação de subexpressões comuns identifica e reutiliza o resultado de cálculos idênticos dentro de um mesmo bloco básico.\nII. O desdobramento de laços (loop unrolling) reduz a sobrecarga de saltos condicionais e manipulação de contadores de laço.\nIII. O código intermediário deve depender estritamente dos registradores físicos da CPU para garantir portabilidade entre diferentes processadores.",
                "comando_text": "É correto o que se afirma em:",
                "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
                "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II apresentam técnicas clássicas de otimização de código intermediário. A afirmativa III é falsa pois a representação intermediária (IR) é independente de arquitetura para permitir portabilidade.\nFonte: Compiladores, UA 8."
            },
            {
                "ua": "08", "obj": 2, "grau": "DIFÍCIL", "kw": "Alocação de Registradores por Coloração de Grafos",
                "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
                "context_text": "Na geração final de código de máquina para arquiteturas RISC-V ou x86_64, o compilador deve mapear um número ilimitado de variáveis temporárias em um número restrito de registradores físicos do processador.",
                "afirmativas": "Com base no algoritmo de alocação de registradores por coloração de grafos de interferência, analise as afirmativas:\n\nI. A construção do grafo de interferência conecta dois registradores virtuais por uma aresta sempre que ambas as variáveis estiverem 'vivas' (live) simultaneamente no mesmo ponto do programa.\n\nPORQUE\n\nII. Se o número cromático necessário para colorir o grafo de interferência for maior do que o número de registradores físicos disponíveis na CPU, o compilador deve realizar o 'spill' de registradores, salvando valores temporários na memória Stack.",
                "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
                "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
                "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
                "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
                "opt_d": "As afirmativas I e II são falsas.",
                "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A interferência entre variáveis vivas impede que compartilhem o mesmo registrador físico; caso faltem registradores físicos (k-coloração), o spill para a pilha é obrigatório.\nFonte: Compiladores, UA 8."
            }
        ]
    }
]

# Executar a geração das disciplinas já prontas
for disc in all_disciplines_data:
    create_discipline_exam(disc['folder'], disc['name'], disc['title'], disc['uas'], disc['questions'])

print("Construção parcial concluída.")
