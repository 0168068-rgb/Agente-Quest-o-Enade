# -*- coding: utf-8 -*-
"""
Script de Geração em Lote de Provas AI 2026-4 para 22 Disciplinas NEAD.
Atende estritamente às regras de formatação ENADE, 4 alternativas (A-D),
nomenclatura padronizada no Excel e Word, e salvamento na pasta 'Provas 2026-4/AI' de cada disciplina.
"""
import os, sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

sys.path.append('/home/hamilcar/Antigravity/agente_gerador_questoes_enade/src')
from docx_exporter import ENADEDocxExporter

nead_path = '/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD'

# Definição dos Dados das 22 Disciplinas com Questões Técnicas ENADE
exams_data = [
    # 1. Cabeamento estruturado II
    {
        "folder": "Cabeamento estruturado II (seg)",
        "file_title": "AI Cabeamento Estruturado II",
        "discipline_name": "Cabeamento Estruturado II",
        "questions": [
            {
                "ua": "05", "q_num": 1, "obj": 1, "grau": "MÉDIA", "kw": "Norma ANSI/TIA-568 e Categorias de Cabos",
                "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
                "base_text": "Em um projeto de infraestrutura de cabeamento estruturado para um centro de dados corporativo, a equipe de engenharia precisa selecionar os subsistemas de cabeamento e categorias de par trançado blindado (S/FTP) capazes de suportar taxas de transmissão de até 10 Gbps em frequências de até 500 MHz, respeitando os limites de distância da norma ANSI/TIA-568.2-D.\n\nPergunta: Considerando a classificação das normas internacionais de cabeamento estruturado, a categoria de cabo de par trançado que atende de forma exata às especificações para 10GBASE-T a 500 MHz é a [lacuna]",
                "opt_a": "Categoria 6A (Cat6A).", "opt_b": "Categoria 5e (Cat5e).", "opt_c": "Categoria 3 (Cat3).", "opt_d": "Categoria 5 (Cat5).",
                "feedback": "A resposta certa é Categoria 6A (Cat6A).\nComentário: A norma ANSI/TIA-568.2-D especifica que a Categoria 6A opera em frequências de até 500 MHz e suporta a aplicação 10GBASE-T em distâncias de até 100 metros.\nFonte: Cabeamento Estruturado II, UA 5."
            },
            {
                "ua": "06", "q_num": 2, "obj": 2, "grau": "MÉDIA", "kw": "Certificação de Redes de Cobre e Parâmetros NEXT/FEXT",
                "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
                "base_text": "Durante o processo de comissionamento de uma rede de cabeamento estruturado em um edifício comercial, um técnico utiliza um certficador de rede de campo (Pentascanner/OTDR) para validar os links permanentes de cobre. O relatório acusou falhas de diafonia na extremidade próxima (NEXT - Near-End Crosstalk) em diversos pontos da sala de telecomunicações.\n\nPergunta: Com base nas boas práticas de conectorização e normas de certificação de cabeamento, a causa primária para o alto nível de ruído por NEXT em conectores RJ-45 é [lacuna]",
                "opt_a": "o destrançamento excessivo dos pares de fios no momento da crimpagem nos conectores fêmea.", "opt_b": "o uso de patch cords com comprimento inferior a 0,5 metros.", "opt_c": "a instalação dos cabos em canaletas plásticas exclusivas sem cabos elétricos.", "opt_d": "a utilização de tomadas de telecomunicações com contatos banhados a ouro.",
                "feedback": "A resposta certa é o destrançamento excessivo dos pares de fios no momento da crimpagem nos conectores fêmea.\nComentário: O destrançamento dos pares acima do limite especificado pelas normas (máximo 13 mm para Cat6/6A) expõe os condutores ao acoplamento eletromagnético mútuo, causando degradação do parâmetro NEXT.\nFonte: Cabeamento Estruturado II, UA 6."
            },
            {
                "ua": "09", "q_num": 3, "obj": 3, "grau": "DIFÍCIL", "kw": "Redes de Fibras Ópticas e Emendas por Fusão",
                "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
                "base_text": "Texto-base: Uma empresa de telecomunicações está implantando o cabeamento de backbone óptico entre dois edifícios separados por 3 km. O projeto prevê a utilização de fibras ópticas monomodo (SMF) conectorizadas em distribuidores internos ópticos (DIO). Durante a fusão de duas extensões de cabo óptico utilizando uma máquina de fusão por alinhamento pela casca/núcleo, a equipe precisa garantir a menor atenuação possível na emenda e validar o link com um refletômetro óptico no domínio do tempo (OTDR).\n\nCom base nas técnicas de conectorização, emendas e testes em redes ópticas, analise as afirmativas:\nI. A fusão de fibras monomodo exige a clivagem precisa da face da fibra em ângulo reto (90°) para minimizar as perdas por inserção e o retorno óptico (ORL).\nII. O uso de fibras ópticas multimodo em substituição às monomodo reduziria a dispersão modal em links de longa distância acima de 2 km.\nIII. O evento de fusão na curva do OTDR é identificado como uma atenuação localizada (degrau de perda não reflexivo).\n\nPergunta: É correto o que se afirma em:",
                "opt_a": "I e III, apenas.", "opt_b": "I e II, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
                "feedback": "A resposta certa é I e III, apenas.\nComentário: As afirmativas I e III são corretas. A clivagem perfeita é essencial para fusões ópticas de baixa perda. A curva do OTDR exibe fusões como eventos atenuativos não reflexivos. A afirmativa II é falsa porque fibras multimodo possuem alta dispersão modal em comparação com fibras monomodo em links longos.\nFonte: Cabeamento Estruturado II, UA 9."
            },
            {
                "ua": "10", "q_num": 4, "obj": 1, "grau": "DIFÍCIL", "kw": "Gerenciamento de Infraestrutura e Data Center (TIA-942)",
                "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
                "base_text": "Texto-base: O gerente de TI de uma instituição financeira supervisiona a modernização da Sala de Equipamentos (ER) e dos racks do Data Center. O projeto adota a norma ANSI/TIA-942 e estabelece a separação dos caminhos de cabeamento óptico e de cobre através de leitos de cabos suspensos (calhas tipo calha aramada), além da organização térmica por corredores quentes e frios (Hot/Cold Aisle).\n\nCom base nas normas de gerenciamento e infraestrutura de Data Centers, analise as afirmativas:\nI. A organização em corredores quentes e frios exige que os racks fiquem dispostos de frente para frente (recebendo ar frio do piso elevado) e de costas para costas (expelindo ar quente para o exaustor).\nII. A mistura de cabos de energia elétrica de alta voltagem no mesmo leito de cabos de dados de cobre sem blindagem é recomendada para economizar espaço físico nos Racks.\nIII. A identificação e etiquetagem dos cabos e painéis de conexão deve seguir a norma ANSI/TIA-606-C para permitir rastreabilidade de ponta a ponta.\n\nPergunta: É correto o que se afirma em:",
                "opt_a": "I e III, apenas.", "opt_b": "I e II, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
                "feedback": "A resposta certa é I e III, apenas.\nComentário: A afirmativa I descreve com precisão a disposição térmica Hot/Cold Aisle da TIA-942. A afirmativa III destaca a norma TIA-606-C de identificação. A afirmativa II é falsa pois a convivência de cabos de potência e dados no mesmo leito gera ruído por indução eletromagnética.\nFonte: Cabeamento Estruturado II, UA 10."
            },
            {
                "ua": "10", "q_num": 5, "obj": 2, "grau": "DIFÍCIL", "kw": "Sistema de Aterramento de Telecomunicações (ANSI/TIA-607)",
                "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
                "base_text": "Texto-base: Em um edifício comercial de múltiplos andares, a infraestrutura de telecomunicações requer um sistema dedicado de aterramento e equipotencialização segundo os parâmetros definidos na norma ANSI/TIA-607-D. Todos os racks de telecomunicações dos andares foram conectados à barra de aterramento principal (TMGB) através do condutor backbone de aterramento.\n\nCom base nas normas de aterramento e proteção de sistemas de telecomunicações, analise as afirmativas:\n\nI. A equipotencialização de todos os racks e painéis de patch panel blindados ao sistema de aterramento de telecomunicações é indispensável para drenar correntes induzidas e descargas eletrostáticas para a terra.\n\nPORQUE\n\nII. O acúmulo de cargas estáticas ou diferenças de potencial terra entre edifícios conectados por cabos de cobre blindados pode causar danos permanentes às portas dos switches de rede e riscos de choque aos operadores.\n\nPergunta: A respeito dessas afirmativas, assinale a opção correta:",
                "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
                "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
                "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
                "opt_d": "As afirmativas I e II são falsas.",
                "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A norma TIA-607 exige a ligação equipotencial para drenar ruídos e surtos elétricos, prevenindo surtos de tensão que danificam interfaces ativas de rede.\nFonte: Cabeamento Estruturado II, UA 10."
            }
        ]
    }
]

print("Script de inicialização de estrutura concluído.")
