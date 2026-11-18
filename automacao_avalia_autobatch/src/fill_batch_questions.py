import sys
import time
import pandas as pd
from playwright.sync_api import sync_playwright

excel_path = "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Cabeamento estruturado II (seg)/questao_2026-3/AD/AD Cabeamento estruturado II.xlsx"
df = pd.read_excel(excel_path).fillna("")

def fill_single_question(page, index):
    if index >= len(df):
        print(f"⚠️ Índice {index} fora dos limites ({len(df)} questões na planilha).")
        return False

    row = df.iloc[index]
    print(f"\n==========================================")
    print(f" 🚀 PREENCHENDO QUESTÃO {index + 1} DE {len(df)}")
    print(f"==========================================")

    # 1. Identificação
    ident = str(row.get('Identificação da questão', '')).strip()
    if page.locator("#Questao_Nome").count() > 0:
        page.locator("#Questao_Nome").fill(ident)
        print("  ✅ Identificação:", ident)
        
    # 2. Palavra-chave
    palavra = str(row.get('Palavra chave', '')).strip()
    if palavra and page.locator("#PalavrasChave").count() > 0:
        page.locator("#PalavrasChave").fill(palavra)
        page.keyboard.press("Enter")
        print("  ✅ Palavra-chave:", palavra)
        
    # 3. Tipo (Múltipla Escolha)
    if page.locator("#Questao_IdTipo").count() > 0:
        try:
            page.locator("#Questao_IdTipo").select_option(value="1")
            print("  ✅ Tipo da Questão: Múltipla Escolha")
        except:
            pass

    # 4. Nível cognitivo
    nivel = str(row.get('Nível cognitivo', '')).strip()
    for select_id in ["#Questao_IdNivelCognitivo", "#Questao_IdNivelDificuldade", "#Questao_IdGrauDificuldade"]:
        if page.locator(select_id).count() > 0:
            try:
                opts = page.locator(f"{select_id} option").all_inner_texts()
                for idx_opt, opt in enumerate(opts):
                    if nivel.lower() in opt.lower():
                        page.locator(select_id).select_option(index=idx_opt)
                        print(f"  ✅ Nível Cognitivo: {opt.strip()}")
                        break
            except Exception:
                pass

    # 5. Textos (usando texto exato da planilha sem duplicar "Disciplina:")
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
            return 'TinyMCE atualizado!';
        }
        return 'TinyMCE ausente';
    }"""
    
    res = page.evaluate(js_tinymce, {
        "texto_q": texto_q,
        "alt_a": alt_a,
        "alt_b": alt_b,
        "alt_c": alt_c,
        "alt_d": alt_d,
        "feedback": feedback
    })
    print("  ✅ Editores de texto:", res)

    # 6. Remoção de Alternativa E
    alt_e = str(row.get('Alternativa E', '')).strip()
    if not alt_e:
        page.evaluate("""() => {
            const btnDeleteE = document.querySelector('button[onclick*="removerAfirmativa"], a[onclick*="removerAfirmativa"], .btn-remove-afirmativa, i.fa-trash');
            if (btnDeleteE) btnDeleteE.click();
        }""")

    # 7. Descobrir e Marcar Resposta Correta via iCheck
    feedback_lower = feedback.lower()
    alt_a_lower = alt_a.lower().rstrip('.')
    alt_b_lower = alt_b.lower().rstrip('.')
    alt_c_lower = alt_c.lower().rstrip('.')
    alt_d_lower = alt_d.lower().rstrip('.')
    
    correct_idx = 0 # Padrão A
    
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
        const input = document.querySelector(selector);
        if (!input) return 'Input não encontrado';
        
        if (typeof $ !== 'undefined' && $.fn && $.fn.iCheck) {
            $(selector).iCheck('check');
            return 'iCheck jQuery OK';
        }
        
        const wrapper = input.closest('.iradio_flat-green, .iradio_square-green, .iradio_flat, div[class*="iradio"]');
        if (wrapper) {
            const helper = wrapper.querySelector('.iCheck-helper') || wrapper;
            helper.click();
            return 'iCheck-helper OK';
        }
        
        input.click();
        input.checked = true;
        return 'Direct click OK';
    }"""

    icheck_res = page.evaluate(js_icheck, correct_idx)
    letter_name = ["A", "B", "C", "D"][correct_idx]
    print(f"  ✅ Resposta Correta: Alternativa {letter_name} ({icheck_res})")
    print(f"✨ Questão {index + 1} preenchida com sucesso!")
    return True

def main():
    start_index = int(sys.argv[1]) if len(sys.argv) > 1 else 2 # Padrão: Questão 3 (índice 2)
    
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = [pg for pg in context.pages if "avalia" in pg.url][0]
        
        print(f"Conectado ao AVALIA. Iniciando preenchimento a partir da Questão {start_index + 1}...")
        fill_single_question(page, start_index)

if __name__ == "__main__":
    main()
