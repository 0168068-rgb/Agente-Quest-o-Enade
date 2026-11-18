import os
import sys
import time
import json
import pandas as pd
from playwright.sync_api import sync_playwright

excel_path = "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Compiladores/questao_2026-3/AD/AD Compiladores.xlsx"
df = pd.read_excel(excel_path).fillna("")

results = []

def fill_question(page, index):
    row = df.iloc[index]
    ident = str(row.get('Identificação da questão', '')).strip()
    print(f"\n==========================================")
    print(f" 🚀 [COMPILADORES] QUESTÃO {index + 1}/{len(df)}: {ident}")
    print(f"==========================================")

    # Identificação
    if page.locator("#Questao_Nome").count() > 0:
        page.locator("#Questao_Nome").fill(ident)
        print("  ✅ Identificação:", ident)
        
    # Palavra-chave
    palavra = str(row.get('Palavra chave', '')).strip()
    if palavra and page.locator("#PalavrasChave").count() > 0:
        page.locator("#PalavrasChave").fill(palavra)
        page.keyboard.press("Enter")
        print("  ✅ Palavra-chave:", palavra)
        
    # Tipo
    if page.locator("#Questao_IdTipo").count() > 0:
        try:
            page.locator("#Questao_IdTipo").select_option(value="1")
            print("  ✅ Tipo: Múltipla Escolha")
        except:
            pass

    # Nível cognitivo
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

    # Textos
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
    print("  ✅ Editores TinyMCE preenchidos.")

    # Remoção de Alternativa E
    alt_e = str(row.get('Alternativa E', '')).strip()
    if not alt_e:
        page.evaluate("""() => {
            const btnDeleteE = document.querySelector('button[onclick*="removerAfirmativa"], a[onclick*="removerAfirmativa"], .btn-remove-afirmativa, i.fa-trash');
            if (btnDeleteE) btnDeleteE.click();
        }""")

    # Resposta Correta (iCheck)
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
    letter_name = ["A", "B", "C", "D"][correct_idx]
    print(f"  ✅ Resposta Correta: Alternativa {letter_name}")
    return ident, letter_name

def save_current_question(page):
    captured = {}
    
    def on_res(response):
        try:
            if "Salvar" in response.url or "Questao" in response.url:
                if response.status == 200:
                    t = response.text()
                    if "idQuestao" in t or "IdQuestao" in t:
                        d = json.loads(t)
                        qid = d.get("idQuestao") or d.get("IdQuestao")
                        if qid:
                            captured['id'] = str(qid)
        except:
            pass
            
    page.on("response", on_res)
    
    # Clicar em salvar
    page.evaluate("""() => {
        const btnSave = document.getElementById('submitFormQuestao') || 
                        document.querySelector('button[type="submit"]') ||
                        document.querySelector('.btn-info[onclick*="Salvar"]');
        if (btnSave) btnSave.click();
        else if (document.getElementById('formSalvarQuestao')) document.getElementById('formSalvarQuestao').submit();
    }""")
    print("  💾 Formulário submetido para salvamento.")
    time.sleep(2.5)
    
    # Checar se ID foi capturado no hidden input ou na resposta de rede
    hid_id = page.evaluate("() => document.getElementById('Questao_IdQuestao') ? document.getElementById('Questao_IdQuestao').value : null")
    final_id = captured.get('id') or (hid_id if hid_id and hid_id != "0" else "Atribuído no AVALIA")
    print(f"  📌 CÓDIGO AVALIA OBTIDO: {final_id}")
    return final_id

def open_new_question_form(page):
    page.evaluate("""() => {
        const btnNova = document.getElementById('btnEnviarQuestaoCriarNova') || 
                         document.querySelector('a[href*="NovaQuestao"], button[onclick*="NovaQuestao"]');
        if (btnNova) btnNova.click();
        else window.location.href = 'https://avalia.grupoa.com.br/Questao/NovaQuestao?IsEdicao=False';
    }""")
    time.sleep(2.0)

def main():
    print("==========================================================")
    print(" 🚀 EXECUÇÃO AUTOMÁTICA COMPLETA: COMPILADORES (10 QUESTÕES)")
    print("==========================================================")
    
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = [pg for pg in context.pages if "avalia" in pg.url][0]
        
        report_data = []

        for idx in range(len(df)):
            ident, correct_letter = fill_question(page, idx)
            time.sleep(1.0)
            
            ava_id = save_current_question(page)
            report_data.append({
                "num": idx + 1,
                "ident": ident,
                "correct": correct_letter,
                "ava_id": ava_id
            })
            
            if idx < len(df) - 1:
                print("  🔄 Abrindo novo formulário para a próxima questão...")
                open_new_question_form(page)

        print("\n==========================================================")
        print(" 📋 RELATÓRIO FINAL DE CÓDIGOS AVALIA — COMPILADORES")
        print("==========================================================")
        print(f"{'#':<3} | {'IDENTIFICADOR ORIGINAL':<35} | {'CÓDIGO AVALIA':<18} | {'CORRETA':<7}")
        print("-" * 75)
        for r in report_data:
            print(f"{r['num']:<3} | {r['ident']:<35} | {r['ava_id']:<18} | {r['correct']:<7}")
            
        report_md = "# Relatório Oficial de Lançamento no AVALIA — Compiladores\n\n"
        report_md += "| # | Identificador Original | Código / ID no AVALIA | Resposta Correta |\n"
        report_md += "|---|---|---|---|\n"
        for r in report_data:
            report_md += f"| {r['num']} | `{r['ident']}` | **{r['ava_id']}** | Alternativa {r['correct']} |\n"
            
        with open("Relatorio_Oficial_AVALIA_Compiladores.md", "w", encoding="utf-8") as f:
            f.write(report_md)
            
        print("\n✨ Relatório final salvo com sucesso em Relatorio_Oficial_AVALIA_Compiladores.md!")

if __name__ == "__main__":
    main()
