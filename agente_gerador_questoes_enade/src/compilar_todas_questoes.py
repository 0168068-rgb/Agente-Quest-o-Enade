import os
import json
import re
import pandas as pd
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Diretório raiz das UAs do NEAD
root_dir = "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD"
# Diretório dos arquivos JSON temporários gerados pelo subagente
json_dir = "/home/hamilcar/.gemini/antigravity/brain/05f9b831-631d-4825-9ab6-e91a8c9beac3"

# Mapeamento de Pasta Física -> (Nome Acadêmico Limpo, UA1, UA2, Nome do Arquivo JSON)
disciplinas_map = {
    "Cabeamento estruturado II (seg)": ("Cabeamento estruturado II", 5, 6, "questoes_Cabeamento estruturado II.json"),
    "Compiladores": ("Compiladores", 2, 3, "questoes_Compiladores.json"),
    "Desenvolvimento de Dispositivos Móveis": ("Desenvolvimento de Dispositivos Móveis", 3, 4, "questoes_Desenvolvimento de Dispositivos Móveis.json"),
    "Estrutura de dados(seg)": ("Estrutura de Dados", 3, 4, "questoes_Estrutura de dados.json"),
    "Gerenciamento de Redes": ("Gerenciamento de redes de computadores", 3, 4, "questoes_Gerenciamento de redes de computadores.json"),
    "Infraestrutura de rede (seg)": ("Infraestrutura de redes", 2, 3, "questoes_Infraestrutura de rede.json"),
    "Infraestrutura de TI (4º per Redes)": ("Infraestrutura de TI", 1, 3, "questoes_Infraestrutura de TI.json"),
    "Infraestrutura e Serviços de TI": ("Infraestrutura e serviços de TI", 1, 3, "questoes_Infraestrutura e serviços de TI.json"),
    "Interação Humano-Computador": ("Interação Humano-Computador", 3, 4, "questoes_Interação Humano-Computador.json"),
    "Programação em Python(seg)": ("Programação em PYTHON", 3, 4, "questoes_Programação em Python.json"),
    "Programação WEB II- Desenvolvimento Back-end": ("Programação WEB II - Desenvolvimento back-end", 2, 5, "questoes_Programação WEB II- Desenvolvimento back-end.json"),
    "Projetos de Redes de Computadores (seg)": ("Projeto de Redes de Computadores", 4, 5, "questoes_Projeto de Redes de Computadores.json"),
    "Redes Convergentes": ("Redes Convergentes", 3, 7, "questoes_Redes Convergentes.json"),
    "Redes de Alta disponibilidade (4º Per redes)": ("Redes de Alta Disponibilidade", 3, 6, "questoes_Redes de Alta Disponibilidade.json"),
    "Redes de Computadores(seg)": ("Redes de Computadores", 3, 4, "questoes_Redes de Computadores.json"),
    "Redes de Longa Distância": ("Redes de Longa Distância", 2, 4, "questoes_Redes de Longa Distância.json"),
    "Redes sem Fio (4º Per Redes)": ("Redes Sem Fio", 2, 6, "questoes_Redes Sem Fio.json"),
    "Segurança da Informação": ("Segurança da informação", 2, 4, "questoes_Segurança da informação.json"),
    "Segurança da Informação e Legislação": ("Segurança da Informação e Legislação", 2, 4, "questoes_Segurança da Informação e Legislação.json"),
    "Segurança de Redes de Computadores": ("Segurança de redes de computadores", 2, 6, "questoes_Segurança de redes de computadores.json"),
    "Servidores e computação na Nuvem": ("Servidores e Computação na Nuvem", 3, 4, "questoes_Servidores e Computação na Nuvem.json"),
    "Sistemas Operacionais de Redes Abertas": ("Sistemas Operacionais de Redes Abertas", 2, 5, "questoes_Sistemas Operacionais de Redes Abertas.json")
}

def configurar_idioma_pt_br(doc):
    # Força o idioma pt-BR (Português do Brasil) no estilo Normal
    style = doc.styles['Normal']
    rPr = style.element.get_or_add_rPr()
    lang = OxmlElement('w:lang')
    lang.set(qn('w:val'), 'pt-BR')
    lang.set(qn('w:eastAsia'), 'pt-BR')
    lang.set(qn('w:bidi'), 'pt-BR')
    rPr.append(lang)

def compilar_disciplina(pasta_fisica, nome_limpo, ua1, ua2, json_filename):
    json_filepath = os.path.join(json_dir, json_filename)
    if not os.path.exists(json_filepath):
        print(f"⚠️ Erro: Arquivo JSON {json_filepath} não encontrado! Pulando...")
        return
        
    # Caminho final de gravação
    pasta_destino = os.path.join(root_dir, pasta_fisica, "questao_2026-3", "AD")
    os.makedirs(pasta_destino, exist_ok=True)
    
    excel_path = os.path.join(pasta_destino, f"AD {nome_limpo}.xlsx")
    word_path = os.path.join(pasta_destino, f"AD {nome_limpo}.docx")
    
    # Carrega as questões do JSON
    with open(json_filepath, 'r', encoding='utf-8') as f:
        questoes = json.load(f)
        
    # Limpa e padroniza os IDs, Tipos e Níveis
    dados_padronizados = []
    for idx, q in enumerate(questoes, 1):
        # Reconstrói a identificação da questão no padrão Kuestion correto (UA-xx_QUESTÃO-x_OBJ-x_Grau)
        if idx <= 3:
            id_kuestion = f"UA-{ua1:02d}_QUESTÃO-{idx}_OBJ-{idx}_FÁCIL"
            tipo_kuestion = "questão de complementação Simples"
            nivel_kuestion = "Reconhecimento"
        elif idx <= 7:
            id_kuestion = f"UA-{ua2:02d}_QUESTÃO-{idx}_OBJ-{idx-3}_MÉDIA"
            tipo_kuestion = "Questão de Resposta Múltiplas"
            nivel_kuestion = "Compreensão"
        else:
            id_kuestion = f"UA-{ua2:02d}_QUESTÃO-{idx}_OBJ-{idx-7}_DIFÍCIL"
            tipo_kuestion = "Questão de asserção e razão"
            nivel_kuestion = "Aplicação e Análise"
            
        # Garante que o enunciado comece com o nome correto da disciplina
        enunciado_bruto = q.get("enunciado", "")
        # Remove eventuais cabeçalhos anteriores ("Disciplina: ...")
        enunciado_limpo = re.sub(r"^Disciplina:.*?\n\n", "", enunciado_bruto, flags=re.IGNORECASE)
        # Monta o enunciado final no padrão
        enunciado_final = f"Disciplina: {nome_limpo}\n\n{enunciado_limpo.strip()}"
        
        # Corrige distratores vazios ou incorretos se existirem
        alternativa_a = q.get("a", "").strip()
        alternativa_b = q.get("b", "").strip()
        alternativa_c = q.get("c", "").strip()
        alternativa_d = q.get("d", "").strip()
        
        # Garante a formatação do feedback
        feedback_raw = q.get("feedback", "")
        feedback_lines = feedback_raw.split("\n")
        
        # Procura a resposta certa no feedback
        gabarito_letra = q.get("gabarito", "").strip().lower()
        if len(gabarito_letra) > 1: # Se for o texto inteiro, tenta reduzir para a letra
            # Ex: "RJ-45 keystone"
            if gabarito_letra.startswith(alternativa_a.lower()[:5]):
                gabarito_letra = "a"
            elif gabarito_letra.startswith(alternativa_b.lower()[:5]):
                gabarito_letra = "b"
            elif gabarito_letra.startswith(alternativa_c.lower()[:5]):
                gabarito_letra = "c"
            elif gabarito_letra.startswith(alternativa_d.lower()[:5]):
                gabarito_letra = "d"
                
        # Monta o texto de feedback ideal
        comentario = ""
        fonte = ""
        for line in feedback_lines:
            if "comentário" in line.lower() or "justificativa" in line.lower():
                comentario = re.sub(r"^(Comentário|Justificativa):\s*", "", line, flags=re.IGNORECASE)
            elif "fonte" in line.lower() or "referência" in line.lower():
                fonte = re.sub(r"^(Fonte|Referência):\s*", "", line, flags=re.IGNORECASE)
        
        # Valores de gabarito e resposta correta textual
        respostas_map = {"a": alternativa_a, "b": alternativa_b, "c": alternativa_c, "d": alternativa_d}
        texto_correto = respostas_map.get(gabarito_letra, gabarito_letra)
        
        feedback_final = f"A resposta certa é {texto_correto}\nComentário: {comentario}\nFonte: {fonte}"
        
        dados_padronizados.append({
            "id": id_kuestion,
            "key": q.get("key", f"q{idx}"),
            "tipo": tipo_kuestion,
            "nivel": nivel_kuestion,
            "enunciado": enunciado_final,
            "a": alternativa_a,
            "b": alternativa_b,
            "c": alternativa_c,
            "d": alternativa_d,
            "gabarito": texto_correto,
            "feedback": feedback_final,
            "comentario": comentario,
            "fonte": fonte
        })
        
    # --- GERAÇÃO EXCEL ---
    colunas = {
        "Identificação da questão": [d["id"] for d in dados_padronizados],
        "Palavra chave": [d["key"] for d in dados_padronizados],
        "Tipo da Questão": [d["tipo"] for d in dados_padronizados],
        "Nível cognitivo": [d["nivel"] for d in dados_padronizados],
        "Texto da Questão": [d["enunciado"] for d in dados_padronizados],
        "Alternativa A": [d["a"] for d in dados_padronizados],
        "Alternativa B": [d["b"] for d in dados_padronizados],
        "Alternativa C": [d["c"] for d in dados_padronizados],
        "Alternativa D": [d["d"] for d in dados_padronizados],
        "Feedback da questão": [d["feedback"] for d in dados_padronizados]
    }
    df = pd.DataFrame(colunas)
    df.to_excel(excel_path, index=False, engine="openpyxl")
    
    # --- GERAÇÃO WORD ---
    doc = Document()
    configurar_idioma_pt_br(doc)
    
    # Configuração de fonte padrão
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    
    # Cabeçalho Institucional
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_p.add_run(f"UNIVERSIDADE NOVA IGUAÇU — UNIG\nNÚCLEO DE EDUCAÇÃO A DISTÂNCIA — NEAD\n\nAvaliação a Distância (AD) — Período 2026.3\nDisciplina: {nome_limpo}")
    title_run.bold = True
    title_run.font.size = Pt(13)
    
    doc.add_paragraph(f"\nEsta avaliação foi elaborada no padrão ENADE com o auxílio da ferramenta Kuestion 4, abordando os conceitos das UAs {ua1} e {ua2}.").italic = True
    doc.add_paragraph().paragraph_format.space_after = Pt(16)
    
    for i, d in enumerate(dados_padronizados, 1):
        # Título da Questão
        q_title = doc.add_paragraph()
        run_title = q_title.add_run(f"Questão {i} — {d['id']} ({d['nivel']})")
        run_title.bold = True
        run_title.font.size = Pt(12)
        q_title.paragraph_format.space_before = Pt(10)
        q_title.paragraph_format.space_after = Pt(4)
        
        # Enunciado sem o prefixo da Disciplina
        enunciado_word = d["enunciado"].replace(f"Disciplina: {nome_limpo}\n\n", "")
        doc.add_paragraph(enunciado_word).paragraph_format.space_after = Pt(6)
        
        # Alternativas de a) a d)
        doc.add_paragraph(f"a) {d['a']}").paragraph_format.left_indent = Inches(0.2)
        doc.add_paragraph(f"b) {d['b']}").paragraph_format.left_indent = Inches(0.2)
        doc.add_paragraph(f"c) {d['c']}").paragraph_format.left_indent = Inches(0.2)
        doc.add_paragraph(f"d) {d['d']}").paragraph_format.left_indent = Inches(0.2)
        
        # Bloco do Professor
        prof_p = doc.add_paragraph()
        prof_p.paragraph_format.space_before = Pt(6)
        prof_p.paragraph_format.space_after = Pt(10)
        
        run_gab = prof_p.add_run(f"✔ Gabarito: {d['gabarito']}\n")
        run_gab.bold = True
        
        prof_p.add_run(f"Justificativa: {d['comentario']}\n").italic = True
        prof_p.add_run(f"Referência Bibliográfica: {d['fonte']}").font.size = Pt(9.5)
        
        # Linha divisória
        doc.add_paragraph("_" * 50).alignment = WD_ALIGN_PARAGRAPH.CENTER
        
    doc.save(word_path)
    print(f" -> Concluída: {nome_limpo} (Arquivos salvos com sucesso!)")

def main():
    print("Iniciando compilação em lote de todas as ADs das disciplinas...")
    print(f"Total a processar: {len(disciplinas_map)} disciplinas.\n")
    
    sucesso = 0
    for pasta, info in disciplinas_map.items():
        try:
            compilar_disciplina(pasta, info[0], info[1], info[2], info[3])
            sucesso += 1
        except Exception as e:
            print(f"❌ Erro ao compilar a disciplina {info[0]} ({pasta}): {e}")
            
    print(f"\nCompilação finalizada!")
    print(f"Disciplinas processadas com sucesso: {sucesso}/{len(disciplinas_map)}")

if __name__ == "__main__":
    main()
