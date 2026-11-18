import os
import docx
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_guide_docx(docx_filepath):
    doc = docx.Document()
    
    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Title
    p_title = doc.add_paragraph()
    r_title = p_title.add_run("📘 Roteiro Oficial de Uso — AVALIA AutoBatch Desktop v5.1")
    r_title.font.name = 'Segoe UI'
    r_title.font.size = Pt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A) # Navy Blue
    p_title.paragraph_format.space_after = Pt(4)

    # Subtitle / Author
    p_sub = doc.add_paragraph()
    r_sub1 = p_sub.add_run("Automação de Cadastro de Questões em Lote no AVALIA (Grupo A)\n")
    r_sub1.font.name = 'Segoe UI'
    r_sub1.font.size = Pt(11)
    r_sub1.font.italic = True
    r_sub1.font.color.rgb = RGBColor(0x47, 0x55, 0x69)
    
    r_sub2 = p_sub.add_run("Criado por: Hamilcar Silva")
    r_sub2.font.name = 'Segoe UI'
    r_sub2.font.size = Pt(11)
    r_sub2.font.bold = True
    r_sub2.font.color.rgb = RGBColor(0x05, 0x96, 0x69) # Green
    p_sub.paragraph_format.space_after = Pt(16)

    # Helper for Section Headers
    def add_h1(text):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.name = 'Segoe UI'
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(8)

    def add_h2(text):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.name = 'Segoe UI'
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)

    def add_p(text, bold_prefix=None):
        p = doc.add_paragraph()
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.font.name = 'Segoe UI'
            r_b.font.size = Pt(10.5)
            r_b.font.bold = True
        r = p.add_run(text)
        r.font.name = 'Segoe UI'
        r.font.size = Pt(10.5)
        p.paragraph_format.space_after = Pt(6)
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.font.name = 'Segoe UI'
            r_b.font.size = Pt(10.5)
            r_b.font.bold = True
        r = p.add_run(text)
        r.font.name = 'Segoe UI'
        r.font.size = Pt(10.5)
        p.paragraph_format.space_after = Pt(4)

    # 1. Objetivos
    add_h1("🎯 Objetivos do Aplicativo")
    add_p("O AVALIA AutoBatch Desktop foi projetado com base em princípios de Usabilidade e Interação Humano-Computador (IHC) para automatizar a inserção repetitiva de questões acadêmicas no sistema AVALIA do Grupo A, proporcionando:")
    add_bullet(" Cadastro automático de 10 a 50+ questões por disciplina em poucos minutos.", "🚀 Agilidade:")
    add_bullet(" Preenchimento exato de enunciado, alternativas, gabarito e feedbacks pedagógicos.", "🎯 Precisão:")
    add_bullet(" Captura automática dos códigos de ID gerados pelo AVALIA e exportação instantânea de relatórios em Microsoft Word (.docx) e Markdown (.md).", "📄 Rastreabilidade:")

    # 2. Passo a Passo
    add_h1("📋 Passo a Passo de Utilização")

    add_h2("1️⃣ Passo 1 — Preparar a Planilha Excel (.xlsx)")
    add_p("Abra o aplicativo AVALIA AutoBatch Desktop.")
    add_p("No Passo 2 da tela principal, clique no botão '📥 Baixar Modelo de Planilha Exemplo (.xlsx)' para obter o arquivo base.")
    add_p("Preencha as colunas da planilha no Excel de acordo com os padrões:")
    add_bullet(" Código/Nome único da questão (Ex: UA-01_QUESTÃO-1_OBJ-1_FÁCIL).", "Identificação da questão: ")
    add_bullet(" Tema principal da questão.", "Palavra chave: ")
    add_bullet(" questão de complementação Simples, resposta Múltipla ou Asserção e Razão.", "Tipo da Questão: ")
    add_bullet(" Reconhecimento, Compreensão ou Aplicação.", "Nível cognitivo: ")
    add_bullet(" Texto descritivo completo do enunciado da questão.", "Texto da Questão: ")
    add_bullet(" Alternativa A, Alternativa B, Alternativa C, Alternativa D (e Alternativa E se houver).", "Alternativas: ")
    add_bullet(" Texto explicativo indicando o gabarito correto (Ex: 'A resposta certa é a alternativa A...').", "Feedback da questão: ")

    add_h2("2️⃣ Passo 2 — Abrir o Navegador Chrome AVALIA")
    add_p("No Passo 1 do aplicativo, clique no botão '🌐 Abrir Chrome AVALIA (Porta 9222)'.")
    add_p("Uma janela dedicada do Google Chrome será aberta. Faça login com suas credenciais do AVALIA.")

    add_h2("3️⃣ Passo 3 — Navegar até a Etapa 4 da Disciplina")
    add_p("No Chrome aberto, selecione a disciplina desejada e avance até a Etapa 4 — Inserção de Questão (onde aparece o formulário para digitação).")
    add_p("Volte ao aplicativo e marque a caixa de seleção '☑️ Confirmo que já naveguei até o Passo 4 (Inserção de Questão) no Chrome'. O badge superior ficará verde ('🟢 PRONTO NA ETAPA 4').")

    add_h2("4️⃣ Passo 4 — Carregar a Planilha e Iniciar a Automação")
    add_p("Clique em '📂 Escolher Excel...' e selecione o arquivo da disciplina.")
    add_p("O aplicativo exibirá a validação e a contagem de questões detectadas.")
    add_p("Clique no botão '🚀 INICIAR INSERÇÃO EM LOTE' e acompanhe a barra de progresso e o console de logs em tempo real.")

    add_h2("5️⃣ Passo 5 — Finalização e Troca Sequencial de Disciplina")
    add_p("Ao concluir o lote, uma mensagem de sucesso notificará a quantidade de questões registradas.")
    add_p("O aplicativo perguntará se deseja carregar a planilha de outra disciplina.")
    add_p("Ao clicar em SIM, o seletor de arquivos abre automaticamente e a confirmação da Etapa 4 é resetada para garantir a segurança no lançamento da próxima disciplina.")

    add_h2("6️⃣ Passo 6 — Relatórios Oficiais Gerados (.docx e .md)")
    add_p("Ao final de cada lote, o programa gera dois relatórios na pasta do aplicativo:")
    add_bullet(" Relatório oficial formatado com tabela profissional em Microsoft Word.", "Relatório Word (.docx): ")
    add_bullet(" Relatório estruturado em texto plano Markdown.", "Relatório Markdown (.md): ")

    # Tabela Exemplo no Word
    add_h2("📊 Estrutura da Tabela do Relatório de Saída")
    headers = ["#", "Identificador Original", "Código / ID no AVALIA", "Resposta Correta", "Tipo de Questão"]
    table = doc.add_table(rows=3, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
            <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

    hdr_row = table.rows[0]
    for c_idx, h_text in enumerate(headers):
        cell = hdr_row.cells[c_idx]
        cell.text = ""
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.space_before = Pt(4)
        run = p.add_run(h_text)
        run.font.name = 'Segoe UI'
        run.font.size = Pt(9.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        tcPr = cell._tc.get_or_add_tcPr()
        tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="1E3A8A"/>'))

    sample_rows = [
        ["1", "UA-01_Q01", "1858323", "Alternativa A", "Resposta Múltipla (62)"],
        ["2", "UA-01_Q02", "1858324", "Alternativa C", "Asserção e Razão (63)"]
    ]
    for r_idx, s_row in enumerate(sample_rows, start=1):
        row = table.rows[r_idx]
        bg_color = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(s_row):
            cell = row.cells[c_idx]
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.space_before = Pt(4)
            run = p.add_run(val)
            run.font.name = 'Segoe UI'
            run.font.size = Pt(9)
            if c_idx == 2:
                run.font.bold = True
                run.font.color.rgb = RGBColor(0x1D, 0x4E, 0xD8)
            tcPr = cell._tc.get_or_add_tcPr()
            tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_color}"/>'))

    add_h1("💡 Dicas e Boas Práticas")
    add_bullet(" Não minimize ou feche a janela do Chrome enquanto a automação estiver em andamento.", "Atenção ao Chrome: ")
    add_bullet(" Se houver alguma instabilidade no servidor AVALIA, a automação efetuará a re-tentativa automaticamente.", "Resiliência: ")
    add_bullet(" Para pausar ou interromper a execução com segurança, clique no botão '⏹️ PAUSAR/PARAR'.", "Interrupção: ")

    doc.save(docx_filepath)
    print(f"✅ Roteiro Word gerado em: {docx_filepath}")

if __name__ == "__main__":
    create_guide_docx("/home/hamilcar/Antigravity/Roteiro_de_Uso_AVALIA_AutoBatch.docx")
