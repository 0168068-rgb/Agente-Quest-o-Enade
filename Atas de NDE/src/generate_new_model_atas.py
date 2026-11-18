import os
import subprocess
import docx
from docx.table import Table
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

TEMPLATES_DIR = '/home/hamilcar/Antigravity/Atas de NDE/templates'
LOCAL_OUTPUT_DIR = '/home/hamilcar/Antigravity/Atas de NDE/atas_geradas_modelo_novo'
os.makedirs(LOCAL_OUTPUT_DIR, exist_ok=True)

# New Official Models
TEMPLATE_NDE = os.path.join(TEMPLATES_DIR, 'template_nde_oficial_2026.docx')
TEMPLATE_COL = os.path.join(TEMPLATES_DIR, 'template_colegiado_oficial_2026.docx')

# Target URIs in .ATAS
BASE_URI_NDE_ATAS = 'google-drive://0168068@professor.unig.edu.br/GVfsSharedWithMe/1OVWk6s2LEwXOp_jAQNacFZtVBSrS9r8i/1wm6ptLxn07qiNjEBWbSB4wvBcmw9jYsw/1bH60AUfQaf_bOCoE_EEWbSSP8BQQKyB3/1VLYMikZEF7_uiwgKsY9-Rf7sqBwAjg9b/1iOJbK7ie2eTkd71AfkpFz5tvSULG0u2d/10FYLdH8hiyGs8hS0iT7boyGirQyMv2oD/1sQZsZ3cbGfewOWFG9cg2jh4OOm4zioI-'
BASE_URI_COL_ATAS = 'google-drive://0168068@professor.unig.edu.br/GVfsSharedWithMe/1OVWk6s2LEwXOp_jAQNacFZtVBSrS9r8i/1wm6ptLxn07qiNjEBWbSB4wvBcmw9jYsw/1bH60AUfQaf_bOCoE_EEWbSSP8BQQKyB3/1VLYMikZEF7_uiwgKsY9-Rf7sqBwAjg9b/1iOJbK7ie2eTkd71AfkpFz5tvSULG0u2d/1oRyFokCNL7juuFi4eod5d64svfqf2LOg'

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

def generate_doc_from_template(template_path, rows_data, output_docx_path):
    doc = docx.Document(template_path)
    body = doc._body._element
    tables = [Table(tbl, doc) for tbl in body.xpath('.//w:tbl')]
    t0 = tables[0] # Content table
    
    # Populate rows 1 to len(rows_data)
    for idx, (c0, c1, c2) in enumerate(rows_data):
        row_idx = idx + 1
        row = t0.rows[row_idx]
        set_cell_formatted(row.cells[0], c0, bold=(idx == 0 or idx == len(rows_data)-1), align=WD_ALIGN_PARAGRAPH.LEFT)
        set_cell_formatted(row.cells[1], c1, bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        set_cell_formatted(row.cells[2], c2, bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        
    doc.save(output_docx_path)
    print(f"Salvo docx: {output_docx_path}")
    
    # Convert to PDF
    pdf_dir = os.path.dirname(output_docx_path)
    subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', output_docx_path, '--outdir', pdf_dir], capture_output=True)
    pdf_path = output_docx_path.replace('.docx', '.pdf')
    # In some folders they use .docx.pdf
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
        print(f"Sucesso: {fname} copiado para o Google Drive!")
    else:
        print(f"Erro ao copiar {fname}: {cp.stderr}")

# ==============================================================================
# DEFINIÇÃO DOS DADOS DAS ATAS (MODELO NOVO)
# ==============================================================================

# 1. COLEGIADO 26.1 (2ª Reunião - 17 de julho de 2026)
col_26_1_rows = [
    (
        "Abertura",
        "Às quinze horas do dia dezessete de julho de dois mil e vinte e seis, por meio de ambiente virtual institucional, reuniu-se ordinariamente o Colegiado do Curso Superior de Tecnologia em Análise e Desenvolvimento de Sistemas (ADS). O Coordenador do Curso e Presidente do Colegiado, Professor Hamilcar Pereira da Silva, declarou aberta a sessão, acolhendo os docentes membros, Professores Marcos Cruz de Azevedo, Selma Sant'Anna de Fonseca e Denise Moraes do Nascimento Vieira, e a representante discente, Ana Carolina Ramos da Cruz, verificando a presença regimental dos convocados para o início dos trabalhos.",
        "Sem deliberação. Abertura e registro de quórum regulamentar da sessão."
    ),
    (
        "Fomento à Participação Discente no Evento Intercurso",
        "O Colegiado apreciou a proposta encaminhada pelo Núcleo Docente Estruturante (NDE) referente a ações de engajamento discente no evento Intercurso do curso de ADS. A professora Selma Sant'Anna de Fonseca destacou que a concessão de incentivos na forma de atribuição de horas de atividades complementares é de suma relevância para mobilizar os discentes matriculados nos períodos letivos iniciais. O professor Marcos Cruz de Azevedo propôs, de forma complementar, que as atividades práticas concebidas no escopo de disciplinas tecnológicas de desenvolvimento de software sejam apresentadas como oficinas coordenadas pelos próprios discentes, incentivando o protagonismo acadêmico.",
        "APROVADO por unanimidade. Encaminha-se a reestruturação e republicação do edital do evento Intercurso contendo as novas diretrizes pedagógicas e modalidades de fomento à participação estudantil."
    ),
    (
        "Sensibilização e Preparação de Alunos Finalistas para o Exame Nacional de Desempenho dos Estudantes (ENADE)",
        "O Presidente do Colegiado pautou o plano de preparação dos estudantes concluintes de Análise e Desenvolvimento de Sistemas para o Exame Nacional de Desempenho dos Estudantes (ENADE). A professora Denise Moraes do Nascimento Vieira defendeu a importância de realizar oficinas presenciais e assíncronas dedicadas à discussão de questões estruturadas em tecnologia e engenharia de software, além de simulados periódicos integrados. O professor Marcos Cruz de Azevedo sugeriu a promoção de uma campanha de comunicação institucional contínua, em parceria com o NEAD, a fim de conscientizar os discentes sobre o impacto do resultado do exame em sua projeção profissional no mercado de TI.",
        "APROVADO por unanimidade. Determina-se a formalização do plano de ação pedagógico do ENADE, incumbindo a comissão e a coordenação de estruturar o cronograma de simulados e as ações promocionais integradas."
    ),
    (
        "Monitoramento de Desempenho e Combate à Evasão no AVA",
        "O Colegiado examinou a análise do NDE a respeito dos índices de evasão precoce e engajamento discente no Ambiente Virtual de Aprendizagem (AVA). A professora Selma Sant'Anna de Fonseca expôs a necessidade de intensificar o monitoramento de acessos e interações nas Unidades de Aprendizagem (UAs) nas primeiras semanas de aula. A professora Denise Moraes do Nascimento Vieira propôs que a equipe de tutoria trabalhe em estreita sintonia com o corpo docente para identificar os casos de não comparecimento virtual ou atraso em entregas avaliativas de disciplinas de algoritmos e desenvolvimento, disparando alertas de busca ativa.",
        "APROVADO por unanimidade. Fica deliberada a implementação de uma rotina semanal de análise dos relatórios de engajamento no AVA, com acionamento tempestivo do acompanhamento tutorial da coordenação acadêmica."
    ),
    (
        "Adequação das Atividades Extensionistas e Curricularização no PPC",
        "Foi submetida à apreciação do Colegiado a regulamentação para o cumprimento da curricularização das atividades extensionistas no Projeto Pedagógico do Curso (PPC) de ADS. O professor Marcos Cruz de Azevedo sustentou que as soluções tecnológicas elaboradas pelos discentes nas disciplinas estruturadoras e nos Projetos Integradores sejam validadas como atividades práticas de extensão tecnológica junto à comunidade externa. A professora Selma Sant'Anna de Fonseca destacou a importância de atualizar formalmente o PPC de acordo com os marcos regulatórios de extensão no ensino superior nacional.",
        "APROVADO por unanimidade. Deliberou-se pela revisão do regulamento interno de extensão do curso e atualização do PPC de Análise e Desenvolvimento de Sistemas, com subsequente submissão da minuta homologada aos órgãos acadêmicos superiores."
    ),
    (
        "Encerramento",
        "O Coordenador do Curso e Presidente do Colegiado, Professor Hamilcar Pereira da Silva, constatando o encerramento da pauta estabelecida para a sessão, registrou os agradecimentos pela presença e ricas discussões promovidas pelos docentes e discentes. Às dezessete horas, declarou encerrada a reunião, determinando a lavratura da respectiva ata acadêmica oficial.",
        "Sem deliberação. Encerramento formal e registro da ata para fins de conferência e assinaturas eletrônicas."
    )
]

# 2. NDE 26.2 (1ª Reunião - 10 de agosto de 2026)
nde_26_2_1_rows = [
    (
        "ABERTURA",
        "A reunião do Núcleo Docente Estruturante do Curso Superior de Tecnologia em Análise e Desenvolvimento de Sistemas foi aberta às quinze horas do dia dez de agosto de dois mil e vinte e seis pelo Coordenador do Curso e Presidente do NDE, Professor Hamilcar Pereira da Silva, que acolheu os membros docentes no início do segundo semestre letivo de 2026, destacando as prioridades pedagógicas e o compromisso institucional com a qualidade da formação acadêmica em EAD.",
        "Sem sugestões."
    ),
    (
        "Acolhimento Discente e Programação das Aulas Inaugurais de 2026.2",
        "O Presidente do NDE apresentou a programação de acolhimento aos calouros e veteranos do semestre letivo 2026.2, enfatizando a relevância das aulas inaugurais síncronas para a ambientação na plataforma virtual. O professor Alan Jefferson de Oliveira da Silva sugeriu a realização de uma live técnica introdutória abordando as ferramentas de desenvolvimento e trilha de aprendizagem. O professor Telmo Viana Rodrigues ressaltou a importância da divulgação dos canais de tutoria pedagógica. O professor Luciano Roberto Padilha de Andrade propôs a elaboração de tutoriais rápidos em vídeo sobre os recursos do AVA. O professor Ronaldo Paulucci de Assis destacou que o acolhimento tempestivo potencializa a retenção discente inicial.",
        "Aprovar a estrutura da aula inaugural e disponibilizar materiais instrucionais de apoio aos discentes no AVA."
    ),
    (
        "Atualização do Banco de Questões e Cronograma da Avaliação Integrada",
        "O Coordenador colocou em pauta a revisão e inserção de novos itens no Banco de Questões para a Avaliação Integrada de 2026.2. O professor Ronaldo Paulucci de Assis defendeu a formulação de questões alinhadas com o perfil de competências do ENADE e demandas da indústria de software. O professor Luciano Roberto Padilha de Andrade recomendou a realização de reuniões de alinhamento com os docentes elaboradores para validação prévia dos distratores. O professor Alan Jefferson de Oliveira da Silva reforçou a necessidade de contemplar cenários reais de programação. O professor Telmo Viana Rodrigues sugeriu a definição de um calendário rigoroso para submissão das questões.",
        "Encaminhar a proposta de cronograma e critérios da Avaliação Integrada para homologação do Colegiado de Curso."
    ),
    (
        "Inserção de Tecnologias Emergentes (Inteligência Artificial e Nuvem)",
        "O coordenador pontuou a necessidade de incorporar tópicos de Inteligência Artificial Generativa e Computação em Nuvem nas Unidades de Aprendizagem (UAs) e nos projetos práticos. O professor Telmo Viana Rodrigues destacou a importância de orientar os estudantes quanto ao uso ético e produtivo de ferramentas de IA no desenvolvimento de código. O professor Alan Jefferson de Oliveira da Silva sugeriu desafios práticos envolvendo microsserviços em nuvem. O professor Luciano Roberto Padilha de Andrade propôs workshops temáticos ao longo do período. O professor Ronaldo Paulucci de Assis reforçou que a atualização contínua eleva a empregabilidade dos egressos.",
        "Propor a inserção de estudos de caso em IA e Cloud nos Projetos Integradores do curso e submeter à apreciação do Colegiado."
    ),
    (
        "Monitoramento de Engajamento e Prevenção à Evasão Precoce no AVA",
        "O Presidente do NDE enfatizou a urgência de acompanhar os acessos estudantis desde a primeira semana letiva para combater a evasão. O professor Alan Jefferson de Oliveira da Silva propôs rotinas de busca ativa para alunos sem acesso nos primeiros quinze dias. O professor Telmo Viana Rodrigues sugeriu o envio de mensagens motivacionais personalizadas. O professor Luciano Roberto Padilha de Andrade recomendou o alinhamento estreito com a tutoria do NEAD para atendimento tempestivo de dúvidas operacionais. O professor Ronaldo Paulucci de Assis enfatizou a importância de incentivar a participação nos fóruns temáticos.",
        "Instituir painel semanal de monitoramento de engajamento discente no AVA com intervenções pedagógicas preventivas."
    ),
    (
        "ENCERRAMENTO",
        "Não havendo outros assuntos a serem tratados na pauta, o Coordenador e Presidente Hamilcar Pereira da Silva agradeceu a rica colaboração de todos os professores do NDE, declarando formalmente encerrada a sessão às dezessete horas, lavrando-se a presente ata.",
        "Término da reunião."
    )
]

# 3. COLEGIADO 26.2 (1ª Reunião - 17 de agosto de 2026)
col_26_2_1_rows = [
    (
        "Abertura",
        "Às quatorze horas do dia dezessete de agosto de dois mil e vinte e seis, por meio de ambiente virtual institucional, reuniu-se ordinariamente o Colegiado do Curso Superior de Tecnologia em Análise e Desenvolvimento de Sistemas (ADS). O Coordenador do Curso e Presidente do Colegiado, Professor Hamilcar Pereira da Silva, declarou aberta a sessão, acolhendo os docentes membros, Professores Marcos Cruz de Azevedo, Selma Sant'Anna de Fonseca e Denise Moraes do Nascimento Vieira, e a representante discente, Ana Carolina Ramos da Cruz, verificando a presença regimental dos convocados para o início dos trabalhos.",
        "Sem deliberação. Abertura e registro de quórum regulamentar da sessão."
    ),
    (
        "Acolhimento Discente e Programação das Aulas Inaugurais de 2026.2",
        "O Colegiado apreciou a proposta pedagógica formulada pelo NDE referente às atividades de acolhimento e aulas inaugurais destinadas aos ingressantes e veteranos de 2026.2. A representante discente Ana Carolina Ramos da Cruz elogiou a iniciativa das lives técnicas e a produção de tutoriais sobre o AVA, destacando que essa abordagem dissipa dúvidas recorrentes dos estudantes. O professor Marcos Cruz de Azevedo e a professora Selma Sant'Anna de Fonseca reforçaram a importância da integração inicial como instrumento de vínculo institucional.",
        "APROVADO por unanimidade. Homologa-se a programação das aulas inaugurais e o plano de acolhimento do período letivo 2026.2."
    ),
    (
        "Atualização do Banco de Questões e Cronograma da Avaliação Integrada",
        "Foi apresentada ao Colegiado a deliberação do NDE com o cronograma de atualização do Banco de Questões e diretrizes avaliativas da Avaliação Integrada de 2026.2. A professora Denise Moraes do Nascimento Vieira enfatizou a seriedade do processo de pré-validação dos itens para garantir o rigor técnico das provas. O professor Marcos Cruz de Azevedo manifestou concordância quanto à aplicação do modelo ENADE nas avaliações do curso.",
        "APROVADO por unanimidade. Aprova-se o cronograma de atualização do banco de itens e os critérios pedagógicos da Avaliação Integrada de 2026.2."
    ),
    (
        "Inserção de Tecnologias Emergentes (Inteligência Artificial e Nuvem)",
        "O Colegiado debateu o encaminhamento do NDE quanto à introdução de temas práticos de Inteligência Artificial e Computação em Nuvem nas atividades acadêmicas e Projetos Integradores de ADS. A professora Selma Sant'Anna de Fonseca ressaltou a aderência da proposta às tendências globais de tecnologia e a relevância de discutir o uso ético de IA pelos estudantes. O professor Marcos Cruz de Azevedo pontuou que o mercado valoriza profissionais aptos a operar em ambientes em nuvem.",
        "APROVADO por unanimidade. Delibera-se pela aprovação da inserção de conteúdos de IA e Cloud Computing nas atividades práticas e integradoras."
    ),
    (
        "Monitoramento de Engajamento e Prevenção à Evasão Precoce no AVA",
        "Foi submetido à análise do Colegiado o plano de acompanhamento contínuo de engajamento dos estudantes no AVA, visando mitigar a evasão por meio de buscas ativas e apoio tutorial integrado. A professora Denise Moraes do Nascimento Vieira destacou a efetividade do monitoramento na identificação rápida de alunos que enfrentam dificuldades nos primeiros módulos.",
        "APROVADO por unanimidade. Fica aprovada a rotina de monitoramento de engajamento discente no AVA com acionamento tempestivo do suporte acadêmico."
    ),
    (
        "Encerramento",
        "O Coordenador do Curso e Presidente do Colegiado, Professor Hamilcar Pereira da Silva, constatando o encerramento da pauta estabelecida para a sessão, registrou os agradecimentos pela presença e ricas discussões promovidas pelos docentes e discentes. Às dezesseis horas, declarou encerrada a reunião, determinando a lavratura da respectiva ata acadêmica oficial.",
        "Sem deliberação. Encerramento formal e registro da ata para fins de conferência e assinaturas eletrônicas."
    )
]

# 4. NDE 26.2 (2ª Reunião - 11 de dezembro de 2026)
nde_26_2_2_rows = [
    (
        "ABERTURA",
        "A reunião do Núcleo Docente Estruturante do Curso Superior de Tecnologia em Análise e Desenvolvimento de Sistemas foi aberta às quinze horas do dia onze de dezembro de dois mil e vinte e seis pelo Coordenador do Curso e Presidente do NDE, Professor Hamilcar Pereira da Silva, com o propósito de consolidar os resultados acadêmicos do período letivo 2026.2, analisar as devolutivas institucionais e definir diretrizes curriculares para 2027.1.",
        "Sem sugestões."
    ),
    (
        "Balanço dos Indicadores Acadêmicos e Desempenho no AVA em 2026.2",
        "O Presidente do NDE apresentou os dados consolidados de aprovação, retenção e participação dos discentes nas disciplinas do segundo semestre de 2026. O professor Telmo Viana Rodrigues destacou o impacto positivo do monitoramento contínuo nas taxas de conclusão das Unidades de Aprendizagem. O professor Alan Jefferson de Oliveira da Silva comentou o bom desempenho discente nos projetos práticos de desenvolvimento de software e banco de dados. O professor Luciano Roberto Padilha de Andrade apontou o crescimento da utilização das bases bibliográficas digitais. O professor Ronaldo Paulucci de Assis reforçou a necessidade de preservar as ações de reforço para os períodos iniciais.",
        "Encaminhar o relatório consolidado de rendimento acadêmico e indicadores de retenção discente ao Colegiado de Curso."
    ),
    (
        "Avaliação dos Relatórios da CPA (Comissão Própria de Avaliação)",
        "O Coordenador expôs a síntese das avaliações institucionais de 2026 coordenadas pela CPA, destacando os pontos fortes e as oportunidades de melhoria apontadas pela comunidade acadêmica. O professor Alan Jefferson de Oliveira da Silva manifestou satisfação quanto à avaliação positiva da atuação docente e da pontualidade dos retornos. O professor Telmo Viana Rodrigues ressaltou a importância de aprimorar os canais de feedback das atividades virtuais. O professor Luciano Roberto Padilha de Andrade propôs um plano de melhorias focado no enriquecimento dos materiais multimídia das UAs. O professor Ronaldo Paulucci de Assis destacou a transparência na devolutiva dos resultados aos estudantes.",
        "Elaborar proposta de plano de ação pedagógico em atendimento às recomendações da CPA e submeter à deliberação do Colegiado."
    ),
    (
        "Consolidação dos Projetos de Extensão e Atividades Práticas Curriculares",
        "O coordenador relatou o cumprimento da carga horária de extensão curricularizada no semestre, com apresentações finais de softwares e soluções desenvolvidas para a comunidade. O professor Luciano Roberto Padilha de Andrade elogiou o amadurecimento dos estudantes e o impacto comunitário gerado. O professor Ronaldo Paulucci de Assis destacou a convergência com os Objetivos de Desenvolvimento Sustentável. O professor Alan Jefferson de Oliveira da Silva sugeriu a manutenção de um acervo digital das iniciativas. O professor Telmo Viana Rodrigues salientou o ganho institucional decorrente do estreitamento de laços com a sociedade.",
        "Homologar a validação das horas de extensão curricularizadas e remeter os dossiês ao Colegiado para arquivamento oficial."
    ),
    (
        "Diretrizes Pedagógicas e Planejamento Acadêmico para o Semestre 2027.1",
        "O Presidente do NDE apresentou as diretrizes organizacionais para a oferta de disciplinas, cronograma letivo e acolhimento dos estudantes no primeiro período de 2027. O professor Telmo Viana Rodrigues recomendou antecipar as datas dos simulados integrados. O professor Alan Jefferson de Oliveira da Silva propôs ampliar os cursos de nivelamento de lógica de programação. O professor Ronaldo Paulucci de Assis sugeriu a organização precoce do calendário de reuniões do NDE. O professor Luciano Roberto Padilha de Andrade sugeriu a revisão ordinária dos planos de ensino.",
        "Encaminhar a proposta de planejamento acadêmico e oferta de disciplinas de 2027.1 para homologação do Colegiado de Curso."
    ),
    (
        "ENCERRAMENTO",
        "Esgotados os assuntos da ordem do dia, o Coordenador e Presidente Hamilcar Pereira da Silva expressou profundo agradecimento a todos os membros docentes do NDE pelo compromisso e rigor acadêmico demonstrados ao longo de todo o ano de 2026, encerrando oficialmente a sessão às dezessete horas.",
        "Término da reunião."
    )
]

# 5. COLEGIADO 26.2 (2ª Reunião - 18 de dezembro de 2026)
col_26_2_2_rows = [
    (
        "Abertura",
        "Às quatorze horas do dia dezoito de dezembro de dois mil e vinte e seis, por meio de ambiente virtual institucional, reuniu-se ordinariamente o Colegiado do Curso Superior de Tecnologia em Análise e Desenvolvimento de Sistemas (ADS). O Coordenador do Curso e Presidente do Colegiado, Professor Hamilcar Pereira da Silva, declarou aberta a sessão, acolhendo os docentes membros, Professores Marcos Cruz de Azevedo, Selma Sant'Anna de Fonseca e Denise Moraes do Nascimento Vieira, e a representante discente, Ana Carolina Ramos da Cruz, verificando a presença regimental dos convocados para o encerramento do ano letivo de 2026.",
        "Sem deliberação. Abertura e registro de quórum regulamentar da sessão."
    ),
    (
        "Balanço dos Indicadores Acadêmicos e Desempenho no AVA em 2026.2",
        "O Colegiado apreciou os relatórios de rendimento acadêmico, retenção e taxas de sucesso dos discentes no período 2026.2 encaminhados pelo NDE. O corpo docente e a representação discente concordaram que o acompanhamento sistemático e os atendimentos tutoriais foram determinantes para os resultados positivos alcançados pelos estudantes nas disciplinas de programação e arquitetura de sistemas.",
        "APROVADO por unanimidade. Homologa-se o relatório consolidado de desempenho acadêmico e retenção referente a 2026.2."
    ),
    (
        "Avaliação dos Relatórios da CPA (Comissão Própria de Avaliação)",
        "Foi analisado pelo Colegiado o plano de ação formulado em resposta aos relatórios da Comissão Própria de Avaliação (CPA) de 2026. A professora Selma Sant'Anna de Fonseca destacou a importância de manter a qualificação contínua dos recursos das UAs, enquanto o professor Marcos Cruz de Azevedo sublinhou o mérito do retorno constante das demandas discentes.",
        "APROVADO por unanimidade. Fica aprovado o plano de ação pedagógico decorrente da avaliação institucional da CPA."
    ),
    (
        "Consolidação dos Projetos de Extensão e Atividades Práticas Curriculares",
        "Foram submetidos à homologação do Colegiado os dossiês das atividades de extensão curricularizadas desenvolvidas pelos discentes de ADS durante o segundo semestre de 2026. A representante discente Ana Carolina Ramos da Cruz destacou a satisfação dos alunos em aplicar o conhecimento técnico em demandas reais da sociedade. O Colegiado parabenizou os orientadores e estudantes pelo trabalho executado.",
        "APROVADO por unanimidade. Homologam-se as atividades extensionistas e as respectivas cargas horárias cumpridas no semestre 2026.2."
    ),
    (
        "Diretrizes Pedagógicas e Planejamento Acadêmico para o Semestre 2027.1",
        "O Colegiado deliberou sobre o planejamento pedagógico para 2027.1, incluindo matriz de ofertas, semanas de acolhimento e nivelamento em programação. A professora Denise Moraes do Nascimento Vieira ressaltou que a organização prévia do calendário letivo assegura tranquilidade e previsibilidade pedagógica para o corpo docente e discente.",
        "APROVADO por unanimidade. Aprova-se o planejamento acadêmico e as diretrizes de oferta de disciplinas para o período letivo de 2027.1."
    ),
    (
        "Encerramento",
        "Não havendo mais assuntos a serem tratados na presente pauta, o Coordenador e Presidente Hamilcar Pereira da Silva expressou sua profunda gratidão aos docentes membros e à representação discente pela dedicação e harmonia institucional mantidas em 2026, declarando encerrada a sessão às dezesseis horas, lavrando-se a respectiva ata acadêmica oficial.",
        "Sem deliberação. Encerramento formal e registro da ata para fins de conferência e assinaturas eletrônicas."
    )
]

# ==============================================================================
# GERAÇÃO E GRAVAÇÃO LOCAL
# ==============================================================================

# 1. Colegiado 26.1 (2ª Reunião)
f_col_26_1 = os.path.join(LOCAL_OUTPUT_DIR, "Ata_Reuniao_Colegiado_ADS_17_JUL_2026.docx")
generate_doc_from_template(TEMPLATE_COL, col_26_1_rows, f_col_26_1)

# 2. NDE 26.2 (1ª Reunião)
f_nde_26_2_1 = os.path.join(LOCAL_OUTPUT_DIR, "Ata_Reuniao_NDE_ADS_10_AGO_2026.docx")
generate_doc_from_template(TEMPLATE_NDE, nde_26_2_1_rows, f_nde_26_2_1)

# 3. Colegiado 26.2 (1ª Reunião)
f_col_26_2_1 = os.path.join(LOCAL_OUTPUT_DIR, "Ata_Reuniao_Colegiado_ADS_17_AGO_2026.docx")
generate_doc_from_template(TEMPLATE_COL, col_26_2_1_rows, f_col_26_2_1)

# 4. NDE 26.2 (2ª Reunião)
f_nde_26_2_2 = os.path.join(LOCAL_OUTPUT_DIR, "Ata_Reuniao_NDE_ADS_11_DEZ_2026.docx")
generate_doc_from_template(TEMPLATE_NDE, nde_26_2_2_rows, f_nde_26_2_2)

# 5. Colegiado 26.2 (2ª Reunião)
f_col_26_2_2 = os.path.join(LOCAL_OUTPUT_DIR, "Ata_Reuniao_Colegiado_ADS_18_DEZ_2026.docx")
generate_doc_from_template(TEMPLATE_COL, col_26_2_2_rows, f_col_26_2_2)

print("\n=== Todos os arquivos (DOCX e PDF) gerados com o NOVO MODELO localmente! ===")

# ==============================================================================
# SINCRONIZAÇÃO COM O GOOGLE DRIVE NA PASTA .ATAS
# ==============================================================================
print("\n=== Sincronizando com as pastas de .ATAS no Google Drive ===")

def copy_file_and_pdf(local_docx, target_uri):
    copy_to_gdrive(local_docx, target_uri)
    pdf_double = local_docx + '.pdf'
    if os.path.exists(pdf_double):
        copy_to_gdrive(pdf_double, target_uri)

# 1. Colegiado 26.1 (colocar a 2ª ata que faltava em Colegiado 26.1)
col_26_1_uri = f"{BASE_URI_COL_ATAS}/26.1"
copy_file_and_pdf(f_col_26_1, col_26_1_uri)

# 2. Criar subpasta 26.2 em NDE/Atas e copiar as duas atas de 26.2
nde_26_2_uri = ensure_gdrive_folder(BASE_URI_NDE_ATAS, "26.2")
copy_file_and_pdf(f_nde_26_2_1, nde_26_2_uri)
copy_file_and_pdf(f_nde_26_2_2, nde_26_2_uri)

# 3. Criar subpasta 26.2 em Colegiado e copiar as duas atas de 26.2
col_26_2_uri = ensure_gdrive_folder(BASE_URI_COL_ATAS, "26.2")
copy_file_and_pdf(f_col_26_2_1, col_26_2_uri)
copy_file_and_pdf(f_col_26_2_2, col_26_2_uri)

print("\n=== Sincronização com .ATAS concluída com êxito! ===")
