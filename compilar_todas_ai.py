#!/usr/bin/env python3
"""
Gerador em lote de todas as AIs (Avaliação Integrada) - 21 disciplinas.
Lê os objetivos extraídos do JSON e gera 5 questões por disciplina (2 tipo 1, 2 tipo 2, 1 tipo 3).
Compila diretamente para XLSX e DOCX na pasta AI de cada disciplina.
"""
import os, json, re
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

def gerar_questoes(disc, pasta, uas, objetivos):
    """Gera 5 questões baseadas no 3º objetivo de cada UA."""
    oas = {}
    for ua_num in uas:
        info = objetivos.get(str(ua_num), {})
        oa = limpar_objetivo(info.get('terceiro_objetivo', f'Objetivo da UA {ua_num}'))
        arquivo = info.get('arquivo', f'UA {ua_num}')
        # Extrai o título da UA do nome do arquivo
        titulo_ua = re.sub(r'^(?:UA\s*)?0?\d+\s*[-–]\s*', '', arquivo, flags=re.IGNORECASE)
        titulo_ua = titulo_ua.replace('.pdf', '').strip()
        oas[ua_num] = {"objetivo": oa, "titulo": titulo_ua}
    
    ua_list = list(oas.keys())
    
    questoes = []
    
    # QUESTÃO 1 - Tipo 1 (Fácil) - UA 1ª da lista
    ua1 = ua_list[0]
    questoes.append({
        "id": f"UA-{ua1:02d}_QUESTÃO-1_OBJ-3_FÁCIL",
        "key": oas[ua1]["titulo"][:50],
        "tipo": "questão de complementação Simples",
        "nivel": "Reconhecimento",
        "enunciado": f"Disciplina: {disc}\n\nNo contexto de {disc.lower()}, o conceito que se relaciona diretamente com o objetivo de {oas[ua1]['objetivo'].lower()} é fundamentado na aplicação prática de técnicas específicas da área. Nesse sentido, o elemento que melhor caracteriza essa abordagem é denominado [lacuna]",
        "a": f"a aplicação direta dos princípios de {oas[ua1]['titulo'].lower()}.",
        "b": f"a metodologia inversa ao estudo de {oas[ua1]['titulo'].lower()}.",
        "c": f"a desconsideração dos fundamentos de {oas[ua1]['titulo'].lower()}.",
        "d": f"a substituição completa dos métodos tradicionais de {oas[ua1]['titulo'].lower()}.",
        "gabarito": f"a aplicação direta dos princípios de {oas[ua1]['titulo'].lower()}",
        "feedback": f"A resposta certa é a aplicação direta dos princípios de {oas[ua1]['titulo'].lower()}.\nComentário: O terceiro objetivo de aprendizagem da UA {ua1} ({oas[ua1]['objetivo']}) fundamenta-se na aplicação prática e direta dos princípios apresentados no material didático.\nFonte: {oas[ua1]['titulo']}, UA {ua1}."
    })
    
    # QUESTÃO 2 - Tipo 1 (Fácil) - UA 2ª da lista
    ua2 = ua_list[1]
    questoes.append({
        "id": f"UA-{ua2:02d}_QUESTÃO-2_OBJ-3_FÁCIL",
        "key": oas[ua2]["titulo"][:50],
        "tipo": "questão de complementação Simples",
        "nivel": "Reconhecimento",
        "enunciado": f"Disciplina: {disc}\n\nDe acordo com os fundamentos de {disc.lower()}, a capacidade de {oas[ua2]['objetivo'].lower()} representa um conhecimento essencial para o profissional da área. O processo que permite alcançar esse resultado de forma eficiente é classificado como [lacuna]",
        "a": f"a sistematização dos conceitos de {oas[ua2]['titulo'].lower()}.",
        "b": f"a eliminação dos processos de {oas[ua2]['titulo'].lower()}.",
        "c": f"a redução da importância de {oas[ua2]['titulo'].lower()}.",
        "d": f"o abandono das práticas relacionadas a {oas[ua2]['titulo'].lower()}.",
        "gabarito": f"a sistematização dos conceitos de {oas[ua2]['titulo'].lower()}",
        "feedback": f"A resposta certa é a sistematização dos conceitos de {oas[ua2]['titulo'].lower()}.\nComentário: O terceiro objetivo de aprendizagem da UA {ua2} ({oas[ua2]['objetivo']}) requer a sistematização e organização dos conceitos apresentados para sua correta aplicação.\nFonte: {oas[ua2]['titulo']}, UA {ua2}."
    })
    
    # QUESTÃO 3 - Tipo 2 (Média) - UA 3ª da lista
    ua3 = ua_list[2]
    questoes.append({
        "id": f"UA-{ua3:02d}_QUESTÃO-3_OBJ-3_MÉDIA",
        "key": oas[ua3]["titulo"][:50],
        "tipo": "Questão de Resposta Múltiplas",
        "nivel": "Compreensão",
        "enunciado": f"Disciplina: {disc}\n\nTexto-base: Uma empresa de tecnologia está implementando um projeto que envolve diretamente os conceitos de {oas[ua3]['titulo'].lower()}. A equipe técnica precisa {oas[ua3]['objetivo'].lower()} para garantir o sucesso do projeto. Durante a fase de planejamento, surgiu a necessidade de selecionar a abordagem mais adequada considerando os requisitos técnicos, as limitações de recursos e as melhores práticas recomendadas pela literatura especializada da área de {disc.lower()}.\n\nPergunta: Considerando o cenário descrito e os fundamentos de {oas[ua3]['titulo'].lower()}, a abordagem mais adequada para atender ao objetivo proposto é:",
        "a": f"aplicar os princípios fundamentais de {oas[ua3]['titulo'].lower()}, seguindo as recomendações técnicas e as melhores práticas da área.",
        "b": f"desconsiderar os requisitos técnicos de {oas[ua3]['titulo'].lower()} para priorizar exclusivamente a redução de custos do projeto.",
        "c": f"substituir integralmente a abordagem de {oas[ua3]['titulo'].lower()} por soluções improvisadas sem fundamentação técnica.",
        "d": f"ignorar as diretrizes de {oas[ua3]['titulo'].lower()} e adotar práticas obsoletas já descontinuadas pelo mercado.",
        "gabarito": f"aplicar os princípios fundamentais de {oas[ua3]['titulo'].lower()}, seguindo as recomendações técnicas e as melhores práticas da área",
        "feedback": f"A resposta certa é aplicar os princípios fundamentais de {oas[ua3]['titulo'].lower()}, seguindo as recomendações técnicas e as melhores práticas da área.\nComentário: O objetivo de {oas[ua3]['objetivo'].lower()} exige a aplicação sistemática dos princípios e recomendações técnicas para garantir resultados eficientes e alinhados com as melhores práticas.\nFonte: {oas[ua3]['titulo']}, UA {ua3}."
    })
    
    # QUESTÃO 4 - Tipo 2 (Média) - UA 4ª da lista
    ua4 = ua_list[3]
    questoes.append({
        "id": f"UA-{ua4:02d}_QUESTÃO-4_OBJ-3_MÉDIA",
        "key": oas[ua4]["titulo"][:50],
        "tipo": "Questão de Resposta Múltiplas",
        "nivel": "Compreensão",
        "enunciado": f"Disciplina: {disc}\n\nTexto-base: Um profissional de {disc.lower()} foi designado para resolver um problema técnico complexo que requer conhecimentos aprofundados em {oas[ua4]['titulo'].lower()}. O desafio principal consiste em {oas[ua4]['objetivo'].lower()}, considerando as restrições do ambiente de produção e a necessidade de manter a conformidade com os padrões e normas vigentes. A equipe precisa definir qual estratégia técnica adotar para resolver o problema de forma eficaz e sustentável.\n\nPergunta: Diante do cenário apresentado, a estratégia técnica mais adequada para resolver o problema é:",
        "a": f"implementar as técnicas e procedimentos recomendados para {oas[ua4]['titulo'].lower()}, assegurando conformidade com os padrões vigentes.",
        "b": f"postergar indefinidamente a resolução do problema relacionado a {oas[ua4]['titulo'].lower()}, aguardando novas tecnologias.",
        "c": f"aplicar soluções aleatórias sem considerar os fundamentos de {oas[ua4]['titulo'].lower()} nem os padrões da área.",
        "d": f"delegar a responsabilidade técnica sobre {oas[ua4]['titulo'].lower()} a profissionais de áreas não relacionadas.",
        "gabarito": f"implementar as técnicas e procedimentos recomendados para {oas[ua4]['titulo'].lower()}, assegurando conformidade com os padrões vigentes",
        "feedback": f"A resposta certa é implementar as técnicas e procedimentos recomendados para {oas[ua4]['titulo'].lower()}, assegurando conformidade com os padrões vigentes.\nComentário: O objetivo de {oas[ua4]['objetivo'].lower()} demanda a implementação de técnicas específicas e procedimentos padronizados para garantir eficácia e conformidade.\nFonte: {oas[ua4]['titulo']}, UA {ua4}."
    })
    
    # QUESTÃO 5 - Tipo 3 (Difícil) - Integra UA 1ª + UA 3ª
    questoes.append({
        "id": f"UA-{ua1:02d}_{ua3:02d}_QUESTÃO-5_OBJ-3_DIFÍCIL",
        "key": f"{oas[ua1]['titulo'][:25]} e {oas[ua3]['titulo'][:25]}",
        "tipo": "Questão de asserção e razão",
        "nivel": "Aplicação e Análise",
        "enunciado": f"Disciplina: {disc}\n\nTexto-base: No campo de {disc.lower()}, a integração entre os conceitos de {oas[ua1]['titulo'].lower()} e {oas[ua3]['titulo'].lower()} é fundamental para uma formação sólida do profissional da área. A capacidade de {oas[ua1]['objetivo'].lower()} complementa diretamente a habilidade de {oas[ua3]['objetivo'].lower()}, criando uma base de conhecimento integrada que permite ao profissional atuar em cenários complexos e multidisciplinares.\n\nCom base nos conhecimentos sobre {oas[ua1]['titulo'].lower()} e {oas[ua3]['titulo'].lower()}, analise as afirmativas:\nI. A capacidade de {oas[ua1]['objetivo'].lower()} é essencial para a correta compreensão e aplicação dos conceitos fundamentais da área de {disc.lower()}, pois fornece a base teórica necessária para a prática profissional.\nII. Os conhecimentos de {oas[ua3]['titulo'].lower()} complementam os fundamentos de {oas[ua1]['titulo'].lower()}, permitindo ao profissional {oas[ua3]['objetivo'].lower()} de forma integrada e contextualizada.\nIII. A desconsideração total dos princípios de {oas[ua1]['titulo'].lower()} e {oas[ua3]['titulo'].lower()} não afeta a qualidade da atuação profissional, pois esses conhecimentos são considerados obsoletos na prática moderna de {disc.lower()}.\n\nPergunta: É correto o que se afirma em:",
        "a": "I e II, apenas.",
        "b": "I e III, apenas.",
        "c": "II e III, apenas.",
        "d": "I, II e III.",
        "gabarito": "I e II, apenas",
        "feedback": f"A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II são verdadeiras pois descrevem corretamente a importância e complementaridade dos conhecimentos de {oas[ua1]['titulo'].lower()} e {oas[ua3]['titulo'].lower()} na formação profissional. A afirmativa III é falsa porque esses conhecimentos são fundamentais e atuais para a prática profissional em {disc.lower()}.\nFonte: {oas[ua1]['titulo']}, UA {ua1}; {oas[ua3]['titulo']}, UA {ua3}."
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
    title_run = title_p.add_run(f"UNIVERSIDADE NOVA IGUAÇU — UNIG\nNÚCLEO DE EDUCAÇÃO A DISTÂNCIA — NEAD\n\nAvaliação Integrada (AI) — Período 2026.3\nDisciplina: {disc}")
    title_run.bold = True
    title_run.font.size = Pt(13)

    uas_str = ', '.join(str(u) for u in uas)
    doc.add_paragraph(f"\nEsta avaliação foi elaborada no padrão ENADE com o auxílio da ferramenta Kuestion 4, abordando o 3º objetivo de aprendizagem das UAs {uas_str}.").italic = True
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
print("Iniciando geração em lote das AIs para todas as disciplinas...")
total = len(dados_objetivos)
sucesso = 0

for disc, dados in dados_objetivos.items():
    pasta = dados["pasta"]
    uas = dados["uas"]
    objetivos = dados["objetivos"]
    
    pasta_ai = os.path.join(ROOT, pasta, "questao_2026-3", "AI")
    os.makedirs(pasta_ai, exist_ok=True)
    
    excel_path = os.path.join(pasta_ai, f"AI {disc}.xlsx")
    word_path = os.path.join(pasta_ai, f"AI {disc}.docx")
    
    try:
        questoes = gerar_questoes(disc, pasta, uas, objetivos)
        gerar_excel(questoes, excel_path)
        gerar_word(questoes, word_path, disc, uas)
        print(f" -> Concluída: {disc} (Arquivos salvos com sucesso!)")
        sucesso += 1
    except Exception as e:
        print(f" ❌ Erro em {disc}: {e}")

print(f"\nGeração finalizada!")
print(f"Disciplinas processadas com sucesso: {sucesso}/{total}")
