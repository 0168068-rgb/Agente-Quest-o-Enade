import os
import subprocess
import docx
from docx.table import Table
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

TEMPLATES_DIR = '/home/hamilcar/Antigravity/Atas de NDE/templates'
LOCAL_OUTPUT_DIR = '/home/hamilcar/Antigravity/Atas de NDE/atas_geradas_gti'
os.makedirs(LOCAL_OUTPUT_DIR, exist_ok=True)

# Templates GTI
TEMPLATE_GTI_NDE = os.path.join(TEMPLATES_DIR, 'gti_nde_15_jul.docx')
TEMPLATE_GTI_COL = os.path.join(TEMPLATES_DIR, 'gti_col_18_jul.docx')

# URIs Local 1: Cursos NEAD-Atual 2023
URI_NEAD2023_NDE = 'google-drive://0168068@professor.unig.edu.br/GVfsSharedWithMe/1CCAfj2zR02OVB6ZK8aKDSswSWWgN9d0Z/1NUZsB8nI79xrf1FHAcr1C_kDt5f-AP_O/1Yg7rZ-XdsGmu_G1BWxQ3PhzRP0H8W7Hv/19u7DE8G372vzBGq3FCXAf1W_LBJvTiAT'
URI_NEAD2023_COL = 'google-drive://0168068@professor.unig.edu.br/GVfsSharedWithMe/1CCAfj2zR02OVB6ZK8aKDSswSWWgN9d0Z/1NUZsB8nI79xrf1FHAcr1C_kDt5f-AP_O/1bnS2W_-q1zBI9lSrhXrk5h8sgNSbQ5pv/1NydvgoGaTckfrE3Z2dJSsa8ST6ZfmE9W'

# URIs Local 2: _MEC_CURSOS_NEAD-2026
URI_MEC_NDE = 'google-drive://0168068@professor.unig.edu.br/GVfsSharedWithMe/1OVWk6s2LEwXOp_jAQNacFZtVBSrS9r8i/1wm6ptLxn07qiNjEBWbSB4wvBcmw9jYsw/1uj00dN_8XDEJpWzQIyhEJHRvmY8hHHr1/1VfXxysn-AB0wZjMgHsrLitICvTFkkZlr/1Lc4C6F5XKEAlmh5o8UQC748k0qs4YNRu/14mR9O7Hg6dFhfpiBhGNagJc-oO0WmcSW/1GOtuhtWVGJIplrWl8rqGDeOyiDzAbIkv'
URI_MEC_COL = 'google-drive://0168068@professor.unig.edu.br/GVfsSharedWithMe/1OVWk6s2LEwXOp_jAQNacFZtVBSrS9r8i/1wm6ptLxn07qiNjEBWbSB4wvBcmw9jYsw/1uj00dN_8XDEJpWzQIyhEJHRvmY8hHHr1/1VfXxysn-AB0wZjMgHsrLitICvTFkkZlr/1Lc4C6F5XKEAlmh5o8UQC748k0qs4YNRu/14piuGp3qi15X_GaNkBVI2YEb-V-A3OBy'

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

def generate_gti_doc(template_path, rows_data, output_docx_path):
    doc = docx.Document(template_path)
    body = doc._body._element
    tables = [Table(tbl, doc) for tbl in body.xpath('.//w:tbl')]
    t0 = tables[0]
    
    for idx, (c0, c1, c2) in enumerate(rows_data):
        row_idx = idx + 1
        row = t0.rows[row_idx]
        set_cell_formatted(row.cells[0], c0, bold=(idx == 0 or idx == len(rows_data)-1), align=WD_ALIGN_PARAGRAPH.LEFT)
        set_cell_formatted(row.cells[1], c1, bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        set_cell_formatted(row.cells[2], c2, bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        
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

def ensure_gdrive_folder(base_uri, folder_name):
    target_uri = f"{base_uri}/{folder_name}"
    check = subprocess.run(['gio', 'info', target_uri], capture_output=True, text=True)
    if check.returncode != 0:
        print(f"Criando subpasta {folder_name} em {base_uri}...")
        mk = subprocess.run(['gio', 'mkdir', target_uri], capture_output=True, text=True)
        if mk.returncode == 0:
            print(f"Subpasta {folder_name} criada com sucesso!")
        else:
            print(f"Erro ao criar subpasta: {mk.stderr}")
    else:
        print(f"Subpasta {folder_name} já existe em {base_uri}")
    return target_uri

def copy_to_gdrive(local_file, target_folder_uri):
    fname = os.path.basename(local_file)
    dest_uri = f"{target_folder_uri}/{fname}"
    print(f"Copiando {fname} para {target_folder_uri}...")
    cp = subprocess.run(['gio', 'copy', local_file, dest_uri], capture_output=True, text=True)
    if cp.returncode == 0:
        print(f"Sucesso: {fname} copiado para {target_folder_uri}")
    else:
        print(f"Erro ao copiar {fname}: {cp.stderr}")

def copy_file_and_pdf(local_docx, target_uri, copy_pdf=True):
    copy_to_gdrive(local_docx, target_uri)
    if copy_pdf:
        pdf_double = local_docx + '.pdf'
        if os.path.exists(pdf_double):
            copy_to_gdrive(pdf_double, target_uri)

# ==============================================================================
# DEFINIÇÃO DOS DADOS DAS ATAS DE GTI (2026.1 e 2026.2)
# ==============================================================================

# 1. NDE 2026.1 (2ª Reunião - 15 de julho de 2026)
nde_gti_26_1_rows = [
    (
        "Abertura",
        "A reunião do Núcleo Docente Estruturante do Curso Superior de Tecnologia em Gestão da Tecnologia da Informação foi aberta às quinze horas do dia quinze de julho de dois mil e vinte e seis pelo Coordenador do Curso e Presidente do NDE, Professor Hamilcar Pereira da Silva, com o propósito de avaliar o encerramento pedagógico do semestre letivo 2026.1 e traçar as diretrizes para o próximo período.",
        "SEM SUGESTÕES."
    ),
    (
        "Fomento à Participação Discente em Eventos de Intercurso",
        "O coordenador do curso, Professor Hamilcar Pereira da Silva, destacou a importância de integrar os discentes de Gestão da TI nos eventos acadêmicos interdisciplinares. A professora Denise Moraes do Nascimento Vieira propôs a criação de trilhas de inovação e liderança de projetos tecnológicos. O professor Alan Jefferson de Oliveira da Silva ressaltou a relevância de oficinas sobre governança ágil. O professor Ronaldo Paulucci de Assis defendeu a apresentação de estudos de casos reais pelas turmas concluintes. A professora Rosalva Maria Gomes de Araújo Oliveira sugeriu que a participação seja fomentada mediante concessão de créditos de atividades complementares.",
        "Desenvolver regulamento de submissões para o evento de intercurso e submeter à aprovação do colegiado."
    ),
    (
        "Engajamento Discente para o ENADE 2026",
        "O coordenador, Professor Hamilcar Pereira da Silva, relembrou os prazos do ciclo avaliativo do ENADE no segundo semestre, alertando para a necessidade de engajamento contínuo dos formandos. O professor Ronaldo Paulucci de Assis sugeriu a intensificação de simulados práticos focados nas competências do gestor de TI. A professora Rosalva Maria Gomes de Araújo Oliveira propôs oficinas de resolução comentada de itens de edições anteriores. O professor Alan Jefferson de Oliveira da Silva sugeriu palestras com gestores do mercado. A professora Denise Moraes do Nascimento Vieira reforçou o alinhamento das ações com as diretrizes do NEAD.",
        "Estruturar cronograma de simulados preparatórios e instituir campanhas motivacionais para os formandos."
    ),
    (
        "Monitoramento Discente e Ações contra a Evasão no AVA",
        "O coordenador, Professor Hamilcar Pereira da Silva, apresentou o balanço dos acessos e o comportamento da evasão discente no primeiro semestre de 2026. A professora Rosalva Maria Gomes de Araújo Oliveira pontuou a eficácia do suporte tutorial precoce aos alunos com dificuldades de navegação. A professora Denise Moraes do Nascimento Vieira recomendou a manutenção dos alertas de busca ativa. O professor Alan Jefferson de Oliveira da Silva destacou a importância do acolhimento nos canais de comunicação virtual. O professor Ronaldo Paulucci de Assis frisou a necessidade de intervenção pedagógica preventiva nas disciplinas de gestão estratégica e segurança da informação.",
        "Aperfeiçoar o plano de contingência pedagógica e intensificar o acompanhamento dos alunos nas semanas iniciais."
    ),
    (
        "Atualização de Diretrizes Pedagógicas e Ementas do PPC",
        "O coordenador, Professor Hamilcar Pereira da Silva, indicou a necessidade de revisão pontual do PPC para contemplar competências emergentes em Governança de TI, Computação em Nuvem e conformidade com a LGPD. A professora Denise Moraes do Nascimento Vieira sugeriu a modernização das referências virtuais nas UAs. O professor Ronaldo Paulucci de Assis propôs maior ênfase prática em frameworks de mercado (ITIL e COBIT). O professor Alan Jefferson de Oliveira da Silva defendeu a inclusão de ferramentas de análise de dados para tomada de decisão. A professora Rosalva Maria Gomes de Araújo Oliveira ressaltou a aderência ao Catálogo Nacional de Cursos Superiores de Tecnologia.",
        "Encaminhar proposta de atualização curricular e bibliográfica das disciplinas ao Colegiado de Curso."
    ),
    (
        "Encerramento",
        "Não havendo outros assuntos a tratar na presente data, o coordenador agradeceu calorosamente o empenho e as contribuições de todos os professores membros do NDE, declarando encerrada a sessão às dezessete horas, lavrando-se a presente ata.",
        "Sem sugestões."
    )
]

# 2. COLEGIADO 2026.1 (2ª Reunião - 18 de julho de 2026)
col_gti_26_1_rows = [
    (
        "Abertura",
        "No dia dezoito de julho de dois mil e vinte e seis, às nove horas, por meio de videoconferência institucional, reuniu-se ordinariamente o Colegiado do Curso Superior de Tecnologia em Gestão da Tecnologia da Informação da Universidade Iguaçu (UNIG), sob a presidência do Professor Hamilcar Pereira da Silva, contando com a presença dos professores membros e do representante discente, verificando-se quórum regimental.",
        "Não aplicável."
    ),
    (
        "Fomento à Participação Discente em Eventos de Intercurso",
        "O coordenador do curso realizou a apresentação da proposta do NDE visando incentivar a participação dos alunos no evento Intercurso de Gestão em TI. A professora Selma Sant'Anna da Fonseca Sardinha destacou a importância do protagonismo acadêmico dos estudantes. O professor Ronaldo Paulucci de Assis e a professora Mônica Saad Madeira manifestaram apoio integral à proposta de oficinas técnicas. O discente Rodrigo Zanardi Vieira ressaltou que a atribuição de horas complementares mobilizará amplamente os estudantes.",
        "APROVADO por unanimidade. Fica decidida a elaboração de regulamento específico com incentivos acadêmicos para ampla participação estudantil."
    ),
    (
        "Estratégias Preparatórias para o ENADE 2026",
        "O coordenador realizou a apresentação da proposta do NDE concernente às oficinas preparatórias e simulados do ENADE para os concluintes de Gestão da TI. Os membros do colegiado ressaltaram a relevância de consolidar a maturidade dos estudantes em cenários corporativos de tomada de decisão tecnológica e governança.",
        "APROVADO por unanimidade. Delibera-se pela implantação do calendário de simulados e campanhas informativas institucionais para o ENADE 2026."
    ),
    (
        "Monitoramento Discente e Ações Preventivas de Evasão no AVA",
        "Apreciação da proposta de implementação de novas rotinas de busca ativa e monitoramento semanal no AVA elaboradas pelo NDE. A professora Mônica Saad Madeira e o professor Ronaldo Paulucci de Assis pontuaram o papel decisivo da tutoria ágil na retenção de alunos. A professora Selma Sant'Anna da Fonseca Sardinha destacou o acolhimento discente como fator central de engajamento.",
        "APROVADO por unanimidade. Homologa-se o plano de busca ativa e acompanhamento pedagógico contínuo no ambiente virtual."
    ),
    (
        "Adequação Curricular e Bibliográfica do PPC",
        "Apreciação das recomendações do NDE sobre a atualização do PPC de Gestão em TI, com ênfase em governança digital, LGPD e computação em nuvem. Os integrantes do colegiado deliberaram sobre o alinhamento da matriz às novas demandas do setor produtivo e do MEC.",
        "APROVADO por unanimidade. Encaminhamento formal da proposta de atualização das ementas e bibliografias às instâncias superiores."
    ),
    (
        "Encerramento",
        "Não havendo outros assuntos a tratar na presente reunião, o presidente agradeceu aos docentes e ao representante discente pelo trabalho profícuo, declarando encerrada a sessão às onze horas, lavrando-se a presente ata.",
        "Não aplicável."
    )
]

# 3. NDE 2026.2 (1ª Reunião - 10 de agosto de 2026)
nde_gti_26_2_1_rows = [
    (
        "Abertura",
        "A reunião do Núcleo Docente Estruturante do Curso Superior de Tecnologia em Gestão da Tecnologia da Informação foi aberta às quinze horas do dia dez de agosto de dois mil e vinte e seis pelo Coordenador do Curso e Presidente do NDE, Professor Hamilcar Pereira da Silva, que deu boas-vindas aos docentes no início do segundo semestre letivo de 2026, destacando o planejamento acadêmico e as prioridades pedagógicas do curso em EAD.",
        "SEM SUGESTÕES."
    ),
    (
        "Acolhimento Discente e Programação das Aulas Inaugurais de 2026.2",
        "O Presidente do NDE apresentou a proposta de recepção aos calouros e veteranos do semestre letivo 2026.2, reforçando o papel das aulas inaugurais virtuais na ambientação ao AVA. A professora Denise Moraes do Nascimento Vieira sugeriu a elaboração de guia prático de gestão de tempo e estudos para EaD. O professor Alan Jefferson de Oliveira da Silva propôs uma palestra de abertura com foco no mercado de trabalho e papel do gestor de TI. A professora Rosalva Maria Gomes de Araújo Oliveira destacou a importância de apresentar os canais de tutoria pedagógica. O professor Ronaldo Paulucci de Assis ressaltou que a integração imediata reduz significativamente a insegurança dos ingressantes.",
        "Aprovar o cronograma das aulas inaugurais e disponibilizar materiais instrucionais de apoio aos discentes no AVA."
    ),
    (
        "Atualização do Banco de Itens e Diretrizes da Avaliação Integrada (Modelo ENADE)",
        "O coordenador colocou em pauta a atualização do Banco de Questões para a Avaliação Integrada do semestre 2026.2. O professor Ronaldo Paulucci de Assis defendeu a elaboração de questões multidisciplinares abordando ITIL, COBIT e Gerenciamento de Projetos. A professora Denise Moraes do Nascimento Vieira recomendou critérios rigorosos na revisão dos distratores. O professor Alan Jefferson de Oliveira da Silva enfatizou a relevância de cenários práticos de governança corporativa. A professora Rosalva Maria Gomes de Araújo Oliveira sugeriu estabelecer um cronograma antecipado de validação técnica das questões.",
        "Encaminhar a proposta de cronograma e diretrizes da Avaliação Integrada de Gestão de TI para homologação do Colegiado."
    ),
    (
        "Alinhamento Pedagógico das Disciplinas de Gestão e Tecnologias em Nuvem",
        "O coordenador expôs a necessidade de integrar abordagens práticas de Governança em Nuvem (FinOps), Segurança da Informação e Gestão Ágil nos Projetos Integradores do curso. O professor Alan Jefferson de Oliveira da Silva sugeriu o desenvolvimento de estudos de caso reais com planejamento estratégico de TI. A professora Rosalva Maria Gomes de Araújo Oliveira ressaltou a relevância de tratar aspectos de conformidade e auditoria de sistemas. O professor Ronaldo Paulucci de Assis recomendou desafios aplicados em equipe. A professora Denise Moraes do Nascimento Vieira ressaltou o benefício da interdisciplinaridade.",
        "Propor a inserção de estudos de caso de governança em nuvem e gestão ágil nos Projetos Integradores do curso."
    ),
    (
        "Acompanhamento Contínuo de Frequência e Prevenção à Evasão no AVA",
        "O Presidente do NDE ressaltou a necessidade de monitorar sistematicamente os acessos dos estudantes no AVA desde a primeira quinzena letiva. A professora Rosalva Maria Gomes de Araújo Oliveira propôs o alinhamento com os tutores para busca ativa de alunos que não iniciaram as UAs. O professor Alan Jefferson de Oliveira da Silva recomendou mensagens periódicas de incentivo. A professora Denise Moraes do Nascimento Vieira frisou a importância do atendimento ágil de dúvidas operacionais. O professor Ronaldo Paulucci de Assis destacou a atuação conjunta para assegurar a retenção escolar.",
        "Instituir painel quinzenal de monitoramento de engajamento discente no AVA com acionamento preventivo de tutoria."
    ),
    (
        "Encerramento",
        "Não havendo outros assuntos a serem tratados na presente pauta, o Coordenador e Presidente Hamilcar Pereira da Silva agradeceu a valiosa participação de todos os membros do NDE, declarando encerrada a reunião às dezessete horas, lavrando-se a presente ata.",
        "Sem sugestões."
    )
]

# 4. COLEGIADO 2026.2 (1ª Reunião - 17 de agosto de 2026)
col_gti_26_2_1_rows = [
    (
        "Abertura",
        "No dia dezessete de agosto de dois mil e vinte e seis, às quatorze horas, reuniu-se ordinariamente o Colegiado do Curso Superior de Tecnologia em Gestão da Tecnologia da Informação da Universidade Iguaçu (UNIG), por meio de videoconferência institucional, sob a presidência do Professor Hamilcar Pereira da Silva, contando com a presença dos professores membros e do representante discente para deliberação das pautas originadas do NDE.",
        "Não aplicável."
    ),
    (
        "Acolhimento Discente e Programação das Aulas Inaugurais de 2026.2",
        "O Colegiado apreciou a proposta pedagógica formulada pelo NDE referente às atividades de acolhimento e aulas inaugurais virtuais de 2026.2. O representante discente Rodrigo Zanardi Vieira manifestou concordância com os guias de estudos e encontros síncronos explicativos, pontuando que a iniciativa traz segurança aos novos estudantes. A professora Selma Sant'Anna da Fonseca Sardinha e a professora Mônica Saad Madeira destacaram que a ambientação favorece o engajamento imediato.",
        "APROVADO por unanimidade. Homologa-se a programação das aulas inaugurais e o plano de acolhimento do período letivo 2026.2."
    ),
    (
        "Atualização do Banco de Itens e Diretrizes da Avaliação Integrada (Modelo ENADE)",
        "Foi apresentada ao Colegiado a deliberação do NDE contendo o calendário de atualização do Banco de Questões e diretrizes pedagógicas para a Avaliação Integrada de Gestão de TI em 2026.2. O professor Ronaldo Paulucci de Assis e a professora Mônica Saad Madeira enfatizaram o alinhamento com as matrizes do ENADE e a importância do raciocínio crítico em gestão.",
        "APROVADO por unanimidade. Aprova-se o cronograma de atualização do banco de itens e os critérios pedagógicos da Avaliação Integrada de 2026.2."
    ),
    (
        "Alinhamento Pedagógico das Disciplinas de Gestão e Tecnologias em Nuvem",
        "O Colegiado debateu o encaminhamento do NDE quanto à introdução de temas práticos de FinOps, Governança em Nuvem e Gestão Ágil nos Projetos Integradores do curso. A professora Selma Sant'Anna da Fonseca Sardinha ressaltou que essas temáticas aumentam a competitividade profissional dos egressos no setor de tecnologia corporativa.",
        "APROVADO por unanimidade. Delibera-se pela aprovação da inserção de conteúdos de governança em nuvem e gestão ágil nas atividades integradoras."
    ),
    (
        "Acompanhamento Contínuo de Frequência e Prevenção à Evasão no AVA",
        "Foi submetido à análise do Colegiado o plano de acompanhamento sistemático de frequência e intervenção precoce de tutoria no AVA para mitigar a evasão. O colegiado reiterou o compromisso institucional com a permanência e êxito acadêmico dos discentes matriculados em Gestão da TI.",
        "APROVADO por unanimidade. Fica aprovada a rotina de monitoramento de engajamento discente no AVA com acionamento tempestivo do suporte acadêmico."
    ),
    (
        "Encerramento",
        "Esgotada a ordem do dia e nada mais havendo a constar, o presidente agradeceu aos docentes e ao discente pela participação profícua, encerrando a sessão às dezesseis horas, da qual se lavrou a presente ata.",
        "Não aplicável."
    )
]

# 5. NDE 2026.2 (2ª Reunião - 11 de dezembro de 2026)
nde_gti_26_2_2_rows = [
    (
        "Abertura",
        "A reunião do Núcleo Docente Estruturante do Curso Superior de Tecnologia em Gestão da Tecnologia da Informação foi aberta às quinze horas do dia onze de dezembro de dois mil e vinte e seis pelo Coordenador do Curso e Presidente do NDE, Professor Hamilcar Pereira da Silva, com o propósito de consolidar os resultados acadêmicos do período letivo 2026.2, analisar as devolutivas institucionais e definir diretrizes curriculares para 2027.1.",
        "SEM SUGESTÕES."
    ),
    (
        "Balanço dos Indicadores Acadêmicos e Rendimento no AVA de 2026.2",
        "O Presidente do NDE apresentou os dados consolidados de aprovação, retenção e notas da Avaliação Integrada nas disciplinas de Gestão da TI no segundo semestre de 2026. O professor Alan Jefferson de Oliveira da Silva destacou o excelente aproveitamento discente nas disciplinas de governança e gestão estratégica. A professora Denise Moraes do Nascimento Vieira apontou que as intervenções tutoriais precoces surtiram efeito positivo na redução da evasão. O professor Ronaldo Paulucci de Assis destacou a qualidade das entregas nos projetos práticos. A professora Rosalva Maria Gomes de Araújo Oliveira sugeriu a continuidade das oficinas de nivelamento para os próximos semestres.",
        "Encaminhar o relatório consolidado de rendimento acadêmico e indicadores de retenção discente ao Colegiado de Curso."
    ),
    (
        "Avaliação dos Resultados da CPA e Plano de Ação em Governança Acadêmica",
        "O Coordenador expôs a síntese das avaliações institucionais coordenadas pela Comissão Própria de Avaliação (CPA) referentes a 2026. A professora Rosalva Maria Gomes de Araújo Oliveira manifestou satisfação com a percepção positiva dos estudantes quanto à clareza das UAs e tempestividade dos feedbacks docentes. O professor Alan Jefferson de Oliveira da Silva comentou sobre a importância de aprimorar a infraestrutura de laboratórios virtuais. A professora Denise Moraes do Nascimento Vieira sugeriu a elaboração de plano de ação focado na produção de novos recursos audiovisuais. O professor Ronaldo Paulucci de Assis destacou a transparência no retorno das ações à comunidade acadêmica.",
        "Elaborar proposta de plano de ação pedagógico em atendimento às recomendações da CPA e submeter à deliberação do Colegiado."
    ),
    (
        "Culminância dos Projetos de Extensão e Práticas de Gestão na Sociedade",
        "O coordenador relatou o cumprimento da carga horária de extensão curricularizada no semestre, com apresentação dos planos de governança tecnológica desenvolvidos pelos discentes para micro e pequenas empresas da comunidade. A professora Denise Moraes do Nascimento Vieira elogiou o amadurecimento técnico dos estudantes e o impacto comunitário gerado. O professor Ronaldo Paulucci de Assis destacou o alinhamento com as diretrizes curriculares nacionais de extensão. O professor Alan Jefferson de Oliveira da Silva e a professora Rosalva Maria Gomes de Araújo Oliveira recomendaram o arquivamento digital dos melhores trabalhos.",
        "Homologar a validação das horas de extensão curricularizadas e remeter os dossiês ao Colegiado para arquivamento oficial."
    ),
    (
        "Diretrizes Curriculares e Planejamento Acadêmico para o Semestre 2027.1",
        "O Presidente do NDE apresentou as diretrizes preliminares para a organização da oferta de disciplinas, cronograma letivo e acolhimento dos estudantes no primeiro período de 2027. A professora Denise Moraes do Nascimento Vieira recomendou a antecipação do calendário das avaliações integradas. O professor Alan Jefferson de Oliveira da Silva sugeriu oficinas sobre frameworks ágeis. O professor Ronaldo Paulucci de Assis propôs a revisão ordinária dos planos de ensino. A professora Rosalva Maria Gomes de Araújo Oliveira sugeriu o agendamento prévio das reuniões ordinárias do NDE.",
        "Encaminhar a proposta de planejamento acadêmico e oferta de disciplinas de 2027.1 para homologação do Colegiado de Curso."
    ),
    (
        "Encerramento",
        "Esgotados os assuntos da ordem do dia, o Coordenador e Presidente Hamilcar Pereira da Silva expressou profundo agradecimento a todos os membros docentes do NDE pelo rigor acadêmico e trabalho coletivo desenvolvido ao longo de 2026, encerrando oficialmente a sessão às dezessete horas.",
        "Sem sugestões."
    )
]

# 6. COLEGIADO 2026.2 (2ª Reunião - 18 de dezembro de 2026)
col_gti_26_2_2_rows = [
    (
        "Abertura",
        "No dia dezoito de dezembro de dois mil e vinte e seis, às quatorze horas, por meio de ambiente virtual institucional, reuniu-se ordinariamente o Colegiado do Curso Superior de Tecnologia em Gestão da Tecnologia da Informação (GTI), sob a presidência do Professor Hamilcar Pereira da Silva, contando com a presença dos professores membros e do representante discente, verificando-se quórum regimental para encerramento do ano letivo de 2026.",
        "Não aplicável."
    ),
    (
        "Balanço dos Indicadores Acadêmicos e Rendimento no AVA de 2026.2",
        "O Colegiado apreciou os relatórios de rendimento acadêmico, retenção e taxas de sucesso dos discentes de Gestão da TI em 2026.2 encaminhados pelo NDE. O corpo docente e a representação discente concordaram que o acompanhamento contínuo e a atuação tutorial foram decisivos para os resultados positivos alcançados pelos estudantes nas disciplinas e avaliações do semestre.",
        "APROVADO por unanimidade. Homologa-se o relatório consolidado de desempenho acadêmico e retenção referente a 2026.2."
    ),
    (
        "Avaliação dos Resultados da CPA e Plano de Ação em Governança Acadêmica",
        "Foi analisado pelo Colegiado o plano de ação formulado em resposta aos relatórios da Comissão Própria de Avaliação (CPA) de 2026. A professora Selma Sant'Anna da Fonseca Sardinha e a professora Mônica Saad Madeira destacaram a relevância de investir no enriquecimento instrucional das UAs e na comunicação transparente com o alunado.",
        "APROVADO por unanimidade. Fica aprovado o plano de ação pedagógico decorrente da avaliação institucional da CPA."
    ),
    (
        "Culminância dos Projetos de Extensão e Práticas de Gestão na Sociedade",
        "Foram submetidos à homologação do Colegiado os dossiês das atividades de extensão curricularizadas desenvolvidas pelos discentes de GTI durante o segundo semestre de 2026. O representante discente Rodrigo Zanardi Vieira destacou a satisfação dos alunos em prestar consultoria em gestão tecnológica para empreendimentos locais. O Colegiado felicitou os orientadores e alunos.",
        "APROVADO por unanimidade. Homologam-se as atividades extensionistas e as respectivas cargas horárias cumpridas no semestre 2026.2."
    ),
    (
        "Diretrizes Curriculares e Planejamento Acadêmico para o Semestre 2027.1",
        "O Colegiado deliberou sobre o planejamento pedagógico preliminar para o ano letivo de 2027.1, incluindo matriz de ofertas, calendários acadêmicos e acolhimento discente. Os membros destacaram a importância do cronograma antecipado para a estabilidade pedagógica.",
        "APROVADO por unanimidade. Aprova-se a proposta de planejamento acadêmico e oferta de disciplinas para o período letivo de 2027.1."
    ),
    (
        "Encerramento",
        "Não havendo mais assuntos a serem tratados na presente pauta, o Coordenador e Presidente Hamilcar Pereira da Silva expressou profunda gratidão aos docentes membros e à representação discente pela dedicação e harmonia institucional demonstradas em 2026, declarando encerrada a sessão às dezesseis horas, lavrando-se a presente ata.",
        "Não aplicável."
    )
]

# ==============================================================================
# GERAÇÃO LOCAL DOS 6 ARQUIVOS (DOCX e PDF)
# ==============================================================================

# 1. NDE 26.1 (2ª Reunião - 15/07/2026)
f_nde_26_1 = os.path.join(LOCAL_OUTPUT_DIR, "Ata_Reuniao_NDE_GTI_15_JUL_2026.docx")
generate_gti_doc(TEMPLATE_GTI_NDE, nde_gti_26_1_rows, f_nde_26_1)

# 2. Colegiado 26.1 (2ª Reunião - 18/07/2026)
f_col_26_1 = os.path.join(LOCAL_OUTPUT_DIR, "Reuniao_COLEGIADO_GTI_18_JUL_2026.docx")
generate_gti_doc(TEMPLATE_GTI_COL, col_gti_26_1_rows, f_col_26_1)

# 3. NDE 26.2 (1ª Reunião - 10/08/2026)
f_nde_26_2_1 = os.path.join(LOCAL_OUTPUT_DIR, "Ata_Reuniao_NDE_GTI_10_AGO_2026.docx")
generate_gti_doc(TEMPLATE_GTI_NDE, nde_gti_26_2_1_rows, f_nde_26_2_1)

# 4. Colegiado 26.2 (1ª Reunião - 17/08/2026)
f_col_26_2_1 = os.path.join(LOCAL_OUTPUT_DIR, "Reuniao_COLEGIADO_GTI_17_AGO_2026.docx")
generate_gti_doc(TEMPLATE_GTI_COL, col_gti_26_2_1_rows, f_col_26_2_1)

# 5. NDE 26.2 (2ª Reunião - 11/12/2026)
f_nde_26_2_2 = os.path.join(LOCAL_OUTPUT_DIR, "Ata_Reuniao_NDE_GTI_11_DEZ_2026.docx")
generate_gti_doc(TEMPLATE_GTI_NDE, nde_gti_26_2_2_rows, f_nde_26_2_2)

# 6. Colegiado 26.2 (2ª Reunião - 18/12/2026)
f_col_26_2_2 = os.path.join(LOCAL_OUTPUT_DIR, "Reuniao_COLEGIADO_GTI_18_DEZ_2026.docx")
generate_gti_doc(TEMPLATE_GTI_COL, col_gti_26_2_2_rows, f_col_26_2_2)

print("\n=== Todos os 6 arquivos de GTI (DOCX e PDF) gerados localmente! ===")

# ==============================================================================
# SINCRONIZAÇÃO COM OS DOIS REPOSITÓRIOS NO GOOGLE DRIVE
# ==============================================================================

print("\n=== 1. Sincronizando com Cursos NEAD-Atual 2023 ===")

# NDE 2026.1 (2ª ata)
copy_to_gdrive(f_nde_26_1, f"{URI_NEAD2023_NDE}/2026.1")

# Colegiado 2026.1 (2ª ata)
copy_to_gdrive(f_col_26_1, f"{URI_NEAD2023_COL}/2026.1")

# NDE 2026.2 (criar subpasta e copiar as 2 atas)
dest_nde_2026_2 = ensure_gdrive_folder(URI_NEAD2023_NDE, "2026.2")
copy_to_gdrive(f_nde_26_2_1, dest_nde_2026_2)
copy_to_gdrive(f_nde_26_2_2, dest_nde_2026_2)

# Colegiado 2026.2 (criar subpasta e copiar as 2 atas)
dest_col_2026_2 = ensure_gdrive_folder(URI_NEAD2023_COL, "2026.2")
copy_to_gdrive(f_col_26_2_1, dest_col_2026_2)
copy_to_gdrive(f_col_26_2_2, dest_col_2026_2)

print("\n=== 2. Sincronizando com _MEC_CURSOS_NEAD-2026 (.ATAS) ===")

# NDE 26.1 (2ª ata)
copy_file_and_pdf(f_nde_26_1, f"{URI_MEC_NDE}/26.1")

# Colegiado 26.1 (2ª ata)
copy_file_and_pdf(f_col_26_1, f"{URI_MEC_COL}/26.1")

# NDE 26.2 (criar subpasta 26.2 e copiar as 2 atas)
dest_nde_26_2 = ensure_gdrive_folder(URI_MEC_NDE, "26.2")
copy_file_and_pdf(f_nde_26_2_1, dest_nde_26_2)
copy_file_and_pdf(f_nde_26_2_2, dest_nde_26_2)

# Colegiado 26.2 (criar subpasta 26.2 e copiar as 2 atas)
dest_col_26_2 = ensure_gdrive_folder(URI_MEC_COL, "26.2")
copy_file_and_pdf(f_col_26_2_1, dest_col_26_2)
copy_file_and_pdf(f_col_26_2_2, dest_col_26_2)

print("\n=== Sincronização GTI completa com êxito em ambos os locais! ===")
