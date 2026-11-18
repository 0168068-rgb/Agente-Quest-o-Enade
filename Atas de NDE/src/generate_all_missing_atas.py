import os
import sys

# Ensure src is in python path
sys.path.insert(0, '/home/hamilcar/Antigravity/Atas de NDE/src')

from docx_generator import (
    generate_nde_doc,
    generate_colegiado_doc,
    ensure_gdrive_folder,
    copy_to_gdrive,
    BASE_URI_NDE,
    BASE_URI_COL,
    LOCAL_OUTPUT_DIR
)

os.makedirs(LOCAL_OUTPUT_DIR, exist_ok=True)

# ==============================================================================
# 1. PAR 1: 2026.1 (2ª REUNIÃO)
# ==============================================================================

# NDE 2026.1 (2ª Reunião) - 06/07/2026
nde_2026_1_pautas = [
    (
        "Abertura",
        "A reunião foi aberta pelo coordenador do curso, Prof. Hamilcar Pereira da Silva, que deu boas-vindas aos membros do NDE e destacou a finalidade da sessão voltada ao encerramento pedagógico do semestre letivo 2026.1 e consolidação das metas acadêmicas planejadas.",
        "Sem sugestões."
    ),
    (
        "Avaliação dos Resultados da Avaliação Integrada e Banco de Questões",
        "O coordenador apresentou o consolidado de rendimento dos estudantes na Avaliação Integrada do semestre, ressaltando a boa participação discente. O professor Alan Jefferson destacou a evolução dos discentes nas disciplinas de desenvolvimento e banco de dados. O professor Telmo Viana apontou que o modelo no formato ENADE tem ampliado a maturidade dos alunos na resolução de problemas. O professor Luciano Padilha ressaltou a necessidade de calibração contínua dos distratores nas disciplinas de infraestrutura. O professor Ronaldo Paulucci sugeriu a expansão do banco de questões com problemas aplicados ao mercado de trabalho.",
        "Encaminhar relatório de desempenho da Avaliação Integrada ao Colegiado e consolidar o cronograma de atualização do banco de questões para o próximo semestre."
    ),
    (
        "Acompanhamento de Evasão e Frequência Discente no AVA",
        "O coordenador expôs os índices de retenção e as taxas de evasão observadas ao longo do período 2026.1. O professor Telmo Viana salientou a eficácia das intervenções pedagógicas e dos comunicados preventivos disparados no meio do semestre. O professor Alan Jefferson enfatizou que o acolhimento aos alunos com menor frequência nas primeiras semanas reduziu o abandono. O professor Luciano Padilha sugeriu a continuidade do monitoramento sistemático das trilhas de aprendizagem no AVA. O professor Ronaldo Paulucci reforçou a importância da atuação conjunta entre tutores e docentes no acompanhamento dos discentes em risco acadêmico.",
        "Manter a rotina de monitoramento dos acessos ao AVA e aprimorar o protocolo de acolhimento discente para o semestre subsequente."
    ),
    (
        "Análise das Atividades Extensionistas e Curricularização da Extensão",
        "O coordenador destacou o andamento dos projetos de extensão curricularizados desenvolvidos pelos alunos no semestre, em consonância com as diretrizes regulatórias vigentes. O professor Luciano Padilha relatou o impacto positivo das ações comunitárias na área de inclusão digital e desenvolvimento de software para entidades parceiras. O professor Alan Jefferson destacou o engajamento discente e a relevância social dos projetos apresentados. O professor Telmo Viana sugeriu a criação de um repositório institucional com os melhores projetos desenvolvidos. O professor Ronaldo Paulucci ressaltou a necessidade de alinhamento contínuo entre os projetos de extensão e o perfil do egresso.",
        "Encaminhar os relatórios das atividades de extensão ao Colegiado de Curso para homologação e registro acadêmico."
    ),
    (
        "Planejamento Pedagógico e Diretrizes para o Semestre 2026.2",
        "O coordenador colocou em pauta o planejamento pedagógico para o segundo semestre de 2026, incluindo a revisão preliminar dos planos de ensino, cronograma de aulas inaugurais e oferta de disciplinas. O professor Ronaldo Paulucci propôs o reforço das oficinas de nivelamento de lógica de programação. O professor Telmo Viana recomendou a atualização prévia das referências bibliográficas virtuais nas Unidades de Aprendizagem (UAs). O professor Luciano Padilha sugeriu workshops temáticos sobre computação em nuvem e segurança da informação. O professor Alan Jefferson enfatizou a importância da pontualidade na publicação dos materiais no AVA.",
        "Encaminhar a proposta de planejamento acadêmico e cronograma do semestre 2026.2 para deliberação do Colegiado."
    ),
    (
        "Encerramento",
        "Sem mais assuntos a tratar, o coordenador agradeceu o empenho e a dedicação de todos os docentes membros do NDE ao longo do semestre letivo de 2026.1, encerrando formalmente a sessão.",
        "Término da reunião."
    )
]

nde_2026_1_file = os.path.join(LOCAL_OUTPUT_DIR, "Ata_Reuniao_NDE_ADS_06_JUL_2026.docx")
generate_nde_doc("06/07/2026", "15H", "16H", "2026.1", nde_2026_1_pautas, nde_2026_1_file)

# Colegiado 2026.1 (2ª Reunião) - 13/07/2026
col_2026_1_pautas = [
    (
        "Abertura",
        "Aos 13 dias do mês de julho de 2026, às 14h, reuniu-se ordinariamente o Colegiado do Curso Superior de Tecnologia em Análise e Desenvolvimento de Sistemas da Universidade Iguaçu (UNIG), sob a presidência do coordenador Prof. Hamilcar Pereira da Silva. O presidente abriu os trabalhos saudando os docentes e a representação discente, ressaltando o propósito de apreciar os relatórios e propostas encaminhadas pelo NDE para o encerramento do período 2026.1.",
        "Aprovado por unanimidade. Registro formal da abertura da reunião."
    ),
    (
        "Avaliação dos Resultados da Avaliação Integrada e Banco de Questões",
        "O Colegiado apreciou os resultados gerais de desempenho dos discentes na Avaliação Integrada do período 2026.1 encaminhados pelo NDE. Os membros destacaram a consistência dos instrumentos avaliativos e a consolidação do padrão ENADE. A representação discente ressaltou que as avaliações simularam adequadamente os desafios práticos da profissão. Os docentes manifestaram concordância quanto à necessidade de contínua atualização do banco de questões.",
        "Aprovado por unanimidade. Homologam-se os resultados da Avaliação Integrada e aprova-se o cronograma de atualização do banco de itens."
    ),
    (
        "Acompanhamento de Evasão e Frequência Discente no AVA",
        "Foi apresentado ao Colegiado o relatório de retenção discente e os índices de frequência no Ambiente Virtual de Aprendizagem do primeiro semestre. Os membros debateram a eficácia das medidas preventivas adotadas pela coordenação e corpo docente, ressaltando que o acompanhamento individualizado mitigou o abandono escolar. Destacou-se a necessidade de fortalecer as ações de tutoria e comunicação nos períodos iniciais.",
        "Aprovado por unanimidade. Delibera-se pela continuidade das ações de retenção e acolhimento contínuo aos estudantes no AVA."
    ),
    (
        "Análise das Atividades Extensionistas e Curricularização da Extensão",
        "Foram submetidos à apreciação do Colegiado os relatórios das atividades de extensão curricularizadas desenvolvidas pelos discentes durante o período 2026.1. O colegiado congratulou os professores orientadores e os alunos pelas iniciativas comunitárias executadas com apoio de tecnologias digitais, constatando o pleno cumprimento da carga horária extensionista regulamentar.",
        "Aprovado por unanimidade. Homologam-se as atividades de extensão curricularizadas desenvolvidas no período 2026.1."
    ),
    (
        "Planejamento Pedagógico e Diretrizes para o Semestre 2026.2",
        "O Colegiado debateu o planejamento pedagógico para o semestre 2026.2 proposto pelo NDE, contemplando o cronograma letivo, matriz de ofertas, oficinas de nivelamento de programação e aprimoramento das bibliografias virtuais nas UAs. Os membros consideraram o planejamento equilibrado e compatível com o calendário institucional e acadêmico da UNIG.",
        "Aprovado por unanimidade. Aprova-se o planejamento acadêmico e cronograma pedagógico para o período letivo 2026.2."
    ),
    (
        "Encerramento",
        "Esgotada a pauta e não havendo outras manifestações, o coordenador agradeceu a valiosa contribuição dos docentes e da representante estudantil, encerrando a presente reunião às 15h, da qual se lavrou a presente ata.",
        "Aprovado por unanimidade. Registro formal do encerramento da sessão."
    )
]

col_2026_1_file = os.path.join(LOCAL_OUTPUT_DIR, "Reuniao_Colegiado_ADS_13_JUL_2026.docx")
generate_colegiado_doc("13/07/2026", "14H", "15H", "2026.1", col_2026_1_pautas, col_2026_1_file)

# ==============================================================================
# 2. PAR 2: 2026.2 (1ª REUNIÃO)
# ==============================================================================

# NDE 2026.2 (1ª Reunião) - 10/08/2026
nde_2026_2_1_pautas = [
    (
        "Abertura",
        "A reunião foi aberta pelo coordenador do curso, Prof. Hamilcar Pereira da Silva, que acolheu os membros do NDE no início do segundo semestre letivo de 2026, destacando as prioridades acadêmicas para o período 2026.2 e o compromisso institucional com a excelência do curso em EAD.",
        "Sem sugestões."
    ),
    (
        "Acolhimento Discente e Aula Inaugural de 2026.2",
        "O coordenador apresentou as diretrizes para a recepção dos calouros e acolhimento dos veteranos no segundo semestre letivo, ressaltando o papel da aula inaugural na ambientação aos recursos do AVA. O professor Alan Jefferson sugeriu a realização de uma live técnica para apresentar a trilha de formação aos novos estudantes. O professor Telmo Viana destacou a importância de apresentar os canais de tutoria e apoio pedagógico. O professor Luciano Padilha recomendou disponibilizar um guia rápido de navegação e boas práticas de estudo no AVA. O professor Ronaldo Paulucci reforçou o impacto positivo do contato precoce para motivação dos ingressantes.",
        "Implementar a programação da aula inaugural e estruturar materiais de acolhimento para publicação imediata no AVA."
    ),
    (
        "Atualização do Banco de Questões e Cronograma da Avaliação Integrada",
        "O coordenador destacou a necessidade de revisão tempestiva das questões para a Avaliação Integrada do semestre 2026.2. O professor Ronaldo Paulucci enfatizou que as questões devem priorizar o raciocínio crítico e competências previstas no PPC. O professor Luciano Padilha sugeriu critérios rigorosos de validação prévia dos enunciados. O professor Alan Jefferson reforçou a pertinência de incluir estudos de casos reais. O professor Telmo Viana sugeriu estabelecer um cronograma claro para entrega e validação dos itens por parte dos docentes.",
        "Encaminhar proposta de cronograma e diretrizes de revisão do banco de questões ao Colegiado de Curso."
    ),
    (
        "Adequação Curricular e Inserção de Tecnologias Emergentes (IA e Cloud)",
        "O coordenador colocou em pauta a contínua modernização dos conteúdos programáticos com base nas tendências do setor tecnológico, especialmente em Inteligência Artificial Generativa e Arquiteturas em Nuvem. O professor Telmo Viana ressaltou a relevância de abordar princípios éticos e práticos do uso de IA no desenvolvimento de software. O professor Alan Jefferson sugeriu a proposição de projetos integradores com microsserviços e cloud computing. O professor Luciano Padilha propôs parcerias acadêmicas para acesso a laboratórios virtuais em nuvem. O professor Ronaldo Paulucci reforçou a importância de manter as ementas alinhadas com as demandas do mercado de TI.",
        "Propor a integração de temas emergentes nas atividades complementares e projetos práticos das disciplinas do curso."
    ),
    (
        "Monitoramento de Engajamento e Prevenção à Evasão no Semestre",
        "O coordenador enfatizou a importância de monitorar semanalmente os acessos dos estudantes no AVA desde os primeiros dias letivos. O professor Alan Jefferson propôs estratégias de contato ativo com alunos sem acesso nas duas primeiras semanas. O professor Telmo Viana sugeriu o uso de avisos pontuais e mensagens de incentivo pelos docentes. O professor Luciano Padilha sugeriu articular ações conjuntas com o NEAD para suporte técnico ágil aos estudantes. O professor Ronaldo Paulucci destacou a relevância do engajamento em fóruns avaliativos para manter o ritmo acadêmico.",
        "Adotar painel de monitoramento quinzenal de acessos e acionar suporte tutorial preventivo para estudantes com baixa participação."
    ),
    (
        "Encerramento",
        "Não havendo outros assuntos a tratar, o coordenador agradeceu a participação e as ricas contribuições dos professores, encerrando a primeira reunião do NDE do semestre 2026.2.",
        "Término da reunião."
    )
]

nde_2026_2_1_file = os.path.join(LOCAL_OUTPUT_DIR, "Ata_Reuniao_NDE_ADS_10_AGO_2026.docx")
generate_nde_doc("10/08/2026", "15H", "16H", "2026.2", nde_2026_2_1_pautas, nde_2026_2_1_file)

# Colegiado 2026.2 (1ª Reunião) - 17/08/2026
col_2026_2_1_pautas = [
    (
        "Abertura",
        "Aos 17 dias do mês de agosto de 2026, às 14h, reuniu-se o Colegiado do Curso Superior de Tecnologia em Análise e Desenvolvimento de Sistemas da Universidade Iguaçu (UNIG), sob a presidência do coordenador Prof. Hamilcar Pereira da Silva, com quórum regimental de docentes e representação discente. O coordenador abriu a sessão saudando os presentes e apresentando as pautas prioritárias originadas do NDE para início do semestre letivo 2026.2.",
        "Aprovado por unanimidade. Registro formal da abertura dos trabalhos."
    ),
    (
        "Acolhimento Discente e Aula Inaugural de 2026.2",
        "O Colegiado apreciou o plano de acolhimento e a programação da aula inaugural para os ingressantes e veteranos do semestre 2026.2 encaminhados pelo NDE. A representante discente manifestou aprovação quanto à realização de encontros síncronos explicativos e à disponibilização do guia rápido do AVA. O corpo docente salientou a importância de integrar os alunos desde o primeiro momento.",
        "Aprovado por unanimidade. Homologa-se o plano de acolhimento e programação das aulas inaugurais do semestre 2026.2."
    ),
    (
        "Atualização do Banco de Questões e Cronograma da Avaliação Integrada",
        "Foi submetido à deliberação do Colegiado o cronograma de atualização do banco de questões e as diretrizes pedagógicas para a Avaliação Integrada de 2026.2. Os membros ressaltaram a conformidade com as diretrizes do ENADE e a relevância de avaliar competências analíticas dos discentes.",
        "Aprovado por unanimidade. Delibera-se pela aprovação do cronograma e critérios da Avaliação Integrada de 2026.2."
    ),
    (
        "Adequação Curricular e Inserção de Tecnologias Emergentes (IA e Cloud)",
        "O Colegiado debateu a proposta do NDE de incorporar abordagens de tecnologias emergentes (Inteligência Artificial e Computação em Nuvem) nas disciplinas aplicadas, projetos integradores e atividades extracurriculares. Os membros destacaram a importância da inovação contínua para assegurar a empregabilidade dos egressos da UNIG.",
        "Aprovado por unanimidade. Aprova-se a inserção de temas de IA e Cloud nos projetos práticos e atividades integradoras."
    ),
    (
        "Monitoramento de Engajamento e Prevenção à Evasão no Semestre",
        "Foi apreciado o plano estratégico de acompanhamento contínuo de engajamento discente no AVA, visando mitigar a evasão por meio de intervenções pedagógicas e suporte preventivo conjunto entre coordenação, docentes e tutoria do NEAD. O colegiado reiterou o compromisso com o sucesso acadêmico discente.",
        "Aprovado por unanimidade. Delibera-se pela aprovação das diretrizes de monitoramento e retenção discente no AVA."
    ),
    (
        "Encerramento",
        "Sem outros assuntos a tratar, o coordenador agradeceu a presença de todos os integrantes do colegiado, registrando a harmonia institucional e dando por encerrada a reunião às 15h.",
        "Aprovado por unanimidade. Registro do encerramento da sessão."
    )
]

col_2026_2_1_file = os.path.join(LOCAL_OUTPUT_DIR, "Reuniao_Colegiado_ADS_17_AGO_2026.docx")
generate_colegiado_doc("17/08/2026", "14H", "15H", "2026.2", col_2026_2_1_pautas, col_2026_2_1_file)

# ==============================================================================
# 3. PAR 3: 2026.2 (2ª REUNIÃO)
# ==============================================================================

# NDE 2026.2 (2ª Reunião) - 11/12/2026
nde_2026_2_2_pautas = [
    (
        "Abertura",
        "A reunião foi aberta pelo coordenador do curso, Prof. Hamilcar Pereira da Silva, que deu boas-vindas aos professores membros do NDE, destacando que a reunião tem como objetivo a consolidação dos resultados pedagógicos do período 2026.2, balanço das metas institucionais e diretrizes curriculares para o próximo ano letivo.",
        "Sem sugestões."
    ),
    (
        "Balanço dos Indicadores Acadêmicos e Desempenho no AVA em 2026.2",
        "O coordenador apresentou os dados consolidados de rendimento acadêmico, aprovação e participação dos discentes nas disciplinas do segundo semestre. O professor Telmo Viana destacou os ganhos qualitativos obtidos a partir dos acompanhamentos quinzenais. O professor Alan Jefferson ressaltou o bom aproveitamento dos estudantes nas disciplinas de desenvolvimento de software e projetos web. O professor Luciano Padilha ressaltou o aumento do uso das bibliotecas digitais nas consultas acadêmicas. O professor Ronaldo Paulucci salientou a importância de manter ações contínuas de nivelamento para os próximos semestres.",
        "Encaminhar o relatório de indicadores acadêmicos e retenção discente ao Colegiado de Curso."
    ),
    (
        "Avaliação dos Relatórios da CPA (Comissão Própria de Avaliação)",
        "O coordenador trouxe à mesa a análise das devolutivas dos alunos e docentes na Avaliação Institucional conduzida pela CPA referente a 2026. O professor Alan Jefferson comentou a satisfação dos alunos com a clareza dos conteúdos e dos prazos. O professor Telmo Viana apontou a necessidade de continuar aperfeiçoando os canais de feedback das atividades virtuais. O professor Luciano Padilha sugeriu a elaboração de um plano de melhorias focado no aprimoramento dos recursos multimídia das UAs. O professor Ronaldo Paulucci reforçou a importância de divulgar à comunidade acadêmica as melhorias implantadas com base na CPA.",
        "Elaborar minuta de plano de ação pedagógico em resposta aos apontamentos da CPA e submeter à apreciação do Colegiado."
    ),
    (
        "Consolidação dos Projetos de Extensão e Atividades Práticas Curriculares",
        "O coordenador relatou o sucesso da culminância dos projetos de extensão universitária desenvolvidos no semestre, destacando as soluções tecnológicas entregues à comunidade pelos estudantes de ADS. O professor Luciano Padilha ressaltou a evolução dos discentes em competências socioemocionais e trabalho em equipe. O professor Ronaldo Paulucci pontuou o alinhamento das atividades com os Objetivos de Desenvolvimento Sustentável (ODS). O professor Alan Jefferson destacou a importância de arquivar o portfólio digital das entregas extensionistas. O professor Telmo Viana enfatizou o papel da extensão na consolidação da imagem institucional da UNIG.",
        "Homologar internamente a validação das horas de extensão e remeter os dossiês ao Colegiado."
    ),
    (
        "Diretrizes Pedagógicas e Planejamento Acadêmico para o Semestre 2027.1",
        "O coordenador apresentou as diretrizes preliminares para a oferta curricular e organização acadêmica do primeiro semestre de 2027. O professor Telmo Viana recomendou a manutenção dos simulados e semanas de acolhimento. O professor Alan Jefferson sugeriu a ampliação das oficinas práticas no início do período. O professor Ronaldo Paulucci destacou a importância de planejar com antecedência o calendário de reuniões ordinárias do NDE para 2027. O professor Luciano Padilha propôs a revisão das bibliografias básicas e complementares do PPC.",
        "Encaminhar a proposta de diretrizes do planejamento de 2027.1 para deliberação do Colegiado de Curso."
    ),
    (
        "Encerramento",
        "Não havendo outros assuntos a tratar, o coordenador agradeceu calorosamente o trabalho coletivo, a dedicação e o rigor acadêmico demonstrados por todos os membros do NDE ao longo do ano de 2026, encerrando oficialmente os trabalhos.",
        "Término da reunião."
    )
]

nde_2026_2_2_file = os.path.join(LOCAL_OUTPUT_DIR, "Ata_Reuniao_NDE_ADS_11_DEZ_2026.docx")
generate_nde_doc("11/12/2026", "15H", "16H", "2026.2", nde_2026_2_2_pautas, nde_2026_2_2_file)

# Colegiado 2026.2 (2ª Reunião) - 18/12/2026
col_2026_2_2_pautas = [
    (
        "Abertura",
        "Aos 18 dias do mês de dezembro de 2026, às 14h, reuniu-se ordinariamente o Colegiado do Curso Superior de Tecnologia em Análise e Desenvolvimento de Sistemas da Universidade Iguaçu (UNIG), sob a presidência do coordenador Prof. Hamilcar Pereira da Silva, contando com a presença dos docentes e da representante estudantil. O presidente abriu a sessão enfatizando o fechamento do ano acadêmico de 2026 e a apreciação das deliberações enviadas pelo NDE.",
        "Aprovado por unanimidade. Registro formal da abertura da reunião."
    ),
    (
        "Balanço dos Indicadores Acadêmicos e Desempenho no AVA em 2026.2",
        "O Colegiado apreciou os relatórios finais de rendimento acadêmico, retenção e taxas de aprovação dos discentes no período 2026.2. O corpo docente e a representação discente concordaram que o acompanhamento continuado foi determinante para os resultados positivos alcançados pelos estudantes nas avaliações e disciplinas.",
        "Aprovado por unanimidade. Homologa-se o relatório de desempenho acadêmico e indicadores do período 2026.2."
    ),
    (
        "Avaliação dos Relatórios da CPA (Comissão Própria de Avaliação)",
        "Foi analisada a proposta de plano de ação em atendimento às avaliações da Comissão Própria de Avaliação (CPA) de 2026. O colegiado deliberou favoravelmente sobre a intensificação dos investimentos na qualidade dos recursos instrucionais do AVA e na transparência das ações institucionais decorrentes da avaliação docente e discente.",
        "Aprovado por unanimidade. Delibera-se pela aprovação do plano de ação e melhorias pedagógicas decorrentes da CPA."
    ),
    (
        "Consolidação dos Projetos de Extensão e Atividades Práticas Curriculares",
        "Foram apresentados para homologação os dossiês das atividades de extensão curricularizadas desenvolvidas pelos alunos no encerramento de 2026.2. O Colegiado ressaltou a relevância social dos projetos aplicados à comunidade e parabenizou a coordenação e estudantes pelo cumprimento exemplar das diretrizes de extensão universitária.",
        "Aprovado por unanimidade. Homologam-se as atividades e cargas horárias dos projetos de extensão de 2026.2."
    ),
    (
        "Diretrizes Pedagógicas e Planejamento Acadêmico para o Semestre 2027.1",
        "Foi submetido à deliberação o planejamento pedagógico preliminar para o ano letivo de 2027.1, incluindo matriz de ofertas, calendários acadêmicos e previsão de acolhimento discente. Os membros deliberaram pela aprovação integral do planejamento para garantir um início de semestre organizado e produtivo.",
        "Aprovado por unanimidade. Aprova-se a proposta de planejamento acadêmico e oferta de disciplinas para 2027.1."
    ),
    (
        "Encerramento",
        "Esgotada a ordem do dia e nada mais havendo a constar, o coordenador expressou profundo reconhecimento a todos os membros do Colegiado pelo profícuo trabalho realizado em 2026, declarando encerrada a sessão às 15h, da qual se lavrou a presente ata.",
        "Aprovado por unanimidade. Registro formal do encerramento da reunião."
    )
]

col_2026_2_2_file = os.path.join(LOCAL_OUTPUT_DIR, "Reuniao_Colegiado_ADS_18_DEZ_2026.docx")
generate_colegiado_doc("18/12/2026", "14H", "15H", "2026.2", col_2026_2_2_pautas, col_2026_2_2_file)

print("\n=== Todos os 6 documentos Word foram gerados com sucesso localmente! ===")

# ==============================================================================
# 4. SINCRONIZAÇÃO COM O GOOGLE DRIVE
# ==============================================================================
print("\n=== Sincronizando com o Google Drive via GVFS ===")

# 1. NDE 2026.1 (2ª ata)
nde_2026_1_dest = f"{BASE_URI_NDE}/2026.1"
copy_to_gdrive(nde_2026_1_file, nde_2026_1_dest)

# 2. Colegiado 2026.1 (2ª ata)
col_2026_1_dest = f"{BASE_URI_COL}/2026.1"
copy_to_gdrive(col_2026_1_file, col_2026_1_dest)

# 3. NDE 2026.2 (Criar subpasta e copiar as 2 atas)
nde_2026_2_dest = ensure_gdrive_folder(BASE_URI_NDE, "2026.2")
copy_to_gdrive(nde_2026_2_1_file, nde_2026_2_dest)
copy_to_gdrive(nde_2026_2_2_file, nde_2026_2_dest)

# 4. Colegiado 2026.2 (Criar subpasta e copiar as 2 atas)
col_2026_2_dest = ensure_gdrive_folder(BASE_URI_COL, "2026.2")
copy_to_gdrive(col_2026_2_1_file, col_2026_2_dest)
copy_to_gdrive(col_2026_2_2_file, col_2026_2_dest)

print("\n=== Processamento concluído com êxito total! ===")
