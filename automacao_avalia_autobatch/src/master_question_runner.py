import os
import time
import pandas as pd
from playwright.sync_api import sync_playwright

# Lista ordenada de todos os 22 arquivos de planilhas AD
EXCEL_FILES = [
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Cabeamento estruturado II (seg)/questao_2026-3/AD/AD Cabeamento estruturado II.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Compiladores/questao_2026-3/AD/AD Compiladores.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Desenvolvimento de Dispositivos Móveis/questao_2026-3/AD/AD Desenvolvimento de Dispositivos Móveis.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Estrutura de dados(seg)/questao_2026-3/AD/AD Estrutura de Dados.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Gerenciamento de Redes/questao_2026-3/AD/AD Gerenciamento de redes de computadores.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Infraestrutura de rede (seg)/questao_2026-3/AD/AD Infraestrutura de redes.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Infraestrutura de TI (4º per Redes)/questao_2026-3/AD/AD Infraestrutura de TI.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Infraestrutura e Serviços de TI/questao_2026-3/AD/AD Infraestrutura e serviços de TI.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Interação Humano-Computador/questao_2026-3/AD/AD Interação Humano-Computador.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Programação em Python(seg)/questao_2026-3/AD/AD Programação em PYTHON.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Programação WEB II- Desenvolvimento Back-end/questao_2026-3/AD/AD Programação WEB II - Desenvolvimento back-end.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Projetos de Redes de Computadores (seg)/questao_2026-3/AD/AD Projeto de Redes de Computadores.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Redes Convergentes/questao_2026-3/AD/AD Redes Convergentes.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Redes de Alta disponibilidade (4º Per redes)/questao_2026-3/AD/AD Redes de Alta Disponibilidade.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Redes de Computadores(seg)/questao_2026-3/AD/AD Redes de Computadores.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Redes de Longa Distância/questao_2026-3/AD/AD Redes de Longa Distância.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Redes sem Fio (4º Per Redes)/questao_2026-3/AD/AD Redes Sem Fio.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Segurança da Informação e Legislação/questao_2026-3/AD/AD Segurança da Informação e Legislação.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Segurança da Informação/questao_2026-3/AD/AD Segurança da informação.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Segurança de Redes de Computadores/questao_2026-3/AD/AD Segurança de redes de computadores.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Servidores e computação na Nuvem/questao_2026-3/AD/AD Servidores e Computação na Nuvem.xlsx",
    "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Sistemas Operacionais de Redes Abertas/questao_2026-3/AD/AD Sistemas Operacionais de Redes Abertas.xlsx"
]

def fill_row_to_form(page, row):
    ident = str(row.get('Identificação da questão', '')).strip()
    if page.locator("#Questao_Nome").count() > 0:
        page.locator("#Questao_Nome").fill(ident)
        
    palavra = str(row.get('Palavra chave', '')).strip()
    if palavra and page.locator("#PalavrasChave").count() > 0:
        page.locator("#PalavrasChave").fill(palavra)
        page.keyboard.press("Enter")
        
    if page.locator("#Questao_IdTipo").count() > 0:
        try:
            page.locator("#Questao_IdTipo").select_option(value="1")
        except:
            pass

    nivel = str(row.get('Nível cognitivo', '')).strip()
    for select_id in ["#Questao_IdNivelCognitivo", "#Questao_IdNivelDificuldade", "#Questao_IdGrauDificuldade"]:
        if page.locator(select_id).count() > 0:
            try:
                opts = page.locator(f"{select_id} option").all_inner_texts()
                for idx_opt, opt in enumerate(opts):
                    if nivel.lower() in opt.lower():
                        page.locator(select_id).select_option(index=idx_opt)
                        break
            except Exception:
                pass

    texto_q = str(row.get('Texto da Questão', ''))
    alt_a = str(row.get('Alternativa A', ''))
    alt_b = str(row.get('Alternativa B', ''))
    alt_c = str(row.get('Alternativa C', ''))
    alt_d = str(row.get('Alternativa D', ''))
    feedback = str(row.get('Feedback da questão', ''))
    
    js_tinymce = """(data) => {
        if (typeof tinymce !== 'undefined') {
            const map = {
                'TextoQuestao': data.texto_q,
                'TextoAfirmativaA': data.alt_a,
                'TextoAfirmativaB': data.alt_b,
                'TextoAfirmativaC': data.alt_c,
                'TextoAfirmativaD': data.alt_d,
                'TextoPadraoResposta': data.feedback,
                'TextoFeedbackQuestao': data.feedback
            };
            
            for (let id in map) {
                let inst = tinymce.get(id);
                if (inst) {
                    inst.setContent(map[id].replace(/\\n/g, '<br>'));
                }
            }
            return 'OK';
        }
        return 'ERR';
    }"""
    
    page.evaluate(js_tinymce, {
        "texto_q": texto_q,
        "alt_a": alt_a,
        "alt_b": alt_b,
        "alt_c": alt_c,
        "alt_d": alt_d,
        "feedback": feedback
    })

    alt_e = str(row.get('Alternativa E', '')).strip()
    if not alt_e:
        page.evaluate("""() => {
            const btnDeleteE = document.querySelector('button[onclick*="removerAfirmativa"], a[onclick*="removerAfirmativa"], .btn-remove-afirmativa, i.fa-trash');
            if (btnDeleteE) btnDeleteE.click();
        }""")

    feedback_lower = feedback.lower()
    alt_a_lower = alt_a.lower().rstrip('.')
    alt_b_lower = alt_b.lower().rstrip('.')
    alt_c_lower = alt_c.lower().rstrip('.')
    alt_d_lower = alt_d.lower().rstrip('.')
    
    correct_idx = 0
    if "resposta certa é " + alt_a_lower in feedback_lower or "alternativa a" in feedback_lower:
        correct_idx = 0
    elif "resposta certa é " + alt_b_lower in feedback_lower or "alternativa b" in feedback_lower:
        correct_idx = 1
    elif "resposta certa é " + alt_c_lower in feedback_lower or "alternativa c" in feedback_lower:
        correct_idx = 2
    elif "resposta certa é " + alt_d_lower in feedback_lower or "alternativa d" in feedback_lower:
        correct_idx = 3
    else:
        for idx_letter, text_alt in enumerate([alt_a_lower, alt_b_lower, alt_c_lower, alt_d_lower]):
            if text_alt and text_alt in feedback_lower[:120]:
                correct_idx = idx_letter
                break

    js_icheck = """(idx) => {
        const selector = 'input[name="Afirmativas[' + idx + '].Verdadeira"]';
        if (typeof $ !== 'undefined' && $.fn && $.fn.iCheck) {
            $(selector).iCheck('check');
        }
    }"""
    page.evaluate(js_icheck, correct_idx)
    return ident

def main():
    print("==========================================================")
    print(" 🚀 MASTER RUNNER DE AUTOMAGIA DE QUESTÕES AVALIA (22 ARQUIVOS)")
    print("==========================================================")
    
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = [pg for pg in context.pages if "avalia" in pg.url][0]
        
        last_filled = ""
        
        for file_idx, file_path in enumerate(EXCEL_FILES, 1):
            file_name = os.path.basename(file_path)
            print(f"\n----------------------------------------------------------")
            print(f" 📂 PROCESSANDO PLANILHA [{file_idx}/22]: {file_name}")
            print(f"----------------------------------------------------------")
            
            try:
                df = pd.read_excel(file_path).fillna("")
            except Exception as e:
                print(f"❌ Erro ao abrir {file_name}: {e}")
                continue
                
            for q_idx in range(len(df)):
                row = df.iloc[q_idx]
                target_ident = str(row.get('Identificação da questão', '')).strip()
                
                print(f"⏳ Aguardando formulário pronto para Questão {q_idx + 1}/{len(df)} ({file_name})...")
                
                # Aguardar formulário limpo ou pronto para a nova questão
                while True:
                    try:
                        val = page.evaluate("""() => {
                            const el = document.getElementById('Questao_Nome');
                            return el ? el.value.trim() : null;
                        }""")
                        
                        if val is not None and (val == "" or (val != target_ident and val != last_filled)):
                            time.sleep(0.8)
                            ident_filled = fill_row_to_form(page, row)
                            last_filled = ident_filled
                            print(f"  ✅ Questão {q_idx + 1}/{len(df)} preenchida: {ident_filled}")
                            break
                    except Exception as ex:
                        pass
                    time.sleep(1.5)
                    
            print(f"🎉 PLANILHA [{file_idx}/22] ({file_name}) CONCLUÍDA COM SUCESSO!")
            
    print("\n🏆 TODAS AS 22 PLANILHAS E SUAS QUESTÕES FORAM PROCESSADAS!")

if __name__ == "__main__":
    main()
