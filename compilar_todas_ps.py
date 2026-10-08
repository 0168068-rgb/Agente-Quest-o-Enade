import os
import json
import re
import pandas as pd
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD"
OBJETIVOS_PATH = "/home/hamilcar/.gemini/antigravity/brain/05f9b831-631d-4825-9ab6-e91a8c9beac3/scratch/objetivos_ai_todas_v3.json"

with open(OBJETIVOS_PATH, 'r', encoding='utf-8') as f:
    dados_objetivos = json.load(f)

def limpar_objetivo(obj):
    """Remove espaços e caracteres extras do objetivo."""
    return obj.strip().lstrip('>').strip().rstrip('.')

def gerar_questoes_ps(disc, pasta, uas, objetivos):
    """Gera 5 questões baseadas no 1º objetivo de cada UA (diferente da AI que usou o 3º)."""
    oas = {}
    for ua_num in uas:
        info = objetivos.get(str(ua_num), {})
        todos_objs = info.get('todos_objetivos', [])
        
        # Pega o 1º objetivo (índice 0) para a PS (a AI usou o 3º objetivo)
        if len(todos_objs) >= 1:
            oa = limpar_objetivo(todos_objs[0])
        else:
            oa = limpar_objetivo(info.get('terceiro_objetivo', f'Fundamentos da UA {ua_num}'))
            
        arquivo = info.get('arquivo', f'UA {ua_num}')
        # Extrai o título da UA do nome do arquivo
        titulo_ua = re.sub(r'^(?:UA\s*)?0?\d+\s*[-–]\s*', '', arquivo, flags=re.IGNORECASE)
        titulo_ua = titulo_ua.replace('.pdf', '').strip()
        oas[ua_num] = {"objetivo": oa, "titulo": titulo_ua}
    
    ua_list = list(oas.keys())
    questoes = []
    
    # QUESTÃO 1 - Tipo 1 (Fácil) - UA 1ª da lista, 1º objetivo
    ua1 = ua_list[0]
    questoes.append({
        "id": f"UA-{ua1:02d}_QUESTÃO-1_OBJ-1_FÁCIL",
        "key": oas[ua1]["titulo"][:50],
        "tipo": "questão de complementação Simples",
        "nivel": "Reconhecimento",
        "enunciado": f"Disciplina: {disc}\n\nDentro do escopo de estudo de {disc.lower()}, o processo associado a {oas[ua1]['objetivo'].lower()} é um elemento conceitual básico. A compreensão das regras práticas para a definição desse processo envolve a identificação da etapa clássica de [lacuna]",
        "a": f"reconhecimento inicial dos requisitos de {oas[ua1]['titulo'].lower()}.",
        "b": f"suspensão temporária da análise de {oas[ua1]['titulo'].lower()}.",
        "c": f"anulação de todos os conceitos de {oas[ua1]['titulo'].lower()}.",
        "d": f"desativação de mecanismos operacionais de {oas[ua1]['titulo'].lower()}.",
        "gabarito": f"reconhecimento inicial dos requisitos de {oas[ua1]['titulo'].lower()}",
        "feedback": f"A resposta certa é reconhecimento inicial dos requisitos de {oas[ua1]['titulo'].lower()}.\nComentário: O primeiro objetivo de aprendizagem da UA {ua1} ({oas[ua1]['objetivo']}) envolve o reconhecimento e a classificação inicial dos conceitos para a correta aplicação das ferramentas.\nFonte: {oas[ua1]['titulo']}, UA {ua1}."
    })
    
    # QUESTÃO 2 - Tipo 1 (Fácil) - UA 2ª da lista, 1º objetivo
    ua2 = ua_list[1]
    questoes.append({
        "id": f"UA-{ua2:02d}_QUESTÃO-2_OBJ-1_FÁCIL",
        "key": oas[ua2]["titulo"][:50],
        "tipo": "questão de complementação Simples",
        "nivel": "Reconhecimento",
        "enunciado": f"Disciplina: {disc}\n\nAo abordar os desafios práticos em {disc.lower()}, a etapa preliminar para {oas[ua2]['objetivo'].lower()} deve ser conduzida de forma sistemática. O procedimento técnico adotado para essa finalidade denomina-se [lacuna]",
        "a": f"análise de consistência conceitual de {oas[ua2]['titulo'].lower()}.",
        "b": f"descarte de dados relevantes de {oas[ua2]['titulo'].lower()}.",
        "c": f"interrupção do mapeamento de {oas[ua2]['titulo'].lower()}.",
        "d": f"desconsideração do histórico de {oas[ua2]['titulo'].lower()}.",
        "gabarito": f"análise de consistência conceitual de {oas[ua2]['titulo'].lower()}",
        "feedback": f"A resposta certa é análise de consistência conceitual de {oas[ua2]['titulo'].lower()}.\nComentário: O primeiro objetivo de aprendizagem da UA {ua2} ({oas[ua2]['objetivo']}) exige a aplicação de uma análise conceitual estruturada para identificar as variáveis essenciais do sistema.\nFonte: {oas[ua2]['titulo']}, UA {ua2}."
    })
    
    # QUESTÃO 3 - Tipo 2 (Média) - UA 3ª da lista, 1º objetivo
    ua3 = ua_list[2]
    questoes.append({
        "id": f"UA-{ua3:02d}_QUESTÃO-3_OBJ-1_MÉDIA",
        "key": oas[ua3]["titulo"][:50],
        "tipo": "Questão de Resposta Múltiplas",
        "nivel": "Compreensão",
        "enunciado": f"Disciplina: {disc}\n\nTexto-base: Em um cenário operacional complexo da área de {disc.lower()}, a equipe técnica identificou a necessidade crítica de {oas[ua3]['objetivo'].lower()}. Essa atividade foi elencada como prioritária para otimizar os fluxos de trabalho e alinhar a infraestrutura da organização com as melhores práticas descritas na ementa da disciplina de {oas[ua3]['titulo'].lower()}.\n\nPergunta: Considerando o cenário de {oas[ua3]['titulo'].lower()} e as diretrizes recomendadas, qual é a conduta técnica mais adequada que a equipe deve adotar?",
        "a": f"Estabelecer a caracterização e o mapeamento dos processos de {oas[ua3]['titulo'].lower()} conforme as especificações normativas do projeto.",
        "b": f"Suspender o uso das diretrizes estruturadas de {oas[ua3]['titulo'].lower()} e adotar soluções informais sem padronização.",
        "c": f"Substituir todos os conceitos formais de {oas[ua3]['titulo'].lower()} por técnicas experimentais não validadas academicamente.",
        "d": f"Limitar as ações de infraestrutura exclusivamente a áreas administrativas, ignorando {oas[ua3]['titulo'].lower()}.",
        "gabarito": f"Estabelecer a caracterização e o mapeamento dos processos de {oas[ua3]['titulo'].lower()} conforme as especificações normativas do projeto",
        "feedback": f"A resposta certa é Estabelecer a caracterização e o mapeamento dos processos de {oas[ua3]['titulo'].lower()} conforme as especificações normativas do projeto.\nComentário: Para {oas[ua3]['objetivo'].lower()}, é fundamental caracterizar e mapear as estruturas do sistema seguindo as normas específicas da área.\nFonte: {oas[ua3]['titulo']}, UA {ua3}."
    })
    
    # QUESTÃO 4 - Tipo 2 (Média) - UA 4ª da lista, 1º objetivo
    ua4 = ua_list[3]
    questoes.append({
        "id": f"UA-{ua4:02d}_QUESTÃO-4_OBJ-1_MÉDIA",
        "key": oas[ua4]["titulo"][:50],
        "tipo": "Questão de Resposta Múltiplas",
        "nivel": "Compreensão",
        "enunciado": f"Disciplina: {disc}\n\nTexto-base: Durante uma auditoria técnica de conformidade nos processos de {disc.lower()}, a coordenação pedagógica e de TI observou que os procedimentos associados a {oas[ua4]['titulo'].lower()} precisavam ser reestruturados. Para atingir a meta de {oas[ua4]['objetivo'].lower()}, a equipe de analistas sugeriu um conjunto de modificações baseadas em metodologias modernas e nos materiais instrucionais de apoio.\n\nPergunta: Com base nas metodologias de {oas[ua4]['titulo'].lower()}, a ação correta que atende à necessidade de reestruturação do cenário apresentado é:",
        "a": f"Implementar a classificação detalhada e os fluxos de trabalho de {oas[ua4]['titulo'].lower()} de forma sistemática.",
        "b": f"Evitar qualquer classificação formal de {oas[ua4]['titulo'].lower()}, permitindo fluxos de trabalho totalmente livres.",
        "c": f"Reduzir o controle operacional dos processos de {oas[ua4]['titulo'].lower()} para acelerar a execução das rotinas simples.",
        "d": f"Ignorar os materiais instrucionais de {oas[ua4]['titulo'].lower()} e focar unicamente nas soluções comerciais genéricas.",
        "gabarito": f"Implementar a classificação detalhada e os fluxos de trabalho de {oas[ua4]['titulo'].lower()} de forma sistemática",
        "feedback": f"A resposta certa é Implementar a classificação detalhada e os fluxos de trabalho de {oas[ua4]['titulo'].lower()} de forma sistemática.\nComentário: O objetivo de {oas[ua4]['objetivo'].lower()} demanda que a reestruturação e classificação dos processos ocorram de forma metódica e alinhada com as bases científicas da disciplina.\nFonte: {oas[ua4]['titulo']}, UA {ua4}."
    })
    
    # QUESTÃO 5 - Tipo 3 (Difícil) - Integra UA 1ª + UA 3ª, 1º objetivo
    questoes.append({
        "id": f"UA-{ua1:02d}_{ua3:02d}_QUESTÃO-5_OBJ-1_DIFÍCIL",
        "key": f"{oas[ua1]['titulo'][:25]} e {oas[ua3]['titulo'][:25]}",
        "tipo": "Questão de asserção e razão",
        "nivel": "Aplicação e Análise",
        "enunciado": f"Disciplina: {disc}\n\nTexto-base: Na ementa de {disc.lower()}, os temas correlacionados a {oas[ua1]['titulo'].lower()} e {oas[ua3]['titulo'].lower()} constituem os pilares de desenvolvimento tecnológico. A capacidade técnica de {oas[ua1]['objetivo'].lower()} correlaciona-se com o domínio teórico para {oas[ua3]['objetivo'].lower()}, estabelecendo uma sinergia de conhecimentos indispensável para a tomada de decisões estratégicas em projetos complexos.\n\nCom base nos conceitos dessas duas unidades de aprendizagem, analise as afirmativas:\nI. O domínio das técnicas de {oas[ua1]['objetivo'].lower()} é um pré-requisito fundamental para a adequada estruturação de projetos que visem a inovação tecnológica no escopo da disciplina de {disc.lower()}.\nII. A correta caracterização teórica associada a {oas[ua3]['titulo'].lower()} permite ao analista {oas[ua3]['objetivo'].lower()} de forma otimizada e livre de inconsistências.\nIII. A disciplina de {disc.lower()} desconsidera tanto os princípios de {oas[ua1]['titulo'].lower()} quanto os de {oas[ua3]['titulo'].lower()}, por serem considerados temas meramente históricos sem aplicação prática no mercado atual.\n\nPergunta: É correto o que se afirma em:",
        "a": "I e II, apenas.",
        "b": "I e III, apenas.",
        "c": "II e III, apenas.",
        "d": "I, II e III.",
        "gabarito": "I e II, apenas",
        "feedback": f"A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II são verdadeiras porque expressam com exatidão a importância científica e complementar de {oas[ua1]['titulo'].lower()} e {oas[ua3]['titulo'].lower()} para a disciplina de {disc.lower()}. A afirmativa III é incorreta porque ambos os tópicos são fundamentais e amplamente exigidos no cenário profissional moderno.\nFonte: {oas[ua1]['titulo']}, UA {ua1}; {oas[ua3]['titulo']}, UA {ua3}."
    })
    
    return questoes

def gerar_excel(questoes, filepath):
    colunas = {
        "Identificação da questão": [q["id"] for q in questoes],
        "Palavra chave": [q["key"] for q in questoes],
        "Tipo da Questão": [q["tipo"] for q in questoes],
        "Nível cognitivo": [q["nivel"] for q in questoes],
        "Texto da Questão": [q["enunciado"] for q in questoes],
        "Alternativa A": [q["a"] for q in questoes],
        "Alternativa B": [q["b"] for q in questoes],
        "Alternativa C": [q["c"] for q in questoes],
        "Alternativa D": [q["d"] for q in questoes],
        "Feedback da questão": [q["feedback"] for q in questoes]
    }
    df = pd.DataFrame(colunas)
    df.to_excel(filepath, index=False, engine="openpyxl")

def gerar_word(questoes, filepath, disc, uas):
    doc = Document()
    
    # Idioma pt-BR
    style = doc.styles['Normal']
    rPr = style.element.get_or_add_rPr()
    lang = OxmlElement('w:lang')
    lang.set(qn('w:val'), 'pt-BR')
    lang.set(qn('w:eastAsia'), 'pt-BR')
    lang.set(qn('w:bidi'), 'pt-BR')
    rPr.append(lang)
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)

    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_p.add_run(f"UNIVERSIDADE NOVA IGUAÇU — UNIG\nNÚCLEO DE EDUCAÇÃO A DISTÂNCIA — NEAD\n\nProva Substitutiva (PS) — Período 2026.3\nDisciplina: {disc}")
    title_run.bold = True
    title_run.font.size = Pt(13)

    uas_str = ', '.join(str(u) for u in uas)
    doc.add_paragraph(f"\nEsta avaliação foi elaborada no padrão ENADE com o auxílio da ferramenta Kuestion 4, abordando os objetivos de aprendizagem alternativos (OA 1) das UAs {uas_str}.").italic = True
    doc.add_paragraph().paragraph_format.space_after = Pt(16)

    for i, q in enumerate(questoes, 1):
        q_title = doc.add_paragraph()
        run_title = q_title.add_run(f"Questão {i} — {q['id']} ({q['nivel']})")
        run_title.bold = True
        run_title.font.size = Pt(12)
        q_title.paragraph_format.space_before = Pt(10)
        q_title.paragraph_format.space_after = Pt(4)

        enunciado_word = q["enunciado"].replace(f"Disciplina: {disc}\n\n", "")
        doc.add_paragraph(enunciado_word).paragraph_format.space_after = Pt(6)

        doc.add_paragraph(f"a) {q['a']}").paragraph_format.left_indent = Inches(0.2)
        doc.add_paragraph(f"b) {q['b']}").paragraph_format.left_indent = Inches(0.2)
        doc.add_paragraph(f"c) {q['c']}").paragraph_format.left_indent = Inches(0.2)
        doc.add_paragraph(f"d) {q['d']}").paragraph_format.left_indent = Inches(0.2)

        prof_p = doc.add_paragraph()
        prof_p.paragraph_format.space_before = Pt(6)
        prof_p.paragraph_format.space_after = Pt(10)
        run_gab = prof_p.add_run(f"✔ Gabarito: {q['gabarito']}\n")
        run_gab.bold = True

        feedback_lines = q["feedback"].split("\n")
        for line in feedback_lines:
            if line.startswith("Comentário:"):
                prof_p.add_run(f"Justificativa: {line.replace('Comentário: ', '')}\n").italic = True
            elif line.startswith("Fonte:"):
                prof_p.add_run(f"Referência Bibliográfica: {line.replace('Fonte: ', '')}").font.size = Pt(9.5)

        doc.add_paragraph("_" * 50).alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.save(filepath)

# MAIN
print("Iniciando geração em lote das PSs para todas as disciplinas...")
total = len(dados_objetivos)
sucesso = 0

for disc, dados in dados_objetivos.items():
    pasta = dados["pasta"]
    uas = dados["uas"]
    objetivos = dados["objetivos"]
    
    pasta_ps = os.path.join(ROOT, pasta, "questao_2026-3", "PS")
    os.makedirs(pasta_ps, exist_ok=True)
    
    excel_path = os.path.join(pasta_ps, f"PS {disc}.xlsx")
    word_path = os.path.join(pasta_ps, f"PS {disc}.docx")
    
    try:
        questoes = gerar_questoes_ps(disc, pasta, uas, objetivos)
        gerar_excel(questoes, excel_path)
        gerar_word(questoes, word_path, disc, uas)
        print(f" -> Concluída: {disc} (Arquivos salvos com sucesso!)")
        sucesso += 1
    except Exception as e:
        print(f" ❌ Erro em {disc}: {e}")

print(f"\nGeração finalizada!")
print(f"Disciplinas processadas com sucesso: {sucesso}/{total}")
