import os
import subprocess
import docx
from docx.table import Table
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

TEMPLATES_DIR = '/home/hamilcar/Antigravity/Atas de NDE/templates'
LOCAL_OUTPUT_DIR = '/home/hamilcar/Antigravity/Atas de NDE/atas_geradas_redes'
os.makedirs(LOCAL_OUTPUT_DIR, exist_ok=True)

# Templates Redes
TEMPLATE_REDES_NDE = os.path.join(TEMPLATES_DIR, 'redes_nde_15_jul_existing.docx')
TEMPLATE_REDES_COL = os.path.join(TEMPLATES_DIR, 'redes_col_18_jul_existing.docx')

# URIs Local 1: Cursos NEAD-Atual 2023
URI_NEAD2023_NDE = 'google-drive://0168068@professor.unig.edu.br/GVfsSharedWithMe/1CCAfj2zR02OVB6ZK8aKDSswSWWgN9d0Z/1SBMeiQgzv4LLNnwFb3eyo4oq0xW3A-S6/1eQlILuwTdNITEeEnQ6bTqgzxzaLR3SMo/1w6uKH5djDAmVxRfqju0-Mwpb_emyf7sf'
URI_NEAD2023_COL = 'google-drive://0168068@professor.unig.edu.br/GVfsSharedWithMe/1CCAfj2zR02OVB6ZK8aKDSswSWWgN9d0Z/1SBMeiQgzv4LLNnwFb3eyo4oq0xW3A-S6/1S3uBVszKVIIq0ABznQWZP-lPe55OiBjN/15gUBxDw9dEgAQQ3aJuI5a2AtXielakaZ'

# URIs Local 2: _MEC_CURSOS_NEAD-2026
URI_MEC_NDE = 'google-drive://0168068@professor.unig.edu.br/GVfsSharedWithMe/1OVWk6s2LEwXOp_jAQNacFZtVBSrS9r8i/1wm6ptLxn07qiNjEBWbSB4wvBcmw9jYsw/1C2v4jjsQ2tDABNSri1P8-e7hggwCsBEA/1rlAKDJLkBBNlbCMhHyVki_bSD5nPv-w8/1uv74MiLvqWLyu8YFzdiV4q999ymYLpwD/1Hvm916_nn8Xp9AJYrzqCIf6LDRaWRyby/1tESlmaGr5ZHXKrnyhK9GgBbuCEojvSMk/1BuU4XnGQjazWq3p4a9xXLEFFqgQHyCpm'
URI_MEC_COL = 'google-drive://0168068@professor.unig.edu.br/GVfsSharedWithMe/1OVWk6s2LEwXOp_jAQNacFZtVBSrS9r8i/1wm6ptLxn07qiNjEBWbSB4wvBcmw9jYsw/1C2v4jjsQ2tDABNSri1P8-e7hggwCsBEA/1rlAKDJLkBBNlbCMhHyVki_bSD5nPv-w8/1uv74MiLvqWLyu8YFzdiV4q999ymYLpwD/1Hvm916_nn8Xp9AJYrzqCIf6LDRaWRyby/1atTOBCOAcABooFpDsiMCf9XIBtw9gzUA'

def set_cell_formatted(cell, text, bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, font_size=10.5):
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(font_size)
    run.bold = bold

def generate_redes_doc(template_path, rows_data, output_docx_path, semester_str="2026.1"):
    doc = docx.Document(template_path)
    
    # Ajustar semestre no cabeçalho
    for node in doc.sections[0].header._element.iter():
        if node.tag.endswith('t') and node.text and 'SEMESTRE:' in node.text:
            node.text = f"SEMESTRE: {semester_str}"
            
    body = doc._body._element
    tables = [Table(tbl, doc) for tbl in body.xpath('.//w:tbl')]
    t0 = tables[0]
    
    for idx, (c0, c1, c2) in enumerate(rows_data):
        row_idx = idx + 1
        row = t0.rows[row_idx]
        set_cell_formatted(row.cells[0], c0, bold=(idx == 0 or idx == len(rows_data)-1), align=WD_ALIGN_PARAGRAPH.LEFT)
        set_cell_formatted(row.cells[1], c1, bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        set_cell_formatted(row.cells[2], c2, bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        
    # Corrigir eventual typo 'Professsor' na tabela de assinaturas (t1)
    if len(tables) > 1:
        t1 = tables[1]
        for row in t1.rows:
            for cell in row.cells:
                if 'Professsor' in cell.text:
                    cell.text = cell.text.replace('Professsor', 'Professor')
        
    doc.save(output_docx_path)
    print(f"Salvo docx: {output_docx_path}")
    
    # PDF conversion
    pdf_dir = os.path.dirname(output_docx_path)
    subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', output_docx_path, '--outdir', pdf_dir], capture_output=True)
    pdf_path = output_docx_path.replace('.docx', '.pdf')
    pdf_double_ext = output_docx_path + '.pdf'
    if os.path.exists(pdf_path):
        subprocess.run(['cp', pdf_path, pdf_double_ext])
        print(f"Gerado PDF: {pdf_double_ext}")

def ensure_gdrive_folder(parent_uri, folder_name):
    target_uri = f"{parent_uri}/{folder_name}"
    check = subprocess.run(['gio', 'info', target_uri], capture_output=True, text=True)
    if check.returncode == 0:
        print(f"Pasta já existe: {folder_name}")
    else:
        mk = subprocess.run(['gio', 'mkdir', target_uri], capture_output=True, text=True)
        if mk.returncode == 0:
            print(f"Criada pasta no Google Drive: {folder_name}")
        else:
            print(f"Aviso/Erro ao criar pasta {folder_name}: {mk.stderr.strip()}")
    return target_uri

def copy_to_gdrive(local_file, target_folder_uri):
    fname = os.path.basename(local_file)
    dest_uri = f"{target_folder_uri}/{fname}"
    print(f"Copiando {fname} para {target_folder_uri} ...")
    cp = subprocess.run(['gio', 'copy', local_file, dest_uri], capture_output=True, text=True)
    if cp.returncode == 0:
        print(f" -> Sucesso: {fname}")
    else:
        print(f" -> Erro ao copiar {fname}: {cp.stderr.strip()}")

def copy_file_and_pdf(local_docx, target_uri, copy_pdf=True):
    copy_to_gdrive(local_docx, target_uri)
    if copy_pdf:
        pdf_double = local_docx + '.pdf'
        if os.path.exists(pdf_double):
            copy_to_gdrive(pdf_double, target_uri)

# ==============================================================================
# CONTEÚDOS DAS ATAS DE CST REDES DE COMPUTADORES (UNIG / NEAD)
# ==============================================================================

# 1. NDE 2026.1 (2ª Reunião - 15 de julho de 2026)
nde_redes_26_1_rows = [
    (
        "Abertura",
        "A reunião do Núcleo Docente Estruturante do Curso Superior de Tecnologia em Redes de Computadores foi iniciada pelo coordenador do curso, Professor Hamilcar Pereira da Silva, que saudou os docentes presentes e constatou o quórum regulamentar da comissão. Os professores Sidnei Castilhos Rodrigues, Giana Laport Alves de Souza, Telmo Viana Rodrigues e Simone Christina Rebello Barros declararam concordância com os tópicos da pauta de trabalho e deram início às atividades de planejamento e avaliação acadêmica.",
        "SEM SUGESTÕES."
    ),
    (
        "Fomento à Participação Discente em Eventos de Intercurso",
        "O coordenador do curso, Professor Hamilcar Pereira da Silva, discorreu sobre a necessidade de impulsionar a participação dos estudantes no evento acadêmico de intercurso, estimulando a atuação discente como ouvintes ou palestrantes de projetos técnicos. O professor Sidnei Castilhos Rodrigues sugeriu a concessão de incentivos acadêmicos na forma de horas adicionais em atividades complementares para os alunos que submeterem trabalhos práticos. A professora Giana Laport Alves de Souza propôs a estruturação de plantões de orientação e tutoria específica para auxiliar os discentes na redação de resumos expandidos e na formatação das apresentações públicas de seus projetos.",
        "Criar comissão interna de mentoria para submissões científicas e emitir resolução sobre aproveitamento especial de atividades complementares para participantes do evento."
    ),
    (
        "Estratégias de Engajamento para o ENADE 2026",
        "O coordenador, Professor Hamilcar Pereira da Silva, pontuou a importância institucional do Exame Nacional de Desempenho dos Estudantes e a urgência em elaborar um plano de ação robusto focado no engajamento dos alunos concluintes deste ciclo avaliativo. O professor Telmo Viana Rodrigues propôs o desenvolvimento e a aplicação regular de simulados específicos da área de infraestrutura de redes e roteamento por meio do Ambiente Virtual de Aprendizagem, utilizando questões de edições anteriores do exame. A professora Simone Christina Rebello Barros reforçou a importância do acompanhamento docente na elaboração de feedbacks detalhados e sessões de esclarecimento de dúvidas para as questões de formação geral e componente específico.",
        "Elaborar banco de questões preparatórias no AVA e instituir encontros virtuais periódicos de nivelamento teórico-prático com os discentes concluintes."
    ),
    (
        "Aprimoramento do Monitoramento de Acessos no AVA",
        "O coordenador, Professor Hamilcar Pereira da Silva, apresentou dados consolidados referentes à frequência e navegação dos alunos no Ambiente Virtual de Aprendizagem, chamando atenção para taxas pontuais de inatividade. A professora Giana Laport Alves de Souza defendeu que a equipe de tutoria atue de forma imediata estabelecendo contato direto com discentes com mais de cinco dias consecutivos sem acesso às salas de aula virtuais. A professora Simone Christina Rebello Barros complementou sugerindo que sejam criados painéis gerenciais de controle que ajudem a monitorar preventivamente os índices de engajamento discente semanais por disciplina.",
        "Normatizar o protocolo de busca ativa discente para a tutoria do NEAD e emitir relatórios de acompanhamento de acessos a cada quinze dias para a coordenação."
    ),
    (
        "Incorporação de Tecnologias Emergentes e Laboratórios Virtuais no Currículo",
        "O coordenador, Professor Hamilcar Pereira da Silva, ressaltou a importância de atualizar continuamente a matriz pedagógica do curso de Redes, incorporando novas ferramentas de virtualização e ambientes em nuvem. O professor Sidnei Castilhos Rodrigues sugeriu que as referências bibliográficas básicas e complementares do PPC fossem revisadas para incorporar manuais atualizados de computação em nuvem e segurança de perímetros virtuais. O professor Telmo Viana Rodrigues recomendou a ampliação da utilização de emuladores e laboratórios virtuais de redes avançados e integrados ao AVA para permitir a realização de práticas complexas de configuração remota.",
        "Revisar as ementas das disciplinas práticas no PPC para contemplar competências em nuvem e firmar novas licenças de laboratórios virtuais simulados."
    ),
    (
        "Encerramento",
        "Não havendo mais pautas ou assuntos a tratar na presente reunião, o coordenador do curso, Professor Hamilcar Pereira da Silva, agradeceu as importantes contribuições e o engajamento de todos os membros presentes. Declarou-se formalmente encerrada a sessão, da qual foi lavrada a presente ata que, lida e achada conforme, será assinada por todos os presentes e arquivada nos registros acadêmicos do NEAD.",
        "Sem sugestões."
    )
]

# 2. COLEGIADO 2026.1 (2ª Reunião - 18 de julho de 2026)
col_redes_26_1_rows = [
    (
        "Abertura",
        "No dia dezoito de julho de dois mil e vinte e seis, realizou-se a reunião ordinária do Colegiado do Curso Superior de Tecnologia em Redes de Computadores da Universidade Iguaçu (UNIG/NEAD), sob a presidência do coordenador Professor Hamilcar Pereira da Silva, com quórum regimental atestado pela presença dos docentes Rodrigo Bandeira Marra, Telmo Viana Rodrigues, Ronaldo Paulicci de Assis e do representante discente Sebastião Goulart da Silva. O presidente iniciou a sessão agradecendo a presença dos membros e apresentando as pautas prioritárias oriundas das análises pedagógicas do Núcleo Docente Estruturante (NDE).",
        "Não aplicável."
    ),
    (
        "Fomento à Participação Discente em Eventos de Intercurso",
        "Apresentação da proposta do NDE de fomento à participação estudantil no evento acadêmico integrado de intercurso. O professor Rodrigo Bandeira Marra ressaltou que a apresentação de projetos de infraestrutura de redes eleva a prática acadêmica dos alunos. O docente Telmo Viana Rodrigues sugeriu que fossem atribuídas pontuações de horas complementares diferenciadas como principal fator de estímulo discente. O professor Ronaldo Paulicci de Assis propôs a realização de minicursos preparatórios conduzidos por professores tutores para orientar os alunos nas submissões. O representante discente Sebastião Goulart da Silva reforçou que a divulgação ampla nos canais digitais do curso facilitará a adesão estudantil.",
        "APROVADO por unanimidade. Determina-se a edição do regulamento para concessão especial de horas complementares e a elaboração do cronograma de mentoria técnica para submissões."
    ),
    (
        "Estratégias de Engajamento para o ENADE 2026",
        "Apresentação do plano de ação preparado pelo NDE para a preparação acadêmica e elevação do engajamento dos discentes concluintes elegíveis para o Exame Nacional de Desempenho dos Estudantes de dois mil e vinte e seis. O professor Ronaldo Paulicci de Assis defendeu a aplicação de simulados periódicos estruturados no Ambiente Virtual de Aprendizagem contendo questões comentadas de edições anteriores. O docente Telmo Viana Rodrigues propôs a realização de oficinas síncronas focadas na resolução coletiva e apreciação detalhada de casos conceituais complexos em rede e roteamento. O professor Rodrigo Bandeira Marra sugeriu o monitoramento contínuo dos resultados discentes. O discente Sebastião Goulart da Silva corroborou as propostas, assinalando que os feedbacks detalhados auxiliam expressivamente na retenção das competências exigidas.",
        "APROVADO por unanimidade. Delibera-se pelo lançamento imediato dos simulados preparatórios no AVA e definição do calendário de oficinas síncronas."
    ),
    (
        "Aprimoramento do Monitoramento de Acessos no AVA",
        "Apreciação da proposta pedagógica do NDE para o aperfeiçoamento das rotinas de monitoramento da frequência discente no Ambiente Virtual de Aprendizagem, servindo como ferramenta de prevenção ativa da evasão escolar. O professor Rodrigo Bandeira Marra recomendou a indicação de acionamento preventivo de busca ativa pela tutoria caso o aluno permaneça sem acesso por cinco dias úteis consecutivos. O professor Ronaldo Paulicci de Assis propôs a qualificação contínua dos retornos pedagógicos dados pelos tutores para manter a motivação estudantil. O professor Telmo Viana Rodrigues sugeriu o envio automático de comunicados preventivos. O discente Sebastião Goulart da Silva reforçou a importância do pronto suporte dos tutores para a superação de eventuais dificuldades técnicas de acesso.",
        "APROVADO por unanimidade. Homologa-se o plano de busca ativa preventiva no AVA em articulação sistemática com a equipe de tutoria do NEAD."
    ),
    (
        "Incorporação de Tecnologias Emergentes e Laboratórios Virtuais no Currículo",
        "Apreciação da proposta de adequação curricular e modernização de ementas e referências bibliográficas do PPC do curso de Redes de Computadores para a inclusão de tecnologias de virtualização e computação em nuvem. O professor Telmo Viana Rodrigues destacou a importância de homologar o uso de emuladores e simuladores virtuais integrados às Unidades de Aprendizagem do AVA para realização de atividades práticas. O professor Rodrigo Bandeira Marra sugeriu a substituição e inserção de literatura atualizada focada em arquiteturas de redes definidas por software. O professor Ronaldo Paulicci de Assis e o representante discente Sebastião Goulart da Silva enfatizaram que a modernização prática do currículo amplia a competitividade no mercado de trabalho de TI.",
        "APROVADO por unanimidade. Determina-se o envio formal das atualizações bibliográficas e planos práticos de laboratório para aprovação no Colegiado Superior e correspondente inclusão no PPC do curso."
    ),
    (
        "Encerramento",
        "Esgotados os temas definidos para a pauta da reunião ordinária do Colegiado de Curso de Redes de Computadores, o presidente, Professor Hamilcar Pereira da Silva, registrou os agradecimentos finais aos membros presentes pelas contribuições institucionais de relevo acadêmico. Declarou-se encerrada a sessão da qual eu, na qualidade de secretário acadêmico, lavrei a presente ata, que lida, apreciada e aprovada, será assinada eletronicamente pelos membros e publicada nos meios oficiais.",
        "Não aplicável."
    )
]

# 3. NDE 2026.2 (1ª Reunião - 10 de agosto de 2026)
nde_redes_26_2_1_rows = [
    (
        "Abertura",
        "A reunião do Núcleo Docente Estruturante do Curso Superior de Tecnologia em Redes de Computadores da Universidade Iguaçu - UNIG/NEAD realizou-se no dia dez de agosto de dois mil e vinte e seis, às 14 horas, sob a coordenação do Prof. Hamilcar Pereira da Silva, com quórum regimental pleno pela presença dos docentes Sidnei Castilhos Rodrigues, Giana Laport Alves de Souza, Telmo Viana Rodrigues e Simone Christina Rebello Barros. O coordenador deu as boas-vindas para o segundo semestre letivo de 2026, abrindo os trabalhos focados nas diretrizes pedagógicas e de infraestrutura técnica para o período.",
        "SEM SUGESTÕES."
    ),
    (
        "Acolhimento Discente, Guia do AVA e Nivelamento em Arquitetura de Redes",
        "O coordenador do curso, Professor Hamilcar Pereira da Silva, abriu a discussão destacando a necessidade de estruturar ações de acolhimento pedagógico para os ingressantes e veteranos do semestre 2026.2, com ênfase na navegação no AVA e ambientação nas salas de aula virtuais. A professora Giana Laport Alves de Souza propôs a realização de encontros síncronos de nivelamento introdutório sobre fundamentos de telecomunicações e modelos OSI/TCP-IP durante as primeiras três semanas. O professor Sidnei Castilhos Rodrigues complementou indicando a criação de um guia rápido em formato interativo para instalação e uso de simuladores de redes nos computadores pessoais dos discentes. A comissão acolheu a proposta, enfatizando o papel do nivelamento na mitigação de retenções prematuras.",
        "Implantar a trilha síncrona de nivelamento em fundamentos de redes no AVA e disponibilizar guia instrucional de simulação computacional aos estudantes na primeira quinzena letiva."
    ),
    (
        "Atualização dos Bancos de Questões e Cronograma da Avaliação Integrada (AI) de 2026.2",
        "O coordenador, Professor Hamilcar Pereira da Silva, apresentou o cronograma de elaboração e validação dos itens avaliativos para a Avaliação Integrada do período 2026.2. O professor Telmo Viana Rodrigues defendeu que as questões contemplem estudos de caso contextualizados, alinhados à matriz de referência do ENADE e abordando desafios práticos de roteamento, switching e serviços em nuvem. A professora Simone Christina Rebello Barros ressaltou a importância de manter um equilíbrio pedagógico rigoroso entre questões conceituais e problemas de aplicação prática de mercado, além da revisão por pares de cada item antes da inclusão no sistema avaliativo institucional. O NDE estabeleceu o cronograma de entrega das questões pelos docentes responsáveis.",
        "Consolidar a matriz de competências da Avaliação Integrada e validar os itens inéditos do banco de questões até a quarta semana de aulas de 2026.2."
    ),
    (
        "Adequação Curricular e Laboratórios Virtuais de Segurança de Redes e Serviços Cloud",
        "O coordenador colocou em debate a necessidade de expandir as práticas de laboratório em ambientes emulados nas disciplinas de Segurança da Informação, Cibersegurança e Computação em Nuvem. O professor Sidnei Castilhos Rodrigues salientou a conveniência de integrar cenários de contenção de incidentes de rede e configuração de firewalls virtuais nas Unidades de Aprendizagem do curso. O professor Telmo Viana Rodrigues propôs a padronização de roteiros de prática remota utilizando ferramentas open source consolidadas e imagens de switches virtuais pré-configurados, permitindo que alunos com diferentes configurações de hardware executem os exercícios com estabilidade.",
        "Homologar novos roteiros práticos emulados para as disciplinas de Segurança e Cloud Computing e atualizar a bibliografia complementar das respectivas ementas no PPC."
    ),
    (
        "Monitoramento Pedagógico Preventivo de Evasão e Busca Ativa na Tutoria Online",
        "O coordenador apresentou o plano semestral de combate à evasão discente no NEAD, destacando a importância do monitoramento sistemático de acessos e postagem de atividades avaliativas. A professora Simone Christina Rebello Barros sugeriu o cruzamento de relatórios de frequência quinzenais gerados pelo AVA com intervenções amigáveis e acolhedoras por parte dos professores tutores. A professora Giana Laport Alves de Souza defendeu que seja estabelecido um protocolo prioritário de contato com discentes que acumularem sete dias sem acesso, investigando eventuais entraves de conectividade ou dificuldades conceituais para assegurar a permanência do aluno no curso.",
        "Adotar painel quinzenal de alerta precoce de acessos no AVA e pactuar rotinas de contato ativo com a equipe de tutoria a partir da segunda semana de aulas."
    ),
    (
        "Encerramento",
        "Não havendo mais temas a serem apreciados, o coordenador Prof. Hamilcar Pereira da Silva agradeceu o comprometimento dos docentes e declarou encerrada a sessão de planejamento do semestre 2026.2. Eu, na qualidade de secretário ad hoc, lavrei a presente ata que segue lida, achada conforme e assinada pelos membros presentes.",
        "Sem sugestões."
    )
]

# 4. COLEGIADO 2026.2 (1ª Reunião - 17 de agosto de 2026)
col_redes_26_2_1_rows = [
    (
        "Abertura",
        "Aos dezessete dias do mês de agosto de dois mil e vinte e seis, às 14h, reuniu-se ordinariamente o Colegiado do Curso Superior de Tecnologia em Redes de Computadores da Universidade Iguaçu - UNIG/NEAD, sob a presidência do Prof. Hamilcar Pereira da Silva, com a presença dos docentes Rodrigo Bandeira Marra, Ronaldo Paulicci de Assis, Telmo Viana Rodrigues e do representante discente Sebastião Goulart da Silva, compondo o quórum regulamentar. O presidente deu as boas-vindas ao colegiado para a condução do semestre 2026.2, saudando especialmente a representação discente.",
        "Aprovado por unanimidade. Registro formal da abertura da sessão colegiada."
    ),
    (
        "Homologação do Plano de Acolhimento Discente, Guia do AVA e Nivelamento Inicial",
        "O Colegiado apreciou a proposta pedagógica formulada pelo NDE referente às ações de acolhimento, oficinas de navegação no AVA e trilhas síncronas de nivelamento em fundamentos de redes para 2026.2. O professor Rodrigo Bandeira Marra ressaltou que a ambientação inicial é fator determinante para o sucesso dos ingressantes no modelo a distância. O professor Ronaldo Paulicci de Assis salientou a pertinência dos vídeos curtos instrucionais. O docente Telmo Viana Rodrigues destacou o valor prático das oficinas de instalação dos softwares emuladores. O representante discente Sebastião Goulart da Silva manifestou pleno apoio à proposta, indicando que o suporte rápido nas primeiras semanas gera confiança e motivação para o corpo estudantil.",
        "APROVADO por unanimidade. Homologa-se o plano de acolhimento e a implementação do módulo de nivelamento de 2026.2."
    ),
    (
        "Aprovação do Cronograma e Critérios da Avaliação Integrada (AI) para 2026.2",
        "Foi submetido à deliberação do Colegiado o calendário institucional e as diretrizes pedagógicas para a realização da Avaliação Integrada do semestre 2026.2. O professor Ronaldo Paulicci de Assis e o professor Telmo Viana Rodrigues explanaram sobre a relevância de manter questões com padrão ENADE para exercitar a capacidade crítica e analítica discente. O professor Rodrigo Bandeira Marra ressaltou a pontualidade nos períodos de abertura e encerramento das janelas de prova no AVA. O discente Sebastião Goulart da Silva reforçou a necessidade de comunicação clara dos prazos com antecedência nos murais das salas virtuais.",
        "APROVADO por unanimidade. Delibera-se pela aprovação do cronograma de elaboração, validação e aplicação da Avaliação Integrada 2026.2."
    ),
    (
        "Homologação de Roteiros Práticos de Laboratórios Virtuais em Segurança de Redes e Cloud",
        "Apreciação da proposta encaminhada pelo NDE para homologação de novos roteiros laboratoriais emulados nas disciplinas de Segurança de Perímetro, Cibersegurança e Redes em Nuvem. O professor Telmo Viana Rodrigues apresentou a modelagem dos laboratórios e sua compatibilidade com os recursos de software livre acessíveis aos alunos. O professor Rodrigo Bandeira Marra ressaltou que a formação prática emulada eleva a empregabilidade dos egressos no setor corporativo. O professor Ronaldo Paulicci de Assis e o representante discente Sebastião Goulart da Silva destacaram que as atividades práticas aproximam a teoria da realidade profissional de TI.",
        "APROVADO por unanimidade. Aprova-se a inclusão dos novos roteiros práticos laboratoriais nas ementas e salas virtuais do curso."
    ),
    (
        "Validação do Fluxo de Busca Ativa e Tutoria Preventiva contra a Evasão Escolar",
        "O Colegiado deliberou sobre o plano de monitoramento da frequência discente e engajamento nas atividades do AVA estruturado em cooperação com o NEAD. O professor Rodrigo Bandeira Marra e o professor Ronaldo Paulicci de Assis destacaram a eficiência das abordagens pedagógicas tempestivas junto aos estudantes que apresentam dificuldades de acesso. O representante discente Sebastião Goulart da Silva destacou que os alertas amigáveis via mensagens e suporte tutorial têm sido fundamentais para resgatar alunos em momentos de sobrecarga profissional.",
        "APROVADO por unanimidade. Homologam-se as diretrizes operacionais de busca ativa discente para o semestre letivo 2026.2."
    ),
    (
        "Encerramento",
        "Esgotada a pauta da reunião ordinária de Colegiado, o presidente, Prof. Hamilcar Pereira da Silva, agradeceu a produtiva colaboração dos membros do colegiado e encerrou os trabalhos. Para constar, lavrou-se a presente ata, que lida e aprovada, vai assinada pelos presentes.",
        "Aprovado por unanimidade. Encerramento formal da sessão colegiada."
    )
]

# 5. NDE 2026.2 (2ª Reunião - 11 de dezembro de 2026)
nde_redes_26_2_2_rows = [
    (
        "Abertura",
        "Aos onze dias do mês de dezembro de dois mil e vinte e seis, às 14 horas, reuniu-se o Núcleo Docente Estruturante do Curso Superior de Tecnologia em Redes de Computadores da UNIG/NEAD, sob a coordenação do Prof. Hamilcar Pereira da Silva, com quórum pleno atestado pela presença dos docentes Sidnei Castilhos Rodrigues, Giana Laport Alves de Souza, Telmo Viana Rodrigues e Simone Christina Rebello Barros. O coordenador abriu a sessão saudando os presentes e pautando o encerramento do ano letivo de 2026 e o planejamento acadêmico para 2027.",
        "SEM SUGESTÕES."
    ),
    (
        "Avaliação dos Resultados da Avaliação Integrada (AI) e Rendimento Acadêmico de 2026.2",
        "O coordenador, Professor Hamilcar Pereira da Silva, apresentou o relatório estatístico consolidado de rendimento dos alunos na Avaliação Integrada e nas atividades avaliativas do semestre 2026.2. O professor Sidnei Castilhos Rodrigues destacou o excelente desempenho dos estudantes nas questões práticas de endereçamento IP e configuração de rotas estáticas e dinâmicas. A professora Giana Laport Alves de Souza observou uma redução expressiva nas taxas de absenteísmo em relação ao semestre anterior, atribuindo o resultado ao suporte tutorial intensificado. A professora Simone Christina Rebello Barros ressaltou a eficácia dos simulados prévios e sugeriu manter o formato de feedback detalhado por questão para o próximo ano letivo.",
        "Elaborar relatório analítico de rendimento acadêmico por componente curricular e encaminhar recomendações aos docentes para intervenções formativas em 2027.1."
    ),
    (
        "Análise dos Indicadores da Autoavaliação Institucional da CPA e Percepção Discente",
        "O NDE analisou detalhadamente o relatório parcial emitido pela Comissão Própria de Avaliação (CPA) relativo ao segundo semestre de 2026. A professora Simone Christina Rebello Barros apontou que os discentes avaliaram positivamente a clareza dos materiais didáticos e a presteza no atendimento dos tutores a distância. O professor Telmo Viana Rodrigues chamou a atenção para as solicitações discentes de expansão dos períodos disponíveis para plantões síncronos de laboratório virtual. A professora Giana Laport Alves de Souza sugeriu a criação de canais centralizados de dúvidas técnicas para agilizar o suporte durante as semanas de testes práticos.",
        "Elaborar plano de ação docente respondendo aos apontamentos da CPA com foco na ampliação de horários de monitoria técnica nos laboratórios virtuais."
    ),
    (
        "Consolidação das Atividades de Extensão Curricularizada e Projetos Comunitários de Redes",
        "O coordenador apresentou o fechamento dos projetos extensionistas desenvolvidos pelos discentes no semestre, no âmbito da curricularização da extensão. O professor Sidnei Castilhos Rodrigues relatou a execução de projetos voltados à segurança digital em escolas públicas e assessoria básica em redes sem fio locais para pequenos comércios comunitários. O professor Telmo Viana Rodrigues enalteceu a alta qualidade dos relatórios técnicos e registros audiovisuais entregues pelos alunos. A comissão expressou satisfação com a plena integração entre os conhecimentos acadêmicos e o benefício social produzido pela comunidade discente.",
        "Homologar o relatório de extensão curricularizada do curso de Redes de Computadores de 2026.2 e consolidar parcerias institucionais para o primeiro semestre de 2027."
    ),
    (
        "Planejamento Docente, Atualização de Planos de Ensino e Cronograma Pedagógico para 2027.1",
        "O NDE debateu as diretrizes para o início do ano letivo de 2027.1, estabelecendo o cronograma de atualização das bibliografias básica e complementar nas ementas do curso, a revisão dos bancos de questões e a parametrização das Unidades de Aprendizagem no AVA. O coordenador solicitou que os professores encaminhem suas propostas de revisão metodológica até meados de janeiro de 2027 para validação e submissão aos órgãos superiores.",
        "Estabelecer o cronograma de entrega e validação dos planos de ensino para 2027.1 até a segunda semana de janeiro de 2027."
    ),
    (
        "Encerramento",
        "Esgotados os assuntos da ordem do dia, o coordenador Prof. Hamilcar Pereira da Silva expressou sincero agradecimento a todos os membros docentes do NDE pelo trabalho exemplar, dedicação pedagógica e rigor institucional demonstrados ao longo de 2026, encerrando oficialmente os trabalhos do ano letivo. Eu, como secretário ad hoc, lavrei a presente ata que é lida, aprovada e assinada por todos.",
        "Sem sugestões."
    )
]

# 6. COLEGIADO 2026.2 (2ª Reunião - 18 de dezembro de 2026)
col_redes_26_2_2_rows = [
    (
        "Abertura",
        "Aos dezoito dias do mês de dezembro de dois mil e vinte e seis, às 14h, reuniu-se ordinariamente o Colegiado do Curso Superior de Tecnologia em Redes de Computadores da Universidade Iguaçu - UNIG/NEAD, sob a presidência do Prof. Hamilcar Pereira da Silva, com a presença dos docentes Rodrigo Bandeira Marra, Ronaldo Paulicci de Assis, Telmo Viana Rodrigues e do representante discente Sebastião Goulart da Silva, registrando-se quórum regimental pleno. O presidente deu início aos trabalhos comemorando a finalização com êxito do ano acadêmico de 2026.",
        "Aprovado por unanimidade. Registro formal da abertura dos trabalhos."
    ),
    (
        "Homologação dos Resultados Finais da Avaliação Integrada e Desempenho Discente de 2026.2",
        "O Colegiado apreciou o relatório consolidado de notas, médias e taxas de aprovação dos estudantes de Redes de Computadores no período letivo 2026.2. O professor Rodrigo Bandeira Marra parabenizou a equipe docente pelos índices positivos de aproveitamento discente. O professor Ronaldo Paulicci de Assis destacou a efetividade do acompanhamento continuado para a consolidação dos conteúdos programáticos. O representante discente Sebastião Goulart da Silva expressou a satisfação da turma com o formato transparente e formativo das avaliações e a pontualidade nos feedbacks.",
        "APROVADO por unanimidade. Homologam-se as médias, conceitos e o resultado geral da Avaliação Integrada referente a 2026.2."
    ),
    (
        "Apreciação do Relatório da CPA e Aprovação do Plano de Melhorias do Curso",
        "O Colegiado examinou o relatório da Autoavaliação Institucional da CPA de 2026 e o respectivo plano de ação proposto pelo NDE. O professor Telmo Viana Rodrigues e o professor Rodrigo Bandeira Marra ressaltaram a relevância de acolher as sugestões discentes quanto à flexibilização dos plantões de laboratório virtual. O discente Sebastião Goulart da Silva pontuou que os alunos valorizam a escuta ativa da coordenação e a constante busca por aprimoramento dos serviços educacionais.",
        "APROVADO por unanimidade. Aprova-se o plano de ação e melhorias acadêmicas em resposta à avaliação da CPA."
    ),
    (
        "Homologação dos Resultados das Atividades de Extensão Curricularizada de 2026.2",
        "Foram apresentados ao Colegiado os relatórios comprobatórios das atividades extensionistas realizadas pelos acadêmicos de Redes de Computadores em 2026.2, destacando ações práticas em conectividade e segurança da informação aplicadas à sociedade local. O professor Ronaldo Paulicci de Assis enalteceu a maturidade profissional demonstrada pelos estudantes nos projetos comunitários. O professor Telmo Viana Rodrigues sublinhou o cumprimento integral da carga horária de extensão estipulada pelas diretrizes curriculares nacionais.",
        "APROVADO por unanimidade. Homologa-se o cumprimento da carga horária e a validação dos projetos de extensão curricularizada de 2026.2."
    ),
    (
        "Aprovação do Calendário Acadêmico Preliminar e Diretrizes Pedagógicas para 2027.1",
        "O Colegiado debateu o planejamento pedagógico e o calendário letivo preliminar para o primeiro semestre de 2027, compreendendo as datas de início das aulas no AVA, períodos de acolhimento e ambientação, semanas de avaliação e cronograma de encontros síncronos. Os membros manifestaram integral aprovação à proposta apresentada pela presidência.",
        "APROVADO por unanimidade. Delibera-se pela aprovação do calendário pedagógico inicial para o período letivo 2027.1."
    ),
    (
        "Encerramento",
        "Esgotados os temas da pauta e nada mais havendo a tratar, o presidente, Prof. Hamilcar Pereira da Silva, agradeceu a valorosa cooperação de todos os membros do Colegiado e parabenizou a comunidade do curso pelos excelentes resultados obtidos ao longo de 2026, declarando encerrada a sessão. Eu, na qualidade de secretário acadêmico, lavrei a presente ata, que lida e achada conforme, é aprovada e assinada por todos.",
        "Aprovado por unanimidade. Encerramento formal da sessão colegiada."
    )
]

# ==============================================================================
# GERAÇÃO LOCAL DOS 6 ARQUIVOS (DOCX e PDF)
# ==============================================================================

def main():
    print("=== GERAÇÃO LOCAL DOS DOCUMENTOS PARA CST REDES DE COMPUTADORES ===")

    # 1. NDE 26.1 (2ª Reunião - 15/07/2026)
    f_nde_26_1 = os.path.join(LOCAL_OUTPUT_DIR, "Ata_Reuniao_NDE_Redes_15_JUL_2026.docx")
    generate_redes_doc(TEMPLATE_REDES_NDE, nde_redes_26_1_rows, f_nde_26_1, semester_str="2026.1")

    # 2. Colegiado 26.1 (2ª Reunião - 18/07/2026)
    f_col_26_1 = os.path.join(LOCAL_OUTPUT_DIR, "Reuniao_Colegiado_Redes_18_JUL_2026.docx")
    generate_redes_doc(TEMPLATE_REDES_COL, col_redes_26_1_rows, f_col_26_1, semester_str="2026.1")

    # 3. NDE 26.2 (1ª Reunião - 10/08/2026)
    f_nde_26_2_1 = os.path.join(LOCAL_OUTPUT_DIR, "Ata_Reuniao_NDE_Redes_10_AGO_2026.docx")
    generate_redes_doc(TEMPLATE_REDES_NDE, nde_redes_26_2_1_rows, f_nde_26_2_1, semester_str="2026.2")

    # 4. Colegiado 26.2 (1ª Reunião - 17/08/2026)
    f_col_26_2_1 = os.path.join(LOCAL_OUTPUT_DIR, "Reuniao_Colegiado_Redes_17_AGO_2026.docx")
    generate_redes_doc(TEMPLATE_REDES_COL, col_redes_26_2_1_rows, f_col_26_2_1, semester_str="2026.2")

    # 5. NDE 26.2 (2ª Reunião - 11/12/2026)
    f_nde_26_2_2 = os.path.join(LOCAL_OUTPUT_DIR, "Ata_Reuniao_NDE_Redes_11_DEZ_2026.docx")
    generate_redes_doc(TEMPLATE_REDES_NDE, nde_redes_26_2_2_rows, f_nde_26_2_2, semester_str="2026.2")

    # 6. Colegiado 26.2 (2ª Reunião - 18/12/2026)
    f_col_26_2_2 = os.path.join(LOCAL_OUTPUT_DIR, "Reuniao_Colegiado_Redes_18_DEZ_2026.docx")
    generate_redes_doc(TEMPLATE_REDES_COL, col_redes_26_2_2_rows, f_col_26_2_2, semester_str="2026.2")

    print("\n=== Todos os 6 arquivos de Redes (DOCX e PDF) gerados localmente! ===")

    # ==============================================================================
    # SINCRONIZAÇÃO COM OS DOIS REPOSITÓRIOS NO GOOGLE DRIVE
    # ==============================================================================

    print("\n=== 1. Sincronizando com Cursos NEAD-Atual 2023 ===")

    # NDE 2026.1 (2ª ata: 15/07)
    copy_to_gdrive(f_nde_26_1, f"{URI_NEAD2023_NDE}/1SPYoLYYFViNHmoXMpg_ZWKu2Ji8BlAWW")

    # Colegiado 2026.1 (2ª ata: 18/07)
    copy_to_gdrive(f_col_26_1, f"{URI_NEAD2023_COL}/1ePNkAjMnO-1cLqamNDQSE8Vsju1k_XNS")

    # NDE 2026.2 (criar subpasta 2026.2 e copiar as 2 atas)
    dest_nde_2026_2 = ensure_gdrive_folder(URI_NEAD2023_NDE, "2026.2")
    copy_to_gdrive(f_nde_26_2_1, dest_nde_2026_2)
    copy_to_gdrive(f_nde_26_2_2, dest_nde_2026_2)

    # Colegiado 2026.2 (criar subpasta 2026.2 e copiar as 2 atas)
    dest_col_2026_2 = ensure_gdrive_folder(URI_NEAD2023_COL, "2026.2")
    copy_to_gdrive(f_col_26_2_1, dest_col_2026_2)
    copy_to_gdrive(f_col_26_2_2, dest_col_2026_2)

    print("\n=== 2. Sincronizando com _MEC_CURSOS_NEAD-2026 (.ATAS) ===")

    # NDE 26.1 (2ª ata: 15/07 - docx e pdf)
    copy_file_and_pdf(f_nde_26_1, f"{URI_MEC_NDE}/1FOsItz3f4JItVSc2GH3j6rXd2PVe86wF")

    # Colegiado 26.1 / 2026.1 (2ª ata: 18/07 - docx e pdf)
    copy_file_and_pdf(f_col_26_1, f"{URI_MEC_COL}/1foDpizVrmpgtUv6AUEihXuBfb0-G6FBu")

    # NDE 26.2 (criar subpasta 26.2 e copiar as 2 atas - docx e pdf)
    dest_nde_26_2 = ensure_gdrive_folder(URI_MEC_NDE, "26.2")
    copy_file_and_pdf(f_nde_26_2_1, dest_nde_26_2)
    copy_file_and_pdf(f_nde_26_2_2, dest_nde_26_2)

    # Colegiado: criar 26.2 (e 2026.2) e copiar as 2 atas
    dest_col_26_2 = ensure_gdrive_folder(URI_MEC_COL, "26.2")
    copy_file_and_pdf(f_col_26_2_1, dest_col_26_2)
    copy_file_and_pdf(f_col_26_2_2, dest_col_26_2)

    dest_col_2026_2_mec = ensure_gdrive_folder(URI_MEC_COL, "2026.2")
    copy_file_and_pdf(f_col_26_2_1, dest_col_2026_2_mec)
    copy_file_and_pdf(f_col_26_2_2, dest_col_2026_2_mec)

    print("\n=== Sincronização Redes de Computadores completa com êxito em ambos os locais! ===")

if __name__ == '__main__':
    main()
