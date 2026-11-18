import docx
import pandas as pd
import re
import os
import sys
import tempfile
import subprocess

def normalize_text(text):
    if not isinstance(text, str):
        return text
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("—", "-").replace("–", "-")
    text = text.replace("\xa0", " ")
    return text.strip()

def clean_option_text(text):
    text_str = normalize_text(str(text))
    match = re.match(r"^\(([A-E])\)\s*(.*)", text_str, re.IGNORECASE)
    if match:
        return match.group(2).strip()
    match = re.match(r"^([A-E])\.\s*(.*)", text_str, re.IGNORECASE)
    if match:
        return match.group(2).strip()
    match = re.match(r"^([A-E])\)\s*(.*)", text_str, re.IGNORECASE)
    if match:
        return match.group(2).strip()
    return text_str

def resolve_gdrive_doc(uri_or_url):
    print(f"\n☁️ Resolvendo documento do Google Drive na nuvem...")
    doc_id = None
    display_name = None
    
    if "google-drive://" in uri_or_url:
        res = subprocess.run(["gio", "info", uri_or_url], capture_output=True, text=True)
        for line in res.stdout.split("\n"):
            if "display-name:" in line:
                display_name = line.split("display-name:")[-1].strip()
            if "target-uri:" in line:
                match_id = re.search(r"/document/d/([a-zA-Z0-9_-]+)", line)
                if match_id:
                    doc_id = match_id.group(1)

    if not doc_id:
        match = re.search(r"/document/d/([a-zA-Z0-9_-]+)", uri_or_url)
        if match:
            doc_id = match.group(1)

    if not doc_id:
        parts = uri_or_url.strip("/").split("/")
        last_part = parts[-1]
        if len(last_part) > 25 and re.match(r"^[a-zA-Z0-9_-]+$", last_part):
            doc_id = last_part

    if not doc_id:
        print("❌ Não foi possível identificar o ID do documento do Google Drive.")
        return None

    temp_dir = os.path.join(tempfile.gettempdir(), "ava_temp_docx")
    os.makedirs(temp_dir, exist_ok=True)
    
    file_prefix = display_name if display_name else f"doc_{doc_id}"
    clean_prefix = re.sub(r'[^\w\s-]', '', file_prefix).strip().replace(" ", "_")
    dest_path = os.path.join(temp_dir, f"temp_{clean_prefix}.docx")
    
    export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=docx"
    
    print(f"  • ID do Documento: {doc_id}")
    if display_name:
        print(f"  • Nome do Documento: '{display_name}'")
    print(f"📥 Baixando temporariamente para pasta de sistema: '{dest_path}'...")
    
    try:
        from playwright.sync_api import sync_playwright
        user_data_dir = "/home/hamilcar/Antigravity/playwright_user_data"
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(user_data_dir, headless=False)
            page = context.pages[0] if context.pages else context.new_page()
            with page.expect_download(timeout=30000) as download_info:
                try:
                    page.goto(export_url)
                except Exception:
                    pass
            download = download_info.value
            download.save_as(dest_path)
            context.close()
        print("✓ Download temporário concluído!")
        return dest_path
    except Exception as e:
        print(f"❌ Erro ao baixar documento da nuvem: {e}")
        return None

def parse_docx_file(doc_path):
    print(f"\n📖 Lendo documento Word: '{os.path.basename(doc_path)}'...")
    doc = docx.Document(doc_path)
    paragraphs = [p.text for p in doc.paragraphs]

    gabarito_start_idx = -1
    for i, text in enumerate(paragraphs):
        if "GABARITO" in text.upper() and i > len(paragraphs) // 2:
            gabarito_start_idx = i
            break

    if gabarito_start_idx == -1:
        for i, text in enumerate(paragraphs):
            if re.match(r"^(?:QUESTÃO|Questão)\s+\d+\s*[—\-–\.]\s*(Discursiva|[A-E])", text.strip(), re.IGNORECASE):
                if i > len(paragraphs) // 2:
                    gabarito_start_idx = i
                    break

    if gabarito_start_idx == -1:
        gabarito_start_idx = len(paragraphs)

    print(f"   • Parágrafos de Questões: 0 a {gabarito_start_idx - 1}")
    print(f"   • Parágrafos de Gabarito: {gabarito_start_idx} a {len(paragraphs) - 1}")

    gabarito_data = {}
    for idx in range(gabarito_start_idx, len(paragraphs)):
        text = paragraphs[idx].strip()
        if not text:
            continue
        m1 = re.match(r"^(\d+)\.\s*\(([A-E]|Discursiva)\)\s*(.*)", text, re.IGNORECASE | re.DOTALL)
        m2 = re.match(r"^(?:QUESTÃO|Questão)\s+(\d+)\s*[—\-–\.]\s*(Discursiva|[A-E])\.?\s*(.*)", text, re.IGNORECASE | re.DOTALL)
        m3 = re.match(r"^(\d+)\s*[—\-–\.]\s*\(([A-E]|Discursiva)\)\s*(.*)", text, re.IGNORECASE | re.DOTALL)
        match = m1 or m2 or m3
        if match:
            q_num = int(match.group(1))
            q_type = match.group(2).strip().upper()
            q_rest = match.group(3).strip()
            justification = normalize_text(q_rest.lstrip(".-–— ").strip())
            
            gabarito_data[q_num] = {
                "type": q_type,
                "justification": justification
            }

    questions_raw = []
    current_q = None
    for idx in range(gabarito_start_idx):
        text = paragraphs[idx]
        match = re.match(r"^(?:QUESTÃO|Questão)\s+(\d+)(?:\s*[—\-–]\s*(.*))?$", text.strip(), re.IGNORECASE)
        if match:
            if current_q:
                questions_raw.append(current_q)
            current_q = {
                "number": int(match.group(1)),
                "type_str": match.group(2).strip() if match.group(2) else "",
                "paragraphs": []
            }
        elif current_q:
            current_q["paragraphs"].append(text)

    if current_q:
        questions_raw.append(current_q)

    parsed_questions = []
    for q in questions_raw:
        q_num = q["number"]
        type_str = q["type_str"]
        
        tema = ""
        dificuldade = ""
        enunciado_body_parts = []
        opcoes_raw = []
        
        for p_text in q["paragraphs"]:
            p_text_stripped = p_text.strip()
            if not p_text_stripped:
                continue
                
            # Pular título redundante da questão (ex: Questão 01 — Discursiva / Múltipla escolha)
            if re.match(r"^(?:QUESTÃO|Questão)\s+\d+", p_text_stripped, re.IGNORECASE):
                continue
                
            if p_text_stripped.startswith("Modalidade:") or p_text_stripped.startswith("Tema:"):
                parts = p_text_stripped.split("|")
                for part in parts:
                    part = part.strip()
                    if "Tema:" in part:
                        tema = part.split("Tema:")[-1].strip().rstrip('.')
                    elif "Dificuldade:" in part:
                        dificuldade = part.split("Dificuldade:")[-1].strip().rstrip('.')
                continue
                
            if p_text_stripped.startswith("Texto-base:") or p_text_stripped.startswith("Texto da questão:"):
                prefix_len = len("Texto-base:") if p_text_stripped.startswith("Texto-base:") else len("Texto da questão:")
                txt = p_text_stripped[prefix_len:].strip()
                if txt:
                    enunciado_body_parts.append(txt)
                continue
                
            if p_text_stripped.startswith("Enunciado:") or p_text_stripped.startswith("Comando:"):
                prefix_len = len("Enunciado:") if p_text_stripped.startswith("Enunciado:") else len("Comando:")
                cmd = p_text_stripped[prefix_len:].strip()
                if cmd:
                    enunciado_body_parts.append(cmd)
                continue
                
            if p_text_stripped.startswith("Opções de resposta:") or re.match(r"^\(([A-Ea-e])\)", p_text_stripped) or re.match(r"^([A-Ea-e])\)", p_text_stripped) or re.match(r"^([A-Ea-e])\.\s", p_text_stripped):
                options_text = p_text_stripped
                if options_text.startswith("Opções de resposta:"):
                    options_text = options_text[len("Opções de resposta:"):].strip()
                
                opt_lines = options_text.split("\n")
                for opt_line in opt_lines:
                    opt_line = opt_line.strip()
                    if opt_line:
                        opcoes_raw.append(opt_line)
                continue
                
            if p_text_stripped.startswith("Espaço para resposta:"):
                continue
                
            enunciado_body_parts.append(p_text_stripped)
            
        # Montagem do Enunciado com quebras de linha duplas (\n\n) para parágrafos distintos no editor
        enunciado_blocks = []
        if tema:
            enunciado_blocks.append(f"Tema: {tema}")
        if dificuldade:
            enunciado_blocks.append(f"Grau de dificuldade: {dificuldade}")
        if enunciado_body_parts:
            enunciado_blocks.append("\n\n".join(enunciado_body_parts))
            
        enunciado = normalize_text("\n\n".join(enunciado_blocks))
        opcoes_clean = [clean_option_text(opt) for opt in opcoes_raw]
        
        correct_letter = ""
        feedback = ""
        is_discursiva = False
        
        if q_num in gabarito_data:
            gab = gabarito_data[q_num]
            if gab["type"] == "DISCURSIVA":
                is_discursiva = True
                feedback = gab["justification"]
            else:
                is_discursiva = False
                correct_letter = gab["type"]
                justification = gab["justification"]
                
                correct_idx = ord(correct_letter) - ord('A')
                correct_option_text = ""
                if 0 <= correct_idx < len(opcoes_clean):
                    correct_option_text = opcoes_clean[correct_idx]
                
                feedback = f"A resposta certa é: {correct_option_text}\n{justification}"
        else:
            print(f"⚠️  Questão {q_num} não encontrada no Gabarito.")
            
        parsed_questions.append({
            "original_number": q_num,
            "type_str": type_str,
            "is_discursiva": is_discursiva,
            "enunciado": enunciado,
            "opcoes": opcoes_clean,
            "correct_letter": correct_letter,
            "feedback": normalize_text(feedback)
        })

    return parsed_questions

def export_to_excel(parsed_questions, doc_path, custom_output_dir=None):
    base_name = os.path.splitext(os.path.basename(doc_path))[0]
    if base_name.startswith("temp_"):
        base_name = base_name[5:]
    clean_name = re.sub(r'[^\w\s-]', '', base_name).strip().lower().replace(" ", "_")
    
    output_dir = custom_output_dir or "/home/hamilcar/Antigravity"
    columns = ["Ordem", "Enunciado", "Resposta 1", "Resposta 2", "Resposta 3", "Resposta 4", "Resposta 5", "Resposta certa", "Feedback"]

    if len(parsed_questions) == 0:
        print("\n⚠️ [ATENÇÃO] Nenhuma questão foi identificada no documento Word!")
        print("💡 Verifique se o documento possui parágrafos no formato 'QUESTÃO XX' ou 'Questão XX — ...'.\n")

    rows_completo = []
    for q in parsed_questions:
        row = {
            "Ordem": q["original_number"],
            "Enunciado": q["enunciado"],
            "Resposta 1": q["opcoes"][0] if len(q["opcoes"]) > 0 else "",
            "Resposta 2": q["opcoes"][1] if len(q["opcoes"]) > 1 else "",
            "Resposta 3": q["opcoes"][2] if len(q["opcoes"]) > 2 else "",
            "Resposta 4": q["opcoes"][3] if len(q["opcoes"]) > 3 else "",
            "Resposta 5": q["opcoes"][4] if len(q["opcoes"]) > 4 else "",
            "Resposta certa": q["correct_letter"],
            "Feedback": q["feedback"]
        }
        rows_completo.append(row)
        
    df_completo = pd.DataFrame(rows_completo, columns=columns)

    rows_mc_only = []
    mc_counter = 1
    for q in parsed_questions:
        if q["is_discursiva"]:
            continue
        row = {
            "Ordem": mc_counter,
            "Enunciado": q["enunciado"],
            "Resposta 1": q["opcoes"][0] if len(q["opcoes"]) > 0 else "",
            "Resposta 2": q["opcoes"][1] if len(q["opcoes"]) > 1 else "",
            "Resposta 3": q["opcoes"][2] if len(q["opcoes"]) > 2 else "",
            "Resposta 4": q["opcoes"][3] if len(q["opcoes"]) > 3 else "",
            "Resposta 5": q["opcoes"][4] if len(q["opcoes"]) > 4 else "",
            "Resposta certa": q["correct_letter"],
            "Feedback": q["feedback"]
        }
        rows_mc_only.append(row)
        mc_counter += 1
        
    df_mc_only = pd.DataFrame(rows_mc_only, columns=columns)

    excel_mc_path = os.path.join(output_dir, f"questoes_{clean_name}.xlsx")
    excel_comp_path = os.path.join(output_dir, f"questoes_{clean_name}_completo.xlsx")
    csv_mc_path = os.path.join(output_dir, f"questoes_{clean_name}.csv")
    csv_comp_path = os.path.join(output_dir, f"questoes_{clean_name}_completo.csv")

    df_mc_only.to_excel(excel_mc_path, index=False)
    df_completo.to_excel(excel_comp_path, index=False)
    df_mc_only.to_csv(csv_mc_path, index=False, encoding="utf-8-sig")
    df_completo.to_csv(csv_comp_path, index=False, encoding="utf-8-sig")

    print("\n" + "═"*75)
    print(" 🎉 CONVERSÃO CONCLUÍDA COM SUCESSO!")
    print("═"*75)
    print(f"  • Planilha de Múltipla Escolha para Automação ({len(df_mc_only)} questões):")
    print(f"    👉 Excel: {excel_mc_path}")
    print(f"    👉 CSV:   {csv_mc_path}")
    print(f"\n  • Planilha Completa / Arquivamento ({len(df_completo)} questões):")
    print(f"    👉 Excel: {excel_comp_path}")
    print(f"    👉 CSV:   {csv_comp_path}")
    print("═"*75 + "\n")

def main():
    print("\n" + "═"*80)
    print(" 📄 CONVERSOR INTERATIVO DE QUESTÕES (WORD .DOCX / NUVEM -> EXCEL .XLSX)")
    print("═"*80)
    
    input_source = None
    is_temp_file = False
    
    if len(sys.argv) > 1:
        input_source = sys.argv[1]
    else:
        current_dir = "/home/hamilcar/Antigravity"
        files = [f for f in os.listdir(current_dir) if f.endswith(".docx") and not f.startswith("~$")]
        
        print("\n📁 Opções de arquivo disponíveis:")
        if files:
            for idx, f in enumerate(files, 1):
                print(f"   [{idx}] {f}")
        print("   [N] Digitar link do Google Drive / Nuvem (google-drive:// ou https://...)")
        print("   [0] Digitar caminho de outro arquivo .docx local")
        
        try:
            choice = input("\n👉 Escolha uma opção (ou cole o link do Google Drive): ").strip()
            if not choice:
                if files:
                    input_source = os.path.join(current_dir, files[0])
                else:
                    print("Nenhum arquivo local selecionado.")
                    sys.exit(1)
            elif choice.lower() == "n" or "google-drive://" in choice or "docs.google.com" in choice:
                if choice.lower() == "n":
                    input_source = input("👉 Cole o link do Google Drive / Nuvem: ").strip()
                else:
                    input_source = choice
            elif choice == "0":
                input_source = input("👉 Digite o caminho do arquivo Word: ").strip()
            elif choice.isdigit() and files and 1 <= int(choice) <= len(files):
                input_source = os.path.join(current_dir, files[int(choice) - 1])
            else:
                input_source = choice
        except KeyboardInterrupt:
            print("\n\n👋 Operação cancelada.")
            sys.exit(0)

    doc_path = None
    if input_source and ("google-drive://" in input_source or "docs.google.com" in input_source or len(input_source) > 25 and "/" not in input_source):
        doc_path = resolve_gdrive_doc(input_source)
        is_temp_file = True
    else:
        doc_path = input_source

    if not doc_path or not os.path.exists(doc_path):
        print(f"\n❌ [ERRO] Arquivo Word não encontrado em: '{doc_path}'")
        sys.exit(1)

    parsed = parse_docx_file(doc_path)
    export_to_excel(parsed, doc_path)
    
    if is_temp_file and os.path.exists(doc_path):
        try:
            os.remove(doc_path)
            print(f"🧹 Arquivo temporário da nuvem excluído da pasta de sistema (/tmp): '{doc_path}'\n")
        except Exception as e:
            print(f"⚠️ Não foi possível excluir arquivo temporário: {e}")

if __name__ == "__main__":
    main()
